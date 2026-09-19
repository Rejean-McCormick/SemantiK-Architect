from __future__ import annotations

from typing import Dict

import structlog
from fastapi import APIRouter, Depends, Response, status

from app.adapters.api.dependencies import get_lexicon_repository, get_pgf_runtime
from app.adapters.engines.pgf_runtime import PgfRuntime
from app.adapters.persistence.filesystem_repo import FileSystemLexiconRepository

logger = structlog.get_logger()
router = APIRouter(prefix="/health", tags=["System"])


@router.get("/live", status_code=status.HTTP_200_OK)
async def liveness_probe() -> dict[str, str]:
    return {"status": "ok", "service": "semantik-architect"}


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_probe(
    response: Response,
    repo: FileSystemLexiconRepository = Depends(get_lexicon_repository),
    pgf_runtime: PgfRuntime = Depends(get_pgf_runtime),
) -> Dict[str, str]:
    health = {"lexicon": "down", "pgf": "down"}
    try:
        if await repo.health_check():
            health["lexicon"] = "up"
    except Exception as exc:
        logger.error("health_check_failed", component="lexicon", error=str(exc))
    try:
        if await pgf_runtime.health_check():
            health["pgf"] = "up"
    except Exception as exc:
        logger.error("health_check_failed", component="pgf", error=str(exc))
    if not all(value == "up" for value in health.values()):
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return health
