# VERDICT - gm_rankone_bill

**GATE RESULT: REVIVED_PASS.** The float32 parity condition named at
`m136_diagram_transformer.py:528` is discharged, and at `dtype_multiplier = 1.0`
the M205 and M204/M206 bills fall ~34.5% UNDER the strict M199 composed headroom
instead of 4.5-4.9% over. The predicted kill mode (catastrophic cancellation in
the quartic collision cells) did not fire.

---

## DEVIATIONS (loud, at the top)

1. **The frozen modules were not edited.** They hardcode `dtype=np.float64` and
   enforce float64-scale guards, so "switching the working dtype to float32"
   was implemented as a *shadow* module (`f32_shadow.py`) in this directory that
   transcribes the identical closed forms with the dtype lifted to a parameter.
   Fidelity was then proved, not assumed: shadow-at-float64 vs the frozen module
   differs by **0.0 absolute on every slot** (stage A). The frozen suites were
   also run unmodified: m205 **6 tests OK**, m203 **4 tests OK**.

2. **Three frozen guards were deliberately relaxed in the shadow, not
   bypassed silently**: symmetry `allclose(atol=2e-13)`, B=1 weight-sum
   `isclose(abs_tol=3e-13)`, singleton-pair `isclose(abs_tol=2e-13)`. These are
   float64-scale fail-closed checks; no float32 array can pass them, so a f32
   parity demonstration cannot be run behind them. All structural checks
   (shape, finiteness, non-negative diagonal, zero K31/K22 diagonal) are kept.

3. **Two of the four recorded M205 f64 diagnostics did not reproduce bitwise**
   in this environment (numpy 2.4.6 / Python 3.14.4):
   - `distinct_delta_tilde_max_abs`: recorded `2.6645352591003757e-15`,
     recomputed `1.3322676295501878e-15` (exactly 1/2x)
   - `compiled_aaaa_aaab_aabb_max_abs`: recorded `6.821210263296962e-13`,
     recomputed `1.1368683772161603e-12` (exactly 5/3x)
   - `physical_owner_source_max_abs` `5.684341886080802e-14` - **bitwise identical**
   - `complete_owner_source_reconstruction_max_abs` `5.258016244624741e-13` - **bitwise identical**

   These are ULP-level differences in tiny absolute max-diff diagnostics, of the
   size a BLAS/summation-order change produces. The frozen assertions
   (`< 4e-10`, `< 5e-10`) still pass with ~3 orders of margin, and every
   *integer* in the frozen cost record reproduces exactly. Recorded as a
   deviation rather than absorbed.

4. **Bridge widths 8 and 12 were used instead of the "n=64 bridge" I
   predeclared for I3/I4.** Reason: the brute cubic oracle inside I4 is
   O(n^3) triples x O(n^2) inner work; n=64 is ~1000x width-12 cost and does not
   fit the envelope. Widths 16/20/24/28/32 were added instead (step 3), which
   covers the same question - the growth trend - at ~1/50 the cost.

5. **I4 at n=256 was not measured and is not claimed.** Its oracle
   (`brute_complete_source`) is labelled *"prohibited outside small-width tests"*
   by the frozen module itself and is infeasible at n=256. What n=256 carries is
   I5 and I6, i.e. the objects the bill actually prices.

6. **Step 3 exceeded the 600 s foreground tool cap and finished in a
   backgrounded shell (608.5 s, exit 0).** Its output was collected and folded
   in; nothing was left pending. Its expensive number (I3d n=256) was
   independently re-derived in step 5.

7. I added one identity beyond the mined four (`I3d`: the physical
   `[4]/[3,1]/[2,2]` collision source, f32 vs f64, up to n=256) and one
   accumulator attack. Both are additions to the falsifier, marked as such;
   neither replaces a predeclared measurement.

---

## Step 0 - arithmetic gate: PASS

Every predeclared integer reproduced exactly (`predeclared_all_match: true`), and
the frozen float64 record reproduced exactly (`frozen_f64_reproduced: true`,
covering 2,076,311,552 / 2,595,389,440 / 7,963,587,520 / 2,580,192,000 /
10,543,779,520).

