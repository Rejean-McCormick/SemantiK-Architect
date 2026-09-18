# ADR-0003 — Strict semantic ingress

Status: **Accepted**  
Date: 2026-09-18

## Context

A new application does not need to infer semantic intent from payload shape or preserve multiple names for the same frame family.

## Decision

Standard JSON requests require explicit `frame_type` and one canonical payload shape per frame family.

For biography:

```json
{
  "frame_type": "bio",
  "subject": {"name": "..."}
}
```

The runtime does not infer `bio` from person-like fields and does not normalize retired frame-type names such as `entity.person`.

Ninai/function-style input, if enabled, is a separate protocol adapter and must normalize to the same domain model before planning.

## Consequences

- ambiguous input is rejected with request/domain validation errors;
- OpenAPI/client contracts are simpler;
- tests target one shape;
- transport normalization cannot create a parallel semantic model.
