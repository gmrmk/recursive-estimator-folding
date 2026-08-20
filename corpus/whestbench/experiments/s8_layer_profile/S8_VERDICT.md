# S8 Verdict: layer-resolved defect profile of the estimator residual field

Ledger id: `s8_tdse_layer_defect_profile`. Date: 2026-08-09.
Artifacts: `run_s8.py`, `s8_results.json`, `s8_run.log` (this directory).

**Verdict: FAIL-PASS / NOT-KILLED.** The measured layer-defect profile is
strongly and coherently non-flat (early layers dominate, near-geometric decay
with per-layer factor ~0.87), so the predeclared fixed-point mean-field
prediction (flat) fails the factor-2 PASS gate on 3/3 nets; the KILL gate does
not fire because the structure is highly coherent across nets (mean pairwise
Spearman 0.988).

Deviations from the predeclaration: none. Runner-level operationalizations
fixed before measurement (documented in the `run_s8.py` header): subsample
seed 20260807; resample seed formula `10_000_000 + net_seed*10_000 +
layer*100 + rep`; coherence := mean pairwise Spearman of per-net share
profiles >= 0.8.

## 1. Mean-field prediction (derived BEFORE measurement)

Derivation order is verifiable: `run_s8.py` computes and checkpoints this
section to `s8_results.json` before any forward pass, and `s8_run.log` prints
it before the first net.

For bias-free He-critical ReLU (gain 2/width), the normalized arccos
correlation map and its derivative are

    f(c)   = ( sqrt(1 - c^2) + (pi - arccos c) * c ) / pi
    chi(c) = f'(c) = (pi - arccos c) / pi

A defect injected at layer l reaches the output through 31 - l downstream
mean-field layers, each contributing a factor chi evaluated on the depth
trajectory. The He trajectory sits at the fixed point c -> 1, where

    chi_1 = f'(1) = (pi - 0)/pi = 1        (exact criticality)

Predicted shape (predeclared, gated): v_l ~ chi_1^(31-l) = 1 for every l — a
**flat profile**, p_l = 1/32 = 0.03125 per layer. Predicted top-5 share
5/32 = 0.156; predicted last-3 share 3/32 = 0.094.

Pre-registered secondary refinement (REPORTED, not gated): a full-layer
redraw is a nonperturbative defect. It sets the cross-net activation
correlation at the redrawn layer's output to gamma_0 = f(0) = 1/pi, which
heals through downstream shared layers via gamma_j = f(gamma_(j-1))
(gamma_j for j = 0..8: 0.3183, 0.4937, 0.6048, 0.6810, 0.7359, 0.7772,
0.8091, 0.8344, 0.8548; algebraic approach to 1 thereafter, gamma_31 =
0.9747). Modeling the layer-(l+j) defect-realization correlation as
ghat_j = (gamma_j - 1/pi)/(1 - 1/pi) gives

    R_l = 1 + sum_{j=1}^{31-l} (1 - gamma_j) / (1 - gamma_0)

which DECREASES in l from R_0 = 6.18 to R_31 = 1 (span 6.2x): early layers
predicted largest because redrawing them also partially scrambles every
downstream layer's defect realization.

## 2. Measurement

Per net seed (101, 202, 303): width 256, depth 32, bias-free ReLU, He init
(`he_mlp_weights` mirror of `run_n8a_gates.py`). Probes: M = 8,192 rows
uniformly subsampled (fixed seed 20260807, no replacement, identical indices
for all nets/arms/reps) from the antipodally-doubled Kerdock design (64,512
rows, radius mean_chi(256) = 15.9844), rotated per net by
`haar_rotation(900000 + net_seed*1000 + 0)`. Baseline residual r(u) =
ybar(u) - mean_u ybar with ybar the neuron-averaged final post-ReLU output.
Arms: for each layer l in 0..31, 3 reps with ONLY layer l redrawn (fresh He
draw, seed formula above); metric v_l = mean_u E_reps[(r - r_l)^2], variant
1 - corr(r, r_l). Total wall time 111 s.

