import hashlib
import json
import secrets
from collections import defaultdict
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from fastapi import APIRouter, Request, Response
from sqlalchemy import text

from northstar.core.auth import CurrentUser, DbSession
from northstar.core.http import ApiError, success
from northstar.core.security import hash_secret, require_idempotency_key
from northstar.core.serialization import order_dict
from northstar.schemas import CheckoutInput, ProfileUpdateInput

router = APIRouter(prefix="/api/v1/customer", tags=["customer"])


@router.get("/orders")
def orders(request: Request, db: DbSession, user: CurrentUser) -> Response:
    rows = (
        db.execute(
            text("SELECT * FROM orders WHERE user_id=:user_id ORDER BY created_at DESC"),
            {"user_id": user["id"]},
        )
        .mappings()
        .all()
    )
    return success(request, [order_dict(db, dict(row)) for row in rows])


def _promotion_discount(db: DbSession, code: str | None, subtotal: Decimal) -> Decimal:
    if not code:
        return Decimal("0")
    now = datetime.now(UTC)
    row = (
        db.execute(
            text(
                "SELECT * FROM promotions WHERE UPPER(code)=:code AND is_active=1 "
                "AND (starts_at IS NULL OR starts_at<=:now) AND (ends_at IS NULL OR ends_at>=:now)"
            ),
            {"code": code.upper(), "now": now},
        )
        .mappings()
        .first()
    )
    if row is None or subtotal < Decimal(str(row["minimum_order"])):
        raise ApiError("Promotion code is invalid for this order.", "INVALID_PROMOTION", 422)
    value = Decimal(str(row["value"]))
    discount = value
    if row["type"] == "percent":
        discount = subtotal * value / Decimal("100")
    return min(subtotal, discount).quantize(Decimal("0.01"))


@router.post("/orders", status_code=201)
def checkout(
    payload: CheckoutInput, request: Request, db: DbSession, user: CurrentUser
) -> Response:
    key = require_idempotency_key(request)
    request_json = json.dumps(
        payload.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
    )
    request_hash = hashlib.sha256(request_json.encode()).hexdigest()
    key_hash = hash_secret(f"{user['id']}:{key}")
    existing = (
        db.execute(
            text("SELECT * FROM idempotency_records WHERE key_hash=:key_hash"),
            {"key_hash": key_hash},
        )
        .mappings()
        .first()
    )
    if existing is not None:
        if not secrets.compare_digest(str(existing["request_hash"]), request_hash):
            raise ApiError(
                "This idempotency key was already used for another request.",
                "IDEMPOTENCY_CONFLICT",
                409,
            )
        return success(request, json.loads(str(existing["response_json"])), "Order created.", 201)

    quantities: dict[int, int] = defaultdict(int)
    for item in payload.items:
        quantities[item.product_id] += item.quantity
        if quantities[item.product_id] > 100:
            raise ApiError("The requested quantity is invalid.", "VALIDATION_ERROR", 422)

    now = datetime.now(UTC)
    lines: list[dict[str, object]] = []
    subtotal = Decimal("0")
    try:
        for product_id, quantity in quantities.items():
            product = (
                db.execute(
                    text(
                        "SELECT * FROM products WHERE id=:id AND status='published' "
                        "AND deleted_at IS NULL LIMIT 1"
                    ),
                    {"id": product_id},
                )
                .mappings()
                .first()
            )
            if product is None:
                raise ApiError("Product not found.", "NOT_FOUND", 404)
            if int(product["stock"]) < quantity:
                raise ApiError(
                    f"Insufficient stock for {product['name']}.", "INSUFFICIENT_STOCK", 409
                )
            unit_price = Decimal(str(product["sale_price"] or product["price"]))
            line_total = (unit_price * quantity).quantize(Decimal("0.01"))
            subtotal += line_total
            lines.append(
                {
                    "product_id": product_id,
                    "product_name": product["name"],
                    "sku": product["sku"],
                    "unit_price": unit_price,
                    "quantity": quantity,
                    "total": line_total,
                }
            )
        discount = _promotion_discount(db, payload.promotion_code, subtotal)
        shipping = Decimal("0") if subtotal >= Decimal("100") else Decimal("8")
        total = max(Decimal("0"), subtotal - discount + shipping)
        number = f"NS-{now:%y%m%d}-{secrets.token_hex(3).upper()}"
        order_result = db.execute(
            text(
                "INSERT INTO orders(number,user_id,customer_name,customer_email,customer_phone,"
                "shipping_address,status,payment_status,subtotal,discount,shipping_fee,total,created_at,updated_at) "
                "VALUES (:number,:user_id,:name,:email,:phone,:address,'pending','unpaid',"
                ":subtotal,:discount,:shipping,:total,:now,:now)"
            ),
            {
                "number": number,
                "user_id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "phone": payload.phone,
                "address": json.dumps(payload.address.model_dump()),
                "subtotal": subtotal,
                "discount": discount,
                "shipping": shipping,
                "total": total,
                "now": now,
            },
        )
        order_id = int(order_result.lastrowid)
        for line in lines:
            updated = db.execute(
                text(
                    "UPDATE products SET stock=stock-:quantity,updated_at=:now "
                    "WHERE id=:id AND stock>=:quantity"
                ),
                {"quantity": line["quantity"], "now": now, "id": line["product_id"]},
            )
            if updated.rowcount != 1:
                raise ApiError("Product stock changed. Please retry.", "STOCK_CONFLICT", 409)
            db.execute(
                text(
                    "INSERT INTO order_items(order_id,product_id,product_name,sku,unit_price,quantity,total,created_at,updated_at) "
                    "VALUES (:order_id,:product_id,:product_name,:sku,:unit_price,:quantity,:total,:now,:now)"
                ),
                {"order_id": order_id, **line, "now": now},
            )
        row = (
            db.execute(text("SELECT * FROM orders WHERE id=:id"), {"id": order_id}).mappings().one()
        )
        data = order_dict(db, dict(row))
        db.execute(
            text(
                "INSERT INTO idempotency_records(key_hash,user_id,request_hash,response_json,status_code,expires_at) "
                "VALUES (:key_hash,:user_id,:request_hash,:response_json,201,:expires_at)"
            ),
            {
                "key_hash": key_hash,
                "user_id": user["id"],
                "request_hash": request_hash,
                "response_json": json.dumps(data),
                "expires_at": now + timedelta(days=1),
            },
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    return success(request, data, "Order created.", 201)


@router.patch("/profile")
def update_profile(
    payload: ProfileUpdateInput, request: Request, db: DbSession, user: CurrentUser
) -> Response:
    db.execute(
        text("UPDATE users SET name=:name,updated_at=:now WHERE id=:id"),
        {"name": payload.name, "now": datetime.now(UTC), "id": user["id"]},
    )
    db.commit()
    user["name"] = payload.name
    return success(request, user, "Profile updated.")
