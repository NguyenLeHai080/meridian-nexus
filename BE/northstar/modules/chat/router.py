import secrets
from datetime import UTC, datetime

from fastapi import APIRouter, Request, Response
from sqlalchemy import text

from northstar.core.auth import DbSession, optional_user
from northstar.core.http import ApiError, limiter, success
from northstar.core.network import client_ip
from northstar.core.security import hash_secret
from northstar.core.serialization import conversation_dict
from northstar.schemas import ChatReplyInput, ChatStartInput

router = APIRouter(prefix="/api/v1/storefront/chat", tags=["chat"])


def _find(db: DbSession, token: str) -> dict[str, object]:
    token_hash = hash_secret(token)
    row = (
        db.execute(
            text(
                "SELECT * FROM conversations "
                "WHERE public_token=:token_hash OR public_token=:legacy_token LIMIT 1"
            ),
            {"token_hash": token_hash, "legacy_token": token},
        )
        .mappings()
        .first()
    )
    if row is None:
        raise ApiError("Conversation not found.", "NOT_FOUND", 404)
    conversation = dict(row)
    if conversation["public_token"] != token_hash:
        db.execute(
            text("UPDATE conversations SET public_token=:token_hash WHERE id=:id"),
            {"token_hash": token_hash, "id": conversation["id"]},
        )
        db.commit()
        conversation["public_token"] = token_hash
    return conversation


def _authorize(conversation: dict[str, object], user: dict[str, object] | None) -> None:
    customer_id = conversation.get("customer_id")
    if customer_id is None:
        return
    if user is None or int(user["id"]) != int(customer_id):
        raise ApiError("Conversation not found.", "NOT_FOUND", 404)


@router.post("", status_code=201)
def start(payload: ChatStartInput, request: Request, db: DbSession) -> Response:
    user = optional_user(request, db)
    limiter.hit(f"chat-start:{client_ip(request)}", 10, 3600)
    now = datetime.now(UTC)
    token = secrets.token_hex(32)
    token_hash = hash_secret(token)
    result = db.execute(
        text(
            "INSERT INTO conversations(public_token,customer_id,guest_name,guest_email,status,last_message_at,created_at,updated_at) "
            "VALUES (:token,:customer_id,:name,:email,'open',:now,:now,:now) RETURNING id"
        ),
        {
            "token": token_hash,
            "customer_id": None if user is None else user["id"],
            "name": payload.name,
            "email": None if payload.email is None else str(payload.email),
            "now": now,
        },
    )
    conversation_id = int(result.scalar_one())
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
    return success(
        request,
        conversation_dict(db, _find(db, token), access_token=token),
        "Conversation started.",
        201,
    )


@router.get("/{token}")
def show(token: str, request: Request, db: DbSession) -> Response:
    conversation = _find(db, token)
    _authorize(conversation, optional_user(request, db))
    return success(request, conversation_dict(db, conversation, access_token=token))


@router.post("/{token}")
def reply(token: str, payload: ChatReplyInput, request: Request, db: DbSession) -> Response:
    conversation = _find(db, token)
    now = datetime.now(UTC)
    user = optional_user(request, db)
    _authorize(conversation, user)
    if conversation["status"] == "closed":
        raise ApiError("Conversation is closed.", "CONVERSATION_CLOSED", 409)
    limiter.hit(f"chat-reply:{hash_secret(token)}:{client_ip(request)}", 30, 60)
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
    return success(
        request,
        conversation_dict(db, _find(db, token), access_token=token),
        "Message sent.",
    )
