from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.ports import LexiconRepo


@pytest.fixture
def mock_repo():
    repo = MagicMock(spec=LexiconRepo)
    repo.health_check = AsyncMock(return_value=True)
    return repo
