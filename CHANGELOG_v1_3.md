# Changelog — 1.3.0-alpha.1

## Mathematical articulation

- Added `MathKristalFormulaAcl` and Formula IR 1.0.0 validation.
- Added explicit `semantik.mathkristal-formula-ir.communication-projection/1.0` boundary.
- Added structural Formula IR → canonical semantic graph projection with source traceability.
- Added `math-pure-1` / `math-natural-1` language planning.
- Added `math.informalize_formula` operation.
- Added Formula IR → Dedukti encoder and versioned math symbol registry.
- Added `InformathMathRealizer` and composite realization routing.
- Added SDK/CLI `project-math` and `render-math` surfaces.
- Added candidate Euler profile and schemas/examples.

## Authority / safety invariants

- No LaTeX parsing or semantic guessing is introduced.
- No parallel natural-language math grammar is embedded in SemantiK Architect.
- Informath/MathCore/GF remains the mathematical realization authority.
- Candidate profiles do not imply `RELEASED` support.
- Kristal v6 assertion selection remains explicit and upstream-owned.

## Validation

- 58 pytest tests pass.
- 16 JSON Schemas meta-validate.
