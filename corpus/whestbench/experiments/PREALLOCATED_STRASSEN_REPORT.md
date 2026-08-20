# Preallocated whole-row Strassen-Winograd compression

Date: 2026-08-06

## Decision

The changed allocation mechanism works, but no tested implementation clears
the entire predeclared engineering gate.  The family is therefore a **killed
implementation**, not a champion change.

The strongest scorer-side result is Mutation B, a single preallocated batched
seven-product matmul.  On the full product it reduces billed FLOPs from
`8.439201792e9` to `7.427768320e9` (`0.880151x`) and median effective proxy
from `8.441711776e9` to `7.471748399e9` (`0.885099x`).  Float32 parity,
residual, call-count, and memory gates pass.  Its median total wall time is
`0.153100 s` versus `0.099056 s` direct (`1.54559x`), narrowly failing the
frozen `<=1.5x` gate.

This result is useful: it proves the prior failure was mostly the allocation
and reconstruction graph.  Residual time fell from the previous
implementation's roughly `0.016870 s` to `0.000263-0.000440 s`.  What remains
is ordinary half-width BLAS throughput, not a FlopScope-accounting or Python
allocation problem.

No WHest data, truth, scorer, public row, locked row, or official submission
was opened.  The frozen random32,256 champion was not modified.

## Frozen experiment boundary

The initial gates were written in `PREDECLARED_GATES.md` before measuring.
After each failure, Mutations B and C were separately frozen in
`PREDECLARED_BATCHED_MUTATION.md` and `PREDECLARED_PACKED_MUTATION.md` before
their single timing screens.  All arrays and networks were fresh synthetic
float32 values, with OpenBLAS forced to one thread.

FlopScope 0.10.0 source and runtime checks establish:

- `fnp.matmul`, `fnp.add`, and `fnp.subtract` expose a real `out=` parameter;
- a non-C-contiguous destination view is accepted, returned by identity, and
  filled correctly (probe error exactly zero);
- `fnp.empty` costs zero billed FLOPs;
- the WHest runner invokes `setup(context)` before opening each per-network
  `BudgetContext`.  Width and depth are present in `SetupContext`, while
  `n_base` is class-fixed, so the maximum workspace shape is knowable without
  seeing an MLP.

Setup allocation is therefore legal under the interface.  It is not free in
the resource sense: buffer bytes and allocation wall time are reported below,
and setup remains subject to its timeout and process memory ceiling.

## Algebra and exact bill

For even core dimensions, the Winograd schedule is

```text
S1=A21+A22   S2=S1-A11   S3=A11-A21   S4=A12-S2
T1=B12-B11   T2=B22-T1   T3=B22-B12   T4=T2-B21

P1=A11 B11  P2=A12 B21  P3=S4 B22  P4=A22 T4
P5=S1 T1    P6=S2 T2    P7=S3 T3

U1=P1+P2    U2=P1+P6    U3=U2+P7    U4=U2+P5
C11=U1      C12=U4+P3   C21=U3-P4   C22=U3+P5
```

Mutation A reuses three large `S`, three small `T`, one product, one output,
and one ragged correction buffer.  It bills

```text
7 * direct(m/2,k/2,n/2)
+ m*k + k*n                     # eight Winograd input additions
+ 7*m*n/4                       # seven output additions
+ m*n/4                         # initialize C11 from P1
```

Mutations B/C explicitly fill seven-way operand stacks.  Three identity
blocks and four arithmetic blocks per stack each require one visible write,
so their full bill is

```text
7 * direct(m/2,k/2,n/2) + 7*(m*k + k*n + m*n)/4.
```

At `(64512,256)@(256,256)` this is `7.427768320e9`, or `0.880151x` direct.
Mutation A is slightly cheaper at `7.419461632e9` (`0.879166x`).  The
shape-only Mutation-A dispatcher checked all `131,072` combinations of
`m in {32256,64512}` and `k,n in [1,256]`: zero selected bills exceeded
direct, and no selected path used more than eight matmul calls.  The one-ragged
dimension paths also matched their closed forms exactly.  Both-ragged paths
dispatch direct because they would need nine calls.

## Gate results

