from __future__ import annotations

import asyncio

from semantik_architect.adapters.lexical.common.normalization import (
    NormalizationOptions,
    build_normalized_index_with_collisions,
    normalize_for_lookup,
)
from semantik_architect.adapters.lexical.local_wikidata.lexeme_dump import (
    lexeme_from_wikidata_record,
)
from semantik_architect.adapters.realization.gf.pgf_runtime import PgfRuntime


def test_lookup_normalization_is_deterministic_and_unicode_safe():
    assert normalize_for_lookup("  Café—TEST_value\u00a0") == "café-test value"
    assert normalize_for_lookup(
        "Crème brûlée", options=NormalizationOptions(strip_marks=True)
    ) == "creme brulee"


def test_normalized_index_reports_collisions():
    index, collisions = build_normalized_index_with_collisions(
        ["Alpha_Beta", "alpha beta", "Unique"]
    )
    assert index["alpha beta"] == "Alpha_Beta"
    assert collisions["alpha beta"] == ["Alpha_Beta", "alpha beta"]
    assert index["unique"] == "Unique"


def test_wikidata_lexeme_record_is_converted_offline():
    record = {
        "id": "L42",
        "type": "lexeme",
        "lemmas": {"fr": {"language": "fr", "value": "réparer"}},
        "lexicalCategory": "Q36484",
        "senses": [{"wikidataItem": {"id": "Q999"}}],
    }
    entry = lexeme_from_wikidata_record(record, "fr")
    assert entry is not None
    assert entry["lemma"] == "réparer"
    assert entry["pos"] == "VERB"
    assert entry["qid"] == "Q999"
    assert entry["features"]["lexeme_id"] == "L42"


def test_pgf_runtime_reports_unavailable_without_artifact(tmp_path):
    runtime = PgfRuntime(tmp_path / "missing.pgf")
    status = asyncio.run(runtime.status())
    assert status["loaded"] is False
    assert status["concrete_languages"] == []
    assert "not found" in (status["error"] or "").lower() or "unavailable" in (
        status["error"] or ""
    ).lower()
    assert asyncio.run(runtime.health_check()) is False
