# Domain Model Lock

Status: **LOCKED / normative**

## Design objective

The domain model must be stable enough for hundreds of languages and multiple upstream domains without turning SA into a universal ontology or leaking Orgo/eThikos/Kristal field names into the core.

The lock therefore fixes the **structural semantic model** while keeping the **semantic vocabulary extensible**.

## Canonical aggregate: CommunicationRequest

A request contains exactly these conceptual components:

```text
CommunicationRequest
  request_schema_version
  semantic_graph
  obligations
  communication_context
  presentation_constraints
  requested_capability_profile
  runtime_selector (optional/policy-controlled)
  operational metadata (deadline/request id; non-semantic)
```

## SemanticGraph

`SemanticGraph` is the canonical structured meaning container.

It contains:

- `nodes`: typed semantic values/entities/concepts;
- `statements`: predicate-role structures connecting nodes;
- optional semantic qualifiers carried from upstream;
- stable IDs local to the request and stable external references where available.

### Structural node kinds

The transport/domain model MUST support at least these structural variants:

- `EntityRef` — a referenced real/domain entity;
- `ConceptRef` — an ontology/lexicalized concept;
- `LiteralValue` — string/boolean/identifier-like literal;
- `QuantityValue` — number plus optional unit/scale;
- `TemporalValue` — instant/date/time/interval/duration;
- `CollectionValue` — an explicitly supplied collection of semantic references.

The set may be versioned, but domain-specific types such as `OrgoTaskDeadline` MUST NOT be added merely to mirror an upstream schema.

### Semantic identifiers

External identity is represented as namespace-qualified references, for example:

```text
wikidata:Q123
wikidata-property:P31
kristal:claim/abc
orgo:task/123
local-concept:repair
```

The core MUST NOT assume that all identifiers are Wikimedia identifiers, even though Wikidata is an important source.

## SemanticStatement

A statement is predicate-role structured meaning:

```text
SemanticStatement
  id
  predicate_ref
  arguments[]:
    role_ref
    value_ref
  polarity
  semantic_qualifiers[]
  source_refs[]
```

The structural shape is locked. The predicate and role vocabularies are extensible registries/ontologies.

This avoids hardcoding every future domain relation while preserving explicit role structure for language planning.

## CommunicationObligation

An obligation is a **must-communicate requirement** over semantic content.

```text
CommunicationObligation
  obligation_id
  semantic_refs[]
  communicative_force
  ordering/grouping constraints
  explicit visibility requirements
  source_refs[]
```

### Communicative force baseline

The baseline registry includes:

- `ASSERT` — communicate content as an assertion/statement;
- `ASK` — communicate a question;
- `DIRECT` — communicate a directive/request/instruction;
- `PRESENT` — present data/identity/value without imposing assertion wording.

The registry is versioned and extensible. Adding a new force requires a contract decision; arbitrary strings are not accepted silently.

### Hard invariant

Every obligation in a successful request MUST be discharged by at least one output unit. There is no `required=false` escape hatch for content obligations.

If a caller does not want content communicated, it must not submit it as a communication obligation.

## SupportingSemanticContext

Some information is needed to communicate correctly but is not itself required to appear as a surface claim.

Examples:

- grammatical gender/class metadata;
- lexical sense hints;
- valency/government metadata;
- pronunciation/transliteration preferences;
- entity type/class information used for lexical choice;
- discourse history supplied for anaphora;
- epistemic metadata not designated for explicit verbalization.

This supporting context MUST be distinguishable from obligations. SA MUST NOT silently promote supporting metadata into a new domain claim.

## CommunicationContext

Context controls articulation, not factual selection.

Baseline fields:

```text
target_language
target_locale
speaker identity/role (optional)
recipient identity/role (optional)
relationship
formality
politeness
register
tone_profile
channel
discourse_context (bounded, explicit)
```

Changing context MAY change wording, pronouns, address, construction and segmentation. It MUST NOT change the obligation set or domain values.

## PresentationConstraints

Constraints govern allowed presentation forms:

```text
allowed_block_kinds
opening_policy
closing_policy
list_policy
ordering_policy_ref
terminology_profile_ref
max_length / channel constraints
format hints
```

A constraint that cannot be satisfied without semantic omission makes the request unsatisfiable. SA does not truncate required meaning to meet a size limit.

## CommunicationPlan

`CommunicationPlan` is language-neutral. It contains:

- ordered/grouped obligation references;
- discourse sequence relationships;
- collection/grouping intent;
- upstream-authorized ordering policies;
- optional non-factual framing intents such as greeting/closing allowed by profile.

It MUST NOT contain:

- GF/PGF objects;
- final target-language word order;
- final sentence boundaries that are linguistically mandatory;
- target-language morphology.

## LanguagePlan

`LanguagePlan` is target-language specific and realizer-neutral. It contains:

- final output block topology;
- realization units within blocks;
- target-language construction operation IDs;
- semantic role bindings;
- lexical concepts/slots and binding requirements;
- grammatical features required by the contract;
- register/politeness decisions;
- source obligation IDs.

There is **no separate canonical `ConstructionPlan` layer** in v1. Construction is represented by `RealizationUnit` inside the `LanguagePlan`. A future additional IR requires an ADR proving that the extra boundary solves a real problem.

## RealizationUnit

A realization unit is the narrowest planned unit sent to the realizer adapter.

Conceptual fields:

```text
unit_id
operation_id        # versioned SA↔GF operation
role_bindings
feature_bindings
lexical_slots
obligation_ids
output_slot          # where it belongs in the LanguagePlan block
```

## CommunicationResult

The canonical output contains:

- target language/locale;
- ordered structured blocks;
- text per block/item;
- optional plain-text projection;
- obligation coverage map;
- preserved source references;
- exact runtime-set identity;
- exact SA↔GF contract version;
- deterministic result identity;
- operational metadata separated from deterministic content.

The output does not become an authority over the original semantics.
