# DEG-4 ENERGY SHARE — trace to sources, and the discrimination of mechanism I

Date: 2026-08-19 · Rung: **R0/R1 only** (committed artifact reads + exact arithmetic;
no forwards, no nets, no estimator, no new measurement) · Runner: two scratchpad scripts,
scalar arithmetic, no writes outside `core/` and the scratchpad.

**Evidence tags** `[O]` observed this session, `[D]` derived this session, `[R]` reported
by a committed artifact, `[A]` assumed, `[GAP]` named hole.

---

## 0. VERDICT

**UNRESOLVED — and both of the two clean readings are individually refuted by exact
arithmetic, which is itself the useful result.**

1. **The "carrier-indexing error" reading is REFUTED.** `runner_fc129.py`'s `share_l`
   slot is unambiguously the **Kerdock-126 arm's** per-degree MSE share, and r0 §5's
   `0.45 %` is a Kerdock-arm per-degree MSE share. Same object, same carrier, correctly
   indexed. Proven by reproducing all three committed forecast figures to the last digit
   from r0's own table `[O, §3.1]`. Transferring r0's `0.45 %` onto the Haar arm under
   the exact defect ratios gives **16.2 %**, not `1.26 %` — a factor **12.8x** the wrong
   way. The corpus already commits that 16 % independently `[R, ULTRAMATH_SLATE entry 1:
   "~16% of estimator error on the Haar host … ~1/36 after the swap"; this trace derives
   16.23 % and 1/36.1]`. **The excess gain does not close as an accounting correction.**

2. **The "0.45 % is genuinely pinned on the right object" reading is also REFUTED.** The
   `0.45 %` is `[D]` from the **infinite-width mean-field iterated arc-cosine kernel** and
   from nothing else. No committed artifact measures the deployed nets' `E_4/E_{≥6}`.
   Worse: the mean-field spectrum's **shape** is contradicted at the readout by a
   sealed-gate committed measurement, by **1.66x / 3.89x / 5.82x** at degrees 8 / 12 / 16
   `[O, §4.2]`.

3. **Mechanism I's direction is corroborated by a second, independent, first-principles
   per-degree profile that the corpus already carries and never applied here.** The exact
   ReLU **kink tail** `λ_n²` — measured-validated at four rungs to within 17 % — puts
   degree 4 at **3.347x** degree 6 where the mean-field kernel puts it at **1.410x**, a
   **2.374x** correction against a demand of **2.436x (A→B) / 2.834x (A→C)** `[D, §4.3]`.
   Applying that one ratio correction closes **96.1 %** of the A→B log gap and **77.3 %**
   of the A→C log gap (92.7 % / 74.6 % under the runner-vector baseline, §4.4) `[D, §4.4]`.

**Why this is UNRESOLVED and not SUPPORTED:** the degree-4 rung of the own-axis ladder
was **never run** — the shipped ladder started at degree 6 `[R, slate entry 8]` — so
`λ_4 = −5.0744e−3` is an extrapolation of a four-rung-validated law, and the full kink
profile is not a drop-in replacement (as a whole spectrum it **overshoots by 3.1x**,
§4.5). The magnitude of mechanism I therefore rests on one unmeasured number.

**Cheapest new measurement (named):** ULTRAMATH_SLATE entry 8, `deg4_rung_dual_carrier` —
add the degree-4 rung to the already-built `deg_ladder_own_axis_capture_v2` ladder.
Cost ≈ 0 (`cost_vs_B: ~0`, diagnostic, synthetic seeded nets, strictly cheaper than the
rungs already consumed, and degree 4 gates **better** than every rung already run —
`feature_reach` is 1.001 at degree 6 and falls monotonically with degree `[O]`).
Predeclared prediction: **3.35x the degree-six rung**. See §6 for the full ladder of
checks in cost order.

---

## 1. Duty 1 — r0 (ledger idx 266) and everything behind its "0.45 % on Kerdock"

### 1.1 The ledger entry, verbatim

`headroom/fold_ledger.json` → `candidates[266]`, `id: "r0_harmonic_energy_spectrum"`,
`status: "killed"`, `bias_class: "diagnostic (R0/R1, no estimator change, no new
forwards)"` `[O]`. Result clause (4), verbatim:

> "(4) TRUNCATION DOES NOT REOPEN: degree 4 (the 42x Bragg notch) carries only 0.45% of
> the estimator error, even degrees >=6 carry 99.55%, no single degree exceeds 13.8%, and
> capturing 50% requires exact integration of degrees {6,8,10,12,14,16,18} at joint
> dimension 6.249e27."

### 1.2 The producing artifact

`experiments/r0_harmonic_energy_spectrum/R0_HARMONIC_SPECTRUM.md`, dated **2026-08-10**,
with `r0_results.json`, `r0_run.log`, `run_r0.py` `[O, all four read]`.

§5, verbatim:

> `MSE/sigma^2 = sum_{l even >= 4} a_l · lam_top(l)` (odd degrees annihilated by antipodal
> pairing, degrees 0 and 2 by the exact 2-design)
>
> | degree | 4 | 6 | 8 | 10 | 12 | 14 | 16 | 18 | 20 | 22–40 | >40 |
> |---|---|---|---|---|---|---|---|---|---|---|---|
> | share of MSE | **0.45 %** | **13.82 %** | 10.18 % | 8.08 % | 6.60 % | 5.51 % | 4.68 % | 4.03 % | 3.51 % | 19.9 % | 23.2 % |
>
> - Degree 4 — the one the Kerdock design was measured to suppress 42x — carries
>   **0.45 %** of the estimator's error. Even degrees >= 6 carry **99.55 %**.

### 1.3 WHAT OBJECT WAS MEASURED — the answer is: **nothing was measured**

