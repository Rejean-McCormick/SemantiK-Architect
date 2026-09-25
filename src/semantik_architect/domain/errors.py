from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


_ERROR_REGISTRY: dict[str, tuple[str, str, bool]] = {
    "SA-REQ-001": ("REQUEST_INVALID", "validation", False),
    "SA-SEM-001": ("SEMANTIC_UNMAPPABLE", "semantic", False),
    "SA-SEM-002": ("OBLIGATION_UNCOVERED", "coverage", False),
    "SA-CON-001": ("CONSTRAINT_UNSATISFIABLE", "planning", False),
    "SA-LANG-001": ("LANGUAGE_UNAVAILABLE", "runtime", False),
    "SA-LANG-002": ("PROFILE_UNAVAILABLE", "runtime", False),
    "SA-LANG-003": ("LANGUAGE_PLANNING_FAILED", "language_planning", False),
    "SA-LEX-001": ("LEXICAL_KNOWLEDGE_MISSING", "lexical_preflight", False),
    "SA-LEX-002": ("LEXICAL_BINDING_FAILED", "lexical_binding", False),
    "SA-GF-001": ("GF_CONTRACT_INCOMPATIBLE", "realization", False),
    "SA-GF-002": ("REALIZATION_FAILED", "realization", False),
    "SA-RUN-001": ("RUNTIME_MISSING", "runtime", True),
    "SA-RUN-002": ("RUNTIME_INTEGRITY_FAILED", "runtime", False),
    "SA-RUN-003": ("RUNTIME_NOT_READY", "runtime", True),
    "SA-ADP-001": ("ADAPTER_CONTRACT_FAILED", "adapter", False),
    "SA-OPS-001": ("DEADLINE_EXCEEDED", "operations", True),
    "SA-OPS-002": ("CANCELLED", "operations", True),
    "SA-INT-001": ("INTERNAL_INVARIANT_BROKEN", "internal", False),
}


@dataclass(frozen=True, slots=True)
class ErrorEnvelope:
    code: str
    category: str
    stage: str
    message_safe: str
    retryable: bool
    request_id: str | None = None
    runtime_set_id: str | None = None
    details: Mapping[str, Any] = field(default_factory=dict)
    schema_version: str = "1.0"

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "schema_version": self.schema_version,
            "code": self.code,
            "category": self.category,
            "stage": self.stage,
            "message_safe": self.message_safe,
            "retryable": self.retryable,
        }
        if self.request_id:
            out["request_id"] = self.request_id
        if self.runtime_set_id:
            out["runtime_set_id"] = self.runtime_set_id
        if self.details:
            out["details"] = dict(self.details)
        return out


class SemantikArchitectError(RuntimeError):
    def __init__(
        self,
        code: str,
        message_safe: str,
        *,
        stage: str | None = None,
        request_id: str | None = None,
        runtime_set_id: str | None = None,
        details: Mapping[str, Any] | None = None,
        retryable: bool | None = None,
    ) -> None:
        if code not in _ERROR_REGISTRY:
            raise ValueError(f"Unknown SA error code: {code}")
        category, default_stage, default_retryable = _ERROR_REGISTRY[code]
        self.envelope = ErrorEnvelope(
            code=code,
            category=category,
            stage=stage or default_stage,
            message_safe=message_safe,
            retryable=default_retryable if retryable is None else retryable,
            request_id=request_id,
            runtime_set_id=runtime_set_id,
            details=dict(details or {}),
        )
        super().__init__(message_safe)

    def to_dict(self) -> dict[str, Any]:
        return self.envelope.to_dict()


def request_invalid(message: str, **kwargs: Any) -> SemantikArchitectError:
    return SemantikArchitectError("SA-REQ-001", message, **kwargs)


def invariant_broken(message: str, **kwargs: Any) -> SemantikArchitectError:
    return SemantikArchitectError("SA-INT-001", message, **kwargs)
