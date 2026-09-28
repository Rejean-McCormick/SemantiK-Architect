from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

STANDARD_LEXICAL_PRECEDENCE: tuple[str, ...] = (
    "request_override",
    "domain",
    "project",
    "wikidata",
    "gf_generic",
)
VALID_LEXICAL_SOURCE_KINDS = frozenset(STANDARD_LEXICAL_PRECEDENCE)
VALID_LEXICAL_USES = frozenset({"knowledge", "binding", "both"})


@dataclass(frozen=True, slots=True)
class LexicalPolicy:
    """Deterministic lexical-source precedence for a RuntimeSet.

    Semantic/lexical knowledge and grammatical realization are deliberately
    separate concerns. Wikidata Lexemes are the default generic lexical
    knowledge source; GF generic lexicons are the last-resort realization
    binding source. Domain/project artifacts may explicitly override both.
    """

    precedence: tuple[str, ...] = STANDARD_LEXICAL_PRECEDENCE
    default_source_kind: str = "project"
    equal_precedence_conflict: str = "fail"

    def __post_init__(self) -> None:
        precedence = tuple(self.precedence)
        if not precedence or len(set(precedence)) != len(precedence):
            raise ValueError("lexical precedence must contain unique source kinds")
        unknown = [kind for kind in precedence if kind not in VALID_LEXICAL_SOURCE_KINDS]
        if unknown:
            raise ValueError(f"unknown lexical source kinds: {unknown}")
        if self.default_source_kind not in precedence:
            raise ValueError("default lexical source kind must appear in precedence")
        if self.equal_precedence_conflict != "fail":
            raise ValueError("only fail-closed equal-precedence conflicts are supported")
        object.__setattr__(self, "precedence", precedence)

    def rank(self, source_kind: str) -> int:
        try:
            return len(self.precedence) - self.precedence.index(source_kind)
        except ValueError as exc:
            raise ValueError(f"lexical source kind not admitted by policy: {source_kind}") from exc

    @classmethod
    def from_manifest(cls, manifest: Mapping[str, Any]) -> "LexicalPolicy":
        raw = manifest.get("lexical_policy")
        if not isinstance(raw, Mapping):
            return cls()
        return cls(
            precedence=tuple(str(x) for x in (raw.get("precedence") or STANDARD_LEXICAL_PRECEDENCE)),
            default_source_kind=str(raw.get("default_source_kind") or "project"),
            equal_precedence_conflict=str(raw.get("equal_precedence_conflict") or "fail"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "policy_version": "1.0",
            "precedence": list(self.precedence),
            "default_source_kind": self.default_source_kind,
            "equal_precedence_conflict": self.equal_precedence_conflict,
        }
