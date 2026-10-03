# Changelog — 1.3

## 1.3.0-alpha.2 — 2026-10-03

### Ecosystem alignment

- Retains `kristal_state/6.0` / `semantik.kristal-v6.communication-projection/1.0` as the stable portable articulation boundary.
- Aligns documentation and executable baseline metadata to Kristal/Kristall `7.0.0-draft.3.2`.
- Normalizes the human-facing integration name to **DaaT** and machine id `daat`; DaaT is explicitly not a communication-selection authority.
- Defines Kompiler as read-only context assembly only; Kompiler context cannot create/drop communication obligations.
- Defines EncyK and Médiathèque as upstream source acquisition/storage authorities, outside SA runtime ownership.
- Removes obsolete SenTient/Da’at boundary language from the active architecture.
- Adds ADR-0015 and a Kristal/Kristall v7 alignment reference without changing the portable v6 projection schema.
- Adds architecture tests preventing runtime imports of EncyK, Kompiler, Médiathèque and Interaction Kernel internals.
- Removes stale incomplete RuntimeSet deployments/activation from source control; `runtime/` now contains documentation only until externally released artifacts are deployed.
- Removes grammar-development `.gf` sources and the old PGF backup from SA profiles; grammar source authority remains GF/Wordbench.
- Removes the obsolete 1.2.1 overlay installer/manifest; 1.3 is the canonical repository state rather than an overlay-on-1.2 workflow.

## 1.3.0-alpha.1

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
