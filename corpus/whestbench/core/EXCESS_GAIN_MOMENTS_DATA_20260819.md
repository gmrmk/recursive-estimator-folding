# EXCESS GAIN — MOMENT TABLE OF THE PAIRED PER-NET DATA (DATA LANE)

**Experiment** `frame_completion_129`, arms A / B / C, n = 100 paired nets.  
**Date** 2026-08-19.  **Lane** DATA (blind half of a blind pair).  
**Metric** `results.per_mlp[*].final_layer_mse` from `report_arm{A,B,C}.json`.

> **Licence / use constraint.** The arm reports are burned-Public100 DESCRIPTIVE data,
> licensed for science reads only. Nothing in this file is a designation, a promotion,
> or an eligibility claim. It is a measurement of the paired per-net distributions.

> **Blindness attestation.** Every number below was computed from the three arm JSONs
> alone. No theory-lane output, and no `core/` document, was read before this file was
> written. The only external inputs used are the four scalars supplied in the task
> brief (the two measured anchors, the two forecast values) plus the quoted `2.83`,
> `3.44`, `se_log = 0.0705`, which are treated as REPORTED and tested against, never
> assumed. Tooling: Python 3.14.4, numpy 2.4.4, scipy 1.17.1, `python -B -P`,
> `PYTHONDONTWRITEBYTECODE=1`, run from a clean scratch dir. Zero billed compute.

## Evidence-tag legend

`[OBS]` observed — computed this session from the arm JSONs, or run as a check.  
`[DER]` derived — follows from `[OBS]` values by algebra shown in-line.  
`[REP]` reported — supplied in the task brief or read out of the JSON metadata.  
`[ASM]` assumed — a modelling choice I made; named so it can be overridden.  
`[GUE]` guessed — pattern-match, not verified. Used nowhere load-bearing.

---

## 0. Verification ledger (read this before any number below)

| check | result | tag |
|---|---|---|
| Net order identical A vs B | `True` | `[OBS]` |
| Net order identical A vs C | `True` | `[OBS]` |
| `mlp_index` identical across all three arms | `True` | `[OBS]` |
| Distinct net names | 100 of 100 | `[OBS]` |
| Failed MLPs | A=0, B=0, C=0 | `[OBS]` |
| `run_config` byte-identical across arms | `True` | `[OBS]` |
| Dataset sha256 identical across arms | `True` | `[OBS]` |
| Dataset sha256 | `5b00938b6bd809fe80acef08772c5654edf467863225ca9e304b76c779ecf433` | `[REP]` |
| Aggregate `final_layer_mse` == mean of per-net array | A=True, B=True, C=True (bit-exact) | `[OBS]` |
| Any non-positive MSE (log-safety) | A=False, B=False, C=False | `[OBS]` |
| schema / whestbench version | 1.1 / 0.14.0 (all arms) | `[REP]` |

**Anchor reproduction** — the two supplied anchors are reproduced *bit-exactly* from
the per-net arrays, which is the first independent signal that this file is reading the
same quantity the brief refers to. `[OBS]`

```
mean(A) = 3.799496813883252e-07
mean(B) = 2.531207893952114e-07
mean(C) = 2.493874381315209e-07
mean(B)/mean(A) = 0.6661955563966138
          anchor = 0.6661955563966138   exact match: True
mean(C)/mean(A) = 0.6563696466865464
          anchor = 0.6563696466865464   exact match: True
mean(C)/mean(B) = 0.9852507126237606   (not supplied in brief)
```

**Method checks run before the numbers were trusted** (each is a second signal on a
piece of machinery this file depends on):

| machinery | validation | result | tag |
|---|---|---|---|
| Sample L-moment estimator (`b0..b3` order-statistic form) | run on 400 000 draws from Normal / Exponential / Uniform, compared to closed-form `τ3, τ4` | Normal τ3 +0.00031 (0), τ4 +0.12243 (0.122602); Exponential τ3 +0.33288 (1/3), τ4 +0.16670 (1/6); Uniform τ3 +0.00104 (0), τ4 +0.00020 (0) | `[OBS]` |
| 2nd-order delta expansion for `Var(log x̄)` (§5) | Monte Carlo, 4 000 000 replicates of the mean of Gamma(k) at n=100, k=1.6418 (CV 0.7804 ≈ arm A) | 1st-order rel. err. **−0.296 %**, 2nd-order rel. err. **+0.008 %** — expansion and the 5/2 coefficient confirmed | `[OBS]` |
| Weighting identity of §6 | algebraic residual against the measured arrays | residual `0.000e+00` (A→B) and `2.498e-16` (A→C) | `[OBS]` |
| Paired-delta `se_log` | 200 000-replicate paired net-level bootstrap | agreement 99.27 % (B/A), 99.41 % (C/A) | `[OBS]` |

---

## 1. Moment table

All arm quantities are `final_layer_mse` in absolute units (order 1e−7). For the raw-space
arm rows, values are ALSO given divided by 1e−7 so the moments are legible; the ratio rows
and all log rows are dimensionless and are given as-is. Skewness and excess kurtosis are
reported in the **population (biased, /n)** form `g1, g2` — the form the moment identities
in §5 use — with the Fisher sample-corrected `G1, G2` alongside. `[OBS]` throughout.

### 1a. Per arm — raw space (units of 1e−7)

| arm | mean | var (ddof=1) | sd | CV | g1 | G1 | g2 (excess) | G2 | m5\* | m6\* | min | median | max |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A | 3.799497 | 8.793837 | 2.965440 | 0.780482 | 1.47644 | 1.49902 | 1.43933 | 1.57646 | 11.5903 | 33.6981 | 0.759803 | 2.634683 | 13.328117 |
| B | 2.531208 | 3.713657 | 1.927085 | 0.761330 | 2.16141 | 2.19446 | 6.20639 | 6.59076 | 37.9482 | 167.0112 | 0.617507 | 1.896300 | 11.677081 |
| C | 2.493874 | 3.145681 | 1.773607 | 0.711185 | 1.80669 | 1.83432 | 3.51923 | 3.76423 | 21.1803 | 73.9804 | 0.637850 | 1.937121 | 9.070377 |

Absolute-unit means and variances, full precision `[OBS]`:

```
arm A: mean=3.799496813883252e-07  var_ddof1=8.793836821607768e-14  sd_ddof1=2.9654404093840374e-07
arm B: mean=2.531207893952114e-07  var_ddof1=3.713656580110394e-14  sd_ddof1=1.9270849955594573e-07
arm C: mean=2.493874381315209e-07  var_ddof1=3.145681439850746e-14  sd_ddof1=1.773606901162359e-07
```

### 1b. Per arm — log space (natural log of MSE)

| arm | mean | var (ddof=1) | sd | g1 | G1 | g2 (excess) | G2 | m5\* | m6\* | min | median | max |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A | -15.036683 | 0.487294 | 0.698065 | 0.38484 | 0.39073 | -0.71106 | -0.68545 | 1.7384 | 6.9319 | -16.39279 | -15.14934 | -13.52822 |
| B | -15.413695 | 0.432672 | 0.657778 | 0.30237 | 0.30700 | -0.45102 | -0.41192 | 2.3228 | 10.1851 | -16.60016 | -15.47820 | -13.66047 |
| C | -15.406728 | 0.390112 | 0.624589 | 0.32414 | 0.32909 | -0.45045 | -0.41133 | 2.1143 | 9.4623 | -16.56775 | -15.45689 | -13.91308 |

### 1c. Paired per-net ratios — raw space

Ratios are formed per net, then summarised. `A/B` means `mse_A[i] / mse_B[i]`. The three
requested directions are given first; the inverse directions follow because the tail and
gain analysis of §2 is naturally stated in the improvement direction.

| ratio | mean | var (ddof=1) | sd | CV | g1 | G1 | g2 (excess) | G2 | m5\* | m6\* | min | median | max |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A/B | 1.740243 | 1.436741 | 1.198641 | 0.688778 | 2.61969 | 2.65976 | 9.69158 | 10.25669 | 59.4999 | 293.2309 | 0.328014 | 1.472338 | 7.996601 |
| A/C | 1.717109 | 1.167159 | 1.080351 | 0.629169 | 1.68382 | 1.70957 | 3.43085 | 3.67127 | 21.1138 | 78.1886 | 0.327984 | 1.507319 | 6.220863 |
| C/B | 1.021162 | 0.029759 | 0.172508 | 0.168933 | 0.65586 | 0.66589 | 1.83944 | 1.99733 | 7.8157 | 41.8734 | 0.550391 | 0.988034 | 1.649526 |
| B/A | 0.813808 | 0.269323 | 0.518963 | 0.637697 | 1.86291 | 1.89140 | 4.53982 | 4.83775 | 27.7100 | 112.2187 | 0.125053 | 0.679192 | 3.048652 |
| C/A | 0.818959 | 0.264435 | 0.514233 | 0.627910 | 1.71442 | 1.74064 | 3.93382 | 4.20032 | 24.8714 | 99.7689 | 0.160749 | 0.663720 | 3.048932 |
| B/C | 1.007410 | 0.031481 | 0.177428 | 0.176123 | 1.27387 | 1.29335 | 4.44784 | 4.74100 | 24.8161 | 113.0564 | 0.606235 | 1.012117 | 1.816891 |

