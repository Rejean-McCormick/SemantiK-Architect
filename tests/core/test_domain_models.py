from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.core.domain.frame import BaseFrame, BioFrame, EventFrame, Frame, RelationalFrame
from app.core.domain.models import LexiconEntry, SurfaceResult


def test_generic_frame_requires_explicit_frame_type() -> None:
    with pytest.raises(ValidationError):
        Frame(subject={"name": "X"})


def test_generic_frame_preserves_explicit_custom_family() -> None:
    frame = Frame(
        frame_type="custom.experimental",
        subject={"name": "X", "qid": "Q1"},
        properties={"foo": "bar"},
    )
    assert frame.frame_type == "custom.experimental"
    assert frame.subject == {"name": "X", "qid": "Q1"}
    assert frame.properties == {"foo": "bar"}


def test_bio_frame_requires_nested_subject_and_canonical_type() -> None:
    frame = BioFrame(
        frame_type="bio",
        subject={"name": "Marie Curie", "qid": "Q7186", "profession": "physicist"},
    )
    assert frame.frame_type == "bio"
    assert frame.name == "Marie Curie"
    assert frame.qid == "Q7186"
    assert frame.profession == "physicist"

    with pytest.raises(ValidationError):
        BioFrame(frame_type="bio", name="Marie Curie")
    with pytest.raises(ValidationError):
        BioFrame(frame_type="entity.person", subject={"name": "Marie Curie"})


def test_event_frame_uses_canonical_fields_only() -> None:
    frame = EventFrame(
        frame_type="event",
        subject={"name": "Ada Lovelace"},
        event_object="Analytical Engine",
        event_type="work",
    )
    assert frame.event_type == "work"
    assert frame.event_object == "Analytical Engine"


def test_relational_frame_uses_canonical_object_field() -> None:
    frame = RelationalFrame(
        frame_type="relational",
        subject={"name": "Marie Curie"},
        relation="spouse_of",
        object={"name": "Pierre Curie"},
    )
    assert frame.relation == "spouse_of"
    assert frame.object.name == "Pierre Curie"


def test_surface_result_synchronizes_debug_contract() -> None:
    result = SurfaceResult(
        text="Bonjour.",
        lang_code="FR",
        construction_id="copula_equative_simple",
        renderer_backend="family",
        fallback_used=False,
        tokens=["Bonjour."],
        debug_info={"slot_keys": ["subject"]},
        generation_time_ms=3.0,
    )
    assert result.lang_code == "fr"
    assert result.debug_info["runtime_path"] == "planner_first"
    assert result.debug_info["construction_id"] == result.construction_id
    assert result.debug_info["renderer_backend"] == result.renderer_backend
    assert result.debug_info["fallback_used"] is False
    assert result.debug_info["tokens"] == ["Bonjour."]


def test_surface_result_requires_complete_contract() -> None:
    with pytest.raises(ValidationError):
        SurfaceResult(text="Hello", lang_code="en")
    with pytest.raises(ValidationError):
        SurfaceResult(
            text="Hello",
            lang_code="en",
            construction_id="copula_equative_simple",
            renderer_backend="family",
            fallback_used=False,
            tokens=[],
            debug_info={},
            generation_time_ms=1.0,
        )


def test_lexicon_entry_contract() -> None:
    entry = LexiconEntry(
        lemma="chat",
        pos="N",
        language="fr",
        source="wikidata",
        confidence=0.75,
    )
    assert entry.lemma == "chat"
    assert entry.language == "fr"
    assert entry.confidence == 0.75

    with pytest.raises(ValidationError):
        LexiconEntry(lemma="chat", pos="N", confidence=1.5)
