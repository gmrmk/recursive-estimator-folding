# S1 (s1_suite_risk_bootstrap) — VERDICT: PASS

Date: 2026-08-09. Harness: `run_s1.py` (this directory). Full numbers: `s1_results.json`.
Ran the full predeclared 100,000 suites per arm (runtime 1.8 s total; no reduction needed).

## Deviations from the predeclaration

- None on arms, gates, budgets, or suite size. Two modeling choices the ledger left
  unspecified, recorded here:
  1. The difficulty factor's "~1.1x spread" was implemented as log-uniform with
     max/min = 1.1 exactly, normalized to mean 1 (vD = 7.57e-4). The gate outcomes are
     insensitive to this shape: vD is ~480x smaller than the rotation variance vF.
  2. The M185 80-net checkpoint was FOUND and used for validation of the across-net
     spread (not for calibrating the rotation-factor distribution — the task assigns
     calibration to the P2 grid). See Limitations.

## Gate outcomes (predeclared thresholds)

| Gate | Value | Threshold | Result |
|---|---|---|---|
| P5-P95 width shrink, R=6 vs R=1 | 58.85% | >= 25% | PASS |
| \|mean shift\|, R=6 vs R=1 | +0.021% | < 2% | PASS |
| Rotation-draw variance dominant across-suite | share 99.79% at R=1 (vF·(1+vD)=0.3645 vs vD=7.6e-4) | dominant | PASS |

## Arm table (100,000 suites of 50 nets each; scale anchored to 1.83e-7 at R=1)

| R | Suite mean (± SE) | SD | P5 | P95 | P5-P95 width (± batch SE) | P(score < 1.6e-7) | P(< 1.0e-7) |
|---|---|---|---|---|---|---|---|
| 1 | 1.82959e-7 ± 3.3e-11 | 1.563e-8 | 1.5830e-7 | 2.0973e-7 | 5.1430e-8 ± 1.6e-10 | 0.06434 | 0 (< 1e-5) |
| 2 | 1.82932e-7 ± 4.0e-11 | 1.103e-8 | 1.6532e-7 | 2.0155e-7 | 3.6230e-8 ± 9.8e-11 | 0.01431 | 0 (< 1e-5) |
| 4 | 1.82995e-7 ± 1.9e-11 | 7.868e-9 | 1.7032e-7 | 1.9620e-7 | 2.5880e-8 ± 6.5e-11 | 0.00107 | 0 (< 1e-5) |
| 6 | 1.82997e-7 ± 1.7e-11 | 6.417e-9 | 1.7255e-7 | 1.9371e-7 | 2.1162e-8 ± 5.3e-11 | 0.00010 | 0 (< 1e-5) |

Note the two-sided nature of the thinning: R=6 cuts the chance of an unluckily BAD
suite draw, and equally cuts the chance of a lucky sub-1.6e-7 draw (6.4% -> 0.01%).
The mechanism buys variance reduction around the same mean, not a better mean.

## Two-signal verification

1. Analytic SD `S*sqrt((vD + (1+vD)*vF/R)/50)` vs bootstrap SD — ratios
   0.999 / 0.996 / 1.003 / 1.000 for R = 1/2/4/6 (independent derivation, agrees).
2. Bitwise repeat of the R=1 first chunk with the same seed: SHA-256 identical (True).
3. Width shrink 58.85% matches the rotation-dominant closed form 1 - 1/sqrt(6) = 59.18%
   to within batch noise.

## Calibration

- Rotation-factor pool: 48 values = 3 nets x 16 per-rotation MSEs from the P2 grid,
  each net mean-normalized, pooled, mean forced to 1. vF = 0.3642; pool max/min = 11.07
  (within-net spreads 7.16x / 11.07x / 4.69x for nets 101/202/303).
- Difficulty factor: log-uniform, max/min = 1.1, mean 1, vD = 7.57e-4.
- Anchor: S = 1.83e-7; realized R=1 bootstrap mean 1.82959e-7 (-0.02% from anchor).

## Limitations

1. M185 spread validation: the model's simulated 80-net single-draw max/min spread is
   9.14-11.94 (P5-P95, median 11.18) vs the observed hosted 15.53x (m185 stage1
   `mse_raw`; identical value recorded in `a1b_tail_diagnostics.json`). The 48-value
   empirical pool has bounded support (max/min 11.07, times up to 1.1 from D), so it
   cannot reproduce the heaviest observed tail: the model somewhat UNDERSTATES the R=1
   tail. This is conservative for the PASS: a heavier-tailed F increases vF and pushes
   the R=6 width shrink toward (and not below) the 59.2% rotation-dominant limit, far
   above the 25% gate. It does mean the absolute widths in the table are lower bounds.
2. The rotation-factor distribution is calibrated from only 3 nets x 16 rotations;
   per-net normalization removes net-level location but the pool conflates possible
   net-shape differences.
3. The model treats the R rotation estimates as independent and unbiased so that
   equal-weight averaging gives exactly MSE = S*D*mean(F_1..F_R) (mean preserved,
   rotation variance / R). Cross-rotation error correlation, if any, would reduce the
   realized shrink; the P2 grid uses distinct rotation seeds per draw, consistent with
   independence.
4. The 1.1x difficulty spread and the 1.83e-7 anchor are taken from the ledger as
   given, not re-measured here.

## Data files used (exact paths)

- `C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\publish\recursive-estimator-folding\corpus\whestbench\experiments\pb1_premise_battery\p2_results.json`
  (`q1_oracle_headroom.per_net.{101,202,303}.mse_per_rotation`, 16 each)
- `C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\publish\recursive-estimator-folding\corpus\whestbench\experiments\a_series_granular_adversarial\m185_g0_stage1_checkpoint.json`
  (80 nets, `mse_raw`; spread 15.53x — validation only)
- `C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\publish\recursive-estimator-folding\corpus\whestbench\experiments\a_series_granular_adversarial\a1b_tail_diagnostics.json`
  (independent record of the 15.53x spread)
