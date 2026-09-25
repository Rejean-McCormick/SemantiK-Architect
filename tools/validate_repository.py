from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import jsonschema


def _test_env(root: Path) -> dict[str, str]:
    env = os.environ.copy()
    entries = [str(root / "src"), str(root)]
    existing = env.get("PYTHONPATH")
    if existing:
        entries.append(existing)
    env["PYTHONPATH"] = os.pathsep.join(entries)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def main() -> int:
    root = Path(__file__).resolve().parents[1]

    subprocess.run(
        [sys.executable, "-m", "compileall", "-q", str(root / "src")],
        check=True,
    )
    subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=root,
        check=True,
        env=_test_env(root),
    )

    count = 0
    for path in (root / "schemas").glob("*.json"):
        schema = json.loads(path.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)
        count += 1

    print(f"validated {count} schemas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
