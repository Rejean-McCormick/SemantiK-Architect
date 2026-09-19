from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from app.core.domain.planning.construction_plan import ConstructionPlan


@dataclass(frozen=True, slots=True)
class ResolutionResult:
    """Backend-agnostic result for one lexical slot resolution."""

    slot_name: str
    input_value: Any
    resolved_value: Any
    kind: str = "unknown"
    source: str = "unknown"
    confidence: float = 0.0
    fallback_used: bool = False
    unresolved: bool = False
    surface_hint: str | None = None
    notes: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        confidence = float(self.confidence)
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("ResolutionResult.confidence must be between 0.0 and 1.0")
        object.__setattr__(self, "confidence", confidence)
        object.__setattr__(self, "notes", tuple(self.notes))

    def as_dict(self) -> dict[str, Any]:
        return {
            "slot_name": self.slot_name,
            "input_value": self.input_value,
            "resolved_value": self.resolved_value,
            "kind": self.kind,
            "source": self.source,
            "confidence": self.confidence,
            "fallback_used": self.fallback_used,
            "unresolved": self.unresolved,
            "surface_hint": self.surface_hint,
            "notes": list(self.notes),
            "metadata": dict(self.metadata),
        }


@runtime_checkable
class LexicalResolverPort(Protocol):
    """Canonical lexical boundary: ConstructionPlan -> ConstructionPlan."""

    async def resolve_plan(
        self,
        *,
        construction_plan: ConstructionPlan,
    ) -> ConstructionPlan:
        ...


__all__ = ["ResolutionResult", "LexicalResolverPort"]
