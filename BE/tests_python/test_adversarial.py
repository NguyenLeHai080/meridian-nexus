from fastapi.testclient import TestClient
from pydantic import ValidationError

from northstar.core.config import Settings
from northstar.main import app
from northstar.modules.auth import router as auth_router_module
from northstar.modules.storefront import router as storefront_router_module

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


def test_sensitive_endpoints_use_context_specific_throttles(monkeypatch) -> None:
    class RecordingLimiter:
        def __init__(self) -> None:
            self.keys: list[str] = []

        def hit(self, key: str, _limit: int, _seconds: int) -> None:
            self.keys.append(key)

    auth_limiter = RecordingLimiter()
    contact_limiter = RecordingLimiter()
    monkeypatch.setattr(auth_router_module, "limiter", auth_limiter)
    monkeypatch.setattr(storefront_router_module, "limiter", contact_limiter)

    with TestClient(app) as client:
        headers = csrf_headers(client)
        client.post(
            "/api/v1/auth/login",
            headers=headers,
            json={"email": "distributed@example.com", "password": "WrongPassword123!"},
        )
        client.post(
            "/api/v1/storefront/contact",
            headers=headers,
            json={
                "name": "Rate Limit Tester",
                "email": "contact-rate-limit@example.com",
                "subject": "Endpoint throttle",
                "message": "Verify dedicated abuse controls.",
            },
        )

    assert any(key.startswith("login-account:") for key in auth_limiter.keys)
    assert any(key.startswith("login-account-ip:") for key in auth_limiter.keys)
    assert any(key.startswith("contact-ip:") for key in contact_limiter.keys)
    assert any(key.startswith("contact-email:") for key in contact_limiter.keys)


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


def test_secure_production_configuration_is_accepted() -> None:
    settings = Settings(
        app_env="production",
        app_key="a-secure-key-with-more-than-thirty-two-characters",
        database_url="postgresql+psycopg://app:secret@postgres/app",
        redis_url="rediss://default:secret@redis.example.com/0",
        frontend_origins=["https://shop.example.com"],
        frontend_url="https://shop.example.com",
        trusted_hosts=["api.example.com"],
        session_cookie="__Host-northstar_session",
        cookie_secure=True,
        enable_hsts=True,
        require_email_verification=True,
        require_privileged_mfa=True,
        smtp_host="smtp.example.com",
        smtp_from_email="no-reply@example.com",
    )
    assert settings.app_env == "production"
