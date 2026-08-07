# M116b independent pre-execution audit

Date: 2026-08-07  
Scope: isolated m116b_inplace_l3_draft source, cheap local generated-only tests,
and local target-free predecessor accounting only. No champion archive, public
or contest material, target, scorer, network, manifest, claim, permanent run,
or full campaign was opened, created, or run.

## Verdict: PASS_TO_BUILD_CAMPAIGN (not PASS_TO_RUN)

This exact B=2,048 source clears the static defect that blocked M116. It
exposes one executable identity, has no billed-but-unimplemented fallback,
owns no full-height output, and has a valid capture-before-overwrite schedule.
It is suitable only as frozen input to build a hash-bound generated-only
runner. No runner exists yet, so this is not authorization to execute a
campaign, create a claim, touch target material, or infer a deployment result.

The projected 414.59375000 MiB is arithmetically non-double-counted under a
specific replacement-process ownership assumption. It is not a new
whole-process peak measurement.

## Frozen identities reviewed

| item | SHA-256 |
|---|---|
| m116b_inplace_l3_draft/__init__.py | 67d73deafc7ce01553dfe396f95c30c0de4fcf556d533626219df063e76bfee5 |
| m116b_inplace_l3_draft/cost_model.py | c2d683adea20582d7d85a740f8109cbb83cb9ac2bc9351c4685f8985dab595ed |
| m116b_inplace_l3_draft/inplace_l3.py | 114d19664317409a170ff937de72ad4527d657ea31ab0500ca76f79cf6d99e83 |
| m116b_inplace_l3_draft/test_inplace_l3.py | 25bf60c70e33fc4f0419f31dabe8f92d3154387c9a0893744ccbb8a851a98d0e |
| M116b implementation note | 396302c171622e89ed5b0bd9a57fcd46a2daea04bd07f786f598a90324634c23 |
| predecessor raw audit: two_axis_winograd/audit.json | 102b39c7c84c41c217918e9534fd67b21b7a78b88bccb994a3f662072bcacdce |
| predecessor L2 operator source | 718c45f000ef6ca2852e39df9c118945390c963612d17d68c3dffd88510ad855 |

Observed test runtime only, not a source pin: Python executable
4b8c3912806b3c1591ba3cb403bff77ad309c3fe5756f87c20b7a6f8f0174262;
NumPy 2.4.6 initializer
65d5e777b6d662ba19cb80800bef3eb999eda7aee51eea62c308feabf679dba4;
and FlopScope 0.10.0+np2.4.6 initializer
f49c7b804649223c077505a3380a6fb2baa691e783564be433543fa0ae6f1b06.

## A. Three-level Winograd identity, bill, and calls: PASS

For one level, the code writes these left operands:

~~~
L0=A11, L1=A12, L3=A22, L4=A21+A22,
L5=L4-A11, L6=A11-A21, L2=A12-L5.
~~~

Its right operands are:

~~~
R0=B11, R1=B21, R2=B22, R4=B12-B11,
R5=B22-R4, R6=B22-B12, R3=R5-B21.
~~~

With Pi=Li*Ri, its fold writes:

~~~
C11=P0+P1
C12=P0+P5+P4+P2
C21=P0+P5+P6-P3
C22=P0+P5+P6+P4.
~~~

Substitution gives the four quadrants of A*B. Applying this bilinear
identity to all seven children twice more gives 343 independent 32 x 32 leaf
products followed by three inverse folds. No right leaf is broadcast and no
affine operand is manufactured by a view.

Each level writes seven child quadrants for a pack or fold, including the
three copied child slots. Under the local FlopScope convention:

~~~
D(m,k,n) = m*n*(2*k-1)
W3(m,k,n) = 343*D(m/8,k/8,n/8)
            + (7/4 + 49/16 + 343/64)*(m*k + k*n + m*n)
          = 343*D(m/8,k/8,n/8) + 651*(m*k + k*n + m*n)/64.
~~~

At the sole executable width, k=n=256:

~~~
leaf products                 86,436*m
left packs                     2,604*m
output folds                   2,604*m
once-only right hierarchy        666,624
W3(m,256,256)              91,644*m + 666,624.
~~~

Thus W3(2,048)=188,353,536 and W3(64,512)=5,912,804,352. The independent
row expansion agrees at 512, 2,048, 4,096, 4,608, and 64,512 rows and charges
the right hierarchy once. Since 64,512=31*2,048+1,024 and both lengths divide
by eight, the target has exactly 32 visible batched leaf matmul calls.

## B. Capture-before-overwrite, tail, and disjointness: PASS

For current X=left[start:stop,:], where rows is 2,048 or the final 1,024:

1. Outer, middle, and leaf packs complete into pairwise-disjoint owned banks
   before X is written. All 343 affine functions of original X are therefore
   captured in leaf_left.
2. The batched leaf GEMM reads leaf_left and leaf_right and writes only the
   disjoint leaf_products. On its return no operation uses X as a source.
3. Folding leaf products into middle_scratch is legal because all middle-left
   children were consumed to form leaf_left. Folding middle products into
   outer_scratch is likewise legal because all outer children were consumed to
   form middle_left. These are dead-left-to-product reuse transitions.
4. Only the final fold writes X. The loop addresses no rows outside
   [start,stop); writable C-contiguous two-dimensional left storage has
   disjoint such row slices, so a processed block cannot modify any future
   block or the tail.

Before right packing or an input write, ownership_ok rejects left/right
overlap and all operand/owned-bank or owned-bank/owned-bank overlap. Right is
only read while copied into its owned three-level hierarchy, then is untouched
by the row loop. This proves the relevant disjointness under the NumPy /
FlopScope shares_memory representation.

