# EXCESS GAIN — VERIFIER SYNTHESIS (LANE 3 OF 3)

**Date** 2026-08-19. **Lane** hostile verifier and synthesizer, closing the blind pair
(`EXCESS_GAIN_MOMENTS_THEORY_20260819.md`, written without opening any per-net array;
`EXCESS_GAIN_MOMENTS_DATA_20260819.md`, written without opening any theory or core
document). This file confronts the two, re-derives both lanes' load-bearing numbers from
scratch, and states the surviving hypothesis at its earned level.

> **Licence / use constraint.** The arm reports are burned-Public100 DESCRIPTIVE data,
> licensed for science reads only. Nothing in this file is a designation, a promotion, or
> an eligibility claim. Oracle and gating figures in §5 are descriptive ceilings on burned
> data, not claimable scores.

**Evidence tags.** `[O]` observed — computed or read this session by this lane. `[D]`
derived — algebra from `[O]` items, shown or named. `[R]` reported — another document
says so. `[A]` assumed — named modelling choice. Tooling: Python 3.14 + numpy,
`python -B -P`, `PYTHONDONTWRITEBYTECODE=1`, clean scratch dir, zero billed compute.
Scripts: `verify1.py`, `verify1b.py`, `verify2.py` (scratchpad; inventory in §7).

---

## 0. Verdict

**Both lanes verify, and their headline results are one result seen in two coordinate
systems — after one correction each.** The excess gain (2.83 / 3.44 quoted SE) is a
**first-moment, arm-A-located forecast miss**, exactly two two-parameter physical
completions of which survive (§3); it is **not** a higher-moment effect, not tail
deletion, not sampling luck, and not an estimand ambiguity that dissolves it. Every
per-net "tail" signature in the data lane — the rank correlations, the decile
concentration, the weighting wedge, the worse-net count — is reproduced within 0.7σ by a
no-mechanism lognormal pairing null fitted to the measured log second moments `[O, §2.2]`.
Kurtosis lives where the theory lane put it: in the instrument layer (effective df 35 /
44 / 7 on the three legs), never in the point estimate. Two open provenance items are
closed this session with bit-exact reproductions: `se_log = 0.0705` is the runner's
score_flop-channel bootstrap, and `v126k` is a first-principles arc-cosine-kernel value
that predates this cell — the circularity attack on arm C's −0.15% agreement is dead.

The corrections: the data lane's §6b reading ("the forecast lands on the unweighted
mean") is a **magnitude coincidence**, not an estimand identity, once v126k's provenance
and the rotation lottery are priced (§2.3). The theory lane's §2.3 "structural
falsification" of the model shape is **point-exact but inference-soft**: z = 1.29 against
the ceiling on a leg with 7 effective degrees of freedom, one-sided p ≈ 0.12 (§1.2).

---

## 1. Verification ledger

### 1.1 Data lane — re-derived from the raw arrays with independent code

All figures below were recomputed by `verify1.py` from `report_arm{A,B,C}.json` alone —
fresh implementations of every estimator (moments, L-moments, paired-delta SE, Spearman
via double argsort, jackknife, trimmed means; no scipy). **Every checked figure matches
the data lane to the printed digit.** `[O]`

| figure | data lane | this lane | match |
|---|---|---|---|
| ratio-of-means A→B / A→C | 0.6661955563966138 / 0.6563696466865464 | same | **bit-exact** |
| mean-of-ratios A→B / A→C (SE) | 0.8138081942 / 0.8189592728 (0.051423) | same | 10 digits |
| weighting term Cov(a,r)/mean(a) | −0.1476126378 / −0.1625896261 | same, residual 0.0 / 2.5e-16 | 10 digits |
| median / geo / trim10 / trim20 of r (A→C) | 0.6637200124 / 0.6907029498 / 0.7462627292 / 0.7160035635 | same | 10 digits |
| paired-delta se_log B/A, C/A, C/B | 0.073837 / 0.073146 / 0.029255 | same | 6 digits |
| z against rounded forecasts | 2.833053 / 3.445451 | same | 6 digits |
| raw g1, g2 — A / B / C | 1.47644, 1.43933 / 2.16141, 6.20639 / 1.80669, 3.51923 | same | 5 digits |
| log sd — A / B / C | 0.698065 / 0.657778 / 0.624589 | same | 6 digits |
| log g2 — A / B / C | −0.71106 / −0.45102 / −0.45045 | same | 5 digits |
| log-ratio C/A g1, g2; τ3, τ4 | −0.00404, −0.14747; −0.00472, +0.12509 | same (sign conv. per direction) | 5 digits |
| influence-function γ2; eff. df | 3.69238 / 2.59531 / 26.39568; 35.13 / 43.52 / 7.04 | same | 5 digits |
| Spearman rel-gain vs arm-A MSE | +0.519292 / +0.469043 | same | 6 digits |
| OLS slope d log r / d log A | −0.454644 / −0.413164 / −0.041480 | same | 6 digits |
| top-decile gain share / arm-A share | 47.834% / 28.059% (quartile 83.826 / 54.237) | 47.8343 / 28.0585 / 83.8259 | 4–5 digits |
| nets made worse; worst regression | 29, 25; 3.048932 / 3.048652 | same | exact / 6 digits |
| mean/median absolute gain | 1.72177 / 1.89608 | 1.721765 / 1.896083 | 5 digits |
| jackknife LOO ranges (all three ratios) | [0.645058, 0.681708] etc.; russell-cox Δ −0.021138 | same | 6 digits |
| log Pearson A–B / A–C / B–C | 0.622777 / 0.609510 / 0.966672 | same | 6 digits |
| L-moments (A raw τ3, τ4) | +0.37514, +0.16386 | same | 5 digits |

