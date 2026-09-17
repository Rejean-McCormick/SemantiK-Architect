import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient

from app.adapters.api.main import create_app
from app.shared.container import container as global_container
from app.core.domain.frame import BioFrame
from app.core.ports import IGrammarEngine, LexiconRepo


@pytest.fixture(scope="function")
def mock_grammar_engine():
    engine = MagicMock(spec=IGrammarEngine)
    engine.generate = AsyncMock()
    engine.get_supported_languages = AsyncMock(return_value=["eng", "fra"])
    engine.reload = AsyncMock()
    engine.health_check = AsyncMock(return_value=True)
    return engine


@pytest.fixture(scope="function")
def mock_repo():
    repo = MagicMock(spec=LexiconRepo)
    repo.get_entry = AsyncMock(return_value=None)
    repo.save_entry = AsyncMock()
    repo.health_check = AsyncMock(return_value=True)
    return repo


@pytest.fixture(scope="function")
def container(mock_grammar_engine, mock_repo):
    global_container.grammar_engine.override(mock_grammar_engine)
    global_container.lexicon_repository.override(mock_repo)
    yield global_container
    global_container.reset_override()
    global_container.unwire()


@pytest.fixture(scope="function")
def client(container):
    app = create_app()
    with TestClient(app) as c:
        yield c


@pytest.fixture
def sample_frame():
    return BioFrame(
        frame_type="bio",
        subject={"name": "Alan Turing", "qid": "Q7251", "profession": "mathematician"},
        context_id="Q7251",
        meta={"tone": "formal"},
    )
