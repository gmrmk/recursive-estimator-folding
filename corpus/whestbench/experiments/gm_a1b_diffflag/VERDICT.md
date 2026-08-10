# VERDICT - gm_a1b_diffflag

**GATE RESULT: REVIVED_PASS** (framing revival only; ZERO score gain, and the
realizable-gain bound is NEGATIVE at every vD tested).

Predeclared gates are in `PREDECLARATION.md`, written before any code.
All numbers below are verbatim from `results.json` / `attack_bestof7.json`.

## DEVIATIONS (loud, at the top)

1. **Reps raised from the mining record's 40k to 200k per arm** (2 disjoint
   streams x 100k) to get a split-sample second signal. No gate was changed.
   Cost: 93 s wall. Predeclared in section 7 of PREDECLARATION.md.
2. **The realizable-gain bound is reported on BOTH MSE columns.** The mid-mseries
   mining record quoted relaxed/default geomeans 0.9779 (worst) / 1.0275 (median),
   CI [0.9355, 1.0223]. Independent recomputation reproduces those EXACTLY, but
   only on the `mse_corr` column; on the score-relevant `mse_raw` column the
   coefficients are 0.9880 / 1.0310 (CI [0.9500, 1.0275] / [0.9830, 1.0813]).
   The mining record did not state which column it used. The verdict is invariant.
3. Nothing else. No arm was added, no gate retuned, the second leg of the
   mid-mseries falsifier (R=6 re-measurement, 24 nets) was NOT run - it is a
   different, more expensive falsifier and was not the item assigned.

## Step 0 (arithmetic gate, run first)

vF = 0.3641995628656461 (recomputed from p2_results.json, asserted equal to
s1b_results.json to 1e-15).

| arm | vD | rho_ceiling_lin | rho_ceiling_log |
|---|---|---|---|
| old_control | 7.568879454111777e-4 | 0.0455 | 0.0502 |
| s17_low     | 0.08135950765383865  | 0.4273 | 0.4654 |
| s17_high    | 0.12203926148075797  | 0.5010 | 0.5430 |

