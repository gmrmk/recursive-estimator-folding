# S12 verdict — finite-width-corrected correlation kernel (capstone)

Ledger id: `s12_finite_width_kernel_capstone`. Date: 2026-08-09. Non-candidate
writeup capstone: pure math + comparison to committed S7/S8 data.
Artifacts: `run_s12.py`, `s12_results.json`, this file. Wall time ~40 s/run.
Sources read (read-only): `../s7_speckle/s7_results.json`, `S7_VERDICT.md`,
`../s8_layer_profile/s8_results.json`, `S8_VERDICT.md`, and the fleet brief
`../../sources/research_physics_depth_finitewidth_20260810.md`.

## VERDICT

- **Route (a) — Jakub-Nica finite-width angle flow: PARTIAL.**
  Transmission gate PASSES (typical d(theta_{l+1})/d(theta_l) = **0.890**,
  inside [0.83, 0.91], vs S8's fitted 0.869-0.879). Curve gate FAILS
  (4 of 7 angles inside CI on every net; needed >= 5 on >= 2/3): the
  deterministic flow leaves the normalized correlation curve essentially at
  mean field and cannot produce the measured slow tail.
- **Route (b) — D/n kernel fluctuation: DERIVED.**
  Expected half-height inflation = **1.577 +/- 0.001** (MC on the exact
  mean-field curve), analytic exponential-tail cross-check **1.868 =
  exp(5D/n)**; both inside the predeclared gate [1.5, 2.4]; measured
  1.70 / 1.77 / 2.20.
- Predeclared EMPIRICAL fallback (both routes miss) does NOT fire.

Combined reading for the writeup: the finite-width **mean drift** (route a)
quantitatively reproduces S8's per-layer defect transmission ~0.87 but not
S7's widened angular correlation; the finite-width **fluctuation** (route b)
reproduces S7's 1.7-2.2x correlation-length inflation in magnitude. The two
committed anomalies are explained by two different moments of the same
finite-width correction.

## Deviations from the predeclaration

None. Operationalizations fixed in the `run_s12.py` header before the first
run (the task text left them open):

- O1. CI half-width for the hit count = 2 x committed `se_per_theta` =
  0.0897 (>= the task's +-0.045 floor). Sensitivity rows at +-0.045 and
  +-0.127 reported unGated (hit counts 3/3/3 and 4/4/4 — same gate outcome
  under every band).
- O2. "Typical" transmission := geometric mean of d(theta_{l+1})/d(theta_l)
  over l = 1..31 of the theta_0 = 90 deg trajectory (S8's probe design is
  mutually ~90 deg). l = 0 excluded: the sin^2 parameterization folds exactly
  at pi/2, so dtheta_1/dtheta_0 there is a sign artifact (value -0.166,
  reported).
- O3. Route (b) gate quantity := MC expectation of the half-height ratio on
  the exact mean-field curve under the predeclared model (B2 below);
  the closed-form exponential-tail value exp(5D/n) is the cross-check.
- O4. E[G] = 1 normalization for the kernel fluctuation factor (forced by the
  compounding derivation: E[K_D] is exactly the mean-field kernel).

Notes (not deviations):

- N1. Re-fitting S8's committed `v_l_mean` (OLS of ln v_l on l) gives
  rho = 0.8758 / 0.8695 / 0.8793 for nets 101 / 202 / 303. The S8 verdict
  quotes 0.869 / 0.879 / 0.876 — identical as a multiset to < 0.001 but with
  a different per-net attribution; the S8 line appears order-permuted. The
  gate band [0.83, 0.91] is unaffected.
- N2. After the first full run, one REPORTED summary was added to the
  harness (half-height xi of the already-predeclared route-(a) curves on a
  fine theta_0 grid). No gate or arm was touched; all gated numbers were
  bitwise identical between the two runs (seeded MC).

## Route (a): derivation and comparison

**Recursion (Jakub & Nica arXiv:2302.09712, Approximation 1, as quoted in the
fleet brief; GATED arm verbatim):**

    ln sin^2 theta_{l+1} = ln sin^2 theta_l - (2/(3pi)) theta_l - rho(n)
    rho(n) = ln((n+5)/(n-1)) - 10n/(n+5)^2 + 6n/(n-1)^2 = 2/n + O(1/n^2)

n = 256: rho = 9.2984e-3 (n*rho = 2.380; the O(1/n^2) term is a 19% effect at
this width; the rho = 2/n = 7.8125e-3 variant is reported and changes nothing).
Iterated D = 32 steps from each S7 probe angle.

**sin^2-to-correlation mapping (documented + justified).** theta_l is by
definition the angle between the two activation vectors at layer l, so the raw
output correlation is c_raw(theta_0) = cos theta_32(theta_0). S7's committed
measurement is mean-removed and normalized; the coherent component removed is
the theta-independent plateau attained at the design's ~90 deg separations
(S7's own documented normalization — applying the identical functional
(c32 - c32(90))/(1 - c32(90)) to S7's committed mean-field c32 values
reproduces S7's committed C_pred to 0.0). The finite-width prediction uses the
same functional with the flow's own plateau:

    c_pred_fw(theta_0) = (cos theta_32(theta_0) - cos theta_32(90deg)) / (1 - cos theta_32(90deg))

The flow's raw plateau is cos theta_32(90 deg) = 0.9808 (mean-field committed:
0.9747; S7's measured coherence plateau: 0.9747).

**Predicted vs measured (CI half-width 0.0897; hits bold-equivalent marked `*`):**

| theta_0 (deg) | 0.5 | 1 | 2 | 5 | 10 | 20 | 45 |
|---|---|---|---|---|---|---|---|
| mean-field C_pred (S7) | 0.9986 | 0.9946 | 0.9808 | 0.9109 | 0.7668 | 0.5185 | 0.1881 |
| **c_pred_fw (verbatim flow)** | 0.9986 | 0.9947 | 0.9809 | 0.9097 | 0.7579 | 0.4859 | 0.1258 |
| net 101 meas (resid) | 0.9997 (-.001)* | 0.9987 (-.004)* | 0.9952 (-.014)* | 0.9766 (-.067)* | 0.9263 (-.168) | 0.7759 (-.290) | 0.4118 (-.286) |
| net 202 meas (resid) | 0.9997 (-.001)* | 0.9988 (-.004)* | 0.9959 (-.015)* | 0.9765 (-.067)* | 0.9350 (-.177) | 0.7668 (-.281) | 0.3916 (-.266) |
| net 303 meas (resid) | 0.9998 (-.001)* | 0.9991 (-.004)* | 0.9962 (-.015)* | 0.9820 (-.072)* | 0.9466 (-.189) | 0.8145 (-.329) | 0.5156 (-.390) |

Hits: **4/7 on every net** (0.5-5 deg in, 10-45 deg out). Curve gate
(>= 5/7 on >= 2/3 nets): **FAIL**. Every unGated variant gives the same 4/7 —
rho = 2/n; the brief's refined mu(theta,n) (adds the -8theta/(15 pi n) and
theta^2 terms); the "hybrid" flow (exact mean-field log-sin^2 contraction
lambda(theta) = ln[sin^2 arccos f(cos theta) / sin^2 theta] in place of its
small-angle expansion -(2/(3pi))theta, keeping -rho(n)); and both rho = 0
limits. At 20 deg the five variants span C_pred 0.461-0.535 versus measured
0.767-0.815: the deterministic drift correction moves the normalized curve by
at most ~0.03 from mean field. Reported diagnostic: the half-height of the
flow's own curve is xi = 19.39 deg (verbatim; ratio 0.93 of mean field — the
verbatim flow slightly NARROWS the normalized curve, an artifact of its
small-angle truncation over-contracting the 90 deg reference trajectory) and
21.72 deg (hybrid; ratio 1.04). Measured: 36-46 deg. Conclusion: the
finite-width mean drift does not explain fact F2 at all; a theta-independent
extra contraction largely cancels in the normalized curve.

**Perturbation transmission (linearized flow).** Differentiating one step of
the recursion:

    T_l = d theta_{l+1} / d theta_l
        = exp(-(b*theta_l + rho)/2) * (cos theta_l - (b/2) sin theta_l) / cos theta_{l+1},   b = 2/(3pi)

(checked against central finite differences to 2.8e-9 max relative error).
Along the theta_0 = 90 deg ambient trajectory (theta descends 90 -> 57.4 ->
48.9 -> ... -> 11.2 deg over 32 layers), T_l runs 0.61 (l=1) up to 0.95 (l=31);
**typical (geomean l=1..31) = 0.8898** — GATE [0.83, 0.91]: **PASS** — against
S8's fitted per-layer defect transmission 0.8695-0.8793 (refit here from the
committed v_l tables; S8 committed quote 0.869-0.879). Sensitivities: arithmetic
mean 0.893, median 0.922, mid-network (l=8..24) geomean 0.917, 45 deg-trajectory
geomean 0.915, |T| geomean incl. the l=0 fold artifact 0.844, per-layer sin^2
flow factor exp(-b theta_l - rho) geomean 0.903. The variance-transmission
reading T^2 = 0.79 falls below the band — the identification of S8's v_l decay
rate with the first power of the angular transmission is the reading the data
supports (0.890 vs 0.869-0.879, within 2.4%); which power is physically forced
remains open (S8's v_l is a variance-like observable, so the naive square would
give 0.79; the near-coincidence of the first power is reported, not claimed as
derived).

