# Error Code Registry

Status: **normative registry**

Stable v1 machine codes:

| Code | Category | Retryable by same input/runtime? |
|---|---|---|
| SA-REQ-001 | REQUEST_INVALID | No |
| SA-SEM-001 | SEMANTIC_UNMAPPABLE | No |
| SA-SEM-002 | OBLIGATION_UNCOVERED | No |
| SA-CON-001 | CONSTRAINT_UNSATISFIABLE | No |
| SA-LANG-001 | LANGUAGE_UNAVAILABLE | No |
| SA-LANG-002 | PROFILE_UNAVAILABLE | No |
| SA-LANG-003 | LANGUAGE_PLANNING_FAILED | No |
| SA-LEX-001 | LEXICAL_KNOWLEDGE_MISSING | No |
| SA-LEX-002 | LEXICAL_BINDING_FAILED | No |
| SA-GF-001 | GF_CONTRACT_INCOMPATIBLE | No |
| SA-GF-002 | REALIZATION_FAILED | Usually no; artifact/input must change |
| SA-RUN-001 | RUNTIME_MISSING | Operationally possible after deployment fix |
| SA-RUN-002 | RUNTIME_INTEGRITY_FAILED | No until artifact replaced |
| SA-RUN-003 | RUNTIME_NOT_READY | Operationally possible |
| SA-ADP-001 | ADAPTER_CONTRACT_FAILED | Depends on upstream/input |
| SA-OPS-001 | DEADLINE_EXCEEDED | Yes only with new deadline/resource state |
| SA-OPS-002 | CANCELLED | Yes with new request |
| SA-INT-001 | INTERNAL_INVARIANT_BROKEN | No; software defect |

Codes are not reused for different meanings within major version 1.
