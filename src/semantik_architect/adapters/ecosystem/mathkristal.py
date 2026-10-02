from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from typing import Any, Iterable, Mapping

from ...domain.communication.request import CommunicationRequest


class MathKristalProjectionError(ValueError):
    """Raised when a MathKristal Formula IR projection is invalid or untraceable."""


FORBIDDEN_SURFACE_KEYS = {
    "label", "labels", "text", "surface_form", "notation", "language", "lang",
    "description", "title", "definition_text", "natural_language", "glyph",
}
NODE_KINDS = {
    "referent", "variable", "literal", "apply", "operation", "relation",
    "quantifier", "lambda", "tuple", "matrix", "piecewise", "set_builder",
    "indexed_family",
}


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _hash(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _walk_forbidden(value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if key in FORBIDDEN_SURFACE_KEYS:
                raise MathKristalProjectionError(f"surface-language key forbidden at {path}.{key}")
            _walk_forbidden(child, f"{path}.{key}")
    elif isinstance(value, list):
        for i, child in enumerate(value):
            _walk_forbidden(child, f"{path}[{i}]")


class FormulaIR:
    """Small runtime validator/view for MathKristal Formula IR 1.0.0.

    This lives in the ACL adapter on purpose: Formula IR is an external domain
    contract and does not become part of SemantiK Architect's core domain model.
    """

    def __init__(self, data: Mapping[str, Any]) -> None:
        self.data = deepcopy(dict(data))
        self.validate()

    @property
    def root(self) -> str:
        return str(self.data["root"])

    @property
    def expression_ref(self) -> str:
        return str(self.data["expression_ref"])

    @property
    def proposition_ref(self) -> str | None:
        value = self.data.get("proposition_ref")
        return str(value) if value else None

    @property
    def nodes(self) -> list[dict[str, Any]]:
        return list(self.data["nodes"])

    @property
    def by_id(self) -> dict[str, dict[str, Any]]:
        return {str(n["id"]): n for n in self.nodes}

    @staticmethod
    def child_refs(node: Mapping[str, Any]) -> list[str]:
        kind = node["kind"]
        if kind in {"apply", "operation", "relation"}:
            return [str(x) for x in node["arguments"]]
        if kind in {"quantifier", "lambda"}:
            return [str(node["body_id"])]
        if kind == "tuple":
            return [str(x) for x in node["items"]]
        if kind == "matrix":
            return [str(x) for row in node["rows"] for x in row]
        if kind == "piecewise":
            refs: list[str] = []
            for case in node["cases"]:
                refs.extend([str(case["value_id"]), str(case["condition_id"])])
            if node.get("otherwise_id"):
                refs.append(str(node["otherwise_id"]))
            return refs
        if kind == "set_builder":
            refs = [str(node["predicate_id"])]
            if node.get("expression_id"):
                refs.append(str(node["expression_id"]))
            return refs
        if kind == "indexed_family":
            return [str(node["base_id"]), *[str(x) for x in node["index_ids"]]]
        if kind == "variable" and node.get("type_node_id"):
            return [str(node["type_node_id"])]
        return []

    @staticmethod
    def binding_refs(node: Mapping[str, Any]) -> list[str]:
        if node["kind"] in {"quantifier", "set_builder"}:
            return [str(node["variable_id"])]
        if node["kind"] == "lambda":
            return [str(x) for x in node["variable_ids"]]
        return []

    def validate(self) -> None:
        d = self.data
        _walk_forbidden(d)
        required = {"contract", "version", "representation_ref", "expression_ref", "closure", "root", "nodes"}
        missing = sorted(required - set(d))
        if missing:
            raise MathKristalProjectionError("Formula IR missing keys: " + ", ".join(missing))
        if d["contract"] != "mathkristal.formula-ir" or d["version"] != "1.0.0":
            raise MathKristalProjectionError("MathKristal Formula IR 1.0.0 is required")
        if d["representation_ref"] != "urn:mathkristal:representation:ast":
            raise MathKristalProjectionError("Formula IR must use the canonical AST representation")
        if d["closure"] not in {"closed", "open"}:
            raise MathKristalProjectionError("closure must be closed or open")
        if not isinstance(d["nodes"], list) or not d["nodes"]:
            raise MathKristalProjectionError("nodes must be a non-empty array")

        by_id: dict[str, dict[str, Any]] = {}
        for node in d["nodes"]:
            if not isinstance(node, Mapping):
                raise MathKristalProjectionError("every Formula IR node must be an object")
            nid = str(node.get("id") or "")
            kind = node.get("kind")
            if not nid.startswith("n:"):
                raise MathKristalProjectionError(f"invalid Formula IR node id: {nid!r}")
            if nid in by_id:
                raise MathKristalProjectionError(f"duplicate Formula IR node id: {nid}")
            if kind not in NODE_KINDS:
                raise MathKristalProjectionError(f"unsupported Formula IR node kind: {kind!r}")
            by_id[nid] = dict(node)
            self._validate_shape(node)
        if self.root not in by_id:
            raise MathKristalProjectionError(f"Formula IR root does not resolve: {self.root}")
        for node in by_id.values():
            for ref in self.child_refs(node) + self.binding_refs(node):
                if ref not in by_id:
                    raise MathKristalProjectionError(f"{node['id']} references missing node {ref}")
            for ref in self.binding_refs(node):
                if by_id[ref]["kind"] != "variable":
                    raise MathKristalProjectionError(f"{node['id']} binds non-variable node {ref}")

        visiting: set[str] = set()
        visited: set[str] = set()
        def dfs(nid: str) -> None:
            if nid in visiting:
                raise MathKristalProjectionError(f"Formula IR cycle detected at {nid}")
            if nid in visited:
                return
            visiting.add(nid)
            for child in self.child_refs(by_id[nid]):
                dfs(child)
            visiting.remove(nid)
            visited.add(nid)
        dfs(self.root)
        bound: set[str] = set()
        for nid in visited:
            bound.update(self.binding_refs(by_id[nid]))
        unreachable = sorted(set(by_id) - visited - bound)
        if unreachable:
            raise MathKristalProjectionError("unreachable Formula IR nodes: " + ", ".join(unreachable))
        self._validate_scope(by_id)

    @staticmethod
    def _validate_shape(node: Mapping[str, Any]) -> None:
        kind = node["kind"]
        required: dict[str, tuple[str, ...]] = {
            "referent": ("ref",), "variable": (), "literal": ("literal_type", "value"),
            "apply": ("function_ref", "arguments"), "operation": ("operator_ref", "arguments"),
            "relation": ("relation_ref", "arguments"), "quantifier": ("quantifier", "variable_id", "body_id"),
            "lambda": ("variable_ids", "body_id"), "tuple": ("items",), "matrix": ("rows",),
            "piecewise": ("cases",), "set_builder": ("variable_id", "predicate_id"),
            "indexed_family": ("base_id", "index_ids"),
        }
        missing = [k for k in required[kind] if k not in node]
        if missing:
            raise MathKristalProjectionError(f"{node['id']} ({kind}) missing {', '.join(missing)}")
        if kind in {"apply", "operation", "relation"}:
            args = node.get("arguments")
            if not isinstance(args, list) or not args:
                raise MathKristalProjectionError(f"{node['id']} arguments must be non-empty")
        if kind == "relation" and len(node["arguments"]) < 2:
            raise MathKristalProjectionError(f"{node['id']} relation needs at least two arguments")
        if kind == "quantifier" and node["quantifier"] not in {"forall", "exists"}:
            raise MathKristalProjectionError(f"{node['id']} has unsupported quantifier")
        if kind == "literal" and node["literal_type"] not in {"integer", "rational", "decimal", "string", "boolean"}:
            raise MathKristalProjectionError(f"{node['id']} has unsupported literal type")

    def _validate_scope(self, by_id: Mapping[str, dict[str, Any]]) -> None:
        free: set[str] = set()
        seen: set[tuple[str, tuple[str, ...]]] = set()
        def walk(nid: str, env: tuple[str, ...]) -> None:
            state = (nid, env)
            if state in seen:
                return
            seen.add(state)
            node = by_id[nid]
            kind = node["kind"]
            if kind == "variable":
                if nid not in env:
                    free.add(nid)
                if node.get("type_node_id"):
                    walk(str(node["type_node_id"]), env)
                return
            if kind == "quantifier":
                walk(str(node["body_id"]), (*env, str(node["variable_id"])))
                return
            if kind == "lambda":
                walk(str(node["body_id"]), (*env, *[str(x) for x in node["variable_ids"]]))
                return
            if kind == "set_builder":
                next_env = (*env, str(node["variable_id"]))
                walk(str(node["predicate_id"]), next_env)
                if node.get("expression_id"):
                    walk(str(node["expression_id"]), next_env)
                return
            for child in self.child_refs(node):
                walk(child, env)
        walk(self.root, ())
        if self.data["closure"] == "closed" and free:
            raise MathKristalProjectionError("free variables in closed Formula IR: " + ", ".join(sorted(free)))

    def semantic_hash(self) -> str:
        # This hash is for request identity/traceability only; MathKristal remains
        # authoritative for its canonical semantic hash.
        return "sha256:" + _hash(self.data)

    def semantic_refs(self) -> Iterable[str]:
        yield str(self.data["representation_ref"])
        yield self.expression_ref
        for key in ("proposition_ref", "formal_context_ref"):
            if self.data.get(key):
                yield str(self.data[key])
        for node in self.nodes:
            for key in ("ref", "domain_ref", "function_ref", "operator_ref", "relation_ref"):
                if node.get(key):
                    yield str(node[key])


class MathKristalFormulaAcl:
    """Explicit Formula IR -> canonical CommunicationRequest anti-corruption layer.

    The ACL never derives a communication obligation from MathKristal state. The
    projection contract explicitly names the Formula IR and the assertion/expression
    selected for articulation.
    """

    CONTRACT = "semantik.mathkristal-formula-ir.communication-projection/1.0"
    MODES = {"PURE", "NATURAL"}

    def map_request(
        self,
        payload: Mapping[str, Any],
        *,
        target_language: str,
        target_locale: str | None = None,
        capability_profile: str,
    ) -> CommunicationRequest:
        if payload.get("contract") != self.CONTRACT:
            raise MathKristalProjectionError(f"Expected contract {self.CONTRACT}")
        formula_raw = payload.get("formula_ir")
        if not isinstance(formula_raw, Mapping):
            raise MathKristalProjectionError("formula_ir is required")
        formula = FormulaIR(formula_raw)
        mode = str(payload.get("mode") or "PURE").upper()
        if mode not in self.MODES:
            raise MathKristalProjectionError("mode must be PURE or NATURAL")
        selected_ref = str(payload.get("selected_ref") or formula.proposition_ref or formula.expression_ref)
        if selected_ref not in {formula.expression_ref, formula.proposition_ref}:
            raise MathKristalProjectionError("selected_ref must be the Formula IR expression_ref or proposition_ref")

        digest = formula.semantic_hash().split(":", 1)[1][:16]
        nodes: list[dict[str, Any]] = []
        statements: list[dict[str, Any]] = []
        value_ids: dict[str, str] = {}
        statement_ids: dict[str, str] = {}
        by_id = formula.by_id

        def add_value(nid: str) -> str:
            if nid in value_ids:
                return value_ids[nid]
            node = by_id[nid]
            lid = f"v/math/{digest}/{len(value_ids)+1}"
            value_ids[nid] = lid
            kind = node["kind"]
            if kind == "referent":
                nodes.append({"id": lid, "kind": "concept_ref", "concept_ref": node["ref"]})
                return lid
            if kind == "literal":
                nodes.append({"id": lid, "kind": "literal", "value": node["value"], "datatype": f"mathkristal:{node['literal_type']}"})
                return lid
            if kind == "variable":
                nodes.append({"id": lid, "kind": "entity_ref", "external_ref": f"urn:mathkristal:bound-variable:{digest}:{_hash(nid)[:12]}"})
                if node.get("domain_ref"):
                    domain_id = f"v/math/{digest}/domain-{len(nodes)+1}"
                    nodes.append({"id": domain_id, "kind": "concept_ref", "concept_ref": node["domain_ref"]})
                    statements.append({
                        "id": f"s/math/{digest}/{len(statements)+1}",
                        "predicate_ref": "urn:mathkristal:relation:has-domain",
                        "arguments": [
                            {"role_ref": "urn:mathkristal:role:variable", "value_id": lid},
                            {"role_ref": "urn:mathkristal:role:domain", "value_id": domain_id},
                        ],
                        "polarity": "positive",
                        "source_refs": [selected_ref, formula.expression_ref],
                    })
                return lid

            nodes.append({"id": lid, "kind": "entity_ref", "external_ref": f"urn:mathkristal:formula-node:{digest}:{_hash(nid)[:12]}"})
            if kind in {"apply", "operation", "relation"}:
                ref_key = {"apply": "function_ref", "operation": "operator_ref", "relation": "relation_ref"}[kind]
                predicate = str(node[ref_key])
                args = [{"role_ref": f"urn:mathkristal:role:argument-{i}", "value_id": add_value(str(child))} for i, child in enumerate(node["arguments"], 1)]
                if kind != "relation":
                    args.append({"role_ref": "urn:mathkristal:role:result", "value_id": lid})
            elif kind == "quantifier":
                predicate = f"urn:mathkristal:quantifier:{node['quantifier']}"
                args = [
                    {"role_ref": "urn:mathkristal:role:bound-variable", "value_id": add_value(str(node["variable_id"]))},
                    {"role_ref": "urn:mathkristal:role:body", "value_id": add_value(str(node["body_id"]))},
                ]
            elif kind == "lambda":
                predicate = "urn:mathkristal:constructor:lambda"
                args = [{"role_ref": f"urn:mathkristal:role:bound-variable-{i}", "value_id": add_value(str(v))} for i, v in enumerate(node["variable_ids"], 1)]
                args.append({"role_ref": "urn:mathkristal:role:body", "value_id": add_value(str(node["body_id"]))})
            elif kind == "tuple":
                predicate = "urn:mathkristal:constructor:tuple"
                args = [{"role_ref": f"urn:mathkristal:role:item-{i}", "value_id": add_value(str(v))} for i, v in enumerate(node["items"], 1)]
                args.append({"role_ref": "urn:mathkristal:role:result", "value_id": lid})
            elif kind == "matrix":
                predicate = "urn:mathkristal:constructor:matrix"
                flat = [str(v) for row in node["rows"] for v in row]
                args = [{"role_ref": f"urn:mathkristal:role:item-{i}", "value_id": add_value(v)} for i, v in enumerate(flat, 1)]
                args.append({"role_ref": "urn:mathkristal:role:result", "value_id": lid})
            elif kind == "piecewise":
                predicate = "urn:mathkristal:constructor:piecewise"
                args = []
                for i, case in enumerate(node["cases"], 1):
                    args.extend([
                        {"role_ref": f"urn:mathkristal:role:case-value-{i}", "value_id": add_value(str(case["value_id"]))},
                        {"role_ref": f"urn:mathkristal:role:case-condition-{i}", "value_id": add_value(str(case["condition_id"]))},
                    ])
                if node.get("otherwise_id"):
                    args.append({"role_ref": "urn:mathkristal:role:otherwise", "value_id": add_value(str(node["otherwise_id"]))})
                args.append({"role_ref": "urn:mathkristal:role:result", "value_id": lid})
            elif kind == "set_builder":
                predicate = "urn:mathkristal:constructor:set-builder"
                args = [
                    {"role_ref": "urn:mathkristal:role:bound-variable", "value_id": add_value(str(node["variable_id"]))},
                    {"role_ref": "urn:mathkristal:role:predicate", "value_id": add_value(str(node["predicate_id"]))},
                ]
                if node.get("expression_id"):
                    args.append({"role_ref": "urn:mathkristal:role:expression", "value_id": add_value(str(node["expression_id"]))})
                args.append({"role_ref": "urn:mathkristal:role:result", "value_id": lid})
            elif kind == "indexed_family":
                predicate = "urn:mathkristal:constructor:indexed-family"
                args = [{"role_ref": "urn:mathkristal:role:base", "value_id": add_value(str(node["base_id"]))}]
                args.extend({"role_ref": f"urn:mathkristal:role:index-{i}", "value_id": add_value(str(v))} for i, v in enumerate(node["index_ids"], 1))
                args.append({"role_ref": "urn:mathkristal:role:result", "value_id": lid})
            else:
                raise MathKristalProjectionError(f"unsupported composite Formula IR node: {kind}")
            sid = f"s/math/{digest}/{len(statements)+1}"
            statement_ids[nid] = sid
            statements.append({"id": sid, "predicate_ref": predicate, "arguments": args, "polarity": "positive", "source_refs": [selected_ref, formula.expression_ref]})
            return lid

        root_value = add_value(formula.root)
        root_statement = statement_ids.get(formula.root)
        if root_statement is None:
            root_statement = f"s/math/{digest}/{len(statements)+1}"
            statements.append({
                "id": root_statement,
                "predicate_ref": "urn:mathkristal:communication:present-value",
                "arguments": [{"role_ref": "urn:mathkristal:role:value", "value_id": root_value}],
                "polarity": "positive",
                "source_refs": [selected_ref, formula.expression_ref],
            })

        # Explicit articulation anchor. The full semantic graph remains available
        # for traceability; the language planner treats this statement as the
        # selected formula articulation unit.
        anchor_id = f"s/math/{digest}/present"
        statements.append({
            "id": anchor_id,
            "predicate_ref": "urn:mathkristal:communication:present-formula",
            "arguments": [{"role_ref": "urn:mathkristal:role:expression", "value_id": root_value}],
            "polarity": "positive",
            "source_refs": [selected_ref, formula.expression_ref],
        })

        context: dict[str, Any] = {"target_language": target_language, "register": "mathematical"}
        if target_locale is not None:
            context["target_locale"] = target_locale
        request = {
            "schema_version": "1.0",
            "request_id": str(payload.get("request_id") or f"mathkristal/{digest}/{target_language}/{mode.lower()}"),
            "semantic_graph": {"graph_id": f"math/{digest}", "nodes": nodes, "statements": statements},
            "obligations": [{
                "obligation_id": f"obligation/math/{digest}",
                "semantic_refs": [anchor_id],
                "force": "PRESENT",
                "ordering": "FIXED",
                "source_refs": [selected_ref, formula.expression_ref],
            }],
            "supporting_context": [
                {"subject_id": root_value, "property_ref": "urn:semantik:math:mode", "value": mode},
                {"subject_id": root_value, "property_ref": "urn:semantik:math:formula-ir", "value": formula.data},
                {"subject_id": root_value, "property_ref": "urn:semantik:math:formula-hash", "value": formula.semantic_hash()},
            ],
            "context": context,
            "constraints": {
                "allowed_block_kinds": ["utterance"],
                "opening_policy": "forbidden",
                "closing_policy": "forbidden",
                "list_policy": "forbidden",
                "terminology_profile_ref": "mathkristal-pure" if mode == "PURE" else "mathkristal-natural",
                "output_format": "plain_text",
            },
            "capability_profile": capability_profile,
        }
        return CommunicationRequest.from_dict(request)

    def kristal_v6_projection(
        self,
        payload: Mapping[str, Any],
        *,
        state_ref: Mapping[str, Any],
        target_language: str,
        target_locale: str | None = None,
        capability_profile: str,
    ) -> dict[str, Any]:
        request = self.map_request(
            payload,
            target_language=target_language,
            target_locale=target_locale,
            capability_profile=capability_profile,
        )
        if state_ref.get("artifact_type") != "kristal_state" or str(state_ref.get("schema_version")) != "6.0":
            raise MathKristalProjectionError("state_ref must identify a Kristal v6 state")
        formula = FormulaIR(payload["formula_ir"])
        selected_ref = str(payload.get("selected_ref") or formula.proposition_ref or formula.expression_ref)
        return {
            "contract": "semantik.kristal-v6.communication-projection/1.0",
            "kristal_standard": "6.0.0",
            "state_ref": deepcopy(dict(state_ref)),
            "selected_assertions": [{"assertion_id": selected_ref, "record_role": "reference_knowledge"}],
            "communication_request": request.to_dict(),
        }
