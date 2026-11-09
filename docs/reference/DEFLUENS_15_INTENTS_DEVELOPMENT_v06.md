# Ars Magna Defluens — 15 practical intents (development map)

Run the existing public SemantiK Architect CLI:

```bash
PYTHONPATH=src python -m semantik_architect.adapters.inbound.cli.main defluens-intents
```

The JSON response enumerates the 15 WordBench practical intent IDs and their
candidate SA↔GF *operation families*. The map is owned by SemantiK Architect
and the Defluens UI consumes it via the public CLI.

- **12/15** intents have an existing SA operation family to start implementing
  and testing (e.g., copular attribute, intransitive event, directive action).
- **3/15** need an explicit contract extension: `condition-real`,
  `source-attribution` and `conditional-instruction`.
- **0/15** are marked `bridge_verified` or `profile_released` merely because
  they appear in this registry. Existing operation family does not imply its
  tense, polarity, modality, temporal, quantity, lexical or composition
  features are accepted by a real PGF/profile.

## Next engineering steps (not implemented in v0.6)

1. Define typed semantic roles for conditional relations and attributed
   propositions in an ADR-reviewed SA↔GF minor contract version.
2. Build lexical binding strategies and GF abstract/concrete functions in the
   language engineering pipeline, backed by RGL (not prose string templates).
3. Extend the SA candidate suite with canonical structured requests for each
   intent, including variant and negative-path tests.
4. Run the real CandidateConformance path on exact, hashed PGF and bridge
   artifacts; do not equate WordBench standalone probe success with this gate.
5. Keep release orchestration in SemantiK Runtime Orchestrator, not Defluens.

This inventory is intentionally narrow to the user's 15 practical intents,
not an attempt to provide every grammatical tense/aspect of every language.
