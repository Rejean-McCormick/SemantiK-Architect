# SemantiK Architect — Kristal v6 migration

Date: 2026-10-01

## Decision

SemantiK Architect 1.2.0 keeps `CommunicationRequest` schema `1.0` as its canonical domain input and adds an explicit boundary contract:

`semantik.kristal-v6.communication-projection/1.0`

This avoids coupling the core language architecture to the full Kristal State schema.

## Mapping rule

```text
Kristal State 6.0
  ↓ explicit assertion selection + semantic mapping by owner/Da’at
Kristal v6 communication projection
  ↓ traceability/non-inference validation
KristalV6Acl
  ↓
CommunicationRequest 1.0
  ↓
existing SemantiK pipeline
```

## Preserved metadata

The ACL may preserve selected assertion `record_role`, `valuations[]`, `applicability`, and `actionability` in `supporting_context` under `kristal-v6:*` property refs.

## Hard boundaries

- a high valuation does not create an obligation;
- `actionability=automatic` does not create a directive;
- `human_review`/`human_decision` do not automatically become questions or commands;
- every selected assertion must remain source-traceable;
- SemantiK never mutates Kristal or the operational owner;
- GF language-development source remains outside SemantiK Architect.
