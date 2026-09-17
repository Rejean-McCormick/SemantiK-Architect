from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass

from app.core.domain.context import SessionContext


@dataclass(slots=True)
class _StoredSession:
    context: SessionContext
    expires_at: float


class InMemorySessionStore:
    """Process-local discourse session storage for the runtime API.

    SemantiK Architect no longer depends on Redis. Session state is deliberately
    ephemeral: it survives requests handled by the same API process, but not
    process restarts and not cross-process/load-balanced deployments.
    """

    def __init__(self, *, ttl_seconds: int = 3600, max_entries: int = 1024) -> None:
        self.ttl_seconds = max(1, int(ttl_seconds))
        self.max_entries = max(1, int(max_entries))
        self._items: dict[str, _StoredSession] = {}
        self._lock = asyncio.Lock()

    @staticmethod
    def _copy_context(context: SessionContext) -> SessionContext:
        return SessionContext.model_validate(context.model_dump())

    def _prune_expired(self, now: float) -> None:
        expired = [key for key, value in self._items.items() if value.expires_at <= now]
        for key in expired:
            self._items.pop(key, None)

    async def get_session(self, session_id: str) -> SessionContext:
        key = str(session_id or "").strip()
        if not key:
            raise ValueError("session_id must be a non-empty string")

        now = time.monotonic()
        async with self._lock:
            self._prune_expired(now)
            stored = self._items.get(key)
            if stored is None:
                return SessionContext(session_id=key)
            return self._copy_context(stored.context)

    async def save_session(self, context: SessionContext) -> None:
        now = time.monotonic()
        async with self._lock:
            self._prune_expired(now)

            if context.session_id not in self._items and len(self._items) >= self.max_entries:
                oldest_key = min(
                    self._items,
                    key=lambda key: self._items[key].expires_at,
                )
                self._items.pop(oldest_key, None)

            self._items[context.session_id] = _StoredSession(
                context=self._copy_context(context),
                expires_at=now + self.ttl_seconds,
            )

    async def clear(self) -> None:
        async with self._lock:
            self._items.clear()


session_store = InMemorySessionStore()
