from __future__ import annotations

import pytest

from app.core.domain.exceptions import LexicalResolutionError, RealizationError
from app.core.domain.models import SurfaceResult
from app.core.domain.planning.construction_plan import ConstructionPlan
from app.core.use_cases.realize_text import RealizeText


class FakeRealizer:
    async def realize(self, plan: ConstructionPlan) -> SurfaceResult:
        return SurfaceResult(
            text="Alan Turing is a mathematician.",
            lang_code=plan.lang_code,
            construction_id=plan.construction_id,
            renderer_backend="family",
            fallback_used=False,
            tokens=["Alan", "Turing", "is", "a", "mathematician."],
            debug_info={},
            generation_time_ms=1.0,
        )


class FakeResolver:
    async def resolve_plan(self, *, construction_plan: ConstructionPlan) -> ConstructionPlan:
        return construction_plan


@pytest.mark.asyncio
async def test_realize_text_enforces_surface_result_contract() -> None:
    plan = ConstructionPlan(
        construction_id="copula_equative_classification",
        lang_code="en",
        slot_map={"subject": "Alan Turing", "profession": "mathematician"},
    )
    result = await RealizeText(FakeRealizer(), FakeResolver()).execute(plan)
    assert isinstance(result, SurfaceResult)
    assert result.debug_info["runtime_path"] == "planner_first"
    assert result.generation_time_ms >= 0


@pytest.mark.asyncio
async def test_realizer_must_return_surface_result() -> None:
    class Bad:
        async def realize(self, plan):
            return {"text": "bad"}
    plan = ConstructionPlan(
        construction_id="copula_equative_classification",
        lang_code="en",
        slot_map={"subject": "Alan Turing"},
    )
    with pytest.raises(RealizationError, match="SurfaceResult"):
        await RealizeText(Bad()).execute(plan)
