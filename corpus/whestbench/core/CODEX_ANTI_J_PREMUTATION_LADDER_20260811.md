# Codex pre-mutation ladder for the incumbent

Status: disclosed working specification; no contest science executed and no
new-forward authority granted by this document.

Initial evidence snapshot: `publish/recursive-estimator-folding` at
`5ca254f9cac246b85507ba5ec91b7bc8ca9c2b29`. Disclosure hardening was checked
against `e549b41a23627e24155aaef22ff1168e26f62968`; later live work is not
silently incorporated.

## Outcome first

The parent remains **Kerdock v3.1 GUARDS**. Nothing below is a candidate yet.
The only path with plausible first-place magnitude is a seed/weight-side
variance mechanism. The most defensible new mechanism is not the earlier
odd/even cumulant idea called "anti-Jacobian." It is:

> infer a layerwise, gate-conditioned residual transport object from the
> weights and a strictly separated pilot; use it to construct a fixed
> orthogonal involution of input space; couple two legal spherical estimates
> through that involution; and retain the child only if their residuals are
> strongly negatively correlated at equal billed cost.

This is an ambitious hypothesis, not a result.

## Corrections that bind this ladder

1. The earlier "anti-Jacobian non-orientable" implementation was not a
   Jacobian construction. It propagated diagonal `W**3 * kappa3` and
   `W**4 * kappa4` sources. Its odd/even prediction missed. That family is not
   reopened.
2. Near-zero signed mean plus large signed RMS does not prove
   non-orientability. A balanced rank-one signed matrix is a direct
   counterexample. The lawful discrete diagnostic is signed-cycle balance or
   weighted frustration on a named residual matrix.
3. A depth chain is contractible. "Non-orientable" is prohibited unless a
   closed loop and its transition maps are explicitly defined. The working
   terms here are **frustrated residual transport** and **mode conversion**.
4. Static terminal `E[J^T J]` top, bottom, and complement controls are final
   kills: all lost on 16/16 networks with near-zero error correlation. They are
   negative controls, not mutation choices.
5. Exact reverse covariance/adjoint transport is also closed as a production
   route: the committed rank explosion gives `O(n^3)` state and `O(n^4)` work
   per layer for all outputs.
6. The newest common-evidence statement that S17 places the incumbent at
   `0.90x` the distinct-direction floor uses a retired n=3 number. The committed
   n=80 revision is `1.0044`, CI `[0.8450, 1.1639]`, and calls the construction
   a lower-bound attempt, not a minimax proof. This leaves uncertainty; it does
   not prove headroom.
7. U-F1 is currently ledgered killed. Its decisive deeper-eligibility and
   integrated-residual artifacts are still outside the tracked tree at this
   snapshot, so their exact numbers remain provisional until committed and
   independently replayable. The independently established composition defect
   stands: the parent already uses one Winograd level.

## Frozen parent W0

`W0` is the hosted v3.1 GUARDS artifact:

- 126 complete real-MUB/Kerdock frames, 256 rows each;
- 32,256 base directions, antipodally doubled to 64,512 paths;
- one shared Haar rotation;
- exact spherical degree 0--2 structure from complete orthonormal frames plus
  antipodes;
- analytic diagonal moment pass, pilot rescue, terminal fold3, and tangent
  correction;
- row-blocked one-level Winograd on the sampled deep products;
- M186/M187 safety guards;
- hosted adjusted score about `1.8321e-7`, raw MSE about `2.8181e-7` under the
  Phase-1 stack.

Every child is compared against these exact bytes. A rung never silently
changes two mechanisms.

## Three orthogonal ladders

The repository already has:

- `R0..R6`: escalating evidence cost (arithmetic, cache, screen, transfer,
  production, adversary, owner gate);
- `P0..P6`: perturbation stress (seed, width, depth, dtype/cost, suite,
  instrument, adversary).

This document adds `M0..M7`: mutation distance from `W0`. A child advances only
when its current `M` rung has enough `R` evidence and declared `P` coverage.

## The mutation ladder

### M0 — byte-frozen incumbent

No mutation. Rehash package, sources, assets, hosted result, current evaluator
pins, and all guards. If Phase-2 rules differ, bind them before any comparison.

**Fatal:** byte drift, rule ambiguity that changes the score ordering, failed
positive guard fixture, or inability to reproduce the parent under the new
stack.

