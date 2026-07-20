import re
import secrets
from datetime import UTC, datetime, timedelta

import pyotp
from fastapi import Request
from sqlalchemy import text
from sqlalchemy.orm import Session

from northstar.core.config import get_settings
from northstar.core.http import ApiError
from northstar.core.network import client_ip
from northstar.core.security import decrypt_secret, hash_context, hash_secret


def validate_password(password: str) -> None:
    if not re.search(r"[a-z]", password):
        raise ApiError("Password must contain a lowercase letter.", "VALIDATION_ERROR", 422)
    if not re.search(r"[A-Z]", password):
        raise ApiError("Password must contain an uppercase letter.", "VALIDATION_ERROR", 422)
    if not re.search(r"\d", password):
        raise ApiError("Password must contain a number.", "VALIDATION_ERROR", 422)
    if not re.search(r"[^A-Za-z0-9]", password):
        raise ApiError("Password must contain a symbol.", "VALIDATION_ERROR", 422)


def issue_action_token(
    db: Session, user_id: int, purpose: str, *, lifetime_minutes: int | None = None
) -> str:
    settings = get_settings()
    token = secrets.token_urlsafe(48)
    now = datetime.now(UTC)
    lifetime = settings.auth_action_token_minutes
    if lifetime_minutes is not None:
        lifetime = lifetime_minutes
    db.execute(
        text("DELETE FROM auth_action_tokens WHERE user_id=:user_id AND purpose=:purpose"),
        {"user_id": user_id, "purpose": purpose},
    )
    db.execute(
        text(
            "INSERT INTO auth_action_tokens(token_hash,user_id,purpose,expires_at,created_at) VALUES (:token_hash,:user_id,:purpose,:expires_at,:created_at)"
        ),
        {
            "token_hash": hash_secret(token),
            "user_id": user_id,
            "purpose": purpose,
            "expires_at": now + timedelta(minutes=lifetime),
            "created_at": now,
        },
    )
    return token


def action_token_user(
    db: Session, token: str, purpose: str, *, email: str | None = None
) -> dict[str, object]:
    row = (
        db.execute(
            text(
                "SELECT t.token_hash,t.user_id,t.expires_at,u.email FROM auth_action_tokens t JOIN users u ON u.id=t.user_id WHERE t.token_hash=:token_hash AND t.purpose=:purpose AND t.used_at IS NULL LIMIT 1"
            ),
            {"token_hash": hash_secret(token), "purpose": purpose},
        )
        .mappings()
        .first()
    )
    if row is None:
        raise ApiError("The action token is invalid or expired.", "INVALID_TOKEN", 422)
    expires_at = datetime.fromisoformat(str(row["expires_at"]).replace("Z", "+00:00"))
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    if expires_at <= datetime.now(UTC):
        raise ApiError("The action token is invalid or expired.", "INVALID_TOKEN", 422)
    if email is not None and not secrets.compare_digest(str(row["email"]).lower(), email.lower()):
        raise ApiError("The action token is invalid or expired.", "INVALID_TOKEN", 422)
    return dict(row)


def matching_totp_step(secret: str, code: str) -> int | None:
    normalized = code.strip().upper().replace("-", "")
    if not normalized.isdigit() or len(normalized) != 6:
        return None
    totp = pyotp.TOTP(secret)
    current_step = int(datetime.now(UTC).timestamp()) // totp.interval
    for offset in (-1, 0, 1):
        candidate_step = current_step + offset
        if secrets.compare_digest(totp.at(candidate_step * totp.interval), normalized):
            return candidate_step
    return None


def verify_mfa_code(db: Session, user_id: int, encrypted_secret: str, code: str) -> bool:
    normalized = code.strip().upper().replace("-", "")
    candidate_step = matching_totp_step(decrypt_secret(encrypted_secret), normalized)
    if candidate_step is not None:
        last_used_step = db.execute(
            text("SELECT mfa_last_used_step FROM users WHERE id=:user_id"), {"user_id": user_id}
        ).scalar_one_or_none()
        if last_used_step is not None and int(last_used_step) >= candidate_step:
            return False
        db.execute(
            text("UPDATE users SET mfa_last_used_step=:step WHERE id=:user_id"),
            {"step": candidate_step, "user_id": user_id},
        )
        return True
    result = db.execute(
        text("DELETE FROM mfa_recovery_codes WHERE user_id=:user_id AND code_hash=:code_hash"),
        {"user_id": user_id, "code_hash": hash_context(f"mfa-recovery:{normalized}")},
    )
    return result.rowcount == 1


def audit_security_event(
    db: Session,
    request: Request,
    event: str,
    *,
    user_id: int | None = None,
    email: str | None = None,
) -> None:
    db.execute(
        text(
            "INSERT INTO security_events (event,user_id,email_hash,ip_hash,request_id,metadata) VALUES (:event,:user_id,:email_hash,:ip_hash,:request_id,'{}')"
        ),
        {
            "event": event,
            "user_id": user_id,
            "email_hash": None if email is None else hash_context(email.lower()),
            "ip_hash": hash_context(client_ip(request)),
            "request_id": request.state.request_id,
        },
    )
    db.commit()
