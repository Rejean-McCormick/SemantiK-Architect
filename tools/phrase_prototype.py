"""Offline five-case SemantiK phrase proof-of-concept.

Uses Architect's canonical profile-3 artifacts, not a second runtime or grammar.
Only the final GF/PGF linearizer is a deterministic test double. No publication,
RuntimeSet release, activation, source approval, or canonical mutation occurs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'examples' / 'phrase-prototype'
PROFILE = ROOT / 'profiles' / 'konstellation-explorer-3'
RUNTIME_SET = 'konstellation-fr-3'
PROFILE_ID = 'konstellation-explorer-3'
REQUIRED_NAMES = ('grammar.pgf', 'bridge.json', 'lexicon.json', 'profile.json', 'conformance.suite.json')
GRAMMAR_PLACEHOLDER = b'PROTOTYPE-NOT-A-COMPILED-PGF\n'


class FixturePgfV3:
    """Test double for the expression-level stage only (NOT real PGF)."""
    NP = {
        'Augustin_NP': 'Augustin',
        'Foi_NP': 'La foi',
        'LeonXIII_NP': 'Léon XIII',
        'JeanPaulII_NP': 'Jean-Paul II',
        'ImmaculeeConception_NP': 'L’Immaculée Conception',
        'ExistenceLibreArbitre_NP': 'l’existence du libre arbitre',
        'EnqueteIntellectuelleAnselme_NP': 'l’enquête intellectuelle d’Anselme',
        'ProprietePriveePrevoyanceFamille_NP': 'la propriété privée comme moyen de prévoyance et de protection de la famille',
        'PrioriteTravailCapital_NP': 'la priorité du travail sur le capital dans le processus de production',
        'Dogme_ClassNP': 'un dogme',
    }
    V2 = {
        'Defendre_V2': 'défend',
        'Stimuler_V2': 'stimule',
        'Affirmer_V2': 'affirme',
    }

    def __init__(self, path: Path):
        self.path = path

    def linearize(self, expression: str, concrete: str) -> str:
        if concrete != 'KonstellationFre':
            raise ValueError('Unexpected concrete GF language')
        parts = expression.split()
        if len(parts) == 4 and parts[0] == 'RealizeTransitive':
            return f'{self.NP[parts[1]]} {self.V2[parts[2]]} {self.NP[parts[3]]}.'
        if len(parts) == 3 and parts[0] == 'RealizeClassification':
            return f'{self.NP[parts[1]]} est {self.NP[parts[2]]}.'
        raise ValueError('Unexpected typed GF expression: ' + expression)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def node(node_id: str, semantic_ref: str) -> dict:
    return {'id': node_id, 'kind': 'entity_ref', 'external_ref': semantic_ref}


def request_for(seed: dict) -> dict:
    """Port of the original standalone prototype's deterministic seed projection."""
    if seed['operation'] == 'transitive_event':
        nodes = [node('n_agent', seed['agent']), node('n_patient', seed['patient'])]
        predicate = seed['predicate']
        args = [{'role_ref':'role:agent','value_id':'n_agent'}, {'role_ref':'role:patient','value_id':'n_patient'}]
    elif seed['operation'] == 'classification':
        nodes = [node('n_entity', seed['entity']), node('n_class', seed['class'])]
        predicate = 'theophile:classified-as'
        args = [{'role_ref':'role:entity','value_id':'n_entity'}, {'role_ref':'role:class','value_id':'n_class'}]
    else:
        raise ValueError('Unknown seed operation')
    canonical = json.dumps(seed, sort_keys=True, ensure_ascii=False, separators=(',',':'))
    digest = hashlib.sha256(canonical.encode('utf-8')).hexdigest()
    source = f"theophile-source:{seed['source_id']}#{seed['locator']}"
    return {
        'schema_version':'1.0',
        'request_id':f'sha256:{digest}',
        'semantic_graph': {
            'graph_id':f"g:{seed['id']}", 'nodes':nodes,
            'statements':[{'id':'s1','predicate_ref':predicate,'arguments':args,'polarity':'positive','source_refs':[source]}]
        },
        'obligations':[{'obligation_id':'o1','semantic_refs':['s1'],'force':'PRESENT','ordering':'FIXED','source_refs':[source]}],
        'supporting_context':[],
        'context':{'target_language':'fr','target_locale':'fr-CA','channel':'offline-build','register':'encyclopedic'},
        'constraints':{'allowed_block_kinds':['utterance'],'opening_policy':'forbidden','closing_policy':'forbidden','list_policy':'forbidden','output_format':'structured'},
        'capability_profile':PROFILE_ID,
        'runtime_selector':{'runtime_set_id':RUNTIME_SET},
    }


