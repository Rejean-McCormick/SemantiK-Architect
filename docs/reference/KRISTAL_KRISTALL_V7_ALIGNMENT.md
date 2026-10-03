# Kristal/Kristall v7 alignment

Status: **normative integration guidance**  
SemantiK Architect: `1.3.0-alpha.2`  
Portable Kristal contract: `kristal_state/6.0` / Standard `6.0.0`  
Kristal/Kristall design baseline: `7.0.0-draft.3.2`

## Decision

SemantiK Architect does not need a new raw-v7 ingress model. Kristall v7 is additive above the unchanged portable v6 artifact, so the existing `semantik.kristal-v6.communication-projection/1.0` remains the stable articulation boundary.

```text
Kristal/Kristall semantic authority
        | explicit communication selection/projection
        v
portable kristal_state/6.0 reference + selected assertions
        |
        v
semantik.kristal-v6.communication-projection/1.0
        | KristalV6Acl
        v
CommunicationRequest 1.0
        |
        v
SemantiK articulation pipeline
```

## DaaT

**DaaT** (`daat`) may be present upstream as the Interaction Kernel admission/contract-mapping boundary toward Kristal/Kristall. DaaT does not decide which assertions become communication obligations and does not author KQ/KP/KA/KS identity or crystallization for SA.

## Kompiler

Kompiler may provide read-only assembled context around a request. That context is advisory/supporting input only. `CommunicationRequest.obligations` remains the complete required-content authority for SA; context ranking/budgeting must never silently drop, add or reclassify obligations.

## Sources

EncyK discovers/acquires/extracts; Médiathèque persists source snapshots/representations. SA consumes neither system as a raw-content store. Provenance/source references may flow through explicit upstream projections.

## Compatibility invariant

No v7 KQ/KP/KA/KS, Mesh, axis, source-registry or crystallization object is imported into SA core. If a future direct v7 communication projection is required, it needs a new explicit versioned ACL contract and ADR; it must not silently reinterpret the existing v6 projection.
