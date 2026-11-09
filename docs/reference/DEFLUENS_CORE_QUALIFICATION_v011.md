# Defluens core qualification v0.11 — SemantiK public GF batch

Candidate-only addition: `preview-candidate-batch` takes the same canonical
`CommunicationRequest` values as `preview-candidate`, grouped in 1–48
uniquely identified vectors:

```json
{"vectors":[{"case_id":"fr:attribute:positive","request":{"schema_version":"1.0"}}]}
```

The placeholder request above is **illustrative and not valid by itself**.
Actual requests must be generated with `defluens-core-batch` / `defluens-core-request`.

CLI invocation:

```text
python -m semantik_architect.adapters.inbound.cli.main preview-candidate-batch \
  --candidate-dir PATH_TO_WORDBENCH_CANDIDATE \
  --runtime-set-id defluens-core-fr-1 -
```

The CLI rejects a missing pipeline lock, duplicate case ID, invalid requests
and oversized input. `CandidateConformance` verifies every lock hash,
uses the existing SA planners and lexical bindings, and calls GF through the
existing realizer. Per-vector exceptions become explicit `ok:false` errors;
they never become synthetic language output. The envelope contains the
PGF SHA-256, pipeline-lock SHA-256, `released:false`, `activated:false` and
`linguistically_certified:false`. No RuntimeSet is admitted or activated.

FR and EN are distinct locked candidates; Defluens's v0.11 qualification
performs 14 semantic parity checks and 28 candidate previews when both are
ready. Absence of PGF remains an explicit block rather than a simulated pass.
