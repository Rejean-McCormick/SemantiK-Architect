# Ecosystem Boundaries

Status: **normative boundary guidance**

## Authority principle

Integration does not transfer ownership. SemantiK Architect consumes explicit semantic/communication projections and returns communication projections. It is an articulation authority, not a source store, ingestion engine, context-ranking system, knowledge ledger, workflow authority or execution engine.

## EncyK

EncyK owns source discovery/acquisition/extraction and source-evidence handoff. SA does not crawl, acquire or parse arbitrary source prose as its canonical input.

## Médiathèque kOA

Médiathèque owns persistent source identity, snapshots, physical representations, integrity facts, rights/access and owner-preserving source references. SA may receive source references through upstream projections but never becomes the canonical source store.

## Interaction Kernel / DaaT

Interaction Kernel transports admitted interactions and artifact references. **DaaT** (`daat`) is the optional anti-corruption/admission and explicit contract-mapping boundary in front of Kristal/Kristall. Neither IK nor DaaT decides what SA must communicate, mints Kristall semantic identity for SA, or owns source bytes. DaaT may carry a mapped contract; semantic/content selection remains with the appropriate upstream authority.

## Kristal / Kristall

The stable portable SA articulation boundary remains `kristal_state/6.0` (Kristal Standard `6.0.0`). The current ecosystem design baseline is Kristal/Kristall `7.0.0-draft.3.2`, additive above portable v6.

Kristal/Kristall owns knowledge-artifact identity, assertions, typed valuations, coordinates/applicability, provenance/evidence, recognition/validation, record roles, actionability, lineage/conflict/supersession, KQ/KP/KA/KS semantic identity, Mesh/axes/registries and crystallization. SA does not create a competing knowledge ledger.

The SA boundary is the explicit `semantik.kristal-v6.communication-projection/1.0`, not raw state ingestion. `record_role`, valuations and actionability remain supporting context unless an upstream semantic/communication projection explicitly selects the underlying assertion and maps its communicative force. `actionability = automatic` is not an instruction to SA and never becomes a directive by itself.

Kristall v7 may align/crystallize knowledge and emit or reference v6-compatible projections; the SA ACL still validates the same portable boundary.

## Kompiler

Kompiler is a read-only context compiler. It may query normalized knowledge outputs and assemble bounded context for a caller, but it does not become truth authority, source authority, semantic-identity authority or communication-obligation authority. If Kompiler-produced context accompanies a request, the explicit `CommunicationRequest.obligations` still determines what SA must communicate. Context budget/ranking is not permission to omit or invent obligations.

## Orgo

Orgo owns Tasks, Cases, assignments, urgency, deadlines, priorities and ordering decisions. Its ACL maps selected communication semantics into SA obligations/context.

## eThikos

eThikos owns the structured question/argument/concept graph and interaction semantics. SA articulates that structure and can support a “render and confirm meaning” workflow.

## KeenKonnect / Konnaxion

These systems own exchange/matching/community state. SA may generate system prompts, explanations, notices and semantic exchanges in participant languages.

Free-form human text follows upstream semantic formalization before target-language re-realization if semantic translation is desired.

## Wikidata/Wikimedia ecosystem

The broader ecosystem may use Wikidata identifiers, dumps, Lexemes and open-source offline components. SA core MUST NOT require live Wikimedia infrastructure.

Rules:

- QIDs/Lexeme IDs are valid external references, not the only identity system;
- local mirrors are first-class lexical inputs and Wikidata Lexemes are the default generic lexical knowledge authority;
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

GF/RGL owns grammar and morphology; generic GF dictionaries are realization fallback rather than SA semantic authority.

SA MUST NOT patch the language after this boundary. A failing construction is fixed in the language/GF development source, rebuilt, reconformed and released as a new immutable artifact.

GF Observatory is evidence/observation infrastructure, not a runtime grammar authority. The immutable released artifact + capability/conformance manifest is what SA executes.

The SemantiK Architect repository MUST NOT carry grammar-development `.gf` sources. Candidate/released PGF artifacts may be referenced for conformance/runtime purposes, but grammar source authority remains GF/Wordbench.

## MathKristal / Informath boundary

MathKristal owns mathematical identity, Formula IR and mathematical epistemic state. SemantiK owns articulation only. Informath owns the MathCore/Informath mathematical language mapping and GF-backed multilingual realization. Wikidata/Wikidata Lexeme may provide lexical alignments but does not become the mathematical truth authority.
