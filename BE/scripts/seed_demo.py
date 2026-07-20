import json
from datetime import UTC, datetime, timedelta

from sqlalchemy import text

from northstar.core.bootstrap import bootstrap_reference_data
from northstar.core.config import get_settings
from northstar.core.database import SessionLocal, initialize_database
from northstar.core.security import password_hash

ADMIN = ("admin@meridian-demo.com", "DemoAdmin123!", "Meridian Admin", "admin")
CUSTOMER = ("customer@meridian-demo.com", "DemoCustomer123!", "Demo Customer", "customer")
CATEGORIES = [
    ("Lighting", "lighting", "Warm lighting for quiet spaces."),
    ("Living", "living", "Considered objects for daily rituals."),
    ("Workspace", "workspace", "Tools for clear and focused work."),
    ("Accessories", "accessories", "Useful details designed to last."),
]
PRODUCTS = [
    ("lighting", "Arc Table Lamp", "arc-table-lamp", "LGT-001", 129, 109, 18, 1),
    ("lighting", "Halo Floor Light", "halo-floor-light", "LGT-002", 219, None, 9, 1),
    ("living", "Luna Side Table", "luna-side-table", "LIV-001", 189, 159, 7, 1),
    ("living", "Still Ceramic Vase", "still-ceramic-vase", "LIV-002", 74, None, 24, 1),
    ("workspace", "Contour Desk Tray", "contour-desk-tray", "WRK-001", 42, None, 35, 1),
    ("workspace", "Oak Monitor Stand", "oak-monitor-stand", "WRK-002", 115, None, 11, 1),
    ("accessories", "Day Carry Pouch", "day-carry-pouch", "ACC-001", 39, None, 40, 0),
    ("accessories", "Everyday Bottle", "everyday-bottle", "ACC-002", 36, 30, 28, 1),
]


def upsert(db, table: str, key: str, value: object, fields: dict[str, object]) -> int:
    row_id = db.execute(
        text(f"SELECT id FROM {table} WHERE {key}=:value LIMIT 1"), {"value": value}
    ).scalar_one_or_none()
    values = {key: value, **fields}
    if row_id is None:
        columns = ",".join(values)
        parameters = ",".join(f":{column}" for column in values)
        return int(
            db.execute(
                text(f"INSERT INTO {table} ({columns}) VALUES ({parameters}) RETURNING id"),
                values,
            ).scalar_one()
        )
    values["id"] = row_id
    updates = ",".join(f"{column}=:{column}" for column in fields)
    db.execute(text(f"UPDATE {table} SET {updates} WHERE id=:id"), values)
    return int(row_id)


def seed_user(db, account: tuple[str, str, str, str], now: datetime) -> int:
    email, password, name, role = account
    user_id = upsert(
        db,
        "users",
        "email",
        email,
        {
            "name": name,
            "password": password_hash.hash(password),
            "email_verified_at": now,
            "created_at": now,
            "updated_at": now,
        },
    )
    role_id = db.execute(text("SELECT id FROM roles WHERE name=:name"), {"name": role}).scalar_one()
    db.execute(text("DELETE FROM role_user WHERE user_id=:id"), {"id": user_id})
    db.execute(
        text("INSERT INTO role_user(role_id,user_id) VALUES (:role_id,:user_id)"),
        {"role_id": role_id, "user_id": user_id},
    )
    return user_id


def seed_catalog(db, now: datetime) -> dict[str, int]:
    categories = {}
    for name, slug, description in CATEGORIES:
        categories[slug] = upsert(
            db,
            "categories",
            "slug",
            slug,
            {
                "name": name,
                "description": description,
                "translations": "{}",
                "is_active": True,
                "created_at": now,
                "updated_at": now,
            },
        )
    product_ids = {}
    for category, name, slug, sku, price, sale, stock, featured in PRODUCTS:
        product_ids[slug] = upsert(
            db,
            "products",
            "slug",
            slug,
            {
                "category_id": categories[category],
                "name": name,
                "sku": sku,
                "excerpt": f"A considered {name.lower()} for everyday use.",
                "description": f"{name} combines durable materials and useful proportions.",
                "translations": "{}",
                "price": price,
                "sale_price": sale,
                "stock": stock,
                "images": json.dumps([f"https://picsum.photos/seed/{slug}/900/1100"]),
                "status": "published",
                "is_featured": featured,
                "published_at": now - timedelta(days=2),
                "created_at": now,
                "updated_at": now,
                "deleted_at": None,
            },
        )
    return product_ids


