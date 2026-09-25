# ADR-0003 — Canonical semantic graph plus explicit obligations

Status: **accepted**

## Context

Key/value SemanticItem models leak domains and blur support metadata with must-say content.

## Decision

Use a typed structural SemanticGraph with extensible predicate/role vocabulary plus a separate CommunicationObligation set and supporting context.

## Consequences

Core remains domain-neutral and scalable while retaining explicit coverage.
