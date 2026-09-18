from __future__ import annotations

import pytest

from app.adapters.api.contracts.generation_request_mapper import parse_generation_payload
from app.core.domain.exceptions import InvalidFrameError
from app.core.domain.frame import BioFrame
from app.core.domain.models import Frame


def test_standard_payload_without_frame_type_is_rejected_even_when_person_like() -> None:
    payload = {
        "subject": {
            "name": "Marie Curie",
            "qid": "Q7186",
        }
    }

    with pytest.raises(InvalidFrameError, match="frame_type"):
        parse_generation_payload(payload, "en")


def test_explicit_bio_frame_type_is_accepted() -> None:
    frame = parse_generation_payload(
        {
            "frame_type": "bio",
            "subject": {"name": "Marie Curie", "qid": "Q7186"},
        },
        "en",
    )

    assert isinstance(frame, BioFrame)
    assert frame.frame_type == "bio"
    assert frame.subject.name == "Marie Curie"


def test_explicit_person_alias_is_normalized_to_bio() -> None:
    frame = parse_generation_payload(
        {
            "frame_type": "entity.person",
            "name": "Marie Curie",
            "profession": "physicist",
        },
        "en",
    )

    assert isinstance(frame, BioFrame)
    assert frame.frame_type == "bio"
    assert frame.subject.name == "Marie Curie"
    assert frame.subject.profession == "physicist"


def test_legacy_type_key_remains_an_explicit_http_boundary_alias() -> None:
    frame = parse_generation_payload(
        {
            "type": "person",
            "name": "Marie Curie",
        },
        "en",
    )

    assert isinstance(frame, BioFrame)
    assert frame.frame_type == "bio"


def test_nonempty_custom_frame_type_is_not_blocked_by_an_http_allowlist() -> None:
    frame = parse_generation_payload(
        {
            "frame_type": "custom.experimental",
            "subject": {"name": "Marie Curie"},
        },
        "en",
    )

    assert isinstance(frame, Frame)
    assert frame.frame_type == "custom.experimental"
