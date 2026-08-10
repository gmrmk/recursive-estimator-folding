# gm_spd_width_scaling

Measures `ℓ*(n)` — the layer at which the M179 zero-order full-covariance
recurrence's pre-ReLU covariance leaves the positive-definite cone — as a
function of width, filling the interval `(48, 256)` that `gm_m179_m199` left
unmeasured.

Read `PREDECLARATION.md` first (written before any code here ran), then
`REPORT.md`.

## Headline

- **0 of 22 replicates at width ≥ 96 complete 32 layers in a PSD-safe state.**
  Spearman `ρ(width, ℓ*) = −0.743` over the 74 cells with width ≥ 32.
- `relu_moments` gates on diagonal variance and pairwise `ρ`, never on the
  spectrum, so the producer **silently propagates numerically non-PSD
  covariance** from roughly layer 10–12 onward at width 256. That is a
  correctness defect in a component described as certified, and it holds
  regardless of whether the ceiling itself is repairable.
- The large-width failure is round-off in the **dense entrywise** float64
  representation. A factored (Cholesky / eigendecomposition) propagation would
  preserve PSD by construction and is **untested** — the natural next mutation.

## Running

Requires the sibling M178/M179/M198/M200 experiment modules, which arrive with
PR #1 (`agent/compression-survivor-corpus`). On a checkout that has them:

```bash
pip install -r requirements.txt   # numpy
python3 run_spd_width_scaling.py --widths 64,96,128,160,192,224 --reps 4 --controls
python3 run_spd_width_scaling.py --widths 32,40,48,56,72,80 --reps 8 --out transition.json
python3 analyze.py
```

`--controls` runs width-256 replicates 0 and 1 against the values recorded in
`gm_m179_m199/diag256.log`; the harness is admissible only if both reproduce.
They do (`ℓ* = 12`, `ℓ* = 10`).

`analyze.py` merges this directory's results with
`gm_m179_m199/diag_spd_depth.json` on `(width, replicate)` — the generator and
`cell_seed` scheme are identical, so overlapping cells are reproduction checks.
96 distinct cells, 6 overlapping, 0 conflicts.

## Firewall

Synthetic He-Gaussian weights only. No truth, scorer, holdout, private data,
leaderboard, submission, network, or champion access. No estimator, variance,
MSE, or score claim — this measures definedness, not accuracy.
