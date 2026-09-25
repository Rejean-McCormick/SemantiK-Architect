"""Offline parsing helpers for Wikidata Lexeme dump records.

The module performs no network access. It recognizes Lexeme-like JSON records,
extracts language-specific lemmas and coarse lexical categories, and converts a
record into a deterministic adapter-local dictionary suitable for later binding.
"""

from __future__ import annotations

import gzip
import json
from pathlib import Path
from typing import Any, Dict, Iterator, Mapping, Optional, Union

# Minimal POS mapping needed by unit tests (extend as desired)
DEFAULT_LEXICAL_CATEGORY_MAP: Dict[str, str] = {
    "Q24905": "NOUN",  # noun
    "Q34698": "ADJ",   # adjective (common)
    "Q36484": "VERB",  # verb (common)
    "Q380057": "PROPN",  # proper noun (sometimes used)
}


# ---------------------------------------------------------------------------
# Basic helpers
# ---------------------------------------------------------------------------


def _iter_json_records(path: Path) -> Iterator[Mapping[str, Any]]:
    """
    Yield JSON objects from a Wikidata dump file.
    Supports NDJSON, JSON Array (single-line or multi-line), and .gz compression.
    """
    if not path.exists():
        raise FileNotFoundError(f"Wikidata dump file not found: {path}")

    opener = gzip.open if path.suffix == ".gz" else open

    with opener(path, "rt", encoding="utf-8") as f:
        # Try NDJSON / JSON-array-per-line style first
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            # Skip array delimiters and commas that appear in pretty-printed arrays
            if line in ("[", "]", ","):
                continue

            # Lines in JSON arrays are often " {...}," -> strip a trailing comma safely
            if line.endswith(","):
                line = line[:-1].rstrip()

            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                # Not line-parseable; fall back to whole-file JSON parsing once.
                f.seek(0)
                data = json.load(f)
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict):
                            yield item
                elif isinstance(data, dict):
                    # Some dumps wrap records under a key; yield dict values if list-like
                    yield data
                return
            else:
                if isinstance(obj, dict):
                    yield obj
                elif isinstance(obj, list):
                    for item in obj:
                        if isinstance(item, dict):
                            yield item


def _is_lexeme_record(record: Mapping[str, Any]) -> bool:
    """Decide whether a JSON record looks like a Wikidata Lexeme."""
    rec_type = record.get("type")
    if rec_type == "lexeme":
        return True

    rec_id = str(record.get("id", ""))
    if rec_id.startswith("L"):
        return True

    if "lemmas" in record:
        return True

    return False


def _get_lemma_for_lang(record: Mapping[str, Any], lang_code: str) -> Optional[str]:
    """Extract a lemma string for a given language code."""
    lemmas = record.get("lemmas")
    if not isinstance(lemmas, dict):
        return None

    # Exact language match
    entry = lemmas.get(lang_code)
    if isinstance(entry, dict):
        val = entry.get("value")
        return val if isinstance(val, str) and val else None

    # Fallback: primary subtag (e.g. "en" from "en-GB")
    primary = lang_code.split("-", 1)[0]
    if primary and primary != lang_code:
        entry = lemmas.get(primary)
        if isinstance(entry, dict):
            val = entry.get("value")
            return val if isinstance(val, str) and val else None

    return None


def _find_first_qid(obj: Any) -> Optional[str]:
    """Find the first string that looks like a Wikidata QID within a nested structure."""
    if isinstance(obj, str):
        return obj if obj.startswith("Q") else None
    if isinstance(obj, dict):
        for v in obj.values():
            found = _find_first_qid(v)
            if found:
                return found
    if isinstance(obj, list):
        for v in obj:
            found = _find_first_qid(v)
            if found:
                return found
    return None


def _get_first_sense_qid(record: Mapping[str, Any]) -> Optional[str]:
    """Extract first sense QID (e.g., from sense.wikidataItem.id)."""
    senses = record.get("senses")
    if not isinstance(senses, list):
        return None
    for sense in senses:
        if not isinstance(sense, dict):
            continue
        # Prefer wikidataItem if present, otherwise search sense object
        qid = _find_first_qid(sense.get("wikidataItem")) or _find_first_qid(sense)
        if qid:
            return qid
    return None


def _extract_pos(
    record: Mapping[str, Any],
    lexical_category_map: Optional[Mapping[str, str]],
) -> Optional[str]:
    lexical_category = record.get("lexicalCategory")
    cat_id: Optional[str] = None

    if isinstance(lexical_category, dict):
        maybe = lexical_category.get("id")
        if isinstance(maybe, str):
            cat_id = maybe
    elif isinstance(lexical_category, str):
        cat_id = lexical_category

    if not cat_id:
        return None

    # Use provided map; fall back to defaults
    if lexical_category_map and cat_id in lexical_category_map:
        return lexical_category_map[cat_id]
    return DEFAULT_LEXICAL_CATEGORY_MAP.get(cat_id)


# ---------------------------------------------------------------------------
# Core Conversion Logic
# ---------------------------------------------------------------------------


def lexeme_from_wikidata_record(
    record: Mapping[str, Any],
    lang_code: str,
    *,
    lexical_category_map: Optional[Mapping[str, str]] = None,
) -> Optional[Dict[str, Any]]:
    """
    Convert a Wikidata record to a dictionary compatible with the internal lemma-entry schema
    expected by unit tests:

      entry = {
        "lemma": "fisico",
        "pos": "NOUN",
        "qid": "Q169470",
        "forms": {"default": "fisico"},
        "features": {"lexeme_id": "L1"},
        "extra": {...}
      }
    """
    if not _is_lexeme_record(record):
        return None

    lemma = _get_lemma_for_lang(record, lang_code)
    if not lemma:
        return None

    lexeme_id = str(record.get("id") or "")
    pos = _extract_pos(record, lexical_category_map=lexical_category_map)
    qid = _get_first_sense_qid(record)

    entry: Dict[str, Any] = {
        "lemma": lemma,
        "pos": pos,
        "qid": qid,
        "forms": {"default": lemma},
        "features": {"lexeme_id": lexeme_id} if lexeme_id else {},
        "extra": {},
    }
    return entry



__all__ = ["lexeme_from_wikidata_record"]
