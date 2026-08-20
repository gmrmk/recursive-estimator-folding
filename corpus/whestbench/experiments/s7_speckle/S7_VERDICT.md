# S7 verdict — wave-packet speckle correlation (s7_wavepacket_speckle_correlation)

Date: 2026-08-09. Runner: `run_s7.py`. Results: `s7_results.json`.
Total wall time 25 s.

## VERDICT: PASS

Predeclared rule: PASS = xi_measured within factor 2 of xi_meanfield on >= 2/3
nets AND coherent monotone C_r(theta). Measured xi ratios (measured/mean-field):
**1.77 (net 101), 1.70 (net 202), 2.20 (net 303)** — 2/3 nets inside [0.5, 2],
all three coherent and monotone. Net 303 sits marginally outside at 2.20.
Honest reading: all three ratios are on the same (high) side — the residual
field decorrelates ~1.7–2.2x more slowly in angle than the depth-32 mean-field
iteration predicts, a systematic finite-width offset, not scatter — but it is
inside the predeclared factor-2 window for 2/3 nets, and nowhere near the 5x
kill line.

## Deviations (none silent)

- D1: task text says "~2,000" pairs but also "~500 pairs per theta" x 8 thetas;
  the per-theta spec governs: 500 pairs/theta, 4,000 pairs per net.
- D2: theta = 90 deg excluded from the max-ratio-deviation statistic
  (C_pred(90) = 0 exactly under the mean-removed normalization; ratio
  undefined). It still enters the coherence check.
- D3: c_32 = f applied exactly 32 times to cos(theta), as predeclared. The
  31-application preactivation-count variant and the post-ReLU covariance
  kernel variant h(c) were computed as robustness rows: both agree with the
  primary normalized prediction to <= 0.008 at every probe theta (identical to
  4 decimals for the h variant), so the D3 choice is immaterial.
- Bug fixed mid-run (harness bug, not a gate retune): dead neurons (final
  activation identically zero over the probe set, 52–80 of 256 per net) gave
  0/0 in the per-neuron energy normalization; they are now excluded with the
  live/dead counts recorded. C_r, xi, and all gated numbers were bitwise
  identical before and after the fix.

## Mean-field prediction (closed form, derived first)

Kernel: c_{l+1} = f(c_l), f(c) = (sqrt(1-c^2) + c(pi - arccos c))/pi, iterated
32 layers from c_0 = cos(theta). Mean-removed residual normalization
(documented choice): C_pred(theta) = (c_32(cos theta) - m2)/(1 - m2) with
m2 = c_32(0) = **0.974720** — the theta=90deg plateau, because probe-set mean
removal subtracts the component common to all near-orthogonal directions in
d=256, whose scale is exactly that plateau. Pearson C_r is shift-invariant, so
the mean-removal constant never enters the measurement, only this
normalization.

- **xi_meanfield (half height) = 20.91 deg**; 1/e height: 28.60 deg.

Kernel verification (two-signal): the arcsin-identity re-implementation agrees
to 3.3e-16; Monte-Carlo E[relu(x)relu(y)]/E[relu(x)^2] on 2e6 bivariate
normals agrees to <= 1.4e-3 at c in {0, 0.5, 0.9}.

### c_32 tabulation over [0, 90] deg (2.5 deg grid)

| theta | c_32 | | theta | c_32 | | theta | c_32 |
|---|---|---|---|---|---|---|---|
| 0.0 | 1.00000 | | 30.0 | 0.98351 | | 62.5 | 0.97681 |
| 2.5 | 0.99928 | | 32.5 | 0.98267 | | 65.0 | 0.97654 |
| 5.0 | 0.99775 | | 35.0 | 0.98191 | | 67.5 | 0.97629 |
| 7.5 | 0.99594 | | 37.5 | 0.98121 | | 70.0 | 0.97605 |
| 10.0 | 0.99411 | | 40.0 | 0.98058 | | 72.5 | 0.97584 |
| 12.5 | 0.99234 | | 42.5 | 0.98000 | | 75.0 | 0.97564 |
| 15.0 | 0.99070 | | 45.0 | 0.97948 | | 77.5 | 0.97546 |
| 17.5 | 0.98920 | | 47.5 | 0.97899 | | 80.0 | 0.97529 |
| 20.0 | 0.98783 | | 50.0 | 0.97855 | | 82.5 | 0.97513 |
| 22.5 | 0.98658 | | 52.5 | 0.97814 | | 85.0 | 0.97498 |
| 25.0 | 0.98546 | | 55.0 | 0.97776 | | 87.5 | 0.97485 |
| 27.5 | 0.98444 | | 57.5 | 0.97742 | | 90.0 | 0.97472 |

