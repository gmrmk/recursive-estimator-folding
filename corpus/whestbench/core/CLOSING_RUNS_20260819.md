# Closing runs — the smoke sign-flip diagnostic and the untouched-split final gate

Two serialized harness jobs, run one at a time on one host, never concurrently.
Every figure below is read directly from the run artifacts by `gen_report.py`;
no number in this document was transcribed by hand.

**Environment, identical for every scored step.** Frozen venv
`C:/Users/strid/.venvs/whestbench-frozen-m178/Scripts/python.exe` (whestbench
0.14.0, flopscope 0.10.0, numpy 2.4.6, CPython 3.14.4), `whest.exe` from the same
venv, `python -B` with `PYTHONDONTWRITEBYTECODE=1`, and `OMP_NUM_THREADS`,
`OPENBLAS_NUM_THREADS`, `MKL_NUM_THREADS`, `NUMEXPR_NUM_THREADS` all pinned to 1.
Dataset `work/whest-full`, split `full`, sha256
`5b00938b6bd809fe80acef08772c5654edf467863225ca9e304b76c779ecf433`, 1000 rows.
Runner `subprocess`, `--flop-budget 272000000000`, `--detail full`.

**Row selection.** `whest run` exposes no row offset; `--n-mlps N` takes the FIRST
N rows. An unburned block is therefore `--n-mlps 132` (or 105) plus a predeclared
index restriction applied in the analysis layer, exactly as the 2026-08-19 19:46
UTC channel entry recorded. The restriction is the only row selection performed.

**Custody.** Public100 rows 0-99 are development-burned. Rows 100-131 were
untouched before these runs. Measured here, from the estimator side: the 132 rows
carry 132 distinct `mlp_seed` values and rows 0-99 share
0 seeds with rows 100-131.

**Ordering, and why it departs from the request.** Job (2) was run FIRST. Job (1)
spends rows 100-104, and running it first would have put holdout values in front of
the operator before the final gate was measured. Reversing the order costs nothing
and removes that leak; nothing else about either job changed.

**Fence.** `fold_floor_splice`, `frame_completion_129`, `row_blocked_production`,
`bprime_rephase` were read-only throughout. Arm and candidate sources were COPIED
to scratch and verified sha256-identical to the fenced originals both before and
after every run. Fenced-tree newest-file mtimes, identical before and after:
`frame_completion_129` 2026-08-19T09:34:40.855039Z, `fold_floor_splice`
2026-08-19T06:27:51.090848Z, `row_blocked_production` 2026-08-07T20:27:16.487235Z,
`bprime_rephase` 2026-08-19T19:31:22.571635Z.

---

## Job 1 — the smoke sign-flip diagnostic

**Role: OFF-PROTOCOL DIAGNOSTIC, fully disclosed.** This is not a gated cell. There
is no predeclaration, no GATE_TOKEN, no ledger write, no verdict, no threshold and
no p-value. Per the rung-2k law at n = 5, every per-net value is printed verbatim
and the block ratios are point estimates only. Rows 0-4 are burned and descriptive;
rows 100-104 were untouched and are spent by this run.

### The question, and the answer

The 129 cell's 5-net smoke at harness seed 424242 measured arm B WORSE (raw MSE
ratio 1.0387) while production at seed 0 with n = 100 measured 0.6662 — a two-anomaly
draw of joint probability order 1e-4. The open question was whether seed 424242's
sample explains the flip (an unlucky five-net draw) or whether the seed moves the
per-net rotations enough to flip the sign at n = 5.

**Neither. The harness seed moves exactly one thing, and it is arm A's frame set.**

Read off the fenced sources first, then measured:

- Arm A's 126 frames are drawn in `setup()` from `ctx.seed`
  (`armA/orthogonal_fold3.py:21`, `rng = fnp.random.default_rng(ctx.seed)`), so arm A
  MOVES with `--seed`.
- Arm B's frame set at width 256 is the deterministic real-MUB/Kerdock construction
  with no RNG on the path at all (`armB/estimator.py:42-82`), so arm B is INVARIANT
  to `--seed`.
