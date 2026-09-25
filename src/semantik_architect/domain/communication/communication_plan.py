from __future__ import annotations

from dataclasses import dataclass
from ..semantics.obligations import CommunicativeForce

@dataclass(frozen=True, slots=True)
class CommunicationPlanItem:
    item_id: str
    obligation_ids: tuple[str,...]
    semantic_refs: tuple[str,...]
    force: CommunicativeForce
    presentation_intent: str

@dataclass(frozen=True, slots=True)
class CommunicationPlan:
    plan_id: str
    items: tuple[CommunicationPlanItem,...]
    source_obligation_ids: tuple[str,...]

    def __post_init__(self)->None:
        object.__setattr__(self,"items",tuple(self.items)); object.__setattr__(self,"source_obligation_ids",tuple(self.source_obligation_ids))
