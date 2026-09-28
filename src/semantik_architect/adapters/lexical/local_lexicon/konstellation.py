"""Canonical evidence display, not free-form linguistic inference."""
import json
from ....domain.errors import SemantikArchitectError
from ....domain.semantics.nodes import CollectionValue, node_to_dict
from ....domain.semantics.statements import SemanticStatement


def statement_literal(request, ref):
    if request.capability_profile != 'konstellation-explorer-1':
        return None
    try:
        statement = request.semantic_graph.get(ref)
    except KeyError:
        return None
    if not isinstance(statement, SemanticStatement):
        return None
    budget = [0]
    def expand(node_id, stack=()):
        budget[0] += 1
        if node_id in stack or len(stack) > 32 or budget[0] > 10000:
            raise SemantikArchitectError('SA-REQ-001', 'Cyclic or excessive explorer collection')
        node = request.semantic_graph.get(node_id)
        if isinstance(node, SemanticStatement):
            raise SemantikArchitectError('SA-REQ-001', 'Explorer argument must reference a value')
        data = node_to_dict(node)
        if isinstance(node, CollectionValue):
            data['members'] = [expand(member, (*stack, node_id)) for member in node.members]
        return data
    payload = {'statement_id': statement.id, 'predicate_ref': statement.predicate_ref,
        'polarity': statement.polarity,
        'arguments': [{'role_ref': a.role_ref, 'value': expand(a.value_id)} for a in statement.arguments],
        'qualifiers': [{'qualifier_ref': q.qualifier_ref, 'value': expand(q.value_id)} for q in statement.qualifiers],
        'source_refs': list(statement.source_refs)}
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
