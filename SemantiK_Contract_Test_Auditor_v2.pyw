# -*- coding: utf-8 -*-
"""
SemantiK Architect — Contract/Test Auditor v2
Read-only audit tool.

Purpose:
- read the current runtime documentation;
- inspect the canonical runtime PGF through WSL/Python when available;
- optionally run the full pytest suite under WSL;
- classify each failing test as:
    CONTRAT_ACTUEL
    TEST_LEGACY
    A_DECIDER
- flag static legacy test/frontend/doc references;
- write HTML + JSON + raw pytest output.

This tool does NOT modify the repository.
"""

from __future__ import annotations

import datetime as _dt
import html
import json
import os
from pathlib import Path
import re
import subprocess
import threading
import traceback
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Any


APP_TITLE = "SemantiK — Audit contrat ↔ tests v2"

DEFAULT_REPO = r"C:\mycode\SemantiK_Architect\SemantiK_Architect"
DEFAULT_DISTRO = "Debian"
DEFAULT_WSL_PYTHON = "/home/kingk/.venvs/semantik-architect-314/bin/python"

CATEGORY_CURRENT = "CONTRAT_ACTUEL"
CATEGORY_LEGACY = "TEST_LEGACY"
CATEGORY_DECIDE = "A_DECIDER"


def _now_stamp() -> str:
    return _dt.datetime.now().strftime("%Y%m%d_%H%M%S")


def _safe_read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _run_hidden(args: list[str], *, timeout: int = 900) -> subprocess.CompletedProcess[str]:
    kwargs: dict[str, Any] = {
        "stdout": subprocess.PIPE,
        "stderr": subprocess.STDOUT,
        "text": True,
        "encoding": "utf-8",
        "errors": "replace",
        "timeout": timeout,
        "check": False,
    }

    if os.name == "nt":
        kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        kwargs["startupinfo"] = si

    return subprocess.run(args, **kwargs)


def _windows_to_wsl(path: Path) -> str:
    s = str(path.resolve())
    m = re.match(r"^([A-Za-z]):\\(.*)$", s)
    if not m:
        raise ValueError(f"Chemin Windows non convertible vers WSL : {s}")
    drive = m.group(1).lower()
    rest = m.group(2).replace("\\", "/")
    return f"/mnt/{drive}/{rest}"


def _line_excerpt(path: Path, needles: list[str], *, context: int = 1) -> list[dict[str, Any]]:
    text = _safe_read(path)
    if not text:
        return []
    lines = text.splitlines()
    out: list[dict[str, Any]] = []
    seen: set[tuple[int, int]] = set()

    for needle in needles:
        nlow = needle.lower()
        for i, line in enumerate(lines):
            if nlow in line.lower():
                a = max(0, i - context)
                b = min(len(lines), i + context + 1)
                key = (a, b)
                if key in seen:
                    continue
                seen.add(key)
                out.append(
                    {
                        "file": str(path),
                        "start_line": a + 1,
                        "end_line": b,
                        "text": "\n".join(lines[a:b]),
                    }
                )
                break
    return out