def seed_content(db, admin_id: int, now: datetime) -> None:
    for title, slug, excerpt, content, vi_title, vi_excerpt in (
        (
            "WordPress or React: Which One Fits Your Business?",
            "choosing-fewer-better-objects",
            "A practical framework for choosing the right website platform.",
            "Compare delivery speed, content management, customization, maintenance and long-term cost before choosing WordPress or React.",
            "WordPress hay React: Giải pháp nào phù hợp với doanh nghiệp?",
            "Khung đánh giá thực tế giúp bạn lựa chọn nền tảng website phù hợp.",
        ),
        (
            "Five Workflows You Can Automate Today",
            "light-for-focus-and-rest",
            "Reduce repetitive work with practical automation ideas.",
            "Start with lead collection, reporting, content publishing, customer follow-up and structured data processing.",
            "5 quy trình bạn có thể tự động hóa ngay hôm nay",
            "Giảm công việc lặp lại bằng những ý tưởng automation dễ triển khai.",
        ),
        (
            "Using ChatGPT and Gemini for Better Content",
            "a-calmer-working-surface",
            "Build a reliable AI-assisted workflow for research and content creation.",
            "Use AI for structured research, outlines, first drafts, visual concepts and quality checks while keeping human review in the process.",
            "Ứng dụng ChatGPT và Gemini để tạo nội dung tốt hơn",
            "Xây dựng quy trình nghiên cứu và sáng tạo nội dung có AI hỗ trợ.",
        ),
    ):
        upsert(
            db,
            "posts",
            "slug",
            slug,
            {
                "author_id": admin_id,
                "title": title,
                "excerpt": excerpt,
                "content": content,
                "translations": json.dumps(
                    {
                        "vi": {
                            "title": vi_title,
                            "excerpt": vi_excerpt,
                            "content": vi_excerpt,
                        }
                    }
                ),
                "cover_image": f"https://picsum.photos/seed/{slug}/1200/800",
                "status": "published",
                "published_at": now - timedelta(days=5),
                "created_at": now,
                "updated_at": now,
                "deleted_at": None,
            },
        )
    for name, code, kind, value, minimum in (
        ("Welcome offer", "WELCOME10", "percent", 10, 50),
        ("Studio opening", "STUDIO20", "fixed", 20, 120),
    ):
        upsert(
            db,
            "promotions",
            "code",
            code,
            {
                "name": name,
                "translations": "{}",
                "type": kind,
                "value": value,
                "minimum_order": minimum,
                "starts_at": now - timedelta(days=1),
                "ends_at": now + timedelta(days=60),
                "is_active": True,
                "created_at": now,
                "updated_at": now,
            },
        )


def seed_site(db, now: datetime) -> None:
    site = {
        "locales": {
            "en": {
                "brand": {"name": "Meridian Nexus", "mark": "MN"},
                "announcement": "Web Development · Automation · AI Creative Solutions",
                "navigation": [
                    {"path": "/", "label": "Home"},
                    {"path": "/products", "label": "Digital Products"},
                    {"path": "/journal", "label": "Insights"},
                    {"path": "/about", "label": "About"},
                ],
                "contact": {"email": "hello@meridian.local"},
                "footer": {
                    "tagline": "Websites, automation and AI solutions built for real growth.",
                    "newsletter_title": "Digital Insights",
                    "newsletter_text": "Practical notes about web development, automation and AI.",
                    "legal": "Meridian Nexus. All rights reserved.",
                    "note": "Built for modern digital businesses.",
                },
                "home_hero": {
                    "eyebrow": "Digital Studio / 2026",
                    "title": "Technology for",
                    "accent": "real business growth.",
                    "description": "Professional websites, automation tools and practical AI solutions.",
                    "image": "https://picsum.photos/seed/meridian-hero/1200/1400",
                    "image_alt": "Meridian Nexus digital studio",
                    "cta_label": "Explore our services",
                    "cta_path": "/products",
                },
            }
        }
    }
    upsert(
        db,
        "site_settings",
        "key",
        "storefront",
        {"value": json.dumps(site), "created_at": now, "updated_at": now},
    )


def seed_order(db, customer_id: int, products: dict[str, int], now: datetime) -> None:
    order_id = upsert(
        db,
        "orders",
        "number",
        "MN-DEMO-1001",
        {
            "user_id": customer_id,
            "customer_name": "Demo Customer",
            "customer_email": CUSTOMER[0],
            "customer_phone": "+84 900 000 001",
            "shipping_address": json.dumps(
                {"line": "12 Nguyen Hue", "city": "Ho Chi Minh City", "country": "Vietnam"}
            ),
            "status": "completed",
            "payment_status": "paid",
            "subtotal": 171,
            "discount": 17.1,
            "shipping_fee": 0,
            "total": 153.9,
            "notes": "Demo order",
            "created_at": now - timedelta(days=10),
            "updated_at": now - timedelta(days=8),
        },
    )
    db.execute(text("DELETE FROM order_items WHERE order_id=:id"), {"id": order_id})
    for slug, name, sku, price in (
        ("arc-table-lamp", "Arc Table Lamp", "LGT-001", 129),
        ("contour-desk-tray", "Contour Desk Tray", "WRK-001", 42),
    ):
        db.execute(
            text(
                "INSERT INTO order_items(order_id,product_id,product_name,sku,unit_price,quantity,total,created_at,updated_at) VALUES (:order_id,:product_id,:name,:sku,:price,1,:price,:now,:now)"
            ),
            {
                "order_id": order_id,
                "product_id": products[slug],
                "name": name,
                "sku": sku,
                "price": price,
                "now": now,
            },
        )


def main() -> None:
    if get_settings().app_env.lower() == "production":
        raise RuntimeError("Demo data cannot be seeded in production.")
    initialize_database()
    bootstrap_reference_data()
    now = datetime.now(UTC)
    with SessionLocal.begin() as db:
        db.execute(
            text("UPDATE users SET email=:new WHERE email=:old"),
            {"new": ADMIN[0], "old": "admin@meridian.local"},
        )
        db.execute(
            text("UPDATE users SET email=:new WHERE email=:old"),
            {"new": CUSTOMER[0], "old": "customer@meridian.local"},
        )
        admin_id = seed_user(db, ADMIN, now)
        customer_id = seed_user(db, CUSTOMER, now)
        products = seed_catalog(db, now)
        seed_content(db, admin_id, now)
        seed_site(db, now)
        seed_order(db, customer_id, products, now)
    print("Demo data seeded successfully.")
    print(f"Admin: {ADMIN[0]} / {ADMIN[1]}")
    print(f"Customer: {CUSTOMER[0]} / {CUSTOMER[1]}")


if __name__ == "__main__":
    main()
