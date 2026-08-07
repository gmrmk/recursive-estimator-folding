# M116b in-place row-streamed L3 implementation

Date: 2026-08-07  
Scope: cleanroom, target-free child under
`work/scorefloor_generation/m116b_inplace_l3_draft`. M116 and prior operators
were read-only references and were not modified. Champion archives, benchmark
rows, truths, scorers, public telemetry, and evaluation networks were not
opened. No manifest, permanent claim, full campaign, or full-height process
run was created.

## Outcome and readiness

M116b changes the failed liveness mechanism rather than changing a block
height: the full 63-MiB owned output is removed. Each complete row block is
fully captured into owned three-level Winograd operands, multiplied as one
343-leaf batch, and folded back into that same now-dead caller-owned block.

Readiness verdict: **READY FOR INDEPENDENT PREEXECUTION AUDIT; NOT READY FOR A
PERMANENT OR FULL CAMPAIGN.** The isolated implementation, cheap generated
parity probes, overlap tests, independent bill expansion, and local FlopScope
microtrace pass. Whole-process peak, depth-32 parity, and residual wall remain
unmeasured and must be frozen before an authorized campaign.

## New child surface

| file | role |
|---|---|
| `cost_model.py` | target-shape direct reference, executable-L3/unsupported dispatcher, exact L3 bill, independent row expansion |
| `inplace_l3.py` | fixed-B owned banks, explicit three-level pack/fold, in-place block reconstruction, ownership checks, diagnostics, pinned FlopScope trace |
| `test_inplace_l3.py` | cheap generated-only bill, parity, tail, overwrite, alias, memory, primitive, and runtime-surface tests |

The runtime surface is deliberately narrow:

```text
input:                 float32 (m,256) and disjoint float32 (256,256)
left storage:          writable C-contiguous (overlapping/strided rows rejected)
successful strategy:   l3_inplace only
block height:          exactly 2048 maximum rows
successful return:     the identical caller left array
owned full output:     none
other shapes/strategy: fail closed before mutation
```

The dispatcher never reports L1 or L2 because this child does not implement
them. It compares the executable L3 bill to a direct reference. If direct is
cheaper, if a row tail is not divisible by eight, or if the width is not the
exact target geometry, the result is `unsupported`. `multiply_inplace` raises
`UnsupportedInplaceShape` before right packing or any input write. There is no
mislabelled direct execution and no overlapping direct `out=left` call.

## Independent owned-byte derivation

For fixed `B=2048`, the row-dependent owned buffers are

```text
outer scratch       7*(B/2)*128       =   448*B elements
middle scratch      49*(B/4)*64       =   784*B elements
leaf-left bank      343*(B/8)*32      = 1,372*B elements
leaf-product bank   343*(B/8)*32      = 1,372*B elements
                                             -----
row banks                                  3,976*B elements.
```

The fixed right hierarchy is

```text
outer right         7*128*128          = 114,688 elements
middle right        49*64*64           = 200,704 elements
leaf right          343*32*32          = 351,232 elements
                                               -------
right banks                                  666,624 elements.
```

Therefore

```text
owned elements = 3,976*2,048 + 666,624 = 8,809,472
owned bytes    = 4*8,809,472            = 35,237,888
owned MiB      = 35,237,888 / 2^20      = 33.60546875 MiB.
```

This is exactly 63 MiB below M116's `96.60546875 MiB` full-height operator
ledger because M116b owns no `64,512 x 256 x 4` output. Using only the prior
target-free synthetic L2 base liveness,

```text
base non-operator peak = 492.44140625 - 111.453125
                       = 380.98828125 MiB
M116b inferred peak    = 380.98828125 + 33.60546875
                       = 414.59375000 MiB.
```

The inference leaves `65.40625 MiB` below the 480-MiB theory ceiling, versus
only `2.40625 MiB` for M116. It is still an inference, not a process-peak
measurement or deployment certificate.

