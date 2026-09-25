import hashlib
import json
from pathlib import Path

from semantik_architect.bootstrap import build_container
from semantik_architect.adapters.realization.gf import GfBridgeRealizer
from semantik_architect.domain.communication.request import CommunicationRequest


class FakePgfRuntime:
    def __init__(self,path): self.path=path
    def linearize(self,expr,concrete_language): return f'{concrete_language}:{expr}'


def _sha(path:Path)->str: return hashlib.sha256(path.read_bytes()).hexdigest()


def _make_runtime(root:Path):
    r=root/'r1'; r.mkdir(parents=True)
    grammar=r/'grammar.pgf'; grammar.write_bytes(b'fake-pgf')
    bridge=r/'bridge.json'; bridge.write_text(json.dumps({
      'schema_version':'1.0','contract_version':'1.0','operations':{
        'clause.transitive_event':{
          'requires':['agent','predicate','patient'],
          'expression':'DoTransitive {agent} {predicate} {patient}', 'consumes_features':['polarity']
        }
      }
    }),encoding='utf-8')
    lex=r/'lexicon.json'; lex.write_text(json.dumps({
      'schema_version':'1.0','lexicon_id':'lex-en-1','entries':[
        {'semantic_ref':'local-concept:repair','language':'en','lexical_ref':'repair_V2','binding_kind':'gf_expr','category':'VERB'}
      ]
    }),encoding='utf-8')
    cap=r/'capabilities.json'; cap.write_text(json.dumps({
      'schema_version':'1.0','manifest_id':'cap1','runtime_set_id':'rt1','languages':{
        'en':{'status':'RELEASED','concrete':'SAGrammarEng','profiles':[{'profile_id':'sa-core-1','status':'RELEASED','evidence_ref':'evidence.json'}]}
      }
    }),encoding='utf-8')
    evidence=r/'evidence.json'; evidence.write_text('{"passed":true}',encoding='utf-8')
    profile=r/'profile.json'; profile.write_text(json.dumps({'schema_version':'1.0','profile_id':'sa-core','profile_version':1,'required_operations':['clause.transitive_event'],'required_features':[],'required_block_kinds':['utterance'],'test_suite_ref':'suite:sa-core-1'}),encoding='utf-8')
    manifest={
      'schema_version':'1.0','runtime_set_id':'rt1','sa_version_range':'>=1.0,<2.0','sa_gf_contract_version':'1.0',
      'artifacts':[
        {'artifact_type':'grammar','artifact_id':'grammar-en','sha256':_sha(grammar),'path':'grammar.pgf'},
        {'artifact_type':'lexical','artifact_id':'lex-en','sha256':_sha(lex),'path':'lexicon.json'},
        {'artifact_type':'other','artifact_id':'sa-gf-bridge-v1','sha256':_sha(bridge),'path':'bridge.json'},
        {'artifact_type':'other','artifact_id':'capability-profile-sa-core-1','sha256':_sha(profile),'path':'profile.json'}
      ],
      'capability_manifest_ref':'capabilities.json','capability_manifest_sha256':_sha(cap),'conformance_evidence_refs':['evidence.json'],'conformance_evidence_sha256':{'evidence.json':_sha(evidence)},'status':'RELEASED'
    }
    (r/'runtime.manifest.json').write_text(json.dumps(manifest),encoding='utf-8')


def _request():
    return CommunicationRequest.from_dict({
      'schema_version':'1.0','request_id':'r1',
      'semantic_graph':{
        'graph_id':'g1',
        'nodes':[
          {'id':'alice','kind':'entity_ref','external_ref':'local:alice','labels':{'en':'Alice'}},
          {'id':'pump','kind':'entity_ref','external_ref':'local:pump','labels':{'en':'pump 1'}},
          {'id':'repair','kind':'concept_ref','concept_ref':'local-concept:repair'}
        ],
        'statements':[{'id':'s1','predicate_ref':'local-predicate:repair_event','polarity':'positive','arguments':[
          {'role_ref':'semantic-role:agent','value_id':'alice'},
          {'role_ref':'semantic-role:patient','value_id':'pump'},
          {'role_ref':'semantic-role:event_type','value_id':'repair'}]}]
      },
      'obligations':[{'obligation_id':'o1','semantic_refs':['s1'],'force':'ASSERT'}],
      'context':{'target_language':'en','target_locale':'en-CA'},
      'constraints':{'allowed_block_kinds':['utterance']},
      'capability_profile':'sa-core-1'
    })


def test_end_to_end_pipeline(tmp_path):
    _make_runtime(tmp_path)
    realizer=GfBridgeRealizer(runtime_factory=FakePgfRuntime)
    c=build_container(tmp_path,realizer=realizer)
    result=c.render.execute(_request())
    assert result.plain_text=='SAGrammarEng:DoTransitive "Alice" repair_V2 "pump 1"'
    assert result.coverage[0].obligation_id=='o1'
    assert result.runtime.runtime_set_id=='rt1'
    assert result.deterministic_result_id.startswith('sha256:')
