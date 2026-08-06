# Preallocated Strassen-Winograd compression: predeclared gates

Date: 2026-08-06

## Frozen invariants

- Objective: reduce the active-regime WHestBench score
  `MSE * max(0.1, C / 272e9)` by changing only the allocation and
  reconstruction schedule of exact sampled matrix products.
- Parent: the immutable random32,256 estimator.  This experiment does not edit
  or run the parent submission.  Its frozen entrypoint SHA-256 is
  `b5314e98d1814af6e014b642591b0549b151e0d9b03e99ed9e913d30490bc638`.
- Accounting/runtime: WHestBench 0.14.0, FlopScope 0.10.0, NumPy 2.4.6,
  float32.  Every matrix multiplication, addition, subtraction, and copy is a
  FlopScope call.  No base-NumPy bridge, native extension, hidden worker, or
  accounting bypass is permitted.
- Data firewall: static source inspection and fresh seeded synthetic matrices
  and depth-32 networks only.  No WHest dataset, truth, scorer, public row,
  locked row, or official submission process may be opened.
- Bias class: exact structural arithmetic modulo ordinary float32
  reassociation.  Inputs, sample nodes, pruning decisions, and output shapes
  are unchanged.
- Resource ceiling: peak process working storage attributable to the candidate
  must remain below 512 MiB.  The hard score budget remains 272e9; the frozen
  champion maximum is 250.488783e9 and is not remeasured here.
- Synthetic seeds are fixed before measurement: 2026080621 through
  2026080648.

## Single changed mechanism

Replace the killed tuple/concatenate reconstruction with one Strassen-Winograd
level using seven sequential `fnp.matmul(..., out=product)` calls, setup-time
preallocated float32 scratch, and `fnp.add`/`fnp.subtract` into preallocated
destinations.  The Winograd schedule uses eight input-block additions and
seven output-block additions.  One visible `fnp.copyto` is allowed when a
strided output quadrant cannot be a matmul destination.  Buffers are allocated
only from `SetupContext.width` and the class-fixed `n_base`; no MLP value,
truth, or data-dependent shape is available in setup.

The dispatcher is a pure function of `(m,k,n)` and the fixed workspace
capacity.  A ragged shape may use its largest even core only if the exact
closed-form bill is below direct and every required `out=` view is accepted by
NumPy/FlopScope without an allocation.  Otherwise it must fall back to direct.

## Ordered gates

1. **API and legality.** FlopScope 0.10.0 source/signatures must expose true
   `out=` for matmul/add/subtract.  Returned objects must be the supplied
   destination and aliasing must be safe.  Setup preallocation is legal only
   because `SetupContext` fixes width/depth before all MLPs and the runner
   invokes setup outside each per-predict budget; all setup buffer bytes and
   setup wall time are still reported.  If a needed ragged strided matmul
   destination is refused, ragged Strassen is killed and dispatches direct.
2. **Closed-form billing.** Across every integer `k,n in [1,256]` for
   `m in {32256,64512}`, the selected method must never bill more than direct.
   Full `(256,256)` must bill at least 10% below direct after all eight input
   additions, seven output additions, the initialization copy if required,
   and all ragged corrections.
3. **Float32 parity.** At least 16 fresh trials spanning full and ragged shapes
   must be finite and shape exact with `max_abs <= 2e-4` and relative
   Frobenius error `<= 3e-6` versus direct NumPy float32.  A fresh depth-32
   width-256 ReLU chain must have final relative error `<= 2e-5`, at most
   `0.02%` gate mismatches, and finite output.
4. **Engineering gate.** On full `(64512,256)@(256,256)`, candidate residual
   wall time must be `< 0.00987 s`, effective proxy
   `billed + 1e11*residual_s` must be below direct with a 2% safety margin,
   total wall ratio must be `<= 1.5`, matmul call count must be `<= 8`, and
   peak measured process memory must be `< 512 MiB`.  Timing uses at least
   seven interleaved direct/candidate pairs after warm-up and reports medians,
   tails, and setup allocation time separately.

Passing all gates yields only a **screened survivor** because official
subprocess validation is firewalled.  Any failure is localized to the exact
allocation/view/schedule link; passing formulas and operators are preserved.
