# M209 predeclaration -- layer-batched recursive Gram control compiler

Date: 2026-08-09. This document is frozen before M209 implementation or
resource execution. M209 is response-free: it may use generated matrices but
must not read challenge weights, truth, a scorer, a leaderboard, a submission,
or any cached response/efficacy record.

## One changed mechanism

M209 changes only the resource schedule of M205's already-proved synthetic
rank-one control. It does not change the B=1 loading, physical-owner table,
residual law, source coefficients, response map, or estimator.

For every source layer `l=1..31`, M205 needs

```text
U_l = diag(u_l) W_l,
B_l = U_l^T U_l,
p_l = W_l^T u_l = sum_rows(U_l).
```

The dense M205/M206 schedule computes both triangles of symmetric `B_l` and
costs `2.076311552B` billed f64 FLOPs for the 31 square products alone. M209
computes each Gram matrix by a fixed depth-3 column partition. At every
internal block it computes one cross block, mirrors it, and recurses into the
two diagonal Gram blocks. At each leaf it computes one diagonal Gram block.
The 31 independent layers are NumPy/FlopScope batch axes. Each tree node is
therefore one batched matmul call across all layers, for exactly 15 matmul
calls rather than 31 dense calls or 465 sequential block calls.

For an interval `I=L+R`:

```text
B[L,R] = U[:,L]^T U[:,R]
B[R,L] = transpose(B[L,R])
gram(L); gram(R)
```

Depth is frozen at three. No depth, block order, precision, or batching may be
tuned after observing a trace.

## Frozen arithmetic prediction

Pinned target shape: `layers=31`, `width=256`, `dtype=float64`. FlopScope's
matmul bill is `2*m*k*n-m*n`, multiplied by two for f64. At depth three the
tree contains cross-node widths `128`, `64` twice, and `32` four times, plus
eight width-32 Gram leaves. The predicted matmul bill is exactly:

```text
2 * 31 * [
  (2*128*256*128 - 128^2)
  + 2*(2*64*256*64 - 64^2)
  + 4*(2*32*256*32 - 32^2)
  + 8*(2*32*256*32 - 32^2)
] = 1,167,925,248.
```

Mirroring the seven internal-node cross blocks copies `28,672` f64 elements
per layer, predicted bill `1,777,664` under the frozen two-times f64 rate.
All weight/factor staging, `U`, row reduction for `p`, diagonal access,
pointwise source assembly, output copies, allocations, and residual wall are
additional and must be measured. No M151 or M179 sharing credit is assumed.

## Fixed gates

1. **Algebra.** On generated integer matrices at widths 8 and 16, the depth-3
   block Gram must equal `U.T @ U` exactly. On finite generated f64 matrices at
   widths 8, 16, and 32, max absolute Gram error must be <= `2e-12`.
2. **Source parity.** M209's `aaaa`, `aaab`, and `aabb` must match M205's
   dense complete-domain compiler at the same generated widths with max
   absolute error <= `2e-10`; collision rows remain physical-owner residual
   territory and are not re-zeroed.
3. **Invariance.** Hidden-coordinate permutation and positive ReLU-gauge tests
   must pass at <= `3e-10`; all-zero `u` must emit exact zero source.
4. **Native bill.** A generated target-shape FlopScope 0.10.0 trace must show
   exactly 15 matmul calls and exactly `1,167,925,248` billed matmul FLOPs. Its
   all-inclusive compiler bill must be strictly below the no-replacement
   headroom `1,986,871,472`; every operation, staging copy, and output write is
   charged. No reshape/view may be silently free.
5. **Caller/liveness.** The trace must bind every `(W_l,u_l)` to one unique
   labelled layer, reject reordering/duplication/dtype substitution, retain no
   rank-3 coefficient table, stay below 512 MiB RSS, and report every live
   staged/output buffer. All-layer staging is lawful only after the sequential
   background pass has actually emitted all 31 factors.
6. **Wall/call hostility.** Run five fresh generated seeds. Report residual
   mean/p99/max and a hostile five-times projection. A resource pass requires
   finite outputs, constant bill, exact call count, and no process above the
   component's strict remaining slot after billed work. Local timing earns no
   production credit by itself.

## Stop and promotion rules

Any algebra, source, binding, bill, memory, or hostile-wall failure kills this
schedule without retuning depth. A pass promotes only an exact response-free
resource component. It supplies no physical `K4/K31/K22/C211`, no sampled
residual proposal, no M198/terminal cost, no source-variance or MSE evidence,
and no winner claim. The next gate would still be one integrated physical
provider plus response trace.

