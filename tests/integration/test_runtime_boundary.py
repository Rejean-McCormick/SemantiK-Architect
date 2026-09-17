from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_removed_development_subsystems_are_absent() -> None:
    forbidden_paths = [
        "app/adapters/redis_bus.py",
        "app/adapters/redis_broker.py",
        "app/workers",
        "builder",
        "generated",
        "ai_services",
        "architect_frontend/src/components/DevDashboard.tsx",
    ]
    residual = [rel for rel in forbidden_paths if (ROOT / rel).exists()]
    assert residual == []


def test_python_sources_do_not_import_removed_local_modules() -> None:
    forbidden_prefixes = (
        "app.adapters.redis_bus",
        "app.adapters.redis_broker",
        "app.workers",
        "ai_services",
        "builder",
        "generated",
    )
    offenders: list[str] = []

    for path in sorted((ROOT / "app").rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            else:
                continue
            for name in names:
                if name.startswith(forbidden_prefixes):
                    offenders.append(f"{path.relative_to(ROOT)}:{node.lineno}: {name}")

    assert offenders == []


def test_runtime_scripts_do_not_offer_build_or_worker_commands() -> None:
    scripts = [ROOT / "scripts" / "enter_wsl_env.sh", ROOT / "scripts" / "run_backend_wsl.sh"]
    forbidden = ("start-worker", " arq ", "manage.py build", "app.workers")
    offenders: list[str] = []
    for path in scripts:
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            if token in text:
                offenders.append(f"{path.relative_to(ROOT)}: {token}")
    assert offenders == []
