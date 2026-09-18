# Language Capabilities

Status: **normative for capability discovery; current concrete list is observational**

## Source of truth

Runtime language capability comes from the **concrete languages present in the loaded PGF**.

The following do not create runtime language capability by themselves:

- a lexicon directory;
- a language card;
- an ISO mapping entry;
- a development readiness score;
- a historical list of target languages.

## Capability derivation

```text
loaded PGF
  -> concrete language names
  -> application language mapping
  -> public /api/v1/languages capability view
```

Optional `runtime/languages.json` may provide display metadata. It must not advertise a language that the loaded runtime cannot realize.

## Current validated snapshot

As of 2026-09-18, the validated runtime PGF exposes:

| PGF concrete | Application code |
| --- | --- |
| `WikiEng` | `en` |
| `WikiFre` | `fr` |

This table describes the current artifact. It is not a permanent two-language architecture rule.

## Adding a runtime language

A new language becomes available only after all runtime requirements are satisfied:

1. the external GF ecosystem produces a PGF containing the required concrete language, if that language uses the GF backend;
2. the artifact is deployed to SemantiK;
3. application/concrete-language mapping is present;
4. required runtime lexical data is present;
5. relevant constructions are realizable;
6. regression tests pass for the new capability.

SemantiK itself does not compile the grammar as part of language onboarding.

## Public behavior

A request for an unavailable language is rejected as a capability/language error. The runtime must not silently substitute another language.

A route resolving `fr` to `WikiFre` but returning English text is a failure, not partial success.
