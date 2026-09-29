from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

from .candidate import CandidateConformance


@dataclass(frozen=True, slots=True)
class CandidateMatrixCaseResult:
    case_id: str
    passed: bool
    plain_text: str = ""
    operation_ids: tuple[str, ...] = ()
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "passed": self.passed,
            "plain_text": self.plain_text,
            "operation_ids": list(self.operation_ids),
            **({"error": self.error} if self.error else {}),
        }


@dataclass(frozen=True, slots=True)
class CandidateMatrixLanguageResult:
    language: str
    capability_profile: str
    runtime_set_id: str
    candidate_root: str
    cases: tuple[CandidateMatrixCaseResult, ...]
    metadata: Mapping[str, Any]

    @property
    def passed(self) -> bool:
        return bool(self.cases) and all(case.passed for case in self.cases)

    @property
    def passed_cases(self) -> int:
        return sum(1 for case in self.cases if case.passed)

    def to_dict(self) -> dict[str, Any]:
        return {
            "language": self.language,
            "capability_profile": self.capability_profile,
            "runtime_set_id": self.runtime_set_id,
            "candidate_root": self.candidate_root,
            "passed": self.passed,
            "passed_cases": self.passed_cases,
            "total_cases": len(self.cases),
            "cases": [case.to_dict() for case in self.cases],
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class CandidateMatrixReport:
    results: tuple[CandidateMatrixLanguageResult, ...]

    @property
    def passed(self) -> bool:
        return bool(self.results) and all(result.passed for result in self.results)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "1.0",
            "status": "PASS" if self.passed else "REVIEW",
            "released": False,
            "activated": False,
            "languages": [result.to_dict() for result in self.results],
        }


CandidateFactory = Callable[[Path, str], CandidateConformance]


class CandidateMatrixConformance:
    """Runs multiple immutable candidate bundles through the same SA pipeline.

    This is candidate/review infrastructure only. It never writes a RuntimeSet,
    capability manifest, release evidence, or activation state. Language build
    and GF/RGL engineering remain upstream of SemantiK Architect.
    """

    def __init__(self, candidate_factory: CandidateFactory | None = None) -> None:
        self._candidate_factory = candidate_factory or (
            lambda root, runtime_set_id: CandidateConformance(root, runtime_set_id)
        )

    @staticmethod
    def _load_suite(root: Path) -> dict[str, Any]:
        path = root / "conformance.suite.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"Candidate suite must be a JSON object: {path}")
        return data

    @staticmethod
    def _assert_identity(
        app: CandidateConformance,
        suite: Mapping[str, Any],
        runtime_set_id: str,
    ) -> None:
        language = str(suite.get("language") or "")
        profile = str(suite.get("capability_profile") or "")
        suite_runtime = str(suite.get("runtime_set_id") or "")
        if not language or language != str(app.lock.get("language") or ""):
            raise ValueError("Candidate suite/language identity mismatch")
        if not profile or profile != str(app.lock.get("profile_id") or ""):
            raise ValueError("Candidate suite/profile identity mismatch")
        if suite_runtime != runtime_set_id:
            raise ValueError("Candidate suite/runtime identity mismatch")

    @staticmethod
    def _check_expected(
        actual: Mapping[str, Any],
        expected: Mapping[str, Any],
        request: Mapping[str, Any],
    ) -> None:
        if "plain_text" in expected and actual.get("plain_text") != expected["plain_text"]:
            raise AssertionError("plain_text mismatch")
        plain = str(actual.get("plain_text") or "")
        for text in expected.get("contains", []):
            if str(text) not in plain:
                raise AssertionError(f"Required text missing: {text}")
        if expected.get("coverage_complete", True):
            expected_ids = {
                str(item.get("obligation_id") or "")
                for item in request.get("obligations", [])
            }
            got_ids = {
                str(item.get("obligation_id") or "")
                for item in (actual.get("coverage") or [])
            }
            if expected_ids != got_ids:
                raise AssertionError(
                    f"coverage mismatch expected={sorted(expected_ids)} got={sorted(got_ids)}"
                )

    def run_candidate(
        self,
        candidate_root: str | Path,
        runtime_set_id: str,
        *,
        metadata: Mapping[str, Any] | None = None,
    ) -> CandidateMatrixLanguageResult:
        root = Path(candidate_root).resolve()
        app = self._candidate_factory(root, runtime_set_id)
        suite = self._load_suite(root)
        self._assert_identity(app, suite, runtime_set_id)
        case_results: list[CandidateMatrixCaseResult] = []

        for raw_case in suite.get("cases", []):
            case_id = str(raw_case.get("case_id") or "")
            operation_ids: tuple[str, ...] = ()
            plain_text = ""
            try:
                request = raw_case["request"]
                plan = app.plan(request)
                operation_ids = tuple(unit.operation_id for unit in plan.units)
                actual = app.render(request)
                self._check_expected(actual, raw_case.get("expected") or {}, request)
                plain_text = str(actual.get("plain_text") or "")
                if not plain_text.strip():
                    raise AssertionError("empty plain_text")
                case_results.append(
                    CandidateMatrixCaseResult(
                        case_id=case_id,
                        passed=True,
                        plain_text=plain_text,
                        operation_ids=operation_ids,
                    )
                )
            except Exception as exc:
                case_results.append(
                    CandidateMatrixCaseResult(
                        case_id=case_id,
                        passed=False,
                        plain_text=plain_text,
                        operation_ids=operation_ids,
                        error=f"{type(exc).__name__}: {exc}",
                    )
                )

        return CandidateMatrixLanguageResult(
            language=str(suite["language"]),
            capability_profile=str(suite["capability_profile"]),
            runtime_set_id=runtime_set_id,
            candidate_root=str(root),
            cases=tuple(case_results),
            metadata=dict(metadata or {}),
        )

    def run(self, candidates: Iterable[Mapping[str, Any]]) -> CandidateMatrixReport:
        results: list[CandidateMatrixLanguageResult] = []
        for item in candidates:
            root = item.get("candidate_root")
            runtime_set_id = str(item.get("runtime_set_id") or "")
            if not root or not runtime_set_id:
                raise ValueError("Each matrix row requires candidate_root and runtime_set_id")
            metadata = item.get("metadata") or {}
            if not isinstance(metadata, Mapping):
                raise ValueError("Candidate matrix metadata must be a mapping")
            results.append(
                self.run_candidate(root, runtime_set_id, metadata=metadata)
            )
        return CandidateMatrixReport(tuple(results))
