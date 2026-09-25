# Runtime Artifact Lock

Status: **LOCKED / normative**

## Goal

A render must be reproducible, offline-capable and pinned to immutable artifacts. To avoid duplicating large resources across hundreds of languages, SA uses a **composed RuntimeSet**, not one monolithic copied bundle per language.

## RuntimeSet

```text
RuntimeSet
  runtime_manifest
  SA application version
  SA↔GF contract version
  GrammarArtifact(s)
  LexicalArtifact(s)
  LocaleDataArtifact(s)
  CapabilityManifest
  ConformanceEvidence
```

Every component has a content identity/hash and immutable version metadata.

## Artifact types

### GrammarArtifact

Contains or references the exact PGF/grammar runtime needed for one or more concrete languages.

### LexicalArtifact

Contains or references admitted lexical snapshots/dictionaries. One lexical artifact may be shared across many language RuntimeSets.

### LocaleDataArtifact

Deterministic formatting data needed for dates, numbers, units or locale conventions when not fully handled by GF.

### CapabilityManifest

Declares released languages, profiles and SA↔GF operations/features supported by this artifact composition.

### ConformanceEvidence

Immutable report linking a language/profile/runtime composition to the test suite version and result hashes.

## Manifest requirements

A runtime manifest MUST identify:

- schema version;
- runtime-set ID/content hash;
- SA compatible version range;
- SA↔GF contract version;
- GF/RGL versions or source identities;
- grammar artifact hashes;
- lexical artifact hashes;
- locale-data hashes;
- capability manifest hash;
- conformance evidence hashes;
- license/provenance references;
- release status.

## Request pinning

A request is executed against exactly one activated RuntimeSet identity. Activation may change between requests but MUST NOT change the artifacts used by a request already in progress.

## Immutability

Runtime artifacts are never patched in place. A change produces a new identity and new conformance evidence.

## Readiness

The runtime is ready for a requested language/profile only if:

- all required artifacts are present and integrity-valid;
- versions/contracts are compatible;
- the exact language/profile is `RELEASED` in the capability manifest;
- required lexical/locale data are available;
- referenced conformance evidence is present and valid.

## Activation and rollback

Activation is atomic. Blue-green/canary strategies MAY be used at deployment level. Rollback means activating the previous known-good RuntimeSet; it never means editing a broken artifact in place.

## Hashed control artifacts

The v1 runtime manifest pins `capability_manifest_sha256` and a `conformance_evidence_sha256` map in addition to ordinary artifact hashes. A released profile definition is itself a hashed `other` artifact named `capability-profile-<profile-identity>`.

When more than one released RuntimeSet can serve the same language/profile, selection MUST be explicit through request pinning or `activation.json`. Ambiguous automatic selection fails closed.