## 3. Per-net v_l table (mean over 3 reps, +/- sem), aggregate shares, gates

| l | v_l net101 (+/-sem) | v_l net202 (+/-sem) | v_l net303 (+/-sem) | share s_l (agg) | p_l flat | dev vs flat (101/202/303) | R_l norm |
|---|---|---|---|---|---|---|---|
| 0 | 1.602e-02 (5e-05) | 3.124e-02 (4e-04) | 2.197e-02 (2e-04) | 0.1138 | 0.0313 | 3.6 / 3.0 / 4.3 | 0.0402 |
| 1 | 1.378e-02 (7e-04) | 2.797e-02 (1e-03) | 2.086e-02 (1e-03) | 0.1030 | 0.0313 | 3.1 / 2.7 / 4.1 | 0.0400 |
| 2 | 1.204e-02 (8e-04) | 2.492e-02 (1e-03) | 1.436e-02 (2e-04) | 0.0826 | 0.0313 | 2.7 / 2.4 / 2.8 | 0.0397 |
| 3 | 1.344e-02 (5e-04) | 2.567e-02 (1e-03) | 1.369e-02 (8e-04) | 0.0852 | 0.0313 | 3.0 / 2.5 / 2.7 | 0.0395 |
| 4 | 9.837e-03 (3e-04) | 2.522e-02 (3e-03) | 1.272e-02 (6e-04) | 0.0744 | 0.0313 | 2.2 / 2.4 / 2.5 | 0.0392 |
| 5 | 1.057e-02 (1e-03) | 2.210e-02 (4e-03) | 1.016e-02 (7e-04) | 0.0677 | 0.0313 | 2.4 / 2.1 / 2.0 | 0.0389 |
| 6 | 7.775e-03 (6e-04) | 2.479e-02 (3e-03) | 9.238e-03 (8e-04) | 0.0620 | 0.0313 | 1.7 / 2.4 / 1.8 | 0.0386 |
| 7 | 7.217e-03 (1e-03) | 2.202e-02 (3e-03) | 6.849e-03 (2e-04) | 0.0531 | 0.0313 | 1.6 / 2.1 / 1.3 | 0.0383 |
| 8 | 7.028e-03 (9e-04) | 1.937e-02 (3e-03) | 6.013e-03 (4e-04) | 0.0482 | 0.0313 | 1.6 / 1.9 / 1.2 | 0.0379 |
| 9 | 5.887e-03 (2e-04) | 1.478e-02 (2e-03) | 5.989e-03 (5e-04) | 0.0409 | 0.0313 | 1.3 / 1.4 / 1.2 | 0.0375 |
| 10 | 4.364e-03 (2e-04) | 1.136e-02 (1e-03) | 6.492e-03 (4e-04) | 0.0349 | 0.0313 | 1.0 / 1.1 / 1.3 | 0.0371 |
| 11 | 4.290e-03 (2e-04) | 9.986e-03 (9e-04) | 4.381e-03 (4e-04) | 0.0290 | 0.0313 | 1.0 / 1.0 / 1.2 | 0.0367 |
| 12 | 4.249e-03 (6e-04) | 1.038e-02 (1e-03) | 3.419e-03 (2e-04) | 0.0274 | 0.0313 | 1.0 / 1.0 / 1.5 | 0.0362 |
| 13 | 2.747e-03 (3e-04) | 9.181e-03 (1e-03) | 3.681e-03 (3e-04) | 0.0232 | 0.0313 | 1.6 / 1.1 / 1.4 | 0.0357 |
| 14 | 3.094e-03 (1e-04) | 6.925e-03 (8e-04) | 2.895e-03 (2e-04) | 0.0201 | 0.0313 | 1.4 / 1.5 / 1.8 | 0.0352 |
| 15 | 2.578e-03 (4e-04) | 6.620e-03 (3e-04) | 2.533e-03 (3e-04) | 0.0179 | 0.0313 | 1.7 / 1.6 / 2.0 | 0.0346 |
| 16 | 2.613e-03 (2e-04) | 7.332e-03 (7e-04) | 1.852e-03 (3e-04) | 0.0173 | 0.0313 | 1.7 / 1.4 / 2.8 | 0.0340 |
| 17 | 1.885e-03 (3e-04) | 4.624e-03 (8e-04) | 1.844e-03 (5e-04) | 0.0128 | 0.0313 | 2.4 / 2.2 / 2.8 | 0.0333 |
| 18 | 1.620e-03 (3e-04) | 3.929e-03 (2e-04) | 1.857e-03 (2e-04) | 0.0115 | 0.0313 | 2.7 / 2.6 / 2.8 | 0.0326 |
| 19 | 1.835e-03 (5e-04) | 3.270e-03 (2e-04) | 1.658e-03 (3e-04) | 0.0110 | 0.0313 | 2.4 / 3.2 / 3.1 | 0.0318 |
| 20 | 1.543e-03 (3e-04) | 3.018e-03 (5e-04) | 1.556e-03 (1e-05) | 0.0098 | 0.0313 | 2.9 / 3.4 / 3.3 | 0.0309 |
| 21 | 1.439e-03 (1e-04) | 3.275e-03 (8e-04) | 1.236e-03 (1e-04) | 0.0092 | 0.0313 | 3.1 / 3.2 / 4.1 | 0.0299 |
| 22 | 9.811e-04 (1e-04) | 2.209e-03 (3e-04) | 1.701e-03 (4e-04) | 0.0080 | 0.0313 | 4.5 / 4.7 / 3.0 | 0.0288 |
| 23 | 1.358e-03 (3e-04) | 2.511e-03 (3e-04) | 1.148e-03 (4e-04) | 0.0080 | 0.0313 | 3.3 / 4.1 / 4.5 | 0.0276 |
| 24 | 1.052e-03 (1e-04) | 1.766e-03 (2e-04) | 1.001e-03 (2e-04) | 0.0063 | 0.0313 | 4.2 / 5.8 / 5.1 | 0.0262 |
| 25 | 8.576e-04 (3e-04) | 1.278e-03 (2e-04) | 1.145e-03 (1e-04) | 0.0056 | 0.0313 | 5.2 / 8.1 / 4.5 | 0.0246 |
| 26 | 6.569e-04 (2e-04) | 1.175e-03 (1e-04) | 1.018e-03 (2e-04) | 0.0048 | 0.0313 | 6.8 / 8.8 / 5.0 | 0.0228 |
| 27 | 3.118e-04 (8e-05) | 1.234e-03 (2e-04) | 6.562e-04 (2e-04) | 0.0033 | 0.0313 | 14.3 / 8.4 / 7.8 | 0.0207 |
| 28 | 6.294e-04 (5e-05) | 9.349e-04 (3e-04) | 5.711e-04 (1e-04) | 0.0036 | 0.0313 | 7.1 / 11.0 / 8.9 | 0.0182 |
| 29 | 4.822e-04 (2e-04) | 4.851e-04 (8e-05) | 3.066e-04 (4e-05) | 0.0022 | 0.0313 | 9.2 / 21.3 / 16.7 | 0.0151 |
| 30 | 2.043e-04 (6e-05) | 5.360e-04 (2e-04) | 4.598e-04 (4e-05) | 0.0020 | 0.0313 | 21.8 / 19.3 / 11.1 | 0.0113 |
| 31 | 1.424e-04 (3e-05) | 3.928e-04 (2e-05) | 2.377e-04 (6e-05) | 0.0012 | 0.0313 | 31.3 / 26.3 / 21.5 | 0.0065 |

