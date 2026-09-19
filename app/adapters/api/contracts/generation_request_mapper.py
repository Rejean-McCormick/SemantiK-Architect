from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Union

import structlog

from app.adapters.ninai import ninai_adapter
from app.core.domain.exceptions import InvalidFrameError
from app.core.domain.frame import BioFrame, EventFrame, Frame, RelationalFrame

logger = structlog.get_logger()

_RETIRED_FRAME_TYPES = {
    "person", "biography", "entity.person", "entity_person",
    "entity.person.v1", "entity.person.v2",
}
_RETIRED_BIO_FLAT_FIELDS = {
    "name", "label", "qid", "gender", "sex",
    "profession", "occupation", "nationality", "citizenship",
    "main_entity", "primary_profession_lemmas", "nationality_lemmas",
}
_TRANSPORT_LANG_KEYS = {"lang", "language", "lang_code"}
_RENDERER_FIELDS = {"backend", "renderer_backend", "gf_ast", "ast", "template", "template_id"}


@dataclass(frozen=True, slots=True)
class MappedGenerationRequest:
    lang_code: str
    frame: Union[BioFrame, EventFrame, RelationalFrame, Frame]
    payload: Dict[str, Any]


def normalize_lang_code(value: str) -> str:
    code = str(value or "").strip().lower().replace("_", "-")
    if not code:
        raise InvalidFrameError("Language code must be non-empty.")
    return code


def map_generation_request(
    payload: Mapping[str, Any],
    *,
    path_lang_code: str,
) -> MappedGenerationRequest:
    if not isinstance(payload, Mapping):
        raise InvalidFrameError("Payload must be a JSON object.")
    lang = normalize_lang_code(path_lang_code)
    raw = dict(payload)

    # The path is authoritative. Redundant body language is accepted only when equal.
    for key in _TRANSPORT_LANG_KEYS:
        if key in raw:
            body_lang = normalize_lang_code(str(raw[key]))
            if body_lang != lang:
                raise InvalidFrameError(
                    f"Language mismatch: path={lang!r}, payload={body_lang!r}."
                )
            raw.pop(key, None)

    if "type" in raw:
        raise InvalidFrameError("Unsupported field 'type'. Use 'frame_type'.")
    forbidden_renderer = sorted(_RENDERER_FIELDS.intersection(raw))
    if forbidden_renderer:
        raise InvalidFrameError(
            "Renderer-specific fields are not semantic input: "
            + ", ".join(forbidden_renderer)
        )

    frame = parse_generation_payload(raw, lang)
    payload_out = frame.model_dump(exclude_none=True) if hasattr(frame, "model_dump") else raw
    return MappedGenerationRequest(lang_code=lang, frame=frame, payload=dict(payload_out))


def parse_generation_payload(
    payload: Mapping[str, Any],
    lang_code: str,
) -> Union[BioFrame, EventFrame, RelationalFrame, Frame]:
    if not isinstance(payload, Mapping):
        raise InvalidFrameError("Payload must be a JSON object.")
    raw = dict(payload)

    if "function" in raw:
        logger.info("ninai_protocol_detected", lang=lang_code)
        try:
            return ninai_adapter.parse(raw)
        except ValueError as exc:
            raise InvalidFrameError(f"Ninai Parsing Error: {exc}") from exc

    frame_type = str(raw.get("frame_type") or "").strip().lower()
    if not frame_type:
        raise InvalidFrameError("Missing required field: frame_type")
    if frame_type in _RETIRED_FRAME_TYPES:
        raise InvalidFrameError(
            f"Retired frame_type {frame_type!r}; use the canonical frame family."
        )

    try:
        if frame_type == "bio":
            retired = sorted(_RETIRED_BIO_FLAT_FIELDS.intersection(raw))
            if retired:
                raise InvalidFrameError(
                    "bio uses nested subject; retired flat fields are not accepted: "
                    + ", ".join(retired)
                )
            subject = raw.get("subject")
            if not isinstance(subject, Mapping):
                raise InvalidFrameError("bio requires a nested subject object.")
            canonical = dict(raw)
            canonical["frame_type"] = "bio"
            canonical["subject"] = dict(subject)
            return BioFrame(**canonical)
        if frame_type == "event":
            return EventFrame(**raw)
        if frame_type == "relational":
            return RelationalFrame(**raw)
        return Frame(**raw)
    except InvalidFrameError:
        raise
    except Exception as exc:
        raise InvalidFrameError(str(exc)) from exc


__all__ = [
    "MappedGenerationRequest",
    "map_generation_request",
    "normalize_lang_code",
    "parse_generation_payload",
]
