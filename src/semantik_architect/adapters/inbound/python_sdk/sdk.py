from __future__ import annotations
from pathlib import Path
from typing import Any, Mapping
from ....bootstrap import build_container, ApplicationContainer
from ....domain.communication.request import CommunicationRequest
from ....domain.errors import SemantikArchitectError

class SemantikArchitect:
    """Stable Python-facing facade over the canonical application use cases."""
    def __init__(self,container:ApplicationContainer)->None: self._c=container

    @classmethod
    def from_runtime_root(cls,runtime_root:str|Path,*,sa_version:str="1.0.0")->"SemantikArchitect":
        return cls(build_container(runtime_root,sa_version=sa_version))

    @staticmethod
    def _request(request:CommunicationRequest|Mapping[str,Any])->CommunicationRequest:
        if isinstance(request,CommunicationRequest): return request
        try: return CommunicationRequest.from_dict(request)
        except SemantikArchitectError: raise
        except Exception as exc: raise SemantikArchitectError("SA-REQ-001",str(exc)) from exc

    def render(self,request:CommunicationRequest|Mapping[str,Any])->dict[str,Any]:
        return self._c.render.execute(self._request(request)).to_dict()

    def validate_request(self,request:CommunicationRequest|Mapping[str,Any])->dict[str,Any]:
        return self._c.validate_request.execute(self._request(request))

    def explain(self,request:CommunicationRequest|Mapping[str,Any])->dict[str,Any]:
        return self._c.explain.execute(self._request(request))

    def capabilities(self)->dict[str,Any]: return self._c.list_capabilities.execute()
    def validate_runtime(self,runtime_set_id:str)->dict[str,Any]: return self._c.validate_runtime.execute(runtime_set_id)
