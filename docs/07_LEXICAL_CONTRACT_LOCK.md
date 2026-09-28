# Lexical Contract Lock

Status: **LOCKED / normative**

## Why lexical resolution has two phases

Construction choice can depend on lexical properties such as valency, governed complements, grammatical class, classifier behavior or available senses. Therefore lexical information cannot be postponed entirely until after language planning.

## Phase A — Lexical Knowledge Preflight

Before final target-language planning, SA may request language-specific lexical knowledge for semantic concepts/entities.

The preflight result may include:

- candidate lexical sense IDs;
- part-of-speech/category information;
- valency/argument-frame metadata;
- grammatical gender/noun class where lexically inherent;
- governed adposition/case/complement information;
- countability/classifier metadata;
- register/domain terminology tags;
- whether a required lexicalization is available in the selected runtime set.

Preflight metadata informs planning. It does not inflect words.

## Phase B — Lexical Binding

After the `LanguagePlan` selects operations, the binder selects exact runtime lexical references compatible with those operations.

Bindings MUST be versioned and traceable to the lexical artifact identity.

## Lexical sources and authority

SA separates **lexical knowledge** from **grammatical realization**.

- local Wikidata/Wikidata Lexeme mirrors are the default generic lexical knowledge authority;
- project-owned lexicons and terminology/domain packs may explicitly override generic Wikidata lexicalization;
- Kristal-derived semantic/lexical projections may provide admitted project/domain knowledge;
- GF dictionaries are generic realization/binding fallback and MUST NOT become a competing semantic authority;
- GF/RGL remains the authority for grammar, morphology, agreement and language-specific realization.

No live service is mandatory.

## Canonical identity

The core uses namespace-qualified semantic/lexical references. Wikimedia QIDs/Lexeme IDs are valid references but are not the only permitted identity system.

## Precedence policy

Lexical precedence MUST be explicit and versioned. The default canonical policy is:

```text
request terminology override
  > active domain terminology pack
  > admitted project lexicon
  > admitted Wikidata/Lexeme projection
  > admitted generic GF lexicon
```

A RuntimeSet MAY replace this ordering only with an explicit versioned `lexical_policy`. Artifact iteration order never has semantic meaning. Equal-precedence conflicts fail closed.

Knowledge and binding are resolved independently: a Wikidata Lexeme may supply the selected sense/category while a GF lexical artifact supplies the executable `gf_expr` for the same semantic reference.

## Failure

If a required concept cannot be lexicalized for the requested released profile, generation fails with a lexical error. SA does not invent an approximate synonym or switch language silently.

## Runtime AI

Probabilistic lexical guessing is not part of the deterministic canonical runtime. AI may assist lexicon development and review outside the production path.
