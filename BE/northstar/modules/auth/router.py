import re
import secrets
from datetime import UTC, datetime

from fastapi import APIRouter, Request, Response
from sqlalchemy import text

from northstar.core.auth import CurrentUser, DbSession, optional_user, serialize_user
from northstar.core.config import get_settings
from northstar.core.http import ApiError, limiter, success
from northstar.core.security import (
    DUMMY_PASSWORD_HASH,
    create_session,
    destroy_session,
    hash_context,
    password_hash,
    verify_password,
)
from northstar.schemas import LoginInput, RegisterInput

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
csrf_router = APIRouter(tags=["security"])


def audit(
    db: DbSession,
    request: Request,
    event: str,
    *,
    user_id: int | None = None,
    email: str | None = None,
) -> None:
    client_ip = request.client.host if request.client is not None else "unknown"
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
            "ip_hash": hash_context(client_ip),
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
def register(payload: RegisterInput, request: Request, db: DbSession) -> Response:
    client_ip = request.client.host if request.client is not None else "unknown"
    limiter.hit(f"register:{client_ip}", 5, 3600)
    if not re.search(r"[a-z]", payload.password):
        raise ApiError("Password must contain a lowercase letter.", "VALIDATION_ERROR", 422)
    if not re.search(r"[A-Z]", payload.password):
        raise ApiError("Password must contain an uppercase letter.", "VALIDATION_ERROR", 422)
    if not re.search(r"\d", payload.password):
        raise ApiError("Password must contain a number.", "VALIDATION_ERROR", 422)
    if not re.search(r"[^A-Za-z0-9]", payload.password):
        raise ApiError("Password must contain a symbol.", "VALIDATION_ERROR", 422)

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
            "VALUES (:name,:email,NULL,:password,:created_at,:updated_at)"
        ),
        {
            "name": payload.name,
            "email": email,
            "password": password_hash.hash(payload.password),
            "created_at": now,
            "updated_at": now,
        },
    )
    user_id = int(result.lastrowid)
    role_id = db.execute(text("SELECT id FROM roles WHERE name='customer'")).scalar_one_or_none()
    if role_id is not None:
        db.execute(
            text("INSERT INTO role_user (role_id,user_id) VALUES (:role_id,:user_id)"),
            {"role_id": role_id, "user_id": user_id},
        )
    db.commit()
    response = success(request, {"user": serialize_user(db, user_id)}, "Registered.", 201)
    create_session(db, request, response, user_id)
    audit(db, request, "auth.registered", user_id=user_id, email=email)
    return response


@router.post("/login")
def login(payload: LoginInput, request: Request, db: DbSession) -> Response:
    settings = get_settings()
    client_ip = request.client.host if request.client is not None else "unknown"
    email = payload.email.lower()
    limiter.hit(f"login-ip:{client_ip}", settings.login_rate_limit * 3, 60)
    limiter.hit(f"login-account:{hash_context(email)}:{client_ip}", settings.login_rate_limit, 60)
    row = (
        db.execute(
            text("SELECT id,password FROM users WHERE email=:email LIMIT 1"), {"email": email}
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
    response = success(request, {"user": serialize_user(db, user_id)}, "Authenticated.")
    create_session(db, request, response, user_id)
    audit(db, request, "auth.login_succeeded", user_id=user_id, email=email)
    return response


@router.get("/me")
def me(request: Request, user: CurrentUser) -> Response:
    return success(request, user)


@router.post("/logout")
def logout(request: Request, db: DbSession, user: CurrentUser) -> Response:
    response = success(request, None, "Logged out.")
    destroy_session(db, request, response)
    response.headers["Clear-Site-Data"] = '"cookies"'
    audit(db, request, "auth.logged_out", user_id=int(user["id"]))
    return response
