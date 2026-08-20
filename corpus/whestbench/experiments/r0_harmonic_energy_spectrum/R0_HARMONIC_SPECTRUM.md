# R0 — Harmonic energy spectrum of the residual, from the committed record alone

Ledger id: `r0_harmonic_energy_spectrum` · Date: 2026-08-10 · Rung: **R0 + R1 only**
Runner: `run_r0.py` (3.9 s) · Results: `r0_results.json` · Console log: `r0_run.log`

---

## DEVIATIONS AND BOUNDARY CALLS — recorded first, loudly

**D1 (the one that matters). Arm B re-derives a committed closed form.** The
depth-32 mean-field correlation kernel `f(c) = (sqrt(1-c^2) + c(pi - arccos c))/pi`,
iterated 32 times, is printed verbatim in `S7_VERDICT.md` §"Mean-field prediction"
and tabulated at 37 grid points and 8 probe points in `s7_results.json`. Arm B
executes those 32 **scalar** iterations and extracts the resulting function's
Taylor series. No network is built or evaluated, no design is generated, no
estimator or m245 code runs, no data is measured. I judged this inside R1
("arithmetic on numbers already in committed artifacts") because the object
re-derived is itself committed and the re-derivation reproduces its committed
tabulation **bitwise** (max abs deviation **0.0** on all 37 table points, **0.0**
on all 8 probe points, **0.0** at the plateau). A reviewer who reads R1 more
tightly should read **Arm A** and the **n_eff discriminator** below, which use
only numbers printed in the JSON and reach the same verdict with a smaller
margin.

**D2. Arm A was re-specified mid-run.** The plan was a square interpolation of
`a_1..a_6` through six committed small-t table points. That system has condition
number > 1e8 in the Gegenbauer basis (the columns `G_1..G_6` are near-collinear on
`t in [0, 0.26]`) and returned nonsense (`a_4 = -10`). Replaced by (i) windowed
overdetermined least squares at three window/order settings and (ii) Richardson
extrapolation of `C(t)/t` to `t = 0` for `a_1`. Arm A therefore resolves **a_1
only**; it does not resolve `a_2..a_6`. Recorded rather than silently swapped.

**D3. The three nets' measured correlation cannot yield a spectrum.** S7's 8
probe angles put 6 points at `t > 0.93` and the remaining two at `t = 0.7071` and
`t = 0`. The interval `t in (0, 0.707)` — exactly where the low-degree
coefficients are pinned — is unsampled. The measured arm is reported as a
**constraint** (via the model-free `n_eff` diagnostic) and never as a fitted
spectrum.

**D4. The estimator-error-by-degree table uses the mean-field spectrum.** Its
implied `N_eff = 100,669` sits **2.1x–3.7x above** S17's measured 27,251 / 39,558
/ 46,955. The discrepancy is reported in §6, not absorbed.

**D5. No R2 was run.** Section 8 specifies the minimal screen that would resolve
what R0/R1 leaves open. It was not executed.

---

## VERDICT (one paragraph)

**Picture (a), max-entropy speckle read as per-mode equipartition, is FALSIFIED —
and picture (b), a truncatable Kolmogorov-type cascade, is ALSO falsified, at the
per-mode level.** The residual's energy per *degree* falls as a shallow power law
`a_l ~ l^-p` with a running exponent `p = 0.19` (l=1→2) rising through `1.10`
(l=4–24) to `1.48` (l=20→40) — genuinely power-law, and remarkably near
Kolmogorov's 5/3 in the resolved band, which is picture (b)'s *first* clause. But
energy per *mode* `a_l / dim H_l` collapses by 1.3e6 between l=1 and l=4 and by
4.3e18 by l=12, a decay driven entirely by the explosion of `dim H_l` and better
fit by an exponential than by any power law at every band tested. So the flat
shelf the corpus measured is a property of the **design's** deviation operator D,
not of the residual **field**; and the fluid analogy fails at its operative
clause, because a cascade whose "inertial range" costs 6.2e27 dimensions to
truncate is not truncatable. **No low-rank or truncation class reopens.** The
central theorem's *conclusion* survives from a genuinely new direction; its
stated *mechanism* ("energy equipartitioned across modes") needs correcting to
"energy spread nearly uniformly over ~40+ degrees, each of astronomical
dimension." At R0/R1 this **RESOLVES** the equipartition question (model-free
margin >= 33x, closed-form margin 1.3e6) and **RESOLVES** the truncation question
(no single degree carries more than 13.8% of the estimator error). It does **not**
resolve the per-net *amplitude* of the spectrum, nor a factor 2.1–3.7 tension with
S17's measured floor; §8 specifies the R2 screen for those.

