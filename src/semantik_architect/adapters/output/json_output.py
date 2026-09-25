from __future__ import annotations
from ...domain.communication.result import CommunicationResult
def project_json(result:CommunicationResult)->dict: return result.to_dict()
