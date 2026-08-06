# ECN-style Jacobian/MaxEnt compressor: frozen synthetic premise

## Outcome

This exact implementation is a **killed implementation**, with its failure
localized to the flatworm ladder attenuation link. The full ladder child
improved over generic three-bin compression on 30 of 32 independent synthetic
units, but its aggregate observable RMS ratio was `0.933605854`, short of the
predeclared `<=0.80` effect gate.

The failed gate does not erase the rest of the result. The observable-Jacobian
`psi`, balanced maximum-entropy `tau`, and exact total-moment `phi` all passed
their structural gates. The biological and ECN metaphors have therefore been
reduced to separable, reusable classical operators rather than accepted as a
single indivisible story.

## Frozen comparison

| Method | Aggregate RMS | Ratio vs generic | Unit wins vs generic |
|---|---:|---:|---:|
| generic q3 | 0.014398755 | 1.000000000 | -- |
| H27 scalar dual-observable | 0.014459339 | 1.004207619 | not promoted |
| Jacobian-MaxEnt, no ladder | 0.013124059 | 0.911471790 | 32/32 |
| Jacobian-MaxEnt + ladder | 0.013442762 | 0.933605854 | 30/32 |

Across units, the no-ladder Jacobian method had median unit ratio
`0.922276748`; the ladder child had median unit ratio `0.939502020`. The ladder
beat its no-ladder parent on only 5 of 32 units. Its mean absolute RMS penalty
relative to the no-ladder variant was `3.193832112e-4`.

The scalar dual-observable comparator was effectively neutral-to-adverse
(`1.0042x`), while the full Jacobian geometry improved all 32 units. This is a
useful premise result: preserving the multidimensional observable sensitivity
contains information that the scalar projection discards, but the fixed depth
smoother did not exploit it correctly.

## What was actually implemented

`psi` maps every Gaussian-mixture component to gate probabilities and an
active-covariance response. The vector geometry is weighted by a cheap analytic
Jacobian of a Gaussian-ReLU response surrogate. This is the defensible part of
the ECN analogy: a constrained map into an observable-sensitive geometry, not
literal finite-field elliptic curves.

`tau` chooses a deterministic central medoid and farthest pair, standardizes
costs by their median positive value, fixes entropic temperature at one, and
uses Sinkhorn scaling into three exactly balanced bins. There are no trained or
post-hoc coefficients.

`phi` reconstructs each bin's mass, mean, and covariance by the law of total
moments, then applies a binwise Gaussian-ReLU closure. The global mean and
covariance remain exact even though nonlinear observable compression is biased.

The flatworm ablation uses two longitudinal lanes with
`m_l=.5*m_(l-1)+.5*u_l`, followed by the commissural matrix
`[[.75,.25],[.25,.75]]`. It exposes consensus and `2*(left-right)`, so the
final pre-commissural contrast is algebraically recoverable rather than averaged
into a scalar.

## Structural audit

- maximum global-mean residual: `3.30e-14`
- maximum global-covariance residual: `3.64e-14`
- minimum bin-covariance eigenvalue: `0.512875333`
- maximum Sinkhorn marginal residual: `4.26e-15`
- minimum hard-assignment effective rank: `2.670542`
- minimum medoid relative gap: `1.72e-5`; no tie ambiguity
- maximum component-permutation residual: `3.89e-16`
- maximum simultaneous coordinate-gauge residual: `5.55e-16`
- maximum contrast-recovery residual: `3.33e-16`
- projected parent-plus-compressor arithmetic: `70.592638976B` FLOPs, below
  the frozen `80B` premise ceiling
- finite outputs and zero structural/resource failures

The coordinate gauge tested here is a simultaneous relabeling of all observable
coordinates. Arbitrary orthogonal rotations are not a symmetry of coordinatewise
ReLU and are therefore not claimed.

## Failure localization and salvage

The ladder's algebra passed, but its attenuation mechanism failed. Repeated
longitudinal smoothing plus commissural mixing pulled the routing geometry away
from the final-layer observable Jacobian. The evidence is direct: the no-ladder
version has lower aggregate error and wins their paired comparison on 27/32
units. Thus the failed link is not loss of contrast representation; it is the
fixed way history is blended with current observable sensitivity.

Preserved components:

1. the Jacobian pullback metric;
2. balanced parameter-free entropic transport;
3. exact PSD total-moment reconstruction;
4. component and coordinate equivariance;
5. the explicit contrast channel itself.

The unresolved family is depth attenuation. A legitimate next generation may
replace only that link—for example, a frozen residual skip that carries the
final Jacobian feature alongside the habituating lane—then freeze new code and
use fresh seeds. Retuning `.5` or `.25` on these 32 units would not count as a
new mechanism and is prohibited by the fold protocol.

## Limits

This was a bounded, target-free synthetic premise test. It read no WHest data,
weights, scorer, public rows, locked rows, or prior reference metrics. It is
not a competition validation and cannot displace the current champion. The
result justifies preserving and separately testing the passing operators in a
future competition-safe generation.
