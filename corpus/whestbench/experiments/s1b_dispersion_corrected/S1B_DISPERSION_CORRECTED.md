# S1B (s1b_dispersion_corrected) — dispersion-corrected suite-risk model

Date: 2026-08-10. Harness: `run_s1b.py` (this directory; copy of
`s1_suite_risk/run_s1.py` with ONLY the dispersion parameter varied).
Full numbers: `s1b_results.json`. Feeds writeup v8.

Context: a verified red-team finding says the committed S1/U9 suite-risk model
(DIFF_RATIO = 1.1, vD = 7.57e-4) understates per-net difficulty variance. This
re-run derives vD from the committed evidence, re-simulates the champion's
suite-score distribution at the corrected values, and validates against the
observed hosted 80-net spread (15.53x).

## Deviations from the dispatch task

1. The task quoted the p2-implied vD as 0.239–0.370 (subtraction-only
   deconvolution `v_obs − vF/16`). The harness uses the deconvolution that is
   exact under the model it simulates, `vD = (v_obs − vF/16)/(1 + vF/16)`,
   giving 0.2335–0.3614. Both are recorded in `s1b_results.json
   vD_derivation`; the difference (~2.4% in vD) changes nothing downstream.
2. Each measured arm was run at BOTH endpoints of its task-stated range
   (s17: 0.081/0.122; p2: 0.2335/0.3614), 5 vD values total including the
   control. R is fixed at 1 (the champion designation, U9 slot A); S1's
   R∈{2,4,6} arms were not re-run — an analytic note on the R=6 gate under
   corrected vD is given instead.
3. Output extensions beyond run_s1.py, required by the task: 100-net suites
   (new seed children), threshold grid {1.55, 1.6, 1.83, 2.0, 2.5}e-7,
   per-arm 80-net bracket test, and a 1e6-suite tail refinement. The model
   (log-uniform difficulty, P2 rotation pool, anchor 1.83e-7, seed prefix) is
   unchanged.
4. Harness defect found and fixed during verification: `SeedSequence.spawn`
   mutates spawn state, so the first run gave successive arms different seed
   children and the bitwise-repeat cross-check failed on non-control arms.
   Fixed by deriving the seed layout fresh per arm (true common random
   numbers). Control reproduction of the committed run was unaffected in both
   runs; all cross-checks pass in the final run.

## 1. Measured vD, derived from committed evidence (n = 3 nets each)

Notation: vD = Var(D)/E[D]^2 of the per-net difficulty factor;
vF = 0.36420 = rotation-factor variance from the P2 pool (48 values,
asserted equal to the committed S1 calibration).

(a) s17 per-net `sigma2_var(ybar)` (rotation-free by construction):
{7.9005e-3, 1.60021e-2, 1.11248e-2}, mean 1.16758e-2, max/min 2.03x.
Relative variance: ddof=0 → **vD = 0.0814**; ddof=1 → **vD = 0.1220**.
Caveat: using sigma^2 as the difficulty factor assumes MSE_i ∝ sigma_i^2
(equal N_eff); s17 shows N_eff/N_eval varies 0.42–0.73, so this is a lower
anchor on champion-MSE dispersion.

