# M139 positive partial-correlation proposal audit — 2026-08-07

## Decision

**KILLED IMPLEMENTATION / PRESERVE THE EXACTNESS AND SAMPLING COMPONENTS.**

M139 changes only the sampling probability of M133’s exact `[2,1,1]`
Hansen--Hurwitz estimator.  It does not approximate a cumulant in the
estimate.  All generated algebraic gates pass and the static target overhead
is `0.846850560B` protected (< `5B`).  Its frozen development response screen
does not pass: the output-MSE ratio to M133 is `1.04159`, its one-sided
bootstrap upper-90% bound is `1.11467`, and the mean ratio worsens from
`.90363` at width 5 to `1.14815` at width 6.  The disjoint confirmation set
therefore remains unopened.

No contest model, evaluator, score, public/private outcome, leaderboard,
submission, or champion artifact was read or used.

## Mutation contract

M131 establishes that the surviving exact nonzero-mean `[2,1,1]` coefficient
contains a genuine trivariate orthant term.  M139 keeps M131’s independent
conditional one-dimensional boundary oracle as the sampled coefficient.  It
first removes the already-owned tree and pair partitions by forming the exact
connected-minus-tree defect.  The zero-mean quadratic bridge jet is retained
only as a surrogate diagnostic,

```text
q2(i;j,k) = [B_ij B_ik + B_ij B_jk + B_ik B_jk] / (4 pi).
```

It is never subtracted from the returned estimator.

Let `S=abs(B-I)`, `s_i` be the source scale, `r_i=||W_i||`, and use the
gauge-invariant strength

```text
v_i = s_i r_i [1 + .35 alpha_i^2/(1+alpha_i^2)].
```

The base three stars reproduce M133’s quadratic geometry with `v` replacing
the unscaled row norm.  A strict-degree Nyström pivot `p` adds the nonnegative
factor

```text
u_p(j) = S_jp / sqrt(sum_l S_lp),
e_ij   = min(8, (1-B_ij^2+2^-12)^(-1/4)),
c_p(i) = min(8, [2^-12 + 1-min(u_p(i)^2,1)]^(-1/2)).
```

to a positive star `S_ij e_ij u_p(j) * S_ik e_ik u_p(k)`.  This is a bounded
positive separation of the partial-correlation boundary mode; it is not a
claim that the exact trivariate cumulant is low rank.  A fixed 5% uniform law
gives every ordered distinct triple support.

For any mixture component with centre `r` and endpoint tables `L,R`, its
exact normalizer is

```text
Z = sum_r a_r [ (sum_j L_rj)(sum_k R_rk) - sum_j L_rj R_rj ].
```

It can be sampled by choosing `r`, then an endpoint with mass
`L_rj(sum R_r-R_rj)`, then the last distinct endpoint.  Thus both construction
and exact normalizers are `O(R n^2)`, never `O(n^3)`.

## Mathematical gates passed

Eight generated tests pass:

1. rank-zero M139 is bitwise/numerically the M133 three-bank probability law;
2. positive mixture normalization and empirical sampler frequencies;
3. exhaustive HH expectation over all ordered triples;
4. permutation covariance;
5. positive ReLU-gauge covariance, using `s_i ||W_i||`;
6. finite near-singular partial-coordinate behavior and tie-safe pivot fallback;
7. frozen-proposal tangent finite differences without a `qdot` term; and
8. the M131 exact defect equals quadratic diagnostic plus residual, while the
   target-shape incremental worksheet stays under the `5B` cap.

If `q0` is frozen before a directional perturbation, then

```text
d/dtheta E_q0 [ Delta(theta) F / q0 ]
  = E_q0 [ Delta_dot(theta) F / q0 ],
```

so proposal differentiation is neither needed nor allowed.

## Predeclared generated response screen

The comparison uses exact local `[2,1,1]` tables from M131’s paired 32/48
quadrature, then the full M121 one-delay conversion and M125b inhomogeneous
coalescing.  It compares M133 and M139 at the same `K=2n` triples per layer,
three generated layers, and 48 repetitions.  It measures final per-output
squared response error relative to exhaustive exact local-source propagation.

| width | seed | M139 / M133 output MSE |
|---:|---:|---:|
| 5 | 139701 | .8384 |
| 5 | 139702 | .9688 |
| 6 | 139701 | .9967 |
| 6 | 139702 | 1.2996 |

The pooled ratio is `1.04159`; a 4,000-resample one-sided bootstrap has
upper-90% ratio `1.11467`.  The prescribed thresholds were ratio at most `.75`,
upper-90% below `.9`, and no worsening from smallest to largest width.  M139
fails all three.  Confirmation widths 7 and 8, seed 139811, are not run.

## Cost ledger and failure-local salvage

At width 256, 31 layers, `K=512`, rank 4, and 25% protection, the added
positive-table/sampling overhead is `846,850,560` billed scalar/copy-equivalent
operations.  Adding it once, non-overlappingly, to M133's complete protected
`K=512` worksheet (`94.940940240B`) gives `95.787790800B`, below `100B` with
its already included exact-coefficient, five-product, allocation, and 100 ms
wall reserves.  This is a static worksheet, not a native trace.

Preserve the exact sampler, covariance proof, finite partial-coordinate
parameterization, and M131 boundary-oracle integration.  The failed link is
the specific frozen rank-4 latent-envelope law at response level.  Reopening
requires a new observable or mechanism--for example an independently derived
conditional-orthant envelope with a certified low-rank factorization--not a
post-result change to rank, ridge, cap, strength, seed, or split.

The analytic ingredients are consistent with (but not proved by) the primary
truncated-normal treatments of [Manjunath and Wilhelm](https://arxiv.org/abs/1206.5387),
[Galarza et al.](https://arxiv.org/abs/2009.13488), and [Mamis](https://arxiv.org/abs/2202.00189).
