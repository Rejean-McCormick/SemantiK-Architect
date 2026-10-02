# MathKristal Formula IR Communication Projection

Status: **1.3 alpha contract / candidate**

## Boundary

Contract:

```text
semantik.mathkristal-formula-ir.communication-projection/1.0
```

Input mathematics is `mathkristal.formula-ir` version `1.0.0`. Formula IR remains an external MathKristal contract and terminates at the ACL. It is not imported into the SemantiK domain model.

## Required behavior

The ACL MUST:

1. validate Formula IR structure, closure, node references and binding scope;
2. reject natural-language/surface-form fields inside Formula IR;
3. require explicit selection of the expression or proposition to articulate;
4. project formula structure into canonical semantic nodes/statements;
5. preserve the selected source through statement/obligation `source_refs`;
6. create exactly one explicit `urn:mathkristal:communication:present-formula` articulation anchor;
7. preserve the validated Formula IR as request supporting context for the math realizer;
8. never infer mathematical truth, proof status, communicative force, or obligations from formula shape.

## Modes

- `PURE`: deterministic verbose MathCore-style verbalization.
- `NATURAL`: controlled Informath NLG variation, only when the RuntimeSet explicitly releases it.

The capability profile and requested mode MUST agree or planning fails.

## Kristal v6

If a MathKristal proposition exists in a Kristal v6 state, the Formula IR projection may be wrapped in `semantik.kristal-v6.communication-projection/1.0`. The selected assertion remains the authority anchor; Formula IR is an articulation representation, not a replacement state.
