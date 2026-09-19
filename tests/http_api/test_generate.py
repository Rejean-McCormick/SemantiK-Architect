from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient

from app.adapters.api.dependencies import get_generate_text_use_case
from app.adapters.api.main import create_app
from app.core.domain.exceptions import LanguageNotFoundError
from app.core.domain.models import SurfaceResult


class StubGenerateTextUseCase:
    def __init__(self, result: Any):
        self.result = result
        self.calls: list[tuple[str, Any]] = []

    async def execute(self, lang_code: str, frame: Any) -> Any:
        self.calls.append((lang_code, frame))
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


def make_client(use_case: Any) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_generate_text_use_case] = lambda: use_case
    return TestClient(app)


def canonical_result(lang: str = "en") -> SurfaceResult:
    return SurfaceResult(
        text="Marie Curie is a Polish physicist.",
        lang_code=lang,
        construction_id="copula_equative_classification",
        renderer_backend="family",
        fallback_used=False,
        tokens=["Marie", "Curie", "is", "a", "Polish", "physicist."],
        debug_info={"runtime_path":"planner_first","slot_keys":["subject","profession","nationality"]},
        generation_time_ms=12.5,
    )


def test_generate_success_uses_canonical_route_and_frame_shape() -> None:
    use_case = StubGenerateTextUseCase(canonical_result())
    with make_client(use_case) as client:
        response = client.post(
            "/api/v1/generate/en",
            json={"frame_type":"bio","subject":{"name":"Marie Curie","qid":"Q7186","profession":"physicist","nationality":"Polish"}},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["lang_code"] == "en"
    assert body["debug_info"]["runtime_path"] == "planner_first"
    assert use_case.calls[0][1].subject.name == "Marie Curie"


def test_generate_without_path_language_is_not_a_route() -> None:
    with make_client(StubGenerateTextUseCase(canonical_result())) as client:
        response = client.post(
            "/api/v1/generate",
            json={"lang_code":"en","frame_type":"bio","subject":{"name":"Marie Curie"}},
        )
    assert response.status_code == 404


def test_missing_frame_type_returns_422() -> None:
    with make_client(StubGenerateTextUseCase(canonical_result())) as client:
        response = client.post("/api/v1/generate/en", json={"subject":{"name":"Marie Curie"}})
    assert response.status_code == 422


def test_retired_entity_person_alias_returns_422() -> None:
    with make_client(StubGenerateTextUseCase(canonical_result())) as client:
        response = client.post("/api/v1/generate/en", json={"frame_type":"entity.person","subject":{"name":"Marie Curie"}})
    assert response.status_code == 422


def test_unknown_language_returns_404() -> None:
    use_case = StubGenerateTextUseCase(LanguageNotFoundError("zzz"))
    with make_client(use_case) as client:
        response = client.post("/api/v1/generate/zzz", json={"frame_type":"bio","subject":{"name":"Marie Curie"}})
    assert response.status_code == 404


def test_non_surface_result_is_server_error() -> None:
    use_case = StubGenerateTextUseCase({"text":"broken"})
    with make_client(use_case) as client:
        response = client.post("/api/v1/generate/en", json={"frame_type":"bio","subject":{"name":"Marie Curie"}})
    assert response.status_code == 500
