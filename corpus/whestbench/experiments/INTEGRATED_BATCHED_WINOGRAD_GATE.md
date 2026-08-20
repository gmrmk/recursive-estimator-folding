# Frozen gate: integrated batched-Winograd full-entry descendant

Date frozen: 2026-08-06

This is a new `recursive-estimator-folding` descendant.  It is not a
retroactive promotion of `preallocated_strassen_compression`, and it cannot
modify the immutable random32,256 fold3 parent.

## Firewall

The screen is fresh-synthetic only.  It may not open a WHestBench dataset row,
truth, scorer, API, submission path, or saved official result.  It uses only
synthetic float32 He weights and setup-time random frames.

## Frozen mechanism

- Parent: random-frame fold3 with `n_base = 126*256 = 32256` and ordinary
  direct hook products.
- Child: the identical estimator, nodes, pruning rules, folds, and controls,
  changing only `_first_sample_matmul` and `_sample_matmul` to the already
  specified `BatchedPreallocatedWinograd` Mutation B.
- Width/depth: 256/32.  Setup seed `2026080672`; synthetic MLP seed
  `2026080671`; independent depth-propagation seed `2026080673`.
- Parent and child run in fresh one-thread processes.  The actual full path
  geometry is attempted; no path-count extrapolation may replace it if it
  completes.
- Explicit dispatcher probes, independent of the estimator trace:
  `(512,256,256)` full, `(512,224,208)` active-even,
  `(512,255,252)` odd-contracted/direct, and `(512,256,253)` odd-output/ragged.
- Static dispatcher enumeration covers `m in {32256,64512}`, every
  `k,n in [1,256]`.

## Required measurements

For each fresh full-entry process: setup wall, whole-predict wall, FlopScope
analytical FLOPs, backend/overhead/residual split, effective compute
`C=F+1e11*residual`, finite output, hook shapes/strategies/bills, and Windows
process peak working set plus end live set.  The paired predictions are
compared by relative Frobenius and maximum absolute error.  The depth-32
screen records ReLU gate mismatches and final relative error.  The report also
records eligible call and direct-hook-bill fractions.

## Promotion screen

All gates must pass:

1. setup `<4.0 s` for both parent and child;
2. every full predict `<20.0 s`, no exception, timeout, or nonfinite output;
3. matched synthetic `C_child/C_parent <= 0.98`;
4. full prediction relative Frobenius `<=2e-5`;
5. depth-32 final relative error `<=2e-5` and gate mismatch fraction
   `<=0.0002` (0.02%);
6. measured child process peak working set `<512 MiB`;
7. every selected dispatcher bill is `<=` its direct bill, both in the
   exhaustive static enumeration and every actual/probe call;
8. every explicit probe is finite and has relative Frobenius `<=3e-6`.

If any gate fails, localize only that link.  Preserve the exact Winograd
operator, its algebraic bill, passing dispatcher branches, and any measured
engineering improvements; do not dismiss the family globally.

