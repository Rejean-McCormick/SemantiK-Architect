# SemantiK-only phrase prototype — report

## Result

Expression-level SemantiK Architect prototype: **PASS (5/5)**. Every CommunicationRequest, profile artifact and conformance vector validates against the current SemantiK Architect schemas. Coverage is complete for every obligation.

Important: this environment does **not** contain the GF compiler nor the Python `pgf` binding, and the uploaded snapshot does not contain `profiles/konstellation-explorer-2/Konstellation.pgf`. Therefore the final PGF linearization step was exercised with a deterministic fixture that consumes the real SA bridge expressions. The SA request validation, communication planning, language planning, lexical binding, bridge expression construction, output assembly and coverage validation are the real repository code.

## What changed from profile 2

- No complete `position.text` sentence is passed as the `patient` slot.
- Semantic nodes reference typed concepts/entities/actions.
- Lexical bindings are `gf_expr` constructors (NP/V2/ClassNP), not sentence literals.
- The GF source assembles a sentence from typed constituents.
- A leak audit checks all 398 current position sentences and fails if a complete one appears in prototype input artifacts.

## Five cases

### A001-core

- Provenance: `A001` — `aug_grace` — Chapitres 2–4
- Semantic origin: `prototype_manual_decomposition_from_existing_ai_assisted_position`
- Existing corpus sentence (comparison only, never sent to SA): Augustin défend l’existence du libre arbitre, notamment à partir des commandements adressés aux humains.
- Generated result: **Augustin défend l’existence du libre arbitre.**

### H131-second-clause

- Provenance: `H131` — `anselm` — Proslogion, ch.1
- Semantic origin: `prototype_manual_decomposition_from_existing_ai_assisted_position`
- Existing corpus sentence (comparison only, never sent to SA): Anselme cherche à comprendre ce qu’il croit ; la foi stimule chez lui l’enquête intellectuelle.
- Generated result: **La foi stimule l’enquête intellectuelle d’Anselme.**

### H223-core

- Provenance: `H223` — `rn` — Rerum novarum, développement sur la propriété et la famille
- Semantic origin: `prototype_manual_decomposition_from_existing_ai_assisted_position`
- Existing corpus sentence (comparison only, never sent to SA): Léon XIII défend la propriété privée comme moyen de prévoyance et de protection de la famille.
- Generated result: **Léon XIII défend la propriété privée comme moyen de prévoyance et de protection de la famille.**

### P014-core

- Provenance: `P014` — `le` — § 12
- Semantic origin: `prototype_manual_decomposition_from_existing_ai_assisted_position`
- Existing corpus sentence (comparison only, never sent to SA): Jean-Paul II affirme la priorité du travail sur le capital dans le processus de production.
- Generated result: **Jean-Paul II affirme la priorité du travail sur le capital dans le processus de production.**

### K003-classification

- Provenance: `D005` — `ccc_mary` — CEC 491 ; citation de la définition de 1854
- Semantic origin: `structured_classification_plus_witness`
- Existing corpus sentence (comparison only, never sent to SA): Marie est dite préservée du péché originel dès sa conception par grâce, en vue des mérites du Christ.
- Generated result: **L’Immaculée Conception est un dogme.**

## Interpretation

The prototype proves that the current SA core can construct French sentences from semantic references without receiving the existing complete sentence. It does **not** yet prove that profile 3 is a production GF RuntimeSet: a real `Konstellation.pgf` must still be compiled and passed through the Runtime Orchestrator conformance/release gates.

Four of the five proposition seeds are manually decomposed from positions whose historical corpus provenance says they were created with AI-assisted reading/paraphrase. Therefore the **realization path** in this prototype is AI-free, but those four semantic inputs are not yet clean-room, human-revalidated replacements for the old AI-derived interpretation. `K003-classification` instead starts from the corpus classification structure plus its witness.

## Next gate

1. Human-review the semantic seeds against the cited source passages (or ingest source excerpts into evidence).
2. Compile `KonstellationFre.gf` with GF (`gf -make KonstellationFre.gf`) to create a real `Konstellation.pgf`.
3. Replace the prototype placeholder PGF with the real compiled artifact.
4. Run Runtime Orchestrator `validate-config`, `plan`, and `release` for `konstellation-fr-3`.
5. Only after real PGF conformance passes, use these deterministic realizations to pre-generate Konstellation text artifacts.