---

## 1. What per-degree information the committed record already contains

Two categories, and conflating them is the trap the question names. Kept apart
throughout.

### 1a. DESIGN properties — how badly the Kerdock design integrates degree l

These say nothing about the residual field. All are exact.

| source | quantity | degrees covered |
|---|---|---|
| S6 `deg4/deg6.closed_form.lam_top` | `lam_top(l)` = mean-square quadrature error per unit degree-l energy | 4, 6 |
| S6 `fingerprint.distinct_values` | the **exact** inner-product census over all 32,256^2 pairs | all l (see below) |
| S6 `haar_H{4,6}_design_over_iid_rms` | `sqrt(N·lam_top)` = design/iid RMS for a Haar H_l function | 4, 6 |
| M191 G0-a `rot{0,1,2}.deg{1..6}.ratio` | measured design/iid RMS on random harmonic polys | 1, 2, 3, 4, 5, 6 |
| S17 §A.1 | the exact 5-shell doubled fingerprint | all l |

**New at R0/R1:** the census is exact and dyadic, so `lam_top(l)` extends to
*every* degree by arithmetic alone —

```
lam_top(l) = (1/N^2)[ N·1 + n_0·G_l(0) + n_+·G_l(1/16) + n_-·G_l(-1/16) ]
N = 32,256   n_0 = 8,225,280   n_+ = 548,352,000   n_- = 483,840,000
```

Recomputed this way, `lam_top(4) = 7.350908201315546e-07` and
`lam_top(6) = 3.194089008420301e-05` — **identical to every printed digit** of
S6's independently-derived closed form. Extended (design/iid **variance** ratio
`N·lam_top`, antipodally-doubled 64,512 design, so all odd l are exactly 0):

| l | 1 | 2 | 3 | 4 | 5 | 6 | 8 | 10 | 12 | 16 | 20 | 40 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| N·lam_top | 0 | 0 | 0 | **0.02371** | 0 | **1.03029** | 0.99905 | 1.00003 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

The degree-4 Bragg suppression is a **single isolated notch**. Degree 6 is
*above* iid (1.0303), and every even degree from 8 up is iid-level to 5 digits.
The Kerdock ±1/16 phase cancellation buys exactly one degree and nothing else —
S6 said this for l=6; the census says it for all l.

### 1b. RESIDUAL-FIELD properties — where the field's energy actually sits

| source | quantity | what it is |
|---|---|---|
| S7 `meanfield.table_c32` / `table_c_pred` (37 pts, f64) | the depth-32 mean-field angular correlation function | **the generating function of the spectrum** |
| S7 `nets[*].c_meas` (8 pts x 3 nets) | measured angular correlation of the actual residual | constrains the spectrum, cannot fit it (D3) |
| S7 `xi` = 36.98 / 35.60 / 45.95 deg, ratio 1.77/1.70/2.20 | correlation length and its finite-width inflation | the spectrum is even more low-degree than mean-field |
| S15 `base_B.r2_base_oos` = 0.3609 / 0.4037 / 0.4385 | degree<=2 (partial) explained variance | anchors `a_1 + partial a_2` |
| S15 `baseA.C4_control_linear.incremental_oos` = 0.2929 / 0.2861 / 0.3667 | the single optimal degree-1 mode's share | anchors `a_1` from below |
| S15 `positive_control.pure_deg4_R2` = 6.1e-6 / 1.15e-5 / 7.9e-6 (max 3.38e-5) | **one zonal H_4 mode's** energy share | anchors per-mode l=4 from above |
| S17 `sigma^2` = 7.900e-3 / 1.600e-2 / 1.112e-2 | field variance over the 64,512 design | converts shares to absolute energy |
| S17 `N_eff` = 39,558 / 27,251 / 46,955 | effective independent draws | the consistency target for the whole spectrum |