### 1d. Paired per-net ratios — log space

| ratio | mean | var (ddof=1) | sd | g1 | G1 | g2 (excess) | G2 | m5\* | m6\* | min | median | max |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| log A/B | 0.377013 | 0.348043 | 0.589952 | 0.07907 | 0.08028 | 0.37642 | 0.45843 | 1.4558 | 18.1496 | -1.11470 | 0.38685 | 2.07902 |
| log A/C | 0.370045 | 0.345909 | 0.588140 | 0.00404 | 0.00410 | -0.14747 | -0.09263 | 0.0505 | 11.9605 | -1.11479 | 0.41011 | 1.82791 |
| log C/B | 0.006967 | 0.028487 | 0.168780 | -0.23433 | -0.23791 | 1.85100 | 2.00949 | -4.9046 | 40.3114 | -0.59713 | -0.01204 | 0.50049 |
| log B/A | -0.377013 | 0.348043 | 0.589952 | -0.07907 | -0.08028 | 0.37642 | 0.45843 | -1.4558 | 18.1496 | -2.07902 | -0.38685 | 1.11470 |
| log C/A | -0.370045 | 0.345909 | 0.588140 | -0.00404 | -0.00410 | -0.14747 | -0.09263 | -0.0505 | 11.9605 | -1.82791 | -0.41011 | 1.11479 |
| log B/C | -0.006967 | 0.028487 | 0.168780 | 0.23433 | 0.23791 | 1.85100 | 2.00949 | 4.9046 | 40.3114 | -0.50049 | 0.01204 | 0.59713 |

Note the exact antisymmetry in log space: `log(A/B) = −log(B/A)`, so the log rows for a
direction and its inverse share variance and even standardized moments and flip the sign
of the odd ones. The table shows this holding to the printed digits, which is a cheap
internal consistency check on the moment code. `[DER]`

### 1e. Deciles

Linear-interpolation quantiles (`numpy.percentile`, default method). `[OBS]`

| series | min | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | max |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A raw /1e−7 | 0.75980 | 1.32921 | 1.54623 | 1.93491 | 2.34120 | 2.63468 | 2.97115 | 4.06206 | 5.95666 | 8.20331 | 13.32812 |
| B raw /1e−7 | 0.61751 | 0.84387 | 1.15935 | 1.39986 | 1.58177 | 1.89630 | 2.34542 | 2.98796 | 3.69937 | 4.74857 | 11.67708 |
| C raw /1e−7 | 0.63785 | 0.91753 | 1.24854 | 1.39574 | 1.55933 | 1.93712 | 2.20885 | 2.92376 | 3.74240 | 4.59462 | 9.07038 |
| A log | -16.39279 | -15.83355 | -15.68231 | -15.45807 | -15.26744 | -15.14934 | -15.02917 | -14.71739 | -14.33360 | -14.01369 | -13.52822 |
| B log | -16.60016 | -16.28789 | -15.97032 | -15.78174 | -15.65955 | -15.47820 | -15.26574 | -15.02351 | -14.80994 | -14.56054 | -13.66047 |
| C log | -16.56775 | -16.20440 | -15.89612 | -15.78471 | -15.67393 | -15.45689 | -15.32574 | -15.04528 | -14.79840 | -14.59321 | -13.91308 |
| A/B raw | 0.32801 | 0.71828 | 0.95941 | 1.06492 | 1.27474 | 1.47234 | 1.73197 | 1.98610 | 2.24720 | 2.98126 | 7.99660 |
| A/C raw | 0.32798 | 0.70418 | 0.88640 | 1.06331 | 1.19741 | 1.50732 | 1.73975 | 1.95713 | 2.29254 | 2.83055 | 6.22086 |
| C/B raw | 0.55039 | 0.87073 | 0.89077 | 0.93284 | 0.96474 | 0.98803 | 1.05368 | 1.07276 | 1.13809 | 1.22279 | 1.64953 |
| B/A raw | 0.12505 | 0.33547 | 0.44500 | 0.50350 | 0.57738 | 0.67919 | 0.78449 | 0.93906 | 1.04237 | 1.39224 | 3.04865 |
| C/A raw | 0.16075 | 0.35368 | 0.43620 | 0.51095 | 0.57481 | 0.66372 | 0.83514 | 0.94109 | 1.12841 | 1.42011 | 3.04893 |
| log A/B | -1.11470 | -0.33091 | -0.04147 | 0.06289 | 0.24273 | 0.38685 | 0.54926 | 0.68617 | 0.80969 | 1.09229 | 2.07902 |
| log A/C | -1.11479 | -0.35073 | -0.12070 | 0.06105 | 0.18016 | 0.41011 | 0.55373 | 0.67148 | 0.82966 | 1.03990 | 1.82791 |
| log C/B | -0.59713 | -0.13843 | -0.11567 | -0.06953 | -0.03590 | -0.01204 | 0.05229 | 0.07023 | 0.12935 | 0.20113 | 0.50049 |

### 1f. L-moments (robust companions) and the stability note

**Stability note — read before using the 5th and 6th standardized moments.** `[OBS]` At
n = 100 the classical 5th and 6th standardized moments are dominated by the two or three
most extreme observations and have sampling error of the same order as their own value.
The bootstrap standard errors below (20 000 paired resamples, seed 7) quantify that
directly: for `arm B raw` the point estimate of `m6*` is 167.0 with a bootstrap SE of
86.5, i.e. the estimate is barely distinguishable from half or double its value. Treat
every `m5*` / `m6*` figure in §1 as an order-of-magnitude descriptor only, and take the
L-moment column as the load-bearing shape statistic. L-moments are linear in the order
statistics, so they have bounded influence and finite variance under exactly the
heavy-tailed conditions where `m5*`/`m6*` degenerate.

Reference values: for a Normal, `L-skew = 0` and `L-kurt = 0.122602`; for an Exponential,
`1/3` and `1/6`; for a Uniform, `0` and `0`. `[DER]`

Arm raw rows are in units of 1e−7, matching §1a; all other rows are dimensionless. L-CV
(`L2/L1`) is only interpretable on positive-support data, so it is shown as `n/a` for the
log series, where the location parameter has no meaningful zero.

| series | L1 (location) | L2 (scale) | L-CV | L-skew (τ3) | L-kurt (τ4) | boot SE g1 | boot SE g2 | boot SE m5\* | boot SE m6\* |
|---|---|---|---|---|---|---|---|---|---|
| arm A raw | 3.799497 | 1.514181 | 0.398521 | +0.37514 | +0.16386 | 0.2402 | 0.9665 | 4.156 | 16.694 |
| arm B raw | 2.531208 | 0.947525 | 0.374337 | +0.34905 | +0.19157 | 0.4433 | 2.4974 | 14.943 | 86.548 |
| arm C raw | 2.493874 | 0.891751 | 0.357577 | +0.34658 | +0.18696 | 0.2693 | 1.3098 | 6.907 | 34.477 |
| arm A log | -15.036683 | 0.398301 | n/a | +0.10279 | +0.07778 | 0.1510 | 0.2547 | 0.917 | 1.886 |
| arm B log | -15.413695 | 0.376082 | n/a | +0.05934 | +0.08360 | 0.1772 | 0.3008 | 1.285 | 3.017 |
| arm C log | -15.406728 | 0.355976 | n/a | +0.07310 | +0.09347 | 0.1655 | 0.2573 | 1.069 | 2.329 |
| A/B raw | 1.740243 | 0.568720 | 0.326805 | +0.31056 | +0.24800 | 0.6021 | 3.7579 | 25.448 | 166.194 |
| A/C raw | 1.717109 | 0.554815 | 0.323110 | +0.27921 | +0.19365 | 0.2999 | 1.5198 | 8.279 | 42.275 |
| C/B raw | 1.021162 | 0.092697 | 0.090776 | +0.12214 | +0.20388 | 0.3965 | 0.8929 | 5.393 | 17.684 |
| B/A raw | 0.813808 | 0.262289 | 0.322299 | +0.30157 | +0.20997 | 0.3789 | 1.9270 | 10.685 | 56.227 |
| C/A raw | 0.818959 | 0.264864 | 0.323415 | +0.28388 | +0.18074 | 0.3726 | 1.8029 | 9.757 | 49.869 |
| B/C raw | 1.007410 | 0.092110 | 0.091433 | +0.08325 | +0.22188 | 0.5570 | 1.9712 | 12.027 | 59.983 |
| A/B log | 0.377013 | 0.330320 | n/a | -0.00520 | +0.15535 | 0.2606 | 0.4121 | 2.280 | 4.896 |
| A/C log | 0.370045 | 0.333475 | n/a | -0.00472 | +0.12509 | 0.1994 | 0.2823 | 1.432 | 2.774 |
| C/B log | 0.006967 | 0.090935 | n/a | +0.02179 | +0.20415 | 0.4348 | 0.7865 | 5.323 | 14.882 |
| B/A log | -0.377013 | 0.330320 | n/a | +0.00520 | +0.15535 | 0.2606 | 0.4121 | 2.280 | 4.896 |
| C/A log | -0.370045 | 0.333475 | n/a | +0.00472 | +0.12509 | 0.1994 | 0.2823 | 1.432 | 2.774 |
| B/C log | -0.006967 | 0.090935 | n/a | -0.02179 | +0.20415 | 0.4348 | 0.7865 | 5.323 | 14.882 |

