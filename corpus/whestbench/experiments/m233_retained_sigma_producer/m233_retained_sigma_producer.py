"""M233 owned retained-sigma producer feeding M228's unchanged kernel."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import sys
import time
import numpy as np
import flopscope as flops
import flopscope.numpy as fnp

HERE=Path(__file__).resolve().parent; EXP=HERE.parent
for d in (EXP/'m224_gauge_invariant_rho08_chart',EXP/'m228_caller_bound_rho08'):
 if str(d) not in sys.path: sys.path.insert(0,str(d))
import m224_gauge_invariant_rho08_chart as m224
import m228_caller_bound_rho08 as m228

M224_CODE_SHA256='6ABA2D0AB618FF5D678977CC07FC89962C09092B537AAFFC282E069C10DFDA7B'
LAYERS=31; WIDTH=256; EVENTS=3968; KERNEL_BILL=5467*EVENTS
RAW_NAMES=('g','repeated_mean','repeated_sigma','repeated_activation_mean','pair_base_left','pair_base_right','pair_slope_left','pair_slope_right','pair_sigma_left','pair_sigma_right','pair_rho','activation_mean_left','activation_mean_right','activation_vii','activation_vjk','activation_vij','activation_vik','tree')
class M233Refusal(RuntimeError): pass

@dataclass(frozen=True)
class RetainedSigmaLayerInput:
 layer:int; epoch:int; diagonal_identity:int; marginal_sigma:np.ndarray; factor:np.ndarray; active_count:int
 @property
 def vector(self): return self.marginal_sigma
 @classmethod
 def from_diagonal(cls,diagonal,*,layer:int,epoch:int):
  d=np.asarray(diagonal,dtype=np.float64)
  if d.ndim!=1 or np.any(d<0) or not np.all(np.isfinite(d)): raise M233Refusal('DIAGONAL_INVALID')
  sigma=np.sqrt(d); count=int(np.count_nonzero(d>0)); factor=np.zeros_like(sigma)
  if count: factor[d>0]=sigma[d>0]/np.sqrt(count)
  return cls(layer,epoch,id(diagonal),sigma,factor,count)
 def bind(self,vector,layer,epoch):
  if layer!=self.layer: raise M233Refusal('LAYER_SUBSTITUTION')
  if epoch!=self.epoch: raise M233Refusal('EPOCH_SUBSTITUTION')
  if vector is not self.vector: raise M233Refusal('COPY_OR_CONDITIONAL_SUBSTITUTION')
  return vector

def _target_inputs(seed=221720001):
 packed=m228.generated_native_batch(seed)
 diagonal=np.ones((LAYERS,WIDTH),dtype=np.float64)
 for layer in range(LAYERS):
  local=packed.local_states[layer*128]
  diagonal[layer,:local.sigma.size]=local.sigma*local.sigma
 labels=np.empty((2,EVENTS),dtype=np.int64); labels[0]=packed.labels[:,2]; labels[1]=packed.labels[:,3]
 offsets=np.repeat(np.arange(LAYERS,dtype=np.int64)*WIDTH,128)
 columns={n:np.asarray(getattr(packed,n),dtype=np.float64) for n in RAW_NAMES}
 return packed,diagonal,labels,offsets,columns

def _workspace():
 return {'sigma':fnp.empty((LAYERS,WIDTH),dtype=fnp.float64),'factor':fnp.empty((LAYERS,WIDTH),dtype=fnp.float64),'active':fnp.empty((LAYERS,WIDTH),dtype=fnp.bool_),'count':fnp.empty(LAYERS,dtype=fnp.float64),'denom':fnp.empty(LAYERS,dtype=fnp.float64),'labels':fnp.empty((2,EVENTS),dtype=fnp.int64),'index':fnp.empty((2,EVENTS),dtype=fnp.int64),'margins':fnp.empty((2,EVENTS),dtype=fnp.float64)}

def trace_static_batch(seed=221720001):
 packed,diagonal,labels,offsets,columns=_target_inputs(seed); w=_workspace(); kernel=m228.PersistentKernel(EVENTS)
 budget=flops.BudgetContext(10**12,quiet=True,wall_time_limit_s=120.0); started=time.perf_counter()
 with budget:
  fnp.sqrt(diagonal,out=w['sigma'])
  fnp.greater(diagonal,fnp.float64(0.0),out=w['active'])
  fnp.sum(w['active'],axis=1,out=w['count'])
  fnp.sqrt(w['count'],out=w['denom'])
  fnp.divide(w['sigma'],w['denom'][:,None],out=w['factor'])
  fnp.copyto(w['labels'],labels)
  fnp.add(w['labels'],offsets[None,:],out=w['index'])
  fnp.take(w['sigma'].reshape(LAYERS*WIDTH),w['index'],out=w['margins'],mode='clip')
  columns['marginal_sigma_left']=w['margins'][0]; columns['marginal_sigma_right']=w['margins'][1]
  kernel.bind(m228.BoundInputs(columns=columns,event_count=EVENTS)); value,radius,chart=kernel.compile()
 wall=time.perf_counter()-started; summary=budget.summary_dict(); total=int(budget.flops_used)
 buffers=sum(int(x.nbytes) for x in w.values())+int(kernel._float_slab.nbytes)+int(kernel._bool_slab.nbytes)
 return {'value':np.asarray(value),'radius':np.asarray(radius),'chart_ok':np.asarray(chart),'billed_flops':total,'producer_billed_flops':total-KERNEL_BILL,'kernel_calls':171,'operations':summary.get('operations',{}),'wall_s':wall,'residual_wall_s':float(budget.residual_wall_time_s or 0.0),'fallback_count':int(np.count_nonzero(~np.asarray(chart))),'all_buffers_owned':buffers>0,'buffer_bytes':buffers,'factor':np.asarray(w['factor']),'sigma':np.asarray(w['sigma'])}

def static_semantic_proof():
 r=trace_static_batch(); packed,diagonal,labels,offsets,_=_target_inputs(); expected=m224.evaluate_numpy(packed)
 local=packed.local_states[0]; gauge=np.linspace(.7,1.4,local.sigma.size,dtype=np.float64); cov=local.covariance; base=RetainedSigmaLayerInput.from_diagonal(np.diag(cov),layer=1,epoch=1); gauged=RetainedSigmaLayerInput.from_diagonal(np.diag(cov*gauge[:,None]*gauge[None,:]),layer=1,epoch=1)
 perm=np.roll(np.arange(local.sigma.size),1); inv=np.argsort(perm); pvec=RetainedSigmaLayerInput.from_diagonal(np.diag(cov[np.ix_(perm,perm)]),layer=1,epoch=1)
 return {'m224_value_parity':bool(np.all(np.abs(r['value']-expected.value)<expected.radius)),'m224_radius_parity':bool(np.allclose(r['radius'],expected.radius,rtol=0,atol=1e-20)),'gauge':bool(np.allclose(gauged.vector,gauge*base.vector,rtol=0,atol=3e-16)),'permutation':bool(np.array_equal(pvec.vector[inv],base.vector))}

__all__=['M233Refusal','RetainedSigmaLayerInput','trace_static_batch','static_semantic_proof']