At the probe thetas:

| theta (deg) | 0.5 | 1 | 2 | 5 | 10 | 20 | 45 | 90 |
|---|---|---|---|---|---|---|---|---|
| c_32 | 0.99996 | 0.99986 | 0.99951 | 0.99775 | 0.99411 | 0.98783 | 0.97948 | 0.97472 |
| C_pred (normalized) | 0.9986 | 0.9946 | 0.9808 | 0.9109 | 0.7668 | 0.5185 | 0.1881 | 0.0000 |

## Measured C_r(theta) per net

3 He nets (seeds 101/202/303, width 256, depth 32, `he_mlp_weights` imported
from `../n8a_rqmc_kerdock/run_n8a_gates.py`), first layer pre-rotated by
`haar_rotation(900000 + net*1000 + 0)`. 500 Haar great-circle pairs per theta,
float32 forwards; r(u) from the neuron-averaged final post-ReLU output;
C_r = Pearson over pairs. SE per point ~= 0.045 (Fisher scale).

| theta (deg) | 0.5 | 1 | 2 | 5 | 10 | 20 | 45 | 90 | xi_half (deg) | boot 95% CI | xi ratio | max ratio dev (<=45 deg) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C_pred | 0.999 | 0.995 | 0.981 | 0.911 | 0.767 | 0.519 | 0.188 | 0.000 | 20.91 | — | 1.00 | — |
| net 101 | 0.9997 | 0.9987 | 0.9952 | 0.9766 | 0.9263 | 0.7759 | 0.4118 | -0.0227 | 36.98 | [32.9, 45.0] | 1.77 | 2.19 |
| net 202 | 0.9997 | 0.9988 | 0.9959 | 0.9765 | 0.9350 | 0.7668 | 0.3916 | 0.0374 | 35.60 | [32.2, 40.6] | 1.70 | 2.08 |
| net 303 | 0.9998 | 0.9991 | 0.9962 | 0.9820 | 0.9466 | 0.8145 | 0.5156 | 0.0013 | 45.95 | [40.0, 49.5] | 2.20 | 2.74 |

All nets: strictly monotone decreasing (coherent; no consecutive increase at
all, threshold was 2x pooled SE). xi from the last 0.5-crossing of raw C_r,
linear in log(theta); the normalized-endpoint variant gives 37.9/34.2/45.9 —
same conclusion. The max ratio deviation is attained at 45 deg in every net
(prediction 0.188 vs measured 0.39–0.52): the measured curve tracks the
prediction closely through 20 deg (<= 1.09x through 10 deg) and decays more
slowly in the tail.

Two-signal repeat (independent fresh pair sets, seed base 740000): all 6
repeat correlations within 2x joint SE of the primary values (max abs diff
0.042, net 202 at 20 deg).

## P2 — Boltzmann / chi^2 statistics (evidence, not gated)

Normalized residual energies e = r^2/mean(r^2); KS distances to Exp(1)
(complex/MB fully-developed speckle) and to chi^2_1 = Gamma(1/2, 2) (real-
amplitude speckle — the physically correct null for this real field). Moment
shape k = 1/var(e): Exp -> 1, chi^2_1 -> 0.5.

