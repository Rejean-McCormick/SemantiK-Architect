# AI Implementation Guardrails

Status: **LOCKED / normative for AI-assisted development**

This file exists specifically to keep coding agents aligned with the architecture.

## Authority

An AI agent MUST treat the architecture locks and accepted ADRs as constraints, not suggestions.

If code and a lock conflict, the agent MUST assume the code is wrong unless an accepted newer ADR changes the lock.

## Mandatory behavior

An implementation agent MUST:

1. read the relevant lock before editing a module;
2. preserve dependency direction;
3. use the canonical domain terminology from the glossary;
4. add/modify tests for every behavioral contract change;
5. fail explicitly rather than invent fallback behavior;
6. keep language-specific behavior out of shared core logic;
7. keep GF/PGF types inside the GF adapter;
8. preserve obligation IDs through planning/output;
9. pin realization to immutable runtime identity;
10. update docs/schema/ADR before implementing an incompatible contract change.

## Forbidden “helpful” shortcuts

An AI agent MUST NOT:

- port classes merely because an earlier implementation contained them;
- create a compatibility shim to make old tests pass;
- add `if language == ...` branches to shared core code;
- add template/fallback English when GF fails;
- guess missing lexemes in production;
- silently turn supporting metadata into a communication obligation;
- silently drop an obligation to satisfy length/style constraints;
- put Orgo/eThikos/Kristal field names into generic domain types;
- add a new infrastructure framework to domain/application code;
- add microservices, queues, CQRS or Event Sourcing without an accepted ADR;
- make a remote API mandatory for canonical rendering;
- change a locked enum/contract by adding “just one string” without versioning.

## Ambiguity protocol

When the documentation does not resolve a design choice:

1. choose the smallest implementation that preserves all locks;
2. do not create a new architectural layer unless necessary;
3. mark the unresolved point as a design question;
4. if the choice changes a public/locked contract, require an ADR before coding it.

## Lock-change protocol for agents

Before changing any `*_LOCK.md` concept, an agent must identify:

- the problem that the current lock cannot solve;
- why an extension point is insufficient;
- affected schemas/contracts/tests;
- affected deployed contracts/artifacts;
- version transition policy;
- proposed ADR and version bump.

## AI-generated language work

AI may generate/review GF language source, lexicon entries and conformance vectors, but a language is not released because AI claims it is complete. Release authority is conformance evidence against the exact immutable artifact.

## Completion checklist

Before declaring a feature done, an AI agent should answer yes to:

- Does every new semantic input map through a canonical type rather than a domain leak?
- Are all obligations preserved?
- Is target-language behavior profile-driven rather than hardcoded?
- Does GF remain behind the bridge port?
- Are failure paths explicit?
- Are runtime identities recorded?
- Are tests aligned with the locked contracts?
