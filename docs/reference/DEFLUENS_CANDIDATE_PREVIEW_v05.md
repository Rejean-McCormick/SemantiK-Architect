# Candidate GF preview for Defluens v0.5

## Public CLI, not a production render

```bat
cd C:\mycode\SemantiK_Architect\SemantiK_Architect
set SEMANTIK_GF_EXECUTABLE=C:\mycode\Grammatical-Framework\gf-3.12-windows\gf.exe
set PYTHONPATH=src
python -m semantik_architect.adapters.inbound.cli.main --runtime-root runtime preview-candidate --candidate-dir "%USERPROFILE%\Downloads\Ars_Magna_Defluens\semantik_candidates\konstellation-fr-3" --runtime-set-id konstellation-fr-3 profiles\konstellation-explorer-3\requests\A001-core.json
```

This reuses **the existing** `CandidateConformance` pipeline: request validation, communication planning, lexical preflight/binding, SA↔GF bridge, real compiled `.pgf` through the existing PGF adapter, output assembly, obligation coverage and immutable input-hash checks. It adds no grammar or planner, no fake PGF and no hidden textual fallback.

A successful response includes a `communication_result` and is labelled `qualification=DEVELOPMENT_ONLY_REAL_GF`, with `released=false` and `activated=false`. It is *not* equivalent to SA production `render` or a language/profile `RELEASED` verdict. Missing/tampered PGF or absent GF runtime fails explicitly. Once qualified through the existing SemantiK Runtime Orchestrator, normal production `render` continues using its existing unchanged path.

**Initial scope**: five French semantic assertions in the already owned `konstellation-explorer-3` fixture; not the 14-language/15-capability product profile. To expand, introduce versioned contract operations and approved RGL-backed GF concrete grammar sources through the usual WordBench → SA candidate process.
