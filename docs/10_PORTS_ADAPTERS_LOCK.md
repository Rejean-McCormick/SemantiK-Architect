# Ports and Adapters Lock

Status: **LOCKED / normative**

## Driving use cases

The application exposes stable use-case ports:

```text
RenderCommunication
ValidateRequest
ListCapabilities
ValidateRuntime
ExplainGeneration   # diagnostics only, not epistemic authority
```

Transport adapters (Python SDK, HTTP, CLI, tests) call these use cases.

## Driven ports

### LexicalKnowledgePort

Provides language-specific planning metadata without inflection.

### LexicalBindingPort

Binds selected semantic concepts to exact admitted runtime lexical entries.

### RealizerPort

Realizes a `LanguagePlan` with its immutable `LexicalBindingSet` through the versioned SA↔GF contract. Primary adapter: GF/PGF.

### RuntimeCatalogPort

Loads immutable runtime manifests/artifacts and resolves an admitted RuntimeSet.

### CapabilityPort

Answers whether a language/profile/operation combination is released for the selected RuntimeSet.

### LocaleDataPort

Provides deterministic locale data not delegated to GF.

### TelemetryPort

Emits operational telemetry without making telemetry availability a semantic dependency.

## Anti-Corruption Layers

Every external semantic model has an ACL/mapping layer:

```text
Kristal -> Kristal ACL -> canonical request
Orgo -> Orgo ACL -> canonical request
eThikos -> eThikos ACL -> canonical request
KeenKonnect/Konnaxion -> ACL -> canonical request
Abstract-Wiki/ZObject optional -> ACL -> canonical request
```

ACLs may use upstream domain knowledge. The SA core must not.

## Adapter rules

- adapters MAY depend on third-party frameworks;
- adapters MUST satisfy reusable port contract tests;
- one ecosystem adapter MUST NOT import another ecosystem adapter;
- adapters MUST NOT mutate canonical semantics to “make generation easier”;
- adapters MUST report unmappable required semantics explicitly;
- no adapter may hide a remote dependency behind a supposedly offline core feature.

## Network policy

The canonical runtime path must function with network disabled when local artifacts are supplied. Optional network-backed adapters are explicit and must obey timeouts/retries/circuit-breaker policy.
