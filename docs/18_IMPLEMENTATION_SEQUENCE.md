# Implementation Sequence

Status: **recommended build order**

## Phase 0 — lock validation and repository skeleton

Implement package skeleton, lint/type/test tooling, documentation/schema validation and architecture import tests.

Exit: empty repo enforces dependency rules.

## Phase 1 — canonical semantic/domain values

Implement immutable semantic graph, statement/value variants, obligations, context, constraints, request/result and stable error envelope.

No PGF, HTTP, database or compatibility code.

## Phase 2 — faithfulness and coverage engine

Implement obligation accounting, deterministic derivation registry, ordering constraints and coverage validation.

Exit: property tests prove obligations cannot disappear silently.

## Phase 3 — communication planning

Implement language-neutral grouping/sequencing and the first bounded communication patterns (single content group, repeated collection, greeting/closing intent).

## Phase 4 — runtime catalog and capability manifests

Implement immutable RuntimeSet selection/readiness before GF realization exists. This prevents ad hoc runtime loading later.

## Phase 5 — lexical knowledge preflight

Implement minimal local lexical knowledge adapter needed by initial language planning.

## Phase 6 — language planning + SA↔GF operation catalog

Implement `LanguagePlan`/`RealizationUnit` with one narrow released profile. Do not add a second IR.

## Phase 7 — GF bridge adapter

Implement the versioned bridge contract against an exact PGF artifact. One fully working end-to-end language/profile slice is more valuable than broad placeholders.

Exit: canonical request -> GF -> communication result succeeds with coverage.

## Phase 8 — lexical binding and local Wikidata/Kristal resources

Add deterministic lexical snapshot integration.

## Phase 9 — conformance harness

Implement common profile suites and immutable evidence output. Bring Albanian/current target language through the real release gate.

## Phase 10 — ecosystem ACLs

Add Kristal, Orgo, eThikos, KeenKonnect/Konnaxion and optional Abstract-Wiki adapters one at a time.

## Phase 11 — API/SDK/operations

Add Python SDK, HTTP, health/readiness, metrics, logging, tracing and deadlines.

## Phase 12 — language scaling

The dominant growth path becomes:

```text
GF language development -> artifact -> SA conformance -> capability manifest -> release
```

not architectural branching in SA.
