# SemantiK Architect v1.1 — lexical authority refinement

- Makes local Wikidata Lexeme projections the default generic lexical knowledge authority.
- Keeps GF/RGL as grammar/morphology authority and generic GF lexicons as realization fallback.
- Implements explicit deterministic lexical precedence: override > domain > project > Wikidata > GF generic.
- Resolves lexical knowledge separately from executable bindings.
- Fails closed on equal-precedence lexical conflicts instead of depending on artifact order.
- Carries source/sense provenance through preflight and binding.
- Adds real P5137 sense→Q extraction and a local Wikidata lexical-artifact builder.

## 1.1.1 — 2026-09-28

- Added generic lexical planning metadata (`preferred_operation`, role/slot/feature maps, independent statement realization).
- Added `konstellation-explorer-2`, an additive profile using normal SA operations instead of serialized statement JSON.
- Preserved `konstellation-explorer-1` unchanged for compatibility.
- Added deterministic collection and structured-literal surface formatting used by lexical binding.
