# Goal-aligned scalar gate-boundary split closure

## Decision

**Hard kill on the predeclared material-effect gate.**

The candidate is mathematically sound and directionally consistent: it records
8/8 nominal wins versus corrected full covariance. But its aggregate ratio is
**0.997502**, only a **0.2498%** MSE reduction versus the required 20%. The
material effect is about 80 times too small. Invariance, win count, corrected
baseline reproduction, and conservative cost all pass; the required conjunction
does not.

No WHest data, scorer, holdout, API, killed sigma-rule component, or post-result
parameter tuning was used. The eight fresh n64 cases, 65,536 antithetic base
samples, corrected fullcov comparator, `q=3`, correlation ridge `1e-8`, and
GL64 Gaussian ReLU map were fixed before the run.

## Operator

For a retained Gaussian component `Z ~ N(mu,C)`, define

```text
sigma_i = sqrt(C_ii)
b_i     = sigma_i phi(mu_i / sigma_i)
```

and solve the relative-regularized system `C a = b` in correlation coordinates.
Writing `S=diag(sigma)`, `C=S R S`, and `b=S p`, solve

```text
(R + lambda I) y = p,   lambda = 1e-8 lambda_max(R),
a = S^-1 y.
```

Then standardize

```text
T = a^T (Z-mu) / sqrt(a^T C a).
```

Split `T~N(0,1)` into the three exactly equal-probability bins with boundaries
`(-inf,-0.4307273)`, `[-0.4307273,0.4307273]`, and `(0.4307273,inf)`.
For a bin with truncated moments `(m_t,v_t)`, let

```text
c = C a / sqrt(a^T C a)
E[Z | bin]   = mu + c m_t
Cov[Z | bin] = C + (v_t - 1) c c^T.
```

Each moment-matched conditional Gaussian is passed through the fixed GL64
full-covariance Gaussian ReLU map. The resulting three children per parent are
reduced by the preserved deterministic `q=3` compressor. Steady growth is only
`q^2=9` children.

## Symmetry proof and audit

For a permutation `P`, `S'=P^TSP`, `R'=P^TRP`, and `p'=P^Tp`; therefore
`y'=P^Ty` and `a'=P^Ta`. For a positive diagonal coordinate scaling `D`,
`S'=DS`, while `R'=R` and `p'=p`; therefore

```text
a' = (DS)^-1 y = D^-1 a.
```

Consequently `a'^T C' a' = a^T C a`, `c'=Dc`, and every conditional mean and
covariance transforms as `(D mu, D C D)`. Coordinatewise ReLU commutes with
positive diagonal scaling.

On the frozen `n=64,L=16,seed=18560` case, tests cover:

- exact recombination of the three truncated bins to mean zero and variance one;
- direction permutation covariance;
- direction positive-coordinate-scale covariance;
- split plus Gaussian-ReLU coordinate-scale covariance;
- end-to-end layerwise permutation equivariance;
- an end-to-end internal positive-coordinate-scale gauge with compensating
  adjacent weights;
- cost accounting.

All seven tests pass. Across all eight accuracy cases there are zero numerical
fallbacks, every steady layer creates nine children, and every layer recompresses
to three components.

## Frozen fresh-n64 result

| L | seed | corrected fullcov MSE | gate-split MSE | ratio | win |
|---:|---:|---:|---:|---:|:---:|
| 16 | 18560 | 3.6884e-4 | 3.6847e-4 | 0.999014 | yes |
| 16 | 18561 | 8.2110e-4 | 8.1932e-4 | 0.997832 | yes |
| 16 | 18562 | 1.4425e-3 | 1.4335e-3 | 0.993736 | yes |
| 16 | 18563 | 2.0847e-4 | 2.0637e-4 | 0.989915 | yes |
| 32 | 18720 | 3.1834e-4 | 3.1643e-4 | 0.993993 | yes |
| 32 | 18721 | 2.8092e-3 | 2.8091e-3 | 0.999959 | yes |
| 32 | 18722 | 3.0041e-4 | 2.9966e-4 | 0.997522 | yes |
| 32 | 18723 | 5.9922e-4 | 5.9812e-4 | 0.998164 | yes |

Summed corrected-fullcov MSE is `0.00686808`; candidate MSE is `0.00685092`.
The consistent sign is interesting mechanism evidence, but the frozen gate
correctly prevents a tiny effect from being promoted.

## Conservative n256/L32 cost

| charged term | arithmetic |
|---|---:|
| covariance sandwiches | 6.442B |
| three correlation eigensolves per layer | 14.496B |
| compressor eigensolver | 4.832B |
| nine GL64 Gaussian ReLU maps | 28.991B |
| conditional moments and recompression | 0.151B |
| subtotal | 54.912B |
| with 25% contingency | **68.640B** |

The `<80B` bound passes. It is a shape-billed arithmetic model, not a completed
FlopScope port; the failed accuracy gate makes a port unwarranted.

## Interpretation

The boundary target appears to identify the correct error direction—the 8/8
sign consistency is unlike the failed spherical sigma rule—but one scalar
partition per component changes too little. The split exactly recombines the
first two preactivation moments, so its effect exists only through nonlinear
within-bin reclosure. At width 64, that correction is almost entirely washed
out by three-bin Gaussianization and subsequent deterministic recompression.

This negative result narrows the frontier: a target-aligned direction is not
enough without a substantially richer yet affordable conditional law. Do not
tune the ridge, bin probabilities, or quadrature order against these outcomes.
A descendant would need a predeclared new mechanism that increases observable
gate-conditional information without reviving exponential component growth.

## Files

- `latent_gate_split.py`: operator, relative solve, exact truncated moments,
  and cost model.
- `run_fresh_n64.py` / `fresh_n64_results.json`: frozen accuracy audit.
- `test_gate_split.py`: seven symmetry and structural tests.
- `structural_audit.py` / `structural_audit.json`: proof witnesses, traces,
  fallbacks, and cost.
- `finalize_decision.py` / `decision.json`: conjunction gate and hashes.
