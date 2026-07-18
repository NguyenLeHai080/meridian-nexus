from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy import text
from sqlalchemy.orm import Session

from northstar.core.database import get_db
from northstar.core.http import ApiError
from northstar.core.security import session_user_id

DbSession = Annotated[Session, Depends(get_db)]


def serialize_user(db: Session, user_id: int) -> dict[str, object]:
    user = (
        db.execute(
            text(
                "SELECT id,name,email,email_verified_at,created_at FROM users WHERE id=:id LIMIT 1"
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
        "created_at": user["created_at"],
        "roles": list(roles),
        "permissions": list(permissions),
    }


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
        if name not in user["permissions"]:
            raise ApiError("You do not have permission for this action.", "FORBIDDEN", 403)
        return user

    return dependency
