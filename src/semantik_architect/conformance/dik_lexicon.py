"""Fail-closed read-only inspection of diK / WordBench lexical candidate bundles.

SA consumes lexical artifacts only when they are pinned in an admitted RuntimeSet.
This module performs development preflight; it cannot build, release or activate.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any

DIK = 'dik.semantik-knowledge-handoff/1.0-candidate'
WB = 'gf-wordbench.dik-semantik-lexicon/1.0-candidate'
LID = re.compile(r'L[1-9][0-9]*\Z')
GF = re.compile(r'[A-Za-z][A-Za-z_0-9]*\Z')
CAT = {'NP','AP','CN','N','N2','A','V','V2','V3','VV','VS','VA','Adv','Prep','Det','Numeral','PN'}


def _read(path: Path) -> dict:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 100 * 1024 * 1024:
        raise ValueError('Missing, symlinked or oversized lexical candidate file')
    result = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(result,dict):
        raise ValueError('Expected lexical object')
    return result


def _hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for part in iter(lambda:f.read(1024*1024),b''):
            h.update(part)
    return h.hexdigest()


def inspect(bundle: Path) -> dict[str,Any]:
    bundle = Path(bundle)
    if bundle.is_symlink():
        raise ValueError('Symlink directory not admitted')
    manifest = _read(bundle/'manifest.json')
    kind = manifest.get('schema_id')
    if kind == DIK:
        name,key = 'semantik.knowledge.json','lexicon_sha256'
        if (manifest.get('status') != 'CANDIDATE_ONLY' or manifest.get('released') is not False
                or manifest.get('gf_bindings') != 0):
            raise ValueError('diK handoff qualification invalid')
        template=bundle/'gf-mapping-review.template.json'
        if _hash(template) != manifest.get('review_template_sha256'):
            raise ValueError('diK review template integrity mismatch')
        t=_read(template)
        if t.get('source_candidate_sha256') != manifest.get('source_candidate_sha256'):
            raise ValueError('diK review source mismatch')
    elif kind == WB:
        name,key = 'lexicon.candidate.json','lexicon_sha256'
        if (manifest.get('status') != 'DEVELOPMENT_CANDIDATE' or manifest.get('released') is not False
                or manifest.get('activated') is not False or manifest.get('gf_verified') is not False):
            raise ValueError('WordBench candidate qualification invalid')
    else:
        raise ValueError('Unsupported diK/WordBench lexical candidate schema')
    path = bundle/name
    doc = _read(path)
    if _hash(path) != manifest.get(key):
        raise ValueError('Lexical artifact integrity mismatch')
    if doc.get('schema_version') != '1.1' or doc.get('source_kind') != 'wikidata':
        raise ValueError('Not SemantiK lexical schema 1.1 knowledge-source artifact')
    entries = doc.get('entries')
    if not isinstance(entries,list):
        raise ValueError('Invalid lexical entries')
    seen=set()
    knowledge=binding=0
    for row in entries:
        if not isinstance(row,dict):
            raise ValueError('Invalid lexical entry')
        semantic, lang = row.get('semantic_ref'), row.get('language')
        if not isinstance(semantic,str) or not semantic or not isinstance(lang,str) or not lang:
            raise ValueError('Missing semantic identity or language')
        lid = semantic.removeprefix('wikidata:lexeme:')
        key_id=(semantic,lang,row.get('use_for'))
        if key_id in seen:
            raise ValueError('Duplicate binding or knowledge identity')
        seen.add(key_id)
        if row.get('source_kind')=='wikidata' and row.get('use_for')=='knowledge' and row.get('binding_kind')=='lexeme_ref':
            if not LID.fullmatch(lid) or row.get('lexical_ref')!=lid or row.get('properties',{}).get('status')!='candidate_observation_only':
                raise ValueError('Knowledge lexical entry altered')
            knowledge+=1
        elif kind==WB and row.get('source_kind')=='project' and row.get('use_for')=='binding' and row.get('binding_kind')=='gf_expr':
            function = row.get('lexical_ref')
            if (not isinstance(function,str) or not GF.fullmatch(function)
                    or row.get('category') not in CAT or row.get('properties',{}).get('gf_artifact_verified') is not False
                    or not LID.fullmatch(str(row.get('properties',{}).get('source_lexeme_id','')))
                    or not row.get('properties',{}).get('semantic_authority_ref')):
                raise ValueError('WordBench review binding is not an unverified candidate')
            binding+=1
        else:
            raise ValueError('Unexpected lexical entry authority or purpose')
    if knowledge != manifest.get('entries' if kind==DIK else 'knowledge_entries'):
        raise ValueError('Knowledge count mismatch')
    if kind==WB and binding != manifest.get('human_reviewed_binding_candidates'):
        raise ValueError('Binding count mismatch')
    if kind==DIK and len(_read(bundle/'gf-mapping-review.template.json').get('decisions',[]))!=knowledge:
        raise ValueError('Review template count mismatch')
    return {'valid':True,'status':'DEVELOPMENT_CANDIDATE_ONLY','schema_id':'semantik.dik-lexical-inspection/1.0',
            'source_schema_id':kind, 'knowledge_entries':knowledge, 'binding_candidates':binding,
            'lexical_artifact_sha256':manifest['lexicon_sha256'],
            'runtime_usable':False,'gf_verified':False,'released':False,
            'notice':'Inspection is NOT lexeme sense approval, grammar conformance, RuntimeSet publication or permission to render.'}
