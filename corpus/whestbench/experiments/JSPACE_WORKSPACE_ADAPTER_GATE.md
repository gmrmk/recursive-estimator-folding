# Predeclared cleanroom gate: JSpace workspace adaptation

Frozen before synthetic network generation or metrics. Source provenance and
the claim boundary are in
[`research_jspace_source_audit_20260806.md`](../../../sources/research_jspace_source_audit_20260806.md).

## Fresh bank

- 12 fresh bias-free He ReLU networks, width/input/output `d=16`, depth `L=8`.
- 384 independent Gaussian states per network; first 288 form a pursuit
  corpus, last 96 are pursuit queries.
- Exact Jacobians are allowed only as synthetic oracle diagnostics.
- Rademacher VJP counts are nested `K in {1,2,4,8,16}` with one fixed cleanroom
  seed stream. No official MLP, truth, scorer, API, or seed selection.

## Frozen workspaces

For standard output-by-input Jacobian `J(x)` compare:

```text
signed workspace:       J_bar = E_x J(x)
mean-J Gram:             G_mean = J_bar^T J_bar
second-moment workspace: G2 = E_x[J(x)^T J(x)].
```

The cancellation ratio is `||J_bar||_F^2 / trace(G2)`. Report PSD spectrum,
effective rank, and top-4/top-8 energy for both Grams.

For Rademacher output probe `z` and VJP `g=J^T z`:

```text
J_hat  = mean outer(z,g)
G2_hat = mean outer(g,g).
```

Compare relative Frobenius error to the exact synthetic workspaces at every K.
The Gram estimate must remain PSD up to `-1e-10` roundoff.

## Frozen pursuit

Use one independently seeded Rademacher output probe per network. Normalize the
288 corpus VJPs and 96 held-out query VJPs. Test 95% norm-squared coverage with
cap 30:

1. upstream-style nonnegative pursuit: maximum positive dot, coefficient
   clipped nonnegative;
2. signed pursuit: maximum absolute dot and signed projection coefficient.

Atoms may be reused, matching the upstream loop. Report achieved coverage,
stalls, terminal residual, and capacity. Never call a stalled `k=30` result a
successful capacity estimate.

## Gate and cost

The second-moment adaptation survives this synthetic rung only if all hold:

- median cancellation ratio `<=0.75` and at least 9/12 networks have ratio
  below `0.75`, showing material information loss in the signed mean;
- at K=16, median Hutchinson Gram relative error `<=0.30`;
- all exact/estimated Grams pass PSD and orthogonal/hidden/output permutation,
  positive-scale, and deterministic tests at `1e-10`;
- signed pursuit has success rate no lower than nonnegative pursuit and either
  reduces median terminal residual by at least 20% or improves successful
  coverage by at least 10 percentage points;
- no nonfinite result.

Cost formulas are reported for exact materialization and VJP workspaces at the
synthetic shape and at `d=256,L=32`. This is a premise test only. Survivors may
enter a later estimator fold only with an explicit link from workspace modes to
mean-estimation error; no source claim supplies that link.
