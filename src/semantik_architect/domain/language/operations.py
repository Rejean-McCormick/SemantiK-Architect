from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class OperationDefinition:
    operation_id: str
    semantic_roles: tuple[str, ...]


V1_OPERATIONS: tuple[OperationDefinition, ...] = (
    OperationDefinition("discourse.greeting", ("recipient",)),
    OperationDefinition("discourse.closing", ()),
    OperationDefinition("clause.intransitive_event", ("agent", "predicate")),
    OperationDefinition("clause.transitive_event", ("agent", "predicate", "patient")),
    OperationDefinition("clause.ditransitive_event", ("agent", "predicate", "patient", "recipient")),
    OperationDefinition("clause.copular_classification", ("entity", "class")),
    OperationDefinition("clause.copular_attribute", ("entity", "attribute")),
    OperationDefinition("clause.existential", ("entity",)),
    OperationDefinition("clause.locative", ("entity", "location")),
    OperationDefinition("clause.possession", ("possessor", "possessed")),
    OperationDefinition("clause.passive_event", ("predicate", "patient")),
    OperationDefinition("question.polar", ("proposition",)),
    OperationDefinition("question.content", ("proposition", "queried_role")),
    OperationDefinition("directive.action", ("predicate",)),
    OperationDefinition("coordination.clause", ("members",)),
    OperationDefinition("relative.subject", ("nominal", "predicate")),
    OperationDefinition("relative.object", ("nominal", "predicate", "object")),
    OperationDefinition("nominal.apposition", ("entity", "description")),
    OperationDefinition("comparison.comparative", ("left", "right", "dimension")),
    OperationDefinition("comparison.superlative", ("entity", "set", "dimension")),
)

V1_OPERATION_IDS = frozenset(item.operation_id for item in V1_OPERATIONS)


def require_known_operation(operation_id: str) -> str:
    if operation_id not in V1_OPERATION_IDS:
        raise ValueError(f"Unknown SA↔GF v1 operation: {operation_id}")
    return operation_id
