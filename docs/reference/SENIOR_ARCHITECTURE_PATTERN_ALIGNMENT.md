# Senior Architecture Pattern Alignment

Status: **reference with normative selections**

The supplied Senior Architect pattern catalog emphasizes failure paths, maintainability and trade-offs: patterns are used only when the problem costs more than the pattern complexity.

## Adopted as architectural foundations

| Pattern | Decision in SA |
|---|---|
| Hexagonal Architecture | Core architecture; domain/application separated from GF, HTTP, data and ecosystem protocols. |
| Modular Monolith | Default packaging/deployment; strict module boundaries without distributed-system overhead. |
| Anti-Corruption Layer | Required for every external semantic model. |
| Idempotency | Natural for deterministic side-effect-light rendering; explicit keys/hashes for retried API/job surfaces. |
| Immutable Infrastructure | Runtime artifacts and deployments replaced, never patched in place. |
| Health Checks | Liveness/readiness separated; readiness checks local critical artifacts. |
| Structured Logging | Required operationally; correlation IDs and stable error codes. |
| Metrics & Alerting | Required operationally; semantic correctness errors are first-class signals. |
| Timeout Budgets | Required for service/remote execution; stop ghost work. |
| Graceful Degradation | Only for auxiliary observability/formatting, never semantic correctness. |

## Conditional patterns

- circuit breaker/backoff: optional remote adapters only;
- rate limiting: service protection, not domain behavior;
- distributed tracing: distributed deployments, optional embedded use;
- blue-green/canary: release/RuntimeSet activation.

## Rejected as default/core

Strangler Fig, CQRS, Event Sourcing, Saga, Transactional Outbox, sharding, pub/sub/DLQ, sidecars/service mesh, BFF, data mesh and microservices-first are not justified by the current SA problem. Introducing any of them into the canonical architecture requires a new ADR and concrete failure/scale evidence.
