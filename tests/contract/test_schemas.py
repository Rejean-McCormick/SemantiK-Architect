import json
from pathlib import Path
import pytest

jsonschema=pytest.importorskip('jsonschema')


def test_all_schemas_are_valid():
    for path in Path('schemas').glob('*.json'):
        jsonschema.Draft202012Validator.check_schema(json.loads(path.read_text(encoding='utf-8')))


def test_examples_validate():
    req_schema=json.loads(Path('schemas/communication_request.schema.json').read_text())
    res_schema=json.loads(Path('schemas/communication_result.schema.json').read_text())
    jsonschema.validate(json.loads(Path('examples/orgo_fr_request.json').read_text()),req_schema)
    jsonschema.validate(json.loads(Path('examples/orgo_fr_result.json').read_text()),res_schema)
