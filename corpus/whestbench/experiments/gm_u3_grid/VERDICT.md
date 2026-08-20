# VERDICT — gm_u3_grid ("U3 tail-model fidelity", the rotation-tail / dispersion identifiability crack)

**GATE RESULT: REVIVED_PASS.** The mined revival survives its own cheapest
falsifier. My predeclared prediction (KILL, 60/40) was WRONG, in exactly the
way I named in advance as the live risk.

Governing document: `PREDECLARATION.md` in this directory (written before any
code). Harness: `run_gm_u3_grid.py`. Numbers: `results.json`, `run.log`.
Post-hoc attack: `attack_gm_u3_grid.py`, `attack_results.json`.

---

## DEVIATIONS (loud, at the top)

1. **numpy 2.4.6 removed `np.trapz`.** The first execution aborted with
   `AttributeError: module 'numpy' has no attribute 'trapz'` *after* Step 0,
   the control asserts and the whole headline grid (including the Gate-A
   numbers) had already printed. Patched to `getattr(np, "trapezoid", np.trapz)`
   and re-run end to end. The second run reproduced every headline cell
   identically (decisive cell `P=0.3767`, `P5/P50/P95 = 8.593/13.934/26.040`
   in both transcripts). No gate, arm, interval or NREP changed.
2. **Post-hoc adversarial attack added** (`attack_gm_u3_grid.py`, attacks
   A1/A2/A3) after Gate A returned REVIVED_PASS. It was NOT predeclared. It
   can only tighten scrutiny of the passing cell, never loosen a gate, and the
   verdict does not depend on it — it corroborates it. Reported in full below,
   including the part that qualifies the result (A2).
3. **The k=12 GPD MLE is a boundary solution** (`xi = -0.95999...`, the
   optimiser floor is -0.96): the committed 12 exceedances prefer a SHORT,
   bounded tail. Disclosed rather than re-thresholded. The predeclared annex
   thresholds k in {6, 16} were run as written and k=16 gives an interior MLE
   (`xi = +0.0943`) — that instability is reported as a finding, not smoothed.
4. No other deviation. Gates `[0.20, 0.90]`, `vD <= 0.01`, LR `3.841`, NREP
   10,000 / 200,000, the 3x3 grid and the xi grid are exactly as predeclared.

---

## STEP 0 — the arithmetic gate (deterministic, no Monte Carlo)

Predeclared step-0 rule: a cell whose maximum attainable spread bound
`(F_upper_endpoint / F_lower_endpoint) * DIFF_RATIO` is below the observation
has `P(sim >= obs) = 0` EXACTLY.

| cell | bound | status |
|---|---|---|
| vD 7.57e-04 x empirical48 | **12.1805** | DEAD — P = 0 exactly |
| vD 7.57e-04 x gpd_ext (k=12 MLE) | **12.2097** | DEAD — P = 0 exactly |
| vD 7.57e-04 x lognorm_ext | inf | alive |
| vD 0.0814 x empirical48 | 29.9849 | alive |
| vD 0.1220 x empirical48 | 37.6964 | alive |

Observation `OBS = 15.531671197493653`.

Step 0 did not kill (the lognormal cell has unbounded support), so the run
continued as predeclared. But step 0 already produces the sharpest single fact
in this experiment: **the committed model's celebrated "P = 0" against the
15.53x observation is a support artifact, not a likelihood statement.** The
48-atom pool has max/min 11.0732; times DIFF_RATIO 1.1 that is 12.1805 < 15.5317,
so the old model *cannot* produce the observation at any sample size. P = 0 was
guaranteed by the choice to resample a 48-value empirical pool with replacement,
before any dispersion parameter was considered.

## Control reproduction (signal 1) — committed cells reproduced bitwise

- `(vD 7.57e-04, empirical48)` vs `s1_results.json crosschecks.m185_spread_validation`:
  P5 **9.141084926428613**, P50 **11.183938237245313**, P95 **11.937161888372628**,
  P(sim >= obs) **0.0** — asserted equal at rel tol 1e-12. PASS.
