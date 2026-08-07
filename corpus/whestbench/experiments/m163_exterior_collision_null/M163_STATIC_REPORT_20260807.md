# M163 — exterior collision-null covariance-star control

Date: 2026-08-07  
Status: **STATIC SURVIVOR; fresh variance screen sealed but not executed.**

No truth, scorer, contest/public/private model, leaderboard, submission, or
champion state was read or changed.

## Localized M161 failure

The already-open M161 diagnostic cells were used only to decompose collision
second moment, never as an M163 promotion/development set. The `iii` stratum
alone carried `86.18%` to `98.97%` of collision second moment; `iik` and `iji`
carried nearly all of the remainder. `ijj` was only `0.0030%` to `0.4664%`.
Their conditional p99 values were also overwhelmingly largest for `iii`.

Thus M163 changes one causal link: the collision behavior of M156's otherwise
exact covariance-star control.

## Exterior factor and exact contraction

For the already-present positive-diagonal Gaussian covariance `V`, set

```text
R_ij = V_ij / sqrt(V_ii V_jj)
G_ij = det([[1,R_ij],[R_ij,1]]) = 1 - R_ij^2
A_ij = V_ij G_ij
cE_ijk = -2 A_ij A_ik.
```

`G` is the squared exterior area of two normalized covariance directions. It
is permutation-covariant and invariant under positive diagonal ReLU gauge.
No row is selected, ranked, or tie-broken. With `R_ii=1`, `A_ii=0` exactly, so
`cE` vanishes bitwise on `iii`, `iik`, and `iji`; it deliberately leaves `ijj`
for the sealed fresh screen. For diagonal/isotropic `V`, `A=0` exactly and the
control falls back to zero with no ridge, clipping, or retry.

The M156 full-domain conservation identity still holds with `cE`: add the
deterministic control once and sample `target-cE` under full-support q0. The
compiler is exactly M156's five-product source compiler applied to `A`, not
to `V`:

```text
Z = A W
P = (W o Z^2)^T W
Q = (W^2 o Z)^T Z
R = (W^2)^T Z^2
S = (W o Z)^T(W o Z)
C_aaab = -6(P+Q)
C_aabb = -2(R+R^T+4S),  C_aaaa=diag(C_aaab).
```

There is no explicit collision mask, cubic label table, Kronecker product, or
Khatri--Rao action in the target compiler. Exhaustive width-3/4/5 source
reconstruction passed; the test suite also passed actual permutation and
positive-gauge covariance and isotropic zero-control fallback.

## Static cost gate

| component | protected bill |
|---|---:|
| five existing f64 square-product families, 31 layers | `12.976947200B` |
| conservative correlation/exterior/finiteness/copy allowance | `0.100000000B` |
| **static compiler total** | **`13.076947200B`** |
| M148 K=128 compiler slot | `14.019121200B` |
| **static margin** | **`0.942174000B`** |

This clears the static `<=14.019B` requirement but is not a native resource
certificate. The sealed fresh protocol requires an inclusive target-shaped
FlopScope trace before it may open a variance premise.

## Disposition

Preserve M156's domain-lift identity and the M163 exterior edge factor. The
fresh development/confirmation protocol is frozen in
`M163_FRESH_VARIANCE_PROTOCOL_20260807.md` and has not been run. If native
compiler, invariance, provider, or fresh variance gates fail, kill only this
M163 configuration and retain the exact localization: M161's tail came from
`iii/iik/iji`, while M163 moves the remaining risk to `ijj`.
