import hashlib
from datetime import UTC, datetime

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text

from northstar.core.database import SessionLocal, _hash_legacy_conversation_tokens
from northstar.main import app

ORIGIN = "http://localhost:5173"


def csrf_headers(client: TestClient) -> dict[str, str]:
    response = client.get("/sanctum/csrf-cookie")
    assert response.status_code == 204
    return {"Origin": ORIGIN, "X-XSRF-TOKEN": client.cookies["XSRF-TOKEN"]}


def register(client: TestClient, email: str) -> None:
    response = client.post(
        "/api/v1/auth/register",
        headers=csrf_headers(client),
        json={
            "name": "Scale Tester",
            "email": email,
            "password": "SecurePassword123!",
            "password_confirmation": "SecurePassword123!",
        },
    )
    assert response.status_code == 201


def test_legacy_chat_tokens_are_hashed_by_data_migration() -> None:
    legacy_token = "a" * 64
    already_hashed_token = hashlib.sha256(b"current-token").hexdigest()
    isolated_engine = create_engine("sqlite://")
    with isolated_engine.begin() as connection:
        connection.exec_driver_sql(
            "CREATE TABLE conversations (id INTEGER PRIMARY KEY, public_token VARCHAR(64))"
        )
        connection.execute(
            text(
                "INSERT INTO conversations(id,public_token) VALUES "
                "(1,:legacy_token),(2,:already_hashed_token)"
            ),
            {
                "legacy_token": legacy_token,
                "already_hashed_token": already_hashed_token,
            },
        )
        _hash_legacy_conversation_tokens(connection)
        stored_tokens = (
            connection.execute(text("SELECT id,public_token FROM conversations ORDER BY id"))
            .mappings()
            .all()
        )

    assert stored_tokens[0]["public_token"] == hashlib.sha256(legacy_token.encode()).hexdigest()
    assert (
        stored_tokens[1]["public_token"]
        == hashlib.sha256(already_hashed_token.encode()).hexdigest()
    )


def test_chat_ownership_pagination_sessions_and_url_validation() -> None:
    with TestClient(app) as client:
        register(client, "chat-owner@example.com")
        conversation = client.post(
            "/api/v1/storefront/chat",
            headers=csrf_headers(client),
            json={"message": "Private customer conversation"},
        )
        assert conversation.status_code == 201
        token = conversation.json()["data"]["token"]
        assert isinstance(token, str)

        headers = csrf_headers(client)
        assert client.post("/api/v1/auth/logout", headers=headers).status_code == 200
        register(client, "different-customer@example.com")
        assert client.get(f"/api/v1/storefront/chat/{token}").status_code == 404

        user_id = int(client.get("/api/v1/auth/me").json()["data"]["id"])
        now = datetime.now(UTC)
        with SessionLocal.begin() as db:
            db.execute(
                text(
                    "INSERT INTO roles(name,label,created_at,updated_at) "
                    "VALUES ('contact-auditor','Contact auditor',:now,:now) "
                    "ON CONFLICT(name) DO NOTHING"
                ),
                {"now": now},
            )
            auditor_role_id = db.execute(
                text("SELECT id FROM roles WHERE name='contact-auditor'")
            ).scalar_one()
            contacts_view_id = db.execute(
                text("SELECT id FROM permissions WHERE name='contacts.view'")
            ).scalar_one()
            db.execute(text("DELETE FROM role_user WHERE user_id=:user_id"), {"user_id": user_id})
            db.execute(
                text(
                    "INSERT INTO role_user(role_id,user_id) VALUES (:role_id,:user_id) "
                    "ON CONFLICT DO NOTHING"
                ),
                {"role_id": auditor_role_id, "user_id": user_id},
            )
            db.execute(
                text(
                    "INSERT INTO permission_role(permission_id,role_id) "
                    "VALUES (:permission_id,:role_id) ON CONFLICT DO NOTHING"
                ),
                {"permission_id": contacts_view_id, "role_id": auditor_role_id},
            )
            first_contact_id = 0
            for index in range(30):
                result = db.execute(
                    text(
                        "INSERT INTO contact_messages(name,email,subject,message,status,created_at,updated_at) "
                        "VALUES (:name,:email,:subject,:message,'new',:now,:now) RETURNING id"
                    ),
                    {
                        "name": f"Customer {index}",
                        "email": f"customer-{index}@example.com",
                        "subject": f"Question {index}",
                        "message": "Pagination test",
                        "now": now,
                    },
                )
                contact_id = int(result.scalar_one())
                if index == 0:
                    first_contact_id = contact_id

        page = client.get("/api/v1/admin/contacts", params={"page": 2, "per_page": 10})
        assert page.status_code == 200
        assert len(page.json()["data"]) == 10
        assert page.json()["meta"]["pagination"]["current_page"] == 2
        assert page.json()["meta"]["pagination"]["total"] >= 30

        forbidden_update = client.patch(
            f"/api/v1/admin/contacts/{first_contact_id}",
            headers=csrf_headers(client),
            json={"status": "resolved"},
        )
        assert forbidden_update.status_code == 403

        with SessionLocal.begin() as db:
            admin_role_id = db.execute(text("SELECT id FROM roles WHERE name='admin'")).scalar_one()
            db.execute(text("DELETE FROM role_user WHERE user_id=:user_id"), {"user_id": user_id})
            db.execute(
                text("INSERT INTO role_user(role_id,user_id) VALUES (:role_id,:user_id)"),
                {"role_id": admin_role_id, "user_id": user_id},
            )

        allowed_update = client.patch(
            f"/api/v1/admin/contacts/{first_contact_id}",
            headers=csrf_headers(client),
            json={"status": "resolved"},
        )
        assert allowed_update.status_code == 200

        invalid_image = client.post(
            "/api/v1/admin/products",
            headers=csrf_headers(client),
            json={
                "name": "Unsafe image",
                "sku": "UNSAFE-IMAGE-1",
                "price": 10,
                "stock": 1,
                "images": ["file:///etc/passwd"],
                "status": "draft",
            },
        )
        assert invalid_image.status_code == 422

        sessions = client.get("/api/v1/auth/sessions")
        assert sessions.status_code == 200
        current = next(item for item in sessions.json()["data"] if item["current"])
        revoked = client.delete(
            f"/api/v1/auth/sessions/{current['id']}",
            headers=csrf_headers(client),
        )
        assert revoked.status_code == 200
        assert client.get("/api/v1/auth/me").status_code == 401
