# Math Pure 1 — candidate

This profile is the first SemantiK Architect mathematical articulation profile.

It consumes **MathKristal Formula IR 1.0.0** through the explicit
`semantik.mathkristal-formula-ir.communication-projection/1.0` ACL and emits one
`math.informalize_formula` realization operation. The operation is realized by a
pinned **Informath** runtime, which owns the MathCore/Informath/GF grammar.

`PURE` requests use the unique/verbose MathCore-style path. `NATURAL` requests may
request Informath variations. SemantiK Architect does not contain a parallel
French/English mathematical grammar.

This directory is a profile specification, **not a released RuntimeSet**.
Release requires a real Informath runtime, immutable artifact hashes, and passing
conformance evidence for every advertised language.