### M1 — arithmetic and magnitude boundary

No estimator execution. Recompute every claimed improvement relative to the
already-Winograd production bill, not a dense baseline. Separate FLOPs,
residual seconds, peak memory, and MSE. Use the actual Phase-2 score law once
published.

Under the provisional Phase-1 law, reaching `3.68e-8` from `1.832e-7` is about
`4.98x`. Even a `1.057x` cost child would still need about `4.71x` variance
gain, or a raw variance ratio near `0.212`.

**Fatal:** a proposal's algebraic ceiling cannot reach its declared rank target
even under zero overhead and no accuracy loss.

### M2 — define the residual object; output remains bit-identical

Use column-vector convention. For layer `l`,

```text
A_l(x) = D_l(x) W_l^T,
D_l(x) = diag(1[W_l^T h_{l-1}(x) > 0]).
```

The first diagnostic is not `J^{-1}` or a terminal Gram. It is a split-sample
pair-map residual

```text
DeltaS_l = S_l(observed on pilot A)
           - C_l(S_{l-1}; moments fitted only on pilot B),
```

with the two samples swapped and averaged only after both estimates are sealed.
The closure map `C_l` and normalization must be frozen before observations.

For the signed graph `sigma_ij = sign(DeltaS_l,ij)`, compute

```text
F_l = min_{s_i in {+1,-1}}
      sum_{i<j} |DeltaS_l,ij| 1[sigma_ij != s_i s_j]
      / sum_{i<j} |DeltaS_l,ij|.
```

Triangle-sign fractions are an exact instrument check on complete graphs;
`F_l` is the load-bearing statistic. Mean/RMS is diagnostic only.

Controls:

- balanced synthetic signed graph: `F=0` after gauge recovery;
- one deliberately frustrated negative cycle: `F>0`;
- zero residual: loud `NO_SIGNAL`, never PASS;
- neuron permutation and positive ReLU gauge: invariant result;
- independent split estimates must exceed their covariance noise floor.

**Fatal:** no positive-fixture firing, split disagreement comparable to signal,
gauge/permutation failure, or the result reduces to diagonal cumulants, terminal
Gram membership, or a random-direction "contraction" scalar.

### M3 — forward-only input subspace; still no estimator mutation

If and only if M2 detects reproducible frustration, probe a frozen small input
dictionary through normalized **forward** tangents. Do not build a dense reverse
carrier. Select the residual-aligned input projector `P_AJ` using pilot A and
score it only on pilot B; swap the folds once.

The projector must be represented directly, not by signed eigenvectors. Define
the involution

```text
R_AJ = I - 2 P_AJ.
```

Require, to numerical tolerance,

```text
P_AJ^2 = P_AJ,
P_AJ^T = P_AJ,
R_AJ^T R_AJ = I,
R_AJ^2 = I.
```

Primary rank and layer band are frozen before the held-out fold. A random
rank-matched projector, terminal-Gram top/bottom projectors, identity, and
antipode are controls.

**Fatal:** dense adjoint state, outcome-selected rank/layer band, projector
instability, no held-out residual alignment, or failure to beat the random
projector by the predeclared margin.

### M4 — exhaust cache oracles before any new forward

Before a new network forward, exhaust the committed caches.

#### M4a: omit-three ceiling control

For frame means `Y_f`, define the full-129 mean and a triple mean:

```text
Ybar = (1/129) sum_f Y_f,
T_b  = (1/3)   sum_{f in b} Y_f.
```

The naïve partition cannot be deployed unchanged: v3.1 uses its first frame for
`pilot_base=256` and its first four frames for `fold_pilot_base=1024`.
Randomly omitting any of those changes pruning/folding decisions and invalidates
the simple fixed-`Y_f` inclusion proof.

For the cache-supported assay, permanently retain seven anchors: the four
incumbent pilot frames and the three completion frames (the latter are available
in the cache only through their aggregate). Let `B` be the other 122 incumbent
frames. Sort `B` by a frozen nonlinear proxy, draw a uniform cyclic shift `s`,
and omit positions `{s, s+41, s+82} mod 122`. Each nonanchor frame is omitted
with probability `3/122`. Use the Horvitz--Thompson frame estimator

```text
Yhat_s = (1/129) [sum_{f in anchors} Y_f
                  + (122/119) sum_{f in retained(B,s)} Y_f].
```

Then, conditional on the frozen ordering and frame outputs,