The `0.45 %` is a product of two factors with completely different epistemic status, and
r0 keeps them apart deliberately (§1a vs §1b, "conflating them is the trap the question
names") `[R]`.

| factor | what it is | carrier | status | source |
|---|---|---|---|---|
| `lam_top(l)` | **DESIGN** property: mean-square quadrature error per unit degree-`l` energy | Kerdock 32,256, antipodally doubled to 64,512 | **exact**, closed form, two independent routes agreeing to every printed digit | S6 closed form; r0's exact dyadic census over all `32,256²` inner-product pairs |
| `a_l` | **RESIDUAL-FIELD** per-degree energy share | none (carrier-free function-side quantity) | **`[D]` from the infinite-width mean-field limit. Not measured on any net.** | r0 Arm B: 32 scalar iterations of `f(c) = (√(1−c²) + c(π − arccos c))/π`, Taylor via Cauchy DFT, exact-rational Gegenbauer transfer |

Exact values, verbatim from `r0_results.json` `[O]`:

```
lam_top(4) = 7.350908201315546e-07      N·lam_top(4) = 0.023711089494163427
lam_top(6) = 3.194089008420301e-05      N·lam_top(6) = 1.0302853505560523
lam_top(8) = 3.097244080614878e-05      N·lam_top(8) = 0.999047050643135
lam_top(l) = 3.100198412…e-05 for every even l >= 10   (N·lam_top = 1.000000)
odd l: exactly 0 on the doubled 64,512 design
```

and from r0 §2 Arm B (mean-field spectrum, the numbers that carry the `0.45 %`):

```
a_1 = 1.1067e-01   a_2 = 9.671e-02   a_3 = 7.267e-02   a_4 = 6.060e-02
a_5 = 4.976e-02    a_6 = 4.298e-02   a_8 = 3.264e-02   a_10 = 2.589e-02
a_12 = 2.115e-02   a_16 = 1.501e-02  a_20 = 1.126e-02  a_24 = 8.765e-03
a_32 = 5.738e-03   a_40 = 4.024e-03  tail(>40) = 0.1485
```

Reconstruction check `[D, this session]`: `a_4·N·lam_top(4) / Σ_{even l≥4} a_l·N·lam_top(l)`
recovers `0.45 %` and the implied `MSE/σ² = 9.90e−06`, `N_eff = 101,018`, against r0's
printed `9.93e-6 / 100,669` — 0.35 % apart, the difference being r0's finer degree grid.

### 1.4 r0's own disclosures about this number, verbatim

- **D1** — "Arm B re-derives a committed closed form… No network is built or evaluated,
  no design is generated, no estimator or m245 code runs, no data is measured."
- **D4** — "**The estimator-error-by-degree table uses the mean-field spectrum.** Its
  implied `N_eff = 100,669` sits **2.1x–3.7x above** S17's measured 27,251 / 39,558 /
  46,955."
- **§8 NOT RESOLVED, item 4** — "*The measured spectrum's amplitude, per net.* Every
  per-degree number above `l = 1` comes from the mean-field closed form (D1). The three
  nets constrain the shape (via `n_eff`) and pin `a_1` (via S15) but cannot fit
  `a_2..a_16` (D3)."
- **§10 Limitations** — "Everything about degrees `l >= 2` rests on the mean-field closed
  form (D1). The three nets constrain but do not measure it (D3)."
- **§1b, corpus sweep** — "**No committed artifact reports residual-field harmonic energy
  above degree 6.**"
- **§8, R2 spec** — `r2_measured_harmonic_spectrum`, ~10 min wall, single process, no GPU.
  **NOT RUN** (confirmed: no `r2_*` directory exists under `experiments/` `[O]`).

### 1.5 The 0.45 % has ONE producer, not two

`PHASE1_WRITEUP_DRAFT_20260808.md` line 526 and `PHASE1_WRITEUP_SHORT_20260817.md`
line 150 `[O]`:

> "For a bias-free He-initialised ReLU network the rotation-averaged two-point function is
> exactly the iterated arc-cosine kernel `K(c) = (E||X||^2/d)·kappa^32(c)`, so the
> estimator's variance decomposes as `sum_l ||f_l||^2 A_l` against the design defects
> above. That predicts `V126 = 2.4977e-7` against a measured geomean of `2.6697e-7` over
> sixteen fresh networks — **the variance of this estimator is predictable from first
> principles to 6.4%** — and it puts the degree-4 share of that variance at **0.4497%**."

This is dated **2026-08-08**, two days *before* r0. It is the **same** iterated arc-cosine
kernel, the **same** decomposition, and the **same** design defects. **r0 is a
re-derivation of the 08-08 object, not a second independent signal for it.** Both are
`[D]` from one kernel. The corpus's own audit already reached this conclusion
`[R, EXCESS_GAIN_MOMENTS_SYNTHESIS §1.4]`:

> "its share4 = 0.45% was never separately validated — the writeup's own two degree-4
> measurements (+0.176%, CI [0.970, 1.028]; +0.42%, no CI quoted) have ±1.5–3% noise and
> cannot distinguish 0.45% from the 1.1–1.3% this cell demands. `[D+R]`"

### 1.6 What the three nets *did* contribute, and what they did not

r0 §1b's residual-field table `[R]`. Every entry constrains; none measures `a_4`.

| source | quantity | what it pins |
|---|---|---|
| S15 `baseA.C4_control_linear.incremental_oos` = 0.2929 / 0.2861 / 0.3667 | one degree-1 mode's share | `a_1` from below — **2.7x** the mean-field 0.1107 |
| S7 `xi` = 36.98 / 35.60 / 45.95 deg, ratio **1.77 / 1.70 / 2.20** | correlation-length inflation | the real field is smoother than mean-field |
| r0 `n_eff(t)` at t=0.7071: measured **2.560 / 2.705 / 1.911** vs mean-field **4.821** | model-free effective degree index | the real field is **1.78–2.52x** lower-degree than mean-field |
| S15 `positive_control.pure_deg4_R2` = 6.1e-6 / 1.15e-5 / 7.9e-6 | **one zonal H_4 mode's** share | per-mode `l=4` from above; straddles the 1-dof fit floor `1/64512 = 1.55e-5` |
| S17 `N_eff` = 39,558 / 27,251 / 46,955 | effective independent draws | the 2.1–3.7x amplitude tension |

**All three shape instruments point the same way: the deployed field is more
low-degree-weighted than the mean field that produced the 0.45 %.** r0 §6.1 states this
and uses it to *strengthen* the equipartition verdict — "The correction strengthens the
verdict" — without ever propagating it into §5's share table `[O, the omission is the
finding]`.

---

## 2. Duty 2 — every other committed per-degree energy figure

| # | figure | OBJECT measured | CARRIER | status | source |
|---|---|---|---|---|---|
| 1 | `share4 = 0.4497 %`, `share6 = 13.55 %`, `share8+ = 86 %`; `v126k = 2.4977e-07` | degree-`l` share of **arm C's MSE**; `E_l = s_l·v126k/A_l^C` | **Kerdock-126** | `[D]` mean-field arccos kernel, committed **2026-08-08** | `PHASE1_WRITEUP_DRAFT_20260808` §"design axis"; consumed by `runner_fc129.py` lines 320–335 |
| 2 | r0 §5 full 11-degree share table (0.45 / 13.82 / 10.18 / 8.08 / 6.60 / 5.51 / 4.68 / 4.03 / 3.51 / 19.9 / 23.2 %) | same object, finer grid | **Kerdock 64,512** | `[D]`, same kernel as #1 — **not independent** | `R0_HARMONIC_SPECTRUM.md` §5, ledger idx 266 |
| 3 | r0 §2 Arm B spectrum `a_1 … a_40` + tail | residual-field per-degree energy share | **carrier-free** | `[D]` infinite-width mean field | `r0_results.json` |
| 4 | **`λ_n` kink tail: `0.0027737, −0.0018494, −0.0010644, −0.00072504, −0.00042447, −0.00017003` at n = 6, 8, 12, 16, 24, 48** | **exact own-axis Gegenbauer coefficient of a single ReLU kink**; energy profile is `λ_n²` | **carrier-free** (`Lineage: carrier-free [O, predeclaration]`) | **`[D]` exact rational arithmetic**, verified to `1.9e-15` max rel. error at degree 48 | `cells/deg_ladder_own_axis_capture_v2/report.json` → `metrics.geometry.lambda_closed_form`; ledger idx 275 |
| 5 | **`ρ_own` measured readout profile: 0.003816 / 0.001750 / 0.000483 / 0.000229 / 0.000108 / 0.000019** at n = 6, 8, 12, 16, 24, 48 | own-axis captured energy at the depth-32 readout, as a fraction of the degree-≥3 **residual** energy | **carrier-free**, synthetic width-256 challenge-family nets, seeds 20260904–06 | **`[O]` sealed-gate measurement** (gate `e605f2b` sealed before the value; SHA-256 `eab0a2f6…41aba7`) | same cell; `PHASE2_CONTRIBUTION_DRAFT` §5 "Artifact 4 — the kink-tail transport identity" |
| 6 | **`λ_4 = −5.0744e−3` exact, "cross-checked by an independent quadrature to 2e-5"**; "deployed carrier about **3.35x** its degree-six rung"; "the entry-layer kink tail is degree-four dominated (**59.4 % of all even energy at four and above**)" | degree-4 kink coefficient and its energy share | **carrier-free** (the 3.35x is the rung *as it reaches the readout*) | `[R]`, **the rung itself was never measured** | `ULTRAMATH_SLATE_20260819.md` entry 8 `deg4_rung_dual_carrier` |
| 7 | M191 G0-a `deg{1..6}.ratio`: deg4 **0.10668 / 0.10719 / 0.09829**, deg6 **0.34750 / 0.41094 / 0.43288** | **NOT a per-degree defect.** RMS quadrature error on **mixed zonal polynomials** `t^d − E[t^d]`, normalised to unit sample variance, against a `1/√64512` comparator | Kerdock 64,512, 3 rotations | `[O]` measured, **object-mismatched** — see §2.1 | `experiments/pb1_premise_battery/m191_g0a_results.json`, `run_m191_g0a.py` |
| 8 | M191 G0-b `r2_summary.deg6` = 0.00105 / 0.00133 / 0.00132 | 12-axis `p6` control-variate basis `R²` against a truth-based CV residual | Kerdock | `[O]`; r0 §1b excludes it: "a *different target* … and contaminated by lower degrees" | `m191_g0b_results.json` |
| 9 | "measured implied `E6/E4 = 0.6975`" against threshold `19.71` | weighted-objective energy ratio for the carrier-optimality condition | frame-union class | `[R]` channel `2026-08-19T08:41:38Z`; **the slate does not carry either figure and files the threshold as vacuous** | `PHASE2_CONTRIBUTION_DRAFT` lines 1499–1528 |
| 10 | `A_l` exact defect table, `A_4^A/A_4^C = 128/3`, `A_4^B = 0`, `A_6^A/A_6^C = 4096/4221`, `A_8^A/A_8^C = 9857662976/9848209601` | **design** defects, five independent code paths | A/B/C | **exact** `[O]`, reproduced this session in `Fraction` arithmetic | `EXCESS_GAIN_MOMENTS_THEORY` §1.3; `ULTRAMATH_SLATE` §0 |
| 11 | S6 `haar_H4_design_over_iid_rms = 0.15398405597386836`, `haar_H6 = 1.0150297289025836` | design/iid **RMS** for a Haar-random degree-`l` harmonic | Kerdock 32,256 | **exact** `[O]` | `r0_results.json` cross-checks; S6 |

**Codex clone** (`C:/Users/strid/Documents/Codex/2026-08-02/https-chatgpt-com-share-6a5556ed-2e1c`):
its `publish/recursive-estimator-folding/corpus/whestbench/` tree is a mirror of this
corpus. Grepped for `0.4497` / `share4` / `per-degree energy`: eleven files, all mirrors
of files already listed above. `AGENT_CHANNEL.md` and `CENTRAL_MOMENT_LADDER_20260819.md`
carry **no** per-degree energy figure `[O, 0 matches]`. **No new source in the clone.**

### 2.1 Item 7 disqualified — M191's "11 % and 40 %" do not measure `A_4` and `A_6`

`PHASE1_WRITEUP_DRAFT/SHORT`, `SECTION_DESIGN_AXIS_CLOSURE`, `HANDOFF_CODEX_SOL` and
`GEN4_CLOSING` all repeat: "the measured angular error sits at degree 4 (11 % of the iid
level) and degree 6 (40 %)" `[R, five places]`. Read against `run_m191_g0a.py` `[O]`, the
degree-6 probe is

```python
p = t ** 6 - 15.0 / (N * (N + 2) * (N + 4))          # t = <u, a>, a a random unit vector
s = p.std();  p = p / s                              # unit SAMPLE variance
errs.append(abs(p.mean()));  iid.append(1.0 / sqrt(M))   # M = 64,512
```

Three object mismatches, each independently disqualifying:

1. **`t⁶` is not a degree-6 harmonic.** It decomposes into `H_6 ⊕ H_4 ⊕ H_2 ⊕ H_0`.
   Subtracting `15/(n(n+2)(n+4))` removes `H_0` only. The `H_4` component survives and is
   suppressed 42x; `H_2` survives and is annihilated exactly. The reported ratio is
   therefore a **mixture** statistic weighted by the polynomial's own energy split, not
   `A_6`.
2. **The comparator is `1/√64512`, not `1/√32256`.** Antipodal doubling leaves `A_l`
   unchanged for even `l` while halving the iid variance, so the comparator is 2x stricter
   in variance than r0's `N·lam_top` convention.
3. **The exact Haar-average answer is committed and disagrees.** A genuinely Haar-random
   `H_6` function gives `haar_H6_design_over_iid_rms = 1.0150297289025836` `[O]` — i.e.
   **101.5 %**, not 40 %. The measured 40 % is **6.4x below** the exact value in variance.

**Consequence:** the "11 % / 40 %" pair is not an independent measurement of the design's
per-degree defects, and it is not evidence about `share4` in either direction. r0 was
right to build §5 from the exact census rather than from M191. This trace records the
mis-citation because five committed documents propagate it as a measurement.

---

## 3. Duty 3 — THE DISCRIMINATION

### 3.1 The forecast's slot is the Kerdock share, and it is correctly indexed

`runner_fc129.py` lines 320–335 `[O]`:

```python
v126k = 2.4977e-07
share4, share8 = 0.004497, 0.86
share6 = 1.0 - share4 - share8
energy = {4: share4 * v126k / float(a_c[4]), 6: share6 * v126k / float(a_c[6]),
          8: share8 * v126k / float(a_c[8])}