**Corpus sweep for degree >= 6 harmonic content.** Grepping the whole corpus for
per-degree harmonic reporting returns exactly three producers: S6 (degrees 4 and
6, design side), M191 G0-a (degrees 1–6, design side) and M191 G0-b
(`r2_summary.deg6` = 0.00105 / 0.00133 / 0.00132 for a 12-axis `p6` control-variate
basis against a truth-based CV residual — a *different target* from the
cross-direction variance, and contaminated by lower degrees exactly as S15 showed
for `p4`; not used here). **No committed artifact reports residual-field harmonic
energy above degree 6.** The word "equipartition" appears nowhere in the corpus;
picture (a) is an extrapolation of S6's flat-D result, not a committed claim.

---

## 2. The spectrum I could build

Isotropy makes this exact rather than approximate. For a rotation-ensemble
residual field on S^255, Schoenberg's theorem gives

```
C(t) = sum_{l>=0} a_l G_l(t),   a_l >= 0,   sum_l a_l = 1,   G_l = C_l^(127)(t)/C_l^(127)(1)
```

and `a_l` **is** the fraction of energy at degree l. The committed correlation
function therefore *is* the spectrum, in a different coordinate system. Mean
removal divides by `1 - a_0`, which is why S7's normalization uses `1 - c_32(0)`.

### Arm B (mean-field, D1) — the full spectrum

Two independent Cauchy radii (0.70 and 0.85, 256-point DFT each, mpmath at 50
dps) give the Taylor coefficients of `c_32` identically to f64. Exact-rational
transfer `a_l = sum_k b_k · m_l·E[t^k G_l(t)]` (transfer bounded, `max|kappa| =
1.0`, so no amplification).

| l | dim H_l | **a_l** (per degree) | cumulative | **a_l / dim H_l** (per mode) | N·lam_top (DESIGN) |
|---|---|---|---|---|---|
| 1 | 2.560e+02 | 1.1067e-01 | 0.111 | **4.323e-04** | 0 |
| 2 | 3.290e+04 | 9.671e-02 | 0.207 | 2.940e-06 | 0 |
| 3 | 2.829e+06 | 7.267e-02 | 0.280 | 2.569e-08 | 0 |
| 4 | 1.831e+08 | 6.060e-02 | 0.341 | **3.309e-10** | 0.02371 |
| 5 | 9.523e+09 | 4.976e-02 | 0.390 | 5.225e-12 | 0 |
| 6 | 4.142e+11 | 4.298e-02 | 0.433 | 1.038e-13 | 1.03029 |
| 8 | 5.094e+14 | 3.264e-02 | 0.503 | 6.408e-17 | 0.99905 |
| 10 | 3.958e+17 | 2.589e-02 | 0.558 | 6.541e-20 | 1.00003 |
| 12 | 2.128e+20 | 2.115e-02 | 0.602 | **9.938e-23** | 1.00000 |
| 16 | 2.567e+25 | 1.501e-02 | 0.670 | 5.848e-28 | 1.00000 |
| 20 | 1.233e+30 | 1.126e-02 | 0.720 | 9.130e-33 | 1.00000 |
| 24 | 2.861e+34 | 8.765e-03 | 0.759 | 3.064e-37 | 1.00000 |
| 32 | 2.800e+42 | 5.738e-03 | 0.814 | 2.050e-45 | 1.00000 |
| 40 | 4.678e+49 | 4.024e-03 | 0.852 | 8.602e-53 | 1.00000 |
| >40 | — | 0.1485 (tail) | 1.000 | — | 1.00000 |

Restricted to the degrees that can generate estimator error at all (l >= 4): total
mass 0.7199, per-degree exponent over l = 4–24 unchanged at **p = 1.099**
(renormalization rescales, it does not tilt).

### Arm A (model-free, committed table only) — a_1 alone

