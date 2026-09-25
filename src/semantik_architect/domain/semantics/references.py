from __future__ import annotations

import re

_SEMANTIC_REF_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]*:.+$")
_LOCAL_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:/-]*$")


def require_semantic_ref(value: str, field_name: str = "semantic_ref") -> str:
    if not isinstance(value, str) or not _SEMANTIC_REF_RE.match(value):
        raise ValueError(f"{field_name} must be a namespace-qualified reference: {value!r}")
    return value


def require_local_id(value: str, field_name: str = "id") -> str:
    if not isinstance(value, str) or not _LOCAL_ID_RE.match(value):
        raise ValueError(f"{field_name} is not a valid local identifier: {value!r}")
    return value


def local_name(ref: str) -> str:
    text = str(ref)
    if ":" in text:
        text = text.split(":", 1)[1]
    return text.rsplit("/", 1)[-1].rsplit("#", 1)[-1].strip().lower().replace("-", "_")
