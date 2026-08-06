# Weight-identified latent-factor Gaussian-mixture closure

## Decision

**Survives the synthetic small-width premise; not promoted and not ready for an
official screen.**

The packet's hard-kill conditions were applied before and after implementation:

- It does **not** collapse to the killed scalar scale mixture.
- Its component construction and reduction are deterministic functions of the
  weights and current explicit mixture state; it does **not** infer a generic
  mixture or copula from insufficient moments.
- Component growth is explicitly capped and its true dense cost remains
  `O(L q n^3)` for fixed `q,r`, not exponential in depth.
- On seven deterministic synthetic networks with `n<=16`, the strongest
  `q=3,r=2` closure reduced summed MSE against exact-forward references by
  **95.26% relative to full-covariance Gaussian reclosure** and won 6/7 cases.

This is premise evidence only. The closure is deliberately biased, the sample
contains only seven synthetic networks, and the exact eigensolver/recompression
path has not been ported to or billed under FlopScope. No dataset target,
official scorer, holdout, API, or killed-candidate hybrid was used.

## The fully specified closure

At layer `l`, retain at most `q` Gaussian components

```text
{pi_a, mu_a, Sigma_a},  a=1,...,q.
```

For each component, apply the known weight matrix exactly to its first two
moments:

```text
a_a = W_l^T mu_a,
V_a = W_l^T Sigma_a W_l.
```

Let the leading `r` simple eigenpairs of `V_a` be `(lambda_j,u_j)` and set

```text
B_a = [sqrt(lambda_1)u_1,...,sqrt(lambda_r)u_r],
D_a = diag(V_a - B_a B_a^T).
```

Use `q` standard-Normal Gauss--Hermite nodes per factor. For tensor node `z_k`,
the conditional surrogate is

```text
Z_l | (a,k) ~ N(a_a + B_a z_k, diag(D_a)).
```

The coordinatewise ReLU mean and variance are then analytic. Each parent
therefore creates `q^r` diagonal-covariance children. Starting at one input
Gaussian produces `q^r` children in layer 1; subsequent layers produce at most

```text
M = q * q^r = q^(r+1)
```

children before recompression.

Recompression is not an unspecified mixture fit. Compute the explicit child
mixture's mean/covariance, take its leading simple covariance direction, sort
child means by their projection on that direction, partition the distribution
into `q` exactly equal-mass quantile bins (splitting a child's mass at a bin
boundary if necessary), and moment-match within each bin. Thus all retained
component parameters are deterministic consequences of the weights, Gaussian
quadrature, and the previous state.

Approximations remain substantial and explicit:

1. covariance outside the leading factors is replaced by its diagonal;
2. the Gaussian factors use finite quadrature;
3. `q^(r+1)` children are reduced to `q` components;
4. each reduced bin is Gaussianized before the next layer.

The bias class is therefore **deliberately biased assumed-density closure**.

## Exact permutation and gauge invariance

Let arbitrary neuron permutations at adjacent layers be `P_(l-1),P_l`, with

```text
W'_l = P_(l-1)^T W_l P_l.
```

If a component transforms as

```text
mu'_a = P_l^T mu_a,
Sigma'_a = P_l^T Sigma_a P_l,
```

then its next preactivation covariance has the same form. For a simple
eigenvalue, its eigenvector transforms as `P_l^T u_j` up to sign. The tensor
Gauss--Hermite node set is invariant under every selected eigenvector sign
flip, so sign changes only permute children. Coordinatewise ReLU commutes with
permutation.

The compressor's leading direction likewise transforms equivariantly up to
sign. A sign flip reverses the equal-mass quantile bins and therefore leaves
the unordered reduced component set unchanged. Component label permutations
are irrelevant because all mixture operations are set sums followed by the
same score order.

Repeated leading eigenvalues have an `O(r)` basis gauge that no finite tensor
grid can respect for arbitrary ReLU integrands. The implementation therefore
does not select an index-based basis: if any required eigengap is at the
declared tolerance boundary, it uses a rank-zero moment-matched fallback. It
similarly falls back on score ties. These fallbacks sacrifice the mechanism at
the singular boundary but preserve the exact mathematical equivariance rule.

Tests cover independent eigenvector sign flips and arbitrary, distinct
permutations at every hidden layer. The structural audit's width-16/depth-16
test has maximum permutation discrepancy `2.22e-15`.

## Why the previous identification kills do not apply

### Not a scalar scale mixture

The latent components shift along weight-induced covariance directions; they
are not `N(0,s_a^2 I)`. After the first `q=3,r=2` layer in the audited case:

- the three component means have affine rank 2;
- best scalar-fit residuals between component means range 0.407--0.814;
- best scalar-fit residuals between component covariances range 0.522--0.905.

All 16 audited layers used all nine rank-two tensor nodes per parent and
recompressed 27 children to three components. The branch did not silently
collapse to one Gaussian or a global radial split.

### Not the underidentified generic GMM

The prior GMM kill correctly showed that mean, full covariance, and marginal
moments do not identify arbitrary component means and covariances. This closure
does not solve that inverse problem. It imposes a particular weight-equivariant
ansatz whose components are constructed forward from known weights. That makes
the estimator identified as an algorithm; it does **not** make its latent
components identifiable as the true hidden law.

### Not the underidentified Gaussian copula

No marginal CDF, latent copula correlation, PSD repair, or dense third/fourth
cumulant tensor is fitted. Dependence is carried by an explicit finite mixture
and up to two known covariance factors. The generic-copula nonuniqueness result
therefore does not apply, although the low-rank mixture remains only an
approximation to the true dependence.

