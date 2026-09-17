import os
from contextlib import asynccontextmanager

import structlog
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.shared.container import container
from app.shared.config import settings
from app.adapters.api.routers import generation, health, languages, entities, frames, ai

logger = structlog.get_logger()


def _normalize_root_path(value: str | None) -> str:
    v = (value or "").strip()
    if not v or v == "/":
        return ""
    if not v.startswith("/"):
        v = "/" + v
    return v.rstrip("/")


def _parse_csv_env(name: str, default: list[str]) -> list[str]:
    raw = (os.getenv(name) or "").strip()
    if not raw:
        return default
    return [x.strip() for x in raw.split(",") if x.strip()]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runtime lifecycle: wire the application; no compiler queue or broker."""
    logger.info("app_startup", env=getattr(settings, "APP_ENV", "development"))
    container.wire(
        modules=[
            "app.adapters.api.routers.generation",
            "app.adapters.api.routers.health",
            "app.adapters.api.routers.languages",
            "app.adapters.api.routers.entities",
            "app.adapters.api.routers.frames",
            "app.adapters.api.routers.ai",
            "app.adapters.api.dependencies",
        ]
    )
    yield
    logger.info("app_shutdown")
    container.unwire()


def create_app() -> FastAPI:
    is_dev = getattr(settings, "APP_ENV", "development") == "development"
    app_name = getattr(settings, "APP_NAME", "Semantik Architect")
    root_path = _normalize_root_path(os.getenv("ARCHITECT_API_ROOT_PATH"))

    app = FastAPI(
        title=app_name,
        version="3.0.0-runtime",
        description="Semantik Architect runtime: semantic planning and text realization using precompiled GF/PGF assets.",
        lifespan=lifespan,
        root_path=root_path,
        docs_url="/docs" if is_dev else None,
        redoc_url=None,
    )

    default_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
    allow_origins = _parse_csv_env("ARCHITECT_CORS_ORIGINS", default_origins) if is_dev else _parse_csv_env("ARCHITECT_CORS_ORIGINS", [])
    allow_all = len(allow_origins) == 0
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if allow_all else allow_origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=600,
    )

    app.include_router(health.router)
    app.include_router(health.router, prefix="/api/v1")
    app.include_router(languages.router, prefix="/api/v1/languages", tags=["Languages"])
    app.include_router(entities.router, prefix="/api/v1/entities", tags=["Entities"])
    app.include_router(frames.router, prefix="/api/v1/entities", tags=["Entities"])
    app.include_router(frames.router, prefix="/api/v1/frames", tags=["Frames"])
    app.include_router(ai.router, prefix="/api/v1", tags=["AI"])
    app.include_router(generation.router, prefix="/api/v1")
    return app


def start():
    uvicorn.run(
        "app.adapters.api.main:create_app",
        host="0.0.0.0",
        port=8000,
        reload=getattr(settings, "APP_ENV", "development") == "development",
        factory=True,
    )


if __name__ == "__main__":
    start()
