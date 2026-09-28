"""Offline Wikidata Lexeme helpers.

Wikidata Lexemes are treated as the default generic lexical *knowledge* source.
They do not replace GF/RGL grammar. Conversion produces knowledge-only lexical
entries unless an upstream build explicitly supplies a GF binding.
"""
from __future__ import annotations

import bz2
import gzip
import json
from pathlib import Path
from typing import Any, Dict, Iterator, Mapping, Optional

DEFAULT_LEXICAL_CATEGORY_MAP: Dict[str, str] = {
    "Q24905": "NOUN",
    "Q34698": "ADJ",
    "Q36484": "VERB",
    "Q380057": "PROPN",
}


def iter_json_records(path: Path) -> Iterator[Mapping[str, Any]]:
    """Stream JSON objects from plain, .gz, or .bz2 NDJSON/JSON-array dumps."""
    if not path.exists():
        raise FileNotFoundError(f"Wikidata dump file not found: {path}")
    if path.suffix == ".gz":
        opener = gzip.open
    elif path.suffix == ".bz2":
        opener = bz2.open
    else:
        opener = open

    with opener(path, "rt", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line in ("[", "]", ","):
                continue
            if line.endswith(","):
                line = line[:-1].rstrip()
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                f.seek(0)
                data = json.load(f)
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict):
                            yield item
                elif isinstance(data, dict):
                    yield data
                return
            if isinstance(obj, dict):
                yield obj
            elif isinstance(obj, list):
                for item in obj:
                    if isinstance(item, dict):
                        yield item


def _is_lexeme_record(record: Mapping[str, Any]) -> bool:
    return (
        record.get("type") == "lexeme"
        or str(record.get("id", "")).startswith("L")
        or "lemmas" in record
    )


def _get_lemma_for_lang(record: Mapping[str, Any], lang_code: str) -> Optional[str]:
    lemmas = record.get("lemmas")
    if not isinstance(lemmas, dict):
        return None
    for code in (lang_code, lang_code.split("-", 1)[0]):
        entry = lemmas.get(code)
        if isinstance(entry, dict):
            value = entry.get("value")
            if isinstance(value, str) and value:
                return value
    return None


def _extract_entity_id_from_snak(snak: Any) -> Optional[str]:
    if not isinstance(snak, dict):
        return None
    value = ((snak.get("datavalue") or {}).get("value"))
    if isinstance(value, dict):
        ident = value.get("id")
        if isinstance(ident, str) and ident.startswith("Q"):
            return ident
        numeric = value.get("numeric-id")
        if isinstance(numeric, int):
            return f"Q{numeric}"
    return None


def _sense_item_qids(sense: Mapping[str, Any]) -> tuple[str, ...]:
    """Return concept QIDs explicitly linked by P5137 (item for this sense)."""
    out: list[str] = []
    claims = sense.get("claims")
    if isinstance(claims, dict):
        for statement in claims.get("P5137", []) or []:
            if not isinstance(statement, dict):
                continue
            qid = _extract_entity_id_from_snak(statement.get("mainsnak"))
            if qid and qid not in out:
                out.append(qid)

    # Backward-compatible fixture/adapter shape used by earlier SA tooling.
    item = sense.get("wikidataItem")
    if (
        isinstance(item, dict)
        and isinstance(item.get("id"), str)
        and item["id"].startswith("Q")
        and item["id"] not in out
    ):
        out.append(item["id"])
    return tuple(out)


def _get_first_sense_qid(record: Mapping[str, Any]) -> Optional[str]:
    senses = record.get("senses")
    if not isinstance(senses, list):
        return None
    for sense in senses:
        if isinstance(sense, dict):
            qids = _sense_item_qids(sense)
            if qids:
                return qids[0]
    return None


def _extract_pos(
    record: Mapping[str, Any],
    lexical_category_map: Optional[Mapping[str, str]],
) -> Optional[str]:
    raw = record.get("lexicalCategory")
    cat_id = None
    if isinstance(raw, dict) and isinstance(raw.get("id"), str):
        cat_id = raw["id"]
    elif isinstance(raw, str):
        cat_id = raw
    if not cat_id:
        return None
    if lexical_category_map and cat_id in lexical_category_map:
        return lexical_category_map[cat_id]
    return DEFAULT_LEXICAL_CATEGORY_MAP.get(cat_id)


