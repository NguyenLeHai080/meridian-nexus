import json
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from northstar.core.auth import CurrentUser, DbSession, permission, serialize_user, serialize_users
from northstar.core.config import get_settings
from northstar.core.http import ApiError, pagination_meta, success
from northstar.core.serialization import (
    conversation_dict,
    iso,
    locale_from_header,
    order_dict,
    orders_dict,
    post_dict,
    product_dict,
    slugify,
)
from northstar.modules.storefront.router import _category, _promotion
from northstar.schemas import (
    CategoryInput,
    CategoryUpdateInput,
    ChatReplyInput,
    ContactStatusInput,
    OrderUpdateInput,
    PostInput,
    ProductInput,
    PromotionInput,
    RolesUpdateInput,
)

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])
Page = Annotated[int, Query(ge=1)]
PerPage = Annotated[int, Query(ge=10, le=100)]


def _option(values: list[str]) -> list[dict[str, str]]:
    return [{"value": value, "label": value.replace("_", " ").title()} for value in values]


@router.get("/dashboard", dependencies=[Depends(permission("dashboard.view"))])
def dashboard(request: Request, db: DbSession) -> Response:
    metrics = (
        db.execute(
            text(
                "SELECT (SELECT COALESCE(SUM(total),0) FROM orders WHERE payment_status='paid') revenue,"
                "(SELECT COUNT(*) FROM orders) orders,(SELECT COUNT(*) FROM orders WHERE status='pending') pending_orders,"
                "(SELECT COUNT(*) FROM products WHERE deleted_at IS NULL) products,"
                "(SELECT COUNT(*) FROM products WHERE deleted_at IS NULL AND stock<=5) low_stock_products,"
                "(SELECT COUNT(DISTINCT u.id) FROM users u JOIN role_user ru ON ru.user_id=u.id "
                "JOIN roles r ON r.id=ru.role_id WHERE r.name='customer') customers,"
                "(SELECT COUNT(*) FROM conversations WHERE status='open') open_conversations"
            )
        )
        .mappings()
        .one()
    )
    recent = (
        db.execute(
            text(
                "SELECT id,number,customer_name,status,total,created_at FROM orders ORDER BY created_at DESC LIMIT 6"
            )
        )
        .mappings()
        .all()
    )
    data = {key: float(value) if key == "revenue" else int(value) for key, value in metrics.items()}
    data["recent_orders"] = [
        {
            **dict(row),
            "id": int(row["id"]),
            "total": float(row["total"]),
            "created_at": iso(row["created_at"]),
        }
        for row in recent
    ]
    return success(request, data)


@router.get("/metadata", dependencies=[Depends(permission("dashboard.view"))])
def metadata(request: Request) -> Response:
    options = {
        "order_statuses": _option(
            ["pending", "confirmed", "processing", "shipped", "completed", "cancelled"]
        ),
        "payment_statuses": _option(["unpaid", "paid", "refunded"]),
        "product_statuses": _option(["draft", "published", "archived"]),
        "promotion_types": _option(["percent", "fixed"]),
        "post_statuses": _option(["draft", "published", "archived"]),
        "contact_statuses": _option(["new", "in_progress", "resolved", "spam"]),
    }
    return success(
        request,
        {
            "options": options,
            "defaults": {
                "order_status": "pending",
                "payment_status": "unpaid",
                "product_status": "draft",
                "promotion_type": "percent",
                "promotion_is_active": True,
                "post_status": "draft",
                "contact_status": "new",
            },
            "publishing": {"product_status": "published", "post_status": "published"},
        },
    )


