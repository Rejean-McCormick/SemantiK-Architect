from __future__ import annotations

import pytest

from app.adapters.api.contracts.generation_request_mapper import (
    map_generation_request,
    parse_generation_payload,
)
from app.core.domain.exceptions import InvalidFrameError
from app.core.domain.frame import BioFrame


def test_canonical_bio_payload_is_accepted() -> None:
    frame = parse_generation_payload(
        {"frame_type": "bio", "subject": {"name": "Marie Curie", "qid": "Q7186"}},
        "en",
    )
    assert isinstance(frame, BioFrame)
    assert frame.frame_type == "bio"
    assert frame.name == "Marie Curie"


def test_missing_frame_type_is_rejected() -> None:
    with pytest.raises(InvalidFrameError, match="frame_type"):
        parse_generation_payload({"subject": {"name": "Marie Curie"}}, "en")


@pytest.mark.parametrize("retired", ["entity.person", "person", "biography"])
def test_retired_bio_aliases_are_rejected(retired: str) -> None:
    with pytest.raises(InvalidFrameError, match="Retired"):
        parse_generation_payload(
            {"frame_type": retired, "subject": {"name": "Marie Curie"}},
            "en",
        )


def test_top_level_type_alias_is_rejected() -> None:
    with pytest.raises(InvalidFrameError, match="Unsupported field 'type'"):
        map_generation_request(
            {"type": "bio", "subject": {"name": "Marie Curie"}},
            path_lang_code="en",
        )


def test_flat_bio_fields_are_rejected() -> None:
    with pytest.raises(InvalidFrameError, match="nested subject"):
        parse_generation_payload(
            {"frame_type": "bio", "name": "Marie Curie"},
            "en",
        )


def test_renderer_specific_fields_are_rejected() -> None:
    with pytest.raises(InvalidFrameError, match="Renderer-specific"):
        map_generation_request(
            {"frame_type": "bio", "subject": {"name": "Marie Curie"}, "backend": "gf"},
            path_lang_code="en",
        )
