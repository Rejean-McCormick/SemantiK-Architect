from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

_ALLOWED_BLOCKS=frozenset({"utterance","question","list","label_value","notice","heading"})

@dataclass(frozen=True, slots=True)
class PresentationConstraints:
    allowed_block_kinds: tuple[str, ...] = ("utterance","question","list","label_value","notice","heading")
    opening_policy: str = "allowed"
    closing_policy: str = "allowed"
    list_policy: str = "allowed"
    ordering_policy_ref: str | None = None
    terminology_profile_ref: str | None = None
    max_length: int | None = None
    output_format: str = "structured"

    def __post_init__(self) -> None:
        object.__setattr__(self,"allowed_block_kinds",tuple(self.allowed_block_kinds))
        unknown=set(self.allowed_block_kinds)-_ALLOWED_BLOCKS
        if unknown: raise ValueError(f"Unknown allowed_block_kinds: {sorted(unknown)}")
        if self.opening_policy not in {"forbidden","allowed","required"}: raise ValueError("invalid opening_policy")
        if self.closing_policy not in {"forbidden","allowed","required"}: raise ValueError("invalid closing_policy")
        if self.list_policy not in {"forbidden","allowed","preferred"}: raise ValueError("invalid list_policy")
        if self.output_format not in {"structured","plain_text","markdown"}: raise ValueError("invalid output_format")
        if self.max_length is not None and self.max_length <= 0: raise ValueError("max_length must be positive")

    @classmethod
    def from_dict(cls,data: Mapping[str,Any]) -> "PresentationConstraints":
        return cls(
            allowed_block_kinds=tuple(str(x) for x in data.get("allowed_block_kinds", _ALLOWED_BLOCKS)),
            opening_policy=str(data.get("opening_policy") or "allowed"),
            closing_policy=str(data.get("closing_policy") or "allowed"),
            list_policy=str(data.get("list_policy") or "allowed"),
            ordering_policy_ref=data.get("ordering_policy_ref"), terminology_profile_ref=data.get("terminology_profile_ref"),
            max_length=data.get("max_length"), output_format=str(data.get("output_format") or "structured")
        )

    def to_dict(self) -> dict[str,Any]:
        out={"allowed_block_kinds":list(self.allowed_block_kinds),"opening_policy":self.opening_policy,"closing_policy":self.closing_policy,"list_policy":self.list_policy,"output_format":self.output_format}
        if self.ordering_policy_ref: out["ordering_policy_ref"]=self.ordering_policy_ref
        if self.terminology_profile_ref: out["terminology_profile_ref"]=self.terminology_profile_ref
        if self.max_length is not None: out["max_length"]=self.max_length
        return out
