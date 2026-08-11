# SPD-loss width scaling of the M179 zero-order recurrence

**Status: MEASURED. `KILL_NO_SCALING` does not fire. `KILL_HARNESS` PASS (2/2).**

`gm_m179_m199` established that the exact zero-order full-covariance recurrence
leaves the positive-definite cone before layer 32 at width 256 (layers 12 and
10), while width 48 reached layer 32 on both replicates it tried. This fills the
unmeasured interval and finds the effect is a width trend, not a width-256
anomaly — with one predeclared clause that did not hold and is reported as such.

## Deviations and failures, at the top

1. **The strict monotonicity clause of `KILL_NO_SCALING` FAILED at one step.**
   Median `ℓ*` over widths 64..224 runs
   `18.5 → 23.5 → 19.5 → 15.5 → 15.0 → 12.5 → 11.0 → 9.0`. The `64 → 72` step
   rises. Width 64 has 4 replicates against width 72's 8 and is the noisiest
   point in the sweep. The kill condition is conjunctive and its second clause
   (width 256 not separated from width 48) is decisively false, so
   `KILL_NO_SCALING` does not fire — **but the strict per-width monotone claim
   is not supported and is not asserted anywhere below.** The robust statement
   is the rank correlation.
2. **The predeclared crossing range was wrong in the safe direction.** The
   prediction was that `ℓ*` crosses below 32 somewhere in `64 ≤ n ≤ 160`. It has
   already crossed at the bottom of that range: no replicate at width ≥ 96
   reaches layer 32. Reported as a missed prediction, not retuned.
3. **The predicted mechanism holds only at large width.** See § Mechanism. At
   small width the floor is reached by genuine decay, far above roundoff. The
   predeclaration asserted one mechanism throughout; that was too simple.
4. Width 48's original `reaches layer 32` record rested on 2 replicates. At 8
   replicates it is `3/8`. No claim in `gm_m179_m199` depended on it, but the
   two-replicate reading was not representative.

## Second signal

Three independently produced datasets were merged on `(width, replicate)`:
this sweep, this experiment's transition sweep, and
`gm_m179_m199/diag_spd_depth.json`. **96 distinct cells, 6 overlapping cells,
0 conflicts.** The width-256 replicates 0 and 1 reproduce `diag256.log`
exactly (`ℓ* = 12` and `ℓ* = 10`), which is the predeclared `KILL_HARNESS`
admissibility check.

## Result

`ℓ*` = first layer with `min eig(C) ≤ 1e-12`; `—` = never tripped through 32.

| width | cells | reach L32 | P(reach) | median `ℓ*` | min | max |
|---:|---:|---:|---:|---:|---:|---:|
| 32 | 8 | 6 | 0.75 | — | 18 | 24 |
| 40 | 8 | 6 | 0.75 | — | 11 | 16 |
| 48 | 8 | 3 | 0.38 | 28.0 | 18 | 30 |
| 56 | 8 | 6 | 0.75 | — | 21 | 30 |
| 64 | 4 | 0 | 0.00 | 18.5 | 12 | 27 |
| 72 | 8 | 1 | 0.12 | 23.5 | 12 | 26 |
| 80 | 8 | 1 | 0.12 | 19.5 | 8 | 30 |
| 96 | 4 | 0 | 0.00 | 15.5 | 10 | 18 |
| 128 | 4 | 0 | 0.00 | 15.0 | 12 | 18 |
| 160 | 4 | 0 | 0.00 | 12.5 | 8 | 14 |
| 192 | 4 | 0 | 0.00 | 11.0 | 10 | 14 |
| 224 | 4 | 0 | 0.00 | 9.0 | 9 | 11 |
| 256 | 2 | 0 | 0.00 | 11.0 | 10 | 12 |

Two statements are supported:

1. **Rank trend.** Spearman `ρ(width, ℓ*) = −0.621` over all 96 cells and
   **`−0.743`** over the 74 cells with width ≥ 32, censoring `reaches 32` at 33.
