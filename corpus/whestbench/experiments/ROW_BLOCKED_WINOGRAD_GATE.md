# Frozen gate: 8192-row streaming Winograd descendant

Date frozen: 2026-08-06, before this descendant's code, tests, timings, or
memory measurements were run.

This is a `recursive-estimator-folding` child of
`integrated_batched_winograd`.  It changes only the failed full-height
seven-left/seven-product workspace mechanism.  The immutable random32,256
fold3 parent, its sample geometry, estimand, controls, pruning, seeds,
precision, and all prior numerical gates remain fixed.

## Invariants and firewall

- Objective: lower the competition score `MSE * C/B` in the active linear
  cost regime by reducing exact sample-path arithmetic without changing the
  estimator distribution or output, where `C = billed_FLOPs + 1e11 *
  residual_wall_s` and `B = 2.72e11`.
- Parent champion artifact remains unchanged: random32,256 fold3 tar SHA-256
  prefix `1874f9`; this synthetic engineering screen cannot promote or rewrite
  it.
- Bias class: exact arithmetic rearrangement, apart from ordinary float32
  reassociation already bounded by the inherited parity gates.
- Runtime/accounting boundary: installed Python, NumPy, WHestBench and
  FlopScope environment used by the parent audit; every `fnp` operation is
  billed and all extra calls/residual time are retained.
- Resource limit: measured process peak working set `<512 MiB`, setup `<4 s`,
  full predict `<20 s`, with the parent's conservative compute gate
  `C_child/C_parent <= 0.98`.
- Development units are fresh synthetic weights only.  No WHestBench dataset
  row, target, scorer, API, saved official result, or submission path may be
  opened.  There is no holdout access in this branch.
- Seeds remain setup `2026080672`, synthetic MLP `2026080671`, independent
  depth propagation `2026080673`, and explicit probes `2026080674+index`.

## Frozen changed mechanism

The fixed block height is **8192 rows**, selected from setup-time memory
algebra before any timing:

```text
full output, 64512 x 256 float32                63.0000 MiB
7 left blocks, 7 x 4096 x 128 float32          14.0000 MiB
7 product blocks, 7 x 4096 x 128 float32       14.0000 MiB
right pack, 7 x 128 x 128 float32               0.4375 MiB
total operator workspace                        91.4375 MiB
```

This replaces only the former `283.9375 MiB` full-height Batched-B workspace.
For each selected hook, form the seven right Winograd operands once, then
process consecutive even row blocks through the bounded seven-left/seven-
product scratch and reconstruct directly into the corresponding full-output
slice.  The last block may be shorter but must be even.  Odd contracted width
still dispatches direct.  An odd output width still uses one direct full-row
tail product.

Row splitting must be proved bill-preserving.  Leaf products, left-stack
fills, and output reconstruction are linear in row count, so their sums over
blocks equal the unsplit bill.  The right-stack fill is charged exactly once,
as before.  The selected arithmetic bill therefore remains
`batched_candidate_bill(m,k,n).total`; only visible matmul call count changes
from one core call to `ceil(m/8192)` core calls, plus an output-tail call when
needed.  Actual call counts and residual time must be reported, not hidden.

## Frozen geometry and measurements

- Parent and child: identical full-entry width 256, depth 32,
  `n_base=126*256=32256`, hence 64512 antipodal sample paths.
- Parent and child run in fresh one-thread processes.  No reduced-row
  extrapolation is permitted if full geometry completes.
- Explicit probes are fixed at `(512,256,256)`, `(512,224,208)`,
  `(512,255,252)`, `(512,256,253)`, plus row-boundary probes
  `(8192,256,256)`, `(8194,256,256)`, `(16386,224,208)`, and
  `(64512,256,253)`.
- Static dispatch checks every `m in {32256,64512}`, every `k,n in [1,256]`.
  A separate row-partition proof checks every even `m in [2,64512]`.
- Record setup/predict wall, analytical FLOPs, backend/overhead/residual,
  effective `C`, finite output, hook shapes/strategies/bills/core-call counts,
  process peak/end working sets, workspace bytes, whole-prediction parity,
  independent depth-32 parity/gate mismatch, and every ragged probe.

## Promotion screen

All gates must pass exactly as frozen:

1. parent and child setup `<4.0 s`;
2. every full predict `<20.0 s`, without exception or nonfinite output;
3. matched-synthetic `C_child/C_parent <= 0.98`;
4. full prediction relative Frobenius `<=2e-5`;
5. depth-32 relative final error `<=2e-5` and gate mismatch fraction
   `<=0.0002`;
6. measured child process peak working set `<512 MiB`;
7. static and every actual selected arithmetic bill `<=` direct, and measured
   FlopScope bill equals the row-block analytical bill;
8. every explicit/ragged probe is finite, has relative Frobenius `<=3e-6`,
   and matches its analytical bill;
9. setup algebra is exactly `91.4375 MiB` at maximum geometry and actual
   core-call counts equal the frozen partition rule.

If any gate fails, localize that link only.  Preserve the exact Winograd
algebra, bill proof, dispatcher, and any passing memory/numerical components.

