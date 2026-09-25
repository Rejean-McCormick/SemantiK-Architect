# Architecture Lock

Status: **LOCKED / normative**

## Architectural style

SA is a **hexagonal modular monolith**.

- Hexagonal architecture protects the domain/application core from GF/PGF, HTTP frameworks, databases, Wikidata protocols and ecosystem-specific models.
- A modular monolith is the default deployment and packaging model. Distributed decomposition is a later deployment choice, not a domain-design assumption.
- Anti-Corruption Layers (ACLs) are mandatory at external semantic boundaries.

## Canonical runtime path

There is exactly one successful production pipeline:

```text
Driving Adapter
    |
    v
ACL / Request Mapper
    |
    v
CommunicationRequest
    |
    v
Request Validation
    |
    v
CommunicationPlanner
    |
    v
CommunicationPlan
    |
    v
Lexical Knowledge Preflight
    |
    v
LanguagePlanner
    |
    v
LanguagePlan
    |
    v
Lexical Binder -> LexicalBindingSet
    |
    v
RealizerPort
    |
    v
GF Bridge Adapter
    |
    v
GF / PGF Runtime
    |
    v
Output Assembly
    |
    v
Faithfulness/Coverage Validation
    |
    v
CommunicationResult
```

No family-engine fallback, alternate compatibility path, emergency template path, or probabilistic replacement is part of the canonical pipeline.

## Stage ownership

### 1. Boundary normalization

External objects are mapped into the canonical request. External field names do not leak into the core merely because they exist upstream.

### 2. Communication planning

Language-neutral planning determines obligation grouping, ordering constraints, discourse sequence and permitted presentation relationships. It does **not** finalize target-language sentence boundaries or grammar.

### 3. Lexical knowledge preflight

Language-specific lexical facts needed for planning are resolved before final construction choice: valency, grammatical class/gender where relevant, governed complement information, lexical availability and terminology constraints.

### 4. Language planning

The target-language planner chooses final block topology, discourse realization, target-language construction operations and register decisions. Different languages may segment the same obligations differently while preserving obligation coverage and permitted ordering.

### 5. Lexical binding

Selected semantic concepts are bound to versioned lexical resources/entries required by the realizer. Morphological inflection remains a GF responsibility.

### 6. GF realization

The GF adapter invokes only operations admitted by the versioned SA↔GF contract. GF runtime details do not cross the realizer port.

### 7. Output and validation

The result is assembled into transport-neutral blocks, checked for complete obligation coverage, and tagged with the exact runtime identities used.

## Dependency direction

```text
adapters  ->  application  ->  domain
              ^      |
              |      v
            ports  pure policies
```

Forbidden:

- `domain -> application`
- `domain/application -> concrete adapter`
- `domain/application -> PGF runtime`
- ecosystem adapter importing another ecosystem adapter;
- core importing HTTP/database frameworks;
- language-specific `if language == ...` logic in core planning.

## State model

The canonical render path is side-effect-light and request-scoped. SA does not become the authority for upstream business state. Durable caches or registries are infrastructure concerns and MUST NOT become hidden semantic authorities.

## Concurrency and determinism

One request is pinned to one immutable runtime set. Mid-request artifact activation MUST NOT change grammar, lexicon or conformance identity.

## Non-goals for the architecture

The following are explicitly rejected until a concrete requirement justifies them:

- microservices-first;
- CQRS;
- Event Sourcing;
- Saga orchestration;
- transactional outbox;
- queues/pub-sub as the canonical render path;
- sharding;
- service mesh/sidecars;
- Strangler Fig coexistence.

## Architecture invariants

A compliant implementation MUST satisfy all of the following:

1. one canonical pipeline;
2. external models terminate at ACLs;
3. core has no framework or PGF dependency;
4. semantic correctness failures fail closed;
5. all successful results are pinned to immutable runtime identities;
6. no language or grammar patching at runtime;
7. no hidden language fallback;
8. no duplicated general-purpose grammar engine;
9. no per-language branches in core;
10. changes to locked boundaries require ADR-governed change.
