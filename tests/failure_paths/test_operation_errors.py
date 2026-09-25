from __future__ import annotations

import pytest

from semantik_architect.domain.errors import SemantikArchitectError
from semantik_architect.domain.language.operations import V1_OPERATION_IDS, require_known_operation


def test_v1_registry_includes_non_factual_discourse_operations() -> None:
    assert "discourse.greeting" in V1_OPERATION_IDS
    assert "discourse.closing" in V1_OPERATION_IDS


def test_known_operation_is_returned_unchanged() -> None:
    assert require_known_operation("clause.transitive_event") == "clause.transitive_event"
    assert require_known_operation("discourse.greeting") == "discourse.greeting"
    assert require_known_operation("discourse.closing") == "discourse.closing"


def test_unknown_operation_uses_stable_language_error_envelope() -> None:
    with pytest.raises(SemantikArchitectError) as caught:
        require_known_operation("unknown.operation")

    assert caught.value.envelope.code == "SA-LANG-003"
