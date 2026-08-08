# M181 G0 notes — terminal rectified-Gaussian smoothing

Date: 2026-08-08. Governing predeclaration: `M181_PREDECLARATION.md`.
Runner: `run_m181_g0.py`. Results: `m181_g0_results.json`.

## VERDICT: ALL THREE ARMS KILLED (kills final per arm)

| arm | aggregate MSE ratio vs Arm 0 (geomean, noise-subtracted) | reduction | bootstrap 95% CI | gate |
|---|---|---|---|---|
| Arm 1 univariate smoothing | **4.2420** | -324.2% | [3.7740, 4.9288] | **KILL** |
| Arm 2 pair-propagation | **7.7698** | -677.0% | [6.7433, 9.2701] | **KILL** |
| Arm 3 CV form | **1.0567** | -5.7% | [1.0318, 1.0888] | **KILL** |

No arm reached the 10% kill bar, let alone the 15% promote bar. Arms 1 and 2
are not merely short of the gate — they are 4.2x and 7.8x WORSE than the
baseline. The predeclaration's honesty bound named this exact failure branch:
"the T2/N5 higher-order-structure findings cut both ways (they say the law is
NOT Gaussian marginally)". Measured: they cut against.

## Deviations (loudly, first)

1. **Plain numpy, no flopscope metering** — the sanctioned G0 deviation
   (N8a/M180 precedent).
2. **16 rotation seeds** (>= the predeclared 12); no timebox reduction was
   needed (total wall ~15 min including truth).
3. **Truth machinery**: the N8c 3.5M chunked iid MC, reduced to the scored
   final-layer row only (sums/sumsq of final activations), with per-chunk
   seeding (`default_rng((9000+net)*1e6 + chunk)`) for clean resumability.
   Statistically identical to one stream: every sample is iid N(0, I).
4. **Truth noise floor: measured, not the forecast.** The predeclaration
   guessed ~6e-9 (~0.02/3.5e6); the measured per-sample final variances give
   1.23e-8 / 2.22e-8 / 1.50e-8 for nets 101/202/303 (2-4x the guess — the
   per-sample final variance is ~0.043-0.078, not 0.02). The MEASURED per-net
   floor was subtracted from every MSE, per the predeclaration's instruction
   to subtract the noise floor. Zero bootstrap draws hit the negative-MSE
   floor guard (`floored_draws = 0`), so the subtraction never distorted a
   ratio.
5. **Arm 3 exact construction** (the predeclared sentence made operational):
   split the 126 Kerdock frames 101 train / 25 holdout (frame % 5 == 4 ->
   holdout; antipodal halves stay with their base direction), i.e. 51,712 /
   12,800 samples = 80.16% / 19.84% (nominal 80/20 is not integral in
   frames). S80/S20/Sfull = per-neuron means of ReLU(z) on train/holdout/all;
   A80 = Arm-1 analytic from train-split moments; D = A80 - S80; scalar
   lambda per (net, seed) = argmin_l ||(S80 + l D) - S20||^2 =
   D.(S20-S80)/D.D; estimate = Sfull + lambda*D. HONESTY NOTE: exact
   unbiasedness would require fixed lambda AND E[D] = 0; here E[D] =
   bias(A80), so the arm is bias-ADAPTIVE (lambda -> 0 when the smoothing
   bias is material), not exactly unbiased. This is the closest operational
   form of the predeclared sentence; it behaved exactly as designed (below).
6. **Arm 2 ran the FULL 32,640-pair M179 `relu_moments` set** at layer 30
   (M178 certified provider underneath) at 3.9 s/seed — the predeclared
   diagonal+top-k fallback was NOT needed; there is no Arm-2 implementation
   bound on this verdict.
7. **Phi/phi in Arms 1/3** via `math.erf` (correctly rounded ~1 ulp,
   vectorized with `frompyfunc`); cross-checked against the M179 univariate
   backbone `asm.relu_gaussian_mean` to max |diff| = 1.5e-16 in the probe.
   Arm 2 uses the M179/M178 kernels exclusively.

## Config

3 synthetic He f32 256x32 nets (seeds 101/202/303, t3-style; M180 Arm A
machinery verbatim); n = 64,512 Kerdock directions per rotation seed
(126 frames x 256, antipodal, exact chi-mean radius 15.984383, one shared
Haar rotation per seed, seed formula `900000 + net*1000 + rep`); 16 rotation
seeds; MC truth 3.5M iid samples per net; bootstrap 4000 paired draws over
rotation-seed indices, shared across arms per draw; geomean aggregation over
nets (M180 conventions).

## Per-arm, per-net MSE and bias/variance decomposition

All values final-layer, mean over the 256 neurons. `bias^2 = MSE_raw -
var(ddof=1 across seeds) - truth_noise` (N8c decomposition). Ratios are on
noise-subtracted MSE vs Arm 0.

### Net 101 (truth noise 1.229e-8)

| arm | MSE raw | variance | bias^2 | bias share | ratio vs Arm 0 |
|---|---|---|---|---|---|
| 0 baseline | 1.997e-07 | 2.035e-07 | -1.61e-08 (~0) | -0.08 | 1.000 |
| 1 univariate | 9.868e-07 | 2.025e-07 | 7.720e-07 | 0.78 | 5.200 |
| 2 pair-prop | 1.820e-06 | 2.015e-07 | 1.606e-06 | 0.88 | 9.646 |
| 3 CV | 2.153e-07 | 2.184e-07 | -1.54e-08 (~0) | -0.07 | 1.083 |