**Normality of the log series** (Shapiro–Wilk, and the τ4 = 0.1226 Normal reference). `[OBS]`

| series | Shapiro W | p | g1 | g2 (excess) | τ3 | τ4 | verdict |
|---|---|---|---|---|---|---|---|
| arm A log | 0.96620 | 0.01140 | +0.3848 | -0.7111 | +0.10279 | +0.07778 | mild right skew + light tails; rejects normal at 5 % |
| arm B log | 0.98239 | 0.20333 | +0.3024 | -0.4510 | +0.05934 | +0.08360 | consistent with normal |
| arm C log | 0.97800 | 0.09273 | +0.3241 | -0.4505 | +0.07310 | +0.09347 | consistent with normal (marginal) |
| A/B log | 0.99166 | 0.79644 | +0.0791 | +0.3764 | -0.00520 | +0.15535 | consistent with normal |
| A/C log | 0.99447 | 0.95900 | +0.0040 | -0.1475 | -0.00472 | +0.12509 | **indistinguishable from normal** |
| C/B log | 0.96040 | 0.00430 | -0.2343 | +1.8510 | +0.02179 | +0.20415 | rejects normal — leptokurtic, left-skewed |

### 1g. What the moment table says

`[DER]` from §1a–1f:

1. **Raw space is strongly right-skewed and heavy-tailed in every arm**, and the treated
   arms are *relatively* heavier-tailed than the control: excess kurtosis rises from
   **1.4393** (A) to **3.5192** (C) to **6.2064** (B), and skewness from 1.4764 to 1.8067 to
   2.1614. The arms did not merely shrink the distribution; they shrank the body more than
   the tail, so the surviving tail is a larger multiple of the new mean. Arm B is the
   extreme case — it has the second-largest maximum (1.1677e−7×10) but the smallest
   D1–D5 of any arm.
2. **Log space is light-tailed in every arm.** Excess kurtosis is *negative* for all three
   (−0.7111, −0.4510, −0.4505) and L-kurt sits below the Normal 0.1226 reference
   (0.0778, 0.0836, 0.0935). The per-net MSE distribution is close to, and slightly
   lighter-tailed than, log-normal.
3. **The A/C log-ratio is statistically indistinguishable from Gaussian**: g1 = +0.0040,
   excess g2 = −0.1475, τ3 = −0.00473, τ4 = +0.12509 against the Normal 0.122602, Shapiro
   W = 0.99447 (p = 0.959). Three independent shape statistics agree. This matters for
   §5: the *log-ratio* instrument is operating on an essentially normal sample, so its
   1/√n scaling is well founded, whatever else is wrong.
4. **The C/B contrast is the only non-Gaussian log contrast** (excess g2 = +1.8510,
   τ4 = +0.20415, Shapiro p = 0.0043) and it is also the tightest (log variance 0.028487
   against 0.3480 and 0.3459 for the A-legs) — B and C track each other closely on most
   nets and diverge sharply on a few.

---

## 2. Tail attribution

Gain is defined two ways per net i, both in the improvement direction:

```
gain_abs[i] = mse_A[i] - mse_X[i]        (absolute MSE removed; > 0 is an improvement)
gain_rel[i] = 1 - mse_X[i]/mse_A[i]      (fraction of that net's MSE removed)
```

### 2a. Rank correlation of per-net gain against arm-A per-net MSE

`[OBS]` Two-sided p-values from `scipy.stats`.

| leg | gain definition | Spearman ρ | p | Kendall τ | p | Pearson r | p |
|---|---|---|---|---|---|---|---|
| A→C | absolute | +0.663414 | 5.430e-14 | +0.522424 | 1.346e-14 | +0.803171 | 8.999e-24 |
| A→C | relative | +0.519292 | 3.100e-08 | +0.361212 | 1.010e-07 | +0.409199 | 2.366e-05 |
| A→B | absolute | +0.641296 | 6.582e-13 | +0.496970 | 2.368e-13 | +0.764586 | 2.109e-20 |
| A→B | relative | +0.469043 | 8.558e-07 | +0.320000 | 2.390e-06 | +0.368119 | 1.645e-04 |

The relative-gain rows are the important ones. A→C relative gain has Spearman
**ρ = +0.5193** (p = 3.10e−08) and Kendall **τ = +0.3612** (p = 1.01e−07) against arm-A
per-net MSE; A→B has ρ = +0.4690, τ = +0.3200. `[OBS]` **Nets that were already worst
under A get the largest *fractional* improvement**, not merely the largest absolute one.
That is the first half of a two-stage amplification: the second half is that those same
nets carry the most weight in a ratio of means (§6).

Equivalently, regressing the log per-net ratio on log arm-A MSE `[OBS]`:

| ratio | Spearman ρ vs arm-A MSE | Kendall τ | Pearson r (log–log) | OLS slope d log(ratio)/d log(A) |
|---|---|---|---|---|
| B/A | -0.469043 | -0.320000 | -0.488879 | -0.413164 |
| C/A | -0.519292 | -0.361212 | -0.539618 | -0.454644 |
| C/B | -0.202820 | -0.136162 | -0.171560 | -0.041480 |

### 2b. Concentration of the aggregate improvement

Nets ranked by **arm-A per-net MSE, descending**. Shares are of the total absolute
improvement `Σ(mse_A − mse_X)`, which equals `n ×` the change in the mean. `[OBS]`

