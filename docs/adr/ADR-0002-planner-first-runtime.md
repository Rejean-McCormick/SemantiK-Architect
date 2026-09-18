# ADR-0002 — Planner-first runtime

Status: **Accepted**  
Date: 2026-09-18

## Context

Multiple renderer technologies can realize the same semantic intent. Allowing each renderer or router to independently decide sentence structure creates semantic drift.

## Decision

Planning is authoritative. The canonical pipeline is:

```text
Frame -> planning -> PlannedSentence -> ConstructionPlan -> lexical resolution -> renderer -> SurfaceResult
```

Renderers consume `ConstructionPlan`; they do not accept raw public payloads as their primary contract.

## Consequences

- construction choice is shared across backends;
- lexical resolution is shared runtime infrastructure;
- renderer-specific code owns surface realization only;
- direct frame-to-engine execution is not a supported second path;
- `SurfaceResult` is the single result contract.