Baseline residual variances Var_u(r): net 101 = 8.116e-03, net 202 =
1.562e-02, net 303 = 1.143e-02.

## 4. Gate outcomes

- **PASS gate** (shape within factor 2 of the flat mean-field on >= 2/3
  nets): **fails on 3/3 nets.** Max dev vs flat = 31.3 (net 101), 26.3
  (net 202), 21.5 (net 303), in every case at layer 31. Layers already
  exceed factor 2 at both ends of the depth range (l <= 5 above flat,
  l >= 17 below flat, all nets).
- **KILL gate** (dev > 5x at >= 2 layers on >= 2 nets AND no coherent
  structure): first clause fires (layers 24-31 exceed 5x on >= 2 nets), but
  the structure is highly coherent — pairwise Spearman of the three per-net
  share profiles = 0.992 / 0.985 / 0.987 (mean 0.988 >= 0.8), and the
  profile is monotone-decreasing in every net. **KILL does not fire.**
- **Verdict: FAIL-PASS / NOT-KILLED.** The flat fixed-point mean-field
  profile is rejected; the measurement found a coherent, reproducible
  alternative structure.

## 5. Reported evidence (not gated)

- **Top-5 concentration:** top-5 layers are {0,1,2,3} plus one of {4,5} in
  every net; shares 0.462 (101), 0.409 (202), 0.511 (303), mean 0.459
  (aggregate profile: 0.459). The predeclared "top-5 >= 50%?" question:
  right at the boundary — one net above 50%, two below; ~2.9x the flat
  mean-field top-5 share of 0.156.
