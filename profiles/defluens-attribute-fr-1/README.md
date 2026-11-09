# Defluens typed French attribute candidate — v0.7

**Development candidate only.** SemantiK Architect owns the canonical communication pipeline; the new CLI mapper only converts four explicit selections into a structured `CommunicationRequest`.

- Subjects: Mira (f), Léa (f), Noa (m)
- Attributes: ready, calm, absent, available
- Polarity: positive/negative
- Tense: present/past/future (RGL French constructions; past tense meaning depends on the RGL tense strategy)
- **72** potential combinations; vocabulary is bounded and must be extended by explicit GF + lexical artifacts, not arbitrary string interpolation.
- Grammar uses SyntaxFre / ParadigmsFre for French predication, agreement, negative polarity, and tense.
- Existing canonical SA op: `clause.copular_attribute`; the bridge consumes *all* entity, attribute and tense/polarity features.
- No GF code or morphology in the Defluens console; candidate build by WordBench; preview by SA's public `preview-candidate` command.

The RGL French PGF must be compiled on Windows GF 3.12. No release or linguistic certification is implied. Existing Konstellation-3 profile remains unchanged.

GF French v0.11.2: the `mkS` / `Output.s` type mismatch is addressed by `mkUtt (mkS ...)` before taking `.s`. Source-level regression tests pass; Windows GF compilation is not yet verified.
