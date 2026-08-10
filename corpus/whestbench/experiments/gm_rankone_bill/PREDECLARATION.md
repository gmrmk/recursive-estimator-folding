# PREDECLARATION - gm_rankone_bill (graveyard revival falsifier)

Written BEFORE any harness code was executed. Mining search key:
`m204_lowrank_b1_lifted_control`.

Worker: Opus-5 falsifier, work dir
`corpus/whestbench/experiments/gm_rankone_bill/`.
Pinned interpreter: `work/whest-v014/Scripts/python.exe` (Python 3.14.4, numpy 2.4.6).

## 0. Records under test

| ledger id | recorded status | recorded reason |
|---|---|---|
| `m205_rankone_complete_physical_owner` | blocked | "The one f64 square costs 2,076,311,552 raw and 2,595,389,440 protected, above strict headroom" |
| `m204_lowrank_b1_lifted_control` | killed | "the no-credit raw minimum ... 2.084422144B, already 0.097550672B above the strict 1.986871472B" |
| `m206_m204_native_replacement_audit` | (same bill as M204) | |
| `m203_terminal_contraction_circuit_no_go` | killed | "depth 5: terminal 7.963587520B plus ... 2.580192000B equals 10.543779520B, 0.252415760B above M151's entire 10.291363760B slot" |

## 1. Mechanism claimed by the revival record

The kill measured a **static arithmetic bill under one dtype convention**, not an
executed cost. The convention is canonical in this lineage:

- `m124_protocol.py:178` - `square_float64 = 2 * square_f32`
- `m136_diagram_transformer.py:528` - precondition: *"float32 parity must be
  independently demonstrated before using dtype_multiplier=1"*

The named unlock condition (an independent float32 parity demonstration) was
never run for the rank-one square or the two-rectangle terminal contraction.
Revival mechanism: **discharge the parity condition, then re-price at
`dtype_multiplier = 1.0`.** No new mathematics, no new provider, no estimator
change.

## 2. Quantities

Let `n = 256`, `L = 31` source layers, `square_f32 = 2 n^3 - n^2 = 33,488,896`,
protection factor `5/4`.

- M205 rank-one square, f32: `raw = L * square_f32`; `protected = ceil(1.25*raw)`
- M204/M206 add the `a = u^T W` term: `L * (2 n^2 - n) = L * 130,816`
- M203 depth-5: `protected_terminal_bill(5)` and `protected_ideal_projection_bill()`
  recomputed with `F64_RATE -> 1`
- Strict M199 composed headroom: `H = 1,986,871,472`; M151 slot `S = 10,291,363,760`

Numerical parity metric, per identity, per slot `s in {aaaa, aaab, aabb}`:

```
rel_s = max|X_f32 - X_f64| / max(|X_f64|, tiny)
rel   = max over slots
```

`X_f64` is produced by the FROZEN, UNEDITED modules
`m205_rankone_complete_physical_owner.py` / `m203_terminal_contraction_circuit_no_go.py`
(read-only imports). `X_f32` is produced by a shadow module in THIS directory that
transcribes the same closed forms with `float32` as the working dtype. The frozen
files are never modified.

Result-normalisation (dividing by the size of the ANSWER, not of the operands) is
chosen deliberately: it is the metric that *detects* catastrophic cancellation,
because cancellation makes the answer small while the rounding error stays
proportional to the operands. A cancellation ratio
`kappa = max(|source(c)|, |source(T-c)|) / max|source(T)|` is reported alongside.

## 3. Step-0 arithmetic gate (run FIRST; STOP if it kills)

Predicted integers (on record, from the mining ledger, to be reproduced exactly):

| quantity | predicted value |
|---|---|
| M205 f32 raw (31 layers) | 1,038,155,776 |
| M205 f32 protected | 1,297,694,720 |
| M205 slack vs H | 689,176,752 (34.68% under) |
| M204/M206 f32 raw | 1,042,211,072 |
| M204/M206 f32 protected | 1,302,763,840 |
| M204/M206 slack vs H | 684,107,632 (34.43% under) |
| M203 depth-5 f32 combined | 5,271,889,760 |
| M203 vs M151 slot S | 5,019,474,000 under (48.8% under) |
| M203 vs strict headroom H | STILL OVER (asymmetry, declared in advance, not averaged away) |

**STEP-0 KILL:** if M205 f32 protected >= H, or M204 f32 protected >= H, the
revival is dead on arithmetic alone; stop, write KILL_CONFIRMED, run nothing else.

**STEP-0 PASS:** both protected f32 bills < H. Proceed to step 1.

## 4. Step-1 identities under test (the cheapest falsifier, as mined)

Fixtures: the EXISTING Philox seeds of the frozen tests, widths 3, 4, 5
(`_cell(width, 205100+w / 205200+w / 205300+w)`, `205400`), plus n=256 He-scale
instances (`W ~ N(0, 2/n)`).

1. **I1 distinct delta-tilde** - `canonical_delta_tilde_distinct` vs
   `rank_one_control_table` on distinct labels.
