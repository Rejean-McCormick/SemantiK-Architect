from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from typing import Any, Callable, Mapping

from ...application.ports.realizer import RealizationResult, RealizedUnit
from ...application.ports.runtime_catalog import RuntimeSetDescriptor
from ...domain.errors import SemantikArchitectError
from ...domain.language.language_plan import LanguagePlan
from ...domain.language.lexical import LexicalBindingSet

_MATH_OPERATION = "math.informalize_formula"
_SAFE_IDENT = re.compile(r"[^A-Za-z0-9_]")


def _ident(text: str, *, prefix: str = "mk") -> str:
    local = text.rsplit(":", 1)[-1].rsplit("/", 1)[-1].rsplit("#", 1)[-1]
    local = _SAFE_IDENT.sub("_", local)
    if not local or not local[0].isalpha():
        local = f"{prefix}_{local}"
    return local


@dataclass(frozen=True, slots=True)
class InformathConfig:
    executable: str
    version: str
    language_codes: Mapping[str, str]
    base_args: tuple[str, ...]
    pure_args: tuple[str, ...]
    natural_args: tuple[str, ...]
    timeout_seconds: float = 20.0
    informath_root: str | None = None
    symbol_registry_path: Path | None = None


class MathKristalDeduktiEncoder:
    """Encode Formula IR as a small Dedukti fragment + Informath symbol table.

    The encoder is intentionally structural. Natural-language wording lives in
    the versioned symbol registry and Informath/GF, never in the Formula IR.
    """

    BUILTIN_QUANTIFIERS = {"forall": "forall", "exists": "exists"}

    def __init__(self, registry: Mapping[str, Any] | None = None) -> None:
        self.registry = dict(registry or {})
        self.symbols = dict(self.registry.get("symbols") or {})

    def _symbol(self, ref: str) -> dict[str, Any]:
        raw = self.symbols.get(ref)
        if not isinstance(raw, Mapping):
            raise SemantikArchitectError(
                "SA-MATH-002",
                f"No Informath symbol mapping for {ref}",
                details={"semantic_ref": ref},
            )
        out = dict(raw)
        out.setdefault("dedukti_id", _ident(ref))
        return out

    @staticmethod
    def _literal(node: Mapping[str, Any]) -> str:
        typ = node["literal_type"]
        value = node["value"]
        if typ == "integer":
            return str(int(value))
        if typ == "boolean":
            return "true" if bool(value) else "false"
        # Non-integer literals are represented by stable identifiers; their
        # verbalization requires an explicit registry entry in a future profile.
        return _ident(f"literal_{typ}_{value}", prefix="lit")

    def encode(self, formula: Mapping[str, Any]) -> tuple[str, str]:
        nodes = {str(n["id"]): dict(n) for n in formula.get("nodes", ())}
        root = str(formula.get("root") or "")
        if root not in nodes:
            raise SemantikArchitectError("SA-MATH-002", "Formula IR root does not resolve")
        variable_names: dict[str, str] = {}
        used: set[str] = set()
        def var_name(nid: str) -> str:
            if nid in variable_names:
                return variable_names[nid]
            candidate = _ident(nid.split(":", 1)[-1], prefix="v")
            base = candidate
            i = 2
            while candidate in used:
                candidate = f"{base}_{i}"; i += 1
            used.add(candidate); variable_names[nid] = candidate
            return candidate

        referenced: dict[str, dict[str, Any]] = {}
        def term(nid: str) -> str:
            node = nodes[nid]; kind = node["kind"]
            if kind == "variable":
                return var_name(nid)
            if kind == "referent":
                sym = self._symbol(str(node["ref"])); referenced[str(node["ref"])] = sym
                return str(sym["dedukti_id"])
            if kind == "literal":
                return self._literal(node)
            if kind in {"apply", "operation", "relation"}:
                key = {"apply":"function_ref", "operation":"operator_ref", "relation":"relation_ref"}[kind]
                ref = str(node[key]); sym = self._symbol(ref); referenced[ref] = sym
                args = " ".join(term(str(x)) for x in node["arguments"])
                return f"({sym['dedukti_id']} {args})"
            if kind == "quantifier":
                q = self.BUILTIN_QUANTIFIERS[str(node["quantifier"])]
                vid = str(node["variable_id"]); v = nodes[vid]
                domain_ref = v.get("domain_ref")
                if not domain_ref:
                    raise SemantikArchitectError("SA-MATH-002", "Quantified variable requires domain_ref for Informath projection", details={"variable_id": vid})
                ds = self._symbol(str(domain_ref)); referenced[str(domain_ref)] = ds
                return f"({q} {ds['dedukti_id']} ({var_name(vid)} => {term(str(node['body_id']))}))"
            raise SemantikArchitectError("SA-MATH-002", f"Informath encoder does not yet support Formula IR node kind {kind}")

        body = term(root)
        declaration = f"mathkristal_statement : Proof {body}.\n"
        prelude: list[str] = []
        table: list[str] = []
        for ref, sym in sorted(referenced.items()):
            did = str(sym["dedukti_id"])
            decl = sym.get("dedukti_declaration")
            if decl:
                prelude.append(str(decl).rstrip(".") + ".")
            mapping = sym.get("gf_mapping") or sym.get("verbal_template")
            if mapping:
                table.append(f"{did} : {mapping}")
        source = "\n".join(prelude + [declaration]) + "\n"
        symbol_table = "\n".join(table) + ("\n" if table else "")
        return source, symbol_table


Runner = Callable[[list[str], str, Mapping[str, str], float], str]


def _default_runner(args: list[str], source: str, env: Mapping[str, str], timeout: float) -> str:
    proc = subprocess.run(args, input=source, text=True, capture_output=True, env=dict(env), timeout=timeout, check=False)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"Informath exited with {proc.returncode}")
    return proc.stdout.strip()