Well beyond the six required. The data lane's blind computation is **verified**.

### 1.2 Theory lane — both load-bearing derivations re-checked

**(a) The ensemble-variance law** `E[A_l] = (P_l(1) + (d−1)P_l(0))/(dm)`,
`Var(A_l)/E[A_l]² = 2(m−1)/(m·h_l)` — confirmed by my own Monte Carlo (own QR-Haar
sampler, own vectorized Gegenbauer recurrence, seed 20260819, disjoint from the theory
lane's four validation points in implementation and seed) `[O, verify2.py]`:

| (d, l, m) | reps | mean rel. err vs closed form | empirical CV² / theory |
|---|---|---|---|
| (8, 4, 3) | 20,000 | +8.1e-4 | 1.0121 |
| (16, 4, 4) | 6,000 | −8.5e-5 | 0.9947 |
| (8, 6, 2) | 20,000 | +3.1e-5 | 1.0135 |

The law holds; the theory's conclusion that the realized Haar defect is deterministic to
1e-4 at (d=256, l=4, m=126) — h₄ = 1.83e8 in the denominator — stands. `[D+O]`

**(b) The kurtosis-corrected SE of the plug-in σ̂**: `E[s]/σ − 1 ≈ −(κ−1)/(8n)`,
`sd(s)/σ ≈ ½√((κ−1)/n)`. Delta-method derivation re-done and MC-checked on Gamma shapes
with exact κ `[O]`:

| κ, n | MC bias / formula | MC sd / formula | regime |
|---|---|---|---|
| 5.29, 100 | −0.0050 / −0.0054 | 0.1027 / 0.1036 | valid (n ≈ 19κ) |
| 5.29, 5 | −0.0894 / −0.1074 | 0.4154 / 0.4634 | edge; formula overstates ~16% |
| 50, 100 | −0.0495 / −0.0612 | 0.3122 / 0.3500 | edge (n = 2κ); overstates ~19% |
| 50, 1000 | −0.0058 / −0.0061 | 0.1088 / 0.1107 | valid again |

The formula and its `n ≫ κ` validity claim are both confirmed — including the theory's
own caveat: at (κ = 50, n = 100) the asymptotic form overstates the bias by ~19%.
**Correction that follows:** inverting the judge's 6.2% bias with the MC-true map gives
κ ≈ 60–65 rather than 50.6. Order and direction unchanged; quote "κ ≈ 50–65, under the
stated identification". `[D+O]`

**(c) The defect/forecast pipeline**, reproduced from my own exact-`Fraction` code (not a
re-run of the runner): A₄ Haar-126 = 3.136387499227966e-05, Kerdock-126 =
7.350908201315546e-07, ratio exactly 128/3; A₄ MUB-129 exactly 0; max_l A_l^B/A_l^C
exactly 2816/2881; forecast ratios **bit-exact**: A→C 0.8444606810318669, A→B
0.8211759295306633, C→B 0.9724264823404788. Arm misses 1.2845920915 / 1.0421512765 /
0.9984683434; log decomposition −0.251974 = (−0.001533 arm C) + (−0.250441 arm A), arm-A
share 99.392%. Implied share4: A→C 0.012641 (2.811×), A→B 0.010883 (2.420×),
disagreement 14.94% of their mean. All theory figures reproduced. `[O]`

**Where the hostile pass landed on the theory lane:** §2.3's "structural falsification
and it does not depend on any energy estimate" is exact about the *point estimates* —
measured C→B = 1.0149700855 against a share-independent ceiling 0.9774383894, factor
1.0384 — but the measured leg carries `se_log = 0.029255` with an influence-function
excess kurtosis of 26.4 (effective df 7.04). z = 1.288 against the ceiling, 1.464 against
the committed-share forecast; one-sided p(T₇) ≈ 0.12 / 0.09; and the data lane's LOO shows
the most favourable single-net deletion still leaves B/C = 0.9938 above the ceiling, so
no single net rescues the model — but one cell at ~1.3σ is **suggestive, not a
falsification**. The claim is demoted to: *a non-quadrature term of point size ≥ 3.84% of
arm C's MSE, supported at p ≈ 0.1, mechanism candidate named (frame-0 pilot), one cell.*
`[D+O]`

### 1.3 Instrument provenance — all three se_log families closed, bit-exact

The brief quoted 2.83 / 3.44 "raw-leg SE" beside `se_log = 0.0705`; the data lane proved
the two are arithmetically incompatible and flagged 0.0705 as unexplained. **Closed:**
re-running the runner's exact bootstrap (`numpy default_rng(20260818)`, 20,000 draws,
one shared index array) on the **score_flop channel** — `mse × max(0.1, flops/272e9)`,
per-net flops from the same reports — returns `[O, verify1.py]`:

