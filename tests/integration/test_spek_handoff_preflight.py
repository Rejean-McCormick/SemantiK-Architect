import hashlib
import json
import sys
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from verify_spek_handoff import verify, HandoffError


def sample(tmp_path):
    req={'schema_version':'1.0','request_id':'demo-1',
        'semantic_graph':{'graph_id':'graph:demo','nodes':[{'id':'n1','kind':'literal','value':'Evidence'}],
                          'statements':[]},
        'obligations':[{'obligation_id':'o1','semantic_refs':['n1'],'force':'PRESENT',
                       'ordering':'FREE','source_refs':['assertion:1']}],
        'context':{'target_language':'fr','target_locale':'fr-CA','register':'neutral','channel':'app'},
        'constraints':{'allowed_block_kinds':['utterance'],'opening_policy':'forbidden',
                       'closing_policy':'forbidden','list_policy':'forbidden','output_format':'structured'},
        'capability_profile':'agriculture-reference-1'}
    f=tmp_path/'req.json';f.write_text(json.dumps(req))
    lock={'format':'spek.private-editorial-handoff/1.0','status':'PRIVATE_UNQUALIFIED_NOT_PUBLISHABLE',
          'language':'fr','fields':[{'request_file':f.name,'request_sha256':'sha256:'+hashlib.sha256(f.read_bytes()).hexdigest(),
          'required_force':'PRESENT','source_assertion_refs':['assertion:1'],'allowed_block_kinds':['utterance']}]}
    return f,lock


def test_private_handoff_language_contract_no_pgf_claim(tmp_path):
    f,lock=sample(tmp_path)
    result=verify(lock,tmp_path)
    assert result['request_count']==1 and result['gf_pgf_execution_verified'] is False
    lock['fields'][0]['source_assertion_refs']=['another:source']
    with pytest.raises(HandoffError):verify(lock,tmp_path)


def test_duplicate_private_request_is_refused(tmp_path):
    _,lock=sample(tmp_path)
    lock['fields'].append(dict(lock['fields'][0]))
    with pytest.raises(HandoffError,match='Duplicate request filename'):
        verify(lock,tmp_path)
