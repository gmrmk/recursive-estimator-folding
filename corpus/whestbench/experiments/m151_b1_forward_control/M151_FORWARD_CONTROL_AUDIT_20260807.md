# M151 B=1 exact forward-control descendant

Date: 2026-08-07  
Status: **REPAIR — source-only premise closed; no estimator, response, contest run, or promotion is authorized.**

## One mechanism

M151 keeps M148's exact `[2,1,1]` control/residual split, but fixes the canonical state to **one** signed 49-node block and takes the control through the existing forward M125b source-carrier interface.  It does not perform M150's direct all-output response-dual contraction.

For every source layer, let `E={(i,j,k): i,j,k distinct}` be M133's ordered-singleton labels and let `F_e` be the same coefficient-free `k4_aaaa`, `k4_aaab`, and `k4_aabb` feature.  The physical unit is singleton-symmetric, so the owner is always one half of the ordered sum.

```text
T_211 = (1/2) sum_{e in E} Delta_e F_e,
Delta_e = kappa(X_i,X_i,X_j,X_k) - tree(i,i,j,k).
```

With exactly 49 signed nodes `s`, the deterministic B=1 state contains conditional moments `r1_si` and `r2_si`.  Set

```text
mu_i = sum_s omega_s r1_si
a_si = r1_si - mu_i
v_si = r2_si - r1_si^2
V_ij = sum_s omega_s a_si a_sj + 1[i=j] sum_s omega_s v_si
dtilde_ijk = sum_s omega_s (a_si^2+v_si)a_sj a_sk
             - V_ii V_jk - 2 V_ij V_ik,       i,j,k distinct.
```

The conditional covariance star is mandatory.  The B=1 control and residual are

```text
C_211 = (1/2) sum_{e in E} dtilde_e F_e
H_e   = Delta_e - dtilde_e
Rhat  = (1/K) sum_{t=1..K} H_{E_t} F_{E_t}/[2 q0(E_t)],
final = B_other + M125b_forward(C_211 + Rhat).
```

Here `q0` is the already frozen full-support M133 law; M151 has no pilot, no adaptive router, and no M146 proposal component.  `K=128` is a prespecified accounting branch, not a post-hoc choice.

## Exactness and ownership

For every fixed state, even an inaccurate canonical state, `C_211` is deterministic.  Because `q0(e)>0` on every ordered distinct label,

```text
E[Rhat] = (1/2) sum_e (Delta_e-dtilde_e)F_e = T_211-C_211.
```

Therefore `E[C_211+Rhat]=T_211`.  The argument neither treats signed cubature weights as probabilities nor assumes the canonical copula is true.  Its quality can only change variance.

Ownership is closed as follows.

- M151 owns only the `[2,1,1]` coefficient `dtilde` and residual `H` on pairwise-distinct labels.
- The ordered `j,k` labels receive exactly the mandatory factor `1/2`; `dtilde(i,j,k)=dtilde(i,k,j)`.
- All repeated labels are zero in this owner and remain with their existing collision classes.
- `B_other` owns every non-`[2,1,1]` path.  No second tree subtraction, M121/M125b source carrier, M128 `k3^2` insertion, or full transported correction is allowed.
- M125b is used only once as the existing forward linear carrier of the *assembled* source.  No second carrier is introduced.

The local test harness proves source equality only; it is not a target estimator and cannot authorize an integration.

## Why this avoids M150's obstruction

M150 needed source-slot covectors for every final output, i.e. generic width-by-width-by-width response tensors and reverse covariance pullbacks.  M151 emits the two dense source matrices and diagonal source vector in the forward direction, then supplies them to the pre-existing forward carrier.  Its known core has `O(n^2)` source storage and a single billed `256x256` forward source emission per source layer; it contains no `(output, source, source)` dual and no reverse affine covariance pullback.  This is a different mechanism, not a low-rank response-atlas claim.

