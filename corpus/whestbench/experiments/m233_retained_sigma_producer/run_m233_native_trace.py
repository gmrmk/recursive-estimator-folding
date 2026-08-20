from __future__ import annotations
import argparse,json,math
import numpy as np
import m233_retained_sigma_producer as m
LIMIT=.016133916999970098; BASE=1.6133916999970097; CEILING=6824272176
def main(seed):
 r=m.trace_static_batch(seed); packed,_,_,_,_=m._target_inputs(seed); expected=m.m224.evaluate_numpy(packed); calls={k:int(v['calls']) for k,v in r['operations'].items()}; wall=r['wall_s']; residual=r['residual_wall_s']
 hostile=r['billed_flops']+5e11*residual
 parity=float(np.max(np.abs(r['value']-expected.value))); radius=float(np.max(np.abs(r['radius']-expected.radius))); chart=int(np.count_nonzero(r['chart_ok']!=expected.chart_ok))
 checks={'bill_has_producer_charge':r['producer_billed_flops']>0,'kernel_calls_exact':r['kernel_calls']==171,'fallback_zero':r['fallback_count']==0,'chart_matches_m224':chart==0,'value_inside_radius':bool(np.all(np.abs(r['value']-expected.value)<expected.radius)),'radius_parity':radius<=1e-20,'raw_gate':wall<LIMIT and BASE/wall>100,'component':hostile<=CEILING}
 for key in ('value','radius','chart_ok','factor','sigma'): r.pop(key,None)
 r.update({'seed':seed,'operation_calls':calls,'raw_speedup_vs_m216':BASE/wall,'hostile_component':hostile,'value_parity_max_abs':parity,'radius_parity_max_abs':radius,'chart_mismatch_count':chart,'checks':checks,'execution_gate_pass':all(checks.values())}); print(json.dumps(r,default=lambda x:x.item() if hasattr(x,'item') else str(x),sort_keys=True,separators=(',',':')))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--seed',type=int,required=True);main(p.parse_args().seed)
