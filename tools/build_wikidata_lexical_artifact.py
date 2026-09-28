from __future__ import annotations

import argparse
import json
from pathlib import Path

from semantik_architect.adapters.lexical.local_wikidata.lexeme_dump import (
    iter_json_records,
    lexical_artifact_entries_from_wikidata_record,
)
from semantik_architect.domain.language.lexical_policy import LexicalPolicy


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a deterministic SA lexical knowledge artifact from a local Wikidata Lexeme dump."
    )
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--language", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--lexicon-id", default=None)
    parser.add_argument(
        "--semantic-refs-file",
        type=Path,
        help="Optional newline-separated semantic refs/QIDs to retain.",
    )
    args = parser.parse_args()

    wanted = None
    if args.semantic_refs_file:
        wanted = set()
        for line in args.semantic_refs_file.read_text(encoding="utf-8").splitlines():
            value = line.strip()
            if value:
                wanted.add(value if ":" in value else f"wikidata:{value}")

    entries: list[dict] = []
    scanned = 0
    for record in iter_json_records(args.input):
        scanned += 1
        for entry in lexical_artifact_entries_from_wikidata_record(record, args.language):
            if wanted is None or entry["semantic_ref"] in wanted:
                entries.append(entry)

    entries.sort(
        key=lambda e: (
            e["language"],
            e["semantic_ref"],
            e.get("sense_ref", ""),
            e["lexical_ref"],
        )
    )
    payload = {
        "schema_version": "1.1",
        "lexicon_id": args.lexicon_id or f"wikidata-lexemes-{args.language}",
        "source_kind": "wikidata",
        "source_ref": str(args.input),
        "lexical_policy": LexicalPolicy().to_dict(),
        "entries": entries,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {"scanned_records": scanned, "entries": len(entries), "output": str(args.output)},
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
