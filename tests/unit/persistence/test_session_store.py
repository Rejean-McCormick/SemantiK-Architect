from __future__ import annotations

import pytest

from app.adapters.persistence.session_store import InMemorySessionStore
from app.core.domain.context import DiscourseEntity, SessionContext


@pytest.mark.asyncio
async def test_missing_session_returns_fresh_context() -> None:
    store = InMemorySessionStore(ttl_seconds=60, max_entries=4)
    context = await store.get_session("demo")
    assert context.session_id == "demo"
    assert context.current_focus is None


@pytest.mark.asyncio
async def test_saved_session_round_trips_without_shared_mutation() -> None:
    store = InMemorySessionStore(ttl_seconds=60, max_entries=4)
    original = SessionContext(session_id="demo")
    original.update_focus(DiscourseEntity(label="Marie Curie", gender="f", qid="Q7186"))
    await store.save_session(original)

    loaded = await store.get_session("demo")
    assert loaded.current_focus is not None
    assert loaded.current_focus.qid == "Q7186"

    loaded.current_focus.label = "changed locally"
    reloaded = await store.get_session("demo")
    assert reloaded.current_focus is not None
    assert reloaded.current_focus.label == "Marie Curie"


@pytest.mark.asyncio
async def test_store_evicts_when_capacity_is_reached() -> None:
    store = InMemorySessionStore(ttl_seconds=60, max_entries=1)
    await store.save_session(SessionContext(session_id="first"))
    await store.save_session(SessionContext(session_id="second"))

    second = await store.get_session("second")
    assert second.session_id == "second"
