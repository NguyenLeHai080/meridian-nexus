from fastapi.testclient import TestClient
from pydantic import ValidationError

from northstar.core.config import Settings
from northstar.main import app

ORIGIN = "http://localhost:5173"


def csrf_headers(client: TestClient) -> dict[str, str]:
    response = client.get("/sanctum/csrf-cookie")
    assert response.status_code == 204
    return {"Origin": ORIGIN, "X-XSRF-TOKEN": client.cookies["XSRF-TOKEN"]}


def register_customer(client: TestClient, email: str) -> None:
    response = client.post(
        "/api/v1/auth/register",
        headers=csrf_headers(client),
        json={
            "name": "Security Tester",
            "email": email,
            "password": "SecurePassword123!",
            "password_confirmation": "SecurePassword123!",
        },
    )
    assert response.status_code == 201


def test_host_csrf_rbac_and_session_tampering_are_rejected() -> None:
    with TestClient(app) as client:
        assert client.get("/health", headers={"Host": "attacker.example"}).status_code == 400

        missing_csrf = client.post(
            "/api/v1/auth/login",
            headers={"Origin": ORIGIN},
            json={"email": "nobody@example.com", "password": "invalid"},
        )
        assert missing_csrf.status_code == 419

        register_customer(client, "security-customer@example.com")
        forbidden = client.get("/api/v1/admin/users")
        assert forbidden.status_code == 403
        assert forbidden.json()["error"]["code"] == "FORBIDDEN"

        client.cookies.set("northstar_session", "tampered-session-token")
        assert client.get("/api/v1/auth/me").status_code == 401


def test_injection_xss_and_path_traversal_payloads_do_not_execute() -> None:
    with TestClient(app) as client:
        injection = client.get(
            "/api/v1/storefront/products",
            params={"search": "%' OR 1=1; DROP TABLE users; --"},
        )
        assert injection.status_code == 200

        payload = "<img src=x onerror=alert(document.domain)>"
        chat = client.post(
            "/api/v1/storefront/chat",
            headers=csrf_headers(client),
            json={"name": "Tester", "email": "xss@example.com", "message": payload},
        )
        assert chat.status_code == 201
        assert chat.json()["data"]["messages"][0]["body"] == payload
        assert "default-src 'none'" in chat.headers["Content-Security-Policy"]

        traversal = client.get("/api/v1/storefront/posts/..%2F..%2F.env")
        assert traversal.status_code in {404, 422}


def test_request_size_limit_and_login_throttling() -> None:
    with TestClient(app) as client:
        oversized = client.post(
            "/api/v1/storefront/contact",
            headers=csrf_headers(client),
            json={
                "name": "Tester",
                "email": "large@example.com",
                "subject": "Large payload",
                "message": "x" * 1_100_000,
            },
        )
        assert oversized.status_code == 413
        assert oversized.json()["error"]["code"] == "REQUEST_TOO_LARGE"

        headers = csrf_headers(client)
        for _attempt in range(8):
            response = client.post(
                "/api/v1/auth/login",
                headers=headers,
                json={"email": "bruteforce@example.com", "password": "WrongPassword123!"},
            )
            assert response.status_code == 422
        blocked = client.post(
            "/api/v1/auth/login",
            headers=headers,
            json={"email": "bruteforce@example.com", "password": "WrongPassword123!"},
        )
        assert blocked.status_code == 429
        assert blocked.json()["error"]["code"] == "RATE_LIMITED"


def test_insecure_production_configuration_fails_closed() -> None:
    try:
        Settings(
            app_env="production",
            app_key="a-secure-key-with-more-than-thirty-two-characters",
            cookie_secure=False,
            enable_hsts=False,
            frontend_origins=["http://shop.example.com"],
            trusted_hosts=["localhost"],
        )
    except ValidationError:
        return
    raise AssertionError("Insecure production settings must not be accepted.")
