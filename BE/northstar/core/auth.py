from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy import bindparam, text
from sqlalchemy.orm import Session

from northstar.core.config import get_settings
from northstar.core.database import get_db
from northstar.core.http import ApiError
from northstar.core.security import session_user_id

DbSession = Annotated[Session, Depends(get_db)]


def serialize_user(db: Session, user_id: int) -> dict[str, object]:
    user = (
        db.execute(
            text(
                "SELECT id,name,email,email_verified_at,mfa_enabled_at,created_at "
                "FROM users WHERE id=:id LIMIT 1"
            ),
            {"id": user_id},
        )
        .mappings()
        .first()
    )
    if user is None:
        raise ApiError("Unauthenticated.", "UNAUTHENTICATED", 401)
    roles = (
        db.execute(
            text(
                "SELECT roles.name FROM roles INNER JOIN role_user ON role_user.role_id=roles.id "
                "WHERE role_user.user_id=:user_id ORDER BY roles.name"
            ),
            {"user_id": user_id},
        )
        .scalars()
        .all()
    )
    permissions = (
        db.execute(
            text(
                "SELECT DISTINCT permissions.name FROM permissions "
                "INNER JOIN permission_role ON permission_role.permission_id=permissions.id "
                "INNER JOIN role_user ON role_user.role_id=permission_role.role_id "
                "WHERE role_user.user_id=:user_id ORDER BY permissions.name"
            ),
            {"user_id": user_id},
        )
        .scalars()
        .all()
    )
    return {
        "id": int(user["id"]),
        "name": user["name"],
        "email": user["email"],
        "email_verified_at": user["email_verified_at"],
        "mfa_enabled": user["mfa_enabled_at"] is not None,
        "created_at": user["created_at"],
        "roles": list(roles),
        "permissions": list(permissions),
    }


def serialize_users(db: Session, user_ids: list[int]) -> list[dict[str, object]]:
    if not user_ids:
        return []
    ids_parameter = bindparam("user_ids", expanding=True)
    users = (
        db.execute(
            text(
                "SELECT id,name,email,email_verified_at,mfa_enabled_at,created_at "
                "FROM users WHERE id IN :user_ids"
            ).bindparams(ids_parameter),
            {"user_ids": user_ids},
        )
        .mappings()
        .all()
    )
    role_rows = (
        db.execute(
            text(
                "SELECT ru.user_id,r.name FROM role_user ru JOIN roles r ON r.id=ru.role_id "
                "WHERE ru.user_id IN :user_ids ORDER BY r.name"
            ).bindparams(ids_parameter),
            {"user_ids": user_ids},
        )
        .mappings()
        .all()
    )
    permission_rows = (
        db.execute(
            text(
                "SELECT DISTINCT ru.user_id,p.name FROM role_user ru "
                "JOIN permission_role pr ON pr.role_id=ru.role_id "
                "JOIN permissions p ON p.id=pr.permission_id "
                "WHERE ru.user_id IN :user_ids ORDER BY p.name"
            ).bindparams(ids_parameter),
            {"user_ids": user_ids},
        )
        .mappings()
        .all()
    )
    roles: dict[int, list[str]] = {user_id: [] for user_id in user_ids}
    permissions: dict[int, list[str]] = {user_id: [] for user_id in user_ids}
    for row in role_rows:
        roles[int(row["user_id"])].append(str(row["name"]))
    for row in permission_rows:
        permissions[int(row["user_id"])].append(str(row["name"]))
    users_by_id = {int(user["id"]): user for user in users}
    return [
        {
            "id": user_id,
            "name": users_by_id[user_id]["name"],
            "email": users_by_id[user_id]["email"],
            "email_verified_at": users_by_id[user_id]["email_verified_at"],
            "mfa_enabled": users_by_id[user_id]["mfa_enabled_at"] is not None,
            "created_at": users_by_id[user_id]["created_at"],
            "roles": roles[user_id],
            "permissions": permissions[user_id],
        }
        for user_id in user_ids
        if user_id in users_by_id
    ]


def optional_user(request: Request, db: DbSession) -> dict[str, object] | None:
    user_id = session_user_id(db, request)
    if user_id is None:
        return None
    return serialize_user(db, user_id)


def current_user(request: Request, db: DbSession) -> dict[str, object]:
    user = optional_user(request, db)
    if user is None:
        raise ApiError("Unauthenticated.", "UNAUTHENTICATED", 401)
    return user


CurrentUser = Annotated[dict[str, object], Depends(current_user)]


def permission(name: str):
    def dependency(user: CurrentUser) -> dict[str, object]:
        settings = get_settings()
        privileged = bool(set(user["roles"]) & {"admin", "manager"})
        if settings.require_privileged_mfa and privileged and not user["mfa_enabled"]:
            raise ApiError(
                "Multi-factor authentication enrollment is required.",
                "MFA_ENROLLMENT_REQUIRED",
                403,
            )
        if name not in user["permissions"]:
            raise ApiError("You do not have permission for this action.", "FORBIDDEN", 403)
        return user

    return dependency
