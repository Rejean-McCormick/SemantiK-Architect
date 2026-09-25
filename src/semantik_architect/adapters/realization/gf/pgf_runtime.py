from __future__ import annotations

import asyncio
import threading
from pathlib import Path
from typing import Any

import logging

try:
    import pgf  # type: ignore
except Exception as exc:  # pragma: no cover - environment dependent
    pgf = None  # type: ignore[assignment]
    _PGF_IMPORT_ERROR: Exception | None = exc
else:
    _PGF_IMPORT_ERROR = None

logger = logging.getLogger(__name__)


class PgfRuntimeUnavailableError(RuntimeError):
    """Raised when the configured PGF runtime cannot be loaded."""


class PgfConcreteLanguageNotFoundError(LookupError):
    """Raised when a concrete grammar is not present in the loaded PGF."""


class PgfRuntime:
    """Thread-safe, async-safe consumer of one precompiled PGF artifact."""

    def __init__(self, pgf_path: str | Path) -> None:
        self.pgf_path = Path(pgf_path).expanduser().resolve()
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
                    "PGF loaded: path=%s concrete_languages=%s",
                    self.pgf_path,
                    sorted(self._grammar.languages.keys()),
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
            raise PgfRuntimeUnavailableError(
                self.last_error or "PGF runtime is unavailable."
            )

    async def status(self) -> dict[str, Any]:
        try:
            await self.ensure_loaded()
        except PgfRuntimeUnavailableError:
            pass
        return {
            "loaded": self._grammar is not None,
            "pgf_path": str(self.pgf_path),
            "error": self.last_error,
            "concrete_languages": (
                sorted(self._grammar.languages.keys())
                if self._grammar is not None
                else []
            ),
        }

    async def get_concrete_languages(self) -> list[str]:
        await self.ensure_loaded()
        return sorted(self._grammar.languages.keys())

    async def health_check(self) -> bool:
        try:
            await self.ensure_loaded()
            return True
        except PgfRuntimeUnavailableError:
            return False

    async def reload(self) -> None:
        async with self._async_lock:
            with self._thread_lock:
                self._grammar = None
                self.last_error = None
        await self.ensure_loaded()

    def resolve_concrete_name(self, concrete_language: str) -> str | None:
        grammar = self.grammar
        if grammar is None:
            return None
        requested = str(concrete_language or "").strip()
        if requested in grammar.languages:
            return requested
        for name in grammar.languages:
            if name.casefold() == requested.casefold():
                return name
        return None

    def parse(self, sentence: str, concrete_language: str):
        grammar = self.grammar
        if grammar is None:
            raise PgfRuntimeUnavailableError(
                self.last_error or "PGF runtime is unavailable."
            )
        concrete = self.resolve_concrete_name(concrete_language)
        if concrete is None:
            raise PgfConcreteLanguageNotFoundError(concrete_language)
        return grammar.languages[concrete].parse(sentence)

    def linearize(self, expr: Any, concrete_language: str) -> str:
        grammar = self.grammar
        if grammar is None:
            raise PgfRuntimeUnavailableError(
                self.last_error or "PGF runtime is unavailable."
            )
        concrete = self.resolve_concrete_name(concrete_language)
        if concrete is None:
            raise PgfConcreteLanguageNotFoundError(concrete_language)
        if isinstance(expr, str):
            try:
                expr = pgf.readExpr(expr) if pgf is not None else expr
            except Exception as exc:
                raise ValueError(f"Invalid GF expression: {exc}") from exc
        return str(grammar.languages[concrete].linearize(expr))


__all__ = [
    "PgfRuntime",
    "PgfRuntimeUnavailableError",
    "PgfConcreteLanguageNotFoundError",
]
