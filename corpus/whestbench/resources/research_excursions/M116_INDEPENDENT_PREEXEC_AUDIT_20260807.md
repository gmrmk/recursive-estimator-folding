# M116 independent pre-execution cleanroom audit

Date: 2026-08-07  
Scope: source, local target-free documentation, and cheap generated-only tests
only. No champion, public or contest material, target data, evaluation network,
manifest, campaign, or claim was opened, created, or run.

## Verdict: REPAIR — no execution authorization

The L3 core has a sound static algebra, a legal two-stage scratch reuse plan,
and its 2,048-row tail is divisible by eight.  It is **not** ready to freeze or
run.  The public chooser can return an L1/L2 bill while this implementation
performs a direct product, so an advertised selected cost can be lower than the
operation actually executed.  In addition, the only full-geometry memory
number is a 477.593750-MiB inference, which fails the proposed <=464-MiB
safety gate, and neither a fixed runtime nor depth-32/residual evidence is
present.

This is a repairable source audit finding, not a reason to consume a one-shot
lifecycle.  The current exact source/configuration must not be executed.

## Reviewed identities

| item | SHA-256 |
|---|---|
| `m116_streamed_l3_draft/__init__.py` | `51aff82cb30bd36eca83cffd1bd2ead51fcc45b6ff120a7810bd99391cf28ce7` |
| `m116_streamed_l3_draft/cost_model.py` | `db2b13f7ae85339f5d9b1b3984db1d952f273f8957cbdaa0cd0e0a3e56511412` |
| `m116_streamed_l3_draft/lifecycle.py` | `3eae4295ba697a9ed3888f70d0a08538f05d46e86993a298c471f999a86a42f8` |
| `m116_streamed_l3_draft/streamed_l3.py` | `567caf7bd3f8e14874936876bbc8373af78415de36ab9a331dbee1749ff9d859` |
| `m116_streamed_l3_draft/test_streamed_l3.py` | `f3fe6c1ca895201b3b815c537754fc6ee6811647fde128304f78cdcd046dcc69` |
| `M116_STREAMED_FUSED_L3_THEORY_20260807.md` | `ae044f785078dc7c410594cd30e92aaf9afbdb443bfb806d08da91b373f26f9a` |
| `M116_STREAMED_FUSED_L3_IMPLEMENTATION_20260807.md` | `de6166185b027eea9bfb31f1475a56a4790898e71a1bb2de5bf5f6e8f6f72370` |

No `m116_streamed_l3_draft/M116_ONE_SHOT_CLAIM.json` existed at audit time.

## A. L3 algebra and call/shape contract — PASS as a static core only

For one Winograd level, `_pack_left` and `_pack_right` each write three copied
and four add/subtract child quadrants.  Under the stated FlopScope convention
that is exactly seven writes, not four: `7mk/4` for a left pack and `7kn/4`
for a right pack. `_fold` makes seven output-quadrant writes, `7mn/4`.
Recursing three levels therefore gives

```text
W3(m,k,n) = 343 D(m/8,k/8,n/8) + 651 (mk + kn + mn) / 64,
D(m,k,n) = mn(2k - 1).
```

The coefficient is `112/64 + 196/64 + 343/64 = 651/64`.  For `k=n=256`,
the one-time right pack is

```text
7kn/4 + 49kn/16 + 343kn/64
= 114,688 + 200,704 + 351,232 = 666,624,
```

and each of the streamed left-pack and fold terms is
`(448 + 784 + 1,372)m = 2,604m`. Thus

```text
W3(m,256,256) = 91,644m + 666,624.
W3(2,048,256,256)  =   188,353,536.
W3(64,512,256,256) = 5,912,804,352.
```

`64,512 = 31*2,048 + 1,024`; both the fixed block and the final 1,024-row
tail divide by eight. More generally, because `2,048` divides by eight, any
`m` eligible for L3 leaves an eight-divisible final tail. The source therefore
performs 32 visible batched `matmul` calls at the full shape (343 leaf products
per call; 10,976 logical leaf GEMMs). The final logical left leaf shape is
`(7,7,7,128,32)` and the shared right leaf shape is `(7,7,7,32,32)`.

