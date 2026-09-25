# Schema and Contract Versioning

Status: **normative reference**

## Independent versions

SA maintains separate versions for:

- application/package version;
- public request/result schema version;
- SA↔GF contract version;
- capability profile version;
- runtime manifest schema version;
- lexical/locale artifact identities.

These versions MUST NOT be collapsed into one global number.

## Compatibility

Readers MUST reject incompatible major versions. Unknown optional fields are accepted only where the schema explicitly allows extension; locked objects with `additionalProperties: false` are intentionally strict.

## Canonical hashing

Deterministic identities SHOULD be computed from canonical serialized semantic content plus explicit version/runtime identifiers, excluding operational metadata such as request time, trace ID and latency.
