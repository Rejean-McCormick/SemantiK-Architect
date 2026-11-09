"""Test the existing SemantiK planner + lexical binding + GF expression bridge.
All stub PGFs here are explicitly fake; real GF compilation is a Windows milestone.
"""
import hashlib
import json
from pathlib import Path
import shutil
import pytest

from semantik_architect.adapters.inbound.cli.defluens_core import catalog, compose_core_request
from semantik_architect.domain.communication.request import CommunicationRequest
from semantik_architect.conformance.candidate import CandidateConformance
from semantik_architect.adapters.realization.gf.bridge import GfBridgeRealizer

SOURCE=Path(__file__).resolve().parents[2]/'profiles'/'defluens-core-1'

def candidate(tmp_path,lang):
    rid=f'defluens-core-{lang}-1'
    for dst,src in [('bridge.json',f'bridge.{lang}.json'),('lexicon.json',f'lexicon.{lang}.json'),('profile.json',f'profile.{lang}.json'),('conformance.suite.json',f'conformance.{lang}.suite.json')]:
        shutil.copy2(SOURCE/src,tmp_path/dst)
    (tmp_path/'grammar.pgf').write_bytes(b'NOT_REAL_GF')
    sha=lambda name:hashlib.sha256((tmp_path/name).read_bytes()).hexdigest()
    lock={'schema_version':'1.0','runtime_set_id':rid,'language':lang,'profile_id':rid,'concrete':'DefluensCoreFre' if lang=='fr' else 'DefluensCoreEng','sa_gf_contract_version':'1.0','inputs':{x:sha(x) for x in ('grammar.pgf','bridge.json','lexicon.json','profile.json','conformance.suite.json')}}
    (tmp_path/'pipeline.lock.json').write_text(json.dumps(lock))
    return CandidateConformance(tmp_path,rid)

@pytest.mark.parametrize('lang',['fr','en'])
@pytest.mark.parametrize('intent',list(catalog()['intents']))
def test_all_six_semantic_families_build_gf_expression(lang,intent,tmp_path):
    spec=catalog()['intents'][intent]
    row={'intent':intent,'concept':spec['options'][0],'polarity':'negative'}
    if spec.get('requires_subject',True):row['subject']='mira'
    if spec.get('supports_tense',True):row['tense']='past'
    if spec.get('requires_object'):row['object']='book'
    request=compose_core_request({'language':lang,'items':[row]})
    c=candidate(tmp_path,lang)
    plan=c.plan(request)
    assert [u.operation_id for u in plan.units]==[spec['operation']]
    from semantik_architect.application.planning.communication_planner import CommunicationPlanner
    req=CommunicationRequest.from_dict(request)
    cp=CommunicationPlanner().plan(req)
    lc=c.lexicon.preflight(req,cp,c.runtime)
    bindings=c.lexicon.bind(req,plan,lc,c.runtime)
    realizer=GfBridgeRealizer()
    expression=realizer._expression_for_unit(plan.units[0],bindings.for_unit(plan.units[0].unit_id),realizer._bridge(c.runtime))
    assert expression.startswith('Realize')
    assert '{' not in expression and '}' not in expression
    assert 'Negative_Polarity' in expression
    assert 'Past_Time' in expression if intent!='directive' else 'Past_Time' not in expression

@pytest.mark.parametrize('lang',['fr','en'])
def test_composition_preserves_obligation_and_order(lang,tmp_path):
    request=compose_core_request({'language':lang,'items':[
        {'intent':'attribute','subject':'mira','concept':'ready'},
        {'intent':'transitive','subject':'noa','concept':'carry','object':'book','polarity':'negative','tense':'past'},
        {'intent':'directive','concept':'wait','polarity':'negative'}]})
    plan=candidate(tmp_path,lang).plan(request)
    assert [u.operation_id for u in plan.units]==['clause.copular_attribute','clause.transitive_event','directive.action']
    assert [u.obligation_ids for u in plan.units]==[('o1',),('o2',),('o3',)]
    assert all(x.output_slot for x in plan.units)

@pytest.mark.parametrize('invalid', [
 {'language':'fr','items':[]},
 {'language':'es','items':[{'intent':'attribute','subject':'mira','concept':'ready'}]},
 {'language':'fr','items':[{'intent':'attribute','subject':'mira','concept':'une phrase libre'}]},
 {'language':'fr','items':[{'intent':'directive','concept':'wait','subject':'mira'}]},
 {'language':'fr','items':[{'intent':'event','subject':'mira','concept':'work','object':'book'}]},
 {'language':'fr','items':[{'intent':'directive','concept':'wait','tense':'past'}]},
 {'language':'fr','items':[{'intent':'attribute','subject':'mira','concept':'ready','extra':'raw GF'}]},
 ])
def test_fail_closed_unknown_or_unadmitted_semantics(invalid):
    with pytest.raises(ValueError):compose_core_request(invalid)

def test_request_deterministic():
    recipe={'language':'fr','items':[{'intent':'location','subject':'lea','concept':'here'}]}
    assert compose_core_request(recipe)==compose_core_request(recipe)
