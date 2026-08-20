# VERDICT — gm_s1s4_vd

**Revival candidate `s1_suite_risk_bootstrap` (with `s1b_dispersion_corrected` and
`s4_designation_portfolio_bootstrap` downstream) is DEAD. S1b's dispersion
correction STANDS, and is now corroborated by a second, independent, cheaper
instrument that the original campaign never used.**

Date 2026-08-10. Predeclared in `PREDECLARATION.md` (written before any code in
this directory ran). Harnesses: `step0_moment.py`, `step1_shape_and_bounds.py`,
`run_s1_gm.py`, `run_s4_gm.py`. Machine-readable: `results.json` plus
`step0_results.json`, `step1_results.json`, `s1_gm_results.json`,
`s4_gm_results.json`, `ndtr_validation.json`.

---

## DEVIATIONS (all declared, none absorbed silently)

* **D1. The mined "definitive settling check" was NOT run.** The record names
  reusing S17's per-net `sigma2_var(ybar)` instrument on 80 nets. Verified this
  session: that instrument reads `s5_kink_concentration/s5_net{101,202,303}_arrays.npz`
  and only 3 such arrays exist. Extending to 80 nets requires 80 fresh He nets,
  a 64,512-point design forward and a 600k-sample truth pass each — outside the
  cheapest falsifier and outside the 90-minute envelope. Recorded as un-run.
* **D2. A replacement second signal was predeclared instead** (gate G5, the
  floor-correlation ceiling). It turned out to be the decisive gate.
* **D3.** S1/S4 were re-run at five vD, not two: the task's 0.081/0.122 plus the
  committed control and the two moment-identity readings.
* **D4.** S1b's exact values 0.0814 / 0.1220 are used where the task says
  0.081 / 0.122.
* **D5 (new, found at run time). The pinned interpreter has no scipy**, and the
  committed `run_s4.py` imports `scipy.special.ndtr`. Rather than change
  interpreters I reimplemented `ndtr` in numpy (Cody CALERF; `ndtr_numpy.py`),
  validated it against the C library `math.erfc` over 300,007 points
  (max relative difference **9.55e-15**, mean 7.96e-17), and required the S4
  control arm to reproduce the committed run. It did, exactly: gains
  0.02852 / 0.06000 / 0.16500 and `scoreA_sd` 1.556004718551518e-08 all match
  `s4_results.json` bit for bit.
* **D6 (verdict mapping).** My predeclared mapping assigns KILL_CONFIRMED only
  if gate **G0** fires. **G0 did not fire.** The kill is delivered instead by
  **G1 FAIL + G5**, both predeclared. I call the item KILL_CONFIRMED on that
  basis and flag the mapping departure here rather than reporting a bland
  INCONCLUSIVE that would hide a decisive result.

---

## 1. The mined arithmetic reproduces EXACTLY

80 nets, 80 distinct `net_seed`, 80 distinct `rot_seed`; the identity
`mse_raw - mse_corr - floor31 = 0` holds to 5.29e-23 absolute (8.18e-17
relative). `vF = 0.364200` from the 48-value P2 pool (identical construction to
`run_s1.py`); pool max/min 11.0732.

| observable | relvar ddof0 | relvar ddof1 | vD = (relvar-vF)/(1+vF) ddof0 | ddof1 | share_D ddof1 |
|---|---|---|---|---|---|
| `mse_raw` | 0.377043 | 0.381816 | **0.009415** | **0.012913** | 3.38% |
| `mse_corr` (floor-subtracted) | 0.554490 | 0.561509 | **0.139489** | **0.144634** | 25.76% |

Observed 80-net max/min: 15.531671 (raw), 35.341683 (floor-subtracted).
`floor31` is 29.55% of `mse_raw` on average (range 9.12%–68.996%) with its own
relative variance 0.281275. Every number the mining record quoted
(0.3770 / 0.3818 / <=0.0129 / 0.5615 / 0.1446 / 0.3642 / 11.07 / 29.6% /
9.1%–69.0% / 0.281 / 15.53) is confirmed to the digit. **The moment identity is
right. Its conclusion is not.**

## 2. G0 — predeclared step-0 kill gate: DID NOT FIRE

