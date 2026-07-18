import secrets
from datetime import UTC, datetime

from fastapi import APIRouter, Request, Response
from sqlalchemy import text

from northstar.core.auth import DbSession, optional_user
from northstar.core.http import ApiError, success
from northstar.core.serialization import conversation_dict
from northstar.schemas import ChatReplyInput, ChatStartInput

router = APIRouter(prefix="/api/v1/storefront/chat", tags=["chat"])


def _find(db: DbSession, token: str) -> dict[str, object]:
    row = (
        db.execute(
            text("SELECT * FROM conversations WHERE public_token=:token LIMIT 1"), {"token": token}
        )
        .mappings()
        .first()
    )
    if row is None:
        raise ApiError("Conversation not found.", "NOT_FOUND", 404)
    return dict(row)


@router.post("", status_code=201)
def start(payload: ChatStartInput, request: Request, db: DbSession) -> Response:
    user = optional_user(request, db)
    now = datetime.now(UTC)
    token = secrets.token_hex(32)
    result = db.execute(
        text(
            "INSERT INTO conversations(public_token,customer_id,guest_name,guest_email,status,last_message_at,created_at,updated_at) "
            "VALUES (:token,:customer_id,:name,:email,'open',:now,:now,:now)"
        ),
        {
            "token": token,
            "customer_id": None if user is None else user["id"],
            "name": payload.name,
            "email": None if payload.email is None else str(payload.email),
            "now": now,
        },
    )
    conversation_id = int(result.lastrowid)
    db.execute(
        text(
            "INSERT INTO messages(conversation_id,sender_id,sender_type,body,created_at,updated_at) "
            "VALUES (:conversation_id,:sender_id,'customer',:body,:now,:now)"
        ),
        {
            "conversation_id": conversation_id,
            "sender_id": None if user is None else user["id"],
            "body": payload.message,
            "now": now,
        },
    )
    db.commit()
    return success(request, conversation_dict(db, _find(db, token)), "Conversation started.", 201)


@router.get("/{token}")
def show(token: str, request: Request, db: DbSession) -> Response:
    return success(request, conversation_dict(db, _find(db, token)))


@router.post("/{token}")
def reply(token: str, payload: ChatReplyInput, request: Request, db: DbSession) -> Response:
    conversation = _find(db, token)
    now = datetime.now(UTC)
    user = optional_user(request, db)
    db.execute(
        text(
            "INSERT INTO messages(conversation_id,sender_id,sender_type,body,created_at,updated_at) "
            "VALUES (:conversation_id,:sender_id,'customer',:body,:now,:now)"
        ),
        {
            "conversation_id": conversation["id"],
            "sender_id": None if user is None else user["id"],
            "body": payload.message,
            "now": now,
        },
    )
    db.execute(
        text("UPDATE conversations SET last_message_at=:now,updated_at=:now WHERE id=:id"),
        {"now": now, "id": conversation["id"]},
    )
    db.commit()
    return success(request, conversation_dict(db, _find(db, token)), "Message sent.")
