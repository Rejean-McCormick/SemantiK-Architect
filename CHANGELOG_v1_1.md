# SemantiK Architect v1.1 — lexical authority refinement

- Makes local Wikidata Lexeme projections the default generic lexical knowledge authority.
- Keeps GF/RGL as grammar/morphology authority and generic GF lexicons as realization fallback.
- Implements explicit deterministic lexical precedence: override > domain > project > Wikidata > GF generic.
- Resolves lexical knowledge separately from executable bindings.
- Fails closed on equal-precedence lexical conflicts instead of depending on artifact order.
- Carries source/sense provenance through preflight and binding.
- Adds real P5137 sense→Q extraction and a local Wikidata lexical-artifact builder.
