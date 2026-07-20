import json
from datetime import UTC, datetime

from sqlalchemy import text
from sqlalchemy.orm import Session

from northstar.core.http import ApiError
from northstar.core.serialization import slugify
from northstar.schemas import ProductInput


def select_options(values: list[str]) -> list[dict[str, str]]:
    return [{"value": value, "label": value.replace("_", " ").title()} for value in values]


def save_product(db: Session, payload: ProductInput, product_id: int | None = None) -> int:
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
