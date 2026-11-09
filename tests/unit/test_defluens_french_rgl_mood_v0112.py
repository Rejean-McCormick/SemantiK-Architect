"""Regression of the French RGL S / Utt realization boundary.

These are *source-contract* tests; they do not claim to execute gf.exe.
The observed Windows GF 3.12 error was `S.s : CommonRomance.Mood => Str`
where Output.s needs Str. `mkUtt` lowers S to an utterance before `.s`.
"""
from pathlib import Path
import re

import pytest

PROFILES = Path(__file__).resolve().parents[2] / 'profiles'
CORE = PROFILES / 'defluens-core-1' / 'DefluensCoreFre.gf'
ATTRIBUTE = PROFILES / 'defluens-attribute-fr-1' / 'DefluensAttributeFre.gf'


@pytest.mark.parametrize('operation,clause', [
    ('RealizeAttribute', 'mkCl x a'),
    ('RealizeClass', 'mkCl x a'),
    ('RealizeEvent', 'mkCl x v'),
    ('RealizeAction', 'mkCl x v o'),
    ('RealizeLocation', 'mkCl x a'),
])
def test_core_sentence_is_realized_through_utterance(operation, clause):
    lines = CORE.read_text(encoding='utf-8').splitlines()
    line, = [x.strip() for x in lines if x.strip().startswith(operation + ' ')]
    assert 'mkUtt (mkS t p (' + clause + '))' in line
    assert line.endswith('))).s} ;')
    assert 'mkS t p (' + clause + ')).s' not in line


def test_directive_is_left_with_its_existing_polarity_and_imperative():
    source = CORE.read_text(encoding='utf-8')
    assert 'RealizeDirective v p = {s = (mkUtt p (mkImp v)).s} ;' in source


def test_fr_adverbs_qualify_paradigms_to_avoid_constructor_ambiguity():
    source = CORE.read_text(encoding='utf-8')
    for place, text in (
        ('Here_Place', 'ici'), ('There_Place', 'là'), ('InParis_Place', 'à Paris')
    ):
        assert f'{place} = ParadigmsFre.mkAdv "{text}" ;' in source
    assert not re.search(r'\b(?:Here|There|InParis)_Place\s*=\s*mkAdv\b', source)


def test_attribute_profile_has_the_same_fr_utterance_boundary():
    source = ATTRIBUTE.read_text(encoding='utf-8')
    assert '(mkUtt (mkS tense polarity (mkCl subject quality))).s' in source
    assert '(mkS tense polarity (mkCl subject quality)).s' not in source


def test_abstract_operation_identifiers_and_english_concrete_are_preserved():
    source = (PROFILES / 'defluens-core-1' / 'DefluensCore.gf').read_text(encoding='utf-8')
    english = (PROFILES / 'defluens-core-1' / 'DefluensCoreEng.gf').read_text(encoding='utf-8')
    for operation in ('RealizeAttribute', 'RealizeClass', 'RealizeEvent',
                      'RealizeAction', 'RealizeLocation', 'RealizeDirective'):
        assert re.search(r'\b' + operation + r'\s*:', source)
        assert re.search(r'\b' + operation + r'\b', english)
