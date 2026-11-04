import importlib.util
from pathlib import Path
import pytest

TOOL=Path(__file__).resolve().parents[1]/'tools'/'inspect_defluens_handoff.py'
spec=importlib.util.spec_from_file_location('handoff_tool',TOOL)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def handoff():
    return {'schema_id':'defluens.wordbench-sa-development-handoff','schema_version':'1.0',
        'sa_conformance_passed':False,'release_ready':False,'publication_authorized':False,
        'rows':[{'language':'Fre','scenario_id':s,'sa_operation_candidate':'clause.locative' if s=='location' else None,
                 'mapping_status':'operation_candidate' if s=='location' else 'contract_extension_required',
                 'gf_status':'candidate_for_review'} for s in mod.EXPECTED]}

def test_declared_operations_not_the_same_as_release():
    result=mod.inspect_handoff(handoff())
    assert result['status']=='DEVELOPMENT_ONLY'
    assert result['runtime_released'] is False
    assert result['contract_gap_count']==14

def test_rejects_fake_release_and_unknown_operations():
    h=handoff();h['publication_authorized']=True
    with pytest.raises(ValueError):mod.inspect_handoff(h)
    h=handoff();h['rows'][0]['sa_operation_candidate']='clause.imaginary'
    assert any(x['issue']=='unknown_sa_operation' for x in mod.inspect_handoff(h)['issues'])
