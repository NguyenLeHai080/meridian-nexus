from datetime import UTC, datetime

from fastapi import APIRouter, Query, Request, Response
from sqlalchemy import text

from northstar.core.auth import DbSession
from northstar.core.database import json_value
from northstar.core.http import ApiError, limiter, pagination_meta, success
from northstar.core.network import client_ip
from northstar.core.security import hash_context
from northstar.core.serialization import (
    SUPPORTED_LOCALES,
    iso,
    locale_from_header,
    post_dict,
    product_dict,
    translated,
)
from northstar.schemas import ContactInput

router = APIRouter(prefix="/api/v1/storefront", tags=["storefront"])


def _locale(request: Request) -> str:
    return locale_from_header(request.headers.get("Accept-Language"))


def _category(db: DbSession, row: dict[str, object], locale: str) -> dict[str, object]:
    count = db.execute(
        text("SELECT COUNT(*) FROM products WHERE category_id=:id AND deleted_at IS NULL"),
        {"id": row["id"]},
    ).scalar_one()
    return {
        "id": int(row["id"]),
        "name": translated(row, "name", locale),
        "slug": row["slug"],
        "description": translated(row, "description", locale),
        "products_count": int(count),
        "is_active": bool(row["is_active"]),
    }


def _promotion(row: dict[str, object], locale: str) -> dict[str, object]:
    return {
        "id": int(row["id"]),
        "name": translated(row, "name", locale),
        "code": row.get("code"),
        "type": row["type"],
        "value": str(row["value"]),
        "minimum_order": str(row["minimum_order"]),
        "ends_at": iso(row.get("ends_at")),
        "is_active": bool(row["is_active"]),
    }


@router.get("/home")
def home(request: Request, db: DbSession) -> Response:
    locale = _locale(request)
    setting = db.execute(
        text("SELECT value FROM site_settings WHERE key='storefront' LIMIT 1")
    ).scalar_one_or_none()
    settings = json_value(setting, {})
    site = {}
    if isinstance(settings, dict):
        locales = settings.get("locales", {})
        if isinstance(locales, dict):
            site = locales.get(locale) or locales.get("en") or {}
    products = (
        db.execute(
            text(
                "SELECT * FROM products WHERE status='published' AND deleted_at IS NULL "
                "AND is_featured=TRUE ORDER BY published_at DESC LIMIT 6"
            )
        )
        .mappings()
        .all()
    )
    categories = (
        db.execute(text("SELECT * FROM categories WHERE is_active=TRUE ORDER BY name"))
        .mappings()
        .all()
    )
    now = datetime.now(UTC)
    promotions = (
        db.execute(
            text(
                "SELECT * FROM promotions WHERE is_active=TRUE "
                "AND (starts_at IS NULL OR starts_at<=:now) AND (ends_at IS NULL OR ends_at>=:now) "
                "ORDER BY ends_at LIMIT 3"
            ),
            {"now": now},
        )
        .mappings()
        .all()
    )
    posts = (
        db.execute(
            text(
                "SELECT * FROM posts WHERE status='published' AND deleted_at IS NULL "
                "ORDER BY published_at DESC LIMIT 3"
            )
        )
        .mappings()
        .all()
    )
    labels = {"en": "English", "vi": "Tiếng Việt", "ja": "日本語", "ko": "한국어"}
    data = {
        "locale": locale,
        "supported_locales": [{"value": code, "label": labels[code]} for code in SUPPORTED_LOCALES],
        "site": site,
        "featured_products": [product_dict(db, dict(row), locale) for row in products],
        "categories": [_category(db, dict(row), locale) for row in categories],
        "promotions": [_promotion(dict(row), locale) for row in promotions],
        "latest_posts": [post_dict(db, dict(row), locale) for row in posts],
    }
    return success(request, data)


@router.get("/products")
def products(
    request: Request,
    db: DbSession,
    search: str | None = Query(default=None, max_length=120),
    category: str | None = Query(default=None, max_length=140),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=12, ge=1, le=48),
) -> Response:
    params: dict[str, object] = {
        "search": None if not search else f"%{search}%",
        "category": category or None,
    }
    total = db.execute(
        text(
            "SELECT COUNT(*) FROM products p LEFT JOIN categories c ON c.id=p.category_id "
            "WHERE p.status='published' AND p.deleted_at IS NULL "
            "AND (:search IS NULL OR p.name LIKE :search OR p.sku LIKE :search) "
            "AND (:category IS NULL OR c.slug=:category)"
        ),
        params,
    ).scalar_one()
    params.update({"limit": per_page, "offset": (page - 1) * per_page})
    rows = (
        db.execute(
            text(
                "SELECT p.* FROM products p LEFT JOIN categories c ON c.id=p.category_id "
                "WHERE p.status='published' AND p.deleted_at IS NULL "
                "AND (:search IS NULL OR p.name LIKE :search OR p.sku LIKE :search) "
                "AND (:category IS NULL OR c.slug=:category) "
                "ORDER BY p.published_at DESC LIMIT :limit OFFSET :offset"
            ),
            params,
        )
        .mappings()
        .all()
    )
    data = [product_dict(db, dict(row), _locale(request)) for row in rows]
    return success(request, data, meta=pagination_meta(page, per_page, int(total)))


@router.get("/products/{slug}")
def product(slug: str, request: Request, db: DbSession) -> Response:
    row = (
        db.execute(
            text(
                "SELECT * FROM products WHERE slug=:slug AND status='published' "
                "AND deleted_at IS NULL LIMIT 1"
            ),
            {"slug": slug},
        )
        .mappings()
        .first()
    )
    if row is None:
        raise ApiError("Product not found.", "NOT_FOUND", 404)
    return success(request, product_dict(db, dict(row), _locale(request)))


@router.get("/posts")
def posts(request: Request, db: DbSession) -> Response:
    rows = (
        db.execute(
            text(
                "SELECT * FROM posts WHERE status='published' AND deleted_at IS NULL "
                "ORDER BY published_at DESC LIMIT 30"
            )
        )
        .mappings()
        .all()
    )
    return success(request, [post_dict(db, dict(row), _locale(request)) for row in rows])


@router.get("/posts/{slug}")
def post(slug: str, request: Request, db: DbSession) -> Response:
    row = (
        db.execute(
            text(
                "SELECT * FROM posts WHERE slug=:slug AND status='published' "
                "AND deleted_at IS NULL LIMIT 1"
            ),
            {"slug": slug},
        )
        .mappings()
        .first()
    )
    if row is None:
        raise ApiError("Post not found.", "NOT_FOUND", 404)
    return success(request, post_dict(db, dict(row), _locale(request)))


@router.post("/contact", status_code=201)
def contact(payload: ContactInput, request: Request, db: DbSession) -> Response:
    email = str(payload.email).lower()
    limiter.hit(f"contact-ip:{client_ip(request)}", 10, 3600)
    limiter.hit(f"contact-email:{hash_context(email)}", 5, 3600)
    result = db.execute(
        text(
            "INSERT INTO contact_messages(name,email,phone,subject,message,status,created_at,updated_at) "
            "VALUES (:name,:email,:phone,:subject,:message,'new',:now,:now) RETURNING id"
        ),
        {**payload.model_dump(), "now": datetime.now(UTC)},
    )
    contact_id = int(result.scalar_one())
    db.commit()
    return success(request, {"id": contact_id}, "Your message has been received.", 201)
