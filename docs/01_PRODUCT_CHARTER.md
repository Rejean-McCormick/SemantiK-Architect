# Product Charter

Status: **normative product boundary**

## Product definition

SemantiK Architect transforms **structured semantic information selected by an upstream authority** into faithful, context-appropriate, multilingual human communication.

Its unit of work is a bounded **communication**, not necessarily one sentence. A communication may contain a greeting, one or more utterances, a question, a list, labels, notices or other bounded blocks.

## Core use cases

### Orgo operational communication

An upstream system may supply:

```text
recipient: Marcel
four ordered tasks
deadline and machine for each task
ordering policy: hardest first
technical contact: Gabriel
```

SA may produce:

```text
Bonjour Marcel. Ce matin, tu as quatre tâches à réaliser.
Je les ai classées par difficulté, la plus difficile en premier.

1. ...
2. ...
3. ...
4. ...

Gabriel est disponible si tu as besoin d'aide.
```

The task set, ordering policy, deadlines and contact are upstream facts/policies. The greeting, segmentation and list presentation are SA articulation decisions.

### eThikos structured thought articulation

A person may build a graph of concepts, propositions and relations. SA renders that structure in natural language so the person can confirm: “Is this what I mean?” SA does not choose the ethical position.

### Semantic translation

Raw source text is formalized upstream (for example by SenTient/Kristal). SA then re-realizes the resulting semantics in another language. SA is therefore not a canonical string-to-string machine translation engine.

## In scope

- faithful semantic-to-communication planning;
- bounded multi-block communication;
- audience, register, formality, politeness, tone and channel adaptation;
- target-language construction selection;
- lexical orchestration;
- deterministic GF realization;
- lists and short presentation structures;
- language/profile capability checks;
- coverage and diagnostics;
- offline deployment.

## Out of scope

- truth determination or claim validation;
- selecting which obligations to omit;
- workflow decisions or task ordering not supplied upstream;
- recommendation ranking;
- raw-text NLP as the canonical ingress;
- article/chapter/long-form editorial planning;
- internal morphology/syntax engines duplicating GF;
- runtime language patching;
- mandatory live external services.

## Decision test

A feature likely belongs in SA if it answers:

> “How should all of this supplied meaning be communicated to this audience in this target language?”

A feature does not belong in SA core if it answers:

> “What is true?”, “What should happen?”, “Which fact is important?”, or “Which supplied fact may be dropped?”
