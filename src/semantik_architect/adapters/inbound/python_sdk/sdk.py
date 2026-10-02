from __future__ import annotations
from pathlib import Path
from typing import Any, Mapping
from ....bootstrap import build_container, ApplicationContainer
from ....domain.communication.request import CommunicationRequest
from ....domain.errors import SemantikArchitectError
from ...ecosystem import MathKristalFormulaAcl

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


    def project_mathkristal(self,payload:Mapping[str,Any],*,target_language:str,target_locale:str|None=None,mode:str="PURE",capability_profile:str|None=None)->dict[str,Any]:
        projection=dict(payload)
        projection.setdefault("contract",MathKristalFormulaAcl.CONTRACT)
        projection["mode"]=mode.upper()
        profile=capability_profile or ("math-pure-1" if mode.upper()=="PURE" else "math-natural-1")
        req=MathKristalFormulaAcl().map_request(projection,target_language=target_language,target_locale=target_locale,capability_profile=profile)
        return req.to_dict()

    def render_mathkristal(self,payload:Mapping[str,Any],*,target_language:str,target_locale:str|None=None,mode:str="PURE",capability_profile:str|None=None)->dict[str,Any]:
        request=self.project_mathkristal(payload,target_language=target_language,target_locale=target_locale,mode=mode,capability_profile=capability_profile)
        return self.render(request)

    def capabilities(self)->dict[str,Any]: return self._c.list_capabilities.execute()
    def validate_runtime(self,runtime_set_id:str)->dict[str,Any]: return self._c.validate_runtime.execute(runtime_set_id)
