from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .nodes import SemanticNode, node_from_dict, node_to_dict
from .statements import SemanticStatement, statement_from_dict, statement_to_dict
from .references import require_local_id


@dataclass(frozen=True, slots=True)
class SemanticGraph:
    graph_id: str
    nodes: tuple[SemanticNode, ...]
    statements: tuple[SemanticStatement, ...]

    def __post_init__(self) -> None:
        require_local_id(self.graph_id, "graph_id")
        object.__setattr__(self, "nodes", tuple(self.nodes))
        object.__setattr__(self, "statements", tuple(self.statements))
        ids=[n.id for n in self.nodes]+[s.id for s in self.statements]
        if len(ids) != len(set(ids)):
            raise ValueError("SemanticGraph node/statement IDs must be unique")
        valid=set(ids)
        for node in self.nodes:
            members=getattr(node,"members",())
            for member in members:
                if member not in valid:
                    raise ValueError(f"Collection {node.id} references missing member {member}")
        for statement in self.statements:
            for arg in statement.arguments:
                if arg.value_id not in valid:
                    raise ValueError(f"Statement {statement.id} references missing value {arg.value_id}")
            for qualifier in statement.qualifiers:
                if qualifier.value_id not in valid:
                    raise ValueError(f"Statement {statement.id} qualifier references missing value {qualifier.value_id}")

    @property
    def node_by_id(self) -> dict[str, SemanticNode]:
        return {n.id:n for n in self.nodes}

    @property
    def statement_by_id(self) -> dict[str, SemanticStatement]:
        return {s.id:s for s in self.statements}

    def has(self, ref: str) -> bool:
        return ref in self.node_by_id or ref in self.statement_by_id

    def get(self, ref: str) -> SemanticNode | SemanticStatement:
        if ref in self.node_by_id: return self.node_by_id[ref]
        if ref in self.statement_by_id: return self.statement_by_id[ref]
        raise KeyError(ref)

    def statements_referencing(self, ref: str) -> tuple[SemanticStatement, ...]:
        return tuple(s for s in self.statements if any(a.value_id == ref for a in s.arguments))


def graph_from_dict(data: Mapping[str, Any]) -> SemanticGraph:
    return SemanticGraph(
        graph_id=str(data["graph_id"]),
        nodes=tuple(node_from_dict(x) for x in data.get("nodes", ())),
        statements=tuple(statement_from_dict(x) for x in data.get("statements", ())),
    )


def graph_to_dict(graph: SemanticGraph) -> dict[str, Any]:
    return {"graph_id":graph.graph_id,"nodes":[node_to_dict(n) for n in graph.nodes],"statements":[statement_to_dict(s) for s in graph.statements]}
