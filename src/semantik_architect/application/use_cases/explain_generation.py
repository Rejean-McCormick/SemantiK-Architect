from __future__ import annotations
from ...domain.communication.request import CommunicationRequest
from ..planning.communication_planner import CommunicationPlanner
from ..planning.language_planner import GenericLanguagePlanner
from ..ports.lexical_knowledge import LexicalKnowledgePort
from ..ports.runtime_catalog import RuntimeCatalogPort
class ExplainGeneration:
    def __init__(self,catalog:RuntimeCatalogPort,lexical:LexicalKnowledgePort)->None: self.catalog=catalog; self.lexical=lexical
    def execute(self,request:CommunicationRequest)->dict:
        runtime=self.catalog.resolve(request.context.target_language,request.capability_profile,request.runtime_selector.runtime_set_id if request.runtime_selector else None)
        cp=CommunicationPlanner().plan(request); lc=self.lexical.preflight(request,cp,runtime); lp=GenericLanguagePlanner().plan(request,cp,lc)
        return {"runtime_set_id":runtime.runtime_set_id,"communication_plan":{"plan_id":cp.plan_id,"items":[{"item_id":i.item_id,"obligation_ids":list(i.obligation_ids),"semantic_refs":list(i.semantic_refs),"force":i.force.value,"presentation_intent":i.presentation_intent} for i in cp.items]},"language_plan":{"plan_id":lp.plan_id,"language":lp.language,"blocks":[{"block_id":b.block_id,"kind":b.kind,"unit_ids":list(b.unit_ids)} for b in lp.blocks],"units":[{"unit_id":u.unit_id,"operation_id":u.operation_id,"role_bindings":dict(u.role_bindings),"lexical_slots":dict(u.lexical_slots),"features":dict(u.feature_bindings),"obligation_ids":list(u.obligation_ids)} for u in lp.units]}}