**Route (a) verdict: PARTIAL** (transmission leg lands inside the gate and
within 2.4% of the measured 0.87; curve leg fails on all nets).

## Route (b): derivation and comparison

**Reconstructed 5-line kernel-fluctuation computation (assumptions stated).**
For bias-free He-init ReLU at width n, given layer-l activations with diagonal
kernel K_l, the next preactivations are z_i iid N(0, K_l) exactly, and

    K_{l+1} = (2/n) sum_i relu(z_i)^2
    E[relu(z)^2] = K/2,  E[relu(z)^4] = 3K^2/2   (Gaussian moments; verified by
        199-node Gauss-Hermite quadrature to <= 1e-16)
    => Var[relu(z)^2] = 5K^2/4
    => Var[K_{l+1} | K_l] = (2/n)^2 * n * 5K_l^2/4 = (5/n) K_l^2
    => E[K_D^2]/E[K_D]^2 = (1 + 5/n)^D = 1.857 ~ exp(5D/n) = exp(0.625) = 1.868,
       Var[ln K_D] ~ 5D/n = 0.625            at D/n = 32/256 = 0.125.

Assumptions: (i) the per-layer multiplicative factors are independent across
layers (true for the diagonal-kernel chain, which is exactly Markov);
(ii) E[K_D] equals the mean-field kernel (exact — each factor has mean 1),
fixing the E[G] = 1 normalization below. Verification by an
exact-in-distribution scalar chain MC (200,000 chains, n = 256, D = 32, seed
20260811): E[K^2]/E[K]^2 = **1.854 +/- 0.014** (vs exact product 1.857 —
within 1 SE; the exp form 1.868 is the D/n-limit rounding of the same number);
Var[ln K_32] = **0.636** (vs 0.625 predicted, +1.7% from the O(1/n) skew
corrections). The 31-stochastic-step bookkeeping variant gives 1.817.

