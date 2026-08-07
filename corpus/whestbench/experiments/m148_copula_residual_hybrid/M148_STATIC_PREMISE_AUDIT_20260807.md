# M148 static premise audit: copula control plus exact residual HH

Date: 2026-08-07  
Status: **REPAIR -- no response run, no truth, scorer, contest model, or champion mutation**

## Decision

There is an exactly unbiased hybrid identity, but the literal high-fidelity implementation is static-cost-killed.

- A deterministic canonical-copula source can be a control even when the copula is wrong: its error is sampled as an exact residual.
- The literal 16-cell, 49-node canonical control cannot fit the 100B protected branch budget at `K=32`, `64`, or `128`, before M147 coefficients, allocations, and wall time.
- A separately identified coarse/global canonical state might fit, but has no residual-alignment evidence or audited contraction. It is an unresolved descendant, not a candidate.

M148 preserves the control/residual interface. It does not reopen M146's cost-killed adaptive deployment configuration or claim a score improvement.

## Ownership and exact hybrid identity

At one source layer, let `E={(i,j,k): i,j,k distinct}` use M133's ordered-singleton convention; `(i,j,k)` and `(i,k,j)` are the two labels of one physical singleton-symmetric unit. Let `F_e(W)` be precisely M133's coefficient-free feature with `k4_aaaa`, `k4_aaab`, and `k4_aabb` outputs.

M147/M131 provides the exact coefficient

```text
Delta_e = kappa(X_i,X_i,X_j,X_k) - tree(i,i,j,k).
T_211   = (1/2) sum_(e in E) Delta_e F_e.                 (1)
```

The half is mandatory: it is M133's ordered-singleton ownership factor.

For a fixed canonical rank-four copula, combine frozen cell `b` and its signed 49-node cubature node into `s`, with `sum_s omega_s=1`. Because Smolyak weights can be signed, this is a finite-cubature **moment functional**, not a probability law. Conditional expectations below are shorthand for the exact independent-coordinate conditional moments at each node. Define

```text
r1_si = E_c[X_i|s];     r2_si = E_c[X_i^2|s]
mu_i  = sum_s omega_s r1_si
a_si  = r1_si-mu_i;     v_si = r2_si-r1_si^2
V_ij  = sum_s omega_s a_si a_sj + 1[i=j] sum_s omega_s v_si.
```

For distinct labels, the exact fourth connected cumulant of this finite-cubature moment functional is

```text
DeltaTilde_(i,j,k)
 = sum_s omega_s (a_si^2+v_si) a_sj a_sk
   - V_ii V_jk - 2 V_ij V_ik.                              (2)
```

This has no Hermite truncation; the finite cubature prior may be inaccurate, but its accuracy affects variance, not the identity below. We use the copula connected cumulant rather than subtracting an additional copula tree: that avoids creating a second tree owner.

```text
C_211 = (1/2) sum_(e in E) DeltaTilde_e F_e
H_e   = Delta_e-DeltaTilde_e.
```

With full-support pre-pilot `q0` and completed-pilot `q1`, the only legal returned residual is

```text
Rhat = (1/K)[ sum_pilot H_E F_E/(2q0(E))
             +sum_main  H_E F_E/(2q1(E|pilot)) ].          (3)
```

The pilot retains `q0`; it is never reweighted with `q1`. Conditional on the pilot, every main summand has expectation `T_211-C_211`, and pilot summands have the same expectation under `q0`. Hence

```text
E[C_211+Rhat]=T_211.
```

The final first-order composition is exactly

```text
final = B_other + C_211 + Rhat.
```

`B_other` owns all non-`[2,1,1]` paths. Prohibited: the full canonical transported correction, a second M121/M125b source, a `[2,1,1]` insertion into M128 `k3^2`, and a source feature other than the same `F_e` in both `C` and `H`.

## Work, sharing, and the contraction barrier

After `(a_si,v_si)` is formed, a sampled `DeltaTilde_e` costs three gathered node columns, one length-`S` reduction, and covariance lookup: `O(S)` scalar work with `S=49*B`; it has no M147 angular quadrature. The exact `Delta_e` still costs M147's recorded favorable lower bound of `108,480` ops per ordinary high-correlation coefficient and `606,720` at the `rho=.999` endpoint adversary.

Allowed logical sharing, with no billing credit until a native trace: M133's row gathers/five-product residual scatter, the exact `F_e` interface, pre-existing background bridge scalars, M125b's single linear transport of the assembled source, and fixed cubature/gauge tables. Not presently shared: 16-cell state construction, canonical conditional moments, dense `C_211` aggregation, M147 certificates/wall time, or M146's pilot-router scans and allocations.

Aggregation can avoid an `n^3` coefficient table: equation (2) is a node-sum of rank-one trilinear fields, and collision exclusions use finite inclusion-exclusion. `V_off=A^T diag(omega) A`, so `V W` is two rectangular maps. It cannot currently avoid a dense-output contraction. Even the leading raw term contains an arbitrary `W^T diag(d) W`; emitting the dense 256-by-256 source needs a square multiplication under FlopScope. A direct adjoint-only contraction would be a new unproven mechanism.

