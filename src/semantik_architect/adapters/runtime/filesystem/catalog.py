from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from ....application.ports.runtime_catalog import RuntimeArtifact, RuntimeSetDescriptor
from ....domain.errors import SemantikArchitectError


class FilesystemRuntimeCatalog:
    """Immutable RuntimeSet catalog backed by manifest files on disk.

    Layout is intentionally simple: any `runtime.manifest.json` under root is
    discovered. Artifact paths are relative to that manifest unless absolute.
    """
    def __init__(self, root: str | Path, *, sa_version: str = "1.0.0") -> None:
        self.root=Path(root).expanduser().resolve()
        self.sa_version=sa_version
        self._cache: dict[str, RuntimeSetDescriptor] | None=None

    @staticmethod
    def _load_json(path:Path)->dict[str,Any]:
        try:
            data=json.loads(path.read_text(encoding='utf-8'))
        except FileNotFoundError as exc:
            raise SemantikArchitectError("SA-RUN-001",f"Runtime file not found: {path}") from exc
        except Exception as exc:
            raise SemantikArchitectError("SA-RUN-002",f"Invalid runtime JSON: {path}",details={"error":str(exc)}) from exc
        if not isinstance(data,dict):
            raise SemantikArchitectError("SA-RUN-002",f"Runtime JSON must be an object: {path}")
        return data

    @staticmethod
    def _sha256(path:Path)->str:
        h=hashlib.sha256()
        with path.open('rb') as f:
            for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
        return h.hexdigest()

    @staticmethod
    def _version_tuple(value:str)->tuple[int,...]:
        parts=[]
        for part in str(value).split('.'):
            digits=''.join(ch for ch in part if ch.isdigit())
            if not digits: break
            parts.append(int(digits))
        return tuple(parts or [0])

    def _version_compatible(self,spec:str)->bool:
        current=self._version_tuple(self.sa_version)
        for clause in (x.strip() for x in str(spec).split(',') if x.strip()):
            if clause.startswith('>=') and current < self._version_tuple(clause[2:]): return False
            if clause.startswith('>') and not clause.startswith('>=') and current <= self._version_tuple(clause[1:]): return False
            if clause.startswith('<=') and current > self._version_tuple(clause[2:]): return False
            if clause.startswith('<') and not clause.startswith('<=') and current >= self._version_tuple(clause[1:]): return False
            if clause.startswith('==') and current != self._version_tuple(clause[2:]): return False
        return True

    def _active_binding(self,language:str,profile:str)->str|None:
        p=self.root/'activation.json'
        if not p.is_file(): return None
        data=self._load_json(p)
        if data.get('schema_version')!='1.0':
            raise SemantikArchitectError("SA-RUN-002","Unsupported activation schema")
        bindings=data.get('bindings') or {}
        value=bindings.get(f"{language}|{profile}") if isinstance(bindings,dict) else None
        return str(value) if value else None

    def _load_descriptor(self,path:Path)->RuntimeSetDescriptor:
        manifest=self._load_json(path)
        if manifest.get('schema_version')!='1.0':
            raise SemantikArchitectError("SA-RUN-002",f"Unsupported runtime manifest schema in {path}")
        artifacts=[]
        for raw in manifest.get('artifacts',[]):
            p=raw.get('path'); resolved=None
            if p:
                resolved=Path(p)
                if not resolved.is_absolute(): resolved=(path.parent/resolved).resolve()
            artifacts.append(RuntimeArtifact(str(raw['artifact_type']),str(raw['artifact_id']),str(raw['sha256']).lower(),resolved,raw.get('license_ref'),raw.get('provenance_ref')))
        cap_ref=str(manifest.get('capability_manifest_ref') or '')
        cap_path=Path(cap_ref)
        if not cap_path.is_absolute(): cap_path=(path.parent/cap_path).resolve()
        capabilities=self._load_json(cap_path)
        if str(capabilities.get('runtime_set_id') or '') != str(manifest['runtime_set_id']):
            raise SemantikArchitectError('SA-RUN-002',f'Capability manifest runtime_set_id mismatch in {path}')
        if not self._version_compatible(str(manifest.get('sa_version_range') or '')):
            raise SemantikArchitectError('SA-RUN-003',f'RuntimeSet is incompatible with SA {self.sa_version}',runtime_set_id=str(manifest['runtime_set_id']))
        return RuntimeSetDescriptor(str(manifest['runtime_set_id']),str(manifest['sa_gf_contract_version']),str(manifest['status']),tuple(artifacts),capabilities,manifest,path.parent.resolve())

    def _scan(self)->dict[str,RuntimeSetDescriptor]:
        out={}
        if not self.root.exists(): return out
        paths=sorted(self.root.rglob('runtime.manifest.json'))
        # also admit explicit *.runtime.json manifests
        paths.extend(p for p in sorted(self.root.rglob('*.runtime.json')) if p not in paths)
        for p in paths:
            desc=self._load_descriptor(p)
            if desc.runtime_set_id in out:
                raise SemantikArchitectError("SA-RUN-002",f"Duplicate runtime_set_id: {desc.runtime_set_id}")
            out[desc.runtime_set_id]=desc
        return out

    def refresh(self)->None: self._cache=self._scan()
    def _all(self)->dict[str,RuntimeSetDescriptor]:
        if self._cache is None: self.refresh()
        return self._cache or {}

    def list_runtime_sets(self)->tuple[RuntimeSetDescriptor,...]: return tuple(self._all().values())

    def _language_profile_released(self,desc:RuntimeSetDescriptor,language:str,profile:str)->bool:
        lang=desc.capability_manifest.get('languages',{}).get(language)
        if not isinstance(lang,dict) or lang.get('status')!='RELEASED': return False
        return any(isinstance(p,dict) and p.get('profile_id')==profile and p.get('status')=='RELEASED' for p in lang.get('profiles',[]))

    def resolve(self,language:str,capability_profile:str,runtime_set_id:str|None=None)->RuntimeSetDescriptor:
        allsets=self._all()
        if runtime_set_id:
            desc=allsets.get(runtime_set_id)
            if desc is None: raise SemantikArchitectError("SA-RUN-001",f"RuntimeSet not found: {runtime_set_id}",runtime_set_id=runtime_set_id)
            self._ensure_ready(desc)
            return desc
        active=self._active_binding(language,capability_profile)
        if active:
            desc=allsets.get(active)
            if desc is None: raise SemantikArchitectError("SA-RUN-001",f"Activated RuntimeSet not found: {active}")
            if not self._language_profile_released(desc,language,capability_profile):
                raise SemantikArchitectError("SA-RUN-003",f"Activated RuntimeSet does not release {language} + {capability_profile}",runtime_set_id=active)
            self._ensure_ready(desc); return desc
        candidates=[d for d in allsets.values() if d.status=='RELEASED' and self._language_profile_released(d,language,capability_profile)]
        if not candidates:
            raise SemantikArchitectError("SA-RUN-001",f"No released RuntimeSet for {language} + {capability_profile}")
        if len(candidates)>1:
            raise SemantikArchitectError("SA-RUN-003",f"Multiple released RuntimeSets exist for {language} + {capability_profile}; activation.json or request pinning is required",details={"runtime_set_ids":sorted(d.runtime_set_id for d in candidates)})
        desc=candidates[0]; self._ensure_ready(desc); return desc

    def _ensure_ready(self,desc:RuntimeSetDescriptor)->None:
        if desc.status!='RELEASED': raise SemantikArchitectError("SA-RUN-003",f"RuntimeSet is not RELEASED: {desc.runtime_set_id}",runtime_set_id=desc.runtime_set_id)
        report=self.validate(desc.runtime_set_id)
        if not report['valid']:
            raise SemantikArchitectError("SA-RUN-002",f"RuntimeSet integrity failed: {desc.runtime_set_id}",runtime_set_id=desc.runtime_set_id,details={"errors":report['errors']})

    def validate(self,runtime_set_id:str)->dict[str,Any]:
        desc=self._all().get(runtime_set_id)
        if desc is None: return {"runtime_set_id":runtime_set_id,"valid":False,"errors":["runtime_set_not_found"]}
        errors=[]
        for a in desc.artifacts:
            if a.path is None: continue
            if not a.path.is_file(): errors.append(f"missing:{a.artifact_id}:{a.path}"); continue
            actual=self._sha256(a.path)
            if actual.lower()!=a.sha256.lower(): errors.append(f"sha256:{a.artifact_id}:expected={a.sha256}:actual={actual}")
        cap_ref=str(desc.manifest.get('capability_manifest_ref') or '')
        cap_path=Path(cap_ref)
        if not cap_path.is_absolute(): cap_path=(desc.root/cap_path).resolve()
        cap_expected=str(desc.manifest.get('capability_manifest_sha256') or '').lower()
        if not cap_path.is_file(): errors.append(f"missing_capability_manifest:{cap_ref}")
        elif not cap_expected or self._sha256(cap_path).lower()!=cap_expected: errors.append(f"sha256:capability_manifest:{cap_ref}")
        evidence=desc.manifest.get('conformance_evidence_refs',[])
        evidence_hashes=desc.manifest.get('conformance_evidence_sha256',{}) or {}
        for ref in evidence:
            p=Path(ref)
            if not p.is_absolute(): p=(desc.root/p).resolve()
            if not p.is_file(): errors.append(f"missing_conformance_evidence:{ref}"); continue
            expected=str(evidence_hashes.get(ref) or '').lower() if isinstance(evidence_hashes,dict) else ''
            if not expected or self._sha256(p).lower()!=expected: errors.append(f"sha256:conformance_evidence:{ref}")
            try:
                edata=self._load_json(p)
                if edata.get('passed') is not True: errors.append(f"conformance_not_passed:{ref}")
            except SemantikArchitectError:
                errors.append(f"invalid_conformance_evidence:{ref}")
        return {"runtime_set_id":runtime_set_id,"valid":not errors,"errors":errors}
