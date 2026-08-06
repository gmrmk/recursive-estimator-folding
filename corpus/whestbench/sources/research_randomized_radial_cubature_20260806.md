# Research note: randomized radial cubature mutation

Date: 2026-08-06

This note motivates a causal descendant of the failed full-covariance `2n`
sigma rule. It does not claim that the descendant passes WHestBench gates.

## Primary sources

1. Alan Genz and John Monahan, *Stochastic Integration Rules for Infinite
   Regions*, SIAM Journal on Scientific Computing, DOI:
   https://doi.org/10.1137/S1064827595286803

   Genz and Monahan derive stochastic rules for normal-weighted integrals by
   combining radial rules with random orthogonal transformations of spherical
   rules. This directly supports testing Haar-rotated spherical frames rather
   than assuming the covariance square-root axes are harmless.

2. Simo Särkkä, Jouni Hartikainen, Lennart Svensson, and Fredrik Sandblom,
   *On the relation between Gaussian process quadratures and sigma-point
   methods*, https://arxiv.org/abs/1504.05994

   The paper relates sigma-point methods, spherical cubature, multivariate
   Gauss--Hermite integration, average-error criteria, and quasi-random point
   selection. It supports treating node orientation and radial order as
   independent cubature design choices.

3. Syed Safwan Khalid, Naveed Ur Rehman, and Shafayat Abrar, *Higher-Degree
   Stochastic Integration Filtering*, https://arxiv.org/abs/1608.00337

   The paper develops higher-degree stochastic spherical--radial integration
   rules. It motivates increasing radial exactness only after the randomized
   angular mutation is isolated by an ablation.

## Proposed factorial mutation

For `X ~ N(0,I_n)`, write `X=R U`, with `U` uniform on the sphere and
`R~chi_n`. The failed rule used one fixed radius `sqrt(n)` and one fixed frame:

```text
mu +/- sqrt(n) V^(1/2) e_j.
```

The proposed audit freezes the q=3 recursion and tests a 2x2 factorial:

```text
angular: fixed covariance-square-root axes vs seeded Haar frame Q
radial:  one radius sqrt(n) vs two-node positive chi_n quadrature
```

Every orthogonal frame exactly preserves degree-two angular moments. A Haar
frame removes deterministic axis alias in distribution. A two-node Gaussian
quadrature for the chi radial law matches moments through degree three,
including `E[R]` and `E[R^2]`; the latter preserves covariance while the former
is exact for zero-mean positively homogeneous ReLU means after angular
integration.

The four-cell ablation distinguishes angular repair from radial repair. The
combined rule has `4n` antipodal/radial points per component and is expected to
remain below 80B under the existing static arithmetic model, but this must be
recomputed before any accuracy result is read.

## Required guards

- Haar seeds are fixed before results and independent of truth.
- Report expectation across fixed independent rotations and between-rotation
  dispersion; do not choose the best rotation.
- Covariance, radial moments, permutation covariance in distribution, and
  positive-gauge covariance in distribution are proved/tested.
- Use frozen synthetic n64 references only; no WHest scorer/data until the
  `ratio<=0.8`, `wins>=6/8`, and `<80B` gates pass.