| method | a_1 |
|---|---|
| Richardson on `C(t)/t` at the three smallest committed t | **0.109822** |
| windowed LS, \|t\|<=0.18, L=3 | 0.118265 |
| windowed LS, \|t\|<=0.26, L=4 | 0.118681 |
| windowed LS, \|t\|<=0.50, L=6 | 0.119461 |
| **Arm B** | **0.110670** |

Richardson agrees with Arm B to **0.77 %**; the windowed fits sit 7 % high and are
stable in `a_1` while `a_2, a_3` swing wildly (D2). Two-signal on `a_1`: yes.
Per-degree resolution from Arm A alone: no.

### What the three measured nets add

S15's regression anchor gives `a_1` in **[0.293, 0.327] / [0.286, 0.363] /
[0.367, 0.403]** — about **2.7x** the mean-field 0.1107, in the same direction and
the same order as S7's independently measured correlation-length inflation
(1.77 / 1.70 / 2.20). Two different instruments (angular correlation of pairs;
out-of-sample regression R^2) agree that the real finite-width field is
**smoother** — more low-degree-weighted — than the infinite-width mean field. The
mean-field spectrum is therefore a **conservative** stand-in for this question:
the real one is even further from equipartition.

---

## 3. Test of picture (a): equipartition

Equipartition means `a_l / dim H_l` constant, i.e. `a_l ∝ dim H_l`.

**Closed-form margin (Arm B).**

| | l = 4 | l = 12 |
|---|---|---|
| `a_l/a_1` predicted by equipartition (= dim H_l / dim H_1) | 715,423.75 | 8.314e+17 |
| `a_l/a_1` observed | 0.5475 | 0.1911 |
| **violation factor** | **1.31e+06** | **4.35e+18** |

**Model-free margin (S15 only, no model at all).** Compare the energy share of a
*randomly chosen* mode at each degree:

| net | per-mode l=1 (`a_1/256`) | per-mode l=4 (single zonal H_4 mode) | ratio, conservative | ratio, pointwise |
|---|---|---|---|---|
| 101 | 1.144e-03 | <= 1.521e-05 (max of 5 axes) | **75.2** | 186.4 |
| 202 | 1.118e-03 | <= 3.381e-05 | **33.1** | 97.1 |
| 303 | 1.432e-03 | <= 2.126e-05 | **67.4** | 181.2 |

Equipartition predicts **1.0** for every one of these. It is out by >= 33x on the
worst net using only committed measured numbers, and the l=4 side is itself only
an upper bound: those single-mode R^2 values (6.1e-6 – 3.4e-5) straddle the
in-sample 1-dof fitting-noise floor `1/64,512 = 1.55e-5`, so the true per-mode
l=4 energy is smaller and the true margin larger.

**Model-free discriminator, no fitting whatsoever.** If per-mode energy were flat
over a band `l <= L`, the normalized correlation would be the band-limited
reproducing kernel `C_eq^(L)(t) = sum_{l<=L} m_l G_l(t) / sum_{l<=L} m_l ~ t^L`
(because `m_L` swamps every lower degree). Its "effective single-degree index"
`n_eff(t) = ln C(t) / ln t` would then be **constant = L at every t** (verified:
`C_eq^(4)` gives n_eff = 4.049 at t=0.707 and 4.032 at t=0.940). Measured:

| t = | 0.2588 | 0.5000 | 0.7071 | 0.9397 | 0.9848 | 0.9962 |
|---|---|---|---|---|---|---|
| mean-field (committed table) | 2.451 | 3.409 | 4.821 | 10.559 | 17.343 | 24.473 |
| measured net 101 | — | — | 2.560 | 4.080 | 5.004 | 6.198 |
| measured net 202 | — | — | 2.705 | 4.268 | 4.389 | 6.231 |
| measured net 303 | — | — | 1.911 | 3.299 | 3.584 | 4.756 |

`n_eff` climbs monotonically by a factor 2.5–10 across the sampled range on every
curve. A band-limited flat spectrum is flatly incompatible with that. And at the
one t where all three nets have committed measurements (t = 0.7071, theta = 45 deg),
measured `C_r` = 0.4118 / 0.3916 / 0.5156 against `C_eq^(4)` = 0.2458,
`C_eq^(6)` = 0.1190, `C_eq^(8)` = 0.0566, `C_eq^(12)` = 0.0122 — the residual is
1.6–2.1x above even the most favourable (L=4) equipartition kernel and 34–42x
above L=12.

