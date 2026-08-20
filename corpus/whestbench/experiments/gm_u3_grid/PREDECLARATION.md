# PREDECLARATION — gm_u3_grid (graveyard revival "U3 tail-model fidelity")

Written 2026-08-10, BEFORE any harness code was written or run.
Falsifier worker: Opus-5, item `gm_u3_grid`, mining key "U3 tail-model fidelity".

## 0. Provenance of the item (read first, verbatim from the mining record)

Mining record: journal.jsonl line 6, `revival_candidates[1]`,
`ledger_id = "U3 tail-model fidelity (UNCERTAINTY_LADDER_20260810 §B;
S1_VERDICT.md Limitation 1) — the rotation-tail / difficulty-dispersion
identifiability crack"`.

`cheapest_falsifier` (verbatim):

> Response-free, offline, minutes, on committed JSON only: re-run the S1b §2
> bracketing simulation over the 2-D grid (vD in {7.57e-4, 0.081, 0.122} x
> F-pool in {empirical-48, GPD-extended, lognormal-extended}), same seeds and
> same code path as the asserted control. If no (vD <= 0.01, heavy-F) cell
> reaches P(sim >= 15.53) in [0.2, 0.9], the attribution is identified, U3's
> 'conservative' disposition is retroactively correct, and the v8 sentence
> stands — fix only the contradicting clause on line 254.

`revival_mechanism` names the grid axes as `(vD, tail index)`, so the GPD shape
parameter xi is a predeclared grid axis, not scope creep.

## 1. Mechanism under test

The observed 80-net max/min spread 15.531671197493653 (m185 stage-1 `mse_raw`,
duplicated in `a1b_tail_diagnostics.json`) is used TWICE in the corpus for two
competing purposes:

- U3 / `S1_VERDICT.md` Limitation 1 and `PHASE1_WRITEUP_DRAFT_20260808.md`
  line 257: the 48-value empirical rotation pool "understates the true tail",
  so S1/S4 widths are lower bounds ("accept as conservative").
- S1b §2 and `PHASE1_WRITEUP_DRAFT_20260808.md` lines 233-235: the same 15.53x
  is the VALIDATOR that selects vD = 0.081-0.122 and rejects vD = 0.23-0.36,
  with the old vD = 7.57e-4 assigned P(sim >= obs) = 0.000.

Both explanations consume the same observation. If a heavier F-pool at
essentially zero net-difficulty dispersion also reproduces 15.53x, the
observation cannot identify vD, and the writeup's strongest sentence
("the corrected model brackets ... which the original model missed entirely")
is a validation that passes for the wrong reason.

## 2. Quantity computed

Exactly the S1b §2 statistic, `run_s1b.py::run_spread80`, unchanged in
structure: NREP = 10,000 replicates of 80 iid draws of `D * F`; report
P5/P50/P95 of `max/min`, and `P(sim >= 15.531671197493653)`.

- `D` = log-uniform on max/min = DIFF_RATIO, normalized to mean 1
  (`draw_D`, unchanged), with DIFF_RATIO inverted from target vD by the same
  `vD_of_ratio` / `ratio_of_vD` pair copied verbatim from `run_s1b.py`.
- `F` = one of three pools (below).
- Seed: identical `seed_layout()` derivation from MASTER_SEED = 20260809, and
  the same `val_seed` child, so the (vD = 7.57e-4, empirical-48) cell must be
  BITWISE the committed control.

### Grid (predeclared, frozen)

Axis 1 — vD in {7.57e-4 (DIFF_RATIO 1.1, committed control), 0.0814 (s17
ddof=0), 0.1220 (s17 ddof=1)}, derived in-harness from the committed JSON by
the identical arithmetic as `run_s1b.py`.