The supplied suite covers two complete blocks plus a 512-row tail. An
independent generated-only 3,072-row check covered the requested
2,048+1,024 partition: the suffix was unchanged after (0,2048) and
(2048,3072), the exact caller-left object was returned, right was unchanged,
and the float32 relative Frobenius error was 1.9949125743886143e-06
(maximum absolute error 1.823902130126953e-05). This is shallow parity only.

## C. Owned ledger and peak interpretation

At B=2,048 the source owns:

~~~
outer scratch                  448*B
middle scratch                 784*B
leaf-left bank               1,372*B
leaf-product bank            1,372*B
row total                    3,976*B = 8,142,848 elements
right hierarchy                666,624 elements
total                        8,809,472 elements
                            35,237,888 bytes
                            33.60546875 MiB.
~~~

There is no output allocation or output entry in memory_ledger; the result is
the caller-left array.

The predecessor target-free L2 audit measured 492.44140625 MiB and reports
its complete 111.453125-MiB workspace. That ledger includes a distinct
full-height 63-MiB self.output. The caller-left activation was not an owned
workspace array. If M116b replaces that same process and the caller is allowed
to surrender the already-live left activation:

~~~
base = 492.44140625 - 111.453125 = 380.98828125 MiB
inferred B=2,048 peak = 380.98828125 + 33.60546875
                       = 414.59375000 MiB.
~~~

This does not double-count output: predecessor output is removed with its
workspace, and the already-live caller-left stays in the base exactly once and
becomes M116b output. The new larger right hierarchy is included in the new
ledger. It is not, however, a comparable measurement: the predecessor was a
depth-32 synthetic estimator process with a different, out-of-place API and
allocator/backend behavior. If integration preserves left or materializes a
separate 63-MiB output/copy, the corresponding inference is 477.59375000 MiB.
A new fresh-process measurement must settle this.

### Prospective B=4,096 mutation only; no change to this verdict

The binding verdict above is only for the frozen B=2,048 source. Still, the
no-output ledger makes a separately named B=4,096 child statically possible
if and only if B=2,048 later fails its frozen call-residual gate; this is not
permission to implement, tune, or substitute it.

Independent B=4,096 accounting is:

~~~
row-owned elements = 3,976*4,096 = 16,285,696
right elements = 666,624
total elements = 16,952,320
workspace = 67,809,280 bytes = 64.66796875 MiB
same-base inference = 380.98828125 + 64.66796875
                    = 445.65625000 MiB.
~~~

That conditional hypothesis is 18.34375 MiB below the same 464-MiB safety
gate, versus 49.40625 MiB for B=2,048. It would have 16 full-target core
calls (15*4,096+3,072) and the unchanged full-product bill
5,912,804,352 because row terms are linear and right packing remains once per
product. It remains an unmeasured prospective mutation with less peak
headroom, not a B=2,048 threshold change.

## D. Strategy identity, FlopScope boundary, runtime, and tests

Dispatch exposes only l3_inplace or unsupported: it requires exact
(m,256) times (256,256), m divisible by eight, and an L3 bill strictly below
direct. It has no direct/L1/L2 fallback and fails before right packing or a
left write on other shapes. It also rejects bad dimensionality, m above
max_m, non-float32 operands, non-writable/non-C-contiguous left storage, and
overlap.

The hot source uses explicit copyto, add, subtract, and batched matmul. Its
AST test finds no stack, concatenate, or reshape. trace_generated_probe
constructs source arrays and workspace before BudgetContext, then includes
operand conversions, packs, GEMM, and folds inside the charged boundary. It
does not measure RNG, setup/allocation, or whole-process peak.

All 11 unittest cases and py_compile passed in the observed runtime. With the
four one-thread variables set, the 512-row test trace and independent
2,048-row trace billed exactly 47,588,352 and 188,353,536, respectively,
with l3_inplace and one visible matmul call. The four variables are not a
runtime lock: the source does not pin interpreter, package hashes, BLAS build,
or allocator. There is also no depth-32 generated test, residual/wall
measurement, full-process peak runner, or fixed lifecycle/claim runner.

## Minimum frozen gates for the permitted build

A new generated-only runner must bind the four source hashes plus config,
interpreter, NumPy, FlopScope, BLAS, and output identities before allocation.
It must fail closed on changed identity, unavailable FlopScope, thread
mismatch, unsupported shape, or a prior claim. No fallback/retry/direct route
is allowed.

| gate | frozen threshold |
|---|---:|
| full 64,512 x 256 static bill / core calls | exactly 5,912,804,352 / 32 |
| FlopScope microchecks, 512 and 2,048 rows | exact static bill; one core and total matmul call |
| block/tail products | finite; relative Frobenius <=3e-6; no future-row or right mutation |
| generated float32 depth-32 parity | finite; relative error <=2e-5; ReLU mismatch fraction <=2e-4 |
| fresh full-process peak working set | <=464 MiB |
| generated full prediction | finite, zero failures, no retry, wall <20 s, residual <=0.170 s |

The 464-MiB peak gate leaves about 49.4 MiB above the B=2,048 hypothesis and
is deliberately unchanged by the prospective B=4,096 arithmetic. Record the
full visible call trace, including the required 32 calls for the full B=2,048
hook, alongside residual; do not assume arithmetic savings erase call cost.

A source, ownership, threshold, block-size, or runtime change requires a new
independent audit. Failure of a frozen gate kills that frozen campaign
instance.
