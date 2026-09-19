from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def _clean_optional_str(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned or None
    cleaned = str(value).strip()
    return cleaned or None


def _coerce_mapping(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, dict):
        return dict(value)
    try:
        return dict(value)
    except Exception as exc:
        raise TypeError("value must be mapping-compatible") from exc


def _coerce_str_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, (list, tuple, set)):
        raise TypeError("tokens must be a sequence of strings")
    out: list[str] = []
    for item in value:
        cleaned = _clean_optional_str(item)
        if cleaned:
            out.append(cleaned)
    return out


def _normalize_lang_code(value: Any) -> str:
    cleaned = _clean_optional_str(value)
    if not cleaned:
        raise ValueError("language code is required")
    normalized = cleaned.lower().replace("_", "-")
    parts = normalized.split("-")
    if not parts[0].isalpha() or len(parts[0]) not in {2, 3}:
        raise ValueError("language code must start with a 2- or 3-letter alphabetic code")
    if any(not part or not part.isalnum() for part in parts[1:]):
        raise ValueError("language code contains an invalid subtag")
    return normalized


class SurfaceResult(BaseModel):
    """Canonical generation result shared by runtime and public API."""

    text: str
    lang_code: str
    construction_id: str
    renderer_backend: str
    fallback_used: bool
    tokens: list[str]
    debug_info: dict[str, Any]
    generation_time_ms: float

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    @field_validator("text")
    @classmethod
    def _validate_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("text must be a non-empty string")
        return cleaned

    @field_validator("lang_code", mode="before")
    @classmethod
    def _normalize_lang_code_field(cls, value: Any) -> str:
        return _normalize_lang_code(value)

    @field_validator("construction_id", "renderer_backend", mode="before")
    @classmethod
    def _normalize_required_labels(cls, value: Any) -> str:
        cleaned = _clean_optional_str(value)
        if not cleaned:
            raise ValueError("field must be a non-empty string")
        return cleaned

    @field_validator("tokens", mode="before")
    @classmethod
    def _normalize_tokens(cls, value: Any) -> list[str]:
        tokens = _coerce_str_list(value)
        if not tokens:
            raise ValueError("tokens must contain at least one non-empty string")
        return tokens

    @field_validator("debug_info", mode="before")
    @classmethod
    def _normalize_debug_info(cls, value: Any) -> dict[str, Any]:
        return _coerce_mapping(value)

    @field_validator("generation_time_ms", mode="before")
    @classmethod
    def _normalize_generation_time_ms(cls, value: Any) -> float:
        try:
            normalized = float(value)
        except Exception as exc:
            raise ValueError("generation_time_ms must be numeric") from exc
        if normalized < 0:
            raise ValueError("generation_time_ms must be non-negative")
        return normalized

    @model_validator(mode="after")
    def _synchronize_debug_contract(self) -> "SurfaceResult":
        debug = dict(self.debug_info)
        debug["lang_code"] = self.lang_code
        debug["construction_id"] = self.construction_id
        debug["renderer_backend"] = self.renderer_backend
        debug["fallback_used"] = self.fallback_used
        debug["tokens"] = list(self.tokens)
        debug["generation_time_ms"] = self.generation_time_ms
        debug.setdefault("runtime_path", "planner_first")
        debug.setdefault("slot_keys", [])
        debug.setdefault("selected_backend", self.renderer_backend)
        debug.setdefault("attempted_backends", [self.renderer_backend])
        object.__setattr__(self, "debug_info", debug)
        return self


class LexiconEntry(BaseModel):
    """Runtime lexical entry used by filesystem/Wikidata adapters."""

    key: Optional[str] = None
    lemma: str
    pos: str
    language: str = "und"
    forms: dict[str, str] = Field(default_factory=dict)
    features: dict[str, Any] = Field(default_factory=dict)
    sense: Optional[str] = None
    wikidata_qid: Optional[str] = None
    source: str = "manual"
    confidence: float = 1.0
    meta: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    @field_validator("lemma", "pos", mode="before")
    @classmethod
    def _normalize_required_text(cls, value: Any) -> str:
        cleaned = _clean_optional_str(value)
        if not cleaned:
            raise ValueError("field must be a non-empty string")
        return cleaned

    @field_validator("language", mode="before")
    @classmethod
    def _normalize_entry_language(cls, value: Any) -> str:
        return _normalize_lang_code(value)

    @field_validator("forms", "features", "meta", mode="before")
    @classmethod
    def _normalize_dict_fields(cls, value: Any) -> dict[str, Any]:
        return _coerce_mapping(value)

    @field_validator("source", mode="before")
    @classmethod
    def _normalize_source(cls, value: Any) -> str:
        cleaned = _clean_optional_str(value)
        if not cleaned:
            raise ValueError("source must be a non-empty string")
        return cleaned

    @field_validator("sense", "wikidata_qid", "key", mode="before")
    @classmethod
    def _normalize_optional_fields(cls, value: Any) -> Optional[str]:
        return _clean_optional_str(value)

    @field_validator("confidence", mode="before")
    @classmethod
    def _normalize_confidence(cls, value: Any) -> float:
        if value is None:
            return 1.0
        try:
            result = float(value)
        except Exception as exc:
            raise ValueError("confidence must be numeric") from exc
        if not 0.0 <= result <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        return result


__all__ = ["SurfaceResult", "LexiconEntry"]
