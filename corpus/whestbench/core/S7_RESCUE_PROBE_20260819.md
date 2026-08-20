# S7 — THE RESCUE-COUNTER PROBE (INSTRUMENT LANE)

**Date** 2026-08-19. **Status** OFF-PROTOCOL, fully disclosed. No cell, no seed consumed,
no gate, no designation surface. Descriptive only: this document can inform a reading and
can never designate one.

**Custody** burned-Public100 nets (`full` split rows 0–7), the same eight networks and the
same order the production cell ran, licensed for science reads only.

**Compute** local CPU, single-threaded (`OMP/MKL/OPENBLAS/NUMEXPR_NUM_THREADS=1`),
`python -B -P`, `PYTHONDONTWRITEBYTECODE=1`, frozen venv
`C:/Users/strid/.venvs/whestbench-frozen-m178` (whestbench 0.14.0, flopscope 0.10.0,
datasets 5.0.1, numpy 2.4.6 — byte-identical package files to the production venv
`work/whest-v014`, verified by file diff on `domain.py`, `dataset.py`, `scoring.py`,
`runner.py`, `subprocess_worker.py`). Total wall time ≈ 4 minutes. **No file under the
corpus tree was modified**; the arms were wrapped by subclassing and by rebinding names
inside `fold3_estimator`'s module namespace from a scratchpad script.

**Evidence tags** `[O]` observed this session, `[D]` derived, `[R]` reported.

---

## 0. The verdict

**Mechanism II is dead as an explanation of the arm-A excess.** The pilot's regime
classification does differ between arms — about 10% of individual rescue decisions flip —
but the flips carry no systematic direction and no family signature. The two arms that
share the phased-Hadamard pilot family (B and C) disagree with **each other** at
`10.570%`, which is *more* than either disagrees with the Haar arm (`A–B 10.192%`,
`A–C 10.032%`) `[O]`. The dead-and-unrescued counts S7 predicted would be strictly larger
in arm A come out at `A 11535 / B 11525 / C 11461` over the eight nets, and the
within-family control B–C reproduces 86% of the A–C gap `[O]`. Arm A is strictly greater
on 5/8 nets against arm B and 6/8 against arm C, against the pre-registered rule of
"≥ 8/10" `[R, SYNTHESIS §4.1]`.

