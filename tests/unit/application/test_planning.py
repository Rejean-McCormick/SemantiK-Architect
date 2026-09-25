from semantik_architect.domain.communication.request import CommunicationRequest
from semantik_architect.application.planning.communication_planner import CommunicationPlanner
from semantik_architect.application.planning.language_planner import GenericLanguagePlanner
from semantik_architect.domain.language.lexical import LexicalPlanningContext


def _request():
    return CommunicationRequest.from_dict({
      'schema_version':'1.0',
      'semantic_graph':{
        'graph_id':'g1',
        'nodes':[
          {'id':'alice','kind':'entity_ref','external_ref':'local:alice','labels':{'en':'Alice'}},
          {'id':'pump','kind':'entity_ref','external_ref':'local:pump','labels':{'en':'pump 1'}},
          {'id':'repair','kind':'concept_ref','concept_ref':'local-concept:repair'},
        ],
        'statements':[{
          'id':'s1','predicate_ref':'local-predicate:repair_event','polarity':'positive',
          'arguments':[
            {'role_ref':'semantic-role:agent','value_id':'alice'},
            {'role_ref':'semantic-role:patient','value_id':'pump'},
            {'role_ref':'semantic-role:event_type','value_id':'repair'},
          ]
        }]
      },
      'obligations':[{'obligation_id':'o1','semantic_refs':['s1'],'force':'ASSERT'}],
      'context':{'target_language':'en'},
      'constraints':{'allowed_block_kinds':['utterance']},
      'capability_profile':'sa-core-1'
    })


def test_transitive_statement_plans_transitive_operation():
    req=_request(); cp=CommunicationPlanner().plan(req)
    lp=GenericLanguagePlanner().plan(req,cp,LexicalPlanningContext('en',{}))
    assert lp.units[0].operation_id=='clause.transitive_event'
    assert lp.units[0].lexical_slots['predicate']=='repair'
    assert lp.units[0].obligation_ids==('o1',)