**Picture (a): FALSIFIED.** Three independent routes, margins 33x (measured,
model-free), ~2.5x–10x drift (measured, model-free, different statistic), 1.3e6
(closed form).

---

## 4. Test of picture (b): turbulent cascade

Split the claim into its two clauses, because they get different answers.

**(b1) "Energy decays with degree following a power law" — HOLDS, per degree.**

| band | per-degree exponent p | log-log R^2 |
|---|---|---|
| l = 1–12 | 0.714 | 0.954 |
| l = 4–24 | **1.099** | 0.994 |
| l = 12–40 | **1.391** | 0.998 |
| l = 1–40 | 1.038 | 0.962 |

Running two-point exponents: 0.195 (1→2), 0.674 (2→4), 0.892 (4→8), 1.121 (8→16),
1.387 (16→32), 1.484 (20→40). **Implied exponent: p ≈ 1.1 over the degrees that
matter (4–24), rising toward ≈ 1.5 and still climbing at l = 40.** Kolmogorov's
5/3 = 1.667 sits just above the resolved range. I flag that proximity as a
numerical fact and explicitly decline to read it as a mechanism: `p` here is a
fixed-point property of the iterated arccos ReLU kernel and is *not* constant, so
it is not an inertial-range exponent in the Kolmogorov sense.

**(b2) "…giving an inertial range in which truncation captures most of the
energy" — FAILS, twice.**

*Per mode, it is not a power law at all.* Fitting `a_l/dim H_l`:

| band | power-law p | log-log R^2 | exponential slope / degree | semi-log R^2 |
|---|---|---|---|---|
| l = 1–12 | 17.8 | 0.932 | −3.860 | **0.995** |
| l = 4–24 | 35.9 | 0.973 | −3.073 | **0.995** |
| l = 12–40 | 58.5 | 0.990 | −2.452 | **0.997** |

The nominal "exponent" triples with the band while the semi-log fit beats the
log-log fit everywhere — the signature of exponential, not power-law, decay. The
decay is `a_l · l! / d^l`: driven by the mode count, not by any transfer.

*And the degree spectrum is too broad to truncate.* Cumulative energy reaches
only 0.341 at l<=4, 0.503 at l<=8, 0.602 at l<=12, 0.852 at l<=40, with a 0.149
tail above l = 40. There is no cutoff and no inertial range with an end.

**Picture (b): its power-law clause holds per degree; its truncation clause,
which is the whole reason the analogy was under test, fails.**

---

## 5. Where the estimator's error actually lives (the operational answer)

Combining the two columns that must never be conflated —
`MSE/sigma^2 = sum_{l even >= 4} a_l · lam_top(l)` (odd degrees annihilated by
antipodal pairing, degrees 0 and 2 by the exact 2-design):

| degree | 4 | 6 | 8 | 10 | 12 | 14 | 16 | 18 | 20 | 22–40 | >40 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| share of MSE | **0.45 %** | **13.82 %** | 10.18 % | 8.08 % | 6.60 % | 5.51 % | 4.68 % | 4.03 % | 3.51 % | 19.9 % | 23.2 % |

- Degree 4 — the one the Kerdock design was measured to suppress 42x — carries
  **0.45 %** of the estimator's error. Even degrees >= 6 carry **99.55 %**.
- **No single degree carries more than 13.8 %.** Capturing 50 % of the error
  requires exactly integrating degrees **{6, 8, 10, 12, 14, 16, 18}**, whose joint
  dimension is **6.25e+27**.

That is the sentence that closes the truncation class. An LES-style truncation
works because low-k modes are *few*; here the "large eddies" that still matter
(degree 6 and up) already number 4.1e11 and the count explodes from there. A
harmonic control variate at degree 6 needs a basis of dimension dim H_6, and a
design exact to degree 18 needs on the order of d^9 points.

---