return sum(energy[l] * float(defects[l]) for l in (4, 6, 8))
```

`energy[l] = s_l·v126k/A_l^C` inverts arm C's own MSE decomposition, so `s_l` **is
defined as** the degree-`l` share of **arm C's** MSE. That is r0 §5's object exactly.
Reproduced this session in `Fraction` arithmetic from r0's shares bucketed to `{4, 6, 8+}`
`[O, exact defect table of THEORY §1.3]`:

| leg | this session | committed |
|---|---|---|
| A→C | `0.8444606810318668` | `0.8444606810318669` |
| A→B | `0.8211759295306634` | `0.8211759295306633` |
| C→B | `0.9724264823404789` | `0.9724264823404788` |
| implied `share4` (A→C) | `0.012640630202671059` (`2.8109x`) | `0.012641` (`2.81x`) |
| implied `share4` (A→B) | `0.010883373653359512` (`2.4201x`) | `0.010883` (`2.42x`) |
| `ln(meas/fc)` A→C, A→B | `−0.251974`, `−0.209154` | `−0.251974`, `−0.209154` |

Agreement to 1 ulp on every figure. **There is no carrier-indexing error in the
forecast.** `[D, two-signal: exact reproduction of six committed constants.]`

### 3.2 The exact Kerdock→Haar transfer of r0's 0.45 %

On the Haar arm every even defect is flat (`N·A_l^A` = 1.011673 at `l=4`, 0.999769 at
`l=6`, 1.000000 for `l ≥ 8`), so the Haar-side error share **is** the energy share. The
transfer is `s_l^H ∝ s_l^K · (A_l^A/A_l^C)` with the exact ratios `128/3`, `4096/4221`,
`9857662976/9848209601`, and `1.000000` for `l ≥ 12` `[R, THEORY §1.3]`:

```
s_4^H = 0.0045·(128/3) / [ 0.0045·(128/3) + 0.1382·(4096/4221) + 0.1018·(…) + 0.7551·1 ]
```

| input | Haar-side deg-4 share | suppression `s_4^K/s_4^H` |
|---|---|---|
| r0 §5, all 11 degrees | **0.162285** | 1 / **36.1** |
| runner 3-bucket `{0.004497, 0.135503, 0.86}` | **0.162028** | 1 / 36.0 |

**Independent confirmation** `[R, ULTRAMATH_SLATE entry 1 `deg4_exclusivity_rule`]`:

> "three ways of spending one degree-four error channel (**~16% of estimator error on the
> Haar host**) … composed selection gain scales with the residual degree-four variance
> share: 1 deployed, **~1/36 after the swap**, exactly 0 after completion."

Two signals — this session's transfer arithmetic and a committed slate entry written
independently — agree on **16 %** and on **1/36**. `[D + R]`

### 3.3 Does 16.2 % reconcile with the implied 1.26 %? — **No. It refutes that reading.**

`1.26 %` is a **Kerdock-side** demand. Its Haar-side counterpart, obtained by the same
exact transfer:

| share vector | Kerdock-side `s_4` | Haar-side `s_4` |
|---|---|---|
| committed (mean-field arccos) | 0.004497 | **0.1620** |
| A→B demand | 0.010883 | **0.3202** |
| A→C demand | 0.012641 | **0.3540** |

The forecast demands the Haar-side degree-4 share be **32–35 %**, against the committed
**16 %**. That is a demand for **1.98–2.19x** more degree-4 energy share on the Haar arm —
a real physical demand about the residual's spectrum, not a bookkeeping slip. And in the
other direction, feeding the Haar-side 16.2 % into the Kerdock slot would inflate the
degree-4 slot **36.1x** (`0.162285/0.004497`) — and is not even well-formed in the
runner's parameterization, which would need `share6 = 1 − 0.162285 − 0.86 = −0.022 < 0` —
against the 2.8x the measurement demands. **No re-indexing of any committed number
produces the observed excess.** `[D, exact]`

---

## 4. THE DISCRIMINATING ARTIFACT READ — the kink tail (ledger idx 275)

### 4.1 What it is

`cells/deg_ladder_own_axis_capture_v2`, ledger idx 275, `bias_class: "exact"`, sealed
gate `e605f2b` predeclared before the value, production seeds 20260904–06, 398.0 s of a
600 s cap, `report.json` SHA-256 `eab0a2f6…41aba7` `[O]`. Ledger mechanism, verbatim:

> "the exact own-axis coefficient at degree n is lambda_n = sqrt(N(d,n)) times half the
> alternating sum of the normalized Gegenbauer coefficients against the exact absolute
> moments, **computed here in exact rational arithmetic**, giving 0.0027737, −0.0018494,
> −0.0010644, −0.00072504, −0.00042447, −0.00017003 at degrees 6, 8, 12, 16, 24, 48."

Its degree-`n` **energy** profile is `λ_n²`. `PHASE2_CONTRIBUTION_DRAFT` §5 states the
transport identity `[O]`: "The degree profile of the depth-32 readout's own-axis harmonic
content **is** the entry-layer kink tail, transported forward with its shape intact",
validated "to within 14 % of the exact ratio at every gated rung."

### 4.2 The measured readout profile falsifies the mean-field spectrum's shape

`metrics.per_degree_readout.*.rho_own_mean` against the two candidate laws, all
normalised at degree 6 `[D, this session; inputs all `[O]`]`:

| degree | MEASURED `ρ_own(n)/ρ_own(6)` | kink `λ_n²/λ_6²` | mean-field `a_n/a_6` | kink error | **mean-field error** |
|---:|---:|---:|---:|---:|---:|
| 6 | 1.000000 | 1.000000 | 1.000000 | — | — |
| 8 | 0.458595 | 0.444566 | 0.759423 | −3.1 % | **+65.6 %** |
| 12 | 0.126572 | 0.147255 | 0.492089 | +16.3 % | **+288.8 %** |
| 16 | 0.060010 | 0.068332 | 0.349232 | +13.9 % | **+482.0 %** |
| 24 | 0.028302 | 0.023420 | 0.203932 | −17.3 % | **+620.6 %** |

The mean-field arc-cosine spectrum decays as `l^{-1.1}` over `l = 4–24` `[R, r0 §4]`; the
kink tail and the measurement both decay as `≈ n^{-2.7}`. **At every degree where both are
defined, the measurement sits on the kink law and off the mean-field law by 1.66x to
7.2x.** The sole basis of the committed 0.45 % is contradicted in shape by a sealed-gate
measurement on real (synthetic He) networks. `[O + D]`

*Limitation named:* `ρ_own` is own-axis captured energy, not total degree-`n` energy. The
cell's own instrument checks (`L1_own_axis_ratio_by_degree` = 1.024 / 0.950 / 1.019 /
0.988 and `L2_exact_span_ratio_by_degree` = 1.009 / 1.011 / 0.988 / 1.002 at degrees
6 / 8 / 12 / 16 `[O]`) show faithful in-span recovery across exactly that range, which is
what licenses reading the *shape* off it. It does not license reading absolute `E_n` off
it.

### 4.3 The degree-4 coefficient, and an independent check of it

`λ_4 = −5.0744e−3` is `[R, slate entry 8 evidence_now: "lambda_4 = −5.0744e-3 exact,
cross-checked by an independent quadrature to 2e-5"]`. **It is not in the cell** — the
shipped ladder's `metrics.config.degrees` is `[6, 8, 12, 16, 24, 48]` `[O]`. The rung was
never run.

Second signal, derived this session from the ReLU Hermite closed form
`c_n = (−1)^{n/2−1}(n−3)!!/√(2π·n!)`, normalised at `n = 6` `[D]`:

| n | Hermite closed form × k | committed `λ_n` | rel. |
|---:|---:|---:|---:|
| 4 | **−0.00506399** | **−5.0744e−3** (slate) | **−0.205 %** |
| 6 | +0.00277366 | +0.00277366 | 0.000 % |
| 8 | −0.00185323 | −0.00184936 | +0.209 % |
| 12 | −0.00107118 | −0.00106436 | +0.641 % |
| 16 | −0.00073292 | −0.000725044 | +1.086 % |
| 24 | −0.00043304 | −0.000424467 | +2.019 % |
| 48 | −0.00017866 | −0.000170033 | +5.074 % |

The drift with `n` is the finite-`d` correction (`d = 256`), which is what the cell's exact
rational route carries and the `d → ∞` Hermite form does not. At `n = 4` the two agree to
**0.21 %**. `λ_4` is confirmed.

Derived consequences `[D]`, both reproducing committed slate figures:

```
λ_4² / λ_6²                          = 3.3471     (slate entry 8: "about 3.35x")
λ_4² / Σ_{even n>=4} λ_n²            = 0.5910     (slate entry 8: "59.4%")
```

*(The `Σ` runs over **all** even degrees — the six committed rungs completed by the same
closed form at the degrees the ladder never stored. The six stored rungs alone give
`0.665`; a pure-Hermite completion gives `0.590`; the figure is fill-methodology-stable
to `±0.001`.)*

### 4.4 The correction, and how much of the gap it closes

The two committed first-principles laws for the same physical quantity — the He net's
per-degree residual energy — disagree at the one ratio the forecast is sensitive to:

```
mean-field arccos kernel   E_4/E_6 = a_4/a_6       = 1.4100
exact ReLU kink tail       E_4/E_6 = λ_4²/λ_6²     = 3.3471
                                          ratio    = 2.3739
demanded boost of E_4/E_{>=6}:   2.436x (A->B)  /  2.834x (A->C)
```

Applying that single ratio correction at degree 4 and leaving degrees ≥ 6 in their
mean-field proportion gives `s_4 = 0.010610` (**1.061 %**, `2.359x` committed), which is
**97.5 %** of the A→B demand and **83.9 %** of the A→C demand `[D]`.

*Baseline sensitivity, named `[D]`:* the committed runner vector's **own** implied
`E_4/E_6` is `1.4420` (`(share4/A_4^C)/(share6/A_6^C)`), 2.3 % above the r0 spectrum's
`1.4100`, because the runner's `{4, 6, 8+}` bucketing and the r0 per-degree grid are not
the same object. Correcting to the kink ratio against that baseline gives `k = 2.321`,
`s_4 = 1.038 %` (`2.31x`), closing **92.7 % / 74.6 %** of the A→B / A→C log gaps. Every
conclusion in this document is unchanged under either baseline.

| share vector | `s_4` | A→C fc | A→B fc | C→B fc |
|---|---:|---:|---:|---:|
| **MEASURED** | — | **0.6564** | **0.6662** | **1.0150** |
| committed (mean-field) | 0.004497 | 0.8445 | 0.8212 | 0.9724 |
| **kink-corrected** | **0.010610** | **0.6950** | **0.6717** | 0.9665 |
| A→B-implied | 0.010883 | 0.6895 | 0.6662 | 0.9662 |
| A→C-implied | 0.012641 | 0.6564 | 0.6330 | 0.9645 |

```
log gap closed by the kink correction:   A->B  96.1 %      A->C  77.3 %
```

`[D, all rows this session; the MEASURED row is `[O]` from
`cells/frame_completion_129_three_arm_regime_decomposition_v1/report.json`.]`

### 4.5 The attack on this conclusion, and what it costs

**Counter-hypothesis: the kink profile is simply the right spectrum, so use it whole.**
Tested and **rejected** `[D]`. Substituted as a complete spectrum it gives `s_4 = 3.272 %`
and forecasts A→C `0.4237` / A→B `0.4003` against measured `0.6564` / `0.6662` — an
**overshoot of 3.1x** on the share and a worse fit than the committed vector. Cause: the
kink tail decays at `p ≈ 2.7` while 86 % of the Kerdock arm's error sits at degrees ≥ 8,
where the mean-field `p ≈ 1.1` tail is what supplies the mass. The kink tail describes the
**own-axis, entry-layer-transported sub-component** (`Σ_n ρ_own(n) ≈ 0.6 %` of residual
energy), not the whole residual. **What survives the attack is the deg-4:deg-6 ratio, not
the profile.** The correction applied in §4.4 is therefore a hybrid — a validated ratio
grafted onto an unvalidated tail — and it is labelled as such.

**Counter-hypothesis: within-degree anisotropy biases the forecast's mean.** Dead by a
committed theorem `[R, THEORY §1.5, Schur on inequivalent `SO(256)` irreps]`:
`E_R[Err_c²] = Σ_{l≥2 even} E_{c,l}·A_l` **exactly, with no cross-degree term**, and
`E[A_l] = defect_random` is "the correct object for the mean, not an approximation."
Anisotropy inflates `se_log`, not the point forecast. So `E_{c,l}` is the only free
parameter, which is precisely what this trace targets.

**Counter-hypothesis: something other than `share4` is required anyway.** Partly true, and
recorded `[R, THEORY §2.3]`: `max_l(A_l^B/A_l^C) = 2816/2881 = 0.9774383894481083` bounds
`forecast(C→B)` above for **every** nonnegative share vector, while measured `C→B` is
`1.0149700854688666` — the model is short by `≥ 3.84 %` structurally. **No value of
`share4` touches that leg.** Mechanism I can carry the A→B leg and most of A→C; it cannot
carry C→B, and this document does not claim it does.

**Net-family mismatch, named `[GAP]`.** The kink-tail cell ran on synthetic width-256
challenge-family nets (seeds 20260904–06); r0's constraints came from synthetic He nets
101 / 202 / 303; the 129 cell's arms ran the deployed estimator. The transport identity
was validated within the first family only.

---

## 5. What each candidate reading survives

| reading | status | killed / carried by |
|---|---|---|
| The forecast mis-indexed the carrier; 0.45 % belonged on Haar | **REFUTED** | §3.1 exact reproduction of six committed constants; §3.3 the transfer runs 36x the wrong way |
| The Haar-side share is 16 %, which reconciles with 1.26 % | **REFUTED** | §3.2–3.3: 16.2 % vs 1.26 % is 12.8x; the Haar counterpart of the demand is 32–35 % |
| 0.45 % is pinned on the right object by committed evidence | **REFUTED** | §1.3–1.5 it is `[D]` from one infinite-width kernel with a single producer; §4.2 its shape is measurement-falsified at 8/12/16 |
| The deg-4 energy share is undercounted, direction and rough magnitude | **CARRIED, not closed** | §4.3–4.4: an exact, measured-validated second law gives 2.374x against a demand of 2.436x/2.834x, closing 96.1 %/77.3 % of the log gaps |
| The undercount is exactly 2.81x and the excess gain is closed | **NOT ESTABLISHED** | the degree-4 rung was never measured; the A→C leg still misses 5.9 %; THEORY §2.3's ≥3.84 % structural short is untouched |

---

## 6. The cheapest new measurements, in cost order

1. **Zero cost, artifact read.** Slate entry 8's own first falsifier: "a receipts read on
   whether the deployed control variate already spans degree four (the named
   counter-hypothesis — redundancy, not smallness)." Also THEORY §11b / slate entry 2's
   "post-control per-degree energy table", flagged there as "a zero-cost artifact read".
2. **≈ Zero cost, already-budgeted diagnostic — THE DISCRIMINATOR.** `ULTRAMATH_SLATE`
   entry 8 `deg4_rung_dual_carrier`: add the degree-4 rung to the existing
   `deg_ladder_own_axis_capture_v2` ladder. `cost_vs_B: ~0`; strictly cheaper than the
   rungs already consumed; and the instrument is at its **most** reliable there —
   `feature_reach_by_degree` runs 1.001 (deg 6), 0.994 (8), 0.727 (12), 0.619 (16), 0.489
   (24), 0.371 (48) `[O]`, so degree 4 gates ahead of every rung already run. Predeclared
   prediction **3.35x the degree-six rung**, exact null on a completed (MUB-129) carrier
   since `A_4^B = 0` identically. This converts `λ_4` from a four-rung extrapolation into
   an observation and measures `E_4/E_6` on real nets, which is the single number the
   whole 2.81x turns on.
3. **~10 min wall, single process, no GPU — only if 2 is ambiguous.** r0 §8's specified
   and never-run `r2_measured_harmonic_spectrum`: unbiased Gegenbauer projection of `a_l`
   for `l = 1..16` on nets 101/202/303 at `M = 40,000` Haar directions, with the
   predeclared gates G1–G4 and the mandatory second signal already written. Arm 2
   (per-output-component field) additionally closes r0's open 2.1–3.7x `N_eff` tension.
   The spec is complete and sealed; it needs only a run.

---

## 7. Two-signal ledger for this document

| claim | signal 1 | signal 2 | agreement |
|---|---|---|---|
| the forecast slot is arm C's share | `runner_fc129.py` lines 320–335 read `[O]` | all three forecast legs reproduced from r0's table in `Fraction` arithmetic | 1 ulp on 3 constants |
| implied `share4` 0.012641 / 0.010883 | bisection this session | THEORY §2.2 committed table | 6 s.f. |
| `ln(meas/fc)` = −0.251974 / −0.209154 | computed this session | THEORY §2.4 committed | all digits |
| Haar-side deg-4 share ≈ 16 % | exact transfer of r0's 11-degree table (0.162285) | SLATE entry 1 "~16% … ~1/36" (this trace: 1/36.1) | independent artifacts |
| `λ_4 = −5.0744e−3` | SLATE entry 8, exact rational + independent quadrature to 2e-5 `[R]` | ReLU Hermite closed form, normalised at n=6, this session | 0.205 % |
| `λ_4²/λ_6² = 3.347`, `λ_4²/Σ = 0.591` | computed this session from `metrics.geometry.lambda_closed_form` plus its all-even closed-form completion (stored rungs alone: 0.665) | SLATE entry 8 "about 3.35x", "59.4%" | 0.0 % / 0.5 % |
| mean-field shape is wrong at the readout | `ρ_own` sealed-gate measurement `[O]` | exact kink law `λ_n²` `[O]` — measurement matches kink to ≤17 %, misses mean-field by 66–621 % | two independent laws, one measurement |
| M191's 11 %/40 % is object-mismatched | `run_m191_g0a.py` source read `[O]` | S6 exact `haar_H6_design_over_iid_rms = 1.01503` vs measured 0.40 | 6.4x in variance |
| r0 §5 reconstructs | `a_4·N·lam_top(4)/Σ` → 0.45 %, `N_eff` 101,018 | r0 printed `9.93e-6 / 100,669` | 0.35 % |

## 8. Limitations

- No new measurement was taken. Every number here is an artifact read or exact/scalar
  arithmetic on committed numbers.
- The degree-4 rung of the own-axis ladder does not exist. `λ_4` is exact as a
  coefficient; its *realised capture at the readout* is extrapolated from four rungs.
- The §4.4 correction is a hybrid: kink-derived ratio at degree 4, mean-field tail at
  degrees ≥ 6. Neither committed profile fits alone (§4.5).
- Three different net families are involved (§4.5 `[GAP]`).
- THEORY §2.3's structural short of ≥ 3.84 % on the C→B leg is untouched by any value of
  `share4`, and THEORY §2.2's near-singularity (`det = −1.6e−05`, `cond = 8.7e+18`) means
  the three arms cannot identify `s_6` and `s_8` separately at any precision.
- r0's own 2.1–3.7x `N_eff` amplitude tension (its §6.2) is orthogonal to everything here
  and remains open; this document uses shape only.


---
---

# ADDENDUM — 2026-08-19 (second dated pass): the deg-4 rung read, and the lambda-sweep triage

Rung: **R0/R1 only.** Committed-artifact reads plus exact/scalar arithmetic and one
small float64 identity check (8 frames, d=256, no network, no estimator, no forward
pass, no truth). Zero billed FLOPs against `B = 2.72e11`; zero estimator wall seconds.
Runner: frozen venv `C:/Users/strid/.venvs/whestbench-frozen-m178/Scripts/python.exe`
under `-B`, `PYTHONDONTWRITEBYTECODE=1`, single-thread env vars. Scripts in the session
scratchpad; nothing written outside this file. `fold_floor_splice`, `frame_completion_129`,
`row_blocked_production` and `bprime_rephase` were opened **read-only** and not modified.
Public100 custody untouched: no row was read, burned or graded.

Evidence tags as in the parent document: `[O]` observed this session, `[D]` derived this
session, `[R]` reported by a committed artifact, `[A]` assumed, `[GAP]` named hole.

---

## A0. VERDICT, BOTH DUTIES

**Duty 1 — the deg-4 rung dual-carrier read: CLOSED NEGATIVE. No lawful degree-four
control survives on any of the three carriers, and the reason on the deployed host is
redundancy, not smallness — which is exactly the counter-hypothesis slate entry 8 named
as its own zero-cost first falsifier. That falsifier is executed here and it lands.**

1. The `59.4 %` is the **kink function's own tail energy**: `lambda_4^2` as a share of
   `sum_{even n >= 4} lambda_n^2`, where `lambda_n` is the exact own-axis Gegenbauer
   coefficient of a single ReLU kink at `d = 256`. It is **not** the estimator error and
   **not** the readout capture. Recomputed independently this session: **0.59022**
   converged (hybrid fill), **0.58854** (pure Hermite). The slate's `59.4 %` is that same
   quantity truncated near `n = 60`; the parent trace's `0.5910` is the same quantity
   truncated near `n = 200`. All three are the same object and none of the differences
   moves a conclusion `[D, §A1]`.
2. **Ceilings under the corrected share, and one inconsistency named.** Annihilating the
   whole degree-four channel removes at most `1.061 %` of MSE on Kerdock-126, **`31.487 %`**
   on Haar-126, and **exactly 0** on the MUB-129 completion. The pairing "Kerdock ~1.06 %,
   Haar ~16 %" mixes the kink-corrected Kerdock share with the *uncorrected* Haar transfer.
   The two internally consistent pairs are **(0.4497 %, 16.228 %)** and
   **(1.061 %, 31.487 %)** `[D, exact transfer, §A2]`.
3. **A lawful control cannot reach those ceilings.** Under the k32 death law the only
   admissible degree-four control is the theorem-fixed own-axis zonal one, whose ceiling
   is the ladder's own currency: `rho_own(4) = 3.3471 × rho_own(6) = 0.012772` of the
   degree-3-and-above readout residual. Adding that rung to the sealed ladder gives a band
   capture of **0.019050 against the 0.02 materiality bar — metric 1.0498, still a KILL**
   by the cell's own predeclared threshold. The rung would have to land at **1.5963× its
   own exact theorem-fixed prediction** to reopen the door `[D, §A3]`.
4. **And it is already spent.** Source read of the deployed `row_blocked` path, with an
   exact identity verified numerically this session: the deployed moment-tangent control's
   entire input is the carrier's quadrature error on `|t|` about the 256 entry axes, whose
   own-axis coefficients **are** the same `lambda_n`, with degree 2 annihilated exactly by
   the orthonormal-frame carrier. **Degree four is therefore the leading live term of the
   deployed control's input, carrying 59.0 % of its even-`n >= 4` signal energy, weighted
   by exactly `lambda_4`** `[O + D, §A4]`.
5. **Cheapest falsifier of what remains.** The only unmeasured quantity that separates
   "already removed" from "still there" is `rho^2`, the tangent control's realised variance
   share — the CENTRAL_MOMENT_LADDER's own `[GAP]`. It is measured by the same panel that
   settles duty 2, at no extra cost `[D, §A6]`.

**Duty 2 — the lambda-sweep settling check: RUNS ARE NEEDED. Priced exactly and filed as
a spec sketch (§A6.3).** No committed artifact stores the tangent arm at all — all 30
`.npz` files in the corpus were enumerated and none contains `delta_mean` or a paired
sampled arm `[O]`. Three things make the run far cheaper than the settling-check text
implies, and one of them changes the design:

- The covariance is taken across the randomization at **fixed** network, so the truth
  cancels: **the sweep is truth-free** and can run on synthetic seeded nets without
  touching Public100 custody `[D]`.
- Conditional on the regime split, **both arms are exactly linear in the empirical
  measure**, so `M̂` and `Δ` each decompose exactly as means over the 126 i.i.d.
  Haar frames. Frame-level pairs give `λ*` at the deployed `N` **exactly**, from a
  single call per network `[D, source read + exact decomposition, §A6.2]`.
- **What the sweep decides collapses to one threshold.** The cost of `λ = 1`
  *relative to the deployed constant* is `(1 − λ_d)(1 + λ_d − 2λ*)`, which
  is **linear** in `λ*` and changes sign at
  `λ* = (1 + λ_d)/2 = 0.9903556099448082`. Above that value the substitution
  **improves** the variance instead of costing `3.868e-4` of it `[D, exact, §A6.1]`.

Price of the settling run: **6 deployed calls (3 synthetic nets × 2 seeds) =
`1.042764e12` billed FLOPs = `3.8337 × B`, residual channel `0.9635 s`.** Not zero, and
not chargeable as a `~0` diagnostic.

---

## A1. Duty 1a — what object the `59.4 %` is

The slate's clause `[R, ULTRAMATH_SLATE entry 8]` reads: "the entry-layer kink tail is
degree-four dominated (**59.4 % of all even energy at four and above**)".

**The object is the ReLU kink's own-axis tail energy, carrier-free, function-side.**
Precisely: `lambda_4^2 / sum_{even n >= 4} lambda_n^2`, where `lambda_n` is the exact
own-axis Gegenbauer coefficient of one rectifier kink at `d = 256`
`[R, cells/deg_ladder_own_axis_capture_v2 → metrics.geometry.lambda_closed_form;
predeclaration causal_mechanism]`. It is none of the three candidates the question offers
as alternatives:

| candidate | is it the 59.4 %? | why |
|---|---|---|
| the kink function's own tail energy | **YES** | `lambda_n` is a property of `relu(t) = (t + \|t\|)/2` alone — carrier-free, network-free, exact rational arithmetic, `Lineage: carrier-free` in the cell's own predeclaration `[O]` |
| the estimator error | no | the estimator error per degree is `a_l · A_l`; no `A_l` and no residual-field `a_l` enters `lambda_n` at any point |
| the readout capture | no | that is `rho_own(n)`, a *measured* quantity (`0.003816 / 0.001750 / …`), reported separately in the same cell; `lambda_n^2` is the reference curve `rho_own` is read **against** |

**Recomputation, this session** `[D]`, from the ReLU Hermite closed form
`c_n = (−1)^(n/2−1) (n−3)!! / sqrt(2π n!)` normalised at `n = 6` against the committed
`lambda_6 = 0.00277366`, evaluated through `lgamma` to avoid the `n!` overflow:

```
Hermite-predicted lambda_4 = -0.0050639871628326    slate lambda_4 = -5.0744e-3
                                                    relative difference -0.2052 %
lambda_4^2 / lambda_6^2    =  3.3470557784401787    slate "about 3.35x"
```

**Fill and truncation sensitivity of the share, stated because the parent trace's
`±0.001` claim is slightly tighter than the arithmetic supports** `[D]`:

| `NMAX` (largest even degree summed) | hybrid fill (committed where stored) | pure Hermite |
|---:|---:|---:|
| 48 (the last stored rung) | 0.59689 | 0.59520 |
| 60 | 0.59499 | 0.59330 |
| 100 | 0.59244 | 0.59075 |
| 200 | 0.59100 | 0.58932 |
| 4000 | 0.59023 | 0.58855 |
| 20000 (converged) | **0.59022** | **0.58854** |
| six stored rungs alone | 0.66484 | — |

The slate's `59.4 %` is the converged value truncated near `n = 60`; the parent trace's
`0.5910` is it truncated near `n = 200`. `c_n^2` decays as `n^{-2.513}` `[D, measured from
the closed form at n = 100 vs 200]`, so the tail converges and the converged answer is
**59.02 %**. Nothing below turns on the 0.4-point difference.

---

## A2. Duty 1b — what a theorem-fixed deg-4 control could remove AT MOST, per carrier

### A2.1 The channel ceiling: annihilate the entire degree-four error

The exact defect ratios are `A_4^A/A_4^C = 128/3`, `A_6^A/A_6^C = 4096/4221`,
`A_8^A/A_8^C = 9857662976/9848209601`, and `1` for `l >= 10`
`[R, EXCESS_GAIN_MOMENTS_THEORY §1.3; reproduced in `Fraction` arithmetic this session
against `metrics.structure` of the sealed 129 cell, where
`a4_suppression_factor_arm_a_over_arm_c = 42.666666666666664` `[O]`]`.

| share vector | Kerdock-126 (arm C) | Haar-126 (arm A) | MUB-129 (arm B) |
|---|---:|---:|---:|
| committed mean-field (r0 §5, 11 degrees) | `0.004497` | **`0.162285`** | `0` |
| committed, runner 3-bucket | `0.004497` | `0.162028` | `0` |
| **kink-corrected (trace §4.4)** | **`0.010610`** | **`0.314870`** | `0` |
| A→B demand | `0.010883` | `0.320436` | `0` |
| A→C demand | `0.012641` | `0.354287` | `0` |

Kerdock-to-Haar suppression of the degree-four share is `1/36.0633` on the committed
vector `[D]`, reproducing SLATE entry 1's `~1/36` from an independent route.

**The inconsistency, named.** "Kerdock ~1.06 %, Haar ~16 %" pairs the **corrected**
Kerdock share with the **uncorrected** Haar transfer. Transferring `1.061 %` through the
same exact ratios gives **`31.487 %`**, a factor `1.9402` above `16.2 %` `[D]`. The two
internally consistent pairs are `(0.4497 %, 16.228 %)` and `(1.061 %, 31.487 %)`. Every
statement below uses one pair or the other, never a mixture.

Arm B's zero is an identity, not a measurement: `A_4,mub(129) = 0` identically
`[R, SLATE §0; `a4_arm_b_mub_completion = 0.0` in the sealed cell `[O]`]`, so a
degree-four control on a completed carrier has **exactly nothing to remove**. That is the
exact-null arm slate entry 8 predeclares, and it is settled by algebra before any run.

### A2.2 The lawful ceiling, which is the binding one

The k32 death law admits theorem-fixed coefficients and rejects fitted ones
`[R, k32_base_sensitivity; CENTRAL_MOMENT_LADDER "Death-law binding"]`. `lambda_4` is
theorem-fixed and exact, so a degree-four **own-axis zonal** control is the one admissible
shape. The sealed ladder states its ceiling explicitly
`[R, deg_ladder_own_axis_capture_v2 predeclaration, inconclusive_band_note]`:

> "Because the k32 death law forbids fitted coefficients, captured energy remains an
> UPPER bound on what a lawful control could remove."

So the lawful ceiling is `rho_own(4)`, in the ladder's currency (fraction of the
degree-3-and-above residual energy of the depth-32 readout), and the predeclared
prediction for it is