- The per-net Haar rotation in BOTH arms is seeded by the dataset's own per-MLP seed
  (`_haar_rotation(int(mlp.seed), mlp.width)`), not by `--seed`, so the rotations move
  with neither the harness seed nor `--n-mlps`.
- With `--dataset`, `--seed` seeds estimator setup ONLY; the MLPs come from the
  dataset. `--n-mlps 5` therefore selects the SAME five networks at both seeds.

Three predictions were filed against those readings before the analysis ran, and all
three hold:

| prediction | outcome |
|---|---|
| P1 arm B rows 0-4 bit-identical at seed 0 and seed 424242 | **True** (MSE True, billed FLOPs True) |
| P2 arm A rows 0-4 differ between the two seeds | **True** (MSE differ True, billed FLOPs differ True) |
| P3 rows 0-4 bit-identical to the SEALED n=100 production reports | **arm A True, arm B True** |
| same five networks at both seeds | **True** |

On the same five rows, arm A's mean raw MSE moves and arm B's does not move at all:

```
arm A  seed 0 2.72416167490519e-07  ->  seed 424242 2.2403511650281872e-07   -17.7600%
arm B  seed 0 2.326969280375124e-07  ->  seed 424242 2.326969280375124e-07   +0.0% (exactly zero)
```

The flip is arm A's denominator falling 17.76% on a 126-frame Haar re-draw. It is
not a network-subset effect — the networks are identical — and it is not a rotation
effect — the rotations are identical, which arm B's bit-level invariance proves,
since a rotation change would have moved arm B too.

### The smoke reproduces exactly

| quantity | recorded smoke | this run, rows 0-4 seed 424242 |
|---|---:|---:|
| raw MSE ratio B/A | 1.0387 | **1.0386627403324278** |
| FLOP-only score ratio B/A | 1.0518 | **1.05171104404762** |

The recorded smoke is reproduced to every printed digit. That settles a second open
question in passing: the smoke WAS run against the dataset on rows 0-4, so no
"seed-specific network subset" ever existed to explain it.

### The four blocks, and what n = 5 is worth

| block | n | raw MSE B/A | FLOP-only score B/A | lawful score B/A |
|---|---:|---:|---:|---:|
| rows 0-4, seed 0 (burned) | 5 | 0.8541964677834734 | 0.87901236908548 | 0.8793655935171254 |
| rows 0-4, seed 0, from the SEALED production reports | 5 | 0.8541964677834734 | 0.87901236908548 | 0.8804349937655691 |
| rows 0-4, seed 424242 (burned) | 5 | 1.0386627403324278 | 1.05171104404762 | 1.044728970050767 |
| rows 100-104, seed 0 (untouched) | 5 | 1.0212486718191618 | 1.022527635583909 | 1.0130327691614005 |
| production reference, seed 0 | 100 | 0.6661955563966138 | 0.68165697632704 | — |

Three different five-net blocks give 0.854, 1.039 and 1.021 against the n = 100
value of 0.666. Changing the seed flips the sign; changing WHICH five rows also
flips the sign, at the production seed, on data no development had touched. At
n = 5 this ratio is not an estimate of anything, which is the rung-2k reading and
is now demonstrated twice over rather than argued.

The lawful column for the sealed production block differs from this run's
(`0.8804349937655691` against `0.8793655935171254`) purely in
residual wall time; the raw-MSE and FLOP-only columns are bit-identical.

### Per-net values, verbatim

**rows 0-4, harness seed 0**

| idx | network | arm A raw MSE | arm B raw MSE | B/A | arm A billed FLOPs | arm B billed FLOPs |
|---:|---|---:|---:|---:|---:|---:|
| 0 | `dominic-nelson` | 2.8297770882090845e-07 | 1.8909281607193407e-07 | 0.668225129321432 | 147582176042 | 151887257529 |
| 1 | `jimmy-brady` | 1.7551386122249824e-07 | 2.3167694962467067e-07 | 1.3199923243154836 | 184970995495 | 190014374826 |
| 2 | `denise-dominguez` | 5.467906021294766e-07 | 3.155059573600738e-07 | 0.5770142283560389 | 175071684231 | 176842792925 |
| 3 | `melinda-young` | 1.4740010101377266e-07 | 2.7606225216914027e-07 | 1.872876953750159 | 177799513771 | 181064294185 |
| 4 | `laura-quinn` | 2.0939856426593906e-07 | 1.5114666496174323e-07 | 0.7218132822046711 | 187781195412 | 188362973886 |

