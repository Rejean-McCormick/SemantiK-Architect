from __future__ import annotations
import time
from dataclasses import replace
from datetime import datetime, timezone
from typing import Any

from ...domain.communication.request import CommunicationRequest
from ...domain.communication.result import CommunicationResult
from ...domain.errors import SemantikArchitectError
from ..validation.request_validation import RequestValidator
from ..validation.coverage import CoverageValidator
from ..planning.communication_planner import CommunicationPlanner
from ..planning.language_planner import GenericLanguagePlanner
from ..output import OutputAssembler
from ..ports.runtime_catalog import RuntimeCatalogPort
from ..ports.capabilities import CapabilityPort
from ..ports.lexical_knowledge import LexicalKnowledgePort
from ..ports.lexical_binding import LexicalBindingPort
from ..ports.realizer import RealizerPort
from ..ports.telemetry import TelemetryPort

class RenderCommunication:
    def __init__(self,*,runtime_catalog:RuntimeCatalogPort,capabilities:CapabilityPort,lexical_knowledge:LexicalKnowledgePort,lexical_binding:LexicalBindingPort,realizer:RealizerPort,sa_version:str="1.0.0",telemetry:TelemetryPort|None=None) -> None:
        self.runtime_catalog=runtime_catalog; self.capabilities=capabilities; self.lexical_knowledge=lexical_knowledge; self.lexical_binding=lexical_binding; self.realizer=realizer; self.sa_version=sa_version; self.telemetry=telemetry
        self.request_validator=RequestValidator(); self.coverage=CoverageValidator(); self.communication_planner=CommunicationPlanner(); self.language_planner=GenericLanguagePlanner(); self.output=OutputAssembler()

    @staticmethod
    def _check_deadline(request:CommunicationRequest)->None:
        if not request.deadline: return
        deadline=datetime.fromisoformat(request.deadline.replace('Z','+00:00'))
        if deadline.tzinfo is None: deadline=deadline.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc)>=deadline:
            raise SemantikArchitectError("SA-OPS-001","Request deadline has been exceeded",request_id=request.request_id)

    def execute(self,request:CommunicationRequest)->CommunicationResult:
        started=time.perf_counter(); self._check_deadline(request); self.request_validator.validate(request)
        if self.telemetry: self.telemetry.event("render.start",{"request_id":request.request_id,"language":request.context.target_language,"profile":request.capability_profile})
        runtime_id=request.runtime_selector.runtime_set_id if request.runtime_selector else None
        runtime=self.runtime_catalog.resolve(request.context.target_language,request.capability_profile,runtime_id)
        self.capabilities.require_released(runtime,request.context.target_language,request.capability_profile)
        self._check_deadline(request)
        communication_plan=self.communication_planner.plan(request)
        lexical_context=self.lexical_knowledge.preflight(request,communication_plan,runtime)
        language_plan=self.language_planner.plan(request,communication_plan,lexical_context)
        require_plan=getattr(self.capabilities,"require_plan",None)
        if callable(require_plan):
            require_plan(runtime,request.context.target_language,request.capability_profile,language_plan)
        self.coverage.validate_plan(request,language_plan)
        bindings=self.lexical_binding.bind(request,language_plan,lexical_context,runtime)
        realization=self.realizer.realize(language_plan,bindings,runtime)
        result=self.output.assemble(request,language_plan,realization,runtime,sa_version=self.sa_version)
        if request.constraints.max_length is not None and len(result.plain_text or "") > request.constraints.max_length:
            raise SemantikArchitectError("SA-CON-001","Rendered communication exceeds max_length and cannot be truncated without changing required meaning",request_id=request.request_id,runtime_set_id=runtime.runtime_set_id,details={"max_length":request.constraints.max_length,"actual_length":len(result.plain_text or "")})
        self.coverage.validate_result(request,result.coverage); self._check_deadline(request)
        elapsed=round((time.perf_counter()-started)*1000,3)
        if self.telemetry: self.telemetry.event("render.success",{"request_id":request.request_id,"runtime_set_id":runtime.runtime_set_id,"elapsed_ms":elapsed})
        return replace(result,operational={"elapsed_ms":elapsed})
