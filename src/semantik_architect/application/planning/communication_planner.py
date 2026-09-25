from __future__ import annotations
from hashlib import sha256
from ...domain.communication.request import CommunicationRequest
from ...domain.communication.communication_plan import CommunicationPlan, CommunicationPlanItem
from ...domain.semantics.nodes import CollectionValue
from ...domain.semantics.obligations import CommunicativeForce

class CommunicationPlanner:
    """Deterministic, language-neutral obligation organization.

    V1 intentionally preserves caller obligation order. It chooses only a broad
    presentation intent; final sentence boundaries and grammar remain language planning.
    """
    def plan(self, request:CommunicationRequest)->CommunicationPlan:
        items=[]
        if request.constraints.opening_policy == "required":
            recipient=request.context.recipient_ref
            refs=(recipient,) if recipient else ()
            items.append(CommunicationPlanItem("cp_opening",(),refs,CommunicativeForce.PRESENT,"greeting"))
        for idx, obligation in enumerate(request.obligations,1):
            intent="question" if obligation.force.value=="ASK" else "utterance"
            if obligation.force.value=="PRESENT": intent="present"
            for ref in obligation.semantic_refs:
                obj=request.semantic_graph.get(ref)
                if isinstance(obj, CollectionValue) and request.constraints.list_policy != "forbidden" and "list" in request.constraints.allowed_block_kinds:
                    intent="list"
                    break
            items.append(CommunicationPlanItem(
                item_id=f"cp{idx}", obligation_ids=(obligation.obligation_id,), semantic_refs=obligation.semantic_refs,
                force=obligation.force, presentation_intent=intent,
            ))
        if request.constraints.closing_policy == "required":
            items.append(CommunicationPlanItem("cp_closing",(),(),CommunicativeForce.PRESENT,"closing"))
        stable="|".join([request.constraints.opening_policy,*(o.obligation_id for o in request.obligations),request.constraints.closing_policy])
        pid="cp:"+sha256(stable.encode()).hexdigest()[:20]
        return CommunicationPlan(pid,tuple(items),tuple(o.obligation_id for o in request.obligations))
