import json
from pathlib import Path

from semantik_architect.domain.communication.request import CommunicationRequest
from semantik_architect.application.validation.request_validation import RequestValidator


def test_example_request_parses_and_validates():
    data=json.loads(Path('examples/orgo_fr_request.json').read_text(encoding='utf-8'))
    req=CommunicationRequest.from_dict(data)
    assert req.schema_version=='1.0'
    assert req.context.target_language=='fr'
    assert len(req.obligations)==2
    RequestValidator().validate(req)


def test_round_trip_keeps_canonical_shape():
    data=json.loads(Path('examples/orgo_fr_request.json').read_text(encoding='utf-8'))
    req=CommunicationRequest.from_dict(data)
    assert CommunicationRequest.from_dict(req.to_dict()).to_dict()==req.to_dict()
