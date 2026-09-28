from __future__ import annotations
from datetime import date, datetime, time
from typing import Any


class BasicLocaleDataAdapter:
    """Deterministic conservative formatter. Rich locale data belongs in RuntimeSet artifacts."""

    @staticmethod
    def _structured(value: Any, language: str) -> str:
        base=language.split('-',1)[0].lower()
        if isinstance(value,bool):
            if base=='fr': return 'oui' if value else 'non'
            return 'yes' if value else 'no'
        if value is None:
            return 'aucune valeur' if base=='fr' else 'none'
        if isinstance(value,list):
            if not value: return 'aucune valeur' if base=='fr' else 'none'
            return '; '.join(BasicLocaleDataAdapter._structured(v,language) for v in value)
        if isinstance(value,dict):
            if 'predicate' in value and 'object' in value:
                return f"{BasicLocaleDataAdapter._structured(value['predicate'],language)} : {BasicLocaleDataAdapter._structured(value['object'],language)}"
            if 'label' in value and isinstance(value.get('label'),str):
                return value['label']
            if set(value).issuperset({'kind','value'}):
                return BasicLocaleDataAdapter._structured(value['value'],language)
            return '; '.join(f"{k}: {BasicLocaleDataAdapter._structured(v,language)}" for k,v in value.items())
        return str(value)

    def format_value(self,value:Any,*,language:str,locale:str|None,datatype:str|None=None)->str:
        if isinstance(value,(datetime,date,time)): return value.isoformat()
        if datatype=='json' or isinstance(value,(dict,list,tuple,bool)):
            return self._structured(value,language)
        return str(value)
