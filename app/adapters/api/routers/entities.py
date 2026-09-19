from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class EntitySummary(BaseModel):
    """Minimal entity summary used by the runtime UI."""

    id: str
    label: str
    description: Optional[str] = None
    type: str


@router.get("/", response_model=List[EntitySummary])
async def list_entities() -> List[EntitySummary]:
    """Return runtime entity history when available.

    SemantiK does not pretend to own a persistent entity catalogue. Session state
    is ephemeral and generation-driven; until a dedicated history projection is
    wired here, the truthful response is an empty collection.
    """

    return []
