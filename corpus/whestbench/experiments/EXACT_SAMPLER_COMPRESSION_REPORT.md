# Exact structural compression audit of random32,256

## Verdict

The current exact Strassen implementation is **not a deployable child**.  It
passes the billing and numerical gates, then fails the predeclared engineering
gate decisively.

The best billed form is a new whole-row rectangular two-level hybrid:

```text
(64,512 x 256) @ (256 x 256)
direct bill                  8.439201792B
rectangular L2 hybrid bill   6.712770560B
bill ratio                   0.795427189
```

It preserves the product to float32 reassociation error, but its seven fused
leaf groups and reconstruction allocations create `0.054923s` of measured
FlopScope residual time for one product.  At the competition's
`1e11 FLOP/s` residual charge, its local effective-compute proxy is `12.205B`
versus `8.444B` direct, a **44.5% regression**.  One-level sequential is the
least bad form, but still regresses the proxy by 8.3% and runs 5.28x slower.

Disposition: **killed implementation; preserve the rectangular algebra and
billing model.**  The frozen champion and submission artifact were not
modified, run, packaged, or submitted.

## Firewall and frozen parent

This audit used source inspection, closed-form formulas, FlopScope
micro-accounting, and fresh seeded synthetic float32 arrays only.  It did not
open a WHest dataset, truth, scorer, public/locked row, or official runner.

The parent entrypoint remained
`b5314e98d1814af6e014b642591b0549b151e0d9b03e99ed9e913d30490bc638`.
The gates were written in `PREDECLARED_GATES.md` before measurements.

## What changed relative to the old Strassen paths

The earlier `strassen_fold3` and `strassen_fused` operators split the large
activation matrix into 128-row square tiles, then applied square Strassen to
each activation/weight tile pair.  That creates a reshape of all activations,
four recursive tile products at full width, per-tile reconstructions, and an
output concatenate.  At the sampler's full structural shape the audited bills
are:

| Old row-tiled operator | Bill ratio | Visible matmul calls |
|---|---:|---:|
| L1 sequential | 0.89825 | 28 |
| L1 fused | 0.90511 | 4 |
| L2 sequential | 0.81950 | 196 |
| L2 fused | 0.83837 | 4 |

The new factorization applies ordinary rectangular Strassen to the entire
`64,512 x k` left operand.  It splits rows, inner columns, and output columns
in halves; no row tiling or activation reshape is required.  A hybrid L2
schedule evaluates the seven outer products sequentially and fuses each
seven-leaf inner level, giving seven visible matmul calls and a 0.79543 bill
ratio at full width.

The prior paths were not promoted because there is no completed candidate
record in `strassen_fold3/equivalence_n14336_net0.json`—that artifact contains
only the ordinary `estimator_n14336` baseline—and the available fused wrappers
target `n_base=14,336`, not the later promoted 32,256 sampler.  The separate
pure-design L2/Strassen diagnostic is stronger negative engineering evidence:
it recorded `415.521B` analytical FLOPs, `3.922s` residual, and `807.727B`
effective compute at a raised budget.  That path is not identical to this
sampler, but it correctly warned that recursive stack/concatenate schedules
can erase arithmetic savings.

## Closed-form accounting

For a direct product, FlopScope 0.10.0 charges

```text
D(m,k,n) = m n (2k - 1).
```

One sequential rectangular Strassen level charges

```text
C1 = 7 D(m/2,k/2,n/2)
     + 5(mk + kn)/4       # input sums
     + 2mn                # output-block sums
     + 2mn                # top/bottom/final concatenates.
```

A fused level adds `7(mk+kn)/4` for the two seven-way stacks.  The hybrid L2
rule uses a sequential outer level and seven fused inner levels.  For ragged
`k,n`, the dispatcher uses the largest core divisible by two or four, computes
the one-column/one-inner remainder directly, counts the required addition and
concatenate, and chooses the least billed option from direct, L1 sequential,
L1 fused, L2 hybrid, and modeled L2 fused.  Selection depends only on operand
shapes.

The formulas matched FlopScope exactly on all 16 predeclared direct/ragged
micro-accounting cases.  Exhaustive enumeration of all `65,536` pairs
`k,n in [1,256]` found zero cases where the billed dispatcher exceeded direct
matmul.  Full-shape results:

