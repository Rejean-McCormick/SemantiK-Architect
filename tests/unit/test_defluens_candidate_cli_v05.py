"""CLI contract for candidate preview. No fake PGF is shipped to users."""
import json
from types import SimpleNamespace
import sys
import importlib
command=importlib.import_module("semantik_architect.adapters.inbound.cli.main")


def test_preview_candidate_delegates_to_existing_pipeline(monkeypatch,capsys,tmp_path):
    import semantik_architect.conformance.candidate as target
    class FakeCandidate:
        def __init__(self, root, runtime_set_id):
            assert root==str(tmp_path)
            assert runtime_set_id=='konstellation-fr-3'
        def render(self, request):
            assert request=={'context':{'target_language':'fr'}}
            return {'plain_text':'from-candidate-test-double','coverage':{'complete':True}}
    (tmp_path/'pipeline.lock.json').write_text('{}')
    monkeypatch.setattr(target,'CandidateConformance',FakeCandidate)
    monkeypatch.setattr(command,'_load',lambda path:{'context':{'target_language':'fr'}})
    assert command.main(['preview-candidate','--candidate-dir',str(tmp_path),
                         '--runtime-set-id','konstellation-fr-3','-'])==0
    result=json.loads(capsys.readouterr().out)
    assert result['status']=='CANDIDATE_PREVIEW'
    assert result['released'] is False and result['activated'] is False
    assert result['communication_result']['plain_text']=='from-candidate-test-double'
