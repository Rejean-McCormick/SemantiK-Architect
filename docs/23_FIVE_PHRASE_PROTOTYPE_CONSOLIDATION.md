# Integration of SemantiK-only five-phrase prototype

**Source:** user-supplied `SemantiK_Phrase_Ops_Console.zip`, standalone `SemantiK_only_phrase_prototype` and nested `bundle/prototype`; base is user-supplied `znapshot_SemantiK_Architect_10271345.zip`.

## Merge decision

Keep one **SemantiK Architect** owner for the canonical profile 3. The five typed French semantic requests and profile already exist in Architect and are byte-identical to the bundled Phrase Ops copy. Do not create a second grammar, another app/runtime, or an unqualified `grammar.pgf` in the Architect repository.

- Imported: the five semantic seed definitions and the original historical report, with their AI-assisted provenance warnings.
- New: read-only fixture checker and 8 regression tests; checks deterministic seed/request identity, schema validation, candidate integrity and optional corpus provenance/leak detection.
- Reused unchanged: canonical GF source, bridge, lexicon, conformance suite, five requests and runtime metadata.
- Intentionally excluded: fake PGF placeholder and candidate lock; historical output reports; duplicated profile sources and `__pycache__`.

## Decision on `unlexer`

The separate standalone prototype omits `flags unlexer = text ;` in `KonstellationFre.gf`. The integrated Phrase Ops copy and existing Architect profile 3 include it. **No conflict is merged into Architect**; Architect remains source of truth. The option remains subject to an actual GF compilation check on a supported workstation.

## Scope and safety

The test exercises the actual Architect application pipeline until the PGF boundary, where a deterministic mock maps typed expressions to the five expected French sentences. This **does not** certify GF morphology, source interpretation, World knowledge, runtime activation, or a release.

The source editorial corpus is external. A read-only `--corpus-root` check is available but not part of the default CI because the real corpus was not supplied with the Architect ZIP. Four seed interpretations originated from AI-assisted prose and require human source verification before publication.

No modifications are made to SemantiK Phrase Ops Console or Runtime Orchestrator by this delivery. Phrase Ops still carries a historical bundled copy; it can eventually become a thin consumer of the Architect fixture rather than retaining independent maintenance of those same files. Do **not** delete an installed standalone prototype folder unless its local changes and output have first been backed up and reviewed.

## Validation

Run `python tools/validate_repository.py` at repository root. This runs the existing full test suite, including the newly added fixture tests. Run `python tools/phrase_prototype.py` for the detailed five-case proof-of-concept report, with `qualification = EXPRESSION_LEVEL_FIXTURE_ONLY`.