Step-0 kill threshold was 0.75 under BOTH formulas at BOTH corrected arms:
**not met (False)**. Proceeded to the Monte Carlo. (The `rho_log` column
reproduces the nseries mining record's quoted 0.465 / 0.543 to 3 decimals.)

## Provenance cross-check

`a1b_tail_diagnostics.json` reproduced EXACTLY from the frozen stage-1
checkpoint: all 7 Spearmans to 1e-12, spread 15.531671197493653, best flag
`borderline_frac` rho -0.5627285513361463, precision 0.50, recall 0.50,
20 flagged / 20 tail of 80.

## Main result - perfect net-difficulty oracle, a1b's exact test, n=80

200,000 replicates per arm. Precision == recall in every single replicate
(both quartile sets have exactly 20 members), so one number covers both.

| arm | vD | oracle Spearman (SE) | oracle precision = recall (SE) | p5 / p95 | population-limit precision (n->inf) | measured chance (null oracle) |
|---|---|---|---|---|---|---|
| old_control | 7.5689e-4 | **0.075622** (0.000250) | **0.281804** (0.000197) | 0.150 / 0.450 | 0.2748 | 0.2492 |
| s17_low     | 0.081360  | **0.462025** (0.000205) | **0.500359** (0.000205) | 0.350 / 0.650 | 0.5149 | 0.2491 |
| s17_high    | 0.122039  | **0.539414** (0.000185) | **0.536547** (0.000200) | 0.400 / 0.700 | 0.5507 | 0.2492 |

A1b measured **0.50 / 0.50** with `borderline_frac`.

Gate arithmetic: KILL required oracle precision >= 0.65 at BOTH corrected arms.
Observed 0.5004 and 0.5365 - both below the 0.60 revive threshold. A1b's 0.50
lies inside the central 90% of the oracle's own per-replicate distribution at
both corrected arms. **REVIVED_PASS.**

Under the OLD committed dispersion model the perfect oracle scores 0.2818
precision and rho 0.0756 - i.e. a1b's own measured 0.50 and 0.5627 were 1.8x
and 7.4x ABOVE what any predictor could achieve under the model in force when
the kill was written. That is an internal contradiction in the committed record,
independent of which corrected vD one adopts.

## Verification signals (all collected after the final harness edit)

1. **Split-sample** (2 disjoint 100k streams): |diff| 0.000653 / 0.000242 /
   0.000108 against 3x pooled SE of 0.001180 / 0.001230 / 0.001202 -
   agree_within_3se = True on all three arms.
2. **Independent recomputation** (population-limit path: exact enumeration over
   the 48-point F pool + deterministic quadrature over D, no RNG): precision
   0.2748 / 0.5149 / 0.5507 vs MC 0.2818 / 0.5004 / 0.5365; Spearman
   0.0765 / 0.4670 / 0.5451 vs MC 0.0756 / 0.4620 / 0.5394. The residual gap is
   the expected finite-n (n=80) vs n->inf offset; both paths agree that the
   corrected-arm precision sits near 0.50-0.55 and far below 0.65.
3. **Bitwise repeat** of the s17_high stream-B precision array: sha256 identical
   (`matches_original: true`).
4. **Null control**: an oracle independent of D gives precision 0.2492 / 0.2491 /
   0.2492 - the true "coin flip" value against a 25% top-quartile base rate.
   A1b's adjudication called 0.50 a "coin flip"; the measured coin flip is 0.249.
5. **Monotonicity control**: vD = 50 gives precision 0.9306 (-> 1 as predicted).
6. **Protocol equivalence**: the rank-based top-20 selection was verified
   identical to a1b's `x >= np.quantile(x, 0.75)` form on 200 random replicates.

## Self-attack (strongest counter-hypothesis) - DOES NOT LAND

A1b chose the best of 7 diagnostics by |rho|, so its 0.50 could be multiplicity
noise rather than ceiling saturation. Tested with 7 INDEPENDENT zero-signal
diagnostics (independence is conservative - it maximises the multiplicity bonus),
200,000 replicates, n=80:

- best-of-7 precision mean **0.3337** (SE 0.000176), p50 0.35, p95 0.45
- P(best-of-7 precision >= 0.50) = **0.0356**
- best-of-7 |rho| mean 0.1935, p95 0.2993, P(|rho| >= 0.5627) = **0.0** in 200k reps

A1b's 0.5627 is unreachable by selection noise and its 0.50 is reached 3.6% of
the time. The diagnostic carries real signal; the attack does not restore the
"coin flip" reading.

## Realizable-gain bound per vD

Policy bounded: "relax pruning on the top quartile flagged by a PERFECT
difficulty oracle", zero routing cost, zero oracle error. Coefficients
recomputed from `m185_g0_stage2_checkpoint.json`, score = MSE x billed_flops:

| column | g_worst (relaxed/default) | g_median | break-even precision |
|---|---|---|---|
| mse_raw  | 0.9880 [0.9500, 1.0275] | 1.0310 [0.9830, 1.0813] | **0.7211** |
| mse_corr | 0.9779 [0.9355, 1.0223] | 1.0275 [0.9707, 1.0876] | **0.5549** |

    gain(vD) = 0.25 * [ prec(vD)*(1 - g_worst) + (1 - prec(vD))*(1 - g_median) ]

| vD | oracle precision | suite gain, mse_raw | suite gain, mse_corr |
|---|---|---|---|
| 7.5689e-4 | 0.2818 | **-0.4716%** | **-0.3385%** |
| 0.081360  | 0.5004 | **-0.2369%** | **-0.0676%** |
| 0.122039  | 0.5365 | **-0.1981%** | **-0.0227%** |

Even at precision 1.0 the bound is only +0.2995% (mse_raw) / +0.5525% (mse_corr)
of suite score, and every group effect's 95% CI contains 1. **The realizable gain
of a perfect difficulty oracle is negative at every vD tested**: the perfect
oracle's precision (0.28-0.54) is below the break-even precision (0.55-0.72)
under both score columns, because mis-flagged median nets lose more than
correctly-flagged tail nets gain.

## What this changes, plainly

- **The a1b/M185 kill of the TARGETED P1 pruning guard STANDS, and is now
  stronger**: it fails on the gain arithmetic (negative expected gain even with a
  perfect oracle) rather than on the absence of a flag.
- **The stated REASON in the committed record is wrong.** "Best single-flag
  top-quartile precision/recall = 0.50/0.50 (coin flip)" is false twice over:
  chance is 0.249 (measured), and 0.50 is exactly what a perfect net-difficulty
  oracle scores under the corrected dispersion model (0.5004 at vD 0.0814).
  Likewise M185 stage-1's `borderline_frac -0.424 runs ANTI-mechanism` dismissed
  a value sitting inside the perfect-oracle band (0.462 / 0.539).
- The campaign claims "no a-priori weight-derived tail flag is available" and
  "the rotation-quality / tail signal is present in NO cheap observable"
  (FAILURE_MODE_GRAPH F5) are stated above their earned level. The defensible
  replacement: per-net difficulty IS cheaply predictable at or near the
  theoretical ceiling from weights alone; it is only ~18-25% of single-draw
  per-net MSE variance; and acting on it loses score.
