# Typed French attribute candidate — canonical SA/GF operation (v0.7)

This is a **development-only** addition under `profiles/defluens-attribute-fr-1/`. No SA core planner, realizer, conformance gate or RuntimeSet release contract is modified.

- Existing operation: `clause.copular_attribute`
- Roles: `entity`, `attribute`
- Semantic features: statement `polarity`, typed literal qualifier `qualifier.tense` (present/past/future)
- Exact bridge: `RealizeAttribute {entity} {attribute} {feature.polarity} {feature.qualifier.tense}`
- RGL French `SyntaxFre` and `ParadigmsFre` perform final tense, polarity, copula and agreement.
- The bounded `defluens-attribute-request` CLI is a user-input mapper to canonical `CommunicationRequest`, *not* a second semantic planner or a text generator.
- Candidate frontend uses the public `preview-candidate` CLI and the locked hash-checked `CandidateConformance` path.

The role/polarity/time slots are all consumed by the bridge; unrelated register metadata is explicitly declared as consumed for this narrow candidate. Unsupported lexical references must fail. The suite verifies only development expressions; it does not issue linguistic gold or runtime activation.
