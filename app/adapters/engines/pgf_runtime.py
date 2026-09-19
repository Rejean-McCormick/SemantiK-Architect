from __future__ import annotations

import asyncio
import json
import threading
from pathlib import Path
from typing import Any

import structlog

from app.core.domain.exceptions import DeploymentError, LanguageNotFoundError
from app.shared.config import settings

try:
    import pgf  # type: ignore
except Exception as exc:  # pragma: no cover - environment dependent
    pgf = None  # type: ignore[assignment]
    _PGF_IMPORT_ERROR: Exception | None = exc
else:
    _PGF_IMPORT_ERROR = None

logger = structlog.get_logger()


class PgfRuntime:
    """Low-level consumer of the deployed precompiled PGF artifact."""

    def __init__(self, pgf_path: str | None = None) -> None:
        configured = pgf_path or settings.PGF_PATH or "runtime/semantik_architect.pgf"
        path = Path(configured).expanduser()
        if not path.is_absolute():
            path = Path(settings.FILESYSTEM_REPO_PATH) / path
        self.pgf_path = path.resolve()
        self._grammar: Any | None = None
        self._async_lock = asyncio.Lock()
        self._thread_lock = threading.Lock()
        self.last_error: str | None = None

    @property
    def grammar(self) -> Any | None:
        if self._grammar is None:
            try:
                asyncio.get_running_loop()
            except RuntimeError:
                self._load_sync()
        return self._grammar

    def _load_sync(self) -> None:
        if self._grammar is not None:
            return
        with self._thread_lock:
            if self._grammar is not None:
                return
            if pgf is None:
                self.last_error = f"PGF Python binding unavailable: {_PGF_IMPORT_ERROR}"
                return
            if not self.pgf_path.is_file():
                self.last_error = f"PGF artifact not found: {self.pgf_path}"
                return
            try:
                self._grammar = pgf.readPGF(str(self.pgf_path))
                self.last_error = None
                logger.info(
                    "pgf_loaded",
                    path=str(self.pgf_path),
                    languages=sorted(self._grammar.languages.keys()),
                )
            except Exception as exc:
                self._grammar = None
                self.last_error = f"Could not load PGF artifact: {exc}"

    async def ensure_loaded(self) -> None:
        if self._grammar is not None:
            return
        async with self._async_lock:
            if self._grammar is None:
                await asyncio.to_thread(self._load_sync)
        if self._grammar is None:
            raise DeploymentError(self.last_error or "PGF runtime is unavailable.")

    async def status(self) -> dict[str, Any]:
        try:
            await self.ensure_loaded()
        except DeploymentError:
            pass
        return {
            "loaded": self._grammar is not None,
            "pgf_path": str(self.pgf_path),
            "error": self.last_error,
            "concrete_languages": (
                sorted(self._grammar.languages.keys()) if self._grammar is not None else []
            ),
        }

    async def get_concrete_languages(self) -> list[str]:
        await self.ensure_loaded()
        return sorted(self._grammar.languages.keys())

    async def health_check(self) -> bool:
        try:
            await self.ensure_loaded()
            return True
        except DeploymentError:
            return False

    async def reload(self) -> None:
        async with self._async_lock:
            with self._thread_lock:
                self._grammar = None
                self.last_error = None
        await self.ensure_loaded()

    def resolve_concrete_name(self, lang_code: str) -> str | None:
        grammar = self.grammar
        if grammar is None:
            return None
        requested = str(lang_code or "").strip()
        if requested in grammar.languages:
            return requested
        normalized = requested.lower().replace("_", "-")
        mapping = self._load_iso_to_wiki()
        concrete = mapping.get(normalized)
        if concrete in grammar.languages:
            return concrete
        # exact case-insensitive concrete match
        for name in grammar.languages:
            if name.lower() == normalized.lower():
                return name
        return None

    def parse(self, sentence: str, language: str):
        grammar = self.grammar
        if grammar is None:
            raise DeploymentError(self.last_error or "PGF runtime is unavailable.")
        concrete = self.resolve_concrete_name(language)
        if concrete is None:
            raise LanguageNotFoundError(language)
        return grammar.languages[concrete].parse(sentence)

    def linearize(self, expr: Any, language: str) -> str:
        grammar = self.grammar
        if grammar is None:
            raise DeploymentError(self.last_error or "PGF runtime is unavailable.")
        concrete = self.resolve_concrete_name(language)
        if concrete is None:
            raise LanguageNotFoundError(language)
        if isinstance(expr, str):
            try:
                expr = pgf.readExpr(expr) if pgf is not None else expr
            except Exception as exc:
                raise ValueError(f"Invalid GF expression: {exc}") from exc
        return str(grammar.languages[concrete].linearize(expr))

    def _load_iso_to_wiki(self) -> dict[str, str]:
        path = Path(settings.FILESYSTEM_REPO_PATH) / "data" / "config" / "iso_to_wiki.json"
        if not path.is_file():
            return {"en": "WikiEng", "eng": "WikiEng", "fr": "WikiFre", "fra": "WikiFre", "fre": "WikiFre"}
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
        out: dict[str, str] = {}
        if isinstance(raw, dict):
            for key, value in raw.items():
                k, v = str(key).strip(), str(value).strip()
                if not k or not v:
                    continue
                if v.startswith("Wiki"):
                    out[k.lower()] = v
                elif k.startswith("Wiki"):
                    out[v.lower()] = k
        return out


__all__ = ["PgfRuntime"]
