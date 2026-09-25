from __future__ import annotations
import json
from typing import Any
from ....application.ports.runtime_catalog import RuntimeSetDescriptor
from ....domain.errors import SemantikArchitectError
from ....domain.language.capabilities import CapabilityProfile

class ManifestCapabilityAdapter:
    def __init__(self)->None:
        self._profiles:dict[tuple[str,str],CapabilityProfile]={}

    def require_released(self,runtime:RuntimeSetDescriptor,language:str,capability_profile:str)->str:
        languages=runtime.capability_manifest.get('languages',{})
        raw=languages.get(language)
        if not isinstance(raw,dict) or raw.get('status')!='RELEASED':
            raise SemantikArchitectError("SA-LANG-001",f"Language is not released: {language}",runtime_set_id=runtime.runtime_set_id)
        for p in raw.get('profiles',[]):
            if isinstance(p,dict) and p.get('profile_id')==capability_profile:
                if p.get('status')!='RELEASED': raise SemantikArchitectError("SA-LANG-002",f"Capability profile is not released: {language} + {capability_profile}",runtime_set_id=runtime.runtime_set_id)
                return str(raw.get('concrete') or language)
        raise SemantikArchitectError("SA-LANG-002",f"Capability profile unavailable: {language} + {capability_profile}",runtime_set_id=runtime.runtime_set_id)

    def _profile_artifact(self,runtime:RuntimeSetDescriptor,identity:str):
        exact=f"capability-profile-{identity}"
        matches=[a for a in runtime.artifacts if a.artifact_type=='other' and a.artifact_id==exact]
        if not matches:
            return None
        if len(matches)!=1 or matches[0].path is None:
            raise SemantikArchitectError("SA-RUN-002",f"Invalid capability profile artifact for {identity}",runtime_set_id=runtime.runtime_set_id)
        return matches[0]

    def get_profile(self,runtime:RuntimeSetDescriptor,identity:str)->CapabilityProfile|None:
        key=(runtime.runtime_set_id,identity)
        if key in self._profiles: return self._profiles[key]
        art=self._profile_artifact(runtime,identity)
        if art is None: return None
        try:
            data=json.loads(art.path.read_text(encoding='utf-8'))
            profile=CapabilityProfile(
                profile_id=str(data['profile_id']), profile_version=int(data['profile_version']),
                required_operations=tuple(str(x) for x in data.get('required_operations',())),
                required_features=tuple(str(x) for x in data.get('required_features',())),
                required_block_kinds=tuple(str(x) for x in data.get('required_block_kinds',())),
                test_suite_ref=str(data.get('test_suite_ref') or '')
            )
        except Exception as exc:
            raise SemantikArchitectError("SA-RUN-002",f"Invalid capability profile artifact: {identity}",runtime_set_id=runtime.runtime_set_id,details={"error":str(exc)}) from exc
        if profile.identity != identity:
            raise SemantikArchitectError("SA-RUN-002",f"Capability profile identity mismatch: expected {identity}, got {profile.identity}",runtime_set_id=runtime.runtime_set_id)
        self._profiles[key]=profile; return profile

    def require_plan(self,runtime:RuntimeSetDescriptor,language:str,identity:str,plan)->None:
        self.require_released(runtime,language,identity)
        profile=self.get_profile(runtime,identity)
        raw=runtime.capability_manifest.get('languages',{}).get(language,{})
        profile_row=next((p for p in raw.get('profiles',[]) if p.get('profile_id')==identity),{}) if isinstance(raw,dict) else {}
        extensions=set(profile_row.get('extension_capabilities',()) if isinstance(profile_row,dict) else ())
        if profile is None:
            raise SemantikArchitectError("SA-RUN-003",f"Released profile artifact is missing: {identity}",runtime_set_id=runtime.runtime_set_id)
        allowed=set(profile.required_operations)|extensions
        used_ops={u.operation_id for u in plan.units}
        disallowed=sorted(used_ops-allowed)
        if disallowed:
            raise SemantikArchitectError("SA-LANG-002",f"Language plan uses operations outside released profile {identity}",runtime_set_id=runtime.runtime_set_id,details={"operations":disallowed})
        used_blocks={b.kind for b in plan.blocks}
        unsupported=sorted(used_blocks-set(profile.required_block_kinds))
        if unsupported:
            raise SemantikArchitectError("SA-LANG-002",f"Language plan uses block kinds outside released profile {identity}",runtime_set_id=runtime.runtime_set_id,details={"block_kinds":unsupported})

    def list_capabilities(self,runtime:RuntimeSetDescriptor|None=None)->dict[str,Any]:
        if runtime is None: return {}
        return {"runtime_set_id":runtime.runtime_set_id,"languages":runtime.capability_manifest.get('languages',{})}
