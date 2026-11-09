# Defluens v0.11.2 — French GF RGL `S` / `Utt` boundary

## Evidence (Windows GF 3.12, 2026-11-05)

The user ran `Qualifier_Candidats_FR_EN_v011.bat --compile-and-real` and GF returned exit 1 for `DefluensCoreFre.gf`. `gf-stderr.log` showed that the `.s` field of `(mkS t p (mkCl ...))` had type `CommonRomance.Mood => Str`, while the bounded Defluens `Output.s` field requires `Str`. Five `lin` entries failed: `RealizeAttribute`, `RealizeClass`, `RealizeEvent`, `RealizeAction`, and `RealizeLocation`.

There were also nonfatal name-resolution warnings for `mkAdv` in `Here_Place`, `There_Place`, and `InParis_Place`, because both `ParadigmsFre` and `ConstructorsFre` exported that name.

## Minimal candidate fix

In **the SemantiK-owned GF concrete sources only**:

- The five sentence linearizations in `profiles/defluens-core-1/DefluensCoreFre.gf` now call `mkUtt (mkS t p (mkCl ...))` before reading `.s`. This converts the RGL sentence to an utterance; no mood string table is exposed to `Output.s`.
- Three lexical adverbs explicitly use `ParadigmsFre.mkAdv` to resolve the renaming warnings.
- The legacy French attribute concrete `profiles/defluens-attribute-fr-1/DefluensAttributeFre.gf` makes the same `mkUtt` correction, preventing a future repeat of this type error.
- `DefluensCore.gf`, `DefluensCoreEng.gf`, lexical dictionaries, planifiers, JSON bridges, conformance suites, and runtime/release files are **unchanged**.

All source hashes are derived by WordBench on every candidate build; changing a `.gf` file is intentional and does not silently change a released artifact. The build remains fail-closed, and an old candidate is backed up only if a new build succeeds with `--force`.

## Windows validation (must be run on user's GF + official RGL)

Install the v0.11.2 correctif into `C:\mycode` and run from PowerShell:

```powershell
& 'C:\mycode\Grammatical-Framework\ars-magna-defluens\Qualifier_Candidats_FR_EN_v011.bat' --compile-and-real
```

On a failure, read the new `gf-stderr.log` and `gf-stdout.log` via `Diagnostiquer_Echec_GF_v0111.bat` (use `--en` for English). A failure must never be interpreted as a PGF build or linguistic qualification.

On successful compilation, the v0.11 qualifier should run **real** candidate previews FR/EN, check the 36 structural cases and 14 semantic-parity checks, and export a linguistic-review TSV. Human approval is still required for naturalness and agreement. No RuntimeSet is released or activated by this workflow.

## Test scope

Source-regression tests check the five `mkUtt` boundaries, the original imperative, the lexical disambiguation, and preservation of the English/abstract operations. Existing SemantiK unit tests exercise semantic requests and GF expression construction with explicitly fake PGFs. **No Windows `gf.exe` or complete `gf-rgl` are available in the patch-production environment**, so this change is a targeted type-correction candidate, not a claim that FR/EN now compiles on Windows.
