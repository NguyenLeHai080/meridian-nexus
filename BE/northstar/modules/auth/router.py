import re
import secrets
from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode

import pyotp
from fastapi import APIRouter, BackgroundTasks, Path, Request, Response
from sqlalchemy import text

from northstar.core.auth import CurrentUser, DbSession, optional_user, serialize_user
from northstar.core.config import get_settings
from northstar.core.http import ApiError, limiter, success
from northstar.core.mailer import send_auth_email
from northstar.core.network import client_ip
from northstar.core.security import (
    DUMMY_PASSWORD_HASH,
    create_session,
    decrypt_secret,
    destroy_session,
    encrypt_secret,
    hash_context,
    hash_secret,
    password_hash,
    verify_password,
)
from northstar.schemas import (
    EmailActionInput,
    LoginInput,
    MfaChallengeInput,
    MfaCodeInput,
    MfaSetupInput,
    PasswordResetInput,
    RegisterInput,
    TokenInput,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
csrf_router = APIRouter(tags=["security"])


def _validate_password(password: str) -> None:
    if not re.search(r"[a-z]", password):
        raise ApiError("Password must contain a lowercase letter.", "VALIDATION_ERROR", 422)
    if not re.search(r"[A-Z]", password):
        raise ApiError("Password must contain an uppercase letter.", "VALIDATION_ERROR", 422)
    if not re.search(r"\d", password):
        raise ApiError("Password must contain a number.", "VALIDATION_ERROR", 422)
    if not re.search(r"[^A-Za-z0-9]", password):
        raise ApiError("Password must contain a symbol.", "VALIDATION_ERROR", 422)


def _issue_action_token(
    db: DbSession,
    user_id: int,
    purpose: str,
    *,
    lifetime_minutes: int | None = None,
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
            "INSERT INTO auth_action_tokens(token_hash,user_id,purpose,expires_at,created_at) "
            "VALUES (:token_hash,:user_id,:purpose,:expires_at,:created_at)"
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


def _action_token_user(
    db: DbSession,
    token: str,
    purpose: str,
    *,
    email: str | None = None,
) -> dict[str, object]:
    row = (
        db.execute(
            text(
                "SELECT t.token_hash,t.user_id,t.expires_at,u.email FROM auth_action_tokens t "
                "JOIN users u ON u.id=t.user_id WHERE t.token_hash=:token_hash "
                "AND t.purpose=:purpose AND t.used_at IS NULL LIMIT 1"
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


def _matching_totp_step(secret: str, code: str) -> int | None:
    normalized = code.strip().upper().replace("-", "")
    if not normalized.isdigit() or len(normalized) != 6:
        return None
    totp = pyotp.TOTP(secret)
    current_step = int(datetime.now(UTC).timestamp()) // totp.interval
    for offset in (-1, 0, 1):
        candidate_step = current_step + offset
        candidate_code = totp.at(candidate_step * totp.interval)
        if secrets.compare_digest(candidate_code, normalized):
            return candidate_step
    return None


def _verify_mfa_code(db: DbSession, user_id: int, encrypted_secret: str, code: str) -> bool:
    normalized = code.strip().upper().replace("-", "")
    candidate_step = _matching_totp_step(decrypt_secret(encrypted_secret), normalized)
    if candidate_step is not None:
        last_used_step = db.execute(
            text("SELECT mfa_last_used_step FROM users WHERE id=:user_id"),
            {"user_id": user_id},
        ).scalar_one_or_none()
        if last_used_step is not None and int(last_used_step) >= candidate_step:
            return False
        db.execute(
            text("UPDATE users SET mfa_last_used_step=:step WHERE id=:user_id"),
            {"step": candidate_step, "user_id": user_id},
        )
        return True
    recovery_hash = hash_context(f"mfa-recovery:{normalized}")
    result = db.execute(
        text("DELETE FROM mfa_recovery_codes WHERE user_id=:user_id AND code_hash=:code_hash"),
        {"user_id": user_id, "code_hash": recovery_hash},
    )
    return result.rowcount == 1


def audit(
    db: DbSession,
    request: Request,
    event: str,
    *,
    user_id: int | None = None,
    email: str | None = None,
) -> None:
    request_client_ip = client_ip(request)
    db.execute(
        text(
            "INSERT INTO security_events "
            "(event,user_id,email_hash,ip_hash,request_id,metadata) "
            "VALUES (:event,:user_id,:email_hash,:ip_hash,:request_id,'{}')"
        ),
        {
            "event": event,
            "user_id": user_id,
            "email_hash": None if email is None else hash_context(email.lower()),
            "ip_hash": hash_context(request_client_ip),
            "request_id": request.state.request_id,
        },
    )
    db.commit()


@csrf_router.get("/sanctum/csrf-cookie", status_code=204)
def csrf_cookie() -> Response:
    settings = get_settings()
    response = Response(status_code=204)
    response.set_cookie(
        "XSRF-TOKEN",
        secrets.token_urlsafe(32),
        max_age=7200,
        httponly=False,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )
    return response


@router.get("/session")
def session(request: Request, db: DbSession) -> Response:
    user = optional_user(request, db)
    return success(request, {"authenticated": user is not None, "user": user})


@router.post("/register", status_code=201)
def register(
    payload: RegisterInput,
    request: Request,
    background_tasks: BackgroundTasks,
    db: DbSession,
) -> Response:
    request_client_ip = client_ip(request)
    limiter.hit(f"register:{request_client_ip}", 5, 3600)
    _validate_password(payload.password)

    email = payload.email.lower()
    exists = db.execute(text("SELECT 1 FROM users WHERE email=:email"), {"email": email}).first()
    if exists is not None:
        raise ApiError(
            "The given data was invalid.",
            "VALIDATION_ERROR",
            422,
            errors={"email": ["This email address is already registered."]},
        )
    now = datetime.now(UTC)
    result = db.execute(
        text(
            "INSERT INTO users (name,email,email_verified_at,password,created_at,updated_at) "
            "VALUES (:name,:email,NULL,:password,:created_at,:updated_at) RETURNING id"
        ),
        {
            "name": payload.name,
            "email": email,
            "password": password_hash.hash(payload.password),
            "created_at": now,
            "updated_at": now,
        },
    )
    user_id = int(result.scalar_one())
    role_id = db.execute(text("SELECT id FROM roles WHERE name='customer'")).scalar_one_or_none()
    if role_id is not None:
        db.execute(
            text("INSERT INTO role_user (role_id,user_id) VALUES (:role_id,:user_id)"),
            {"role_id": role_id, "user_id": user_id},
        )
    settings = get_settings()
    verification_token = None
    if settings.require_email_verification:
        verification_token = _issue_action_token(db, user_id, "verify_email")
    db.commit()
    response = success(
        request,
        {
            "user": None if settings.require_email_verification else serialize_user(db, user_id),
            "verification_required": settings.require_email_verification,
        },
        "Registered.",
        201,
    )
    if settings.require_email_verification and verification_token is not None:
        verification_url = f"{settings.frontend_url}/verify-email?token={verification_token}"
        background_tasks.add_task(
            send_auth_email,
            email,
            "Verify your Meridian Nexus account",
            f"Verify your account using this link:\n\n{verification_url}",
        )
    else:
        create_session(db, request, response, user_id)
    audit(db, request, "auth.registered", user_id=user_id, email=email)
    return response


@router.post("/login")
def login(payload: LoginInput, request: Request, db: DbSession) -> Response:
    settings = get_settings()
    request_client_ip = client_ip(request)
    email = payload.email.lower()
    limiter.hit(f"login-ip:{request_client_ip}", settings.login_rate_limit * 3, 60)
    limiter.hit(
        f"login-account:{hash_context(email)}",
        settings.login_rate_limit * 3,
        300,
    )
    limiter.hit(
        f"login-account-ip:{hash_context(email)}:{request_client_ip}",
        settings.login_rate_limit,
        60,
    )
    row = (
        db.execute(
            text(
                "SELECT id,password,email_verified_at,mfa_secret,mfa_enabled_at "
                "FROM users WHERE email=:email LIMIT 1"
            ),
            {"email": email},
        )
        .mappings()
        .first()
    )
    encoded_password = DUMMY_PASSWORD_HASH if row is None else str(row["password"])
    password_is_valid = verify_password(payload.password, encoded_password)
    authenticated = row is not None and password_is_valid
    if not authenticated:
        audit(db, request, "auth.login_failed", email=email)
        raise ApiError("The provided credentials are invalid.", "INVALID_CREDENTIALS", 422)
    user_id = int(row["id"])
    if settings.require_email_verification and row["email_verified_at"] is None:
        audit(db, request, "auth.login_unverified", user_id=user_id, email=email)
        raise ApiError("Email verification is required.", "EMAIL_NOT_VERIFIED", 403)
    if not str(row["password"]).startswith("$argon2"):
        db.execute(
            text("UPDATE users SET password=:password,updated_at=:updated_at WHERE id=:id"),
            {
                "password": password_hash.hash(payload.password),
                "updated_at": datetime.now(UTC),
                "id": user_id,
            },
        )
        db.commit()
    if row["mfa_enabled_at"] is not None and row["mfa_secret"] is not None:
        challenge_token = _issue_action_token(
            db,
            user_id,
            "mfa_login",
            lifetime_minutes=5,
        )
        db.commit()
        audit(db, request, "auth.mfa_challenge_issued", user_id=user_id, email=email)
        return success(
            request,
            {"user": None, "mfa_required": True, "challenge_token": challenge_token},
            "Multi-factor authentication required.",
            202,
        )
    response = success(
        request,
        {"user": serialize_user(db, user_id), "mfa_required": False, "challenge_token": None},
        "Authenticated.",
    )
    create_session(db, request, response, user_id)
    audit(db, request, "auth.login_succeeded", user_id=user_id, email=email)
    return response


@router.post("/email/verification-notification", status_code=202)
def resend_verification(
    payload: EmailActionInput,
    request: Request,
    background_tasks: BackgroundTasks,
    db: DbSession,
) -> Response:
    email = payload.email.lower()
    limiter.hit(f"verify-email-account:{hash_context(email)}", 6, 3600)
    limiter.hit(f"verify-email:{hash_context(email)}:{client_ip(request)}", 3, 3600)
    row = (
        db.execute(
            text("SELECT id,email_verified_at FROM users WHERE email=:email LIMIT 1"),
            {"email": email},
        )
        .mappings()
        .first()
    )
    if row is not None and row["email_verified_at"] is None:
        token = _issue_action_token(db, int(row["id"]), "verify_email")
        db.commit()
        verification_url = f"{get_settings().frontend_url}/verify-email?token={token}"
        background_tasks.add_task(
            send_auth_email,
            email,
            "Verify your Meridian Nexus account",
            f"Verify your account using this link:\n\n{verification_url}",
        )
    return success(request, None, "If verification is required, an email has been sent.", 202)


@router.post("/verify-email")
def verify_email(payload: TokenInput, request: Request, db: DbSession) -> Response:
    token_row = _action_token_user(db, payload.token, "verify_email")
    now = datetime.now(UTC)
    user_id = int(token_row["user_id"])
    db.execute(
        text("UPDATE users SET email_verified_at=:now,updated_at=:now WHERE id=:user_id"),
        {"now": now, "user_id": user_id},
    )
    db.execute(
        text("DELETE FROM auth_action_tokens WHERE user_id=:user_id AND purpose='verify_email'"),
        {"user_id": user_id},
    )
    db.commit()
    response = success(request, {"user": serialize_user(db, user_id)}, "Email verified.")
    create_session(db, request, response, user_id)
    audit(db, request, "auth.email_verified", user_id=user_id, email=str(token_row["email"]))
    return response


@router.post("/forgot-password", status_code=202)
def forgot_password(
    payload: EmailActionInput,
    request: Request,
    background_tasks: BackgroundTasks,
    db: DbSession,
) -> Response:
    email = payload.email.lower()
    limiter.hit(f"forgot-password-account:{hash_context(email)}", 6, 3600)
    limiter.hit(f"forgot-password:{hash_context(email)}:{client_ip(request)}", 3, 3600)
    user_id = db.execute(
        text("SELECT id FROM users WHERE email=:email LIMIT 1"), {"email": email}
    ).scalar_one_or_none()
    if user_id is not None:
        token = _issue_action_token(db, int(user_id), "reset_password")
        db.commit()
        reset_query = urlencode({"token": token, "email": email})
        reset_url = f"{get_settings().frontend_url}/reset-password?{reset_query}"
        background_tasks.add_task(
            send_auth_email,
            email,
            "Reset your Meridian Nexus password",
            f"Reset your password using this link:\n\n{reset_url}",
        )
    return success(request, None, "If the account exists, a reset email has been sent.", 202)


@router.post("/reset-password")
def reset_password(payload: PasswordResetInput, request: Request, db: DbSession) -> Response:
    _validate_password(payload.password)
    token_row = _action_token_user(
        db,
        payload.token,
        "reset_password",
        email=payload.email.lower(),
    )
    user_id = int(token_row["user_id"])
    now = datetime.now(UTC)
    db.execute(
        text(
            "UPDATE users SET password=:password,mfa_pending_secret=NULL,updated_at=:now "
            "WHERE id=:user_id"
        ),
        {"password": password_hash.hash(payload.password), "now": now, "user_id": user_id},
    )
    db.execute(text("DELETE FROM auth_sessions WHERE user_id=:user_id"), {"user_id": user_id})
    db.execute(text("DELETE FROM auth_action_tokens WHERE user_id=:user_id"), {"user_id": user_id})
    db.commit()
    response = success(request, None, "Password reset completed.")
    destroy_session(db, request, response)
    audit(db, request, "auth.password_reset", user_id=user_id, email=payload.email)
    return response


@router.post("/mfa/challenge")
def mfa_challenge(payload: MfaChallengeInput, request: Request, db: DbSession) -> Response:
    limiter.hit(
        f"mfa-challenge:{hash_secret(payload.challenge_token)}:{client_ip(request)}",
        5,
        300,
    )
    token_row = _action_token_user(db, payload.challenge_token, "mfa_login")
    user_id = int(token_row["user_id"])
    encrypted_secret = db.execute(
        text("SELECT mfa_secret FROM users WHERE id=:user_id"), {"user_id": user_id}
    ).scalar_one_or_none()
    if encrypted_secret is None or not _verify_mfa_code(
        db, user_id, str(encrypted_secret), payload.code
    ):
        db.rollback()
        audit(db, request, "auth.mfa_failed", user_id=user_id, email=str(token_row["email"]))
        raise ApiError("The multi-factor code is invalid.", "INVALID_MFA_CODE", 422)
    db.execute(
        text("DELETE FROM auth_action_tokens WHERE user_id=:user_id AND purpose='mfa_login'"),
        {"user_id": user_id},
    )
    db.commit()
    response = success(request, {"user": serialize_user(db, user_id)}, "Authenticated.")
    create_session(db, request, response, user_id)
    audit(db, request, "auth.mfa_succeeded", user_id=user_id, email=str(token_row["email"]))
    return response


@router.post("/mfa/setup")
def mfa_setup(
    payload: MfaSetupInput,
    request: Request,
    db: DbSession,
    user: CurrentUser,
) -> Response:
    limiter.hit(f"mfa-setup:{user['id']}:{client_ip(request)}", 5, 3600)
    row = (
        db.execute(
            text("SELECT email,password,mfa_secret,mfa_enabled_at FROM users WHERE id=:user_id"),
            {"user_id": user["id"]},
        )
        .mappings()
        .one()
    )
    if not verify_password(payload.password, str(row["password"])):
        raise ApiError("The provided credentials are invalid.", "INVALID_CREDENTIALS", 422)
    if row["mfa_enabled_at"] is not None:
        if payload.current_code is None or row["mfa_secret"] is None:
            raise ApiError("The current MFA code is required.", "MFA_CODE_REQUIRED", 422)
        if not _verify_mfa_code(
            db,
            int(user["id"]),
            str(row["mfa_secret"]),
            payload.current_code,
        ):
            db.rollback()
            raise ApiError("The multi-factor code is invalid.", "INVALID_MFA_CODE", 422)
    secret = pyotp.random_base32()
    db.execute(
        text("UPDATE users SET mfa_pending_secret=:secret,updated_at=:now WHERE id=:user_id"),
        {
            "secret": encrypt_secret(secret),
            "now": datetime.now(UTC),
            "user_id": user["id"],
        },
    )
    db.commit()
    uri = pyotp.TOTP(secret).provisioning_uri(
        name=str(row["email"]),
        issuer_name=get_settings().app_name,
    )
    audit(db, request, "auth.mfa_setup_started", user_id=int(user["id"]))
    return success(request, {"secret": secret, "provisioning_uri": uri})


@router.post("/mfa/confirm")
def mfa_confirm(
    payload: MfaCodeInput,
    request: Request,
    db: DbSession,
    user: CurrentUser,
) -> Response:
    limiter.hit(f"mfa-confirm:{user['id']}:{client_ip(request)}", 10, 600)
    encrypted_secret = db.execute(
        text("SELECT mfa_pending_secret FROM users WHERE id=:user_id"),
        {"user_id": user["id"]},
    ).scalar_one_or_none()
    if encrypted_secret is None:
        raise ApiError("Start multi-factor setup first.", "MFA_SETUP_REQUIRED", 409)
    secret = decrypt_secret(str(encrypted_secret))
    matched_step = _matching_totp_step(secret, payload.code)
    if matched_step is None:
        raise ApiError("The multi-factor code is invalid.", "INVALID_MFA_CODE", 422)
    now = datetime.now(UTC)
    recovery_codes = [secrets.token_hex(5).upper() for _index in range(10)]
    db.execute(
        text(
            "UPDATE users SET mfa_secret=mfa_pending_secret,mfa_pending_secret=NULL,"
            "mfa_enabled_at=:now,mfa_last_used_step=:step,updated_at=:now WHERE id=:user_id"
        ),
        {"now": now, "step": matched_step, "user_id": user["id"]},
    )
    db.execute(
        text("DELETE FROM mfa_recovery_codes WHERE user_id=:user_id"),
        {"user_id": user["id"]},
    )
    for code in recovery_codes:
        db.execute(
            text(
                "INSERT INTO mfa_recovery_codes(user_id,code_hash,created_at) "
                "VALUES (:user_id,:code_hash,:now)"
            ),
            {
                "user_id": user["id"],
                "code_hash": hash_context(f"mfa-recovery:{code}"),
                "now": now,
            },
        )
    db.commit()
    audit(db, request, "auth.mfa_enabled", user_id=int(user["id"]))
    return success(
        request,
        {"user": serialize_user(db, int(user["id"])), "recovery_codes": recovery_codes},
        "Multi-factor authentication enabled.",
    )


@router.get("/me")
def me(request: Request, user: CurrentUser) -> Response:
    return success(request, user)


@router.get("/sessions")
def sessions(request: Request, db: DbSession, user: CurrentUser) -> Response:
    settings = get_settings()
    current_token = request.cookies.get(settings.session_cookie, "")
    current_hash = hash_secret(current_token) if current_token else ""
    rows = (
        db.execute(
            text(
                "SELECT token_hash,expires_at,last_seen_at,created_at FROM auth_sessions "
                "WHERE user_id=:user_id ORDER BY last_seen_at DESC"
            ),
            {"user_id": user["id"]},
        )
        .mappings()
        .all()
    )
    data = [
        {
            "id": row["token_hash"],
            "expires_at": row["expires_at"],
            "last_seen_at": row["last_seen_at"],
            "created_at": row["created_at"],
            "current": secrets.compare_digest(str(row["token_hash"]), current_hash),
        }
        for row in rows
    ]
    return success(request, data)


@router.delete("/sessions/{session_id}")
def revoke_session(
    request: Request,
    db: DbSession,
    user: CurrentUser,
    session_id: str = Path(pattern=r"^[a-f0-9]{64}$"),
) -> Response:
    settings = get_settings()
    current_token = request.cookies.get(settings.session_cookie, "")
    is_current = bool(current_token) and secrets.compare_digest(
        hash_secret(current_token), session_id
    )
    result = db.execute(
        text("DELETE FROM auth_sessions WHERE token_hash=:token_hash AND user_id=:user_id"),
        {"token_hash": session_id, "user_id": user["id"]},
    )
    if result.rowcount != 1:
        db.rollback()
        raise ApiError("Session not found.", "NOT_FOUND", 404)
    db.commit()
    response = success(request, None, "Session revoked.")
    if is_current:
        destroy_session(db, request, response)
    audit(db, request, "auth.session_revoked", user_id=int(user["id"]))
    return response


@router.post("/logout")
def logout(request: Request, db: DbSession, user: CurrentUser) -> Response:
    response = success(request, None, "Logged out.")
    destroy_session(db, request, response)
    response.headers["Clear-Site-Data"] = '"cookies"'
    audit(db, request, "auth.logged_out", user_id=int(user["id"]))
    return response
