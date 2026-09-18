# Testing and Validation

Status: **normative**

## Goal

Tests validate the canonical architecture described in this documentation. They do not preserve superseded APIs or runtime paths.

## Required test layers

### Domain and planning

Validate:

- canonical frames;
- required `frame_type` behavior;
- frame conversions where they are part of the current domain contract;
- `PlannedSentence` behavior;
- `ConstructionPlan` validation and immutability expectations;
- slot mapping and reserved-key rules.

### Lexical resolution

Validate:

- lexical reference preservation;
- language-scoped lookup;
- plan resolution without corrupting semantic slots;
- runtime language scope derived from the deployed PGF.

### Renderer contracts

Every renderer test targets:

```text
ConstructionPlan -> SurfaceResult
```

Tests must not require a direct `Frame -> renderer` API.

### API

Validate:

- canonical route and JSON shape;
- explicit `frame_type`;
- rejection of retired frame aliases;
- `SurfaceResult` response shape;
- public/debug parity;
- language capability errors;
- deployment auth behavior separately from semantic validation.

### Dynamic GF

GF tests load:

```text
runtime/semantik_architect.pgf
```

or the configured `PGF_PATH`.

A configured standard run must not skip because a test still expects a local `gf/semantik_architect.pgf` build output.

## Full-suite gate

A refactor is not complete until the complete test suite has been run after targeted gates pass.

Skipped tests are reviewed as deliberately as failures. A skip caused by stale paths, removed build workflows, or absent pre-cutover infrastructure is a test defect.

## Diagnostic gate

The external SemantiK LevelUpDiag profile should remain green across these runtime concerns:

- runtime boundary;
- Python integrity;
- dependency readiness;
- PGF runtime contract;
- API import/surface contract;
- frontend runtime surface;
- runtime regression tests.

## Anti-drift scan

The active repository must not introduce runtime references to retired architecture such as:

- grammar build workers or queues;
- local GF source ownership;
- old PGF paths under `gf/`;
- development tools APIs;
- direct frame-to-engine generation;
- a second generation result model parallel to `SurfaceResult`.