**Mapping to correlation-length inflation (the predeclared model; its one loud
assumption named).** Model: the realized per-net normalized correlation curve
is the mean-field curve with its accumulated log-decay scaled by the net's
kernel-fluctuation factor,

    c_G(theta) = c_mf(theta)^G,   ln G ~ N(-s2/2, s2),  s2 = 5D/n = 0.625,  E[G] = 1,

i.e. the same multiplicative fluctuation that the depth compounds into the
diagonal kernel is assumed to multiply the angular log-decay exponent. This
identification is exactly the "missing link" the fleet brief flags: no
published result maps quenched kernel fluctuations to the angular observable;
everything downstream of it is exact. The half-height then solves
c_mf(xi_G) = 2^(-1/G); for a purely exponential curve xi_G/xi_mf = 1/G exactly,
so E[xi_G]/xi_mf = exp(s2) = 1.868 in closed form.

Numbers (MC, 2e6 draws, seed 20260812, on the exact mean-field normalized
curve recomputed on a 0.01-deg grid — grid verified against S7's committed
2.5-deg table to 1.1e-15 and xi_mf = 20.9120 vs committed 20.9120):

| quantity | value |
|---|---|
| expected inflation E[xi_G]/xi_mf (GATED) | **1.577 +/- 0.001** |
| analytic exponential-tail cross-check exp(5D/n) | **1.868** |
| MC machinery validated on a pure exponential curve | 1.8681 (vs 1.8682) |
| median inflation | 1.306 |
| model quantiles (2.5 / 25 / 75 / 97.5%) | 0.39 / 0.84 / 2.09 / 4.04 |
| censored at 90 deg | 0.10% |
| measured (S7, per net, with bootstrap-CI ratios) | 1.77 [1.57-2.15], 1.70 [1.54-1.94], 2.20 [1.91-2.37] |

