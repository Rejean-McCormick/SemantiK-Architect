from __future__ import annotations

import argparse
import os
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parent


def pgf_path() -> Path:
    raw = (os.getenv("PGF_PATH") or "").strip()
    return Path(raw).expanduser().resolve() if raw else repo_root() / "runtime" / "semantik_architect.pgf"


def doctor() -> int:
    p = pgf_path()
    print(f"Repository : {repo_root()}")
    print(f"PGF        : {p}")
    print(f"PGF exists : {p.is_file()}")
    try:
        import pgf  # noqa: F401
        print("pgf module : available")
    except Exception as exc:
        print(f"pgf module : unavailable ({exc})")
        return 2
    return 0 if p.is_file() else 1


def serve(host: str, port: int, reload: bool) -> int:
    import uvicorn
    uvicorn.run("app.adapters.api.main:create_app", factory=True, host=host, port=port, reload=reload)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="SemantiK Architect runtime manager")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor", help="Check PGF runtime readiness")
    pserve = sub.add_parser("serve", help="Start the API")
    pserve.add_argument("--host", default="0.0.0.0")
    pserve.add_argument("--port", type=int, default=8000)
    pserve.add_argument("--reload", action="store_true")
    args = parser.parse_args()
    if args.command == "doctor":
        return doctor()
    return serve(args.host, args.port, args.reload)


if __name__ == "__main__":
    raise SystemExit(main())
