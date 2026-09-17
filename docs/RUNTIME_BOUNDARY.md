# SemantiK Architect — Runtime Boundary

## Decision

SemantiK Architect is a consumer of Grammatical Framework runtime artifacts. It is
not a grammar-development, RGL-maintenance, compilation, repair, or audit environment.

## Kept here

- semantic frame/domain model;
- planning and construction selection;
- lexical lookup needed at runtime;
- GF/PGF runtime adapters;
- text-generation API and generation UI;
- runtime health, configuration, deployment, and tests.

## Removed from here

- `builder/` and generated GF bridge sources;
- grammar factories, grammar repair scripts, AI grammar authoring agents;
- GF/RGL backups and quarantines;
- build/onboarding queue, worker, Redis compilation pipeline;
- developer tools API/dashboard, Everything Matrix UI, grammar refiner UI;
- source `.gf` ownership inside the runtime repository.

## Runtime contract

The application receives a precompiled `semantik_architect.pgf`. The default location
is `runtime/semantik_architect.pgf`, overridable with `PGF_PATH`.

A missing PGF is a deployment/configuration error, not a signal for SemantiK Architect
to synthesize or compile a grammar.

Language availability is read from the loaded PGF, not from an Everything Matrix. Optional display names may be supplied in `runtime/languages.json`.

## Runtime session state

Optional `X-Session-ID` discourse state is held in an in-process bounded/TTL
store. No Redis broker or compilation queue is part of the application runtime.
The state is intentionally ephemeral and is not shared across API processes.

