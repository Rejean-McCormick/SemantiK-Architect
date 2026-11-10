# SemantiK Architect language realization authority — Branch 04 final-system integration

**Scope:** `TARGET_DESIGN` plus named local tests; not a public release, current Git HEAD or production assertion.

SemantiK Architect 1.3.0-alpha.2 is a deterministic typed communication planner/realizer that consumes `CommunicationRequest/1.0` and delegates grammar execution to **qualified external GF/PGF RuntimeSets**. It is **not** a canonical Kristal v11 read-view importer, source harvester, Context Pack manager, editor or public publisher. Its documented portable Kristal v6 communication boundary is a separate adopted input lane; a Framework v11 → SA generic adapter must **not** be inferred without an approved ACL.

**Existing real interface:** `tools/verify_spek_handoff.py` checks `spek.private-editorial-handoff/1.0` request package integrity; it cannot turn a Spek text into certified output. `integrations/konstellation_light/contract.py` and `contract.schema.json` are present with identical bytes in the three supplied SA, Orchestrator and Spek snapshots (checked independently by the LevelUpDiag read-only tool in this branch). This establishes **source compatibility only**, not runtime qualification.

**Handoff to Orchestrator:** pinned grammar artifacts, SA version range, conformance suite and evidence. Orchestrator owns release sequence; SA owns communication correctness. **Handoff to Spek:** explicit typed requests, deterministic `CommunicationResult`, declared language and RuntimeSet, with no invented facts or silent fallback.

**Blockers:** no independently compiled and semantically qualified GF/PGF RuntimeSet in this branch establishes production-level multilingual output; the observed RuntimeSet inspector is explicitly not a publication grant.

