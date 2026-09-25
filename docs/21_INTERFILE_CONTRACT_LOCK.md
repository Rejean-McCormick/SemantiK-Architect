# Interfile / Producer-Consumer Contract Lock

Status: **LOCKED / normative**

This document prevents adjacent modules from redefining shared objects independently.

## Canonical flow contracts

| Contract | Producer | Consumer | Persistence | Public? |
|---|---|---|---|---|
| `CommunicationRequest` | inbound ACL / SDK mapper | `RenderCommunication` use case | no by core | yes |
| `CommunicationPlan` | `CommunicationPlanner` | `LanguagePlanner` | no | diagnostic only |
| `LexicalPlanningContext` | `LexicalKnowledgePort` adapter | `LanguagePlanner` | optional cache outside core | no |
| `LanguagePlan` | `LanguagePlanner` | lexical binder + output planning | no | diagnostic only |
| `LexicalBindingSet` | `LexicalBindingPort` adapter | `RealizerPort` | optional artifact/cache ref | no |
| `RealizationResult` | `RealizerPort` | output assembler / coverage validator | no | no |
| `CommunicationResult` | output assembler | driving adapter/client | caller choice | yes |
| `RuntimeSetDescriptor` | `RuntimeCatalogPort` | render use case / readiness | immutable catalog | operational public |

## CommunicationRequest

Must already be canonical. Core planners never receive raw Orgo/Kristal/eThikos objects.

## CommunicationPlan

Contains only language-neutral grouping/sequence/discourse intent. It may reference obligation IDs and semantic IDs, never GF operations or lexical runtime IDs.

## LexicalPlanningContext

Ephemeral language-specific knowledge keyed by semantic IDs. It may include valency/class/government/availability metadata needed for planning.

It MUST NOT contain inflected strings used as a hidden renderer and MUST NOT mutate the semantic graph.

## LanguagePlan

Contains target-language block topology and `RealizationUnit`s. Each unit references an SA↔GF `operation_id` and unresolved lexical slots/concept references where applicable.

The planner MUST NOT require PGF objects.

## LexicalBindingSet

Immutable map from `RealizationUnit` lexical slots to exact runtime lexical references plus lexical artifact identity.

The binding set is separate from `LanguagePlan` so the plan remains a planning artifact and lexical binding can be tested/replaced independently.

Conceptual shape:

```text
LexicalBindingSet
  runtime_lexicon_id
  bindings:
    (unit_id, slot_id) -> lexical_ref
```

## RealizerPort input

The realizer receives:

```text
LanguagePlan
+ LexicalBindingSet
+ RuntimeSetDescriptor
+ remaining deadline/cancellation context
```

It returns `RealizationResult` containing realized unit text and unit IDs. It does not assemble transport-specific Markdown/HTML.

## CommunicationResult assembly

Output assembly combines realized units according to `LanguagePlan` block topology, then coverage validation proves all obligations are discharged.

A result cannot be marked successful before coverage validation completes.

## Mutation rule

All canonical/inter-stage values are immutable. Stages return new values rather than mutating earlier contracts in place.

## Version rule

Public contracts (`CommunicationRequest`, `CommunicationResult`) are schema-versioned. Internal contracts are package-versioned and locked by architecture tests; incompatible redesign requires an ADR and updates to this document.