@router.get("/products", dependencies=[Depends(permission("products.view"))])
def products(request: Request, db: DbSession, page: Page = 1, per_page: PerPage = 25) -> Response:
    total = int(
        db.execute(text("SELECT COUNT(*) FROM products WHERE deleted_at IS NULL")).scalar_one()
    )
    rows = (
        db.execute(
            text(
                "SELECT p.*,c.name category_name,c.slug category_slug,c.translations category_translations "
                "FROM products p LEFT JOIN categories c ON c.id=p.category_id "
                "WHERE p.deleted_at IS NULL ORDER BY p.created_at DESC LIMIT :limit OFFSET :offset"
            ),
            {"limit": per_page, "offset": (page - 1) * per_page},
        )
        .mappings()
        .all()
    )
    locale = locale_from_header(request.headers.get("Accept-Language"))
    return success(
        request,
        [product_dict(db, dict(row), locale) for row in rows],
        meta=pagination_meta(page, per_page, total),
    )


def _save_product(db: DbSession, payload: ProductInput, product_id: int | None = None) -> int:
    values = payload.model_dump()
    values["images"] = json.dumps([str(image) for image in payload.images])
    values["now"] = datetime.now(UTC)
    if product_id is None:
        values["slug"] = slugify(payload.name)
        result = db.execute(
            text(
                "INSERT INTO products(category_id,name,slug,sku,excerpt,description,price,sale_price,stock,images,status,is_featured,published_at,created_at,updated_at) "
                "VALUES (:category_id,:name,:slug,:sku,:excerpt,:description,:price,:sale_price,:stock,:images,:status,:is_featured,:published_at,:now,:now) RETURNING id"
            ),
            values,
        )
        return int(result.scalar_one())
    values["id"] = product_id
    result = db.execute(
        text(
            "UPDATE products SET category_id=:category_id,name=:name,sku=:sku,excerpt=:excerpt,description=:description,"
            "price=:price,sale_price=:sale_price,stock=:stock,images=:images,status=:status,is_featured=:is_featured,"
            "published_at=:published_at,updated_at=:now WHERE id=:id AND deleted_at IS NULL"
        ),
        values,
    )
    if result.rowcount != 1:
        raise ApiError("Product not found.", "NOT_FOUND", 404)
    return product_id


def _product_response(
    request: Request, db: DbSession, product_id: int, message: str, status: int = 200
) -> Response:
    row = (
        db.execute(text("SELECT * FROM products WHERE id=:id"), {"id": product_id}).mappings().one()
    )
    locale = locale_from_header(request.headers.get("Accept-Language"))
    return success(request, product_dict(db, dict(row), locale), message, status)


@router.post("/products", status_code=201, dependencies=[Depends(permission("products.manage"))])
def create_product(payload: ProductInput, request: Request, db: DbSession) -> Response:
    try:
        product_id = _save_product(db, payload)
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ApiError("SKU or product slug already exists.", "CONFLICT", 409) from error
    return _product_response(request, db, product_id, "Product created.", 201)


@router.put("/products/{product_id}", dependencies=[Depends(permission("products.manage"))])
def update_product(
    product_id: int, payload: ProductInput, request: Request, db: DbSession
) -> Response:
    _save_product(db, payload, product_id)
    db.commit()
    return _product_response(request, db, product_id, "Product updated.")


@router.delete(
    "/products/{product_id}", status_code=204, dependencies=[Depends(permission("products.manage"))]
)
def delete_product(product_id: int, db: DbSession) -> Response:
    db.execute(
        text("UPDATE products SET deleted_at=:now WHERE id=:id"),
        {"now": datetime.now(UTC), "id": product_id},
    )
    db.commit()
    return Response(status_code=204)


@router.get("/categories", dependencies=[Depends(permission("products.view"))])
def categories(request: Request, db: DbSession) -> Response:
    rows = db.execute(text("SELECT * FROM categories ORDER BY name")).mappings().all()
    locale = locale_from_header(request.headers.get("Accept-Language"))
    return success(request, [_category(db, dict(row), locale) for row in rows])


