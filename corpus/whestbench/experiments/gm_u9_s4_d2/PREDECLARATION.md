# PREDECLARATION — gm_u9_s4_d2

Graveyard revival item: **gm_u9_s4_d2** (mining key "U9 designation refresh").
Written **before** any harness code was authored. Phase-2 calibration / writeup
science only. Phase-1 selection is frozen and nothing here touches it.

## 0. Deviations declared up front (loud)

1. **`scipy` is absent from the pinned interpreter**
   (`work/whest-v014/Scripts/python.exe`, Python 3.14.4, numpy 2.4.6, no scipy).
   The frozen harness `s4_portfolio/run_s4.py` imports `scipy.special.ndtr`.
   I therefore supply a drop-in `ndtr` that mirrors the Cephes `ndtr` branch
   structure on top of `math.erf` / `math.erfc` (libm), vectorised with
   `np.frompyfunc`. This is the ONLY substitution in the copied harness besides
   the dispersion parameter and the output path.
   *Materiality test (predeclared):* the copula output `U = ndtr(Z)` is consumed
   only through `qmap`, i.e. `floor(U*48)` for the pool marginal and
   `floor(U*2**20)` for the fbar6 marginal. A <=1-ulp difference in `U` changes an
   index only if `U` lands within ~1e-16 of a lattice boundary (probability
   ~1e-9 over the whole run). The **control arm reproducing the committed cells
   exactly is the empirical proof** that the substitution is immaterial; if the
   control does not reproduce, this is reported as a hard deviation and the run
   is declared INCONCLUSIVE rather than quoted.
2. **Precision extension (predeclared, not scope enlargement).** In addition to
   the committed N_SUITES = 100,000 main pass (required for the exact control
   reproduction), the decisive quantity is recomputed at 1,000,000 suites on a
   *different sampling path and a different master seed* (signal 2, section 5).
   No new arms, no new thresholds, no new rho values.
3. The frozen sources `run_s4.py`, `run_s1b.py`, `run_u9.py`, `s4_results.json`,
   `s1b_results.json` are read-only. All writes go to
   `corpus/whestbench/experiments/gm_u9_s4_d2/`.

## 1. What the original record claims

`s4_portfolio/S4_VERDICT.md` (ledger `s4_designation_portfolio_bootstrap`),
certified pass **D2**: "decorrelated 2nd entry ~doubles tail (2.00x at
1.55e-7)". Committed cells (`s4_results.json`, master seed 202608094,
100k suites, 50 nets):

| quantity | committed value |
|---|---|
| P(A < 1.55e-7) (single designation) | 0.02849 |
| P(min(A,B) < 1.55e-7), same_mean, rho_pair=0 | **0.05701** |
| P(min(A,B) < 1.60e-7), same_mean, rho_pair=0 | **0.12373** |
| P(min < 1.55e-7), sens_fold3cap (Door A), rho=0 | **0.87683** |
| P(min < 1.60e-7), sens_fold3cap (Door A), rho=0 | **0.93972** |
| score corr(A,B) at rho_pair=0 | 0.002389 |
| calibration vD | 7.568879454111777e-4 |
| calibration vF | 0.3641995628656461 |
| A's R=1 suite SD | 1.556004718551518e-8 |

Door B union factor as certified: U(1.55e-7) = 0.05701 / 0.02849 = **2.00105**.

## 2. Mechanism under test (from the mining record)

Per-net MSE = S * D_i * F_i; suite score = S * mean_i(D_i F_i) over N=50 nets.
D is **shared** between two entries designated on the same private suite; the
rotation factors F are independent at rho_pair = 0. Hence, exactly:

    Var(score)/S^2 = ( vD + (1+vD) vF ) / N
    Cov(scoreA, scoreB)/S^2 = vD / N
    corr(scoreA, scoreB) | rho_pair=0  =  vD / ( vD + (1+vD) vF )        (Eq. 1)

