# Session and Discourse State

Status: **normative**

## Purpose

SemantiK may retain small amounts of discourse state to support context-sensitive planning, reference choice, or continuity across generation requests.

## Contract

Session state is:

- optional;
- in-process;
- bounded;
- TTL-based;
- ephemeral;
- not shared automatically across API processes;
- not a durable database.

When exposed by the HTTP layer, `X-Session-ID` identifies the optional discourse context. The semantic frame remains valid without a session.

## Architectural rule

Session/context influences planning or reference choice **before realization**. It must not be implemented as ad hoc post-generation string rewriting.

## Non-goals

Session state is not:

- Redis-backed runtime coordination;
- a grammar compilation queue;
- a job broker;
- a persistent conversation database;
- a substitute for explicit semantic input.

Deployments that require durable or cross-process conversational state need a separately designed persistence contract.
