import hashlib
import json
import shutil
from pathlib import Path
import pytest
from semantik_architect.conformance.candidate import CandidateConformance
from semantik_architect.conformance.harness import ConformanceHarness
from semantik_architect.adapters.realization.gf import GfBridgeRealizer
from semantik_architect.adapters.inbound.cli.main import main
from semantik_architect.domain.errors import SemantikArchitectError
PROFILE=Path('profiles/konstellation-explorer-1')
class FixturePgf:
    """Contract fixture, never a compiled grammar or publication proof."""
    def __init__(self,path): pass
    def linearize(self,expression,concrete):
        assert concrete=='KonstellationFre'
        assert expression.startswith('Present ')
        decoder=json.JSONDecoder(); label,end=decoder.raw_decode(expression[8:])
        value,_=decoder.raw_decode(expression[8+end:].lstrip())
        return label+' : '+value

def candidate(tmp_path):
    root=tmp_path/'konstellation-fr-1';root.mkdir()
    for name in ('bridge.json','lexicon.json','profile.json','conformance.suite.json'): shutil.copy2(PROFILE/name,root/name)
    (root/'grammar.pgf').write_bytes(b'contract-fixture-only')
    lock={'schema_version':'1.0','runtime_set_id':root.name,'language':'fr','profile_id':'konstellation-explorer-1','concrete':'KonstellationFre','sa_gf_contract_version':'1.0','inputs':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in root.iterdir()}}
    (root/'pipeline.lock.json').write_text(json.dumps(lock))
    return CandidateConformance(root,root.name,realizer=GfBridgeRealizer(runtime_factory=FixturePgf))

def test_konstellation_contract_pipeline_preserves_all_statement_arguments(tmp_path):
    app=candidate(tmp_path);suite=json.loads((PROFILE/'conformance.suite.json').read_text())
    report=ConformanceHarness(app).run(suite)
    assert report.passed, report.to_dict()
    request=suite['cases'][2]['request'];result=app.render(request)
    for statement in request['semantic_graph']['statements']:
        assert statement['predicate_ref'] in result['plain_text']
        for argument in statement['arguments']: assert argument['role_ref'] in result['plain_text']
    assert not (app.root/'runtime.manifest.json').exists()
    assert not (app.root/'activation.json').exists()
    assert app.runtime.status=='CANDIDATE'

def test_unknown_explorer_predicate_and_cycles_are_rejected(tmp_path):
    app=candidate(tmp_path);request=json.loads((PROFILE/'requests/query.json').read_text())
    request['semantic_graph']['statements'][0]['predicate_ref']='konstellation:invented'
    with pytest.raises(SemantikArchitectError): app.render(request)
    request=json.loads((PROFILE/'requests/page.json').read_text())
    collection=next(n for n in request['semantic_graph']['nodes'] if n['kind']=='collection')
    collection['members']=[collection['id']]
    with pytest.raises((SemantikArchitectError,ValueError)): app.render(request)

def test_candidate_hashes_and_identity_are_mandatory(tmp_path):
    app=candidate(tmp_path);(app.root/'lexicon.json').write_text('{}')
    with pytest.raises(ValueError,match='integrity'): app.verify()
    with pytest.raises(ValueError,match='identity'): CandidateConformance(app.root,'other')

def test_conformance_never_passes_empty_suite():
    report=ConformanceHarness(None).run({'suite_id':'empty','language':'fr','capability_profile':'konstellation-explorer-1','runtime_set_id':'empty','cases':[]})
    assert not report.passed

def test_cli_invalid_runtime_returns_failure(tmp_path,capsys):
    assert main(['--runtime-root',str(tmp_path),'validate-runtime','missing'])==1

def test_candidate_cli_writes_failure_evidence_without_publishing(tmp_path,capsys):
    app=candidate(tmp_path);output=tmp_path/'evidence.json'
    # Fake PGF bytes must never qualify through the production GF adapter.
    rc=main(['--runtime-root',str(tmp_path),'conformance','--suite',str(app.root/'conformance.suite.json'),'--runtime-set-id',app.root.name,'--candidate-dir',str(app.root),'--output',str(output)])
    assert rc==1
    evidence=json.loads(output.read_text())
    assert evidence['passed'] is False
    assert evidence['profile_id']=='konstellation-explorer-1'
    assert not (app.root/'runtime.manifest.json').exists()

def test_explorer_does_not_drop_discourse_constraints(tmp_path):
    app=candidate(tmp_path);request=json.loads((PROFILE/'requests/query.json').read_text())
    request['context']['tone_profile']='persuasive'
    with pytest.raises(SemantikArchitectError): app.render(request)


def test_candidate_plan_is_available_for_review_without_realization(tmp_path):
    app=candidate(tmp_path); suite=json.loads((PROFILE/'conformance.suite.json').read_text())
    plan=app.plan(suite['cases'][0]['request'])
    assert plan.language=='fr'
    assert plan.units
    assert all(unit.operation_id for unit in plan.units)
