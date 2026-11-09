"""Candidate-only semantic/bridge tests. No claim that real gf.exe ran."""
import hashlib
import json
from pathlib import Path
import pytest
from semantik_architect.adapters.inbound.cli.defluens_attribute import compose_request
from semantik_architect.domain.communication.request import CommunicationRequest
from semantik_architect.application.validation.request_validation import RequestValidator
from semantik_architect.conformance.candidate import CandidateConformance
from semantik_architect.adapters.realization.gf.bridge import GfBridgeRealizer

PROFILE = Path(__file__).resolve().parents[2]/'profiles/defluens-attribute-fr-1'
FILES = ('bridge.json','lexicon.json','profile.json','conformance.suite.json')

class FakePgf:
    """Expression spy only; never emits grammatical French."""
    def __init__(self,path): self.path=path
    def linearize(self,expr,concrete):
        assert concrete=='DefluensAttributeFre'
        return '[EXPRESSION ONLY] '+expr

def candidate(tmp_path):
    for name in FILES:
        (tmp_path/name).write_bytes((PROFILE/name).read_bytes())
    (tmp_path/'grammar.pgf').write_bytes(b'STUB:NOT_A_REAL_GF_ARTIFACT')
    hashes={n:hashlib.sha256((tmp_path/n).read_bytes()).hexdigest() for n in (*FILES,'grammar.pgf')}
    (tmp_path/'pipeline.lock.json').write_text(json.dumps({'schema_version':'1.0',
        'runtime_set_id':'defluens-attribute-fr-1','language':'fr',
        'profile_id':'defluens-attribute-fr-1','concrete':'DefluensAttributeFre',
        'sa_gf_contract_version':'1.0','inputs':hashes}),encoding='utf-8')
    return CandidateConformance(tmp_path,'defluens-attribute-fr-1',
        realizer=GfBridgeRealizer(runtime_factory=FakePgf))

@pytest.mark.parametrize('subject,attribute,polarity,tense',[
    ('mira','ready','negative','present'),('lea','calm','positive','past'),
    ('noa','absent','negative','future'),('lea','available','positive','future')])
def test_real_sa_planning_and_bridge_expression(tmp_path,subject,attribute,polarity,tense):
    payload=compose_request(subject,attribute,polarity,tense)
    RequestValidator().validate(CommunicationRequest.from_dict(payload))
    app=candidate(tmp_path)
    plan=app.plan(payload)
    assert len(plan.units)==1
    assert plan.units[0].operation_id=='clause.copular_attribute'
    assert plan.units[0].feature_bindings['polarity']==polarity
    assert plan.units[0].feature_bindings['qualifier.tense']==tense
    result=app.render(payload)
    text=result['plain_text']
    assert text.startswith('[EXPRESSION ONLY] RealizeAttribute ')
    assert {'mira':'Mira_Subject','lea':'Lea_Subject','noa':'Noa_Subject'}[subject] in text
    assert {'ready':'Ready_Quality','calm':'Calm_Quality','absent':'Absent_Quality','available':'Available_Quality'}[attribute] in text
    assert ('Negative_Polarity' if polarity=='negative' else 'Positive_Polarity') in text
    assert {'present':'Present_Time','past':'Past_Time','future':'Future_Time'}[tense] in text
    assert result['coverage']

def test_unknown_concept_fails_closed(tmp_path):
    app=candidate(tmp_path)
    payload=compose_request('mira','ready','negative','present')
    payload['semantic_graph']['nodes'][1]['concept_ref']='defluens:unknown'
    with pytest.raises(Exception,match='lexical|binding|SA-LEX|No exact'):
        app.render(payload)

def test_request_mapper_rejects_unknowns():
    for values in [('evil','ready','negative','present'),('mira','ready','bad','present'),
                   ('mira','ready','negative','yesterday')]:
        with pytest.raises(ValueError):compose_request(*values)

def test_72_unique_semantic_request_identities():
    from semantik_architect.adapters.inbound.cli.defluens_attribute import SUBJECTS,ATTRIBUTES,POLARITIES,TENSES
    ids={compose_request(s,a,p,t)['request_id'] for s in SUBJECTS for a in ATTRIBUTES for p in POLARITIES for t in TENSES}
    assert len(ids)==72