| quantity | float64 (recorded kill) | float32 (`dtype_multiplier=1.0`) |
|---|---|---|
| M205 one square x 31 layers, raw | 2,076,311,552 | **1,038,155,776** |
| M205 protected (x1.25) | 2,595,389,440 | **1,297,694,720** |
| vs strict headroom 1,986,871,472 | +608,517,968 OVER | **-689,176,752 UNDER (34.686529134482434%)** |
| M204/M206 raw (incl. `a=u^T W`) | 2,084,422,144 | **1,042,211,072** |
| M204/M206 protected | 2,605,527,680 | **1,302,763,840** |
| vs strict headroom | +618,656,208 OVER | **-684,107,632 UNDER (34.431398388914005%)** |
| M203 depth-5 combined | 10,543,779,520 | **5,271,889,760** |
| vs M151 slot 10,291,363,760 | +252,415,760 OVER | **-5,019,474,000 UNDER (48.773652521247584%)** |
| M203 vs strict headroom | OVER | **STILL OVER by 3,285,018,288** |

The M203 asymmetry is stated, not averaged away: float32 pricing flips M203
against the M151 slot but **not** against the strict composed headroom.

## Step 1 - the four recorded identities under float32

Result-normalised relative error `max|X_f32 - X_f64| / max|X_f64|`, on the
existing Philox fixtures of the frozen tests. f32 eps = 1.1920929e-07.

| identity | w=3 | w=4 | w=5 |
|---|---|---|---|
| I1 distinct delta-tilde | 7.058838099663777e-08 | 2.0709964946533769e-07 | 2.789891084060463e-07 |
| I2 compiled aaaa/aaab/aabb (f32 compiler vs f32 brute) | 2.135126338414621e-07 | 2.3844632191779517e-08 | 2.8368222937920966e-07 |
| I2 (f32 compiler vs frozen f64 brute) | 2.028410017964707e-07 | 2.0154087401360558e-07 | 2.5164155281683544e-07 |
| I3 physical K4/K31/K22 mapping | 6.594541724193052e-08 | 2.669476237016602e-07 | 6.837516605763766e-08 |
| I4 source(T)=source(c)+source(T-c) | 3.634286410407317e-07 | **2.812268819151885e-06** | 2.249244868751993e-06 |

| n=256 He-scale | value |
|---|---|
| I5 M203 packed vs expanded, float32 | 3.055125013760283e-07 |
| I5 M203 packed float32 vs float64 | 6.3011482861566e-07 |
| **I6 compiler float32 vs float64 (THE billed square)** | **2.54531923204353e-07** |

Worst predeclared entry: **2.812268819151885e-06** (I4, width 4).
GATE R (`<= 1.0e-05`): **MET on every predeclared entry.**
GATE K (`> 1.0e-03`): **not triggered anywhere, including the extensions.**

I6 is flat in n - 2.5222657193491275e-07 (n=64), 3.177091359260942e-07 (n=128),
2.54531923204353e-07 (n=256) - which
is the load-bearing statement, because the object M205 prices is exactly this one
square per source layer.

## Step 2/3/4 - the attack, and what it changed

The mined falsifier's stated kill mode was catastrophic cancellation in the
quartic collision cells. It was hunted specifically.

**I1 carries an exact structural cancellation** (the `raw` term cancels
`cov[i,i]*cov[j,k]` identically; only `-2 cov[i,j] cov[i,k]` survives), with an
amplification factor kappa measured at exactly `n/2`: 1.500, 2.000, 2.500, 4.000,
6.000, 8.000, 12.000, 16.000, 24.000 for n = 3,4,5,8,12,16,24,32,48. The f32
error tracks it linearly and only reaches **3.6402651881608304e-06 at n=48** -
three orders below GATE K.

**I4 (naive sequential accumulator) does degrade with width**, and this is the
one place the attack landed:

| width | 8 | 12 | 16 | 20 | 24 | 28 | 32 |
|---|---|---|---|---|---|---|---|
| naive f32 | 8.053e-06 | 4.799e-06 | 1.883e-05 | 3.459e-05 | 1.604e-05 | **7.379363385615973e-05** | 3.391e-05 |
| blocked f32 | 2.162e-06 | 8.568e-07 | 9.374e-07 | 1.808e-06 | 1.061e-06 | 1.631e-06 | 2.046e-06 |
| operand-normalised, naive | 4.217e-07 | 4.374e-07 | 2.212e-06 | 1.352e-06 | 2.677e-06 | 5.465e-06 | 2.869e-06 |
| operand-normalised, blocked | 1.132e-07 | 7.809e-08 | 1.101e-07 | 7.068e-08 | 1.770e-07 | 1.208e-07 | 1.731e-07 |
| kappa (cancellation ratio) | 17.23 | 10.97 | 8.51 | 25.58 | 5.99 | 13.50 | 11.82 |

