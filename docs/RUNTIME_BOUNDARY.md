# Runtime Boundary

Status: **normative**

## Decision

SemantiK Architect is a **semantic/NLG runtime** and a **consumer of precompiled GF runtime artifacts**. It is not a GF grammar-development environment.

## Responsibilities kept in this repository

SemantiK Architect owns:

- semantic frame/domain models;
- request normalization into canonical semantic input;
- planning and construction selection;
- `PlannedSentence` and `ConstructionPlan` runtime contracts;
- runtime lexical lookup and lexical resolution;
- renderer dispatch and realization;
- GF/PGF runtime adapters;
- non-GF runtime renderers where supported;
- the public generation API and runtime UI;
- runtime capability reporting;
- optional in-process discourse/session state;
- health, observability, deployment configuration, tests, and diagnostics.

## Responsibilities outside this repository

SemantiK Architect does not own:

- GF source grammar authoring;
- `.gf` source files for the runtime grammar;
- RGL maintenance or vendoring;
- grammar repair or grammar-generation agents;
- GF source alignment or compilation workflows;
- language-onboarding build pipelines;
- grammar build workers or queues;
- Redis/ARQ compilation infrastructure;
- grammar-development dashboards or tools APIs;
- maturity matrices for grammar-development readiness;
- GF/RGL backups, quarantines, or source archives.

Those concerns belong to the external GF development/validation ecosystem. The boundary between systems is the deployed PGF artifact and any explicitly versioned runtime data that SemantiK requires.

## PGF deployment contract

The default runtime artifact is:

```text
runtime/semantik_architect.pgf
```

It may be overridden with:

```text
PGF_PATH
```

A missing or unreadable PGF is a deployment/configuration failure. The application must not respond by synthesizing or compiling a grammar.

## Capability contract

Language capability is determined from the **loaded PGF concrete languages**, then mapped to application language codes. Lexicon directory presence, old language inventories, or development matrices do not define runtime capability.

Optional display metadata may live in `runtime/languages.json`, but it cannot create a capability that is absent from the loaded PGF.

## Generation ingress contract

Standard JSON generation requests carry explicit semantic intent:

- `frame_type` is mandatory;
- the frame family is not inferred from payload shape;
- each public frame family has one canonical JSON shape;
- retired aliases are rejected rather than normalized;
- unsupported frame types are request/domain validation errors.

Ninai/function-style input, when enabled, is a separate input protocol. It must normalize to the same canonical domain model before planning and does not create a second runtime pipeline.

## No hidden second runtime

There is one canonical generation path. A facade may compose the stages, but it must not introduce an alternate direct frame-to-engine execution path.

The renderer contract is:

```text
ConstructionPlan -> SurfaceResult
```

not:

```text
Frame -> renderer
```

## Runtime state

Optional discourse/session state is ephemeral, bounded, and in-process. It is not a grammar-build queue, a persistence layer, or a cross-process coordination mechanism. See `SESSION_STATE.md`.