2. **I2 compiled aaaa/aaab/aabb parity** - `compile_lifted_rank_one_control` vs
   `brute_complete_source`.
3. **I3 physical K4/K31/K22 mapping** - `brute_complete_source(physical_only)` vs
   the independent direct `[4]/[3,1]/[2,2]` source.
4. **I4 complete reconstruction** - `source(T) = source(c) + source(T-c)`.
   *This is the cancellation-sensitive one.*
5. **I5 M203 two-rectangle packing** - `packed_terminal_contractions` vs
   `expanded_terminal_contractions`, at n=256 He-scale floats (the frozen test
   uses exact integers; floats are the load-bearing regime for the f32 claim).
6. **I6 n=256 compiler parity** - `compile_lifted_rank_one_control` f32 vs f64 at
   n=256 He-scale. This is the DECISIVE n=256 measurement, because the billed
   object priced by M205 is exactly this one square per source layer.

Scale-down declared in advance: identities I1-I4 use cubic/quartic brute oracles
that are `O(n^3)` python triples with `O(n^2)` inner work, i.e. infeasible at
n=256 inside the compute envelope. They are run at widths 3, 4, 5 exactly as the
mined falsifier specifies, plus an added n=64 bridge for I3/I4 where affordable.
n=256 carries I5 and I6. Nothing is quietly dropped; anything not run is named as
not run.

## 5. Gates (exact numbers, fixed now)

f32 machine epsilon = 1.1920929e-07. Standard f32 GEMM backward-error scale for
inner dimension k is `~ k * eps`; at k = 256 with three chained products the
worst-case bound is `~9.2e-05`.

- **GATE R (REVIVE):** every identity I1-I6 has `rel <= 1.0e-05`.
  (the mined record's "~1e-6 scale (f32 eps-limited)", with one order of slack
  granted for n=256 accumulation) AND step 0 passed.
- **GATE K (KILL):** any identity has `rel > 1.0e-03`. Three orders above the
  expected scale = fewer than ~3 correct significant digits out of a reference
  with 15 = the identity has been lost to cancellation. Reported as
  KILL_CONFIRMED for the parity premise.
- **Between 1.0e-05 and 1.0e-03 (inclusive/exclusive):** INCONCLUSIVE. No
  retuning of the threshold after the fact. The number is reported verbatim and
  the verdict says INCONCLUSIVE.

Sub-gate explicitly named by the mined falsifier: the **quartic collision cells**
(the `aaaa` slot and the whole of I3, which lives entirely in collision cells) are
reported separately under the same thresholds.

## 6. Two-signal verification plan

1. **Independent recomputation of the frozen record.** The harness reproduces the
   four M205_RESULTS_20260809.json f64 numbers (2.6645352591003757e-15,
   6.821210263296962e-13, 5.684341886080802e-14, 5.258016244624741e-13) and the
   M203 recorded cost table, from the frozen modules. If these do not reproduce,
   the environment is not the recorded one and the run is BLOCKED, not passed.
2. **Transcription fidelity.** The shadow module, run with `float64` as its
   working dtype, must agree with the frozen module to `<= 1e-12` absolute on
   every slot. This proves the f32 numbers measure dtype, not a transcription bug.
3. **Exact-rational ground truth.** At width 3, `fractions.Fraction` evaluation of
   the compiler and of the brute source establishes that the f64 reference itself
   is accurate to `~1e-15`, so "f32 vs f64" is a fair parity statement.
4. **Bit-repeat.** The entire harness is run twice in fresh interpreters; the
   decisive numbers must be bitwise identical.

## 7. Prediction ON RECORD

Step 0 **passes** (the mined integers are correct arithmetic; I reproduced them by
hand before writing this).

Step 1: I predict the identities **HOLD at f32-eps scale (REVIVE)**, with
`rel ~ 1e-7 .. 1e-5`. Reasoning: every identity is a polynomial contraction whose
two sides are computed from the same operands with no structurally-enforced
cancellation to zero; the residual `T - c` is a difference of two independently
drawn tables, so it is generically the same order as its operands.

The strongest counter-hypothesis, and the one I will test specifically, is I4: if
the rank-one control `-2 u_i^2 u_j u_k` happens to sit at the same magnitude as
the physical owner table, `source(c)` and `source(T-c)` are large and nearly
cancelling, and f32 would lose the identity in exactly the "quartic collision
cell" way the mined falsifier names. `kappa` is reported to price that risk
whichever way the test lands.

**HONEST CEILING (carried verbatim from the mining record):** this removes exactly
ONE of M205's four recorded blockers. The layer-bound physical K4/K31/K22
provider, the complete-domain proposal / residual-event accounting, and the
integrated native trace all remain absent, so nothing promotes. A REVIVE here
means only that the cost gate stops being binding. Nothing in this experiment
touches the frozen Phase-1 selection, and nothing here reads truth, scorer,
holdout, private data, or the held M245/M243/M244 lane.
