# Implementation Status

Status: **informative / current repository state**

The canonical SemantiK Architect v1 core is implemented in this repository.

## Implemented canonical pipeline

The repository contains executable implementations for:

- immutable canonical semantic graph values, statements, obligations, context and constraints;
- `CommunicationRequest` parsing/validation and stable application errors;
- language-neutral `CommunicationPlanner`;
- lexical knowledge preflight and exact lexical binding;
- target-language `LanguagePlan` / `RealizationUnit` planning with no language-code branches in core;
- explicit planner-support hints for extensible predicates;
- obligation and semantic-reference coverage validation;
- strict SA↔GF bridge realization through immutable bridge specifications;
- strict consumption of semantic lexical slots and communicatively relevant features at the bridge boundary;
- PGF runtime loading/linearization;
- immutable filesystem RuntimeSet catalog, artifact hashes, SA-version compatibility and explicit activation;
- released language/profile gates and hashed capability-profile artifacts;
- conformance-evidence hashing and release validation;
- deterministic output assembly and result identity;
- required opening/closing discourse operations;
- local deterministic lexical artifacts plus offline Wikidata Lexeme parsing utilities;
- explicit fail-closed lexical-source precedence with Wikidata as generic lexical knowledge authority and GF generic lexicons as binding fallback;
- source/sense provenance carried through lexical preflight and exact binding;
- Python SDK, CLI, minimal HTTP adapter, health/readiness and output projections;
- conformance harness, reusable multilingual candidate-matrix runner with fail-closed per-language candidate `extension_capabilities`, and release validator;
- architecture, contract, integration and failure-path tests.

## External release inputs

A production render requires an admitted RuntimeSet containing real release artifacts:

1. a PGF grammar artifact exposing the functions referenced by its bridge specification;
2. an `sa-gf-bridge-*` artifact for the exact SA↔GF contract version;
3. one or more lexical artifacts;
4. a capability manifest;
5. one hashed capability-profile artifact for every released profile;
6. passing, hashed conformance evidence.

Language development remains outside SA. A language becomes callable only after its exact artifacts pass the SA profile release gate.

## Ecosystem ACL status

The canonical ACL interface, canonical-schema adapter, and `KristalV6Acl` are implemented. The Kristal adapter consumes the explicit `semantik.kristal-v6.communication-projection/1.0` boundary, verifies selected-assertion traceability, and preserves v6 role/valuation/applicability/actionability metadata as supporting context. Other product-specific ACLs are added only when the upstream structured semantic contract is explicit. SA does not infer structured meaning from free text or from metadata magnitude inside an ACL.

## Deliberately absent

The repository contains no family grammar engine, safe-mode renderer, alternate pseudo-grammar, language fallback, raw-text understanding engine, business-state store, or article-generation pipeline.

## 1.3 alpha mathematical articulation

Implemented in the current snapshot:

- MathKristal Formula IR 1.0.0 ACL validation and canonical graph projection;
- explicit formula articulation anchors and source traceability;
- `math-pure-1` / `math-natural-1` language planning;
- Formula IR → Dedukti serialization;
- versioned math symbol registry with external alignment fields;
- Informath RealizerPort adapter and composite realization routing;
- SDK/CLI math projection/render surfaces;
- Euler candidate artifacts and contract tests.

Not released in this snapshot: a production Informath RuntimeSet. The profile remains candidate until a concrete Informath runtime is pinned and passes conformance.
