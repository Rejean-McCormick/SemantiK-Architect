# ADR-0004 — Runtime capabilities derive from PGF

Status: **Accepted**  
Date: 2026-09-18

## Context

Historical target-language inventories and lexicon directories can diverge from what the deployed runtime can actually realize.

## Decision

The loaded PGF concrete languages are the source of truth for GF runtime language capability. Application mappings and lexicon data refine that capability; they do not create grammar capability by themselves.

## Consequences

- `/api/v1/languages` is runtime-derived;
- tests validate only deployed runtime languages;
- the current `WikiEng`/`WikiFre` artifact means current public application capability includes `en`/`fr`;
- adding a language requires deploying an artifact/data set that passes runtime tests.
