# M236 preimplementation erratum 1 -- global ownership bridge and legal runtime views

Date: 2026-08-09. This erratum is sealed after the independent static audit
and before every M236 implementation, test, native trace, or statistical
readout. It supplements, and does not rewrite, the frozen M236
predeclaration and manifest.

Parent predeclaration SHA256:

```text
793786132F08CE71ABACE2BDA29ADE347ED2800B9615799F85BA7F71836E3CC1
```

Parent manifest SHA256:

```text
3B9D3B43D7995FED5D1CA331B465F4DD71C236F0BA5F6D7497E392364D844CF2
```

## 1. Immutable global-to-local block bridge

Setup constructs exactly four immutable `BlockPlan` records, in this order:

```text
global_ids=( 1, 2, 3, 4, 5, 6, 7, 8), local_ids=(1,2,3,4,5,6,7,8)
global_ids=( 9,10,11,12,13,14,15,16), local_ids=(1,2,3,4,5,6,7,8)
global_ids=(17,18,19,20,21,22,23,24), local_ids=(1,2,3,4,5,6,7,8)
global_ids=(25,26,27,28,29,30,31),    local_ids=(1,2,3,4,5,6,7)
```

Each plan binds, at setup time:

- its half-open zero-based global span `[start, stop)`;
- the exact matching rows of the one global setup receipt;
- direct `aaaa`, `aaab`, and `aabb` views into the one global output bank;
- first-`len(global_ids)` views of every shared B=8 staging, M212-internal,
  and M235-row owner;
- a block-local M212 staged/workspace wrapper and block-local M235
  receipt/state/full-domain wrapper containing only those prebound views;
- one preallocated Python weight-slot list and one factor-slot list of exactly
  the block length.

Before either charged stack call, staging validates that the live source
records have global layers exactly equal to `plan.global_ids`, in order, with
unique weight/factor objects and the frozen producer epoch. Only after that
validation may the bridge assign `plan.local_ids` to the block-local M212 and
M235 metadata so the unchanged inherited kernels accept their canonical
`1..B` contract.

Local IDs are kernel-private validation labels. They may never select a
global receipt row, input row, output row, or destination. Those selections
come only from the immutable plan's global span. The bridge must reject a
cross-block plan, receipt, staged owner, output owner, epoch, reorder,
duplicate, omitted layer, or relabeled-global-record substitution before a
charged write.

The last block is a true seven-layer view. No eighth dummy layer, padding,
masked row, or eighth charged element is permitted. The four global spans
must be pairwise disjoint and their ordered union must be exactly layers
1 through 31.

## 2. Exact output aliases and liveness evidence

The three global source arrays are the only source-output allocations. For
each block and each of `aaaa`, `aaab`, and `aabb`, the static receipt must
record owner object, data pointer, shape, strides, byte offset, and global
span. It must prove that:

- every block destination is the exact named slice of the corresponding
  global owner;
- the block destinations are non-overlapping and cover every global layer
  exactly once;
- M212 writes directly to those views and M235 mutates those same views;
- no block-local output allocation, output assembly, concatenation, or copy
  exists.

All shared B=8 numerical owners are allocated once in setup. Plan wrappers
and slices may alias them, but may not own storage. The exact setup-owned
`fnp.empty` count remains 18.

## 3. Permitted metered runtime results

The predeclaration phrase "Predict ... creates no views or arrays" is narrowed
as follows. Predict may create only the return values of operations already
enumerated in the frozen charged ledger, including M212's metered
reshape/transpose/swapaxes/diagonal results and M235's
`take_along_axis` result. It may not create any other participant-authored or
unmetered numerical workspace, view, array, packed operand, output, or copy.

Every plan view, global-output view, receipt view, workspace alias, and Python
slot list is setup-built. The only materialized selected-row gather live in a
block is exactly:

```text
shape=(8,32,256), dtype=float64, bytes=524288
```

or, for the final block:

```text
shape=(7,32,256), dtype=float64, bytes=458752
```

At most one gather may be live. It must die before the next block begins.
No gather owner may survive predict. The frozen operation counts, bills, and
58.949219 MiB numerical peak are unchanged.

## 4. Official same-worker lifecycle and response ABI

The one-process and later ten-process gates use the pinned official
`SubprocessRunner` lifecycle. Timing starts immediately before
`SubprocessRunner.start()` and ends only after its successful setup response.
The same actual worker process then executes every ordered prediction. The
harness must distinguish the launcher PID from the setup manifest's
`os.getpid()` and query RSS for the latter.

The audit entrypoint returns the unchanged harmless carrier view directly:

```text
mlp.weights[31][:32]
```

After the official worker's validation, the response must have shape
`[32,256]`, dtype `float32`, and all finite values. No response wrapper,
post-budget sidecar computation, alternate local component state, second
worker, or split replay is permitted.

Every prediction must pass the frozen exact bills and operation dictionaries,
both frozen wall caps, current-field and receipt identity, source invariants,
staging-slot release, response ABI, and actual worker peak RSS strictly below
496 MiB. These checks are conjunctive.

## 5. Stop and credit remain unchanged

This erratum authorizes only RED tests and implementation after an independent
preimplementation re-audit. It grants no native, variance, MSE, score,
submission, leaderboard, or prize credit. G0 remains closed. Any failure of
the bridge, aliases, byte parity, ledger, lifecycle, wall, or RSS gate kills
fixed M236 without a block-size or topology retune.
