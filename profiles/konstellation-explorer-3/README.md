# Konstellation Explorer profile 3 — prototype

Goal: realize proposition sentences from typed semantic references rather than passing a complete upstream prose sentence as `patient`.

This profile is additive. It does not modify `konstellation-explorer-1`, `konstellation-explorer-2`, `konstellation-fr-1`, or `konstellation-fr-2`.

The prototype uses typed GF categories (`NP`, `V2`, `ClassNP`) and SemantiK Architect `gf_expr` bindings. Compile in this directory with:

    gf -make KonstellationFre.gf

The resulting `Konstellation.pgf` must then be released as a new RuntimeSet (`konstellation-fr-3`) through SemantiK Runtime Orchestrator. Do not reuse the expression-level fixture as a production PGF.
