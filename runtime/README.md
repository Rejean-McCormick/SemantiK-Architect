# Runtime artifacts

SemantiK Architect executes only immutable, released RuntimeSets. Source control does not ship a language runtime by default.

A typical runtime directory is:

```text
runtime/
  activation.json                 # optional when only one released set matches
  fr-core-2026-09/
    runtime.manifest.json
    capabilities.json
    bridge.json
    lexicon.json
    grammar.pgf
    profile-sa-core-1.json
    conformance-sa-core-1.json
```

`runtime.manifest.json` pins SHA-256 identities for grammar, lexical, bridge and profile artifacts, plus the capability-manifest hash and every conformance-evidence hash.

`activation.json` maps `language|profile` to one released RuntimeSet when multiple released sets coexist. Requests may instead pin `runtime_selector.runtime_set_id`.

The bridge and lexical artifact formats are documented in `docs/reference/GF_BRIDGE_SPEC.md` and the JSON Schemas under `schemas/`.
