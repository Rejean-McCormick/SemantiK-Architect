# Status and Capability Values

Status: **normative registry**

## Language/profile lifecycle

```text
DEVELOPMENT
CANDIDATE
RELEASED
RETIRED
```

Only `RELEASED` is callable by production policy.

## Ordering state

```text
FIXED
POLICY
FREE
```

## Communicative force

```text
ASSERT
ASK
DIRECT
PRESENT
```

Additions require versioned registry change.

## Runtime integrity state

```text
UNKNOWN
VALID
INVALID
```

`UNKNOWN` is never production-ready.

## Capability declaration

A capability entry is either present in a released profile or absent. Runtime does not expose “best effort”, “partial”, “maybe” or “fallback” as successful capability states.
