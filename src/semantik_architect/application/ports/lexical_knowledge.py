from __future__ import annotations
from typing import Protocol
from ...domain.communication.request import CommunicationRequest
from ...domain.communication.communication_plan import CommunicationPlan
from ...domain.language.lexical import LexicalPlanningContext
from .runtime_catalog import RuntimeSetDescriptor

class LexicalKnowledgePort(Protocol):
    def preflight(self, request:CommunicationRequest, plan:CommunicationPlan, runtime:RuntimeSetDescriptor)->LexicalPlanningContext: ...
