"""Project an EXISTING CommunicationResult into a multilingual definition candidate.

Never calls GF, a model or SemantiK itself. A supplied review reference labels
external editorial review metadata, not authenticated approval or publication.
"""
import argparse
import json
from pathlib import Path
from contract import ContractError,new_document,save

def export(result,*,slug,node_id,state_ref,surface_digest,review_ref=None):
    if result.get('schema_version')!='1.0' or not isinstance(result.get('blocks'),list):
        raise ContractError('CommunicationResult 1.0 required')
    if not result.get('coverage') or not isinstance(result.get('source_refs'),list) or not result.get('source_refs'):
        raise ContractError('Communication coverage and source references required')
    if not result.get('runtime',{}).get('runtime_set_id'):
        raise ContractError('Runtime identity missing')
    text='\n'.join(b['text'].strip() for b in result['blocks'] if b.get('kind')=='utterance' and isinstance(b.get('text'),str)).strip()
    if not text:raise ContractError('No realized utterance; never fabricate one')
    p={'provider':'semantik_architect','source_refs':result['source_refs'],
       'review_status':'reviewed' if review_ref else 'candidate',
       'runtime_set_id':result['runtime']['runtime_set_id']}
    if review_ref:p['review_ref']=review_ref
    locale=result.get('locale') or result.get('language')
    return new_document(slug,state_ref,surface_digest,locale,[{'node_id':node_id,'definition':text,'provenance':p}])

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ['result','slug','node-id','state-ref','surface-digest','out']:ap.add_argument('--'+k,required=True)
    ap.add_argument('--review-ref',help='Operator-supplied external editorial receipt; not verified here')
    a=ap.parse_args()
    data=json.loads(Path(a.result).read_text(encoding='utf-8'))
    print(save(a.out,export(data,slug=a.slug,node_id=a.node_id,state_ref=a.state_ref,
                         surface_digest=a.surface_digest,review_ref=a.review_ref)))
