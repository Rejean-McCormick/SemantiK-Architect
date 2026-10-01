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

The supplied GF grammar is deliberately conservative: it structures French evidence presentation without inventing propositions beyond the request. Richer RGL realization can evolve behind the same SA operation/lexical contracts.

Les sources GF/RGL sont maintenues hors de SemantiK Architect dans GF/Wordbench. Ce dossier ne porte que les contrats/artefacts nécessaires à la conformance SA.
