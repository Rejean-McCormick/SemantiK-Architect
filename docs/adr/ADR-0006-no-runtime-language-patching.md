# ADR-0006 — No runtime language patching or hidden fallback

Status: **accepted**

## Context

Fallback renderers hide underdeveloped grammar and produce false success.

## Decision

Only released language/profile artifacts may serve production. Grammar gaps are fixed in the GF language repository and revalidated.

## Consequences

Failures are explicit; no family-engine/safe-mode duplicate grammar.