| Strategy | Bill | Ratio | Calls |
|---|---:|---:|---:|
| Direct | 8.439202B | 1.00000 | 1 |
| L1 sequential | 7.456637B | 0.88357 | 7 |
| L1 fused | 7.485653B | 0.88701 | 1 |
| L2 sequential | 6.661992B | 0.78941 | 49 |
| L2 hybrid | 6.712771B | 0.79543 | 7 |
| L2 fully fused | 6.741787B | 0.79887 | 1 |

The fully fused L2 lower bound is already `496.125 MiB` from the two left
stacks and leaf product alone, before any reconstruction outputs or
temporaries.  Therefore it cannot pass the predeclared 512 MiB temporary gate.

## Numerical gate

Sixteen fresh trials covered full width, active columns, ragged dimensions,
and thin folded-product shapes.  All outputs were finite.

```text
maximum absolute error             5.24521e-6
maximum relative Frobenius error   6.37850e-7
gate limits                        2e-4 and 3e-6
```

A fresh 32-layer width-256 synthetic He/ReLU chain gave:

```text
relative final error       4.09856e-6   (limit 2e-5)
gate mismatches            5 / 4,194,304
gate mismatch fraction     1.19209e-6   (limit 2e-4)
```

Thus numerical association is not the failed link.

## Engineering gate

The fresh full-shape local screen reports the FlopScope decomposition, so the
residual charge can be compared directly rather than inferred from wall time.

| Strategy | Wall ratio | Residual | Bill | `bill + 1e11*residual` | Ratio vs direct |
|---|---:|---:|---:|---:|---:|
| Direct | 1.000 | 0.000045s | 8.439B | 8.444B | 1.000 |
| L1 sequential | 5.283 | 0.016870s | 7.457B | 9.144B | 1.083 |
| L1 fused | 6.195 | 0.021159s | 7.486B | 9.602B | 1.137 |
| L2 hybrid | 14.512 | 0.054923s | 6.713B | 12.205B | 1.445 |

All three exceed the predeclared 1.5x wall threshold.  More importantly, even
the cheapest effective option loses after the exact residual charge.  Reusing
this implementation throughout the early sampled layers would compound the
loss; there is no reason to risk an estimator-level or official-row run.

The folded last-three-layer products are hard-coded inside `fold3_estimator`
rather than routed through `_sample_matmul`.  Representative synthetic folded
shapes show the dispatcher correctly falls back to direct for very thin
products and uses L1 only when it is billed cheaper.  Refactoring those
closures cannot rescue the branch because the full first/early-layer products
already lose effective compute.

## Failure localization and salvage

Passed components:

- whole-row rectangular Strassen is algebraically valid and numerically stable;
- the ragged cost formula is exact under FlopScope 0.10.0;
- shape-only dispatch never increases billed FLOPs;
- removing the old row-tile reshape improves the full-shape billed ratio.

Failed link:

- the present Python allocation graph retains seven products and constructs
  multiple sum/stack/concatenate temporaries; its residual charge costs more
  than the matmul bill it removes.

Untested family remainder:

- a genuinely changed schedule using preallocated `out=` buffers or a
  Winograd reconstruction with fewer live temporaries may reopen L1.  Its kill
  condition is now sharp: on the full product it must cut L1-sequential
  residual from `0.016870s` to below roughly `0.00987s` merely to reach parity,
  and below that with safety margin.  Re-running the same allocation graph or
  only retuning tile size does not address the failure.

## Artifacts

- `PREDECLARED_GATES.md`: immutable audit gates and firewall.
- `cost_model.py`: direct, complete-core, ragged, call-count, and dispatcher
  formulas.
- `rectangular_strassen.py`: L1 sequential/fused, L2 hybrid, ragged product,
  and exact shape dispatcher.
- `estimator.py`: unpromoted subclass of random32,256; retained only as the
  killed implementation.
- `run_audit.py`: fresh-static/synthetic audit and prior-tile comparison.
- `test_exact_compression.py`: four regression tests.
- `decision.json`: machine-readable disposition and gate results.

Four tests pass.  No champion artifact was changed.
