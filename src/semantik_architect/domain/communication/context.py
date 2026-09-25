from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class CommunicationContext:
    target_language: str
    target_locale: str | None = None
    speaker_ref: str | None = None
    recipient_ref: str | None = None
    relationship: str | None = None
    formality: str | None = None
    politeness: str | None = None
    register: str | None = None
    tone_profile: str | None = None
    channel: str | None = None
    discourse_context: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        lang=str(self.target_language or "").strip()
        if len(lang) < 2:
            raise ValueError("target_language must be a non-empty language code")
        object.__setattr__(self,"target_language",lang)
        object.__setattr__(self,"discourse_context",dict(self.discourse_context))

    @classmethod
    def from_dict(cls,data: Mapping[str,Any]) -> "CommunicationContext":
        return cls(**{k:data.get(k) for k in (
            "target_language","target_locale","speaker_ref","recipient_ref","relationship","formality","politeness","register","tone_profile","channel"
        )}, discourse_context=data.get("discourse_context") or {})

    def to_dict(self) -> dict[str,Any]:
        out={"target_language":self.target_language}
        for k in ("target_locale","speaker_ref","recipient_ref","relationship","formality","politeness","register","tone_profile","channel"):
            v=getattr(self,k)
            if v is not None: out[k]=v
        if self.discourse_context: out["discourse_context"]=dict(self.discourse_context)
        return out
