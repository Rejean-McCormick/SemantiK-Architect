# GF / PGF Runtime Contract

Status: **normative**

## Role of GF

GF is a **runtime realization backend** in SemantiK Architect. GF is not the semantic model, not the planner, and not the repository's grammar-development workflow.

The runtime relationship is:

```text
ConstructionPlan
    -> GF runtime adapter
    -> precompiled PGF concrete language
    -> SurfaceResult
```

## Artifact ownership

SemantiK consumes a precompiled artifact:

```text
runtime/semantik_architect.pgf
```

The artifact is produced outside this repository by the GF development/validation ecosystem.

The runtime repository does not own the `.gf` sources that produced it.

## Configuration

Default:

```text
runtime/semantik_architect.pgf
```

Optional deployment override:

```text
PGF_PATH=/absolute/or/deployment/path/semantik_architect.pgf
```

`PGF_PATH` changes the deployed artifact location. It does not authorize source generation or compilation.

## Runtime loader requirements

The runtime environment must provide a compatible PGF binding. Loading the artifact is part of application readiness.

A missing, unreadable, or incompatible PGF is a deployment failure.

SemantiK must not:

- invoke the GF compiler to repair the failure;
- search for local `.gf` sources and build a replacement;
- clone or vendor an RGL;
- mutate grammar sources;
- submit a grammar build job.

## Concrete languages

The loaded PGF is the source of truth for concrete language capability.

Current validated artifact snapshot:

```text
WikiEng
WikiFre
```

Application-level mapping currently resolves these to:

```text
WikiEng -> en
WikiFre -> fr
```

The mapping is runtime/application metadata. The concrete names remain PGF-owned identifiers.

## Renderer contract

The GF adapter consumes `ConstructionPlan` and returns `SurfaceResult`.

It may use resolved lexical material and renderer-specific metadata, but it must not independently re-plan the sentence or accept a raw API payload as its primary contract.

Direct frame-to-GF execution is not a second supported runtime path.

## Diagnostics

GF realization should expose useful runtime facts through `debug_info`, such as:

- selected backend;
- attempted backends;
- resolved PGF concrete language;
- construction ID;
- slot keys;
- optional AST/linearization details when safe and useful;
- fallback reason if another renderer is used after GF cannot realize a plan.

Diagnostics do not change the public semantic contract.

## Testing

Dynamic GF tests use the canonical runtime artifact path or `PGF_PATH`. A standard configured test run must not skip GF tests because they still reference an old `gf/` path or expect a local build step.
