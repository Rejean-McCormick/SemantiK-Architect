# ADR-0005 — No backward-compatibility layer for pre-cutover internals

Status: **Accepted**  
Date: 2026-09-18

## Context

The application is being established around a new canonical architecture. Maintaining old internal shapes, routes, aliases, and alternate engine paths would permanently increase complexity without a product requirement.

## Decision

SemantiK does not preserve pre-cutover internal APIs solely for old tests, scripts, or abandoned clients.

When the canonical contract changes during this cutover:

- callers are updated;
- tests are updated;
- superseded code is removed;
- superseded documentation is removed from active docs;
- Git history provides historical recovery.

## Consequences

- no `Sentence` result contract alongside `SurfaceResult`;
- no retired frame aliases at semantic ingress;
- no old PGF path support;
- no grammar-development tools API in the runtime;
- no alternate direct frame-to-engine runtime.