Gate (expected inflation in [1.5, 2.4]): **PASS** — both the real-curve MC
expectation (1.58) and the closed-form exponential-tail value (1.87) are
inside, bracketing the measured mean 1.89. **Route (b) verdict: DERIVED**
(magnitude), with one honest caveat reported: as a single global per-net
factor the model over-disperses — it predicts a per-net inflation IQR of
0.84-2.09 (only 23% of model draws land inside the measured band 1.5-2.4),
whereas the three measured ratios sit in the tight band 1.70-2.20. The
realized per-net curves evidently self-average over the 500 pairs/theta and
the within-net angle ensemble, shrinking the quenched scatter while retaining
a net-level common inflation of the predicted magnitude. Deriving that
partial self-averaging is the residual open item.

## Two-signal verification (all in `s12_results.json.checks`)

1. Flow re-implemented in two parameterizations (additive log-sin^2 vs
   multiplicative sin^2): max |dtheta_32| = 1.4e-16.
2. Hybrid flow at rho = 0 reproduces S7's committed mean-field c32 at all 8
   probe angles to 1.4e-15; the normalization functional reproduces S7's
   committed C_pred exactly (0.0); the fine c32 grid matches S7's committed
   2.5-deg table to 1.1e-15; xi_mf recomputed = 20.912020 vs committed
   20.912020.
3. Transmission analytic vs central finite differences: 2.8e-9 max rel.
4. ReLU Gaussian moments by quadrature: exact to 1e-16.
5. Kernel factor three ways: exact product 1.857, D/n-limit 1.868,
   exact-chain MC 1.854 +/- 0.014.
6. xi-inflation MC machinery reproduces the closed-form exp(s2) on a synthetic
   pure-exponential curve (1.8681 vs 1.8682).
7. S8's 0.87 refit independently from the committed v_l tables
   (0.8695/0.8758/0.8793 as a multiset vs committed 0.869/0.876/0.879).
8. Full harness rerun (seeded): all gated numbers bitwise identical.

## Limitations

- Route (a)'s verbatim recursion is a small-angle approximation; at
  theta_0 >= 45 deg its first steps over-contract (rho=0 endpoint error at
  90 deg: 2.1e-3 in c32). The hybrid variant removes this and confirms the
  curve-gate failure is not a truncation artifact.
- The transmission comparison identifies S8's v_l geometric rate with the
  first power of |dtheta'/dtheta|; the variance-power reading gives 0.79 and
  would fail. The data prefers the first power; no derivation of the power is
  claimed.
- Route (b)'s G-to-log-decay identification is the unpublished link (brief's
  own flag); the derivation is exact only downstream of it.
- The model treats G as fully quenched per net; the measured tight per-net
  band shows partial self-averaging that the model does not capture.

## Paragraph for writeup section 3e (ready to paste)

Finite-width theory accounts for both committed anomalies, but through two
different moments of the same 1/n correction. The mean drift of the
Jakub-Nica angle flow (ln sin^2 theta decreasing by (2/(3pi))theta + rho(n)
per layer, rho(256) = 9.3e-3) linearizes to a per-layer angular perturbation
transmission whose typical value along the ambient 90-degree trajectory is
0.890, within 2.4% of the 0.869-0.879 geometric decay fitted to S8's
layer-resampling profile — the flat chi_1 = 1 mean-field prediction is
replaced, at finite width, by a sustained O(1) ambient angle that contracts
perturbations geometrically. The same deterministic flow, however, moves the
normalized angular correlation curve by less than 0.03 from mean field (its
own half-height is 19-22 degrees versus the measured 36-46), so the 1.70-2.20x
correlation-length inflation of S7 is not a drift effect. It is a fluctuation
effect: the ReLU kernel's per-layer variance (5/n)K^2 compounds to
Var[ln K_D] = 5D/n = 0.625 (exact-chain Monte Carlo: 0.636), and treating the
realized per-net kernel as the mean-field kernel times this log-normal factor
inflates the expected half-height crossing by 1.58 (exact mean-field curve)
to 1.87 (exponential-tail closed form exp(5D/n)) — squarely bracketing the
measured 1.70-2.20. What remains empirical is the dispersion: a fully
quenched per-net factor predicts more net-to-net scatter than the tight
measured band, indicating partial self-averaging across the probe ensemble
that the five-line model does not yet derive.
