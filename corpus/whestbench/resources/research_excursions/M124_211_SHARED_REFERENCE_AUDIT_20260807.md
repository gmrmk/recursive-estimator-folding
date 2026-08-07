# M124 [2,1,1] shared-reference audit -- 2026-08-07

## Verdict

**REPAIR before freeze; keep the M124 outcome grid inert.**

M122 defines the three-label fourth-cumulant collision `[2,1,1]` (`aabc`)
through an exact tripartite normal-ordered series followed by the connected
set-partition formula. M124's `_replace_collisions` replaces only entries with
one or two unique labels. Its candidate source and its purported dense
reference therefore use the same tree continuation on every `[2,1,1]` entry.

This is a shared-reference defect: the frozen M124 fidelity grid could pass
without measuring the missing collision. No M124 outcome has been executed,
so the repair is available without consuming or retrying a one-shot.

No contest/public/private datum, scorer, champion, package, upload, or
submission was accessed. The numerical falsifier used one already-declared
generated Philox M124 cell: width 8, alpha scale 0.15, seed 1240801.

## Static evidence

The exact M122 reference is

```text
exact_collision_cumulant(state, (i,i,j,k))
```

for three distinct labels `i,j,k`. In contrast,
`m124_shared_projector.py::_replace_collisions` has branches only for
`len(unique)==1` and `len(unique)==2`; three-label entries retain
`weighted_tree4` unchanged. `CollisionCorrections` likewise stores only
`diagonal4`, `majority4`, and `paired4` arrays, all O(n2) or smaller.

The direct M126 source draft makes the same boundary explicit:
`collision_repeated_exact` handles `[4]`, `[3,1]`, and `[2,2]` and states that
it does not include an exact `[2,1,1]` defect tensor.

## Generated falsifier

`audit_m124_211_shared_reference.py` constructs each canonical exact
`(i,i,j,k)` value with M122's independent 48-term tail-checked series, scatters
all 12 slot permutations, subtracts the tree continuation, transports the
difference through the frozen generated weight, and evaluates the repeated
fourth-cumulant and one-delay Edgeworth response changes.

| statistic | value |
|---|---:|
| tree relative error within `[2,1,1]` | 0.6971803074 |
| exact `[2,1,1]` norm / M124 base-source norm | 0.1317205951 |
| full transported k4 relative change | 0.08104717034 |
| transported repeated-slice relative change | 0.07395217883 |
| one-delay mean-response relative change | 0.01317825971 |
| one-delay covariance-response relative change | 0.02102398320 |

One cell is not a width-law estimate, but the static shared-reference flaw is
deterministic and needs no grid. The measured cell also shows that the omitted
term is not numerically zero. The result does not kill a rank-four projected
source; it invalidates the current reference and cost-completeness claim.

## Required mutation

1. Preserve M124's exact k3 Gram, shared projector, tree cores, and one/two-label
   collision components.
2. Give `[2,1,1]` an independent reference and a distinct approximation/error
   gate. The candidate may use an output-aligned direct contraction, a
   rigorously frozen separated approximation, or an explicitly approximate
   tree continuation, but candidate and reference may not share it silently.
3. Charge its construction, transport, response, copies, and wall time. The
   old `6B collision_cores` and `4B analytic_collision_source_scalars` reserves
   are not an implementation or a call trace.
4. Rebuild and rehash a separately named frozen manifest only after an
   independent pre-execution audit. Do not merely flip `execution_authorized`
   in the existing draft.

Until these steps pass, M124 remains a preserved source component and its
outcome state remains `UNOPENED`.
