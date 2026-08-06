# Predeclared gate: canonical latent-factor copula

Written on 2026-08-06 before this mutation was evaluated against any frozen
synthetic activation-path oracle.

## Frozen parent, objective, and firewall

- Parent: `latent_copula_resummation`, with its exact rectified-Gaussian
  conditional moments and law-of-total-cumulance contraction.
- Preserve exactly the six cases `(n,L,seed) = (8,2,83802), (8,4,83804),
  (12,2,84202), (12,4,84204), (16,2,84602), (16,4,84604)`, 32,768 Philox
  base inputs plus negatives, 16 principal-score cells, rank four, copied
  response state, next-row weights, standardization, transport, and metrics.
- Preserve the 49-node and 201-node rank-four Gaussian Smolyak rules, the
  rectified-Gaussian response prior, clipping, and every noncanonical
  arithmetic step.  No fitted coefficient, oracle-selected sign, case-specific
  node, or retuning is allowed.
- Formation reads only copied `(p,m,D,U,W)`.  Activation paths are accuracy
  oracle data and cross the firewall only after this file, implementation, and
  tests are frozen.  Read no WHest row, target, scorer, package, submission,
  API, official holdout, or private instance.
- Bias class: deterministic approximation to the same fixed
  rectified-Gaussian copula prior.  Canonicalization changes only numerical
  integration coordinates; it adds no missing higher-order prior state.

## Exactly one changed mechanism

Before applying either unchanged sparse grid, replace each inferred factor
`B` by a deterministic representative of its right-orthogonal equivalence
class.  Compute `S=B^T B`, diagonalize it, order nonzero eigenspaces by
decreasing eigenvalue, fix simple-eigenvalue signs with permutation-equivariant
coordinate seeds, and resolve exactly repeated eigenspaces using their left
projectors and the same fixed seed sequence.  Null columns are appended last.

The primary seeds are target-free coordinate functions that commute with a
row permutation: `1`, powers of `diag(BB^T)`, row sums of `BB^T`, and products
of those quantities.  A deterministic coordinate-pivot fallback is permitted
only for a mathematically unresolved symmetric degeneracy and its count must
be reported.  The frozen six cases must use zero fallbacks.

For generic factors this produces `C(BQ)=C(B)` for every orthogonal `Q` up to
roundoff, while preserving `CC^T=BB^T`.  Apply the same 49-node candidate and
201-node reference to `C`; change nothing else.

## Frozen gates

1. **Factor identity:** on fixed full-rank, rank-deficient, and exactly
   degenerate deterministic examples, `CC^T` agrees with `BB^T` within
   `1e-10` relative; repeated calls agree; all values are finite.
2. **Right-orthogonal presentation invariance:** for both 49- and 201-node
   rules, replacing every factor by `BQ` changes isolated `k3/k4` responses by
   at most `1e-10` combined relative squared energy on the six-case aggregate.
   Unit tests also include reflections and exact repeated spectra.
3. **Symmetry/gauge:** coordinate permutation and positive coordinate gauge
   response defects are each `<=1e-10`; no activation-path value can affect
   formation.  Frozen cases require zero projector fallback.
4. **Cubature convergence:** report isolated 49-versus-201 response residual
   energy for `k3`, `k4`, and combined; require combined `<=0.10`.
5. **Direct isolated repair:** 49-node isolated standardized `k3`, `k4`, and
   combined fidelity are each `>=0.80`, material-sign accuracy is `>=0.80`,
   and all three fidelities exceed the q4 parent `(0.732135, 0.655277,
   0.673419)`.
6. **Transport:** total standardized `k3`, `k4`, combined, correction, and
   material-sign accuracy are each `>=0.80`; combined exceeds the frozen zero
   conditional baseline and is no more than `0.01` below q4's `0.931300`.
7. **Validity:** clipping remains exactly `481/1152`, residual variances are
   at least `-1e-12`, node counts remain 49/201, and all deterministic tests
   pass.
8. **Complexity:** charge the parent's 49-node envelope plus, for every target
   cell/layer, one `r x n` by `n x r` Gram contraction, one symmetric `r x r`
   eigendecomposition, factor rotation, projector/seed work, float64 billing,
   and 25% contingency.  Total must remain `<80 B` at
   `n=256,L=32,cells=16,r=4`.  The 201-node reference is diagnostic only.

Passing every gate permits only
`screen_factor_gauge_canonicalized_latent_copula`.  If presentation invariance
and convergence pass but isolated fidelity remains below `0.80`, kill this
literal fixed-prior candidate and preserve canonicalization as a reusable
operator: correcting the grid covariance cannot manufacture the missing
signed higher-order state.
