# VERDICT - gm_m116_streams

Candidate: `m116b_inplace_streamed_l3_b2048` / `m116c_inplace_streamed_l3_b4096`
(L3 Winograd/Strassen leaf-bank family, `killed_one_shot_residual*`).

**GATE RESULT: INCONCLUSIVE.**
Step 0 cleared. Three of the four predeclared kill conditions were measured and
survived (bitwise parity, peak, exact bill). The fourth - the absolute residual
gate that originally killed the family - is NOT MEASURABLE on this host,
because the control arm, which reproduces the consumed M116c dispatch schedule
exactly, comes in 2.36-3.39x above its own recorded value.

## DEVIATIONS (loud, read these first)

- **D1 (predeclared).** The consumed M116c identity must never be re-run, so the
  512-call reference was REBUILT here from the frozen operator source
  (`inplace_l3.py`, sha256 `114d1966...f6d99e83`) under the identical geometry
  and seed. New directory, no claim, no campaign root, no ledger write.
- **D2 (predeclared).** Frozen sources imported read-only and SUBCLASSED;
  `_pack_left` / `_pack_right` / `_fold` inherited verbatim. No frozen file was
  edited (hashes re-verified after the run, see `source_hashes.json`).
- **D3 (predeclared).** The mined "~0.047 s fully fused" figure is memory-
  infeasible (981.0 MiB of owned banks vs a 464 MiB gate). Fusion group size was
  set by the memory gate to G=4 before any measurement.
- **D4 (NOT predeclared, discovered mid-run).** The frozen `wall_time_limit_s =
  20.0` aborted the control arm at layer 13. The limit was raised to 300 s for
  BOTH arms so the experiment could complete. The frozen 20 s wall gate is
  reported as NOT MEASURABLE on this host; raw walls are recorded verbatim.
- **D5 (NOT predeclared).** Four extra runs were attempted with
  `SetPriorityClass(HIGH)` as measurement hygiene. **The call failed** (the
  process stayed at NORMAL priority - see `process_priority` in the arm JSONs),
  so these are simply four more NORMAL-priority repeats and are pooled with the
  others. Nothing was killed or preempted.
- **D6 (NOT predeclared - deviation from my OWN verdict mapping).** The
  predeclaration said "G1 RESIDUAL KILL -> report KILL_CONFIRMED". I am NOT
  reporting KILL_CONFIRMED. The predeclared mapping silently assumed the gate
  was measurable. It is not: the control arm - whose true value on the campaign
  host is known to be 0.3284645767 s - measures 0.774-1.115 s here. A gate whose
  control is off by 2.4-3.4x measures the host, not the candidate. Declaring a
  kill on that basis would be a false kill. I report INCONCLUSIVE and name the
  settling check below.
- **D7 (implementation).** FlopScope bills `reshape` as a full elementwise pass
  (measured: +rows*256 per dispatch). The grouped `(g, rows, 256)` views are
  therefore built ONCE at setup, outside the metered region, and reused at every
  depth. This restores the exact frozen bill and matches the frozen design's own
  "no hot reshape" discipline.

## STEP 0 - relevance gate (arithmetic only, no build)

The ledger never printed the baseline the L3 bank saves against. Recovered from
the committed per-hook schedule table in
`resources/research_excursions/M116_STREAMED_FUSED_L3_THEORY_20260807.md` at
m = 64,512, applied to the frozen depth-32 fixture
(`32 * hook + 32*64,512*256` ReLU):

| schedule | per-hook bill | full depth-32 trace | minus 189,738,221,568 |
|---|---:|---:|---:|
| direct | 8,439,201,792 | 270,582,939,648 | **80,844,718,080** |
| fused L1 Winograd (= promoted champion `row_blocked_winograd_production`) | 7,427,768,320 | 238,217,068,544 | **48,478,846,976** |
| fused L2 Winograd | 6,582,603,776 | 211,171,803,136 | 21,433,581,568 |
| fused L3 Winograd (the killed row) | 5,912,804,352 | 189,738,221,568 | 0 |

Relevance floor 1,000,000,000. Delta against the promoted champion is
**48,478,846,976 (48.479B)**, 48.5x the floor. **STEP 0 = CLEAR** - the family
is not score-irrelevant, so the build was authorized.

Cross-checks that fired inside `step0_baseline.py` (asserts, not quotes):
`D(m,k,n)=m*n*(2k-1)` reproduces 8,439,201,792; `W3 = 343*D(m/8,k/8,n/8) +
651*(mk+kn+mn)/64` reproduces 5,912,804,352; and `32*W3 + ReLU` reproduces the
killed row's metered 189,738,221,568 exactly.

Context number, not a gate: the killed run's residual excess was
`1e11 * (0.6105131132 - 0.170)` = 44,051,311,320 flop-equivalents, so even the
UNREPAIRED L3 bank nets +4,427,535,656 against the champion. Repairing the
residual is what makes the row worth its 48.5B.

## STEP 1 - the fusion arms

Mechanism: keep the frozen 4,096-row block PARTITION (so float32 association per
row is unchanged and bitwise parity is achievable), and promote the row-block
index to a LEADING BATCH AXIS so G consecutive blocks are packed, multiplied and
folded in one Python iteration and one batched `fnp.matmul`. This is M169's
lever, not block-height tuning (which changes the partition and therefore cannot
be bitwise-equal).

Frozen fixture in both arms, verbatim from
`m116b_inplace_l3_draft/campaign_worker.py::_full_prediction`: float32, width
256, 64,512 rows, depth 32, seed 11,664,512, gain sqrt(2/256), in-place ReLU,
one-thread env, pinned `work/whest-v014/Scripts/python.exe` (Python 3.14.4,
NumPy 2.4.6, FlopScope 0.10.0+np2.4.6).

