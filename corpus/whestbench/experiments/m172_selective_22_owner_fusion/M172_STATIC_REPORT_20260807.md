# M172 selective physical `[2,2]` owner fusion

Status: **STATIC OWNER-ALGEBRA PASS; development BLOCKED on M174's unlawful actual-caller staging ABI.**

M172 changes one mechanism only.  For each `i != j`, it moves the physical
`[2,2]` owner into M163's complete-domain ordered rows,

```text
T[i,j,j] = K22[i,j] / 2,
r[i,j,j] = K22[i,j] / 2 - cE[i,j,j],
cE[i,j,j] = -2 A[i,j]^2,
A = V o (1-R^2).
```

The old separate `[2,2]` source/probe contribution is retired exactly.
`[4]` and `[3,1]` remain separate owners, so `iii`, `iik`, and `iji` are
exactly zero target rows in this arm.  M163 still contributes its unchanged
control, which is exactly zero on those three patterns.

No response, truth, scorer, leaderboard, submission, champion, or source
variance work was read or run.

## Static algebra results

An independent dense symmetric fourth-tensor source, the old separate
`[2,2]` source, and the M172 complete table agree for every generated width
`2..7`.  The maximum absolute discrepancies were:

| width | tensor/table | old-`[2,2]`/table | complete M163 add/subtract |
|---:|---:|---:|---:|
| 2 | `5.55e-17` | `5.55e-17` | `1.67e-16` |
| 3 | `3.55e-15` | `3.55e-15` | `1.73e-14` |
| 4 | `3.55e-15` | `3.55e-15` | `1.63e-13` |
| 5 | `7.11e-15` | `7.11e-15` | `8.07e-13` |
| 6 | `2.84e-14` | `3.55e-14` | `8.81e-13` |
| 7 | `4.26e-14` | `4.26e-14` | `1.07e-11` |

All are below the frozen `3e-10` tolerance.  The width-two conservation
check uses the same exterior coefficient with an independent complete-source
oracle because the unchanged M156 production compiler intentionally refuses
width two; widths `3..7` invoke M163's actual unchanged five-product
compiler.

The suite also checks actual permutation and positive-gauge covariance,
complete-domain conservation, literal `K22/2-cE` rows, exact retirement,
deliberate retained-owner double count, and deliberate M156 collision
re-zeroing.  The latter is a hard failure: M156's old residual API produces
`-cE` on `ijj`, omitting `K22/2`; M172 uses M167's
`complete_residual_table` instead.

## Inclusive static call/cost delta

At target width 256, there are `32,640` unordered physical `[2,2]` units and
`65,280` nonzero ordered `ijj` representatives.  The frozen collision mass
is unchanged at `eta=0.011688232421875`, uniformly on those ordered
representatives; zero rows receive no mass in this arm.

M163's five dense products per layer (`155` across 31 layers) are unchanged.
The M129 primal physical-`K22` provider has two dense contractions per
accepted provider event.  M172 retires their old separate-owner contribution
but charges the same two contractions in the residual path: the generic
physical K22 formation/transport remains necessary.  Net dense-call credit
is therefore exactly zero.

M172 additionally charges five float64 operations per accepted ordered
`ijj` event: `K22/2`, `Aij^2`, multiplication by `-2`, subtraction, and the
HH importance division, plus one setup division for the uniform ordered-row
mass.  The protocol names no source-draw count, so the total is explicitly
recorded as `5 * accepted_ordered_ijj_events + 1`; it is not converted into an
unlicensed target resource claim.

## M169 resource dependency and staged-input gate

M169's closeout manifest and all 15 listed artifact hashes were independently
verified.  It is an exact native resource survivor: both parity checks have
zero mismatches, all five generated traces have two matrix calls and the
predeclared bill `10,477,162,760`, and its reported linear p99 residual is
`5.322182989 ms` below `7.08391688 ms`.

This is conditional evidence only.  M169 requires its caller to already own
all 31 labelled `W_l,V_l` arrays before invocation and explicitly forbids
assuming that a sequential covariance/source provider can materialize later
states early.  M174 has now audited the actual caller and frozen
`REPAIR_NOT_A_LAWFUL_ACTUAL_CALLER_PRECONDITION`: the base estimator owns
only diagonal variances, no labelled full-covariance `V_l` archive exists,
and no M163-slot-to-M125b source-carrier ABI or integrated liveness trace is
available.  The M169 generated-stack result therefore cannot open M172
development.  This is an interface/resource block, not an algebraic failure
or an empirical source-variance kill.

## Frozen development boundary

Development cells are frozen exactly as

```text
(iso_w5,5,1720501,.22)  (factor_w5,5,1720502,.50)
(iso_w6,6,1720601,.22) (factor_w6,6,1720602,.50)
(iso_w7,7,1720701,.22) (factor_w7,7,1720702,.50).
```

The six confirmation cells remain sealed.  There has been no parameter,
support, eta, provider, order, or seed change; source-variance execution
count remains zero.
