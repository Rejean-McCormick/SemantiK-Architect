# Validation Report — SemantiK Architect 1.3.0-alpha.1

Date: 2026-10-02

## Repository validation

- Python compilation: **PASS**
- pytest: **58 passed**
- JSON Schema meta-validation: **16 schemas PASS**
- MathKristal Euler Formula IR schema: **PASS**
- MathKristal communication projection: **PASS**
- Math planner `math.informalize_formula`: **PASS**
- Formula IR → Dedukti structural encoding: **PASS**
- Informath adapter command/language/symbol-table assembly with injected runner: **PASS**
- existing Kristal v6 ACL tests: **PASS**
- existing lexical/GF/conformance/runtime tests: **PASS**

## Candidate runtime

`math-informath-candidate-1`: **integrity-valid CANDIDATE**.

It is intentionally not `RELEASED`: this snapshot does not bundle a production Informath binary/PGF nor language conformance evidence. Release remains fail-closed.

## Commands

```bash
PYTHONPATH=src:. python tools/validate_repository.py
PYTHONPATH=src:. python -m semantik_architect.adapters.inbound.cli.main --runtime-root runtime validate-runtime math-informath-candidate-1
```