- `(vD 0.0814, empirical48)` and `(vD 0.1220, empirical48)` vs
  `s1b_results.json arms.s17_low/s17_high.spread80`: all four fields asserted
  equal at rel tol 1e-12. PASS (11.643/18.188/25.508, P = **0.7196**; and
  13.193/21.216/31.214, P = **0.8621**).

So the grid is on the identical code path and seed as the asserted control.

## The 2-D grid (the mined falsifier, verbatim)

NREP = 10,000; `P` is `P(sim spread >= 15.5317)`; MC SE <= 0.005.

| vD \ F-pool | empirical48 | gpd_ext (POT k=12, MLE xi) | lognorm_ext (MLE) |
|---|---|---|---|
| **7.57e-04** | P = **0.0000** (exact, step-0) | P = **0.0000** (exact, step-0) | P = **0.3767** (SE 0.0048) |
| 0.0814 | P = 0.7196 | P = 0.6855 | P = 0.7151 |
| 0.1220 | P = 0.8621 | P = 0.8563 | P = 0.8335 |

Decisive cell in full: `(vD = 7.568e-04, lognorm_ext)` gives simulated 80-net
spread **P5 = 8.593, P50 = 13.934, P95 = 26.040**, `brackets_observed = True`
(8.593 <= 15.5317 <= 26.040), **P(sim >= 15.5317) = 0.3767**.

### GATE A — verbatim from the mining record

> "If no (vD <= 0.01, heavy-F) cell reaches P(sim >= 15.53) in [0.2, 0.9], the
> attribution is identified ... and the v8 sentence stands."

One of the two decisive cells reaches it: **0.3767 in [0.20, 0.90]**.
**GATE A = REVIVED_PASS.** The attribution is NOT identified.

### GATE B — the tail-index axis (predeclared as axis 3)

95% profile-likelihood CI for the GPD shape from the committed 12 exceedances:
**xi in [-0.9900, 0.1731]** (MLE xi = -0.96000, sigma = 1.73177, nll = 7.14701).
At vD = 7.57e-04, sweeping xi with sigma re-profiled:

| xi | LR vs MLE | in 95% CI | P(sim >= obs) |
|---|---|---|---|
| -0.20 | 2.322 | yes | 0.079 |
| -0.10 | 2.695 | yes | 0.195 |
| **0.00** | **3.093** | **yes** | **0.325** |
| +0.10 | 3.515 | yes | 0.449 |
| +0.20 | 3.956 | no | 0.559 |

`xi* = 0.00` (a plain exponential tail) is the smallest swept xi landing in
[0.20, 0.90], and it sits INSIDE the 95% profile CI (LR 3.093 < 3.841).
**GATE B RESCUES** — it agrees with Gate A instead of qualifying it.

Predeclared annex (POT threshold sensitivity), MLE xi at each threshold:

- k = 6: xi = -0.9600 (boundary, short tail) -> P = 0.000 at vD 7.57e-04
- k = 12: xi = -0.9600 (boundary, short tail) -> P = 0.000 at vD 7.57e-04
- **k = 16: xi = +0.0943 (interior MLE) -> P = 0.285 at vD 7.57e-04**

At the k = 16 threshold the *fitted, unstretched* GPD reaches the gate on its
own. Nothing distinguishes k = 16 from k = 12 as a POT choice on 48 points;
that the answer flips between them is the identifiability problem restated.

## Two-signal verification of the decisive number

The one number the verdict rests on is `P = 0.3767`. Three independent routes:

| route | value |
|---|---|
| headline MC (PCG64, committed seed layout, 10,000 reps) | **0.3767** |
| deterministic quadrature of `P(range <= log obs) = INT 80 f(x)[F(x+r)-F(x)]^79 dx` (no RNG, no sampler, no estimator in common) | **0.372536** |
| Philox generator + inverse-CDF sampler, disjoint seed, 200,000 reps | **0.372315** |

