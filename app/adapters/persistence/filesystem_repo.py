import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiofiles
import structlog

from app.core.domain.models import LexiconEntry
from app.core.ports import LexiconRepo

logger = structlog.get_logger()


class FileSystemLexiconRepository(LexiconRepo):
    """Runtime lexical storage. It does not scaffold languages or persist GF source."""

    def __init__(self, base_path: str):
        self.root = Path(base_path).resolve()
        self.lexicon_base = self.root / "data" / "lexicon"
        self.lexicon_base.mkdir(parents=True, exist_ok=True)

    def _get_file_path(self, lang_code: str) -> Path:
        return self.lexicon_base / lang_code / "lexicon.json"

    async def _load_file(self, lang_code: str) -> Dict[str, Any]:
        path = self._get_file_path(lang_code)
        if not path.exists():
            return {}
        try:
            async with aiofiles.open(path, mode="r", encoding="utf-8") as handle:
                content = await handle.read()
                return json.loads(content) if content else {}
        except Exception as exc:
            logger.error("repo_read_failed", lang=lang_code, error=str(exc))
            return {}

    async def _save_file(self, lang_code: str, data: Dict[str, Any]) -> None:
        path = self._get_file_path(lang_code)
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            async with aiofiles.open(path, mode="w", encoding="utf-8") as handle:
                await handle.write(json.dumps(data, indent=2, ensure_ascii=False))
        except Exception as exc:
            logger.error("repo_write_failed", lang=lang_code, error=str(exc))
            raise IOError(f"Could not save lexicon for {lang_code}") from exc

    async def get_entry(self, lang: str, key: str) -> Optional[LexiconEntry]:
        data = await self._load_file(lang)
        raw_entry = data.get(key)
        return LexiconEntry(**raw_entry) if raw_entry else None

    async def save_entry(self, lang: str, entry: LexiconEntry) -> None:
        data = await self._load_file(lang)
        try:
            value = entry.model_dump()
        except AttributeError:
            value = entry.dict()
        key = entry.lemma if entry.lemma else entry.word
        data[key] = value
        await self._save_file(lang, data)
        logger.info("lexicon_entry_saved", lang=lang, lemma=key)

    async def get_entries_by_concept(self, lang_code: str, qid: str) -> List[LexiconEntry]:
        data = await self._load_file(lang_code)
        results: list[LexiconEntry] = []
        for raw_entry in data.values():
            entry_qid = raw_entry.get("qid") or raw_entry.get("wikidata_qid")
            if not entry_qid:
                entry_qid = (raw_entry.get("features") or {}).get("qid")
            if entry_qid == qid:
                results.append(LexiconEntry(**raw_entry))
        return results

    async def health_check(self) -> bool:
        try:
            self.lexicon_base.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as exc:
            logger.error("storage_health_check_failed", error=str(exc))
            return False