```text
E_s[Yhat_s] = (1/129) sum_{f=1}^{129} Y_f.
```

The frame weights sum to one and every retained frame is a complete basis, so
the weighted second moment remains exact and antipodes retain odd cancellation.
The production child would also have to apply these weights consistently to
the first-moment/variance residuals and final mean; weighting only the final
output is not a valid splice.

For an abstract equal-triple partition with fixed pilot decisions,

```text
Yhat_b - Ybar = (1/42)(Ybar - T_b),
E_b[Yhat_b | partition] = Ybar,
D_P = 1/(43*42^2) sum_b ||T_b - Ybar||^2.
```

This preserves the full-129 conditional mean at 126-frame cost, but it cannot
beat the full-129 variance. Existing matched evidence puts that ceiling near a
`3.42%` raw improvement; its isolated degree-4 value is only `0.176%`.
Therefore balanced omission is a calibration/control, not the winner.

Use only the restricted replay actually supported by committed caches:

```text
A = 129*f129 - 126*f126
f_O = (sum_old - sum_{f in O} frame_mean_f + A)/126.
```

First require cache identity between the P2 and S11 shared `f126` records.

**Fatal:** cache mismatch, algebraic trace tie, less than the existing 20%
oracle-headroom screen, or any claim that a 3.42%-ceiling mechanism reaches the
fivefold target.

#### M4b: coupled-rotation magnitude oracle

The high-upside hypothesis is the paired coupling

```text
Q ~ Haar,
Q' = Q R_AJ.
```

This is **not** presumed cache-supported. Existing per-rotation outputs may be
used only if they contain the exact frozen `(Q, Q R_AJ)` pair for the same
network, pilot state, frames, and estimator path. A generic cached rotation, a
relative rotation of the wrong conjugacy class, or an algebraically transformed
output is not a substitute. If no exact pair exists, M4b is the first new
premise-only forward and requires a separate immutable predeclaration,
authorization, resource meter, and receipt. M4a's cache-only authority does not
carry over to it.

For fixed weights and fixed orthogonal `R_AJ`, right invariance makes `Q'` Haar
whenever `Q` is Haar. (The multiplication side must be frozen with the code's
row/column convention; Haar is invariant on either fixed side.) Thus each arm
has the same marginal spherical law; only their dependence changes. This
theorem does not by itself validate the deployed deterministic seed map,
radial approximation, adaptive pilot decisions, or a frame split.

Do not infer the covariance from `rank(P_AJ)` or from S6's 32,256-dimensional
degree-4 design operator: those are different spaces. Let the centered
full-estimator error be `e(Q)` and define the induced Haar-space involution

```text
(U_R e)(Q) = e(Q R_AJ),
Pi_-       = (I - U_R)/2.
```

Only for this induced action does the equal-variance identity

```text
Corr(e(Q), e(Q R_AJ)) = 1 - 2 ||Pi_- e||^2 / ||e||^2
```

hold. The fraction on the right is energy in the negative eigenspace of
`U_R`, not input-projector rank divided by design-span rank. The mandatory
sanity check is `R_AJ=-I`: because the design is antipodally doubled and the
remaining harmonic errors are even, the estimator is unchanged and the
correlation is `+1`, not `-1`. Any surrogate predicting the latter is rejected
before it can screen the mechanism. A theoretical S6-to-covariance bound may
replace direct measurement only if its intertwining map is written down and
proved for the actual nonlinear estimator.

Estimate the paired error covariance only on held-out rotations/nets. If two
half-budget arms each have approximately twice the full-budget variance, their
equal average has approximate ratio

```text
V_pair / V_W0 = 1 + rho,
```

before design-degradation and feature cost. The committed M195 63+63 topology
already measured a geometric-panel design debt `r_ind = 1.113996` even with
independent halves. With effective paired covariance

```text
kappa = 2 Cov(e_Q,e_Q') / (Var(e_Q)+Var(e_Q')),
r_score = r_ind (1+kappa) (1+DeltaC/C0),
```

parity needs `kappa <= -0.1023`, a 20% win needs `kappa <= -0.2819`, and
a fivefold score ratio `0.2` needs `kappa <= -0.8205` before overhead. The
predeclared winner-magnitude gate is therefore
`upper_90_CI(kappa) <= -0.82`, plus the direct adjusted-score gate. A cheaper
premise screen may use `upper_90_CI(kappa) <= -0.282`; passing it earns only
the next rung, not a winner claim.

