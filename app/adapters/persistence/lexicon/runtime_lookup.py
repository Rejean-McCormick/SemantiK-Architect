from __future__ import annotations

from typing import Any

from .cache import get_or_build_index


def get_entry(lang_code: str, key: str | None) -> Any | None:
    """Return a runtime lexicon entry by QID or lemma using the canonical index."""
    if not key:
        return None
    lang = str(lang_code).strip().lower().replace("_", "-")
    lang = {"eng": "en", "fra": "fr", "fre": "fr"}.get(lang, lang)
    try:
        index = get_or_build_index(lang)
    except (FileNotFoundError, ValueError):
        return None
    text = str(key).strip()
    if not text:
        return None
    if text.upper().startswith("Q") and text[1:].isdigit():
        try:
            hit = index.lookup_by_qid(text)
        except Exception:
            hit = None
        if hit is not None:
            return hit
    try:
        return index.lookup_by_lemma(text, pos=None)
    except TypeError:
        try:
            return index.lookup_by_lemma(text)
        except Exception:
            return None
    except Exception:
        return None


def get_feature(entry: Any, key: str, default: Any = None) -> Any:
    if entry is None:
        return default
    if isinstance(entry, dict):
        if key in entry:
            return entry.get(key, default)
        features = entry.get("features")
        if isinstance(features, dict) and key in features:
            return features.get(key, default)
        extra = entry.get("extra")
        if isinstance(extra, dict) and key in extra:
            return extra.get(key, default)
        return default
    value = getattr(entry, key, None)
    if value is not None:
        return value
    features = getattr(entry, "features", None)
    if isinstance(features, dict) and key in features:
        return features.get(key, default)
    extra = getattr(entry, "extra", None)
    if isinstance(extra, dict) and key in extra:
        return extra.get(key, default)
    return default


def get_facts(entry: Any, property_id: str) -> list[str]:
    for container_name in ("facts", "features", "extra"):
        container = entry.get(container_name) if isinstance(entry, dict) else getattr(entry, container_name, None)
        if not isinstance(container, dict):
            continue
        value = container.get(property_id)
        if isinstance(value, list):
            return [str(item) for item in value if str(item).strip()]
        if value is not None and str(value).strip():
            return [str(value)]
    return []


__all__ = ["get_entry", "get_feature", "get_facts"]
