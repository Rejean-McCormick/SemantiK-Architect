from __future__ import annotations

from ...application.ports.realizer import RealizationResult, RealizedUnit
from ...domain.language.language_plan import LanguagePlan
from ...domain.language.lexical import LexicalBindingSet
from ...application.ports.runtime_catalog import RuntimeSetDescriptor
from .gf import GfBridgeRealizer
from .informath import InformathMathRealizer


class CompositeRealizer:
    """Route realization units to their authoritative realization backend."""

    def __init__(self, gf=None, informath=None) -> None:
        self.gf = gf or GfBridgeRealizer()
        self.informath = informath or InformathMathRealizer()

    @staticmethod
    def _subplan(plan: LanguagePlan, units) -> LanguagePlan:
        ids = {u.unit_id for u in units}
        blocks = tuple(
            type(b)(b.block_id, b.kind, tuple(x for x in b.unit_ids if x in ids), b.obligation_ids)
            for b in plan.blocks if any(x in ids for x in b.unit_ids)
        )
        return LanguagePlan(plan.plan_id, plan.language, plan.locale, blocks, tuple(units), plan.capability_profile)

    def realize(self, plan: LanguagePlan, bindings: LexicalBindingSet, runtime: RuntimeSetDescriptor) -> RealizationResult:
        math_units = [u for u in plan.units if u.operation_id == "math.informalize_formula"]
        gf_units = [u for u in plan.units if u.operation_id != "math.informalize_formula"]
        out: dict[str, RealizedUnit] = {}
        if gf_units:
            result = self.gf.realize(self._subplan(plan, gf_units), bindings, runtime)
            out.update(result.by_id())
        if math_units:
            result = self.informath.realize(self._subplan(plan, math_units), bindings, runtime)
            out.update(result.by_id())
        return RealizationResult(tuple(out[u.unit_id] for u in plan.units))