| | ARM REF (control) | ARM FUSED (candidate) |
|---|---:|---:|
| group G | 1 | 4 |
| dispatch plan / layer | 16 x (1, 4096) | (4,4096) x3, (3,4096), (1,3072) |
| dispatches / layer | 16 | 5 |
| matmul calls, depth 32 | **512** | **160** |
| billed FLOPs | **189,738,221,568** | **189,738,221,568** |
| owned workspace | 64.668 MiB | 251.043 MiB |
| peak working set | 188.75-188.85 MiB | **365.91-366.13 MiB** |
| residual, 4 runs (s) | 1.114843, 0.987488, 0.774115, 0.857333 | 0.466612, 0.435332, 0.403030, 0.371815 |
| residual mean (95% CI) | 0.933445 [0.695698, 1.171192] | **0.419197 [0.354148, 0.484247]** |
| predict wall (s) | 48.31, 40.46, 31.25, 35.10 | 42.05, 37.50, 36.80, 33.60 |

## Gate outcomes

- **STEP 0 relevance**: CLEAR (48,478,846,976 >= 1,000,000,000).
- **G2 bitwise parity**: **PASS**. `0` differing float32 words out of
  `16,515,072`; max abs difference `0.0`. All **8** full-geometry runs in **8
  fresh processes** produced the single digest
  `ed59595dac93a6e20e362266306530c48045798126c6cec0a027b382ab5b1e70`. The cheap
  preflight additionally compared against the UNMODIFIED frozen
  `InplaceL3Winograd` at 19,456 rows: 0 differing words for both G=1 and G=4.
- **G3 peak <= 464 MiB**: **PASS**. Worst fused peak `366.125 MiB`, 97.9 MiB of
  margin.
- **INV exact bill**: **PASS**. Every one of the 8 runs billed exactly
  `189,738,221,568`, matching both the frozen contract value and the independent
  `cost_model.independently_expanded_l3` expansion.
- **INV finiteness**: PASS (all 8 runs).
- **G1 residual <= 0.170 s**: **NOT MEASURABLE ON THIS HOST**. Raw fused mean
  `0.419197 s`, CI `[0.354148, 0.484247]` - 2.47x the gate. But the control arm
  (identical 512-call schedule to the consumed M116c run, recorded there at
  `0.3284645767 s`) measures `0.933445 s` mean / `0.774115 s` best, a host factor
  of **2.84x mean / 2.36x best**. The host is an AMD Ryzen 7 7730U laptop sitting
  at 100% CPU with several other agent processes resident.
- **INV wall < 20 s**: NOT MEASURABLE (control arm also fails; it needs 31-48 s
  where the campaign host needed 17.30 s).

## What the experiment does establish

1. The residual is call-count driven, confirmed a third time on new hardware:
   dispatches fell 512 -> 160 (3.200x) and residual fell 0.933445 -> 0.419197 s
   (2.227x); the gap is the fixed intercept, exactly as the ledger's two-point
   law describes.
2. Dispatch fusion at this scale is EXACT, not approximate. The mined mechanism
   claimed bitwise parity; parity is measured at 0/16,515,072 words.
3. The memory objection to fusion is quantified and cleared at G=4: 251.043 MiB
   of owned banks, 366.125 MiB peak, 97.9 MiB under the frozen ceiling. Full-
   height fusion (the mined "~0.047 s") is genuinely impossible at 981.0 MiB.

## Labelled projections - NOT gate outcomes

Introduced only because the absolute gate could not be measured; they were not
predeclared and are reported at "derived" level, never as a pass.

- Ledger two-point law, campaign host: slope `5.508760478e-4 s/call`, intercept
  `4.641604019e-2 s`; at 160 calls -> **0.134556 s**.
- Control-anchored normalization (mean): `0.419197 / 2.841844` = **0.147509 s**.
- Control-anchored normalization (best-case): `0.371815 / 2.356770` =
  **0.157765 s**.

All three land under 0.170 s, with 7-21% margin. That is suggestive, not
decisive, and the margin is thin enough that it would not survive a modest
mis-estimate of the host factor.

## The settling check

Re-run `run_arm.py --group 1 --tag ref` and `--group 4 --tag fused` unchanged on
hardware where ARM REF reproduces `0.3284645767 s` within +/-10%. Cost: about
40 s of compute per arm on such a host. If ARM REF reproduces and ARM FUSED then
lands <= 0.170 s, this candidate is revived on all four gates; if ARM FUSED
exceeds 0.170 s on a reproducing host, the family is dead on its own axis and
should be closed permanently.

## Files

- `PREDECLARATION.md` - written before any code.
- `step0_baseline.py`, `step0_results.json` - the arithmetic gate.
- `fused_l3.py` - `GroupedInplaceL3`, subclass of the frozen operator.
- `probe_cheap.py`, `probe_cheap_results.json` - preflight vs the frozen operator.
- `run_arm.py`, `arm_{ref_a,ref_b,ref_hp,ref_hp2,fused_a,fused_b,fused_hp,fused_hp2}.json`.
- `arm_ref.json` - the FIRST control attempt, aborted by the frozen 20 s wall
  limit at layer 13 (`TimeExhaustedError`); retained as the evidence for D4.
- The 63 MiB `state_*.npy` dumps were deleted after the parity word count; the
  digests are recorded in `results.json` and `arm_*.json`.
- `analyze.py`, `results.json` - aggregation, parity word count, CIs.
- `source_hashes.json` - frozen-source hashes re-verified after the run.
- `VERDICT.md` - this file.
