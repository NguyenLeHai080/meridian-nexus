import re
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import bindparam, text
from sqlalchemy.orm import Session

from northstar.core.database import json_value

SUPPORTED_LOCALES = ("en", "vi", "ja", "ko")


def locale_from_header(value: str | None) -> str:
    if not value:
        return "en"
    for segment in value.split(","):
        code = segment.split(";")[0].strip().lower().split("-")[0]
        aliases = {"vn": "vi", "jp": "ja", "kr": "ko"}
        code = aliases.get(code, code)
        if code in SUPPORTED_LOCALES:
            return code
    return "en"


def translated(row: dict[str, object], field: str, locale: str) -> object:
    translations = json_value(row.get("translations"), {})
    if isinstance(translations, dict):
        localized = translations.get(locale, {})
        if isinstance(localized, dict):
            value = localized.get(field)
            if value not in (None, ""):
                return value
    return row.get(field)


def iso(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value.isoformat().replace("+00:00", "Z")
    raw = str(value)
    if "T" not in raw and " " in raw:
        raw = raw.replace(" ", "T", 1)
    return raw


def money(value: object) -> float:
    if value is None:
        return 0.0
    return float(Decimal(str(value)))


def slugify(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return normalized or f"item-{int(datetime.now(UTC).timestamp())}"


def product_dict(db: Session, row: dict[str, object], locale: str) -> dict[str, object]:
    category = None
    category_id = row.get("category_id")
    if category_id is not None and "category_name" in row:
        category_data = {
            "name": row.get("category_name"),
            "slug": row.get("category_slug"),
            "translations": row.get("category_translations"),
        }
        category = {
            "id": int(category_id),
            "name": translated(category_data, "name", locale),
            "slug": category_data["slug"],
        }
    elif category_id is not None:
        category_row = (
            db.execute(
                text("SELECT id,name,slug,translations FROM categories WHERE id=:id"),
                {"id": category_id},
            )
            .mappings()
            .first()
        )
        if category_row is not None:
            category_data = dict(category_row)
            category = {
                "id": int(category_data["id"]),
                "name": translated(category_data, "name", locale),
                "slug": category_data["slug"],
            }
    return {
        "id": int(row["id"]),
        "name": translated(row, "name", locale),
        "slug": row["slug"],
        "sku": row["sku"],
        "excerpt": translated(row, "excerpt", locale),
        "description": translated(row, "description", locale),
        "price": money(row["price"]),
        "sale_price": None if row.get("sale_price") is None else money(row["sale_price"]),
        "stock": int(row["stock"]),
        "images": json_value(row.get("images"), []),
        "is_featured": bool(row["is_featured"]),
        "category": category,
        "published_at": iso(row.get("published_at")),
    }


def post_dict(db: Session, row: dict[str, object], locale: str) -> dict[str, object]:
    author = row.get("author_name")
    if author is None and row.get("author_id") is not None and "author_name" not in row:
        author = db.execute(
            text("SELECT name FROM users WHERE id=:id"), {"id": row["author_id"]}
        ).scalar_one_or_none()
    return {
        "id": int(row["id"]),
        "title": translated(row, "title", locale),
        "slug": row["slug"],
        "excerpt": translated(row, "excerpt", locale),
        "content": translated(row, "content", locale),
        "cover_image": row.get("cover_image"),
        "author": author,
        "status": row["status"],
        "published_at": iso(row.get("published_at")),
        "created_at": iso(row.get("created_at")),
    }


def order_dict(
    db: Session, row: dict[str, object], include_items: bool = True
) -> dict[str, object]:
    items: list[dict[str, object]] = []
    if include_items:
        item_rows = (
            db.execute(
                text("SELECT * FROM order_items WHERE order_id=:id ORDER BY id"),
                {"id": row["id"]},
            )
            .mappings()
            .all()
        )
        for item in item_rows:
            items.append(
                {
                    "id": int(item["id"]),
                    "product_name": item["product_name"],
                    "sku": item["sku"],
                    "unit_price": money(item["unit_price"]),
                    "quantity": int(item["quantity"]),
                    "total": money(item["total"]),
                }
            )
    return {
        "id": int(row["id"]),
        "number": row["number"],
        "customer_name": row["customer_name"],
        "customer_email": row["customer_email"],
        "status": row["status"],
        "payment_status": row["payment_status"],
        "subtotal": money(row["subtotal"]),
        "discount": money(row["discount"]),
        "shipping_fee": money(row["shipping_fee"]),
        "total": money(row["total"]),
        "shipping_address": json_value(row.get("shipping_address"), None),
        "items": items,
        "created_at": iso(row.get("created_at")),
    }


def orders_dict(db: Session, rows: list[dict[str, object]]) -> list[dict[str, object]]:
    if not rows:
        return []
    order_ids = [int(row["id"]) for row in rows]
    statement = text(
        "SELECT * FROM order_items WHERE order_id IN :order_ids ORDER BY order_id,id"
    ).bindparams(bindparam("order_ids", expanding=True))
    item_rows = db.execute(statement, {"order_ids": order_ids}).mappings().all()
    items_by_order: dict[int, list[dict[str, object]]] = {order_id: [] for order_id in order_ids}
    for item in item_rows:
        items_by_order[int(item["order_id"])].append(
            {
                "id": int(item["id"]),
                "product_name": item["product_name"],
                "sku": item["sku"],
                "unit_price": money(item["unit_price"]),
                "quantity": int(item["quantity"]),
                "total": money(item["total"]),
            }
        )
    data = []
    for row in rows:
        order = order_dict(db, row, include_items=False)
        order["items"] = items_by_order[int(row["id"])]
        data.append(order)
    return data


def conversation_dict(
    db: Session,
    row: dict[str, object],
    *,
    access_token: str | None = None,
    include_messages: bool = True,
) -> dict[str, object]:
    customer = row.get("guest_name")
    if "customer_name" in row and row.get("customer_name") is not None:
        customer = row["customer_name"]
    elif row.get("customer_id") is not None:
        customer = db.execute(
            text("SELECT name FROM users WHERE id=:id"), {"id": row["customer_id"]}
        ).scalar_one_or_none()
    assigned_to = row.get("assigned_name")
    if assigned_to is None and row.get("assigned_to") is not None and "assigned_name" not in row:
        assigned_to = db.execute(
            text("SELECT name FROM users WHERE id=:id"), {"id": row["assigned_to"]}
        ).scalar_one_or_none()
    messages = []
    if include_messages:
        for message in (
            db.execute(
                text("SELECT * FROM messages WHERE conversation_id=:id ORDER BY id"),
                {"id": row["id"]},
            )
            .mappings()
            .all()
        ):
            messages.append(
                {
                    "id": int(message["id"]),
                    "sender_type": message["sender_type"],
                    "body": message["body"],
                    "created_at": iso(message.get("created_at")),
                }
            )
    return {
        "id": int(row["id"]),
        "token": access_token,
        "status": row["status"],
        "customer": customer or "Guest",
        "assigned_to": assigned_to,
        "messages": messages,
        "last_message_at": iso(row.get("last_message_at")),
    }
