# M176 — exact labelled zero-order BackgroundArchive producer

## Disposition

**NO-GO / FIRST LINK REMAINS BROKEN.**  The mathematical zero-order Gaussian
recurrence and the complete M125b Jacobian are specified on a strict open-SPD
domain.  The current repository does not contain a single implementation that
is simultaneously:

1. exact under that specified recurrence;
2. endpoint-policy-complete or fail-closed on its declared domain;
3. built from installed FlopScope operations and fully metered; and
4. capable of emitting immutable, labelled B=8 `BackgroundEntry` objects.

Accordingly M176 does **not** create a background loop, resource trace, or
candidate.  Building one from the available code would change the frozen
mathematics at the first layer.  M175's first broken link therefore remains
open.  The independently missing `Source211 -> TangentState` conversion is
not touched.

No response, source conversion, efficacy, truth, scorer, leaderboard,
submission, or champion artifact was read or changed.

## Exact contract that a future producer must satisfy

Let the immutable model weights be `W_l`, with `l=1,...,31`, and let the
post-ReLU zero-order state be `(mu_l,V_l)`.  The frozen recurrence is

```text
mu_0 = 0,                         V_0 = I,
a_l  = mu_(l-1) W_l,
C_l  = W_l^T V_(l-1) W_l,
mu_l[i] = E[ReLU(X_i)],           X ~ N(a_l,C_l),
V_l[i,j] = E[ReLU(X_i) ReLU(X_j)] - mu_l[i] mu_l[j].
```

For `C_l[ii]>0` and the declared non-singular bivariate domain, write
`sigma_i=sqrt(C_ii)`, `alpha_i=a_i/sigma_i`,
`p_i=Phi(alpha_i)`, `r_i=phi(alpha_i)/(2 sigma_i)`, and
`m_i=mu_l[i]`.  The complete post-ReLU local Jacobian needed by M125b is:

```text
K_ij    = P(X_i>0,X_j>0),                                      i != j
Hmu_ij  = E[1{X_i>0} ReLU(X_j)] - p_i m_j,                      i != j
Hv_ij   = .5 f_Xi(0) E[ReLU(X_j) | X_i=0] - r_i m_j,            i != j

K_ii    = p_i
Hmu_ii  = 2 m_i (1-p_i)
Hv_ii   = p_i - 2 m_i r_i.
```

Thus for a signed pre-ReLU tangent `(a,A)`, including the exact direct
diagonal limit,

```text
u_i^+ = p_i a_i + r_i A_ii,
U_ij^+ = K_ij A_ij + Hmu_ij a_i + Hmu_ji a_j
                     + Hv_ij A_ii + Hv_ji A_jj,                i != j
U_ii^+ = 2m_i(1-p_i)a_i + (p_i-2m_i r_i)A_ii.
```

This pins the required mathematics.  It also makes clear why a covariance
archive alone is insufficient: each downstream M125b map needs the full
`(p,r,K,Hmu,Hv)` bundle from the *same* pre-ReLU state and operation order.

## Required B=8 ABI (unimplemented)

For the fixed blocks `[1..8], [9..16], [17..24], [25..31]`, a lawful entry
would be immutable and labelled:

```text
BackgroundEntry[
  layer=l,
  W_l: model-weight identity + explicit f32->f64 cast provenance,
  mu_l,V_l: zero-order post-ReLU state,
  J_(l+1): {p,r,K,Hmu,Hv} derived from (a_(l+1),C_(l+1)) for l<31,
  producer_epoch, operation/cast trace
]
```

The background must advance only with `(mu,V)`; no signed tangent or later
source carrier may feed back into it.  A block may be released only after its
last consumer.  This is retained as the M175/M176 salvage contract, not an
implemented interface.

## Why no installed producer satisfies it

### Existing FlopScope full-covariance estimator: semantic mismatch

`fullcov_gaussian_mm/estimator.py` is the only target-shaped FlopScope
closure.  It is deliberately a different numerical model:

- its `_phi2_gauss10` is a fixed ten-node approximation;
- it floors marginal variances at `1e-24`;
- it clips pair correlations to `[-1+1e-12,1-1e-12]`; and
- it overwrites a single covariance state and returns only stacked means.

It neither emits `V_l` archives nor constructs `K,Hmu,Hv` to the M125b
contract.  Reusing it would silently replace the open-domain exact/fail-closed
recurrence with a clipped/floored GL10 closure.  That is a new estimator
mechanism, not archival plumbing.

### Existing M120 analytic code: useful reference, not a metered producer

`m120_price_normal_ordered_adjoint/m120c_analytic_dense_reference.py` does
state the needed formulas and uses direct diagonal limits.  It remains an
ordinary NumPy reference with scalar adaptive 32/64-point Plackett quadrature,
an a-posteriori paired-order disagreement indicator, and refusal when
`abs(rho) >= 1-1e-10`.  It imports no FlopScope operations, contains no
target-width archive/liveness runner, and provides neither an installed
operation trace nor a remainder enclosure that converts its paired-order
indicator into an exact guarantee.  It therefore cannot be wrapped as a
FlopScope producer without a new bivariate primitive, a charge ledger, and a
separately audited endpoint contract.

This is consistent with the earlier M120C R3 audit: replacing clips/floors
requires either closed-form endpoint-complete blocks or a bundled numerical
primitive with a documented remainder and differentiation enclosure.

### M125b is solely a consumer

`m125_forward_tangent.py` declares `LocalReluJacobian` and applies the
five-block map but accepts those arrays as already-made values.  It has no
`analytic_local_kernels` or equivalent builder.  It therefore proves carrier
linearity only after a valid background producer exists.

## Formal first broken link

```text
exact (a_l,C_l) -> [endpoint-complete bivariate values + derivatives]
                 -> labelled {mu_l,V_l,p,r,K,Hmu,Hv}
                 -> B=8 BackgroundArchive
```

The bracketed primitive is absent from the installed FlopScope path.  The
first link is not storage, block scheduling, or casting: it is the unbuilt
and unmetered exact/fail-closed bivariate ReLU kernel-plus-derivative
primitive.  Implementing a block archive before that primitive would create
plausible labels around semantically wrong values.

## Preserved components and next admissible mutation

Preserve:

- M175's fixed B=8 liveness schedule;
- zero-order/background versus signed-carrier separation;
- M120/M125b local recurrence formulas and direct diagonal limits; and
- M169's block-local source compiler layout, conditionally.

The only admissible repair that reopens this branch is one mechanism: a
bundled FlopScope bivariate ReLU value-and-Jacobian primitive with declared
open/endpoint policy, certified or explicitly fail-closed error accounting,
and a generated target-shaped trace.  It must not add a `Source211` conversion
or attempt estimator efficacy in the same mutation.

## Static evidence

`verify_m176_static.py` and `test_m176_static.py` check the relevant source
identities without executing a model.  Their pass means the no-go evidence is
still present; it is not a pass of a BackgroundArchive producer.
