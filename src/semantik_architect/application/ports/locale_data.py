from __future__ import annotations
from typing import Protocol, Any
class LocaleDataPort(Protocol):
    def format_value(self, value:Any, *, language:str, locale:str|None, datatype:str|None=None)->str: ...
