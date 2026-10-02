from __future__ import annotations
import json
from pathlib import Path
import jsonschema

ROOT=Path(__file__).resolve().parents[2]

def test_math_examples_validate():
    formula_schema=json.loads((ROOT/'schemas/mathkristal_formula_ir.schema.json').read_text())
    projection_schema=json.loads((ROOT/'schemas/mathkristal_formula_projection.schema.json').read_text())
    config_schema=json.loads((ROOT/'schemas/informath_runtime_config.schema.json').read_text())
    registry_schema=json.loads((ROOT/'schemas/math_symbol_registry.schema.json').read_text())
    formula=json.loads((ROOT/'examples/mathkristal_euler_formula.json').read_text())
    projection=json.loads((ROOT/'examples/mathkristal_euler_projection.json').read_text())
    config=json.loads((ROOT/'profiles/math-pure-1/informath.config.json').read_text())
    registry=json.loads((ROOT/'profiles/math-pure-1/math-symbol-registry.json').read_text())
    jsonschema.validate(formula,formula_schema)
    jsonschema.validate(projection,projection_schema)
    jsonschema.validate(config,config_schema)
    jsonschema.validate(registry,registry_schema)
