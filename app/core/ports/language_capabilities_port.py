from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class LanguageCapabilitiesPort(Protocol):
    """Runtime language capabilities derived from the deployed PGF."""

    async def list_codes(self) -> list[str]:
        ...

    async def supports(self, lang_code: str) -> bool:
        ...


__all__ = ["LanguageCapabilitiesPort"]
