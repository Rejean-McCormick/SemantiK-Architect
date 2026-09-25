from semantik_architect.application.planning.communication_planner import CommunicationPlanner
from semantik_architect.application.planning.language_planner import GenericLanguagePlanner
from semantik_architect.domain.communication.request import CommunicationRequest
from semantik_architect.domain.language.lexical import LexicalPlanningContext


def test_explicit_planning_hint_maps_extensible_predicate_without_core_branch():
    req=CommunicationRequest.from_dict({
      'schema_version':'1.0',
      'semantic_graph':{
        'graph_id':'g',
        'nodes':[
          {'id':'x','kind':'entity_ref','external_ref':'demo:x','labels':{'en':'X'}},
          {'id':'y','kind':'entity_ref','external_ref':'demo:y','labels':{'en':'Y'}}
        ],
        'statements':[{'id':'s','predicate_ref':'domain:opaque_relation','polarity':'positive','arguments':[
          {'role_ref':'domain:lhs','value_id':'x'},{'role_ref':'domain:rhs','value_id':'y'}]}]
      },
      'obligations':[{'obligation_id':'o','semantic_refs':['s'],'force':'ASSERT'}],
      'supporting_context':[
        {'subject_id':'s','property_ref':'sa:operation','value':'nominal.apposition'},
        {'subject_id':'s','property_ref':'sa:role-map','value':{'entity':'role:lhs','description':'role:rhs'}},
        {'subject_id':'s','property_ref':'sa:slot-map','value':{'entity':'role:lhs','description':'role:rhs'}}
      ],
      'context':{'target_language':'en'},
      'constraints':{'allowed_block_kinds':['utterance']},
      'capability_profile':'sa-core-1'
    })
    cp=CommunicationPlanner().plan(req)
    lp=GenericLanguagePlanner().plan(req,cp,LexicalPlanningContext('en',{}))
    assert lp.units[0].operation_id=='nominal.apposition'
    assert lp.units[0].lexical_slots=={'entity':'x','description':'y'}
