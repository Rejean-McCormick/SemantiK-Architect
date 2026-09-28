from __future__ import annotations

import json
from pathlib import Path

import pytest

from semantik_architect.adapters.lexical.local_lexicon.json_lexicon import RuntimeJsonLexiconAdapter
from semantik_architect.application.ports.runtime_catalog import RuntimeArtifact, RuntimeSetDescriptor
from semantik_architect.domain.errors import SemantikArchitectError


def _runtime(tmp_path: Path, artifacts: list[tuple[str, dict]], *, precedence=None):
    rows = []
    for artifact_id, payload in artifacts:
        path = tmp_path / f"{artifact_id}.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        rows.append(RuntimeArtifact("lexical", artifact_id, "0" * 64, path))
    policy = {
        "policy_version": "1.0",
        "precedence": precedence
        or ["request_override", "domain", "project", "wikidata", "gf_generic"],
        "default_source_kind": "project",
        "equal_precedence_conflict": "fail",
    }
    return RuntimeSetDescriptor(
        "rt", "1.0", "RELEASED", tuple(rows), {}, {"lexical_policy": policy}, tmp_path
    )


def test_wikidata_knowledge_beats_gf_generic_but_gf_can_bind(tmp_path):
    wikidata = {
        "schema_version": "1.1",
        "lexicon_id": "wd",
        "source_kind": "wikidata",
        "entries": [
            {
                "semantic_ref": "wikidata:Q1",
                "language": "fr",
                "lexical_ref": "wikidata:L1-S1",
                "binding_kind": "lexeme_ref",
                "use_for": "knowledge",
                "sense_ref": "wikidata:L1-S1",
                "properties": {"lemma": "chien"},
            }
        ],
    }
    gf = {
        "schema_version": "1.1",
        "lexicon_id": "gf",
        "source_kind": "gf_generic",
        "entries": [
            {
                "semantic_ref": "wikidata:Q1",
                "language": "fr",
                "lexical_ref": "chien_N",
                "binding_kind": "gf_expr",
                "use_for": "both",
            }
        ],
    }
    loaded = RuntimeJsonLexiconAdapter()._load(_runtime(tmp_path, [("gf", gf), ("wd", wikidata)]))
    assert loaded.knowledge[("fr", "wikidata:Q1")].source_kind == "wikidata"
    assert loaded.knowledge[("fr", "wikidata:Q1")].lexical_ref == "wikidata:L1-S1"
    assert loaded.bindings[("fr", "wikidata:Q1")].source_kind == "gf_generic"
    assert loaded.bindings[("fr", "wikidata:Q1")].lexical_ref == "chien_N"


def test_project_binding_beats_wikidata_and_gf_generic(tmp_path):
    artifacts = []
    for kind, ref in [
        ("gf_generic", "gf_N"),
        ("wikidata", "wd_N"),
        ("project", "project_N"),
    ]:
        artifacts.append(
            (
                kind,
                {
                    "schema_version": "1.1",
                    "lexicon_id": kind,
                    "source_kind": kind,
                    "entries": [
                        {
                            "semantic_ref": "wikidata:Q1",
                            "language": "fr",
                            "lexical_ref": ref,
                            "binding_kind": "gf_expr",
                            "use_for": "both",
                        }
                    ],
                },
            )
        )
    loaded = RuntimeJsonLexiconAdapter()._load(_runtime(tmp_path, artifacts))
    assert loaded.knowledge[("fr", "wikidata:Q1")].lexical_ref == "project_N"
    assert loaded.bindings[("fr", "wikidata:Q1")].lexical_ref == "project_N"


def test_equal_precedence_conflict_fails_closed(tmp_path):
    a = {
        "schema_version": "1.1",
        "lexicon_id": "a",
        "source_kind": "project",
        "entries": [{"semantic_ref": "x:1", "language": "fr", "lexical_ref": "a_N"}],
    }
    b = {
        "schema_version": "1.1",
        "lexicon_id": "b",
        "source_kind": "project",
        "entries": [{"semantic_ref": "x:1", "language": "fr", "lexical_ref": "b_N"}],
    }
    with pytest.raises(SemantikArchitectError) as exc:
        RuntimeJsonLexiconAdapter()._load(_runtime(tmp_path, [("a", a), ("b", b)]))
    assert exc.value.envelope.code == "SA-LEX-003"