**rows 0-4, harness seed 424242**

| idx | network | arm A raw MSE | arm B raw MSE | B/A | arm A billed FLOPs | arm B billed FLOPs |
|---:|---|---:|---:|---:|---:|---:|
| 0 | `dominic-nelson` | 1.3997045300584432e-07 | 1.8909281607193407e-07 | 1.3509480894802754 | 148126740397 | 151887257529 |
| 1 | `jimmy-brady` | 1.8024618952949822e-07 | 2.3167694962467067e-07 | 1.285336185077885 | 185725343663 | 190014374826 |
| 2 | `denise-dominguez` | 3.777644792535284e-07 | 3.155059573600738e-07 | 0.8351922287228304 | 172895543955 | 176842792925 |
| 3 | `melinda-young` | 2.7179385142517276e-07 | 2.7606225216914027e-07 | 1.015704552261156 | 178437931863 | 181064294185 |
| 4 | `laura-quinn` | 1.5040060930004984e-07 | 1.5114666496174323e-07 | 1.0049604563782386 | 191447535699 | 188362973886 |

**rows 100-104, harness seed 0 (untouched)**

| idx | network | arm A raw MSE | arm B raw MSE | B/A | arm A billed FLOPs | arm B billed FLOPs |
|---:|---|---:|---:|---:|---:|---:|
| 100 | `stephanie-robles` | 5.406313334788138e-07 | 4.71395878776093e-07 | 0.8719359193311833 | 172011272867 | 178607308214 |
| 101 | `alicia-jones` | 7.601009315294505e-07 | 4.0047578409030393e-07 | 0.5268718501429535 | 172169826260 | 177568608807 |
| 102 | `chad-garcia` | 4.0575292814537534e-07 | 9.441348538530292e-07 | 2.3268713257806963 | 158566536217 | 161332391430 |
| 103 | `janet-smith` | 3.311374427994451e-07 | 6.376614010150661e-07 | 1.9256698838532391 | 169356014644 | 171272993277 |
| 104 | `amanda-irwin` | 5.594372964878858e-07 | 1.9857608890561096e-07 | 0.35495682921439076 | 174153051635 | 175338533716 |

### Compute

```
armA --n-mlps 105 --seed 0        2026-08-20T00:06:41Z -> 00:19:23Z   762 s   rc=0
armB --n-mlps 105 --seed 0        2026-08-20T00:19:46Z -> 00:32:09Z   743 s   rc=0
armA --n-mlps 5   --seed 424242   2026-08-20T00:32:51Z -> 00:33:31Z    40 s   rc=0
armB --n-mlps 5   --seed 424242   2026-08-20T00:33:31Z -> 00:34:09Z    38 s   rc=0
```

Rows 5-99 were evaluated as a by-product of reaching rows 100-104 with `--n-mlps 105`;
they are already burned and are not analysed here.

---

## Job 2 — the untouched-split final gate

**Role: descriptive, disclosed, one evaluation on an untouched split.** This closes
the ten-step contract's last unrun item. It is not a gated cell and writes no ledger
record. The incumbent is `row_blocked_production/candidate_source`; the candidate is
`v31_guards/package_source` (Kerdock v3.1 GUARDS = frozen v3 + M186 + M187).

Both package copies were sha256-verified against the fenced originals, and the
candidate's eight hashes match the sealed `v31_results.json` G0 record file for file,
including `estimator.py` `5e7d52156b330bf63ac4ff0e0f38d864b32677f82bc8ed4d1382787a27d3e0c9`.

### The answer

**The recorded relationship does not reproduce on the untouched split.** On rows
100-131 the candidate/incumbent ratio lands ABOVE one on all three channels, against
the recorded 0.7630845:

| channel | rows 0-99 (burned, this run) | rows 100-131 (untouched) | bootstrap 95% CI, untouched | se_log |
|---|---:|---:|---:|---:|
| raw final-layer MSE | 0.8072029587689873 | **1.1090186370260011** | [0.83568831221551, 1.41166149300596] | 0.1352768670544865 |
| FLOP-only adjusted score | 0.7956499857199367 | **1.083424919449592** | [0.8175691978249092, 1.3785746553723564] | 0.13497947703642996 |
| lawful adjusted score | 0.7752913926540259 | **1.0577448695371092** | [0.799420860135626, 1.3445063058542202] | 0.13438713934853255 |
| *recorded, rows 0-99* | *0.7630845* | — | — | — |

Distances, in the untouched block's own log-unit standard errors:

| channel | from the recorded 0.7630845 | from parity (1.0) |
|---|---:|---:|
| raw final-layer MSE | 2.764 se_log | 0.765 se_log |
| FLOP-only adjusted score | 2.597 se_log | 0.594 se_log |
| lawful adjusted score | 2.430 se_log | 0.418 se_log |

So the untouched split excludes the recorded advantage at roughly 2.4 to 2.8 se_log,
and does NOT distinguish the two estimators from parity at 0.4 to 0.8 se_log. The
honest verdict is that the recorded 0.7631 does not transfer, not that the incumbent
wins.

### Guard-fire counts — the v3.1 canary predeclaration

**Zero, on every net, on every channel.**

| counter | all 132 rows | rows 100-131 |
|---|---:|---:|
| `m186_empty_regime_fired` | 0 | 0 |
| `m187_finite_output_fired` | 0 | 0 |
| `m187_entries_nonfinite` | 0 | 0 |
| `m187_entries_replaced_analytic` | 0 | 0 |
| `m187_entries_clamped` | 0 | 0 |
| records written | 132 | 32 |

**How the counts were obtained, and why they are trustworthy.** Guard activations
live in `self.last_guard_report` on the estimator instance, which the harness report
does not carry. A recorder subclass (`estimator_probe.py`) was added to the scratch
copy: it calls `super().predict(...)`, returns that object unchanged, performs no
array arithmetic and no flopscope op, and appends one JSON line per predict. Billed
FLOPs and raw MSE are therefore bit-identical to the uninstrumented package — measured,
not asserted: an instrumented and an uninstrumented two-net run returned identical
`final_layer_mse` and identical `flops_used`. Only residual wall time is perturbed,
which is why the FLOP-only channel is reported alongside the lawful one.

The recorder writes on every predict, fired or not, so the line count is its own
liveness proof: 132 records for 132 scored networks. Vacuity was
checked separately on synthetic nets only (no dataset network, no seed consumed): the
recorder reports `m186_empty_regime_fired: true` on the all-negative-shift net and
`m187_finite_output_fired: true` with `m187_entries_nonfinite: 164` on the He x 1e3
net, the latter reproducing the sealed `v31_results.json` G2 figure exactly. A zero
here is therefore a measured zero, not a silent probe.

### Structural integrity

| check | incumbent | candidate |
|---|---:|---:|
| failed networks, rows 100-131 | 0 | 0 |
| minimum score multiplier, rows 100-131 | 0.5782706728492647 | 0.5608447682426471 |

No network failed and none sits on the 0.1 multiplier floor, so the metered-regime
premise holds on the untouched block.

### Aggregates

| quantity | rows 0-99 incumbent | rows 0-99 candidate | rows 100-131 incumbent | rows 100-131 candidate |
|---|---:|---:|---:|---:|
| raw final-layer MSE | 3.089542512668686e-07 | 2.493887857468735e-07 | 3.340880228019927e-07 | 3.705098436945775e-07 |
| FLOP-only adjusted score | 1.942097061347884e-07 | 1.5452294991281748e-07 | 2.1463197799143754e-07 | 2.3253763346667982e-07 |
| lawful adjusted score | 2.0830442601794825e-07 | 1.6149662854345261e-07 | 2.3031117402163912e-07 | 2.4361046271845714e-07 |
| mean billed FLOPs | 173794057943.81 | 170493906987.46 | 175279276646.5 | 172130818296.125 |
| mean effective compute | 186291350850.11786 | 178160909488.22247 | 188067619758.92462 | 180396992983.4123 |
| mean residual wall time (s) | 0.12497292906307848 | 0.07667002500762464 | 0.12788343112424627 | 0.08266174687287275 |

