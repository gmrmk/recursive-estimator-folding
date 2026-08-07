# M169 native compiler audit closeout

Status: **RESOURCE SURVIVOR — CONDITIONAL ALL-LAYER-STAGING INTERFACE ONLY; NO SOURCE-EFFICACY RUN.**

M169 preserves the frozen M163 exterior coefficient and float64 expression
order.  It changes one mechanism only: legal scheduling of independent dense
products.  Generated width-256 Gaussian matrices for 31 layers were the sole
inputs.  No response, source-efficacy result, network call, truth, scorer,
contest artifact, leaderboard, submission, or champion state was read or
changed.

## Exact scheduling and FlopScope legality

For each already-owned layer, M163 still evaluates

```text
Z = A @ W
P = (W o Z^2)^T @ W        Q = (W^2 o Z)^T @ Z
R = (W^2)^T @ Z^2          S = (W o Z)^T @ (W o Z).
```

M169 stacks the 31 `A,W` pairs into `(31,256,256)` and calls one batched
`matmul` for `Z`.  It writes the four unchanged post-Z operand pairs into
preallocated `(31,4,256,256)` `lhs`/`rhs` buffers, then calls one batched
`matmul`.  The leading `(31,4)` axes are NumPy batch axes, not matrix axes:
there are exactly 124 independent 256-by-256 products, with no 1024-by-1024
block construction and no cross terms.

This is directly supported by pinned FlopScope 0.10.0+NumPy 2.4.6:
`fnp.matmul` maps non-vector inputs to `...ij,...jk->...ik`; its own
row-blocked compiler already calls it on three-dimensional preallocated
left/right/product buffers.  `fnp.stack(..., out=...)` charges every output
element and `fnp.copyto` charges every destination element.  M169 uses those
instrumented operations only.  `reshape` is absent.

The interface condition is material: M169 is valid only after its caller
already owns all 31 labelled `(W_l,V_l)` arrays.  The frozen compiler is pure
per-layer — a compiled layer reads only its own pair — so this schedule does
not move a compiler dependency.  This pass does **not** claim that an unknown
sequential covariance/source provider may materialize its later states early;
such a provider must reject M169 rather than reorder its state transition.

## Exactness gates

Against frozen M164's M163 sidecar, every output component was bitwise equal:

| shape / seed | reference matmuls | M169 matmuls | mismatched elements | max abs difference |
|---|---:|---:|---:|---:|
| 7 / 3 / 169001 | 15 | 2 | 0 | 0.0 |
| 256 / 31 / 169002 | 155 | 2 | 0 | 0.0 |

The output formula, coefficients, collision nulls, and arithmetic precision
therefore remain frozen M163 semantics.  The target parity comparison includes
all 31 layer sources, not merely the final layer.

## Predeclared accounting and five fresh processes

The manifest predeclared exactly two matrix calls, a compiler bill of
`10,477,162,760`, no reshape bill, a 5.0 ms nominal p99 residual prediction,
and a hard hostile-5x residual limit of `7.08391688 ms`.  The arithmetic
prediction held exactly in every process.

| item | predeclared / limit | observed |
|---|---:|---:|
| matrix calls | 2 | 2 in all 5 |
| compiler bill | 10,477,162,760 | 10,477,162,760 in all 5 |
| compiler slot | <= 14,019,121,200 | pass; 3,541,958,440 margin |
| stack bill (3 calls) | 24,379,392 | 24,379,392 |
| copy bill (65 calls, including packing) | fully charged | 8,158,212 |
| reshape bill | 0 | no reshape operation |
| persistent allocations | reported | 21 arrays, 327.066 MiB |
| peak RSS | <= 512 MiB | 404.238 MiB |
| residual p99, linear | <= 7.08391688 ms | 5.322182989 ms |
| maximum residual | <= 7.08391688 ms | 5.363303237 ms |
| every inherited hostile-5x total | <= 100B | 98.213B–99.140B |

The p99 exceeded the 5.0 ms nominal prediction by 0.322 ms, but it passed the
predeclared hard gate without retry, tuning, or a second mechanism.  The
highest observed working set was 404.238 MiB; peak private bytes (reported
separately rather than substituted for RSS) were 577.074 MiB.

At p99, the hostile calculation is

```text
85,980,878,800 + 10,477,162,760 + 5 * 1e11 * 0.005322182989
= 99,119,133,054.4 < 100,000,000,000.
```

Every individual process also passed; the worst individual effective total was
`99,139,693,178.3`.

## Disposition and salvage map

M169 is a **resource-closed compiler survivor** for callers that satisfy the
explicit all-layer-ownership contract.  It reduces the frozen M164 dispatch
count from 155 to 2 while retaining bitwise target-shape output and keeping
every projection under 100B.

No estimator, source-variance, residual-p99 efficacy, provider accuracy,
network response, or contest evaluation was opened.  Accordingly this is not
a champion or efficacy promotion.  If a future caller proves it must generate
`V_l` or transport its source strictly layer by layer, kill only the M169
all-layer staging application; retain the independent-product batch layout,
the fully charged packing ledger, and the exact M163 exterior compiler.
