# M208 predeclaration -- physically normalized rank-one cumulant control

Date: 2026-08-09. Status: `PREDECLARED_RESPONSE_FREE`.

This file is frozen before implementation. M208 may use generated weights and
independent small-width algebra oracles only. It may not read a contest model,
truth, scorer, leaderboard, submission, private instance, or champion outcome.

## Campaign invariants

- Official objective: minimize private-suite mean
  `MSE * max(0.1, C / 272e9)` with zero nonfinite or over-budget failures.
- Evaluator: `whest.exe` SHA-256
  `888a44d9c886df88cf8933398c154e113f530f3dc2705282170820a101dd674a`.
- Frozen deployable champion: guarded Kerdock v3.1 tar SHA-256
  `8382e269c9b32e0935492734ddf8182560120f7e9331621aa18839d5d1f4ea06`.
- Exact-control research envelope: `100e9` billed-equivalent operations. The
  strict no-replacement partial is `98.013128528e9`, leaving
  `1.986871472e9` for every still-uncredited term.
- Bias class if the later residual path is completed: exact deterministic
  control plus an unbiased full-support Horvitz--Hansen residual. M208 itself
  proves only a response-free deterministic source identity.
- Randomness: generated premise cells use fixed Philox seeds. Any future
  variance screen must use whole fresh generated networks and a separately
  frozen confirmation split.

## One changed mechanism

M205 assigns physical owners to the target but retains M204's artificial
complete-table control

```text
c_old[i,j,k] = kappa * u_i^2 u_j u_k,  kappa = -2,
```

even on collision rows. That extension is not the physical owner table of a
rank-one fourth cumulant and its compiler needs
`B = W^T diag(u^2) W`, which M206 proves cannot receive M151/M179 reuse credit.

M208 changes only the control's collision normalization. Let

```text
K_abcd(control) = kappa * u_a u_b u_c u_d,  kappa = -2.
```

Use M167's physical owner multiplicities:

```text
c[i,i,i] = kappa * u_i^4 / 6
c[i,i,j] = c[i,j,i] = kappa * u_i^3 u_j / 3       (i != j)
c[i,j,j] = kappa * u_i^2 u_j^2 / 2                (i != j)
c[i,j,k] = kappa * u_i^2 u_j u_k                  (i,j,k distinct).
```

Thus M208 is coefficient-identical to M204/M205 on every distinct
`[2,1,1]` row and changes only the failed collision boundary. The complete
physical target `T` is split exactly as `T = c + (T-c)`; no collision target
is zeroed or relabelled.

## Predicted exact compiler

For `p = W^T u`, multilinearity of the physical rank-one cumulant predicts

```text
C_aaaa[a]  = kappa * p_a^4
C_aaab[a,b]= kappa * p_a^3 p_b
C_aabb[a,b]= kappa * p_a^2 p_b^2.
```

The compiler therefore needs one float64 row-by-square projection per source
layer and `O(n^2)` pointwise/outer-product work. It must not form M204's
`B`, `rho`, `(W^2)^T(W^2)`, a dense rank-three table, or a cubic label loop.

At `n=256`, 31 layers, FlopScope's float64 row-matmul bill is frozen as

```text
31 * 2 * (2*n^2-n) = 8,110,592 operations.
```

The implementation must separately count every square-output fill,
pointwise power, copy, allocation, and residual second. No source/compiler
cost credit is claimed before a native trace.

## Response-free premise gates

1. At widths `3..7`, compare the p-only compiler against an independent
   complete-table enumeration using the physical owner multiplicities.
   Maximum absolute source-slot error must be at most `5e-10`.
2. Verify the M208 and M205/M204 controls agree exactly on every pairwise-
   distinct coefficient and differ on a nonzero collision witness.
3. Verify complete conservation against arbitrary generated physical `K4`,
   directed `K31`, symmetric `K22`, and singleton-symmetric distinct tables:
   `source(T) = source(c) + source(T-c)` to `8e-10`.
4. Verify hidden-label permutation and positive-ReLU-gauge covariance.
5. A hostile operation test must fail if the compiler calls or constructs a
   dense Gram, `rho`, cubic coefficient table, or exhaustive triple loop.
6. Static accounting must show the row projection plus declared pointwise
   operations is below the strict `1.986871472e9` remainder. This is only a
   necessary component gate; M198, the physical residual coefficient
   provider, terminal response, copies, allocations, and wall remain unpaid.

## Kill and preservation rules

Kill M208 if any multiplicity, source parity, distinct-row identity,
conservation, symmetry, gauge, forbidden-operation, or static-cost gate fails.
Do not repair it by tuning `u`, `kappa`, owner fractions, or tolerances after
the run. Preserve a passing p-only identity as a component only. It may open a
separate native-cost trace, then a separately predeclared generated source-
variance screen; it cannot replace Kerdock v3.1 or claim a winning score here.
