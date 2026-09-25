# ADR-0009 — Hexagonal modular monolith

Status: **accepted**

## Context

SA needs strong boundaries but not distributed-system complexity.

## Decision

Use ports/adapters plus strict modules in one default package/process.

## Consequences

Easy testing/maintenance; distributed deployment remains possible later behind ports.
