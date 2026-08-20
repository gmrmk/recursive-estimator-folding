# S4 Verdict — Designation Portfolio Bootstrap

**Ledger id:** `s4_designation_portfolio_bootstrap`
**Date:** 2026-08-09 | **Runtime:** 4.0 s | **Suites per cell:** 100,000 (full predeclared count; no reduction needed)
**Deviations from predeclaration:** none.

## VERDICT: SURVIVES

The portfolio frame survives via the **same-mean arm**: the diversification gain
P(min < T | rho=0.0) − P(min < T | rho=1.0) exceeds the predeclared 2-percentage-point
bar at **all three** thresholds. The R6 arm fails the bar everywhere on its own.

### Gate table (gate arms: same_mean, r6; bar = 2.00 pp at ANY threshold)

| arm @ T | gain (pp) | 95% CI (pp) | meets 2 pp? |
|---|---|---|---|
| same_mean @ 1.55e-7 | **2.85** | [2.80, 2.91] | YES |
| same_mean @ 1.60e-7 | **6.00** | [5.88, 6.12] | YES |
| same_mean @ 1.70e-7 | **16.50** | [16.28, 16.72] | YES |
| r6 @ 1.55e-7 | 0.00 | [0.00, 0.00] | no |
| r6 @ 1.60e-7 | 0.00 | [-0.00, 0.01] | no |
| r6 @ 1.70e-7 | 1.53 | [1.44, 1.61] | no |

CIs are chunk-paired (common random numbers across rho, 10 chunks of 10k).

## Harness check — S1 reproduction (PASS)

Candidate A was re-simulated through S4's Gaussian-copula inverse-CDF path (a
different sampling route than S1's direct integer indexing — a genuine second
derivation of the same marginal):

- A's R=1 suite SD: **1.5560e-8** vs S1 bootstrap reference **1.5626e-8** (ratio 0.9958, within the 2% tolerance) and analytic `S*sqrt((vD+(1+vD)vF)/50)` = 1.5640e-8 (ratio 0.9949).
- P(A < 1.6e-7) = **0.0637** vs S1's 0.0643 (difference 0.0006, within combined MC noise ~0.0011 for two independent 100k runs).
- R6 marginal construction: presample variance 0.060694 vs target vF/6 = 0.060700.

## Single-designation baseline

P(scoreA < T), A = v3.1 profile (mean 1.83e-7, R=1):

| T | P(A < T) |
|---|---|
| 1.55e-7 | 0.0285 |
| 1.60e-7 | 0.0637 |
| 1.70e-7 | 0.2063 |

## P(at least one of two designated entries < T) — full grid

Per-cell binomial 95% CI half-width is at most ~0.31 pp (worst case at P≈0.5);
full per-cell SEs are in `s4_results.json`.

### same_mean arm (B: mean 1.83e-7, R=1 — pure correlation effect)

| rho_pair | P(min<1.55e-7) | P(min<1.60e-7) | P(min<1.70e-7) | score corr(A,B) |
|---|---|---|---|---|
| 0.0 | 0.0570 | 0.1237 | 0.3713 | 0.002 |
| 0.3 | 0.0559 | 0.1193 | 0.3488 | 0.257 |
| 0.6 | 0.0511 | 0.1097 | 0.3191 | 0.534 |
| 0.9 | 0.0424 | 0.0901 | 0.2684 | 0.855 |
| 1.0 | 0.0285 | 0.0637 | 0.2063 | 1.000 |

Decorrelating a same-mean second entry roughly **doubles** the hit probability at
every threshold (0.0285→0.0570; 0.0637→0.1237; 0.2063→0.3713). Most of the gain
survives partial correlation: even at rho=0.9 the entry pair beats a clone pair by
1.4/2.6/6.2 pp; at rho=0.6 by 2.3/4.6/11.3 pp.

### r6 arm (B: mean 1.83e-7, rotation variance /6)

| rho_pair | P(min<1.55e-7) | P(min<1.60e-7) | P(min<1.70e-7) | score corr(A,B) |
|---|---|---|---|---|
| 0.0 | 0.0285 | 0.0638 | 0.2216 | 0.005 |
| 0.3 | 0.0285 | 0.0638 | 0.2174 | 0.274 |
| 0.6 | 0.0285 | 0.0637 | 0.2116 | 0.553 |
| 0.9 | 0.0285 | 0.0637 | 0.2067 | 0.846 |
| 1.0 | 0.0285 | 0.0637 | 0.2063 | 0.946 |

