# M161 — response-free variance premise for the M156 complete-domain star

Date: 2026-08-07  
Status: **KILLED: frozen complete-domain star control fails source variance and tail gates.**

No neural-network output, truth, scorer, contest/public/private model,
leaderboard, submission, or champion artifact was read or changed. This is a
generated-Gaussian source-only falsifier.

## Frozen mechanism

For the exact distinct-label target `Delta_ijk` from M147 and an already
present Gaussian-background preactivation covariance `V`, M161 keeps M156's
complete-domain control

```text
c_ijk = -2 V_ij V_ik,                         for every ordered triple,
Delta*_ijk = Delta_ijk on pairwise-distinct labels and 0 on collisions,
H_ijk = Delta*_ijk - c_ijk.
```

The complete-domain identity is exact:

```text
(1/2) sum_all c_ijk F_ijk
 + E_q[(Delta*_E-c_E) F_E/(2q(E))]
= (1/2) sum_distinct Delta_ijk F_ijk.
```

The state covariance is not fit, inferred, or newly constructed for this
control; it is the fixed Gaussian covariance used to construct each generated
background. M161 uses one predeclared full-support q0: uniform within distinct
and collision strata, with the collision mass fixed to the width-256 M156
value `0.011688232421875`. The proposal is target-free and nonadaptive.

## Exact-provider and ownership result

All six cells were well inside the declared SPD / endpoint-excluded domain:
maximum absolute off-diagonal correlation was `0.42432`; the smallest
covariance eigenvalue was `0.34850`. M147's actual `48/64` certified
noncentral `[2,1,1]` provider completed every distinct coefficient. Its
largest value paired-order disagreement was `8.35e-10 < 2e-8`; the tangent
disagreement was zero for the frozen zero tangent.

The complete source reconstruction

```text
compiled_star_source + exhaustive_residual_source = exhaustive_distinct_target_source
```

held with maximum absolute error at most `1.43e-14`. Collision target entries
were exactly zero and residual entries exactly `-c`; no physical collision
source owner was reused.

The source proxy flattens all three complete M156 source slots (`aaaa`,
`aaab`, and `aabb`). It is deliberately a **pre-transport** proxy: no complete
M125b source-to-output carrier was available in this small-width, response-free
audit. A scalar coefficient proxy is reported separately only as a diagnostic;
it has physical ReLU-scale units and is not gauge invariant by itself.

## Frozen gate result

| gate | required | observed | result |
|---|---:|---:|---|
| source HH residual/raw upper-90 | `< 0.25` | `7.3968e8` | fail |
| maximum source p99 ratio | `<= 1.25` | `6.5364e5` | fail |
| collision-only p99/raw ratio | `<= 1.25` | `3.7533e12` | fail |
| width slope | `<= 0` | negative | pass, non-decisive |

The pooled source residual/raw ratio is `3.2011e8`. Across all six cells,
collision rows account for `0.9999782` to `0.99999993` of the residual source
second moment. The most favourable individual source ratio is still
`1.6989e7`. This is a decisive kill, not an uncertain near-miss.

## Aggressive symmetry audit

On an independent structural replay of `isotropic_w4`, permutation errors for
the certified target/control were `1.63e-19` and `0`; full source-proxy raw
and residual variance relative errors were `4.24e-22` and `0`. Under a positive
hidden ReLU gauge, the scaled target/control relative errors were `3.95e-17`
and `1.31e-16`, and the full source raw/residual relative errors were
`2.96e-21` and `2.89e-16`. The separate scalar-coefficient diagnostic changes
by `4.42e-6` under that gauge, as expected because it omits the compensating
source feature; it is not used for the physical gate.

## Interpretation and salvage

The exact domain lift solves M155's masked Khatri--Rao compiler obstruction,
but it moves a nonzero covariance-star coefficient onto rows whose exact
`[2,1,1]` target is zero. Under the frozen full-support HH law those rows are a
tail bomb, not a harmless cancellation. The failure is therefore in the
**collision extension**, not in the exact control/residual conservation law,
the five-product compiler, the M147 provider, or the source-slot ownership.

Do not retune collision mass, q0, cells, `K`, or the star coefficient. A new
descendant must change the collision mechanism—for example, use a control that
vanishes on collision strata or retain collisions in a separately bounded
unbiased residual with its own proposal/cost proof. It must then re-enter the
same source-variance and p99 ladder from a new frozen manifest.
