# ADR-0007 — Documentation authority and history policy

Status: **Accepted**  
Date: 2026-09-18

## Context

The previous `docs/` tree contained multiple generations of architecture, status snapshots, upgrade specifications, and contradictory contracts.

## Decision

The active `docs/` tree contains current target documentation only.

- normative documents are listed in `docs/README.md`;
- ADRs record durable decisions;
- superseded specifications are removed rather than retained in an active archive directory;
- Git history is the historical archive.

## Consequences

A document cannot remain active merely because part of it is still useful. Useful current material is consolidated into the canonical docs, then the obsolete source document is removed.