Axis 2 — F-pool:
- `empirical48` : the committed 48-value mean-normalized P2 pool (unchanged).
- `gpd_ext` : semi-parametric peaks-over-threshold. Body = empirical values at
  or below the threshold u = the (48-k)-th order statistic; tail = u + GPD(xi,
  sigma) with (xi, sigma) by MLE on the k exceedances. Primary k = 12 (top
  25%, standard POT choice). Mixture rescaled to mean 1 (scale is irrelevant
  to a max/min ratio; recorded for the vF side-report).
- `lognorm_ext` : fully parametric lognormal, MLE (mu, sigma) on the log of all
  48 normalized pool values, rescaled to mean 1. Unbounded support both tails —
  deliberately the MOST generous heavy-F variant available from the data.

Axis 3 (the mined "tail index" axis) — for `gpd_ext`, xi swept over
{-0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0} with
sigma re-profiled at each xi (profile MLE), at every vD in axis 1.

Robustness annex (predeclared, same run): POT threshold k in {6, 16} for
`gpd_ext` at the MLE xi.

## 3. STEP-0 ARITHMETIC GATE (run first, stop if it kills)

Deterministic, no Monte Carlo. For each heavy-F variant with a finite upper
endpoint (GPD with fitted xi < 0 has endpoint u + sigma/(-xi)), the model's
exact maximum attainable 80-draw spread is

    bound = (F_upper_endpoint / F_lower_endpoint) * DIFF_RATIO

and if `bound < 15.531671197493653` then P(sim >= 15.53) = 0 EXACTLY for that
cell, with no sampling error.

STEP-0 KILL: if EVERY heavy-F variant at every vD <= 0.01 has
`bound < 15.5316...`, the gate kills at step 0 and no MC is needed.
(`lognorm_ext` has unbounded support, so step 0 cannot kill it; it is expected
that step 0 is partial.)

## 4. GATES (frozen numbers)

**GATE A (primary, verbatim from the mined falsifier).**
Decisive cells: vD <= 0.01 (i.e. vD = 7.57e-4) x heavy-F (`gpd_ext` at MLE xi,
`lognorm_ext`).
- KILL_CONFIRMED if NEITHER decisive cell has
  `P(sim >= 15.5316...)` inside the closed interval [0.20, 0.90].
- REVIVED_PASS if EITHER decisive cell has `P(sim >= 15.5316...)` inside
  [0.20, 0.90].
MC standard error at NREP = 10,000 is <= 0.005, so a boundary case
(P within 2 SE = 0.01 of 0.20 or 0.90) is resolved by the 200,000-replicate
confirmation run of §5 rather than by the 10,000-replicate headline run.

**GATE B (the mined "tail index" axis; interpretive, cannot rescue a Gate-A
kill by itself, and is fixed here in advance).**
Find the set of xi at vD = 7.57e-4, k = 12, for which
`P(sim >= 15.5316...)` in [0.20, 0.90]; call its lower edge xi*.
- Gate B FAILS TO RESCUE (kill stands, strengthened) if xi* lies OUTSIDE the
  95% profile-likelihood CI of xi from the committed 12 exceedances
  (LR test, 2*Delta loglik <= 3.841).
- Gate B RESCUES (the 15.53x does not identify vD) if xi* lies INSIDE that CI.
A Gate-A KILL with a Gate-B RESCUE is reported as INCONCLUSIVE, never as a
pass; a Gate-A PASS is a pass regardless of Gate B.

## 5. Two-signal verification (required before any verdict is written)

1. **Control reproduction (committed).** Cell (vD = 7.57e-4, empirical48) must
   reproduce `s1_results.json crosschecks.m185_spread_validation`
   (`model_sim_spread_p5/p50/p95`, `p_sim_ge_observed`) to rel tol 1e-12, and
   cells (0.0814 / 0.1220, empirical48) must reproduce the corresponding
   `s1b_results.json arms.s17_low/s17_high.spread80` fields to rel tol 1e-12.
   Asserted in-harness; a failure aborts the run.