### Not ordinary full-covariance reclosure

If the children were globally moment-matched to one Gaussian at every layer,
the construction would collapse to a low-rank approximation of the killed
Gaussian reclosure. Here, `q>=3` components are separately linearly propagated
and passed through the next nonlinear ReLU before recompression. Since the
conditional ReLU mean is nonlinear in component mean/variance, the next result
is not a function of global mean and covariance alone.

## True `q,r,L,n` cost

In this implementation `q` is both the retained mixture cap and the number of
one-dimensional Gauss--Hermite nodes. Let `K=q^r`; after the first layer the
steady child count is `M=qK=q^(r+1)`.

| operation per layer | time | reason |
|---|---:|---|
| propagate `q` full component covariances | `Theta(q n^3)` | dense `W^T Sigma_a W` |
| identify component factors | `Theta(q n^3)` with dense `eigh` | this cost must not be hidden; partial iteration changes constants, not the stated exact reference |
| form and rectify children | `Theta(q^(r+1) n r)` | factor shifts and univariate Gaussian formulas |
| child/global/bin moment covariance | `Theta(q^(r+1) n^2)` | outer products of child means |
| compressor leading direction | `Theta(n^3)` with dense `eigh` | one mixture covariance decomposition |

Hence

```text
T = Theta(L[(q+1)n^3 + q^(r+1)n^2 + q^(r+1)nr]).
```

For fixed `q,r` this is `Theta(L q n^3)`, not exponential in `L`. The optimized
memory bound is

```text
Theta(q n^2 + q^(r+1)n),
```

because child residual covariances are diagonal. The clarity-first NumPy
reference stores those diagonals as dense matrices, so its actual peak storage
is `Theta(q^(r+1)n^2)`; that is an implementation artifact and is disclosed.

At `n=256,L=32`:

| configuration | steady children | covariance-sandwich floor (`4qLn^3`) | rough dense-eigen-inclusive arithmetic* |
|---|---:|---:|---:|
| `q3,r1` | 9 | 6.44B | about 26B |
| `q3,r2` | 27 | 6.44B | about 26.2B |
| `q5,r1` | 25 | 10.74B | about 40B |

`*` The illustration charges roughly `9n^3` for each of `q+1` dense symmetric
eigendecompositions per layer and includes child outer-product work. It is not
an official FlopScope measurement. A legal counted eigensolver and residual
runtime audit are mandatory before any width-256 screen.

Thus mixture growth does not itself violate the 272B ceiling, but the branch is
not package-ready merely because its asymptotics fit.

## Small-width premise

Gate declared in code before the run: a candidate must have summed MSE no more
than 80% of fullcov over the fixed cases. Synthetic weights are iid
`N(0,2/n)`, matching the observed He scale. References are:

- deterministic tensor Gauss--Hermite orders 17 versus 15 at `n=4`;
- 1,048,576 fixed Philox base samples (2,097,152 exact antithetic forward
  paths) at `n=8,16`, with reported Monte Carlo standard errors.

| reference | n | L | seed | fullcov MSE | q3,r2 MSE | ratio |
|---|---:|---:|---:|---:|---:|---:|
| tensor GH17 | 4 | 8 | 101 | 1.7839e-3 | 5.2308e-5 | 0.0293 |
| tensor GH17 | 4 | 16 | 202 | 4.7685e-2 | 1.0585e-4 | 0.00222 |
| tensor GH17 | 4 | 32 | 303 | 1.1353e-10 | 6.0368e-13 | 0.00532 |
| exact-forward MC | 8 | 16 | 401 | 4.7002e-3 | 1.6071e-5 | 0.00342 |
| exact-forward MC | 8 | 32 | 402 | 2.4358e-4 | 7.9794e-5 | 0.3276 |
| exact-forward MC | 16 | 16 | 501 | 2.3931e-3 | 2.4235e-3 | 1.0127 |
| exact-forward MC | 16 | 32 | 502 | 1.8597e-4 | 2.2814e-5 | 0.1227 |

Aggregate results:

| candidate | summed-MSE ratio to fullcov | case wins | gate |
|---|---:|---:|---|
| q3,r1 | 0.1284 | 5/7 | pass, but dominated by q3,r2 |
| q5,r1 | 0.1320 | 5/7 | kill: higher cost and slightly worse than q3,r1 |
| q3,r2 | **0.04738** | **6/7** | **survive premise** |

The one q3,r2 loss is real and disclosed (`n=16,L=16`, 1.27% worse). The
strong aggregate is also influenced by a large fullcov failure on the
`n=4,L=16` network. This is why the result is a survivor, not a promotion.

## Next gate if authorized

Only the `q=3,r=2` mechanism merits continuation. Before any official-score or
large public-target evaluation, it needs:

1. a FlopScope-compatible partial eigensolver with every operation billed;
2. diagonal child storage and a deterministic residual-time profile;
3. a target-free width-256 numerical stability/cost smoke;
4. then a predeclared matched public development premise, still without any
   locked split.

Do not hybridize this survivor with a killed branch, and do not infer a
competition win from synthetic small-width evidence.

## Files

- `latent_factor_closure.py`: explicit closure and fullcov comparator.
- `run_premise.py`: fixed synthetic gate and exact-forward references.
- `premise_results.json`: machine-readable accuracy results.
- `structural_audit.py` / `structural_audit.json`: scale-collapse, component
  growth, and permutation diagnostics.
- `test_invariance.py`: deterministic sign-gauge and permutation guards.
