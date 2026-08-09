# M205 predeclaration -- rank-one B=1 control with complete physical owners

Date: 2026-08-09.  This document is frozen before M205 algebra tests.  M205
does not run source variance, a response carrier, MSE, contest instances,
truth, a scorer, a leaderboard query, a submission, or a champion mutation.

## One changed mechanism

M205 changes M204's **collision ownership** only.  It retains M204's fixed
rank-one Rademacher B=1 loading and one-square-product compiler, but replaces
the M156 zero-target collision extension by M167's physical complete table:

```text
T[i,i,i] = K4[i] / 6
T[i,i,j] = T[i,j,i] = K31[i,j] / 3                 (i != j)
T[i,j,j] = T[j,i,i] = K22[i,j] / 2                 (i != j)
T[i,j,k] = Delta211[i,j,k]                         (i,j,k distinct).
```

The fixed B=1 state uses exactly 49 nodes.  For a finite symmetric covariance
with nonnegative diagonal, let `A={i:V_ii>0}`, `m=|A|`, and set

```text
u_i = sqrt(V_ii)/sqrt(m)  if m>0 and i in A, else 0,
d_i = V_ii-u_i^2.
omega_0=omega_1=1/2; omega_2..omega_48=0;
r1_0=mu+u; r1_1=mu-u; r2_s=r1_s^2+d.
```

For `m=0`, M205 uses `u=0,d=diag(V)` rather than throwing.  This is a
zero-control state and preserves the exact residual law.  It is necessary for
totality on zero-variance M179 states; it is not an accuracy claim.

The control is lifted to every ordered triple:

```text
c_ijk = -2 u_i^2 u_j u_k,
R_ijk = T_ijk-c_ijk,
C = (1/2) sum_all c_ijk F(i,j,k),
Rhat = (1/K) sum_t R_Et F(E_t)/(2q(E_t)).
```

No tuning of `u`, rank, proposal, collision mass, source coefficient, or
residual count is allowed in M205.  The complete-domain proposal/provider is
not implemented by this component.

## Frozen source compiler

For `p=W^T u`, `rho=(W^2)^T(u^2)`, and
`B=W^T diag(u^2) W`, emit

```text
C_aaab = -6 [ diag(p^2) B + (rho*p) p^T ]
C_aabb = -2 [ rho (p^2)^T + (p^2) rho^T + 4 diag(p) B diag(p) ]
C_aaaa = diag(C_aaab).
```

The target compiler is constrained to one float64 square `B` contraction per
source layer, plus declared vector/pointwise work.  Brute cubic sums are
small-width test oracles only.

## Fixed response-free gates

1. B=1/49-node finite state, nonnegative conditional variance, covariance
   star, rank-one `dtilde`, zero-variance totality, hidden permutation, and
   positive ReLU-gauge covariance.
2. At widths 3, 4, and 5, compare all `aaaa`, `aaab`, and `aabb` slots from
   the compiler to an independent complete ordered-triple sum.
3. At the same widths, construct arbitrary nonzero physical `K4`, directed
   `K31`, symmetric `K22`, and singleton-symmetric distinct coefficients;
   prove `source(T)=source(c)+source(T-c)`, including every collision class.
4. Record, but do not waive, the strict physical-provider/native-cost block:
   M179+M151's no-replacement partial leaves `1.986871472B`; all collision
   provider, complete-domain proposal, M198, terminal, allocation, and wall
   work remains nonnegative and untraced.

## Stop rule

Any algebra, ownership, invariance, or static-cost arithmetic failure kills
this configuration.  A pass is only an exact physical-owner component pass.
It cannot authorize source variance: a separate native physical provider and
one integrated strict cost trace must pass first.
