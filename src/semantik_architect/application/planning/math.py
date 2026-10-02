from __future__ import annotations

from hashlib import sha256

from ...domain.communication.request import CommunicationRequest
from ...domain.communication.communication_plan import CommunicationPlan
from ...domain.language.language_plan import LanguagePlan, LanguageBlockPlan
from ...domain.language.realization_unit import RealizationUnit
from ...domain.errors import SemantikArchitectError
from ...domain.semantics.statements import SemanticStatement

MODE_PROP = "urn:semantik:math:mode"
FORMULA_PROP = "urn:semantik:math:formula-ir"
PRESENT_PREDICATE = "urn:mathkristal:communication:present-formula"


def _support_one(request: CommunicationRequest, subject_id: str, prop: str):
    values = request.support_values(subject_id, prop)
    if len(values) != 1:
        raise SemantikArchitectError(
            "SA-MATH-001",
            f"Math profile requires exactly one {prop} supporting value",
            request_id=request.request_id,
            details={"subject_id": subject_id, "count": len(values)},
        )
    return values[0]


def plan(request: CommunicationRequest, communication_plan: CommunicationPlan) -> LanguagePlan:
    mode = "PURE" if request.capability_profile == "math-pure-1" else "NATURAL"
    units: list[RealizationUnit] = []
    blocks: list[LanguageBlockPlan] = []
    seq = 0
    for block_seq, item in enumerate(communication_plan.items, 1):
        generated: list[str] = []
        for ref in item.semantic_refs:
            obj = request.semantic_graph.get(ref)
            if not isinstance(obj, SemanticStatement) or obj.predicate_ref != PRESENT_PREDICATE:
                raise SemantikArchitectError(
                    "SA-MATH-001",
                    "Math capability profiles only accept explicit present-formula articulation statements",
                    request_id=request.request_id,
                    details={"semantic_ref": ref, "predicate_ref": getattr(obj, "predicate_ref", None)},
                )
            rolemap = {str(a.role_ref).rsplit(":",1)[-1].replace("-","_"): a.value_id for a in obj.arguments}
            expression_id = rolemap.get("expression")
            if not expression_id:
                raise SemantikArchitectError("SA-MATH-001", "Math articulation statement has no expression role", request_id=request.request_id)
            formula = _support_one(request, expression_id, FORMULA_PROP)
            declared_mode = str(_support_one(request, expression_id, MODE_PROP)).upper()
            if declared_mode != mode:
                raise SemantikArchitectError(
                    "SA-MATH-001",
                    "Math articulation mode does not match capability profile",
                    request_id=request.request_id,
                    details={"declared_mode": declared_mode, "expected_mode": mode},
                )
            seq += 1
            unit_id = f"math{seq}"
            units.append(RealizationUnit(
                unit_id=unit_id,
                operation_id="math.informalize_formula",
                role_bindings={"expression": expression_id},
                feature_bindings={
                    "math_mode": mode,
                    "math_formula_ir": formula,
                    "register": request.context.register or "mathematical",
                },
                lexical_slots={},
                obligation_ids=item.obligation_ids,
                semantic_refs=(ref,),
                output_slot=f"b{block_seq}",
            ))
            generated.append(unit_id)
        if generated:
            blocks.append(LanguageBlockPlan(f"b{block_seq}", "utterance", tuple(generated), item.obligation_ids))
    stable = "|".join([communication_plan.plan_id, request.context.target_language, request.capability_profile, *(u.unit_id for u in units)])
    return LanguagePlan(
        plan_id="lp:" + sha256(stable.encode()).hexdigest()[:20],
        language=request.context.target_language,
        locale=request.context.target_locale,
        blocks=tuple(blocks),
        units=tuple(units),
        capability_profile=request.capability_profile,
    )
