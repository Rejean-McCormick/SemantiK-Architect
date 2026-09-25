from __future__ import annotations

from typing import Any, Mapping

from ...domain.communication.request import CommunicationRequest


class CanonicalAcl:
    """Boundary adapter for callers that already speak the canonical schema."""

    def map_request(self, payload: Mapping[str, Any], **_: Any) -> CommunicationRequest:
        return CommunicationRequest.from_dict(payload)
