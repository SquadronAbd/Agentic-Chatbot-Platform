from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings

from app.core.database import get_db
from app.api.v1 import auth, conversations, messages, users, documents, chat
from app.api.v1 import agent_tools, api_keys, audit_logs, analytics
from app.api.v1.internal import documents as internal_documents

app = FastAPI(title="Agentic Chatbot Platform - Backend")

# CORS — allow the Next.js dev server (port 3000) and any localhost origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Internal maintenance (service-to-service)
app.include_router(internal_documents.router, prefix=API_V1_PREFIX)

# WebSocket
app.include_router(chat.router, prefix=API_V1_PREFIX)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/health/db")
async def health_db(db: AsyncSession = Depends(get_db)):
    await db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}