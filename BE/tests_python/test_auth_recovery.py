from urllib.parse import parse_qs, urlparse

import pyotp
from fastapi.testclient import TestClient

from northstar.core.config import get_settings
from northstar.main import app
from northstar.modules.auth import router as auth_router_module

ORIGIN = "http://localhost:5173"


def csrf_headers(client: TestClient) -> dict[str, str]:
    response = client.get("/sanctum/csrf-cookie")
    assert response.status_code == 204
    return {"Origin": ORIGIN, "X-XSRF-TOKEN": client.cookies["XSRF-TOKEN"]}


def test_email_verification_and_password_recovery(monkeypatch) -> None:
    delivered_messages: list[str] = []

    def capture_email(_recipient: str, _subject: str, body: str) -> None:
        delivered_messages.append(body)

    monkeypatch.setattr(auth_router_module, "send_auth_email", capture_email)
    settings = get_settings()
    previous_requirement = settings.require_email_verification
    settings.require_email_verification = True
    try:
        with TestClient(app) as client:
            email = "verified-customer@example.com"
            registration = client.post(
                "/api/v1/auth/register",
                headers=csrf_headers(client),
                json={
                    "name": "Verified Customer",
                    "email": email,
                    "password": "SecurePassword123!",
                    "password_confirmation": "SecurePassword123!",
                },
            )
            assert registration.status_code == 201
            assert registration.json()["data"]["user"] is None
            assert registration.json()["data"]["verification_required"] is True
            assert delivered_messages

            blocked_login = client.post(
                "/api/v1/auth/login",
                headers=csrf_headers(client),
                json={"email": email, "password": "SecurePassword123!"},
            )
            assert blocked_login.status_code == 403
            assert blocked_login.json()["error"]["code"] == "EMAIL_NOT_VERIFIED"

            verification_url = delivered_messages.pop()
            verification_token = parse_qs(urlparse(verification_url.splitlines()[-1]).query)[
                "token"
            ][0]
            verified = client.post(
                "/api/v1/auth/verify-email",
                headers=csrf_headers(client),
                json={"token": verification_token},
            )
            assert verified.status_code == 200
            assert client.get("/api/v1/auth/me").status_code == 200

            mfa_setup = client.post(
                "/api/v1/auth/mfa/setup",
                headers=csrf_headers(client),
                json={"password": "SecurePassword123!"},
            )
            assert mfa_setup.status_code == 200
            secret = mfa_setup.json()["data"]["secret"]
            mfa_confirm = client.post(
                "/api/v1/auth/mfa/confirm",
                headers=csrf_headers(client),
                json={"code": pyotp.TOTP(secret).now()},
            )
            assert mfa_confirm.status_code == 200
            recovery_code = mfa_confirm.json()["data"]["recovery_codes"][0]
            assert mfa_confirm.json()["data"]["user"]["mfa_enabled"] is True

            assert (
                client.post("/api/v1/auth/logout", headers=csrf_headers(client)).status_code == 200
            )
            password_login = client.post(
                "/api/v1/auth/login",
                headers=csrf_headers(client),
                json={"email": email, "password": "SecurePassword123!"},
            )
            assert password_login.status_code == 202
            challenge_token = password_login.json()["data"]["challenge_token"]
            totp_code = pyotp.TOTP(secret).now()
            mfa_login = client.post(
                "/api/v1/auth/mfa/challenge",
                headers=csrf_headers(client),
                json={"challenge_token": challenge_token, "code": totp_code},
            )
            assert mfa_login.status_code == 200
            replay_login = client.post(
                "/api/v1/auth/login",
                headers=csrf_headers(client),
                json={"email": email, "password": "SecurePassword123!"},
            )
            replayed_code = client.post(
                "/api/v1/auth/mfa/challenge",
                headers=csrf_headers(client),
                json={
                    "challenge_token": replay_login.json()["data"]["challenge_token"],
                    "code": totp_code,
                },
            )
            assert replayed_code.status_code == 422

            forgot = client.post(
                "/api/v1/auth/forgot-password",
                headers=csrf_headers(client),
                json={"email": email},
            )
            assert forgot.status_code == 202
            reset_url = delivered_messages.pop()
            reset_query = parse_qs(urlparse(reset_url.splitlines()[-1]).query)
            reset = client.post(
                "/api/v1/auth/reset-password",
                headers=csrf_headers(client),
                json={
                    "token": reset_query["token"][0],
                    "email": reset_query["email"][0],
                    "password": "NewSecurePassword456!",
                    "password_confirmation": "NewSecurePassword456!",
                },
            )
            assert reset.status_code == 200
            assert client.get("/api/v1/auth/me").status_code == 401

            login = client.post(
                "/api/v1/auth/login",
                headers=csrf_headers(client),
                json={"email": email, "password": "NewSecurePassword456!"},
            )
            assert login.status_code == 202
            recovery_login = client.post(
                "/api/v1/auth/mfa/challenge",
                headers=csrf_headers(client),
                json={
                    "challenge_token": login.json()["data"]["challenge_token"],
                    "code": recovery_code,
                },
            )
            assert recovery_login.status_code == 200
    finally:
        settings.require_email_verification = previous_requirement
