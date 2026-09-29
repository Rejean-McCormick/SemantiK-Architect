# SemantiK Architect Multilingual Candidate Matrix Overlay v0.2.0

Additive overlay for SemantiK Architect **1.1.2**.

## What this update adds

SemantiK Architect now exposes a reusable, review-only multilingual candidate matrix:

```text
already-built candidate bundles
  -> CandidateMatrixConformance
  -> one validated LanguagePlan + realization result per suite case
  -> matrix PASS / REVIEW
```

This is the permanent SA-side integration point for multilingual conformance. It deliberately does **not** move GF/RGL language engineering into SemantiK Architect and it never releases or activates a RuntimeSet.

The previous GF CLI UTF-8 correction remains included in this overlay.

## Files added/updated

- `src/semantik_architect/conformance/matrix.py`
- `src/semantik_architect/conformance/candidate.py`
- `src/semantik_architect/conformance/__init__.py`
- `docs/reference/MULTILINGUAL_CANDIDATE_MATRIX.md`
- `docs/22_IMPLEMENTATION_STATUS.md`
- `tests/integration/test_candidate_matrix.py`
- `tests/integration/test_konstellation.py`
- package version metadata (`1.1.2`)
- existing GF CLI UTF-8 patch and regression test

## Apply

```powershell
.\Apply-Overlay.ps1
```

Default target:

```text
C:\mycode\SemantiK_Architect\SemantiK_Architect
```

The script backs up every overwritten file.

## Validation

The supplied snapshot passes:

```text
43 passed
```

with `PYTHONPATH=src:. pytest -q`.
