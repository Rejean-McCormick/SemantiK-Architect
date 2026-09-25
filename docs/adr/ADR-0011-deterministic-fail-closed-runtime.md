# ADR-0011 — Deterministic fail-closed production runtime

Status: **accepted**

## Context

Wrong meaning/language is more damaging than explicit failure.

## Decision

Canonical runtime is deterministic and fails closed on semantic/language/runtime correctness errors; graceful degradation is auxiliary-only.

## Consequences

Reproducible, auditable behavior; fewer hidden surprises.
