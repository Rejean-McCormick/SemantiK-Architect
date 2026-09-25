from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from typing import Iterable

from ...domain.communication.request import CommunicationRequest
from ...domain.communication.communication_plan import CommunicationPlan, CommunicationPlanItem
from ...domain.language.language_plan import LanguagePlan, LanguageBlockPlan
from ...domain.language.realization_unit import RealizationUnit
from ...domain.language.lexical import LexicalPlanningContext
from ...domain.semantics.statements import SemanticStatement
from ...domain.semantics.nodes import CollectionValue, ConceptRef
from ...domain.semantics.references import local_name
from ...domain.errors import SemantikArchitectError
from ...domain.language.operations import require_known_operation

_AGENT={"agent","actor","subject","speaker"}; _PATIENT={"patient","object","theme"}; _RECIPIENT={"recipient","goal","beneficiary"}
_LOCATION={"location","place"}; _POSSESSOR={"possessor","owner"}; _POSSESSED={"possessed","possession"}; _ATTRIBUTE={"attribute","quality","descriptor"}; _CLASS={"class","type","category"}
_EVENT_TYPE={"event_type","action","predicate"}; _TIME={"time","deadline","date","when"}; _CONTACT={"contact"}; _VALUE={"value"}; _HOLDER={"holder"}


def _roles(stmt:SemanticStatement)->dict[str,str]:
    return {local_name(a.role_ref):a.value_id for a in stmt.arguments}

def _first(rolemap:dict[str,str], names:set[str])->str|None:
    return next((v for k,v in rolemap.items() if k in names),None)

@dataclass(frozen=True, slots=True)
class OperationChoice:
    operation_id:str
    roles:dict[str,str]
    lexical_slots:dict[str,str]
    features:dict[str,object]

