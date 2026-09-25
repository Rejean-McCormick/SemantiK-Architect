from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys


def test_cli_module_help_is_warning_free() -> None:
    root = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    src = str(root / "src")
    current = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = src if not current else src + os.pathsep + current
    env["PYTHONDONTWRITEBYTECODE"] = "1"

    process = subprocess.run(
        [
            sys.executable,
            "-W",
            "error::RuntimeWarning",
            "-m",
            "semantik_architect.adapters.inbound.cli.main",
            "--help",
        ],
        cwd=root,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert process.returncode == 0, process.stderr or process.stdout
    assert process.stderr == ""
    for command in (
        "render",
        "validate-request",
        "explain",
        "capabilities",
        "validate-runtime",
        "conformance",
        "serve",
    ):
        assert command in process.stdout
