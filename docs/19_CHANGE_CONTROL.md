# Change Control

Status: **normative process**

## Why locks exist

The locks prevent implementation agents from solving local problems by silently changing architecture. They are intentionally harder to change than normal code.

## Changes that require an ADR

An ADR is mandatory for:

- canonical pipeline stage changes;
- new/removal of canonical domain aggregate types;
- changes to obligation semantics;
- incompatible schema changes;
- SA↔GF operation semantic changes;
- new canonical runtime dependency;
- new grammar backend as a production default;
- relaxation of fail-closed/faithfulness rules;
- change from modular monolith to distributed domain decomposition;
- lifecycle/status value changes;
- allowing runtime AI in the default path.

## Versioning

Public schemas and SA↔GF contracts use semantic versioning.

A major version is required for an incompatible change to meaning or required structure. Additive optional fields may be minor when old readers remain valid.

## Lock update sequence

1. write/accept ADR;
2. update affected lock(s);
3. update JSON schema/contract version;
4. update tests/goldens/conformance vectors;
5. implement code;
6. regenerate documentation manifest/reference indexes;
7. release with explicit migration notes.

Code-first contract changes are prohibited.

## Extension points that do not require architectural redesign

Subject to existing registries/version rules, the following are expected growth:

- new semantic predicates/roles in an admitted vocabulary;
- new lexical entries;
- new language/profile artifacts;
- additive SA↔GF operations in a minor contract version;
- new ecosystem ACL adapter;
- new output projection adapter;
- new optional telemetry backend.
