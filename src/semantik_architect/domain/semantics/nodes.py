from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence, TypeAlias

from .references import require_local_id, require_semantic_ref


@dataclass(frozen=True, slots=True)
class EntityRef:
    id: str
    external_ref: str
    labels: Mapping[str, str] = field(default_factory=dict)
    kind: str = field(default="entity_ref", init=False)

    def __post_init__(self) -> None:
        require_local_id(self.id)
        require_semantic_ref(self.external_ref, "external_ref")
        object.__setattr__(self, "labels", dict(self.labels))


@dataclass(frozen=True, slots=True)
class ConceptRef:
    id: str
    concept_ref: str
    kind: str = field(default="concept_ref", init=False)

    def __post_init__(self) -> None:
        require_local_id(self.id)
        require_semantic_ref(self.concept_ref, "concept_ref")


@dataclass(frozen=True, slots=True)
class LiteralValue:
    id: str
    value: Any
    datatype: str | None = None
    kind: str = field(default="literal", init=False)

    def __post_init__(self) -> None:
        require_local_id(self.id)


@dataclass(frozen=True, slots=True)
class QuantityValue:
    id: str
    value: int | float
    unit_ref: str | None = None
    kind: str = field(default="quantity", init=False)

    def __post_init__(self) -> None:
        require_local_id(self.id)
        if self.unit_ref is not None:
            require_semantic_ref(self.unit_ref, "unit_ref")


@dataclass(frozen=True, slots=True)
class TemporalValue:
    id: str
    temporal_kind: str
    value: str | Mapping[str, Any]
    kind: str = field(default="temporal", init=False)

    def __post_init__(self) -> None:
        require_local_id(self.id)
        if self.temporal_kind not in {"instant", "date", "time", "interval", "duration"}:
            raise ValueError(f"Unsupported temporal_kind: {self.temporal_kind}")


@dataclass(frozen=True, slots=True)
class CollectionValue:
    id: str
    members: tuple[str, ...]
    ordering: str = "FREE"
    ordering_policy_ref: str | None = None
    kind: str = field(default="collection", init=False)

    def __post_init__(self) -> None:
        require_local_id(self.id)
        object.__setattr__(self, "members", tuple(self.members))
        for member in self.members:
            require_local_id(member, "collection member")
        if self.ordering not in {"FIXED", "POLICY", "FREE"}:
            raise ValueError(f"Unsupported collection ordering: {self.ordering}")
        if self.ordering_policy_ref is not None:
            require_semantic_ref(self.ordering_policy_ref, "ordering_policy_ref")


SemanticNode: TypeAlias = EntityRef | ConceptRef | LiteralValue | QuantityValue | TemporalValue | CollectionValue


def node_from_dict(data: Mapping[str, Any]) -> SemanticNode:
    kind = data.get("kind")
    if kind == "entity_ref":
        return EntityRef(str(data["id"]), str(data["external_ref"]), data.get("labels") or {})
    if kind == "concept_ref":
        return ConceptRef(str(data["id"]), str(data["concept_ref"]))
    if kind == "literal":
        return LiteralValue(str(data["id"]), data.get("value"), data.get("datatype"))
    if kind == "quantity":
        return QuantityValue(str(data["id"]), data["value"], data.get("unit_ref"))
    if kind == "temporal":
        return TemporalValue(str(data["id"]), str(data["temporal_kind"]), data["value"])
    if kind == "collection":
        return CollectionValue(
            str(data["id"]), tuple(str(x) for x in data.get("members", ())),
            str(data.get("ordering") or "FREE"), data.get("ordering_policy_ref")
        )
    raise ValueError(f"Unknown semantic node kind: {kind!r}")


def node_to_dict(node: SemanticNode) -> dict[str, Any]:
    if isinstance(node, EntityRef):
        out={"id":node.id,"kind":node.kind,"external_ref":node.external_ref}
        if node.labels: out["labels"]=dict(node.labels)
        return out
    if isinstance(node, ConceptRef): return {"id":node.id,"kind":node.kind,"concept_ref":node.concept_ref}
    if isinstance(node, LiteralValue):
        out={"id":node.id,"kind":node.kind,"value":node.value}
        if node.datatype is not None: out["datatype"]=node.datatype
        return out
    if isinstance(node, QuantityValue):
        out={"id":node.id,"kind":node.kind,"value":node.value}
        if node.unit_ref is not None: out["unit_ref"]=node.unit_ref
        return out
    if isinstance(node, TemporalValue): return {"id":node.id,"kind":node.kind,"temporal_kind":node.temporal_kind,"value":node.value}
    if isinstance(node, CollectionValue):
        out={"id":node.id,"kind":node.kind,"members":list(node.members),"ordering":node.ordering}
        if node.ordering_policy_ref: out["ordering_policy_ref"]=node.ordering_policy_ref
        return out
    raise TypeError(type(node))
