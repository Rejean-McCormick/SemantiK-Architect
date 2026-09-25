from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from .references import require_local_id, require_semantic_ref


@dataclass(frozen=True, slots=True)
class SemanticArgument:
    role_ref: str
    value_id: str

    def __post_init__(self) -> None:
        require_semantic_ref(self.role_ref, "role_ref")
        require_local_id(self.value_id, "value_id")


@dataclass(frozen=True, slots=True)
class SemanticQualifier:
    qualifier_ref: str
    value_id: str

    def __post_init__(self) -> None:
        require_semantic_ref(self.qualifier_ref, "qualifier_ref")
        require_local_id(self.value_id, "value_id")


@dataclass(frozen=True, slots=True)
class SemanticStatement:
    id: str
    predicate_ref: str
    arguments: tuple[SemanticArgument, ...]
    polarity: str = "positive"
    qualifiers: tuple[SemanticQualifier, ...] = ()
    source_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        require_local_id(self.id)
        require_semantic_ref(self.predicate_ref, "predicate_ref")
        object.__setattr__(self, "arguments", tuple(self.arguments))
        object.__setattr__(self, "qualifiers", tuple(self.qualifiers))
        object.__setattr__(self, "source_refs", tuple(self.source_refs))
        if not self.arguments:
            raise ValueError("SemanticStatement.arguments must not be empty")
        if self.polarity not in {"positive", "negative"}:
            raise ValueError(f"Unsupported polarity: {self.polarity}")

    def role_map(self) -> dict[str, str]:
        return {a.role_ref: a.value_id for a in self.arguments}


def statement_from_dict(data: Mapping[str, Any]) -> SemanticStatement:
    args=tuple(SemanticArgument(str(x["role_ref"]), str(x["value_id"])) for x in data.get("arguments", ()))
    qualifiers=tuple(SemanticQualifier(str(x["qualifier_ref"]), str(x["value_id"])) for x in data.get("qualifiers", ()))
    return SemanticStatement(
        id=str(data["id"]), predicate_ref=str(data["predicate_ref"]), arguments=args,
        polarity=str(data.get("polarity") or "positive"), qualifiers=qualifiers,
        source_refs=tuple(str(x) for x in data.get("source_refs", ()))
    )


def statement_to_dict(statement: SemanticStatement) -> dict[str, Any]:
    out: dict[str, Any]={
        "id":statement.id,"predicate_ref":statement.predicate_ref,
        "arguments":[{"role_ref":a.role_ref,"value_id":a.value_id} for a in statement.arguments],
        "polarity":statement.polarity,
    }
    if statement.qualifiers: out["qualifiers"]=[{"qualifier_ref":q.qualifier_ref,"value_id":q.value_id} for q in statement.qualifiers]
    if statement.source_refs: out["source_refs"]=list(statement.source_refs)
    return out
