from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from semantik_architect.adapters.ecosystem.kristal_v6 import KristalV6Acl, KristalV6ProjectionError


def payload():
    return json.loads(Path("examples/kristal_v6_communication_projection.json").read_text(encoding="utf-8"))


def test_kristal_v6_projection_preserves_metadata_without_changing_obligation_force():
    req = KristalV6Acl().map_request(payload(), target_language="fr", target_locale="fr-CA", capability_profile="orgo-operational-1")
    assert req.obligations[0].force.value == "PRESENT"
    assertion_id = payload()["selected_assertions"][0]["assertion_id"]
    assert req.support_values(assertion_id, "kristal-v6:record_role") == ("decision",)
    actionability = req.support_values(assertion_id, "kristal-v6:actionability")[0]
    assert actionability["mode"] == "human_review"
    assert actionability["requires_human_validation"] is True


def test_kristal_v6_projection_requires_selected_assertion_traceability():
    data = payload()
    data["communication_request"]["semantic_graph"]["statements"][0]["source_refs"] = []
    data["communication_request"]["obligations"][0]["source_refs"] = []
    with pytest.raises(KristalV6ProjectionError, match="traceable"):
        KristalV6Acl().map_request(data, target_language="fr", capability_profile="orgo-operational-1")


def test_actionability_never_creates_a_communication_obligation():
    data = payload()
    data["selected_assertions"][0]["actionability"] = {"mode":"automatic", "requires_human_validation":False}
    before = deepcopy(data["communication_request"]["obligations"])
    req = KristalV6Acl().map_request(data, target_language="fr", capability_profile="orgo-operational-1")
    assert data["communication_request"]["obligations"] == before
    assert len(req.obligations) == len(before)
    assert req.obligations[0].force.value == before[0]["force"]


def test_rejects_unknown_actionability_mode():
    data = payload()
    data["selected_assertions"][0]["actionability"] = {"mode":"execute_now"}
    with pytest.raises(KristalV6ProjectionError, match="Unsupported actionability"):
        KristalV6Acl().map_request(data, target_language="fr", capability_profile="orgo-operational-1")


def test_kristal_portable_contract_and_v7_design_baseline_are_explicit():
    assert KristalV6Acl.STANDARD == "6.0.0"
    assert KristalV6Acl.PORTABLE_CONTRACT == "kristal_state/6.0"
    assert KristalV6Acl.KRISTALL_DESIGN_BASELINE == "7.0.0-draft.3.2"
