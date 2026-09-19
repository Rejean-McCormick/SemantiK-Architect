from __future__ import annotations

from typing import Any

from app.core.domain.models import SurfaceResult


def map_generation_response(
    result: Any,
    *,
    requested_lang_code: str | None = None,
) -> dict[str, Any]:
    """Serialize only the canonical SurfaceResult contract."""
    if not isinstance(result, SurfaceResult):
        raise RuntimeError(
            f"Generation result must be SurfaceResult, got {type(result).__name__}."
        )
    if requested_lang_code:
        requested = requested_lang_code.strip().lower().replace("_", "-")
        if result.lang_code != requested:
            raise RuntimeError(
                f"Generation language mismatch: requested {requested!r}, got {result.lang_code!r}."
            )
    return result.model_dump()


__all__ = ["map_generation_response"]
