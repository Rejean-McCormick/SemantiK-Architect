from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Mapping

from ....application.ports.locale_data import LocaleDataPort
from ....application.ports.runtime_catalog import RuntimeSetDescriptor
from ....domain.communication.communication_plan import CommunicationPlan
from ....domain.communication.request import CommunicationRequest
from ....domain.errors import SemantikArchitectError
from ....domain.language.language_plan import LanguagePlan
from ....domain.language.lexical import (
    LexicalBinding,
    LexicalBindingSet,
    LexicalKnowledge,
    LexicalPlanningContext,
)
from ....domain.language.lexical_policy import (
    LexicalPolicy,
    VALID_LEXICAL_SOURCE_KINDS,
    VALID_LEXICAL_USES,
)
from ....domain.semantics.nodes import (
    CollectionValue,
    ConceptRef,
    EntityRef,
    LiteralValue,
    QuantityValue,
    TemporalValue,
)


@dataclass(frozen=True, slots=True)
class LexiconRecord:
    semantic_ref: str
    language: str
    lexical_ref: str
    binding_kind: str = "gf_expr"
    category: str | None = None
    properties: Mapping[str, Any] = field(default_factory=dict)
    source_kind: str = "project"
    use_for: str = "both"
    source_ref: str | None = None
    sense_ref: str | None = None


@dataclass(frozen=True, slots=True)
class LoadedLexicon:
    lexicon_id: str
    knowledge: Mapping[tuple[str, str], LexiconRecord]
    bindings: Mapping[tuple[str, str], LexiconRecord]
    policy: LexicalPolicy


