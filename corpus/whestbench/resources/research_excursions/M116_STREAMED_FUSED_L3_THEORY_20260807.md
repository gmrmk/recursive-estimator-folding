# M116 streamed fused L3 leaf-bank theory audit

Date: 2026-08-07  
Scope: local source and prior target-free engineering records only.  No WHestBench row, target, scorer, public result, evaluation network, or champion archive was opened or changed.

## Verdict: REPAIR

The proposed **256-square, three-level, streamed fused Winograd leaf bank**
does have a valid bounded-batch algebraic schedule, but the current supplied
source is not that schedule.  The literal recursive `fused_strassen.py` route
is **KILL** because its charged `stack`/`concatenate` tree is bill-killed.
The replacement L3 Winograd schedule is **REPAIR**, not IMPLEMENT: it has no
source, FlopScope trace, numerical certificate, or measured liveness result.

Using only the target-free fused-L2 synthetic audit's non-operator live set,
the 2048-row replacement predicts `477.593750 MiB`, technically below the
stated 480-MiB ceiling but with only `2.406250 MiB` of margin.  Every larger
specified block is over.  This is too small to call a complete liveness proof
or a zero-cliff schedule; allocator behavior and the new leaf bank must be
measured under a frozen, generated-only gate before any implementation is
eligible for a fuller screen.

Further, the 2048 option makes 32 visible 343-leaf batched `matmul` calls for
one 64,512-row full-width hook, versus the frozen L2 schedule's 11 calls at
6144 rows.  The M116 premise itself localizes the preceding L3 failure to
allocation/call residual; the generated L2 audit already shows 166 visible
calls versus its parent's 137.  There is no principled basis for claiming this
new 32-call schedule clears the residual wall.  Do not score it or tune a
block height.  The only authorized next action is a separately frozen,
generated-only repair gate for a new preallocated source.

## Terminology and current level

There are two distinct local implementations which should not be conflated.

* `strassen_fused/fused_strassen.py` is **classic Strassen**, not the
  lower-overhead Winograd operand variant.  Its default is `strassen_levels =
  2`; the supplied `estimator_l1_n14336.py` and `estimator_l2_n14336.py`
  select levels one and two respectively.  Despite its module docstring, it
  contains no M116 L3 configuration.  It creates `fnp.stack` operands and
  returns recursively reconstructed `fnp.concatenate` arrays.
* `two_axis_winograd/two_level_winograd.py` is the current proven
  **two-level fused Winograd-equivalent** schedule: seven preallocated
  operands at each level, one 49-leaf batched call per row block, then direct
  folds into a preallocated output.  `two_axis_winograd/cost_model.py`
  identifies its L2 row height as 6144.  Its target-free synthetic audit
  records `111.453125 MiB` operator workspace and a `492.44140625 MiB` peak.
* The M116 proposal in `headroom_recursion/MUTANT_MATH_EXECUTION_PLAN_20260807.md`
  is therefore properly called a **streamed, preallocated, three-level
  Winograd leaf bank with 343 Strassen-family products**.  Calling a literal
  port of `fused_strassen.py` “L3 Winograd” would be false and would conceal
  both its `stack`/`concatenate` bill and its allocation tree.

The rest of this note analyzes only the viable interpretation: the Winograd
operand/fold identities used by the proven L2 operator, extended exactly one
level to a 256 x 256 tile with 32 x 32 leaves.

## FlopScope bill, exactly

Let

```text
D(m, k, n) = m*n*(2*k - 1)
S = m*k + k*n + m*n.
```

The local audited convention charges one FLOP for every element written by an
add, subtract, `copyto`, stack, or concatenate.  Basic slices are views.  The
preallocated Winograd pack intentionally charges seven filled child slots per
operand bank, including identity children; its seven-operation fold charges
seven output-quadrant writes.  A level therefore has explicit pack/fold cost
`7*S/4` in addition to its child products.

For a complete L3 core (each dimension divisible by eight), the bill is

```text
W3(m,k,n) = 343*D(m/8,k/8,n/8) + 651*S/64.
```