|MC - quadrature| = 0.004164 (predeclared tolerance 0.01: PASS).
|MC - Philox200k| = 0.004385 vs 3 combined SE = 0.014894 (PASS).
Bitwise repeat of every MC cell: SHA-256 identical (`bitwise_repeat_ok = true`
for all six live cells). All three routes put the value far inside [0.20, 0.90];
the pass is not a boundary artifact.

## Adversarial attack on the pass (post-hoc, Deviation 2)

**A1 — is the passing model admissible?** If the lognormal fitted the committed
48 values badly, the pass would be hollow. KS statistic **0.09760**;
parametric-bootstrap (fit-refit, 20,000 replicates) **p = 0.2998**; bootstrap
P95 of the KS statistic 0.1275. The committed pool cannot reject the lognormal
at any conventional level. The passing cell is an admissible model of the same
data. The attack fails to break the pass.

**A2 — which tail does the work?** (the part that qualifies the result). Clipping
the fitted lognormal at the empirical support ends, at vD = 7.57e-04:

| variant | P50 | P(sim >= obs) |
|---|---|---|
| full lognormal | 13.934 | **0.3767** |
| lower tail clipped at empirical min 0.25825 | 11.932 | 0.1624 |
| upper tail clipped at empirical max 2.85963 | 11.977 | 0.1678 |
| both ends clipped | 10.793 | 0.0000 |

