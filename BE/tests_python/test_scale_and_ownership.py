from datetime import UTC, datetime

from fastapi.testclient import TestClient
from sqlalchemy import text

from northstar.core.database import SessionLocal
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
            admin_role_id = db.execute(text("SELECT id FROM roles WHERE name='admin'")).scalar_one()
            db.execute(
                text(
                    "INSERT INTO role_user(role_id,user_id) VALUES (:role_id,:user_id) "
                    "ON CONFLICT DO NOTHING"
                ),
                {"role_id": admin_role_id, "user_id": user_id},
            )
            for index in range(30):
                db.execute(
                    text(
                        "INSERT INTO contact_messages(name,email,subject,message,status,created_at,updated_at) "
                        "VALUES (:name,:email,:subject,:message,'new',:now,:now)"
                    ),
                    {
                        "name": f"Customer {index}",
                        "email": f"customer-{index}@example.com",
                        "subject": f"Question {index}",
                        "message": "Pagination test",
                        "now": now,
                    },
                )

        page = client.get("/api/v1/admin/contacts", params={"page": 2, "per_page": 10})
        assert page.status_code == 200
        assert len(page.json()["data"]) == 10
        assert page.json()["meta"]["pagination"]["current_page"] == 2
        assert page.json()["meta"]["pagination"]["total"] >= 30

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
