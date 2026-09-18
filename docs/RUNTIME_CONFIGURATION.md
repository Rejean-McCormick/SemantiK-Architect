# Runtime Configuration

Status: **normative**

## Principles

Runtime configuration selects deployed resources and operational behavior. It must not reintroduce grammar-development workflows into the application.

## PGF artifact

Default:

```text
runtime/semantik_architect.pgf
```

Supported override:

```text
PGF_PATH
```

No second PGF-path variable is part of the canonical contract.

## Optional language display metadata

```text
runtime/languages.json
```

This file may provide names or presentation metadata for languages already present in the PGF. It does not create capability.

## Lexical runtime data

Runtime lexical data and application-to-concrete mappings live in runtime data/configuration locations such as:

```text
data/lexicon/
data/config/iso_to_wiki.json
```

The exact data layout may evolve without changing the architectural boundary.

## Session state

Optional discourse state is configured as bounded in-process state with TTL semantics. It is ephemeral and process-local. See `SESSION_STATE.md`.

## Authentication

Authentication is deployment-specific. A reverse proxy, gateway, or host policy may enforce access controls before requests reach SemantiK.

The semantic runtime contract does not depend on a built-in API-key header.

## Invalid deployment states

Readiness must fail when required runtime resources cannot be loaded, including a required PGF artifact.

The runtime must not repair deployment configuration by building grammar artifacts on startup.
