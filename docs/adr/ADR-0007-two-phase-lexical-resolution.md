# ADR-0007 — Two-phase lexical knowledge and binding

Status: **accepted**

## Context

Construction choice may depend on lexical properties, while morphology belongs to GF.

## Decision

Resolve lexical planning facts before LanguagePlan; bind exact runtime lexical entries after operation selection.

## Consequences

Planning has required information without duplicating morphology.
