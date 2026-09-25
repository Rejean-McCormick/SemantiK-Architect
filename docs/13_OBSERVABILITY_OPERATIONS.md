# Observability and Operations

Status: **normative operational guidance**

## Structured logs

Production logs SHOULD be structured JSON with:

- request/correlation ID;
- stage;
- stable error code;
- target language/profile;
- RuntimeSet ID;
- SA↔GF contract version;
- duration;
- success/failure.

Raw semantic payloads, private messages and PII MUST NOT be logged by default.

## Metrics

Recommended metrics:

- request count/latency/error rate;
- planning vs lexical vs GF realization latency;
- failures by stable error category;
- language/profile request distribution;
- runtime readiness failures;
- lexical miss rate;
- obligation coverage/invariant failures;
- saturation/concurrency.

## Tracing

Distributed tracing is optional for embedded/local use and recommended when SA participates in distributed kOA request chains. Trace context is operational and excluded from deterministic content identity.

## Health

### Liveness

Answers whether the process/event loop is alive. It does not perform expensive GF generation or external calls.

### Readiness

Answers whether the configured canonical runtime can serve. It verifies active RuntimeSet manifests, integrity state and required local resources. Optional remote services MUST NOT make an otherwise offline runtime unready.

## Time budgets

Service requests SHOULD carry an absolute deadline. Stages consume the remaining budget; downstream remote calls receive the remaining deadline. Work should stop when the requester can no longer receive the result.

## Deployment patterns

Immutable artifacts plus atomic activation support blue-green/canary releases. Rollback activates a previous immutable RuntimeSet/application version.
