from __future__ import annotations

from typing import Protocol


class _RuntimeValidator(Protocol):
    def validate(self, runtime_set_id: str) -> dict: ...


class ValidateRuntime:
    def __init__(self, validator: _RuntimeValidator) -> None:
        self.validator = validator

    def execute(self, runtime_set_id: str) -> dict:
        return self.validator.validate(runtime_set_id)
