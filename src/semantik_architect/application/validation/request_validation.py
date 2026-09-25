from __future__ import annotations
from ...domain.communication.request import CommunicationRequest
from ...domain.errors import SemantikArchitectError

class RequestValidator:
    def validate(self, request:CommunicationRequest)->None:
        graph=request.semantic_graph
        obligation_ids=[o.obligation_id for o in request.obligations]
        if len(obligation_ids)!=len(set(obligation_ids)):
            raise SemantikArchitectError("SA-REQ-001","Obligation IDs must be unique",request_id=request.request_id)
        for obligation in request.obligations:
            missing=[ref for ref in obligation.semantic_refs if not graph.has(ref)]
            if missing:
                raise SemantikArchitectError("SA-REQ-001",f"Obligation {obligation.obligation_id} references missing semantics",request_id=request.request_id,details={"missing_refs":missing})
        valid_support_subjects=set(graph.node_by_id)|set(graph.statement_by_id)|set(obligation_ids)
        unknown_support=sorted({entry.subject_id for entry in request.supporting_context if entry.subject_id not in valid_support_subjects})
        if unknown_support:
            raise SemantikArchitectError("SA-REQ-001","Supporting context references unknown subjects",request_id=request.request_id,details={"subject_ids":unknown_support})
        allowed=set(request.constraints.allowed_block_kinds)
        if not allowed:
            raise SemantikArchitectError("SA-CON-001","No output block kinds are allowed",request_id=request.request_id)
        if request.constraints.opening_policy=="required" and "utterance" not in allowed:
            raise SemantikArchitectError("SA-CON-001","Required opening needs utterance output",request_id=request.request_id)
        if request.constraints.closing_policy=="required" and "utterance" not in allowed:
            raise SemantikArchitectError("SA-CON-001","Required closing needs utterance output",request_id=request.request_id)