## 6. Attack on the conclusion, and the tension it found

The strongest counter-hypothesis is that the mean-field spectrum is simply wrong
about the real nets. Tested three ways.

1. **Direction of the finite-width offset.** If the real spectrum had *more* high-
   degree energy, equipartition would be less dead. It has *less*: S7's `xi` runs
   1.70–2.20x the mean field, S15's `a_1` runs 2.7x, and the `n_eff` table shows
   the measured curves *below* the mean-field curve at every t. The correction
   strengthens the verdict.
2. **Absolute-scale check against S17 — this one landed, partially.** The spectrum
   implies `MSE/sigma^2 = 9.93e-6`, i.e. `N_eff = 100,669`. S17 measured
   `N_eff = 39,558 / 27,251 / 46,955` (`MSE/sigma^2 = 2.53e-5 / 3.67e-5 /
   2.13e-5`). The prediction is **2.1x–3.7x optimistic**, and pushing the spectrum
   toward the measured (smoother) nets makes it *more* optimistic, not less. The
   leading explanation is an object mismatch that S17 itself discloses: its
   `sigma^2` is `Var(ybar)` of the **neuron-averaged scalar**, while the champion
   MSE is per-**output-component**; S7 measures only ~1.5–2 effective independent
   neuron amplitudes out of 256, so the per-component field carries more
   incoherent (high-degree) energy than the average does. Secondary contributors:
   the champion MSE includes 4–6 % truth-MC noise (`m191_g0b.truth_noise_final`),
   and 16 rotation replicates give ~36 % relative SE per net. **This is reported,
   not absorbed.** It does not move the verdict: both pictures are tested by
   *shape*, and a uniform 2–4x scale factor changes no exponent, no ratio, and no
   per-degree share. §8 names the check that settles it.
3. **Isotropy.** `a_l` is the rotation-*ensemble* spectrum, which is the right
   object for the estimator's MSE (the grader supplies a Haar rotation). For a
   *fixed* net the energy within a degree is anisotropic: S15's Base-B captures
   0.03–0.07 of the variance using only 376 of the 32,896 degree-2 modes, chosen
   along the first-layer singular directions. Output-side estimators see the
   isotropic spectrum; a seed-side estimator would see the anisotropic one. That
   distinction is squarely inside P1 §4.5's open door and is untouched here.

---

## 7. Consequence for the theorem

The measured theorem's clause (a) says the degree-4 deviation operator D has mass
"flat at ~1/N across the entire 32,256-mode design span". That is a statement
about the **design**, it is exactly right, and this analysis reproduces its
numbers from the census. Nothing here disturbs it.

What this analysis does disturb is the *extension* of that flatness to the
residual field — the reading in which "maximum entropy" implies per-mode
equipartition and hence "nothing to truncate because everything is equally
everywhere." The residual field is nearly the opposite: an extremely smooth,
strongly low-degree-weighted field (correlation length 36–46 deg on a sphere whose
design points are 86.4 deg apart) whose per-mode energy collapses by six orders of
magnitude between degree 1 and degree 4.

The conclusion survives for a **different and stronger reason**: not "energy is
everywhere equally" but "the energy that the design does not already integrate is
spread over 40+ degrees, no one of which carries more than 14 % of the error, and
the cheapest of those degrees already costs 4.1e11 dimensions to touch." The
fluid analogy is therefore a **contrast, not a mechanism** — it has a power law
where we have a power law, and an inertial range where we have a dimension wall.
Suggested wording repair for P1 clause (b)/§3.1 F1: replace "delocalised over
~1.8e8 dimensions" as the *reason* nothing bites with "spread across every degree
above the design's exactness, each of dimension >= 1.8e8" — the flatness that kills
low-rank correction is flatness **across degrees**, not across modes.

---

## 8. Does R0/R1 resolve it? — honesty clause, and the R2 spec

**RESOLVED at R0/R1**

1. *Equipartition is dead.* Margin >= 33x from committed measured numbers with no
   model (S15 per-mode l=1 vs l=4), corroborated by the `n_eff` drift (measured,
   model-free) and 1.3e6 from the committed closed form.