```
rho_own(4) = rho_own(6) × lambda_4^2/lambda_6^2 = 0.003816 × 3.3470558 = 0.012772
```

Against the campaign's own `2 %` materiality bar for a control, `0.012772` is **63.86 %
of the bar on its own** `[D]`.

**Conversion to an MSE share, with its unknown named.** On the Haar arm every even defect
is flat (`N·A_4^A = 1.011673`, `N·A_6^A = 0.999769`, `1.000000` for `l >= 8` `[R]`), so
energy currency and error currency coincide up to one factor: the ladder's denominator
counts degree-3-and-above **energy**, while the estimator error counts only even degrees
`>= 4`. Call that factor `k_odd = E(deg >= 3) / E(even, deg >= 4) >= 1`. The Haar-host MSE
ceiling is `0.012772 · k_odd`. `k_odd` **is not measured in any committed artifact
`[GAP]`**; its settling check is the never-run `r2_measured_harmonic_spectrum` of r0 §8,
whose Arm 1 measures `a_l` for `l = 1..16` directly. Under near-equipartition across
parities `k_odd ≈ 2 [A]`, giving `≈ 2.6 %` of Haar MSE. On the Kerdock arm the same own-axis
energy enters the error `128/3 = 42.6667×` weaker, which is why the structured carrier's
degree-four channel is economically dead independent of everything else.