The `651/64` is not a heuristic:

```text
outer pack/fold:                         7/4  = 112/64
seven middle pack/folds:              7*7/16 = 196/64
49 innermost pack/folds:            49*7/64  = 343/64
                                                        -----
                                                        651/64.
```

For the intended `k=n=256` core this becomes

```text
leaf products       = 343*D(m/8,32,32) = 86,436*m
all left fills      = (448 + 784 + 1,372)*m = 2,604*m
all output folds    = (448 + 784 + 1,372)*m = 2,604*m
once-only right fill= 114,688 + 200,704 + 351,232 = 666,624
W3(m,256,256)      = 91,644*m + 666,624.
```

Thus no fill, copy, or reconstruction work has been hidden in the leaf
matmul.  The once-only right fill is paid once per complete product, not once
per row block.  All row-dependent terms are linear in row count, so splitting
into blocks of sizes divisible by eight preserves this bill exactly.

For comparison at `m=64,512`:

| schedule | exact billed FLOPs |
|---|---:|
| direct | 8,439,201,792 |
| fused L1 Winograd | 7,427,768,320 |
| fused L2 Winograd | 6,582,603,776 |
| proposed fused L3 Winograd | 5,912,804,352 |

L3 saves `669,799,424` billed FLOPs over L2 for this one square hook.  That
is real arithmetic headroom, but it is not an effective-compute certificate.

### Literal `fused_strassen.py` is bill-killed

The recursive source instead pays classic-Strassen arithmetic plus
`fnp.stack` and three `fnp.concatenate` operations at every level.  Per level
its billed wrapper work is

```text
5*(m*k/4) + 5*(k*n/4) + 2*m*n       # arithmetic sums/fold
+ 7*(m*k/4 + k*n/4)                 # two seven-way stacks
+ 2*m*n                             # top, bottom, final concatenations
= 3*m*k + 3*k*n + 4*m*n.
```

At 256-square L3 this wrapper term alone is
`655,360*m + 1,146,880*m + 2,007,040*m = 3,809,280*m`, far above direct
arithmetic (`130,816*m`).  No batching removes these charged writes.  A
literal L3 recursion in that file is therefore not a candidate under the
stated FlopScope model.

### Calls and partition identity

For a fully fused, preallocated L3 core, every row block performs precisely
one batched `fnp.matmul` with logical shapes

```text
left:  (7, 7, 7, rows/8, 32)
right: (7, 7, 7, 32, 32)
out:   (7, 7, 7, rows/8, 32).
```

For `m=64,512`, all requested block heights leave an eight-divisible tail:

| block rows | blocks / batched calls | final tail rows | exact per-block bill | L3 less than L2 per full block |
|---:|---:|---:|---:|---:|
| 2,048 | 32 | 1,024 | 188,353,536 | 20,923,392 |
| 4,096 | 16 | 3,072 | 376,040,448 | 42,198,016 |
| 8,192 | 8 | 7,168 | 751,414,272 | 84,747,264 |
| 16,384 | 4 | 15,360 | 1,502,161,920 | 169,845,760 |

The per-block numbers include the once-only right fill only if the displayed
block is considered a standalone product; for a streamed full product, charge
the 666,624 right-fill elements once across all blocks.  The full-product
formula above, not a sum of standalone product bills, is the required bill.

There are no output or contracted-dimension tails for a 256-square hook.  A
general dispatcher must require `m,k,n` core divisibility by eight, otherwise
compare direct, frozen L1, frozen L2, and a correctly charged ragged L3 path;
it must never silently pad, truncate, or reuse the 256-square formula.

## Bounded legal leaf-bank schedule

All 343 leaves *can* be put into one bounded batched matmul without a view
trick, provided they are materialized into disjoint owned buffers:

1. Pack the seven outer right operands, then their 49 middle operands, then
   their 343 leaf operands.  The 343 right leaves are distinct affine
   combinations and must occupy a real `(7,7,7,32,32)` bank.
2. For one row block, pack outer left, pack middle left, then pack all 343
   leaf-left operands.
