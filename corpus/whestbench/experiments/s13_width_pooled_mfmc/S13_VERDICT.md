# S13 -- width-pooled surrogate MFMC: premise verdict

**ledger id:** `s13_width_pooled_mfmc_premise`
**date:** 2026-08-09
**verdict:** **WIDTH-FIDELITY CLOSED.** Closed-form MFMC gain of the width-64
pooled surrogate = **0.9552x** (geomean over nets 101/202/303), below the
predeclared 1.1x line. The pooled surrogate is not merely too weak -- its
correlation with the full net (rho ~ 0.07-0.18) is below even the
*any-gain* threshold (0.489), so the constrained MFMC optimum degenerates to
plain single-model MC. With depth already dead (S10, 0.056x), the fidelity
family is fully dead on both axes.

## Deviations from the predeclaration
**None.** Arms, seeds, subsample size, pooling construction, cost model, and
gates are exactly as predeclared. Two implementation notes (not deviations):
1. "corr of the mean-removed fields" IS the Pearson rho (Pearson is invariant
   to mean removal); the additional context number reported is the uncentered
   cosine of the raw positive fields, which is trivially near 1 (0.88-0.96)
   and carries no control-variate information.
2. The fixed 8,192-direction subsample is drawn (seeded permutation, no
   replacement) from the antipodally-doubled 64,512-point design without
   enforcing +-u pairing; both nets see the identical subsample.
3. The width-128 gain is reported although rho did not "rise strongly"
   (reporting it is strictly more information; predeclared as the trend arm).

## Gate outcome (predeclared)
- gain >= 1.3x -> arm proposal for Sol
- gain < 1.1x -> width-fidelity CLOSED (joins depth)   <-- **THIS**
- 1.1-1.3x -> inconclusive

Geomean width-64 gain **0.9552x** (bootstrap 95% CI [0.9520, 0.9589]);
independent-resample recompute 0.9539x. Same verdict under every reading:
the unconstrained closed form gives < 1 (surrogate would *hurt*), and the
feasibility-constrained optimum gives exactly 1.0 (surrogate excluded by the
Peherstorfer model-selection rule) -- both < 1.1.

## Construction (deterministic, training-free)
Same weight draw as the full net (seeds 101/202/303, width 256, depth 32,
bias-free He, stored `(in, out)`, forward `act @ W`; per-net Haar rotation
seed `900000 + net*1000 + 0` folded into the first matmul as
`rotation.T @ W1`, exactly as the champion).

**Hidden layers (l=2..32):** average disjoint k x k blocks in both dims,
256x256 -> (256/k)x(256/k). Rescale derivation: a pooled entry averages k^2
iid N(0, 2/256) entries -> variance 2/(256 k^2); He for fan_in 256/k wants
2k/256; factor = sqrt[(2k/256) / (2/(256 k^2))] = **k^(3/2)** (k=4: 8;
k=2: 2*sqrt(2)).

**Input layer W_1:** the probe u stays 256-d (the SAME rotated u feeds both
nets), so pool the OUTPUT dim only, 256x256 -> 256x(256/k). A pooled entry
averages k iid N(0, 2/256) column entries -> variance 2/(256 k); He with
fan_in 256 (unchanged) wants 2/256; factor = **sqrt(k)** (k=4: 2;
k=2: sqrt(2)).

**Empirical variance check (rescaled matrices vs He target):** hidden-layer
mean variance / (2/64): 1.0020 / 0.9998 / 1.0002 (nets 101/202/303, k=4);
/ (2/128): 1.0000 / 0.9977 / 1.0019 (k=2). Input layer / (2/256): 1.0159 /
1.0265 / 0.9889 (k=4) -- a single 256x64 matrix has 16,384 entries, so the
variance estimate's own sd is ~1.6%; all deviations are within ~2 sd. Both
rescales confirmed.

**Surrogate target:** h(u) = mean over its 256/k final post-ReLU neurons;
full target g(u) = mean over 256 final post-ReLU neurons.

## Measured correlations (Pearson, 8,192 directions)
| net | rho pooled-64 | resample | rho pooled-128 | resample |
|-----|---------------|----------|----------------|----------|
| 101 | +0.1122 [0.090, 0.134] | +0.1330 | +0.2709 [0.250, 0.292] | +0.2746 |
| 202 | +0.1761 [0.155, 0.199] | +0.1718 | +0.2080 [0.186, 0.228] | +0.2031 |
| 303 | +0.0714 [0.049, 0.094] | +0.0696 | +0.2175 [0.197, 0.238] | +0.1709 |

