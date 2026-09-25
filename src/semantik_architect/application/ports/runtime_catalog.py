from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Protocol, Any

@dataclass(frozen=True, slots=True)
class RuntimeArtifact:
    artifact_type: str
    artifact_id: str
    sha256: str
    path: Path | None = None
    license_ref: str | None = None
    provenance_ref: str | None = None

@dataclass(frozen=True, slots=True)
class RuntimeSetDescriptor:
    runtime_set_id: str
    sa_gf_contract_version: str
    status: str
    artifacts: tuple[RuntimeArtifact,...]
    capability_manifest: Mapping[str,Any]
    manifest: Mapping[str,Any]
    root: Path

    def artifacts_of_type(self,kind:str)->tuple[RuntimeArtifact,...]: return tuple(a for a in self.artifacts if a.artifact_type==kind)
    def artifact_by_id(self,artifact_id:str)->RuntimeArtifact:
        for a in self.artifacts:
            if a.artifact_id==artifact_id: return a
        raise KeyError(artifact_id)

class RuntimeCatalogPort(Protocol):
    def resolve(self, language:str, capability_profile:str, runtime_set_id:str|None=None)->RuntimeSetDescriptor: ...
    def list_runtime_sets(self)->tuple[RuntimeSetDescriptor,...]: ...
    def validate(self, runtime_set_id:str)->dict[str,Any]: ...
