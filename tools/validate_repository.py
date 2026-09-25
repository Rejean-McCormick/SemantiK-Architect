from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import jsonschema


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    subprocess.run([sys.executable, "-m", "compileall", "-q", str(root / "src")], check=True)
    subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=root, check=True, env={**__import__('os').environ, "PYTHONPATH": f"{root/'src'}:{root}"})
    count = 0
    for path in (root / "schemas").glob("*.json"):
        schema = json.loads(path.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)
        count += 1
    print(f"validated {count} schemas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
