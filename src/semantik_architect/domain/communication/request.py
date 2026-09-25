from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import re
from typing import Any, Mapping

from ..semantics.graph import SemanticGraph, graph_from_dict, graph_to_dict
from ..semantics.obligations import CommunicationObligation, obligation_from_dict
from .context import CommunicationContext
from .constraints import PresentationConstraints


@dataclass(frozen=True, slots=True)
class SupportingContextEntry:
    subject_id: str
    property_ref: str
    value: Any

    @classmethod
    def from_dict(cls,data:Mapping[str,Any]) -> "SupportingContextEntry":
        return cls(str(data["subject_id"]),str(data["property_ref"]),data.get("value"))

    def to_dict(self)->dict[str,Any]: return {"subject_id":self.subject_id,"property_ref":self.property_ref,"value":self.value}


@dataclass(frozen=True, slots=True)
class RuntimeSelector:
    runtime_set_id: str | None = None

    @classmethod
    def from_dict(cls,data: Mapping[str,Any] | None) -> "RuntimeSelector | None":
        if not data: return None
        return cls(runtime_set_id=data.get("runtime_set_id"))


@dataclass(frozen=True, slots=True)
class CommunicationRequest:
    semantic_graph: SemanticGraph
    obligations: tuple[CommunicationObligation, ...]
    context: CommunicationContext
    constraints: PresentationConstraints
    capability_profile: str
    supporting_context: tuple[SupportingContextEntry, ...] = ()
    runtime_selector: RuntimeSelector | None = None
    request_id: str | None = None
    deadline: str | None = None
    schema_version: str = "1.0"

    def __post_init__(self)->None:
        if self.schema_version != "1.0": raise ValueError(f"Unsupported CommunicationRequest schema: {self.schema_version}")
        object.__setattr__(self,"obligations",tuple(self.obligations)); object.__setattr__(self,"supporting_context",tuple(self.supporting_context))
        if not self.obligations: raise ValueError("At least one communication obligation is required")
        if not re.match(r"^[a-z][a-z0-9-]*-[0-9]+$",self.capability_profile): raise ValueError("capability_profile must be profile-id-N")
        if self.deadline:
            datetime.fromisoformat(self.deadline.replace("Z","+00:00"))

    @classmethod
    def from_dict(cls,data:Mapping[str,Any])->"CommunicationRequest":
        return cls(
            schema_version=str(data.get("schema_version") or ""), request_id=data.get("request_id"),
            semantic_graph=graph_from_dict(data["semantic_graph"]),
            obligations=tuple(obligation_from_dict(x) for x in data.get("obligations",())),
            supporting_context=tuple(SupportingContextEntry.from_dict(x) for x in data.get("supporting_context",())),
            context=CommunicationContext.from_dict(data["context"]), constraints=PresentationConstraints.from_dict(data["constraints"]),
            capability_profile=str(data["capability_profile"]), runtime_selector=RuntimeSelector.from_dict(data.get("runtime_selector")), deadline=data.get("deadline")
        )

    def support_values(self, subject_id: str, property_ref: str) -> tuple[Any,...]:
        return tuple(x.value for x in self.supporting_context if x.subject_id==subject_id and x.property_ref==property_ref)

    def to_dict(self)->dict[str,Any]:
        out={"schema_version":self.schema_version,"semantic_graph":graph_to_dict(self.semantic_graph),"obligations":[{
            "obligation_id":o.obligation_id,"semantic_refs":list(o.semantic_refs),"force":o.force.value,"ordering":o.ordering.value,
            **({"ordering_policy_ref":o.ordering_policy_ref} if o.ordering_policy_ref else {}),
            **({"visibility_requirements":list(o.visibility_requirements)} if o.visibility_requirements else {}),
            **({"source_refs":list(o.source_refs)} if o.source_refs else {}),
        } for o in self.obligations],"supporting_context":[x.to_dict() for x in self.supporting_context],"context":self.context.to_dict(),"constraints":self.constraints.to_dict(),"capability_profile":self.capability_profile}
        if self.request_id: out["request_id"]=self.request_id
        if self.runtime_selector and self.runtime_selector.runtime_set_id: out["runtime_selector"]={"runtime_set_id":self.runtime_selector.runtime_set_id}
        if self.deadline: out["deadline"]=self.deadline
        return out
