# SemantiK Architect Documentation

Status: **authoritative runtime documentation**  
Cutover date: **2026-09-18**

SemantiK Architect is a semantic/NLG application runtime. It accepts explicit semantic input, plans constructions, resolves lexical material, realizes text through runtime renderers, and returns a structured surface result.

This documentation describes **one canonical runtime contract**. The repository does not preserve pre-cutover internal APIs, alternate runtime paths, retired route shapes, or historical GF-development workflows.

## Documentation authority

When implementation, tests, comments, examples, or older project material disagree with these documents, the documents below define the intended architecture and the mismatch is a defect to resolve.

Normative documents, in priority order:

1. `RUNTIME_BOUNDARY.md` — what belongs in SemantiK Architect and what does not.
2. `ARCHITECTURE.md` — the canonical runtime pipeline and internal contracts.
3. `API_GENERATION_CONTRACT.md` — the public generation API.
4. `GF_RUNTIME.md` — PGF ownership, loading, and renderer boundary.
5. `LANGUAGE_CAPABILITIES.md` — how runtime language capability is determined.
6. `LEXICON_RUNTIME.md` — runtime lexical resolution responsibilities.
7. `RUNTIME_CONFIGURATION.md` — deployment/runtime configuration.
8. `SESSION_STATE.md` — optional ephemeral discourse state.
9. `TESTING_AND_VALIDATION.md` — required verification and anti-drift rules.

Supporting documents:

- `CONTRIBUTING.md`
- `GLOSSARY.md`
- `POSITIONING.md` — conceptual/theoretical context; non-normative.
- `FILETREE.md`
- `adr/` — accepted architectural decisions.

## Canonical runtime in one line

```text
semantic input
  -> canonical Frame
  -> planning
  -> PlannedSentence
  -> ConstructionPlan
  -> lexical resolution
  -> realization
  -> SurfaceResult
  -> public JSON response
```

The planner/construction contracts define **what is said**. Renderers define **how it is surfaced**.

## Runtime artifact

SemantiK Architect consumes a precompiled GF artifact:

```text
runtime/semantik_architect.pgf
```

`PGF_PATH` may point to a different deployed PGF artifact. SemantiK Architect does not author, repair, align, or compile GF source.

## Current language snapshot

The currently validated PGF artifact exposes:

```text
WikiEng -> en
WikiFre -> fr
```

This is a deployment snapshot, not a hard-coded architectural limit. Runtime capability is derived from the loaded PGF.

## Documentation policy

Active documentation must describe the current target system only. Historical specifications, status snapshots, upgrade plans, and superseded architecture notes are not kept in the active `docs/` tree. Git history is the archive.
