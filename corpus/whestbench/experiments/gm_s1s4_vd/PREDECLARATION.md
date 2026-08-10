# PREDECLARATION — gm_s1s4_vd (graveyard revival of `s1_suite_risk_bootstrap`,
# with `s1b_dispersion_corrected` and `s4_designation_portfolio_bootstrap` downstream)

Written 2026-08-10 BEFORE any new computation in this directory. Mining search
key: `s1_suite_risk_bootstrap`. Mining record: journal.jsonl line 38,
`result.revival_candidates[0]`.

Everything below is fixed before the harness runs. No gate is retuned after a
result is seen.

## DEVIATIONS (declared up front, loudly)

D1. **The mined "definitive settling check" is NOT run.** The mining record names
    a settling check: "reuse S17's rotation-free per-net `sigma2_var(ybar)`
    instrument (`experiments/s17_ibc_floor/run_s17.py`, section A) on the
    committed 80-net panel instead of 3 nets". Verified this session: that
    instrument reads `s5_kink_concentration/s5_net{101,202,303}_arrays.npz`
    (`ybar` over the 64,512-point design). Only 3 such arrays exist in the repo;
    extending to the m185 80-net panel requires generating 80 synthetic He nets
    and running 64,512-point design forwards + a 600k-sample truth pass per net
    (m185 stage 1 billed ~26.5 s/net of *predict* time alone plus a 37.6 s truth
    wall on net 1000, i.e. > 80 min of the 90-min envelope for the truth passes
    alone, with no checkpointing in the S5 harness). It is outside the CHEAPEST
    falsifier the task instructs me to run and outside the compute envelope. It
    is recorded here as the named, un-run settling check.
D2. In its place I predeclare a *different*, free second signal that lives in the
    same file: the **floor-correlation ceiling** (gate G5 below). It is new to
    this falsifier and is therefore declared here before being computed.
D3. Arms added beyond the task's "vD 0.081 and 0.122": the S1/S4 re-runs also
    carry the committed control (vD = 7.57e-4) and the two moment-identity
    readings. Five arms total, matching S1b's arm count. Reason: the corrected
    S1 gates and the S4 Door-B number are only interpretable against the control
    and against the reading this falsifier derives.
D4. S1b's operative values are quoted in the task as 0.081/0.122; S1b's harness
    actually used 0.0814 / 0.1220 (`s1b_results.json`). I use S1b's exact values
    so the comparison is bit-comparable, and label them "0.081/0.122" arms.

## 1. Mechanism under test

S1b fixed the per-net difficulty dispersion `vD` by matching ONE order statistic
— the m185 stage-1 80-net max/min spread of `mse_raw`, 15.53x — with the
difficulty SHAPE frozen at S1's log-uniform, because its dispatch pinned
"modify ONLY the dispersion parameter". Under S1's own generative model
(`mse_i = S * D_i * F_i`, `D ⟂ F`, `E[D]=E[F]=1`) and on a panel with exactly
one distinct rotation per net, the relative variance of the observable obeys an
EXACT moment identity:

    relvar(mse) = Var(mse)/E[mse]^2 = (1+vD)(1+vF) - 1 = vD + (1+vD)*vF
    =>  vD = (relvar_obs - vF) / (1 + vF)              [shape-free]

The second moment therefore identifies `vD` with no shape assumption, and the
range is then free to identify the SHAPE (tail index). S1b spent the range on
`vD` instead, with the shape frozen — so its `vD` is shape-driven, not
moment-driven.

## 2. Quantities computed

Panel: `a_series_granular_adversarial/m185_g0_stage1_checkpoint.json`, 80 nets,
80 distinct `net_seed`, 80 distinct `rot_seed` (to be asserted).
Rotation pool: `pb1_premise_battery/p2_results.json` `q1_oracle_headroom.per_net`
`mse_per_rotation`, 3 nets x 16, per-net mean-normalized, pooled, mean forced to
1 — identical construction to `run_s1.py`, giving `vF`.

Two floor treatments, both to be reported:
  * **raw**: observable = `mse_raw`.
  * **corr**: observable = `mse_corr = mse_raw - floor31` (identity to be
    asserted exactly from the file).

