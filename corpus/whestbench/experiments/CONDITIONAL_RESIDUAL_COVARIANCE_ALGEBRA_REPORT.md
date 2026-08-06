# Conditional residual covariance algebra

## Verdict

Promote the fixed covariance-generated algebra as a successful representation
premise. Do not promote coefficient formation or recurrence.

Using only twelve predeclared matrix directions per conditional cell—identity,
`diag(d)`, and the ten symmetric products of four covariance factors—rank 4
achieves:

| metric | covariance algebra | unrestricted rank-4 ceiling |
|---|---:|---:|
| standardized next-row k3 fidelity | 0.983464 | 0.993974 |
| standardized next-row k4 fidelity | 0.969492 | 0.984388 |
| combined standardized fidelity | 0.972741 | 0.986618 |
| combined correction fidelity | 0.988152 | 0.995497 |
| material signs | 97/97 | 97/97 |

Every frozen 0.80 representation/sign gate passes. The algebra retains most of
the successful unrestricted spectrum while eliminating arbitrary dense factor
directions. The remaining links are stable coefficient formation and a ReLU
recurrence. No WHest data, scorer, holdout, API, or post-metric basis change was
used.

## Frozen algebra

For each of the same 16 principal-score cells, inputs are only the existing
conditional mean `m`, diagonal covariance residual `d`, and four covariance
factors `U_0,...,U_3`.

The ordered symmetric matrix generators are exactly:

```text
I
diag(d)
U_a U_a^T, a=0..3
(U_a U_b^T + U_b U_a^T)/sqrt(2), a<b.
```

They span at most twelve Frobenius-orthonormal matrix directions. The k3 linear
space is the ordered span of

```text
1, m, d, U_0, U_1, U_2, U_3,
```

with dimension at most seven.

For exact conditional residual unfoldings, the oracle projects only the small
cores

```text
C3 = Q_L^T K3 Q_M,        at most 7 x 12
C4 = Q_M^T K4 Q_M,        at most 12 x 12,
```

then takes rank 1, 2, or 4 inside them. Rank 4 was frozen as the gate. This does
not delete repeated or all-distinct tensor sectors: each algebra matrix is
dense, and its directional polynomial reconstructs all index patterns.

## Rank ladder and energy geometry

| rank | total k3 | total k4 | combined | correction | signs |
|---:|---:|---:|---:|---:|---:|
| 1 | 0.9162 | 0.9123 | 0.9132 | 0.9538 | 96/97 |
| 2 | 0.9604 | 0.9437 | 0.9476 | 0.9758 | 97/97 |
| 4 | 0.9835 | 0.9695 | 0.9727 | 0.9882 | 97/97 |

The matrix/linear subspaces contain only `0.7867` of exact k3 unfolding energy
and `0.6864` of k4 energy. Rank 4 retains `0.7794` and `0.6685`, respectively.
Despite that modest Frobenius capture, actual final directional contractions
are `0.9835/0.9695`. The metric-relevant geometry is substantially smaller
than the raw tensor geometry.

For the conditional residual terms alone, rank-4 next-row fidelity is `0.9240`
for k3 and `0.7970` for k4. The latter is just below 0.80, but the predeclared
gate concerns the actual total next-row cumulants after exact conditional
mean/covariance coupling; those reach `0.9835/0.9695/0.9727`. This separation
is precisely why the total-cumulance identity must remain part of the method.

### Per-case rank-4 totals

| n | L | k3 | k4 |
|---:|---:|---:|---:|
| 8 | 2 | 0.9823 | 0.9480 |
| 8 | 3 | 0.9805 | 0.9659 |
| 8 | 4 | 0.9999 | 0.9997 |
| 12 | 2 | 0.9813 | 0.9656 |
| 12 | 3 | 0.9937 | 0.9754 |
| 12 | 4 | 0.9984 | 0.9826 |
| 16 | 2 | 0.8917 | 0.8337 |
| 16 | 3 | 0.9870 | 0.9827 |
| 16 | 4 | 0.9942 | 0.9948 |

Even the weakest case remains above the gate.

## Convergence

On the three doubled-sample depth-4 cases, rank 4 reaches:

| metric | doubled result |
|---|---:|
| k3 fidelity | 0.997126 |
| k4 fidelity | 0.995103 |
| combined fidelity | 0.995556 |
| correction fidelity | 0.999002 |
| material signs | 30/30 |
| projected k3/k4 subspace energy | 0.9680 / 0.9005 |
| conditional k3/k4 row fidelity | 0.9754 / 0.9201 |

The dramatic depth-4 energy alignment suggests the covariance algebra becomes
more exact as deep conditional distributions collapse onto their dominant
response modes. This is a hypothesis from the frozen diagnostics, not an L=32
extrapolation.

Exact bank reproduction stays within `1.27e-13` standardized k3, `3.20e-12`
standardized k4, and `7.04e-15` correction error. Coordinate permutation scaled
error is `1.01e-15`; preserved exact tensor symmetry errors remain below
`2.77e-16`.

## Can diagonal/iijj probes identify the coefficients?

The answer is: locally in the larger small-n cases, but not uniformly or
stably enough to claim an algorithm.

For k3, all probes `k3[i,i,j]` define a linear map from the `7x12` core. For
k4, all `k4[i,i,j,j]` define a map from the symmetric `12x12` core. Full-core
design ranks saturate at 64 of 84 for k3 and 58 of 78 for k4 in generic n>=12
cases. Those deficiencies largely reflect core directions that vanish after
full polynomial symmetrization, so full-core rank is too pessimistic.

The relevant rank-4 tangent dimensions are:

```text
k3: 4 * (7 + 12 - 4) = 60
k4: 12*4 - 4*3/2 = 42.
```

- Every n=12 and n=16 cell has full local tangent rank for both k3 and k4.
- At n=8, k4 has only 36 distinct iijj probes for 42 tangent directions and is
  necessarily non-identifiable; some highly collapsed cells also lose k3 rank.
- Even when locally full-rank, tangent condition numbers can exceed `1e10`.
  The n=16 cases are milder, with observed maxima around `4.16e4` for k3 and
  `4.47e3` for k4, but this is not an n=256 guarantee.

Therefore repeated probes could in principle determine local rank-4
coefficients in generic sufficiently wide cells. They do not yet provide a
stable formation method. The probes themselves are not analytically available
from the current layer state, and the earlier pair-repeated failure showed that
using them by index deletion is invalid. Here they would only identify a dense
algebraic reconstruction, which is a different and still-open use.

Randomized or optimized directional probe designs may condition the small core
better than coordinate iijj probes, but their exact weights-only evaluation is
also unresolved.

## n=256 state and arithmetic

Conservatively materializing twelve algebra matrices in every cell plus rank-4
small-core coefficients and conditional covariance state costs:

```text
6,342,736 float64 values = 50,741,888 bytes.
```

The matrices can instead be generated from `d,U`, reducing retained state, but
the conservative declared scaling is `O(B r_cov^2 n^2)`.

Contracting twelve matrix directions and seven linear directions with all
next-layer rows costs

```text
B*12*(2n^3-n^2) + B*7*(2n^2-n)
= 6,444,519,424 billed-like terms at n=256,
```

or `O(B r_cov^2 n^3)` terminal arithmetic. The largest small-n oracle run used
140.32 MiB peak working set and formed no dense n4 tensor.

These figures cover representation and terminal contraction only. The current
oracle obtains `C3,C4` by projecting exact empirical tensors. It supplies no
cheap probe values, regularized coefficient solve, or multi-layer update.

## Next rung

The covariance algebra is no longer the uncertain link. The next mutation is
matrix-free coefficient formation:

1. form only the 7x12 and 12x12 cores through cumulant-operator products or
   response identities, never the full pair matrix;
2. use regularized, condition-aware directional probes rather than assuming
   coordinate iijj stability;
3. cross-fit coefficients on small-n samples to detect spectral overfitting;
4. then derive or falsify the ReLU update for the small cores.

If exact probe formation remains weight-analyticly inaccessible, preserve this
algebra and return to matrix-free response-vector/Price-Hermite formation. Do
not enlarge the basis: rank 1 and rank 4 already show ample representational
headroom.

Artifacts: `PREDECLARED_GATE.md`, `covariance_algebra.py`, `run_oracle.py`,
`oracle_results.json`, `convergence_audit.json`, `resource_audit.json`,
`structural_audit.json`, `decision.json`, and tests in this directory.
