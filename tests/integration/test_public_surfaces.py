from __future__ import annotations

import json
from pathlib import Path

from semantik_architect.adapters.inbound.cli.main import main
from semantik_architect.adapters.inbound.python_sdk import SemantikArchitect
from semantik_architect.conformance.harness import ConformanceHarness


ROOT = Path(__file__).resolve().parents[2]


def _request() -> dict:
    return json.loads((ROOT / "examples" / "orgo_fr_request.json").read_text(encoding="utf-8"))


def test_python_sdk_validates_request_without_runtime(tmp_path):
    app = SemantikArchitect.from_runtime_root(tmp_path)
    result = app.validate_request(_request())
    assert result["valid"] is True
    assert result["request_id"] == "example:orgo:repair-4356"
    assert app.capabilities() == {}


def test_cli_validate_request(tmp_path, capsys):
    rc = main(
        [
            "--runtime-root",
            str(tmp_path),
            "validate-request",
            str(ROOT / "examples" / "orgo_fr_request.json"),
        ]
    )
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["valid"] is True


def test_cli_returns_stable_request_error(tmp_path, tmp_path_factory, capsys):
    bad = tmp_path_factory.mktemp("request") / "bad.json"
    bad.write_text("{}", encoding="utf-8")
    rc = main(["--runtime-root", str(tmp_path), "validate-request", str(bad)])
    assert rc == 2
    payload = json.loads(capsys.readouterr().err)
    assert payload["code"] == "SA-REQ-001"


class _ConformanceApp:
    def render(self, request):
        return {
            "plain_text": "ok",
            "coverage": [
                {"obligation_id": item["obligation_id"], "status": "realized"}
                for item in request.get("obligations", [])
            ],
        }


def test_conformance_harness_checks_surface_and_coverage():
    suite = {
        "suite_id": "suite:test",
        "language": "fr",
        "capability_profile": "sa-core-1",
        "runtime_set_id": "runtime:test",
        "cases": [
            {
                "case_id": "ok",
                "request": {"obligations": [{"obligation_id": "o1"}]},
                "expected": {"plain_text": "ok", "coverage_complete": True},
            },
            {
                "case_id": "bad-surface",
                "request": {"obligations": []},
                "expected": {"plain_text": "different"},
            },
        ],
    }
    report = ConformanceHarness(_ConformanceApp()).run(suite)
    assert report.passed is False
    assert [item.passed for item in report.results] == [True, False]
    assert report.to_dict()["results"][1]["error"] == "plain_text mismatch"
