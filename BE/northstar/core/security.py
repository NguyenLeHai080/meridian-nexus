import hashlib
import secrets
from base64 import urlsafe_b64encode
from datetime import UTC, datetime, timedelta

import bcrypt
from cryptography.fernet import Fernet, InvalidToken
from fastapi import Request, Response
from pwdlib import PasswordHash
from sqlalchemy import text
from sqlalchemy.orm import Session

from northstar.core.config import get_settings
from northstar.core.http import ApiError
from northstar.core.network import client_ip

password_hash = PasswordHash.recommended()
DUMMY_PASSWORD_HASH = password_hash.hash("not-a-real-user-password")


def hash_secret(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def hash_context(value: str) -> str:
    settings = get_settings()
    return hashlib.sha256(f"{settings.app_key}:{value}".encode()).hexdigest()


def encrypt_secret(value: str) -> str:
    settings = get_settings()
    key = urlsafe_b64encode(hashlib.sha256(settings.app_key.encode()).digest())
    return Fernet(key).encrypt(value.encode()).decode()


def decrypt_secret(value: str) -> str:
    settings = get_settings()
    key = urlsafe_b64encode(hashlib.sha256(settings.app_key.encode()).digest())
    try:
        return Fernet(key).decrypt(value.encode()).decode()
    except InvalidToken as error:
        raise ApiError(
            "Multi-factor configuration is invalid.", "MFA_CONFIGURATION_ERROR", 500
        ) from error


def verify_password(password: str, encoded: str) -> bool:
    if encoded.startswith(("$2y$", "$2b$", "$2a$")):
        normalized = encoded.replace("$2y$", "$2b$", 1)
        try:
            return bcrypt.checkpw(password.encode(), normalized.encode())
        except ValueError:
            return False
    try:
        return password_hash.verify(password, encoded)
    except Exception:
        return False


def create_session(db: Session, request: Request, response: Response, user_id: int) -> None:
    settings = get_settings()
    token = secrets.token_urlsafe(48)
    now = datetime.now(UTC)
    expires_at = now + timedelta(minutes=settings.session_lifetime_minutes)
    request_client_ip = client_ip(request)
    user_agent = request.headers.get("User-Agent", "unknown")
    current_token = request.cookies.get(settings.session_cookie)
    if current_token:
        db.execute(
            text("DELETE FROM auth_sessions WHERE token_hash=:token_hash"),
            {"token_hash": hash_secret(current_token)},
        )
    db.execute(
        text(
            "INSERT INTO auth_sessions "
            "(token_hash,user_id,expires_at,last_seen_at,ip_hash,user_agent_hash) "
            "VALUES (:token_hash,:user_id,:expires_at,:last_seen_at,:ip_hash,:user_agent_hash)"
        ),
        {
            "token_hash": hash_secret(token),
            "user_id": user_id,
            "expires_at": expires_at,
            "last_seen_at": now,
            "ip_hash": hash_context(request_client_ip),
            "user_agent_hash": hash_context(user_agent),
        },
    )
    db.commit()
    response.set_cookie(
        settings.session_cookie,
        token,
        max_age=settings.session_lifetime_minutes * 60,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )


def destroy_session(db: Session, request: Request, response: Response) -> None:
    settings = get_settings()
    token = request.cookies.get(settings.session_cookie)
    if token:
        db.execute(
            text("DELETE FROM auth_sessions WHERE token_hash = :token_hash"),
            {"token_hash": hash_secret(token)},
        )
        db.commit()
    response.delete_cookie(
        settings.session_cookie,
        path="/",
        secure=settings.cookie_secure,
        httponly=True,
        samesite="lax",
    )
    response.delete_cookie(
        "XSRF-TOKEN",
        path="/",
        secure=settings.cookie_secure,
        samesite="lax",
    )


def session_user_id(db: Session, request: Request) -> int | None:
    settings = get_settings()
    token = request.cookies.get(settings.session_cookie)
    if not token:
        return None
    now = datetime.now(UTC)
    row = (
        db.execute(
            text(
                "SELECT user_id,expires_at,last_seen_at,ip_hash,user_agent_hash FROM auth_sessions "
                "WHERE token_hash = :token_hash LIMIT 1"
            ),
            {"token_hash": hash_secret(token)},
        )
        .mappings()
        .first()
    )
    if row is None:
        return None
    expires_at = datetime.fromisoformat(str(row["expires_at"]).replace("Z", "+00:00"))
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    if expires_at <= now:
        db.execute(
            text("DELETE FROM auth_sessions WHERE token_hash = :token_hash"),
            {"token_hash": hash_secret(token)},
        )
        db.commit()
        return None
    request_client_ip = client_ip(request)
    user_agent = request.headers.get("User-Agent", "unknown")
    if settings.session_bind_ip and not secrets.compare_digest(
        str(row["ip_hash"]), hash_context(request_client_ip)
    ):
        db.execute(
            text("DELETE FROM auth_sessions WHERE token_hash=:token_hash"),
            {"token_hash": hash_secret(token)},
        )
        db.commit()
        return None
    if settings.session_bind_user_agent and not secrets.compare_digest(
        str(row["user_agent_hash"]), hash_context(user_agent)
    ):
        db.execute(
            text("DELETE FROM auth_sessions WHERE token_hash=:token_hash"),
            {"token_hash": hash_secret(token)},
        )
        db.commit()
        return None
    last_seen_at = datetime.fromisoformat(str(row["last_seen_at"]).replace("Z", "+00:00"))
    if last_seen_at.tzinfo is None:
        last_seen_at = last_seen_at.replace(tzinfo=UTC)
    if (now - last_seen_at).total_seconds() >= settings.session_touch_interval_seconds:
        db.execute(
            text("UPDATE auth_sessions SET last_seen_at=:now WHERE token_hash=:token_hash"),
            {"now": now, "token_hash": hash_secret(token)},
        )
        db.commit()
    return int(row["user_id"])


def require_idempotency_key(request: Request) -> str:
    key = request.headers.get("Idempotency-Key", "")
    if len(key) < 12 or len(key) > 200:
        raise ApiError("A valid idempotency key is required.", "IDEMPOTENCY_KEY_REQUIRED", 422)
    return key
