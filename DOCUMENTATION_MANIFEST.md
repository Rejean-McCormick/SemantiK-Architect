# Documentation Manifest

Status: **normative index**

This repository documentation is the design authority for SemantiK Architect.

## Authority order

When documents conflict, apply this order:

1. accepted ADR with a later decision date/version;
2. `*_LOCK.md` documents;
3. JSON schemas under `schemas/`;
4. other normative documents;
5. examples/reference material;
6. implementation code comments.

A code implementation that conflicts with a lock is wrong unless the lock has first been changed through the documented change-control process.

## Locked documents

- `docs/02_ARCHITECTURE_LOCK.md`
- `docs/03_DOMAIN_MODEL_LOCK.md`
- `docs/04_COMMUNICATION_SEMANTICS_LOCK.md`
- `docs/05_LANGUAGE_PLANNING_LOCK.md`
- `docs/06_SA_GF_CONTRACT_LOCK.md`
- `docs/07_LEXICAL_CONTRACT_LOCK.md`
- `docs/08_RUNTIME_ARTIFACT_LOCK.md`
- `docs/09_LANGUAGE_CONFORMANCE_LOCK.md`
- `docs/10_PORTS_ADAPTERS_LOCK.md`
- `docs/11_FAITHFULNESS_LOCK.md`
- `docs/12_FAILURE_ERROR_LOCK.md`
- `docs/14_TESTING_RELEASE_LOCK.md`
- `docs/16_AI_IMPLEMENTATION_GUARDRAILS.md`
- `docs/17_REPOSITORY_STRUCTURE_LOCK.md`
- `docs/21_INTERFILE_CONTRACT_LOCK.md`

## Supporting documents

- `docs/00_START_HERE.md`
- `docs/01_PRODUCT_CHARTER.md`
- `docs/13_OBSERVABILITY_OPERATIONS.md`
- `docs/15_ECOSYSTEM_BOUNDARIES.md`
- `docs/18_IMPLEMENTATION_SEQUENCE.md`
- `docs/19_CHANGE_CONTROL.md`
- `docs/20_GLOSSARY.md`
- `docs/22_IMPLEMENTATION_STATUS.md`
- `docs/reference/*`
- `docs/adr/*`

## Contract schemas

- `schemas/communication_request.schema.json`
- `schemas/communication_result.schema.json`
- `schemas/runtime_manifest.schema.json`
- `schemas/capability_manifest.schema.json`
- `schemas/capability_profile.schema.json`
- `schemas/error_envelope.schema.json`
- `schemas/sa_gf_contract.schema.json`
- `schemas/gf_bridge_spec.schema.json`
- `schemas/lexical_artifact.schema.json`
- `schemas/conformance_suite.schema.json`
- `schemas/runtime_activation.schema.json`

Schemas are intentionally narrower than the conceptual model. They lock transport-level structure while permitting versioned semantic vocabularies and extension registries.