@router.post("/categories", status_code=201, dependencies=[Depends(permission("products.manage"))])
def create_category(payload: CategoryInput, request: Request, db: DbSession) -> Response:
    now = datetime.now(UTC)
    result = db.execute(
        text(
            "INSERT INTO categories(name,slug,description,is_active,created_at,updated_at) VALUES (:name,:slug,:description,TRUE,:now,:now) RETURNING id"
        ),
        {
            "name": payload.name,
            "slug": slugify(payload.name),
            "description": payload.description,
            "now": now,
        },
    )
    category_id = int(result.scalar_one())
    db.commit()
    row = (
        db.execute(text("SELECT * FROM categories WHERE id=:id"), {"id": category_id})
        .mappings()
        .one()
    )
    return success(request, _category(db, dict(row), "en"), "Category created.", 201)


@router.put("/categories/{category_id}", dependencies=[Depends(permission("products.manage"))])
def update_category(
    category_id: int, payload: CategoryUpdateInput, request: Request, db: DbSession
) -> Response:
    result = db.execute(
        text(
            "UPDATE categories SET name=:name,slug=:slug,description=:description,"
            "is_active=:is_active,updated_at=:now WHERE id=:id"
        ),
        {**payload.model_dump(), "now": datetime.now(UTC), "id": category_id},
    )
    if result.rowcount != 1:
        raise ApiError("Category not found.", "NOT_FOUND", 404)
    db.commit()
    row = (
        db.execute(text("SELECT * FROM categories WHERE id=:id"), {"id": category_id})
        .mappings()
        .one()
    )
    return success(request, _category(db, dict(row), "en"), "Category updated.")


@router.get("/orders", dependencies=[Depends(permission("orders.view"))])
def admin_orders(
    request: Request, db: DbSession, page: Page = 1, per_page: PerPage = 25
) -> Response:
    total = int(db.execute(text("SELECT COUNT(*) FROM orders")).scalar_one())
    rows = (
        db.execute(
            text("SELECT * FROM orders ORDER BY created_at DESC LIMIT :limit OFFSET :offset"),
            {"limit": per_page, "offset": (page - 1) * per_page},
        )
        .mappings()
        .all()
    )
    return success(
        request,
        orders_dict(db, [dict(row) for row in rows]),
        meta=pagination_meta(page, per_page, total),
    )


@router.patch("/orders/{order_id}", dependencies=[Depends(permission("orders.manage"))])
def update_order(
    order_id: int, payload: OrderUpdateInput, request: Request, db: DbSession
) -> Response:
    result = db.execute(
        text(
            "UPDATE orders SET status=:status,payment_status=:payment_status,updated_at=:now WHERE id=:id"
        ),
        {**payload.model_dump(), "now": datetime.now(UTC), "id": order_id},
    )
    if result.rowcount != 1:
        raise ApiError("Order not found.", "NOT_FOUND", 404)
    db.commit()
    row = db.execute(text("SELECT * FROM orders WHERE id=:id"), {"id": order_id}).mappings().one()
    return success(request, order_dict(db, dict(row)), "Order updated.")


@router.get("/promotions", dependencies=[Depends(permission("promotions.view"))])
def promotions(request: Request, db: DbSession) -> Response:
    rows = db.execute(text("SELECT * FROM promotions ORDER BY created_at DESC")).mappings().all()
    locale = locale_from_header(request.headers.get("Accept-Language"))
    return success(request, [_promotion(dict(row), locale) for row in rows])


@router.post(
    "/promotions", status_code=201, dependencies=[Depends(permission("promotions.manage"))]
)
def create_promotion(payload: PromotionInput, request: Request, db: DbSession) -> Response:
    values = payload.model_dump()
    values.update(
        {"code": payload.code.upper() if payload.code else None, "now": datetime.now(UTC)}
    )
    result = db.execute(
        text(
            "INSERT INTO promotions(name,code,type,value,minimum_order,starts_at,ends_at,is_active,created_at,updated_at) VALUES (:name,:code,:type,:value,:minimum_order,:starts_at,:ends_at,:is_active,:now,:now) RETURNING id"
        ),
        values,
    )
    promotion_id = int(result.scalar_one())
    db.commit()
    row = (
        db.execute(text("SELECT * FROM promotions WHERE id=:id"), {"id": promotion_id})
        .mappings()
        .one()
    )
    return success(request, _promotion(dict(row), "en"), "Promotion created.", 201)


