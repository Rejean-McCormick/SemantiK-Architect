# ADR-0005 — Versioned SA↔GF bridge contract

Status: **accepted**

## Context

Direct coupling to arbitrary GF/RGL AST details would create unstable per-language integration.

## Decision

SA targets a thin versioned operation catalog/bridge grammar; only the GF adapter uses PGF.

## Consequences

GF remains grammar authority; SA gains stable multi-language integration and conformance.