## B. Dispatcher/cost identity — REQUIRED REPAIR

`best_bill` compares `direct`, `l1_batched`, `l2_batched`, and `l3_batched`.
`StreamedL3Winograd.multiply`, however, implements only the L3 branch. Every
other selected strategy takes `xp.matmul(left, right, out=output)` while
recording the lower selected L1/L2 strategy in `last_selected_strategy`.
The committed test explicitly accepts this mismatch for `(34,256) @
(256,256)`: selected `l1_batched`, executed `direct`.

This invalidates any dispatcher or cost claim that treats `best_bill.total` as
the bill of this class. It also makes candidate `core_calls` metadata false for
L1/L2, because all candidates are assigned `ceil(m/2048)` although no L1/L2
implementation or their distinct blocking contract exists here.

Minimal exact repair (choose one and test it):

1. Make this class expose only `direct` and `l3_batched`: default the
   non-eight-divisible path to `direct`, and remove L1/L2 from the operational
   chooser. Keep analytical L1/L2 helpers only under names that cannot be
   confused with an executable bill; or
2. actually implement L1 and L2 in this class, with their own owned-buffer,
   call-count, trace, and bill tests.

In either case, store the executed bill and require in tests that selected
strategy, executed strategy, `last_total_matmul_calls`, and FlopScope bill
all agree on L3, L1/L2 if implemented, and direct fallback. The current
`last_selected_strategy != last_strategy` test must become a failure, not a
documented feature.

## C. Allocation/liveness and peak — static ledger passes; deployment gate fails

The source-owned allocation at `max_m=64,512`, `B=2,048`, is exactly

```text
output                   16,515,072 elements = 63.000000 MiB
row scratch                 8,142,848 elements = 31.062500 MiB
right banks                   666,624 elements =  2.542969 MiB
total                      25,324,544 elements = 96.605469 MiB
                                                       101,298,176 bytes.
```

The liveness reuse is algebraically legal: leaf products are folded only after
all middle-left children have been consumed, then middle products are folded
only after all outer-left children have been consumed. `leaf_left`,
`leaf_products`, every right bank, and `output` are separate allocations.
The code has no hot-path `stack`, `concatenate`, or `reshape`.

The inferred base was calculated as
`492.44140625 - 111.453125 = 380.98828125 MiB` from the predecessor L2
measurement. The predecessor's 111.453125-MiB operator ledger *already
included its own 63-MiB output*, so adding the L3's 96.605469-MiB complete
ledger does **not** double count the output if this is truly a replacement
run:

```text
380.98828125 + 96.60546875 = 477.593750 MiB.
```

That resolves the arithmetic double-count question, but not liveness. It is
an inference from a different operator/process, only 2.406250 MiB below 480,
and **13.593750 MiB above** the prospective <=464-MiB safety gate. It is a
failed deployment gate, not usable headroom.

The present API cannot legally count a caller-buffer reuse as a saving:
`__init__` always allocates `self.output`, `multiply` has no `out=` argument,
and `ownership_ok` rejects output/input sharing. Reusing `left` or a caller
output would change the ownership contract and needs a new liveness proof
(including proof that every input row is packed before it is overwritten), a
new peak measurement, and a new source identity. It cannot reduce this
source's claimed 96.605469 MiB.

`ownership_ok` is nevertheless only a post-hoc aggregate check; the tests use
the NumPy backend, not an operation-by-operation FlopScope alias proof. Add
explicit tests that every pack/fold/matmul destination is disjoint from its
live inputs, and measure allocations during `multiply` in the frozen backend.

## D. FlopScope boundary — microcheck passes; evidence is incomplete

Observed, generated-only local runtime:

```text
Python 3.14.4 (MSC v.1944), NumPy 2.4.6, FlopScope 0.10.0+np2.4.6
trace_generated_probe(rows=512):
{strategy: l3_batched, core_calls: 1, matmul_calls: 1,
 billed_flops: 47,588,352}
```