The small-width source compiler in `m151_b1_forward_control.py` intentionally enumerates labels as a parity oracle.  That cubic loop is prohibited in the target implementation.  A native B=1 compiler must establish its own exact aggregation trace before this branch may progress.

## Protected static ledger

M148's K=128 endpoint residual subtotal is `85.980878800 B`.  Dividing its node-linear B=16 maps by 16, while retaining one dense forward source emission, gives the known B=1 control core:

| item | protected B FLOPs |
|---|---:|
| `49x256 @ 256x256` map | 0.496773760 |
| `256x49 @ 49x256` map | 0.497428480 |
| one `256x256` dense forward source emission | 2.595389440 |
| 49-node pointwise allowance | 0.138165760 |
| **known B=1 control core** | **3.727757440** |
| K=128 endpoint residual subtotal | 85.980878800 |
| **known branch total** | **89.708636240** |
| **100B remainder for every untraced new cost** | **10.291363760** |

This remainder is an inclusive cap, not free headroom.  It must pay B=1 state construction, canonicalization, tables, copies/allocations, any uncredited source-carrier calls, coefficient glue, and residual wall time at `1e11 FLOPs/s`.  No M125b sharing credit is presumed until a native trace proves it.  The B=1 core is a conditional static survivor; the whole implementation is not yet cost-certified.

Call risks are explicit: 93 known B=1 control map/emission calls across 31 layers, at most 31 state-provider calls, 3,968 K=128 exact residual coefficient calls, and 155 five-product residual batches.  There may be no all-output dual, reverse covariance pullback, adaptive proposal scan, or B>1 stacking.

The f64 B=1 working payload before allocator copies is about 2.076 MiB: state/moments, two rectangular workspaces, one covariance, and the three source slots.  The only available hash-bound Formal-L1 reference peak is 474.859 MiB, leaving 37.141 MiB to a 512 MiB cap, but that is an exposure bracket rather than a memory credit.  The gate demands a measured integrated high-water mark at or below 512 MiB.

## Closed source-only premise gate

All items below must pass before any generated residual-variance screen, response activity, or integration work.  Failure of any item kills this B=1 provider/configuration while preserving the algebra above.

1. Bind the formal sources and the M148/M147 premises by SHA-256; reject a changed hash, changed target shape, B not equal to one, node count not equal to 49, nonfinite state, negative conditional variance, or cubature weight sum outside `3e-13`.
2. On independent Philox-only small widths, exhaustively verify the three emitted source slots against the ordered formula to `4e-11`, exact `j/k` symmetry, zero repeated-label entries, covariance-star inclusion, and the half-owner guard.  These are response-free algebra tests only.
3. Supply an audited source-only B=1 canonical-state constructor that is positive-ReLU-gauge and hidden-label permutation covariant, fixed before residual sampling, and has no truth/scorer/label or outcome input.  It must expose only its conditional moments and signed weights.
4. Produce a native target-shaped FlopScope trace for the exact forward compiler plus one M125b carrier insertion.  Its inclusive, non-overlapped new arithmetic and residual wall cost must be at most `10.291363760 B`; allocation high-water must be at most 512 MiB; all expected calls must be counted.  A benchmark or theoretical payload is not a substitute.
5. Bind an exact M147-compatible residual coefficient provider.  The K=128 endpoint allowance already includes M148's `2.407464960 B` lower bound, but no missing certification, refusal, or unpriced wall time may be ignored.
6. Confirm one source owner only and no `n^3` response-dual allocation/call.  The target compiler must not use the parity oracle's exhaustive triple loop.

Only after these conditions could the separate M148 frozen source-level residual-variance gate be considered.  This artifact neither opens that gate nor makes an efficacy claim.

## Disposition

**REPAIR / conditional static survivor, source premise closed.**  The preserved identity is useful and exact.  M151 is not deployable until a B=1 state provider and native trace satisfy the inclusive cap.  If they do not, kill the provider configuration without reviving M150's adjoint path or M146's router.
