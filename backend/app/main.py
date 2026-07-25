from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.v1 import auth, conversations, messages, users, documents, chat
from app.api.v1 import agent_tools, api_keys, audit_logs, analytics

app = FastAPI(title="Agentic Chatbot Platform - Backend")

API_V1_PREFIX = "/api/v1"

# Rate limiting is applied per-route in auth.py, not at router level
app.include_router(auth.router, prefix=API_V1_PREFIX)

# Core CRUD
app.include_router(conversations.router, prefix=API_V1_PREFIX)
app.include_router(messages.router, prefix=API_V1_PREFIX)
app.include_router(users.router, prefix=API_V1_PREFIX)
app.include_router(documents.router, prefix=API_V1_PREFIX)

# Config/tooling
app.include_router(agent_tools.router, prefix=API_V1_PREFIX)
app.include_router(api_keys.router, prefix=API_V1_PREFIX)

# Observability
app.include_router(audit_logs.router, prefix=API_V1_PREFIX)
app.include_router(analytics.router, prefix=API_V1_PREFIX)

# WebSocket
app.include_router(chat.router, prefix=API_V1_PREFIX)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/health/db")
async def health_db(db: AsyncSession = Depends(get_db)):
    await db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}