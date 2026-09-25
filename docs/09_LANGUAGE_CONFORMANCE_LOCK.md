# Language Conformance Lock

Status: **LOCKED / normative**

## Principle

SA supports **released capability profiles**, not nominal language codes and not partially working languages disguised by fallbacks.

A language/profile pair is binary at runtime:

```text
RELEASED -> callable
not RELEASED -> unavailable
```

## Relationship to GF language completeness

GF language development occurs outside SA. A language may be broadly mature in GF, but SA runtime support is granted only after the exact SA↔GF contract/profile workload passes conformance.

This is not permission to support underdeveloped languages. It is a precise release gate for the subset of capabilities SA promises.

## Capability profiles

Profiles are versioned workload contracts, for example:

```text
sa-core-1
orgo-operational-1
ethikos-dialogue-1
keenkonnect-system-1
```

A profile declares:

- required SA↔GF operations;
- required register/politeness distinctions;
- required lexical classes;
- required block/communication functions;
- semantic faithfulness vectors;
- formatting/locale requirements;
- failure behavior.

Profiles MAY extend other profiles.

## Baseline conformance dimensions

The core profile should cover, as applicable:

- declarative positive/negative clauses;
- intransitive/transitive/ditransitive events;
- copular attribution/classification;
- existence, location, possession;
- polar/content questions;
- directives;
- coordination;
- required relative constructions;
- temporal expressions and deadlines;
- quantities/numerals;
- names/identifiers/technical references;
- agreement features relevant to the language;
- address/vocative and formality distinctions required by the profile;
- list-item/short-fragment realization;
- semantic role, polarity, modality, time and quantity preservation.

## Release gates

A language/profile becomes `RELEASED` only when:

1. external GF language build succeeds;
2. immutable grammar artifact is produced;
3. bridge contract compatibility is verified;
4. required lexical artifacts are present;
5. profile conformance suite passes completely;
6. golden/regression tests pass;
7. property/metamorphic faithfulness tests pass;
8. failure-path tests pass;
9. runtime integrity/readiness checks pass;
10. immutable evidence is signed/recorded in the release manifest.

There is no “mostly released” state.

## Development status values

Allowed lifecycle states:

```text
DEVELOPMENT
CANDIDATE
RELEASED
RETIRED
```

Only `RELEASED` is callable by production policy.

## Extensions

A mature language MAY expose extra legitimate capabilities beyond shared profiles. These are named/versioned extension capabilities. Shared application code MUST NOT require a language-specific extension unless the product explicitly opts into it.

## Scale rule

Adding a released language SHOULD require only:

```text
new validated GF artifact
+ lexical/locale artifacts
+ capability manifest entry
+ conformance evidence
```

It MUST NOT require modifying shared domain/application logic.
