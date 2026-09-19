from __future__ import annotations

import pytest

from app.core.domain.frame import BioFrame
from app.core.domain.planning.planned_sentence import PlannedSentence
from app.core.use_cases.plan_text import PlanText


@pytest.mark.asyncio
async def test_plan_text_returns_canonical_planned_sentence() -> None:
    frame = BioFrame(frame_type="bio", subject={"name": "Alan Turing", "profession": "mathematician"})
    result = await PlanText().execute_one("en", frame)
    assert isinstance(result, PlannedSentence)
    assert result.lang_code == "en"
    assert result.construction_id == "copula_equative_classification"
    assert result.frame is not None
