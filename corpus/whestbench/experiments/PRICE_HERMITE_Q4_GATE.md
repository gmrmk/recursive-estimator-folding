# Predeclared gate: Price--Hermite order-four connected response

Written before any order-four synthetic measurement on 2026-08-06.

## Frozen parent and firewall

- Preserve the six synthetic cases `(n,L,seed)` in the parent
  `price_hermite_higher_moment_response/run_fresh_oracle.py`, including 32,768
  Philox base inputs plus negatives, 16 cells, covariance rank four, next-row
  weights, and evaluation metrics.
- Preserve the rectified-normal marginal inversion, the clipped Price factor
  inversion `B=U/a1`, the exact scalar total-cumulance transport, the
  `39.325794304 B` inherited state envelope, and the `80 B` ceiling.
- Candidate formation may read only `(p,m,D,U,W)`. Activation paths remain
  evaluation-oracle data below the same firewall. No WHest row, target,
  scorer, package, submission, API, or holdout may be read.
- The one changed mechanism is analytic chaos order: enlarge `q<=2` to
  `q<=4`. No response is fitted and no coefficient is selected from oracle
  cumulants.

## Frozen analytic operator

For each conditional coordinate, infer the same unique rectified-normal
`sigma,alpha` from its supplied mean and variance, then use the exact
probabilists'-Hermite coefficients

```text
a1 = sigma Phi(alpha)
aq = sigma phi(alpha) He_{q-2}(-alpha) / q!,  q=2,3,4.
```

Thus the centered response is

```text
X_i-E X_i ~= sum_{q=1}^4 aq_i Hq(Z_i),
R = diag(s^2)+BB'.
```

For `Y=sum_i w_i(X_i-E X_i)`, compute `k3(Y),k4(Y)` by enumerating only
connected loop-free Wick multigraphs on three and four copies of `Y`. A graph
with edge multiplicities `e_ab`, vertex degrees `q_a in {1,...,4}`, has frozen
coefficient

```text
prod_a q_a! / prod_{a<b} e_ab!.
```

Vertex-isomorphic graphs and automorphic diagonal/factor edge choices are
folded with exact integer orbit multiplicities. For each positive edge power,

```text
R_ij^e = F_e(i).F_e(j) + delta_ij [1-||B_i||^(2e)],
```

where `F_e` is the multinomial symmetric-power feature of the rank-four row
`B_i`. This is an exact diagonal-plus-low-rank contraction. It may form small
feature tensors but never an `n^3` or `n^4` cumulant tensor. The already
certified `64/58` cubic/quartic polynomial quotient is the interpretation of
the resulting directional polynomial; no response-free SVD is recharged or
used to manufacture a right-hand side in this rung.

## Frozen gates

1. **Coefficient identity:** `a1..a4` agree with numerical Gaussian Hermite
   projection to relative error `<=1e-9` on deterministic thresholds.
2. **Contraction identity:** the folded low-rank multigraph engine agrees with
   an independently evaluated dense-correlation connected-graph oracle to
   relative error `<=1e-10`; its `q<=2` restriction agrees with the certified
   quadratic-chaos formulas to `<=1e-10`.
3. **Formation and symmetry:** changing activation paths with `(p,m,D,U,W)`
   fixed cannot change the candidate. Coordinate permutations and the same
   positive gauge action as the parent change directional responses by at
   most `1e-10` relative.
4. **Validity:** latent residual variances stay at least `-1e-12`; factor-row
   clipping is reported and held identical to the parent.
5. **Repair:** aggregate isolated-conditional standardized `k3`, `k4`, and
   combined fidelity are each `>=0.80`, with material-sign accuracy `>=0.80`.
   Each fidelity must also exceed the frozen parent q2 value on the identical
   cases (`0.6706853361`, `0.1623414455`, `0.2823353394`).
6. **Transport:** aggregate total standardized `k3`, `k4`, combined, and
   Edgeworth-correction fidelity and material signs are each `>=0.80`, and
   combined fidelity exceeds the zero-conditional-cumulant baseline.
7. **Complexity:** a conservative target count for all orbit-folded feature
   contractions, float64 billed at 2x with 25% contingency, plus inherited
   `39.325794304 B`, is `<80 B`. Outputs must be finite and all tests pass.

If repair passes but complexity fails, preserve the exact q4 response and
localize compression as the failed link. If complexity passes but repair
fails, preserve exact coefficients, graph folding, q2 reduction, and total
cumulance; localize the order-four rectified-Gaussian conditional prior and/or
the frozen clipped factor inversion. Only passing every gate permits
`screen_price_hermite_q4_response`.
