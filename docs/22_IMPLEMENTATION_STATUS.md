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
- Python SDK, CLI, minimal HTTP adapter, health/readiness and output projections;
- conformance harness and release validator;
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

The canonical ACL interface and canonical-schema adapter are implemented. Product-specific ACLs are added only when the corresponding upstream structured semantic contract is explicit. SA does not infer structured meaning from free text inside an ACL.

## Deliberately absent

The repository contains no family grammar engine, safe-mode renderer, alternate pseudo-grammar, language fallback, raw-text understanding engine, business-state store, or article-generation pipeline.