| quantity | value | identity |
|---|---|---|
| score_flop bootstrap se_log B/A | **0.07054498655771349** | = the recorded "achieved se_log", **all 17 digits** |
| raw-MSE bootstrap, same seed, B/A | 0.073892 | = the draft's "se_log 0.073892 (A→B)" |
| raw-MSE bootstrap, same seed, C/A | 0.073272 | = the draft's "0.073272 (A→C)" |
| paired-delta (first order) B/A, C/A | 0.073837 / 0.073146 | = the values behind 2.83 / 3.44 |

So: **0.0705 is the gated score_flop instrument (a different estimand — flop-adjusted
score, whose A→B ratio is 0.68166, not 0.66620); the 2.83/3.44 z-values are raw-MSE
paired-delta.** The brief conflated two channels of one runner. No estimator was wrong;
data-lane open item 1 and theory-lane open item (iv)'s neighbour are closed. `[O]`

### 1.4 `v126k` provenance — the circularity attack is dead

`PHASE1_WRITEUP_DRAFT_20260808.md` (§ around line 522) `[O, read this session]`: for a
bias-free He-initialised ReLU network the rotation-averaged two-point function is the
iterated arc-cosine kernel `K(c) = (E‖X‖²/d)·κ^32(c)`; the decomposition `Σ_l ‖f_l‖² A_l`
then **predicts** `V126 = 2.4977e-7` and puts the degree-4 share at 0.4497%. That is a
**first-principles value committed 2026-08-08, eleven days before this cell ran**, and it
was validated then against a measured *geomean* of 2.6697e-7 over sixteen fresh networks
("predictable from first principles to 6.4%"). Consequences:

- Theory §2.4's strongest self-attack (v126k fitted to this pipeline → arm C's −0.15%
  circular) is **refuted by provenance**. Arm C's agreement is a real prediction coming
  true. `[O]`
- The kernel's estimand is the ensemble **arithmetic** mean (it is an expectation over
  He weight draws and rotations), which fixes which average the forecast should be
  compared to — see §2.3. `[D]`
- A caveat travels with the 6.4%: that validation compared an arithmetic-mean prediction
  to a **geomean** measurement; at the measured log-variance (~0.39) those two estimands
  differ by ~20%. The kernel's absolute calibration was never held to better than a few
  tens of percent, and its share4 = 0.45% was never separately validated — the writeup's
  own two degree-4 measurements (+0.176%, CI [0.970, 1.028]; +0.42%, no CI quoted) have
  ±1.5–3% noise and cannot distinguish 0.45% from the 1.1–1.3% this cell demands. `[D+R]`

---

## 2. THE CONFRONTATION

### 2.1 Pre-registered signatures vs blind measurements

Theory §6 predictions were written before any per-net array was opened; data-lane values
were computed without reading the theory. Column "fitted null" is my no-mechanism
lognormal pairing null (§2.2), which neither lane had.