### The burned block reproduces the record — in the billed channel exactly

Rows 0-99 came along with `--n-mlps 132`, which makes them a free reproduction check
against `ROW_BLOCKED_WINOGRAD_PRODUCTION_REPORT.md` and the v3.1 designation record.

| quantity | recorded | this run, rows 0-99 | delta |
|---|---:|---:|---:|
| incumbent mean billed FLOPs | 173.794058B | 173.794058B | **exact to the printed digit** |
| incumbent raw MSE | 3.089460087e-07 | 3.089542512668686e-07 | +0.00267% |
| incumbent mean effective compute | 189.852556B | 186.291351B | -1.876% |
| incumbent mean residual (s) | 0.160585 | 0.12497292906307848 | -22.176% |
| incumbent lawful adjusted | 2.121762464e-07 | 2.0830442601794825e-07 | -1.825% |
| v3.1 lawful adjusted | 1.6190840245440636e-07 | 1.6149662854345261e-07 | -0.254% |
| v3.1 / incumbent lawful ratio | 0.7630845 | 0.7752913926540259 | +1.600% |

Reading, at its earned level. Billed FLOPs reproduce the record exactly, so the
estimator, dataset and budget are the recorded ones. Raw MSE differs by 2.7e-5
relative, the size the production report itself attributes to float32 reassociation
(it records -0.001704% for the Winograd reassociation); the single-thread BLAS pinning
used here is the plausible source and is NOT verified — the settling check is a
multi-threaded rerun, about 15 minutes. The lawful channel is 1.8% low because this
host's residual wall time is 22% below the recorded run's, which is the machine-state
channel the 129 cell's predeclaration already names as non-reproducible. The burned
block therefore reproduces the record at 0.7753 against 0.7631 — same conclusion,
residual-channel drift of +1.6%.

### The attack, and it lands

The strongest counter-hypothesis to "the relationship reverses" is that a ratio of
MEANS on a heavy-tailed channel at n = 32 is decided by two or three networks. Tested:

| idx | network | incumbent FLOP-only | candidate FLOP-only | excess | share of block excess |
|---:|---|---:|---:|---:|---:|
| 110 | `veronica-gonzalez` | 5.208343e-07 | 1.109524e-06 | 5.8869e-07 | 102.7% |
| 126 | `anthony-torres` | 1.839003e-07 | 6.405855e-07 | 4.5669e-07 | 79.7% |
| 115 | `douglas-kirk` | 2.618104e-07 | 6.909767e-07 | 4.2917e-07 | 74.9% |
| 102 | `chad-garcia` | 3.383941e-07 | 5.024091e-07 | 1.6402e-07 | 28.6% |
| 103 | `janet-smith` | 2.208975e-07 | 3.465748e-07 | 1.2568e-07 | 21.9% |
| | **block total excess** | | | **5.7298e-07** | 100% |

```
untouched FLOP-only ratio of means      1.083424919449592
leave-one-out range over the 32 nets    [0.9975252042021331, 1.1270560567880121]
minimum attained by dropping idx 110 (veronica-gonzalez)
```

**One network carries the whole reversal.** `veronica-gonzalez` alone contributes
102.7% of the block's total excess, and dropping it returns the ratio to 0.9975 —
parity. The tail-robust summaries stay on the candidate's side of one, and they stay
close to their burned-block values:

| summary | rows 0-99 | rows 100-131 |
|---|---:|---:|
| median per-net FLOP-only ratio | 0.8137135338200052 | 0.8381505428334922 |
| geometric mean of per-net ratio | 0.8042953587545854 | 0.9169049830047887 |
| nets where the candidate is better | 61/100 | 18/32 |
| paired per-net mean log-ratio | -0.21778871562887858 | -0.08675142931918366 |
| paired t on that mean | -3.396 | -0.810 |

