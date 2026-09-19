# SemantiK Architect

SemantiK Architect is the **semantic/NLG application runtime**. It accepts canonical
semantic frames, plans constructions, resolves lexical material, and realizes text
through runtime renderers, including a precompiled Grammatical Framework PGF artifact.

## Product boundary

SemantiK Architect **uses GF; it does not develop GF**. This repository does not own:

- `.gf` source authoring, repair, generation, or compilation;
- RGL source trees, backups, or alignment workflows;
- grammar-build workers, queues, Redis/ARQ build infrastructure;
- grammar-development dashboards, maturity matrices, or refinement tools.

Those responsibilities belong to the external GF development/validation ecosystem.
SemantiK consumes the deployed runtime contract, primarily
`runtime/semantik_architect.pgf` plus semantic and lexical runtime data.

## Canonical architecture

```text
HTTP / external semantic protocol
    -> canonical Frame
    -> planning
    -> PlannedSentence
    -> ConstructionPlan
    -> lexical resolution
    -> renderer dispatch
    -> SurfaceResult
    -> public response
```

There is no direct `Frame -> engine` runtime path and no parallel `Sentence` result
contract. `ConstructionPlan` is the renderer input contract; `SurfaceResult` is the
single generation result contract.

## PGF runtime

Place the precompiled grammar at:

```text
runtime/semantik_architect.pgf
```

or set `PGF_PATH` to another deployed `.pgf` file.

A missing PGF is a deployment/readiness error. SemantiK never responds by compiling,
synthesizing, or repairing GF source.

Check readiness:

```bash
python manage.py doctor
```

Start the API:

```bash
python manage.py serve --reload
```

## Generation API

The canonical endpoint is:

```http
POST /api/v1/generate/{lang_code}
```

Standard JSON requests require an explicit, canonical `frame_type`. SemantiK does not
infer a frame family from payload shape and does not normalize retired aliases.

Canonical biography example:

```json
{
  "frame_type": "bio",
  "subject": {
    "name": "Marie Curie",
    "qid": "Q7186",
    "profession": "physicist",
    "nationality": "Polish"
  }
}
```

`entity.person`, the top-level key `type`, flat person payloads, renderer ASTs, and
backend-selection fields are not part of the standard semantic ingress contract.
Ninai/function-style input is a separate protocol adapter that must normalize to the
same canonical domain before planning.

## Runtime languages

Runtime language capability comes from the **loaded PGF concrete languages**, mapped
to application language codes. Lexicon inventories and historical language lists do
not create runtime capability. The currently deployed PGF exposes English and French.

## Session state

Optional `X-Session-ID` discourse context is process-local, bounded, and ephemeral.
It is not a persistence layer or cross-process coordination mechanism.

## Documentation

The normative documentation starts at `docs/README.md`. In particular:

- `docs/ARCHITECTURE.md`
- `docs/RUNTIME_BOUNDARY.md`
- `docs/API_GENERATION_CONTRACT.md`
- `docs/GF_RUNTIME.md`
- `docs/LANGUAGE_CAPABILITIES.md`
- `docs/TESTING_AND_VALIDATION.md`

Git history is the archive for superseded architecture; the active documentation tree
contains only the current runtime contract.