class InformathMathRealizer:
    """RealizerPort adapter for MathCore/Informath-backed mathematical language.

    The adapter invokes a pinned external Informath runtime. If the executable,
    config, language, symbol mapping, or output is unavailable it fails closed.
    """

    def __init__(self, runner: Runner = _default_runner) -> None:
        self._runner = runner
        self._config_cache: dict[str, InformathConfig] = {}
        self._registry_cache: dict[str, Mapping[str, Any]] = {}

    @staticmethod
    def _artifact(runtime: RuntimeSetDescriptor, prefix: str):
        matches = [a for a in runtime.artifacts if a.artifact_type == "other" and a.artifact_id.startswith(prefix)]
        if len(matches) != 1 or matches[0].path is None:
            raise SemantikArchitectError("SA-MATH-003", f"RuntimeSet requires exactly one {prefix} artifact", runtime_set_id=runtime.runtime_set_id, details={"found":[a.artifact_id for a in matches]})
        return matches[0]

    def _config(self, runtime: RuntimeSetDescriptor) -> InformathConfig:
        if runtime.runtime_set_id in self._config_cache:
            return self._config_cache[runtime.runtime_set_id]
        art = self._artifact(runtime, "informath-config")
        try:
            raw = json.loads(art.path.read_text(encoding="utf-8"))
            if raw.get("schema_version") != "1.0":
                raise ValueError("unsupported Informath config schema")
            cfg = InformathConfig(
                executable=str(raw.get("executable") or "RunInformath"),
                version=str(raw["informath_version"]),
                language_codes={str(k):str(v) for k,v in dict(raw.get("language_codes") or {}).items()},
                base_args=tuple(str(x) for x in raw.get("base_args", ())),
                pure_args=tuple(str(x) for x in raw.get("pure_args", ())),
                natural_args=tuple(str(x) for x in raw.get("natural_args", ())),
                timeout_seconds=float(raw.get("timeout_seconds", 20.0)),
                informath_root=raw.get("informath_root"),
            )
        except Exception as exc:
            raise SemantikArchitectError("SA-MATH-003", "Informath runtime config is invalid", runtime_set_id=runtime.runtime_set_id, details={"error":str(exc)}) from exc
        self._config_cache[runtime.runtime_set_id] = cfg
        return cfg

    def _registry(self, runtime: RuntimeSetDescriptor) -> Mapping[str, Any]:
        if runtime.runtime_set_id in self._registry_cache:
            return self._registry_cache[runtime.runtime_set_id]
        art = self._artifact(runtime, "math-symbol-registry")
        try:
            raw = json.loads(art.path.read_text(encoding="utf-8"))
            if raw.get("schema_version") != "1.0":
                raise ValueError("unsupported math symbol registry schema")
        except Exception as exc:
            raise SemantikArchitectError("SA-MATH-003", "Math symbol registry is invalid", runtime_set_id=runtime.runtime_set_id, details={"error":str(exc)}) from exc
        self._registry_cache[runtime.runtime_set_id] = raw
        return raw

    def supports(self, plan: LanguagePlan) -> bool:
        return any(u.operation_id == _MATH_OPERATION for u in plan.units)

    def realize(self, plan: LanguagePlan, bindings: LexicalBindingSet, runtime: RuntimeSetDescriptor) -> RealizationResult:
        cfg = self._config(runtime)
        code = cfg.language_codes.get(plan.language)
        if not code:
            raise SemantikArchitectError("SA-MATH-003", f"Informath language mapping unavailable: {plan.language}", runtime_set_id=runtime.runtime_set_id)
        registry = self._registry(runtime)
        encoder = MathKristalDeduktiEncoder(registry)
        realized: list[RealizedUnit] = []
        for unit in plan.units:
            if unit.operation_id != _MATH_OPERATION:
                raise SemantikArchitectError("SA-MATH-003", f"Informath realizer cannot realize operation {unit.operation_id}", runtime_set_id=runtime.runtime_set_id)
            formula = unit.feature_bindings.get("math_formula_ir")
            if not isinstance(formula, Mapping):
                raise SemantikArchitectError("SA-MATH-002", "Math realization unit is missing Formula IR", runtime_set_id=runtime.runtime_set_id)
            mode = str(unit.feature_bindings.get("math_mode") or "PURE").upper()
            if mode not in {"PURE", "NATURAL"}:
                raise SemantikArchitectError("SA-MATH-002", f"Unsupported math realization mode: {mode}")
            source, symbols = encoder.encode(formula)
            with tempfile.TemporaryDirectory(prefix="semantik-informath-") as tmp:
                symbol_path = Path(tmp) / "mathkristal.dkgf"
                symbol_path.write_text(symbols, encoding="utf-8")
                args = [cfg.executable, *cfg.base_args, f"-to-lang={code}", f"-add-symboltables={symbol_path}"]
                args.extend(cfg.pure_args if mode == "PURE" else cfg.natural_args)
                env = os.environ.copy()
                if cfg.informath_root:
                    env["INFORMATH_ROOT"] = cfg.informath_root
                try:
                    text = self._runner(args, source, env, cfg.timeout_seconds).strip()
                except Exception as exc:
                    raise SemantikArchitectError("SA-MATH-004", "Informath realization failed", runtime_set_id=runtime.runtime_set_id, details={"unit_id":unit.unit_id,"error":str(exc)}) from exc
            if not text:
                raise SemantikArchitectError("SA-MATH-004", "Informath returned empty mathematical language", runtime_set_id=runtime.runtime_set_id, details={"unit_id":unit.unit_id})
            realized.append(RealizedUnit(unit.unit_id, text))
        return RealizationResult(tuple(realized))
