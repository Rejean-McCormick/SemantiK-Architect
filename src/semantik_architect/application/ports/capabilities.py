from __future__ import annotations
from typing import Protocol
from .runtime_catalog import RuntimeSetDescriptor

class CapabilityPort(Protocol):
    def require_released(self, runtime:RuntimeSetDescriptor, language:str, capability_profile:str)->str: ...
    def list_capabilities(self, runtime:RuntimeSetDescriptor|None=None)->dict: ...
