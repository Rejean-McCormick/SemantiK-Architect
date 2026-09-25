from __future__ import annotations
from typing import Protocol
from ...domain.communication.request import CommunicationRequest
from ...domain.language.language_plan import LanguagePlan
from ...domain.language.lexical import LexicalPlanningContext, LexicalBindingSet
from .runtime_catalog import RuntimeSetDescriptor

class LexicalBindingPort(Protocol):
    def bind(self, request:CommunicationRequest, plan:LanguagePlan, lexical_context:LexicalPlanningContext, runtime:RuntimeSetDescriptor)->LexicalBindingSet: ...
