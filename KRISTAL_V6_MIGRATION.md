# SemantiK Architect — Kristal v6 migration

Date: 2026-10-01

## Decision

SemantiK Architect 1.2.0 introduced and 1.3.0-alpha.2 retains `CommunicationRequest` schema `1.0` as its canonical domain input and adds an explicit boundary contract:

`semantik.kristal-v6.communication-projection/1.0`

This avoids coupling the core language architecture to the full Kristal State schema.

## Mapping rule

```text
Kristal State 6.0
  ↓ explicit communication selection/projection by upstream semantic authority
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

## Current v7 alignment

Kristal/Kristall `7.0.0-draft.3.2` is additive above `kristal_state/6.0`, so this migration remains the active portable SA boundary. DaaT (`daat`) may map admitted external contracts toward Kristal but does not own communication selection.