---

## A3. Duty 1c — does anything lawful survive? The ladder's own arithmetic says no

The sealed cell's thresholds are `kill_when_gte = 0.75`, `pass_when_lte = 0.25` on
`metric = max(floor_sum_gated, R2_BAR) / own_sum_gated`, with `R2_BAR = 0.02`,
`floor_sum_gated = 0.00027`, `own_sum_gated = 0.006278` over gated rungs `{6, 8, 12, 16}`
`[O, metrics.cumulative and metrics.gating]`.

Adding the never-run degree-four rung at exactly its predeclared value:

| band | own sum | metric | disposition |
|---|---:|---:|---|
| gated `{6,8,12,16}` (as sealed) | `0.006278` | `3.1857` | KILL |
| gated + deg-4 at `3.3471×` | **`0.019050`** | **`1.0498`** | **KILL** |
| all six rungs + deg-4 at `3.3471×` | `0.019177` | `1.0429` | KILL |
| Haar-defect-weighted band + deg-4 | `0.019199` | `1.0417` | KILL |
| reach-corrected band + deg-4 | `0.019378` | `1.0321` | KILL |
| Kerdock-defect-weighted band + deg-4 | `0.006695` | `2.9874` | KILL |

**What the rung would have to be to reopen the door** `[D, exact]`:

