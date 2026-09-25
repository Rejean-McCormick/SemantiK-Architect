from __future__ import annotations

from typing import Any, Mapping, Protocol

from ...domain.communication.request import CommunicationRequest


class EcosystemAcl(Protocol):
    def map_request(
        self,
        payload: Mapping[str, Any],
        *,
        target_language: str,
        target_locale: str | None = None,
        capability_profile: str,
    ) -> CommunicationRequest: ...
