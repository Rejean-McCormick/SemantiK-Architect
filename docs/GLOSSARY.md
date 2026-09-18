# Glossary

Status: **canonical terminology**

## Application language code

The language identifier used by SemantiK API/domain/runtime code, for example `en` or `fr`.

## Canonical frame

A validated semantic domain object with an explicit `frame_type` and one documented shape for that frame family.

## Concrete language

A concrete grammar name exposed by the loaded PGF, for example `WikiEng` or `WikiFre`.

## Construction

A reusable sentence/clause realization pattern selected by the planner and identified by `construction_id`.

## ConstructionPlan

The canonical renderer input. It carries a construction ID, language, semantic slot map, generation options, and runtime metadata.

## Frame

Structured semantic input describing what the application should express before sentence construction and surface realization.

## GF

Grammatical Framework. In SemantiK it is a realization technology consumed through a precompiled PGF artifact.

## Lexical resolution

The runtime stage that binds semantic/construction slots to language-appropriate lexical material before realization.

## Ninai adapter

An optional input adapter for function-style/Ninai semantic structures. It normalizes into the canonical SemantiK domain model before planning.

## PGF

Portable Grammar Format, the compiled GF runtime artifact consumed by SemantiK.

## PlannedSentence

The planner output describing a planned sentence/construction before final renderer handoff.

## Planner-first

The architectural rule that construction and information-structure decisions are made before renderer realization.

## Renderer

A backend that consumes `ConstructionPlan` and returns `SurfaceResult`. GF/PGF and family/construction renderers are examples.

## Runtime capability

A language/construction capability that is actually available from deployed runtime artifacts and data, not merely listed as a development target.

## SurfaceResult

The canonical generation result containing text, language, construction, renderer, fallback status, tokens, diagnostics, and generation time.
