from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.repositories.user_repository import UserRepository

router = APIRouter(prefix="/chat", tags=["chat"])


@router.websocket("/stream")
async def chat_stream(websocket: WebSocket, token: str = Query(...), db: AsyncSession = Depends(get_db)):
    # Auth check: token passed as a query param since WebSocket handshakes
    # don't carry an Authorization header the same way HTTP requests do.
    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    repo = UserRepository(db)
    user = await repo.get_by_id(payload.get("sub"))
    if user is None or not user.is_active:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # PLACEHOLDER: the agent/RAG teammate replaces this echo with real
            # LangGraph invocation — retrieve -> plan -> tool_executor -> respond -> memory_write.
            await websocket.send_text(f"echo: {data}")
    except WebSocketDisconnect:
        pass