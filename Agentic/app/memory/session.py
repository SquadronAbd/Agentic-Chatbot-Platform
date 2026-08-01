"""
session.py — Redis-backed session manager with in-memory fallback.

Each session is stored in Redis as a JSON blob under the key
`session:<session_id>` with a 24-hour TTL. If Redis is unavailable at
startup (or any time), the manager falls back to an in-process dict so
the service keeps running without degradation.
"""
import json
from loguru import logger

from app.memory.conversation import ConversationMemory, Message
from app.config.settings import settings


def _make_redis():
    """Return a Redis client or None if the connection fails."""
    try:
        import redis as redis_lib
        client = redis_lib.Redis.from_url(settings.REDIS_URL, decode_responses=True)
        client.ping()
        logger.info("SessionManager: Redis connected at {}", settings.REDIS_URL)
        return client
    except Exception as exc:
        logger.warning("SessionManager: Redis unavailable ({}), falling back to in-memory", exc)
        return None


_SESSION_TTL = 86_400   # 24 hours
_KEY_PREFIX = "session:"


def _memory_to_dict(memory: ConversationMemory) -> dict:
    return {
        "summary": memory.summary,
        "messages": [{"role": m.role, "content": m.content} for m in memory.messages],
    }


def _dict_to_memory(data: dict) -> ConversationMemory:
    mem = ConversationMemory()
    mem.summary = data.get("summary", "")
    for m in data.get("messages", []):
        mem.messages.append(Message(role=m["role"], content=m["content"]))
    return mem


class SessionManager:
    """
    Manages conversation memories for multiple users/sessions.

    Primary store: Redis (JSON, 24-h TTL per session).
    Fallback store: in-process dict (used when Redis is unavailable).
    """

    def __init__(self):
        self._redis = _make_redis()
        self._local: dict[str, ConversationMemory] = {}   # fallback

    # ── internal helpers ─────────────────────────────────────────────────────

    def _load(self, session_id: str) -> ConversationMemory | None:
        if self._redis is None:
            return self._local.get(session_id)
        try:
            raw = self._redis.get(f"{_KEY_PREFIX}{session_id}")
            return _dict_to_memory(json.loads(raw)) if raw else None
        except Exception as exc:
            logger.warning("Redis read failed for {}: {}", session_id, exc)
            return self._local.get(session_id)

    def _save(self, session_id: str, memory: ConversationMemory) -> None:
        if self._redis is None:
            self._local[session_id] = memory
            return
        try:
            self._redis.setex(
                f"{_KEY_PREFIX}{session_id}",
                _SESSION_TTL,
                json.dumps(_memory_to_dict(memory)),
            )
            self._local[session_id] = memory   # keep local copy for same-request reuse
        except Exception as exc:
            logger.warning("Redis write failed for {}: {}", session_id, exc)
            self._local[session_id] = memory

    def _delete(self, session_id: str) -> bool:
        existed = False
        if self._redis is not None:
            try:
                existed = bool(self._redis.delete(f"{_KEY_PREFIX}{session_id}"))
            except Exception as exc:
                logger.warning("Redis delete failed for {}: {}", session_id, exc)
        if session_id in self._local:
            del self._local[session_id]
            existed = True
        return existed

    # ── public API (same interface as before) ────────────────────────────────

    def create_session(self, session_id: str) -> ConversationMemory:
        mem = ConversationMemory()
        self._save(session_id, mem)
        return mem

    def get_memory(self, session_id: str) -> ConversationMemory:
        # Check local cache first to avoid a Redis round-trip within the same request
        if session_id in self._local:
            return self._local[session_id]
        mem = self._load(session_id)
        if mem is None:
            mem = self.create_session(session_id)
        else:
            self._local[session_id] = mem
        return mem

    def save_memory(self, session_id: str, memory: ConversationMemory) -> None:
        """Persist a memory object — call this after mutating conversation history."""
        self._save(session_id, memory)

    def delete_session(self, session_id: str) -> bool:
        return self._delete(session_id)

    def clear_session(self, session_id: str) -> bool:
        mem = self._load(session_id)
        if mem is None:
            return False
        mem.clear()
        self._save(session_id, mem)
        return True

    def session_exists(self, session_id: str) -> bool:
        if session_id in self._local:
            return True
        if self._redis is None:
            return False
        try:
            return bool(self._redis.exists(f"{_KEY_PREFIX}{session_id}"))
        except Exception:
            return False

    def list_sessions(self) -> list[str]:
        if self._redis is None:
            return list(self._local.keys())
        try:
            keys = self._redis.keys(f"{_KEY_PREFIX}*")
            return [k.removeprefix(_KEY_PREFIX) for k in keys]
        except Exception:
            return list(self._local.keys())

    def total_sessions(self) -> int:
        return len(self.list_sessions())


# Module-level singleton — import this everywhere instead of instantiating SessionManager()
session_manager = SessionManager()
