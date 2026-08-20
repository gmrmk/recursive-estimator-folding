from __future__ import annotations
import importlib.util, json
from pathlib import Path
import sys, unittest
import numpy as np

HERE=Path(__file__).resolve().parent
def _load():
 p=HERE/'m233_retained_sigma_producer.py'; s=importlib.util.spec_from_file_location('m233_native',p)
 if s is None or s.loader is None: raise RuntimeError('load M233')
 m=importlib.util.module_from_spec(s); sys.modules[s.name]=m; s.loader.exec_module(m); return m

class M233Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.m=_load()
 def test_frozen_contract(self):
  d=json.loads((HERE/'M233_STATIC_LEDGER_20260809.json').read_text()); self.assertEqual(d['kernel']['calls'],171); self.assertEqual(d['dimensions']['events'],3968); self.assertFalse(d['gates']['variance_gate_authorized'])
 def test_m205_factor_zero_and_binding_refusals(self):
  x=self.m.RetainedSigmaLayerInput.from_diagonal(np.array([0.,.64,1.69]),layer=7,epoch=19)
  np.testing.assert_array_equal(x.marginal_sigma,[0.,.8,1.3]); np.testing.assert_allclose(x.factor,[0.,.8/np.sqrt(2),1.3/np.sqrt(2)])
  with self.assertRaisesRegex(self.m.M233Refusal,'COPY'): x.bind(x.marginal_sigma.copy(),7,19)
  with self.assertRaisesRegex(self.m.M233Refusal,'EPOCH'): x.bind(x.marginal_sigma,7,20)
  with self.assertRaisesRegex(self.m.M233Refusal,'COPY'): x.bind(x.marginal_sigma*.9,7,19)
 def test_generated_m224_parity_gauge_and_permutation(self):
  p=self.m.static_semantic_proof(); self.assertTrue(p['m224_value_parity']); self.assertTrue(p['m224_radius_parity']); self.assertTrue(p['gauge']); self.assertTrue(p['permutation'])
 def test_inclusive_trace_has_charged_producer_and_kernel_ledger(self):
  r=self.m.trace_static_batch(); self.assertEqual(r['kernel_calls'],171); self.assertGreater(r['producer_billed_flops'],0); self.assertTrue(r['all_buffers_owned']); self.assertEqual(r['fallback_count'],0)

if __name__=='__main__': unittest.main()
