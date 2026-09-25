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

## Lexical sources

Adapters may draw from:

- local Wikidata/Wikidata Lexeme mirrors;
- Kristal-derived semantic/lexical projections;
- GF dictionaries;
- project-owned lexicons;
- terminology packs;
- domain dictionaries.

No live service is mandatory.

## Canonical identity

The core uses namespace-qualified semantic/lexical references. Wikimedia QIDs/Lexeme IDs are valid references but are not the only permitted identity system.

## Precedence policy

Lexical precedence MUST be explicit and versioned. A recommended policy shape is:

```text
request terminology override
  > active domain terminology pack
  > admitted project lexicon
  > admitted Wikidata/Lexeme projection
  > admitted generic GF lexicon
```

The actual precedence is configuration/profile data, never hidden adapter order.

## Failure

If a required concept cannot be lexicalized for the requested released profile, generation fails with a lexical error. SA does not invent an approximate synonym or switch language silently.

## Runtime AI

Probabilistic lexical guessing is not part of the deterministic canonical runtime. AI may assist lexicon development and review outside the production path.
