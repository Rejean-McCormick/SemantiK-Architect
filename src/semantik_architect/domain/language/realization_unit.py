from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Mapping

@dataclass(frozen=True, slots=True)
class RealizationUnit:
    unit_id: str
    operation_id: str
    role_bindings: Mapping[str,str]
    feature_bindings: Mapping[str,Any] = field(default_factory=dict)
    lexical_slots: Mapping[str,str] = field(default_factory=dict)
    obligation_ids: tuple[str,...] = ()
    semantic_refs: tuple[str,...] = ()
    output_slot: str = ""

    def __post_init__(self)->None:
        object.__setattr__(self,"role_bindings",dict(self.role_bindings)); object.__setattr__(self,"feature_bindings",dict(self.feature_bindings)); object.__setattr__(self,"lexical_slots",dict(self.lexical_slots)); object.__setattr__(self,"obligation_ids",tuple(self.obligation_ids)); object.__setattr__(self,"semantic_refs",tuple(self.semantic_refs))
