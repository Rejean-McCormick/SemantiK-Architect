from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from ...domain.communication.request import CommunicationRequest


class KristalV6ProjectionError(ValueError):
    """Raised when a Kristal v6 communication projection is incomplete or untraceable."""


class KristalV6Acl:
    """Map an explicit Kristal v6 communication projection into CommunicationRequest.

    SemantiK Architect deliberately does not infer communicative obligations from a raw
    Kristal State. Upstream mapping (normally Da’at / an owner ACL) must select the
    assertions to communicate and provide a canonical CommunicationRequest projection.
    This adapter verifies traceability and preserves v6 role/valuation/actionability
    metadata as supporting context without changing the core semantic graph.
    """

    CONTRACT = "semantik.kristal-v6.communication-projection/1.0"
    STANDARD = "6.0.0"
    ACTIONABILITY_MODES = {
        "automatic",
        "human_review",
        "human_decision",
        "manual",
        "prohibited",
        "insufficient_information",
        "not_applicable",
    }

    @staticmethod
    def _source_refs(request: Mapping[str, Any]) -> set[str]:
        refs: set[str] = set()
        graph = request.get("semantic_graph")
        if isinstance(graph, Mapping):
            for statement in graph.get("statements", ()) or ():
                if isinstance(statement, Mapping):
                    refs.update(str(x) for x in (statement.get("source_refs") or ()))
        for obligation in request.get("obligations", ()) or ():
            if isinstance(obligation, Mapping):
                refs.update(str(x) for x in (obligation.get("source_refs") or ()))
        return refs

    @staticmethod
    def _support(subject_id: str, property_ref: str, value: Any) -> dict[str, Any]:
        return {"subject_id": subject_id, "property_ref": property_ref, "value": value}

    def map_request(
        self,
        payload: Mapping[str, Any],
        *,
        target_language: str,
        target_locale: str | None = None,
        capability_profile: str,
    ) -> CommunicationRequest:
        if payload.get("contract") != self.CONTRACT:
            raise KristalV6ProjectionError(f"Expected contract {self.CONTRACT}")
        if payload.get("kristal_standard") != self.STANDARD:
            raise KristalV6ProjectionError("Kristal Standard 6.0.0 is required")

        state_ref = payload.get("state_ref")
        if not isinstance(state_ref, Mapping):
            raise KristalV6ProjectionError("state_ref is required")
        if state_ref.get("artifact_type") != "kristal_state":
            raise KristalV6ProjectionError("state_ref.artifact_type must be kristal_state")
        if str(state_ref.get("schema_version")) != "6.0":
            raise KristalV6ProjectionError("state_ref.schema_version must be 6.0")
        state_id = str(state_ref.get("state_id") or "")
        if not state_id:
            raise KristalV6ProjectionError("state_ref.state_id is required")

        selected = payload.get("selected_assertions")
        if not isinstance(selected, list) or not selected:
            raise KristalV6ProjectionError("selected_assertions must be a non-empty array")
        assertion_ids: list[str] = []
        for item in selected:
            if not isinstance(item, Mapping):
                raise KristalV6ProjectionError("selected_assertions entries must be objects")
            assertion_id = str(item.get("assertion_id") or "")
            if not assertion_id:
                raise KristalV6ProjectionError("selected assertion_id is required")
            assertion_ids.append(assertion_id)
            actionability = item.get("actionability")
            if actionability is not None:
                if not isinstance(actionability, Mapping):
                    raise KristalV6ProjectionError("actionability must be an object")
                mode = actionability.get("mode")
                if mode not in self.ACTIONABILITY_MODES:
                    raise KristalV6ProjectionError(f"Unsupported actionability mode: {mode!r}")
            valuations = item.get("valuations")
            if valuations is not None and not isinstance(valuations, list):
                raise KristalV6ProjectionError("valuations must be an array")
        if len(assertion_ids) != len(set(assertion_ids)):
            raise KristalV6ProjectionError("selected_assertions must be unique")

        projected = payload.get("communication_request")
        if not isinstance(projected, Mapping):
            raise KristalV6ProjectionError("communication_request is required")
        request = deepcopy(dict(projected))
        if str(request.get("schema_version")) != "1.0":
            raise KristalV6ProjectionError("CommunicationRequest schema 1.0 is required")

        refs = self._source_refs(request)
        missing = [assertion_id for assertion_id in assertion_ids if assertion_id not in refs]
        if missing:
            raise KristalV6ProjectionError(
                "Every selected Kristal assertion must remain traceable through source_refs: "
                + ", ".join(missing)
            )

        context = dict(request.get("context") or {})
        context["target_language"] = target_language
        if target_locale is not None:
            context["target_locale"] = target_locale
        request["context"] = context
        request["capability_profile"] = capability_profile

        support = list(request.get("supporting_context") or [])
        support.append(self._support(state_id, "kristal-v6:artifact_status", state_ref.get("artifact_status")))
        if state_ref.get("applicability") is not None:
            support.append(self._support(state_id, "kristal-v6:applicability", state_ref.get("applicability")))
        if state_ref.get("content_hash") is not None:
            support.append(self._support(state_id, "kristal-v6:content_hash", state_ref.get("content_hash")))

        for item in selected:
            assertion_id = str(item["assertion_id"])
            for field, prop in (
                ("record_role", "kristal-v6:record_role"),
                ("valuations", "kristal-v6:valuations"),
                ("applicability", "kristal-v6:applicability"),
                ("actionability", "kristal-v6:actionability"),
            ):
                if item.get(field) is not None:
                    support.append(self._support(assertion_id, prop, item[field]))
        request["supporting_context"] = support

        return CommunicationRequest.from_dict(request)
