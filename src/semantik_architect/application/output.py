from __future__ import annotations
from collections import defaultdict
from ..domain.communication.request import CommunicationRequest
from ..domain.communication.result import CommunicationResult, ResultBlock, ResultListItem, CoverageEntry, RuntimeIdentity
from ..domain.language.language_plan import LanguagePlan
from .ports.realizer import RealizationResult
from .ports.runtime_catalog import RuntimeSetDescriptor

class OutputAssembler:
    def assemble(self,request:CommunicationRequest,plan:LanguagePlan,realization:RealizationResult,runtime:RuntimeSetDescriptor,*,sa_version:str)->CommunicationResult:
        realized=realization.by_id(); blocks=[]; coverage_blocks=defaultdict(set); coverage_units=defaultdict(set)
        for block in plan.blocks:
            missing=[u for u in block.unit_ids if u not in realized]
            if missing: raise ValueError(f"Realizer omitted units: {missing}")
            texts=[realized[u].text for u in block.unit_ids]
            if block.kind=='list':
                items=tuple(ResultListItem(f"{block.block_id}:i{i+1}",txt,tuple(plan.unit_by_id[uid].obligation_ids)) for i,(uid,txt) in enumerate(zip(block.unit_ids,texts)))
                rb=ResultBlock(block.block_id,'list',block.obligation_ids,items=items)
            else:
                rb=ResultBlock(block.block_id,block.kind,block.obligation_ids,text=" ".join(texts).strip())
            blocks.append(rb)
            for uid in block.unit_ids:
                for oid in plan.unit_by_id[uid].obligation_ids:
                    coverage_blocks[oid].add(block.block_id); coverage_units[oid].add(uid)
        coverage=tuple(CoverageEntry(o.obligation_id,tuple(sorted(coverage_blocks[o.obligation_id])),tuple(sorted(coverage_units[o.obligation_id]))) for o in request.obligations)
        plain=[]
        for b in blocks:
            if b.kind=='list': plain.extend(f"- {i.text}" for i in b.items)
            elif b.kind=='label_value': plain.append(f"{b.label}: {b.value}")
            elif b.text: plain.append(b.text)
        sources=[]
        for o in request.obligations:
            for ref in o.source_refs:
                if ref not in sources: sources.append(ref)
            for semantic_ref in o.semantic_refs:
                try:
                    obj=request.semantic_graph.get(semantic_ref)
                except KeyError:
                    continue
                for ref in getattr(obj,"source_refs",()):
                    if ref not in sources: sources.append(ref)
        rid=RuntimeIdentity(sa_version,runtime.runtime_set_id,runtime.sa_gf_contract_version,request.capability_profile)
        tmp=CommunicationResult(request.context.target_language,tuple(blocks),coverage,rid,"pending",request.context.target_locale,"\n".join(plain),tuple(sources),{})
        payload=tmp.to_dict(include_operational=False); payload.pop('deterministic_result_id',None)
        did=CommunicationResult.compute_identity(payload)
        return CommunicationResult(request.context.target_language,tuple(blocks),coverage,rid,did,request.context.target_locale,"\n".join(plain),tuple(sources),{})
