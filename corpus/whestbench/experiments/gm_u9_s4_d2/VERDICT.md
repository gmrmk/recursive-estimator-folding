# VERDICT — gm_u9_s4_d2

Revival item **gm_u9_s4_d2** ("U9 designation refresh + S4 portfolio pass D2
under S1b corrected dispersion"). Predeclaration: `PREDECLARATION.md` in this
directory, written before any harness code. Phase-2 calibration / writeup
science only; the Phase-1 selection is frozen and untouched by this run.

## GATE RESULT: REVIVED_PASS

The Door B union factor does **not** stay at or above 1.95 under corrected
dispersion. S4's certified pass D2 headline — "decorrelated 2nd entry ~doubles
tail (2.00x at 1.55e-7)" — was produced by the refuted near-degenerate
difficulty model and does not survive the S1b correction as a numeral.

## Deviations (loud, as required)

1. **`scipy` absent from the pinned interpreter.** `run_s4.py` imports
   `scipy.special.ndtr`; the pinned `whest-v014` python (3.14.4, numpy 2.4.6)
   has no scipy. A Cephes-shaped `ndtr` on libm `erf`/`erfc` was substituted
   (declared in PREDECLARATION section 0.1). **Proven immaterial:** the
   old_control arm reproduces all 31 committed S4 cells with `abs_diff = 0.0`,
   including `scoreA_sd = 1.556004718551518e-08` and
   `score_corr_AB = 0.002388759363511759` at full double precision.
2. **Harness gate-logic defect, found and corrected before the verdict.** The
   first implementation required BOTH arms' CIs to be clean of 1.95
   (conjunctive `all(...)`), which is not the predeclared rule — PREDECLARATION
   section 5 conditions INCONCLUSIVE on "the **deciding arm's** 95% CI". Under
   the disjunctive REVIVED_PASS criterion the deciding arm is the smallest-U
   arm. Corrected to match the predeclaration; **no number changed** (run 1 and
   run 2 are value-identical, see cross-check 5). Run 1's raw output is kept as
   `gm_u9_s4_d2_results_run1.json`.
3. **Union-bound formula corrected.** PREDECLARATION Eq. 2 stated the
   equal-marginal bound `U <= 2 - pA`, which is a population statement. In a
   finite sample `pA` and `pB` differ by MC noise (e.g. 0.02849 vs 0.02947 in
   the control), so the honest finite-sample bound is the two-marginal form
   `U <= 1 + (pB/pA)(1 - pA)` (from `P(both) >= pA*pB`, Harris/FKG: both tail
   events are decreasing in the shared difficulty vector D). Under the corrected
   form the bound is respected in every arm at every threshold; under the
   equal-marginal form the control appeared to violate it by 0.030, which was
   MC noise in `pB - pA`, not a modelling error.
4. **Precision extension** (predeclared, section 0.2): a 1,000,000-suite
   independent-path recomputation on a different master seed. No new arms, no
   new thresholds, no new rho values.

## Step 0a — arithmetic pre-check (run before the simulation, on record)

Using S1b's committed 50-net single-entry probabilities and the Jensen bound:

| arm | vD | pA(1.55e-7) committed S1b | bound 2 - pA |
|---|---|---|---|
| old_control | 7.5689e-4 | 0.02939 | 1.97061 |
| s17_low | 0.0813595 | 0.04992 | 1.95008 |
| s17_high | 0.1220393 | 0.06053 | **1.93947** |

Recorded before running: the bound alone already forbids U >= 1.95 at
vD = 0.1220. It did not kill the run (it is a bound, on a different sampling
path), but it fixed the predicted direction in advance.

## Step 0 — blocking control gate: PASS

31/31 committed S4 cells reproduced with `abs_diff = 0.0`. The four cells named
in the mining record's `cheapest_falsifier`:

| cell | committed | this run | abs diff |
|---|---|---|---|
| P(min<1.55e-7) same_mean rho=0 (Door B) | 0.057010000000000005 | 0.057010000000000005 | 0.0 |
| P(min<1.60e-7) same_mean rho=0 (Door B) | 0.12372999999999998 | 0.12372999999999998 | 0.0 |
| P(min<1.55e-7) sens_fold3cap rho=0 (Door A) | 0.87683 | 0.87683 | 0.0 |
| P(min<1.60e-7) sens_fold3cap rho=0 (Door A) | 0.9397199999999998 | 0.9397199999999998 | 0.0 |

plus baseline pA = 0.028489999999999998 / 0.06373000000000001 / 0.2063,
`scoreA_mean = 1.82926005895453e-07`, `scoreA_sd = 1.556004718551518e-08`,
`gain same_mean@1.55e-7 = 0.02852`, all at `abs_diff = 0.0`.

## Decisive numbers — Door B union factor U(T) = P(min(A,B)<T | rho_pair=0) / P(A<T)

`U_pooled` is the ratio of pooled means (the estimator that reproduces the
committed 2.00x headline); the CI is the chunk-paired mean-of-ratios over 10
chunks of 10k, as predeclared.

| arm | vD | DIFF_RATIO | pA(1.55e-7) | P(min<1.55e-7) | **U_pooled** | U chunk-mean [95% CI] |
|---|---|---|---|---|---|---|
| old_control (committed) | 7.568879e-4 | 1.1 | 0.02849 | 0.05701 | **2.00105** | 2.0085 [1.9458, 2.0712] |
| vd_s17_low | 0.08135950765383865 | 2.7078820324077753 | 0.04844 | 0.09322 | **1.92444** | 1.9271 [1.8803, 1.9738] |
| vd_s17_high | 0.12203926148075797 | 3.40428993278139 | 0.05922 | 0.11133 | **1.87994** | 1.8821 [1.8457, 1.9185] |

All three thresholds (`U_pooled`):

| arm | U(1.55e-7) | U(1.60e-7) | U(1.70e-7) |
|---|---|---|---|
| old_control (committed) | 2.00105 | 1.94147 | 1.79981 |
| vd_s17_low (vD=0.0814) | **1.92444** | 1.85097 | 1.69100 |
| vd_s17_high (vD=0.1220) | **1.87994** | 1.80988 | 1.65253 |

Induced two-entry score correlation at rho_pair = 0 (the shared-suite
difficulty draw), simulated vs the closed form vD/(vD+(1+vD)vF):

| arm | simulated (se) | analytic Eq. 1 | 1e6-suite path (se) |
|---|---|---|---|
| old_control | 0.002389 (0.002341) | 0.002072 | 0.002017 (0.000910) |
| vd_s17_low | 0.173564 (0.002608) | 0.171215 | 0.171167 (0.000984) |
| vd_s17_high | 0.232645 (0.002728) | 0.229965 | 0.230003 (0.000977) |

i.e. **0.24% -> 17.1% / 23.0%**, a 83x / 111x rise in the correlation between
two entries designated on the same private suite.

## Gate arithmetic

Predeclared rule (verbatim from the mining record): *"If the factor stays
>= 1.95x at both vD values, the revival is dead and S4's D2 pass stands as
written."*

* U(1.55e-7) = 1.9244 at vD = 0.0814 and 1.8799 at vD = 0.1220 — **below 1.95
  at both**, so `both_arms_ge_1.95_pointwise = false`. KILL_CONFIRMED is not
  reachable.
* Deciding arm (smallest U): `vd_s17_high`, chunk-paired 95% CI
  **[1.8457, 1.9185]**, wholly below 1.95 -> not INCONCLUSIVE.
* **Verdict: REVIVED_PASS.**

Robustness of the call: the 1e6-suite independent path gives 95% CIs
**[1.8977, 1.9222]** (vD=0.0814) and **[1.8621, 1.8837]** (vD=0.1220) — clean of
1.95 at *both* arms, so the verdict also survives the stricter conjunctive
reading of the CI rule that the first (defective) implementation used.

## Why U falls — decomposition at T = 1.55e-7

`U = 1 + (pB - P(both))/pA`. Setting `P(both) = pA*pB` isolates the
tail-heaviness effect from the correlation effect:

| arm | U if entries were independent | U observed | correlation contribution |
|---|---|---|---|
| old_control | 2.00493 | 2.00105 | -0.004 |
| vd_s17_low | 1.97887 | 1.92444 | **-0.054** |
| vd_s17_high | 1.95508 | 1.87994 | **-0.075** |

So of the total fall 2.00105 -> 1.87994 (-0.121) at vD = 0.1220, the shared
net-difficulty correlation supplies -0.075 and the heavier single-entry tail
(pA 0.02849 -> 0.05922, which lowers the 2-pA ceiling) supplies -0.046. The
correlation is the larger of the two, which is the mechanism the revival
predicted.

## Secondary result (reported, not a gate): S4's own verdict does NOT move

S4's predeclared gate is the diversification *gain*
`P(min<T | rho=0) - P(min<T | rho=1) >= 2 pp` in the same_mean or r6 arm. At the
corrected vD the gain **grows**:

| arm | gain same_mean @1.55e-7 | @1.60e-7 | @1.70e-7 | S4 gate |
|---|---|---|---|---|
| old_control | 2.852 pp | 6.000 pp | 16.500 pp | SURVIVES |
| vd_s17_low | 4.478 pp | 7.857 pp | 16.631 pp | SURVIVES |
| vd_s17_high | 5.211 pp | 8.571 pp | 16.573 pp | SURVIVES |

**S4's SURVIVES verdict is unchanged.** What dies is the certified magnitude
"2.00x doubling", not the portfolio conclusion. The r6 arm changes side at the
loosest threshold: its 1.7e-7 gain goes 1.526 pp (fails 2 pp, committed) ->
4.725 pp (vD=0.0814) -> 5.319 pp (vD=0.1220), so under corrected dispersion the
r6 arm passes S4's gate on its own at 1.7e-7, where the committed model said it
did not. It still fails at 1.55e-7 and 1.60e-7 in every arm.

## Secondary result: U9's Door A / Door B table under corrected dispersion

| cell | committed (U9) | vD=0.0814 | vD=0.1220 |
|---|---|---|---|
| Door B P(win) @1.55e-7 | 0.05701 | 0.09322 | 0.11133 |
| Door B P(win) @1.60e-7 | 0.12373 | 0.17090 | 0.19154 |
| Door A P(win) @1.55e-7 | 0.87683 | 0.84871 | 0.83655 |
| Door A P(win) @1.60e-7 | 0.93972 | 0.91507 | 0.90362 |
| Door A / Door B ratio @1.55e-7 | 15.38x | 9.10x | **7.51x** |
| Door A / Door B ratio @1.60e-7 | 7.59x | 5.35x | **4.72x** |

The Door A cells move *down* and the Door B cells move *up*, exactly as the
mining record predicted (Door A's 1.41e-7 mean sits below the threshold, so
extra dispersion costs it; Door B's 1.83e-7 mean sits above, so extra dispersion
helps it). The 15x Door A / Door B gap is not stable: it halves.

## Cross-checks (two-signal rule)

1. **STEP 0 exact reproduction** — 31/31 committed S4 cells at `abs_diff = 0.0`
   through a substituted `ndtr`. This is simultaneously the control gate and the
   proof that deviation 1 is immaterial.
2. **Signal 2, independent path** — S1-style direct integer indexing of the
   rotation pool (no Gaussian copula, no `ndtr`), master seed 20260810
   (disjoint from 202608094), 1,000,000 suites. U(1.55e-7) = 1.9100 (se 0.0062)
   and 1.8729 (se 0.0055) vs the copula path's 1.9271 (se 0.0239) and 1.8821
   (se 0.0186). `signal1_vs_signal2_agree_low = true`,
   `signal1_vs_signal2_agree_high = true` (both differences inside
   1.96 * hypot(se1, se2)). The two paths also agree on the correlation
   (0.171167 vs 0.173564; 0.230003 vs 0.232645).
3. **Analytic Eq. 1** — simulated rho=0 score correlation matches
   vD/(vD+(1+vD)vF) within 1 MC standard error in every arm, and the 1e6-suite
   path matches it to 5e-5 / 4e-5. Bootstrap SD vs analytic
   `S*sqrt((vD+(1+vD)vF)/50)`: ratios 0.99486 / 0.99523 / 0.99555.
4. **Union bound** — `U_pooled <= 1 + (pB/pA)(1-pA)` holds in all 3 arms x 3
   thresholds x 2 doors (`respects_union_bound = true` everywhere).
5. **Bitwise / determinism** — chunk-0 re-spawn repeat `true` in every arm; the
   rho=1.0 same_mean entry is bitwise identical to A in every chunk of every
   arm; and the entire corrected re-run reproduced run 1 value-for-value
   (`run1 vs run2 exact-value differences: NONE`), covering U, pA, pmin, the
   1e6-suite path and the chunk-0 SHA-256 of scoreA
   (`2ace948e...`, `bc418c85...`, `7f31150a...`).
6. **Anchor preserved** — the dispersion change is mean-preserving:
   scoreA_mean 1.829260e-7 / 1.829018e-7 / 1.828957e-7; only the SD moves
   (1.556005e-8 / 1.775513e-8 / 1.876931e-8).

## Honest limits

* The fall is real but modest. "Roughly doubles" survives as prose (U is still
  1.88-1.92); the certified numeral **2.00x** and the implicit near-independence
  of two same-suite entries do not. Anyone quoting D2 must quote ~1.9x with the
  17-23% shared-difficulty correlation stated, and must not treat the two
  designations as independent draws.
* vD itself rests on n = 3 nets (S1b's own `n3_caveat`: a chi2(2) CI on the
  ddof=1 variance spans ~[0.27x, 39.5x]). The two arms used here are the two
  S1b arms that bracket the observed 80-net 15.53x spread; the p2-derived arms
  (vD = 0.234 / 0.361) do not bracket and were not run, per the mined falsifier.
  At those larger vD the union factor would fall further, so 1.92 / 1.88 is the
  conservative end of the corrected range.
* U is a *threshold* statistic. The prize criterion is a ranking, in which the
  shared difficulty factor cancels multiplicatively; this run measures only the
  absolute-threshold quantity that S4/U9 actually computed. Separating the two
  statistics is the follow-on writeup task the mining record names, and it is
  not measured here.
* rho_pair between two *real* candidate families remains unmeasured (S4's own
  first limitation). This run only re-prices the rho_pair = 0 idealisation.

## Files

* `PREDECLARATION.md` — predeclared mechanism, gates and predicted numbers
* `run_gm_u9_s4_d2.py` — harness (copy of `s4_portfolio/run_s4.py`; only the
  dispersion parameter, the `ndtr` import and the output path differ)
* `gm_u9_s4_d2_results.json` — full grid, union factors, CIs, cross-checks
* `gm_u9_s4_d2_results_run1.json` — pre-correction run (deviations 2 and 3),
  kept for the value-identity comparison
* `VERDICT.md` — this file

Frozen sources read only: `s4_portfolio/{run_s4.py,s4_results.json}`,
`s1b_dispersion_corrected/{run_s1b.py,s1b_results.json}`,
`s17_ibc_floor/s17_results.json`, `pb1_premise_battery/p2_results.json`,
`u9_designation_refresh/`. Nothing outside this directory was written.
