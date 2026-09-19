from __future__ import annotations

from typing import Literal, Protocol, runtime_checkable

from app.core.domain.models import SurfaceResult
from app.core.domain.planning.construction_plan import ConstructionPlan

RealizerSupportStatus = Literal["full", "partial", "fallback_only", "unsupported"]


@runtime_checkable
class RealizerPort(Protocol):
    """Canonical renderer boundary: ConstructionPlan -> SurfaceResult."""

    async def realize(self, construction_plan: ConstructionPlan) -> SurfaceResult:
        ...


@runtime_checkable
class RealizerCapabilitiesPort(RealizerPort, Protocol):
    def supports(self, construction_id: str, lang_code: str) -> bool:
        ...

    def get_support_status(
        self, construction_id: str, lang_code: str
    ) -> RealizerSupportStatus:
        ...


__all__ = ["RealizerSupportStatus", "RealizerPort", "RealizerCapabilitiesPort"]