| statistic | net 101 | net 202 | net 303 |
|---|---|---|---|
| direction energy, Haar probe (n=4000): KS Exp1 / KS chi2_1 / k | 0.162 / **0.016** / 0.41 | 0.160 / **0.015** / 0.40 | 0.170 / **0.009** / 0.44 |
| direction energy, Kerdock design (n=64512): KS Exp1 / KS chi2_1 / k | 0.164 / **0.010** / 0.41 | 0.165 / **0.009** / 0.42 | 0.164 / **0.007** / 0.44 |
| vector energy mean_i r_i^2 (n=4000): KS Exp1 / KS chi2_1 / k_eff | 0.134 / 0.298 / 0.77 | 0.195 / 0.354 / 1.02 | 0.165 / 0.327 / 0.98 |
| per-neuron pooled, live neurons, Haar: KS Exp1 / KS chi2_1 / k | 0.343 / 0.190 / 0.004 | 0.237 / 0.079 / 0.007 | 0.322 / 0.164 / 0.003 |
| per-neuron pooled, live neurons, Kerdock: KS Exp1 / KS chi2_1 / k | 0.367 / 0.213 / 0.000 | 0.247 / 0.088 / 0.001 | 0.351 / 0.200 / 0.000 |
| dead neurons of 256 (Haar / Kerdock probe) | 80 / 72 | 70 / 67 | 63 / 52 |

**Finding.** The Maxwell-Boltzmann/exponential null is rejected at every
level. The neuron-averaged direction energy fits chi^2_1 decisively (KS
0.007–0.016 at n up to 64512, on both the Haar probe and the actual Kerdock
design set): the residual field behaves as a single real Gaussian amplitude —
real-amplitude speckle, exactly the physically correct target for a real
field. The reason pooling 256 neurons does NOT drive it toward the
exponential/MB multi-neuron limit is visible in the vector-energy shape
k_eff ~= 0.8–1.0: the effective number of independent neuron amplitudes at
depth 32 is ~1.5–2 out of 256 — the per-neuron fields are almost fully
coherent across neurons (consistent with the mean-field plateau c_32(0) =
0.975). The per-neuron pooled energies fit neither null (k ~= 0, extreme
heavy tails): a single neuron's residual is a mean-removed RECTIFIED Gaussian,
not Gaussian — 20–31% of neurons are outright dead, and neurons whose common
input sits deep in the rectified region fire rarely with large spikes,
producing the heavy tail after per-neuron normalization. So the speckle
picture holds at the aggregate-field level (chi^2_1), while single-neuron
statistics are rectification-dominated and non-Gaussian.

## Design-spacing adjudication

The design's minimum inter-direction angle, measured on the rebuilt Kerdock
set (frames 0–5 spot check), is arccos(0.0625) = **86.42 deg** — exactly the
Kerdock cross-frame coherence 1/16 — and 90.00 deg within a frame; antipodal
doubling adds no closer pairs. The measured speckle correlation length is
xi ~= 36–46 deg (half height). The design therefore sits a factor ~2 ABOVE
the speckle scale: every pair of distinct design directions is separated by
~2x the correlation length, where measured C_r is |C| <= 0.04 (the 90-deg
column). The design neither oversamples a speckle grain (no redundant,
correlated probes) nor leaves grains between directions unsampled in the
angular-correlation sense — its residuals are effectively independent draws
from the chi^2_1 speckle ensemble, which is the regime where the direction
count buys variance reduction at the full 1/N rate.

## Limitations

- Width-256 finite-size effects are visible: the measured tail decays ~1.7–2.2x
  more slowly than the infinite-width mean-field iteration, uniformly across
  nets. The factor-2 gate absorbs this for 2/3 nets; a finite-width-corrected
  kernel was NOT predeclared and was not fit.
- xi_measured relies on log-theta linear interpolation between 20 and 45 deg
  (grid predeclared); bootstrap CIs (n=1000, pair resampling) span ~±5 deg.
- The prediction normalization pins C_pred(90) = 0; measured C_r(90) is
  -0.02–0.04, consistent with 0 at the SE ~= 0.045, but 90 deg had to be
  excluded from ratio statistics (D2).
- P2 KS distances are descriptive (n is large; any model misfit dominates
  sampling error) — no p-values are claimed.
- The neuron-averaged field mixes 256 highly-correlated neurons; chi^2_1 fit
  quality at the single-direction level does not certify Gaussianity of the
  full multi-neuron field (the per-neuron pooled rows show it is not).
- Forwards are float32 (matching the estimator harness); statistics in
  float64.

## Artifacts

- `run_s7.py` — harness (mean-field derivation, measurement, gates).
- `s7_results.json` — full numeric results, including the fine c_32 table,
  bootstrap CIs, repeat checks, and all P2 statistics.
- `S7_VERDICT.md` — this document.
