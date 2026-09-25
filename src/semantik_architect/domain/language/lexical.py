from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Mapping

@dataclass(frozen=True, slots=True)
class LexicalKnowledge:
    semantic_ref: str
    language: str
    available: bool
    candidate_refs: tuple[str,...] = ()
    category: str | None = None
    properties: Mapping[str,Any] = field(default_factory=dict)

@dataclass(frozen=True, slots=True)
class LexicalPlanningContext:
    language: str
    entries: Mapping[str,LexicalKnowledge]
    lexical_artifact_ids: tuple[str,...] = ()

    def __post_init__(self)->None: object.__setattr__(self,"entries",dict(self.entries)); object.__setattr__(self,"lexical_artifact_ids",tuple(self.lexical_artifact_ids))

@dataclass(frozen=True, slots=True)
class LexicalBinding:
    unit_id: str
    slot_id: str
    lexical_ref: str
    binding_kind: str = "gf_expr"  # gf_expr | literal
    semantic_ref: str | None = None

@dataclass(frozen=True, slots=True)
class LexicalBindingSet:
    runtime_lexicon_id: str
    bindings: tuple[LexicalBinding,...]

    def __post_init__(self)->None: object.__setattr__(self,"bindings",tuple(self.bindings))
    def for_unit(self,unit_id:str)->dict[str,LexicalBinding]: return {b.slot_id:b for b in self.bindings if b.unit_id==unit_id}