- **Last-3 layers (29-31, the ones the fold trichotomy exactifies):** shares
  0.0058 (101), 0.0043 (202), 0.0061 (303), mean 0.0054 — **16-22x BELOW**
  their mean-field share of 0.094. The layers the fold already exactifies
  are the ones whose realized-weight defects matter least to the final
  residual field.
- **Shape law (post-hoc observation, labeled derived-after-measurement):**
  the profile is close to geometric, v_l ~ rho^l with fitted rho = 0.869 /
  0.879 / 0.876 per net (aggregate 0.876), i.e. an effective per-layer
  defect-transmission factor of ~0.87 for this observable, not the
  mean-field chi_1 = 1. The pre-registered healing refinement R_l predicts
  the correct SIGN of the deviation (decreasing in l, early layers dominate,
  last-3 below flat) but is far too shallow: R spans 6.2x where the
  measurement spans ~95x; max dev vs R_l = 9.5 / 10.3 / 8.1 per net
  (log-share correlation with R_l: 0.88 / 0.87 / 0.83).

## 6. Cross-checks (two-signal verification)

1. **Identity recomputation:** every per-arm v was independently recomputed
   as Var(r) + Var(r_l) - 2 Cov(r, r_l); max relative discrepancy vs the
   direct mean-square-difference = 2.55e-14 (float64 roundoff).
2. **Bitwise repeat:** the full resampled-arm forward (net 101, layer 13,
   rep 0) rebuilt from seeds a second time reproduced ybar bit-for-bit.
3. **Variant metric:** the 1 - corr(r, r_l) profile tells the same story
   (monotone decreasing, spans 1.00 -> 0.006); normalized-shape max ratio vs
   the v_l shape = 1.90 / 1.41 / 2.62 per net, with the worst discrepancy at
   the noisiest deep-layer tail. Same ordering, same verdict under either
   metric.
4. **Constants:** mean_chi(256) closed form matched the frozen v3 constant
   to < 1e-9; Kerdock direction radii verified at 15.9844 (rtol 1e-5).

## 7. Limitations

- 3 reps per (net, layer): per-layer sem/mean reaches ~0.3-0.4 in the
  deepest layers, so individual deep-layer dev values (e.g. 31.3 vs 21.5)
  carry wide error bars; the shape conclusion is unaffected (the profile
  spans two orders of magnitude and is monotone in all nets).
- v_l conflates the layer's own defect with the partial scrambling of
  downstream defect realizations (nonperturbative redraw); the pre-registered
  refinement models this crudely (ghat linear-in-f) and underpredicts the
  observed steepness. A per-layer transmission measurement (small-epsilon
  weight perturbations instead of full redraws) would separate the two
  contributions; not predeclared, not run.
- Layer 0's defect is injected on a deterministic input (the probe design)
  rather than a random activation field; its v_0 is not strictly
  exchangeable with l >= 1. It sits smoothly on the profile, so no
  correction was applied.
- Findings are for synthetic He nets at width 256 / depth 32 under the
  frozen Kerdock probe design; no claim about trained nets.
