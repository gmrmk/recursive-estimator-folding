# PREDECLARATION - gm_flatworm revival of `flatworm_response_ladder` (fold ledger idx 33)

Written 2026-08-10 BEFORE any candidate accuracy number was computed.
Mining key: `flatworm_response_ladder`. Ledger record: `corpus/whestbench/headroom/fold_ledger.json`
candidate index 33, `status = proposed`, no `result` field.

## DEVIATIONS (recorded loudly, at the top)

1. **Artifact location.** The mined falsifier names `P0_FREEZE_AUDIT.json` and the
   frozen 24-state bank. Neither the bank nor the parent/dual code is inside the
   publish repo (only the reports are). The frozen sources live in the working tree
   at `work/scorefloor_generation/{latent_randomized_radial,
   randomized_radial_susceptibility_compressor,
   randomized_radial_dual_observable_compressor, flatworm_ladder_attenuator}`.
   Those files are imported READ-ONLY and unmodified; all new code is in this
   directory. `P0_FREEZE_AUDIT.json` (in `flatworm_ladder_attenuator/`) audits the
   *router* P0/P1 (physarum) artifacts, not the 24 compressor states; the 24 states
   are frozen instead by `gate_contract.json` of the dual-observable run
   (cases, rotation seed 104729, snapshot layers `0, floor(L/2), L-2`). I therefore
   re-derive the 24 states from that frozen contract and verify them bitwise against
   the frozen `frozen_states()` generator (see cross-check X1).
2. **Baseline provenance.** The scalar-fusion baseline (idx 27) is re-run here with the
   unmodified frozen module and must reproduce the committed
   `one_step_results.json` aggregate `0.9659440475280408` / `17` wins exactly. If it
   does not reproduce, the run is BLOCKED, not reinterpreted.
3. **AMENDMENT A1 (written before any run, cost-accounting only).** The lane evidence
   `e_l = lambda_max(G_l)/tr(G_l)` is computed in the deployed controller by a fixed
   64-step power iteration from the permutation-equivariant all-ones start vector, not
   by a full eigendecomposition. Reason: charging two extra full `eigh` per layer at
   `2 * 9 * depth * width^3 = 9.66B` would push the conservative n256/L32 bound to
   `84.0B` and kill the record on an accounting choice rather than on the mechanism.
   The exact `eigvalsh` value is still computed and reported as a diagnostic
   (`max_abs_evidence_difference`). No accuracy number was seen when this amendment was
   written.
4. No other deviation. Scope is exactly the mined cheapest falsifier: one pass over the
   24 frozen P0 states, two-lane controller vs scalar fusion. No new states, no
   n=128 branch, no truth/scorer/holdout/private read, no submission, no git.

## Mechanism under test

Idx 32 killed the flatworm ladder as an *allocation* transform over a four-expert
router. Idx 33 applies the same frozen topology to a different object: a **two-lane
depth controller** over the two response geometries of the killed scalar-fusion
compressor (idx 27), which averaged them 1:1 by trace and lost their late contrast
(gate/active Gram cosine falls 0.72-0.75 at layer 0 to 0.15-0.25 late).

Per layer `t` of the frozen forward pass, with `mu = m W_{t+1}`,
`Sigma = W_{t+1}^T C W_{t+1}`, `sigma = sqrt(diag Sigma)`, `alpha = mu/sigma`,
`R = diag(1/sigma) Sigma diag(1/sigma)`:

```text
lane 1 (gate)   G1(t) = diag(phi(alpha)) R diag(phi(alpha)) / tr(.)
lane 2 (active) G2(t) = diag(Phi(alpha)) R diag(Phi(alpha)) / tr(.)
```

Ladder state (constants inherited verbatim from the frozen
`flatworm_ladder.py`: `RHO = 0.5`, `KAPPA = 0.25`; pair map = lane swap):

```text
evidence      e_l(t) = lambda_max(G_l(t)) / tr(G_l(t))          in (0,1]
longitudinal  m_l(0) = e_l(0);  m_l(t) = RHO*m_l(t-1) + (1-RHO)*e_l(t)
commissural   [d1,d2]^T = (I - KAPPA*L) [m1,m2]^T,  L = [[1,-1],[-1,1]]
lane weights  w_l(t) = d_l(t) / (d1(t)+d2(t))        (arm A2)
fused Gram    F_ctrl(t) = w1(t)*G1(t) + w2(t)*G2(t)
```

then the unchanged idx-27 pipeline: unique top eigenvector `v` of `F_ctrl`,
standardized pullback `d = W diag(1/sigma) v / sqrt(v^T R v)`, unchanged signed
equal-mass q3 bins with exact within-bin first/second moments.

`w1 = w2 = 1/2` reproduces the killed scalar fusion exactly (the fused Gram is then
`0.5 * F_dual`, same top eigenvector), so the controller is a strict generalization
and the comparison is like-for-like.

Depth and coefficients are fixed a priori; no reference outcome, oracle value, error,
or idx-27 per-state result enters the controller. The controller function receives
only `(children cloud, next weight)` of the forward pass.

