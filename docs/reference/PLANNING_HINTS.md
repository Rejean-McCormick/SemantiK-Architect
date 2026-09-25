# Canonical Planning Support Hints

Status: **normative extension registry for v1**

The semantic vocabulary is extensible. The shared planner therefore cannot contain domain-specific branches for every future predicate. ACLs may attach explicit support metadata to a statement without changing its factual content.

Reserved v1 support properties:

- `sa:operation` — exact SA↔GF operation ID to use for the statement;
- `sa:role-map` — map from canonical operation role/slot names to statement roles or explicit semantic refs;
- `sa:slot-map` — exact lexical slot mapping when it differs from the role map;
- `sa:feature-map` — non-factual grammatical/realization features required by the operation.

Binding values in role/slot maps use:

- `role:<local-role-name>` to select a statement argument by role;
- `ref:<semantic-id-or-reference>` to bind an explicit semantic reference;
- an exact role reference/local role name;
- otherwise an explicit semantic ID/reference.

These hints are supporting semantic context, not new claims. They MUST NOT add facts, delete obligations or override runtime language behavior. Language-specific realization still belongs to the admitted RuntimeSet/GF bridge.
