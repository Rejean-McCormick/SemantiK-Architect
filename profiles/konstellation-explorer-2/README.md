# Konstellation Explorer profile 2

Candidate French profile for structured Konstellation communication through SemantiK Architect.

Profile 2 replaces the profile-1 canonical-JSON display strategy with SA-native language planning:

- Konstellation still supplies only `CommunicationRequest` semantics and obligations;
- SA validates the Konstellation vocabulary and keeps every statement/obligation;
- lexical artifact metadata maps predicate roles to existing SA↔GF v1 operations;
- the generic SA planner consumes those mappings; no Konstellation-specific language planner is required;
- GF receives typed realization slots rather than a serialized `SemanticStatement`;
- complex literal values remain deterministic and traceable;
- no source, qualifier, epistemic status or coverage obligation may disappear silently.

`konstellation-explorer-1` remains immutable and compatible for canonical evidence display. This profile is additive and must be released as a distinct RuntimeSet, conventionally `konstellation-fr-2`.

The corresponding GF grammar is maintained and released from GF/Wordbench. This profile carries only SA-side planning, bridge, lexical and conformance artifacts; richer RGL realization can evolve behind the same contracts without moving grammar-source authority into SA.
