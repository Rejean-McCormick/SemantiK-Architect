"""Bounded Defluens development request → canonical SemantiK CommunicationRequest.

This is an inbound adapter, NOT a parallel planner or GF realization path.
Any unrecognized concept is rejected before it can reach the GF bridge.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from typing import Any

CATALOG_PATH = Path(__file__).resolve().parents[5] / 'profiles' / 'defluens-core-1' / 'catalog.json'


def catalog() -> dict:
    return json.loads(CATALOG_PATH.read_text(encoding='utf-8'))


def _bounded(value: Any, choices: list[str], name: str) -> str:
    if not isinstance(value, str) or value not in choices:
        raise ValueError(f'Unsupported {name}: choose from {", ".join(choices)}')
    return value


def compose_core_request(recipe: dict) -> dict:
    if not isinstance(recipe, dict) or set(recipe) - {'language', 'items'}:
        raise ValueError('Expected recipe with language and items only')
    c = catalog()
    lang = _bounded(recipe.get('language'), list(c['languages']), 'language')
    rows = recipe.get('items')
    if not isinstance(rows, list) or not 1 <= len(rows) <= 8:
        raise ValueError('Provide 1–8 semantic items')
    nodes, statements, obligations = [], [], []
    for idx, row in enumerate(rows, 1):
        if not isinstance(row, dict) or set(row) - {'intent','subject','concept','object','polarity','tense'}:
            raise ValueError(f'Unexpected item fields in item {idx}')
        intent = _bounded(row.get('intent'), list(c['intents']), 'intent')
        spec = c['intents'][intent]
        concept = _bounded(row.get('concept'), spec['options'], 'concept')
        polar = _bounded(row.get('polarity', 'positive'), c['polarities'], 'polarity')
        role = spec['role']
        sid = f's{idx}'
        args = []
        if spec.get('requires_subject', True):
            subject = _bounded(row.get('subject'), c['subjects'], 'subject')
            nid = f'n{idx}_subject'
            nodes.append({'id':nid,'kind':'entity_ref','external_ref':'defluens:subject-'+subject})
            args.append({'role_ref':'role:agent' if intent in ('event','transitive') else 'role:entity','value_id':nid})
        elif row.get('subject') not in (None,''):
            raise ValueError('Directives do not accept a grammatical subject in this profile')
        cid=f'n{idx}_concept'
        nodes.append({'id':cid,'kind':'concept_ref','concept_ref':f'defluens:{intent}-{concept}'})
        args.append({'role_ref':'role:'+role,'value_id':cid})
        if spec.get('requires_object'):
            obj = _bounded(row.get('object'), c['objects'], 'object')
            oid=f'n{idx}_object'
            nodes.append({'id':oid,'kind':'entity_ref','external_ref':'defluens:object-'+obj})
            args.append({'role_ref':'role:patient','value_id':oid})
        elif row.get('object') not in (None,''):
            raise ValueError('Object is only supported for transitive events')
        qualifiers=[]
        if spec.get('supports_tense',True):
            tense = _bounded(row.get('tense','present'),c['tenses'],'tense')
            tid=f'n{idx}_tense'
            nodes.append({'id':tid,'kind':'literal','value':tense})
            qualifiers.append({'qualifier_ref':'qualifier:tense','value_id':tid})
        elif row.get('tense') not in (None,'','present'):
            raise ValueError('Directive tense is not supported by this profile')
        statements.append({'id':sid,'predicate_ref':'defluens:relation-'+intent,'arguments':args,
                           'polarity':polar,'qualifiers':qualifiers})
        obligations.append({'obligation_id':f'o{idx}','semantic_refs':[sid],
                            'force':'DIRECT' if intent=='directive' else 'PRESENT','ordering':'FIXED'})
    runtime=f'defluens-core-{lang}-1'
    result={'schema_version':'1.0',
      'semantic_graph':{'graph_id':'g:defluens-core','nodes':nodes,'statements':statements},
      'obligations':obligations,'supporting_context':[],
      'context':{'target_language':lang,'target_locale': 'fr-CA' if lang=='fr' else 'en-CA',
                 'channel':'offline-build','register':'encyclopedic'},
      'constraints':{'allowed_block_kinds':['utterance'],'opening_policy':'forbidden',
                     'closing_policy':'forbidden','list_policy':'forbidden','output_format':'structured'},
      'capability_profile':runtime,'runtime_selector':{'runtime_set_id':runtime}}
    raw=json.dumps(result,sort_keys=True,ensure_ascii=False,separators=(',',':'))
    result['request_id']='sha256:'+hashlib.sha256(raw.encode('utf-8')).hexdigest()
    return result


def validate_core_batch(batch: dict) -> dict:
    """Public development CLI batch. The existing SA validators own all verdicts.

    A bounded batch is faster than many new process launches on Windows.
    It neither plans grammar nor realizes text nor approves a RuntimeSet.
    """
    import re
    from ....domain.communication.request import CommunicationRequest
    from ....application.validation.request_validation import RequestValidator
    from ....domain.errors import SemantikArchitectError

    if not isinstance(batch, dict) or set(batch) != {'vectors'}:
        raise ValueError('Expected a vectors batch only')
    vectors = batch['vectors']
    if not isinstance(vectors, list) or not 1 <= len(vectors) <= 48:
        raise ValueError('Expected 1–48 semantic vectors')
    if len(json.dumps(batch,ensure_ascii=False).encode('utf-8')) > 100_000:
        raise ValueError('Core batch exceeds 100 kB')
    results=[]; seen=set(); validator=RequestValidator()
    for vector in vectors:
        if not isinstance(vector, dict) or set(vector) != {'case_id','recipe'}:
            raise ValueError('Each vector requires case_id and recipe only')
        case_id=vector['case_id']
        if not isinstance(case_id,str) or not re.fullmatch(r'[a-z0-9][a-z0-9:_-]{0,79}',case_id) or case_id in seen:
            raise ValueError('Invalid or repeated case ID')
        seen.add(case_id)
        try:
            request=compose_core_request(vector['recipe'])
            validator.validate(CommunicationRequest.from_dict(request))
            results.append({'case_id':case_id,'ok':True,'validated':True,'request':request})
        except (ValueError, KeyError, TypeError, SemantikArchitectError) as exc:
            results.append({'case_id':case_id,'ok':False,'validated':False,'error':str(exc)[:500]})
    return {'schema_id':'semantik.defluens-core-batch', 'schema_version':'1.0',
            'candidate_only':True,'released':False,'results':results}


def preview_core_batch(batch: dict, candidate_dir: str, runtime_set_id: str) -> dict:
    """Run independent, typed requests through ONE locked CandidateConformance.

    The existing SA request validator, planner, lexical binder and GF realizer
    remain the *only* execution path.  Failures are per vector; no fixture text
    and no fallback are possible. This public CLI is development-only.
    """
    import re
    from hashlib import sha256
    from ....conformance.candidate import CandidateConformance
    from ....domain.errors import SemantikArchitectError

    if not isinstance(batch, dict) or set(batch) != {'vectors'}:
        raise ValueError('Expected {"vectors": [...]} only')
    vectors = batch['vectors']
    if not isinstance(vectors, list) or not 1 <= len(vectors) <= 48:
        raise ValueError('Expected 1–48 candidate preview vectors')
    if len(json.dumps(batch, ensure_ascii=False).encode('utf-8')) > 250_000:
        raise ValueError('Candidate preview batch exceeds 250 kB')
    ids: set[str] = set()
    for vector in vectors:
        if not isinstance(vector, dict) or set(vector) != {'case_id', 'request'}:
            raise ValueError('Each vector must have case_id and request only')
        key = vector['case_id']
        if (not isinstance(key, str) or not re.fullmatch(r'[a-z0-9][a-z0-9:_-]{0,79}', key)
                or key in ids or not isinstance(vector['request'], dict)):
            raise ValueError('Invalid/duplicate case_id or non-object canonical request')
        ids.add(key)

    root = Path(candidate_dir).resolve()
    if not (root / 'pipeline.lock.json').is_file():
        raise ValueError('WordBench pipeline.lock.json missing; no PGF candidate to preview')
    # The existing conformance constructor verifies lock identity and all
    # immutable candidate hashes. It never releases or activates an artifact.
    candidate = CandidateConformance(root, runtime_set_id)
    rows = []
    for vector in vectors:
        try:
            result = candidate.render(vector['request'])
            rows.append({'case_id': vector['case_id'], 'ok': True, 'communication_result': result})
        except (SemantikArchitectError, ValueError, KeyError, TypeError, OSError, RuntimeError) as exc:
            rows.append({'case_id': vector['case_id'], 'ok': False,
                         'error': str(exc)[:1000]})
    return {
        'schema_id': 'semantik.candidate-preview-batch', 'schema_version': '1.0',
        'status': 'CANDIDATE_PREVIEW_BATCH', 'runtime_set_id': runtime_set_id,
        'candidate_only': True, 'released': False, 'activated': False,
        'linguistically_certified': False,
        'pgf_sha256': candidate.lock['inputs']['grammar.pgf'],
        'pipeline_lock_sha256': sha256((root / 'pipeline.lock.json').read_bytes()).hexdigest(),
        'results': rows,
    }
