# VERDICT -- gm_s17_reuse (ledger id s17_information_complexity_lower_bound)

**GATE RESULT: STANDS (predeclared gate satisfied) -- with two corrections to
the S17 record that the n=3 measurement could not see.**

The mined revival is a PRECISION revival, and its predeclared gate is met:
the n=80 pooled `champ/(sigma^2/64512)` 95% CI excludes 1.2 from below, so the
floor claim STANDS and U18's dichotomy holds. The revival is therefore KILLED
AS A DECISION-MOVER (Phase-2 effort allocation does not change), which is the
mining record's first outcome branch. The original S17 record is confirmed in
direction and refuted in two of its stated numbers.

## DEVIATIONS (loud, at the top)

1. **Numerator harmonization (predeclared before any compute).** S17's
   numerators were RAW MSEs (16 rotation replicates) against a 3.5M-sample MC
   truth, carrying an unsubtracted truth-MC floor. The m185 panel ships
   `mse_corr` (floor-corrected, single rotation draw r=0). Both numerators
   were run: PRIMARY `mse_corr`, and S17-CONVENTION
   `mse_corr + floor31*600000/3.5e6` (adds back exactly S17's truth floor).
   Both give the same gate.
2. **Single-draw numerator noise (predeclared).** m185 stage 1 is ONE rotation
   per net where S16/S17 averaged 16. The pooled mean stays unbiased but the
   per-net sd is inflated. Consequence: the realized `se` is **0.1602**, not
   the mining record's projected **~0.06**, and the realized CI is
   **[1.6900, 2.3277]**, not the projected **~[1.7, 1.9]**. The record's
   precision arithmetic was optimistic by 2.7x on `se`.
3. **S3 tolerance was predeclared too tight.** I predeclared `rel err < 1e-12`
   for the independent-code-path recomputation of `sigma^2`. A float32 GEMM
   forward with different chunking cannot meet that; observed agreement is
   **1.7e-8**, which is float32-grade. The check passes at its physically
   attainable tolerance; the predeclared number was wrong, not the result.
4. **Staging executed as predeclared.** n=20 ran first, straddled 1.2 AND
   included 1.0, so the run was extended to all 80 exactly as the mining
   record prescribes. No gate was retuned.
5. Nothing else: no estimator change, no submission, no network, no git, no
   held-lane (m245/M243/M244) contact, no truth/scorer/holdout reads. All
   writes confined to this directory.

## STEP 0 -- arithmetic kill gate (run first)

Re-derived S17 section A from the committed `s5_net{101,202,303}_arrays.npz`
plus the committed S16/m181 champion MSEs. All three per-net ratios and the
pooled reproduce **BITWISE** (`rel err = 0.00e+00`, float equality True):

    net 101 sigma2=7.9004722096335002e-03 ratio=1.6308265471219099 (ref identical)
    net 202 sigma2=1.6002145106185965e-02 ratio=2.3673079336291769 (ref identical)
    net 303 sigma2=1.1124831593729415e-02 ratio=1.3739080295883108 (ref identical)
    pooled reproduced 1.7906808367797993 == reference 1.7906808367797993

Step 0 PASSES: the mined instrument is exactly the object in the record and
is reusable. Artifact: `step0_results.json`.

## HEADLINE NUMBERS (n = 80, seeds 1000..1079)

| accounting | pooled | sd | se | 95% t CI | bootstrap CI (20k) | gate |
|---|---|---|---|---|---|---|
| PRIMARY `mse_corr/(sigma^2/64512)` | **2.0088** | 1.4329 | 0.1602 | **[1.6900, 2.3277]** | [1.7080, 2.3335] | **STANDS** |
| S17-CONVENTION | **2.1117** | 1.4421 | 0.1612 | **[1.7908, 2.4326]** | [1.8010, 2.4350] | **STANDS** |
| distinct-direction `/(sigma^2/32256)` | **1.0044** | -- | -- | **[0.8450, 1.1639]** | -- | (includes 1.0) |
| per-output design floor `/(mean_j Var_j/64512)` | 0.3641 | -- | -- | [0.3105, 0.4177] | -- | (diagnostic) |

S17 n=3 reference: pooled 1.7906808367797993, se 0.29770000995332074,
t95 CI [0.5096776939506602, 3.071683979608938].

Gate arithmetic: `ci_lo = 1.6900 > 1.2` -> **STANDS**; `1.0 < 1.6900` -> not
REOPENS; `1.6900 < 2.5` -> not REOPENS_UPWARD.

Stage record: n=20 (seeds 1000..1019) gave pooled **1.4836**, se 0.2475, CI
**[0.9656, 2.0016]** -> `REOPENS` + `STRADDLES_1.2` -> extended to 80 per the
predeclared rule. Artifacts `results_n20.json`, `checkpoint_n20.json`.

Precision delivered: CI width **2.5620 -> 0.6377** (4.02x collapse); se
**0.2977 -> 0.1602** (1.86x).

## TWO-SIGNAL VERIFICATION

- **S1 numerator, independent recomputation** -- `mse_raw` recomputed from the
  checkpoint's stored 256-vectors `pred31`/`truth31` for all 80 nets:
  **max rel err 0.0e+00, exact on every net.**
- **S2 split-sample** (parity of net seed): even n=40 pooled 2.1122 CI
  [1.5864, 2.6380] -> STANDS; odd n=40 pooled 1.9055 CI [1.5225, 2.2886] ->
  STANDS. **Halves agree on the gate.**
- **S3 independent code path** for `sigma^2` (chunked, different summation
  order and blocking) on 5 nets: **max rel err 1.7e-08** (float32 grade).
- **S4 two-way `sigma^2`** (`Var(ybar)` vs `mean((ybar-mean)^2)`): max rel
  diff **0.0e+00** on all 80.
- **Bootstrap** (20k percentile) reproduces the t CI to <0.02 on both ends.
- **NET IDENTITY** -- the load-bearing premise that my reconstructed He net is
  the net m185 measured. Independent 60k-sample iid-Gaussian MC of the
  layer-31 mean vector vs the committed 600k `truth31`:
  `mean_j (mine - truth31)^2` = 1.3843e-06 / 3.1803e-07 / 5.2223e-07 on nets
  1000 / 1040 / 1079, i.e. **8.1e-07 / 3.8e-07 / 2.4e-07 of the field scale**
  and 0.66x / 0.44x / 0.30x of the expected sum of the two MC floors. If the
  weights differed at all this statistic would be O(1) relative. Same nets.
- **Stage-order attack**: first-20 mean 1.4836 vs last-60 mean 2.1839,
  diff 0.7003, se 0.3700, t 1.893, **permutation two-sided p = 0.0586**
  (20k permutations). Ordinary sampling variation, not an ordering artifact.

## THE TWO CORRECTIONS TO THE S17 RECORD

1. **S17's own class rule flips from (i) to (ii) at the point estimate.**
   `run_s17.py` lines 202-204: `pooled < 2.0 -> class i`, `2.0-4.0 -> class ii
   (modest headroom)`. n=3 gave 1.7907 -> class **i** ("GATE (i) OBTAINS --
   the champion sits at the point-evaluation floor"). n=80 gives **2.0088**
   (PRIMARY) and **2.1117** (S17-convention) -> class **ii**. The 95% CI
   straddles 2.0 in both accountings (`[1.6900, 2.3277]`, `[1.7908, 2.4326]`),
   so the i/ii boundary is **NOT resolved even at n=80** -- but the headline
   "GATE (i) OBTAINS" is no longer the point estimate, and should be restated
   as "class i/ii, boundary unresolved, pooled 2.01 [1.69, 2.33]".

2. **"champion/floor = 0.90 on distinct-direction accounting" is an n=3
   artifact and must be retired.** At n=80 the distinct-direction ratio is
   **1.0044, CI [0.8450, 1.1639]** -- the champion sits exactly ON that floor,
   not 10% below it. The mining record's objection ("a floor the champion
   beats by 10% is not a lower bound") is dissolved by the measurement rather
   than by argument.

3. **ednacob bracket, propagated.** The generous end of S17's bracket is
   `variance_per_flop_ratio / pooled = 3.9657744377832187 / pooled`:
   n=3 gave **2.2147x**; n=80 gives **1.9742x** (PRIMARY, CI 1.7037-2.3467)
   and **1.8780x** (S17-convention). The tight end is unchanged at
   **3.9658x** (it never used the pooled ratio). Direction is unchanged --
   ednacob still sits below the point-evaluation floor in every accounting --
   so U18's dichotomy (seed-side extraction vs over-budget/suspect) survives
   intact. But S17's confidence line, "high on the arithmetic (>=2.2x below
   the point floor in every accounting)", is **FALSIFIED**: the generous
   accounting is 1.88-1.97x. Amend the number, keep the conclusion.

## DIAGNOSTIC FINDING (labelled, not gated)

S17's `sigma^2` is `Var_u(neuron-mean of the layer-31 output)`, which is NOT
`mean_j Var_u(y_j)`. On the same design the two differ by a factor of
**5.52** (2.0088 / 0.3641). Against the per-output iid floor
`mean_j Var_j / 64512`, the champion sits at **0.3641, CI [0.3105, 0.4177]**,
i.e. ~2.7x BELOW it -- because the champion carries an analytic
(diagonal-Gaussian) control variate, so a pure per-output iid floor is not
binding on it. My predeclared point prediction for this diagnostic was ~0.1;
observed 0.3641, so the prediction was off by 3.6x while its direction (the
champion sits below the per-output floor) held. This says the S17 floor is a
*neuron-averaged field* floor, and any future restatement of "the
point-evaluation floor" should name which of the two objects it means.

## PREDICTION vs OBSERVATION (self-scored)

| predeclared | observed | hit? |
|---|---|---|
| step 0 rel err < 1e-12 | 0.00e+00 bitwise | yes |
| n=20 PRIMARY point 1.5, band [1.2, 1.9] | 1.4836 | yes |
| n=20 CI half-width <= 0.35 | 0.2590 | yes |
| n=20 S17-conv point 1.75, band [1.4, 2.1] | 1.5797 | yes (band) |
| n=20 gate STANDS, flagged marginal | STRADDLES_1.2 + REOPENS -> extended | no (flagged) |
| per-output diagnostic ~0.1 | 0.3641 | no (direction yes) |
| final gate | STANDS | -- |

No n=80 point prediction was predeclared (only the n=20 stage), so the n=80
pooled 2.0088 landing above the n=20 band is not scored as a hit or a miss.

## FILES

- `PREDECLARATION.md` -- written before any code ran
- `step0_reproduce_s17.py`, `step0_results.json` -- step-0 arithmetic gate
- `run_gm_s17_reuse.py`, `gm_s17_reuse_checkpoint.json` -- the 80-net instrument run
- `checkpoint_n20.json`, `results_n20.json` -- the n=20 stage, preserved
- `analyze_gm_s17_reuse.py`, `results.json` -- pooled stats, gates, S1-S4, bootstrap
- `addendum_checks.py` -- net-identity MC check and downstream propagation
