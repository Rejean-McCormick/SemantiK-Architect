# ADR-0008 — Composed immutable RuntimeSet

Status: **accepted**

## Context

One copied monolithic pack per language would duplicate large shared artifacts and complicate 300-language scaling.

## Decision

A RuntimeSet pins hashes of grammar, lexical, locale, capability and conformance artifacts.

## Consequences

Resources can be shared while requests remain reproducible and immutable.
