# Communication Semantics Lock

Status: **LOCKED / normative**

## Fundamental rule

SA receives **what must be communicated**. It does not decide which obligations deserve to survive.

This is the defining product invariant.

## Obligation completeness

A successful request satisfies:

```text
input obligation set == discharged obligation set
```

Multiple obligations MAY be fused into one sentence. One obligation MAY require several surface units. A collection MAY become a list. None of these transformations authorize semantic deletion.

## Planning freedoms

SA MAY, when allowed by constraints/context:

- group compatible obligations;
- split dense content across multiple utterances;
- present homogeneous repeated content as a list;
- add a greeting or closing;
- add non-factual transitions;
- state deterministic derivations such as a count of explicitly supplied items;
- use pronouns/anaphora when referential identity remains unambiguous;
- choose a language-appropriate discourse order where upstream order is not semantically significant.

## Forbidden planning decisions

SA MUST NOT:

- rank tasks unless ranking is supplied;
- infer urgency from wording;
- omit “less important” content;
- convert uncertain content into fact;
- decide which side of an ethical argument is better;
- fabricate a missing deadline/contact/value;
- use external hidden knowledge to enrich domain facts;
- summarize by deletion unless the caller explicitly supplies a different obligation set for a summarization use case.

## Ordering semantics

Ordering has three states:

1. `FIXED` — upstream supplied order is semantically/operationally meaningful and MUST be preserved.
2. `POLICY` — upstream provides a named ordering policy/result; SA preserves the resulting order and may verbalize the policy if obligated.
3. `FREE` — ordering is communicatively neutral; SA may reorder for discourse naturalness.

SA MUST NOT convert `FREE` into a business ranking; it may only choose a presentation order.

## Deterministic derivations

A derivation MAY be spoken if all of the following hold:

- inputs are entirely present in the request;
- the derivation algorithm is deterministic and versioned;
- the derivation is semantics-preserving;
- no hidden business judgment is involved;
- provenance/coverage can identify the source inputs.

Examples:

- count four supplied tasks;
- render a supplied timestamp in the target locale;
- convert a supplied unit using an explicitly selected deterministic conversion rule.

Non-example:

- call a task “difficult” because its urgency is 6 unless the upstream semantic model defines/provides that relation.

## Non-factual discourse material

SA may generate conventional discourse framing authorized by profile/context:

- greetings;
- thanks/closings;
- list introductions;
- structural transitions;
- politeness particles;
- grammatical function words.

Such material MUST NOT imply new domain facts.

## Bounded communication vs. long-form authorship

SA may create several sentences and lists needed to discharge a bounded request. It does not perform open-ended editorial selection, chapter planning, article synthesis or narrative research.