2. **Reachability collapse.** **0 of 22 replicates at width ≥ 96 completed 32
   layers in a PSD-safe state**, against 21 of 32 at widths 32–56. At the
   production width of 256 the recurrence trips by layer 10–12 of 32.

Replicate spread is large at every width (e.g. width 80 spans `ℓ* = 8` to
`reaches 32`), so **no single-replicate claim is admissible** and none is made.

## Mechanism

Recorded per layer: `assembly_scale = ε · n · λ_max`, the scale at which an
entrywise-assembled Gram matrix goes indefinite from float64 round-off alone.
The table gives the median of `|min eig| / assembly_scale` **at the failure
layer**:

| width | 32 | 40 | 48 | 56 | 64 | 72 | 80 | 96 | 128 | 160 | 192 | 224 | 256 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ratio | 431 | 41 | 15.6 | 13.4 | 2.63 | 3.83 | 0.154 | 3.08 | 0.59 | 0.251 | 0.248 | 0.0398 | 0.677 |

**The mechanism changes with width.** Below ~64 the failure occurs with
`min eig` one to three orders of magnitude *above* the round-off scale: the
covariance is genuinely, geometrically ill-conditioning with depth and trips a
real floor. From ~80 upward the ratio falls to `O(1)` and below: `min eig` is at
or beneath the entrywise-assembly noise.

> **CORRECTION (superseded by `gm_factored_cholesky`).** An earlier version of
> this section read that ratio as showing that *at production width the
> indefiniteness **is** round-off in the dense entrywise representation*. That
> causal inference was wrong. `gm_factored_cholesky` removed the assembly error
> entirely by forming `C = M^T M` as a Gram (PSD by construction) and the trip
> layer was **unchanged in 6 of 6 cells**. `lambda_min` decays geometrically —
> median per-layer ratio 0.081–0.120 at width 256 — as a property of the
> propagated covariance itself; round-off is concurrent, not causal. The ratio
> measurement above stands; only the causal reading was wrong.

## What this does and does not license

**Licensed:**

- The exact zero-order full-covariance recurrence, *as represented*, does not
  reach depth 32 at production width. `gm_m179_m199`'s ARM C reachability kill
  is a width effect, not a seed accident.
- `relu_moments` gates on diagonal variance and pairwise `ρ` and never on the
  spectrum, so the producer **silently propagates a numerically non-PSD
  covariance** from roughly layer 10–12 onward at width 256. That is a
  correctness defect in a component described as certified, and it is
  independent of everything above: it is true even if the ceiling is repairable.

**Not licensed:**

- This is **not** a statement that no Gaussian closure can reach depth 32. The
  large-width failure is round-off in a *dense entrywise* float64 representation.
  A factored propagation (Cholesky or eigendecomposition of `V`, composing
  factors rather than re-assembling entries) would preserve PSD by construction
  and is **untested**. That is the natural next mutation and this experiment
  does not close it.
- No estimator, variance, MSE, score, champion, promotion, or submission claim.
  Accuracy is not measured here at all — only definedness.
- Higher precision is predicted to buy only logarithmically many layers at large
  width, since the crossing is set by `ε · n · λ_max` against a geometrically
  decaying `λ_min`. **Predicted, not measured.** A float128 arm would test it.

## Reproduction

```bash
pip install -r requirements.txt
cd corpus/whestbench/experiments/gm_spd_width_scaling
python3 run_spd_width_scaling.py --widths 64,96,128,160,192,224 --reps 4 --controls
python3 run_spd_width_scaling.py --widths 32,40,48,56,72,80 --reps 8 --out transition.json
python3 analyze.py
```

Requires the M178/M179/M198/M200 modules that live alongside this directory.
Synthetic He-Gaussian weights only, via `m200.generated_weights` with the
`cell_seed` scheme of `gm_m179_m199/diag_spd_depth.py`. No truth, scorer,
holdout, private data, leaderboard, submission, network, or champion access.
Wall time for the full sweep is about 6 minutes on 4 cores.
