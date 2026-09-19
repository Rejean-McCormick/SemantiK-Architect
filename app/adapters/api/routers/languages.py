from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.adapters.api.dependencies import get_language_capabilities
from app.adapters.engines.language_capabilities import RuntimeLanguageCapabilities
from app.shared.config import settings

router = APIRouter()


class LanguageOut(BaseModel):
    code: str
    name: str
    z_id: Optional[str] = None


def _metadata() -> dict[str, dict[str, str]]:
    path = Path(settings.FILESYSTEM_REPO_PATH) / "runtime" / "languages.json"
    if not path.is_file():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    items = raw if isinstance(raw, list) else raw.get("languages", []) if isinstance(raw, dict) else []
    out: dict[str, dict[str, str]] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        code = str(item.get("code") or "").strip().lower()
        if code:
            out[code] = {
                "name": str(item.get("name") or code),
                "z_id": str(item.get("z_id") or ""),
            }
    return out


@router.get("/", response_model=List[LanguageOut])
async def list_languages(
    capabilities: RuntimeLanguageCapabilities = Depends(get_language_capabilities),
) -> List[LanguageOut]:
    try:
        meta = _metadata()
        return [
            LanguageOut(
                code=code,
                name=meta.get(code, {}).get("name", code),
                z_id=meta.get(code, {}).get("z_id") or None,
            )
            for code in await capabilities.list_codes()
        ]
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
