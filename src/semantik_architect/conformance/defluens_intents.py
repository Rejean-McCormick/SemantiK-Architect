"""Development-only mapping of the Defluens 15 semantic intents to SA operation families.

This inventory is NOT a released capability profile and does NOT claim that GF
features are bound, that an SA bridge variant exists, or that a PGF is qualified.
The realizer, planning, lexical and conformance authorities remain in SemantiK.
"""
from __future__ import annotations
from ..domain.language.operations import V1_OPERATION_IDS

INTENT_ROWS = (('factual-present', 'Énoncé factuel au présent', 'Present factual statement', 'clause.copular_attribute', ['tense=present'], 'Mira is ready.'), ('past-event', 'Événement passé', 'Past event', 'clause.intransitive_event', ['tense=past'], 'Mira arrived.'), ('past-state', 'État passé', 'Past state', 'clause.copular_attribute', ['tense=past'], 'Mira was tired.'), ('future-reference', 'Référence future', 'Future reference', 'clause.intransitive_event', ['tense=future'], 'Mira will return.'), ('factual-negation', 'Négation factuelle', 'Factual negation', 'clause.copular_attribute', ['polarity=negative'], 'Mira is not ready.'), ('temporal-order', 'Ordre temporel', 'Temporal ordering', 'clause.intransitive_event', ['time_relation=after', 'time_modifier'], 'Mira rests after the meeting.'), ('condition-real', 'Condition réelle', 'Real-world condition', None, ['antecedent', 'consequent', 'conditional_relation'], 'If Mira arrives, the device works.'), ('possibility', 'Possibilité', 'Possibility', 'clause.intransitive_event', ['modality=possible'], 'Mira can return.'), ('source-attribution', 'Attribution de source', 'Source attribution', None, ['source_identity', 'attributed_proposition'], 'Mira says that the device is ready.'), ('quantity', 'Quantité explicite', 'Explicit quantity', 'clause.transitive_event', ['quantity=2', 'quantified_patient'], 'Mira carries two books.'), ('location', 'Localisation', 'Location', 'clause.locative', [], 'Mira is in the house.'), ('instruction', 'Instruction', 'Instruction', 'directive.action', ['force=DIRECT'], 'Wait!'), ('prohibition', 'Interdiction', 'Prohibition', 'directive.action', ['force=DIRECT', 'polarity=negative'], 'Do not wait!'), ('obligation', 'Obligation', 'Obligation', 'directive.action', ['modality=obligatory'], 'You must wait.'), ('conditional-instruction', 'Instruction conditionnelle', 'Conditional instruction', None, ['directive', 'condition'], 'Wait if Mira arrives.'))


def describe_practical_intents() -> dict:
    items=[]
    for ident,fr,en,op,features,gloss in INTENT_ROWS:
        if op is not None and op not in V1_OPERATION_IDS:
            raise ValueError(f"Unknown SA operation for {ident}: {op}")
        items.append({"id":ident,"label_fr":fr,"label_en":en,"meaning_en":gloss,
                      "sa_operation_family":op,"required_semantics":list(features),
                      "mapping_status":"OPERATION_FAMILY_IDENTIFIED" if op else "CONTRACT_EXTENSION_REQUIRED",
                      "bridge_verified":False,"profile_released":False,"source":"semantik_architect.conformance.defluens_intents"})
    return {"schema_id":"semantik.defluens-practical-intent-map","schema_version":"1.0",
            "phase":"DEVELOPMENT","profile_released":False,"bridge_verified":False,
            "candidate_only":True,"total":len(items),
            "mapped_families":sum(x["sa_operation_family"] is not None for x in items),
            "requires_contract_extension":sum(x["sa_operation_family"] is None for x in items),
            "intents":items,
            "notice":"An existing operation family is NOT evidence that its tense, polarity, modality, composition or lexicon is fully realized. WordBench probes and SA profiles are separate evidence."}
