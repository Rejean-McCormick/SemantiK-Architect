# SemantiK Architect

**SemantiK Architect v1.0 — deterministic semantic-to-human communication engine**

SemantiK Architect (SA) is the **semantic-to-human communication layer** of the kOA ecosystem. It receives complete structured meaning selected by an upstream authority and turns that meaning into faithful, context-appropriate, multilingual communication. It does **not** decide what is true, what should be selected, or which supplied facts may be discarded.

SA is designed for deterministic, offline-capable operation and delegates grammar, morphology, agreement, and language-specific realization to validated **Grammatical Framework (GF/RGL)** runtimes through a versioned SA↔GF contract.

## Mission

> Given structured semantic content, explicit communication obligations, and a communication context, produce a faithful human presentation in the requested language without inventing, filtering, silently omitting, or covertly changing the supplied meaning.

## Canonical pipeline

```text
Upstream domain / Kristal / semantic source
                  |
             boundary ACL
                  v
       Canonical CommunicationRequest
          |                  |
          |                  +-- CommunicationContext
          |
          +-- SemanticGraph
          +-- CommunicationObligations
                  |
                  v
          CommunicationPlanner
                  |
                  v
           CommunicationPlan
           (language-neutral)
                  |
                  v
       Lexical Knowledge Preflight
                  |
                  v
             LanguagePlanner
                  |
                  v
              LanguagePlan
       (target-language structure,
        blocks + realization units)
                  |
                  v
            Lexical Binder
                  |
                  v
       versioned SA <-> GF contract
                  |
                  v
              GF / RGL
                  |
                  v
         CommunicationResult
       + coverage + runtime identity
```

## Ownership boundary

SA owns **articulation**, not **content authority**.

SA owns:

- communication planning over all supplied obligations;
- grouping, segmentation, bounded block structure, list-vs-prose choice where allowed;
- register, formality, politeness, audience adaptation and discourse framing;
- target-language construction choice;
- lexical orchestration and binding;
- lowering to a versioned GF bridge contract;
- output assembly, semantic coverage validation, diagnostics and runtime identity.

SA does not own:

- truth, provenance, certainty or authority decisions;
- task priority, ethical decisions, civic outcomes or recommendation ranking;
- selection of which supplied facts are important enough to keep;
- raw-text understanding in the canonical path;
- GF/RGL language development;
- an internal duplicate grammar engine;
- hidden language fallback;
- article or long-form editorial planning;
- live Wikimedia services as a required runtime dependency.

## Locked invariants

1. **No invention.** Output domain claims must come from the canonical input semantics or a declared deterministic derivation.
2. **No silent omission.** Every communication obligation must be discharged or the request fails.
3. **No content selection.** SA may reorganize obligations; it may not decide to remove them.
4. **No status elevation.** Epistemic and modal distinctions supplied as communicatively relevant must not be flattened.
5. **No hidden fallback.** Requested language/profile failure is an error, never a successful response in another language or pseudo-grammar.
6. **One canonical runtime path.** Only the architecture defined by this repository is a runtime target.
7. **GF is behind a contract.** Core code never imports PGF/GF runtime classes.
8. **Validated profiles only.** A language is usable only for explicitly released conformance profiles.
9. **Offline-first.** The canonical runtime requires no network service.
10. **Deterministic by default.** Pinned input + config + runtime artifact set produces stable structured output.
11. **Fail closed on semantic correctness.** Graceful degradation is allowed only for non-critical operational features.
12. **Scale by artifacts, not language branches.** The 300th language must not require a new branch in SA core.

## Start here

Read [`docs/00_START_HERE.md`](docs/00_START_HERE.md). The files named `*_LOCK.md` are normative architecture locks and require ADR-governed change. The executable implementation status is recorded in [`docs/22_IMPLEMENTATION_STATUS.md`](docs/22_IMPLEMENTATION_STATUS.md).