(b) p2 per-net 16-rotation mean MSEs (`q1_oracle_headroom`):
{1.99720e-7, 5.87209e-7, 2.36925e-7}, mean 3.41284e-7, max/min 2.94x
(cross-checked against s17 `champion_mse`: max rel diff 1.8e-6).
Observed relative variance: ddof=0 → 0.26160; ddof=1 → 0.39240.
Rotation noise of a 16-rotation mean under the model: vF/16 = 0.022762.
Deconvolved vD = (v_obs − vF/16)/(1 + vF/16): ddof=0 → **0.2335**;
ddof=1 → **0.3614** (subtraction-only: 0.2388/0.3696, the task's quote).

Both estimates rest on n=3 nets (a chi2(2) CI on a ddof=1 variance spans
~[0.27x, 39.5x]), so the point values are wide. The third, independent signal
that disciplines the range is the observed 80-net spread below.

## 2. Bracketing test — the required verification

Simulated 80-net single-draw max/min spread of D·F (10,000 replicates,
identical seed and code path to S1 cross-check 3) vs the observed hosted
spread 15.53x (m185 stage1 `mse_raw`; identical value in
`a1b_tail_diagnostics.json`):

| arm | vD | DIFF_RATIO | sim spread P5 | P50 | P95 | P(sim ≥ 15.53) | brackets 15.53x? |
|---|---|---|---|---|---|---|---|
| old_control | 7.57e-4 | 1.10 | 9.14 | 11.18 | 11.94 | 0.000 | **NO — understates** |
| s17_low | 0.0814 | 2.71 | 11.64 | 18.19 | 25.51 | 0.720 | **YES** |
| s17_high | 0.1220 | 3.40 | 13.19 | 21.22 | 31.21 | 0.862 | **YES** |
| p2_low | 0.2335 | 5.55 | 17.64 | 30.43 | 48.14 | 0.978 | NO — overshoots |
| p2_high | 0.3614 | 8.67 | 23.95 | 43.19 | 72.09 | 0.999 | NO — overshoots |

The control row reproduces the committed `s1_results.json` cross-check to
1e-12 (asserted), including the P5/P50/P95 = 9.14/11.18/11.94 that
S1_VERDICT.md Limitation 1 already flagged against the observed 15.53x.

**Bracketing verdict: PASS.** The old model fails the bracket (observed spread
above its P95 — it understates dispersion); the corrected model at the
s17-implied vD ~0.08–0.12 brackets the observation. The p2-implied 0.23–0.36
overshoots it under the committed log-uniform shape — consistent with its n=3
estimate being dragged up by the net-202 outlier — so 0.08–0.12 is the
operative corrected range and 0.23–0.36 is an upper sensitivity, not the
central model.

## 3. Champion suite-score distributions (R=1, anchor 1.83e-7, 1e6 suites)

50-net suites:

| arm | vD | mean | SD | P5 | P95 | P(<1.55e-7) | P(<1.6e-7) | P(<1.83e-7) | P(<2.0e-7) | P(<2.5e-7) |
|---|---|---|---|---|---|---|---|---|---|---|
| old_control | 7.57e-4 | 1.830e-7 | 1.565e-8 | 1.583e-7 | 2.098e-7 | 0.0291 | 0.0641 | 0.514 | 0.859 | 0.99993 |
| s17_low | 0.0814 | 1.830e-7 | 1.786e-8 | 1.551e-7 | 2.137e-7 | 0.0491 | 0.0921 | 0.518 | 0.830 | 0.99954 |
| s17_high | 0.1220 | 1.830e-7 | 1.887e-8 | 1.537e-7 | 2.155e-7 | 0.0594 | 0.1058 | 0.519 | 0.818 | 0.99915 |
| p2_low | 0.2335 | 1.830e-7 | 2.141e-8 | 1.499e-7 | 2.200e-7 | 0.0871 | 0.1380 | 0.520 | 0.792 | 0.99729 |
| p2_high | 0.3614 | 1.830e-7 | 2.398e-8 | 1.460e-7 | 2.246e-7 | 0.1156 | 0.1687 | 0.522 | 0.769 | 0.99372 |

100-net suites:

| arm | vD | mean | SD | P5 | P95 | P(<1.55e-7) | P(<1.6e-7) | P(<1.83e-7) | P(<2.0e-7) | P(<2.5e-7) |
|---|---|---|---|---|---|---|---|---|---|---|
| old_control | 7.57e-4 | 1.830e-7 | 1.106e-8 | 1.654e-7 | 2.017e-7 | 0.0033 | 0.0143 | 0.511 | 0.933 | 1.00000 |
| s17_low | 0.0814 | 1.830e-7 | 1.261e-8 | 1.630e-7 | 2.044e-7 | 0.0086 | 0.0279 | 0.514 | 0.907 | 0.999997 |
| s17_high | 0.1220 | 1.830e-7 | 1.333e-8 | 1.619e-7 | 2.057e-7 | 0.0123 | 0.0354 | 0.514 | 0.895 | 0.999993 |
| p2_low | 0.2335 | 1.830e-7 | 1.512e-8 | 1.592e-7 | 2.088e-7 | 0.0246 | 0.0568 | 0.516 | 0.868 | 0.99995 |
| p2_high | 0.3614 | 1.830e-7 | 1.694e-8 | 1.564e-7 | 2.120e-7 | 0.0411 | 0.0809 | 0.517 | 0.843 | 0.99979 |

MC batch SE on the P-values is ≤ 5e-4 (per-chunk, 100 chunks); percentile
agreement between the 100k and 1e6 runs (disjoint seed streams) is within
0.12% everywhere. The mean is unchanged at 1.83e-7 in every arm — the
difficulty factor is mean-1 by construction; the correction widens the
distribution symmetrically-in-probability around the same anchor (both tails
grow: the lucky sub-1.6e-7 side AND the unlucky >2e-7 side).

## 4. HEADLINE for the writeup (replaces the "99.79% rotation-draw / 1.1x" claim)

**Corrected dispersion: vD ≈ 0.08–0.12** (s17-implied, validated by the
15.53x bracket; the old 7.57e-4 is ~100–160x too small; net max/min
difficulty ratio ~2.7–3.4x, not 1.1x). Under it, at R=1:

- **Across-suite variance split: 17–23% net-difficulty / 77–83%
  rotation-draw** (old claim: 0.21% / 99.79%). Under the p2-implied upper
  sensitivity the difficulty share reaches 34–42%.
- **Honest fresh-seed suite-score band for the champion (P5–P95):**
  - 50-net suite: **[1.54e-7, 2.16e-7]** (envelope of the bracketing arms;
    old model said [1.58e-7, 2.10e-7]). Upper sensitivity (p2_high):
    [1.46e-7, 2.25e-7].
  - 100-net suite: **[1.62e-7, 2.06e-7]**; upper sensitivity [1.56e-7, 2.12e-7].
- S1's PASS survives the correction: the analytic R=6 SD shrink is 44%/40%
  at vD = 0.081/0.122 (25% gate), and rotation-draw variance stays dominant
  (share 0.77–0.83). Only at the p2 upper sensitivity does the shrink
  approach the gate (33%/28%) and the rotation share fall to 0.66/0.58. The
  committed "99.79% rotation-draw" number and the 1.1x spread are wrong
  either way and should not be quoted.

## 5. Downside tail for the private re-run

P(champion suite-score worse than 2.5e-7), corrected dispersion, R=1
(1e6 suites, batch SE in brackets):

| suite size | old model | s17_low (vD 0.081) | s17_high (vD 0.122) | p2_low | p2_high |
|---|---|---|---|---|---|
| 50 nets | 6.7e-5 (8e-6) | **4.6e-4 (2.0e-5)** | **8.5e-4 (2.7e-5)** | 2.7e-3 (4.8e-5) | 6.3e-3 (7.9e-5) |
| 100 nets | <1e-6 | 3e-6 (2e-6) | 7e-6 (3e-6) | 5.2e-5 (8e-6) | 2.1e-4 (1.5e-5) |

The honest downside number: **P(worse than 2.5e-7) ≈ 0.05–0.09% on a 50-net
private suite** under the bracket-validated dispersion (7–13x the old model's
0.007%), rising to ~0.3–0.6% under the p2-implied upper sensitivity. On a
100-net suite it is ≤ 1e-5 (validated range) and ≤ 2e-4 (upper sensitivity).
For context at nearer thresholds: P(worse than 2.0e-7) is 17–18% at 50 nets
(9–11% at 100) under the validated range, vs 14% (6.7%) under the old model.

## Two-signal verification (all asserted or recorded in `s1b_results.json`)

1. Control arm reproduces committed `s1_results.json` exactly: R=1 mean, SD,
   P5, P95, P(<1.6e-7)=0.06434, chunk0 SHA-256, and the m185 spread
   validation P5/P50/P95 (asserts, rel tol 1e-12). The old-model bracket
   failure and the corrected-model bracket are therefore computed on the
   identical code path and seed as the committed run.
2. Analytic SD `S*sqrt((vD+(1+vD)vF)/n)` vs bootstrap SD: ratios within
   [0.999, 1.002] across all 5 arms x 2 suite sizes (independent derivation).
3. Bitwise repeat of chunk 0: SHA-256 identical, all arms.
4. 100k-suite and 1e6-suite runs (disjoint seed streams) agree on P5/P95
   within 0.12%.
5. Input cross-check: p2 16-rotation means vs s17 `champion_mse` (independent
   recomputation in s17): max rel diff 1.8e-6.

## Limitations

- All vD estimates come from 3 nets; the range, not the point values, is the
  deliverable. The 80-net bracket is the only wide-n signal and it selects
  the s17-implied range under the committed log-uniform difficulty shape.
- The log-uniform (bounded-support) shape is inherited from S1 unchanged. A
  heavier-tailed difficulty shape at the same vD would widen the simulated
  80-net spread and could re-admit larger vD; shape was not varied because
  the task pins "modify ONLY the dispersion parameter".
- The 80-net observed spread is a single realization of one hosted suite;
  P(sim ≥ obs) = 0.72/0.86 at the s17 arms means the observation sits in the
  lower half of the corrected model's spread distribution — comfortable, not
  tight.
- Anchor 1.83e-7 and the P2 rotation pool are taken from the ledger as
  given, as in S1.

## Files

- `run_s1b.py` — harness (this directory)
- `s1b_results.json` — full machine-readable results
- Inputs (read-only): `s1_suite_risk/s1_results.json`,
  `s17_ibc_floor/s17_results.json`, `pb1_premise_battery/p2_results.json`,
  `a_series_granular_adversarial/m185_g0_stage1_checkpoint.json`,
  `a_series_granular_adversarial/a1b_tail_diagnostics.json`