## Blockwise overwrite proof

Let the current caller slice be `A_r = left[start:stop,:]`, with even block
height divisible by eight and `stop-start <= 2048`.

1. Before the row loop, all 343 right leaves are materialized into owned banks.
   The API rejects any `shares_memory(left,right)` relationship and also
   rejects either operand sharing with owned workspace.
2. Writable C-contiguous left storage is required, excluding internal row
   overlap and strided-view counterexamples. For `A_r`, `_pack_left` first creates all seven outer operands in owned
   `outer_scratch`, then all 49 middle operands in owned `middle_scratch`, then
   all 343 leaf operands in owned `leaf_left`. No destination aliases `A_r`.
3. The single batched matmul reads only `leaf_left` and `leaf_right`, writing
   disjoint `leaf_products`. At its return, every mathematical dependency on
   the original entries of `A_r` has been consumed; `A_r` is dead.
4. The first fold overwrites dead middle-left storage with 49 middle products.
   The second overwrites dead outer-left storage with seven outer products.
   The final fold writes the complete output directly into `A_r`.
5. Every memory access for this iteration is either an owned bank or rows
   `[start:stop)`. No later source row is addressed. The dynamic observer test
   verifies that after blocks ending at rows 2048 and 4096, the complete
   unprocessed suffix remains bitwise equal to its original value.

Thus sequential overwrite is safe by capture-before-write and disjoint row
support. The two-full-block-plus-512-row-tail probe also confirms the final
complete L3 tail behaves identically.

## Billing and calls

Writing the final fold into caller storage changes allocation ownership, not
the charged arithmetic. The exact complete-core bill remains

```text
W3(m,k,n) = 343*D(m/8,k/8,n/8)
          + 651*(m*k + k*n + m*n)/64,
D(m,k,n)  = m*n*(2*k - 1).
```

The independent expansion separately sums all per-block leaves, three left
pack levels, three output folds, and the once-only right hierarchy. It agrees
at every tested size:

| rows | exact bill | core calls |
|---:|---:|---:|
| 512 | 47,588,352 | 1 |
| 2,048 | 188,353,536 | 1 |
| 4,096 | 376,040,448 | 2 |
| 4,608 | 422,962,176 | 3 |
| 64,512 | 5,912,804,352 | 32 |

The pinned local FlopScope microtrace at 512 generated rows observed exactly
`47,588,352` billed FLOPs and one leaf matmul call.

## Cheap verification

Executed with the local WHest/FlopScope Python runtime:

```text
work/whest-v014/Scripts/python.exe -m unittest test_inplace_l3.py
work/whest-v014/Scripts/python.exe -m py_compile cost_model.py inplace_l3.py test_inplace_l3.py
```

Result: `11` tests passed. They cover:

* dense 512-row in-place parity and identity of the returned left object;
* 4608 rows as two full blocks plus a 512-row tail;
* bitwise preservation of every unprocessed suffix at each block boundary;
* rejection of a right operand aliased into left before mutation;
* fail-closed unsupported/direct-reference behavior before mutation;
* fail-before-mutation behavior for noncontiguous and read-only left storage;
* exact bills, independent expansions, and call counts;
* absence of hot `stack`, `concatenate`, and `reshape` calls;
* the exact no-output memory ledger and fixed runtime surface;
* pinned one-thread FlopScope tracing and fail-closed unavailability behavior.

No manifest, lifecycle claim, full-height allocation, depth-32 campaign, or
permanent run was performed.

## Independent-audit gate

An independent preexecution audit should hash and inspect this isolated source,
repeat primitive-level bill traces at one block and a multi-block tail, prove
the two buffer-reuse transitions are nonoverlapping, and freeze process-peak,
depth-parity, residual-wall, timeout, and no-retry gates. Only after those
checks may a separate manifest be created. Any mutation of B, dispatcher,
buffer ownership, or thresholds constitutes a new child.
