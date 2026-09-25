# SA ↔ GF Operation Catalog v1

Status: **normative seed registry**

This catalog defines the initial operation namespace. Exact GF functions are implementation details of the bridge grammar/concrete language; these IDs are the SA-side semantic grammatical requests.

| Operation ID | Required semantic intent | Notes |
|---|---|---|
| `discourse.greeting` | authorized non-factual opening, optional recipient | register/politeness-aware; carries no domain claim |
| `discourse.closing` | authorized non-factual closing | register/politeness-aware; carries no domain claim |
| `clause.intransitive_event` | event + subject/actor | tense/aspect/mood features as supplied/required |
| `clause.transitive_event` | event + subject/actor + object/patient | preserves role identity |
| `clause.ditransitive_event` | event + actor + theme + recipient/goal | language implementation chooses natural argument strategy |
| `clause.copular_classification` | entity + class/concept | “X is a Y”-type semantics, language-specific realization |
| `clause.copular_attribute` | entity + attribute | attributive predication |
| `clause.existential` | existence of entity/content | |
| `clause.locative` | entity + location | |
| `clause.possession` | possessor + possessed | MUST NOT force an English-style `have` construction |
| `clause.passive_event` | event with patient-prominent realization | only when discourse/profile permits |
| `question.polar` | proposition queried for truth value | |
| `question.content` | proposition with queried role/value | question role explicit |
| `directive.action` | requested/required action semantics | register/politeness features may alter realization |
| `coordination.clause` | two or more compatible clause units | conjunction semantics explicit |
| `relative.subject` | nominal + subject-gap relative semantics | |
| `relative.object` | nominal + object-gap relative semantics | |
| `nominal.apposition` | two co-referential nominal descriptions | |
| `comparison.comparative` | ordered comparison semantics | |
| `comparison.superlative` | maximal/minimal comparison semantics | |

## Version rule

Adding a fully optional operation is a minor SA↔GF contract change. Changing the semantic meaning/role requirements of an existing operation is a major change.

## Conformance rule

A language does not have to implement every operation ever defined. A released capability profile identifies the exact required subset. Within that released profile, every required operation must pass conformance; there is no runtime best-effort substitution.
