# SemantiK Architect 1.2.0 — Validation Report

Validation date: **2026-10-01**

## Result

**PASS** for the repository core, Kristal v6 communication boundary, schemas, multilingual candidate matrix, deterministic runtime path and architecture guardrails.

## Automated validation

- `PYTHONPATH=src:. python tools/validate_repository.py`: **PASS**;
- pytest: **47 passed**;
- JSON Schema meta-validation: **12 schemas PASS**;
- `semantik.kristal-v6.communication-projection/1.0` canonical example: **PASS**;
- `KristalV6Acl` selected-assertion traceability: **PASS**;
- `actionability=automatic` non-inference: **PASS** — no obligation or communicative force is created/changed;
- unknown Kristal actionability mode: fail-closed;
- LevelUpDiag 2.2.0 `S30`: **PASS** against this snapshot;
- LevelUpDiag 2.2.0 `S10`: **PASS** after removing misplaced `.gf` grammar-development sources.

## Architecture adjustment

Grammar-development `.gf` sources were removed from the SemantiK Architect profile directories. Grammar source authority remains GF/Wordbench. Candidate/released PGF/runtime artifacts may still participate in SA conformance/runtime workflows.

## Kristal v6 boundary

SemantiK Architect does not ingest raw `kristal_state` as a request. An upstream owner/Da’at mapping supplies one explicit communication projection. Selected Kristal assertion IDs must remain visible in `source_refs`. `record_role`, `valuations[]`, `applicability`, and `actionability` are preserved as supporting context unless the upstream mapping explicitly selects the underlying assertion as a communication obligation.

## Runtime note

The SmartSnap contains profile/runtime manifests whose real PGF artifacts are not all present. Full deployed RuntimeSet acceptance therefore remains an external release-input concern and is not silently downgraded to a fallback renderer.
