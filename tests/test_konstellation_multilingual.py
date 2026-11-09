import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'integrations'/'konstellation_light'))
from contract import new_document,validate,ContractError
DIGEST='sha256:'+'a'*64
class ContractTests(unittest.TestCase):
    def test_locale_without_fixed_supported_languages(self):
        doc=new_document('astronomy','urn:kristal:astronomy:state',DIGEST,'ja',[
            {'node_id':'KQ1','label':'星', 'provenance':{'provider':'dik','source_refs':[], 'review_status':'reviewed','review_ref':'review:1'}}])
        self.assertEqual(validate(doc,require_reviewed=True)['locale'],'ja')
    def test_candidate_never_published_by_reader(self):
        doc=new_document('astronomy','urn:kristal:astronomy:state',DIGEST,'fr-CA',[
            {'node_id':'KQ1','definition':'Note candidate.', 'provenance':{'provider':'editorial','source_refs':['source:1'], 'review_status':'candidate'}}])
        with self.assertRaises(ContractError):validate(doc,require_reviewed=True)
    def test_reject_duplicate_identity(self):
        row={'node_id':'KQ1','label':'Term', 'provenance':{'provider':'dik','source_refs':[], 'review_status':'reviewed','review_ref':'r1'}}
        with self.assertRaises(ContractError):new_document('astronomy','urn:kristal:astronomy:state',DIGEST,'en',[row,row])

import json
from from_semantik import export
class SemantiKAdapterTests(unittest.TestCase):
    def test_existing_result_as_candidate(self):
        result=json.loads((ROOT/'examples/orgo_fr_result.json').read_text(encoding='utf-8'))
        doc=export(result,slug='astronomy',node_id='KQ1',state_ref='urn:x',surface_digest=DIGEST)
        self.assertEqual(doc['locale'],'fr-CA')
        self.assertEqual(doc['entries'][0]['provenance']['review_status'],'candidate')
        self.assertIn('Marcel',doc['entries'][0]['definition'])
    def test_missing_actual_text_refused(self):
        with self.assertRaises(ContractError):export({'schema_version':'1.0','blocks':[], 'coverage':[1], 'source_refs':[], 'runtime':{'runtime_set_id':'x'}},slug='astronomy',node_id='KQ1',state_ref='urn:x',surface_digest=DIGEST)
