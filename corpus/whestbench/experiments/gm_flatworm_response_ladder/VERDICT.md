# VERDICT - `flatworm_response_ladder` (fold ledger idx 33): KILL CONFIRMED

Run date 2026-08-10. Predeclaration frozen in `PREDECLARATION.md` before any code was
written and before any accuracy number existed. Machine-readable results in
`results.json` (full), `summary.json` (gates), `step0_results.json` (ladder trace),
`bit_repeat.json` (X4).

## Decision

**The two-lane flatworm depth controller does not improve on the killed scalar
dual-observable fusion. Ledger idx 33 is killed at its own first kill condition
("no improvement over scalar fusion on fresh states").** The kill is NOT by lane
collapse, NOT by broken symmetry/PSD/moments, NOT by cost, and NOT by any use of
reference outcomes: every one of those gates passed. The mechanism ran cleanly and
was measured; it is simply not better.

## Decisive numbers (verbatim)

| arm | aggregate one-step RMS ratio vs generic | wins vs generic | head-to-head wins vs scalar fusion |
|---|---:|---:|---:|
| generic q3 (denominator) | 1.0000000000 | 0/24 | - |
| scalar fusion (idx 27) | **0.9659440475280408** | 17/24 | - |
| controller at w=(0.5,0.5) | 0.9659440475280408 | 17/24 | 0/24 (bitwise identical) |
| + longitudinal leak (A1) | 0.9664838665220531 | 17/24 | 11/24 |
| **+ commissural diffusion (A2, the candidate)** | **0.9667868818213292** | 17/24 | **12/24** |

`ratio_A2 - ratio_A0 = +0.0008428342932884636` (the controller is **worse**).

Gates:

```text
G1  improves on scalar fusion            FAIL  (0.9667868818213292 >= 0.9659440475280408)
G1b head-to-head wins >= 13/24           FAIL  (12/24)
G2  no lane collapse (step 0)            PASS  (min lane weight 0.4096460665624148 > 0.01)
G3  no reference outcomes in controller  PASS  (controller sees only (cloud, next weight))
G4  exact source moments <= 1e-10        PASS  (5.171651206593552e-15)
G4  PSD >= -1e-10                        PASS  (-3.3592466699482446e-16)
G4  permutation <= 1e-10                 PASS  (6.896234698024585e-14)
G4  positive gauge <= 1e-10              PASS  (1.0348284358569968e-15)
G4  lane-evidence invariance <= 1e-10    PASS  (6.661338147750939e-15)
G4  spectral ambiguities / collapses     PASS  (0 / 0)
G5  conservative n256/L32 cost < 80B     PASS  (73.316433920B)
G6  family materiality ratio <= 0.80     FAIL  (0.9667868818213292, reported not decisive)
```

## Step 0 (run first, as mined)

The mined cheapest falsifier named the lane-collapse check as the pre-accuracy gate.
Over 184 scored layers across the 8 frozen cases:

```text
minimum leak lane weight         0.31929213312482974
minimum commissural lane weight  0.4096460665624148
gate floor                       0.01
```

Step 0 did **not** kill, so the accuracy pass ran. The commissural gate-lane weight
spans `[0.409646, 0.521280]` (mean `0.471792`) and correlates with the lane cosine at
`+0.4566`: the controller does move, in the predicted direction (more weight to the
active lane where the lanes decorrelate), by at most ~18% relative. That movement is
real and it is not enough.

## Two-signal verification

- **X1 state-bank fidelity (bitwise).** My per-layer ladder generator reproduces the
  frozen `frozen_states()` snapshots exactly for all 24 states: children weights/means,
  next weight, next frame all bitwise equal. PASS.
- **X2 baseline reproduction.** The scalar-fusion arm reproduces the committed idx-27
  artifact exactly: `0.9659440475280408` and `17/24`, relative difference `0.0`. PASS.
- **X3 harness equivalence.** The controller at `w=(0.5,0.5)` equals scalar fusion with
  max relative per-state difference `0.0`, so the controller is a strict generalization
  and the comparison is like-for-like. PASS.
- **X4 bit repeat.** Full independent rerun; results JSON identical excluding timing,
  SHA-256 `2e0b3145094cfa22545dc483d8346b6a9bcd7bae4c9a2240aef39007c1af08fb` both runs.
