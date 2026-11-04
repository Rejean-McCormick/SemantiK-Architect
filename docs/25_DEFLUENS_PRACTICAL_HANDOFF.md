# Ars Magna Defluens 15-capability practical pilot: SA compatibility

GF WordBench produces a read-only **development** handoff of the 14-language /
15-intent GF probes. Run `PYTHONPATH=src python tools/inspect_defluens_handoff.py
/path/to/semantik_handoff.json` for the exact SA v1 operation registry check.

This inspection **does not** turn isolated GF probes into `CommunicationRequest`
conformance; it never emits `grammar.pgf`, bridge variants, lexical artifacts,
profiles, release evidence or `RELEASED` state.

Existing mappings to `clause.copular_attribute`, `clause.intransitive_event`,
`clause.transitive_event`, `clause.locative` and `directive.action` are *candidates*,
not assertions that a bridge variant consumes every feature and lexical slot.
The conditions and source-attribution intents need explicit versioned contract
analysis. Semantic fidelity and time/modality/negation preservation must be
verified by the existing `CandidateMatrixConformance` / release harness.

**Ownership:** WordBench builds GF language implementations; SemantiK Architect
owns canonical semantic planning and SA↔GF; SemantiK Runtime Orchestrator
owns promotion/rollback; Defluens is an external UI/coordination client.

To prove the first real vertical slice, build a PGF for one language in
WordBench, package an immutable SA candidate (PGF + bridge + lexicon + profile
+ suite + lock), run SemantiK candidate conformance, and then use the normal
release controller. Never publish a practical-probe ZIP directly.
