from __future__ import annotations

import json
from pathlib import Path

import pytest

from semantik_architect.adapters.ecosystem.mathkristal import MathKristalFormulaAcl, MathKristalProjectionError
from semantik_architect.application.planning.communication_planner import CommunicationPlanner
from semantik_architect.application.planning.language_planner import GenericLanguagePlanner
from semantik_architect.domain.language.lexical import LexicalPlanningContext

ROOT=Path(__file__).resolve().parents[2]


def payload():
    return json.loads((ROOT/'examples/mathkristal_euler_projection.json').read_text(encoding='utf-8'))


def test_mathkristal_projection_is_explicit_and_traceable():
    req=MathKristalFormulaAcl().map_request(payload(),target_language='fr',capability_profile='math-pure-1')
    assert req.context.target_language=='fr'
    assert req.capability_profile=='math-pure-1'
    assert req.obligations[0].source_refs[0]=='urn:mathkristal:proposition:euler-formula'
    stmt=req.semantic_graph.get(req.obligations[0].semantic_refs[0])
    assert stmt.predicate_ref=='urn:mathkristal:communication:present-formula'
    expression_id=stmt.arguments[0].value_id
    assert req.support_values(expression_id,'urn:semantik:math:mode')==('PURE',)
    formula=req.support_values(expression_id,'urn:semantik:math:formula-ir')[0]
    assert formula['contract']=='mathkristal.formula-ir'


def test_math_planner_emits_one_informath_operation():
    req=MathKristalFormulaAcl().map_request(payload(),target_language='fr',capability_profile='math-pure-1')
    cp=CommunicationPlanner().plan(req)
    lp=GenericLanguagePlanner().plan(req,cp,LexicalPlanningContext('fr',{}))
    assert len(lp.units)==1
    unit=lp.units[0]
    assert unit.operation_id=='math.informalize_formula'
    assert unit.feature_bindings['math_mode']=='PURE'
    assert unit.feature_bindings['math_formula_ir']['expression_ref']=='urn:mathkristal:expression:euler-formula'
    assert unit.lexical_slots=={}


def test_formula_ir_rejects_surface_language_keys():
    bad=payload(); bad['formula_ir']['nodes'][0]['label']='z variable'
    with pytest.raises(MathKristalProjectionError):
        MathKristalFormulaAcl().map_request(bad,target_language='fr',capability_profile='math-pure-1')


def test_formula_mode_must_match_profile():
    p=payload(); p['mode']='NATURAL'
    req=MathKristalFormulaAcl().map_request(p,target_language='fr',capability_profile='math-pure-1')
    cp=CommunicationPlanner().plan(req)
    with pytest.raises(Exception):
        GenericLanguagePlanner().plan(req,cp,LexicalPlanningContext('fr',{}))
