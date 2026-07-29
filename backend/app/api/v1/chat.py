import asyncio
import json

import httpx
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_token
from app.repositories.message_repository import MessageRepository
from app.repositories.user_repository import UserRepository

router = APIRouter(prefix="/chat", tags=["chat"])

# Chunk size for simulated streaming — words per send.
# Agentic returns a full answer at once; we re-chunk it so the frontend
# receives a progressive stream rather than one large payload.
_WORDS_PER_CHUNK = 4


async def _call_agentic(session_id: str, question: str) -> dict:
    """POST to Agentic /chat and return the parsed JSON response."""
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            f"{settings.AI_SERVICE_URL}/chat",
            json={"session_id": session_id, "question": question},
        )
        response.raise_for_status()
        return response.json()


async def _stream_answer(websocket: WebSocket, answer: str) -> None:
    """Send answer to the client in small word chunks then signal [DONE]."""
    words = answer.split()
    for i in range(0, len(words), _WORDS_PER_CHUNK):
        chunk = " ".join(words[i : i + _WORDS_PER_CHUNK])
        # Preserve spacing so the frontend can concatenate chunks naturally.
        await websocket.send_text(chunk + " ")
        await asyncio.sleep(0.03)
    await websocket.send_text("[DONE]")


@router.websocket("/stream")
async def chat_stream(
    websocket: WebSocket,
    token: str = Query(...),
    conversation_id: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    # --- Auth ---
    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    repo = UserRepository(db)
    user = await repo.get_by_id(payload.get("sub"))
    if user is None or not user.is_active:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Stable session_id scoped to user + conversation so Agentic memory
    # is isolated per conversation rather than per user globally.
    session_id = f"{user.id}_{conversation_id or 'default'}"
    msg_repo = MessageRepository(db)

    await websocket.accept()

    try:
        while True:
            question = await websocket.receive_text()

            if question.strip() == "[STOP]":
                await websocket.send_text("[DONE]")
                continue

            # Persist user message
            if conversation_id:
                await msg_repo.create(conversation_id, "user", question)

            # Call Agentic
            try:
                result = await _call_agentic(session_id, question)
                answer = result.get("answer") or "I was unable to generate a response."
            except httpx.HTTPStatusError as exc:
                answer = f"AI service error ({exc.response.status_code}). Please try again."
            except httpx.RequestError:
                answer = "Could not reach the AI service. Please check that it is running."

            # Persist assistant message
            if conversation_id:
                await msg_repo.create(conversation_id, "assistant", answer)

            # Stream answer back to client
            await _stream_answer(websocket, answer)

    except WebSocketDisconnect:
        pass