**Fatal:** nonnegative covariance, failure to beat a random rank-matched
reflection, insufficient magnitude, or benefit limited to the fitting nets.

### M5 — first actual estimator mutation: budget-neutral coupled frames

Only after M4b passes. Keep 126 complete frames and all antipodes, but use a
frozen 63/63 assignment:

```text
63 complete frames under Q,
63 complete frames under Q R_AJ.
```

Each complete orthonormal frame contributes `I/d` to the second moment, so the
union remains an exact spherical 2-design; antipodes retain all odd-degree
zeros. This does not preserve the parent's cross-frame mutual-unbiased geometry,
and M180's random remix was strongly harmful. The random reflection control is
therefore load-bearing: the child survives only if weight-conditioned negative
covariance overcomes the known remix penalty.

No truth, scorer output, held-out label, or final-path value may enter
`P_AJ`, the frame assignment, or the seed map. Every pilot, tangent, eigensolve,
and transformation is billed. The parent's adaptive pruning/folding cannot be
learned from one arm and silently applied to the other: either both arms use an
independent, fixed, fully billed shared pilot, or the child is explicitly
classified as introducing bias and must pass a separate frozen bias gate.

**Promotion gate:** on fresh whole networks with common random numbers, the
upper 90% CI of the complete adjusted-score ratio is below both `1.0` and the
predeclared rank-target ratio; zero failures; no tail-net regression; all
resource limits and guards pass.

### M6 — declared-axis transfer and hostile suite

Cross the mechanism's actual axes rather than reflexively testing only width:

- depth / gate coherence: at least 8, 16, and 32;
- seed and network families;
- rank and layer band, with one frozen primary and corrections for controls;
- dtype and announced cost model;
- positive instrument fixtures;
- adversarial nets that collapse, saturate, permute, or rescale gates.

The production point remains mandatory. Unrun perturbations are listed.

**Fatal:** sign reversal, hidden subgroup dependence, width/depth transfer
failure, any unmetered path, or a detector that can return a structural zero.

### M7 — factorial combination, package, and one lawful canary

Only independently passing mutations may combine. Use a `2x2` factorial:

```text
W0,
W0 + compute child,
W0 + AJ coupling,
W0 + both.
```

This exposes antagonism instead of assuming multiplicative gains. Rebuild the
package from frozen sources, validate exact members/hashes, rerun guard positive
controls, measure full FLOPs/residual/RSS/wall, and consume a hosted canary only
under the published Phase-2 authority.

## Fish-schooling bridge: what is useful and what is not

The useful abstraction is sparse, topological influence:

- modes are agents;
- squared cross-layer overlaps define influence weights;
- retain the one or two strongest neighbors per mode rather than a metric
  radius;
- concentrated continuation is "schooling";
- diffuse mixing is "swarming";
- signed cycles/frustration are "milling";
- sudden leakage is a "burst" or mode-conversion event.

Those labels generate hypotheses only. The mathematical objects are the
transition weights, cycle products, frustration, forward tangent response, and
paired covariance. Biological resemblance is never evidence.

## MiroFish boundary

MiroFish is a local LLM social-agent simulator, not a fish-physics simulator.
It may run a blind council that proposes counterexamples, controls, and failure
modes from this document. Its output cannot choose a rank, threshold, layer,
seed, frame subset, or winning arm, and it receives no held-out result. Every
suggestion re-enters at M1 or M2 and must survive the same gates.

## Stop rules

Stop the branch immediately if any of these occurs:

1. The proposed score is a quadratic frame energy; complete bases make it a
   trace constant.
2. The mechanism is only the killed diagonal `kappa3/kappa4`, JSpace
   top/bottom/complement, or exact reverse-adjoint family with new language.
3. The split-sample residual does not clear its own measurement floor.
4. The weight-side proxy has held-out `|rho| < 0.4` or a sign reversal.
5. Coupled residual covariance cannot approach the declared magnitude gate.
6. A selector uses truth/scorer/held-out outputs or lacks an inclusion/bias
   proof.
7. Full billed cost, residual, memory, or failure rate erases the gain.
8. Phase-2 rules make the mechanism unlawful or unscoreable.

## Current decision

`W0` remains the winner. The next lawful work is M1--M4 design and cached
falsification only. No production mutation is earned yet.
