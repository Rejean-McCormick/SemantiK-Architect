from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from ..adapters.inbound.python_sdk import SemantikArchitect


@dataclass(frozen=True, slots=True)
class ConformanceCaseResult:
    case_id: str
    passed: bool
    error: str | None = None


@dataclass(frozen=True, slots=True)
class ConformanceReport:
    suite_id: str
    language: str
    capability_profile: str
    runtime_set_id: str
    results: tuple[ConformanceCaseResult, ...]

    @property
    def passed(self) -> bool:
        return all(item.passed for item in self.results)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "1.0",
            "suite_id": self.suite_id,
            "language": self.language,
            "capability_profile": self.capability_profile,
            "runtime_set_id": self.runtime_set_id,
            "passed": self.passed,
            "results": [
                {
                    "case_id": item.case_id,
                    "passed": item.passed,
                    **({"error": item.error} if item.error else {}),
                }
                for item in self.results
            ],
        }


class ConformanceHarness:
    """Executes immutable request/result vectors through the public SDK."""

    def __init__(self, app: SemantikArchitect) -> None:
        self.app = app

    def run(self, suite: Mapping[str, Any]) -> ConformanceReport:
        results: list[ConformanceCaseResult] = []
        for case in suite.get("cases", []):
            case_id = str(case.get("case_id") or "")
            try:
                actual = self.app.render(case["request"])
                expected = case.get("expected") or {}
                if "plain_text" in expected and actual.get("plain_text") != expected["plain_text"]:
                    raise AssertionError("plain_text mismatch")
                if expected.get("coverage_complete", True):
                    expected_ids = {
                        obligation["obligation_id"]
                        for obligation in case["request"].get("obligations", [])
                    }
                    got_ids = {
                        coverage["obligation_id"]
                        for coverage in actual.get("coverage", [])
                    }
                    if expected_ids != got_ids:
                        raise AssertionError(
                            f"coverage mismatch expected={sorted(expected_ids)} "
                            f"got={sorted(got_ids)}"
                        )
                results.append(ConformanceCaseResult(case_id, True))
            except Exception as exc:  # report every failing vector, do not stop suite
                results.append(ConformanceCaseResult(case_id, False, str(exc)))

        return ConformanceReport(
            str(suite["suite_id"]),
            str(suite["language"]),
            str(suite["capability_profile"]),
            str(suite["runtime_set_id"]),
            tuple(results),
        )

    def run_file(self, path: str | Path) -> ConformanceReport:
        return self.run(json.loads(Path(path).read_text(encoding="utf-8")))
