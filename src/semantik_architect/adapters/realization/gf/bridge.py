from __future__ import annotations
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from ....application.ports.realizer import RealizationResult, RealizedUnit
from ....application.ports.runtime_catalog import RuntimeSetDescriptor, RuntimeArtifact
from ....domain.language.language_plan import LanguagePlan
from ....domain.language.lexical import LexicalBindingSet, LexicalBinding
from ....domain.errors import SemantikArchitectError
from ....domain.language.operations import V1_OPERATION_IDS
from .pgf_runtime import PgfRuntime, PgfRuntimeUnavailableError, PgfConcreteLanguageNotFoundError

_PLACEHOLDER_RE=re.compile(r"\{([A-Za-z][A-Za-z0-9_.-]*)\}")

@dataclass(frozen=True, slots=True)
class BridgeVariant:
    requires: tuple[str,...]
    expression: str
    when: Mapping[str, Any]
    consumes_features: tuple[str, ...]

@dataclass(frozen=True, slots=True)
class BridgeOperation:
    operation_id: str
    variants: tuple[BridgeVariant,...]

@dataclass(frozen=True, slots=True)
class GfBridgeSpec:
    contract_version: str
    operations: Mapping[str,BridgeOperation]
    feature_values: Mapping[str, Mapping[str, str]]

    @classmethod
    def from_dict(cls,data:Mapping[str,Any])->"GfBridgeSpec":
        if data.get('schema_version')!='1.0': raise ValueError('Unsupported GF bridge spec schema')
        ops={}
        for op_id,raw in (data.get('operations') or {}).items():
            variants=[]
            if 'expression' in raw:
                variants.append(BridgeVariant(tuple(str(x) for x in raw.get('requires',())),str(raw['expression']),dict(raw.get('when') or {}),tuple(str(x) for x in raw.get('consumes_features',()))))
            for v in raw.get('variants',()):
                variants.append(BridgeVariant(tuple(str(x) for x in v.get('requires',())),str(v['expression']),dict(v.get('when') or {}),tuple(str(x) for x in v.get('consumes_features',()))))
            if not variants: raise ValueError(f'Bridge operation {op_id} has no expression variants')
            # most-specific first so optional adjunct-aware variants win deterministically
            variants.sort(key=lambda v:(len(v.requires),v.expression),reverse=True)
            if str(op_id) not in V1_OPERATION_IDS:
                raise ValueError(f'Unknown SA↔GF v1 operation in bridge: {op_id}')
            ops[str(op_id)]=BridgeOperation(str(op_id),tuple(variants))
        return cls(str(data['contract_version']),ops,{str(k):{str(vk):str(vv) for vk,vv in dict(v).items()} for k,v in dict(data.get('feature_values') or {}).items()})

