from __future__ import annotations

from typing import Any, Dict, NoReturn, Optional

import structlog
from fastapi import APIRouter, Body, Depends, Header, HTTPException, status

from app.adapters.api.contracts.generation_request_mapper import map_generation_request
from app.adapters.api.contracts.generation_response_mapper import map_generation_response
from app.adapters.api.dependencies import get_generate_text_use_case
from app.adapters.persistence.session_store import session_store
from app.core.domain.context import DiscourseEntity
from app.core.domain.exceptions import (
    DomainError,
    InvalidFrameError,
    LanguageNotFoundError,
    UnsupportedFrameTypeError,
)
from app.core.domain.frame import BioFrame
from app.core.domain.models import SurfaceResult
from app.core.use_cases.generate_text import GenerateText

logger = structlog.get_logger()
router = APIRouter(prefix="/generate", tags=["Generation"])


@router.post(
    "/{lang_code}",
    response_model=SurfaceResult,
    status_code=status.HTTP_200_OK,
    summary="Generate text from a canonical semantic frame",
)
async def generate_text(
    lang_code: str,
    payload: Dict[str, Any] = Body(...),
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    use_case: GenerateText = Depends(get_generate_text_use_case),
) -> dict[str, Any]:
    try:
        mapped = map_generation_request(payload, path_lang_code=lang_code)
        frame = mapped.frame
        if x_session_id and isinstance(frame, BioFrame):
            await _apply_discourse_context(x_session_id, frame)
        result = await use_case.execute(mapped.lang_code, frame)
        return map_generation_response(result, requested_lang_code=mapped.lang_code)
    except Exception as exc:
        _raise_generation_http_exception(exc, lang=lang_code)


def _raise_generation_http_exception(exc: Exception, *, lang: Optional[str]) -> NoReturn:
    if isinstance(exc, (InvalidFrameError, UnsupportedFrameTypeError, ValueError)):
        logger.warning("generation_bad_request", lang=lang, error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        )
    if isinstance(exc, LanguageNotFoundError):
        logger.warning("generation_language_not_found", lang=lang, error=str(exc))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, DomainError):
        logger.error("generation_runtime_error", lang=lang, error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Generation failed: {exc}",
        )
    logger.critical("unexpected_generation_crash", lang=lang, error=str(exc), exc_info=True)
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An unexpected error occurred during text generation.",
    )


def _extract_subject_qid(frame: BioFrame) -> Optional[str]:
    subj = frame.subject
    if isinstance(subj, dict):
        value = subj.get("qid")
    else:
        value = getattr(subj, "qid", None)
    return value.strip() if isinstance(value, str) and value.strip() else None


def _normalize_discourse_gender(value: Any) -> str:
    normalized = str(value or "").strip().lower()
    return {
        "m": "m", "male": "m", "masculine": "m",
        "f": "f", "female": "f", "feminine": "f",
        "n": "n", "neuter": "n", "c": "c", "common": "c",
    }.get(normalized, "n")


async def _apply_discourse_context(session_id: str, frame: BioFrame) -> None:
    context = await session_store.get_session(session_id)
    subject_qid = _extract_subject_qid(frame)
    if not subject_qid:
        return

    original_label = frame.name
    if context.current_focus and context.current_focus.qid == subject_qid:
        gender = str(getattr(context.current_focus, "gender", "") or "").lower()
        frame.name = "She" if gender in {"f", "female"} else "He" if gender in {"m", "male"} else "It"

    new_entity = DiscourseEntity(
        label=original_label or frame.name,
        gender=_normalize_discourse_gender(frame.gender),
        qid=subject_qid,
        recency=0,
    )
    context.update_focus(new_entity)
    await session_store.save_session(context)


__all__ = ["router", "generate_text"]
