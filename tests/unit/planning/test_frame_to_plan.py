from __future__ import annotations

import pytest

from app.core.bridges.frame_to_plan import (
    FrameToPlanBridge,
    FrameToPlanError,
    frame_to_plan,
    frames_to_plans,
)
from app.core.domain.frame import BioFrame, EventFrame, Frame, RelationalFrame
from app.core.domain.planning.planned_sentence import PlannedSentence


def test_bio_frame_maps_to_canonical_classification_plan() -> None:
    frame = BioFrame(
        frame_type="bio",
        subject={
            "name": "Ada Lovelace",
            "qid": "Q7259",
            "profession": "mathematician",
            "nationality": "British",
        },
    )
    plan = frame_to_plan(frame, lang_code="en")
    assert isinstance(plan, PlannedSentence)
    assert plan.lang_code == "en"
    assert plan.construction_id == "copula_equative_classification"
    assert plan.metadata["canonical_frame_type"] == "bio"
    assert plan.frame is frame


def test_event_frame_maps_to_event_construction() -> None:
    frame = EventFrame(
        frame_type="event",
        subject={"name": "Ada Lovelace"},
        event_object="Analytical Engine",
        event_type="participation",
    )
    plan = frame_to_plan(frame, lang_code="en")
    assert plan.construction_id == "transitive_event"
    assert plan.metadata["canonical_frame_type"] == "event.generic"


def test_relational_frame_maps_to_relational_planning_family() -> None:
    frame = RelationalFrame(
        frame_type="relational",
        subject={"name": "Ada Lovelace"},
        relation="member_of",
        object={"name": "Royal Society"},
    )
    plan = frame_to_plan(frame, lang_code="en")
    assert plan.metadata["canonical_frame_type"] == "relation.definition"
    assert plan.lang_code == "en"


def test_explicit_custom_frame_type_is_preserved() -> None:
    frame = Frame(frame_type="custom.experimental", subject={"name": "X"})
    plan = frame_to_plan(frame, lang_code="fr")
    assert plan.metadata["canonical_frame_type"] == "custom.experimental"
    assert plan.metadata["original_frame_type"] == "custom.experimental"


def test_batch_planning_preserves_input_order() -> None:
    frames = [
        BioFrame(frame_type="bio", subject={"name": "A", "profession": "one"}),
        BioFrame(frame_type="bio", subject={"name": "B", "profession": "two"}),
    ]
    plans = frames_to_plans(frames, lang_code="en")
    assert [plan.frame.name for plan in plans] == ["A", "B"]
    assert [plan.lang_code for plan in plans] == ["en", "en"]


def test_injected_selector_must_return_canonical_selection_shape() -> None:
    frame = BioFrame(frame_type="bio", subject={"name": "Ada", "profession": "mathematician"})
    bridge = FrameToPlanBridge(selector=lambda *args, **kwargs: {"bad": "shape"})
    with pytest.raises(FrameToPlanError, match="construction_id"):
        bridge.map_frame(frame, lang_code="en")


def test_planner_rejects_missing_frame_type() -> None:
    with pytest.raises(Exception, match="frame_type"):
        frame_to_plan({"subject": {"name": "Ada"}}, lang_code="en")
