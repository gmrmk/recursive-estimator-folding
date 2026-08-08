# N7 predeclaration — does RQMC superconvergence materialize at depth 32?

Date: 2026-08-08 (before code/run). The one open scientific lever from
RESEARCH_INTEL_20260808.md §3.

## Mechanism under test

The final-layer integrand's effective dimension reportedly collapses
(participation ratio 128 -> 5.2 by layer 32). Randomized QMC (rank-1
Kronecker lattice with Cranley-Patterson shifts, antithetic) on
low-effective-dimension integrands can achieve MSE ~ N^-2 rather than MC's
N^-1. If real here, honest full-budget RQMC (~65k samples) reaches raw MSE
far below the sampling family's 2.5e-7 plateau.

## Measurement

2-3 synthetic He nets. For N in {4096, 16384, 65536, 262144}: R = 6
independent Cranley-Patterson replicates of the lattice estimator (golden
Kronecker vector, inverse-CDF normals, antithetic pairs) and R = 6 plain-MC
replicates. MSE(N) = mean over replicates of per-neuron squared error vs a
3-4M-sample MC truth (truth noise ~5e-9-7e-9, resolves MSE down to ~2.5e-8;
points below 5x truth noise are censored from the fit). Fit slope beta on
log MSE vs log N over the uncensored points.

## Predeclared verdicts

- MC control must show beta_MC in [-1.2, -0.8] (harness sanity; else invalid).
- KILL (superconvergence absent): beta_RQMC > -1.25 — RQMC is then a
  constant-factor gain only, the leaders' band is NOT honestly reachable by
  sampling rate, and the honest ceiling remains the ~2.5e-7-family plateau
  divided by small constants.
- INTERESTING: beta_RQMC in (-1.7, -1.25] — extrapolate to the budget point
  and report the implied honest raw MSE with the censoring caveat.
- SUPERCONVERGENCE: beta_RQMC <= -1.7 — the leaders' band is plausibly
  honestly reachable; N8 (a metered RQMC estimator variant) becomes the
  next mutation.

## Bias class / firewall

Response-free premise probe: synthetic nets + own sampling only; no public
rows, no submission credit, descriptive slope measurement.