2. **Independent recomputation, non-Monte-Carlo.** For every decisive cell,
   `P(spread >= t)` is recomputed by numerical quadrature of the order-statistic
   identity `P(max <= t*min) = INT 80 h(x) [H(t x) - H(x)]^79 dx`, where `H` is
   the CDF of `D*F` built by quantile-quadrature over F composed with the exact
   log-uniform CDF of D. This shares no code, no RNG and no estimator with the
   MC. Agreement required within 0.01 absolute.
3. **Independent-generator MC repeat.** Every decisive cell re-run at
   NREP = 200,000 with `Philox` (not `PCG64`) and a disjoint seed, using
   inverse-CDF sampling instead of the mixture-branch sampler. Agreement with
   the headline MC required within 3 combined SE.
4. **Bitwise repeat** of the headline MC for every cell (same code path, fresh
   seed derivation) — SHA-256 of the spread vector must match.

## 6. PREDICTION ON RECORD (before the run)

I predict **KILL_CONFIRMED on Gate A**, at roughly 60/40 confidence — i.e. I
predict the mining record's own honest expectation is upheld and U3's
"accept as conservative" disposition turns out to be retroactively correct
for the identification question.

Reasoning stated in advance, with the input statistics I computed from the
committed pool BEFORE writing the harness (these are inputs, not outcomes):
the 48-value pool has log-mean -0.15360, log-SD (ddof=1) 0.55269, max/min
11.0732. A pure-lognormal 80-draw typical spread is
`exp(sd_log * (z_{1-1/81} - z_{1/81})) = exp(0.55269 * 4.49240) = 11.98`,
only 7% above the empirical pool's own max/min and 30% short of 15.53. The
committed empirical-48 control puts the 80-draw spread at P50 = 11.18,
P95 = 11.94, so a heavy-F variant must inflate the P50 by ~39% to put 15.53 at
its median. A tail fitted to 48 values whose largest member is 2.86 is unlikely
to buy that much at fixed near-zero vD.

The specific live risk to that prediction, named in advance: `lognorm_ext` has
an unbounded LOWER tail as well, and the max/min spread is far more sensitive
to the min than the proxy above suggests once the 80-draw minimum can fall
below the empirical floor 0.2582. If `lognorm_ext` lands P in [0.20, 0.90],
Gate A is a REVIVED_PASS and I will report it as such without retuning.

Secondary predictions on record:
- `gpd_ext` at MLE xi with k = 12: I predict a fitted xi < 0 (bounded upper
  endpoint) and a step-0 arithmetic kill of that cell.
- Gate B: I predict xi* (the xi needed to enter [0.20, 0.90]) is >= 0.3 and
  that the 95% profile CI from 12 exceedances is wide enough to contain it,
  i.e. I predict Gate B RESCUES and the overall verdict is therefore likely to
  be reported as INCONCLUSIVE-with-a-Gate-A-kill rather than a clean
  KILL_CONFIRMED. This is predeclared so that it cannot be claimed after the
  fact.

## 7. Kill honesty / no-retune clause

The three gate numbers ([0.20, 0.90]; vD <= 0.01; 3.841 LR) are frozen by this
document. No arm, threshold, pool variant, NREP or interval is changed after
seeing a result. Anything that has to change is recorded as a DEVIATION at the
top of VERDICT.md.

## 8. Firewall compliance

Reads: committed JSON under `corpus/whestbench/experiments/` only
(`pb1_premise_battery/p2_results.json`, `s1_suite_risk/s1_results.json`,
`s1b_dispersion_corrected/s1b_results.json`,
`s17_ibc_floor/s17_results.json`,
`a_series_granular_adversarial/m185_g0_stage1_checkpoint.json`,
`a_series_granular_adversarial/a1b_tail_diagnostics.json`).
Writes: this directory only. No git, no network, no submission, no
truth/scorer/private/holdout read, no contact with m245_*/M243/M244 lane.
The 80-net spread 15.53x is a LOCAL SYNTHETIC checkpoint (m185 stage 1), as
corrected in the writeup itself at line 236-238.
