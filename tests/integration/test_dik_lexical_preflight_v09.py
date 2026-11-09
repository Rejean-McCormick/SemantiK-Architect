from pathlib import Path
import hashlib
import json
import pytest
from semantik_architect.conformance.dik_lexicon import inspect


def _save(path, doc):
    path.write_text(json.dumps(doc)+'\n')
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_valid_knowledge_only(tmp_path):
    lex={'schema_version':'1.1','source_kind':'wikidata','entries':[
        {'semantic_ref':'wikidata:lexeme:L101','language':'fr','lexical_ref':'L101',
        'source_kind':'wikidata','use_for':'knowledge','binding_kind':'lexeme_ref',
        'properties':{'status':'candidate_observation_only'}}]}
    h=_save(tmp_path/'semantik.knowledge.json',lex)
    templ={'source_candidate_sha256':'a'*64,'decisions':[{'source_lexeme_id':'L101','decision':'pending'}]}
    th=_save(tmp_path/'gf-mapping-review.template.json',templ)
    _save(tmp_path/'manifest.json',{'schema_id':'dik.semantik-knowledge-handoff/1.0-candidate',
        'status':'CANDIDATE_ONLY','released':False,'gf_bindings':0,'entries':1,'lexicon_sha256':h,
        'review_template_sha256':th,'source_candidate_sha256':'a'*64})
    result=inspect(tmp_path)
    assert result['valid'] and not result['runtime_usable'] and not result['released']
    (tmp_path/'semantik.knowledge.json').write_text('{}')
    with pytest.raises(ValueError,match='integrity'):
        inspect(tmp_path)


def test_release_claim_refused(tmp_path):
    _save(tmp_path/'manifest.json',{'schema_id':'dik.semantik-knowledge-handoff/1.0-candidate',
                                  'status':'CANDIDATE_ONLY','released':True,'gf_bindings':0})
    with pytest.raises(ValueError,match='qualification'):
        inspect(tmp_path)
