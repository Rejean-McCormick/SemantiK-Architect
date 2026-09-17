# SemantiK Architect

SemantiK Architect is the **semantic/NLG application runtime**. It accepts semantic
frames, plans constructions, resolves lexical material, and realizes text through a
precompiled Grammatical Framework PGF artifact.

## Product boundary

SemantiK Architect **uses GF; it does not develop GF**. This repository does not own:

- generation or repair of `.gf` source modules;
- RGL source trees or RGL backups;
- grammar scaffolding, compilation orchestration, or compiler workers;
- language-development dashboards, maturity matrices, or grammar-refinement tools.

Those responsibilities belong to the external GF development/validation ecosystem.
SemantiK Architect consumes only the resulting runtime contract, primarily
`runtime/semantik_architect.pgf` plus runtime data required by its semantic and lexical layers.

## Runtime

Place the compiled grammar at:

```text
runtime/semantik_architect.pgf
```

or set `PGF_PATH` to another `.pgf` file.

Check the runtime:

```bash
python manage.py doctor
```

Start the API:

```bash
python manage.py serve --reload
```

The central generation path remains:

```text
semantic frame -> planning -> lexical resolution -> GF/PGF realization -> surface text
```

See `docs/RUNTIME_BOUNDARY.md` for the migration boundary.

## Request sessions

`X-Session-ID` discourse context is process-local and ephemeral. It no longer
requires Redis. For horizontally scaled deployments, treat session affinity or
an external session service as a deployment concern rather than a grammar-build
dependency of SemantiK Architect.

