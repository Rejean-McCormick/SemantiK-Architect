from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Mapping

from .references import require_local_id, require_semantic_ref


class CommunicativeForce(StrEnum):
    ASSERT = "ASSERT"
    ASK = "ASK"
    DIRECT = "DIRECT"
    PRESENT = "PRESENT"


class OrderingMode(StrEnum):
    FIXED = "FIXED"
    POLICY = "POLICY"
    FREE = "FREE"


@dataclass(frozen=True, slots=True)
class CommunicationObligation:
    obligation_id: str
    semantic_refs: tuple[str, ...]
    force: CommunicativeForce
    ordering: OrderingMode = OrderingMode.FREE
    ordering_policy_ref: str | None = None
    visibility_requirements: tuple[str, ...] = ()
    source_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        require_local_id(self.obligation_id, "obligation_id")
        object.__setattr__(self, "semantic_refs", tuple(self.semantic_refs))
        object.__setattr__(self, "visibility_requirements", tuple(self.visibility_requirements))
        object.__setattr__(self, "source_refs", tuple(self.source_refs))
        if not self.semantic_refs:
            raise ValueError("CommunicationObligation.semantic_refs must not be empty")
        for ref in self.semantic_refs:
            require_local_id(ref, "semantic_refs item")
        if self.ordering_policy_ref:
            require_semantic_ref(self.ordering_policy_ref, "ordering_policy_ref")
        for ref in self.visibility_requirements:
            require_semantic_ref(ref,"visibility_requirement")


def obligation_from_dict(data: Mapping[str, Any]) -> CommunicationObligation:
    return CommunicationObligation(
        obligation_id=str(data["obligation_id"]),
        semantic_refs=tuple(str(x) for x in data.get("semantic_refs", ())),
        force=CommunicativeForce(str(data["force"])),
        ordering=OrderingMode(str(data.get("ordering") or "FREE")),
        ordering_policy_ref=data.get("ordering_policy_ref"),
        visibility_requirements=tuple(str(x) for x in data.get("visibility_requirements", ())),
        source_refs=tuple(str(x) for x in data.get("source_refs", ())),
    )
