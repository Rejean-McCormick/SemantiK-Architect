from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
from ...domain.language.language_plan import LanguagePlan
from ...domain.language.lexical import LexicalBindingSet
from .runtime_catalog import RuntimeSetDescriptor

@dataclass(frozen=True, slots=True)
class RealizedUnit:
    unit_id: str
    text: str

@dataclass(frozen=True, slots=True)
class RealizationResult:
    units: tuple[RealizedUnit,...]

    def by_id(self)->dict[str,RealizedUnit]: return {u.unit_id:u for u in self.units}

class RealizerPort(Protocol):
    def realize(self, plan:LanguagePlan, bindings:LexicalBindingSet, runtime:RuntimeSetDescriptor)->RealizationResult: ...