def _forms_for_lang(record: Mapping[str, Any], lang_code: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for form in record.get("forms", []) or []:
        if not isinstance(form, dict):
            continue
        reps = form.get("representations") or {}
        representation = None
        if isinstance(reps, dict):
            for code in (lang_code, lang_code.split("-", 1)[0]):
                row = reps.get(code)
                if isinstance(row, dict) and isinstance(row.get("value"), str):
                    representation = row["value"]
                    break
        if not representation:
            continue
        out.append(
            {
                "form_id": form.get("id"),
                "value": representation,
                "grammatical_features": [
                    x
                    for x in (form.get("grammaticalFeatures") or [])
                    if isinstance(x, str)
                ],
            }
        )
    return out


def lexeme_from_wikidata_record(
    record: Mapping[str, Any],
    lang_code: str,
    *,
    lexical_category_map: Optional[Mapping[str, str]] = None,
) -> Optional[Dict[str, Any]]:
    """Legacy compact conversion retained for existing callers."""
    if not _is_lexeme_record(record):
        return None
    lemma = _get_lemma_for_lang(record, lang_code)
    if not lemma:
        return None
    lexeme_id = str(record.get("id") or "")
    return {
        "lemma": lemma,
        "pos": _extract_pos(record, lexical_category_map),
        "qid": _get_first_sense_qid(record),
        "forms": {"default": lemma},
        "features": {"lexeme_id": lexeme_id} if lexeme_id else {},
        "extra": {},
    }


def lexical_artifact_entries_from_wikidata_record(
    record: Mapping[str, Any],
    lang_code: str,
    *,
    lexical_category_map: Optional[Mapping[str, str]] = None,
    semantic_namespace: str = "wikidata",
) -> list[dict[str, Any]]:
    """Convert one Lexeme to SA v1.1 knowledge entries.

    One entry is emitted per explicit sense→Q mapping. These records are
    deliberately ``use_for=knowledge`` and ``binding_kind=lexeme_ref``: a
    Wikidata sense identifier must never masquerade as an executable GF term.
    """
    if not _is_lexeme_record(record):
        return []
    lemma = _get_lemma_for_lang(record, lang_code)
    if not lemma:
        return []
    lexeme_id = str(record.get("id") or "")
    category = _extract_pos(record, lexical_category_map)
    forms = _forms_for_lang(record, lang_code)
    out: list[dict[str, Any]] = []
    senses = record.get("senses")
    if not isinstance(senses, list):
        return out

    for sense in senses:
        if not isinstance(sense, dict):
            continue
        sense_id = str(sense.get("id") or lexeme_id)
        glosses = sense.get("glosses") or {}
        gloss = None
        if isinstance(glosses, dict):
            row = glosses.get(lang_code) or glosses.get(lang_code.split("-", 1)[0])
            if isinstance(row, dict) and isinstance(row.get("value"), str):
                gloss = row["value"]

        for qid in _sense_item_qids(sense):
            prefix = f"{semantic_namespace}:" if semantic_namespace else ""
            out.append(
                {
                    "semantic_ref": f"{prefix}{qid}",
                    "language": lang_code,
                    "lexical_ref": f"wikidata:{sense_id}",
                    "binding_kind": "lexeme_ref",
                    "category": category,
                    "source_kind": "wikidata",
                    "use_for": "knowledge",
                    "source_ref": f"wikidata:{lexeme_id}",
                    "sense_ref": f"wikidata:{sense_id}",
                    "properties": {
                        "lemma": lemma,
                        "lexeme_id": lexeme_id,
                        "sense_id": sense_id,
                        "gloss": gloss,
                        "forms": forms,
                    },
                }
            )
    return out


__all__ = [
    "iter_json_records",
    "lexeme_from_wikidata_record",
    "lexical_artifact_entries_from_wikidata_record",
]