2. *No truncation or low-rank class reopens.* No single degree carries more than
   13.8 % of the estimator error; 50 % needs seven degrees of joint dimension
   6.25e27. This holds for any spectrum in the family the committed data allow,
   because it depends only on the *breadth* of `a_l` and on `lam_top(l) ≈ 1/N` for
   every even `l >= 6` — and the latter is exact arithmetic on the census.
3. *The degree-4 Bragg notch is operationally irrelevant.* 0.45 % of the error.
   Extending `lam_top` across all degrees from the exact census is new and settles
   this: degree 4 is the only suppressed degree, and it is not where the error is.

**NOT RESOLVED at R0/R1**

4. *The measured spectrum's amplitude, per net.* Every per-degree number above
   l = 1 comes from the mean-field closed form (D1). The three nets constrain the
   shape (via `n_eff`) and pin `a_1` (via S15) but cannot fit `a_2..a_16` (D3).
5. *The 2.1x–3.7x N_eff tension* (§6.2). Unresolved; the object-mismatch
   hypothesis is untested.
6. *The exponent's asymptote.* `p` is still rising at l = 40 and the tail above
   l = 40 holds 14.9 % of the mass. Whether `p -> 5/3` or `p -> 2` is not settled,
   and no committed artifact touches degrees above 6.

### The minimal R2 screen (specified; NOT RUN)

`r2_measured_harmonic_spectrum`. Purpose: measure `a_l` for `l = 1..16` directly
on the committed nets and close items 4–6.

- **Nets / design.** Synthetic He nets 101 / 202 / 303, width 256, depth 32,
  bias-free, at their committed rotations `haar_rotation(900000 + seed*1000)`,
  imported read-only from `n8a_rqmc_kerdock/run_n8a_gates.py`. No new nets.
- **Data.** Per net, `M = 40,000` fresh Haar directions at radius
  `mean_chi(256) = 15.98438266660853` (the same probe construction and scale S7
  used for its 4,000-pair arm; S7 cost 25 s total, so ~2 min/net here). Nothing
  else is generated.
- **Basis / estimator.** Unbiased Gegenbauer projection, no fitting:
  `a_l_hat = m_l · [ (1/(M(M-1))) sum_{i!=j} G_l(<u_i,u_j>) r_i r_j ] / [(1/M) sum_i r_i^2]`,
  `r = f - mean(f)`, `G_l` by the normalized three-term recurrence used here,
  `l = 1..16`, chunked pair sums (O(M^2 L) ≈ 2.6e10 fused ops, seconds).
- **Degrees required.** 1–16. Degrees 1–3 anchor against S15; 4 and 6 anchor
  against S6/M191; 8–16 are the genuinely new range.
- **Second signal (mandatory).** (i) Bin the same pairs by `<u_i,u_j>` into 200
  bins on `t in [-0.5, 0.5]` and recover `a_l` by projection against the Haar
  weight; agree to 10 % on `l <= 8`. (ii) Reproduce S7's committed `c_meas` at its
  8 probe angles from the same forwards, within 2x the committed SE 0.0449.
- **Arm 2 (closes item 5).** Repeat on the **per-output-component** field
  `r_i(u)`, `i = 1..256`, reporting `sigma^2_component` and `a_l^component`. This
  is the disclosed S17 object mismatch and the only named candidate for the
  2.1–3.7x gap.
- **Predeclared gates.**
  - **G1 (equipartition).** KILL equipartition if
    `(a_1_hat/dim H_1) / (a_4_hat/dim H_4) > 1e3` on >= 2/3 nets.
    Prediction: 1.3e6. Equipartition predicts 1.
  - **G2 (cascade).** The cascade picture SURVIVES only if, for the per-mode
    sequence `a_l_hat/dim H_l` over `l = 4..12`, the log-log fit's log-R^2 exceeds
    the semi-log fit's **and** the fitted exponent `p < 6`, on >= 2/3 nets.
    Prediction: fails both (p = 17.8–58.5, semi-log wins).
  - **G3 (truncation reopen).** A truncation class REOPENS if some single degree
    `l >= 4` carries >= 50 % of `sum_{even l>=4} a_l_hat · lam_top(l)` on >= 2/3
    nets. Prediction: max single-degree share 13.8 % ⇒ stays closed.
  - **G4 (floor reconciliation).** The spectral account of the champion's MSE is
    CONFIRMED if `|N_eff_implied / N_eff_S17 − 1| <= 0.5` on >= 2/3 nets using the
    Arm-2 per-component numbers. Otherwise the object-mismatch hypothesis is
    refuted and the residual gap is reported open.
  - INCONCLUSIVE otherwise; no gate is retuned after the fact.