@router.put(
    "/promotions/{promotion_id}",
    dependencies=[Depends(permission("promotions.manage"))],
)
def update_promotion(
    promotion_id: int, payload: PromotionInput, request: Request, db: DbSession
) -> Response:
    values = payload.model_dump()
    values.update(
        {
            "id": promotion_id,
            "code": payload.code.upper() if payload.code else None,
            "now": datetime.now(UTC),
        }
    )
    result = db.execute(
        text(
            "UPDATE promotions SET name=:name,code=:code,type=:type,value=:value,"
            "minimum_order=:minimum_order,starts_at=:starts_at,ends_at=:ends_at,"
            "is_active=:is_active,updated_at=:now WHERE id=:id"
        ),
        values,
    )
    if result.rowcount != 1:
        raise ApiError("Promotion not found.", "NOT_FOUND", 404)
    db.commit()
    row = (
        db.execute(text("SELECT * FROM promotions WHERE id=:id"), {"id": promotion_id})
        .mappings()
        .one()
    )
    return success(request, _promotion(dict(row), "en"), "Promotion updated.")


@router.delete(
    "/promotions/{promotion_id}",
    status_code=204,
    dependencies=[Depends(permission("promotions.manage"))],
)
def delete_promotion(promotion_id: int, db: DbSession) -> Response:
    db.execute(text("DELETE FROM promotions WHERE id=:id"), {"id": promotion_id})
    db.commit()
    return Response(status_code=204)


@router.get("/users", dependencies=[Depends(permission("users.view"))])
def users(request: Request, db: DbSession, page: Page = 1, per_page: PerPage = 25) -> Response:
    total = int(db.execute(text("SELECT COUNT(*) FROM users")).scalar_one())
    ids = (
        db.execute(
            text("SELECT id FROM users ORDER BY created_at DESC LIMIT :limit OFFSET :offset"),
            {"limit": per_page, "offset": (page - 1) * per_page},
        )
        .scalars()
        .all()
    )
    return success(
        request,
        serialize_users(db, [int(user_id) for user_id in ids]),
        meta=pagination_meta(page, per_page, total),
    )


@router.get("/roles", dependencies=[Depends(permission("users.view"))])
def roles(request: Request, db: DbSession) -> Response:
    rows = db.execute(text("SELECT * FROM roles ORDER BY name")).mappings().all()
    data = []
    for role in rows:
        permissions = (
            db.execute(
                text(
                    "SELECT p.id,p.name,p.label FROM permissions p JOIN permission_role pr ON pr.permission_id=p.id WHERE pr.role_id=:id ORDER BY p.name"
                ),
                {"id": role["id"]},
            )
            .mappings()
            .all()
        )
        data.append(
            {
                "id": int(role["id"]),
                "name": role["name"],
                "label": role["label"],
                "permissions": [dict(item) for item in permissions],
            }
        )
    return success(request, data)


@router.put("/users/{user_id}/roles", dependencies=[Depends(permission("users.manage_roles"))])
def update_roles(
    user_id: int, payload: RolesUpdateInput, request: Request, db: DbSession, actor: CurrentUser
) -> Response:
    if int(actor["id"]) == user_id and "admin" not in payload.roles:
        raise ApiError("You cannot remove your own administrator role.", "CANNOT_DEMOTE_SELF", 409)
    if get_settings().require_privileged_mfa and set(payload.roles) & {"admin", "manager"}:
        mfa_enabled_at = db.execute(
            text("SELECT mfa_enabled_at FROM users WHERE id=:user_id"), {"user_id": user_id}
        ).scalar_one_or_none()
        if mfa_enabled_at is None:
            raise ApiError(
                "The user must enable multi-factor authentication before receiving this role.",
                "MFA_ENROLLMENT_REQUIRED",
                409,
            )
    available_roles = db.execute(text("SELECT id,name FROM roles")).mappings().all()
    requested_roles = set(payload.roles)
    role_rows = [role for role in available_roles if role["name"] in requested_roles]
    if len(role_rows) != len(set(payload.roles)):
        raise ApiError("One or more roles are invalid.", "VALIDATION_ERROR", 422)
    db.execute(text("DELETE FROM role_user WHERE user_id=:id"), {"id": user_id})
    for role in role_rows:
        db.execute(
            text("INSERT INTO role_user(role_id,user_id) VALUES (:role_id,:user_id)"),
            {"role_id": role["id"], "user_id": user_id},
        )
    db.commit()
    return success(request, serialize_user(db, user_id), "Roles updated.")


