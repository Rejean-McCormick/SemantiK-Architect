# SemantiK Architect 1.2.1 — Kristal v6 compatible candidate capabilities

- Preserves the complete Kristal v6 communication boundary from 1.2.0.
- Adds optional `extension_capabilities` to candidate `pipeline.lock.json`.
- Validates extension IDs against the canonical SA↔GF v1 operation catalog.
- Rejects non-array, duplicate and unknown extension declarations fail-closed.
- Mirrors candidate extensions into the candidate capability manifest.
- Exposes admitted extensions in `CandidateMatrixConformance` reports.
- Keeps old candidate bundles backward compatible when the field is absent.
- Does not release or activate any RuntimeSet and adds no language-specific grammar logic to SA.