The R6 variant's own left tail cannot reach the tight thresholds
(P(B_r6 < 1.6e-7) = 0.0001, P(B_r6 < 1.55e-7) = 0.0), so pairing A with a
decorrelated R6 entry adds nothing below 1.7e-7 and only +1.5 pp at 1.7e-7.
Variance reduction (R6) is a *single-entry consistency* play; it removes exactly
the tail mass a portfolio needs.

### l2 arm (B: mean 2.10e-7 — decision support, not a gate input)

| rho_pair | P(min<1.55e-7) | P(min<1.60e-7) | P(min<1.70e-7) |
|---|---|---|---|
| 0.0 | 0.0286 | 0.0645 | 0.2127 |
| 1.0 | 0.0285 | 0.0637 | 0.2063 |

**Does diversification ever beat designating A twice?** Effectively no at a
2.10e-7 mean: a fully decorrelated worse-mean entry beats the single-designation
baseline by at most +0.64 pp (at 1.7e-7) and by ≤0.08 pp at the tight thresholds.
The second slot should go to a comparable-mean entry or not be counted on at all.

### sens_fold3cap arm (B: mean 1.41e-7 — WEAK EVIDENCE, 5-net number; decision support only)

| rho_pair | P(min<1.55e-7) | P(min<1.60e-7) | P(min<1.70e-7) |
|---|---|---|---|
| 0.0 | 0.8768 | 0.9397 | 0.9900 |
| 1.0 | 0.8763 | 0.9386 | 0.9883 |

If the fold3cap 1.41e-7 mean is real, that entry alone clears 1.55e-7 with
p≈0.88 and correlation becomes irrelevant (gains ≤0.17 pp). The portfolio
question then collapses into a mean question. This number rests on 5 nets and is
labeled weak evidence per the predeclaration.

## Cross-checks (two-signal rule)

1. **rho=1 identity:** same_mean B is bitwise identical to A at rho_pair=1.0 (asserted every chunk) — the correlation dial's endpoint is exact.
2. **rho=0 independence product:** simulated P(min<T) vs 1−(1−pA)(1−pB) from the same run's marginals agrees to ≤0.016 pp in every arm (residual gap consistent with the shared-difficulty score correlation of 0.002).
3. **Bitwise repeat:** chunk 0 re-run from re-spawned seeds reproduces scoreA and the (same_mean, rho=0.3) min-scores hash exactly.
4. **Copula dial realized:** factor-level Pearson correlations at dialed rho {0, 0.3, 0.6, 0.9, 1.0} came out {0.000, 0.257, 0.536, 0.856, 1.000} (pool marginal) — slightly below latent rho, as expected for a skewed marginal under a Gaussian copula (the dial is the latent/rank correlation, per predeclaration).

## Limitations

- **rho_pair between real candidate families is UNKNOWN.** This experiment measures the value of decorrelation IF achievable, not whether any two families we could actually field are decorrelated. Two same-family variants likely sit at rho ≥ 0.9; the table shows even that retains 1.4–6.2 pp over a pure clone, but the load-bearing decision (what rho two real entries would have) is unmeasured.
- All absolute probabilities inherit S1's model: rotation pool from only 3 nets × 16 rotations, difficulty spread fixed at 1.1x. S1's own m185 cross-check showed the model UNDER-predicts the observed 80-net spread (15.5x observed vs model p95 ≈ 11.9), so real tails are likely heavier than modeled; the rho-*comparative* gains are more robust than the absolute P levels.
- The anchor 1.83e-7 (A's true suite mean) is itself an estimate; P(A<T) near a threshold is sensitive to it.
- The R6-arm coupling ties B's *averaged* rotation factor rank to A's single-draw rank at the dialed rho (the natural reading of the predeclaration); a mechanistic model of shared rotations would induce a specific rho rather than a dialed one.
- Prize thresholds are unknown; T = {1.55e-7, 1.6e-7, 1.7e-7} bracket the near-rival band per the task context.
- fbar6 presample renormalized to mean exactly 1 (a ~2.5e-4 relative nudge) to keep the anchor exact.

## Files

- `run_s4.py` — harness (this directory)
- `s4_results.json` — full grid, gains with CIs, cross-checks, calibration
- `S4_VERDICT.md` — this file