@router.get("/conversations", dependencies=[Depends(permission("chat.view"))])
def conversations(
    request: Request, db: DbSession, page: Page = 1, per_page: PerPage = 25
) -> Response:
    total = int(db.execute(text("SELECT COUNT(*) FROM conversations")).scalar_one())
    rows = (
        db.execute(
            text(
                "SELECT c.*,customer.name customer_name,assignee.name assigned_name "
                "FROM conversations c LEFT JOIN users customer ON customer.id=c.customer_id "
                "LEFT JOIN users assignee ON assignee.id=c.assigned_to "
                "ORDER BY c.last_message_at DESC LIMIT :limit OFFSET :offset"
            ),
            {"limit": per_page, "offset": (page - 1) * per_page},
        )
        .mappings()
        .all()
    )
    return success(
        request,
        [conversation_dict(db, dict(row), include_messages=False) for row in rows],
        meta=pagination_meta(page, per_page, total),
    )


@router.get("/conversations/{conversation_id}", dependencies=[Depends(permission("chat.view"))])
def conversation(conversation_id: int, request: Request, db: DbSession) -> Response:
    row = (
        db.execute(text("SELECT * FROM conversations WHERE id=:id"), {"id": conversation_id})
        .mappings()
        .first()
    )
    if row is None:
        raise ApiError("Conversation not found.", "NOT_FOUND", 404)
    return success(request, conversation_dict(db, dict(row)))


@router.post("/conversations/{conversation_id}", dependencies=[Depends(permission("chat.reply"))])
def reply_conversation(
    conversation_id: int,
    payload: ChatReplyInput,
    request: Request,
    db: DbSession,
    user: CurrentUser,
) -> Response:
    now = datetime.now(UTC)
    db.execute(
        text(
            "INSERT INTO messages(conversation_id,sender_id,sender_type,body,created_at,updated_at) VALUES (:id,:user_id,'staff',:body,:now,:now)"
        ),
        {"id": conversation_id, "user_id": user["id"], "body": payload.message, "now": now},
    )
    db.execute(
        text(
            "UPDATE conversations SET assigned_to=COALESCE(assigned_to,:user_id),last_message_at=:now,updated_at=:now WHERE id=:id"
        ),
        {"user_id": user["id"], "now": now, "id": conversation_id},
    )
    db.commit()
    return conversation(conversation_id, request, db)


@router.get("/posts", dependencies=[Depends(permission("content.manage"))])
def posts(request: Request, db: DbSession, page: Page = 1, per_page: PerPage = 25) -> Response:
    total = int(
        db.execute(text("SELECT COUNT(*) FROM posts WHERE deleted_at IS NULL")).scalar_one()
    )
    rows = (
        db.execute(
            text(
                "SELECT p.*,u.name author_name FROM posts p LEFT JOIN users u ON u.id=p.author_id "
                "WHERE p.deleted_at IS NULL ORDER BY p.created_at DESC LIMIT :limit OFFSET :offset"
            ),
            {"limit": per_page, "offset": (page - 1) * per_page},
        )
        .mappings()
        .all()
    )
    locale = locale_from_header(request.headers.get("Accept-Language"))
    return success(
        request,
        [post_dict(db, dict(row), locale) for row in rows],
        meta=pagination_meta(page, per_page, total),
    )


