from __future__ import annotations
from ...domain.communication.request import CommunicationRequest
from ..validation.request_validation import RequestValidator
class ValidateRequest:
    def __init__(self)->None: self.validator=RequestValidator()
    def execute(self,request:CommunicationRequest)->dict:
        self.validator.validate(request); return {"valid":True,"request_id":request.request_id}
