# SemantiK Architect 1.2.1 — Kristal v6 + multilingual candidate extensions

SemantiK Architect remains a deterministic semantic-to-human multilingual communication engine. Version 1.2.1 preserves the **Kristal v6 communication projection** boundary introduced in 1.2.0 and adds fail-closed per-language candidate `extension_capabilities` for multilingual SA↔GF conformance.

## 1.2.1 multilingual candidate completion

Candidate `pipeline.lock.json` files may now declare known SA↔GF operations in `extension_capabilities`. These extensions are admitted only during candidate conformance, are reflected in the candidate capability manifest and matrix report, and never imply `RELEASED` or activation. Existing candidate bundles without the field remain valid.

This change does **not** move language grammar into SemantiK Architect: GF/RGL remains the authority for morphology, word order, governed case/adpositions and final realization.

## Canonical pipeline

```text
external domain model / Kristal v6
        ↓ explicit ACL / communication projection
CommunicationRequest
        ↓
CommunicationPlanner
        ↓
CommunicationPlan
        ↓ lexical preflight
LanguagePlanner
        ↓
LanguagePlan / RealizationUnit
        ↓ exact lexical binding
versioned SA↔GF bridge
        ↓
PGF/GF
        ↓
CommunicationResult + coverage + RuntimeSet identity
```

## Kristal v6 integration

SemantiK Architect does **not** treat raw `kristal_state` as a communication request and does not infer what should be said from valuation magnitude, record role, or actionability.

The adapter `KristalV6Acl` accepts `semantik.kristal-v6.communication-projection/1.0`:

- pins Kristal Standard `6.0.0`;
- references one `kristal_state`;
- explicitly selects the assertions to communicate;
- requires every selected assertion to remain traceable through `source_refs` in the mapped canonical request;
- preserves `record_role`, `valuations`, `applicability`, and `actionability` as supporting context;
- never creates communication obligations from `actionability = automatic` or a high valuation.

This keeps authority clear: Kristal owns its knowledge/state artifact, the upstream owner/Da’at owns the mapping decision, and SemantiK Architect owns articulation only.

See [`docs/reference/KRISTAL_V6_COMMUNICATION_PROJECTION.md`](docs/reference/KRISTAL_V6_COMMUNICATION_PROJECTION.md).

## Other 1.1.x capabilities retained

- reusable review-only multilingual `CandidateMatrixConformance`;
- explicit lexical planning metadata and deterministic lexical-source precedence;
- local Wikidata Lexeme support;
- immutable RuntimeSet/capability/conformance model;
- strict SA↔GF bridge and fail-closed realization;
- offline canonical runtime path.

## Validation

Run:

```bash
PYTHONPATH=src:. python tools/validate_repository.py
```

The repository validator compiles sources, executes pytest, and validates all declared JSON schemas.

## Fail-closed invariant

Canonical rendering has **no hidden fallback**. Missing runtime/language capability, unmappable semantics, invalid lexical binding or GF failure remains an explicit error rather than silently changing language or meaning.