The 13-test suite and `py_compile` pass there. The aggregate 512-row result
equals the static formula. `fnp.asarray(left/right)` is evaluated *inside* the
`BudgetContext`; for this contiguous float32 probe it is a nonmaterializing
conversion and costs zero. The preallocated `fnp.empty` calls occur before the
context and have FlopScope cost zero, so this trace is an operator-FLOP check,
not an allocation/whole-process check. RNG generation, scaling, and `astype`
are also deliberately outside the context.

Consequently the trace does cover the `multiply` pack/copy/add/subtract,
batched matmul, and folds for that one L3 probe, but it does **not** establish
the full deployment bill, setup cost, peak, or primitive sequence. It records
only aggregate FLOPs, not primitive counts/shapes, and there is no frozen
trace artifact. A system-Python attempt failed before collection because it
has no NumPy, further demonstrating that the source itself does not select a
runtime.

The observed runtime files are evidence only, not a source pin:

| observed file | SHA-256 |
|---|---|
| `work/whest-v014/Scripts/python.exe` | `4b8c3912806b3c1591ba3cb403bff77ad309c3fe5756f87c20b7a6f8f0174262` |
| `.../numpy/__init__.py` | `65d5e777b6d662ba19cb80800bef3eb999eda7aee51eea62c308feabf679dba4` |
| `.../flopscope/__init__.py` | `f49c7b804649223c077505a3380a6fb2baa691e783564be433543fa0ae6f1b06` |

The four one-thread environment variables are useful but do not pin the
interpreter, NumPy/FlopScope versions and hashes, BLAS build, or allocator.

## E. Numerical, residual, and lifecycle gates — NOT PRESENT

The unit tests establish two shallow float32 product comparisons (512 and
2,048 rows) with relative Frobenius error <=3e-6. `numerical_diagnostics`
uses float64 only to measure the result; it does not change the float32
operator. There is no frozen generated width-256/depth-32 propagation,
ReLU-gate mismatch, residual-wall, timeout, or full-shape process-peak test.
Those omissions alone prohibit execution authorization.

`FixedPathLifecycle.claim` is atomic (`O_CREAT | O_EXCL`) for its draft-local
sentinel, but it is only a primitive. No execution entry point invokes it
before loading/allocating work; its arbitrary `purpose` text binds no source,
runtime, configuration, output path, or acceptance results. The tests claim a
temporary path rather than exercise a fixed frozen runner. It is therefore
not yet a fixed one-shot deployment lifecycle. The absence of the actual
sentinel is correct for this audit.

## Minimal repair list before a new pre-execution audit

1. Repair the executable dispatcher/accounting identity exactly as in section
   B; prohibit a lower non-executed selected bill.
2. Add a source-owned runtime lock/launcher that asserts exact interpreter,
   NumPy, FlopScope, BLAS/thread, and relevant package hashes before any
   trace; regenerate the source hash table afterward.
3. Freeze generated-only config/seeds and emit a primitive FlopScope artifact
   for direct and every executable dispatch path, including 2,048 blocks and
   a full-shape call/tail accounting expansion. Include all conversions that
   materialize in the charged boundary.
4. Add allocation/alias instrumentation and fresh one-thread whole-process
   generated measurements. The current 477.593750-MiB inference fails the
   <=464-MiB gate; do not attempt an output-reuse shortcut without a distinct
   source, API, and proof.
5. Add frozen float32 depth-32 direct/L3 parity, finite, ReLU mismatch,
   residual-wall, timeout, and matched direct/L2/L3 tests. Predeclare all
   acceptance thresholds.
6. Implement a real fixed runner that validates the frozen identities and
   obtains the atomic claim before irreversible work. It must fail closed and
   bind source/config/runtime/output/acceptance hashes; do not create it or a
   claim under this audit.

Only after all six repairs and a fresh independent audit can the appropriate
verdict become `PASS_TO_FREEZE`. This audit is **REPAIR**, and authorizes no
manifest, claim, campaign, target access, or deployment execution.