Neither single tail reaches the 0.20 gate alone (0.162 / 0.168); the pass needs
unbounded support at BOTH ends, roughly symmetrically. U3's own wording was
about the UPPER tail only ("the empirical rotation pool understates the true
tail"), so the mechanism that revives U3 is broader than the sentence U3 wrote.
Stated plainly because it is the one place the result is weaker than the
headline suggests.

**A3 — closed-form consequence** (identity `SD = S*sqrt((vD+(1+vD)vF/R)/n)`,
validated against the bootstrap in S1b two-signal item 2 to ratio
[0.999, 1.002]; my closed form reproduces the committed old-control bootstrap
SD 1.562588e-08 as 1.564050e-08, ratio 0.99907):

| model | vF | vD | 50-net suite SD | difficulty share at R=1 |
|---|---|---|---|---|
| committed OLD (refuted) model | 0.36420 | 7.57e-04 | 1.5640e-08 | 0.21% |
| **PASSING ALTERNATIVE (lognormal F)** | **0.34862** | **7.57e-04** | **1.5303e-08** | **0.22%** |
| S1b headline s17_low | 0.36420 | 0.0814 | 1.7840e-08 | 17.1% |
| S1b headline s17_high | 0.36420 | 0.1220 | 1.8853e-08 | 23.0% |

The model that passes the bracket at near-zero vD has **less** rotation variance
than the committed pool (0.34862 vs 0.36420) and a suite SD 2% **narrower** than
the old refuted model — while reproducing the old "99.79% rotation-draw /
0.21% difficulty" split. The bracketing test is therefore a statement about the
SHAPE of the 80-draw extremes, not about total variance, and it cannot separate
"more net-difficulty dispersion" from "a rotation pool with smooth unbounded
support at the same variance".

## What this does and does not overturn

Does NOT overturn:
- The headline **vD = 0.081–0.122**. That is derived independently in S1b from
  rotation-free per-net `sigma2_var(ybar)` on 3 nets; nothing here touches it.
  (The mining record predicted exactly this limit.)
- The Phase-1 selection, frozen and untouched. No submission, no scorer, no
  private/holdout data was read.
- The direction of S1b's correction: at vD 0.081/0.122 the observation is
  bracketed under EVERY F-shape tested (P = 0.686–0.862 across all three
  pools) — that row of the grid is shape-robust.

DOES overturn (all writeup-science, Phase-2 planning only):
1. **`PHASE1_WRITEUP_DRAFT_20260808.md` lines 233–235**: "The corrected model
   brackets the independently observed 15.53x 80-net max/min spread
   (P(sim >= obs) = 0.72–0.86), which the original model missed entirely
   (P = 0)" — the second clause is a support artifact (step-0 bound 12.1805)
   and the sentence reads as though the bracket SELECTS the corrected
   dispersion. It does not: an admissible F-shape at the ORIGINAL vD = 7.57e-04
   brackets the same observation with P = 0.3767. The bracket is a valid
   refutation of the *empirical-48-pool-with-DIFF_RATIO-1.1 model as a joint
   object*; it is not evidence for vD.
2. **S1B_DISPERSION_CORRECTED.md §2 "Bracketing verdict: PASS"** and §4's
   "validated by the 15.53x bracket": the word "validated" is doing work the
   test cannot do. S1b's own Limitations section names the twin of this
   ("a heavier-tailed difficulty shape at the same vD would widen the simulated
   spread") and was task-pinned out of testing it; the rotation-shape limb is
   the one measured here and it is the one that breaks the identification.
3. **The live self-contradiction in writeup §3d** (lines 233–235 vs line 257):
   both statements attribute the same observation to different causes. This
   experiment shows the observation is genuinely consistent with EITHER, so
   neither clause may be stated as established. U3's "S1/S4 widths are LOWER
   BOUNDS, non-blocking, accept as conservative" is NOT retroactively correct:
   at the passing alternative the 50-net suite SD is 1.5303e-08, **narrower**
   than the committed 1.5626e-08 — the rotation-tail limb moves the width the
   opposite way from what "conservative" asserts.

## Honest limits of this result

- The 48 pool values are 3 nets x 16 rotations with each block normalised to
  its own mean; they are not strictly iid. That caveat applies equally to the
  committed empirical-48 pool and to every fit here.
- `xi* = 0.00` sits inside a 95% profile CI built from 12 exceedances; that CI
  is wide because the data are few. The correct reading is "the committed data
  cannot rule this tail out", not "this tail is the truth".
- The passing cell needs unbounded support at both ends (A2), which is more
  than U3's upper-tail sentence claimed.
- Every number here is a 10,000-replicate MC statistic (cross-checked to
  ~0.004 by two independent routes), on synthetic committed artifacts only.
  The 15.53x itself is a LOCAL SYNTHETIC 80-net checkpoint (m185 stage 1), as
  the writeup itself corrects at lines 236–238.

## Prediction vs outcome

Predeclared: KILL_CONFIRMED at 60/40, with the named live risk "`lognorm_ext`
has an unbounded LOWER tail as well ... If `lognorm_ext` lands P in [0.20,
0.90], Gate A is a REVIVED_PASS and I will report it as such without retuning."
That is precisely what happened (0.3767), and A2 confirms the named mechanism
(both tails, lower tail worth 0.168 of the 0.377 on its own). Secondary
predictions: the k=12 GPD MLE being a bounded-tail step-0 kill — CORRECT.
Gate B rescuing — CORRECT, though it turned out to be moot because Gate A
passed outright. My prediction that `xi* >= 0.3` was WRONG: `xi* = 0.00`.

## Files

- `PREDECLARATION.md` — governing document, written first
- `run_gm_u3_grid.py` — harness (step 0, control asserts, grid, gates, verification)
- `results.json` — all numbers, machine-readable
- `run.log` — full console transcript of the completed run
- `attack_gm_u3_grid.py`, `attack_results.json` — post-hoc adversarial attack
- `VERDICT.md` — this file

Inputs, all read-only and committed:
`pb1_premise_battery/p2_results.json`, `s1_suite_risk/s1_results.json`,
`s1b_dispersion_corrected/s1b_results.json`, `s17_ibc_floor/s17_results.json`,
`a_series_granular_adversarial/m185_g0_stage1_checkpoint.json`,
`a_series_granular_adversarial/a1b_tail_diagnostics.json`.
