from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping

from ....application.ports.runtime_catalog import RuntimeSetDescriptor
from ....application.ports.locale_data import LocaleDataPort
from ....domain.communication.request import CommunicationRequest
from ....domain.communication.communication_plan import CommunicationPlan
from ....domain.language.language_plan import LanguagePlan
from ....domain.language.lexical import LexicalKnowledge, LexicalPlanningContext, LexicalBinding, LexicalBindingSet
from ....domain.semantics.nodes import EntityRef, ConceptRef, LiteralValue, QuantityValue, TemporalValue
from ....domain.errors import SemantikArchitectError

@dataclass(frozen=True, slots=True)
class LexiconRecord:
    semantic_ref:str
    language:str
    lexical_ref:str
    binding_kind:str="gf_expr"
    category:str|None=None
    properties:Mapping[str,Any]=field(default_factory=dict)

class RuntimeJsonLexiconAdapter:
    """Reads immutable lexical JSON artifacts selected by RuntimeSet.

    Supported artifact shape:
      {"lexicon_id":"...", "entries":[{semantic_ref,language,lexical_ref,binding_kind?,category?,properties?}]}
    """
    def __init__(self,locale_data:LocaleDataPort|None=None)->None:
        self._cache:dict[tuple[str,str],tuple[str,dict[tuple[str,str],LexiconRecord]]]={}
        self.locale_data=locale_data

    def _load(self,runtime:RuntimeSetDescriptor)->tuple[str,dict[tuple[str,str],LexiconRecord]]:
        key=(runtime.runtime_set_id,"lexical")
        if key in self._cache: return self._cache[key]
        records={}; ids=[]
        for art in runtime.artifacts_of_type('lexical'):
            if art.path is None or not art.path.is_file(): continue
            try: data=json.loads(art.path.read_text(encoding='utf-8'))
            except Exception as exc: raise SemantikArchitectError("SA-LEX-001",f"Invalid lexical artifact {art.artifact_id}",runtime_set_id=runtime.runtime_set_id,details={"error":str(exc)}) from exc
            if data.get('schema_version')!='1.0': raise SemantikArchitectError('SA-LEX-001',f'Unsupported lexical artifact schema in {art.artifact_id}',runtime_set_id=runtime.runtime_set_id)
            ids.append(str(data.get('lexicon_id') or art.artifact_id))
            for raw in data.get('entries',[]):
                try:
                    rec=LexiconRecord(str(raw['semantic_ref']),str(raw['language']),str(raw['lexical_ref']),str(raw.get('binding_kind') or 'gf_expr'),raw.get('category'),dict(raw.get('properties') or {}))
                except Exception as exc: raise SemantikArchitectError("SA-LEX-001",f"Invalid lexical record in {art.artifact_id}",details={"record":raw,"error":str(exc)}) from exc
                records[(rec.language,rec.semantic_ref)]=rec
        lexicon_id='+'.join(ids) or 'none'
        self._cache[key]=(lexicon_id,records); return self._cache[key]

    @staticmethod
    def _node_semantic_ref(request:CommunicationRequest, ref:str)->str|None:
        try: obj=request.semantic_graph.get(ref)
        except KeyError: return ref if ':' in ref else None
        if isinstance(obj,EntityRef): return obj.external_ref
        if isinstance(obj,ConceptRef): return obj.concept_ref
        return ref

    def _surface_literal(self,request:CommunicationRequest,ref:str)->str|None:
        try: obj=request.semantic_graph.get(ref)
        except KeyError: return None
        lang=request.context.target_language; locale=request.context.target_locale
        if isinstance(obj,EntityRef):
            return obj.labels.get(locale or '') or obj.labels.get(lang) or obj.labels.get(lang.split('-',1)[0])
        if isinstance(obj,LiteralValue):
            return self.locale_data.format_value(obj.value,language=lang,locale=locale,datatype=obj.datatype) if self.locale_data else str(obj.value)
        if isinstance(obj,QuantityValue):
            base=self.locale_data.format_value(obj.value,language=lang,locale=locale,datatype="quantity") if self.locale_data else str(obj.value)
            return f"{base} {obj.unit_ref}" if obj.unit_ref else base
        if isinstance(obj,TemporalValue):
            return self.locale_data.format_value(obj.value,language=lang,locale=locale,datatype=obj.temporal_kind) if self.locale_data else str(obj.value)
        return None

    def preflight(self,request:CommunicationRequest,plan:CommunicationPlan,runtime:RuntimeSetDescriptor)->LexicalPlanningContext:
        lexicon_id,records=self._load(runtime); lang=request.context.target_language
        semantic_refs=set()
        for item in plan.items:
            for ref in item.semantic_refs:
                obj=request.semantic_graph.get(ref)
                if hasattr(obj,'arguments'):
                    semantic_refs.add(getattr(obj,'predicate_ref'))
                    for arg in obj.arguments:
                        semantic_refs.add(self._node_semantic_ref(request,arg.value_id) or arg.value_id)
                        semantic_refs.add(arg.value_id)
                else: semantic_refs.add(self._node_semantic_ref(request,ref) or ref)
        entries={}
        for ref in semantic_refs:
            semantic_ref=self._node_semantic_ref(request,ref) or ref
            rec=records.get((lang,semantic_ref))
            surface=self._surface_literal(request,ref)
            if rec:
                entries[ref]=LexicalKnowledge(ref,lang,True,(rec.lexical_ref,),rec.category,rec.properties)
                if semantic_ref!=ref: entries[semantic_ref]=entries[ref]
            elif surface is not None:
                entries[ref]=LexicalKnowledge(ref,lang,True,(surface,),"LITERAL",{"binding_kind":"literal"})
                if semantic_ref!=ref: entries[semantic_ref]=entries[ref]
            else:
                entries[ref]=LexicalKnowledge(ref,lang,False,(),None,{})
                if semantic_ref!=ref: entries[semantic_ref]=entries[ref]
        return LexicalPlanningContext(lang,entries,(lexicon_id,))

    def bind(self,request:CommunicationRequest,plan:LanguagePlan,lexical_context:LexicalPlanningContext,runtime:RuntimeSetDescriptor)->LexicalBindingSet:
        lexicon_id,records=self._load(runtime); out=[]; lang=request.context.target_language
        for unit in plan.units:
            for slot,ref in unit.lexical_slots.items():
                semantic_ref=self._node_semantic_ref(request,ref) or ref
                rec=records.get((lang,semantic_ref))
                if rec:
                    out.append(LexicalBinding(unit.unit_id,slot,rec.lexical_ref,rec.binding_kind,semantic_ref)); continue
                surface=self._surface_literal(request,ref)
                if surface is not None:
                    out.append(LexicalBinding(unit.unit_id,slot,surface,'literal',semantic_ref)); continue
                # statement predicates may be lexicalized by exact semantic predicate ref
                rec=records.get((lang,ref))
                if rec:
                    out.append(LexicalBinding(unit.unit_id,slot,rec.lexical_ref,rec.binding_kind,ref)); continue
                # predicate slots are allowed to use the semantic predicate itself only if lexicon knows it; no guessing.
                raise SemantikArchitectError("SA-LEX-002",f"No exact lexical binding for {ref} in {lang}",request_id=request.request_id,runtime_set_id=runtime.runtime_set_id,details={"unit_id":unit.unit_id,"slot":slot,"semantic_ref":semantic_ref})
        return LexicalBindingSet(lexicon_id,tuple(out))
