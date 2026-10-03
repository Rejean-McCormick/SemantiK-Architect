# ADR-0015 — Kristall v7 ecosystem boundary

**Status:** Accepted  
**Date:** 2026-10-03

## Decision

SemantiK Architect retains `semantik.kristal-v6.communication-projection/1.0` as its stable portable Kristal ingress while aligning to Kristal/Kristall `7.0.0-draft.3.2`. Kristall v7 is additive above `kristal_state/6.0`; no raw v7 semantic registry is imported into SA core.

DaaT (`daat`) is not the authority for communication selection. Kompiler may supply read-only context but cannot create or remove obligations. EncyK/Médiathèque source acquisition/storage remain upstream and outside SA.

Any future direct v7 SA projection requires a new versioned ACL contract plus an ADR.