## Arms (predeclared, no others)

- **A0 scalar fusion** - frozen `dual_reduce_components` (idx 27), unmodified import.
- **A0c controller with fixed w=(0.5,0.5)** - harness equivalence check only.
- **A1 + longitudinal leak** - `w_l = m_l / (m1+m2)` (no commissural coupling).
- **A2 + commissural diffusion** - full two-lane controller, THE candidate.
- **GEN generic compressor** - unchanged parent, the common denominator.

## Step 0 (arithmetic/structural gate, run FIRST, STOP if it kills)

The mined falsifier: "The predeclared lane-collapse check is cheaper still - if either
lane's contribution goes to zero the record dies before any accuracy number is needed."

**G2 LANE COLLAPSE:** over every case and every layer `t = 0..depth-2`,
`min(w1(t), w2(t)) > 0.01`. If any lane weight falls to <= 0.01 the record is KILLED at
step 0 and no accuracy number is reported.

## Gates (from the ledger kill condition of idx 33, verbatim scope)

Ledger kill condition: "No improvement over scalar fusion on fresh states, any collapse
to one lane, use of reference outcomes to set depth/coefficients, broken symmetry/PSD/
moments, or target cost at least 80B."

- **G1 IMPROVEMENT (decisive).** `ratio_A2 < ratio_A0` strictly, where
  `ratio_X = sqrt( sum_s e_X(s)^2 / sum_s e_GEN(s)^2 )` over the 24 states and
  `e = hypot(mean rel err, covariance rel err)` against the uncompressed one-step
  point-cloud reference. Reference value `ratio_A0 = 0.9659440475280408`.
  KILL if `ratio_A2 >= 0.9659440475280408`.
- **G1b WINS (supporting).** head-to-head `A2` beats `A0` on `>= 13/24` states.
- **G2 LANE COLLAPSE.** as step 0 above.
- **G3 NO REFERENCE OUTCOMES.** controller signature carries no reference/observable
  argument; asserted structurally and by the recorded call graph.
- **G4 STRUCTURAL.** max source moment relative error `<= 1e-10`; min normalized
  covariance eigenvalue `>= -1e-10`; max permutation and positive-gauge unordered
  error `<= 1e-10`; zero spectral ambiguities; zero tie/degenerate collapses.
- **G5 COST.** conservative n256/L32 arithmetic with 25% contingency `< 80B`.
- **G6 FAMILY MATERIALITY (inherited, reported not decisive).** `ratio_A2 <= 0.80`.

VERDICT RULE: `REVIVED_PASS` requires G1 AND G1b AND G2 AND G3 AND G4 AND G5, plus both
verification signals agreeing. Anything else is `KILL_CONFIRMED`. No retuning of RHO,
KAPPA, the evidence functional, the lane definition, or the arm set after seeing any
number.

## Predicted outcome (on record, before running)

The mined revival record's `expected_gain` is "Zero for the score, and not close",
bounded by two measured numbers: the family's realized floor on these states is
`0.965944` (idx 27) and the best member ever reached is `0.911472` (idx 34, which
fails its own audit). **I predict KILL_CONFIRMED at G1**: `ratio_A2 >= 0.965944`,
landing in `[0.95, 1.00]`, with `A1` and `A2` differing from `A0` by less than 2% in
aggregate ratio. I predict G2 does NOT kill (the commissural operator
`(I - 0.25 L)` is nonexpansive and pulls the two lane weights toward each other, so
weights should stay near 0.5 and no lane can be starved), and I predict G4/G5 pass
(the controller changes only a positive convex weighting of two PSD Grams, leaving the
moment/PSD/symmetry/cost structure of idx 27 intact). The ledger's own prediction for
idx 33 - that the two-lane state "improves the scalar dual-observable compressor" - is
what I expect to be falsified.

## Two-signal verification (required for any PASS claim)

- **X1 state-bank fidelity.** My per-layer generator must reproduce the frozen
  `frozen_states()` snapshots bitwise (children weights/means and next weight/frame)
  for all 8 cases.
- **X2 baseline reproduction.** A0 rerun must equal the committed idx-27 aggregate
  `0.9659440475280408`, `17/24` wins, to `<= 1e-12` relative.
- **X3 harness equivalence.** A0c (controller at w=0.5) must equal A0 per-state joint
  error to `<= 1e-12` relative.
- **X4 bit-repeat.** Full run repeated; per-state joint errors identical bitwise.
- **X5 split-sample.** L16 (12 states) and L32 (12 states) sub-aggregate ratios
  reported separately; a PASS claim requires the same direction in both halves.
- **X6 paired permutation null.** 20000 random sign flips of the per-state
  `log(e_A2/e_A0)` differences; two-sided p-value for the observed mean.

## Compute envelope

The frozen idx-27 run took 11.81 s for 24 states. Four arms plus per-layer ladder
evidence is bounded by a few minutes, far inside the 90-minute envelope.
