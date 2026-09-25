# Faithfulness and Determinism Lock

Status: **LOCKED / normative**

## Correctness model

Faithfulness is a hard correctness property, not a style preference.

### F1 — No invention

Every output domain claim must be supported by submitted semantic content or an explicitly declared deterministic derivation. Conventional non-factual discourse material is exempt only under the rules below.

### F2 — Obligation completeness

Every communication obligation must be mapped to output coverage. If any obligation remains undischargeable, the request fails.

### F3 — Role preservation

Agent/patient/recipient/location/time/quantity and other semantic roles must not be swapped or silently changed by lexical/construction choice.

### F4 — Polarity/modality preservation

Negation, uncertainty, hypotheticality, obligation, permission and other communicatively relevant modality must remain intact.

### F5 — Identity preservation

Entity identity, identifiers, names, references and numbers must not be silently substituted.

### F6 — No status elevation

Disputed/uncertain/hypothetical material designated for explicit communication must not be phrased as unqualified fact.

### F7 — Deterministic derivations only

Derived statements must be deterministic, declared and traceable to request semantics.

### F8 — Presentation is not authority

Natural wording never changes the authority or truth status of upstream data.

## Coverage model

The successful result records at least:

```text
obligation_id -> block_id -> realization_unit_id(s)
```

Development/diagnostic mode MAY add token/span mappings. The coverage map is a QA/debugging artifact, not a new truth ledger.

## Conventional discourse material

Authorized additions include greetings, politeness markers, transitions, list introductions and closings when enabled by profile/context. They must not create domain facts.

## Deterministic identity

For identical:

- canonical request semantic content;
- presentation/profile versions;
- SA application version;
- RuntimeSet identity;
- SA↔GF contract version;

SA MUST produce the same deterministic structured result. Request timestamps, trace IDs and measured latency are excluded from the deterministic content identity.

## Runtime AI policy

LLMs/probabilistic models are not required in the canonical production path. AI may be used heavily to develop languages, lexicons, tests, mappings and documentation. Any future probabilistic realizer/planner is a distinct explicit experimental adapter/profile and never silently replaces the deterministic path.
