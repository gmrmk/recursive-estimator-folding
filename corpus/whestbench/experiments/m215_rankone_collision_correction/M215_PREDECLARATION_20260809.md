# M215 predeclaration -- exact rank-one collision correction

Date: 2026-08-09. Frozen before implementation and before any M215 test or
resource execution. This mutation is generated-only and response-free.
Challenge weights, responses, truth, scorer, leaderboard data, submissions,
and source-variance or efficacy measurements are forbidden.

## Failed-parent boundary and one changed mechanism

M205/M212 compile the rank-one coefficient

```text
c(i,j,k) = -2 u_i^2 u_j u_k
```

over the **complete** ordered triple domain. M151's `C_211` owner is instead
strictly pairwise-distinct. M215 changes only this ownership boundary: it
computes the exact contribution of all repeated-label rows and subtracts it
from the live M212 source. The resulting source is exactly the strict-
distinct rank-one control, so already-paid legacy physical `[4]`, `[3,1]`,
and `[2,2]` owners may remain injected rather than being discarded and
re-created by a new complete-domain provider.

M215 neither changes `u` nor estimates a physical coefficient. It is an exact
real-arithmetic compiler identity and a float64 implementation audit.

## Frozen algebra

Let `W` have labelled rows, set `S=diag(u)W`, and reuse the live M212 objects

```text
p   = S^T 1
B   = S^T S
rho = diag(B).
```

Define the new collision objects

```text
A = (S^2)^T S   = (W^2)^T diag(u^3) W
t = (S^3)^T 1
E = (S^3)^T S   = (W^3)^T diag(u^4) W
D = (S^2)^T S^2 = (W^2)^T diag(u^4) (W^2).
```

For M205's half-owned forward feature, the frozen collision source is

```text
Ccol_aaab = -18 diag(p) A - 6 t p^T - 12 diag(rho) B + 24 E

Ccol_aabb = -12 [A diag(p) + diag(p) A^T]
             - 4 rho rho^T - 8 (B hadamard B) + 24 D

Ccol_aaaa = diag(Ccol_aaab).
```

The deployed operation is in-place subtraction

```text
Cstrict = Cfull(M212) - Ccol.
```

No cubic coefficient tensor, triple enumeration, response dual, or physical
collision recomputation is allowed in the target circuit. The cubic M205
routine is permitted only as a generated width-3..7 parity oracle.

## Frozen target circuit and prediction

The target receives a live, canonical M212 staged stack and workspace. It
must not restage or copy `W` or `u`. Four additional persistent float64 planes
hold `S^2`, `S^3`, `A`, and `E` (62.0 MiB at 31x256x256). A single supported
broadcast-batched matmul computes `A,E`; M212's depth-3 symmetric recursion is
reused structurally to compute `D` into the now-dead `B` plane.

Frozen target dimensions and operations:

```text
width=256; layers=31; dtype=float64; D recursion depth=3
incremental matmul calls=5
  A/E fused conventional bill       4,152,623,104
  D symmetric recursive bill        1,167,925,248
incremental reshape calls=4             16,252,928
predicted inclusive incremental bill 5,446,508,544
M212+M215 arithmetic bill            6,695,761,920
```

The prediction includes every declared pointwise operation, reduction,
recursive block copy, and final `aaaa` copy. Backend packing belongs to the
supported shape-billed matmul; every participant-created plane is declared.

## Frozen response-free gates

1. Before implementation, tests must fail because the M215 module is absent.
2. At generated widths 3,4,5,6,7 and fixed Philox seeds, all three collision
   slots must match an independent cubic M205 collision-only source within
   `2e-9`, and `full-collision` must match an independent strict-distinct
   cubic source within `2e-9`.
3. Hidden-label permutation and positive ReLU gauge covariance must hold at
   generated small width; zero `u` must emit exact zero correction.
4. The native circuit must contain no cubic array or triple loop, must issue
   exactly five incremental matmul calls and four incremental reshapes, and
   must bill exactly `5,446,508,544` FLOPs under FlopScope 0.10.0.
5. Five fresh processes with seeds 215700001..215700005 must be finite,
   bill-identical, remain below 512 MiB peak RSS, and each satisfy

   `incremental_bill + 5 * 1e11 * incremental_residual_wall_s
      <= 6,824,272,176`.

6. The caller must preserve canonical layer order and a single producer epoch;
   malformed bindings fail closed.

## Stop and promotion rule

Any identity, symmetry, binding, predicted-bill, memory, or hostile-wall
failure kills this fixed implementation. A pass promotes only an exact
strict-distinct ownership bridge and isolated resource component. It does not
authorize variance, MSE, a full-DAG cost claim, a submission, or a winner.
M198 conversion, terminal work, physical distinct-residual provider, copies
outside this component, and integrated wall time remain separate unknowns.

