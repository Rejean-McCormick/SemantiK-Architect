# Conceptual Positioning

Status: **reference / non-normative**

This document explains the ideas that inform SemantiK Architect. It does not override the runtime, API, or domain contracts.

## What kind of system this is

SemantiK Architect is a practical multilingual NLG runtime that separates semantic intent, planning, lexical choice, and realization.

Its conceptual pipeline is:

```text
semantic input
  -> canonical frame
  -> planning / construction choice
  -> lexical resolution
  -> realization
  -> surface result
```

## Relation to Grammatical Framework

SemantiK shares GF's useful separation between abstract intent and language-specific realization, but SemantiK's internal semantic/planning contract is not a GF AST.

GF participates as a runtime realization backend through PGF. Grammar engineering itself remains outside SemantiK.

## Relation to construction grammar

The runtime treats recurrent structural patterns as constructions. The planner selects a construction; the renderer realizes it in a language/backend.

This helps separate:

- semantic roles;
- information packaging;
- construction choice;
- lexical material;
- morphology and word order.

## Relation to frame semantics

Frames provide structured semantic input that is distinct from wording. `frame_type` makes the intended semantic family explicit before realization.

## Relation to Ninai / Abstract Wikipedia

Function-style abstract representations such as Ninai can serve as an external semantic notation. The adapter boundary allows those structures to be normalized into SemantiK frames without making the external notation the internal runtime architecture.

This supports structured-content and Abstract-Wikipedia-like workflows while preserving a stable runtime contract.

## Relation to multilingual NLG

SemantiK aims to share semantics, planning, construction identifiers, lexical contracts, and renderer interfaces across languages while allowing language-specific realization behavior where required.

Runtime support remains evidence-based: a language is supported only when deployed artifacts/data and tests demonstrate it.