class GfBridgeRealizer:
    """Versioned SA↔GF adapter driven by an immutable bridge-spec artifact."""
    def __init__(self, runtime_factory=PgfRuntime)->None:
        self._runtime_factory=runtime_factory
        self._runtime_cache:dict[str,PgfRuntime]={}
        self._bridge_cache:dict[str,GfBridgeSpec]={}

    @staticmethod
    def _select_artifact(runtime:RuntimeSetDescriptor,kind:str, *, prefix:str|None=None)->RuntimeArtifact:
        items=[a for a in runtime.artifacts if a.artifact_type==kind and (prefix is None or a.artifact_id.startswith(prefix))]
        if len(items)!=1:
            raise SemantikArchitectError("SA-RUN-003",f"RuntimeSet {runtime.runtime_set_id} requires exactly one {kind} artifact"+(f" with prefix {prefix}" if prefix else ""),runtime_set_id=runtime.runtime_set_id,details={"found":[a.artifact_id for a in items]})
        if items[0].path is None: raise SemantikArchitectError("SA-RUN-003",f"Runtime artifact has no local path: {items[0].artifact_id}",runtime_set_id=runtime.runtime_set_id)
        return items[0]

    def _bridge(self,runtime:RuntimeSetDescriptor)->GfBridgeSpec:
        if runtime.runtime_set_id in self._bridge_cache: return self._bridge_cache[runtime.runtime_set_id]
        art=self._select_artifact(runtime,'other',prefix='sa-gf-bridge')
        try: spec=GfBridgeSpec.from_dict(json.loads(art.path.read_text(encoding='utf-8')))  # type: ignore[union-attr]
        except Exception as exc:
            raise SemantikArchitectError("SA-GF-001","GF bridge specification is invalid",runtime_set_id=runtime.runtime_set_id,details={"artifact_id":art.artifact_id,"error":str(exc)}) from exc
        if spec.contract_version != runtime.sa_gf_contract_version:
            raise SemantikArchitectError("SA-GF-001","GF bridge contract version does not match RuntimeSet",runtime_set_id=runtime.runtime_set_id,details={"bridge":spec.contract_version,"runtime":runtime.sa_gf_contract_version})
        self._bridge_cache[runtime.runtime_set_id]=spec; return spec

    def _pgf(self,runtime:RuntimeSetDescriptor)->PgfRuntime:
        if runtime.runtime_set_id in self._runtime_cache: return self._runtime_cache[runtime.runtime_set_id]
        art=self._select_artifact(runtime,'grammar')
        rt=self._runtime_factory(art.path)  # type: ignore[arg-type]
        self._runtime_cache[runtime.runtime_set_id]=rt; return rt

    @staticmethod
    def _render_binding(binding:LexicalBinding)->str:
        if binding.binding_kind=='gf_expr': return binding.lexical_ref
        if binding.binding_kind=='literal': return json.dumps(binding.lexical_ref,ensure_ascii=False)
        raise ValueError(f"Unknown lexical binding kind: {binding.binding_kind}")

    @staticmethod
    def _concrete(runtime:RuntimeSetDescriptor,language:str)->str:
        raw=runtime.capability_manifest.get('languages',{}).get(language,{})
        concrete=raw.get('concrete') if isinstance(raw,dict) else None
        if not concrete: raise SemantikArchitectError("SA-LANG-001",f"No concrete GF language declared for {language}",runtime_set_id=runtime.runtime_set_id)
        return str(concrete)

    def _expression_for_unit(self,unit,bindings:dict[str,LexicalBinding],spec:GfBridgeSpec)->str:
        op=spec.operations.get(unit.operation_id)
        if op is None: raise SemantikArchitectError("SA-GF-001",f"Operation not implemented by bridge: {unit.operation_id}")
        values={slot:self._render_binding(binding) for slot,binding in bindings.items()}
        for key,value in unit.feature_bindings.items():
            encoder=spec.feature_values.get(key,{})
            encoded=encoder.get(str(value))
            values[f"feature.{key}"]=encoded if encoded is not None else json.dumps(value,ensure_ascii=False)
        available=set(values)
        lexical_slots=set(bindings)
        semantic_features=set(unit.feature_bindings)
        variant=None
        for candidate in op.variants:
            placeholders=set(_PLACEHOLDER_RE.findall(candidate.expression))
            feature_placeholders={p.split('.',1)[1] for p in placeholders if p.startswith('feature.')}
            if any(unit.feature_bindings.get(k)!=v for k,v in candidate.when.items()):
                continue
            if not set(candidate.requires)<=available or not placeholders<=available:
                continue
            if not lexical_slots<=placeholders:
                continue
            if not semantic_features <= (feature_placeholders | set(candidate.consumes_features)):
                continue
            variant=candidate
            break
        if variant is None:
            raise SemantikArchitectError("SA-GF-001",f"No bridge variant can faithfully consume all semantic slots/features for {unit.operation_id}",details={"available_slots":sorted(available),"required_semantic_slots":sorted(lexical_slots),"semantic_features":sorted(semantic_features),"variants":[{"requires":list(v.requires),"when":dict(v.when),"consumes_features":list(v.consumes_features),"placeholders":sorted(set(_PLACEHOLDER_RE.findall(v.expression)))} for v in op.variants]})
        return _PLACEHOLDER_RE.sub(lambda m:values[m.group(1)],variant.expression)

    def realize(self,plan:LanguagePlan,bindings:LexicalBindingSet,runtime:RuntimeSetDescriptor)->RealizationResult:
        spec=self._bridge(runtime); pgf=self._pgf(runtime); concrete=self._concrete(runtime,plan.language); realized=[]
        for unit in plan.units:
            ub=bindings.for_unit(unit.unit_id)
            expr=self._expression_for_unit(unit,ub,spec)
            try: text=pgf.linearize(expr,concrete).strip()
            except (PgfRuntimeUnavailableError,PgfConcreteLanguageNotFoundError,ValueError) as exc:
                raise SemantikArchitectError("SA-GF-002",f"GF realization failed for {unit.unit_id}",runtime_set_id=runtime.runtime_set_id,details={"operation_id":unit.operation_id,"error":str(exc)}) from exc
            except Exception as exc:
                raise SemantikArchitectError("SA-GF-002",f"GF realization failed for {unit.unit_id}",runtime_set_id=runtime.runtime_set_id,details={"operation_id":unit.operation_id,"error":str(exc)}) from exc
            if not text: raise SemantikArchitectError("SA-GF-002",f"GF returned empty text for {unit.unit_id}",runtime_set_id=runtime.runtime_set_id)
            realized.append(RealizedUnit(unit.unit_id,text))
        return RealizationResult(tuple(realized))
