from __future__ import annotations
from typing import Protocol, Mapping, Any
class TelemetryPort(Protocol):
    def event(self,name:str,fields:Mapping[str,Any]|None=None)->None: ...
