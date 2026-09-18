# Runtime Architecture

Status: **normative**

## Architectural center

SemantiK Architect is planner-first and construction-centered. The stable center is not a language-specific engine and not GF itself.

```text
HTTP / input adapter
    |
    v
canonical semantic Frame
    |
    v
planning
    |
    v
PlannedSentence
    |
    v
ConstructionPlan
    |
    v
lexical resolution
    |
    v
realization / renderer dispatch
    |
    v
SurfaceResult
    |
    v
public response mapper
```

The planner decides the sentence intent and construction. The renderer realizes that already-planned intent.

## Layer 1 — Input normalization

Transport adapters convert external requests into canonical domain objects.

Responsibilities:

- establish the authoritative application language code;
- require explicit semantic intent;
- validate the canonical frame shape;
- normalize supported external protocols such as Ninai into canonical frames;
- remove transport-only fields before domain processing.

This layer must not choose renderer-specific syntax or templates.

## Layer 2 — Planning

Planning determines **what is to be realized**.

The planning layer owns:

- construction selection;
- information packaging;
- topic/focus decisions where available;
- discourse-sensitive choices;
- language-independent generation options;
- the production of `PlannedSentence` data.

Biography is a supported domain, not the architecture. New frame families must enter through the same planning abstraction.

## Layer 3 — ConstructionPlan

`ConstructionPlan` is the canonical handoff from planning to lexical/realization stages.

Its stable conceptual fields are:

- `construction_id`;
- `lang_code`;
- `slot_map`;
- `generation_options`;
- optional topic/focus identifiers;
- metadata required by runtime dispatch or diagnostics.

`slot_map` contains semantic/construction slots. Control envelopes, diagnostics, or internal bookkeeping must not masquerade as semantic slots.

Plan objects are treated as runtime value objects. Later stages must not depend on shared mutable plan state.

## Layer 4 — Lexical resolution

Lexical resolution binds semantic/construction slots to language-appropriate lexical material before realization.

It is shared runtime infrastructure, not renderer-specific preprocessing. It may resolve lexical references, entity references, lemmas, forms, features, and surface hints while preserving the semantic identity of the original slots.

See `LEXICON_RUNTIME.md`.

## Layer 5 — Realization

Renderers consume a `ConstructionPlan` and return a `SurfaceResult`.

Supported renderer families may include:

- GF/PGF realization;
- family/construction renderers;
- an explicitly configured safe-mode renderer.

All renderers obey the same input/output contract. No renderer becomes a second planner.

Backend selection is an internal runtime concern. Public semantic input does not depend on renderer-specific instructions.

## Layer 6 — SurfaceResult

`SurfaceResult` is the one canonical generation result.

Required public/runtime fields:

- `text`;
- `lang_code`;
- `construction_id`;
- `renderer_backend`;
- `fallback_used`;
- `tokens`;
- `debug_info`;
- `generation_time_ms`.

There is no parallel `Sentence` result contract.

## Orchestration rule

A high-level generation use case may compose planning, lexical resolution, and realization. Such a facade is composition only. It must not maintain a direct engine path that bypasses `ConstructionPlan`.

## Error boundaries

- input/schema problems -> request/domain validation error;
- unsupported language -> capability/language error;
- planner failure -> domain/planning error;
- lexical failure -> domain/lexical error;
- realization failure -> realization/runtime error;
- missing PGF -> deployment/readiness error.

Errors must not be converted into successful `SurfaceResult` objects.

## Architectural invariants

1. One semantic input becomes one canonical domain representation before planning.
2. Planning is authoritative for construction choice.
3. `ConstructionPlan` is the renderer input contract.
4. Lexical resolution is independent of renderer choice.
5. `SurfaceResult` is the result contract.
6. Runtime capabilities come from deployed runtime artifacts, not development inventories.
7. No GF compilation occurs inside the application runtime.
8. No pre-cutover internal API is kept only to satisfy old callers or tests.
