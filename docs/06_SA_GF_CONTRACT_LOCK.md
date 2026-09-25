# SA ↔ GF Contract Lock

Status: **LOCKED / normative**

## Purpose

The SA↔GF contract is the stable ABI-like boundary between semantic/language planning and grammatical realization. It prevents SA from becoming coupled to arbitrary RGL internals and prevents each language from requiring bespoke Python logic.

## Principle

SA targets a **versioned bridge contract**, not arbitrary GF ASTs.

GF/RGL remains the authority for grammar. The bridge contract is deliberately thin: it specifies the grammatical operations SA needs to request, while the GF language implementation decides how those operations are realized naturally.

## Contract components

A contract release contains:

1. `contract_version`;
2. operation catalog;
3. required semantic roles for each operation;
4. feature schema for each operation;
5. lexical binding requirements;
6. GF abstract bridge grammar identity;
7. expected result category per operation;
8. conformance vectors and error expectations.

## Operation IDs

Operation IDs are stable, namespaced and versioned. Baseline families include:

```text
clause.intransitive_event
clause.transitive_event
clause.ditransitive_event
clause.copular_classification
clause.copular_attribute
clause.existential
clause.locative
clause.possession
clause.passive_event
question.polar
question.content
directive.action
coordination.clause
relative.subject
relative.object
nominal.apposition
comparison.comparative
comparison.superlative
```

This catalog is extensible. An operation is not considered usable merely because a GF function with a similar name exists; it must be admitted by the SA↔GF contract and conformance profile.

## Language implementation

A target language runtime MUST provide a concrete implementation compatible with the bridge abstract grammar/contract version.

The implementation MAY use:

- standard RGL constructors;
- language-specific RGL extensions;
- legitimate language-specific structures;
- language-owned lexical resources.

It MUST NOT require SA core to know how the language implements the construction.

## Contract compatibility

Semantic versioning rules:

- patch: clarifications/test additions that do not change operation meaning or wire shape;
- minor: additive operations/features with old behavior preserved;
- major: changed operation semantics, removed operations, incompatible feature/role changes.

A runtime artifact MUST declare the exact compatible contract range/version. SA MUST reject incompatible combinations before realization.

## Core dependency rule

Only the GF adapter may import/use PGF runtime APIs. Domain and application code exchange realizer-neutral values and operation IDs.

## Failure behavior

If an operation required by a released capability profile is absent or fails for a language, the request fails. SA MUST NOT substitute a different unvalidated construction solely to hide a grammar gap.

During language development, that failure becomes actionable evidence for the GF language repository.

## No duplicate grammar

The new SA repository MUST NOT contain a parallel Romance/Germanic/Slavic/etc. grammar implementation, emergency templates or safe-mode morphology.

## Presentation boundary

GF realizes linguistic units. List numbering, Markdown bullets, UI cards and other transport/presentation formatting are output-adapter concerns unless a language-specific utterance itself requires grammatical realization.

## Bridge-spec artifact enforcement

The executable v1 adapter format is defined in `reference/GF_BRIDGE_SPEC.md` and schema `schemas/gf_bridge_spec.schema.json`. A successful bridge variant must consume every semantic lexical slot and every communicatively relevant feature of the `RealizationUnit`; unused semantic inputs are a contract failure, not a warning.

The v1 operation registry includes non-factual `discourse.greeting` and `discourse.closing` operations for required bounded framing. They carry no domain claim and do not discharge business obligations.
