"""Bounded UNESCO mt1.10 Framework-v11 semantic-handoff -> CommunicationRequest.

Explicit v11 identity preservation, not a v11 Framework validator, authoritative
crosswalk, RuntimeSet release, GF realization, or article publication. An
operator must choose a reviewed UNESCO-to-KQ selection and a target locale.
Unsupported v11 assertion shapes are rejected instead of silently rewritten.
"""
from __future__ import annotations
import hashlib,re
from typing import Any

from ...domain.communication.request import CommunicationRequest

SOURCE_FORMAT='kristal.integration.unesco-mt1-10-semantic-handoff/1.0'
LOCALES=('en','fr','es','de','nl','sv','da','no','nn','fi','et','af','it','pt')
KQ=re.compile(r'^KQ[0-9]+$');KP=re.compile(r'^KP[0-9]+$');KA=re.compile(r'^KA[0-9]+$');KS=re.compile(r'^KS[0-9]+$')

class UNESCOProjectionError(ValueError):pass


def build_request(data:dict,*,unesco_id:str,capability_profile='defluens-core-1')->CommunicationRequest:
    if (data.get('profile')!=SOURCE_FORMAT or data.get('branch')!='unesco-mt1-10' or
        data.get('semantic_grain')!='one_branch_kristal'):
        raise UNESCOProjectionError('Wrong UNESCO v11 semantic handoff')
    if (data.get('publication_authorized') is not False or
        data.get('authoritative_authoring_checked') is not False or
        data.get('qualified_language_runtime') is not False):
        raise UNESCOProjectionError('Untrusted authorization or runtime qualification claim')
    locale=data.get('locale')
    if locale not in LOCALES:raise UNESCOProjectionError('Unsupported/missing target locale')
    ns=data.get('namespace_id')
    if not isinstance(ns,str) or not ns.strip():raise UNESCOProjectionError('Missing source namespace')
    scope=hashlib.sha256(ns.encode('utf8')).hexdigest()[:24]
    prefix='kristal-v11:'+scope+'/'
    row=next((x for x in data.get('selections',[]) if x.get('unesco_id')==unesco_id),None)
    if row is None:raise UNESCOProjectionError('Selected UNESCO concept not present')
    if not KQ.fullmatch(str(row.get('local_kq'))):raise UNESCOProjectionError('Invalid selected KQ')
    if not isinstance(row.get('decision_ref'),str) or not row['decision_ref'].strip():
        raise UNESCOProjectionError('KQ selection must have reviewed decision reference')
    assertions=row.get('assertions')
    if not isinstance(assertions,list) or not assertions:
        raise UNESCOProjectionError('Cannot realize a concept without selected source-backed KAs')
    entries={};statements=[];obligations=[];support=[]
    def node(kid):
        if not KQ.fullmatch(str(kid)):raise UNESCOProjectionError('Assertion referent is not a v11 KQ')
        if kid not in entries:
            d={'id':'n_'+kid,'kind':'entity_ref','external_ref':prefix+kid}
            if kid==row['local_kq'] and isinstance(row.get('lexical'),dict):
                v=row['lexical']
                if (v.get('status') in ('direct','fallback') and
                    isinstance(v.get('term'),str) and v['term'].strip()):
                    d['labels']={locale:v['term']}
            entries[kid]=d
        return entries[kid]['id']
    seen=set()
    for a in assertions:
        aid=a.get('id');sub=a.get('subject');pred=a.get('predicate');obj=a.get('object')
        if not KA.fullmatch(str(aid)) or aid in seen:raise UNESCOProjectionError('Duplicate/invalid KA')
        seen.add(aid)
        if sub!=row['local_kq'] or not KP.fullmatch(str(pred)):
            raise UNESCOProjectionError('Assertion source/predicate does not match KQ/KP')
        if not isinstance(obj,dict) or obj.get('kind') not in ('entity','literal'):
            raise UNESCOProjectionError('Unrepresentable v11 KA object')
        subj_id=node(sub)
        if obj['kind']=='entity':
            object_id=node(obj.get('id'))
        else:
            if 'value' not in obj or not isinstance(obj['value'],(str,int,float,bool)):
                raise UNESCOProjectionError('Unsupported literal value')
            object_id='v_'+aid
            if object_id in entries:raise UNESCOProjectionError('Duplicate literal ID')
            entries[object_id]={'id':object_id,'kind':'literal','value':obj['value']}
        source_ids=a.get('sources')
        if not isinstance(source_ids,list) or not source_ids or any(not KS.fullmatch(str(k)) for k in source_ids):
            raise UNESCOProjectionError('KA sources must retain KS identities')
        stmt='s_'+aid
        refs=[prefix+k for k in source_ids]
        statements.append({'id':stmt,'predicate_ref':prefix+pred,
                           'arguments':[{'role_ref':'semantic-role:subject','value_id':subj_id},
                                        {'role_ref':'semantic-role:object','value_id':object_id}],
                           'polarity':'positive','source_refs':refs})
        obligations.append({'obligation_id':'o_'+aid,'semantic_refs':[stmt],
                            'force':'PRESENT','ordering':'FREE','source_refs':refs})
        support.append({'subject_id':stmt,'property_ref':'kristal-v11:canonical-assertion-id',
                        'value':{'namespace_id':ns,'ka_id':aid,'ks_ids':source_ids}})
    support.append({'subject_id':'n_'+row['local_kq'],'property_ref':'kristal-v11:unesco-selection',
                    'value':{'unesco_id':unesco_id,'decision_ref':row['decision_ref'],
                             'origin_view_sha256':data.get('view_sha256')}})
    request={'schema_version':'1.0','request_id':'unesco-mt1-10:'+unesco_id+':'+locale,
             'semantic_graph':{'graph_id':'unesco_mt1_10_'+unesco_id+'_'+locale,
                               'nodes':list(entries.values()),'statements':statements},
             'obligations':obligations,'supporting_context':support,
             'context':{'target_language':locale,'target_locale':locale,
                        'register':'encyclopedic','channel':'draft'},
             'constraints':{'allowed_block_kinds':['utterance','list','notice','heading'],
                            'opening_policy':'allowed','closing_policy':'allowed',
                            'list_policy':'allowed','output_format':'structured'},
             'capability_profile':capability_profile}
    # Uses the REAL SemantiK request domain model for a parse/shape check.
    return CommunicationRequest.from_dict(request)
