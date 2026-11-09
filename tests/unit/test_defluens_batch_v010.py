"""SA public CLI batch is only a bounded adapter around canonical validation."""
import pytest
from semantik_architect.adapters.inbound.cli.defluens_core import validate_core_batch


def _good():
    return {'language':'fr','items':[{'intent':'attribute','subject':'mira','concept':'ready'}]}


def test_valid_and_refused_vectors_in_one_canonical_batch():
    outcome=validate_core_batch({'vectors':[
        {'case_id':'fr:attribute:positive','recipe':_good()},
        {'case_id':'fr:reject:unknown','recipe':{'language':'fr','items':[{'intent':'invented'}]}},
    ]})
    assert outcome['candidate_only'] and outcome['released'] is False
    good,bad=outcome['results']
    assert good['ok'] and good['validated']
    assert good['request']['capability_profile']=='defluens-core-fr-1'
    assert not bad['ok'] and not bad['validated'] and 'error' in bad


@pytest.mark.parametrize('bad',[{'vectors':[]}, {'vectors':'not a list'},
    {'vectors':[{'case_id':'x','recipe':_good()},{'case_id':'x','recipe':_good()}]},
    {'vectors':[{'case_id':'a wrong id','recipe':_good()}]},
    {'vectors':[{'case_id':'valid','recipe':_good(),'raw_gf':'Tree'}]},
    {'vectors':[{'case_id':str(i),'recipe':_good()} for i in range(49)]}])
def test_batch_fail_closed(bad):
    with pytest.raises(ValueError):validate_core_batch(bad)
