# Five-phrase prototype — integrated in SemantiK Architect

**Status:** offline expression-level test fixture, **not** a production GF/PGF RuntimeSet or validated statement of historical truth.

The former standalone `SemantiK_only_phrase_prototype` has been absorbed as an **example and regression gate** of SemantiK Architect. **There is no additional engine.** The current authoritative profile assets already live at:

- `profiles/konstellation-explorer-3/` — GF sources, semantic-to-GF bridge, lexicon, five `CommunicationRequest`s and conformance suite;
- `runtime/konstellation-fr-3/` — existing runtime metadata; **not changed or activated** by this consolidation.

This directory holds only the five original **semantic seeds** and the original explanatory report. The fixture runner is `tools/phrase_prototype.py`; tests live in `tests/integration/test_phrase_prototype.py`. We have *not* copied the old duplicate `profile/`, `requests/`, `candidate/`, fake `grammar.pgf`, old execution logs or historical output JSON, to avoid competing authorities and misleading release artifacts.

## Quick check (no GF compiler required)

From the repository root with validation dependencies installed:

```powershell
py -m pip install -e ".[dev]"
py tools/phrase_prototype.py
py -m pytest -q tests/integration/test_phrase_prototype.py
```

The runner uses real SemantiK Architect request validation, communication planning, lexical bindings, coverage validation, GF bridge expressions and output assembly. **Only the PGF final linearization is simulated** by a local `FixturePgfV3` test double. The candidate bundle is created in a temporary directory and destroyed; the runtime catalog, profiles, source corpus and active releases are never modified. Five cases must match the **existing Architect canonical conformance suite** exactly, including expected French text and source-reference IDs.

For an optional provenance / full-sentence leakage check against your independent editorial corpus:

```powershell
py tools/phrase_prototype.py --corpus-root C:\path\to\editorial-corpus
```

The corpus must have `edition/editorial.json` with `positions`, `sources` and `classifications`. The tool reads it but never writes to it. Without that external corpus, it does **not** claim source-level review or the historical full-corpus leakage audit.

## GF drift decision

The former standalone prototype had a copy of `KonstellationFre.gf` *without* `flags unlexer = text ;`. The Architect copy and the Phrase Ops bundled copy **agree** and include the flag. This integration uses Architect's existing source unchanged and asserts that flag remains present. No native `gf -make` build has been run here, so this is **not** a compiler compatibility or linguistic conformance claim.

## Provenance boundary

Four original seeds are `prototype_manual_decomposition_from_existing_ai_assisted_position`; one is `structured_classification_plus_witness`. Their source IDs and locators are *references*, not verified original source readings. See `PROTOTYPE_REPORT_SOURCE.md`. No identity, signature, authorization, publication or RuntimeSet activation is minted by this fixture.

Next qualification step: human-review seeds against original passages, compile real GF/PGF, run actual GF conformance, then submit candidate to SemantiK Runtime Orchestrator. None of these steps are silently performed by this patch.