def validate_seeds(seeds: list[dict], *, profile: Path = PROFILE) -> list[tuple[str, dict]]:
    if len(seeds) != 5:
        raise ValueError('Expected precisely the original five independent seeds')
    cases: list[tuple[str, dict]] = []
    seen: set[str] = set()
    for seed in seeds:
        sid = seed.get('id')
        if not isinstance(sid,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,99}',sid):
            raise ValueError('Unsafe seed identifier')
        if sid in seen:
            raise ValueError('Duplicate seed identifier')
        seen.add(sid)
        request=request_for(seed)
        canonical=read_json(profile/'requests'/f'{sid}.json')
        if request != canonical:
            raise ValueError(f'Seed/canonical request drift for {sid}')
        cases.append((sid,request))
    if {p.stem for p in (profile/'requests').glob('*.json')} != seen:
        raise ValueError('Canonical request fixture set differs from seed set')
    return cases


def validate_artifacts(profile: Path, cases: list[tuple[str,dict]]) -> None:
    import jsonschema
    checks = {
        'profile.json':'capability_profile.schema.json',
        'bridge.json':'gf_bridge_spec.schema.json',
        'lexicon.json':'lexical_artifact.schema.json',
        'conformance.suite.json':'conformance_suite.schema.json',
    }
    for filename, schema in checks.items():
        jsonschema.Draft202012Validator(read_json(ROOT/'schemas'/schema)).validate(read_json(profile/filename))
    request_schema = read_json(ROOT/'schemas/communication_request.schema.json')
    for _, request in cases:
        jsonschema.Draft202012Validator(request_schema).validate(request)
    gf=(profile/'KonstellationFre.gf').read_text(encoding='utf-8')
    # Do not let the deprecated duplicate grammar silently replace Architect's source.
    if 'flags unlexer = text' not in gf:
        raise ValueError('Canonical profile-3 GF unlexer flag missing')


def audit_corpus(corpus_root: Path, seeds: list[dict], *, profile: Path = PROFILE) -> dict:
    """Optional read-only provenance and no-complete-sentence audit."""
    editorial=read_json(corpus_root/'edition'/'editorial.json')
    positions={p['id']:p for p in editorial['positions']}
    classifications={c['id']:c for c in editorial['classifications']}
    sources={s['id']:s for s in editorial['sources']}
    for seed in seeds:
        position=positions.get(seed.get('source_position_id'))
        if position is None or position['source']!=seed['source_id'] or position['locator']!=seed['locator'] or seed['source_id'] not in sources:
            raise ValueError('Corpus provenance mismatch for '+seed['id'])
        cid=seed.get('source_classification_id')
        if cid and (cid not in classifications or seed['source_position_id'] not in classifications[cid].get('witnesses', [])):
            raise ValueError('Corpus classification witness mismatch for '+seed['id'])
    # Do not scan expected results or the historical report: they deliberately quote outputs.
    inputs=[FIXTURE/'semantic-seeds.json',profile/'lexicon.json',*sorted((profile/'requests').glob('*.json'))]
    contents=[path.read_text(encoding='utf-8') for path in inputs]
    for position in editorial['positions']:
        sentence=position.get('text','').strip()
        if sentence and any(sentence in content for content in contents):
            raise ValueError('Complete corpus sentence leaked into semantic input: '+position['id'])
    return {'positions_audited':len(editorial['positions']),'semantic_seeds_checked':len(seeds),'input_artifacts_scanned':len(inputs)}


