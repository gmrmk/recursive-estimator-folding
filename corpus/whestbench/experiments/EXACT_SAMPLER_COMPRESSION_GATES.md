# Exact sampler compression: predeclared gates

Date: 2026-08-06

## Invariants

- Objective: reduce the WHestBench active-regime score
  `MSE * max(0.1, C / 272e9)` by changing only the implementation of matrix
  products in the promoted random32,256 sampler.
- Accounting boundary: every arithmetic, stack, concatenate, copy, gather, and
  reshape remains visible to FlopScope 0.10.0.  No native bridge, hidden
  compute, untracked buffer, evaluator quirk, or data-dependent accounting
  bypass is allowed.
- Runtime boundary: WHestBench 0.14.0, FlopScope 0.10.0, NumPy 2.4.6,
  float32 sample/weight arithmetic.
- Hard resource ceiling: 272e9 effective compute per network.  Screening safety
  ceiling: 258.4e9 (95% of the hard ceiling).  The frozen champion's recorded
  maximum is 250.488783e9; this audit does not rerun or modify it.
- Bias class: exact structural child.  It must evaluate the same matrix
  products; the only permitted prediction change is ordinary float32
  reassociation.  No weight truncation, neuron pruning change, or sample change.
- Data firewall: no WHest dataset, public/locked truth, scorer, official row, or
  submission execution.  Only source inspection, closed-form billing, and
  fresh seeded synthetic arrays/networks are permitted.
- Frozen champion entrypoint SHA-256:
  `b5314e98d1814af6e014b642591b0549b151e0d9b03e99ed9e913d30490bc638`.
- Frozen dependencies:
  `orthogonal_fold3.py=7dbee34ecec4936adc77a232cd7b7ade3dfff6d35282708455bf4450847035d6`,
  `fold3_estimator.py=505a726f4d6dbdb1946edf7d3806b3f2ee795d06be2cad10a8de0cc58ff04ab7`.
- Prior operators, inspected but not trusted as candidates:
  `strassen.py=4df5c056e8edc69b8c6a8f280f1c72ccebde1a03f3856e94ba676440d2b2fe05`,
  `fused_strassen.py=f3ebd8f0be27f1176bd80601dce918fa0ae8d1e94ba86e610c0baa0f383ddc74`.
- Reproducible synthetic randomization seeds: 2026080601 through 2026080616.

## Candidate mechanism

For a sampled product `A[m,k] @ W[k,n]` with `m=64,512`, tile complete
128-by-128 blocks and use one or two fused Strassen levels only when the
complete-tile bill plus all FlopScope-visible additions, stacks, reshapes,
concatenations, and ragged direct products is less than one direct product.
Fall back to direct matmul otherwise.  The operator is selected from shapes
alone, never from values or truth.

Predicted signature: exact-shape billing improves most when `k,n >= 128` and
especially at `k=n=256`; it should disappear for `k<128` or `n<128`.  Ragged
remainders may erase the gain.  Fused L2 should have fewer matmul calls than
ordinary recursive Strassen but much larger temporaries.

## Kill and promotion gates

The audit has three ordered gates.  A failure stops promotion but preserves
the passing sub-operators.

1. **Closed-form billing gate.** Across all integer `k,n in [1,256]` at
   `m=64,512`, a shape dispatcher must never choose a variant with a larger
   predicted FlopScope bill than direct matmul.  At `(256,256)` it must save at
   least 10% of the matrix-product bill after counting stacks, additions,
   reshapes, concatenations, and tile accumulation.  Ordinary recursive and
   fused L1/L2 are compared separately.
2. **Synthetic numerical gate.** On at least 16 fresh seeded float32 trials
   spanning full, active-column, ragged, and folded products, every returned
   value must be finite, shape-exact, and satisfy both
   `max_abs_error <= 2e-4` and `relative_Frobenius_error <= 3e-6` versus direct
   NumPy float32 matmul.  A depth-32 synthetic ReLU chain must satisfy
   `relative_final_error <= 2e-5` and no more than 0.02% gate mismatches.
3. **Engineering plausibility gate.** Peak live temporary storage for one
   product must be at most 512 MiB, matmul-call count must be at most 8 per
   product, and a local fresh-synthetic timing screen must not be more than
   1.5x direct at `(64,512,256)@(256,256)`.  Because local timing cannot certify
   official residual time, passing this gate yields only a **screened
   survivor**, never a promoted champion.  Deployment would still require a
   separately authorized official-subprocess cost/parity validation.

## Decision vocabulary

- `killed implementation`: a specified operator fails a gate.
- `preserved component`: an exact tile or billing formula passes even if its
  enclosing implementation fails.
- `screened survivor`: all synthetic/static gates pass; no champion change.
- `validated child` and `promoted champion`: unavailable in this audit because
  the required independent official validation is explicitly firewalled.
