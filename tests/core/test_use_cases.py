from unittest.mock import AsyncMock, MagicMock
import pytest

from app.core.domain.models import Frame, Sentence
from app.core.use_cases.generate_text import GenerateText


@pytest.mark.asyncio
async def test_generate_text_uses_runtime_engine():
    engine = MagicMock()
    engine.generate = AsyncMock(return_value=Sentence(text="runtime output", lang_code="eng"))
    use_case = GenerateText(engine=engine)
    frame = Frame(frame_type="bio", subject={"name": "Ada Lovelace"}, properties={})
    result = await use_case.execute("eng", frame)
    assert getattr(result, "text", "") == "runtime output"
    assert engine.generate.called
