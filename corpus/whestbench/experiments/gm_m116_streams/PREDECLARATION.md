# PREDECLARATION - gm_m116_streams (graveyard revival of m116b_inplace_streamed_l3_b2048)

Date: 2026-08-10. Written BEFORE any experiment code.
Mining key: `m116b_inplace_streamed_l3_b2048`.
Ledger rows: `m116b_inplace_streamed_l3_b2048` (killed_one_shot_residual),
`m116c_inplace_streamed_l3_b4096` (killed_one_shot_residual_family_closed).

## DEVIATIONS (loud, at the top)

- D1. The mined Step-1 falsifier says "bitwise parity against the 512-call
  reconstruction". The consumed M116c run identity is permanently consumed and
  MUST NOT be re-run. I therefore REBUILD the 512-call (B=4096) streamed
  reference myself, in my own directory, from the frozen operator source
  (`inplace_l3.py`, sha256 `114d19664317409a170ff937de72ad4527d657ea31ab0500ca76f79cf6d99e83`),
  under the identical frozen geometry/seed, and take bitwise parity against
  THAT. This is a reproduction of the reference, not a retry of the consumed
  identity: new directory, no claim file, no campaign root, no ledger write.
- D2. Frozen sources are imported read-only and SUBCLASSED. `_pack_left`,
  `_pack_right`, `_fold` are reused verbatim (they are `@staticmethod`s and are
  shape-generic over leading batch axes), so the fused arm's arithmetic is the
  frozen arithmetic by construction. No frozen file is edited.
- D3. The mined expected-gain note says a fully batch-fused leaf bank "lands
  near 0.047 s" (i.e. ~1-2 dispatches). That is memory-infeasible: fusing all
  64,512 rows needs `4*(3976*64512 + 666624)` = 1,028,665,344 B = 981.0 MiB of
  owned banks, far above the 464 MiB peak gate. The fusion group size is
  therefore chosen by the memory gate, not by the residual wish. Predeclared
  choice: G = 4 blocks of 4,096 rows per dispatch (see below). This is a
  documented scale-down of the mined mechanism to fit a FROZEN gate, declared
  before measurement.
- D4. Compute envelope: each full arm is one depth-32 forward over 64,512x256
  (previously measured predict wall ~17.3-17.7 s). Two arms plus a peak-probe
  child fit well inside ~90 min. No scale-down of the geometry is predeclared.

## Mechanism under test

The kill measured DISPATCH COUNT, not arithmetic. Both consumed runs passed
every gate except residual wall:

| run | matmul calls | residual_s | gate |
|---|---:|---:|---:|
| M116b B=2048 | 1024 | 0.6105131132 | 0.170 |
| M116c B=4096 |  512 | 0.3284645767 | 0.170 |

FlopScope defines `residual_wall_time_s = wall - flopscope_backend_time -
flopscope_overhead_time` (verified by reading
`work/whest-v014/Lib/site-packages/flopscope/_budget.py:689-707`): it is USER
Python between instrumented ops. It is therefore proportional to the number of
Python-level row-block iterations, not to arithmetic.

Two-point law fitted from the two consumed runs:

```
slope     = (0.6105131132 - 0.3284645767) / (1024 - 512) = 5.508760478e-4 s/call
intercept = 0.3284645767 - 512*5.508760478e-4            = 4.641604250e-2 s
```

Revival lever (M169's established, bitwise-verified batch-axis call fusion,
built two days after the L3 family was closed): keep the B=4096 row-block
PARTITION exactly (so the float32 association is unchanged and bitwise parity
is achievable), but promote the row-block index to a LEADING BATCH AXIS so that
G consecutive blocks are packed, multiplied and folded in ONE Python iteration
and ONE batched `fnp.matmul`. Block-height tuning (the lever the ledger closed)
changes the partition and therefore cannot be bitwise-equal; batch-axis fusion
can.

## Arms (exactly two, both response-free / synthetic / generated-only)

Frozen fixture in both arms, taken verbatim from
`m116b_inplace_l3_draft/campaign_worker.py::_full_prediction` and
`campaign_contract.json`: float32, width 256, full rows 64,512, depth 32,
seed `full_prediction = 11664512`, gain `sqrt(2/256)`, in-place
`fnp.maximum(state, 0.0, out=state)` per layer, one-thread env, pinned
`work/whest-v014/Scripts/python.exe`.

