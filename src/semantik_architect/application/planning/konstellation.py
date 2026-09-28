"""Lossless, language-neutral planning for the versioned explorer profile.

One semantic statement becomes one labelled GF realization unit. Qualifications
remain separate units within the same obligation; none are inferred or dropped.
"""
from hashlib import sha256
from ...domain.errors import SemantikArchitectError
from ...domain.language.language_plan import LanguagePlan, LanguageBlockPlan
from ...domain.language.realization_unit import RealizationUnit
from ...domain.semantics.statements import SemanticStatement

PROFILE = 'konstellation-explorer-1'
ROLES = {
    'selection-type': {'selection', 'type'},
    'selection-identities': {'selection', 'values'},
    'selection-link': {'selection', 'relation', 'target'},
    'read-context': {'dataset', 'policy'},
    'result-page': {'selection', 'members', 'total', 'page_count', 'has_more'},
    'inspected-entity': {'entity'},
    'reported-assertion': {'assertion', 'subject', 'relation', 'value'},
    **{f'filter-{op}': {'selection', 'relation', 'values'} for op in ('in', 'none_of')},
    **{f'filter-{op}': {'selection', 'relation'} for op in ('exists', 'missing_in_view')},
    'filter-overlaps': {'selection', 'relation', 'interval', 'match'},
    **{f'assertion-{field}': {'assertion', 'value'} for field in (
        'status', 'certainty', 'validationStatus', 'validatedAs', 'authority',
        'recognitionStatus', 'artifactStatus', 'scope', 'qualifiers',
        'validationPolicyRef', 'readerLabels', 'conflictsWith', 'ruleRef')},
}


def validate_statement(stmt):
    name = stmt.predicate_ref.removeprefix('konstellation:')
    expected = ROLES.get(name)
    roles = [a.role_ref for a in stmt.arguments]
    if (not stmt.predicate_ref.startswith('konstellation:') or expected is None
        or set(roles) != {'konstellation-role:' + r for r in expected}
        or len(roles) != len(expected) or stmt.polarity != 'positive'):
        raise SemantikArchitectError('SA-REQ-001', 'Unsupported Konstellation predicate, roles or polarity')


def plan(request, communication_plan):
    if request.supporting_context or request.constraints.opening_policy != 'forbidden' or request.constraints.closing_policy != 'forbidden':
        raise SemantikArchitectError('SA-CON-001', 'Explorer profile requires explicit semantics without framing or planning overrides')
    if 'utterance' not in request.constraints.allowed_block_kinds:
        raise SemantikArchitectError('SA-CON-001', 'Explorer profile requires utterance blocks')
    context=request.context
    if any(getattr(context,k) for k in ('speaker_ref','recipient_ref','relationship','formality','politeness','tone_profile','discourse_context')) or context.register not in (None,'encyclopedic'):
        raise SemantikArchitectError('SA-CON-001', 'Explorer profile does not silently apply unsupported discourse constraints')
    if request.constraints.ordering_policy_ref or request.constraints.terminology_profile_ref or request.constraints.output_format != 'structured':
        raise SemantikArchitectError('SA-CON-001', 'Unsupported explorer presentation constraints')
    units, blocks = [], []
    for index, item in enumerate(communication_plan.items, 1):
        if item.force.value != 'PRESENT':
            raise SemantikArchitectError('SA-REQ-001', 'Explorer statements must be reported with PRESENT force')
        ids = []
        for ref in item.semantic_refs:
            statement = request.semantic_graph.get(ref)
            if not isinstance(statement, SemanticStatement):
                raise SemantikArchitectError('SA-REQ-001', 'Explorer obligations must reference statements')
            validate_statement(statement)
            uid = f'u{len(units)+1}'
            ids.append(uid)
            units.append(RealizationUnit(uid, 'nominal.apposition',
                {'entity': statement.predicate_ref, 'description': statement.id}, {},
                {'entity': statement.predicate_ref, 'description': statement.id},
                item.obligation_ids, (ref,), f'b{index}'))
        if not ids:
            raise SemantikArchitectError('SA-REQ-001', 'Empty explorer obligation')
        blocks.append(LanguageBlockPlan(f'b{index}', 'utterance', tuple(ids), item.obligation_ids))
    digest = sha256(request.request_id.encode()).hexdigest()[:20]
    return LanguagePlan(f'lp:{digest}', request.context.target_language,
        request.context.target_locale, tuple(blocks), tuple(units), PROFILE)