class GenericLanguagePlanner:
    """Language-neutral default planner driven by semantic roles and lexical metadata.

    It contains no language-code branches. Language-specific behavior belongs in
    runtime metadata/bridge grammar or an explicitly injected planner strategy.
    """
    def plan(self, request:CommunicationRequest, communication_plan:CommunicationPlan, lexical_context:LexicalPlanningContext)->LanguagePlan:
        units=[]; blocks=[]; unit_seq=0
        for block_seq,item in enumerate(communication_plan.items,1):
            generated=[]
            if item.presentation_intent=="greeting":
                recipient=self._recipient_semantic_ref(request)
                slots={"recipient":recipient} if recipient else {}
                generated=[OperationChoice("discourse.greeting",dict(slots),dict(slots),self._context_features(request))]
                block_kind="utterance"
            elif item.presentation_intent=="closing":
                generated=[OperationChoice("discourse.closing",{}, {},self._context_features(request))]
                block_kind="utterance"
            elif item.presentation_intent=="list":
                generated=self._plan_list(request,item,lexical_context)
                block_kind="list"
            else:
                generated=self._plan_item(request,item,lexical_context)
                block_kind="question" if item.force.value=="ASK" else "utterance"
                if block_kind not in request.constraints.allowed_block_kinds:
                    if "utterance" in request.constraints.allowed_block_kinds: block_kind="utterance"
                    else: raise SemantikArchitectError("SA-CON-001",f"Required block kind {block_kind} is not allowed",request_id=request.request_id)
            ids=[]
            for choice in generated:
                unit_seq+=1; uid=f"u{unit_seq}"; ids.append(uid)
                units.append(RealizationUnit(uid,choice.operation_id,choice.roles,choice.features,choice.lexical_slots,item.obligation_ids,item.semantic_refs,f"b{block_seq}"))
            if not ids:
                raise SemantikArchitectError("SA-LANG-003",f"No realization unit could be planned for {item.item_id}",request_id=request.request_id)
            blocks.append(LanguageBlockPlan(f"b{block_seq}",block_kind,tuple(ids),item.obligation_ids))
        digest=sha256((request.context.target_language+"|"+"|".join(u.operation_id for u in units)).encode()).hexdigest()[:20]
        return LanguagePlan(f"lp:{digest}",request.context.target_language,request.context.target_locale,tuple(blocks),tuple(units),request.capability_profile)

    @staticmethod
    def _support_last(request:CommunicationRequest, subject_id:str, property_ref:str):
        values=request.support_values(subject_id,property_ref)
        return values[-1] if values else None

    @staticmethod
    def _recipient_semantic_ref(request:CommunicationRequest)->str|None:
        target=request.context.recipient_ref
        if not target:
            return None
        for node in request.semantic_graph.nodes:
            if getattr(node,"external_ref",None)==target:
                return node.id
        return target

    @staticmethod
    def _context_features(request:CommunicationRequest)->dict[str,object]:
        out={}
        for name in ("formality","politeness","register","relationship","tone_profile"):
            value=getattr(request.context,name)
            if value is not None: out[name]=value
        return out

    @staticmethod
    def _semantic_value(request:CommunicationRequest,ref:str):
        obj=request.semantic_graph.get(ref)
        if hasattr(obj,"value"): return getattr(obj,"value")
        if hasattr(obj,"concept_ref"): return getattr(obj,"concept_ref")
        if hasattr(obj,"external_ref"): return getattr(obj,"external_ref")
        return ref

    def _qualifier_features(self,request:CommunicationRequest,stmt:SemanticStatement)->dict[str,object]:
        return {f"qualifier.{local_name(q.qualifier_ref)}":self._semantic_value(request,q.value_id) for q in stmt.qualifiers}

    def _hinted_choice(self,request:CommunicationRequest,stmt:SemanticStatement,force,attachments:tuple[SemanticStatement,...],lexical_context:LexicalPlanningContext)->OperationChoice|None:
        hinted=self._support_last(request,stmt.id,"sa:operation")
        if hinted is None:
            return None
        operation_id=require_known_operation(str(hinted))
        rm=_roles(stmt)
        role_hint=self._support_last(request,stmt.id,"sa:role-map") or {}
        slot_hint=self._support_last(request,stmt.id,"sa:slot-map") or {}
        feature_hint=self._support_last(request,stmt.id,"sa:feature-map") or {}
        if not isinstance(role_hint,dict) or not isinstance(slot_hint,dict) or not isinstance(feature_hint,dict):
            raise SemantikArchitectError("SA-LANG-003",f"Invalid planning hint for {stmt.id}",request_id=request.request_id)
        def resolve(spec):
            if isinstance(spec,str) and spec.startswith("role:"):
                wanted=spec.split(":",1)[1].lower().replace("-","_")
                found=_first(rm,{wanted})
                if found is None: raise SemantikArchitectError("SA-LANG-003",f"Planning hint role {wanted} is absent from {stmt.id}",request_id=request.request_id)
                return found
            if isinstance(spec,str) and spec.startswith("ref:"):
                return spec.split(":",1)[1]
            if isinstance(spec,str):
                # exact role ref or local role name first; otherwise an explicit semantic ref/id
                for role_ref,value_id in ((a.role_ref,a.value_id) for a in stmt.arguments):
                    if role_ref==spec or local_name(role_ref)==spec.lower().replace("-","_"):
                        return value_id
                return spec
            raise SemantikArchitectError("SA-LANG-003",f"Invalid planning hint binding in {stmt.id}",request_id=request.request_id)
        roles={str(k):resolve(v) for k,v in role_hint.items()}
        slots={str(k):resolve(v) for k,v in slot_hint.items()}
        # if no slot map is supplied, role bindings are also lexical slots; predicate is explicit
        if not slots:
            slots=dict(roles)
            if "predicate" not in slots:
                event=_first(rm,_EVENT_TYPE)
                slots["predicate"]=event or stmt.predicate_ref
        features={"polarity":stmt.polarity,**self._context_features(request),**self._qualifier_features(request,stmt),**{str(k):v for k,v in feature_hint.items()}}
        self._add_attachment_slots(request,attachments,roles,slots,features)
        return OperationChoice(operation_id,roles,slots,features)

    def _add_attachment_slots(self,request:CommunicationRequest,attachments:tuple[SemanticStatement,...],roles:dict[str,str],slots:dict[str,str],features:dict[str,object])->None:
        for idx,extra in enumerate(attachments,1):
            erm=_roles(extra); pred=local_name(extra.predicate_ref)
            t=_first(erm,_TIME)
            if t and "deadline" in pred:
                roles["deadline"]=t; slots["deadline"]=t; continue
            if t and pred in {"time","date","temporal_relation"}:
                roles["time"]=t; slots["time"]=t; continue
            c=_first(erm,_CONTACT)
            if c and ("contact" in pred or "support" in pred):
                roles["contact"]=c; slots["contact"]=c
                continue
            v=_first(erm,_VALUE); holder=_first(erm,_HOLDER)
            if v and ("phone" in pred or "telephone" in pred):
                if holder: roles["holder"]=holder; slots["holder"]=holder
                roles["phone"]=v; slots["phone"]=v
                continue
            # Extensible predicates remain representable without teaching the core their meaning:
            # the bridge must consume both relation and arguments or fail closed.
            slots[f"attachment{idx}_predicate"]=extra.predicate_ref
            for role_ref,value_id in ((a.role_ref,a.value_id) for a in extra.arguments):
                key=f"attachment{idx}_{local_name(role_ref)}"
                roles[key]=value_id; slots[key]=value_id
            features[f"attachment{idx}_polarity"]=extra.polarity

    def _plan_list(self,request:CommunicationRequest,item:CommunicationPlanItem,lexical_context:LexicalPlanningContext)->list[OperationChoice]:
        out=[]
        for ref in item.semantic_refs:
            obj=request.semantic_graph.get(ref)
            if isinstance(obj,CollectionValue):
                for member in obj.members:
                    target=request.semantic_graph.get(member)
                    if isinstance(target,SemanticStatement): out.append(self._choice_for_statement(request,target,item.force,(),lexical_context))
                    else: out.append(OperationChoice("nominal.apposition",{"entity":member,"description":member},{"entity":member,"description":member},{}))
            elif isinstance(obj,SemanticStatement): out.append(self._choice_for_statement(request,obj,item.force,(),lexical_context))
        return out

    def _plan_item(self,request:CommunicationRequest,item:CommunicationPlanItem,lexical_context:LexicalPlanningContext)->list[OperationChoice]:
        statements=[request.semantic_graph.get(r) for r in item.semantic_refs if isinstance(request.semantic_graph.get(r),SemanticStatement)]
        if not statements:
            refs=list(item.semantic_refs)
            expanded=[]
            for ref in refs:
                obj=request.semantic_graph.get(ref)
                if isinstance(obj,CollectionValue):
                    for member in obj.members:
                        target=request.semantic_graph.get(member)
                        if isinstance(target,SemanticStatement):
                            expanded.append(self._choice_for_statement(request,target,item.force,(),lexical_context))
            if expanded:
                return expanded
            if item.force.value=="PRESENT" and len(refs)>=2:
                return [OperationChoice("nominal.apposition",{"entity":refs[0],"description":refs[1]},{"entity":refs[0],"description":refs[1]}, self._context_features(request))]
            raise SemantikArchitectError("SA-LANG-003",f"Obligation {item.obligation_ids[0]} has no plannable statement",request_id=request.request_id)
        primary=statements[0]; attachments=tuple(statements[1:])
        return [self._choice_for_statement(request,primary,item.force,attachments,lexical_context)]

    def _choice_for_statement(self,request:CommunicationRequest,stmt:SemanticStatement,force,attachments:tuple[SemanticStatement,...],lexical_context:LexicalPlanningContext)->OperationChoice:
        hinted=self._hinted_choice(request,stmt,force,attachments,lexical_context)
        if hinted is not None:
            return hinted
        rm=_roles(stmt); roles:dict[str,str]={}; slots:dict[str,str]={}; features={"polarity":stmt.polarity,**self._context_features(request),**self._qualifier_features(request,stmt)}
        agent=_first(rm,_AGENT); patient=_first(rm,_PATIENT); recipient=_first(rm,_RECIPIENT); loc=_first(rm,_LOCATION); possessor=_first(rm,_POSSESSOR); possessed=_first(rm,_POSSESSED); attr=_first(rm,_ATTRIBUTE); klass=_first(rm,_CLASS); event=_first(rm,_EVENT_TYPE)
        predicate_semantic=event or stmt.predicate_ref
        if agent: roles["agent"]=agent; slots["agent"]=agent
        if patient: roles["patient"]=patient; slots["patient"]=patient
        if recipient: roles["recipient"]=recipient; slots["recipient"]=recipient
        if loc: roles["location"]=loc; slots["location"]=loc
        if possessor: roles["possessor"]=possessor; slots["possessor"]=possessor
        if possessed: roles["possessed"]=possessed; slots["possessed"]=possessed
        if attr: roles["attribute"]=attr; slots["attribute"]=attr
        if klass: roles["class"]=klass; slots["class"]=klass
        slots["predicate"]=predicate_semantic
        self._add_attachment_slots(request,attachments,roles,slots,features)
        if force.value=="DIRECT": op="directive.action"
        elif force.value=="ASK": op="question.content" if any(local_name(q.qualifier_ref) in {"query","question_role"} for q in stmt.qualifiers) else "question.polar"
        elif possessor and possessed: op="clause.possession"
        elif loc and (agent or patient): op="clause.locative"
        elif klass: op="clause.copular_classification"
        elif attr: op="clause.copular_attribute"
        elif agent and patient and recipient: op="clause.ditransitive_event"
        elif agent and patient: op="clause.transitive_event"
        elif agent: op="clause.intransitive_event"
        elif len(rm)==1: op="clause.existential"
        else: op="clause.copular_attribute"
        knowledge=lexical_context.entries.get(predicate_semantic) or lexical_context.entries.get(stmt.predicate_ref)
        if knowledge and knowledge.properties.get("preferred_operation"):
            op=require_known_operation(str(knowledge.properties["preferred_operation"]))
        return OperationChoice(op,roles,slots,features)
