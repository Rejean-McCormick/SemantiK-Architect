from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class CapabilityProfile:
    profile_id: str
    profile_version: int
    required_operations: tuple[str,...]
    required_features: tuple[str,...]
    required_block_kinds: tuple[str,...]
    test_suite_ref: str

    @property
    def identity(self)->str: return f"{self.profile_id}-{self.profile_version}"
