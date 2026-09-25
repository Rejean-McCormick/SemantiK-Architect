from __future__ import annotations
import logging
from typing import Mapping, Any
class LoggingTelemetry:
    def __init__(self,logger:logging.Logger|None=None)->None: self.logger=logger or logging.getLogger('semantik_architect.telemetry')
    def event(self,name:str,fields:Mapping[str,Any]|None=None)->None: self.logger.info('%s %s',name,dict(fields or {}))
class NullTelemetry:
    def event(self,name:str,fields:Mapping[str,Any]|None=None)->None: return None
