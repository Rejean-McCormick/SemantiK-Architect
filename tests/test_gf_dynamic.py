from __future__ import annotations

from pathlib import Path

import pytest

from app.adapters.engines.pgf_runtime import PgfRuntime
from app.shared.config import settings


@pytest.fixture(scope="module")
def pgf_runtime() -> PgfRuntime:
    path = Path(settings.PGF_PATH)
    if not path.is_file():
        pytest.fail(f"Canonical runtime PGF missing: {path}")
    return PgfRuntime(str(path))


@pytest.mark.asyncio
async def test_pgf_runtime_loads_canonical_artifact(pgf_runtime: PgfRuntime) -> None:
    status = await pgf_runtime.status()
    assert status["loaded"] is True, status
    assert set(status["concrete_languages"]) >= {"WikiEng", "WikiFre"}


@pytest.mark.asyncio
async def test_pgf_runtime_reports_concrete_languages(pgf_runtime: PgfRuntime) -> None:
    languages = await pgf_runtime.get_concrete_languages()
    assert "WikiEng" in languages
    assert "WikiFre" in languages


def test_pgf_runtime_resolves_application_codes(pgf_runtime: PgfRuntime) -> None:
    assert pgf_runtime.resolve_concrete_name("en") == "WikiEng"
    assert pgf_runtime.resolve_concrete_name("fr") == "WikiFre"
