from __future__ import annotations

import pytest

from app.core.domain.frame import BioFrame
from app.core.domain.models import SurfaceResult
from app.core.domain.planning.construction_plan import ConstructionPlan
from app.core.use_cases.generate_text import GenerateText


class Caps:
    async def supports(self, code: str) -> bool:
        return code in {"en", "fr"}
    async def list_codes(self) -> list[str]:
        return ["en", "fr"]


class Realizer:
    async def realize(self, plan: ConstructionPlan) -> SurfaceResult:
        return SurfaceResult(
            text="Ada Lovelace est une mathématicienne britannique.", lang_code=plan.lang_code,
            construction_id=plan.construction_id, renderer_backend="family",
            fallback_used=False,
            tokens=["Ada","Lovelace","est","une","mathématicienne","britannique."],
            debug_info={}, generation_time_ms=1.0,
        )


@pytest.mark.asyncio
async def test_generate_text_french_is_planner_first() -> None:
    frame = BioFrame(frame_type="bio", subject={"name":"Ada Lovelace","profession":"mathématicienne","nationality":"britannique"})
    result = await GenerateText(realizer=Realizer(), capabilities=Caps()).execute("fr", frame)
    assert isinstance(result, SurfaceResult)
    assert result.lang_code == "fr"
    assert result.debug_info["runtime_path"] == "planner_first"
