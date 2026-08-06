# Full-covariance spherical--radial sigma closure

## Decision

**Hard kill on the frozen fresh-width accuracy and win gates.**

This branch addresses two diagnosed failure modes of the selected-factor
closure at once without touching WHest:

- no selected-rank collapse: every component uses the unique symmetric square
  root of its entire propagated covariance;
- no `q^r` tensor growth: each component creates exactly `2n` spherical--radial
  sigma points.

The retained `q=3` equal-mass projection compressor is unchanged. Before
results, survival required aggregate MSE ratio `<=0.8` versus the corrected
full-covariance comparator, at least 6/8 case wins, scale and permutation tests,
and a conservative width-256/depth-32 billed-arithmetic bound below `80B`.

The candidate's aggregate ratio is **8.8716** with **1/8** wins. Accuracy is
11.09 times the maximum allowed ratio, so the branch is rejected despite
passing covariance, invariance, and cost premises.

## Operator

For each retained component with propagated law `N(mu,V)`, compute the unique
symmetric PSD square root

```text
L = V^(1/2)
```

and use the equally weighted points

```text
mu + sqrt(n) L e_j,  mu - sqrt(n) L e_j,  j=1,...,n.
```

Their mean is `mu` and their covariance is the entire PSD-projected `V`. ReLU
is evaluated pointwise, so the children have zero residual covariance. At
steady state, three parents create `6n` children, which the existing
deterministic compressor reduces to at most three Gaussian components.

The PSD check rejects eigenvalues below `-1e-10` relative to spectral scale;
only eigenvalues within `64*eps` relative to zero are projected away. This
avoids an absolute threshold that would break positive-scale equivariance.

## Frozen n=64 audit

The corrected comparator uses the converged 256-node Gauss--Legendre
bivariate-normal integral. Each truth reference is the original 65,536 fixed
Philox antithetic base samples. All stored comparator MSEs reproduce exactly.

| L | seed | corrected fullcov MSE | sigma MSE | ratio | win |
|---:|---:|---:|---:|---:|:---:|
| 16 | 18560 | 3.6884e-4 | 6.4320e-3 | 17.439 | no |
| 16 | 18561 | 8.2110e-4 | 1.5077e-2 | 18.362 | no |
| 16 | 18562 | 1.4425e-3 | 9.0639e-4 | 0.628 | yes |
| 16 | 18563 | 2.0847e-4 | 1.9072e-3 | 9.149 | no |
| 32 | 18720 | 3.1834e-4 | 1.7954e-2 | 56.398 | no |
| 32 | 18721 | 2.8092e-3 | 1.3256e-2 | 4.719 | no |
| 32 | 18722 | 3.0041e-4 | 2.1732e-3 | 7.234 | no |
| 32 | 18723 | 5.9922e-4 | 3.2254e-3 | 5.383 | no |

Summed baseline MSE is `0.00686808`; summed candidate MSE is `0.0609308`.

## Structural audit

On the frozen `n=64,L=16,seed=18560` member:

- sigma-point covariance relative error: `3.01e-15`;
- PSD projection relative error: below `3e-15` throughout the trace;
- every steady layer creates 384 children and recompresses to `q=3`;
- scaling the first weight matrix by `0.375` scales the final estimate by the
  same factor within the declared tolerance;
- distinct neuron permutations at every layer commute with the estimate within
  the declared tolerance.

Five unit tests cover covariance recovery, scale, permutation, deterministic
point children, and the resource bound.

## Conservative cost bound

At `n=256,L=32,q=3`, steady child count is 1,536.

| charged term | arithmetic |
|---|---:|
| covariance sandwiches | 6.442B |
| three symmetric square roots per layer | 14.496B |
| compressor eigensolver | 4.832B |
| global and within-bin child moment passes | 12.885B |
| sigma-point formation | 0.050B |
| subtotal | 38.705B |
| with 25% contingency | **48.381B** |

The cost gate passes with substantial margin. This is a conservative
shape-billed arithmetic bound, not a completed FlopScope port; the failed
accuracy gate makes such a port unnecessary.

## Failure interpretation

Matching the entire covariance does not make a `2n` rule adequate after ReLU.
The spherical--radial rule is a low-degree moment rule whose axes are fixed by
the covariance square root. Deep ReLU means depend on how mass crosses many
coordinate gate hyperplanes, information that is not determined by mean and
covariance. The result therefore removes selected-rank truncation but replaces
it with severe angular/gate aliasing. The unchanged three-component compressor
can further discard distinctions among the 384 children, but the current test
does not separate those two losses.

Do not tune radii, rotate the axes from observed errors, or increase node count
within this killed child. A causally valid descendant would need a new operator
that targets gate-crossing structure with a known unbiased/randomized symmetry,
and would require its own predeclared test.

## Files

- `latent_full_sigma.py`: explicit sigma closure and cost bound.
- `run_fresh_n64.py` / `fresh_n64_results.json`: frozen eight-case evidence.
- `test_full_sigma.py`: structural tests.
- `structural_audit.py` / `structural_audit.json`: machine-readable
  covariance, invariance, growth, and cost evidence.
- `finalize_decision.py` / `decision.json`: conjunction gate and hashes.
