from __future__ import annotations

from app.adapters.engines.construction_realizer import ConstructionRealizer
from app.adapters.engines.family_construction_adapter import FamilyConstructionAdapter
from app.adapters.engines.gf_construction_adapter import GFConstructionAdapter
from app.adapters.engines.language_capabilities import RuntimeLanguageCapabilities
from app.adapters.engines.pgf_runtime import PgfRuntime
from app.adapters.engines.safe_mode_construction_adapter import SafeModeConstructionAdapter
from app.adapters.persistence.filesystem_repo import FileSystemLexiconRepository
from app.adapters.persistence.lexicon.lexical_resolution import LexicalResolver
from app.core.use_cases.generate_text import GenerateText
from app.shared.config import settings


class RuntimeContainer:
    """Small explicit dependency graph for the application runtime.

    The project does not need a DI framework: dependencies are few, stable, and
    intentionally visible. Long-lived runtime services are cached; GenerateText
    remains a lightweight per-request facade.
    """

    def __init__(self) -> None:
        self._lexicon_repository: FileSystemLexiconRepository | None = None
        self._lexical_resolver: LexicalResolver | None = None
        self._pgf_runtime: PgfRuntime | None = None
        self._language_capabilities: RuntimeLanguageCapabilities | None = None
        self._construction_realizer: ConstructionRealizer | None = None

    def lexicon_repository(self) -> FileSystemLexiconRepository:
        if self._lexicon_repository is None:
            self._lexicon_repository = FileSystemLexiconRepository(
                base_path=settings.FILESYSTEM_REPO_PATH
            )
        return self._lexicon_repository

    def lexical_resolver(self) -> LexicalResolver:
        if self._lexical_resolver is None:
            self._lexical_resolver = LexicalResolver()
        return self._lexical_resolver

    def pgf_runtime(self) -> PgfRuntime:
        if self._pgf_runtime is None:
            self._pgf_runtime = PgfRuntime()
        return self._pgf_runtime

    def language_capabilities(self) -> RuntimeLanguageCapabilities:
        if self._language_capabilities is None:
            self._language_capabilities = RuntimeLanguageCapabilities(
                pgf_runtime=self.pgf_runtime()
            )
        return self._language_capabilities

    def construction_realizer(self) -> ConstructionRealizer:
        if self._construction_realizer is None:
            pgf_runtime = self.pgf_runtime()
            self._construction_realizer = ConstructionRealizer(
                gf_realizer=GFConstructionAdapter(engine=pgf_runtime),
                family_realizer=FamilyConstructionAdapter(),
                safe_mode_realizer=SafeModeConstructionAdapter(),
            )
        return self._construction_realizer

    def generate_text_use_case(self) -> GenerateText:
        return GenerateText(
            realizer=self.construction_realizer(),
            capabilities=self.language_capabilities(),
            lexical_resolver=self.lexical_resolver(),
        )

    def reset(self) -> None:
        """Drop cached runtime services, primarily for tests/reload tooling."""
        self._lexicon_repository = None
        self._lexical_resolver = None
        self._pgf_runtime = None
        self._language_capabilities = None
        self._construction_realizer = None


container = RuntimeContainer()

__all__ = ["RuntimeContainer", "container"]