So the DIRECTION survives the untouched split and the MAGNITUDE does not. Under the
ratio-of-means convention the recorded 0.7631 is excluded; under the per-net median
or geometric mean the candidate still leads, by 0.838 and 0.917 against 0.814 and
0.804 on the burned block. Which arm happens to draw the worst network decides the
sign of the ratio of means at this n. On rows 0-99 the incumbent held the worst net
(max/mean 4.56 against the candidate's 3.75); on rows 100-131 the candidate does
(max/mean 4.77 against the incumbent's 2.46).

### rung-2k, reported at filing

`se_log` is a rung-2 statistic, so at n = 32 its own sampling error is governed by
the rung-4 moment of the per-net influence `u_i = y_i/mean(y) - x_i/mean(x)`:
`rel(se) = sqrt((g2(u)+2)/(4n))`, `eff df = 1/(2 rel^2)`, window `se*(1 +- 1.96 rel)`.

| channel | influence excess kurtosis | rel error of se | eff df | 95% window on se_log |
|---|---:|---:|---:|---:|
| raw final-layer MSE | 1.8170108922619992 | 0.17268583495989726 | 16.767046730137295 | [0.0909747416741881, 0.1840662967598008] |
| FLOP-only adjusted score | 2.1710175363683373 | 0.18051613363596516 | 15.34397768457338 | [0.08884805918662814, 0.18614314214544248] |
| lawful adjusted score | 2.184896368878092 | 0.18081621299501904 | 15.29309076228271 | [0.08838514242470757, 0.1854225154424889] |

The se is good to about +-18% at 95%, i.e. roughly 15 effective degrees of freedom.
Any distance quoted above in se_log units inherits that window; the 2.4-2.8 se_log
exclusion of the recorded ratio would still exceed 2 se_log at the wide edge of the
window, and the 0.4-0.8 se_log distance from parity would not reach 1 se_log at the
narrow edge. No gate is applied and no p-value is claimed.

### Per-net values, rows 100-131, verbatim

| idx | network | incumbent raw MSE | candidate raw MSE | incumbent billed FLOPs | candidate billed FLOPs | incumbent FLOP-only | candidate FLOP-only | incumbent lawful | candidate lawful |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | `stephanie-robles` | 8.259291917056544e-07 | 4.764702339343785e-07 | 174192688725 | 169246004543 | 5.289368624988011e-07 | 2.964731006509636e-07 | 5.671196600394482e-07 | 3.081041770330797e-07 |
| 101 | `alicia-jones` | 2.5619246457608824e-07 | 4.2866312810474483e-07 | 175611332870 | 168191582281 | 1.6540551535094526e-07 | 2.65064447725956e-07 | 1.778604720756827e-07 | 2.763641338373204e-07 |
| 102 | `chad-garcia` | 5.82834616125183e-07 | 8.809000178189308e-07 | 157923331385 | 155131432024 | 3.3839405965068574e-07 | 5.024091221846245e-07 | 3.6421761897640204e-07 | 5.235144183722049e-07 |
| 103 | `janet-smith` | 3.5804561093755183e-07 | 5.888755367777776e-07 | 167811352704 | 160081933208 | 2.2089749375426718e-07 | 3.4657475862604905e-07 | 2.384854312556207e-07 | 3.642036788130935e-07 |
| 104 | `amanda-irwin` | 3.9771606452632113e-07 | 1.3905079754295002e-07 | 174083118197 | 174880360040 | 2.545428406977251e-07 | 8.940166741970679e-08 | 2.7355877167044713e-07 | 9.282451008899124e-08 |
| 105 | `ashley-jackson` | 3.0451153065769176e-07 | 2.6245319872941764e-07 | 187579002501 | 183484503073 | 2.0999988665743567e-07 | 1.7704446598818572e-07 | 2.2299400940456056e-07 | 1.846222714004633e-07 |
| 106 | `christopher-cruz` | 1.517664998118562e-07 | 2.743887250744592e-07 | 173173956435 | 170524413185 | 9.662501921584861e-08 | 1.72021971793759e-07 | 1.0297361838712747e-07 | 1.795131370845126e-07 |
| 107 | `samuel-ferguson` | 2.6819952836376615e-07 | 2.541049184401345e-07 | 190114157911 | 186569489101 | 1.8745782164339984e-07 | 1.742949441596587e-07 | 2.0144587655940053e-07 | 1.8369830198261416e-07 |
| 108 | `abigail-singleton` | 6.922005724163682e-08 | 2.0674558243172214e-07 | 168539581946 | 165188837895 | 4.289088055067522e-08 | 1.255590533155188e-07 | 4.666222593740671e-08 | 1.3220350668690962e-07 |
| 109 | `brent-harris` | 4.1010986251421855e-07 | 2.489990151843813e-07 | 170800176346 | 163422235620 | 2.575251354362586e-07 | 1.496028519434188e-07 | 2.753541036790354e-07 | 1.5867297966196814e-07 |
| 110 | `veronica-gonzalez` | 7.830404342712427e-07 | 1.6793533177406061e-06 | 180919040125 | 179706352171 | 5.208342784831484e-07 | 1.1095237453582009e-06 | 5.617501273951282e-07 | 1.1634637716424287e-06 |
| 111 | `martha-kline` | 3.869500915243407e-07 | 4.2335869920862024e-07 | 171832746332 | 171495869154 | 2.4445109161781697e-07 | 2.669274561937102e-07 | 2.626658708726676e-07 | 2.7963950175153975e-07 |
| 112 | `holly-rich` | 3.260210803546215e-07 | 4.988960426999256e-07 | 173285555311 | 170298386653 | 2.0770126453067185e-07 | 3.123573205123659e-07 | 2.2570814006894594e-07 | 3.2726739742404754e-07 |
| 113 | `kelly-brown` | 1.9411876905905956e-07 | 1.651995091833669e-07 | 188997232359 | 185046139086 | 1.3488202243050786e-07 | 1.123879829164862e-07 | 1.4461418827988117e-07 | 1.1881510624726221e-07 |
| 114 | `christian-nelson` | 3.7244922168611083e-07 | 2.122742301935432e-07 | 179822608438 | 180412357199 | 2.462308476261006e-07 | 1.407974053008098e-07 | 2.6593432887721943e-07 | 1.4795302132278284e-07 |
| 115 | `douglas-kirk` | 4.162865252510528e-07 | 1.1440864682299434e-06 | 171065919107 | 164275750282 | 2.618104303453335e-07 | 6.909767020439614e-07 | 2.850371676174453e-07 | 7.280606668589525e-07 |
| 116 | `howard-martinez` | 3.468261127181904e-07 | 1.750778437781264e-07 | 173790110615 | 172467756678 | 2.2159907534362047e-07 | 1.110120697074809e-07 | 2.3835346684633673e-07 | 1.1667617903042227e-07 |
| 117 | `shelly-sanchez` | 2.0778145426447736e-07 | 2.2963092760619475e-07 | 185380218761 | 180349055098 | 1.4161239502216004e-07 | 1.5225632652593554e-07 | 1.5200677682405369e-07 | 1.5900161676325625e-07 |
| 118 | `kirsten-clements` | 4.76589065101507e-07 | 3.0520203608830343e-07 | 180973661813 | 180781632129 | 3.1709583930681603e-07 | 2.0284897872477006e-07 | 3.3902216013952303e-07 | 2.1241705141665176e-07 |
| 119 | `james-james` | 1.669532849746247e-07 | 1.195647598706273e-07 | 174008197059 | 172440083500 | 1.0680602982173484e-07 | 7.580057785201626e-08 | 1.1493216788168971e-07 | 7.922386198613358e-08 |
| 120 | `kevin-brennan` | 2.4126211428665556e-07 | 1.302278462844697e-07 | 180149206813 | 174960662026 | 1.5979109751017778e-07 | 8.376746397114332e-08 | 1.704423054808744e-07 | 8.702417519866219e-08 |
| 121 | `melinda-kennedy` | 2.2267244048634893e-07 | 1.378358120973644e-07 | 171415329349 | 168652596188 | 1.403289328048276e-07 | 8.546458660993324e-08 | 1.5095872571700887e-07 | 9.062529124112864e-08 |
| 122 | `kirk-west` | 1.5028292921215325e-07 | 7.530050538662181e-08 | 184874104472 | 179933299638 | 1.0214493366002132e-07 | 4.981275146552888e-08 | 1.097852404270264e-07 | 5.2163649839221563e-08 |
| 123 | `angela-johnson` | 1.7000806451505923e-07 | 1.9067553580498497e-07 | 169878579817 | 168423670664 | 1.0617914910755578e-07 | 1.1806718252242842e-07 | 1.134121172504156e-07 | 1.2290649265266444e-07 |
| 124 | `sharon-mitchell` | 2.174997746351437e-07 | 1.6469257957396621e-07 | 190948031699 | 189688409000 | 1.5268806566748814e-07 | 1.1485394629960128e-07 | 1.6274192080708247e-07 | 1.192059295889593e-07 |
| 125 | `jennifer-morton` | 3.1037561143421044e-07 | 1.5328825497817888e-07 | 174974097654 | 171893466961 | 1.9966063435481432e-07 | 9.687224114926814e-08 | 2.1245219449019882e-07 | 1.0158956883578334e-07 |
| 126 | `anthony-torres` | 2.954858473458444e-07 | 1.045644694386283e-06 | 169283506856 | 166633340835 | 1.839002958272839e-07 | 6.405855468822753e-07 | 1.9680301134210581e-07 | 6.669730825444852e-07 |
| 127 | `michael-cruz` | 3.626986710969504e-07 | 4.4126568354840856e-07 | 183911890928 | 180945748242 | 2.4523749425923857e-07 | 2.9354834295288374e-07 | 2.6076687786106746e-07 | 3.08656176806317e-07 |
| 128 | `carol-wagner` | 4.66173503355094e-07 | 2.437825514789438e-07 | 167624404551 | 166319070200 | 2.8728697028437955e-07 | 1.4906502681235868e-07 | 3.066504464573132e-07 | 1.568745290468907e-07 |
| 129 | `ruth-fuller` | 2.5287943117291434e-07 | 1.5684940990468021e-07 | 157289623015 | 152549776962 | 1.462327588141005e-07 | 8.796817094698632e-08 | 1.5637245225678388e-07 | 9.39366830882569e-08 |
| 130 | `kristen-riley` | 1.9399639938910695e-07 | 2.0102635289731552e-07 | 166458727366 | 164990487245 | 1.1872203586726838e-07 | 1.219391026235787e-07 | 1.2743025609472044e-07 | 1.2765735634376558e-07 |
| 131 | `robert-english` | 5.05940477069089e-07 | 2.024307832471095e-07 | 172225361228 | 169201484595 | 3.2035213758489155e-07 | 1.2592495975418966e-07 | 3.4144583771983217e-07 | 1.3168258239985833e-07 |

### Compute

```
incumbent --n-mlps 132 --seed 0   2026-08-19T23:33:35Z -> 23:48:56Z   921 s   rc=0
v3.1      --n-mlps 132 --seed 0   2026-08-19T23:49:36Z -> 2026-08-20T00:04:17Z   881 s   rc=0
```

---

## What is claimed, and at what level

**Observed this session.** Every figure in the tables above; the four P-checks; the
guard-fire zeros with their liveness and vacuity proofs; the exact reproduction of the
recorded smoke ratios and of the sealed production per-net values on rows 0-4; the
exact reproduction of the incumbent's recorded mean billed FLOPs; fence integrity by
sha256 and mtime before and after.

**Derived.** That the harness seed's only live channel is arm A's frame draw — from
the source readings plus arm B's measured bit-level invariance, which no other
mechanism explains. That the untouched-block reversal is a tail artefact of the
ratio-of-means at n = 32 — from the leave-one-out collapse to 0.9975 and the stability
of the median and geometric mean across blocks.

**Assumed, and named.** That the 2.7e-5 raw-MSE gap against the recorded production
figures is float32 reassociation from single-thread BLAS pinning. Not verified; the
settling check is a multi-threaded rerun of the incumbent at `--n-mlps 132`, about 15
minutes.

**Not done.** No ledger record was written, no verdict was produced, no cell was
predeclared or sealed, and no promotion or designation was touched. Neither job is a
gated instrument and neither may be cited as one.

**What rows were spent.** Rows 100-131 are no longer untouched: 32 rows for job 2
(incumbent and v3.1) and rows 100-104 additionally for job 1 (arms A and B). Rows
132-999 of the `full` split remain unburned.

