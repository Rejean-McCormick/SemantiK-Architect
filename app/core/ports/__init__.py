from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol, runtime_checkable

from .language_capabilities_port import LanguageCapabilitiesPort
from .lexical_resolver_port import LexicalResolverPort
from .planner_port import PlannerPort
from .realizer_port import RealizerCapabilitiesPort, RealizerPort, RealizerSupportStatus

JSONMapping = Mapping[str, Any]


@runtime_checkable
class LexiconRepo(Protocol):
    async def get_entry(self, lang: str, key: str) -> dict[str, Any] | None:
        ...

    async def save_entry(self, lang: str, entry: JSONMapping) -> None:
        ...

    async def health_check(self) -> bool:
        ...


__all__ = [
    "LanguageCapabilitiesPort",
    "LexicalResolverPort",
    "PlannerPort",
    "RealizerPort",
    "RealizerCapabilitiesPort",
    "RealizerSupportStatus",
    "LexiconRepo",
]