class RuntimeJsonLexiconAdapter:
    """Resolve immutable lexical artifacts selected by a RuntimeSet.

    Lexical knowledge authority and executable realization bindings are resolved
    independently.  The default deterministic policy is::

        request_override > domain > project > wikidata > gf_generic

    A Wikidata Lexeme can therefore be the selected generic sense while a lower
    precedence GF generic entry supplies only the executable ``gf_expr``.
    Artifact iteration order never decides a collision.
    """

    def __init__(self, locale_data: LocaleDataPort | None = None) -> None:
        self._cache: dict[tuple[str, str], LoadedLexicon] = {}
        self.locale_data = locale_data

    @staticmethod
    def _same_record(a: LexiconRecord, b: LexiconRecord) -> bool:
        return (
            a.semantic_ref,
            a.language,
            a.lexical_ref,
            a.binding_kind,
            a.category,
            dict(a.properties),
            a.source_kind,
            a.use_for,
            a.source_ref,
            a.sense_ref,
        ) == (
            b.semantic_ref,
            b.language,
            b.lexical_ref,
            b.binding_kind,
            b.category,
            dict(b.properties),
            b.source_kind,
            b.use_for,
            b.source_ref,
            b.sense_ref,
        )

    @staticmethod
    def _admit(
        target: dict[tuple[str, str], LexiconRecord],
        key: tuple[str, str],
        rec: LexiconRecord,
        policy: LexicalPolicy,
        *,
        purpose: str,
        runtime_id: str,
    ) -> None:
        current = target.get(key)
        if current is None:
            target[key] = rec
            return
        new_rank = policy.rank(rec.source_kind)
        old_rank = policy.rank(current.source_kind)
        if new_rank > old_rank:
            target[key] = rec
            return
        if new_rank < old_rank:
            return
        if RuntimeJsonLexiconAdapter._same_record(current, rec):
            return
        raise SemantikArchitectError(
            "SA-LEX-003",
            f"Conflicting {purpose} lexical entries at equal precedence for {key[1]} in {key[0]}",
            runtime_set_id=runtime_id,
            details={
                "source_kind": rec.source_kind,
                "existing": {
                    "lexical_ref": current.lexical_ref,
                    "source_ref": current.source_ref,
                    "sense_ref": current.sense_ref,
                },
                "candidate": {
                    "lexical_ref": rec.lexical_ref,
                    "source_ref": rec.source_ref,
                    "sense_ref": rec.sense_ref,
                },
            },
        )

    def _load(self, runtime: RuntimeSetDescriptor) -> LoadedLexicon:
        key = (runtime.runtime_set_id, "lexical-v1.1")
        if key in self._cache:
            return self._cache[key]

        try:
            policy = LexicalPolicy.from_manifest(runtime.manifest)
        except ValueError as exc:
            raise SemantikArchitectError(
                "SA-LEX-001",
                "Invalid RuntimeSet lexical policy",
                runtime_set_id=runtime.runtime_set_id,
                details={"error": str(exc)},
            ) from exc

        knowledge: dict[tuple[str, str], LexiconRecord] = {}
        bindings: dict[tuple[str, str], LexiconRecord] = {}
        ids: list[str] = []

        # Stable artifact ordering aids reproducibility; precedence, never order,
        # decides which source wins.
        artifacts = sorted(runtime.artifacts_of_type("lexical"), key=lambda a: a.artifact_id)
        for art in artifacts:
            if art.path is None or not art.path.is_file():
                continue
            try:
                data = json.loads(art.path.read_text(encoding="utf-8"))
            except Exception as exc:
                raise SemantikArchitectError(
                    "SA-LEX-001",
                    f"Invalid lexical artifact {art.artifact_id}",
                    runtime_set_id=runtime.runtime_set_id,
                    details={"error": str(exc)},
                ) from exc

            if data.get("schema_version") not in {"1.0", "1.1"}:
                raise SemantikArchitectError(
                    "SA-LEX-001",
                    f"Unsupported lexical artifact schema in {art.artifact_id}",
                    runtime_set_id=runtime.runtime_set_id,
                )

            ids.append(str(data.get("lexicon_id") or art.artifact_id))
            artifact_source = str(data.get("source_kind") or policy.default_source_kind)
            artifact_source_ref = str(
                data.get("source_ref") or art.provenance_ref or art.artifact_id
            )
            if (
                artifact_source not in VALID_LEXICAL_SOURCE_KINDS
                or artifact_source not in policy.precedence
            ):
                raise SemantikArchitectError(
                    "SA-LEX-001",
                    f"Lexical source kind not admitted: {artifact_source}",
                    runtime_set_id=runtime.runtime_set_id,
                )

            rows = data.get("entries", [])
            if not isinstance(rows, list):
                raise SemantikArchitectError(
                    "SA-LEX-001",
                    f"Lexical artifact entries must be an array in {art.artifact_id}",
                )
            for raw in rows:
                try:
                    source_kind = str(raw.get("source_kind") or artifact_source)
                    use_for = str(raw.get("use_for") or "both")
                    if (
                        source_kind not in VALID_LEXICAL_SOURCE_KINDS
                        or source_kind not in policy.precedence
                    ):
                        raise ValueError(f"source_kind={source_kind}")
                    if use_for not in VALID_LEXICAL_USES:
                        raise ValueError(f"use_for={use_for}")
                    default_binding = (
                        "lexeme_ref"
                        if source_kind == "wikidata" and use_for == "knowledge"
                        else "gf_expr"
                    )
                    rec = LexiconRecord(
                        semantic_ref=str(raw["semantic_ref"]),
                        language=str(raw["language"]),
                        lexical_ref=str(raw["lexical_ref"]),
                        binding_kind=str(raw.get("binding_kind") or default_binding),
                        category=raw.get("category"),
                        properties=dict(raw.get("properties") or {}),
                        source_kind=source_kind,
                        use_for=use_for,
                        source_ref=str(raw.get("source_ref") or artifact_source_ref),
                        sense_ref=(
                            str(raw["sense_ref"]) if raw.get("sense_ref") else None
                        ),
                    )
                except Exception as exc:
                    raise SemantikArchitectError(
                        "SA-LEX-001",
                        f"Invalid lexical record in {art.artifact_id}",
                        details={"record": raw, "error": str(exc)},
                    ) from exc

                record_key = (rec.language, rec.semantic_ref)
                if rec.use_for in {"knowledge", "both"}:
                    self._admit(
                        knowledge,
                        record_key,
                        rec,
                        policy,
                        purpose="knowledge",
                        runtime_id=runtime.runtime_set_id,
                    )
                if rec.use_for in {"binding", "both"}:
                    if rec.binding_kind not in {"gf_expr", "literal"}:
                        if rec.binding_kind == "lexeme_ref":
                            # Deliberately knowledge-only: a Wikidata sense ID is
                            # not an executable GF expression.
                            continue
                        raise SemantikArchitectError(
                            "SA-LEX-001",
                            f"Unsupported lexical binding kind: {rec.binding_kind}",
                            runtime_set_id=runtime.runtime_set_id,
                        )
                    self._admit(
                        bindings,
                        record_key,
                        rec,
                        policy,
                        purpose="binding",
                        runtime_id=runtime.runtime_set_id,
                    )

        loaded = LoadedLexicon(
            "+".join(ids) or "none",
            knowledge,
            bindings,
            policy,
        )
        self._cache[key] = loaded
        return loaded

    def validate_runtime(self, runtime: RuntimeSetDescriptor) -> dict[str, Any]:
        loaded = self._load(runtime)
        return {
            "lexicon_id": loaded.lexicon_id,
            "knowledge_entries": len(loaded.knowledge),
            "binding_entries": len(loaded.bindings),
            "lexical_policy": loaded.policy.to_dict(),
        }

    @staticmethod
    def _node_semantic_ref(request: CommunicationRequest, ref: str) -> str | None:
        try:
            obj = request.semantic_graph.get(ref)
        except KeyError:
            return ref if ":" in ref else None
        if isinstance(obj, EntityRef):
            return obj.external_ref
        if isinstance(obj, ConceptRef):
            return obj.concept_ref
        return ref

    def _surface_literal(self, request: CommunicationRequest, ref: str, *, _stack: tuple[str, ...] = (), _budget: list[int] | None = None) -> str | None:
        budget = _budget if _budget is not None else [0]
        budget[0] += 1
        if ref in _stack or len(_stack) > 32 or budget[0] > 10000:
            raise SemantikArchitectError("SA-REQ-001", "Cyclic or excessive semantic collection", request_id=request.request_id)
        try:
            obj = request.semantic_graph.get(ref)
        except KeyError:
            return None
        if request.capability_profile == "konstellation-explorer-1":
            from .konstellation import statement_literal
            explorer_value = statement_literal(request, ref)
            if explorer_value is not None:
                return explorer_value
        lang = request.context.target_language
        locale = request.context.target_locale
        if isinstance(obj, EntityRef):
            return (obj.labels.get(locale or "") or obj.labels.get(lang) or obj.labels.get(lang.split("-", 1)[0]))
        if isinstance(obj, LiteralValue):
            return self.locale_data.format_value(obj.value, language=lang, locale=locale, datatype=obj.datatype) if self.locale_data else str(obj.value)
        if isinstance(obj, QuantityValue):
            base = self.locale_data.format_value(obj.value, language=lang, locale=locale, datatype="quantity") if self.locale_data else str(obj.value)
            return f"{base} {obj.unit_ref}" if obj.unit_ref else base
        if isinstance(obj, TemporalValue):
            return self.locale_data.format_value(obj.value, language=lang, locale=locale, datatype=obj.temporal_kind) if self.locale_data else str(obj.value)
        if isinstance(obj, CollectionValue):
            values=[]
            for member in obj.members:
                value=self._surface_literal(request, member, _stack=(*_stack, ref), _budget=budget)
                if value is None:
                    return None
                values.append(value)
            return ", ".join(values)
        return None

    def preflight(
        self,
        request: CommunicationRequest,
        plan: CommunicationPlan,
        runtime: RuntimeSetDescriptor,
    ) -> LexicalPlanningContext:
        loaded = self._load(runtime)
        lang = request.context.target_language
        semantic_refs: set[str] = set()
        for item in plan.items:
            for ref in item.semantic_refs:
                obj = request.semantic_graph.get(ref)
                if hasattr(obj, "arguments"):
                    semantic_refs.add(getattr(obj, "predicate_ref"))
                    for arg in obj.arguments:
                        semantic_refs.add(
                            self._node_semantic_ref(request, arg.value_id) or arg.value_id
                        )
                        semantic_refs.add(arg.value_id)
                else:
                    semantic_refs.add(self._node_semantic_ref(request, ref) or ref)

        entries: dict[str, LexicalKnowledge] = {}
        for ref in semantic_refs:
            semantic_ref = self._node_semantic_ref(request, ref) or ref
            rec = loaded.knowledge.get((lang, semantic_ref))
            surface = self._surface_literal(request, ref)
            if rec:
                entries[ref] = LexicalKnowledge(
                    ref,
                    lang,
                    True,
                    (rec.lexical_ref,),
                    rec.category,
                    rec.properties,
                    rec.source_kind,
                    rec.source_ref,
                    rec.sense_ref,
                )
                if semantic_ref != ref:
                    entries[semantic_ref] = entries[ref]
            elif surface is not None:
                entries[ref] = LexicalKnowledge(
                    ref,
                    lang,
                    True,
                    (surface,),
                    "LITERAL",
                    {"binding_kind": "literal"},
                    "request_override",
                    "semantic_graph",
                    None,
                )
                if semantic_ref != ref:
                    entries[semantic_ref] = entries[ref]
            else:
                # If no semantic dictionary knows the concept, a binding-capable
                # GF generic entry remains an explicit deterministic fallback.
                fallback = loaded.bindings.get((lang, semantic_ref))
                if fallback:
                    entries[ref] = LexicalKnowledge(
                        ref,
                        lang,
                        True,
                        (fallback.lexical_ref,),
                        fallback.category,
                        fallback.properties,
                        fallback.source_kind,
                        fallback.source_ref,
                        fallback.sense_ref,
                    )
                    if semantic_ref != ref:
                        entries[semantic_ref] = entries[ref]
                else:
                    entries[ref] = LexicalKnowledge(ref, lang, False, (), None, {})
                    if semantic_ref != ref:
                        entries[semantic_ref] = entries[ref]
        return LexicalPlanningContext(lang, entries, (loaded.lexicon_id,))

    def bind(
        self,
        request: CommunicationRequest,
        plan: LanguagePlan,
        lexical_context: LexicalPlanningContext,
        runtime: RuntimeSetDescriptor,
    ) -> LexicalBindingSet:
        loaded = self._load(runtime)
        out: list[LexicalBinding] = []
        lang = request.context.target_language
        for unit in plan.units:
            for slot, ref in unit.lexical_slots.items():
                semantic_ref = self._node_semantic_ref(request, ref) or ref
                rec = loaded.bindings.get((lang, semantic_ref))
                if rec:
                    out.append(
                        LexicalBinding(
                            unit.unit_id,
                            slot,
                            rec.lexical_ref,
                            rec.binding_kind,
                            semantic_ref,
                            rec.source_kind,
                            rec.source_ref,
                            rec.sense_ref,
                        )
                    )
                    continue
                surface = self._surface_literal(request, ref)
                if surface is not None:
                    out.append(
                        LexicalBinding(
                            unit.unit_id,
                            slot,
                            surface,
                            "literal",
                            semantic_ref,
                            "request_override",
                            "semantic_graph",
                            None,
                        )
                    )
                    continue
                rec = loaded.bindings.get((lang, ref))
                if rec:
                    out.append(
                        LexicalBinding(
                            unit.unit_id,
                            slot,
                            rec.lexical_ref,
                            rec.binding_kind,
                            ref,
                            rec.source_kind,
                            rec.source_ref,
                            rec.sense_ref,
                        )
                    )
                    continue
                knowledge = lexical_context.entries.get(ref) or lexical_context.entries.get(
                    semantic_ref
                )
                raise SemantikArchitectError(
                    "SA-LEX-002",
                    f"No exact lexical binding for {ref} in {lang}",
                    request_id=request.request_id,
                    runtime_set_id=runtime.runtime_set_id,
                    details={
                        "unit_id": unit.unit_id,
                        "slot": slot,
                        "semantic_ref": semantic_ref,
                        "knowledge_source_kind": (
                            knowledge.source_kind if knowledge else None
                        ),
                        "knowledge_source_ref": knowledge.source_ref if knowledge else None,
                    },
                )
        return LexicalBindingSet(loaded.lexicon_id, tuple(out))