Rule: kill iff `vD_moment >= 0.08` under BOTH floor treatments.
`raw = 0.012913` (< 0.08), `corr = 0.144634` (>= 0.08). Not both. Continue.

## 3. G1 — the candidate's own identification claim: **FAIL**

The candidate asserts vD is "six to nine times BELOW S1b's operative
0.081–0.122". On n = 80 nets a relative variance is a wide statistic. Bootstrap
(20,000 resamples, seed 20260810):

| reading | point | bootstrap mean | 95% CI | P(vD >= 0.08) |
|---|---|---|---|---|
| raw ddof0 | 0.009415 | 0.00545 | [-0.06084, **0.07821**] | 0.0223 |
| raw ddof1 | 0.012913 | 0.00890 | [-0.05823, **0.08258**] | 0.0290 |
| corr ddof0 | 0.139489 | 0.13308 | [0.03064, 0.24751] | 0.8318 |
| corr ddof1 | 0.144634 | 0.13814 | [0.03441, 0.25402] | 0.8538 |

G1 required point < 0.08 **and** the bootstrap 95% upper bound < 0.08. The upper
bound is **0.08258 > 0.08**. **G1 FAILS.** The panel's second moment does not
exclude S1b's operative range even on the raw observable that is most favourable
to the candidate.

## 4. G5 — the decisive gate: the panel refutes its own raw reading

`floor31` is the truth-side MC variance of the 600k-sample truth pass. Verified
at source: `run_m185_g0.py` line 342 calls `truth_stats(weights, 7_000_000+seed,
N_TRUTH_S1)` — net seed only; `rot` enters only `predict_once` on line 346. So
`floor31` is **rotation-free**, and for any rotation-free net statistic Z,
`Cov(Z, mse) = Cov(Z, E[mse|net]) = S*Cov(Z,D)`, whence by Cauchy–Schwarz

    share_D  >=  Corr(Z, mse)^2      and      vD  >=  Corr(Z, mse)^2 * relvar_obs.

| observable | Pearson rho(floor31, ·) | Spearman | implied share_D >= | implied **vD >=** | moment point |
|---|---|---|---|---|---|
| `mse_raw` | **0.5157924971295733** | 0.6669010782934834 | 0.2660419000951609 | **0.10157901224992172** | 0.012913 |
| `mse_corr` | 0.330426266963636 | 0.4650961087669949 | 0.1091815 | 0.061306429024019546 | 0.144634 |

Bootstrap on the raw arm (20,000 resamples): lower bound mean 0.1036928185098767,
**95% CI [0.0472284798166269, 0.1762333409407358]**, `P(bound >= 0.08) = 0.7475`,
rho 95% CI [0.36898, 0.66189]. Permutation null (20,000 permutations): null sd
0.11245330530307354, **two-sided p = 0.0** (0 of 20,000 permutations reached
|0.5158|).

The candidate's headline reading (vD = 0.0129, difficulty share 3.4%) is
**arithmetically impossible on its own panel**: 0.0129 lies far below the 2.5th
percentile 0.0472 of what the panel's own rotation-free component forces. The
point bound 0.10158 lands **inside S1b's operative 0.081–0.122** — S1b's replacement
value is independently corroborated by an instrument nobody in the campaign used.
Reported honestly: the point bound also sits above 0.0814, so the strict reading
prefers the upper half of S1b's range; the bootstrap CI does not sharply exclude
0.0814 (P = 0.748).

The committed A1b weights-only Spearman magnitudes (max 0.5627, multivariate
0.5543) are also rotation-free and point the same way; they are rank
correlations, so they are corroborating, not a strict Cauchy–Schwarz bound.

**Why the raw moment reading is small anyway:** `mse_raw = mse_corr + floor31`,
and `floor31` is a *less* dispersed, positively correlated additive component
worth 25.15% of the mean. Adding it *damps* the relative variance of the
observable (0.3818 raw vs 0.5615 floor-subtracted). The moment identity assumes a
purely multiplicative `S*D*F`; the truth floor makes that false, and the raw
reading is the artefact.

## 5. G2 — shape freedom: **PASS** (the candidate's one correct mechanism claim)

Difficulty shape family `log D ~ ExponentialPower(beta)`, scale solved so vD is
held exactly; `beta = inf` reproduces S1's committed log-uniform. 20,000
replicates of the 80-net max/min per cell.

