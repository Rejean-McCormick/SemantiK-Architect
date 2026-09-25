import pytest
from semantik_architect.domain.communication.request import CommunicationRequest
from semantik_architect.application.validation.request_validation import RequestValidator
from semantik_architect.domain.errors import SemantikArchitectError


def test_missing_semantic_reference_fails_closed():
    req=CommunicationRequest.from_dict({
      'schema_version':'1.0','semantic_graph':{'graph_id':'g','nodes':[{'id':'x','kind':'literal','value':'x'}],'statements':[]},
      'obligations':[{'obligation_id':'o','semantic_refs':['missing'],'force':'PRESENT'}],
      'context':{'target_language':'en'},'constraints':{'allowed_block_kinds':['utterance']},'capability_profile':'sa-core-1'
    })
    with pytest.raises(SemantikArchitectError) as ei: RequestValidator().validate(req)
    assert ei.value.envelope.code=='SA-REQ-001'
