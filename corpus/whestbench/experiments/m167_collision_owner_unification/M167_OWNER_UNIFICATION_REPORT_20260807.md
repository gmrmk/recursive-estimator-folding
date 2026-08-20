# M167 collision-owner unification

Status: **owner algebra passes; M163 `ijj` relabelling is rejected; no efficacy was run.**

M156 encodes the hidden fourth-order multiset `{i,i,j,k}` in a complete ordered, singleton-symmetric table. Its original target convention was zero on collision triples because separate physical owners supplied those entries. M167 proves that those owners can instead be moved into this table without double counting:

```text
iii       -> [4]:   T[i,i,i]       = K4[i] / 6
iik, iji  -> [3,1]: T[i,i,j]       = T[i,j,i] = K31[i,j] / 3
ijj       -> [2,2]: T[i,j,j]       = K22[i,j] / 2
                         and T[j,i,i] = K22[i,j] / 2
```

The factors are orbit factors. A direct dense symmetric fourth-tensor contraction and the complete M156 feature sum agree on every generated width from 2 through 6, with maximum error at most `7.11e-14`. The existing separate `[4]`, `[3,1]`, and `[2,2]` source must then be retired completely; retaining it is detected as a nonzero double count.

This changes one interface detail: M156's `residual_table` deliberately applies a zero collision extension. M167 uses a complete-domain subtraction instead, so the physical collision target is not erased after ownership transfer. With that correction, both the M156 and M163 add/subtract laws conserve the complete source on generated widths 3 through 6 (worst errors `2.98e-11` and `6.82e-13`). Permutation and positive-gauge covariance also pass on widths 2 through 6.

## The `ijj` result

M163's exterior control puts `cE[i,j,j] = -2 A[i,j]^2` in each of the two `[2,2]` representatives. Under M167's mapping, calling that the physical owner would require

```text
K22[i,j] = -4 A[i,j]^2.
```

That identity is false on generated exact M122 ReLU collision states: maximum absolute mismatches for widths 2 through 6 were `0.751`, `0.301`, `0.406`, `0.513`, and `0.240`. Therefore M163 and the real `[2,2]` source share support but not coefficient semantics. The correct unified expression is physical `K22` in the complete target and `K22/2 - cE` in its residual arm. It is not lawful to delete the physical `[2,2]` owner by relabelling `cE` as it.

## Static disposition

M167 adds zero dense products and claims zero deployment calls: it is an ownership algebra repair, not a compiler or performance result. M156/M163 still use their existing five-product deterministic control compiler. Generic physical `[2,2]` formation and residual transport remain the known Khatri--Rao-class obstruction, so no source-variance, native-wall, cost, or outcome gate was opened.
