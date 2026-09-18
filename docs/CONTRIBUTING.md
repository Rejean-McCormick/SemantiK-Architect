# Contributing

Status: **normative contributor rules**

## First rule

Read `RUNTIME_BOUNDARY.md` and `ARCHITECTURE.md` before changing runtime behavior.

## Generation changes

A runtime generation change must preserve the canonical pipeline:

```text
Frame -> planning -> ConstructionPlan -> lexical resolution -> realization -> SurfaceResult
```

Do not add a shortcut path around `ConstructionPlan` to make one caller or test pass.

## API changes

Public request/response changes require an update to `API_GENERATION_CONTRACT.md` and, when architectural, an ADR.

Do not add input aliases merely to accept an older shape. This is a new application contract: callers and tests are updated to the canonical form instead.

## Renderer changes

A renderer:

- consumes a `ConstructionPlan`;
- returns a `SurfaceResult`;
- does not choose semantic intent;
- does not own API normalization;
- does not become a grammar compiler.

## GF changes

Do not add `.gf` source, an RGL, GF compilation scripts, or grammar-development workflows to this repository.

Changes to the runtime grammar are produced externally and enter SemantiK as a new deployed PGF artifact.

## Language changes

Do not claim support from a target-language list. Capability is proven by the deployed artifact/data plus passing runtime tests.

## Lexicon changes

Lexicon work in this repository is runtime lookup/resolution work. Language-development scoring and source-authoring pipelines belong elsewhere.

## Documentation changes

- Keep active docs current-only.
- Use ADRs for durable architectural decisions.
- Do not add status snapshots that become competing sources of truth.
- Do not create an in-repo archive of superseded docs; Git history is the archive.

## Before commit

Run, at minimum:

1. targeted tests for the changed contract;
2. full pytest;
3. dynamic PGF/runtime tests when affected;
4. LevelUpDiag when runtime/API/frontend boundaries are affected;
5. a repository scan for prohibited architecture drift.
