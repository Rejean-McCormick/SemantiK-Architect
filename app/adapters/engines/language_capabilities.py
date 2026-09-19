from __future__ import annotations

import json
from pathlib import Path

from app.adapters.engines.pgf_runtime import PgfRuntime
from app.shared.config import settings


class RuntimeLanguageCapabilities:
    """Application language capabilities derived only from loaded PGF concretes."""

    def __init__(self, pgf_runtime: PgfRuntime) -> None:
        self.pgf_runtime = pgf_runtime

    async def list_codes(self) -> list[str]:
        concretes = await self.pgf_runtime.get_concrete_languages()
        mapping = self._concrete_to_application()
        missing = sorted(name for name in concretes if name not in mapping)
        if missing:
            raise RuntimeError(
                "Loaded PGF concrete languages lack application mappings: "
                + ", ".join(missing)
            )
        return sorted({mapping[name] for name in concretes})

    async def supports(self, lang_code: str) -> bool:
        normalized = str(lang_code or "").strip().lower().replace("_", "-")
        return normalized in set(await self.list_codes())

    def concrete_for(self, lang_code: str) -> str | None:
        normalized = str(lang_code or "").strip().lower().replace("_", "-")
        for concrete, app_code in self._concrete_to_application().items():
            if app_code == normalized:
                return concrete
        return None

    def _concrete_to_application(self) -> dict[str, str]:
        path = Path(settings.FILESYSTEM_REPO_PATH) / "data" / "config" / "iso_to_wiki.json"
        out: dict[str, str] = {"WikiEng": "en", "WikiFre": "fr"}
        if not path.is_file():
            return out
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return out
        if isinstance(raw, dict):
            for key, value in raw.items():
                k, v = str(key).strip(), str(value).strip()
                if not k or not v:
                    continue
                if v.startswith("Wiki"):
                    candidate = k.lower().replace("_", "-")
                    current = out.get(v)
                    if current is None or (len(candidate) == 2 and len(current) != 2):
                        out[v] = candidate
                elif k.startswith("Wiki"):
                    candidate = v.lower().replace("_", "-")
                    current = out.get(k)
                    if current is None or (len(candidate) == 2 and len(current) != 2):
                        out[k] = candidate
        return out


__all__ = ["RuntimeLanguageCapabilities"]