Q1. `relvar_obs` at ddof 0 and ddof 1, per treatment.
Q2. `vD_moment = (relvar_obs - vF)/(1+vF)`, per treatment and ddof.
Q3. `share_D = vD/(vD + (1+vD)*vF) = vD/relvar_obs` (the "difficulty share of
    across-suite variance" that the writeup publishes as 17–23%).
Q4. Nonparametric bootstrap 95% CI on `vD_moment` (resample the 80 nets, 20,000
    reps, fixed seed), per treatment.
Q5. **Shape refit.** Difficulty shape family: `log D ∝ GenNormal(beta)`
    (exponential-power, density ∝ exp(-|x|^beta)), scale solved by bisection so
    that `Var(D)/E[D]^2 = vD` exactly on a fixed 2^22 presample; `beta = inf`
    reproduces S1's committed log-uniform exactly, `beta = 2` is lognormal,
    `beta = 1` is log-Laplace. Rotation factor `F` stays the committed empirical
    P2 pool, unchanged. For each `(vD, beta)` simulate 20,000 replicates of the
    80-net max/min of `D*F` and report P5/P50/P95 and `P(sim >= 15.5317)`.
Q6. S1 re-run (copy of `run_s1.py`, only the difficulty variance re-targeted;
    same MASTER_SEED 20260809, same anchor 1.83e-7, same pool, same
    R in {1,2,4,6}, same 100k suites x 50 nets, same chunking) at
    vD in {7.57e-4 control, vD_moment(raw), vD_moment(corr), 0.0814, 0.1220}:
    width shrink R6 vs R1, mean shift, rotation share, P(<1.6e-7), P(<1.0e-7).
Q7. S4 re-run (copy of `run_s4.py`, same MASTER_SEED 202608094, same anchor,
    same copula, same 100k x 50, same rho grid, same arms) at the same five vD:
    the Door-B number = same_mean `P(min<T | rho=0) - P(min<T | rho=1)` at
    T in {1.55, 1.6, 1.7}e-7, plus the realized score correlation at rho=0
    (the shared-difficulty floor that Door-B cannot decorrelate away).
Q8. Floor-correlation ceiling (see G5).

## 3. PREDICTED OUTCOME (on record, before running)

P1. `vD_moment(raw)` = 0.0094 (ddof0) / 0.0129 (ddof1); its bootstrap 95% upper
    bound lies below 0.08.
P2. `vD_moment(corr)` = 0.139 (ddof0) / 0.145 (ddof1) — above 0.08, below the
    p2-implied 0.23–0.36 sensitivity.
P3. At BOTH vD readings some finite tail index `beta` reproduces the observed
    15.5317 range with the observation inside [P5, P95] — i.e. the range does
    NOT identify vD once the shape is free, which is the mechanism claim.
P4. S1 at vD 0.0814/0.1220 keeps all three gates PASS, with R6-vs-R1 width
    shrink near 44%/40% and rotation share near 0.83/0.77 (S1b's analytic
    numbers, here measured by bootstrap). At `vD_moment(raw)` the shrink returns
    to ~58–59% (committed 58.85%).
P5. S4's Door-B gain shrinks monotonically as vD rises, because the shared
    net-difficulty component puts a floor under the pair correlation that no
    rotation-seed choice can remove. Predicted: at vD = 0.1220 the T=1.6e-7 gain
    falls below 5.0 pp but stays above the 2 pp gate, so S4 still SURVIVES; the
    committed "~doubles P(at least one < T)" claim no longer holds at 1.6e-7.
P6. The floor-correlation ceiling is VIOLATED under the raw reading (predicted
    |Corr(floor31, mse_raw)| > sqrt(share_D_raw) ~ 0.18), which means neither
    S1b's point range nor the raw point reading is the final answer and the
    honest deliverable is a BOUND — exactly the candidate's stated revival
    mechanism ("restate ... as BOUNDS rather than point values").

## 4. STEP-0 ARITHMETIC KILL GATE (run first, stop if it fires)

Verbatim from the mining record's `cheapest_falsifier`:

> "Predeclare: if a two-parameter (vD, tail-index) fit to the 80-net panel's
>  second moment AND range jointly puts vD >= 0.08 under both floor treatments,
>  S1b stands and this candidate is dead."

Operationalized:

  **G0 (KILL).** If `vD_moment >= 0.08` under BOTH the raw AND the
  floor-subtracted treatment (ddof=1 point estimates, the more generous of the
  two), then S1b's operative 0.081–0.122 is confirmed by the moment and the
  candidate is DEAD. Report KILL_CONFIRMED and stop; no further arms are run.

## 5. REMAINING GATES (exact numbers)

  **G1 (identification).** `vD_moment(raw, ddof1) < 0.08` AND its bootstrap 95%
  upper bound `< 0.08`. Meaning: the second moment of the same 80-net panel S1b
  validated against is incompatible with S1b's operative range under the raw
  observable. PASS iff both hold.

  **G2 (shape freedom).** There exists a tail index `beta` in the declared grid
  {1.0, 1.25, 1.5, 2, 3, 4, 6, 10, inf} at which the observed 15.5317 lies
  inside the simulated [P5, P95] of the 80-net max/min, AT BOTH `vD_moment(raw)`
  AND `vD_moment(corr)`. PASS iff true at both. (This is the "the range is a
  shape statistic, not a dispersion statistic" claim.)

  **G3 (S1 robustness).** Report the three S1 gates at all five vD. S1's PASS is
  "robust under every reading" iff width shrink >= 25%, |mean shift| < 2% and
  rotation share > 0.5 at every one of the five arms.

  **G4 (S4 Door-B).** Report the same_mean rho0-minus-rho1 gain at all three
  thresholds for all five vD, with batch-SE 95% CIs. S4's verdict stands iff
  gain >= 2.0 pp at ANY threshold in the same_mean or r6 arms, at the corrected
  vD. Separately record whether the committed "~doubles P(at least one < T)"
  statement survives: it does iff `P(min<T|rho=0) / P(min<T|rho=1) >= 1.9`.

  **G5 (second signal, floor-correlation ceiling).** `floor31` is the truth-side
  MC variance of the 600k-sample truth pass (`run_m185_g0.py` lines 185–191:
  `floor31 = mean(var31)/n_samples`); it is a property of the net and the truth
  sampler and does not involve `rot_seed`, hence it is ROTATION-FREE. Under the
  S1 model, `E[mse_raw | net] = S*D`, so for any rotation-free net statistic `Z`:
      `|Corr(Z, mse_raw)| = |S*Cov(Z,D)| / (sd(Z) sd(mse_raw)) <= sqrt(share_D)`.
  Compute Pearson and Spearman `Corr(floor31, mse_raw)` and compare with
  `sqrt(share_D)` implied by each vD reading; do the same with the committed
  A1b weights-only Spearman magnitudes (max 0.5627, multivariate 0.5543), which
  are also rotation-free. Record which readings the ceiling excludes. This gate
  does not by itself pass or kill the candidate; it decides whether the
  deliverable is a point value or a bound.

## 6. VERDICT MAPPING

  * **KILL_CONFIRMED** — G0 fires.
  * **REVIVED_PASS** — G0 does not fire AND G1 PASS AND G2 PASS. Meaning: the
    kill record's own arithmetic, run as predeclared, shows S1b's vD point range
    is not identified by the panel's second moment, and the published
    17–23%/77–83% split must be restated as a bound.
  * **INCONCLUSIVE** — anything else.

## 7. TWO-SIGNAL VERIFICATION (required before any PASS claim)

  V1. Control reproduction: the S1 copy at DIFF_RATIO = 1.1 must reproduce the
      committed `s1_results.json` R=1 SD `1.562588338576902e-08`,
      `P(<1.6e-7) = 0.06434`, chunk0 SHA-256, and the m185 spread validation
      P5/P50/P95, to rel tol 1e-12. The S4 copy at DIFF_RATIO = 1.1 must
      reproduce the committed same_mean gains 2.85 / 6.00 / 16.50 pp and the
      harness SD check.
  V2. Independent recomputation of `vD_moment` by a second, algebraically
      different path: forward Monte-Carlo. Simulate `D*F` at the fitted
      `(vD, beta)` and check the simulated relvar reproduces `relvar_obs` to
      within MC error — i.e. close the loop the identity opened.
  V3. Bitwise repeat: chunk-0 SHA-256 of every S1 arm and of the S4 scoreA /
      min-score streams must match on a fresh spawn of the same seed.
  V4. Cross-simulator check against S1b: my shape simulator at `beta = inf`,
      vD = 0.0814 must reproduce S1b's committed 80-net spread row
      (P5/P50/P95 = 11.64/18.19/25.51, `P(sim>=15.53) = 0.720`) to MC error.

## 8. Firewall

Reads: the four committed JSON artifacts named above plus `s1_results.json`,
`s4_results.json`, `s1b_results.json`, `s17_results.json` (read-only).
Writes: this directory only. Scripts are COPIED here and edited in the copy; the
originals are not modified. No git, no network, no submissions, no truth/scorer/
private/holdout reads, no contact with m245_*/M243/M244/journal-m245*.
Python: the pinned interpreter
`work/whest-v014/Scripts/python.exe`, `PYTHONIOENCODING=utf-8`.