At `vD = 0.012913`: the observed 15.5317 lies inside [P5,P95] for
beta in {1, 1.25, 1.5, 2, 3} (`P(sim>=obs)` 0.085 / 0.077 / 0.070 / 0.062 /
0.052) but NOT for beta in {4, 6, 10, inf} (0.043 / 0.035 / 0.031 / **0.029**).
At `vD = 0.144634`: every beta in the grid brackets it.

So the range statistic is a **shape** statistic, and S1b's identification of vD
from it was shape-driven — exactly as the candidate argued. It just does not
follow that vD is small: the moment reading that would make it small is the one
G5 refutes. Note also that at the raw moment reading S1's own frozen shape still
fails the bracket (P = 0.029), so that reading rescues nothing.

## 6. G3 — corrected S1 gates (100k suites x 50 nets, R in {1,2,4,6}, anchor 1.83e-7)

Control arm reproduces the committed `s1_results.json` **bit for bit**: R=1 SD
1.562588338576902e-08, P(<1.6e-7) 0.06434, width shrink 0.5885287257007297,
rotation share 0.9979276522337025, chunk-0 SHA-256
`2da4b50ee3a797cea3736c46e3be7f8a96f5841f7c734a52120e3baacff5489e`, m185 spread
P50 11.183938237245313 — all rel-diff 0.0.

| arm | vD | D max/min | width shrink R6/R1 (gate 0.25) | mean shift (gate 2%) | rotation share R1 (gate 0.5) | R=1 P5 | R=1 P95 | P(<1.6e-7) | verdict |
|---|---|---|---|---|---|---|---|---|---|
| control | 0.000757 | 1.100 | **0.5885** | +0.021% | 0.99793 | 1.5830e-7 | 2.0973e-7 | 0.06434 | PASS |
| moment raw | 0.012913 | 1.483 | **0.5570** | +0.026% | 0.96618 | 1.5777e-7 | 2.1035e-7 | 0.06911 | PASS |
| **s17_low 0.0814** | 0.081400 | 2.709 | **0.4429** | +0.036% | 0.82872 | 1.5501e-7 | 2.1362e-7 | 0.09303 | PASS |
| **s17_high 0.1220** | 0.122000 | 3.404 | **0.4008** | +0.040% | 0.77009 | 1.5353e-7 | 2.1549e-7 | 0.10621 | PASS |
| moment corr | 0.144634 | 3.806 | **0.3798** | +0.042% | 0.74242 | 1.5276e-7 | 2.1639e-7 | 0.11360 | PASS |

**S1's PASS is robust under every reading** — but that was already true in S1b,
so nothing the candidate promised here is a correction. The candidate's specific
claim that "S1's R=6 SD shrink returns to ~58% (the committed 58.85%)" is
**wrong**: at the raw moment reading the measured shrink is **0.5570**, and
58.85% belongs only to the old vD = 7.57e-4. S1b's analytic 44% / 40% at
0.0814 / 0.1220 is confirmed by bootstrap: **0.4429 / 0.4008** (analytic SD
shrink 0.4438 / 0.4014, ratio to bootstrap within 0.997–1.004 at every R).

The m185 bracket rows inside this harness reproduce S1b's table exactly
(s17_low P5/P50/P95 = 11.64/18.19/25.51, `P(sim>=obs)` 0.720; s17_high
13.19/21.21/31.21, 0.862; control 9.14/11.18/11.94, 0.000), and my *independent*
step-1 simulator (different seeds and different shape machinery) gives
11.74/18.02/25.58 (0.710) and 13.20/21.09/31.18 (0.861) — agreement to MC error.

## 7. G4 — S4 Door-B under corrected dispersion (100k joint suites)

Door-B = two designations of the same estimator differing only in the
participant-owned rotation-seed constant = `rho_pair = 0` with net difficulty
SHARED. Control reproduces the committed `s4_results.json` exactly.

same_mean arm, gain = P(min<T | rho=0) − P(min<T | rho=1), +/- 95% batch CI:

