# ADR-0006 — Ephemeral in-process session state

Status: **Accepted**  
Date: 2026-09-18

## Context

Discourse-sensitive generation can benefit from short-lived context, while the application does not require a distributed broker or durable conversation database for its runtime contract.

## Decision

Optional session/discourse state is bounded, TTL-based, in-process, and ephemeral.

## Consequences

- no Redis requirement for normal runtime state;
- no cross-process state guarantee;
- context may influence planning/reference choice;
- durable conversational state requires a separate future contract.
