# T2 report — the full-covariance closure is not a score candidate (K1 fired)

Date: 2026-08-08. Predeclared: T2_PREDECLARATION.md (written before code).
Disposition: **killed implementation** (closure-as-standalone-estimator at
depth 32), **preserved component** (the certified M178/M179 machinery itself —
its exactness certificates are untouched; this kill is about score value).

## Measured (3 seeds, He-init f32 width-256 depth-32, response-free)

| seed | closure raw MSE | MC noise floor | bias MSE | closure wall |
|---|---:|---:|---:|---:|
| 101 | 7.2707e-5 | 1.076e-7 | 7.2600e-5 | 120.70 s |
| 202 | 1.7879e-4 | 1.950e-7 | 1.7860e-4 | 126.85 s |
| 303 | 3.7099e-5 | 1.314e-7 | 3.6968e-5 | 128.47 s |

Mean bias MSE **9.6055e-5**. Kill gate K1 (bias >= 2.102e-6) **FIRED** — by a
factor of ~46. K3 clear (MC floor 200-1000x below signal; the measurement is
fully resolved, this is not noise). Ground truth: 400k-sample chunked MC per
net, variance-derived noise floor subtracted. Artifact: t2_results.json.

## Consequences

1. **No floor, no wall, no vectorization saves it.** Even a zero-cost closure
   at the 0.1 floor would score 9.6e-6 adjusted — 46x worse than the L2
   sampler (2.1020e-7). The planned T2b vectorized-closure mutation is
   CANCELLED before it was built; the wall question (125 s/net as-implemented,
   multiplier 46, strict-fail) is moot.
2. **The corpus's 8.76e-7 "exact (mu,sigma) closure oracle ceiling" is
   contradicted at the observed level.** The propagated exact full-covariance
   Gaussian closure reaches only ~9.6e-5 at depth 32. Either that reported
   number measured a different object (shallower depth, per-layer-conditioned
   oracle rather than a propagated closure, or a different input law) or it
   was wrong. Every downstream ceiling built on it (including the old plan's
   4.7e-8 k3/k4 arm) inherits this doubt and must not be cited as a forecast.
3. **Slot-2 hierarchy collapses to: fold3-n100, then the Kerdock lottery.**
   The closure exits the submission portfolio entirely.
4. **The Algorithmic-Contribution paper gains its sharpest figure**: the
   certified-exact Gaussian closure quantifies the non-Gaussianity wall —
   depth-32 closure bias (9.6e-5 full-cov, 7.2e-4 diagonal, measured this
   session with certified machinery) vs the sampling family's 3.1e-7 at
   matched budget. Exactness of the moment recurrence is worth ~7.5x over
   diagonal, and the remaining gap to samplers is higher-order structure the
   Gaussian family cannot see. That is a real, honest, novel measurement.

## Evidence classes
Numerical certificate: the MSE table (observed, fresh this session).
Resource observation: wall times (observed; certified per-pair implementation,
not a vectorized bound). Reported-level carry: the 8.30e9 billed-FLOPs figure
(M179 G4) — unused in the verdict since K1 fires on MSE alone.
