# ADR-0013 — Wikidata Lexemes as primary generic lexical authority

Status: **accepted**

## Context

SA needs a large multilingual dictionary without making the grammar engine the owner of semantic identity. GF/RGL is strong at grammar, morphology and realization, while Wikidata Lexemes provides language-neutral links between lexical senses and Wikidata concepts.

## Decision

1. Local Wikidata/Wikidata Lexeme projections are the default **generic lexical knowledge authority**.
2. GF/RGL remains the **grammar and morphology authority**.
3. Generic GF lexicons are realization/binding fallback, not the canonical semantic dictionary.
4. Domain and project terminology may override generic Wikidata lexicalization explicitly.
5. Runtime precedence is explicit and deterministic: `request_override > domain > project > wikidata > gf_generic`.
6. Lexical knowledge resolution and executable GF binding are separate. A Wikidata sense may win knowledge resolution while a GF entry supplies the executable `gf_expr` for the same semantic reference.
7. Equal-precedence conflicts fail closed; artifact iteration order never decides meaning.
8. Canonical runtime remains offline-first. Live Wikimedia services are not required.

## Consequences

Semantic identity survives changes to the grammatical engine, GF does not become a competing ontology, multilingual lexical coverage can scale from local Wikidata mirrors, and runtime realization remains deterministic and validated.
