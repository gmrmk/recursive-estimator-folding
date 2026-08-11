# Predeclaration — characterizing G7 as depth degeneracy

Written before any code in this directory was run. No result was read before
this file was committed.

## What is already established

`gm_factored_cholesky` closed the representation question: forming `C = MᵀM` as
a Gram, PSD by construction, leaves the trip layer unchanged in 6/6 cells.
`λ_min` decays geometrically — median per-layer ratio `0.0814` / `0.1202` at
width 256 — while `λ_max` holds at `O(8)`. Round-off is concurrent, not causal.

`gm_spd_width_scaling` established the width law: `ρ(width, ℓ*) = −0.743`,
0/22 replicates reach depth 32 at width ≥ 96.

**What is claimed but not yet measured** is the *mechanism*: that this is the
spectral form of finite-width depth degeneracy (Jakub & Nica, arXiv:2302.09712,
already in `sources/research_physics_depth_finitewidth_20260810.md`). That claim
currently rests on a plausible chain — exponential angle contraction drives
correlations toward 1, and a correlation matrix with off-diagonals near 1 has
`λ_min → 0` — plus two consistent endpoint numbers (`max|ρ| = 0.942, 0.971` at
layer 32). **A plausible chain and two endpoints is not a mechanism claim.** This
experiment measures the link directly, or fails to.

## Predictions, stated before running

**P1 — the spectral collapse *is* the angle contraction.** Per layer,
`λ_min/λ_max` tracks `1 − ρ̄` (mean absolute off-diagonal correlation) up to a
constant factor. *Falsified* if the ratio `(λ_min/λ_max)/(1 − ρ̄)` drifts by more
than 10x across the healthy prefix — that would mean the two quantities are not
measuring the same geometry and the depth-degeneracy attribution is unsupported.

**P2 — the per-layer decay rate is width-dependent.** `r(n) = median
λ_min(l+1)/λ_min(l)` decreases with `n` (faster collapse at larger width). This
is the prediction most likely to be wrong: the competing account is that `r` is
roughly width-independent and the observed `ℓ*(n)` trend comes from `λ_min`
starting lower at larger `n` (more dimensions, more chances for a near-degenerate
direction — a Marchenko–Pastur-style effect) rather than from contracting faster.
**These two accounts are distinguishable and this experiment separates them.**

**P3 — required precision is linear in depth.** `log10 κ(L)` grows linearly in
`L` with slope `log10(1/r)`. This turns "you would need ~35 digits" from an
extrapolation into a fitted line with a residual.

**P4 — the mechanism discriminator: orthogonal initialization.** Haar-orthogonal
weights at matched scale (`sqrt(2)·Q`, same expected column norm as He's
`sqrt(2/n)` Gaussian) **slow or remove** the collapse relative to He-Gaussian at
the same width and depth.

Rationale for P4: dynamical isometry. Orthogonal initialization preserves
singular-value structure through depth where Gaussian initialization does not. If
orthogonal init also collapses at the same rate, the obstruction is a property of
**ReLU composition itself**, which is the stronger and more general claim. If
orthogonal init survives to depth 32, the obstruction is a property of the
**Gaussian ensemble**, which is narrower — and it would mean the competition's
He-initialized networks are a hard case rather than a universal one.

Either outcome sharpens the paper. **P4 is the highest-information measurement
here and its result should be reported first regardless of direction.**

## Scope and honesty limits

- The competition's networks are He-Gaussian. **The orthogonal arm is a
  mechanism diagnostic and is not a competition claim of any kind.** No result
  from it may be read as changing any score, variance, or estimator statement.
- Synthetic weights only; the He arm uses `m200.generated_weights` with the
  `gm_m179_m199` `cell_seed` scheme so cells remain comparable with the existing
  SPD record. The orthogonal arm uses a generator defined in this directory,
  seeded from the same scheme, and is labelled distinctly everywhere.
- float64 only. No clip, floor, ridge, or eigenvalue truncation.
- Effective rank is reported as spectral entropy `exp(−Σ pᵢ log pᵢ)` with
  `pᵢ = λᵢ/Σλ`. It is a descriptive statistic, not a gate.
- Decay rates are medians over the healthy prefix (layers before the floor
  trip). Once `λ_min` is at the floor the ratio is measuring noise, and including
  those layers would bias the fit toward 1.
- **This measures definedness and geometry, not accuracy.** Nothing here touches
  `t2`'s 311x or the 1.40x analytic-control cap, and a deeper G7 does not improve
  the score arm.

## Second signal

The He arm at width 256, replicates 0 and 1, must reproduce `ℓ* = 12` and `10`
from `gm_spd_width_scaling` / `diag256.log`. A mismatch invalidates this harness
before any claim is read from it.
