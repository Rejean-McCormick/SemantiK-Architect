import hashlib
import json
import shutil
from pathlib import Path
import pytest
from semantik_architect.conformance.candidate import CandidateConformance
from semantik_architect.conformance.harness import ConformanceHarness
from semantik_architect.adapters.realization.gf import GfBridgeRealizer
from semantik_architect.domain.errors import SemantikArchitectError

PROFILE=Path('profiles/konstellation-explorer-2')

class FixturePgfV2:
    """Expression-level contract fixture; production compilation is verified separately."""
    def __init__(self,path): pass
    def linearize(self,expression,concrete):
        assert concrete=='KonstellationFre'
        name, _, rest=expression.partition(' ')
        values=[]; decoder=json.JSONDecoder(); text=rest.lstrip()
        while text:
            value,end=decoder.raw_decode(text); values.append(value); text=text[end:].lstrip()
        if name=='PresentClassification': return f'{values[0]} : {values[1]}'
        if name=='PresentReadContext': return f'{values[0]} — données : {values[1]} ; politique : {values[2]}'
        if name=='PresentResultPage': return f'{values[0]} : {values[1]} — total : {values[2]} ; cette page : {values[3]} ; suite : {values[4]}'
        if name=='PresentReportedAssertion': return f'{values[0]} — {values[1]} : {values[2]}'
        if name in {'PresentAttribute','PresentEntity','PresentFilterUnary','PresentSelectionIdentities'}: return f'{values[0]} : {values[1]}'
        if name in {'PresentFilterValues','PresentSelectionLink'}: return f'{values[0]} — {values[1]} : {values[2]}'
        if name=='PresentFilterOverlap': return f'{values[0]} — {values[1]} : {values[2]} ; correspondance : {values[3]}'
        raise AssertionError(name)

def candidate(tmp_path):
    root=tmp_path/'konstellation-fr-2';root.mkdir()
    for name in ('bridge.json','lexicon.json','profile.json','conformance.suite.json'): shutil.copy2(PROFILE/name,root/name)
    (root/'grammar.pgf').write_bytes(b'contract-fixture-v2')
    lock={'schema_version':'1.0','runtime_set_id':root.name,'language':'fr','profile_id':'konstellation-explorer-2','concrete':'KonstellationFre','sa_gf_contract_version':'1.0','inputs':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in root.iterdir()}}
    (root/'pipeline.lock.json').write_text(json.dumps(lock))
    return CandidateConformance(root,root.name,realizer=GfBridgeRealizer(runtime_factory=FixturePgfV2))

def test_profile2_uses_structured_sa_operations_and_not_statement_json(tmp_path):
    app=candidate(tmp_path); suite=json.loads((PROFILE/'conformance.suite.json').read_text())
    report=ConformanceHarness(app).run(suite)
    assert report.passed, report.to_dict()
    request=suite['cases'][2]['request']; result=app.render(request)
    text=result['plain_text']
    assert 'predicate_ref' not in text and 'role_ref' not in text and 'statement_id' not in text
    assert 'Augustin' in text or 'Assertion rapportée' in text
    assert 'Certitude' in text
    assert {c['obligation_id'] for c in result['coverage']}=={o['obligation_id'] for o in request['obligations']}

def test_profile2_keeps_explorer_fail_closed_contract(tmp_path):
    app=candidate(tmp_path); request=json.loads((PROFILE/'requests/query.json').read_text())
    request['semantic_graph']['statements'][0]['predicate_ref']='konstellation:invented'
    with pytest.raises(SemantikArchitectError): app.render(request)
