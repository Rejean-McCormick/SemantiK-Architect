"""Typed-input request mapper for the Defluens French candidate profile.

Converts user-chosen enumerated concepts to the canonical SemantiK
CommunicationRequest. It does NOT plan grammar, render strings or release PGF.
Unlisted concepts fail closed rather than accepting arbitrary GF expressions.
"""
from __future__ import annotations
import hashlib
import json

SUBJECTS = ('mira', 'lea', 'noa')
ATTRIBUTES = ('ready', 'calm', 'absent', 'available')
POLARITIES = ('positive', 'negative')
TENSES = ('present', 'past', 'future')
PROFILE = 'defluens-attribute-fr-1'
RUNTIME_ID = 'defluens-attribute-fr-1'


def compose_request(subject: str, attribute: str, polarity: str, tense: str) -> dict:
    choices = {'subject': (subject, SUBJECTS), 'attribute': (attribute, ATTRIBUTES),
               'polarity': (polarity, POLARITIES), 'tense': (tense, TENSES)}
    for name, (value, permitted) in choices.items():
        if not isinstance(value, str) or value not in permitted:
            raise ValueError(f'Unsupported {name}: choose from {", ".join(permitted)}')
    result = {
        'schema_version':'1.0',
        'semantic_graph':{
            'graph_id':'g:defluens-attribute',
            'nodes':[
                {'id':'n_entity','kind':'entity_ref','external_ref':'defluens:'+subject},
                {'id':'n_attribute','kind':'concept_ref','concept_ref':'defluens:'+attribute},
                {'id':'n_tense','kind':'literal','value':tense},
            ],
            'statements':[{
                'id':'s1','predicate_ref':'defluens:copular-attribute',
                'arguments':[{'role_ref':'role:entity','value_id':'n_entity'},
                             {'role_ref':'role:attribute','value_id':'n_attribute'}],
                'polarity':polarity,
                'qualifiers':[{'qualifier_ref':'qualifier:tense','value_id':'n_tense'}],
            }],
        },
        'obligations':[{'obligation_id':'o1','semantic_refs':['s1'],
                        'force':'PRESENT','ordering':'FIXED'}],
        'supporting_context':[],
        'context':{'target_language':'fr','target_locale':'fr-CA',
                   'channel':'offline-build','register':'encyclopedic'},
        'constraints':{'allowed_block_kinds':['utterance'],'opening_policy':'forbidden',
                       'closing_policy':'forbidden','list_policy':'forbidden',
                       'output_format':'structured'},
        'capability_profile':PROFILE,
        'runtime_selector':{'runtime_set_id':RUNTIME_ID},
    }
    normalized = json.dumps(result,ensure_ascii=False,sort_keys=True,separators=(',',':'))
    result['request_id'] = 'sha256:'+hashlib.sha256(normalized.encode('utf-8')).hexdigest()
    return result
