from dependency_injector import containers, providers

from app.shared.config import settings
from app.adapters.llm_adapter import GeminiAdapter
from app.adapters.persistence.filesystem_repo import FileSystemLexiconRepository
from app.adapters.engines.gf_wrapper import GFGrammarEngine
from app.adapters.engines.python_engine_wrapper import PythonGrammarEngine
from app.core.use_cases.generate_text import GenerateText


class Container(containers.DeclarativeContainer):
    """Runtime-only dependency injection container.

    SemantiK Architect consumes a precompiled PGF artifact. Grammar source
    development, compilation, repair, audit, and onboarding are outside this
    application boundary.
    """

    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.adapters.api.routers.generation",
            "app.adapters.api.routers.languages",
            "app.adapters.api.routers.health",
            "app.adapters.api.dependencies",
        ]
    )

    config = providers.Object(settings)

    lexicon_repository = providers.Singleton(
        FileSystemLexiconRepository,
        base_path=settings.FILESYSTEM_REPO_PATH,
    )

    if settings.USE_MOCK_GRAMMAR:
        grammar_engine = providers.Singleton(PythonGrammarEngine)
    else:
        grammar_engine = providers.Singleton(GFGrammarEngine)

    llm_adapter = providers.Factory(GeminiAdapter)
    generate_text_use_case = providers.Factory(GenerateText, engine=grammar_engine)


container = Container()