```
own sum needed to escape KILL          = 0.02 / 0.75 = 0.0266667
  (the cell's own predicted signature quotes "the 0.0267 that escaping KILL requires")
rho_own(4) needed                      = 0.0266667 - 0.006278 = 0.0203887
                                       = 5.3429 x rho_own(6)
                                       = 1.5963 x its own exact kink-tail prediction
rho_own(4) needed for PASS             = 0.073722 = 19.32 x rho_own(6)
```

So the degree-four rung, landing **exactly where the theorem puts it**, leaves the band
`4.98 %` short of materiality. The rung is worth running as a *measurement* — it converts
`lambda_4` from a four-rung extrapolation into an observation, it gates better than every
rung already run (`feature_reach` is monotone decreasing in degree: `1.001489`, `0.993573`,
`0.727028`, `0.618848`, `0.489337`, `0.370694` at `6/8/12/16/24/48` `[O]`), and it carries
an exact null on a completed carrier. It is **not** worth running as a construction gate,
because its own predeclared success value fails the bar.

**The slate's "corrected ceilings" do not reproduce.** Entry 8 states "2.28x short of the
bar on the structured carrier but only 1.13x short on Haar". Eight weightings were tried
against the sealed cell's committed metrics `[D]`. The Haar leg reproduces to three
significant figures **only if the degree-four rung is taken at `3.00×` the degree-six rung**
(`0.02 / (0.006278 + 3.00 × 0.003816) = 1.1283`), which contradicts entry 8's own `3.35×`
prediction — at `3.35×` the figure is `1.0498`. The structured leg reproduces under none of
the eight (closest: `2.1401` on a v1-anchor basis, `2.9874` defect-weighted). **Filed as an
unreproducible committed figure**, in the same class as the M191 `11 % / 40 %`
mis-citation the parent document records in §2.1.

---

## A4. Duty 1d — THE ZERO-COST FALSIFIER, EXECUTED: the deployed control already spans degree four

Slate entry 8's own first falsifier `[R]`: *"a receipts read on whether the deployed
control variate already spans degree four (the named counter-hypothesis — redundancy, not
smallness)."* Here it is, from
`experiments/row_blocked_production/candidate_source/{base_estimator,fold3_estimator,orthogonal_fold3}.py`
`[O, all three read]`.

### A4.1 The control's input is the own-axis kink quadrature error, exactly

```python
first_pre = z @ mlp.weights[0]
x = concatenate((maximum(first_pre, 0.0), maximum(-first_pre, 0.0)), axis=0)
sigma0 = sqrt(sum(weights[0] * weights[0], axis=0))
exact_first_mean = sigma0 / sqrt(2.0 * pi)
first_moment_residual = mean(x, axis=0) - exact_first_mean
```

`x` has `2 × 32256` rows, so `mean(x, axis=0)[j] = (1/2)·mean_i |⟨z_i, w_j⟩|`. With
`radial_conditioning = True` the carrier is `z_i = r q_i`, `‖q_i‖ = 1`, `r` the exact
mean chi radius, so

```
first_moment_residual[j] = (r ||w_j|| / 2) * ( mean_i |t_ij| - E|t| ),   t_ij = <q_i, w_hat_j>
```

which is **exactly the carrier's quadrature error on the zonal `|t|` about the entry axis
`ŵ_j`** `[D]`. Since `relu(t) = (t + |t|)/2` and the linear part is orthogonal to every
zonal above degree one, `|t|/2` has own-axis Gegenbauer coefficients `lambda_n` at every
even `n >= 2` — **the same `lambda_n` the sealed ladder computes in exact rational
arithmetic** `[R, the cell's own causal_mechanism states this identity]`.

Degree 2 is annihilated exactly by any orthonormal-frame union (`X_2 = S_2 = 0`
`[R, SLATE §0]`), verified this session: `mean_i t_ij^2 = 0.00390625000000000` against
`1/256 = 0.00390625000000000`, all seventeen digits `[O]`. **The leading live term of the
deployed control's input is therefore degree four, weighted by exactly `lambda_4`, and it
carries `59.0 %` of the input's even-`n >= 4` signal energy** `[D]`.

### A4.2 A second, exact identity the corpus does not currently hold

```python
first_variance_residual = (mean(x * x, axis=0) - 0.5 * radial_covariance * sigma0**2)
                          - 2.0 * exact_first_mean * first_moment_residual
```

`relu(p)^2 + relu(−p)^2 = p^2` for every `p`, so the first bracket equals
`(1/2)·mean_i p_ij^2 − (r^2/2d)·‖w_j‖^2`, and on an orthonormal frame
`mean_i t_ij^2 = 1/d` **exactly**. **The bracket is identically zero on the deployed
carrier**, hence

```
first_variance_residual = -2 * exact_first_mean * first_moment_residual      exactly
```

Verified numerically this session at `d = 256`, 8 frames, float64: max `|bracket|` =
`1.7763568394002505e-15` against a term scale of `0.6134829207863401`, i.e. `2.896e-15`
relative — float64 roundoff `[O]`. Max `|fvr + 2·m·fmr|` is the same `1.78e-15` `[O]`.

**Consequence.** The deployed moment-tangent control has **one** independent input per
entry axis, not two. `CENTRAL_MOMENT_LADDER` §0 records that
`first_variance_residual` "is already the known-mean central second moment, which is
exactly unbiased at every `n`"; the stronger fact is that on this carrier it carries no
information at all beyond `first_moment_residual`. The whole tangent control is driven by
the degree-`>=4` even own-axis kink tail, degree four first.

### A4.3 What this does to slate entry 8's construction leg

The counter-hypothesis entry 8 names — **redundancy, not smallness** — is **confirmed**.
A theorem-fixed degree-four own-axis control on the deployed Haar host would be built on
the same axes, from the same zonal family, with the same theorem-fixed coefficient, as the
control the estimator already runs. It is not an additive channel. What is left for it to
attack is the part of that channel the deployed control fails to remove, and that residue
is governed by one unmeasured number, `rho^2` (§A6).

Two attacks on this reading, both run `[D]`:

- *"The tangent transports through the diagonal-Gaussian map, so it may not actually reach
  the readout's degree-four content."* The transport identity is measured-validated —
  "the degree profile of the depth-32 readout's own-axis harmonic content **is** the
  entry-layer kink tail, transported forward with its shape intact … to within 14 % of
  the exact ratio at every gated rung" `[R, PHASE2_CONTRIBUTION_DRAFT §5]` — and the
  parent document's §4.2 measures the same agreement at `<= 17 %` on four rungs. The
  attack does not land on the *slope*; it lands on the *fraction*, which is `rho^2`.
