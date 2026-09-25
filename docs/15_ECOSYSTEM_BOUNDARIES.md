# Ecosystem Boundaries

Status: **normative boundary guidance**

## Authority principle

Integration does not transfer ownership. SA consumes semantic projections and returns communication projections.

## Kristal

Kristal owns structured epistemic state, provenance, certainty/status/authority and artifact identity. SA may verbalize required distinctions but does not create a competing truth ledger.

## SenTient

SenTient owns semantic ingestion/resolution/normalization of raw material in the canonical ecosystem flow. SA does not parse arbitrary source prose as its canonical input.

## Orgo

Orgo owns Tasks, Cases, assignments, urgency, deadlines, priorities and ordering decisions. Its ACL maps selected communication semantics into SA obligations/context.

## eThikos

eThikos owns the structured question/argument/concept graph and interaction semantics. SA articulates that structure and can support a “render and confirm meaning” workflow.

## KeenKonnect / Konnaxion

These systems own exchange/matching/community state. SA may generate system prompts, explanations, notices and semantic exchanges in participant languages.

Free-form human text follows semantic ingestion/formalization before target-language re-realization if semantic translation is desired.

## Wikidata/Wikimedia ecosystem

The broader ecosystem may use Wikidata identifiers, dumps, Lexemes and open-source offline components. SA core MUST NOT require live Wikimedia infrastructure.

Rules:

- QIDs/Lexeme IDs are valid external references, not the only identity system;
- local mirrors are first-class sources;
- ZObjects/Ninai/Udiron/Wikifunctions types terminate at optional adapters;
- reuse of good offline open-source components is preferred to needless rewriting;
- the SA canonical model is not defined by Wikimedia protocols.

## Compatibility strategy

```text
reuse -> wrap -> extend -> replace -> rewrite
```

Moving right requires a concrete technical benefit such as determinism, offline capability, semantic fidelity, language coverage, maintainability, performance or integration quality.

## GF language-development ecosystem

Language engineering is upstream of the SA production runtime.

Recommended authority flow:

```text
language repository / RGL work
        -> GF Wordbench build + validation
        -> immutable PGF/grammar artifact + validation evidence
        -> GF Observatory maturity/evidence projection (optional operational view)
        -> SA conformance profile suite
        -> capability manifest RELEASED
        -> SA RuntimeSet activation
```

SA MUST NOT patch the language after this boundary. A failing Albanian construction is fixed in the Albanian/GF development source, rebuilt, reconformed and released as a new immutable artifact.

GF Observatory is evidence/observation infrastructure, not a runtime grammar authority. The immutable released artifact + capability/conformance manifest is what SA executes.