- **Firewall.** Synthetic nets only; frozen sources imported read-only and never
  edited; no truth arrays, no scorer, no submission, no git; no touch of any
  `m24*` / `*_fable_oracle` lane; writes confined to the R2 directory.
- **Cost.** ~10 min wall, single process, no GPU.

---

## 9. Two-signal verification ledger

Every number the verdict rests on, re-derived a second way.

| claim | signal 1 | signal 2 | agreement |
|---|---|---|---|
| dim H_4, dim H_6 | `C(d+l-1,l) − C(d+l-3,l-2)` | `(2l+d-2)/l · C(l+d-3,l-1)` and S6 `constants` | exact integer match |
| `G_4(0), G_4(1/16), G_6(0), G_6(1/16)` | exact-rational recurrence | S6 `constants` | all digits |
| `C_4^(127)` coefficients and `C_4(1)` | exact-rational recurrence | S6 `constants` | exact integers |
| `lam_top(4), lam_top(6)` | exact census sum (this run) | S6 independent closed form | all digits |
| `sqrt(N·lam_top)` | this run | S6 `haar_H{4,6}_design_over_iid_rms` | all digits |
| odd degrees exact on the doubled design | `G_l(t)+G_l(−t) = 0` derivation | M191 G0-a deg 1/3/5 ratio = 0.0 | exact |
| mean-field kernel | 32 scalar iterations (this run) | S7 committed 37-pt table + 8-pt probe + plateau | **max abs dev 0.0** |
| Taylor coefficients `b_k` | Cauchy DFT at rho = 0.70 | Cauchy DFT at rho = 0.85 | max abs diff 0.0 (f64) |
| `b_0` | this run: 0.9747204751243134 | S7 `m2_plateau`: 0.9747204751243136 | 2 ulp |
| `a_1` | Arm B closed form: 0.110670 | Arm A Richardson on committed table: 0.109822 | 0.77 % |
| `a_1` (real nets) | S15 C4 control: 0.293 / 0.286 / 0.367 | S7 xi inflation 1.77/1.70/2.20 x mean-field 0.1107 | same direction, same order |
| equipartition dead | S15 per-mode l1/l4 >= 33x | `n_eff(t)` drift 2.5–10x, both arms | independent statistics |
| reconstruction | `sum_l a_l G_l(t)` | S7 committed `table_c_pred`, theta >= 60 deg | max abs 3.8e-4 |

Determinism: two consecutive runs printed identical values on every quantity.

---

## 10. Limitations

- Everything about degrees `l >= 2` rests on the mean-field closed form (D1). The
  three nets constrain but do not measure it (D3).
- The Gegenbauer expansion is truncated at `l = 40`; 14.9 % of the mass sits above
  it, and that tail is assigned iid-level `lam_top = 1/N` in §5 (correct to 5
  digits for every even `l >= 8`, but the *mass* is extrapolated).
- The estimator-error table's absolute scale is 2.1x–3.7x off S17's measurement
  (§6.2); only its *shape* is used in the verdict.
- `a_l` is the rotation-ensemble spectrum; within-degree anisotropy for a fixed
  net is real (§6.3) and is not measured here.
- Three synthetic He nets, one rotation each, at a single (width, depth) =
  (256, 32) under one frozen probe design. No claim about trained networks.
- No R2, no new measurement, no forward pass, no submission, no git.

## Files

- `run_r0.py` — the harness (deterministic; committed JSONs read-only)
- `r0_results.json` — all numbers
- `r0_run.log` — console output of the committed run
- `R0_HARMONIC_SPECTRUM.md` — this document
