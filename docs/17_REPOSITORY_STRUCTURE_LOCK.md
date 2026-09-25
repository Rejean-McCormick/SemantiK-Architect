# Repository Structure Lock

Status: **LOCKED / normative direction**

```text
semantik-architect/
├── README.md
├── pyproject.toml
├── src/semantik_architect/
│   ├── domain/
│   │   ├── semantics/
│   │   │   ├── graph.py
│   │   │   ├── nodes.py
│   │   │   ├── statements.py
│   │   │   ├── obligations.py
│   │   │   └── references.py
│   │   ├── communication/
│   │   │   ├── context.py
│   │   │   ├── constraints.py
│   │   │   ├── request.py
│   │   │   ├── communication_plan.py
│   │   │   └── result.py
│   │   ├── language/
│   │   │   ├── language_plan.py
│   │   │   ├── realization_unit.py
│   │   │   ├── capabilities.py
│   │   │   └── lexical.py
│   │   └── errors.py
│   ├── application/
│   │   ├── ports/
│   │   │   ├── lexical_knowledge.py
│   │   │   ├── lexical_binding.py
│   │   │   ├── realizer.py
│   │   │   ├── runtime_catalog.py
│   │   │   ├── capabilities.py
│   │   │   ├── locale_data.py
│   │   │   └── telemetry.py
│   │   ├── planning/
│   │   │   ├── communication_planner.py
│   │   │   └── language_planner.py
│   │   ├── validation/
│   │   │   ├── request_validation.py
│   │   │   └── coverage.py
│   │   └── use_cases/
│   │       ├── render_communication.py
│   │       ├── validate_request.py
│   │       ├── list_capabilities.py
│   │       └── validate_runtime.py
│   ├── adapters/
│   │   ├── inbound/{http,cli,python_sdk}/
│   │   ├── ecosystem/{kristal,orgo,ethikos,keen_konnect,abstract_wiki_optional}/
│   │   ├── lexical/{local_wikidata,local_lexicon,gf_lexicon}/
│   │   ├── realization/gf/
│   │   ├── runtime/filesystem/
│   │   ├── locale/
│   │   └── output/{json,markdown,plain_text}/
│   ├── bootstrap/
│   └── observability/
├── schemas/
├── tests/{unit,architecture,contract,integration,conformance,golden,property,failure_paths}/
├── docs/{adr,reference}/
└── runtime/README.md
```

## Import rules

- `domain` imports only standard library and explicitly approved domain-safe utility packages.
- `application` imports domain + port abstractions only.
- adapters may import third-party frameworks and application/domain contracts.
- `adapters/ecosystem/*` do not import one another.
- PGF import exists only under `adapters/realization/gf`.
- HTTP framework imports exist only under inbound HTTP adapter/bootstrap.
- no compatibility package, family grammar engine or safe-mode package exists.

CI MUST enforce these boundaries with architecture/import tests.
