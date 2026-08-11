# Spectral PSD guard — closing the silent-acceptance defect

**Status: implemented, tested (11/11), additive. The frozen M179 producer is not
modified.** This is a detector, not a repair.

## The defect

`gm_m179_m199` found it and stated it in the producer's own terms:

> `relu_moments` checks diagonal variance and pairwise rho, never the spectrum,
> so it silently **ACCEPTS** a numerically non-PSD covariance from layer 12-13
> onward at width 256. … The 31-layer archive was never validated for spectral
> PSD at depth, and that is a gap in our own record.

`gm_spd_width_scaling` then measured it as a width law rather than one width's
anomaly.

## Blast radius, measured over the 74 cells on record

| width | cells | spectral guard fires | median first-loss layer | layers downstream | share of archive |
|---:|---:|---:|---:|---:|---:|
| 32 | 8 | 2 | 21.0 | 12 | 38% |
| 64 | 4 | 4 | 18.5 | 14.5 | 45% |
| 96 | 4 | **4** | 15.5 | 17.5 | 55% |
| 128 | 4 | **4** | 15.0 | 18 | 56% |
| 160 | 4 | **4** | 12.5 | 20.5 | 64% |
| 192 | 4 | **4** | 11.0 | 22 | 69% |
| 224 | 4 | **4** | 9.0 | 24 | **75%** |
| 256 | 2 | **2** | 11.0 | 22 | **69%** |

Two numbers are the headline:

- **The shipping per-pair guard (`|rho| ≤ RHO_MAX`) fired 0 times in 74 runs.**
  Not rarely — never. It has no recorded instance of refusing anything.
- **At width ≥ 96 the spectral guard fires in 18 of 18 cells.** At production
  width 256, layers 11–32 — **69% of the archived layers** — are downstream of
  the loss, and 75% at width 224.

So the certified provider emits a 31-layer background archive at production
width in which roughly two thirds of the layers carry a numerically non-PSD
covariance, behind a guard that has never once fired.

## Why this is additive, not a patch

`m179_background_producer.py` is frozen under `M179_SHA256SUMS_20260807.txt`.
Editing it would break the manifest and violate the fold discipline, which is
the same discipline that caught this defect. So the guard is a **separate
mechanism** that composes in front of the frozen producer:

```python
from m179_background_producer import relu_moments
from spectral_psd_guard import guarded_zero_order_recurrence

states = guarded_zero_order_recurrence(weights, relu_moments)
```

`relu_moments` is injected rather than imported, so the module and its tests run
on a checkout without PR #1.

Style matches the producer's existing stratum discipline: **fail closed, raise,
no clip, no floor, no ridge, no eigenvalue truncation.** The refusal carries the
diagnostic the per-pair guard cannot produce — layer, `min eig`, `lambda_max`,
and the entrywise assembly scale `eps · n · lambda_max`, plus whether the
eigenvalue sits at or below that scale (the round-off regime measured above
width ~80) or far above it (genuine ill-conditioning, below ~64).

## The witness in the test suite

The clearest demonstration that a per-pair guard *cannot* see this: the
equicorrelation matrix `(1−r)I + r·11ᵀ` has eigenvalues `1+(n−1)r` once and
`1−r` with multiplicity `n−1`. At `r = −1/(n−1)` the first is **exactly zero**,
so the matrix is singular — while **every** pairwise correlation is exactly
`−1/(n−1) = −0.2` for `n=6`, nowhere near `RHO_MAX`.

A per-pair guard sees six harmless correlations. The matrix is singular. No
tightening of a pairwise bound can ever catch it; the quantity is spectral.

## What this does and does not do

**Does.** Makes the silent acceptance loud, at the first unsafe layer, with a
diagnostic that names the regime. Any archive produced under it is either
spectrally validated at depth or refused.

**Does not.** It does not make the closure reach layer 32. Nothing here changes
the mathematics, and it will cause runs that currently "succeed" to fail closed
— **that is the point**, and the ledger should record which. The honest repair,
still untested, is to propagate a *factored* state (Cholesky or
eigendecomposition of `V`, composing factors rather than re-assembling the
covariance entrywise), which preserves PSD by construction.

**Recommended disposition:** land this before the M178/M179 provider is cited as
certified in any filing. A provider that silently propagates non-PSD state
through two thirds of its output layers should not carry that word.

## Reproduction

```bash
pip install -r requirements.txt        # numpy
python3 -m unittest tests.test_spectral_psd_guard -v
```

numpy only; no corpus data, truth, scorer, holdout, private data, leaderboard,
submission, or champion access. No estimator, variance, MSE, or score claim.
