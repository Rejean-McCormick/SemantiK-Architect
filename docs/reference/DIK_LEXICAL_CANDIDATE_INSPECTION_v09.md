# SemantiK Architect — diK / WordBench candidate preflight

The existing runtime JSON lexical adapter and `LexicalPolicy` are authoritative.
This addition is a **read-only validation surface**, not a second lexical store,
planner or PGF renderer.

```powershell
cd C:\mycode\SemantiK_Architect\SemantiK_Architect
$env:PYTHONPATH = 'src'
python -m semantik_architect.adapters.inbound.cli.main inspect-dik-lexicon --bundle C:\lex-data\wordbench-fr
```

The inspector checks candidate manifest status, SHA-256, lexical-artifact 1.1
roles, lexeme identity, counts, provenance and non-activation. It reports
`runtime_usable=false`, `gf_verified=false`, `released=false` even when all
candidate checks pass. It never writes to `runtime/activation.json`.

Production still requires an externally compiled PGF, a matching versioned
SA↔GF bridge, an admitted lexical artifact, profile conformance, immutable
RuntimeSet and normal release gates. `wikidata:lexeme:L…` is a *source lexeme*
namespace, not an inferred semantic sense or an approved Kristal identity.

A human-reviewed `target_semantic_ref` remains candidate-only until a semantic
owner and the normal release process authorize it. Duplicate target binding
identities fail closed, and all lexical-source precedence remains unchanged.
