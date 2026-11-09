"""Guard the development mapping; it never grants production eligibility."""
from semantik_architect.conformance.defluens_intents import describe_practical_intents
from semantik_architect.domain.language.operations import V1_OPERATION_IDS


def test_intent_map_has_15_unique_entries_and_known_operations():
    data=describe_practical_intents()
    intents=data['intents']
    assert len(intents)==15 and len({x['id'] for x in intents})==15
    assert data['mapped_families']==12 and data['requires_contract_extension']==3
    assert {x['id'] for x in intents if not x['sa_operation_family']}=={
        'condition-real','source-attribution','conditional-instruction'}
    assert all(x['sa_operation_family'] is None or x['sa_operation_family'] in V1_OPERATION_IDS for x in intents)
    assert all(x['bridge_verified'] is False and x['profile_released'] is False for x in intents)


def test_intent_map_never_activates_or_releases():
    data=describe_practical_intents()
    assert data['profile_released'] is False
    assert data['bridge_verified'] is False
    assert data['phase']=='DEVELOPMENT'