def prepare_candidate(destination: Path, *, profile: Path = PROFILE) -> None:
    """Create ONLY an isolated temporary candidate, never the real RuntimeSet."""
    if destination.exists() and any(destination.iterdir()):
        raise ValueError('Candidate destination must be empty')
    destination.mkdir(parents=True, exist_ok=True)
    import shutil
    for name in ('bridge.json','lexicon.json','profile.json','conformance.suite.json'):
        shutil.copyfile(profile/name,destination/name)
    (destination/'grammar.pgf').write_bytes(GRAMMAR_PLACEHOLDER)
    inputs={name:hashlib.sha256((destination/name).read_bytes()).hexdigest() for name in REQUIRED_NAMES}
    lock={'schema_version':'1.0','runtime_set_id':RUNTIME_SET,'language':'fr','profile_id':PROFILE_ID,
          'concrete':'KonstellationFre','sa_gf_contract_version':'1.0','inputs':inputs}
    (destination/'pipeline.lock.json').write_text(json.dumps(lock,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def check(*, corpus_root:Path|None=None, profile:Path=PROFILE, seeds: list[dict]|None=None) -> dict:
    """Run real Architect planning/binding/coverage with a clearly fake PGF boundary."""
    if str(ROOT/'src') not in sys.path:
        sys.path.insert(0,str(ROOT/'src'))
    from semantik_architect.conformance.candidate import CandidateConformance
    from semantik_architect.conformance.harness import ConformanceHarness
    from semantik_architect.adapters.realization.gf import GfBridgeRealizer

    seeds=seeds if seeds is not None else read_json(FIXTURE/'semantic-seeds.json')['seeds']
    cases=validate_seeds(seeds,profile=profile)
    validate_artifacts(profile,cases)
    suite=read_json(profile/'conformance.suite.json')
    by_id={case['case_id']:case for case in suite['cases']}
    if set(by_id)!={sid for sid,_ in cases} or len(suite['cases'])!=5:
        raise ValueError('Conformance cases do not match five semantic seeds')
    for sid,req in cases:
        if req!=by_id[sid]['request']:
            raise ValueError('Conformance suite drifts from canonical request: '+sid)
    extra=audit_corpus(corpus_root,seeds,profile=profile) if corpus_root else None
    with tempfile.TemporaryDirectory(prefix='semantik-phrase-fixture-') as temp:
        candidate=Path(temp)/'candidate'
        prepare_candidate(candidate,profile=profile)
        app=CandidateConformance(candidate,RUNTIME_SET,realizer=GfBridgeRealizer(runtime_factory=FixturePgfV3))
        report=ConformanceHarness(app).run(suite).to_dict()
        if not report['passed']:
            raise ValueError('Expression fixture conformance failed: '+json.dumps(report,ensure_ascii=False))
        outputs=[]
        for sid,req in cases:
            result=app.render(req)
            expected=by_id[sid]['expected']['plain_text']
            if result['plain_text']!=expected:
                raise ValueError('Expression fixture output mismatch: '+sid)
            outputs.append({'case':sid,'text':result['plain_text'],'request_id':req['request_id'],'coverage':result['coverage']})
    return {'status':'PASS','qualification':'EXPRESSION_LEVEL_FIXTURE_ONLY','case_count':len(outputs),
            'gf_compiler_executed':False,'pgf_compiled':False,'public_release_authorized':False,
            'profile_id':PROFILE_ID,'runtime_set_id':RUNTIME_SET,'cases':outputs,
            'corpus_audit':extra}


def main() -> int:
    parser=argparse.ArgumentParser(description='Check embedded 5-case SemantiK phrase prototype (offline; fake PGF)')
    parser.add_argument('--corpus-root',type=Path,help='Optional separate source corpus for provenance/leak audit')
    args=parser.parse_args()
    try:
        print(json.dumps(check(corpus_root=args.corpus_root),ensure_ascii=False,indent=2))
        return 0
    except (ValueError, KeyError, OSError) as exc:
        print('FAIL: '+str(exc),file=sys.stderr)
        return 1

if __name__=='__main__':
    raise SystemExit(main())