| arm | vD | share_D | realized rho0 score corr | T=1.55e-7 | T=1.60e-7 | T=1.70e-7 | verdict |
|---|---|---|---|---|---|---|---|
| control | 0.000757 | 0.21% | 0.0024 | 2.852 +/- 0.053 pp | 6.000 +/- 0.122 pp | 16.500 +/- 0.221 pp | SURVIVES |
| moment raw | 0.012913 | 3.38% | 0.0349 | 3.159 +/- 0.078 pp | 6.301 +/- 0.126 pp | 16.499 +/- 0.209 pp | SURVIVES |
| **s17_low** | 0.081400 | 17.13% | **0.1736** | 4.478 +/- 0.140 pp | 7.856 +/- 0.141 pp | 16.633 +/- 0.177 pp | SURVIVES |
| **s17_high** | 0.122000 | 22.99% | **0.2326** | 5.208 +/- 0.107 pp | 8.570 +/- 0.136 pp | 16.570 +/- 0.145 pp | SURVIVES |
| moment corr | 0.144634 | 25.76% | **0.2604** | 5.549 +/- 0.121 pp | 8.914 +/- 0.147 pp | 16.499 +/- 0.153 pp | SURVIVES |

The **doubling** claim ("a fully decorrelated same-mean second entry ~doubles
P(at least one < T)"), ratio P(rho=0)/P(rho=1):

| arm | T=1.55e-7 | T=1.60e-7 | T=1.70e-7 |
|---|---|---|---|
| control | 2.0011 | 1.9415 | 1.7998 |
| moment raw | 2.0119 | 1.9174 | 1.7757 |
| **s17_low 0.0814** | 1.9244 | **1.8508** | 1.6911 |
| **s17_high 0.1220** | 1.8796 | **1.8099** | 1.6524 |
| moment corr | 1.8545 | 1.7907 | 1.6313 |

Findings, both directions reported:
1. **S4's gate SURVIVES more strongly, not less**, under corrected dispersion —
   my predeclared prediction P5 had the sign wrong. Raising vD fattens both
   suite-score tails, so the absolute pp gain grows (6.00 -> 8.57 pp at 1.6e-7)
   even though the pair correlation floor rises.
2. **The "~doubles" wording fails** at corrected dispersion: at 1.6e-7 the ratio
   falls from 1.9415 to 1.8508 / 1.8099 / 1.7907. It should be restated as
   "raises P(at least one < 1.6e-7) by ~8–9 points, a factor ~1.8".
3. **The S4 ledger's "near-zero rho_pair (~0.2% of variance)" for the Door-B
   construction is WRONG under every corrected reading** — measured shared-
   difficulty score correlation 0.1736 / 0.2326 / 0.2604 against an analytic
   share_D of 0.1713 / 0.2299 / 0.2576 (independent cross-check, agreement
   0.1–1.3%). This one sub-claim of the revival candidate **survives and should
   be carried into the writeup**: 17–26%, not 0.2%.

## 8. Two-signal verification

| # | signal | result |
|---|---|---|
| V1 | S1 control vs committed `s1_results.json` | identical incl. chunk-0 SHA-256; all rel-diff 0.0 |
| V1 | S4 control vs committed `s4_results.json` | gains and `scoreA_sd` identical to 1e-12 |
| V2 | forward MC closes the moment identity | simulated relvar reproduces `vD+(1+vD)vF` in every shape cell (`sim_relvar_forward_check` vs `model_relvar_identity` in `step1_results.json`) |
| V3 | bitwise repeat, fresh spawn of the same seed | true for all 5 S1 arms and all 5 S4 arms; S4 rho=1 same_mean bitwise equals A in all arms |
| V4 | independent simulator vs S1b's committed bracket table | 11.74/18.02/25.58 (P 0.710) vs 11.64/18.19/25.51 (0.720); 13.20/21.09/31.18 (0.861) vs 13.19/21.22/31.21 (0.862) |
| V5 | permutation null for the decisive correlation | p = 0.00000 of 20,000; null sd 0.1125 vs observed 0.5158 |
| V6 | analytic vs bootstrap SD, all R, all arms | ratios in [0.9959, 1.0036] |
| V7 | S4 realized rho=0 score correlation vs analytic share_D | 0.1736/0.2326/0.2604 vs 0.1713/0.2299/0.2576 |
| V8 | `ndtr` substitute vs C library `math.erfc` | max rel diff 9.55e-15 over 300,007 points; and exact control reproduction |

## 9. Scorecard against the predeclared predictions

| # | prediction | outcome |
|---|---|---|
| P1 | vD_moment(raw) = 0.0094/0.0129 **and** bootstrap upper bound < 0.08 | **HALF WRONG** — point values exact; upper bound is 0.08258 |
| P2 | vD_moment(corr) = 0.139/0.145 | RIGHT |
| P3 | some beta brackets 15.53 at both readings | RIGHT |
| P4 | S1 PASS everywhere; 44%/40% at S1b's vD; ~58–59% at the raw reading | RIGHT on the first two (0.4429/0.4008); **WRONG** on the third (0.5570) |
| P5 | S4 Door-B gain shrinks with vD; < 5 pp at 1.6e-7 | **WRONG, sign inverted** — gain grows to 8.57 pp; only the ratio degrades |
| P6 | floor ceiling violated under the raw reading | RIGHT, and decisive |

## 10. Bottom line for the writeup

* **Keep S1b.** vD in the region 0.08–0.15 is now supported by two independent
  instruments: the 80-net range bracket (S1b) and the rotation-free
  floor-correlation lower bound vD >= 0.10158 (this work, permutation p < 5e-5).
  The published "the old model is ~100–160x too small" headline is safe.
* **Do NOT publish "vD ~ 0.013 / difficulty share 3.4%".** It comes from a
  moment identity whose multiplicative premise the truth floor breaks, and the
  same panel excludes it.
* **Publish the split as a bound, not a point** — the one durable half of the
  candidate. Difficulty share of across-suite variance: **17–26%** (S1b's
  17–23% is the lower part of it; the floor-subtracted observable gives 25.8%).
* **Fix the S4 ledger sentence.** "Near-zero rho_pair (~0.2% of variance)" for
  the two-rotation-seed Door-B construction is wrong; it is 17–26%. S4's verdict
  is unaffected (gains 4.5–8.6 pp, gate 2 pp), but "~doubles" should become
  "factor ~1.8".
* S1's three gates PASS at every vD examined, so no S1-derived decision changes.

## 11. Limitations (attack pass on my own decisive gate)

1. **The G5 bound assumes the S1 model's own conditional structure**: given the
   net, the rotation factor is an independent draw. In m185 the rotation is
   `rot = rot_seed(seed, 0)`, a deterministic pseudorandom function of the net
   seed. Read literally that makes `E[mse|net] = mse` and the bound vacuous
   (share_D = 1); read as S1/S1b intend it — the rotation is an independent
   pseudorandom draw given the net — the bound holds. Both S1 and S1b rest on
   the same reading, so the bound is exactly as strong as the model it is being
   used to correct. It is not stronger.
2. **`vF = 0.3642` is itself an n = 48 estimate** from 3 nets. The moment
   identity and the bound both use it. A larger true `vF` pushes the moment
   reading of `vD` down and leaves the G5 bound unchanged (the bound does not
   use `vF`), so the tension the two create is if anything understated here.
3. **n = 80 for every statistic.** The bootstrap CI on the bound
   [0.0472, 0.1762] is wide; it excludes the candidate's 0.0129 comfortably but
   does not resolve 0.0814 vs 0.1220.
4. **The un-run settling check (D1) remains the way to close this properly.**
   Per-net `sigma2_var(ybar)` on 80 nets needs no rotation pool, no shape, no
   floor treatment and no independence assumption. Its predeclared kill line
   stands unchanged for whoever can pay for the forwards: relative variance
   >= 0.08 confirms S1b, < 0.03 forces withdrawal of the 100-480x headline.

## 12. Firewall statement

Reads: `m185_g0_stage1_checkpoint.json`, `a1b_tail_diagnostics.json`,
`p2_results.json`, `s1_results.json`, `s4_results.json`, `s1b_results.json`,
`run_m185_g0.py`, `run_s1.py`, `run_s4.py`, `run_s17.py` — all read-only, all
committed synthetic-He-net artifacts. Writes: this directory only. Original
harnesses unmodified (copies live here). No git, no network, no submissions, no
truth/scorer/private/holdout reads, no contact with the held m245/M243/M244 lane.
Interpreter: pinned `work/whest-v014/Scripts/python.exe`, numpy 2.4.6, no scipy.
Total compute: about 110 seconds across all four harnesses.
