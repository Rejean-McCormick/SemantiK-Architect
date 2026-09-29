import hashlib
import json
import shutil
from pathlib import Path

from semantik_architect.adapters.realization.gf import GfBridgeRealizer
from semantik_architect.conformance.candidate import CandidateConformance
from semantik_architect.conformance.matrix import CandidateMatrixConformance

PROFILE = Path('profiles/konstellation-explorer-1')


class FixturePgf:
    def __init__(self, path):
        self.path = path

    def linearize(self, expression, concrete):
        assert concrete == 'KonstellationFre'
        assert expression.startswith('Present ')
        decoder = json.JSONDecoder()
        label, end = decoder.raw_decode(expression[8:])
        value, _ = decoder.raw_decode(expression[8 + end:].lstrip())
        return label + ' : ' + value


def _candidate_root(tmp_path: Path) -> Path:
    root = tmp_path / 'konstellation-fr-1'
    root.mkdir()
    for name in ('bridge.json', 'lexicon.json', 'profile.json', 'conformance.suite.json'):
        shutil.copy2(PROFILE / name, root / name)
    (root / 'grammar.pgf').write_bytes(b'contract-fixture-only')
    inputs = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in root.iterdir()
    }
    (root / 'pipeline.lock.json').write_text(json.dumps({
        'schema_version': '1.0',
        'runtime_set_id': root.name,
        'language': 'fr',
        'profile_id': 'konstellation-explorer-1',
        'concrete': 'KonstellationFre',
        'sa_gf_contract_version': '1.0',
        'inputs': inputs,
    }), encoding='utf-8')
    return root


def test_candidate_matrix_runs_candidate_suite_without_releasing(tmp_path):
    root = _candidate_root(tmp_path)

    def factory(candidate_root, runtime_set_id):
        return CandidateConformance(
            candidate_root,
            runtime_set_id,
            realizer=GfBridgeRealizer(runtime_factory=FixturePgf),
        )

    report = CandidateMatrixConformance(factory).run([{
        'candidate_root': root,
        'runtime_set_id': root.name,
        'metadata': {'source': 'test-matrix'},
    }])
    payload = report.to_dict()
    assert report.passed
    assert payload['status'] == 'PASS'
    assert payload['released'] is False
    assert payload['activated'] is False
    language = payload['languages'][0]
    assert language['language'] == 'fr'
    assert language['passed_cases'] == language['total_cases']
    assert all(case['operation_ids'] for case in language['cases'])
    assert language['metadata']['source'] == 'test-matrix'
