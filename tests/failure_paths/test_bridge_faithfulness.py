import hashlib, json
from pathlib import Path
import pytest

from semantik_architect.adapters.realization.gf import GfBridgeRealizer
from semantik_architect.application.ports.runtime_catalog import RuntimeArtifact, RuntimeSetDescriptor
from semantik_architect.domain.language.language_plan import LanguageBlockPlan, LanguagePlan
from semantik_architect.domain.language.lexical import LexicalBinding, LexicalBindingSet
from semantik_architect.domain.language.realization_unit import RealizationUnit
from semantik_architect.domain.errors import SemantikArchitectError


class FakePgf:
    def __init__(self,path): pass
    def linearize(self,expr,concrete): return expr


def test_bridge_rejects_unconsumed_semantic_slot(tmp_path: Path):
    grammar=tmp_path/'g.pgf'; grammar.write_bytes(b'x')
    bridge=tmp_path/'bridge.json'; bridge.write_text(json.dumps({
      'schema_version':'1.0','contract_version':'1.0','operations':{
        'directive.action':{'requires':['agent','predicate','patient'],'expression':'Do {agent} {predicate} {patient}','consumes_features':['polarity']}
      }
    }),encoding='utf-8')
    arts=(
      RuntimeArtifact('grammar','g',hashlib.sha256(grammar.read_bytes()).hexdigest(),grammar),
      RuntimeArtifact('other','sa-gf-bridge-v1',hashlib.sha256(bridge.read_bytes()).hexdigest(),bridge),
    )
    runtime=RuntimeSetDescriptor('r','1.0','RELEASED',arts,{'languages':{'en':{'status':'RELEASED','concrete':'Eng','profiles':[]}}},{},tmp_path)
    unit=RealizationUnit('u','directive.action',{}, {'polarity':'positive'}, {'agent':'a','predicate':'p','patient':'b','deadline':'t'},('o',),('s',),'b')
    plan=LanguagePlan('lp','en',None,(LanguageBlockPlan('b','utterance',('u',),('o',)),),(unit,),'p-1')
    bindings=LexicalBindingSet('lex',(
      LexicalBinding('u','agent','Alice','literal'),LexicalBinding('u','predicate','repair_V2'),LexicalBinding('u','patient','pump','literal'),LexicalBinding('u','deadline','16:00','literal')
    ))
    with pytest.raises(SemantikArchitectError) as ei:
        GfBridgeRealizer(runtime_factory=FakePgf).realize(plan,bindings,runtime)
    assert ei.value.envelope.code=='SA-GF-001'
