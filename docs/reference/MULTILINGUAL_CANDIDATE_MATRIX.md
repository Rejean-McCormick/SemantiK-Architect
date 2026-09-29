# Multilingual Candidate Matrix

Status: **informative implementation reference**

## Purpose

`CandidateMatrixConformance` runs the same SemantiK Architect candidate-conformance path across multiple immutable language/profile candidate bundles and produces one review result per language.

It exists to support cross-language development and evidence gathering without moving GF/RGL language construction into SA.

## Boundary

The matrix **consumes** candidate bundles that already contain:

- `grammar.pgf`;
- `bridge.json`;
- `lexicon.json`;
- `profile.json`;
- `conformance.suite.json`;
- `pipeline.lock.json`.

It does **not** compile a GF language, edit RGL sources, create a production RuntimeSet, write release evidence, or activate a runtime.

The authority flow therefore remains:

```text
GF/RGL language source
  -> external build
  -> immutable SA candidate bundle
  -> CandidateMatrixConformance
  -> review result
  -> normal release gate (separate)
```

## API

```python
from semantik_architect.conformance import CandidateMatrixConformance

report = CandidateMatrixConformance().run([
    {
        "candidate_root": "state/candidates/Fre/semantik-core-fr-lab-1",
        "runtime_set_id": "semantik-core-fr-lab-1",
        "metadata": {"rgl_code": "Fre"},
    },
    {
        "candidate_root": "state/candidates/Eng/semantik-core-en-lab-1",
        "runtime_set_id": "semantik-core-en-lab-1",
        "metadata": {"rgl_code": "Eng"},
    },
])
```

For each suite case the matrix records:

- pass/fail;
- realized `plain_text`;
- the SA↔GF operation IDs selected by the validated `LanguagePlan`;
- a deterministic error string when the case fails.

## Identity checks

Before running a candidate, the matrix requires the suite language, capability profile and runtime-set identity to match `pipeline.lock.json`. Candidate artifact integrity remains enforced by `CandidateConformance`.

## Release semantics

A matrix `PASS` is development evidence only. It is **not** equivalent to `RELEASED` under the Language Conformance Lock. Production release still requires all release gates, immutable evidence pinning and an admitted RuntimeSet.