- *"The regime partition breaks the linearity, so the control's reach is smaller than the
  algebra suggests."* This is the one live nonlinearity, and it is already scoped: the
  regime partition is named as the estimator's only nonlinearity `[R, CENTRAL_MOMENT_LADDER
  §3.b]`. It is a discrete conditioning, and §A6.2 derives from the source that both arms
  decompose exactly conditional on it, so it changes the size of the residue and not the
  fact that the deployed control occupies the channel.

### A4.4 The answer to "does ANY lawful deg-4 control survive"

**No, on all three carriers, for three different reasons — and the three reasons do not
overlap, so no carrier choice rescues it** `[D]`:

| carrier | why it is dead | level |
|---|---|---|
| MUB-129 (completed) | `A_4 = 0` identically: zero degree-four error for every network and every rotation, so zero to remove and zero fluctuation to select on | exact identity `[R + O]` |
| Kerdock-126 (structured) | the whole channel is worth `1.061 %` of MSE, and the own-axis part of it enters the error `42.6667×` weaker still | exact defect ratio `[O]` + corrected share `[D]` |
| Haar-126 (deployed `row_blocked`) | the channel is worth `31.487 %`, but the deployed moment-tangent control **already occupies it**, with the same theorem-fixed coefficient on the same axes | source read + exact identity `[O + D]` |

Independently of all three, the sealed ladder's materiality arithmetic kills the
construction at its own predicted success value (§A3).

---

## A5. Duty 1e — the exact cheapest falsifier of what is left

What survives is one number: **how much of the degree-four own-axis channel the deployed
control already removes.** Everything else is closed by exact arithmetic above.

That number is `rho^2 = Cov(M̂, Δ)^2 / (Var(M̂)·Var(Δ))`, the tangent
control's realised variance share — which is precisely the `[GAP]` that
`CENTRAL_MOMENT_LADDER` §3.a.5 already carries, and precisely what the duty-2 panel
measures. **The two open items are the same number.** Falsifier ladder, in cost order:

1. **Zero cost, done above.** The receipts read (§A4). It removes entry 8's
   construction leg and leaves only its diagnostic leg.
2. **Zero cost, done above.** The materiality arithmetic (§A3). At the theorem's own
   value the rung fails the bar by `4.98 %`; it needs `1.5963×` its prediction to pass.
3. **`3.8337 × B`, §A6.3.** One instrumented panel measuring `λ*`, `rho^2` and the
   redundancy fraction together. Discharges three ledger items in one run.
4. **`~0`, still worth running, but as a measurement only.** Slate entry 8's degree-four
   rung on the sealed ladder — it converts `lambda_4` from a four-rung extrapolation into
   an observation, gates better than every rung already run, and carries an exact null on
   a completed carrier. Predeclared prediction stands at `3.3471×` the degree-six rung.
   **Its verdict is predetermined by §A3: KILL at metric `1.0498`.** Filing it as a
   construction gate would be filing a cell whose success value is already known to fail.

---

## A6. Duty 2 — the lambda-sweep: triage, exact decision content, and the priced spec sketch

### A6.1 What the sweep actually decides — one threshold, not an estimate

`SECTION_ESTIMATOR_AND_CONSTANTS_ROW_BLOCKED` A2, `CENTRAL_MOMENT_LADDER` §3.a.5 and
`PHASE2_CONTRIBUTION_DRAFT` line 3250 all carry the same `[A]`: "the frozen `λ` sits
at the optimum `λ*`", pricing `λ → 1` at `(1−λ)²/λ² = 3.8683631e-4`
of the MSE the tangent control removes. Reproduced exactly this session `[O]`.

The price relative to the **deployed** constant — which is the number a swap decision
needs — is **linear** in `λ*`, not quadratic `[D, exact]`:

```
[Var(M - 1*D) - Var(M - lambda_d*D)] / Var(D) = (1 - lambda*)^2 - (lambda_d - lambda*)^2
                                              = (1 - lambda_d)(1 + lambda_d - 2 lambda*)
