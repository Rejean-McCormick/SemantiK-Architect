from __future__ import annotations

import json
from pathlib import Path

from semantik_architect.adapters.realization.informath import MathKristalDeduktiEncoder, InformathMathRealizer
from semantik_architect.domain.language.language_plan import LanguagePlan, LanguageBlockPlan
from semantik_architect.domain.language.realization_unit import RealizationUnit
from semantik_architect.domain.language.lexical import LexicalBindingSet
from semantik_architect.application.ports.runtime_catalog import RuntimeArtifact, RuntimeSetDescriptor

ROOT=Path(__file__).resolve().parents[2]


def formula():
    return json.loads((ROOT/'examples/mathkristal_euler_formula.json').read_text(encoding='utf-8'))


def registry():
    return json.loads((ROOT/'profiles/math-pure-1/math-symbol-registry.json').read_text(encoding='utf-8'))


def test_dedukti_encoder_preserves_euler_structure():
    source, table=MathKristalDeduktiEncoder(registry()).encode(formula())
    assert 'forall Complex' in source
    assert 'EqComplex' in source
    assert 'complex_exp' in source
    assert 'times_complex' in source
    assert 'plus_complex' in source
    assert 'complex_exp : "the exponential of #1"' in table
    assert 'EqComplex : "#1 is equal to #2"' in table


def test_informath_realizer_invokes_pinned_language_and_symbol_table(tmp_path):
    cfg=tmp_path/'informath.config.json'; reg=tmp_path/'math-symbol-registry.json'
    cfg.write_text((ROOT/'profiles/math-pure-1/informath.config.json').read_text(encoding='utf-8'),encoding='utf-8')
    reg.write_text((ROOT/'profiles/math-pure-1/math-symbol-registry.json').read_text(encoding='utf-8'),encoding='utf-8')
    artifacts=(
        RuntimeArtifact('other','informath-config-0.4','0'*64,cfg),
        RuntimeArtifact('other','math-symbol-registry-euler-1','0'*64,reg),
    )
    runtime=RuntimeSetDescriptor('test-math','1.0','RELEASED',artifacts,{'languages':{}},{},tmp_path)
    unit=RealizationUnit('math1','math.informalize_formula',{'expression':'v/root'},{'math_mode':'PURE','math_formula_ir':formula()},{},('o1',),('s1',),'b1')
    plan=LanguagePlan('lp','fr',None,(LanguageBlockPlan('b1','utterance',('math1',),('o1',)),),(unit,),'math-pure-1')
    captured={}
    def runner(args, source, env, timeout):
        captured['args']=args; captured['source']=source; captured['timeout']=timeout
        return "pour tout nombre complexe z, l'exponentielle de ..."
    result=InformathMathRealizer(runner=runner).realize(plan,LexicalBindingSet('none',()),runtime)
    assert result.units[0].text.startswith('pour tout')
    assert '-to-lang=Fre' in captured['args']
    assert any(x.startswith('-add-symboltables=') for x in captured['args'])
    assert 'mathkristal_statement : Proof' in captured['source']
