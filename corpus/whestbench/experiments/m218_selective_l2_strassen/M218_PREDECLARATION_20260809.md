# M218 predeclaration -- selective exact L2 Strassen for M215 A/E only

Date: 2026-08-09. Frozen before M218 implementation, tests, or resource
execution. M218 is generated-only and response-free. Challenge weights,
responses, truth, scorer, leaderboard data, submissions, and efficacy or
source-variance measurements are forbidden.

## Non-negotiable invariants

- Objective: reduce the exact cost of M215's strict-distinct ownership bridge
  without changing its coefficient, source equation, collision semantics, or
  physical-owner routing. The official score remains
  `MSE * max(0.1,C/2.72e11)`; M218 measures no MSE.
- Legality/accounting: FlopScope base version 0.10.0 with NumPy 2.4.6,
  float64 charged at 2x, supported matmul billed from operand shapes, every
  participant-created buffer and operation exposed. Backend packing inside a
  supported call is permitted; hidden participant compute is forbidden.
- Bias class: exact bilinear identity in real arithmetic, audited float64
  reassociation. No approximation, tuning, or fitted coefficient.
- Strict incremental effective cap:
  `bill + 5*1e11*residual_wall_s <= 6,824,272,176`.
- Generated algebra units are widths 4, 8, and 12. Frozen target resource and
  numerical units are isolated seeds 218700001..218700005. No contest or
  untouched evaluation unit is exposed.
- Parent M215 result hash:
  `df543fc17bdacc68f938a43f290e875e6da6bf0266c40e955286ae5025d10616`.
  M215 sidecar hash:
  `44a2dd7ee31ff417e25c9ecf282630c5b26f2bff483b27b642b0eb5eabb53e74`.

## One changed mechanism

M215 computes, with `S=diag(u)W`,

```text
A=(S^2)^T S,   E=(S^3)^T S,   D=(S^2)^T(S^2).
```

M218 replaces only the conventional broadcast-batched `A/E` matmul with the
classic exact seven-product Strassen identity recursively applied exactly two
levels. M215's `D` symmetric recursion, every pointwise source term, receipt,
binding, and in-place subtraction remain unchanged.

For quadrants of `X,Y`, one level is frozen as

```text
M1=(X11+X22)(Y11+Y22)   M2=(X21+X22)Y11
M3=X11(Y12-Y22)         M4=X22(Y21-Y11)
M5=(X11+X12)Y22         M6=(X21-X11)(Y11+Y12)
M7=(X12-X22)(Y21+Y22)

Z11=M1+M4-M5+M7; Z12=M3+M5;
Z21=M2+M4;       Z22=M1-M2+M3+M6.
```

The target factors level by level:

1. one reusable `level` plane builds seven 128x128 transforms;
2. seven inner transforms produce a `(7,7,31,64,64)` leaf pack;
3. all 49 leaf products are one supported matmul call;
4. inner and outer recombination reuse `level` and write one conventional
   output plane;
5. the right leaf pack for `S` is built once and reused by `A` and `E`;
6. the left pack is rebuilt first from `(S^2)^T`, then `(S^3)^T`.

No recursion deeper than two, conventional fallback, cubic coefficient,
triple loop, response dual, or change to `D` is allowed.

## Frozen exact prediction

Target: width 256, 31 source layers, float64, Strassen depth 2, D depth 3.

```text
two 49-leaf A/E matmuls               3,160,686,592
unchanged four-call D recursion       1,167,925,248
all Strassen transform/recombine        167,608,320
unchanged M215 non-A/E work              125,960,192
---------------------------------------------------
predicted incremental bill            4,622,180,352
M212 + M218 arithmetic bill            5,871,433,728
recovery versus M215                     824,328,192
```

Expected operation ledger:

```text
matmul:   6 calls, 4,328,611,840
copyto:  81 calls,    85,089,792
add:     51 calls,    95,232,000
subtract:20 calls,    27,934,720
multiply:16 calls,    65,011,712
reshape:  4 calls,    16,252,928
sum:      1 call,      4,047,360
```

Additional M218 storage above M212 is exactly 231.53125 MiB: M215's four
`powers/cross` planes (62 MiB), one seven-branch 128x128 level array
(27.125 MiB), and three 49-leaf arrays (142.40625 MiB). Complete declared
persistent storage is 333.61328125 MiB; peak RSS must be below 512 MiB.

## Frozen gates

1. TDD RED: tests fail because the M218 module is absent.
2. Integer matrices at widths 4,8,12 match direct matmul bit-exactly when all
   intermediate integers remain exactly representable.
3. Generated float64 widths 4,8,12: `A`, `E`, collision slots, and final
   strict-distinct slots match M215 within
   `2e-9*(1+max_abs(M215_reference))`; finite, permutation, gauge, and zero-
   factor contracts remain inherited.
4. Each target seed performs an audit-only generated M215 NumPy comparison
   outside the resource context. Maximum slot error must obey the same frozen
   bound. Audit work earns no deployment or cost credit.
5. Exactly the predicted operation calls and bills above occur in every fresh
   isolated target process; all outputs are finite and binding fails closed.
6. All five target seeds remain below 512 MiB RSS and satisfy the strict
   five-times residual-wall cap. Any miss kills this implementation without
   retuning or seed replacement.

## Allowance interpretation and stop rule

If the arithmetic prediction passes, the M214 bookkeeping remainder becomes
`6,824,272,176 - 4,622,180,352 = 2,202,091,824` before M218 residual wall and
all other unknowns. Including the explicit terminal floor sensitivity leaves
`2,067,874,608`. These are diagnostic upper bounds only: the physical distinct
provider, M198, terminal implementation, lifecycle, copies, and integrated
wall remain unearned. M218 cannot grant a credible integrated fit merely by
passing its isolated component gate.

Any identity, numerical, bill, call-count, allocation, RSS, or hostile-wall
failure kills M218 while preserving M215. A pass promotes only a cheaper
exact collision-correction resource component; it authorizes no variance,
MSE, score, submission, integrated-DAG claim, or winner claim.

