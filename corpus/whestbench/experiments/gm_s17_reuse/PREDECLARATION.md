# PREDECLARATION -- gm_s17_reuse (graveyard revival, ledger id s17_information_complexity_lower_bound)

Written BEFORE any code was run in this directory. Mining search key:
`s17_information_complexity_lower_bound`. Mining record: workflow
`wf_436a0c3d-2f0` journal line 37, revival_candidates[1].

## 0. DEVIATIONS DECLARED UP FRONT (loud, before any compute)

1. **Numerator harmonization.** S17's per-net `champion_mse` came from S16: a
   RAW MSE (16 rotation replicates) against the cached m181 3.5M-sample MC
   truth, so it carries an un-subtracted truth-MC floor of roughly
   `mean_j Var_j / 3.5e6` (~3.1e-8 on a ~0.11 field, i.e. ~+16% on a 2e-7
   champion MSE). The 80-net m185 panel instead ships `mse_raw` (single
   rotation draw, r=0, 600k-sample truth) together with `floor31` and
   `mse_corr = mse_raw - floor31`. I therefore run TWO numerators:
   - PRIMARY `champ_corr_i = mse_corr_i` (floor-corrected estimator MSE);
   - S17-CONVENTION `champ_s17_i = mse_corr_i + (floor31_i * 600000) / 3.5e6`
     (adds back exactly the 3.5M-sample truth floor S17's numerators carry).
   The gate is evaluated on BOTH; the PRIMARY is the decisive one, the
   S17-convention one is the like-for-like comparison against 1.7907.
2. **Single-draw numerator noise.** m185 stage-1 is ONE rotation per net
   (r=0), where S17/S16 averaged 16. M185_G0_NOTES records within-net
   single-draw MSE spreads of 2.3-8.7x. Each per-net ratio is still an
   unbiased estimate of that net's ratio, so the pooled mean is unbiased, but
   the per-net sd (and hence the CI) will be wider than the mining record's
   "se ~0.06 at n=80" projection, which assumed net-level dispersion only.
3. **Design/rotation lineage.** m185 rotation seed formula `900000 +
   net_seed*1000 + r` at r=0 is IDENTICAL to the S5/S16/n8a formula, and the
   frozen v3 `_haar_rotation` (estimator.py:138) is mirrored verbatim by
   `n8a.haar_rotation`. sigma^2 is measured on exactly the rotated design the
   m185 estimator sampled. Frozen v3 `n_base = 126*256 = 32256`
   (estimator.py:47), antipodally doubled -> `N_FULL = 64512`; this is the
   denominator S17 gated on.
4. No estimator is modified, no submission, no held-lane (m245/M243/M244)
   contact, no network, no git. Synthetic He nets (`n8a.he_mlp_weights`,
   bit-identical to m185's `he_weights`) plus committed cached JSON/NPZ only.

## 1. MECHANISM UNDER TEST

Not a mechanism revival: a PRECISION revival. S17's gate-(i) verdict ("the
champion sits at the point-evaluation floor") rests on n=3 nets, pooled
`champ/(sigma^2/64512) = 1.7907`, sd 0.5156, se 0.2977, t95 CI
[0.5097, 3.0717] -- a CI spanning 6x that includes the champion being AT or
BELOW its own floor. The mined claim is that S17's section-A instrument
(built once, used on 3 nets, never reused) can be re-run response-free on the
committed 80-net m185 panel to collapse that CI.

## 2. EQUATION / QUANTITY (S17 section A, verbatim reuse)

For each net seed `s`:
- `R = haar_rotation(900000 + s*1000 + 0)` (float32 QR, sign-fixed).
- `W = he_mlp_weights(s)` (float32 He, width 256, depth 32).
- `first_eff = (R.T @ W[0]).astype(float32)`.
- `pre1 = kerdock_base @ first_eff`, `act = [relu(pre1); relu(-pre1)]`
  (64512 x 256), then `act = relu(act @ W[l])` for `l = 1..31`.
- `ybar(u) = mean over the 256 neurons of the layer-31 post-ReLU activation`,
  float64; `sigma2_s = Var(ybar)` (population, ddof=0).
- `floor_s = sigma2_s / 64512` (equal-FLOP accounting -- S17's gated
  denominator; `sigma2_s / 32256` is the distinct-direction accounting, also
  reported).
- `ratio_s = champ_s / floor_s`.
Pooled: mean, sd (ddof=1), se, two-sided 95% t CI with n-1 df.

## 3. PREDICTED OUTCOME (on record, before running)

- **Step 0** (re-derive S17's three-net numbers from the cached S5 arrays):
  PASS, relative error < 1e-12 on all three `ratio_champ_over_costfloor`.
- **n=20 PRIMARY pooled ratio**: point prediction **1.5**, predicted interval
  [1.2, 1.9]; predicted 95% CI half-width <= 0.35.
- **n=20 S17-CONVENTION pooled ratio**: point prediction **1.75**, predicted
  interval [1.4, 2.1] (i.e. reproducing S17's 1.7907 within its own noise).
- **Predicted gate: STANDS** (CI lower bound > 1.2), but flagged MARGINAL: if
  the pooled lands near 1.4 with half-width ~0.3 the CI straddles 1.2 and I
  extend to all 80 nets as the mining record prescribes.
- **Diagnostic cross-check accounting** (NOT gated): the per-output iid floor
  `mean_j Var_j / 64512 = floor31_s * 600000 / 64512`. Predicted
  `champ / that floor` ~ 0.1, i.e. the champion sits an order of magnitude
  BELOW the per-output iid floor because it carries an analytic control
  variate. If this obtains it is a finding about WHICH object S17's "point
  evaluation floor" is, recorded but not gated.

## 4. GATES (verbatim from the mining record's cheapest_falsifier)

> the floor claim STANDS if the n=80 pooled champ/(sigma^2/N_forwards) 95% CI
> excludes 1.2 from below; REOPENS if the CI includes 1.0; REOPENS UPWARD if
> it excludes 2.5 from above. [...] run 20 first and extend only if the CI
> still straddles 1.2.

Operationalized:
- `STANDS`      iff `ci_lo > 1.2`
- `REOPENS`     iff `ci_lo <= 1.0 <= ci_hi`
- `REOPENS_UPWARD` iff `ci_lo > 2.5`
- `STRADDLES_1.2` iff `ci_lo <= 1.2 <= ci_hi` and not REOPENS -> extend n=20 -> n=80.
Staging: n=20 (seeds 1000..1019) first; extend to all 80 (1000..1079) if the
n=20 CI straddles 1.2 or includes 1.0.

## 5. STEP-0 ARITHMETIC KILL GATE (run first, stop if it kills)

Re-derive, from the committed `s5_net{101,202,303}_arrays.npz` and the
committed S16/m181 champion MSEs, every number in `s17_results.json`
section A_per_net / A_pooled. KILL CONDITION: if any of the three
`ratio_champ_over_costfloor` fails to reproduce to relative error < 1e-12,
the mined instrument is NOT the object in the record, the reuse premise is
falsified at step 0, and I stop and report that.

## 6. TWO-SIGNAL VERIFICATION (predeclared)

- **S1 numerator, independent recomputation**: recompute `mse_raw` from the
  checkpoint's stored 256-vectors `pred31`, `truth31` and require agreement
  with the stored `mse_raw` to relative error < 1e-12, for every net used.
- **S2 split-sample**: split the panel by parity of net_seed; both halves'
  pooled ratios and CIs must agree on the gate verdict.
- **S3 bit-repeat**: recompute `sigma2` for 3 nets through an independent code
  path (frame-blocked chunked accumulation, different summation order) and
  require agreement to relative error < 1e-12.
- **S4 permutation-free sanity**: `sigma2` computed two ways per net --
  `Var(ybar)` and `mean((ybar - mean(ybar))**2)` -- S17's own two-way check.

## 7. WHAT EACH OUTCOME MEANS

- `STANDS`: S17's gate-(i) verdict is EARNED at n>=20; the mined "precision
  revival" yields no change of decision; U18's dichotomy holds. The revival
  candidate is KILLED as a decision-mover while the original record is
  CONFIRMED. Reported plainly as a success.
- `REOPENS`: the champion is AT/BELOW its own floor at n>=20; S17's headline
  and the "ednacob-honest is IMPOSSIBLE" arithmetic must be withdrawn.
- `REOPENS_UPWARD`: in-frame headroom the campaign has been calling exhausted.

## 8. COMPUTE ENVELOPE

Estimated ~3-9 s/net for the 64512-direction depth-32 forward (2.6e11 FLOPs,
float32). n=20 ~2 min; n=80 ~8 min. Well inside the 90-minute envelope. If it
overruns, the harness checkpoints per net and resumes in the foreground.
