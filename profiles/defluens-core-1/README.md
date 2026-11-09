# Defluens Core v0.8 — six semantic families, two candidate languages

This **candidate-only** extension uses SemantiK Architect's canonical CommunicationRequest → planning → lexical binding → versioned SA↔GF bridge → GF pipeline. WordBench compiles and hashes its source and PGF; Defluens is a thin UI client.

Six **existing** SA operation IDs: `clause.copular_attribute`, `clause.copular_classification`, `clause.intransitive_event`, `clause.transitive_event`, `clause.locative`, `directive.action`.

Two language concretes (RGL French/English), bounded input vocabulary, 1–8 ordered statements per request. Polarity and tense exposed where the operation supports them. Each language has an independent immutable candidate bundle and cannot be called as `RELEASED`.

This is **not** 15 SA-integrated intentions or 14 qualified languages: the other 14×15 WordBench probes remain separate GF evidence. Conditional attribution, numeric phenomena and broader lexical realization are future extensions. No literal prose templates, no token interpolation from user text, no runtime grammar modification, no semantic-selection or truth assertions are introduced here.

The SA CLI `defluens-core-catalog` returns bounded options. `defluens-core-request -` takes a JSON recipe on stdin and emits the canonical request. `preview-candidate` then realizes the candidate using an exact PGF built on GF 3.12 by WordBench.

Source: `DefluensCore.gf`, `DefluensCoreFre.gf`, `DefluensCoreEng.gf`. French and English use official RGL Syntax/Paradigms modules. The French/English PGFs must be compiled on the user's Windows installation. The GF source compiles have not been verified in this environment.

GF French v0.11.2: `DefluensCoreFre.gf` lowers `S` to `Utt` before reading `.s` and explicitly qualifies `ParadigmsFre.mkAdv`; see `../../docs/reference/DEFLUENS_GF_FRENCH_MOOD_FIX_v0112.md`. This is a source-level fix pending Windows GF recompilation.
