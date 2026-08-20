# M210 predeclaration -- same-level fused recursive Gram

Date: 2026-08-09. Frozen before implementation or resource execution. M210 is
generated-only and response-free; challenge weights, truth, scorer,
leaderboard, submissions, cached responses, and efficacy records are banned.

## Parent failure and one changed mechanism

M209 proved the exact symmetric block-Gram source compiler and its inclusive
`1.226651648B` bill, but its final bound implementation failed the hostile
five-times residual gate in two of five processes by at most `9.13008248M`.
M210 changes only dispatch topology. The recursion depth remains three, the
31-layer staging/binding contract remains unchanged, and every M205 source
formula remains unchanged.

At tree level `q`, reshape the already-staged `U` columns into `2^q`
contiguous blocks and treat `(layer,node)` as batch axes. One batched matmul
computes all cross blocks at that level. A fourth batched call computes all
eight leaves. Thus the exact same 15 block products use four matmul dispatches:

```text
level 0: 1 node  x 31 layers
level 1: 2 nodes x 31 layers
level 2: 4 nodes x 31 layers
leaves : 8 nodes x 31 layers
```

The packed products are copied into both standard-layout Gram triangles. All
reshapes and copies are explicitly billed. No raw NumPy assignment,
`as_strided`, hidden symmetry tag, untracked native code, or free view is
allowed.

## Frozen predictions

- width `256`, layers `31`, f64, depth `3`;
- exactly four matmul calls;
- unchanged matmul bill `1,167,925,248`;
- exactly four charged reshapes of the full `31x256x256` scaled-weight bank,
  predicted reshape bill `16,252,928`;
- every cross product is copied once to the upper and once to the lower
  triangle, and every leaf product once to its diagonal block;
- no compiler/source semantics or precision change.

The all-inclusive bill is not guessed. It must be measured and remain below
the strict component headroom `1,986,871,472`.

## Gates

1. Exact integer Gram parity and f64 Gram/source parity use M209/M205's frozen
   thresholds; every output must be exactly symmetric after placement.
2. Canonical layer order, unique weight/factor objects, producer epoch,
   float64-only inputs, and compile-after-stage checks remain fail-closed.
3. Pinned FlopScope 0.10.0 must report exactly four matmul calls, exact matmul
   bill `1,167,925,248`, exactly four reshape calls, reshape bill
   `16,252,928`, no rank-3 coefficient array, and inclusive bill below
   `1,986,871,472`.
4. Five fresh generated processes use seeds
   `210700001..210700005`. Every one must be finite, bill-identical, below
   512 MiB RSS, and satisfy

   ```text
   inclusive_bill + 5 * 1e11 * residual_wall_s <= 1,986,871,472.
   ```

5. The result earns resource-component credit only. It cannot supply or claim
   physical `K4/K31/K22/C211`, residual proposals, M198 conversion, terminal
   response, source variance, MSE, leaderboard improvement, or a winner.

## Stop rule

Any semantic, billing, binding, memory, or single-process hostile-wall failure
kills M210 without changing depth, layout, or packing. Preserve the exact
level-fusion identity separately from a failed target schedule.