```

| `λ*` | `Δ / Var(Δ)` | price / variance removed |
|---:|---:|---:|
| `0.95` | `+1.556821e-03` | `+1.725009e-03` |
| `0.97` | `+7.852698e-04` | `+8.345943e-04` |
| `0.9807112198896164` (`= λ_d`, the committed `[A]`) | `+3.720570e-04` | `+3.868363e-04` |
| **`0.9903556099448082`** | **`0`** | **`0`** |
| `0.995` | `−1.791692e-04` | `−1.809745e-04` |
| `1.0` | `−3.720570e-04` | `−3.720570e-04` |

**The whole settling check reduces to one binary question: is `λ* > 0.99035561`?**
Above it, the theorem-fixed substitution is not a cost at all — it *improves* the variance
while removing the host's last fitted scalar in the correction path. The committed
assumption `λ_deployed = λ*` sits `0.96 %` below that threshold, so it is the
*conservative* branch: the committed price is an upper bound on the cost only if `λ*`
is at or below `λ_d`, and is a *lower* bound on the benefit if `λ*` exceeds
`0.99035561`. Precision needed to answer it is `± 0.0096` in `λ*`, half the
precision needed to distinguish `λ_d` from `1`.

### A6.2 Is it a pure artifact read? No — and here is the enumeration

The settling-check text says "one offline `λ`-sweep over the stored tangent and
sampled arms; **no forwards**". **No stored tangent arm exists.** Every `.npz` in the
corpus was enumerated with its array names and shapes `[O, 30 files]`:

| file family | arrays | is it `(M̂, Δ)` paired? |
|---|---|---|
| `a_series_granular_adversarial/a4_det_run{1,2}.npz` | `stack (32,256)`, `billed ()` | no — post-correction output stacks, 2 deterministic draws |
| `s11_full129_breakeven/s11_stacks.npz` | 18 × `(32,256)` primary/reserve at f126/f129/fctrl | no — output stacks only |
| `pb1_premise_battery/p2_partial_net*.npz` | `frame_means (16,126,256)` | sampled side only; no tangent |
| `m181_terminal_smoothing/*` | `arm0..arm3 (16,256)`, `lambdas (16,)`, `means (256,)` | different control (terminal smoothing), different `λ` |
| `m180`, `m191_g0b`, `s2`, `s3`, `s5`, `s6` | design / CV / kink / eigen arrays | no tangent arm |
| `frame_completion_129/arm*/kerdock_phases.npz`, `v31_*/sobol_owen_u32.npz` | carrier assets | inputs, not arms |

`experiments/fold_floor_splice/full.json` is a bytecode-hygiene / self-check / cost
artifact with no arms `[O]`. **`delta_mean` appears in the corpus only as source code, never
as stored data** `[O, 44 files matched on the identifier, every one of them `.py` or prose]`.
Therefore: **runs are needed.** The settling-check text's "no forwards" is not achievable
as written and should be re-filed.

**Three findings that make the run much cheaper than the text implies** `[D]`:

**(a) The sweep is truth-free.** `λ* = Cov(M̂, Δ)/Var(Δ)` is taken over the
randomization at fixed network, and the truth `t` is constant there, so
`Cov(M̂ − t, Δ) = Cov(M̂, Δ)`. **No truth is read, no Public100 row is
burned, and the panel may be synthetic seeded nets** exactly as the deg-ladder cells are.
(The *other* `[GAP]` — the control's realised share of the graded MSE — does need truth,
because MSE carries the analytic rows' bias; `rho^2`, the variance share, does not.)

**(b) One call per network yields 126 exact replicates.** Read against the deployed
source: conditional on the regime split, every operation between the layer-1 activations
and `final_mean` is **row-wise** — `x = maximum(x @ W, 0)` in the deep loop; `pre31` and
`pre32` are row-wise linear maps; `sampled_kink` and each term of `mean_on` are plain row
means (`final_weights is None` under `radial_conditioning = True`); the `dead32` columns
take deterministic analytic means `[O]`. The carrier is 126 **i.i.d.** Haar frames
(`rng.standard_normal((126,256,256))` then `qr` `[O]`), frame `f` owning rows
`[256f, 256f+256)` and `[32256+256f, 32256+256f+256)`. Hence
`M̂ = (1/126)·Σ_f M̂_f` **exactly**. `Δ` likewise: `first_moment_residual` is a
row mean, `first_variance_residual` is a fixed multiple of it (§A4.2), and the tangent
recursion is linear, so `Δ = (1/126)·Σ_f Δ_f`. Both scale as `1/126`, so the
frame-level ratio **is** `λ*` at the deployed `N` — no extrapolation, no `N`-scaling
law needed.

*Named limit:* the regime split is computed from pilot rows `x[:1024]` and
`x[32256:33280]`, i.e. **frames 0..3** (and frame 0 alone in the deep loop's cold rescue)
`[O]`. Regress on frames `4..125` — 122 exchangeable replicates per (net, seed,
coordinate) — so the conditioning frames do not enter their own regression.

**(c) `λ*` is `N`-independent, which settles a design question before it is asked.**
Because both arms are linear in the empirical measure conditional on the split,
`λ* − 1` is not an `O(N^{-1/2})` second-order sampling term; it is an `O(1)` mismatch
between the true row-wise deep response and the diagonal-Gaussian analytic tangent. The
deployed `λ_d − 1 = −0.0193` is `4.9×` the `N^{-1/2}` scale at `N = 64512`, which is
consistent with the mismatch reading and inconsistent with the sampling reading `[D]`.
A reduced-`N` economy arm is therefore neither needed nor sound.

### A6.3 SPEC SKETCH — `moment_tangent_lambda_sweep_v1`

- **id**: `moment_tangent_lambda_sweep_v1`. **bias_class**: `diagnostic (variance-only,
  truth-free, no estimator change)`. **evidence_role**: `development`. **terminal**: false.
- **hypothesis**: `λ* ≠ λ_deployed`, and specifically `λ* > 0.99035561`, in
  which case substituting the theorem-fixed `λ = 1` **reduces** variance while
  removing the deployed host's last fitted scalar in the correction path.
- **frozen inputs**: a **copy** of `experiments/row_blocked_production/candidate_source/`
  (the fenced original is read-only; copying out is permitted, editing it is not), with a
  single diagnostic change — emit `(final_mean_pre_correction, delta_mean)` and their
  per-frame decompositions alongside the return value. **Zero additional billed FLOPs**:
  both quantities already exist inside `predict`, and per-frame means carry the same adds
  as the global mean.
- **panel**: 3 synthetic seeded depth-32 width-256 He networks (the campaign's
  `101/202/303` convention) × 2 setup seeds. **6 deployed calls.**
- **statistic**: pooled least-squares slope of `M̂_f` on `Δ_f` over frames
  `4..125`, per output coordinate, centred within (net, seed, coordinate); reported with a
  frame-level bootstrap CI. The by-`λ` variance curve is then free — the sweep itself
  is offline arithmetic on the stored arms.
- **co-primaries, both free from the same arms**: `rho^2` (the `[GAP]` of
  CENTRAL_MOMENT_LADDER §3.a.5 and PHASE2 line 3252), and the degree-four redundancy
  fraction of §A5 — the share of the own-axis degree-four channel the deployed control
  already removes.
- **thresholds**: `PASS` (substitution is free or better) if the CI for `λ*` lies
  wholly above `0.9903556099448082`; `KILL` if it lies wholly below; `INCONCLUSIVE`
  otherwise. Gate on the threshold, never on the point estimate.
- **rung-2k law compliance** `[R, CENTRAL_MOMENT_LADDER §2.6]`: the statistic is a
  **second**-order quantity (a covariance ratio), so its sampling error is governed by
  moments up to `μ_4`. The predeclaration must therefore either carry the exact finite-`n`
  window at rung 4, or gate on an L-moment, or file descriptive-only. **Chosen: gate on the
  frame-level bootstrap CI with the `μ_4` window predeclared from the same frames** — the
  126-frame decomposition makes the finite-`n` window computable in-run rather than assumed.
- **second signals, in-run, each able to fail independently**: (i) the exact identity
  `first_variance_residual = −2·exact_first_mean·first_moment_residual` asserted at
  import — its failure is a protocol kill and proves the carrier is not the deployed one;
  (ii) `mean_i t² = 1/256` to `1e-15` on the realised frames; (iii)
  `mean_f M̂_f == M̂` and `mean_f Δ_f == Δ` to float32 roundoff, which is the
  frame-decomposition claim itself; (iv) billed FLOPs per call reproducing `0.638949 B`.
- **budget**: `billed_flops_declared = 1.042764e12`; `wall_seconds` cap `1200`.
- **collision check**: touches no killed id; changes no estimator constant; the deployed
  `moment_tangent_lambda` stays `0.9807112198896164` and no submission or champion lineage
  is designated by this cell.

**Exact price** `[D, from committed per-net cost]`. Deployed `row_blocked` per network:
billed `F = 173.794058e9`, residual `0.160585 s` (`= 16.0585e9` in the score's units),
`C = 189.852556e9 = 0.697987 B`
`[R, DESIGNATION_POLICY "row_blocked: C = 189.852556e9, analytical = 173.794058e9,
residual …" and the ledger's `champion_score` string]`. **Second signal on the billed
figure:** the sealed 129 cell's `mean_multiplier_arm_a = 0.6390864316824633` `[O]` gives
`0.6390864316824633 × 2.72e11 = 173.831509e9`, agreeing with `173.794058e9` to
`2.15e-4` — two independent artifacts, one number.

| panel | calls | billed FLOPs | `× B` | residual channel |
|---|---:|---:|---:|---:|
| **3 nets × 2 seeds (specified)** | **6** | **`1.042764e12`** | **`3.8337`** | **`0.9635 s`** |
| 8 nets × 2 seeds | 16 | `2.7807e12` | `10.22` | `2.57 s` |
| 3 nets × 8 seeds | 24 | `4.1711e12` | `15.33` | `3.85 s` |

Wall bound: the sealed 129 cell ran **300** deployed net-calls (3 arms × 100 networks)
under a `3600 s` cap `[O, predeclaration budgets]`, so a deployed net-call costs at most
`12 s` wall including harness and truth overhead — the 6-call panel fits inside `72 s`
`[D, upper bound]`. Total (non-residual) wall per call is not recorded in any artifact read
`[GAP]`; the `12 s` figure is a cap-derived ceiling, not a measurement.

**Sizing, stated as a function of the unknown it depends on** `[D]`. If `λ*` sits at the
deployed value, its distance to the decision threshold is `0.0096444`, so a 3σ verdict
needs `σ(λ̂) <= 0.0032148`, i.e. relative `0.0032780`, i.e.
`n_eff >= ((1 − rho²)/rho²) / 0.0032780²`:

| `rho²` | `n_eff` required |
|---:|---:|
| `0.99` | `940` |
| `0.95` | `4,898` |
| `0.90` | `10,340` |
| `0.80` | `23,266` |
| `0.70` | `39,884` |
| `0.50` | `93,063` |

The specified panel supplies `3 nets × 2 seeds × 122 frames = 732` replicate slots per
output coordinate, across 256 coordinates whose effective independent count is between
`26` and `91` `[D, from the cell's ridge-collinearity spectrum: top-one gradient share
`0.038` at the readout against an isotropic null of `0.011` `[O]`]` — so `19,032` to
`66,612` effective pairs. That decides the threshold at `rho² >= 0.9` and leaves
`rho² <= 0.8` undecided. `rho²` is itself a co-primary of this cell, so the sequencing is:
run the 6-call panel, read `rho²`, and re-size from the measured value rather than from an
assumed one. At `rho² = 0.5` the required panel is `93,063 / (122 × 26..91)` =
`30` to `10` net·seed cells, i.e. `10` to `30` deployed calls (`1.74e12` to `5.21e12`
billed, `6.4×` to `19.2× B`).

**Why this is not filed at `cost_vs_B ~ 0`.** `3.8337 × B` of billed FLOPs is `3485×` the
`~0.11 % of B per call` the slate's rung-2 cells are priced at. It is a real charge and
must be declared as one. What buys it back is that a single panel discharges **three**
standing ledger items: the `λ_deployed = λ*` assumption, the tangent control's
realised variance share, and slate entry 8's degree-four redundancy fraction.

---

## A7. Two-signal ledger for this addendum

| claim | signal 1 | signal 2 | agreement |
|---|---|---|---|
| `lambda_4 = −5.0744e−3` | SLATE entry 8 `[R]` | ReLU Hermite closed form via `lgamma`, normalised at `n=6` on the committed `lambda_6` `[D]` | `0.205 %` |
| `lambda_4²/lambda_6² = 3.34706` | computed from committed constants `[D]` | SLATE entry 8 "about 3.35x" `[R]` | `0.09 %` |
| the `59.4 %` is the kink's own tail energy | cell `predeclaration.causal_mechanism` + `metrics.geometry` `[O]` | independent Hermite recomputation converging to `0.59022` `[D]` | same object, `0.4` pt on truncation |
| Haar-side deg-4 share `= 0.162285` | exact `Fraction` transfer of r0's 11-degree table `[D]` | SLATE entry 1 `"~16 % … ~1/36"`; this session derives `1/36.063` `[R]` | independent artifacts |
| `A_4^A/A_4^C = 128/3` | THEORY §1.3 `[R]` | sealed 129 cell `a4_suppression_factor_arm_a_over_arm_c = 42.666666666666664` `[O]` | exact |
| deg-4 rung leaves the band short | `0.006278 + 0.012772 = 0.019050` vs `R2_BAR = 0.02` `[D]` | the cell's own predicted signature quotes "the 0.0267 that escaping KILL requires"; `0.02/0.75 = 0.0266667` `[O]` | exact |
| `first_variance_residual = −2·m·first_moment_residual` on the deployed carrier | algebra: `relu(p)² + relu(−p)² = p²`, `mean_i t² = 1/d` on an orthonormal frame `[D]` | float64 check, 8 frames, `d=256`: max abs `1.78e-15`, relative `2.90e-15` `[O]` | roundoff |
| degree 2 annihilated by the deployed carrier | `Σ_k ⟨q_k, ŵ⟩² = 1` `[D]` | measured `mean_i t² = 0.00390625000000000` vs `1/256` `[O]` | 17 digits |
| deployed billed cost `173.794058e9`/net | DESIGNATION_POLICY / ledger `champion_score` `[R]` | sealed 129 cell `mean_multiplier_arm_a × B = 173.831509e9` `[O]` | `2.15e-4` |
| `λ → 1` price `3.8683631e-4` | committed in three documents `[R]` | recomputed `(1−λ)²/λ²` this session `[O]` | all digits |
| the slate's `2.28× / 1.13×` ceilings | eight weightings computed against the sealed metrics `[D]` | none reproduces the pair; the Haar leg reproduces at `3.00×` (`1.1283`), not at entry 8's own `3.35×` (`1.0498`) | **disagree — filed** |

## A8. Limitations

- `rho_own(4)` is a **prediction**, not a measurement: the degree-four rung of the own-axis
  ladder still does not exist. Every ceiling in §A3 inherits that status. What is
  measured is the profile it sits on (`<= 17 %` agreement with `lambda_n²` at four rungs).
- `k_odd = E(deg >= 3)/E(even, deg >= 4)` is unmeasured `[GAP]`, so the conversion of the
  ladder's currency into a Haar-host MSE share carries one unpinned factor `>= 1`. Settling
  check: r0 §8's never-run `r2_measured_harmonic_spectrum`, Arm 1.
- `rho²`, the tangent control's realised variance share, remains unmeasured. It is the sole
  quantity separating "the deployed control already removed the degree-four channel" from
  "it entered the channel with the right slope and removed little of it". §A6.3 measures it.
- The frame decomposition of §A6.2 is exact **conditional on the regime split**; the
  between-seed component of `λ*` (the regime-partition channel) is what the second seed
  is for, and 2 seeds bound it rather than resolve it.
- The float64 identity check in §A4.2 used 8 frames on one random `W0`, not the deployed
  126-frame carrier on a real network. It verifies the algebraic identity, not the deployed
  run.
- The deg-4 redundancy argument is about the deployed **Haar** host. It says nothing about
  a hypothetical host that drops the moment-tangent control, and nothing about degrees
  `>= 6`, whose door the sealed ladder already closed at idx 274/275.