3. Invoke the single batched leaf matmul into a separate 343-leaf product
   bank.
4. Fold leaf products into the now-dead middle-left storage, fold that into
   the now-dead outer-left storage, then fold directly into the output slice.

The middle-left and outer-left aliases are legal only *after* all of their
child operands have been consumed.  They are not overlapping inputs to the
leaf matmul, and no fold may write an output that overlaps its product source.
This is the exact L2 liveness discipline extended one level.

For `B` rows, the owned row-dependent bank sizes in float32 elements are

```text
outer scratch (left, then outer products)         7*(B/2)*128 =  448*B
middle scratch (left, then middle products)    7^2*(B/4)*64  =  784*B
leaf-left bank                                7^3*(B/8)*32  = 1,372*B
leaf-product bank                             7^3*(B/8)*32  = 1,372*B
                                                                  ------
row scratch                                               = 3,976*B.
```

The right-bank allocation, if all three construction levels remain owned, is

`114,688 + 200,704 + 351,232 = 666,624` elements (`2.54296875 MiB`).
It could be reduced only by a separately proved packing/liveness repair; it
may not be treated as a broadcast view, because the children are not repeated
copies.  The complete operator allocation at maximum `m=64,512` also contains
the `64,512 x 256` final float32 output (`63 MiB`):

```text
workspace(B) = 4 * (256*64,512 + 3,976*B + 666,624) bytes.
```

| block rows | row scratch | right banks | output | exact workspace | inferred peak using L2 base `380.98828125 MiB` |
|---:|---:|---:|---:|---:|---:|
| 2,048 | 31.062500 MiB | 2.542969 MiB | 63 MiB | 96.605469 MiB | 477.593750 MiB |
| 4,096 | 62.125000 MiB | 2.542969 MiB | 63 MiB | 127.667969 MiB | 508.656250 MiB |
| 8,192 | 124.250000 MiB | 2.542969 MiB | 63 MiB | 189.792969 MiB | 570.781250 MiB |
| 16,384 | 248.500000 MiB | 2.542969 MiB | 63 MiB | 314.042969 MiB | 695.031250 MiB |

For the exact level-2 comparison, its preallocated schedule has row scratch
`448*B + 784*B + 784*B = 2,016*B` elements and right banks of
`114,688 + 200,704 = 315,392` elements.  Its maximum-product workspace is

```text
workspace_L2(B) = 4 * (256*64,512 + 2,016*B + 315,392) bytes.
```

| block rows | L2 workspace | L2 inferred peak | L3 workspace | L3 inferred peak |
|---:|---:|---:|---:|---:|
| 2,048 | 79.953125 MiB | 460.941406 MiB | 96.605469 MiB | 477.593750 MiB |
| 4,096 | 95.703125 MiB | 476.691406 MiB | 127.667969 MiB | 508.656250 MiB |
| 8,192 | 127.203125 MiB | 508.191406 MiB | 189.792969 MiB | 570.781250 MiB |
| 16,384 | 190.203125 MiB | 571.191406 MiB | 314.042969 MiB | 695.031250 MiB |

The target-free L2 base is its measured synthetic peak less its audited
operator workspace: `492.44140625 - 111.453125 = 380.98828125 MiB`.  It
represents live base activations, weights, interpreter/allocator state, and
other non-operator liveness which the M116 claim is required to include.  The
2048 result is only an inference from that base, so it is not a safe margin.

### Illegal or unproved shortcuts

The following are counterexamples to the claimed bounded-bank result and must
fail a gate rather than be rationalized as views.

* `fnp.stack` at any level allocates and writes a new seven-way bank; it is
  already paid in the classic source and defeats the preallocated plan unless
  eliminated in favour of explicit owned destinations.
* `reshape` is only a view for compatible contiguous storage.  A transpose,
  advanced index, non-contiguous slice, or a batch-axis reshape that needs
  contiguity can allocate.  `reshape` cannot manufacture the affine leaf
  operands and cannot be billed as universally free.