- **X5 split sample.** L16 (12 states): scalar `0.9679743760679285` vs commissural
  `0.9679507536950875` (commissural better by `2.4e-5`), 7/12 head-to-head.
  L32 (12 states): scalar `0.9638794884616851` vs commissural `0.9656044595231655`
  (commissural worse by `1.7e-3`), 5/12. The two halves disagree in direction, so the
  predeclared consistency requirement for a PASS claim fails independently of G1.
- **X6 paired permutation null.** Mean paired `log(e_A2/e_A0) = -0.015449637328657046`
  over 24 states, 20000 sign-flip draws, two-sided `p = 0.11014449277536123`, null SD
  `0.011558267653522206`. Even under the unweighted paired statistic - the metric most
  favourable to the controller - the effect is not distinguishable from noise.

## Attack on the conclusion

The strongest counter-hypothesis is that the aggregate metric hides a real deep-layer
repair: layer-0 states carry ~96% of the generic joint-error energy, so a controller
that only helps deep states cannot register. The evidence against rescuing the record
on that basis is X6 plus the per-state table in `results.json`: the controller's single
best state is `(L32, layer 30, seed 18720)` at ratio `0.76582` and it also loses on 12
of 24 states, including `(L16, layer 14, seed 18560)` at `1.01000` and
`(L16, layer 8, seed 18563)` at `1.00973`. The unweighted paired statistic that would
credit the deep repair returns `p = 0.11`, and the split halves disagree. The deep
repair is a signature, not a promotion.

Second counter-hypothesis: the controller is too timid (weights only move within
`[0.41, 0.52]`), so this tests a weak instantiation rather than the two-lane family.
That is true and is recorded as the honest scope of this kill: what dies here is the
predeclared flatworm longitudinal+commissural recurrence as the depth controller for
these two response lanes, with the ladder's own frozen `RHO=0.5, KAPPA=0.25`. The
commissural operator `(I - 0.25 L)` is by construction a contraction toward equal lane
weights, so the topology that idx 32 preserved is exactly the topology that prevents
this controller from expressing strong late contrast. Choosing a different evidence
functional, a larger `KAPPA`, or a genuine rank-two partition after seeing these
numbers would be post-result tuning and is not done.

## Scope of the kill (what the ledger should now record)

Idx 33 moves from `proposed` to `killed`. The kill is scoped and measured:

- Killed: the flatworm longitudinal/commissural recurrence as a depth-varying convex
  lane weighting over `F_gate`/`F_active` for q3 response geometry. It is worse than
  1:1 trace fusion by `+0.00084` aggregate ratio and wins only 12/24 head to head.
- Preserved (unchanged by this result): both response Grams as separate gauge-invariant
  metrics, the standardized pullback, exact q3 moment/PSD/symmetry structure, and the
  open leaf that idx 27 actually named - a fixed **rank-two** response-subspace
  partition, which is a different object from a scalar reweighting and is untested.
- Also measured here and new: the leak-only arm (`0.9664838665220531`, 11/24) is also
  worse than scalar fusion, so the degradation is not caused by the commissural
  coupling alone; longitudinal depth memory over these lanes is itself unhelpful.
- The expert-bank oracle bound (`0.8290544993`) that made idx 32's accuracy claim
  nonidentifiable indeed does not apply here, as the mining record argued. It did not
  need to: the record dies on its own like-for-like comparison.

## Firewall statement

No truth vector, prediction array, WHest row, scorer, holdout, private or official
data, API, leaderboard, submission, network call, or git command was read or made.
Frozen sources under `work/scorefloor_generation/` were imported read-only and are
unmodified, verified by re-hashing them now and comparing against the hashes recorded
inside the original committed runs:

```text
gate_contract.json            241b3e04f4bfc20a14e50db513684dd5b01decc160a60f09cb7c9f05b65e49a1  (matches idx-27 one_step_results.json)
dual_observable_compressor.py 5c7dd33a5629b857cd8a37fd094dfd42a60d581054548df70ca6f77e74d51355  (matches idx-27 one_step_results.json)
randomized_radial.py          150657841fb72b3150e32fe465fb4c24d12c4d11e90df2ce9f1dc22b306215cf  (matches both published reports)
``` The held m245/M243/M244
lane was not read or touched. All writes are confined to this directory.
