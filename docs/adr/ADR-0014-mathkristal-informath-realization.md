# ADR-0014 — MathKristal Formula IR and Informath realization

Status: **accepted for 1.3 alpha**

## Context

SemantiK needs to articulate canonical mathematical expressions without parsing display notation or embedding a parallel multilingual mathematics grammar.

## Decision

1. MathKristal Formula IR is accepted only through an ACL and remains external to the core domain model.
2. The canonical semantic graph preserves structural traceability and an explicit `present-formula` communication anchor.
3. Mathematical language planning emits `math.informalize_formula`.
4. The `RealizerPort` may route that operation to a versioned Informath adapter; ordinary operations continue through the SA↔GF bridge.
5. Informath/MathCore/GF owns mathematical grammatical realization.
6. Formula IR → Dedukti and the symbol registry are deterministic versioned bridge artifacts.
7. No math runtime is `RELEASED` until real Informath artifacts and conformance evidence are pinned.

## Consequences

The one canonical application pipeline is preserved while realization becomes backend-specialized behind the port. SemantiK gains structure-preserving mathematical articulation without becoming a theorem prover, CAS, Formula IR authority, or grammar implementation.
