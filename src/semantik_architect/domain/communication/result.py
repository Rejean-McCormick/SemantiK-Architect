from __future__ import annotations
from dataclasses import dataclass, field
from hashlib import sha256
import json
from typing import Any, Mapping

@dataclass(frozen=True, slots=True)
class ResultListItem:
    item_id: str
    text: str
    obligation_ids: tuple[str,...]

@dataclass(frozen=True, slots=True)
class ResultBlock:
    block_id: str
    kind: str
    obligation_ids: tuple[str,...]
    text: str | None = None
    items: tuple[ResultListItem,...] = ()
    label: str | None = None
    value: str | None = None

    def to_dict(self)->dict[str,Any]:
        if self.kind=="list": return {"block_id":self.block_id,"kind":"list","items":[{"item_id":i.item_id,"text":i.text,"obligation_ids":list(i.obligation_ids)} for i in self.items],"obligation_ids":list(self.obligation_ids)}
        if self.kind=="label_value": return {"block_id":self.block_id,"kind":"label_value","label":self.label or "","value":self.value or "","obligation_ids":list(self.obligation_ids)}
        return {"block_id":self.block_id,"kind":self.kind,"text":self.text or "","obligation_ids":list(self.obligation_ids)}

@dataclass(frozen=True, slots=True)
class CoverageEntry:
    obligation_id: str
    block_ids: tuple[str,...]
    realization_unit_ids: tuple[str,...]

@dataclass(frozen=True, slots=True)
class RuntimeIdentity:
    sa_version: str
    runtime_set_id: str
    sa_gf_contract_version: str
    capability_profile: str | None = None

    def to_dict(self)->dict[str,Any]:
        out={"sa_version":self.sa_version,"runtime_set_id":self.runtime_set_id,"sa_gf_contract_version":self.sa_gf_contract_version}
        if self.capability_profile: out["capability_profile"]=self.capability_profile
        return out

@dataclass(frozen=True, slots=True)
class CommunicationResult:
    language: str
    blocks: tuple[ResultBlock,...]
    coverage: tuple[CoverageEntry,...]
    runtime: RuntimeIdentity
    deterministic_result_id: str
    locale: str | None = None
    plain_text: str | None = None
    source_refs: tuple[str,...] = ()
    operational: Mapping[str,Any] = field(default_factory=dict)
    schema_version: str = "1.0"

    def to_dict(self, *, include_operational: bool=True)->dict[str,Any]:
        out={"schema_version":self.schema_version,"language":self.language,"blocks":[b.to_dict() for b in self.blocks],"coverage":[{"obligation_id":c.obligation_id,"block_ids":list(c.block_ids),"realization_unit_ids":list(c.realization_unit_ids)} for c in self.coverage],"runtime":self.runtime.to_dict(),"deterministic_result_id":self.deterministic_result_id}
        if self.locale: out["locale"]=self.locale
        if self.plain_text is not None: out["plain_text"]=self.plain_text
        if self.source_refs: out["source_refs"]=list(self.source_refs)
        if include_operational: out["operational"]=dict(self.operational)
        return out

    @staticmethod
    def compute_identity(payload: Mapping[str,Any])->str:
        raw=json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(",",":"),default=str).encode("utf-8")
        return "sha256:"+sha256(raw).hexdigest()
