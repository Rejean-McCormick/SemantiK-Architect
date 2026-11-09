# SemantiK Architect — Defluens core acceptance v0.10

The existing **`compose_core_request`** mapper and **`RequestValidator`** remain
sole authorities for the six-operation French/English development profile.

New public CLI:

```powershell
$env:PYTHONPATH = 'src'
python -m semantik_architect.adapters.inbound.cli.main defluens-core-batch C:\path\to\vectors.json
```

Input: `{"vectors":[{"case_id":"fr:attribute:positive","recipe":{"language":"fr","items":[...]}}]}`.
Up to 48 uniquely identified vectors, capped at 100 kB. Every vector is
validated through the existing canonical request mapper + validator. The
output supplies per-vector success/refusal and the canonical request on success.
A failure is reported explicitly; unknown concepts do not trigger fallbacks.

This command **does not** invoke a GF grammar, a runtime planner, or a
RuntimeSet publisher. It does not prove grammatical fidelity. Defluens checks
its own 36-vector matrix against this public response. Realization belongs to
the existing `preview-candidate` API and needs a locked candidate prepared by
WordBench. Both paths are development-only; no runtime activation is implied.
