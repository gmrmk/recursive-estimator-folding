# M150 direct-adjoint contraction of canonical C_211

Date: 2026-08-07  
Status: **KILL STATIC AS AN EXACT ALL-OUTPUT IMPLEMENTATION; preserve the source/dual associativity interface**  
Scope: generated source algebra and static cost only. No response outcome, truth, scorer, contest model, public row, submission, or champion was used.

## Decision

The canonical C_211 control can be contracted exactly with a supplied full response dual before its source matrices are emitted. The equality retains ordered-singleton half ownership, covariance-star terms, collision exclusions, and all M133 aaaa/aaab/aabb slots. But the all-output exact ReLU response dual is a generic third-order object. Existing M125b is a forward mean/covariance carrier, not that dual. An exact reverse dual incurs O(L n^4) affine work. Hence no rectangular-GEMM-only exact implementation closes under the current interfaces.

This kills the exact direct-adjoint implementation, not a future certified restricted response atlas.

## Frozen source identity

For signed finite cubature nodes s from B canonical blocks (B in {1,2,4}, normally S=49B), define:

```text
mu_i = sum_s omega_s r1_si
a_si = r1_si-mu_i
V_ij = sum_s omega_s a_si a_sj + 1[i=j] sum_s omega_s v_si
t_si = a_si^2+v_si.
```

The last term in V is the required covariance-star. For pairwise-distinct labels:

```text
d_ijk = DeltaTilde_ijk
      = sum_s omega_s t_si a_sj a_sk - V_ii V_jk - 2 V_ij V_ik.       (1)
C_211 = (1/2) sum_{i,j,k distinct} d_ijk F_(i,j,k).                    (2)
```

All repeated labels are deliberately zero in this owner. They belong to other collision classes. The factor one-half is mandatory because (i,j,k) and (i,k,j) are two ordered labels of one singleton-symmetric physical unit. Equation (1) is symmetric under j<->k.

## Exact associative contraction

Let x=W_i, y=W_j, z=W_k. M133 supplies:

```text
F_aaab = 6 (x*y*z)x^T + 3(x^2*z)y^T + 3(x^2*y)z^T
F_aabb = 2[x^2(y*z)^T+(y*z)(x^2)^T]
       + 4[(x*y)(x*z)^T+(x*z)(x*y)^T]
F_aaaa = diag(F_aaab).
```

For each final output o, let h_o, A_o, B_o be the three response covectors and set:

```text
Abar_o = A_o + diag(h_o)
Bbar_o = (B_o+B_o^T)/2.
```

Then no source matrix must be formed to state the exact local contraction:

```text
Phi_ijk,o = 6 (x*y*z)^T Abar_o x
          + 3 (x^2*z)^T Abar_o y
          + 3 (x^2*y)^T Abar_o z
          + 4 (x^2)^T Bbar_o(y*z)
          + 8 (x*y)^T Bbar_o(x*z).                                   (3)
<dual,C_211> = (1/2) sum_distinct d_ijk Phi_ijk.                       (4)
```

This includes all source slots. An independent ordered-singleton guard is:

```text
C_aaab = 3 sum_distinct d_ijk[(x*y*z)x^T+(x^2*z)y^T].                  (5)
```

## Generated parity

`test_direct_adjoint_control.py` uses Philox arrays only. It checks signed-node covariance stars, zero repeated-label coefficients, singleton symmetry, every source slot, and exhaustive equality:

```text
contract_source(dense_c211(W,d), dual)
== direct_c211_dual_contract(W,d,dual)
```

The max absolute tolerance is 3e-11, evaluated independently for B=1,2,4. All four tests pass. No cost or efficacy claim follows from this parity.

## Why rectangular GEMMs cannot close this exactly

Equation (3) requires all-output matrices Abar[o,a,b] and Bbar[o,a,b]. At target shape these are 256-by-256-by-256 response tensors. A universal shared CP representation would require:

```text
Abar[o,a,b] = sum_r L[o,r] U[a,r] V[b,r].
```

Accounting for its two scale gauges per component, a generic n-by-n-by-n tensor needs R(3n-2)>=n^3. At n=256 this gives R>=21,903 and at least 16,777,698 free parameters. Thus there is no general exact O(n)-rank rectangular atlas to substitute for the matrices in (3).

This is dynamically realized in the exact M120 pullback: a rank-one terminal covariance covector becomes `diag(w_o) K diag(w_o)` after the first ReLU Hadamard pullback, which is full rank for generic K. M120's generated rank falsifier observed rank 1 -> rank n. M125b cannot rescue this: it is forward and needs dense source emission; running it on canonical factors would be a prohibited second source carrier.

## Static target cost

One exact all-output covariance-adjoint state has n^3=16,777,216 float64 entries (128 MiB). One reverse affine layer needs two float64 square GEMMs for each of 256 outputs:

```text
one float64 256x256 GEMM                     66,977,792 billed FLOPs
all-output exact affine pullback, one layer  34,292,629,504 billed FLOPs
30 reverse layers                         1,028,778,885,120 billed FLOPs.
```

That is 1.029e12 FLOPs before ReLU pullbacks, canonical state construction, M149/M147 coefficient work, source contraction, allocation, or wall time. It exceeds M148's remaining K128 endpoint slot (14.019B) in one reverse layer. The alternative is dense source emission plus M125b, exactly the mechanism M150 was meant to avoid.

## M149/M147 boundary and salvage

M150 binds no M149 hash because its provider is unfinished. It assumes only an abstract certified local `[2,1,1]` coefficient provider. M147's frozen endpoint bridge remains relevant but its literal target kernel is cost-killed; M150 does not alter that conclusion.

Preserve equations (1)--(5) and the generated parity harness. Reopen only if a new frozen response atlas proves exact restricted action for both Abar and Bbar on every bilinear form in (3), passes exhaustive small-width full-dual parity plus permutation/gauge checks, and has a native target trace below the M148 K128 endpoint slot with exactly-one source ownership. An empirical low-rank fit, a generic tensor truncation, or a second M121/M125b carrier fails this protocol.