For the literal `B=16`, `S=784` float64 control, the leading raw term alone requires across 31 source layers:

| operation | protected bill |
|---|---:|
| `(784x256) @ (256x256)` | 7.948380160 B |
| `(256x784) @ (784x256)` | 7.958855680 B |
| one `(256x256) @ (256x256)` source emission | 2.595389440 B |
| preserved 49-node pointwise allowance | 2.210652160 B |
| **leading-term floor** | **20.713277440 B** |

This excludes covariance-star terms, collision exclusion, source-state formation, canonicalization, exact residual coefficients, residual products, copies, and wall time.

## Conservative K worksheet

Fixed protected M133 common work is `80.326002640 B`. It includes M126/M125b, path/[2,2], proposal setup, allocation reserve, and the existing 100 ms wall reserve. Residual five products scale from M133's audited 512-draw amount. Coefficient entries below are M147 operation lower bounds, not wall-time promises.

| K/layer | residual products | exact coeff ordinary / endpoint | subtotal ordinary / endpoint | headroom ordinary / endpoint |
|---:|---:|---:|---:|---:|
| 32 | 0.811852800 B | 0.107612160 / 0.601866240 B | 81.245467600 / 81.739721680 B | 18.754532400 / 18.260278320 B |
| 64 | 1.623705600 B | 0.215224320 / 1.203732480 B | 82.164932560 / 83.153440720 B | 17.835067440 / 16.846559280 B |
| 128 | 3.247411200 B | 0.430448640 / 2.407464960 B | 84.003862480 / 85.980878800 B | 15.996137520 / 14.019121200 B |

The `20.713277440 B` floor exceeds every remaining slot. Independently, merely importing the former canonical response arithmetic costs `34.004172800 B` over 31 layers plus `0.134892160 B` for canonicalization. Literal 16-cell M148 is therefore static-cost-killed for every K.

A global/coarse `B=1` control has an indicative leading-map floor around `3.73 B`, so it is not statically ruled out. It has no residual-variance evidence and must receive a separately frozen state constructor, exact aggregation proof, and native trace.

## Fidelity bracket and falsification protocol

The `0.97746--0.97788` transported-correction fidelity implies only the optimistic orthogonal-energy bracket `1-rho^2=0.04457--0.04375`. It is not a coefficientwise `[2,1,1]` cosine, does not establish signs, tails, calibration, or proposal quality, and is used in no coefficient or gate.

Before any deployment/response work, freeze and run only this generated source-level premise after an audited M147-compatible state provider and target-shape `C_211` trace exist:

1. Use 24 fresh generated SPD cells, balanced across diagonal and iid-He families, widths `12,16,24`, and four independent seeds per family/width. Freeze a disjoint confirmation set first.
2. Exhaustively enumerate `E` once per cell with certified exact `Delta_e`, `F_e`, `C_211`, and `H_e`. Record finite-population fixed-`q0` variances `V_H(q0)` and `V_Delta(q0)` plus p99 squared HH contributions. This is not an end-to-end response/truth outcome.
3. Primary K=128 gate, pooled and per family: one-sided paired-bootstrap 90% upper bound for `V_H(q0)/V_Delta(q0)` is `<.25`; residual p99/raw p99 is `<=1.25`; no worsening width trend. This is the variance reduction needed for 128 residual draws to replace 512 raw draws.
4. K=64 `<.125` and K=32 `<.0625` are diagnostic-only branches, not post-hoc K selection.
5. Before enumeration, require exhaustive small-width equality of symbolic aggregate `C_211` to `(1/2)sum DeltaTilde_e F_e` within `2e-11`, singleton symmetry, positive ReLU gauge and permutation covariance, finite cubature weight sum, exactly-one source ownership, and zero coefficient-certificate failures.
6. A separate response-free target-shape trace must fit below 100B with no resource failures and wall time inside the remaining slot. A source variance win cannot waive this cost gate.

## Static disposition

**REPAIR.** The reliable insight is a control-variate conservation law, not a claim that the copula is true. The shared god node is the dense source aggregation/transport interface. Change that interface (for example, an audited global state plus direct adjoint contraction) before reopening a premise; do not rerun the literal 16-cell copula or revive M146's measured-expensive router.

## What-if oracle: decision triggers

| branch | IF | consequence | action |
|---|---|---|---|
| Best | an exact global/coarse aggregation trace costs below the K=128 endpoint slot and source residual ratio passes `.25` | 128 residual draws can replace 512 raw draws at matched leading variance | open the frozen generated source premise only |
| Likely | the control contracts, but its residual ratio is above `.25` | algebra survives; it is not a useful sample-count reduction | preserve the interface and kill that coarse-state configuration |
| Worst | the aggregate needs the literal 16 cells or any unaccounted router work | cost exceeds the branch before efficacy | retain the static kill; do not run a variance screen |
| Contrarian | total `0.977` fidelity does not localize to `[2,1,1]` and residual tails inflate | average energy appears good while HH p99 dominates | reject through the prespecified p99 gate, not a retuned proposal |
| Second order | a direct adjoint contraction avoids dense source emission | the current cubic barrier may disappear without changing residual unbiasedness | treat it as a new named mutation and rerun ownership/cost audits |
