# Language Planning Lock

Status: **LOCKED / normative**

## Goal

Language planning converts a language-neutral `CommunicationPlan` into a target-specific `LanguagePlan` without assuming that all languages express the same semantic relation with the same construction.

## No English pivot

SA MUST NOT plan through English as an intermediate representation.

```text
semantic meaning -> English sentence -> translate
```

is not the canonical design.

The canonical design is:

```text
semantic meaning -> target-language planning -> GF target language
```

## Language-specific construction is legitimate

Two fully developed languages may realize the same semantics through different grammatical strategies. That is not a patch.

Therefore the language planner may choose different SA↔GF operation variants, segmentation, argument packaging, politeness realization or information structure while preserving obligation semantics.

## What the language planner owns

- final block topology for the target language;
- sentence/utterance segmentation;
- speech-act realization;
- register and politeness realization;
- construction operation choice;
- information structure where supported;
- explicit/implicit argument realization only where semantic recoverability and contract rules allow it;
- anaphora/pronominalization when referential identity is preserved;
- lexical sense/candidate selection in cooperation with lexical services.

## What it does not own

- morphology tables;
- conjugation/declension implementation;
- language-specific low-level agreement algorithms already in GF/RGL;
- task/business policy;
- truth or relevance filtering;
- runtime grammar repair.

## Block topology

The v1 block kinds are:

- `utterance`;
- `question`;
- `list`;
- `label_value`;
- `notice`;
- `heading` (optional presentation block, no domain claim by itself).

New block kinds require a schema-compatible extension or major contract change. Output adapters may project these blocks to text/Markdown/HTML without altering semantic content.

## Register model

Register is input context plus language-specific realization. The core recognizes abstract dimensions, not hardcoded strings for every language:

- formality;
- politeness;
- directness;
- institutional/operational/conversational register;
- speaker/recipient relationship;
- channel constraints.

Each language profile declares which distinctions it can faithfully realize.

## No language-specific branches in core

Forbidden in shared planning/application code:

```python
if language == "sq": ...
elif language == "fr": ...
```

Language differences belong in:

- versioned language profile data;
- lexical resources;
- GF concrete grammars/bridge implementation;
- explicitly registered language-planning strategies behind a stable interface only when generic metadata cannot express the distinction.

Any language-specific planner strategy requires a declared capability and conformance tests; it is not an ad hoc exception.
