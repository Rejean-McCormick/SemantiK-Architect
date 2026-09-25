from __future__ import annotations
from datetime import date, datetime, time
from typing import Any

class BasicLocaleDataAdapter:
    """Deterministic conservative formatter. Rich locale data belongs in RuntimeSet artifacts."""
    def format_value(self,value:Any,*,language:str,locale:str|None,datatype:str|None=None)->str:
        if isinstance(value,(datetime,date,time)): return value.isoformat()
        return str(value)
