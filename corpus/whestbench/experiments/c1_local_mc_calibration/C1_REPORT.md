# C1 report — our local suite is 1.65x HARDER than the hosted one

Date: 2026-08-08. Predeclared: C1_PREDECLARATION.md (before the run).
Verdict: **case (C) — R > 1.25: our local suite is harder, and every local
score we hold UNDERSTATES its hosted expectation.**

## Measurement

Plain budget-matched antithetic Monte-Carlo estimator (57,344 samples, dense
forward, final layer only), pinned v0.14 subprocess runner, local public
indices 0..24, seed 0.

| quantity | value |
|---|---:|
| completed networks | 22 of 25 |
| mean adjusted (completed) | **1.0686e-6** |
| mean final-layer MSE | 1.0980e-6 |
| mean effective compute | 2.650e11 (97.4% of B) |
| implied per-sample variance v | 0.0630 |
| **hosted MC reference (observed on every submission page)** | **6.470e-7** |
| **ratio R = local / hosted** | **1.652** |

Deviation (loud): 3 of 25 networks tripped `combined_budget_exhausted` —
57,344 samples sat at 97.4% of budget with per-net spread pushing 3 over.
Those 3 are excluded; their zero-prediction penalties would otherwise swamp
the mean (the raw 25-net figure is 0.0978, an artifact, not a baseline).
A rerun at ~45k samples would clear it, but the calibration does not need it.

## Reading

R = 1.652 means a budget-matched MC estimator scores 1.65x WORSE on our
local networks than the grader's own MC reference scores on its 50-MLP public
split. Our suite has higher per-sample variance. Therefore local adjusted
scores should be **divided by ~1.65** to estimate hosted performance:

| candidate | local adjusted (descriptive) | hosted expectation |
|---|---:|---:|
| Kerdock M71 v3 | 1.619e-7 | **~9.8e-8** |
| two-axis L2 | 2.102e-7 | ~1.27e-7 |
| L1 champion | 2.122e-7 | ~1.28e-7 |
| our live entry #318609 | — | 5.47e-7 (measured) |

The estimate is conservative in direction: our reference is ANTITHETIC MC,
which is already variance-reduced. If the grader's reference is plain iid,
the true R is larger still and our candidates look better, not worse.

## Consequence

Against the board observed today, ~9.8e-8 places Kerdock v3 around **rank
13-14** — inside the top 15, and effectively at parity with the best honest
entry seen (oabuod #326058: adjusted 9.45e-8, MSE 1.872e-7 at 50.65% budget).
In the score-determining invariant MSE x C, Kerdock projects to ~2.70e4
against oabuod's 2.58e4: a 1.05x gap, not the 1.7x that the uncalibrated
local numbers implied.

The honest field's leader (rank 5, ednacob 4.62e-8) remains ~2.1x ahead. The
top four (4e-10 to 1e-9) are the unmetered-wall tier and are not a
like-for-like comparison.

## Status

DESCRIPTIVE calibration on burned public rows. It changes reporting and
expectation-setting only — no candidate was modified, promoted, or scored by
it.