- ARM REF (control, reproduces the consumed M116c arithmetic): block height
  4,096, no fusion. 64,512 = 15*4,096 + 3,072 -> 16 blocks/layer -> 512 matmul
  calls, 512 Python block iterations.
- ARM FUSED (candidate): identical 4,096-row partition, dispatch groups
  [4,4,4,3, tail(3,072)] per layer -> 5 dispatches/layer -> 160 matmul calls,
  160 Python block iterations.

Owned-bank arithmetic for ARM FUSED at G=4 (R = 16,384 fused rows):
`4*(3976*16384 + 666624)` = 260,571,136 B = 248.50 MiB. M116b measured whole-
process peak 186.58203125 MiB at a 33.60546875 MiB workspace, so the non-
operator base is ~152.98 MiB and the predicted ARM FUSED peak is ~401.5 MiB,
under the 464 MiB gate with ~62 MiB of margin.

## Predicted outcome (ON RECORD, before measurement)

- STEP 0: pre-L3 baseline minus 189.738221568B is far above the 1B relevance
  floor, so Step 0 does NOT kill. Predicted baseline = the promoted champion's
  (row_blocked_winograd_production, L1 fused Winograd) arithmetic on the same
  frozen fixture: `32 * 7,427,768,320 + 32*64,512*256 = 238,217,068,544`.
  Predicted delta = `238,217,068,544 - 189,738,221,568 = 48,478,846,976`
  (48.479B). Second reading, versus unfused direct
  `32*8,439,201,792 + 528,482,304 = 270,582,939,648` -> delta 80.845B.
- ARM REF residual: predicted 0.32 +/- 0.08 s (reproduces 0.3284645767 s).
- ARM FUSED residual: predicted `0.04641604 + 160*5.508760478e-4` = 0.1345 s,
  i.e. UNDER the 0.170 s gate but with only ~26% margin. I predict PASS on
  residual, and I state plainly that this is the tight gate.
- Bitwise parity ARM FUSED vs ARM REF: predicted EXACT (0 differing float32
  words out of 16,515,072), because the per-block elementwise arithmetic and
  the per-block `(rows/8,32)x(32,32)` gemm shapes are unchanged; only a leading
  batch axis is added.
- Bill: exactly 189,738,221,568 in both arms; matmul calls 512 (REF) and 160
  (FUSED).
- Peak: ARM FUSED <= 464 MiB (predicted ~401 MiB).

## KILL CONDITIONS (frozen; no retuning past a failed gate)

- STEP-0 KILL: `baseline_bill - 189,738,221,568 < 1,000,000,000`. If this
  fires, STOP: the family is score-irrelevant and stays closed. No build.
- G1 RESIDUAL KILL: ARM FUSED `residual_wall_time_s > 0.170` s.
- G2 PARITY KILL: ARM FUSED final depth-32 state is not BITWISE equal to ARM
  REF's final state (any nonzero count of differing float32 words).
- G3 PEAK KILL: ARM FUSED whole-process peak working set > 464 MiB.
- Preserved invariants (any failure is also a kill): billed FLOPs !=
  189,738,221,568; any non-finite value; predict wall >= 20 s.

Exactly ONE fused configuration (G=4 over 4,096-row blocks) is authorized. If
G1/G2/G3 fails I report KILL_CONFIRMED; I do NOT try another G, another block
height, or a relaxed gate.

## Two-signal verification plan (required for any PASS claim)

1. Bill cross-check: FlopScope-metered `context.flops_used` must equal the
   closed-form `32*(343*D(rows/8,32,32) + 651*(m*k+k*n+m*n)/64 summed per
   block, right hierarchy once) + 32*64,512*256` computed independently by
   `cost_model.independently_expanded_l3`.
2. Bitwise repeat: ARM FUSED is executed twice in two FRESH processes; the
   sha256 of the final state buffer must match across both, and match the
   parity comparison against ARM REF.
3. Reference reproduction: ARM REF's residual must land in the neighbourhood of
   the ledger's consumed 0.3284645767 s, which independently validates that my
   harness measures the same quantity the kill measured.

## Firewall

New dir `corpus/whestbench/experiments/gm_m116_streams/` only. Frozen sources
read-only + subclassed. No git, no network, no submission, no truth/scorer/
private/holdout, no m245_*/M243/M244 lane. Synthetic generated arrays only.
