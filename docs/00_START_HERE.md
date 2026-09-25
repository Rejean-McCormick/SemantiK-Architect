# Start Here

Status: **normative navigation**

## Purpose

This documentation defines SemantiK Architect from first principles. The locked contracts in this repository are the implementation authority.

## Normative words

The terms **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are normative requirements in the RFC 2119 sense.

## Read in this order

1. `01_PRODUCT_CHARTER.md`
2. `02_ARCHITECTURE_LOCK.md`
3. `03_DOMAIN_MODEL_LOCK.md`
4. `04_COMMUNICATION_SEMANTICS_LOCK.md`
5. `05_LANGUAGE_PLANNING_LOCK.md`
6. `06_SA_GF_CONTRACT_LOCK.md`
7. `07_LEXICAL_CONTRACT_LOCK.md`
8. `08_RUNTIME_ARTIFACT_LOCK.md`
9. `09_LANGUAGE_CONFORMANCE_LOCK.md`
10. `10_PORTS_ADAPTERS_LOCK.md`
11. `11_FAITHFULNESS_LOCK.md`
12. `12_FAILURE_ERROR_LOCK.md`
13. `14_TESTING_RELEASE_LOCK.md`
14. `16_AI_IMPLEMENTATION_GUARDRAILS.md`
15. `17_REPOSITORY_STRUCTURE_LOCK.md`
16. `21_INTERFILE_CONTRACT_LOCK.md`

## Three categories of design decision

### Locked

Stable boundaries and invariants. Changing them requires an ADR and, where applicable, a schema/contract version bump.

### Extensible

The shape and extension mechanism are locked, but registries/vocabularies can grow without redesign. Examples: semantic predicate vocabulary, SA↔GF operation catalog, conformance profiles.

### Experimental

Optional adapters, research backends, or future functionality. Experimental code MUST remain behind a port and MUST NOT redefine the canonical path.

## AI implementation rule

If an implementation agent encounters ambiguity between plausible designs, it MUST NOT silently invent a new architecture. It must follow the locks, choose the smallest compliant implementation, and record unresolved design questions rather than introducing unapproved abstractions.

## Current implementation

See [`22_IMPLEMENTATION_STATUS.md`](22_IMPLEMENTATION_STATUS.md) for the exact source code currently present. Architecture documents describe the target contract; the implementation-status file prevents specification from being mistaken for completed code.
