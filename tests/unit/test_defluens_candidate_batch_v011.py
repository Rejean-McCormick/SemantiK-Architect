"""Bounded candidate batch: same locked SemantiK/GF pipeline, never fake success."""
from __future__ import annotations
import json
from types import SimpleNamespace
import pytest

from semantik_architect.adapters.inbound.cli.defluens_core import preview_core_batch


def test_batch_invokes_one_candidate_and_keeps_independent_errors(tmp_path, monkeypatch):
    from semantik_architect.conformance import candidate as target
    observed = []
    class CandidateDouble:
        def __init__(self, root, runtime):
            observed.append(('constructed', runtime))
            self.lock = {'inputs':{'grammar.pgf':'a'*64}}
        def render(self, request):
            observed.append(('render', request['id']))
            if request['id'] == 'bad':
                raise ValueError('Refused by real SA validator (test double)')
            return {'plain_text':'TEST DOUBLE ONLY', 'coverage':[]}
    monkeypatch.setattr(target,'CandidateConformance',CandidateDouble)
    (tmp_path/'pipeline.lock.json').write_text('{"test":true}',encoding='utf-8')
    vectors = [{'case_id':'fr:a', 'request':{'id':'ok'}},
               {'case_id':'fr:b', 'request':{'id':'bad'}}]
    out = preview_core_batch({'vectors':vectors}, str(tmp_path),'defluens-core-fr-1')
    assert observed == [('constructed','defluens-core-fr-1'),('render','ok'),('render','bad')]
    assert out['status']=='CANDIDATE_PREVIEW_BATCH'
    assert [x['ok'] for x in out['results']] == [True,False]
    assert out['released'] is False and out['activated'] is False
    assert not out['linguistically_certified']
    assert out['pgf_sha256']=='a'*64


@pytest.mark.parametrize('vectors', [[],
    [{'case_id':'duplicate', 'request':{}},{'case_id':'duplicate','request':{}}],
    [{'case_id':'bad space','request':{}}],
    [{'case_id':'fr:a','request':'not a request'}]])
def test_bad_vectors_refused_before_loading_candidate(vectors, tmp_path):
    with pytest.raises(ValueError):
        preview_core_batch({'vectors':vectors},str(tmp_path),'defluens-core-fr-1')


def test_missing_lock_cannot_fall_back_to_mock(tmp_path):
    with pytest.raises(ValueError,match='pipeline.lock'):
        preview_core_batch({'vectors':[{'case_id':'fr:a','request':{}}]},
                           str(tmp_path),'defluens-core-fr-1')