| gate | A: sequential scratch | B: one batched call | C: packed sequential |
|---|---:|---:|---:|
| billed/direct | `0.879166` | `0.880151` | `0.880151` |
| median residual | `0.0002628 s` | `0.0004398 s` | `0.0005274 s` |
| median effective/direct | `0.882057` | `0.885099` | `0.886148` |
| median wall/direct | `1.55874` **fail** | `1.54559` **fail** | `1.70148` **fail** |
| max full-product abs error | `1.18256e-4` | `1.25885e-4` | `1.08719e-4` |
| full relative Frobenius | `6.03289e-7` | `6.04481e-7` | `6.03392e-7` |
| setup workspace | `189.1875 MiB` | `283.9375 MiB` | `189.4375 MiB` |
| conservative estimator peak | `417.6875 MiB` | `480.9375 MiB` | `386.4375 MiB` |
| measured process peak working set | `227.547 MiB` | `385.410 MiB` | `291.051 MiB` |
| measured peak pagefile/private | `311.504 MiB` | `406.375 MiB` | `311.902 MiB` |

All residuals are far below `0.00987 s`; all effective ratios beat direct by
more than the frozen 2% safety margin; all full parity and memory thresholds
pass.  Peak memory was measured in three fresh, separate Windows processes so
allocator retention from one variant could not contaminate another.  Only
total wall fails.

Mutation A also passed 16 full/active/ragged numerical trials with maximum
absolute error `5.96046e-6`, maximum relative Frobenius error
`6.03468e-7`, and all finite outputs.  Its depth-32 trial had relative final
error `2.95968e-6` and `0/4,194,304` ReLU gate flips.  The required independent
depth-32 checks for B and C yielded:

- B: relative final error `2.74189e-6`, `2/4,194,304` flips
  (`4.76837e-7`), finite;
- C: relative final error `2.47985e-6`, `1/4,194,304` flips
  (`2.38419e-7`), finite.

All are comfortably inside the `2e-5` and `0.02%` gates.  The final test suite
contains nine deterministic tests covering bills, full/ragged values,
dispatcher safety, dtype/memory, depth-32 propagation, and B/C parity.

## Scorer-product threshold

Above the score floor, let `r_C` be effective-compute ratio and `r_V` the raw
MSE ratio.  Compression improves score when

```text
r_C * r_V < 1.
```

For Mutation B's full-product proxy, `r_C=0.885099`.  It tolerates
`r_V < 1.129817` for bare parity, or `r_V <= 1.107221` while retaining the
predeclared 2% score safety.  With unchanged MSE (`r_V=1`), the product is
`0.885099`, so the scorer-side compression gate passes decisively.

That is not a deployment claim.  It is a single full-product proxy, whereas a
network contains varying active/ragged shapes, and the tiny float32
reassociation effect on actual MSE cannot be certified without a separately
authorized matched scorer gate.  The total-wall gate already prevents such a
promotion here.

## Failure localization and salvage

Passed components:

- true setup-preallocated `out=` buffers are legal and work for strided full
  and ragged destinations;
- the minimal-addition Winograd algebra and closed-form FlopScope bills are
  exact;
- allocation/reconstruction residual has been reduced by about 38-64x;
- shape-only dispatch, float32 parity, depth-32 gate stability, memory, and
  scorer-side effective proxy all pass.

Failed link:

- seven half-width GEMMs plus their Winograd memory traffic take more than
  `1.5x` the wall time of one highly optimized full-width GEMM on the pinned
  one-core NumPy backend.  Batching and explicit contiguous packing do not
  repair it; packing makes it worse.

Consequently, rerunning the same seven-product arithmetic with different
buffer counts is not justified.  Reopening requires a genuinely new kernel
mechanism or an official clarification that total-wall ratio is irrelevant
and only residual/effective compute matters.  The scorer-side B operator is
preserved for that future branch; it is not folded into the champion now.

## Reproducibility

Runtime: Python 3.14.4, NumPy 2.4.6, FlopScope 0.10.0, one OpenBLAS thread.

- `cost_model.py` SHA-256:
  `21B077A7BCDF244B9480E891A8B63ECEE05427D2725EA30EF5D2FC016BC03023`
- `winograd.py` SHA-256:
  `ED4646685FD3C578950BD0D72E3E447D9BBCBC1A437961D48FC3D98516CE589B`
- `estimator.py` SHA-256:
  `0A5145E313859AB985338FAE40BB6319BAF0BA812BF969AC1F18E697E13081BA`
- `test_preallocated_strassen.py` SHA-256:
  `CFE4BD4883995BD16AAFB7B523FEEB4AF8E06733174C021171EEAB6DA69CD1CC`
