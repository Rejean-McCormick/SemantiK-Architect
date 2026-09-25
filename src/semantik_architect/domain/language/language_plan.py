from __future__ import annotations
from dataclasses import dataclass
from .realization_unit import RealizationUnit

@dataclass(frozen=True, slots=True)
class LanguageBlockPlan:
    block_id: str
    kind: str
    unit_ids: tuple[str,...]
    obligation_ids: tuple[str,...]

@dataclass(frozen=True, slots=True)
class LanguagePlan:
    plan_id: str
    language: str
    locale: str | None
    blocks: tuple[LanguageBlockPlan,...]
    units: tuple[RealizationUnit,...]
    capability_profile: str

    def __post_init__(self)->None:
        object.__setattr__(self,"blocks",tuple(self.blocks)); object.__setattr__(self,"units",tuple(self.units))
        unit_ids={u.unit_id for u in self.units}
        for b in self.blocks:
            missing=set(b.unit_ids)-unit_ids
            if missing: raise ValueError(f"Language block {b.block_id} references missing units: {sorted(missing)}")

    @property
    def unit_by_id(self)->dict[str,RealizationUnit]: return {u.unit_id:u for u in self.units}
