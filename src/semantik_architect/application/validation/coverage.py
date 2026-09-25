from __future__ import annotations
from ...domain.communication.request import CommunicationRequest
from ...domain.communication.result import CoverageEntry
from ...domain.language.language_plan import LanguagePlan
from ...domain.errors import SemantikArchitectError

class CoverageValidator:
    def validate_plan(self, request:CommunicationRequest, plan:LanguagePlan)->None:
        expected={o.obligation_id for o in request.obligations}
        covered={oid for u in plan.units for oid in u.obligation_ids}
        missing=sorted(expected-covered)
        unknown=sorted(covered-expected)
        semantic_missing={}
        for obligation in request.obligations:
            represented={ref for u in plan.units if obligation.obligation_id in u.obligation_ids for ref in u.semantic_refs}
            absent=sorted(set(obligation.semantic_refs)-represented)
            if absent: semantic_missing[obligation.obligation_id]=absent
        if missing or unknown or semantic_missing:
            raise SemantikArchitectError("SA-SEM-002","Language plan does not cover exactly the submitted obligations and semantic references",request_id=request.request_id,details={"missing":missing,"unknown":unknown,"semantic_missing":semantic_missing})

    def validate_result(self, request:CommunicationRequest, coverage:tuple[CoverageEntry,...])->None:
        expected={o.obligation_id for o in request.obligations}
        got={c.obligation_id for c in coverage}
        if expected != got:
            raise SemantikArchitectError("SA-SEM-002","Result coverage is incomplete",request_id=request.request_id,details={"missing":sorted(expected-got),"unknown":sorted(got-expected)})
        for c in coverage:
            if not c.block_ids or not c.realization_unit_ids:
                raise SemantikArchitectError("SA-SEM-002",f"Obligation {c.obligation_id} has empty output coverage",request_id=request.request_id)
