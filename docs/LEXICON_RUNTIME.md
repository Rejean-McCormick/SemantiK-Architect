# Lexicon Runtime

Status: **normative**

## Role

The lexicon is a runtime subsystem that supports lexical resolution between planning and realization.

```text
PlannedSentence / ConstructionPlan
    -> lexical resolution
    -> renderer-ready lexical material
```

It does not define language capability and it is not a grammar-development maturity system.

## Runtime responsibilities

Lexical resolution may provide:

- lemma/surface selection;
- language-specific forms;
- grammatical features;
- entity labels;
- lexical references such as `LexemeRef`;
- entity references such as `EntityRef`;
- renderer-safe surface hints;
- provenance/debug metadata where useful.

The semantic slot identity must remain visible through lexical resolution.

## Plan integrity

`ConstructionPlan.slot_map` is for constructional/semantic slots. Control envelopes and bookkeeping keys must not be injected as pseudo-slots.

Canonical reference/value objects must remain recognizable as such through plan freezing/normalization; they must not be accidentally converted into unrelated mapping-proxy shapes.

## Runtime data

Runtime lexical data may be stored under:

```text
data/lexicon/
```

and language/concrete mapping under runtime configuration such as:

```text
data/config/iso_to_wiki.json
```

Exact storage layout is an implementation detail; the contract is the lexical-resolution behavior.

## Language scope

Lexicon validation must be scoped to languages that the deployed runtime actually exposes. Tests must not fail because lexicon data is absent for languages that are not present in the loaded PGF.

## Out of scope

The runtime lexicon subsystem does not own:

- grammar maturity scoring;
- language-development readiness matrices;
- AI lexicon authoring agents;
- GF/RGL source generation;
- bulk language onboarding pipelines.

Those are development/data-production concerns outside the runtime boundary.