* Broadcasting a single right leaf across the `(7,7,7)` batch dimensions is
  mathematically wrong: each path has a different affine right operand.
  Broadcasting is only lawful for an actually identical dimension, not a way
  to avoid a 343-child bank.
* Folding into a left bank before every required child is packed, or using the
  output slice as left input without a full ownership proof, corrupts future
  children.  The L1 owned-buffer proof does not automatically extend across
  three recursive packing levels.
* `fnp.concatenate` creates a fresh result and is charged one write per
  destination element.  It is forbidden in the hot L3 path; direct folds into
  the final output are required.

## Float32 reconstruction risk

The schedule is algebraically exact over reals, but not bitwise equal to
direct float32 GEMM.  It adds another affine transformation and another
seven-operation fold over the already non-associative L2 schedule.  Cancellation
in the transformed operands/products can amplify relative error, and even a
very small absolute difference can flip a ReLU whose direct preactivation is
near zero.  The prior L2 depth-32 parity result (`4.24263e-6` relative and one
gate mismatch in 4,194,304) is evidence for L2 only; it is not a certificate
for L3.  No float64 escape hatch, tolerance-dependent branch, or post-hoc
repair is permitted: all arithmetic must remain accounted float32 and use a
single fixed comparison protocol.

## Strictly target-free generated gate (for a future liveness repair only)

This is deliberately a prospective gate, not authorization to revive the
killed schedule.  Freeze its source hash, widths, block height, synthetic
seeds, and acceptance thresholds before execution.  Generate only local
float32 matrices and generated width-256/depth-32 networks; do not read any
benchmark row, truth, scorer, public telemetry, or evaluation network.

1. **Static bill and shape gate.** Enumerate `m in {32, 512, 2,048, 64,512}`
   plus every requested block boundary/tail, and `k,n in 1..256`.  The
   dispatcher must select the minimum of direct, frozen L1, frozen L2, and
   fully charged L3.  Independently expand every L3 term, prove no selected
   bill exceeds direct or L2, and assert exactly `ceil(m/B)` core calls for a
   valid core (plus explicitly charged ragged tails, if any).
2. **Primitive-accounting gate.** In an official local FlopScope context,
   compare measured FLOPs with an independent expansion.  Trace each `matmul`
   and require the logical L3 leaf shapes above.  Require zero hot-path
   `stack`/`concatenate`; any `copyto`, add, subtract, or materialization must
   appear in the formula.  If a reshape is retained, assert both
   `shares_memory` and no allocation in an isolated context; otherwise charge
   and reject it.
3. **Liveness/alias gate.** Inventory every owned allocation in bytes,
   including base activations, final output, all right banks, all row scratch,
   and temporaries.  Assert that only the two documented reuse pairs overlap,
   and that inputs to each `matmul`/fold are disjoint from its destination.
   In fresh one-thread generated processes, require a measured whole-process
   peak strictly below a predeclared safety threshold with a nontrivial margin
   (for example `<=464 MiB` for a 480-MiB deployment ceiling); a calculated
   `479.x` is a fail, not a pass.
4. **Numerical gate.** On frozen random float32 probes and a generated
   32-layer width-256 network, require finite output, direct-comparison
   relative Frobenius error `<=3e-6` on each product, depth final relative
   error `<=2e-5`, and ReLU mismatch fraction `<=2e-4`.  Report maximum
   absolute error and every mismatch; do not use values to change the
   schedule.
5. **Residual/cliff gate.** Compare only generated, matched direct/L2/L3
   processes under the same thread and allocator settings.  Require every
   run to finish inside a frozen timeout, no outlier peak above the safety
   threshold, and a predeclared effective-compute improvement over L2 after
   the full FlopScope residual charge.  A better analytical bill without this
   result is a failure.

Decision rule: an implementation is eligible only if all five gates pass in
one frozen campaign.  A mismatch in bill, trace, alias proof, finite/parity
result, timeout, or peak is an immediate **KILL** for that exact source and
configuration.  A liveness-reducing mechanism that changes the resource
algebra may start a new child, but it must repeat all gates and cannot inherit
the killed M116 result.
