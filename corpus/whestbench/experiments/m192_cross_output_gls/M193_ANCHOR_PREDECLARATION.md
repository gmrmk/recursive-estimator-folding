# M193 predeclaration -- truth-free analytic-anchor frame attenuation

Date: 2026-08-08, written after the frozen M192 oracle result and before M193
runner code or result inspection.

## Parent evidence and single changed link

M192 cross-fitted held-output oracle GLS produced a panel MSE ratio 0.126193
(87.38 percent reduction; bootstrap ratio interval [0.10764, 0.15165]) and
improved all three networks.  Every one of its 384 outer fits selected
shrinkage alpha=0.25.  We therefore freeze alpha=0.25 rather than retune it.

M193 changes exactly one causal link: replace the unavailable training truth
mu with the diagonal-Gaussian analytic mean already computed by the champion
for pruning and guard fallback.  The 126 x 256 frame matrices, truths used only
for final scoring, networks, rotations, and baseline remain identical to M192.

## Truth-free operator

For each network and rotation, let X contain the 126 per-frame estimates and
let a be the champion's diagonal-Gaussian final-layer analytic mean.  Assign
each output neuron j to one of eight folds by

    fold(j) = count_i[ W_L[i,j] > 0 ] mod 8.

This assignment is derived from weights only; it is equivariant to output
permutation and invariant to positive hidden gauges and hidden-unit
permutations because those operations preserve the sign count of each final
column.  A fold with fewer than 16 training outputs is a hard failure.

For held fold H_f and training outputs T_f, form

    R_f = X[:,T_f] - 1 a[T_f]^T,
    C_f = R_f R_f^T / |T_f|,
    tau_f = tr(C_f)/126,
    Cbar_f = 0.75 C_f + 0.25 tau_f I,
    w_f = Cbar_f^(-1)1 / (1^T Cbar_f^(-1)1),
    mhat[H_f] = w_f^T X[:,H_f].

The analytic anchor is used only to learn relative frame weights and is never
blended into the reported estimate.  Hence its large absolute bias is not
automatically inherited.  Held outputs never participate in their own weight
fit.  All weights must be finite and sum to one within 1e-10.

## Prediction and gates

Prediction: anchor error is predominantly constant across frames, so it adds
a near-constant rank-one term to C_f that does not alter a sum-one GLS optimum;
the frame-relative covariance discovered by M192 survives.  Expected panel
MSE reduction is at least 20 percent.

Primary statistic is the same network-geometric mean of rotation-mean MSE
ratios as M192.  KILL if reduction is below 10 percent, any network worsens,
the analytic anchor is nonfinite, or any resource/symmetry precheck fails.
SCREEN SURVIVOR if reduction is at least 20 percent, every network improves,
and the paired bootstrap ratio upper endpoint is below 0.90.  Between those
lines is UNRESOLVED.

G0 is unmetered cached-data arithmetic.  A survivor advances to a minimal-diff
v3.1 build only after a FlopScope quote for retaining 126 frame accumulators,
forming eight 126 x 126 second moments, and solving their fixed systems.  The
production build must beat an equal-total-cost v3.1 baseline; it may not claim
the postprocessing is free.

## Bias and firewall

M193 is a truth-free, cross-fitted, deliberately biased ensemble estimator;
the bias must be measured across independent Haar rotations and whole
networks.  It uses only weights, the already-computed analytic pass, and the
already-paid frame outputs.  Cached synthetic truths are read only after
predictions are frozen for scoring.  No public/private challenge truth,
submission, scorer, or frozen candidate source is touched.
