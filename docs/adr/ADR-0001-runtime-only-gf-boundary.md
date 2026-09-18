# ADR-0001 — Runtime-only GF boundary

Status: **Accepted**  
Date: 2026-09-18

## Context

Earlier project material mixed application runtime concerns with GF source authoring, RGL maintenance, compilation, repair, and language-development workflows.

## Decision

SemantiK Architect consumes precompiled PGF artifacts and does not own GF source/build workflows.

The canonical artifact is `runtime/semantik_architect.pgf`, optionally overridden by `PGF_PATH`.

## Consequences

- `.gf` source does not belong in the runtime repository.
- Missing PGF is a deployment error.
- GF compilation is external.
- RGL ownership is external.
- language capability is observed from the loaded PGF.
- dynamic tests exercise the deployed artifact, not a local build step.
