# Generation API Contract

Status: **normative**

## Canonical HTTP surface

The canonical generation endpoint is:

```http
POST /api/v1/generate/{lang_code}
Content-Type: application/json
Accept: application/json
```

The language in the path is authoritative for the request.

The core runtime also exposes capability and operational endpoints documented elsewhere:

- `GET /api/v1/languages`
- `GET /health/live`
- `GET /health/ready`

Routes for grammar development, grammar repair, build management, or arbitrary tools execution are not part of the SemantiK runtime API.

## Authentication

The semantic API contract does not define a built-in API-key scheme. Authentication and authorization are deployment concerns and may be enforced by a reverse proxy, gateway, or hosting environment.

## Standard semantic-frame request

A standard request body is one JSON object with explicit semantic intent.

Rules:

1. `frame_type` is required and non-empty.
2. SemantiK does not infer a frame family from field names or object shape.
3. Each frame family uses one canonical shape.
4. Retired frame-type names are rejected rather than normalized.
5. The top-level key `type` is not an alias for `frame_type`.
6. Renderer-specific ASTs, templates, or backend selection are not semantic input.

### Canonical biography request

```json
{
  "frame_type": "bio",
  "subject": {
    "name": "Marie Curie",
    "qid": "Q7186",
    "profession": "physicist",
    "nationality": "Polish"
  }
}
```

The canonical biography frame is `frame_type: "bio"` with a nested `subject` object.

### Rejected: implicit semantic intent

```json
{
  "subject": {
    "name": "Marie Curie"
  }
}
```

Result: HTTP `422` because `frame_type` is missing.

### Rejected: retired frame-type alias

```json
{
  "frame_type": "entity.person",
  "subject": {
    "name": "Marie Curie"
  }
}
```

Result: HTTP `422` because `entity.person` is not the canonical biography frame type.

## Ninai/function-style input

Ninai/function-style input is a separate protocol adapter, not an alias system. If enabled, a payload identified by its `function` structure is parsed by the Ninai adapter and converted into canonical SemantiK domain objects before planning.

The resulting runtime path is still exactly the same planner/construction pipeline.

## Success response

A successful generation returns one JSON object representing `SurfaceResult`.

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `text` | string | yes | final surface text |
| `lang_code` | string | yes | returned application language code |
| `construction_id` | string | yes | selected construction |
| `renderer_backend` | string | yes | renderer that produced the final text |
| `fallback_used` | boolean | yes | whether an explicit fallback renderer was used |
| `tokens` | string[] | yes | token representation of the final text |
| `debug_info` | object | yes | machine-readable runtime diagnostics |
| `generation_time_ms` | number | yes | non-negative generation time in milliseconds |

Example:

```json
{
  "text": "Marie Curie is a Polish physicist.",
  "lang_code": "en",
  "construction_id": "copula_equative_classification",
  "renderer_backend": "family",
  "fallback_used": false,
  "tokens": ["Marie", "Curie", "is", "a", "Polish", "physicist."],
  "debug_info": {
    "runtime_path": "planner_first",
    "construction_id": "copula_equative_classification",
    "renderer_backend": "family",
    "lang_code": "en",
    "slot_keys": ["nationality", "profession", "subject"],
    "fallback_used": false,
    "selected_backend": "family",
    "attempted_backends": ["family"]
  },
  "generation_time_ms": 12.5
}
```

## Response invariants

- `text` is the authoritative surface text.
- `lang_code`, `construction_id`, `renderer_backend`, and `fallback_used` are authoritative top-level fields.
- `debug_info` must not contradict top-level fields.
- `generation_time_ms` is non-negative; tests must not require an exact zero duration.
- `tokens` represent the returned text and must be present.
- public serializers do not accept arbitrary objects and invent missing canonical fields.

## Diagnostics contract

Stable shared diagnostic keys, when applicable:

- `runtime_path` — canonical value: `planner_first`;
- `construction_id`;
- `renderer_backend`;
- `lang_code`;
- `slot_keys`;
- `fallback_used`;
- `selected_backend`;
- `attempted_backends`.

Renderer-specific diagnostics may be added, but `debug_info` must stay machine-readable and must not contain credentials, secrets, or raw sensitive payload dumps.

## Errors

Expected public status classes:

| Status | Meaning |
| --- | --- |
| `404` | requested language/capability is not available |
| `422` | invalid semantic request, invalid frame, mismatch, or unsupported frame type |
| `5xx` | unexpected planner, lexical, realization, or infrastructure failure |

Deployment auth layers may return their own `401`/`403` responses before SemantiK request handling.
