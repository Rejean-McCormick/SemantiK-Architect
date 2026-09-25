# Failure and Error Lock

Status: **LOCKED / normative**

## Principle

Semantic correctness is on the critical path. Failures that risk wrong language or wrong meaning fail closed.

## Stable error envelope

All application errors use a stable machine-readable envelope:

```text
code
category
stage
message_safe
retryable
request_id (optional)
runtime_set_id (if selected)
details (structured; no unsafe payload logging)
```

Transport adapters map this envelope to HTTP/CLI/SDK conventions without changing its meaning.

## Stable categories

The v1 registry includes:

```text
REQUEST_INVALID
SEMANTIC_UNMAPPABLE
OBLIGATION_UNCOVERED
CONSTRAINT_UNSATISFIABLE
LANGUAGE_UNAVAILABLE
PROFILE_UNAVAILABLE
LANGUAGE_PLANNING_FAILED
LEXICAL_KNOWLEDGE_MISSING
LEXICAL_BINDING_FAILED
GF_CONTRACT_INCOMPATIBLE
REALIZATION_FAILED
RUNTIME_MISSING
RUNTIME_INTEGRITY_FAILED
RUNTIME_NOT_READY
ADAPTER_CONTRACT_FAILED
DEADLINE_EXCEEDED
CANCELLED
INTERNAL_INVARIANT_BROKEN
```

Exact machine codes are listed in `reference/ERROR_CODE_REGISTRY.md` and are stable within a major contract version.

## Fail-closed conditions

A request MUST fail when:

- canonical semantic input is invalid;
- an obligation cannot be planned or realized;
- a required lexicalization is unavailable;
- requested language/profile is not released;
- RuntimeSet is missing/incompatible/corrupt;
- SA↔GF contract is incompatible;
- GF realization fails;
- a hard presentation constraint requires semantic deletion;
- deadline/cancellation prevents completion.

## Graceful degradation

Allowed only for auxiliary concerns:

- metrics exporter unavailable;
- trace backend unavailable;
- optional detailed span diagnostics unavailable;
- optional pretty formatting fails while canonical structured blocks remain intact.

Never degrade semantic completeness, language correctness, identity, modality or released-profile requirements.

## Retry policy

Deterministic validation/planning errors are non-retryable until input/runtime changes.

Remote transient adapter errors MAY use bounded retries with exponential backoff/jitter. Retries must honor the request deadline and MUST NOT mutate semantic content.

## No fallback success

The following are forbidden:

```text
sq requested -> GF failure -> English success
released profile missing -> reduced template success
lexeme missing -> guessed synonym success
```