def collect_contract_evidence(repo: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    current_sources = [
        repo / "README.md",
        repo / "docs" / "RUNTIME_BOUNDARY.md",
        repo / "runtime" / "README.md",
    ]

    current_needles = [
        "semantic/NLG application runtime",
        "uses GF; it does not develop GF",
        "runtime/semantik_architect.pgf",
        "semantic frame -> planning -> lexical resolution",
        "precompiled",
        "PGF_PATH",
        "runtime contract",
        "must not",
        "does not own",
    ]

    evidence: list[dict[str, Any]] = []
    for p in current_sources:
        if p.exists():
            evidence.extend(_line_excerpt(p, current_needles, context=1))

    legacy_doc_patterns = [
        "gf/semantik_architect.pgf",
        "manage.py align",
        "/api/v1/tools",
        "Everything Matrix",
        "maturity matrix",
        "builder/orchestrator",
        "redis",
        "arq",
        "compile grammar",
        "grammar compilation",
        "gf-rgl",
    ]
    doc_drift: list[dict[str, Any]] = []

    docs_dir = repo / "docs"
    if docs_dir.exists():
        for p in docs_dir.rglob("*.md"):
            # The boundary doc is authoritative and may mention forbidden items as negatives.
            if p.name.upper() == "RUNTIME_BOUNDARY.MD":
                continue
            text = _safe_read(p)
            low = text.lower()
            hits = [pat for pat in legacy_doc_patterns if pat.lower() in low]
            if hits:
                doc_drift.append(
                    {
                        "file": str(p.relative_to(repo)),
                        "patterns": hits,
                    }
                )

    return evidence, doc_drift


def detect_runtime_languages(repo: Path, distro: str, wsl_python: str) -> dict[str, Any]:
    wsl_repo = _windows_to_wsl(repo)
    pgf_path = f"{wsl_repo}/runtime/semantik_architect.pgf"
    code = (
        "import json, pgf\n"
        f"p={pgf_path!r}\n"
        "g=pgf.readPGF(p)\n"
        "print(json.dumps(sorted(g.languages.keys())))\n"
    )
    try:
        cp = _run_hidden(
            ["wsl.exe", "-d", distro, "--", wsl_python, "-c", code],
            timeout=60,
        )
        if cp.returncode == 0:
            lines = [ln.strip() for ln in cp.stdout.splitlines() if ln.strip()]
            langs = json.loads(lines[-1]) if lines else []
            return {"ok": True, "pgf": pgf_path, "languages": langs, "raw": cp.stdout}
        return {"ok": False, "pgf": pgf_path, "languages": [], "raw": cp.stdout}
    except Exception as exc:
        return {"ok": False, "pgf": pgf_path, "languages": [], "raw": repr(exc)}


def run_pytest(repo: Path, distro: str, wsl_python: str) -> dict[str, Any]:
    wsl_repo = _windows_to_wsl(repo)
    code = (
        "import os, pytest\n"
        f"repo={wsl_repo!r}\n"
        "os.chdir(repo)\n"
        "raise SystemExit(pytest.main(['-ra','--tb=short']))\n"
    )
    cp = _run_hidden(
        ["wsl.exe", "-d", distro, "--", wsl_python, "-c", code],
        timeout=1200,
    )
    return {
        "returncode": cp.returncode,
        "output": cp.stdout,
    }


FAIL_RE = re.compile(r"^FAILED\s+(.+?)(?:\s+-\s+(.+))?$")
SKIP_RE = re.compile(r"^SKIPPED\s+(?:\[\d+\]\s+)?(.+)$")
COLLECT_RE = re.compile(r"collected\s+(\d+)\s+items")
SUMMARY_PATTERNS = [
    re.compile(
        r"(?:(\d+)\s+failed,\s*)?"
        r"(?:(\d+)\s+passed,\s*)?"
        r"(?:(\d+)\s+skipped,\s*)?"
        r"(?:(\d+)\s+warnings?)?"
    ),
]


def parse_pytest(output: str) -> dict[str, Any]:
    failures: list[dict[str, str]] = []
    skips: list[str] = []
    collected = None

    for line in output.splitlines():
        s = line.strip()
        m = FAIL_RE.match(s)
        if m:
            failures.append({
                "nodeid": m.group(1).strip(),
                "reason": (m.group(2) or "").strip(),
            })
            continue
        m = SKIP_RE.match(s)
        if m:
            skips.append(m.group(1).strip())
            continue
        m = COLLECT_RE.search(s)
        if m:
            collected = int(m.group(1))

    # Extract final summary counts conservatively.
    summary = {"failed": None, "passed": None, "skipped": None, "warnings": None}
    for line in reversed(output.splitlines()):
        low = line.lower()
        if " passed" in low or " failed" in low or " skipped" in low:
            for key in summary:
                mm = re.search(rf"(\d+)\s+{key}", low)
                if mm:
                    summary[key] = int(mm.group(1))
            if any(v is not None for v in summary.values()):
                break

    return {
        "collected": collected,
        "summary": summary,
        "failures": failures,
        "skips": skips,
    }


def _test_source_text(repo: Path, nodeid: str) -> str:
    rel = nodeid.split("::", 1)[0]
    p = repo / rel
    return _safe_read(p)


def _failure_blob(repo: Path, failure: dict[str, str]) -> str:
    nodeid = failure["nodeid"]
    reason = failure["reason"]
    src = _test_source_text(repo, nodeid)
    # Source can be large; only pattern matching uses it.
    return (nodeid + "\n" + reason + "\n" + src).lower()


def classify_failure(
    repo: Path,
    failure: dict[str, str],
    runtime_languages: list[str],
) -> dict[str, Any]:
    blob = _failure_blob(repo, failure)
    nodeid = failure["nodeid"]
    reason = failure["reason"]

    runtime_langs = set(runtime_languages)
    runtime_has_en_fr_only = runtime_langs == {"WikiEng", "WikiFre"}

    # Strong legacy markers: old artifact location, grammar-dev tools, or languages
    # not present in the canonical runtime artifact.
    legacy_rules: list[tuple[str, str]] = [
        ("gf/semantik_architect.pgf", "ancien emplacement PGF; le contrat actuel utilise runtime/semantik_architect.pgf"),
        ("/api/v1/tools", "surface d'outil de développement GF hors frontière runtime"),
        ("refine_grammar", "fonction de raffinage/développement GF hors frontière runtime"),
        ("manage.py align", "workflow d'alignement/compilation de l'ancienne architecture"),
        ("everything matrix", "matrice de maturité de l'ancienne architecture GF"),
        ("maturity matrix", "matrice de maturité de l'ancienne architecture GF"),
        ("builder/orchestrator", "orchestration de compilation GF hors runtime"),
    ]
    for marker, rationale in legacy_rules:
        if marker in blob:
            return {
                "category": CATEGORY_LEGACY,
                "confidence": "haute",
                "rationale": rationale,
            }

    if runtime_has_en_fr_only:
        unsupported_markers = [
            "/generate/de", "/generate/es", "/generate/it",
            "['pt', 'ru']", '["pt", "ru"]',
            "missing lexicon source for languages: ['pt', 'ru']",
            "test_language_directories_integrity",
        ]
        if any(m in blob for m in unsupported_markers):
            return {
                "category": CATEGORY_LEGACY,
                "confidence": "haute",
                "rationale": "le PGF runtime observé n'expose que WikiEng/WikiFre; ce test attend une couverture langue plus large",
            }

    # Runtime concrete-language names are intentionally GF names.
    if "resolved_language" in blob and ("wikieng" in blob or "wikifre" in blob):
        return {
            "category": CATEGORY_LEGACY,
            "confidence": "haute",
            "rationale": "le test confond code applicatif (en/fr) et concrete GF runtime (WikiEng/WikiFre)",
        }

    # Tests that still assume pre-refactor internal/result shapes.
    if 'isinstance(result, sentence)' in blob or 'assert isinstance(result, sentence)' in blob:
        return {
            "category": CATEGORY_LEGACY,
            "confidence": "haute",
            "rationale": "le test exige l'ancien type Sentence alors que le runtime planner-first retourne le résultat canonique SurfaceResult",
        }

    if 'getattr(frame, "subject", {})["name"]' in blob or "entity' object is not subscriptable" in blob:
        return {
            "category": CATEGORY_LEGACY,
            "confidence": "haute",
            "rationale": "le test suppose que subject est un dict; le domaine canonique matérialise désormais un objet Entity",
        }

    if "missing_frame_type" in nodeid.lower() or "missing frame type" in blob:
        return {
            "category": CATEGORY_DECIDE,
            "confidence": "haute",
            "rationale": "le runtime accepte actuellement un bio implicite; décider si frame_type doit rester obligatoire dans le contrat HTTP",
        }

    # Compatibility constructors from the old SurfaceResult/Sentence shape.
    if "sentence(" in blob and "tokens" in reason.lower() and "field required" in reason.lower():
        return {
            "category": CATEGORY_LEGACY,
            "confidence": "moyenne",
            "rationale": "le test construit l'ancien Sentence minimal sans tokens; vérifier s'il faut conserver une façade de compatibilité plutôt qu'affaiblir SurfaceResult",
        }

    # Product/API decisions not resolved by the current minimal runtime boundary.
    decide_rules: list[tuple[bool, str]] = [
        (
            "tests/http_api/test_entities.py" in nodeid.replace("\\", "/"),
            "la présence de /api/v1/entities n'est pas établie par la frontière runtime minimale; décision de surface publique requise",
        ),
        (
            "403" in reason and "test_generate" in nodeid,
            "l'authentification bloque avant le contrat métier; décider le comportement de test/auth avant de modifier le runtime",
        ),
        (
            "generation_time_ms" in blob and "== 0.0" in blob,
            "attente temporelle exacte probablement trop stricte; décider si 0.0 est contractuel ou si seule la non-négativité l'est",
        ),
    ]
    for cond, rationale in decide_rules:
        if cond:
            return {
                "category": CATEGORY_DECIDE,
                "confidence": "haute" if "entities" in rationale or "authentification" in rationale else "moyenne",
                "rationale": rationale,
            }

    # Modern pipeline failures are current-contract candidates.
    current_path_markers = [
        "plan_text",
        "frame_to_slots",
        "construction_plan",
        "lexical_resolution",
        "family_construction_adapter",
        "gf_construction_adapter",
        "realize_text",
        "surface_result",
        "runtime_path",
        "planner_first",
        "model_dump",
    ]
    if any(m in blob for m in current_path_markers):
        return {
            "category": CATEGORY_CURRENT,
            "confidence": "moyenne",
            "rationale": "échec situé dans le pipeline documenté frame → planning → lexical resolution → réalisation → surface",
        }

    # Languages endpoint belongs to runtime capabilities; a 500 is a current bug candidate.
    if "languages" in nodeid.lower() or "/languages" in blob:
        return {
            "category": CATEGORY_CURRENT,
            "confidence": "moyenne",
            "rationale": "la découverte de langues/capacités doit dériver du runtime PGF; un 500 est à traiter côté runtime",
        }

    return {
        "category": CATEGORY_DECIDE,
        "confidence": "faible",
        "rationale": "aucun marqueur documentaire suffisamment fort; revue humaine nécessaire avant modification",
    }


def static_legacy_findings(repo: Path, runtime_languages: list[str]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []

    targets: list[Path] = []
    tests = repo / "tests"
    if tests.exists():
        targets.extend(tests.rglob("*.py"))

    req_dir = repo / "architect_frontend" / "src" / "data" / "requests"
    if req_dir.exists():
        targets.extend(req_dir.glob("*.json"))

    patterns = [
        ("gf/semantik_architect.pgf", "ancien emplacement PGF"),
        ("/api/v1/tools", "outil de développement GF hors frontière runtime"),
        ("refine_grammar", "workflow de raffinage GF legacy"),
        ("manage.py align", "workflow d'alignement/compilation legacy"),
        ("everything matrix", "ancienne matrice de maturité"),
    ]

    runtime_has_en_fr_only = set(runtime_languages) == {"WikiEng", "WikiFre"}

    for p in targets:
        text = _safe_read(p)
        low = text.lower()
        for marker, rationale in patterns:
            if marker in low:
                findings.append(
                    {
                        "file": str(p.relative_to(repo)),
                        "marker": marker,
                        "rationale": rationale,
                    }
                )

        if runtime_has_en_fr_only:
            for marker in ("/generate/de", "/generate/es", "/generate/it"):
                if marker in low:
                    findings.append(
                        {
                            "file": str(p.relative_to(repo)),
                            "marker": marker,
                            "rationale": "langue absente du PGF runtime actuellement observé (WikiEng/WikiFre)",
                        }
                    )

    # dedupe
    uniq: list[dict[str, Any]] = []
    seen = set()
    for f in findings:
        key = (f["file"], f["marker"])
        if key not in seen:
            seen.add(key)
            uniq.append(f)
    return uniq


def _html_escape(s: Any) -> str:
    return html.escape(str(s), quote=True)


def build_html(data: dict[str, Any]) -> str:
    evidence_rows = []
    for ev in data["contract_evidence"]:
        try:
            rel = str(Path(ev["file"]).relative_to(Path(data["repo"])))
        except Exception:
            rel = ev["file"]
        evidence_rows.append(
            f"<details><summary><code>{_html_escape(rel)}:{ev['start_line']}-{ev['end_line']}</code></summary>"
            f"<pre>{_html_escape(ev['text'])}</pre></details>"
        )

    failures_rows = []
    for f in data["classified_failures"]:
        cat = f["classification"]["category"]
        cls = {
            CATEGORY_CURRENT: "current",
            CATEGORY_LEGACY: "legacy",
            CATEGORY_DECIDE: "decide",
        }.get(cat, "")
        failures_rows.append(
            "<tr>"
            f"<td class='{cls}'><strong>{_html_escape(cat)}</strong></td>"
            f"<td>{_html_escape(f['classification']['confidence'])}</td>"
            f"<td><code>{_html_escape(f['nodeid'])}</code></td>"
            f"<td>{_html_escape(f['reason'])}</td>"
            f"<td>{_html_escape(f['classification']['rationale'])}</td>"
            "</tr>"
        )

    drift_rows = "".join(
        "<tr>"
        f"<td><code>{_html_escape(x['file'])}</code></td>"
        f"<td>{_html_escape(', '.join(x['patterns']))}</td>"
        "</tr>"
        for x in data["doc_drift"]
    )

    static_rows = "".join(
        "<tr>"
        f"<td><code>{_html_escape(x['file'])}</code></td>"
        f"<td><code>{_html_escape(x['marker'])}</code></td>"
        f"<td>{_html_escape(x['rationale'])}</td>"
        "</tr>"
        for x in data["static_legacy_findings"]
    )

    counts = {CATEGORY_CURRENT: 0, CATEGORY_LEGACY: 0, CATEGORY_DECIDE: 0}
    for f in data["classified_failures"]:
        counts[f["classification"]["category"]] = counts.get(f["classification"]["category"], 0) + 1

    summary = data.get("pytest", {}).get("parsed", {}).get("summary", {})
    runtime = data["runtime"]

    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>SemantiK Contract/Test Audit</title>
<style>
body {{ font-family: Segoe UI, Arial, sans-serif; margin: 28px; color: #202124; }}
h1, h2 {{ margin-bottom: .35em; }}
code, pre {{ font-family: Consolas, monospace; }}
pre {{ background: #f6f8fa; padding: 12px; overflow-x: auto; }}
table {{ border-collapse: collapse; width: 100%; margin: 12px 0 28px; }}
th, td {{ border: 1px solid #d0d7de; padding: 8px; vertical-align: top; text-align: left; }}
th {{ background: #f6f8fa; }}
.current {{ background: #eaf7ea; }}
.legacy {{ background: #fff1e8; }}
.decide {{ background: #fff8cf; }}
.cards {{ display: flex; gap: 12px; flex-wrap: wrap; margin: 14px 0 24px; }}
.card {{ border: 1px solid #d0d7de; border-radius: 8px; padding: 12px 16px; min-width: 170px; }}
.small {{ color: #57606a; font-size: .92em; }}
</style>
</head>
<body>
<h1>SemantiK Architect — Audit contrat ↔ tests</h1>
<p class="small">Généré le {_html_escape(data['generated_at'])}. Audit en lecture seule.</p>

<div class="cards">
  <div class="card"><strong>PGF</strong><br>{_html_escape(runtime.get('pgf'))}</div>
  <div class="card"><strong>Langues runtime</strong><br>{_html_escape(', '.join(runtime.get('languages', [])) or 'non détectées')}</div>
  <div class="card current"><strong>{CATEGORY_CURRENT}</strong><br>{counts.get(CATEGORY_CURRENT, 0)} FAIL</div>
  <div class="card legacy"><strong>{CATEGORY_LEGACY}</strong><br>{counts.get(CATEGORY_LEGACY, 0)} FAIL</div>
  <div class="card decide"><strong>{CATEGORY_DECIDE}</strong><br>{counts.get(CATEGORY_DECIDE, 0)} FAIL</div>
</div>

<h2>1. Contrat documentaire actuel</h2>
<p>Sources prioritaires lues : README.md, docs/RUNTIME_BOUNDARY.md, runtime/README.md.</p>
{''.join(evidence_rows) or '<p>Aucun extrait contractuel détecté.</p>'}

<h2>2. Pytest</h2>
<p>
Collectés : {_html_escape(data.get('pytest', {}).get('parsed', {}).get('collected'))}<br>
Résumé : failed={_html_escape(summary.get('failed'))},
passed={_html_escape(summary.get('passed'))},
skipped={_html_escape(summary.get('skipped'))},
warnings={_html_escape(summary.get('warnings'))}
</p>

<table>
<thead>
<tr><th>Classe</th><th>Confiance</th><th>Test</th><th>Erreur</th><th>Pourquoi</th></tr>
</thead>
<tbody>
{''.join(failures_rows) or '<tr><td colspan="5">Aucun FAIL pytest analysé.</td></tr>'}
</tbody>
</table>

<h2>3. Références legacy statiques dans tests / frontend</h2>
<table>
<thead><tr><th>Fichier</th><th>Marqueur</th><th>Interprétation</th></tr></thead>
<tbody>
{static_rows or '<tr><td colspan="3">Aucun marqueur legacy statique détecté.</td></tr>'}
</tbody>
</table>

<h2>4. Dette documentaire potentielle</h2>
<p>Ces documents contiennent encore des marqueurs de l'ancienne architecture. Ce tableau ne dit pas qu'ils sont faux ligne par ligne : il indique qu'ils doivent être revus contre la frontière runtime actuelle.</p>
<table>
<thead><tr><th>Document</th><th>Marqueurs</th></tr></thead>
<tbody>
{drift_rows or '<tr><td colspan="2">Aucune dérive documentaire détectée par les règles actuelles.</td></tr>'}
</tbody>
</table>

<h2>5. Ordre d'action recommandé</h2>
<ol>
<li><strong>TEST_LEGACY</strong> : réécrire/supprimer le test ou l'asset afin qu'il cible le contrat runtime actuel. Ne pas modifier le runtime pour satisfaire une assertion ancienne.</li>
<li><strong>A_DECIDER</strong> : prendre une décision de produit/contrat (surface API, auth, compatibilité), puis documenter avant de modifier le code.</li>
<li><strong>CONTRAT_ACTUEL</strong> : corriger le code runtime, ou corriger le test seulement si l'assertion contredit explicitement le contrat documenté.</li>
<li>Relancer l'audit jusqu'à disparition des ambiguïtés.</li>
</ol>

<p class="small">La classification est un triage automatique fondé sur la documentation et les marqueurs du dépôt. Les cas A_DECIDER sont volontairement conservateurs.</p>
</body>
</html>
"""


def perform_audit(
    repo: Path,
    distro: str,
    wsl_python: str,
    run_tests: bool,
    status_cb,
) -> Path:
    if not repo.exists():
        raise FileNotFoundError(f"Repo introuvable : {repo}")

    status_cb("Lecture du contrat documentaire…")
    evidence, doc_drift = collect_contract_evidence(repo)

    status_cb("Inspection du PGF runtime…")
    runtime = detect_runtime_languages(repo, distro, wsl_python)

    pytest_info: dict[str, Any] = {
        "run": False,
        "returncode": None,
        "output": "",
        "parsed": {"collected": None, "summary": {}, "failures": [], "skips": []},
    }

    if run_tests:
        status_cb("Exécution du full pytest sous WSL…")
        raw = run_pytest(repo, distro, wsl_python)
        pytest_info.update({"run": True, **raw})
        pytest_info["parsed"] = parse_pytest(raw["output"])

    status_cb("Classification des FAIL…")
    langs = runtime.get("languages", [])
    classified = []
    for f in pytest_info["parsed"]["failures"]:
        classified.append(
            {
                **f,
                "classification": classify_failure(repo, f, langs),
            }
        )

    status_cb("Scan legacy statique…")
    static_findings = static_legacy_findings(repo, langs)

    data = {
        "generated_at": _dt.datetime.now().isoformat(timespec="seconds"),
        "repo": str(repo),
        "runtime": runtime,
        "contract_evidence": evidence,
        "doc_drift": doc_drift,
        "static_legacy_findings": static_findings,
        "pytest": pytest_info,
        "classified_failures": classified,
    }

    report_root = Path(r"C:\mycode\_temp") if os.name == "nt" else repo / ".audit"
    report_dir = report_root / f"SemantiK_Contract_Audit_{_now_stamp()}"
    report_dir.mkdir(parents=True, exist_ok=False)

    status_cb("Écriture du rapport…")
    (report_dir / "audit.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (report_dir / "pytest.txt").write_text(pytest_info["output"], encoding="utf-8")
    (report_dir / "report.html").write_text(build_html(data), encoding="utf-8")

    return report_dir / "report.html"


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("790x410")
        self.minsize(720, 360)

        main = ttk.Frame(self, padding=16)
        main.pack(fill="both", expand=True)

        ttk.Label(
            main,
            text="Audit doc actuelle → tests",
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="w")

        ttk.Label(
            main,
            text=(
                "Lecture seule. Classe les FAIL pytest en CONTRAT_ACTUEL / "
                "TEST_LEGACY / A_DECIDER et signale la dette documentaire."
            ),
        ).pack(anchor="w", pady=(4, 14))

        form = ttk.Frame(main)
        form.pack(fill="x")

        ttk.Label(form, text="Repo").grid(row=0, column=0, sticky="w", pady=4)
        self.repo_var = tk.StringVar(value=DEFAULT_REPO)
        ttk.Entry(form, textvariable=self.repo_var).grid(row=0, column=1, sticky="ew", padx=8)
        ttk.Button(form, text="Parcourir…", command=self._browse).grid(row=0, column=2)

        ttk.Label(form, text="WSL distro").grid(row=1, column=0, sticky="w", pady=4)
        self.distro_var = tk.StringVar(value=DEFAULT_DISTRO)
        ttk.Entry(form, textvariable=self.distro_var).grid(row=1, column=1, sticky="ew", padx=8)

        ttk.Label(form, text="Python WSL").grid(row=2, column=0, sticky="w", pady=4)
        self.python_var = tk.StringVar(value=DEFAULT_WSL_PYTHON)
        ttk.Entry(form, textvariable=self.python_var).grid(row=2, column=1, sticky="ew", padx=8)

        form.columnconfigure(1, weight=1)

        self.run_pytest_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            main,
            text="Exécuter le full pytest sous WSL et classifier les FAIL",
            variable=self.run_pytest_var,
        ).pack(anchor="w", pady=(14, 8))

        self.status = tk.StringVar(value="Prêt.")
        ttk.Label(main, textvariable=self.status).pack(anchor="w", pady=(8, 4))

        self.progress = ttk.Progressbar(main, mode="indeterminate")
        self.progress.pack(fill="x", pady=(0, 14))

        buttons = ttk.Frame(main)
        buttons.pack(fill="x")

        self.run_btn = ttk.Button(buttons, text="Lancer l'audit", command=self._start)
        self.run_btn.pack(side="left")

        ttk.Button(buttons, text="Fermer", command=self.destroy).pack(side="right")

        ttk.Separator(main).pack(fill="x", pady=14)
        ttk.Label(
            main,
            text=(
                "Sorties : C:\\mycode\\_temp\\SemantiK_Contract_Audit_<timestamp>\\"
                "\nreport.html + audit.json + pytest.txt"
            ),
        ).pack(anchor="w")

    def _browse(self) -> None:
        p = filedialog.askdirectory(initialdir=self.repo_var.get() or DEFAULT_REPO)
        if p:
            self.repo_var.set(p)

    def _set_status(self, text: str) -> None:
        self.after(0, lambda: self.status.set(text))

    def _start(self) -> None:
        repo = Path(self.repo_var.get().strip())
        distro = self.distro_var.get().strip() or DEFAULT_DISTRO
        wsl_python = self.python_var.get().strip() or DEFAULT_WSL_PYTHON
        run_tests = bool(self.run_pytest_var.get())

        self.run_btn.configure(state="disabled")
        self.progress.start(10)
        self.status.set("Démarrage…")

        def worker() -> None:
            try:
                report = perform_audit(
                    repo,
                    distro,
                    wsl_python,
                    run_tests,
                    self._set_status,
                )
            except Exception as exc:
                tb = traceback.format_exc()
                self.after(
                    0,
                    lambda: self._failed(exc, tb),
                )
                return

            self.after(
                0,
                lambda: self._done(report),
            )

        threading.Thread(target=worker, daemon=True).start()

    def _failed(self, exc: Exception, tb: str) -> None:
        self.progress.stop()
        self.run_btn.configure(state="normal")
        self.status.set("Échec.")
        messagebox.showerror(
            APP_TITLE,
            f"{exc}\n\nDétail :\n{tb[-3500:]}",
        )

    def _done(self, report: Path) -> None:
        self.progress.stop()
        self.run_btn.configure(state="normal")
        self.status.set(f"Terminé : {report}")
        try:
            webbrowser.open(report.as_uri())
        except Exception:
            pass
        messagebox.showinfo(
            APP_TITLE,
            "Audit terminé.\n\n"
            f"Rapport :\n{report}\n\n"
            "Le dépôt n'a pas été modifié.",
        )


if __name__ == "__main__":
    App().mainloop()
