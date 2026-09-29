from __future__ import annotations

import asyncio
import re
import subprocess
from pathlib import Path

import semantik_architect.adapters.realization.gf.pgf_runtime as runtime_module
from semantik_architect.adapters.realization.gf.pgf_runtime import PgfRuntime


def test_gf_cli_backend_linearizes_without_python_binding(tmp_path, monkeypatch):
    pgf_path = tmp_path / "grammar.pgf"
    pgf_path.write_bytes(b"real-pgf-placeholder-for-test")
    gf_exe = tmp_path / "gf.exe"
    gf_exe.write_bytes(b"fake")

    monkeypatch.setattr(runtime_module, "pgf", None)
    monkeypatch.setattr(runtime_module, "_PGF_IMPORT_ERROR", ImportError("no pgf"))
    monkeypatch.setenv("SEMANTIK_GF_EXECUTABLE", str(gf_exe))

    def fake_run(argv, *, cwd=None, input=None, stdout=None, stderr=None, timeout=None, shell=None, check=None):
        script = bytes(input or b"").decode("utf-8")
        assert script.startswith("se utf8\n")
        if "pg -langs" in script:
            return subprocess.CompletedProcess(argv, 0, stdout=b"Languages: KonstellationFre\n")
        if "wf -file=" in script:
            assert "l -unlextext -lang=KonstellationFre" in script
            match = re.search(r'wf -file="([^"]+)"', script)
            assert match is not None
            output = Path(cwd) / match.group(1)
            output.write_text("Augustin défend l’existence du libre arbitre.\n", encoding="utf-8")
            return subprocess.CompletedProcess(argv, 0, stdout=b"")
        raise AssertionError(script)

    monkeypatch.setattr(runtime_module.subprocess, "run", fake_run)

    runtime = PgfRuntime(pgf_path)
    status = asyncio.run(runtime.status())
    assert status["loaded"] is True
    assert status["backend"] == "gf_cli"
    assert status["concrete_languages"] == ["KonstellationFre"]
    assert runtime.linearize(
        "RealizeTransitive Augustin_NP Defendre_V2 ExistenceLibreArbitre_NP",
        "KonstellationFre",
    ) == "Augustin défend l’existence du libre arbitre."


def test_gf_cli_sends_unicode_expression_after_utf8_terminal_switch(tmp_path, monkeypatch):
    pgf_path = tmp_path / "grammar.pgf"
    pgf_path.write_bytes(b"real-pgf-placeholder-for-test")
    gf_exe = tmp_path / "gf.exe"
    gf_exe.write_bytes(b"fake")

    monkeypatch.setattr(runtime_module, "pgf", None)
    monkeypatch.setattr(runtime_module, "_PGF_IMPORT_ERROR", ImportError("no pgf"))
    monkeypatch.setenv("SEMANTIK_GF_EXECUTABLE", str(gf_exe))

    seen = []

    def fake_run(argv, *, cwd=None, input=None, stdout=None, stderr=None, timeout=None, shell=None, check=None):
        raw = bytes(input or b"")
        script = raw.decode("utf-8")
        seen.append(script)
        assert script.startswith("se utf8\n")
        if "pg -langs" in script:
            return subprocess.CompletedProcess(argv, 0, stdout=b"Languages: KonstellationLabFre\n")
        if "wf -file=" in script:
            assert '"La foi"' in script
            assert '"l’enquête intellectuelle d’Anselme"' in script
            match = re.search(r'wf -file="([^"]+)"', script)
            assert match is not None
            output = Path(cwd) / match.group(1)
            output.write_text("La foi stimule l’enquête intellectuelle d’Anselme.\n", encoding="utf-8")
            return subprocess.CompletedProcess(argv, 0, stdout=b"")
        raise AssertionError(script)

    monkeypatch.setattr(runtime_module.subprocess, "run", fake_run)

    runtime = PgfRuntime(pgf_path)
    assert runtime.linearize(
        'PresentTransitive "La foi" "stimule" "l’enquête intellectuelle d’Anselme"',
        "KonstellationLabFre",
    ) == "La foi stimule l’enquête intellectuelle d’Anselme."
    assert any("l’enquête intellectuelle d’Anselme" in script for script in seen)
