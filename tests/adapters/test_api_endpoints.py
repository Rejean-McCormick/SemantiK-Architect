import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.adapters.api.main import create_app
from app.shared.config import settings
from app.core.domain.models import Sentence

API_PREFIX = "/api/v1"


@pytest.fixture
def client(container):
    app = create_app()
    with TestClient(app) as c:
        yield c


class TestGenerationEndpoint:
    def test_generate_success(self, client, mock_grammar_engine):
        mock_grammar_engine.generate.return_value = Sentence(text="Success text", lang_code="eng")
        payload = {"frame_type": "bio", "subject": {"name": "Test"}, "properties": {}}
        headers = {"x-api-key": settings.API_KEY}
        response = client.post(f"{API_PREFIX}/generate/eng", json=payload, headers=headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["text"] == "Success text"

    def test_generate_validation_error(self, client):
        headers = {"x-api-key": settings.API_KEY}
        response = client.post(f"{API_PREFIX}/generate/eng", json={"bad": "data"}, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestHealthEndpoints:
    def test_liveness(self, client):
        response = client.get("/health/live")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "ok"

    def test_readiness_healthy(self, client):
        response = client.get("/health/ready")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"storage": "up", "engine": "up"}

    def test_readiness_engine_unhealthy(self, client, mock_grammar_engine):
        mock_grammar_engine.health_check.return_value = False
        response = client.get("/health/ready")
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert response.json()["engine"] == "down"
