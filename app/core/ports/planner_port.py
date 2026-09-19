from __future__ import annotations

from typing import Any, Protocol, Sequence, runtime_checkable

from app.core.domain.planning.planned_sentence import PlannedSentence


@runtime_checkable
class PlannerPort(Protocol):
    """Canonical planner boundary: semantic frames -> PlannedSentence list."""

    def plan(
        self,
        frames: Sequence[Any],
        *,
        lang_code: str,
        domain: str = "auto",
    ) -> list[PlannedSentence]:
        ...


__all__ = ["PlannerPort"]