S1b (`s1b_dispersion_corrected`, bracket-validated against the observed 80-net
15.53x spread) replaces vD = 7.5689e-4 with the two bracketing arms
**vD = 0.08135950765383865** (s17_low) and **vD = 0.12203926148075797**
(s17_high). Under Eq. 1 the two-entry correlation rises from 0.00207 to

    vD=0.0813595 : 0.0813595 / (0.0813595 + 1.0813595*0.3641996) = 0.171215
    vD=0.1220393 : 0.1220393 / (0.1220393 + 1.1220393*0.3641996) = 0.229965

(these equal S1b's committed `difficulty_share_range_R1` = [0.17121, 0.22997]).

Consequence for the union. Writing q(D) = P(score < T | D), conditional
independence of A and B given D gives

    P(min < T) = 2 pA - E[ q(D)^2 ],     U(T) := P(min<T) / pA = 2 - E[q^2]/pA
    Jensen:  E[q^2] >= pA^2   =>   U(T) <= 2 - pA                        (Eq. 2)

so the union factor is bounded above by 2 - pA and is pushed further below that
bound by the shared-difficulty correlation.

## 3. Arithmetic pre-check (step 0a, run before the simulation)

Using S1b's **committed** 50-net single-entry probabilities at T = 1.55e-7
(`s1b_results.json`, `suite_50.p_below["1.55e-07"]`):

| arm | vD | pA (committed S1b) | Eq. 2 bound U <= 2 - pA |
|---|---|---|---|
| old_control | 7.5689e-4 | 0.02939 | 1.97061 |
| s17_low | 0.0813595 | 0.04992 | 1.95008 |
| s17_high | 0.1220393 | 0.06053 | **1.93947** |

Predeclared reading: the bound alone already forbids U >= 1.95 at vD = 0.1220
(1.93947 < 1.95), and sits 8e-5 above 1.95 at vD = 0.0814. This is a *bound*,
not the answer; it uses S1b's integer-index sampling path whose pA differs from
S4's copula path by ~3% relative (control: 0.02939 vs 0.02849). It is recorded
here so the direction of the result cannot be claimed post hoc. It does **not**
by itself decide the gate; the simulated U does.

## 4. Exact falsifier (as mined, unchanged)

Run the committed S4 harness three times, varying **only** the dispersion
parameter (log-uniform difficulty family retained; DIFF_RATIO inverted from the
target vD by the same bisection S1b uses):

* `old_control` : DIFF_RATIO = 1.1  (vD = 7.5689e-4)
* `vd_s17_low`  : vD = 0.08135950765383865 (DIFF_RATIO = 2.7078820324077753)
* `vd_s17_high` : vD = 0.12203926148075797 (DIFF_RATIO = 3.40428993278139)

Everything else identical: MASTER_SEED = 202608094, N_SUITES = 100,000,
N_CHUNKS = 10, N_NETS = 50, ANCHOR = 1.83e-7, RHO_LIST = {0, .3, .6, .9, 1.0},
THRESH = {1.55e-7, 1.6e-7, 1.7e-7}, all four B-arms, the P2 rotation pool
(48 values), the 2^20 fbar6 presample, and the CRN layout.
vD for the two corrected arms is **re-derived in-harness** from
`s17_ibc_floor/s17_results.json` (relative variance of the three per-net
`sigma2_var(ybar)` values, ddof 0 and 1) exactly as `run_s1b.py` does, and
asserted equal to S1b's committed values.

Reported quantities: the Door B union factor
**U(T) = P(min(A,B) < T | rho_pair=0) / P(A < T)** for the `same_mean` arm at
all three thresholds (headline: T = 1.55e-7), the induced two-entry score
correlation, and the same for the `sens_fold3cap` (Door A) arm.

## 5. Gates

**STEP 0 (blocking control gate).** The `old_control` arm must reproduce the
committed cells 0.05701 / 0.12373 / 0.93972 / 0.87683, the baseline
0.02849 / 0.06373 / 0.2063, corr 0.002389, and scoreA_sd 1.556004718551518e-8.
Tolerance: probabilities exactly equal; scoreA mean/SD relative |Δ| <= 1e-12.
If STEP 0 fails, STOP and report the run as INCONCLUSIVE / BLOCKED with the
mismatch verbatim. No corrected-arm number is quoted before STEP 0 passes.

**PRIMARY GATE (verbatim from the mining record's cheapest_falsifier).**
"If the factor stays >= 1.95x at both vD values, the revival is dead and S4's
D2 pass stands as written."

* **KILL_CONFIRMED** (original record stands): U(1.55e-7) >= 1.95 at BOTH
  vD = 0.0814 and vD = 0.1220.
* **REVIVED_PASS** (D2's certified 2.00x does not survive corrected
  dispersion): U(1.55e-7) < 1.95 at at least one of the two vD values.
* **INCONCLUSIVE**: the deciding arm's 95% CI on U straddles 1.95.

Decision is on the point estimate, per the mined text; the 95% CI must lie
wholly on the decided side, otherwise INCONCLUSIVE. CI = chunk-paired (10
chunks of 10k, per-chunk ratio pmin_c / pA_c, mean +- 1.96 SE).

**Secondary (reported, not a gate):** S4's own predeclared gate
(diversification gain P(min<T | rho=0) - P(min<T | rho=1) >= 2 pp in the
same_mean or r6 arm) recomputed at the corrected vD, so the writeup can state
whether S4's SURVIVES verdict itself moves or only its headline multiple.

## 6. Predicted outcome (on record, before running)

1. STEP 0 passes; the ndtr substitution is immaterial.
2. Simulated corr(A,B) at rho_pair=0 matches Eq. 1: 0.1712 / 0.2300 (+-0.002).
3. pA(1.55e-7) rises from 0.02849 to roughly 0.048-0.052 (vD=0.0814) and
   0.058-0.062 (vD=0.1220).
4. **U(1.55e-7) falls from 2.001 to approximately 1.90-1.92 at vD=0.0814 and
   1.86-1.89 at vD=0.1220 — below 1.95 at both.**
   Gaussian working: z = (1.55-1.83)/SD with SD = 1.783e-8 / 1.885e-8 gives
   z = -1.570 / -1.485; Phi2(z,z,rho) with rho from Eq. 1 gives
   E[q^2]/pA ~ 0.10 / 0.13, hence U ~ 1.90 / 1.87.
5. Therefore the predeclared verdict is **REVIVED_PASS**: the certified "2.00x
   doubling" is a number produced by the refuted near-degenerate difficulty
   model and does not survive the corrected dispersion.
6. **Honest limit predicted:** the fall is modest. "Roughly doubles" survives as
   prose (U still ~1.9); what dies is the certified numeral 2.00x and the
   implicit near-independence of two same-suite entries. S4's own 2-pp
   diversification gate is predicted to still PASS at the corrected vD
   (predicted gain at 1.55e-7 ~ 4.5-5.5 pp vs the 2 pp bar), so S4's SURVIVES
   verdict is predicted to be unchanged; only the D2 magnitude claim moves.

## 7. Two-signal verification plan

* **Signal 1** — the copied S4 copula harness (Gaussian copula + inverse-CDF),
  100k suites, seed 202608094.
* **Signal 2** — independent recomputation of U on a **different sampling path**
  (S1-style direct integer indexing of the pool, no copula, no ndtr) with a
  **different master seed** (20260810) and 1,000,000 suites, shared D, F_A and
  F_B drawn independently. Agreement required: |U_1 - U_2| within the combined
  95% MC interval.
* **Signal 3 (analytic)** — simulated corr(A,B) at rho_pair=0 vs the closed form
  vD/(vD+(1+vD)vF) (Eq. 1), and simulated U vs the Jensen bound 2 - pA (Eq. 2),
  which U must not exceed.
* **Signal 4 (bitwise)** — chunk-0 repeat from re-spawned seeds inside every
  arm, plus the rho=1.0 same_mean == A bitwise identity.

## 8. Compute envelope

Committed S4 runtime is 4.0 s at 100k suites. Three arms plus the 1e6-suite
independent path is expected well under 10 minutes on the pinned interpreter,
inside the ~90-minute envelope. No scale-down anticipated.

## 9. Files to be produced

`run_gm_u9_s4_d2.py`, `gm_u9_s4_d2_results.json`, `VERDICT.md`,
this `PREDECLARATION.md` — all in
`corpus/whestbench/experiments/gm_u9_s4_d2/`.