| leg | top 1 net | top 5 | **top decile (10)** | **top quartile (25)** | top half (50) | (same nets' share of arm-A total MSE) |
|---|---|---|---|---|---|---|
| A→C | 6.459 % | 32.557 % | **47.834 %** | **83.826 %** | 94.955 % | decile 28.059 % / quartile 54.237 % |
| A→B | 6.260 % | 32.631 % | **46.957 %** | **83.789 %** | 93.183 % | decile 28.059 % / quartile 54.237 % |

The top decile of arm-A nets carries **47.83 %** of the total A→C improvement while
holding only **28.06 %** of arm-A total MSE; the top quartile carries **83.83 %** while
holding **54.24 %**. The improvement is therefore more concentrated than the MSE itself —
super-proportional, not merely proportional to where the error was. `[DER]`

The ten nets of that top decile, in order: `andrew-oneal`, `david-davis`, `taylor-robbins`, `sonia-reynolds`, `erica-hopkins`, `laura-fuentes`, `christopher-lee`, `joseph-green`, `karen-stokes`, `julia-arellano`. `[OBS]`

**Improvement share by arm-A decile** (decile 1 = worst arm-A nets). `[OBS]`

| decile (by arm-A MSE, desc) | A→C improvement share | A→B improvement share | share of arm-A MSE |
|---|---|---|---|
| 1 | +0.47834 | +0.46957 | 0.28059 |
| 2 | +0.22133 | +0.22548 | 0.18999 |
| 3 | +0.17904 | +0.18154 | 0.13094 |
| 4 | +0.02965 | +0.02586 | 0.09301 |
| 5 | +0.04118 | +0.02938 | 0.07354 |
| 6 | +0.04256 | +0.04430 | 0.06501 |
| 7 | +0.01908 | +0.02123 | 0.05562 |
| 8 | +0.00689 | +0.01116 | 0.04582 |
| 9 | -0.00736 | -0.00546 | 0.03719 |
| 10 | -0.01072 | -0.00307 | 0.02829 |

Deciles 9 and 10 — the *best-conditioned* nets under A — have **negative** improvement
shares on both legs. The treated arms actively degrade the easiest nets. `[OBS]`

### 2c. Mean vs median vs trimmed — is the tail story live?

`[OBS]`

| leg | mean gain (abs) | median gain (abs) | mean/median | nets made **worse** | mean gain (rel) | median gain (rel) |
|---|---|---|---|---|---|---|
| A→C | 1.305622e-07 | 7.583046e-08 | **1.72177** | 29 / 100 | +0.181041 | +0.336280 |
| A→B | 1.268289e-07 | 6.688994e-08 | **1.89608** | 25 / 100 | +0.186192 | +0.320808 |

**Mean absolute gain is 1.72× the median on A→C and 1.90× on A→B.** By the brief's own
criterion (`mean gain >> median gain` ⇒ tail story live) **the tail story is live on both
legs.** `[DER]`

The relative-gain row inverts the comparison and is worth pausing on: mean relative gain
(+0.1810) is *below* median relative gain (+0.3363), because 29 of 100 nets are made
worse and the worst of them is made worse by a factor of ~3 (`gain_rel` min = −2.0489,
i.e. arm C's MSE is 3.05× arm A's on that net). So the two tails do different jobs: the
**upper arm-A tail supplies the aggregate win**, and a **separate set of easy nets
supplies a dispersed loss** that the mean-of-ratios registers and the ratio-of-means
almost ignores. `[DER]`

### 2d. The four ratio summaries

This is the table the rest of the document turns on. `[OBS]`

| leg | **aggregate ratio-of-means** `mean(X)/mean(A)` | mean of per-net ratios | median of per-net ratios | 10 %-trimmed mean of per-net ratios | 20 %-trimmed | geometric mean of per-net ratios |
|---|---|---|---|---|---|---|
| A→C | **0.6563696467** | 0.8189592728 | 0.6637200124 | 0.7462627292 | 0.7160035635 | 0.6907029498 |
| A→B | **0.6661955564** | 0.8138081942 | 0.6791919669 | 0.7345681992 | 0.7042224786 | 0.6859074962 |

The spread across these five estimators of "the ratio" is **0.6564 → 0.8190 on A→C**, a
range of 0.163 — which is *larger than the entire forecast-vs-measured gap of 0.188 the
campaign is trying to explain*. The choice of estimator is not a rounding detail here; it
is comparable in size to the effect. `[DER]` This is developed in §6.

---

## 3. Sensitivity — leave-one-net-out jackknife

`[OBS]` Each row drops one net, recomputes on the remaining 99, and reports the spread.
`jack_se` is the standard jackknife SE, `√((n−1)/n · Σ(θ₍ᵢ₎ − θ̄)²)`.

| quantity | full sample | LOO min | LOO max | LOO range | jackknife SE | jackknife bias est. |
|---|---|---|---|---|---|---|
| R_BA — raw ratio of means | 0.666196 | 0.645058 | 0.681708 | 0.036650 | 0.049620 | +1.942819e-03 |
| R_BA — log ratio of means | -0.406172 | -0.438415 | -0.383154 | 0.055261 | 0.074558 | +1.388299e-04 |
| R_BA — **se_log** (paired delta) | 0.073837 | 0.068080 | 0.075568 | 0.007488 | 0.007835 | +3.572111e-02 |
| R_BA — se_log (naive log-ratio sample) | 0.058995 | 0.057008 | 0.059594 | 0.002587 | 0.004692 | +2.923785e-02 |
| R_CA — raw ratio of means | 0.656370 | 0.638109 | 0.671020 | 0.032911 | 0.048438 | +2.126874e-03 |
| R_CA — log ratio of means | -0.421031 | -0.449247 | -0.398956 | 0.050290 | 0.073774 | +5.185792e-04 |
| R_CA — **se_log** (paired delta) | 0.073146 | 0.068866 | 0.075130 | 0.006264 | 0.006790 | +3.562129e-02 |
| R_CA — se_log (naive log-ratio sample) | 0.058814 | 0.057447 | 0.059411 | 0.001964 | 0.004115 | +2.918986e-02 |
| R_CB — raw ratio of means | 0.985251 | 0.972059 | 1.006282 | 0.034223 | 0.029508 | +8.139240e-04 |
| R_CB — log ratio of means | -0.014859 | -0.028339 | 0.006262 | 0.034601 | 0.029843 | +3.797493e-04 |
| R_CB — **se_log** (paired delta) | 0.029255 | 0.021455 | 0.030235 | 0.008780 | 0.008702 | +1.240725e-02 |
| R_CB — se_log (naive log-ratio sample) | 0.016878 | 0.015896 | 0.017049 | 0.001153 | 0.001723 | +8.330310e-03 |

**Reading.** `[DER]`

- The aggregate ratios are **stable against any single net**: `R_BA` moves over
  [0.645058, 0.681708] (range 0.036650) and `R_CA` over [0.638109, 0.671020] (range
  0.032911). Even the single most influential net moves `R_BA` by only 0.0211, which is
  **13.6 % of the 0.1550 forecast gap**. No single net manufactures the excess gain.
- `se_log` is markedly less stable than the ratio it qualifies. Dropping one net moves the
  A→B `se_log` over [0.068080, 0.075568] — a **10.1 % swing** — with jackknife SE 0.007835
  on a point value of 0.073837. The instrument is roughly ±11 % uncertain at n = 100,
  which is exactly the magnitude §5 predicts from the kurtosis of the paired influence
  function. Any σ figure quoted to three digits is over-stated in precision.
- `R_CB` is the fragile one: its LOO range (0.034223) is comparable to the A-legs' while
  the effect itself is only 0.0147 from unity, so the B-vs-C ordering is **not** robust to
  single-net deletion — LOO max 1.006282 crosses 1.0.

### 3a. The nets that move the estimate most

**B/A raw ratio of means** (full sample 0.666196) `[OBS]`

| direction | net | LOO value | Δ vs full | arm A MSE | arm B MSE | arm C MSE |
|---|---|---|---|---|---|---|
| drop ⇒ ratio falls | `russell-cox` | 0.645058 | -0.021138 | 3.341373e-07 | 1.018668e-06 | 9.070377e-07 |
| drop ⇒ ratio falls | `laura-fuentes` | 0.653098 | -0.013098 | 1.025976e-06 | 1.167708e-06 | 6.426959e-07 |
| drop ⇒ ratio falls | `luke-king` | 0.656330 | -0.009866 | 2.643091e-07 | 5.483277e-07 | 5.481573e-07 |
| drop ⇒ ratio falls | `dawn-martin` | 0.656856 | -0.009339 | 2.857115e-07 | 5.425226e-07 | 4.737182e-07 |
| drop ⇒ ratio falls | `abigail-morrow` | 0.658488 | -0.007708 | 8.158020e-07 | 8.300466e-07 | 7.983303e-07 |
| drop ⇒ ratio rises | `sonia-reynolds` | 0.681708 | +0.015512 | 1.090869e-06 | 1.542652e-07 | 1.753566e-07 |
| drop ⇒ ratio rises | `david-davis` | 0.680253 | +0.014057 | 1.327955e-06 | 3.692336e-07 | 3.916529e-07 |
| drop ⇒ ratio rises | `taylor-robbins` | 0.676920 | +0.010725 | 1.197464e-06 | 4.030982e-07 | 2.656322e-07 |
| drop ⇒ ratio rises | `andrew-oneal` | 0.675715 | +0.009519 | 1.332812e-06 | 5.389098e-07 | 4.895194e-07 |
| drop ⇒ ratio rises | `dustin-merritt` | 0.675374 | +0.009179 | 8.024696e-07 | 1.932147e-07 | 1.760033e-07 |

**C/A raw ratio of means** (full sample 0.656370) `[OBS]`

| direction | net | LOO value | Δ vs full | arm A MSE | arm B MSE | arm C MSE |
|---|---|---|---|---|---|---|
| drop ⇒ ratio falls | `russell-cox` | 0.638109 | -0.018261 | 3.341373e-07 | 1.018668e-06 | 9.070377e-07 |
| drop ⇒ ratio falls | `alexandra-hawkins` | 0.645247 | -0.011123 | 6.014773e-07 | 5.828911e-07 | 8.107032e-07 |
| drop ⇒ ratio falls | `luke-king` | 0.646439 | -0.009930 | 2.643091e-07 | 5.483277e-07 | 5.481573e-07 |
| drop ⇒ ratio falls | `julia-arellano` | 0.647285 | -0.009084 | 8.610879e-07 | 5.849685e-07 | 9.025342e-07 |
| drop ⇒ ratio falls | `dawn-martin` | 0.648780 | -0.007589 | 2.857115e-07 | 5.425226e-07 | 4.737182e-07 |
| drop ⇒ ratio rises | `sonia-reynolds` | 0.671020 | +0.014650 | 1.090869e-06 | 1.542652e-07 | 1.753566e-07 |
| drop ⇒ ratio rises | `taylor-robbins` | 0.670510 | +0.014141 | 1.197464e-06 | 4.030982e-07 | 2.656322e-07 |
| drop ⇒ ratio rises | `david-davis` | 0.669460 | +0.013090 | 1.327955e-06 | 3.692336e-07 | 3.916529e-07 |
| drop ⇒ ratio rises | `andrew-oneal` | 0.666879 | +0.010509 | 1.332812e-06 | 5.389098e-07 | 4.895194e-07 |
| drop ⇒ ratio rises | `dustin-merritt` | 0.665799 | +0.009430 | 8.024696e-07 | 1.932147e-07 | 1.760033e-07 |

The structure of that list is itself informative `[DER]`: the nets whose removal *raises*
the ratio (i.e. that supply the gain) are uniformly **high-A, low-treated** —
`sonia-reynolds` (A = 1.0909e−06 → B = 1.5427e−07, a 7.07× reduction), `david-davis`,
`taylor-robbins`, `andrew-oneal`. The nets whose removal *lowers* it are **A-normal,
treated-catastrophic** — `russell-cox` (A = 3.3414e−07 → B = 1.0187e−06, a 3.05×
*degradation*). The aggregate is a contest between a handful of large rescues and a
handful of large regressions, and the rescues win.

---

## 4. Cross-arm structure

### 4a. Per-net correlation matrices

`[OBS]` Pearson on raw MSE, Pearson on log MSE, Spearman, Kendall. n = 100 paired.

**Pearson, raw MSE**

| | A | B | C |
|---|---|---|---|
| **A** | 1.000000 | 0.541555 | 0.522373 |
| **B** | 0.541555 | 1.000000 | 0.923287 |
| **C** | 0.522373 | 0.923287 | 1.000000 |

**Pearson, log MSE**

| | A | B | C |
|---|---|---|---|
| **A** | 1.000000 | 0.622777 | 0.609510 |
| **B** | 0.622777 | 1.000000 | 0.966672 |
| **C** | 0.609510 | 0.966672 | 1.000000 |

**Spearman**

| | A | B | C |
|---|---|---|---|
| **A** | 1.000000 | 0.626811 | 0.600216 |
| **B** | 0.626811 | 1.000000 | 0.971665 |
| **C** | 0.600216 | 0.971665 | 1.000000 |

**Kendall τ**

| | A | B | C |
|---|---|---|---|
| **A** | 1.000000 | 0.446465 | 0.422222 |
| **B** | 0.446465 | 1.000000 | 0.865051 |
| **C** | 0.422222 | 0.865051 | 1.000000 |

Raw covariances (absolute units) `[OBS]`:

```
cov(A,A) = 8.79383682160777e-14
cov(A,B) = 3.094802933487592e-14
cov(A,C) = 2.7474355448378697e-14
cov(B,B) = 3.7136565801103963e-14
cov(B,C) = 3.155696071180394e-14
cov(C,C) = 3.1456814398507474e-14
```

**Reading.** `[DER]` The two treated arms are near-duplicates of each other
(Pearson raw **0.9233**, log **0.9667**, Spearman **0.9717**, Kendall **0.8651**) and both
are only moderately coupled to the control (A–B raw 0.5416, A–C raw 0.5224; log 0.6228 and
0.6095). B and C are two samples of one intervention, not two interventions. Whatever the
treated arms are doing, it **decorrelates them from the control by about the same amount**
— which is why the C/B contrast is tight and the A-legs are wide.

### 4b. Do the C/B per-net ratios track arm-A conditioning?

Using arm-A per-net MSE as the conditioning proxy, as directed. `[OBS]` `[ASM]` — the
proxy choice is the brief's, and arm-A MSE conflates net conditioning with arm-A
estimator behaviour; nothing below separates those.

| statistic | value | p |
|---|---|---|
| Spearman ρ (C/B vs arm-A MSE) | -0.202820 | 0.042992 |
| Kendall τ | -0.136162 | 0.044723 |
| Pearson r (log C/B vs log A) | -0.171560 | 0.087877 |
| OLS slope d log(C/B) / d log(A) | -0.041480 | — |

**Verdict: weak and not robust.** `[DER]` The rank correlations are negative and sit
just under the 5 % line (ρ = −0.2028, p = 0.0430; τ = −0.1362, p = 0.0447) while the
log–log Pearson does not clear it at all (r = −0.1716, p = 0.0879). Three tests of the
same hypothesis straddle the threshold, and the fitted slope is −0.0415 — C beats B by
about 4 % per e-fold of arm-A MSE, against a C/B log SD of 0.1688. Compare the A-legs,
where the same statistic is unambiguous (C/A: ρ = −0.5193, p = 3.10e−08, slope −0.4546).
There is a hint that C's advantage over B lives on the badly-conditioned nets, but it is
roughly a tenth the strength of the A→C conditioning effect and it would not survive a
multiplicity correction across the tests reported in this file.

---

## 5. Instrument check

### 5a. First: the quoted σ values are reproduced, and they are LOG-scale

`[OBS]` This was not stated in the brief — the brief calls 2.83 and 3.44 "raw-leg SE" —
but the arithmetic identifies the convention unambiguously:

```
A→B:  log(forecast / measured) / se_log_paired_delta
        = log(0.8212 / 0.6661955564) / 0.0738367614
        = 0.2091834295 / 0.0738367614
        = 2.833053       quoted: 2.83
A→C:  log(forecast / measured) / se_log_paired_delta
        = log(0.8445 / 0.6563696467) / 0.0731459074
        = 0.2520206202 / 0.0731459074
        = 3.445451       quoted: 3.44
```

Both quoted σ are reproduced to within rounding (2.833053 vs 2.83; 3.445451 vs 3.44).
`[DER]` **The quoted gaps are log-scale z-statistics computed with a paired-delta
`se_log`, not raw-scale ones.** The `se_log` values that generate them are
**0.073837** (A→B) and **0.073146** (A→C).

On the *raw* scale the same paired-delta instrument gives larger σ, because the raw SE is
`R × se_log` and `R < 1`: `[OBS]`

| leg | forecast | measured | raw gap | implied SE behind the quoted σ | paired-delta raw SE | bootstrap raw SE (200k) | σ under paired delta | σ under bootstrap |
|---|---|---|---|---|---|---|---|---|
| A→B | 0.8212 | 0.6661955564 | 0.1550044436 | 0.054772 | 0.049190 | 0.049104 | **3.1512** | 3.1567 |
| A→C | 0.8445 | 0.6563696467 | 0.1881303533 | 0.054689 | 0.048011 | 0.048003 | **3.9185** | 3.9191 |

### 5b. The quoted `se_log = 0.0705` is NOT reproduced by any estimator over these arrays

`[OBS]` This is a negative result and it is reported as one. I computed every standard
`se_log` construction over the three per-net arrays. Grouped by **estimand**, because that
is where the discrepancies live:

**Estimand 1 — SE of `log(mean X / mean A)`** (the estimand the 0.666 / 0.656 anchors
actually name, since those are ratios of means):

| leg | paired delta (1st order) | paired bootstrap 200k | jackknife | naive unpaired delta |
|---|---|---|---|---|
| B/A | **0.073837** | 0.073299 | 0.074558 | 0.109031 |
| C/A | **0.073146** | 0.072715 | 0.073774 | 0.105591 |
| C/B | **0.029255** | 0.028772 | 0.029843 | 0.104183 |

**Estimand 2 — SE of the mean log-ratio** (i.e. of the *geometric*-mean ratio; a different
quantity):

| leg | sd(log ratio)/√n |
|---|---|
| B/A | 0.058995 |
| C/A | 0.058814 |
| C/B | 0.016878 |

**Estimand 3 — SE of a single arm's `log(mean)`:**

| arm | sd(log x)/√n | CV/√n (delta, 1st order) |
|---|---|---|
| A | 0.069806 | 0.078048 |
| B | 0.065778 | 0.076133 |
| C | 0.062459 | 0.071119 |

**None of these is 0.0705.** `[OBS]` The two values that *do* reproduce the quoted σ are
0.073837 and 0.073146. If 0.0705 were used on both legs the σ would be **2.967** and
**3.575**, not 2.83 and 3.44. The nearest computable neighbours to 0.0705 are the arm-C
first-order delta `CV_C/√n = 0.071119` and the arm-A log SD `sd(log A)/√n = 0.069806`,
neither of which is a leg statistic. `[DER]` **Flagged for the theory lane: `se_log =
0.0705` is a third number whose provenance is not in these three files.** It is not
reconcilable with the σ figures it is quoted beside. Settling check: whichever script
emitted `se_log` should be re-run with its own inputs printed; I cannot close this from
the arm reports.

### 5c. (a) naive 1/√n normal scaling vs (b) the kurtosis-corrected formula

The formula. For a mean of n iid draws with coefficient of variation `CV`, skewness `γ1`
and excess kurtosis `γ2`, expanding `log(1+δ)` with `δ = (x̄−μ)/μ` and collecting to
`O(n⁻²)`: `[DER]`

```
Var(log x̄) = CV²/n  −  γ1·CV³/n²  +  (5/2)·CV⁴/n²  +  (11/12)·γ2·CV⁴/n³  +  O(n⁻³)
             \_____/    \________________________/     \______________/
             (a) naive        skewness + CV⁴ terms       kurtosis term
```

**This expansion was validated before use** `[OBS]`: 4 000 000 Monte-Carlo replicates of
the mean of Gamma(k = 1.6418) at n = 100 (CV = 0.7804, matched to arm A) give
`Var(log x̄) = 0.0061089548`; the naive term alone is 0.0060908759 (**−0.296 %**), the
second-order form is 0.0061094253 (**+0.008 %**). The 5/2 coefficient is confirmed.

Applied to the measured per-net moments: `[OBS]`

| arm | CV | γ1 | γ2 (excess) | (a) naive `CV/√n` | (b) 2nd-order | (b) + kurtosis term | effect of (b) on SE | effect of the **kurtosis term alone** |
|---|---|---|---|---|---|---|---|---|
| A | 0.776570 | 1.47644 | 1.43933 | 0.07765702 | 0.07779710 | 0.07780018 | +0.18039 % | +0.003964 % |
| B | 0.757514 | 2.16141 | 6.20639 | 0.07575140 | 0.07567457 | 0.07568695 | -0.10142 % | +0.016355 % |
| C | 0.707620 | 1.80669 | 3.51923 | 0.07076205 | 0.07075262 | 0.07075834 | -0.01332 % | +0.008078 % |

**Answer to the brief's question: no — (b) does not reproduce 0.0705, and it cannot.**
`[DER]` The reason is structural, not numerical. Kurtosis enters `Var(log x̄)` only at
`O(n⁻³)`, because the fourth central moment of a *sample mean* is `3σ⁴/n² + γ2σ⁴/n³` —
the `3σ⁴/n²` piece is distribution-free and the kurtosis-carrying piece is suppressed by
a further factor of n. At n = 100 the entire kurtosis term moves the SE by **+0.004 % to
+0.016 %**, and the whole second-order correction (which is dominated by skewness, not
kurtosis) moves it by **−0.10 % to +0.18 %**. Moving 0.073837 to 0.0705 requires **−4.5 %**
— two to three orders of magnitude more than any higher-moment correction can supply at
this n. **The 0.0705-vs-0.0738 discrepancy is an estimand or convention difference, not a
moment correction.**

### 5d. Where kurtosis *does* bite: the precision of `se_log` itself

The fourth moment governs not the value of `se_log` but its own sampling error, through
`Var(s²) = (1/n)(μ₄ − ((n−3)/(n−1))σ⁴)`, giving effective df `ν ≈ 2n/(γ2+2)` and a
relative SE on the estimated SE of `½√((γ2+2)/n)`. `[DER]` Evaluated on the paired
influence function `u_i = X_i/mean(X) − A_i/mean(A)` whose variance *is* `n·se_log²`:
`[OBS]`

| leg | γ1 of u | γ2 of u (excess) | SE-of-SE inflation vs normal `√((γ2+2)/2)` | effective df `2n/(γ2+2)` | relative SE of `se_log` | jackknife check on `se_log` |
|---|---|---|---|---|---|---|
| B/A | +0.28078 | 3.69238 | 1.6871× | 35.13 | 11.93 % | jack SE 0.007835 on 0.073837 = 10.61 % |
| C/A | -0.06495 | 2.59531 | 1.5158× | 43.52 | 10.72 % | jack SE 0.006790 on 0.073146 = 9.28 % |
| C/B | -2.26561 | 26.39568 | 3.7680× | 7.04 | 26.64 % | jack SE 0.008702 on 0.029255 = 29.75 % |

The kurtosis-corrected relative SE (11.93 %, 10.72 %) and the independent jackknife
(10.61 %, 9.28 %) agree to about a percentage point — two independent signals on the same
claim. `[DER]` **So the correct kurtosis statement is: `se_log ≈ 0.0738 ± 0.008` on the
A→B leg, and every σ derived from it inherits ~±11 % — 2.83 σ is really 2.83 ± 0.31 σ.**
The C/B leg is far worse (γ2 of u = 26.40, ν_eff = 7.05, relative SE 26.6 %); any
inference on C-vs-B from n = 100 is running on the equivalent of seven degrees of freedom.

---

## 6. The finding: the gap is a weighting term, and it is a first-moment object

This section was not requested as such. It falls out of §2d and it is the largest
single result in the data lane, so it is reported here rather than left implicit.

### 6a. An exact identity

For per-net ratios `r_i = mse_X[i]/mse_A[i]`, the aggregate ratio-of-means is the
**arm-A-MSE-weighted** mean of `r_i`, so `[DER]`:

```
mean(X)/mean(A)  =  Σ a_i r_i / Σ a_i  =  mean(r)  +  Cov(a, r) / mean(a)
                                          \______/    \_______________/
                                          unweighted    the weighting term
```

Verified against the measured arrays with zero residual `[OBS]`:

| leg | ratio-of-means | unweighted mean(r) | `Cov(a,r)/mean(a)` | identity residual |
|---|---|---|---|---|
| A→B | 0.6661955564 | 0.8138081942 | -0.1476126378 | 0.000e+00 |
| A→C | 0.6563696467 | 0.8189592728 | -0.1625896261 | 2.498e-16 |

### 6b. The forecast lands on the unweighted mean, not on the ratio-of-means

`[OBS]` `[DER]`

| leg | forecast | unweighted mean(r) | gap | SE of unweighted mean `sd(r)/√n` | **z** | ratio-of-means | gap | **quoted z** |
|---|---|---|---|---|---|---|---|---|
| A→B | 0.8212 | 0.8138081942 | +0.007392 | 0.051896 | **+0.1424** | 0.6661955564 | +0.155004 | 2.83 |
| A→C | 0.8445 | 0.8189592728 | +0.025541 | 0.051423 | **+0.4967** | 0.6563696467 | +0.188130 | 3.44 |

**The second-moment forecast is not off by 2.83 σ and 3.44 σ. Against the unweighted mean
of the per-net defect ratios it is off by +0.14 σ and +0.50 σ.** `[DER]` The weighting
term accounts for **95.2 %** of the A→B gap and **86.4 %** of the A→C gap:

| leg | total gap forecast − ratio-of-means | of which weighting term `Cov(a,r)/mean(a)` | share | residual (genuine forecast error) |
|---|---|---|---|---|
| A→B | +0.155004 | +0.147613 | 95.2 % | +0.007392 |
| A→C | +0.188130 | +0.162590 | 86.4 % | +0.025541 |

### 6c. The attack that would have killed this, and what it returned

`[OBS]` The strongest counter-hypothesis is coincidence: with two legs and five candidate
ratio estimators, one of them landing near the forecast is not surprising. The
discriminating test is **ordering**, because the two legs' forecasts are ordered
(C forecast 0.8445 > B forecast 0.8212) and the two candidate estimands order them
*oppositely*:

| quantity | A→B | A→C | C − B | agrees with forecast ordering? |
|---|---|---|---|---|
| forecast | 0.8212 | 0.8445 | +0.023300 | — |
| unweighted mean(r) | 0.813808 | 0.818959 | +0.005151 | **yes, same sign** |
| ratio-of-means | 0.666196 | 0.656370 | -0.009826 | **no, opposite sign** |

The forecast says C should be the *weaker* leg; the unweighted per-net mean agrees; the
ratio-of-means reverses it. `[DER]` The attack did not land — but it did not land cleanly
either, and the wobble is reported: the C−B difference in unweighted means is
**+0.005151 against a paired SE of 0.014476, z = +0.356**. The *ordering* agreement is
individually insignificant. What survives at strength is the *level* agreement on two
legs (+0.14 σ, +0.50 σ), with the ordering as weak corroboration rather than proof.

### 6d. Mechanism, in one paragraph

`[DER]` from §2a, §2b, §4a and §6a. The weighting term is `Cov(a_i, r_i)/mean(a)`, a
covariance between two *first*-moment per-net objects: how bad a net was under A, and what
fraction of that badness survived treatment. It is large and negative
(−0.1476, −0.1626) because the two ingredients are strongly rank-coupled — relative gain
against arm-A MSE has Spearman ρ = +0.4690 (A→B) and +0.5193 (A→C). Badly-conditioned nets
get a *larger fraction* of their error removed, and they simultaneously carry the *most
weight* in a mean-of-MSE aggregate. The excess gain is that product. A per-degree
energy-share × defect-ratio forecast, being an average over structural components rather
than an MSE-weighted average over nets, has no term for it: it predicts `mean(r)` and is
compared against `Σa r/Σa`. To the owner's framing — *"we are looking at the kurtosis —
what about the other elements and the inference between them"* — the measured answer from
the data lane is that **the missing element is not a higher moment at all; it is the
first-order covariance between the difficulty distribution and the gain distribution, and
"the inference between them" is literally a covariance the aggregation step takes and the
forecast does not.** Kurtosis is real here (§1g: excess 1.44 → 6.21 across arms) and it
governs how *uncertain* every number in this file is (§5d), but it does not move the
point estimate by more than a fraction of a percent.

---

## 7. What this lane does not establish

`[ASM]` / limits, stated so the theory lane can price them:

1. **Provenance of `se_log = 0.0705` is unresolved** (§5b). It reconciles with neither the
   σ figures quoted beside it nor any estimator over these arrays. Settling check named
   in §5b.
2. **`n = 100`, one seed, one dataset sha.** Every SE here is a within-run SE over nets; it
   carries no seed-to-seed or dataset-to-dataset variance. The jackknife in §3 bounds
   single-net influence only.
3. **Arm-A per-net MSE as a conditioning proxy is the brief's choice** and it conflates
   net conditioning with arm-A estimator behaviour. §6 does not depend on the causal
   reading — the identity holds whatever `a_i` means — but §2a and §4b do.
4. **The 5th and 6th standardized moments in §1 should not be used quantitatively**, per
   the stability note in §1f. Use the L-moment columns.
5. **No claim is made about which estimand is *correct*.** §6 establishes that the forecast
   and the anchor are computing different averages and quantifies the difference. Which
   one the benchmark should score is a design question, not a measurement one, and it is
   outside this lane.
6. **Multiplicity is uncorrected** across the ~40 hypothesis tests reported here. The
   headline results (§2a, §6b) clear any reasonable correction; §4b explicitly does not.

---

## Appendix — per-net data (all 100 nets, full precision)

`[OBS]` Sorted by arm-A MSE descending, so row 1–10 is the top decile of §2b.

| # | net | arm A | arm B | arm C | B/A | C/A | C/B |
|---|---|---|---|---|---|---|---|
| 1 | `andrew-oneal` | 1.3328117348e-06 | 5.3890983054e-07 | 4.8951937970e-07 | 0.40434055 | 0.36728322 | 0.90835118 |
| 2 | `david-davis` | 1.3279551467e-06 | 3.6923358948e-07 | 3.9165286125e-07 | 0.27804673 | 0.29492928 | 1.06071840 |
| 3 | `taylor-robbins` | 1.1974644849e-06 | 4.0309819838e-07 | 2.6563219535e-07 | 0.33662643 | 0.22182887 | 0.65897639 |
| 4 | `sonia-reynolds` | 1.0908693184e-06 | 1.5426516597e-07 | 1.7535657548e-07 | 0.14141489 | 0.16074939 | 1.13672179 |
| 5 | `erica-hopkins` | 1.0860800330e-06 | 4.3110304659e-07 | 4.6229098416e-07 | 0.39693488 | 0.42565094 | 1.07234451 |
| 6 | `laura-fuentes` | 1.0259763030e-06 | 1.1677080920e-06 | 6.4269590894e-07 | 1.13814334 | 0.62642374 | 0.55039090 |
| 7 | `christopher-lee` | 9.7953943623e-07 | 3.1836742664e-07 | 3.1326135286e-07 | 0.32501747 | 0.31980474 | 0.98396170 |
| 8 | `joseph-green` | 8.8045749180e-07 | 3.2545648310e-07 | 3.7273457565e-07 | 0.36964474 | 0.42334193 | 1.14526702 |
| 9 | `karen-stokes` | 8.7858450115e-07 | 4.1222216396e-07 | 3.9979315147e-07 | 0.46918898 | 0.45504234 | 0.96984875 |
| 10 | `julia-arellano` | 8.6108792630e-07 | 5.8496846123e-07 | 9.0253416829e-07 | 0.67933650 | 1.04813242 | 1.54287663 |
| 11 | `abigail-morrow` | 8.1580202504e-07 | 8.3004658791e-07 | 7.9833034761e-07 | 1.01746081 | 0.97858343 | 0.96178981 |
| 12 | `mary-lopez` | 8.1216353465e-07 | 4.6912194307e-07 | 4.1386439875e-07 | 0.57762005 | 0.50958259 | 0.88221070 |
| 13 | `dustin-merritt` | 8.0246962852e-07 | 1.9321473133e-07 | 1.7600326885e-07 | 0.24077513 | 0.21932702 | 0.91092055 |
| 14 | `riley-king` | 7.5062661153e-07 | 5.0971107157e-07 | 4.5385218073e-07 | 0.67904743 | 0.60463108 | 0.89041068 |
| 15 | `ryan-reilly` | 7.3989491511e-07 | 3.6074229115e-07 | 3.2137134554e-07 | 0.48755882 | 0.43434728 | 0.89086130 |
| 16 | `april-coleman` | 7.1800036494e-07 | 1.4573785734e-07 | 1.4033537354e-07 | 0.20297741 | 0.19545307 | 0.96293013 |
| 17 | `mark-sanchez` | 7.1389848699e-07 | 3.7275069076e-07 | 4.0721803884e-07 | 0.52213403 | 0.57041449 | 1.09246756 |
| 18 | `david-robinson` | 6.5441776087e-07 | 4.6356535677e-07 | 3.8026280436e-07 | 0.70836304 | 0.58107042 | 0.82030031 |
| 19 | `bryan-stanley` | 6.0999042262e-07 | 4.3116011739e-07 | 4.2703976533e-07 | 0.70683096 | 0.70007618 | 0.99044357 |
| 20 | `alexandra-hawkins` | 6.0147726799e-07 | 5.8289111848e-07 | 8.1070322722e-07 | 0.96909917 | 1.34785348 | 1.39083133 |
| 21 | `michael-phelps` | 5.9421273590e-07 | 7.4308161402e-08 | 1.2257325466e-07 | 0.12505313 | 0.20627840 | 1.64952614 |
| 22 | `kayla-conley` | 5.8621685639e-07 | 1.7707404254e-07 | 1.6635307531e-07 | 0.30206235 | 0.28377395 | 0.93945489 |
| 23 | `denise-dominguez` | 5.4679060213e-07 | 3.1550595736e-07 | 3.1097042097e-07 | 0.57701423 | 0.56871940 | 0.98562456 |
| 24 | `elizabeth-hess` | 5.2126722494e-07 | 2.1014918161e-07 | 1.9357619863e-07 | 0.40315058 | 0.37135693 | 0.92113706 |
| 25 | `jamie-taylor` | 4.7911464662e-07 | 1.3893298956e-07 | 1.2474801281e-07 | 0.28997859 | 0.26037195 | 0.89790059 |
| 26 | `jennifer-smith` | 4.6448406010e-07 | 2.7627891086e-07 | 3.2557971963e-07 | 0.59480816 | 0.70094918 | 1.17844579 |
| 27 | `tyler-davis` | 4.5911173174e-07 | 4.0755114128e-07 | 3.8331393171e-07 | 0.88769490 | 0.83490337 | 0.94052965 |
| 28 | `courtney-williams` | 4.5172902219e-07 | 5.6143346683e-07 | 5.5180277059e-07 | 1.24285454 | 1.22153491 | 0.98284624 |
| 29 | `rachel-myers` | 4.3823251872e-07 | 2.9902122378e-07 | 2.5292860073e-07 | 0.68233463 | 0.57715617 | 0.84585501 |
| 30 | `courtney-garcia` | 4.3402295091e-07 | 2.1243644710e-07 | 2.0573881443e-07 | 0.48945902 | 0.47402750 | 0.96847230 |
| 31 | `daniel-miller` | 3.9428400100e-07 | 1.9814595476e-07 | 1.8503281751e-07 | 0.50254627 | 0.46928817 | 0.93382082 |
| 32 | `ruben-watson` | 3.8453612206e-07 | 2.9869914897e-07 | 2.9042203664e-07 | 0.77677787 | 0.75525294 | 0.97228947 |
| 33 | `philip-sampson` | 3.7985995505e-07 | 4.7098450295e-07 | 4.5914742941e-07 | 1.23988985 | 1.20872817 | 0.97486738 |
| 34 | `jeremy-davis` | 3.7752204207e-07 | 1.6280598913e-07 | 2.0042573112e-07 | 0.43124896 | 0.53089809 | 1.23107100 |
| 35 | `molly-bates` | 3.6100931311e-07 | 1.6940552428e-07 | 1.5763893657e-07 | 0.46925527 | 0.43666169 | 0.93054189 |
| 36 | `christopher-thompson` | 3.5801150489e-07 | 1.4102053569e-07 | 1.3318386038e-07 | 0.39389945 | 0.37201000 | 0.94442884 |
| 37 | `matthew-schneider` | 3.3960063206e-07 | 1.9016715669e-07 | 2.4883857463e-07 | 0.55997292 | 0.73273884 | 1.30852550 |
| 38 | `russell-cox` | 3.3413726896e-07 | 1.0186683994e-06 | 9.0703770184e-07 | 3.04865244 | 2.71456610 | 0.89041508 |
| 39 | `tiffany-robertson` | 3.0547417396e-07 | 2.3884010147e-07 | 2.5995561259e-07 | 0.78186676 | 0.85099048 | 1.08840857 |
| 40 | `cody-jennings` | 2.9952582281e-07 | 3.1722134963e-07 | 3.0516096672e-07 | 1.05907847 | 1.01881355 | 0.96198118 |
| 41 | `michelle-jimenez` | 2.9550716363e-07 | 1.2004082350e-07 | 1.3779754227e-07 | 0.40621967 | 0.46630864 | 1.14792233 |
| 42 | `john-smith` | 2.9390042755e-07 | 1.4043720853e-07 | 1.3314281944e-07 | 0.47783942 | 0.45302016 | 0.94805943 |
| 43 | `dawn-martin` | 2.8571145094e-07 | 5.4252262771e-07 | 4.7371818823e-07 | 1.89884804 | 1.65803011 | 0.87317683 |
| 44 | `bryan-salas` | 2.8322978096e-07 | 2.6255170837e-07 | 2.2912612963e-07 | 0.92699188 | 0.80897612 | 0.87268954 |
| 45 | `dominic-nelson` | 2.8297770882e-07 | 1.8909281607e-07 | 1.2659687343e-07 | 0.66822513 | 0.44737401 | 0.66949594 |
| 46 | `scott-weber` | 2.7621751997e-07 | 1.7551488440e-07 | 1.8716613681e-07 | 0.63542271 | 0.67760415 | 1.06638327 |
| 47 | `christopher-rhodes` | 2.7611088171e-07 | 7.3816366353e-08 | 7.9107294937e-08 | 0.26734320 | 0.28650553 | 1.07167690 |
| 48 | `toni-dorsey` | 2.7182167628e-07 | 2.6127764841e-07 | 2.2753150120e-07 | 0.96120976 | 0.83706165 | 0.87084181 |
| 49 | `kevin-garrison` | 2.6451670010e-07 | 1.0815524831e-07 | 1.1429718683e-07 | 0.40887871 | 0.43209819 | 1.05678817 |
| 50 | `luke-king` | 2.6430905109e-07 | 5.4832770502e-07 | 5.4815728845e-07 | 2.07457029 | 2.07392553 | 0.99968921 |
| 51 | `matthew-walls` | 2.6262750907e-07 | 1.1676437595e-07 | 1.4055953557e-07 | 0.44460071 | 0.53520492 | 1.20378784 |
| 52 | `adrienne-davis` | 2.5977885798e-07 | 2.0719541283e-07 | 2.1812884654e-07 | 0.79758382 | 0.83967128 | 1.05276871 |
| 53 | `andrew-rogers` | 2.5448977681e-07 | 1.1668375066e-07 | 1.0305318199e-07 | 0.45850074 | 0.40494036 | 0.88318366 |
| 54 | `scott-campos` | 2.5112564117e-07 | 1.4299126860e-07 | 1.2670868443e-07 | 0.56940131 | 0.50456291 | 0.88612882 |
| 55 | `sean-johnston` | 2.4596980097e-07 | 2.5536530757e-07 | 2.2501909314e-07 | 1.03819781 | 0.91482406 | 0.88116548 |
| 56 | `james-fry` | 2.4428095458e-07 | 1.3563087009e-07 | 1.4515829605e-07 | 0.55522491 | 0.59422683 | 1.07024526 |
| 57 | `mary-mccall` | 2.4105278840e-07 | 2.3157491569e-07 | 2.0139654566e-07 | 0.96068134 | 0.83548731 | 0.86968204 |
| 58 | `jennifer-ortiz` | 2.3865953835e-07 | 1.0978904186e-07 | 1.2488081325e-07 | 0.46002369 | 0.52325926 | 1.13746155 |
| 59 | `daniel-kelly` | 2.3728375709e-07 | 2.6580900681e-07 | 2.9693612191e-07 | 1.12021577 | 1.25139675 | 1.11710331 |
| 60 | `lisa-phillips` | 2.3460488308e-07 | 3.2619701074e-07 | 3.3233675367e-07 | 1.39041015 | 1.41658072 | 1.01882219 |
| 61 | `joyce-castaneda` | 2.3339204347e-07 | 1.6624623811e-07 | 1.4696867368e-07 | 0.71230465 | 0.62970730 | 0.88404210 |
| 62 | `stephanie-page` | 2.2413209422e-07 | 1.1294179814e-07 | 1.0284591667e-07 | 0.50390730 | 0.45886296 | 0.91060987 |
| 63 | `greg-williams` | 2.2405643563e-07 | 1.7664964957e-07 | 1.7213301362e-07 | 0.78841587 | 0.76825740 | 0.97443167 |
| 64 | `diane-brennan` | 2.2200148919e-07 | 1.4242418445e-07 | 1.4426453276e-07 | 0.64154608 | 0.64983588 | 1.01292160 |
| 65 | `laura-quinn` | 2.0939856427e-07 | 1.5114666496e-07 | 1.2637194402e-07 | 0.72181328 | 0.60349957 | 0.83608821 |
| 66 | `samantha-robinson` | 2.0741352103e-07 | 1.8467841301e-07 | 2.1714423326e-07 | 0.89038753 | 1.04691455 | 1.17579651 |
| 67 | `melissa-robinson` | 2.0434876546e-07 | 3.7639622974e-07 | 3.8103695488e-07 | 1.84193053 | 1.86464036 | 1.01232936 |
| 68 | `kenneth-parker` | 1.9774699922e-07 | 6.1971789478e-08 | 7.0683910280e-08 | 0.31338928 | 0.35744618 | 1.14058204 |
| 69 | `brittney-brandt` | 1.9621560909e-07 | 1.4115200031e-07 | 1.6956761328e-07 | 0.71937192 | 0.86419023 | 1.20131215 |
| 70 | `amy-joseph` | 1.9451761091e-07 | 3.3035064462e-07 | 3.3304644376e-07 | 1.69830713 | 1.71216602 | 1.00816042 |
| 71 | `holly-hensley` | 1.9109585025e-07 | 2.5537011084e-07 | 3.4218439282e-07 | 1.33634566 | 1.79064272 | 1.33995475 |
| 72 | `thomas-johnson` | 1.9013978658e-07 | 8.4630656261e-08 | 1.0967558239e-07 | 0.44509704 | 0.57681553 | 1.29593208 |
| 73 | `jason-wolf` | 1.8710771599e-07 | 1.0568589914e-07 | 1.4392743708e-07 | 0.56483988 | 0.76922235 | 1.36184144 |
| 74 | `jimmy-brady` | 1.7551386122e-07 | 2.3167694962e-07 | 2.1379878490e-07 | 1.31999232 | 1.21813049 | 0.92283149 |
| 75 | `manuel-carson` | 1.7291061738e-07 | 1.2093798318e-07 | 1.4672302484e-07 | 0.69942485 | 0.84854838 | 1.21320879 |
| 76 | `vanessa-smith` | 1.7161059418e-07 | 3.0575546361e-07 | 1.9946986640e-07 | 1.78168175 | 1.16234005 | 0.65238365 |
| 77 | `kevin-martinez` | 1.7049279677e-07 | 1.5747079374e-07 | 1.5250972751e-07 | 0.92362139 | 0.89452300 | 0.96849532 |
| 78 | `laura-moran` | 1.6926523472e-07 | 8.1196510848e-08 | 6.9323732532e-08 | 0.47969987 | 0.40955683 | 0.85377724 |
| 79 | `martin-glass` | 1.5748106819e-07 | 1.5864858938e-07 | 1.9384808070e-07 | 1.00741372 | 1.23092942 | 1.22187081 |
| 80 | `kristina-wilkinson` | 1.5531097119e-07 | 9.8048822395e-08 | 7.9447858070e-08 | 0.63130648 | 0.51154054 | 0.81028875 |
| 81 | `richard-pierce` | 1.5187202962e-07 | 9.1069999542e-08 | 8.1552400388e-08 | 0.59964959 | 0.53698104 | 0.89549139 |
| 82 | `william-wang` | 1.5048752289e-07 | 7.7879882099e-08 | 8.5937223560e-08 | 0.51751720 | 0.57105880 | 1.10345857 |
| 83 | `melinda-young` | 1.4740010101e-07 | 2.7606225217e-07 | 2.8515000849e-07 | 1.87287695 | 1.93453062 | 1.03291923 |
| 84 | `sharon-leonard` | 1.4435170215e-07 | 1.9600702217e-07 | 2.0752443675e-07 | 1.35784351 | 1.43763069 | 1.05876021 |
| 85 | `cindy-smith` | 1.3974869262e-07 | 7.8402763393e-08 | 7.9907522377e-08 | 0.56102681 | 0.57179442 | 1.01919268 |
| 86 | `dawn-pollard` | 1.3868464066e-07 | 1.8192497464e-07 | 1.7572887145e-07 | 1.31178892 | 1.26711127 | 0.96594144 |
| 87 | `donald-warner` | 1.3830148760e-07 | 1.4326724340e-07 | 1.5337292325e-07 | 1.03590530 | 1.10897522 | 1.07053727 |
| 88 | `anthony-harris` | 1.3507465724e-07 | 2.1942427963e-07 | 2.0407389911e-07 | 1.62446668 | 1.51082300 | 0.93004247 |
| 89 | `yesenia-durham` | 1.3373596630e-07 | 8.2191860429e-08 | 9.2399361051e-08 | 0.61458307 | 0.69090884 | 1.12419114 |
| 90 | `stephanie-garza` | 1.3332262938e-07 | 1.3596309145e-07 | 1.4344828969e-07 | 1.01980506 | 1.07594855 | 1.05505316 |
| 91 | `marc-allison` | 1.2930831872e-07 | 1.0351881485e-07 | 1.3714861780e-07 | 0.80055805 | 1.06063260 | 1.32486658 |
| 92 | `joshua-keller` | 1.2788436266e-07 | 1.2636661495e-07 | 1.1829543922e-07 | 0.98813187 | 0.92501880 | 0.93612889 |
| 93 | `larry-mendoza` | 1.2395562976e-07 | 1.1710344694e-07 | 1.2573548247e-07 | 0.94472068 | 1.01435879 | 1.07371291 |
| 94 | `wendy-clayton` | 1.2104740676e-07 | 6.7380959479e-08 | 6.3784966642e-08 | 0.55664934 | 0.52694203 | 0.94663191 |
| 95 | `crystal-taylor` | 1.0933942463e-07 | 6.5127075288e-08 | 7.0412227160e-08 | 0.59564128 | 0.64397839 | 1.08115138 |
| 96 | `tracy-cook` | 1.0591919875e-07 | 9.4584869714e-08 | 1.1862209703e-07 | 0.89299080 | 1.11993008 | 1.25413396 |
| 97 | `lori-kennedy` | 9.9228159911e-08 | 9.2939828278e-08 | 1.1089222340e-07 | 0.93662755 | 1.11754792 | 1.19316148 |
| 98 | `diane-ortiz` | 9.5054716098e-08 | 1.3390385334e-07 | 1.3480349992e-07 | 1.40870289 | 1.41816740 | 1.00671860 |
| 99 | `melissa-smith` | 8.7233132717e-08 | 2.5116762004e-07 | 2.6596785574e-07 | 2.87926860 | 3.04893161 | 1.05892573 |
| 100 | `mark-green` | 7.5980281622e-08 | 6.1750689895e-08 | 6.9315539974e-08 | 0.81271994 | 0.91228327 | 1.12250632 |

---

*Data lane, blind half. Generated 2026-08-19 from `report_arm{A,B,C}.json` only.*