The derived lever does not exist, and it fails for a reason that is provable rather than
statistical. **For a rotationally-invariant weight vector, a Hadamard basis and a Haar
basis are distributionally identical probes.** Both are orthonormal, so Parseval pins the
sum of squared responses to `r̄²‖w‖²` for both; a Gaussian `w` stays Gaussian under any
orthogonal map, so the 256 responses have the same law and so does their maximum.
Measured over 4,000 draws: `max|⟨u,w⟩|` is `3.0512` under a Haar frame and `3.0495` under
the raw Hadamard — a ratio of `0.9994` `[O]`. The `‖w‖₁/‖w‖₂` ceiling (`12.79` in this
geometry, and the theory's `≈16` is its flat-`w` upper bound, not its typical value)
requires a probe that **selects** the sign pattern `sign(w)`; a Hadamard basis supplies
256 fixed sign patterns out of `2²⁵⁶` and selects nothing.

Two further independent reasons the lever cannot reach the rescue test at all, both read
off the code: `predict()` left-multiplies `W₀` by a fresh per-net Haar rotation in all
three arms, which restores rotational invariance even for structured weights `[O]`; and
the rescue test is applied to `pilot_x = [relu(p); relu(−p)]`, not to the frame rows, so
the flat `±r̄/16` geometry is already gone one ReLU before the first `max(pilot_pre) > 0`
is ever evaluated `[O]`.

**Consequence for the split.** Mechanism II loses its lever, so mechanism I (the degree-4
energy share undercounted ≈ 2.8×) and the residual `λ`/threshold mis-tuning channel carry
the arm-A leg alone. This is not a null result about the counts — the counts genuinely
move — it is a null result about **attribution**: the movement is the frame-draw lottery,
measured against a control that was built to price exactly that lottery.

---

## 1. What was built, and why it can be trusted

### 1.1 The instrument

`s7_probe.py` (scratchpad) imports each arm's **unmodified** sources from
`experiments/frame_completion_129/<arm>/` and observes them at three seams:

| seam | what it yields |
|---|---|
| `Probe(arm.Estimator)._sample_matmul` | the main-loop rescue at layers 1…`depth−4`, recomputed alongside the source and validated against the column count of the weight the source actually passes |
| `fold3_estimator._initial_regimes` (rebound) | the initial dead/kink/on partition at layers 29, 30, 31 |
| `fold3_estimator._refine_dead` / `._refine_on` (rebound) | terminal rescues, demotions, and the full `max/min(pilot_pre)` vectors |

The main-loop rescue is inline in `fold3_estimator.predict` (lines 95–112) and has no
seam, so the probe recomputes it from the same operands with the same expression. That
recomputation is **checked at every layer of every net of every arm** against
`weight.shape[1]`, the column count the unmodified source derived independently; a
divergence would raise. It never raised (24 arm×net runs, 28 layers each) `[O]`.

The per-net Haar rotation is likewise reconstructed in the wrapper and checked
bit-for-bit against the rotated `W₀` the source hands to `_first_sample_matmul`:
identical on all 24 arm×net cells `[O]`.

### 1.2 Fidelity to the production run — the load-bearing check

The probe's classification is only interesting if it is *production's* classification.
`flops_used` is a function of the dead/kink/on split (every set size enters a matmul
dimension), so a digit-exact FLOP match is a sharp fidelity test. Running the
**uninstrumented** arm estimators inside the harness's own `flopscope.BudgetContext`:

| arm | nets | `flops_used` vs `report_<arm>.json` |
|---|---|---|
| armA | 8/8 | digit-exact |
| armB | 8/8 | digit-exact |
| armC | 8/8 | digit-exact |

e.g. `armA/dominic-nelson = 147,582,176,042` this session and in the archive `[O]`.

Getting there found a real trap worth recording: **the production run fed the estimators
`float32` weights.** `whestbench.runner._mlp_to_payload` ships `w.tolist()` and
`subprocess_worker._payload_to_mlp` casts with `fnp.asarray(w, dtype=fnp.float32)`, while
loading the parquet directly through `MLP.from_row` yields `float64` (datasets returns
nested Python lists; the Arrow feature is `float32` but the list round-trip loses it).
flopscope charges float64 at exactly 2× float32, and the direct-load run billed **1.43×**
the archived FLOPs and blew the 272 GFLOP budget `[O]`. Any future off-protocol replay of
these arms must reproduce `_payload_to_mlp`, not `from_row`.

Reassuringly, the classification counts came out **identical** under float64 and float32
(only the margin values moved in the fifth decimal) `[O]` — the split is not living on the
numerical edge of the arithmetic.

### 1.3 The structural invariant, checked

Every initial partition in the estimator is a function of `analytic_alphas`, which come
from `_diagonal_gaussian_pass` on the rotated MLP — and the rotation is the same draw in
all three arms. So the cold sets, the structural-active sets, and the terminal
dead/kink/on partitions **must** be bit-identical across arms, and the pilot can only
rescue or demote inside them.

> Initial (α-only) partitions differing between arms: **0 of 248** (8 nets × 28 loop
> layers + 8 nets × 3 terminal layers) `[O]`

This isolates the channel: the pilot family is the only free variable, and it has exactly
one degree of freedom per candidate neuron.

---

## 2. THE COUNTS, VERBATIM

Eight nets, `full` split rows 0–7, names verified identical to `report_armA.json`
`per_mlp[0:8]`. `dead_alpha = −2.0`, `on_alpha = 3.0`, `pilot_base = 256`,
`fold_pilot_base = 1024`, `n_base = 32,256` (A, C) / `33,024` (B). (Deviation from
the S7 spec, disclosed by the hostile-verification pass 2026-08-19: SYNTHESIS §4.1
asked for ~10 nets *spanning the arm-A MSE range*; this probe took the split's first
eight rows unselected — selection-free, but the count–MSE coupling the spanning was
meant to expose went unprobed.)

### 2.1 Main loop, layers 1…28 — per-net totals over 28 layers

`cold` is bit-identical across arms by §1.3, so it is printed once.

```
net                 cold  resc_A  resc_B  resc_C  unres_A  unres_B  unres_C
dominic-nelson      2015     381     392     409     1634     1623     1606
jimmy-brady         1623     512     515     511     1111     1108     1112
denise-dominguez    1668     485     477     469     1183     1191     1199
melinda-young       1728     501     513     507     1227     1215     1221
laura-quinn         1633     561     542     561     1072     1091     1072
rachel-myers        1783     473     487     494     1310     1296     1289
joshua-keller       1649     484     492     506     1165     1157     1143
michelle-jimenez    1657     522     509     538     1135     1148     1119
TOTAL              13756    3919    3927    3995     9837     9829     9761
```

### 2.2 Terminal fold, layers 29/30/31 — per-net totals over the three layers

```
net                 dRes_A  dRes_B  dRes_C  oDem_A  oDem_B  oDem_C  kink_A  kink_B  kink_C
dominic-nelson          34      33      31      12       9       9     193     189     187
jimmy-brady             64      67      67      10      11      10     423     427     426
denise-dominguez        66      65      62      27      21      22     310     303     301
melinda-young           73      78      73      20      19      23     411     415     414
laura-quinn             81      75      75      14      16      20     447     443     447
rachel-myers            51      50      55      12      10      14     368     365     374
joshua-keller           61      64      63      10       5       9     350     348     351
michelle-jimenez        48      48      50      11      12      15     353     354     359

TOTAL dead_rescued    A=  478  B=  480  C=  476
TOTAL on_demoted      A=  116  B=  103  C=  122
TOTAL final_kink      A= 2855  B= 2844  C= 2859
TOTAL final_dead      A= 1698  B= 1696  C= 1700
TOTAL final_on        A= 1591  B= 1604  C= 1585
```

### 2.3 The S7 statistic — total dead-and-unrescued (main loop unrescued + terminal final dead)

```
net                     A      B      C   A-B   A-C   B-C
dominic-nelson       1933   1923   1908    10    25    15
jimmy-brady          1286   1280   1284     6     2    -4
denise-dominguez     1392   1401   1412    -9   -20   -11
melinda-young        1432   1415   1426    17     6   -11
laura-quinn          1232   1257   1238   -25    -6    19
rachel-myers         1511   1498   1486    13    25    12
joshua-keller        1392   1381   1368    11    24    13
michelle-jimenez     1357   1370   1339   -13    18    31
TOTAL               11535  11525  11461    10    74    64

A-B: mean +1.250  se 5.308  t +0.236  95% CI [-11.30, +13.80]  A larger on 5/8 nets
A-C: mean +9.250  se 5.888  t +1.571  95% CI [ -4.67, +23.17]  A larger on 6/8 nets
B-C: mean +8.000  se 5.355  t +1.494  95% CI [ -4.66, +20.66]  B larger on 5/8 nets   <-- CONTROL
```

**Read the last line first.** B and C share the phased-Hadamard family; between them the
S7 statistic moves by `+64` with `t = +1.49`, against `+74` and `t = +1.57` for the
cross-family A–C contrast. The control absorbs 86% of the effect the hypothesis wanted to
attribute to the pilot type.

### 2.4 Paired t on the probe's own counts, n = 8

```
main-loop rescued  A-B: mean  -1.000  sd 12.649  se 4.472  t -0.224
main-loop rescued  A-C: mean  -9.500  sd 14.813  se 5.237  t -1.814
main-loop rescued  B-C: mean  -8.500  sd 13.491  se 4.770  t -1.782   <-- CONTROL
terminal dead-resc A-B: mean  -0.250  sd  3.412  se 1.206  t -0.207
terminal dead-resc A-C: mean  +0.250  sd  3.655  se 1.292  t +0.193
terminal dead-resc B-C: mean  +0.500  sd  3.071  se 1.086  t +0.461   <-- CONTROL
terminal on-demote A-B: mean  +1.625  sd  2.925  se 1.034  t +1.572
terminal on-demote A-C: mean  -0.750  sd  3.694  se 1.306  t -0.574
terminal on-demote B-C: mean  -2.375  sd  2.066  se 0.730  t -3.252   <-- CONTROL
```

Nine contrasts. The single largest `|t|` in the whole probe is `3.252`, and it is a
**within-family** contrast (B vs C on terminal demotions). Under the pilot-family
hypothesis that cell should have been the quietest one in the table.

---

## 3. DECISION-LEVEL DISAGREEMENT — the sharp form

Net totals can cancel: arm A rescuing neuron 5 and not 9, arm C rescuing 9 and not 5,
gives equal counts and two different estimators. The cold sets are bit-identical across
arms (§1.3), so the symmetric difference of the rescued sets is a well-defined
decision-level disagreement rate.

```
MAIN LOOP  (one decision = one (net, layer, cold neuron); 13,756 decisions)
  A vs B: 1402 / 13756 = 10.192%
  A vs C: 1380 / 13756 = 10.032%
  B vs C: 1454 / 13756 = 10.570%     <-- CONTROL, the HIGHEST of the three

TERMINAL dead rescue (2,176 decisions)
  A vs B:  126 / 2176 =  5.790%
  A vs C:  130 / 2176 =  5.974%
  B vs C:   68 / 2176 =  3.125%      <-- CONTROL

TERMINAL on demotion (1,707 decisions)
  A vs B:   65 / 1707 =  3.808%
  A vs C:   70 / 1707 =  4.101%
  B vs C:   43 / 1707 =  2.519%      <-- CONTROL
```

The main loop is flat: no family structure at all, the control is the largest.

The terminal fold *does* cluster B with C, at roughly half the cross-family rate — and
that clustering has a mechanical cause with nothing to do with detection power. The
main-loop pilot reads frame 0 only (256 rows); the fold pilot reads frames 0–3 (1024
rows). Arm B's frames are `phases[0:128] ∪ {I}` and arm C's are `phases[2:128]`, so:

```
MAIN-LOOP PILOT, frame 0, 256 rows -- bit-identical rows shared
  A/B    0 / 256      A/C    0 / 256      B/C    0 / 256
FOLD PILOT, frames 0..3, 1024 rows -- bit-identical rows shared
  A/B    0 / 1024     A/C    0 / 1024     B/C  512 / 1024
  (arm B frames 2,3 == arm C frames 0,1, verified byte-equal)
```

`[O]` **B and C literally share half of the fold pilot's rows and none of the main-loop
pilot's rows, and their agreement follows exactly that pattern.** The terminal
"family effect" is a shared-sample effect, correctly proportioned, not a Hadamard-versus-
Haar effect. (Also confirmed in passing: arm B's frame 0 is the all-plus Walsh row —
row sum `+256·r̄/16` — while arm C's frame 0 is `H·diag(φ₂)` with row sum `+16·r̄/16`,
reproducing THEORY ledger item 17 `[O]`.)

**The flips are threshold coin-flips.** At a disagreed decision, the median
`|max(pilot_pre)|` is `0.0828` (A–B), `0.0847` (A–C), `0.0818` (B–C), against a per-arm median over **all** cold
decisions of `0.3796` / `0.3848` / `0.3837` and a 10th percentile of `0.0650` / `0.0637` /
`0.0642` (A / B / C) `[O]`. Decisions flip
where the statistic is sitting on zero, which is where any re-draw of 512 pilot rows will
flip it regardless of where those rows came from.

---

## 4. THE DETECTION LEVER, MEASURED DIRECTLY

### 4.1 Layer-1 paired detector on the real nets

At layer 1 the active set is `arange(256)` in every arm by construction, so the rescue
test's weight columns are bit-identical across arms and the **only** difference is the 512
pilot rows. For all 256 layer-1 columns of all 8 nets (n = 2,048 exactly paired triples),
computing the estimator's own statistic `max(pilot_pre, axis=0)`:

```
pooled mean  M_A = 3.55753   M_B = 3.55388   M_C = 3.56346
paired B-A: mean diff -0.003654  se 0.013091  t -0.279   B larger on 49.8%
paired C-A: mean diff +0.005923  se 0.013163  t +0.450   C larger on 50.1%
paired C-B: mean diff +0.009577  se 0.013167  t +0.727   C larger on 50.3%
columns with M > 0 (i.e. "would fire"):  A 2048   B 2048   C 2048   of 2048
```

Coin flips on every pairing, and at layer 1 all 256 columns fire in all three arms, so no
detection difference is even expressible there. `[O]`

Extending to the deeper layers, restricted to the net×layer cells where the entering
active set is bit-identical between the pair (so the pairing stays exact):

```
A-B: n=168  mean -0.038033  se 0.035154  t -1.082   A larger on 50.6%
A-C: n=139  mean -0.014400  se 0.035499  t -0.406   A larger on 52.5%
B-C: n=108  mean +0.034257  se 0.049570  t +0.691   B larger on 48.1%
```

Pooled over all cold decisions unrestricted, the median-of-layer-medians of
`max(pilot_pre)` is `−0.20762` (A), `−0.21306` (B), `−0.20448` (C) — arm A is not the
worst detector; it is indistinguishable. `[O]`

### 4.2 Synthetic isolation of the `‖w‖₁/‖w‖₂` claim

`max_i |⟨u_i, w⟩|` for `w ~ N(0, I₂₅₆)`, 4,000 draws, 256 probe rows:

```
mean ||w||_1 / ||w||_2 = 12.7811          (the theory's lever; ~16 is its flat-w ceiling)
Haar frame                   mean max|<u,w>| = 3.0512   (x1.0000)
raw Hadamard                 mean max|<u,w>| = 3.0495   (x0.9994)
Hadamard x Haar rotation     mean max|<u,w>| = 3.0475   (x0.9988)
ceiling if the probe could CHOOSE any sign pattern: (1/16)*E||w||_1 = 12.7901
```

The Hadamard basis realises `3.05` of an available `12.79` — the same `3.05` a Haar frame
realises. `[O]`

**Why, in one line.** Any orthonormal frame scaled to `r̄` satisfies
`Σ_i ⟨u_i,w⟩² = r̄²‖w‖²` (Parseval), so all three arms' pilots carry *identical total
detection energy*; and an orthogonal map sends a Gaussian `w` to a Gaussian, so for a
generic weight row the 256 responses are identically distributed under Haar and under
Hadamard, and so is their maximum. `‖w‖₁` is the value of an *adaptive* probe
`u = sign(w)/16`, and a fixed basis of 256 rows contains that pattern with probability
`256/2²⁵⁶`. `[D, and measured above]`

---

## 5. SECOND INDEPENDENT SIGNAL — the archived FLOP channel at n = 100

Arms A and C bill the same row count (126 frames, identical `n_base`, identical code
path), so **every** per-net difference in `flops_used` between them is the dead/kink/on
split moving. This channel was measured by the harness on 100 networks and knows nothing
about this probe.

```
mean log(C/A) = -0.000191   sd 0.016608   se 0.001661   t = -0.115
nets where C bills MORE than A: 49 / 100   (exactly equal: 0)
ratio spread: p5 0.97519   p50 0.99955   p95 1.02590

B/A after removing the 129/126 row ratio: mean log -0.000253  t -0.151   47/100 above
B/C after removing the 129/126 row ratio: mean log -0.000063  t -0.046   48/100 above
```

`[O]` Three statements follow, and they agree with the probe on all three:

1. **The splits are not identical between arms** — no net bills exactly equal, and the
   per-net spread is ±2.5% at the 5/95 points. The probe's non-zero disagreement rates are
   real, not instrument noise.
2. **The split difference has no systematic direction** — `t = −0.115` on 100 nets,
   49/100 above unity. (Corrected by the hostile-verification pass 2026-08-19: this is
   a direction-null on the flop-visible *aggregate* of the split, not a higher-power
   measurement of the S7 count itself. Calibrating log-flops per dead-and-unrescued
   neuron on these same nets gives `b = 8.3e-5 ± 18.5e-5` (r = +0.12, 16 within-net
   pairs), so the n = 100 CI maps to a neuron-equivalent bound of roughly ±40 per net
   at the measured coupling — comparable to, not tighter than, the n = 8 count
   channel's ±14. The channel's value is independence, not power.)
3. **B versus C is as quiet as A versus C** — `t = −0.046` versus `t = −0.115`. The
   control again.

---

## 6. CORRECTIONS TO THE THEORY DOCUMENT

Three, all from reading the source and measuring:

1. **`‖w‖₁/‖w‖₂ ≈ 16` is the ceiling, not the value.** For a dense Gaussian row in `R²⁵⁶`
   the ratio is `12.78`; `16` is attained only by a perfectly flat `w`. More importantly
   the ratio is irrelevant here: it prices an *adaptive* probe, and neither pilot is one
   (§4.2). `[O]`
2. **A Hadamard basis is not a better firing detector than a Haar basis at identical
   cost.** THEORY §2.5's central sentence is the claim this probe was built to test, and
   it is false for rotationally-invariant weights, which the per-net Haar rotation
   guarantees regardless of the true weight law. Measured advantage: `×0.9994`. `[O+D]`
3. **"Replaced by the analytic diagonal-Gaussian mean" holds only at the last layer.** In
   `fold3_estimator.predict`, a confirmed-dead neuron in the main loop (layers
   `1…depth−4`) and at layers 29 and 30 is simply dropped from `next_active` / `kink`,
   i.e. its sampled activation is treated as exactly `0` on all `2·n_base` rows and it
   never re-enters. The analytic-mean substitution happens only for `dead32` at
   `mlp.depth−1` (lines 235–237). The misclassification channel is real and is still
   outside every `A_l`; its *form* is column zeroing with downstream propagation, not
   mean substitution. `[O]`

None of the three rescues mechanism II; (3) sharpens what the surviving residual channel
would have to look like if anyone revives it.

---

## 7. ATTACK ON THIS DOCUMENT

**The strongest way this is wrong: n = 8 is small.** The 95% CI on the A–C S7 statistic is
`[−4.67, +23.17]` per net, so a systematic arm-A penalty of up to ~23 extra dead neurons
per net (≈1.3% of the cold pool) is not excluded by the count channel alone. That is the
honest bound, and it is why the conclusion does not rest on the counts. It rests on
(i) the control, which reproduces 86% of the A–C gap at the same `t` and cannot be a
pilot-family effect by construction; (ii) the n = 100 archived FLOP channel, an
independent direction-null on the flop-visible aggregate of the same split
(`t = −0.115`; a diluted proxy for the S7 count itself — coupling calibrated at §5.2);
and (iii) the direct measurement of the lever itself at n = 2,048 exactly paired columns
plus 4,000 synthetic draws, which is not a statistical argument about counts but a
measurement of the mechanism, and it returns `×0.9994`.

**Where the attack landed and changed the answer.** I first read the terminal fold's B–C
clustering (`3.1%` versus `5.8%/6.0%`) as a genuine family signature and was drafting it
as partial support for mechanism II. Checking what else differs between the B and C fold
pilots found the cause: they share 512 of 1024 rows byte-for-byte, and the main-loop
pilot, which shares none, shows no clustering whatsoever. The clustering is a
shared-sample artifact and the corrected reading is in §3.

**The counter-hypothesis I tested rather than re-read.** "The counts are equal by
construction and the probe is measuring nothing." Falsified: the archived n = 100 FLOP
channel shows the splits genuinely differ between arms (0/100 exactly equal, ±2.5%
spread), and the probe's 10% decision-flip rate is the same phenomenon seen directly.
The probe measures a live channel; the channel has no direction.

**What I did not look at.** No per-net MSE modelling of the rescue differences (the probe
records classification, not the error each misclassification costs, so it cannot price the
channel — only rule out a systematic count difference). No re-run at a different rotation
offset (SYNTHESIS §4.2 is still open and still needs a custody ruling). No fresh-seed nets
(§4.3's micro-cell is untouched); note however that §4.3's **P1** — the `A′/A` prediction,
`[0.72, 0.85]` under Repair II versus `[0.97, 1.03]` under Repair I — is now forecastable
from §4 of this document: swapping arm A's frame 0 for a phased-Hadamard row changes the
pilot's detection statistic by `×0.999`, so P1 should land in the Repair-I band. That is a
prediction filed here, not a result.

---

## 8. EVIDENCE LEDGER

| # | claim | level | signal 1 | signal 2 |
|---|---|---|---|---|
| 1 | the probe reproduces production's classification | `[O]` | `flops_used` digit-exact vs `report_arm*.json` on 24/24 arm×net cells | classification counts unchanged between float64 and float32 arithmetic |
| 2 | the wrapper's recomputed rescue equals the source's | `[O]` | `weight.shape[1]` assertion passes at 28 layers × 8 nets × 3 arms | rotated `W₀` reconstruction byte-equal to the source's on 24/24 |
| 3 | initial partitions are pilot-independent | `[O]` | 0 of 248 differ between arms | derivable: they are functions of `analytic_alphas`, and the rotation draw is shared `[D]` |
| 4 | rescue decisions differ between arms at ≈10% | `[O]` | symmetric-difference count, 13,756 decisions | archived n=100 FLOP channel: 0/100 nets bill exactly equal |
| 5 | the difference carries no family signature | `[O]` | control B–C `10.570%` ≥ A–B `10.192%` ≥ A–C `10.032%` | S7 statistic: control B–C `+64`, `t +1.49` vs A–C `+74`, `t +1.57` |
| 6 | no systematic direction in the flop-visible aggregate at n=100 | `[O]` | archived `mean log(C/A) = −0.000191`, `t = −0.115`, n=100 | probe A–C `t = +1.571` at n=8, CI straddles 0 |
| 7 | the Hadamard pilot is not a better detector | `[O]` | layer-1 paired, n=2048: `t = −0.279 / +0.450`, win rates 49.8% / 50.1% | synthetic: `×0.9994` raw Hadamard vs Haar, 4,000 draws |
| 8 | Parseval kills the lever for rotationally-invariant `w` | `[D]` | `Σ⟨u_i,w⟩² = r̄²‖w‖²` for any orthonormal frame | Gaussian law invariant under orthogonal maps; measured ratio `0.9994` |
| 9 | the Haar rotation independently kills it | `[O]` | `predict()` rotates `W₀` in all three arms | measured: Hadamard×rotation `×0.9988` vs Haar |
| 10 | the terminal B–C clustering is shared rows | `[O]` | 512/1024 fold-pilot rows byte-equal (B frames 2,3 == C frames 0,1) | 0/256 main-loop pilot rows shared, and no main-loop clustering |
| 11 | flips sit on the decision threshold | `[O]` | median `\|max(pilot_pre)\|` at a flip `0.082–0.085` | median over all cold decisions `0.380`, p10 `0.064` |
| 12 | arm B's frame 0 is the all-plus Walsh row | `[O]` | row sum `+256·r̄/16` vs arm C's `+16·r̄/16` | reproduces THEORY ledger item 17 independently |
| 13 | production fed float32 weights | `[O]` | `subprocess_worker._payload_to_mlp` source | float64 replay bills 1.43× and exhausts the budget; float32 replay is digit-exact |

**Open, with named checks.** (i) The *cost* of a misclassification — this probe counts
decisions, it does not price them; settling it needs a per-net MSE decomposition with the
rescue set forced to a common choice across arms, which is a new instrument. (ii) The
rotation-offset probe (SYNTHESIS §4.2), still needing a custody ruling. (iii) The
fresh-seed micro-cell (SYNTHESIS §4.3), whose P1 now has a forecast (§7).

**Artifacts.** Probe and analysis scripts, and the raw per-net JSON
(`s7_armA.json`, `s7_armB.json`, `s7_armC.json`), are in the session scratchpad
`…/7c1d8a18-611c-4493-9d65-0b4a9ad5fd33/scratchpad/`:
`s7_probe.py`, `s7_analyse.py`, `s7_sets.py`, `s7_detect.py`, `s7_overlap.py`,
`s7_fidelity.py`. Nothing under the corpus tree was written except this document.
