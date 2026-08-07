# Full-covariance Gaussian moment matching premise

## Decision

**Kill this standalone analytic branch.**  It is mathematically validated,
legal, deterministic, and cheap, but its raw accuracy is 38.8 times worse
than the predeclared `1.4e-6` promotion gate.  Its residual also has no stable
alignment with the frozen Monte Carlo parent, so it does not qualify as a
cost-positive control.

No locked index was read.  All scored work used public indices 0--4.

## Method

The implementation follows Kuang and Lin,
"[Exact Gaussian Moment Matching for Residual Networks: a Second-Order
Method](https://arxiv.org/abs/2601.22307v2)," Appendix E.  Starting from
`N(0,I)`, every layer applies

```text
mu_pre    = mu @ W
Sigma_pre = W.T @ Sigma @ W
```

and computes the exact mean and full covariance of an elementwise ReLU under
that Gaussian.  It then re-Gaussianizes and repeats for all 32 layers.  For
`a=mu1/sigma1`, `b=mu2/sigma2`, and correlation `rho`, the implemented
off-diagonal covariance is

```text
mu2*sigma1*Phi2;1(a,b;rho)
+ mu1*sigma2*Phi2;1(b,a;rho)
+ sigma1*sigma2*(1-rho^2)*phi2(a,b;rho)
+ (mu1*mu2+Sigma12)*Phi2(a,b;rho)
- M1*M2.
```

`Phi2` uses the paper's fixed ten-point Gaussian quadrature of Plackett's
identity from correlation zero to `rho`.  All MLP-dependent scored arithmetic
uses FlopScope operations; SciPy appears only in the unscored formula tests.

## Formula and port validation

Seven formula tests pass:

- exact independence;
- exact univariate diagonal moments;
- zero off-diagonal covariance for independent coordinates;
- the known zero-mean arc-cosine ReLU kernel;
- four noncentral correlated moments against an independent conditional
  one-dimensional SciPy integral;
- symmetry; and
- controlled `Phi2` comparisons with SciPy.

On a 175-case grid with `a,b` in `{-3,-1.5,0,1.5,3}` and `rho` in
`{-0.95,-0.8,-0.5,0,0.5,0.8,0.95}`, the fixed rule has mean absolute
`Phi2` error `6.39e-8`, 95th percentile `1.73e-7`, and worst error
`2.88e-6` at `(0,0,-0.95)`.  The deep competition network reaches absolute
correlations near 0.989, so quadrature order was explicitly audited.  Raising
the order from 10 to 96 changes the index-0 final prediction by only
`1.33e-10`; raw MSE remains `7.58652e-5`.  Thus quadrature is not the cause of
the estimator failure.

The scored FlopScope port matches the independent NumPy implementation on
index 0 to maximum absolute final-output difference `1.38e-14`.

## Official 272B subprocess premise

Public indices 0--4, setup seed 0:

| Estimator | Raw MSE | Adjusted | Mean C | Analytical F | Failures |
|---|---:|---:|---:|---:|---:|
| Full covariance | `5.4281535e-5` | `5.4281535e-6` | `16.141B` | `6.189B` | 0/5 |
| Diagonal baseline | `9.3641650e-4` | `9.3641650e-5` | `0.464B` | `0.020B` | 0/5 |
| Frozen parent | `1.5686923e-7` | `1.4123151e-7` | `248.963B` | — | 0/5 |

Full covariance improves raw MSE by about 17.25x over the diagonal analytic
pass, confirming that the off-diagonal calculation matters.  Repeated
Gaussian re-closure nevertheless accumulates substantial bias over 32 ReLU
layers and remains roughly 346x worse raw than the frozen parent.

## Residual-control gate

On the same five networks, the cosine between the parent error and
`fullcov - parent` is `-0.0183`; for `fullcov - diagonal` it is `-0.0460`.
The best in-sample scalar correction improves parent raw MSE by only 0.21%.
Leave-one-network-out fitting reverses that result and worsens MSE by 2.81%.
There is no evidence for a stable, cost-positive control, so the alternative
promotion gate also fails.

## Files

- `fullcov.py`: independent NumPy reference.
- `test_fullcov.py`: SciPy/integration formula tests.
- `estimator.py`: standalone FlopScope implementation.
- `test_estimator.py`: estimator contract tests.
- `estimator_diagonal.py`: frozen diagonal analytic comparator.
- `premise_results.json`: machine-readable ledger.

Nothing here was packaged, submitted, or promoted.

## SHA-256

```text
fullcov.py                 091989fbb2249f792f595020e2a475982fd6c5605e51b83065a1837cf51492f6
estimator.py               4ad95e6cb5af482331a6a849f9d4d8299d0f06f741514b8204a194b7cabee951
estimator_diagonal.py      44275adfe2f016d811d0ac0bbab3e5e8cc2706625d4e9ee796a49518687bd6dd
test_fullcov.py            2000a334c34bccb937119632ed0f321edd9a0ef34ee8dc32fcafc22305d7f72b
test_estimator.py          d451ce23ec11ae40766e11c203e4417af349c00df7c04f5433081cca40fc16a9
premise_results.json       c4a0f37be6a83a56b090e1abcd5f5bfd1d8fff989d1e5d96e5bf3bb581abce15
```
