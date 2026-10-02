# Informath Mathematical Realization

Status: **candidate integration**

## Responsibility

SemantiK Architect does not implement a second mathematical natural-language grammar. Mathematical `RealizationUnit`s are delegated to Informath, whose MathCore/Informath grammars and GF/RGL concrete syntaxes own the linguistic realization.

```text
Formula IR
  ↓ MathKristal ACL
CommunicationRequest
  ↓ math language planner
math.informalize_formula
  ↓ structural encoder
Dedukti fragment + versioned symbol table
  ↓ Informath
MathCore / Informath
  ↓ GF/RGL
human language
```

## Runtime artifacts

A released math RuntimeSet MUST pin, hash and validate:

- one `informath-config*` artifact;
- one `math-symbol-registry*` artifact;
- the capability profile;
- conformance evidence for every released language/profile.

The config maps BCP-47/SA language codes to Informath concrete codes and declares separate argument sets for `PURE` and `NATURAL` modes.

## Symbol registry

The symbol registry maps stable MathKristal semantic references to:

- a Dedukti identifier;
- an explicit Dedukti declaration;
- an Informath/GF symbol-table mapping;
- optional Wikidata, OpenMath and MMT alignment identifiers.

Unmapped symbols fail closed. Wikidata Lexemes remain generic lexical knowledge; the symbol registry carries the grammatical/function mapping needed to make a formal math identifier realizable by Informath.

## No fallback

If Informath is missing, returns an error/empty result, lacks the target language, or cannot map a Formula IR symbol, SemantiK returns a stable math error. It does not use emergency templates.