lambda (arm 3): mean -0.035, sd 0.150 across seeds.

### Net 202 (truth noise 2.219e-8)

| arm | MSE raw | variance | bias^2 | bias share | ratio vs Arm 0 |
|---|---|---|---|---|---|
| 0 baseline | 5.872e-07 | 5.690e-07 | -3.99e-09 (~0) | -0.01 | 1.000 |
| 1 univariate | 1.792e-06 | 5.691e-07 | 1.201e-06 | 0.67 | 3.132 |
| 2 pair-prop | 3.568e-06 | 5.702e-07 | 2.975e-06 | 0.83 | 6.275 |
| 3 CV | 5.984e-07 | 5.808e-07 | -4.62e-09 (~0) | -0.01 | 1.020 |

lambda (arm 3): mean 0.005, sd 0.118.

### Net 303 (truth noise 1.504e-8)

| arm | MSE raw | variance | bias^2 | bias share | ratio vs Arm 0 |
|---|---|---|---|---|---|
| 0 baseline | 2.369e-07 | 2.178e-07 | 4.07e-09 (~0) | 0.02 | 1.000 |
| 1 univariate | 1.055e-06 | 2.171e-07 | 8.230e-07 | 0.78 | 4.688 |
| 2 pair-prop | 1.734e-06 | 2.169e-07 | 1.502e-06 | 0.87 | 7.749 |
| 3 CV | 2.521e-07 | 2.328e-07 | 4.27e-09 (~0) | 0.02 | 1.068 |

lambda (arm 3): mean 0.040, sd 0.124.

## Mechanism autopsy — why the hybrid dies

The predeclared mechanism claimed two wins: bias stays small (one terminal
Gaussian-closure step from an empirical start) and variance drops ("two
smooth moments replace a kinked average"). BOTH halves failed, independently:

1. **The bias is not small.** Arm 1's bias^2 alone is 4-6x Arm 0's ENTIRE
   MSE on every net (bias share 0.67-0.78 of arm-1 MSE). The terminal
   pre-activation law after 31 ReLU layers is materially non-Gaussian, and
   the rectified-Gaussian identity inherits that error in full. Arm 2, which
   stacks TWO rectification steps under Gaussian closure, roughly doubles
   arm 1's bias^2 (share 0.83-0.88) — the same accumulation direction T2
   measured layerwise, now visible in a single terminal step because the
   per-step closure error is large, not because steps accumulate.
2. **There is no variance win to trade for.** var(arm1) = var(arm0) to
   within 1% on every net (e.g. net 101: 2.025e-7 vs 2.035e-7). The
   empirical (mu_i, sigma_i) are computed from the same n samples, and their
   sampling noise passes through the smooth functional at the same magnitude
   as the kinked average's own noise. Even at zero bias, G0 would have found
   ~0% reduction — the kink-noise premise itself is wrong at n = 64,512.
3. **Arm 3 worked exactly as designed and therefore killed itself.** Its
   holdout-fit lambda collapsed to ~0 (per-net means -0.035 / 0.005 /
   0.040) — an internal, truth-free measurement inside every replicate that
   the analytic direction D is bias-dominated. What remains is the sample
   mean plus lambda-fitting noise: bias^2 ~ 0, variance up 3-7%, net MSE
   +5.7% [CI +3.2%, +8.9%]. The safety valve functioned; there was simply
   nothing on the other side of it.

## Verification signals (second signals, per the uncertainty protocol)

- **Arm 0 anchor**: its measured bias^2 is ~0 on all three nets (slightly
  negative twice — within decomposition estimator noise), matching the
  analytic exact-unbiasedness argument (positive homogeneity + Haar rotation
  + exact mean-chi radius). The harness reproduces a known-true fact.
- **Bias-source check** (`verify_m181_bias_source.py`): the SAME arm-1/arm-2
  constructions applied to 262,144 fresh iid N(0,I) samples (no Kerdock, no
  antipodal, disjoint seed stream) reproduce the same deviation-from-truth
  field: cosine 0.9684 (arm 1) and 0.9838 (arm 2) against the Kerdock-run
  deviation, with matching magnitudes (rms 9.66e-4 vs 8.93e-4; 1.38e-3 vs
  1.28e-3), while the plain iid MC mean sits at the 2.5e-4 noise scale. The
  bias is a property of the terminal law, not of the sampling-path plumbing.
- **Internal consistency**: arm 3's lambda ~ 0 is an independent holdout
  measurement agreeing with the truth-based scoring; `floored_draws = 0`;
  the probe's rect_mean vs M179-backbone check passed at 1.5e-16.

## Disposition

M181 is KILLED at G0 on all three predeclared arms; kills are final per arm
per the firewall. The T2-killed closure component cannot be rescued by
composing it with the promoted Kerdock sampler at the terminal layer: under
the sampling distribution the terminal pre-activation law is far enough from
Gaussian that one closure step costs 4-8x the baseline's total MSE, and the
hoped-for variance reduction from smoothing does not exist at matched n.
G1-G4 do not open. No retuning was performed after any gate read.

## Files

- `run_m181_g0.py` — gate runner (probe / per-net / aggregate subcommands)
- `m181_g0_results.json` — machine-readable per-net tables, CIs, verdicts
- `m181_truth_net{101,202,303}.npz` — 3.5M-sample truth means + noise floors
- `m181_g0_partial_net{101,202,303}.npz` — per-seed estimate stacks (4 arms)
- `verify_m181_bias_source.py` — post-verdict iid-MC bias-source check
- `M181_G0_NOTES.md` — this file