@router.post("/posts", status_code=201, dependencies=[Depends(permission("content.manage"))])
def create_post(payload: PostInput, request: Request, db: DbSession, user: CurrentUser) -> Response:
    now = datetime.now(UTC)
    values = payload.model_dump()
    values.update(
        {
            "slug": payload.slug or slugify(payload.title),
            "cover_image": None if payload.cover_image is None else str(payload.cover_image),
            "author_id": user["id"],
            "now": now,
        }
    )
    result = db.execute(
        text(
            "INSERT INTO posts(author_id,title,slug,excerpt,content,cover_image,status,published_at,created_at,updated_at) VALUES (:author_id,:title,:slug,:excerpt,:content,:cover_image,:status,:published_at,:now,:now) RETURNING id"
        ),
        values,
    )
    post_id = int(result.scalar_one())
    db.commit()
    row = db.execute(text("SELECT * FROM posts WHERE id=:id"), {"id": post_id}).mappings().one()
    return success(request, post_dict(db, dict(row), "en"), "Post created.", 201)


@router.put("/posts/{post_id}", dependencies=[Depends(permission("content.manage"))])
def update_post(post_id: int, payload: PostInput, request: Request, db: DbSession) -> Response:
    values = payload.model_dump()
    values.update(
        {
            "id": post_id,
            "slug": payload.slug or slugify(payload.title),
            "cover_image": None if payload.cover_image is None else str(payload.cover_image),
            "now": datetime.now(UTC),
        }
    )
    result = db.execute(
        text(
            "UPDATE posts SET title=:title,slug=:slug,excerpt=:excerpt,content=:content,"
            "cover_image=:cover_image,status=:status,published_at=:published_at,"
            "updated_at=:now WHERE id=:id AND deleted_at IS NULL"
        ),
        values,
    )
    if result.rowcount != 1:
        raise ApiError("Post not found.", "NOT_FOUND", 404)
    db.commit()
    row = db.execute(text("SELECT * FROM posts WHERE id=:id"), {"id": post_id}).mappings().one()
    return success(request, post_dict(db, dict(row), "en"), "Post updated.")


@router.delete(
    "/posts/{post_id}", status_code=204, dependencies=[Depends(permission("content.manage"))]
)
def delete_post(post_id: int, db: DbSession) -> Response:
    db.execute(
        text("UPDATE posts SET deleted_at=:now WHERE id=:id"),
        {"now": datetime.now(UTC), "id": post_id},
    )
    db.commit()
    return Response(status_code=204)


@router.get("/contacts", dependencies=[Depends(permission("contacts.view"))])
def contacts(request: Request, db: DbSession, page: Page = 1, per_page: PerPage = 25) -> Response:
    total = int(db.execute(text("SELECT COUNT(*) FROM contact_messages")).scalar_one())
    rows = (
        db.execute(
            text(
                "SELECT * FROM contact_messages ORDER BY created_at DESC "
                "LIMIT :limit OFFSET :offset"
            ),
            {"limit": per_page, "offset": (page - 1) * per_page},
        )
        .mappings()
        .all()
    )
    return success(
        request,
        [{**dict(row), "id": int(row["id"]), "created_at": iso(row["created_at"])} for row in rows],
        meta=pagination_meta(page, per_page, total),
    )


@router.patch("/contacts/{contact_id}", dependencies=[Depends(permission("contacts.manage"))])
def update_contact(
    contact_id: int, payload: ContactStatusInput, request: Request, db: DbSession
) -> Response:
    db.execute(
        text("UPDATE contact_messages SET status=:status,updated_at=:now WHERE id=:id"),
        {"status": payload.status, "now": datetime.now(UTC), "id": contact_id},
    )
    db.commit()
    row = (
        db.execute(text("SELECT * FROM contact_messages WHERE id=:id"), {"id": contact_id})
        .mappings()
        .first()
    )
    if row is None:
        raise ApiError("Contact message not found.", "NOT_FOUND", 404)
    data = {**dict(row), "id": int(row["id"]), "created_at": iso(row["created_at"])}
    return success(request, data, "Contact status updated.")