| sig | theory's pre-registered prediction (verbatim gist) | blind measurement | fitted null (mean ± sd, 95%) | verdict |
|---|---|---|---|---|
| **S1** | Spearman ρ(gain, MSE_A) = +0.65 ± 0.08, band [0.57, 0.71] — "the NULL, not the signature"; informative only > +0.75; < +0.45 falsifies §4 | **+0.519292** (A→C rel.), +0.469043 (A→B) `[O both lanes]` | +0.508 ± 0.078 [0.344, 0.654] | **HELD as null.** Pre-reg band missed low 1.6σ (pool-parameterized); the measured-parameter null is dead centre (0.14σ). Deletion criterion (>0.75) not fired; §4-falsifier (<0.45) not fired. Landed in the pre-registration's unclassified [0.45, 0.55) gray zone — a bookkeeping gap, noted. |
| **S2a** | mean-of-ratios gain **negative** (−0.032), 37 pts below median-of-ratios (+0.344) | **+0.181041**, 15.5 pts below median-of-ratios gain +0.336280 `[O]` | MoR 0.814 ± 0.050 (gain +0.19) | **Direction HELD** (mean far below median; the brief's "mean > median" is indeed backwards under this reading). **Point FAILED ~4.1σ**: the pool-transfer `E[1/F] = ν/(ν−2) = 1.573` overstates the deployed Jensen factor, measured 1.24 (§2.3). |
| **S2b** (diagnostic) | aggregate minus median-of-ratios gain: **2 ± 3 pts**; 8.66 pts = full-deletion ceiling | **0.735 pts** (A→C), 1.300 pts (A→B) `[O]` | 3.31 ± 3.90 [−4.3, +11.2] | **HELD, at the no-deletion end.** The cleanest deletion detector in the set came back empty. |
| **S3** | top-decile share of aggregate gain 30–40%; diagnostic = arm-A minus arm-C top-decile MSE shares, **≤ 5 pts**; > 10 pts "would be genuine evidence for tail deletion" | share of gain **47.834%**; shares of own totals: arm A 28.059%, arm C 17.705% → **diff 10.353 pts** `[O]` | share 45.1 ± 7.5% [31.0, 60.1]; diff 8.99 ± 3.12 [2.87, 15.05] | **Bands FAILED; no mechanism evidence.** Both measurements sit within 0.7σ of the *fitted* null — the pre-registered thresholds (χ²_5.49-based) were mis-calibrated, and the "≥10 pts ⇒ deletion" line is itself generated by the null at its median+0.4σ. |
| **S4** (sharpest) | skew_A/skew_C ∈ [0.9, 1.3]; kurt_A/kurt_C ∈ [0.9, 1.4]; both arms near skew 1.6, κ ≈ 50; ratio > 2 overturns the document | skew ratio **0.817**; kurt ratio **0.681** (full) / 0.409 (excess); levels: full κ = 4.44 (A), 6.52 (C), 9.21 (B) `[O]` | kurt ratio (full) 1.50 ± 1.26 [0.30, 5.10] | **Bands FAILED low; overturn criterion NOT fired** (0.68 ≪ 2, and in the opposite direction: the *treated* arms are the heavier-tailed ones). Level prediction κ ≈ 50 failed ~10× — it belonged to the production channel inversion, not this cell. The null band shows the test was un-powered at n = 100: kurtosis ratios cannot carry a signature here at all. |
| **S5** | skew of the bootstrap log-ratio **+0.00 ± 0.07**; > +0.15 is the cleanest tail-deletion evidence | **+0.0452** (C/A), +0.0463 (B/A) — my own 200k paired bootstrap `[O]` | ≈ γ1(u)/√n ≈ −0.006 – +0.03 | **HELD.** No deletion signal from the second clean detector either. |
| **S6** | arm-A per-net measured/forecast: median ∈ [1.15, 1.35], positive on > 70% of nets; "< 15 nets ⇒ tail after all" | C-anchored proxy (forecast_A,i := c_i / 0.844461): median **1.2723**, positive on **63%** `[O]` | — | **Substantially HELD** (location shift confirmed; the miss is not a 15-net tail at ratio level). The >70% sub-claim missed narrowly — 29 degraded nets pull it down. Caveat: absolute-discrepancy concentration (top 6 nets = 50% of Σ(fc·a−c)) is a mechanical weight effect (4 of those 6 are top-6 by arm-A MSE, holding 18.6% of ΣA); the proxy is not a per-net energy forecast. |
| **S7** | arm A classifies strictly more neurons dead-and-unrescued (pilot mechanism, sign derived, magnitude unknown) | **UNTESTABLE from these files** — per_mlp schema carries mse/flops/timing only, no rescue diagnostics `[O, schema read]` | — | **OPEN.** Named probe in §4. |

**Scorecard.** The two purpose-built deletion detectors (S2b, S5) both returned null.
The four band misses (S1, S2a, S3, S4) all trace to one cause: the theory parameterized
its nulls from the P2 rotation-pool transfer (CV 0.603, ν 5.49) rather than the deployed
per-arm dispersions — which it itself flagged as `[A]` and estimated to be ~20% lighter.
With measured parameters, every signature lands within 0.7σ of the no-mechanism null.
**Nothing in the per-net data moves toward tail deletion**; S7 remains the only untested
signature.

### 2.2 The fitted null that closes the tail story

`verify1.py` fits the minimal shared-factor model to the measured log second moments
`[O]`: `ln a = μ_A + D + F_A`, `ln c = μ_C + D + F_C`, `ln b = μ_B + D + F_B`, Gaussian,
with σ_D = 0.5252 (from the two A-leg covariances, 0.2860/0.2657 averaged), σ_FA =
0.4598, σ_FB = 0.3960, σ_FC = 0.3380, corr(F_B, F_C) = 0.906. **Zero composition effect,
zero deletion, zero degree structure** — pairing statistics only. 4,000 replicates of
n = 100 reproduce, within 0.7σ each: Spearman (0.508 vs measured 0.519), top-decile gain
share (45.1% vs 47.8%), S3 difference (9.0 vs 10.4 pts), the weighting wedge (−0.153 vs
−0.163), mean-of-ratios (0.814 vs 0.819), worse-count (25.9 vs 29), mean/median absolute
gain (1.63 vs 1.72), and the log-log slope (−0.433 vs −0.455). Closed-form checks of the
same null: RoM/MoR = e^(−σ_FA²) = 0.8094 vs measured 0.8015; MoR/geo = e^((σ_FA²+σ_FC²)/2)
= 1.1769 vs measured 1.1857. `[D+O]`

Two honest limits `[A]`: log-normality (the measured log space is slightly *lighter*-
tailed, g2 ≈ −0.45 to −0.71, so the null if anything over-produces tail concentration —
conservative in the direction that matters); and unit difficulty loading in all three
arms with σ_D² identified as the average of two covariances that differ by 7%.

What the fit *does* measure, beyond the null test: **arm C's conditional dispersion is
26% lighter than arm A's** (σ_FC = 0.338 vs σ_FA = 0.460), arm B's 14% lighter, and the
two treated arms' idiosyncratic terms correlate at 0.906 — B and C are one intervention
sampled twice, and the intervention shrinks the per-net lottery as well as the mean. By
the theory's own theorem (`E[F] = 1`), this lightening moves the scored ratio-of-means by
**zero**; it is real, and it is score-invisible. `[D]`

### 2.3 Cross-lane confrontation: one gap, two coordinate systems, one correction each

The two headlines are algebraically the same fact. Exact bridge `[D]`, all terms
measured:

```
ln(measured/forecast RoM, A→C) = −0.251974
  data-lane coordinates:   −0.030675 (forecast vs mean-of-ratios)  + −0.221299 (weighting term)
  theory coordinates:      −0.001533 (arm C's own miss)            + −0.250441 (arm A's own miss)
  bridge:  arm-A miss  =  weighting term + (forecast-vs-MoR gap − arm-C miss)
           0.250441    =  0.221299      + (0.030675 − 0.001533)          ✓ exact
```

**The correction to the data lane's §6b.** "The forecast lands on the unweighted mean
(z = +0.14, +0.50)" is arithmetically right and interpretively wrong, on two `[O]` facts
neither lane had together: (i) v126k's kernel provenance fixes the forecast's estimand as
the pooled arithmetic mean (§1.4), so the model *should* be compared to the
ratio-of-means, where it misses by the full gap; and (ii) the S1 rotation panel `[R]`
plus the fitted σ_FA say each net's realized ratio r_i is a lottery draw around its
physical ratio ρ_i, with denominator noise inflating `E[r_i] = ρ_i·E[1/L_A] ≈ ρ_i × 1.235`
(lognormal, e^(σ_FA²) = 1.2355) `[D]`. Correcting the mean-of-ratios for that Jensen
inflation puts the physical per-net mean ratio at 0.8190/1.2355 = **0.6629** — within
1.0 log-point of the pooled 0.6564. The composition tilt (hard nets *physically* gaining
more) is ≈ −1.0 log-point of the −22.1-point wedge; the other −21 points are arm-A
lottery noise regressing to the mean. So the forecast (0.8445) misses the physical
per-net ratio (≈ 0.663) by +24.2 log-points, and its +2.55-point agreement with the
measured mean-of-ratios is **two unrelated ~22–25-point effects cancelling**: the
kernel's arm-A under-prediction against the Jensen inflation of a noisy-denominator
statistic. The data lane hedged exactly here (§7.5, "which estimand is correct is a
design question") — the hedge was the right instinct, and this closes it.

The alternative reading — per-net ratios deterministic, dispersion all cross-net, the
wedge a real composition effect — is not excluded by any second moment in this cell (the
two parameterizations are observationally equivalent on one seed `[D]`). It is disfavored
by the S1 panel's direct 16-rotation measurement (within-net rotation CV ≈ 0.60 `[R]`),
and the two readings are cleanly separated by the rotation-offset probe in §4.3.

**What survives of each lane.** Theory: the 99.39% arm-A attribution (exact arithmetic,
provenance-hardened by §1.4), all four theorems, the deletion refutation, the instrument
analysis. Data: the exact identity, every measured number (§1.1), the estimator-spread
warning (the five "ratios" span 0.163 — larger than the gap), and the effective-df
result. What falls: the theory's pool-parameterized signature bands (§2.1) and the
data lane's §6b estimand identification.

---

## 3. H-MOMENT — the surviving hypothesis, at its earned level

**Statement.** The excess gain of the structured arms over the harmonic forecast on
burned-Public100 is a **first-moment, arm-A-located mis-forecast**, of which exactly two
two-parameter physical completions survive all three measured legs `[D, verify2.py; both
close the A→C, A→B, C→B system to residual +0.0000 by construction of two dof against
three constrained legs — the chain closure is the consistency content]`:

- **Repair I — spectral.** The He-kernel's degree-4 energy share is under-counted ~2.8×
  (committed 0.4497% → demanded 1.264% on the A→C leg), amplified onto the Haar arm by
  the exact 128/3 defect leverage (A₄ ratio), **plus** a +5.24% multiplicative
  non-quadrature penalty specific to arm B. Under this repair the C→B reversal is fully
  explained (0.9645 × 1.0524 = 1.0150 = measured, residual 0.0000).
- **Repair II — estimator (the theory lane's §2.5).** Shares as committed; arm A carries
  a +28.66% non-quadrature penalty (the pilot/dead-neuron-rescue channel running on a
  Haar carrier: the rescue reads the first frame's rows, a flat ± Hadamard probe detects
  firing at up to ‖w‖₁/‖w‖₂ ≈ 16× the resolution of a Haar probe), **plus** +4.37% on
  arm B (frame-0 = the unphased all-plus Walsh row `[O, theory's asset read]`). Same C→B
  closure.

The three aggregates cannot distinguish I from II (the share system is near-singular:
det −1.6e-05, cond 8.7e18 `[D, reproduced]`; the two legs' implied share4 disagree by
14.94%, so neither repair is pure). Both repairs require a **~4–5% arm-B penalty** — the
C→B reversal is the one leg neither spectral nor Haar-side stories touch, and the frame-0
pilot hazard is its only named candidate. Earned level: the *location* of the miss (arm A,
+28.46%, a cross-net location shift, S6) is `[D]` on exact arithmetic with provenance-
hardened calibration; the *mechanism split* between I and II is **hypothesis**, with the
discriminating checks named in §4.

**What the excess gain is NOT** — each with its evidence:

1. **Not ensemble-tail deletion.** Mechanically impossible (shared rotation seed, k = 1,
   `E[F] = 1` moves a ratio of means by 0 — theorem `[D]`); and empirically absent: both
   purpose-built detectors null (S2b: 0.74 pts vs 8.66 ceiling; S5: +0.045 vs +0.15
   threshold) `[O]`.
2. **Not any per-net "tail" or conditioning mechanism.** All eight tail signatures inside
   0.7σ of the fitted no-mechanism pairing null (§2.2) `[O]`. The "badly-conditioned nets
   gain more" reading is, to −1 log-point, regression to the mean against a noisy arm A.
3. **Not cross-degree covariance.** Exactly zero in the mean by Schur (theorem,
   re-checked in form; it moves variance only) `[D]`.
4. **Not a kurtosis or higher-moment correction to the instrument.** Kurtosis enters
   Var(log x̄) at O(n⁻³): +0.004% to +0.016% at n = 100, vs the −4.5% that 0.0705 would
   have needed — and 0.0705 is a different channel anyway (§1.3) `[O]`.
5. **Not sampling luck.** For the gap to be a 1-SE event, se_log would need to be 0.252
   against a jackknife-bounded 0.073 ± 0.008; even the tail-inflated simulated p ≈ 5e-3
   rejects `[R, theory §5.4, spot-consistent with my eff-df numbers]`.
6. **Not the radial-conditioning floor** (common additive floor moves the ratio the wrong
   way, +33.9% over-prediction of arm C if fitted to arm A) `[R, theory §2.4, arithmetic
   checked]`.
7. **Not truncation** (degrees ≥ 12 carrier-neutral; including them widens the gap)
   `[R, theory §1.3, mechanism checked at l = 4–8 in my own Fraction code]`.

**Where kurtosis actually lives — the answer to the owner's framing** ("moments about the
mean … we are looking at the Kurtosis — what about the other elements and the inference
between them"): the fourth moment governs **the inference layer, at two removes from the
score**. (i) The precision of the SE itself: effective df 2n/(γ₂+2) = 35.1 / 43.5 / 7.0
on the three legs, so every quoted σ carries ±11% (A-legs) to ±27% (C/B) — "2.83σ" is
2.83 ± 0.31σ. (ii) The plug-in σ̂ at small n: the (κ−1)/(8n) bias law (verified, with its
validity edge quantified in §1.2b) is why the m129 smoke's five-net instrument was not an
estimate of anything and why the honour-window breach was an instrument event, not a
physics event. (iii) Berry–Esseen at n = 100 caps what any normal tail probability means
on this channel — the 2.83/3.44 are distances, not p-values `[R, checked in form]`. The
"inference between the elements" that moves the *point estimate* is a first-moment
covariance — and §2.2/§2.3 show it is mostly the pairing statistics of arm A's own
lottery, with ≈ −1 log-point of genuine composition.

---

## 4. Cheapest next falsifiers, ranked

**4.0 — Done this session, zero compute:** v126k provenance (§1.4 — circularity dead);
se_log 0.0705 provenance (§1.3 — channel identified, bit-exact). Two of the theory
lane's five open items closed; a third (the judge's 6.2% definition) is bounded by
§1.2b's refinement (κ ≈ 50–65 under the stated identification).

**4.1 — S7 instrumented probe (hours, local CPU, no harness authorization, no scored
row).** Copy the three estimators to scratch, add a counter at the rescue test
(`base_estimator.py` line 160, `max(pilot_pre) > 0`), run all three arms on ~10
Public100 nets spanning the arm-A MSE range, log per-net dead-and-unrescued counts.
Custody: descriptive diagnostics on burned nets; no designation surface. **Decision
rule:** arm A strictly greater on ≥ 8/10 nets confirms the Repair-II sign; counts equal
kills the pilot channel and leaves Repair I carrying the A-leg alone (with the fitted-λ
channel as the residual candidate). This is the single highest-information hour available.

**4.2 — Rotation-offset probe (settles lottery vs composition; needs an owner custody
ruling).** Re-run arms A and C on the same 100 nets with `_haar_rotation(int(mlp.seed) +
K, width)`, K ≠ 0 — new rotation draw, same nets, same physics. If per-net r_i
decorrelates against the original run (predicted under the lottery reading: corr ≈
σ_ρ²/(σ_ρ²+σ_lottery²) ≈ 0.05–0.15), the Jensen re-reading of §2.3 is confirmed
measured; if r_i reproduces, the composition reading wins and §6b's identification is
rehabilitated. Zero billed compute, but it executes estimators on burned nets — filed
as requiring the owner's reading of the custody clause before running.

**4.3 — Fresh-seed micro-cell (the designation-relevant falsifier; sketch).** n = 32
fresh nets (seed family disjoint from 0 and 424242), five arms, one authorization-class
run: **A** (Haar-126, as shipped), **A′** (Haar-126 with a phased-Hadamard frame at
index 0, so the pilot is the flat ± probe — the only change is which frame the pilot
reads), **C** (Kerdock-126), **B** (MUB-129 as run), **B′** (MUB-129 with frame order
rotated so index 0 is a phased row, not the all-plus Walsh row). Pre-registered
predictions, filed here before any such run exists:

| # | prediction | discriminates |
|---|---|---|
| P1 | A′/A ratio-of-means ∈ [0.72, 0.85] under Repair II; ∈ [0.97, 1.03] under Repair I | the mechanism split of §3 |
| P2 | B′/B ≤ 0.96 if the frame-0 hazard is real; ∈ [0.98, 1.02] otherwise | the C→B reversal's candidate |
| P3 | C/A ∈ [0.56, 0.76] (the excess reproduces on fresh seeds; it is physics or estimator, not luck) | H-MOMENT vs sampling-fluke residual |
| P4 | mean-of-ratios / ratio-of-means ∈ [1.15, 1.35] (the Jensen/RTM wedge re-appears with fresh nets) | §2.3's reading |
| P5 | paired se_log ≈ 0.073·√(100/32) ≈ 0.13 — margins in P1–P3 are sized to be ≥ 2σ decisions at n = 32 | instrument honesty |

If B′ confirms P2, the completion leg flips sign: C→B′ ≈ 0.965–0.972 (the quadrature
forecast), i.e. **completing to 129 pays ~+3% once the pilot hazard is removed** —
reversing this cell's H2-adjacent conclusion that completion is a small net loss. That
is the concrete accuracy content hiding in this analysis.

---

## 5. The campaign's two tracks

### 5.1 Contribution manuscript — a results-subsection candidate

Title candidate: *"The excess gain decomposed: a pre-registered two-lane confrontation."*
Contents, all measured: (1) the blind theory/data pair and this confrontation table —
the adversarial-collaboration structure is itself a methods contribution; (2) the exact
bridge identity (§2.3) between the weighting decomposition and the per-arm attribution;
(3) the fitted-null result — **every per-net tail signature of a paired benchmark is
reproducible by lognormal pairing statistics with zero mechanism**, a warning with reach
beyond this campaign (mean-of-ratios vs ratio-of-means on paired heavy-tailed data);
(4) the two-parameter repair pair with the near-singular share system, stating honestly
that three aggregates cannot separate them; (5) the C→B non-quadrature term at its
demoted level (point ≥ 3.84%, p ≈ 0.1, candidate named); (6) instrument doctrine:
per-channel se provenance (§1.3), effective df, distances-not-p-values. Fits the draft as
a §13-adjacent subsection; every number in it is already two-signal.

### 5.2 Accuracy runway to Oct 16 — unclaimed MSE, honestly bounded

| lever | size (this cell, descriptive) | earned level | cost to claim |
|---|---|---|---|
| **B′ pilot re-phase** (frame-0 hazard) | +4.4–5.2% on the B-family; would flip the completion leg from −1.5% to ≈ +3% | hypothesis with sign `[D]`, magnitude from both repairs' B-penalty; unconfirmed | 4.1 probe (hours), then the 4.3 cell |
| **Per-net A/C gating** (oracle ceiling) | pooled ratio 0.6564 → 0.5826 (min(A,C), 7.37 pts) or 0.5563 (min(A,B,C), 10.00 pts) | oracle on burned data `[O]`; **not claimable** — needs a legal pilot-based selector that wins on ~29 regressed nets | selector design + fresh cell; realizable slice unknown, plausibly small |
| **The 2.83/3.44-SE excess itself** | **zero new MSE** — it is already in the score; both repairs say it re-appears on fresh seeds (P3) | `[D]` | none; do not spend runway re-claiming it |
| **share4 re-fit** | zero direct MSE; corrects forecasts and any future design choice priced off share4 (e.g. degree-4-exactness trades) | demanded 2.4–2.8× `[D]`; not separable from Repair II by these arms | falls out of 4.1 + 4.3 |
| **Conditional-lottery lightening** (σ_FC 26% below σ_FA) | zero on the scored mean (`E[F] = 1`), real on dispersion/CI width | `[D+O]` | none; report, don't chase |

Net: the runway's one genuinely new accuracy lever from this investigation is the **B′
re-phase (~3–5% on the completion family, unconfirmed)**; everything else is either
already banked, an oracle ceiling, or forecast hygiene. This is consistent with the
channel's 13:07 entry: the "unexplained excess accuracy physics in leaving the Haar
family" is now explained to two candidate mechanisms with a named discriminator — and
most of its headline magnitude was never available to claim twice.

---

## 6. Attack on this synthesis

**Strongest way this is wrong:** the Jensen re-reading (§2.3) leans on σ_FA from a
three-moment decomposition whose difficulty-loading assumption is untestable in one cell,
and on the S1 panel's rotation CV transferring to the deployed arm. If the true within-net
lottery is much smaller, the composition reading revives and §6b's identification with it.
I priced this: the two readings differ by a measured, cheap experiment (4.2), and nothing
upstream of §2.3 — the verification ledger, the null-reproduction of the signatures, the
provenance closures, the repair pair — depends on which one wins. **Tested the specific
way it would fail:** the closed-form lognormal checks (RoM/MoR, MoR/geo) agree with the
fitted null to 1.0% and 0.75% — if the lottery were absent those identities would have no
reason to hold; they could have failed and did not.

**Second:** my fitted null is Gaussian-in-log `[A]` while the measured log space is
lighter-tailed; a null with the measured L-moments would concentrate slightly *less*, so
the "signatures within 0.7σ" margins would widen, not shrink — the conservative direction.

**Third:** the S3/S4/S6 verdicts use my operationalizations (own-total decile shares;
C-anchored per-net forecast). Both are stated inline; if the theory lane meant different
statistics, the table's raw ingredients (§1.1) are sufficient to recompute any variant,
and no variant I tried moves a verdict.

**Wobble reported:** the S6 positive-fraction sub-claim (63% vs > 70%) and the S1 gray
zone are genuine small misses of otherwise-held signatures; they are in the table, not
smoothed over.

---

## 7. Custody, constraints, inventory

Zero billed compute: no harness invocation, no estimator execution, no scored row, no
seed consumed; all computation was local numpy on the already-committed reports. Writes
confined to this file, the scratchpad, and (with this commit) the channel entry. Reads:
the three arm reports, the two lane documents, `runner_fc129.py`, the report schema, and
two provenance greps into committed core documents (`PHASE1_WRITEUP_DRAFT_20260808.md`,
`PHASE2_CONTRIBUTION_DRAFT_20260819.md`). The per-net arrays remain descriptive under
burned-Public100 custody; nothing here designates, promotes, or validates.

Scratchpad inventory (session `7c1d8a18`, dir `scratchpad/`): `verify1.py` (arm-report
re-derivations, runner-bootstrap reproduction, fitted null MC, S5 bootstrap, oracle
bounds, exact-Fraction forecast pipeline; JSON dump `verify1_out.json`), `verify1b.py`
(A→B share inversion, T₇ tail probabilities, S6 concentration, Jensen bookkeeping),
`verify2.py` (Haar variance-law MC, κ-SE MC, Var(log x̄) expansion spot check at 1M reps
— naive −0.20%, 2nd-order +0.10%, consistent with the data lane's 4M-rep −0.296%/+0.008%
within joint MC error; two-parameter repair chains). Re-run: `python -B -P <script>` with
`PYTHONDONTWRITEBYTECODE=1` from any clean directory.

*Verifier lane, closing the trio. 2026-08-19.*
