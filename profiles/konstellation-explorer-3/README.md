# Konstellation Explorer profile 3 — prototype

Goal: realize proposition sentences from typed semantic references rather than passing a complete upstream prose sentence as `patient`.

This profile is additive. It does not modify `konstellation-explorer-1`, `konstellation-explorer-2`, `konstellation-fr-1`, or `konstellation-fr-2`.

The prototype uses typed GF categories (`NP`, `V2`, `ClassNP`) and SemantiK Architect `gf_expr` bindings. Grammar development and compilation occur in GF/Wordbench; only a candidate/admitted PGF artifact is supplied to the release pipeline. The resulting `Konstellation.pgf` must then be released as a new RuntimeSet (`konstellation-fr-3`) through SemantiK Runtime Orchestrator. Do not reuse the expression-level fixture as a production PGF.

## Five-case conformance fixture

The original five-phrase standalone prototype is integrated into the parent SemantiK Architect repository under `examples/phrase-prototype/`, and this folder is its **single authoritative GF/profile source**. Run `python tools/phrase_prototype.py` from repository root for the real Architect planning pipeline with a **simulated PGF linearization**. This is a fixture check only, not a released RuntimeSet.
