import re

from fastapi.testclient import TestClient

from northstar.main import app


def csrf_headers(client: TestClient) -> dict[str, str]:
    response = client.get("/sanctum/csrf-cookie")
    assert response.status_code == 204
    return {
        "Origin": "http://localhost:5173",
        "X-XSRF-TOKEN": client.cookies["XSRF-TOKEN"],
    }


def test_security_and_authentication_contract() -> None:
    with TestClient(app) as client:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json()["data"]["status"] == "ok"
        assert health.headers["X-Content-Type-Options"] == "nosniff"

        blocked = client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@example.com", "password": "invalid"},
        )
        assert blocked.status_code == 403
        assert blocked.json()["error"]["code"] == "UNTRUSTED_ORIGIN"

        headers = csrf_headers(client)
        registration = client.post(
            "/api/v1/auth/register",
            headers=headers,
            json={
                "name": "Test Customer",
                "email": "customer@example.com",
                "password": "SecurePassword123!",
                "password_confirmation": "SecurePassword123!",
            },
        )
        assert registration.status_code == 201
        assert registration.json()["data"]["user"]["roles"] == ["customer"]

        me = client.get("/api/v1/auth/me")
        assert me.status_code == 200
        assert me.json()["data"]["email"] == "customer@example.com"

        forbidden = client.get("/api/v1/admin/dashboard")
        assert forbidden.status_code == 403
        assert forbidden.json()["error"]["code"] == "FORBIDDEN"

        logout = client.post("/api/v1/auth/logout", headers=headers)
        assert logout.status_code == 200
        assert client.get("/api/v1/auth/me").status_code == 401


def test_local_swagger_docs_use_nonce_scoped_csp() -> None:
    with TestClient(app) as client:
        docs = client.get("/docs")
        assert docs.status_code == 200

        nonce_match = re.search(r'<script nonce="([^"]+)">', docs.text)
        assert nonce_match is not None

        policy = docs.headers["Content-Security-Policy"]
        assert "default-src 'none'" in policy
        assert f"'nonce-{nonce_match.group(1)}'" in policy
        assert "script-src" in policy
        assert "style-src https://cdn.jsdelivr.net" in policy
        assert "img-src https://fastapi.tiangolo.com data:" in policy
        assert "connect-src 'self'" in policy
        assert "'unsafe-inline'" not in policy

        health = client.get("/health")
        assert health.headers["Content-Security-Policy"] == (
            "default-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'"
        )


def test_validation_and_localization_contract() -> None:
    with TestClient(app) as client:
        invalid = client.post(
            "/api/v1/storefront/contact",
            headers=csrf_headers(client),
            json={"name": "", "email": "bad", "subject": "", "message": ""},
        )
        assert invalid.status_code == 422
        assert invalid.json()["error"]["code"] == "VALIDATION_ERROR"
        assert "email" in invalid.json()["errors"]

        storefront = client.get(
            "/api/v1/storefront/home", headers={"Accept-Language": "ja-JP,ja;q=0.9"}
        )
        assert storefront.status_code == 200
        assert storefront.json()["data"]["locale"] == "ja"
