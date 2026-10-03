# Kristal v6 Communication Projection

Status: **normative boundary contract**

Contract: `semantik.kristal-v6.communication-projection/1.0`  
Portable Kristal baseline: Standard `6.0.0` (`kristal_state/6.0`)  
Kristal/Kristall design baseline: `7.0.0-draft.3.2`  
SemantiK canonical request: `CommunicationRequest` schema `1.0`

## Purpose

Kristal v6 can preserve several kinds of records and measurements in one `kristal_state`. That does not imply that every assertion should be verbalized. SemantiK Architect therefore consumes an explicit communication projection rather than a raw state.

```text
Kristal State
  assertions + valuations + roles + actionability
        ↓ explicit upstream communication selection/projection
semantik.kristal-v6.communication-projection/1.0
        ↓ KristalV6Acl (traceability validation)
CommunicationRequest v1.0
        ↓ existing SA pipeline
CommunicationResult
```

## Required projection fields

- `kristal_standard = 6.0.0`;
- `state_ref` identifying one `kristal_state` and its status/applicability/hash when available;
- `selected_assertions[]` carrying the Kristal assertion IDs and optional `record_role`, `valuations[]`, `applicability`, `actionability`;
- one fully mapped canonical `communication_request`.

Every selected assertion ID MUST appear in at least one statement or obligation `source_refs` in the mapped request. This makes the communication projection auditable without forcing SA core to understand the complete Kristal State schema.

## Non-inference rule

The following are never communication obligations by themselves:

- `record_role = authoritative_constraint`;
- `record_role = decision`;
- a `high`/`established` valuation;
- `actionability.mode = automatic`;
- `actionability.mode = human_review` or `human_decision`.

An upstream mapping decides whether the underlying assertion must be communicated and assigns the communicative force (`ASSERT`, `ASK`, `DIRECT`, `PRESENT`). The ACL verifies and preserves; it does not make that semantic decision.

## Metadata preservation

Selected assertion metadata is appended to `CommunicationRequest.supporting_context` under `kristal-v6:*` property refs. This allows language/planning profiles to use explicitly supported distinctions later without leaking Kristal field names into generic domain classes.

## Authority

Kristal/Kristall owns the knowledge artifact and semantic identity. The explicit upstream communication projection owns selection/communicative force. DaaT may transport/map an admitted contract but does not choose obligations. SemantiK Architect owns articulation. A communication result does not mutate Kristal/Kristall or operational owner state.

## Kristall v7

Kristall `7.0.0-draft.3.2` is additive above portable v6. A v7 pipeline may produce or reference a v6-compatible projection for SA; the ACL contract above remains unchanged.