**Attribution: accumulator, not cancellation.** Replacing the n^3-term
*sequential* Python `+=` in `brute_complete_source` with a blocked/pairwise
reduction of the *identical* algebra holds the error at 8.6e-07 - 2.0e-06, flat
in width, and holds the operand-normalised error at 7.1e-08 - 1.8e-07, i.e. at
f32 eps, flat in width. The blocked path was proved algebraically identical: in
float64 it agrees with the frozen naive oracle to 1.496e-15 - 1.143e-14.
kappa does not predict the naive error (kappa is lowest at w=24 where the error is
mid-range, and w=28 has the worst error at kappa 13.5) - the error tracks the
number of sequential accumulations, not the cancellation ratio.

The same attack on the quartic collision cells directly (I3d, up to n=256):

| n | 16 | 32 | 64 | 128 | 256 |
|---|---|---|---|---|---|
| naive f32 | 4.453e-07 | 8.565e-07 | 2.822e-06 | 7.680e-06 | **8.627878278326958e-06** |
| blocked f32 | 1.089e-07 | 2.162e-07 | 3.671e-07 | 1.095e-06 | **1.239e-06** |
| blocked-vs-naive f64 control | 1.273e-15 | 1.617e-15 | 7.306e-15 | 1.020e-14 | 1.184e-14 |

At full width n=256 the quartic collision cells hold the identity to
**8.63e-06 naive / 1.24e-06 blocked** - inside GATE R even with the oracle's own
prohibited accumulator, and two orders inside it once blocked.

## Verification (two-signal, all four planned signals collected)

1. **Independent recomputation of the frozen record** - 2 of 4 f64 diagnostics
   bitwise identical, all 4 same order, all frozen cost integers exact, both
   frozen suites green unmodified (see deviation 3).
2. **Transcription fidelity** - shadow-at-float64 vs frozen module: worst
   absolute difference **0.0**.
3. **Exact-rational ground truth (width 3, `fractions.Fraction`)** - the f64
   compiler is accurate to **2.0193961366861051e-16** against exact rational
   arithmetic, so "f32 vs f64" is a fair parity statement; the f32 compiler is
   **2.0284100182998444e-07 / 1.0106821633707031e-07** (aaab/aabb) against the
   same exact reference, i.e. ~1.7 f32 ulp.
4. **Alt-association cross-check at n=256** - re-deriving the f64 compiler with a
   different einsum reduction order agrees to **1.976e-15**, so the n=256 f64
   reference is not itself an artefact of one BLAS path.
5. **Bit-repeat in fresh interpreters** - steps 0, 1, 2, 4 re-run end to end and
   compared bitwise: **all identical**; I3d n=256 re-derived standalone:
   `8.627878278326958e-06`, **bitwise identical**.

## What this does and does not promote

**Does:** the float32 parity precondition is discharged for the rank-one square
and the two-rectangle terminal contraction. Priced at `dtype_multiplier = 1.0`,
M205 fits the strict M199 composed headroom with 689,176,752 to spare and
M204/M206 with 684,107,632. The cost gate the exact-control lane sits behind
stops being binding, and M199's BLOCKED_OVERLAP slack becomes worth re-deriving.

**Does not (carried verbatim from the mining record):** this removes exactly ONE
of M205's four recorded blockers. The layer-bound physical K4/K31/K22 provider,
the complete-domain proposal / residual-event accounting, and the integrated
native trace all remain absent. **Nothing promotes.** M204's separate kill leg -
M206's refutation of the arithmetic-identical M151 replacement premise (nonzero
collision rows vs M151's zero repeated-label rows) - is untouched by this work
and still stands; only its *cost* leg is cleared. M203 flips against the M151
slot but not against the strict composed headroom.

**Not verified, named as such:** whether the already-booked 98,013,128,528 is
itself f64-priced (the mining record's "upside not claimed"; I did not check it
and it must not be quoted). No truth, scorer, holdout, private, response, MSE,
or leaderboard data was read. Nothing in the held M245/M243/M244 lane was
touched. The frozen Phase-1 selection is untouched.
