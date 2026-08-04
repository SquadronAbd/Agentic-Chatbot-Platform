import asyncio
import json
import logging
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_token
from app.repositories.message_repository import MessageRepository
from app.repositories.user_repository import UserRepository

router = APIRouter(prefix="/chat", tags=["chat"])

# Chunk size for simulated streaming — words per send.
_WORDS_PER_CHUNK = 4

# Re-validate the JWT every N seconds inside the message loop.
# Keeps the WS from running indefinitely on an expired token.
_TOKEN_RECHECK_INTERVAL = 60


async def _call_agentic(session_id: str, question: str, owner_id: str) -> dict:
    """POST to Agentic /chat and return the parsed JSON response."""
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            f"{settings.AI_SERVICE_URL}/chat",
            json={"session_id": session_id, "question": question, "owner_id": owner_id},
        )
        response.raise_for_status()
        return response.json()


async def _stream_answer(websocket: WebSocket, answer: str) -> None:
    """Send answer to the client in small word chunks then signal [DONE]."""
    words = answer.split()
    for i in range(0, len(words), _WORDS_PER_CHUNK):
        chunk = " ".join(words[i : i + _WORDS_PER_CHUNK])
        await websocket.send_text(chunk + " ")
        await asyncio.sleep(0.03)
    await websocket.send_text("[DONE]")


def _token_expired(payload: dict) -> bool:
    """Return True if the JWT exp claim has passed."""
    exp = payload.get("exp")
    if exp is None:
        return False
    return datetime.now(timezone.utc).timestamp() > exp


@router.websocket("/stream")
async def chat_stream(
    websocket: WebSocket,
    token: str = Query(...),
    conversation_id: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    # --- Initial auth ---
    jwt_payload = decode_token(token)
    if jwt_payload is None or jwt_payload.get("type") != "access":
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    repo = UserRepository(db)
    user = await repo.get_by_id(jwt_payload.get("sub"))
    if user is None or not user.is_active:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    session_id = f"{user.id}_{conversation_id or 'default'}"
    msg_repo = MessageRepository(db)
    last_token_check = datetime.now(timezone.utc).timestamp()

    await websocket.accept()
    logger.info("WS accepted for user=%s conv=%s", user.id, conversation_id)

    try:
        while True:
            # Re-validate token periodically so expired sessions are closed.
            now = datetime.now(timezone.utc).timestamp()
            if now - last_token_check >= _TOKEN_RECHECK_INTERVAL:
                if _token_expired(jwt_payload):
                    await websocket.send_text("[AUTH_EXPIRED]")
                    await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                    return
                last_token_check = now

            raw = await websocket.receive_text()
            logger.info("WS message received (%d bytes)", len(raw))

            if raw.strip() == "[STOP]":
                await websocket.send_text("[DONE]")
                continue

            # Accept either plain text or JSON {question, conversation_id}.
            # JSON lets the client pass a per-message conversation_id so the
            # WebSocket doesn't need to reconnect every time the active chat changes.
            msg_conv_id = conversation_id
            question = raw
            try:
                msg_payload = json.loads(raw)
                question = msg_payload.get("question", raw)
                msg_conv_id = msg_payload.get("conversation_id") or conversation_id
            except (json.JSONDecodeError, AttributeError):
                pass

            logger.info("WS question=%r conv=%s", question[:80], msg_conv_id)
            session_id = f"{user.id}_{msg_conv_id or 'default'}"

            if msg_conv_id:
                try:
                    await msg_repo.create(msg_conv_id, "user", question)
                except Exception as db_err:
                    logger.error("DB error saving user message: %s", db_err)

            try:
                result = await _call_agentic(session_id, question, str(user.id))
                answer = result.get("answer") or "I was unable to generate a response."
            except httpx.HTTPStatusError as exc:
                logger.error("Agentic HTTP error %s: %s", exc.response.status_code, exc.response.text)
                answer = f"AI service error ({exc.response.status_code}). Please try again."
            except httpx.RequestError as req_err:
                logger.error("Agentic request error: %s", req_err)
                answer = "Could not reach the AI service. Please check that it is running."
            except Exception as exc:
                logger.error("Unexpected error calling agentic: %s", exc)
                answer = "An unexpected error occurred. Please try again."

            if msg_conv_id:
                try:
                    await msg_repo.create(msg_conv_id, "assistant", answer)
                except Exception as db_err:
                    logger.error("DB error saving assistant message: %s", db_err)

            await _stream_answer(websocket, answer)

    except WebSocketDisconnect:
        logger.info("WS disconnected for user=%s", user.id)
    except Exception as exc:
        logger.error("Unhandled WS error for user=%s: %s", user.id, exc)
