# M236 predeclaration -- fixed B=8 layer-batched M212+M235

Date: 2026-08-09. Frozen before every M236 implementation, test, native
trace, or statistical readout. Generated-only and response-free. M235 remains
`KILLED_FROZEN_NATIVE_RSS`; M236 is a new ownership/liveness child, not a
repair or reinterpretation of that result.

## One changed mechanism

M236 changes only the layer-storage topology. The 31 independent source
layers are compiled in four immutable blocks:

```text
[1..8], [9..16], [17..24], [25..31]
```

Everything statistical and algebraic is inherited unchanged: one setup-seed
Philox receipt, `k=32`, float64 arithmetic, M212 recursion depth 3, M215/M235
coefficients and operation order within a layer, and global output layout
`aaaa[31,256]`, `aaab[31,256,256]`, `aabb[31,256,256]`.

Layers never interact in M212 or M235. Each block uses the corresponding
read-only receipt slice and writes its outputs directly into prebound global
output slices. No full temporary, concatenation, assembly copy, dynamic view,
runtime workspace, per-block RNG, adaptive block size, or retry is allowed.

## Frozen ownership and liveness

Setup owns exactly 18 `fnp.empty` arrays:

```text
global source outputs (aaaa, aaab, aabb)                 3
B=8 staged weight and factor                             2
B=8 M212 internals excluding the three output arrays    11
B=8 M235 powers and cross workspaces                     2
TOTAL                                                    18
```

It also owns one full immutable `rank_order[31,256]` and its selected view.
Four block plans and every source/workspace/receipt view are constructed in
setup. Predict iterates that immutable plan tuple and creates no views or
arrays. Staging slots retain at most eight f32 weight/factor views and must be
cleared before returning from predict.

The exact target-shape numerical peak is frozen as:

```text
full global source outputs             31.060547 MiB
full immutable rank receipt             0.060547 MiB
B=8 M212 staging + internals            18.328125 MiB
B=8 M235 powers + cross                  9.000000 MiB
B=8 selected-row gather                  0.500000 MiB
TOTAL                                   58.949219 MiB
```

This removes `80.005859 MiB` from M235's `138.955078 MiB` numeric peak. The
conditional projection from M235's observed worst worker RSS is
`557.644531-80.005859=477.638672 MiB`; this is a premise, not native evidence.
M236 requires actual official-worker peak RSS strictly below `496 MiB`, giving
at least 16 MiB safety below the contest cap.

Any full 31-layer f64 staged/internal/row workspace, block-local source output
bank, output copy, or selected gather above `524,288` bytes kills M236.

## Frozen call and bill ledger

Partitioning only the independent layer batch preserves charged element
totals but changes calls. The required per-predict receipts are:

```text
M212 bill       1,249,253,376
M235 bill         864,960,512
combined bill   2,114,213,888

M212 calls:
  stack 8, matmul 16, reshape 16, add 12, copyto 100,
  diagonal 8, multiply 44, sum 4, swapaxes 32, transpose 32
M235 calls:
  take_along_axis 4, matmul 8, add 36, copyto 4,
  multiply 64, sum 4
```

Every operation shape and per-operation subtotal must sum to the parent bill.
No call fusion, padding, dummy layer, dtype change, packing credit, or changed
FlopScope namespace is permitted. Setup's receipt diagnostic remains 32,768.

The M235 lawful and conservative combined residual caps remain respectively
`3.227087104 ms` and `3.227021568 ms`; the stricter conservative cap is
binding. M235 component residual remains at most `2.025121700262334 ms`.

## Frozen proof order

1. **RED contract first.** Module absence is the only accepted initial RED.
2. **Static liveness gate.** Prove all array owners, aliases, byte counts,
   output-slice ownership, global layer IDs, and absence of all-31 workspaces.
3. **Algebra gate.** Preserve M235's exhaustive small-width cubic, independent
   row-loop, gauge, zero, subset-mean, permutation/covariance, and symmetry
   tests. At target shape, require raw byte equality for every source layer
   against the frozen full M235 reference on predeclared f32-quantized fixtures.
4. **One-process native falsifier.** One official setup-seed-0 worker executes
   `A -> B -> A` with source seeds `227700001` and `227710001`. It must pass
   exact bills/calls, both wall caps, setup under 4 s, receipt/current-field
   identity, raw A replay, finiteness/symmetry, staging-slot release, and peak
   worker RSS `<496 MiB`. One failure kills fixed M236.
5. **Independent audit.** No aggregate or statistical gate opens until the
   one-process result is independently confirmed.
6. **Ten-process native gate.** Only after approval, use M235's five setup
   seeds and primary/mirror `A-B-A` / `B-A-B` sequences. All 30 predictions
   must pass the same gates, including `<496 MiB`.
7. **G0 remains closed** until the complete native gate passes.

The audit harness must use the same official worker instance for setup and all
predictions, distinguish the venv launcher PID from manifest `os.getpid()`,
and read worker—not launcher—RSS. Audit-only pointer inspection may not enter
the production correction or affect output, source, bill, or gate boundaries.

## Frozen provenance

```text
M212 m212_flopscope_sidecar.py
  197569262FF487FCB5AF175CA5351F2ABB5B70885760CECC958FBCD8397F1C78
M235 m235_setup_shared_philox_row_receipt.py
  642B84EF75861C3FCEF971F23D50F0EE6EFCDBB6629F58A087C47BFFF3034FE2
M235 one-process result
  1934F1CD51AF7432D54680F2B2B715A3BAFC168EBEC0360C2330F9569AB0B27F
M235 disposition
  5412BCA5B158AC403E1EB868447F2A6EA16B6A68C27995932DAB8C382FA55EAF
```

## Stop and credit

Any algebra, ownership, byte-parity, bill, call, setup, wall, identity,
staging-release, or `<496 MiB` RSS failure kills M236. No post-result block-size
change, slot-lifetime repair, threshold change, padding, or timing-boundary
change is allowed. A failure may seed a separately predeclared child only.

Even a full native pass grants a memory-safe compiler component, not source
efficiency, whole-response MSE, score, submission, leaderboard, or prize
credit.
