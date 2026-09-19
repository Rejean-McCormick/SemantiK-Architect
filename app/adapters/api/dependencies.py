from __future__ import annotations

from app.adapters.engines.language_capabilities import RuntimeLanguageCapabilities
from app.adapters.engines.pgf_runtime import PgfRuntime
from app.adapters.persistence.filesystem_repo import FileSystemLexiconRepository
from app.core.use_cases.generate_text import GenerateText


def _get_container():
    from app.shared.container import container
    return container


def get_generate_text_use_case() -> GenerateText:
    return _get_container().generate_text_use_case()


def get_pgf_runtime() -> PgfRuntime:
    return _get_container().pgf_runtime()


def get_language_capabilities() -> RuntimeLanguageCapabilities:
    return _get_container().language_capabilities()


def get_lexicon_repository() -> FileSystemLexiconRepository:
    return _get_container().lexicon_repository()


__all__ = [
    "get_generate_text_use_case",
    "get_pgf_runtime",
    "get_language_capabilities",
    "get_lexicon_repository",
]
