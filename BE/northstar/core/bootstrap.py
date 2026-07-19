from datetime import UTC, datetime

from sqlalchemy import text

from northstar.core.database import SessionLocal

PERMISSIONS = {
    "dashboard.view": "View dashboard",
    "products.view": "View products",
    "products.manage": "Manage products",
    "orders.view": "View orders",
    "orders.manage": "Manage orders",
    "promotions.view": "View promotions",
    "promotions.manage": "Manage promotions",
    "users.view": "View users and roles",
    "users.manage_roles": "Assign user roles",
    "chat.view": "View conversations",
    "chat.reply": "Reply to conversations",
    "content.manage": "Manage posts and content",
    "contacts.view": "View contact messages",
}

ROLE_PERMISSIONS = {
    "admin": list(PERMISSIONS),
    "manager": [name for name in PERMISSIONS if name not in {"users.view", "users.manage_roles"}],
    "staff": [
        "dashboard.view",
        "products.view",
        "orders.view",
        "orders.manage",
        "chat.view",
        "chat.reply",
    ],
    "customer": [],
}


def bootstrap_reference_data() -> None:
    now = datetime.now(UTC)
    with SessionLocal.begin() as db:
        for name, label in PERMISSIONS.items():
            db.execute(
                text(
                    "INSERT INTO permissions(name,label,created_at,updated_at) VALUES "
                    "(:name,:label,:now,:now) ON CONFLICT(name) DO UPDATE SET label=:label"
                ),
                {"name": name, "label": label, "now": now},
            )
        labels = {
            "admin": "Administrator",
            "manager": "Store manager",
            "staff": "Sales staff",
            "customer": "Customer",
        }
        for role_name, permission_names in ROLE_PERMISSIONS.items():
            db.execute(
                text(
                    "INSERT INTO roles(name,label,created_at,updated_at) VALUES "
                    "(:name,:label,:now,:now) ON CONFLICT(name) DO UPDATE SET label=:label"
                ),
                {"name": role_name, "label": labels[role_name], "now": now},
            )
            role_id = db.execute(
                text("SELECT id FROM roles WHERE name=:name"), {"name": role_name}
            ).scalar_one()
            db.execute(text("DELETE FROM permission_role WHERE role_id=:id"), {"id": role_id})
            for permission_name in permission_names:
                permission_id = db.execute(
                    text("SELECT id FROM permissions WHERE name=:name"),
                    {"name": permission_name},
                ).scalar_one()
                db.execute(
                    text(
                        "INSERT INTO permission_role(permission_id,role_id) "
                        "VALUES (:permission_id,:role_id) ON CONFLICT DO NOTHING"
                    ),
                    {"permission_id": permission_id, "role_id": role_id},
                )
