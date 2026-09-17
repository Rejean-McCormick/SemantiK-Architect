from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.ports import IGrammarEngine
from app.shared.config import settings
from app.shared.container import Container

router = APIRouter()


class LanguageOut(BaseModel):
    code: str
    name: str
    z_id: Optional[str] = None


@lru_cache(maxsize=1)
def _runtime_language_metadata() -> dict[str, dict[str, str]]:
    """Optional presentation metadata; runtime capability comes from the PGF."""
    path = Path(settings.FILESYSTEM_REPO_PATH) / "runtime" / "languages.json"
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    out: dict[str, dict[str, str]] = {}
    items = raw if isinstance(raw, list) else raw.get("languages", []) if isinstance(raw, dict) else []
    for item in items:
        if not isinstance(item, dict):
            continue
        code = str(item.get("code", "")).strip().lower()
        if not code:
            continue
        out[code] = {
            "name": str(item.get("name", code)).strip() or code,
            "z_id": str(item.get("z_id", "")).strip(),
        }
    return out


@router.get("/", response_model=List[LanguageOut])
@inject
async def list_languages(
    engine: IGrammarEngine = Depends(Provide[Container.grammar_engine]),
) -> List[LanguageOut]:
    """List languages actually available in the loaded runtime grammar."""
    try:
        codes = await engine.get_supported_languages()
        meta = _runtime_language_metadata()
        result: list[LanguageOut] = []
        for raw in sorted({str(code).strip().lower() for code in codes if str(code).strip()}):
            details = meta.get(raw, {})
            result.append(
                LanguageOut(
                    code=raw,
                    name=details.get("name", raw),
                    z_id=details.get("z_id") or None,
                )
            )
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
