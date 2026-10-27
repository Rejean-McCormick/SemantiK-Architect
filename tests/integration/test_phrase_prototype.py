"""Integrated checks for the former standalone SemantiK-only phrase prototype."""
import copy
import json
from pathlib import Path

import pytest

from tools import phrase_prototype as pp


def seeds():
    return json.loads((pp.FIXTURE / 'semantic-seeds.json').read_text(encoding='utf-8'))['seeds']


def test_five_cases_through_real_architect_with_fake_pgf():
    result=pp.check()
    assert result['status']=='PASS'
    assert result['case_count']==5
    assert result['gf_compiler_executed'] is False
    assert result['pgf_compiled'] is False
    assert result['public_release_authorized'] is False
    assert {x['case'] for x in result['cases']}=={x['id'] for x in seeds()}
    assert all(x['coverage'][0]['obligation_id']=='o1' for x in result['cases'])


def test_canonical_profile_is_the_single_source():
    assert (pp.PROFILE/'KonstellationFre.gf').is_file()
    assert 'flags unlexer = text' in (pp.PROFILE/'KonstellationFre.gf').read_text(encoding='utf-8')
    assert not (pp.FIXTURE/'profile').exists()
    assert not (pp.FIXTURE/'candidate').exists()
    assert not (pp.FIXTURE/'runtime').exists()


def test_seed_projection_matches_all_five_canonical_requests():
    assert len(pp.validate_seeds(seeds()))==5


def test_reject_seed_tampering_and_duplicate_ids():
    changed=copy.deepcopy(seeds())
    changed[0]['agent']='theophile:unknown'
    with pytest.raises(ValueError,match='drift'):
        pp.validate_seeds(changed)
    changed=copy.deepcopy(seeds())
    changed[1]['id']=changed[0]['id']
    with pytest.raises(ValueError,match='Duplicate'):
        pp.validate_seeds(changed)
    changed=copy.deepcopy(seeds())
    changed[0]['id']='../../etc/passwd'
    with pytest.raises(ValueError,match='Unsafe'):
        pp.validate_seeds(changed)


def test_candidates_are_temporary_and_never_overwrite(tmp_path):
    candidate=tmp_path/'candidate'
    pp.prepare_candidate(candidate)
    assert (candidate/'grammar.pgf').read_bytes()==pp.GRAMMAR_PLACEHOLDER
    (candidate/'grammar.pgf').write_bytes(b'REAL-PGF-DO-NOT-OVERWRITE')
    with pytest.raises(ValueError,match='empty'):
        pp.prepare_candidate(candidate)
    assert (candidate/'grammar.pgf').read_bytes()==b'REAL-PGF-DO-NOT-OVERWRITE'


def test_integrity_tamper_detected_by_real_candidate_verifier(tmp_path):
    from semantik_architect.conformance.candidate import CandidateConformance
    from semantik_architect.adapters.realization.gf import GfBridgeRealizer
    candidate=tmp_path/'candidate'
    pp.prepare_candidate(candidate)
    (candidate/'lexicon.json').write_text('{}',encoding='utf-8')
    with pytest.raises(ValueError,match='integrity'):
        CandidateConformance(candidate,pp.RUNTIME_SET,realizer=GfBridgeRealizer(runtime_factory=pp.FixturePgfV3))


def test_corpus_audits_provenance_and_leak(tmp_path):
    allseeds=seeds()
    corpus=tmp_path/'corpus'/'edition'
    corpus.mkdir(parents=True)
    positions=[{'id':s['source_position_id'],'source':s['source_id'],'locator':s['locator'],'text':'Un extrait de référence différent.'} for s in allseeds]
    data={'positions':positions,'classifications':[{'id':'K003','witnesses':['D005']}],
          'sources':[{'id':s['source_id']} for s in allseeds]}
    (corpus/'editorial.json').write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
    audit=pp.audit_corpus(corpus.parent,allseeds)
    assert audit['semantic_seeds_checked']==5
    assert audit['positions_audited']==5
    data['positions'][0]['locator']='FAKE'
    (corpus/'editorial.json').write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
    with pytest.raises(ValueError,match='provenance'):
        pp.audit_corpus(corpus.parent,allseeds)
    # Only tests expected refusal if complete source sentence leaks into input.
    data['positions'][0]['locator']=allseeds[0]['locator']
    data['positions'][0]['text']='theophile:augustin'
    (corpus/'editorial.json').write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
    with pytest.raises(ValueError,match='leaked'):
        pp.audit_corpus(corpus.parent,allseeds)


def test_prototype_keeps_four_ai_assisted_seed_warnings():
    origins=[s['semantic_origin'] for s in seeds()]
    assert origins.count('prototype_manual_decomposition_from_existing_ai_assisted_position')==4
    assert origins.count('structured_classification_plus_witness')==1
