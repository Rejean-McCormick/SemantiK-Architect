from typing import Dict

import structlog
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Response, status

from app.core.ports import IGrammarEngine, LexiconRepo
from app.shared.container import Container

logger = structlog.get_logger()
router = APIRouter(prefix="/health", tags=["System"])


@router.get("/live", status_code=status.HTTP_200_OK)
async def liveness_probe():
    return {"status": "ok", "service": "semantik-architect"}


@router.get("/ready", status_code=status.HTTP_200_OK)
@inject
async def readiness_probe(
    response: Response,
    repo: LexiconRepo = Depends(Provide[Container.lexicon_repository]),
    engine: IGrammarEngine = Depends(Provide[Container.grammar_engine]),
) -> Dict[str, str]:
    """Readiness for the runtime-only application: storage + PGF engine."""
    health_status = {"storage": "down", "engine": "down"}

    try:
        if not hasattr(repo, "health_check") or await repo.health_check():
            health_status["storage"] = "up"
    except Exception as exc:
        logger.error("health_check_failed", component="storage", error=str(exc))

    try:
        if await engine.health_check():
            health_status["engine"] = "up"
    except Exception as exc:
        logger.error("health_check_failed", component="engine", error=str(exc))

    if not all(value == "up" for value in health_status.values()):
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        logger.warning("readiness_probe_failed", status=health_status)
    return health_status
