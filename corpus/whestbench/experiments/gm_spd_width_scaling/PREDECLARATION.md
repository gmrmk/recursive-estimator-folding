# Predeclaration — SPD-loss width scaling of the M179 zero-order recurrence

Written before any code in this directory was run. No results were read before
this file was committed.

## Mechanism under test

One mechanism only: **the width dependence of the depth at which the M179
zero-order full-covariance recurrence leaves the positive-definite cone.**

`gm_m179_m199` established, at two widths, that the pre-ReLU covariance
`C = W^T (V W)` acquires `min eig(C) <= VARIANCE_FLOOR` before layer 32:

| width | rep 0 | rep 1 |
|---:|---:|---:|
| 48 | reaches 32 | reaches 32 |
| 256 | **layer 12** | **layer 10** |

Every width in `(48, 256)` is unmeasured. This experiment measures that
interval.

## Why this is the cheapest falsifier of the strongest available claim

The `gm_m179_m199` VERDICT records two facts that together make the interval
decisive:

1. The M179 producer's own guard is **per-pair** (`|rho| <= RHO_MAX`) and is
   never violated at width 256. The recurrence therefore *completes* all 32
   layers while silently carrying a numerically non-PSD covariance from layer
   12 onward.
2. `relu_moments` "checks diagonal variance and pairwise rho, never the
   spectrum". The 31-layer archive "was never validated for spectral PSD at
   depth".

If SPD loss is a **scaling law** in width, the exact Gaussian closure is
undefined at production width as a matter of structure, and the certified
provider needs a spectral guard. If it is a **narrow numerical artifact**
confined to width 256, the defect is local and repairable by conditioning.
These predict opposite curves and the experiment separates them cheaply.

## Predicted signature

`ell*(n)` — the first layer with `min eig(C) <= 1e-12` — is **monotonically
decreasing in width** over `64..256`, crossing below 32 somewhere in
`64 <= n <= 160`, and reaching `10-12` by `n = 256`.

Rationale for the prediction: `C` is assembled entrywise from the M178 Owen-T /
Tallis moments, so each entry carries `O(eps)` error while `lambda_max` grows
with `n`. An entrywise-assembled Gram matrix goes indefinite once
`lambda_min <~ eps * n * lambda_max`. Depth drives `lambda_min` down
geometrically (the width-2 trace falls `2.66 -> 2.9e-5` over eight layers),
so `ell*` should fall as `n` rises.

## Kill conditions (predeclared)

- **KILL_NO_SCALING** — `ell*(n)` shows no monotone trend over `64..224` and
  width 256 is not separated from width 48 beyond replicate spread. The
  structural reading is then refuted and the width-256 result is a local
  artifact.
- **KILL_HARNESS** — the reproduction cells at width 256 fail to return
  `ell* = 12` (rep 0) and `ell* = 10` (rep 1). Any other value means this
  harness does not reproduce `gm_m179_m199` and no result from it may be used.

## Scope and honesty limits

- Synthetic He-Gaussian weights only, via `m200.generated_weights`, the same
  generator and the same `cell_seed` scheme as `diag_spd_depth.py`. No truth,
  scorer, holdout, private data, leaderboard, submission, or champion work.
- This measures **where the closure becomes undefined**, not its accuracy. It
  makes no estimator, variance, MSE, or score claim.
- 4 replicates per width. Replicate spread at small widths in the existing
  record is large (width 2: layers 20 and 29), so **no single-replicate claim
  is admissible** and the reported statistic is the per-width min/median/max.
- Float64 only. A float128 or factored-propagation repair is a *different*
  mechanism and is explicitly out of scope here.

## Second signal

Width 256, replicates 0 and 1, are run as reproduction controls against
`diag256.log`. The harness is admissible only if both reproduce exactly.
