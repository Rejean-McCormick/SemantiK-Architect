from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a pinned SemantiK Architect RuntimeSet manifest")
    parser.add_argument("--runtime-dir", required=True)
    parser.add_argument("--runtime-set-id", required=True)
    parser.add_argument("--sa-version-range", default=">=1.0,<2.0")
    parser.add_argument("--contract-version", default="1.0")
    parser.add_argument("--capabilities", default="capabilities.json")
    parser.add_argument("--evidence", action="append", default=[])
    parser.add_argument(
        "--artifact",
        action="append",
        default=[],
        help="type:id:path (type is grammar|lexical|locale|other)",
    )
    parser.add_argument("--status", choices=["CANDIDATE", "RELEASED", "RETIRED"], default="CANDIDATE")
    parser.add_argument("--output", default="runtime.manifest.json")
    args = parser.parse_args()

    root = Path(args.runtime_dir).resolve()
    capability_path = (root / args.capabilities).resolve()
    if not capability_path.is_file():
        raise SystemExit(f"capability manifest not found: {capability_path}")

    artifacts = []
    for spec in args.artifact:
        try:
            artifact_type, artifact_id, rel = spec.split(":", 2)
        except ValueError as exc:
            raise SystemExit(f"invalid --artifact {spec!r}; expected type:id:path") from exc
        path = (root / rel).resolve()
        if not path.is_file():
            raise SystemExit(f"artifact not found: {path}")
        artifacts.append(
            {
                "artifact_type": artifact_type,
                "artifact_id": artifact_id,
                "sha256": sha256(path),
                "path": str(Path(rel)),
            }
        )

    evidence_hashes = {}
    for rel in args.evidence:
        path = (root / rel).resolve()
        if not path.is_file():
            raise SystemExit(f"evidence not found: {path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        if args.status == "RELEASED" and data.get("passed") is not True:
            raise SystemExit(f"RELEASED runtime requires passing evidence: {rel}")
        evidence_hashes[rel] = sha256(path)

    manifest = {
        "schema_version": "1.0",
        "runtime_set_id": args.runtime_set_id,
        "sa_version_range": args.sa_version_range,
        "sa_gf_contract_version": args.contract_version,
        "artifacts": artifacts,
        "capability_manifest_ref": args.capabilities,
        "capability_manifest_sha256": sha256(capability_path),
        "conformance_evidence_refs": list(args.evidence),
        "conformance_evidence_sha256": evidence_hashes,
        "status": args.status,
    }
    output = root / args.output
    output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
