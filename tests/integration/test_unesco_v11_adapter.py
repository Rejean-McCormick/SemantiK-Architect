import unittest
from semantik_architect.adapters.ecosystem.unesco_v11 import build_request,UNESCOProjectionError

class TestUNESCOV11(unittest.TestCase):
 def setUp(self):
  self.data={'profile':'kristal.integration.unesco-mt1-10-semantic-handoff/1.0',
   'branch':'unesco-mt1-10','semantic_grain':'one_branch_kristal','publication_authorized':False,
   'authoritative_authoring_checked':False,'qualified_language_runtime':False,
   'locale':'fr','namespace_id':'urn:local:unesco','view_sha256':'a'*64,
   'selections':[{'unesco_id':'concept10','local_kq':'KQ100','decision_ref':'manual-1',
    'lexical':{'status':'direct','term':'politique éducative'},
    'assertions':[{'id':'KA123','subject':'KQ100','predicate':'KP9',
                   'object':{'kind':'entity','id':'KQ200'},'sources':['KS5']}]}]}
 def test_request_parses_real_domain_model_and_preserves_references(self):
  r=build_request(self.data,unesco_id='concept10')
  d=r.to_dict()
  self.assertEqual(d['context']['target_language'],'fr')
  self.assertEqual(d['semantic_graph']['statements'][0]['id'],'s_KA123')
  self.assertTrue(d['semantic_graph']['statements'][0]['source_refs'][0].endswith('KS5'))
  self.assertEqual(d['obligations'][0]['force'],'PRESENT')
 def test_literals_remain_literal(self):
  self.data['selections'][0]['assertions'][0]['object']={'kind':'literal','value':'A source quote'}
  r=build_request(self.data,unesco_id='concept10')
  self.assertEqual([n['kind'] for n in r.to_dict()['semantic_graph']['nodes']],['entity_ref','literal'])
 def test_refuse_source_free_assertion(self):
  self.data['selections'][0]['assertions'][0]['sources']=[]
  with self.assertRaises(UNESCOProjectionError):build_request(self.data,unesco_id='concept10')
 def test_refuse_unselected_article(self):
  with self.assertRaises(UNESCOProjectionError):build_request(self.data,unesco_id='concept999')
 def test_14_locale_input_is_structural_not_qualified(self):
  self.data['locale']='nn'
  self.assertEqual(build_request(self.data,unesco_id='concept10').context.target_language,'nn')
if __name__=='__main__':unittest.main()
