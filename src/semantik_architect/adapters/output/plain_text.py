from __future__ import annotations
from ...domain.communication.result import CommunicationResult

def project_plain_text(result:CommunicationResult)->str:
    return result.plain_text or ""
