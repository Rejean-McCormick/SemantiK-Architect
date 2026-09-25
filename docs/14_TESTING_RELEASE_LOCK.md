# Testing and Release Lock

Status: **LOCKED / normative**

## Testing layers

### 1. Domain invariant tests

Pure tests, no filesystem/network/GF. Cover semantic graph validation, obligation completeness, ordering rules, context invariants and deterministic planning.

### 2. Architecture tests

CI enforces import/dependency boundaries, forbidden language branches and adapter isolation.

### 3. Port contract tests

Every adapter implementation passes reusable contract suites for error semantics, determinism where applicable, runtime identity and cancellation behavior.

### 4. Communication planner tests

Verify grouping/order and that planning never drops obligations.

### 5. Language planner property tests

Verify that changing language/register can alter structure but cannot alter obligation identity, entity values, polarity, time or quantity.

### 6. GF bridge integration tests

Run against exact admitted PGF/grammar artifacts and verify operation lowering plus expected failures.

### 7. Language conformance tests

One common profile corpus plus language-specific legitimate extensions. Release is pass/fail, not an informal quality score.

### 8. Golden communication tests

Use meaningful fixtures from Orgo, eThikos, Kristal and KeenKonnect. Goldens verify structured blocks and, where stable, surface realization.

### 9. Metamorphic/cross-language tests

Examples:

- same request in two released languages discharges the same obligation IDs;
- formality change cannot alter deadline/entity/quantity;
- output formatting change cannot alter LanguagePlan semantic bindings;
- reordering only occurs when order state permits it.

### 10. Failure-path tests

Missing/corrupt runtime, incompatible contract, missing lexeme, unsupported operation, deadline exhaustion, invalid ACL mapping, telemetry outage and cancellation are tested deliberately.

## Release gate

A production release requires:

- all locked-contract tests pass;
- schema validation passes;
- architecture boundary tests pass;
- active RuntimeSet integrity passes;
- released language/profile evidence is present;
- docs/ADR validation passes;
- no known semantic correctness regression is waived silently.

## Golden update rule

A golden output change is never accepted solely because “the new output looks reasonable.” The change must be classified as:

- semantics-preserving wording change;
- intended contract/profile change with ADR/version update;
- bug fix;
- language artifact change with renewed conformance evidence.