(brackets: bootstrap 95% CI over directions; "resample" = independent
disjoint 8,192-direction subset.)

## Gain computation (Peherstorfer two-model closed form)
Derived in `run_s13.py`'s docstring: with optimal alpha* = rho sig_g/sig_h
and optimal allocation under budget n1 + w*n2 = p,

  Var(MFMC)/Var(MC) = ( sqrt(1 - rho^2) + sqrt(w) |rho| )^2,  GAIN = 1/ratio,

with feasibility n2 >= n1 iff rho^2 >= w/(1+w) and any gain iff
|rho| > 2 sqrt(w)/(1+w).

**FLOP model (MACs/direction):** full = 32 * 256^2 = 2,097,152.
Pooled-64 = 256*64 + 31*64^2 = 143,360 -> **w64 = 35/512 = 0.06836**
(input layer 1/4, hidden layers 1/16 each, cost-weighted total ~1/14.6).
Pooled-128 = 256*128 + 31*128^2 = 540,672 -> **w128 = 33/128 = 0.2578**.

**Required rho at w64:** any gain 0.489; 1.1x 0.607; 1.3x 0.727.
Measured: 0.07-0.18. Not close -- the best net (202) reaches 24% of the
1.3x requirement.

**Gains (per net 101/202/303):** width-64: 0.9555 / 0.9418 / 0.9685,
geomean **0.9552** [0.9520, 0.9589]; width-128: 0.8262 / 0.8514 / 0.8471,
geomean **0.8415** [0.8366, 0.8470]. Feasibility fails for every net and
both widths, so these closed-form values are the *optimistic unconstrained*
numbers; the constrained truth is "gain = 1.0, surrogate excluded."

## Width trend (two-signal arm 2)
rho roughly doubles from width 64 to width 128 (0.07-0.18 -> 0.17-0.27),
but the cost-adjusted gain FALLS (0.955 -> 0.842): the rho a surrogate must
clear grows much faster with its cost (any-gain threshold 0.489 -> 0.807)
than the measured rho grows with its width. The axis has no sweet spot in
either direction: cheaper surrogates need less rho but lose it faster
(width-64 delivers ~0.1), and richer surrogates gain rho far too slowly to
pay their cost (width-128 would need 0.854 for even 1.1x, delivers ~0.22).
Extrapolating the doubling trend, a width-256 "surrogate" at cost ~1 is the
full net itself -- there is no intermediate width where measured rho meets
the requirement curve.

## Two-signal verification
1. **Independent disjoint resample:** every rho reproduces within ~0.02
   (worst: net 303 width-128, 0.217 -> 0.171 -- consistent with the CI
   width); gate metric 0.9552 (primary) vs 0.9539 (resample). Same verdict.
2. **Width-128 trend arm** independently confirms the mechanism (rho rises
   with width but nowhere near the cost-required curve).
3. **Internal:** every Pearson rho was recomputed from raw float64 sums and
   required to match `np.corrcoef` to 1e-12 (the harness raises on
   disagreement; the run was clean). The construction was verified against
   its own algebra by the empirical He-variance checks above.

## S10 contrast: why the fidelity family dies on both axes
S10 killed depth-fidelity at 0.056x: the depth telescope's coupled
increments never decouple because each He/ReLU layer is close to an
independent nonlinear re-mixing of the neuron-mean, so the expensive deep
levels carry full fresh variance. S13 shows the width axis dies by the same
re-mixing, in a different guise: here the coupling is *maximal by
construction* -- the surrogate's weights are literal block-averages of the
full net's own weight draw, and both nets see the identical rotated probe u
-- yet after 32 layers of ReLU mixing in different-dimensional spaces the
two neuron-mean fields share only rho ~ 0.1. Depth-fidelity failed as
"catastrophically worse than MC" (levels cost up to 32x); width-fidelity
fails as "merely useless" (the cheap model is affordable but uncorrelated).
The common root cause is the same: the champion target is a deep-net
functional whose direction-dependence is re-randomized layer by layer, so no
structurally-derived cheap trajectory stays correlated with it. Fidelity
surrogates (depth-truncated or width-pooled) are closed as a family.

## Files
- `run_s13.py` -- harness (predeclaration + derivations in docstring;
  imports frozen n8a constructor/directions read-only).
- `s13_results.json` -- per-net rho/CIs/gains, construction checks, cost
  model, thresholds, gate.
- `S13_VERDICT.md` -- this file.
