# M194 predeclaration -- independent-pilot projected block GLS

Date: 2026-08-08.  This protocol was frozen after M193 failed and before the
M194 runner was written or its outputs were inspected.

## Parent, first break, and frozen cache

M192 established a large oracle premise: output-cross-fitted GLS weights over
the 126 Kerdock frames reduced cached MSE by about 87 percent.  M193 replaced
truth with the paid diagonal-Gaussian analytic mean and failed by about three
orders of magnitude.  Its first break is now localized.  If

    X_j = mu_j 1 + e_j,      a_j = mu_j - delta_j,

then the analytic-anchor residual is `e_j + delta_j 1`.  Its second moment is

    C_a = C_e + q 1^T + 1 q^T + s 1 1^T,
    q = E_j[delta_j e_j].

The rank-one term is harmless to a sum-one rule, but the projected cross term
`P q`, `P = I - 1 1^T/126`, is not.  M193 measured exactly this failure: the
anchor error is far larger than the frame error and produces unstable contrast
weights.  M194 changes that failed information link; it is not a coefficient
retune of M193.

G0 reads only the existing synthetic P2 cache: three He networks
101/202/303, 16 independent Haar rotations per network, 126 frame estimates
by 256 final outputs, and the existing 3.5M-sample truths.  Rotations 0--7 are
the main estimators.  Rotation `r+8` is the independent pilot for main rotation
`r`; only its first eight complete frames are averaged.  No forward, scorer,
private instance, submission, or frozen estimator source is touched.

## Identifiable operator

For a main frame matrix `X` in R^(126 x 256), let `y` be the independent
eight-frame pilot mean.  Split outputs into fixed folds
`H_f = {j: j mod 8 = f}`.  On training outputs `T_f`, form

    R = X[:, T_f] - 1 y[T_f]^T,
    c = (1/126) 1^T R,
    Z = P R = R - 1 c,
    A = Z Z^T / |T_f|,
    b = Z c^T / |T_f|,
    tau_z = tr(A) / 125.

Conditional on the fixed network, independent Haar randomization gives a
zero-mean pilot error independent of the main-rotation error.  Therefore the
pilot contributes only `s_p 1 1^T` in expectation and

    P C_p P = P C_e P,       P C_p u = P C_e u,
    u = 1/126.

These are exactly the two covariance blocks needed by a sum-one correction.
Freeze `lambda = 1/3`, the projected-block counterpart of M192's unanimously
selected `alpha = 0.25`.  Solve

    v = -(A + lambda tau_z P)^+ b,
    w = u 1 + v,

enforcing `1^T v = 0` numerically.  Apply `w` only to held outputs of the main
matrix.  The pilot is never blended into the prediction.  If `tau_z` is
nonpositive/nonfinite, a solve is singular, a weight is nonfinite, or the
sum-one error exceeds 1e-10, fall back to uniform and record it.

One frozen diagnostic also computes the same projected-block rule using
training truth in place of the pilot.  It may explain a failure but may not
alter M194, lambda, frame count, folds, pairs, or gates.

## Prediction and gates

Prediction: the independent pilot removes the unidentifiable M193 cross term,
so M194 preserves at least 20 percent raw-MSE reduction on all three networks.

Primary statistic is the geometric mean across networks of the ratio of mean
rotation MSEs.  Report both raw ratio and the deliberately conservative
sample-cost-adjusted ratio

    ratio_cost = ratio_raw * (126 + 8) / 126.

This charges every pilot frame as a full additional main frame and ignores
fixed-cost amortization.  It is a screen approximation, not an official
flopscope quote.

Kill if raw reduction is below 10 percent, any network worsens, any fallback
occurs, or any result is nonfinite.  Screen survivor requires raw reduction at
least 20 percent on every network, cost-adjusted panel reduction at least
15 percent, and a rotation-cluster bootstrap upper 95 percent bound below
0.90 after the same cost factor.  Anything between is unresolved.  This
three-network cache gate can only screen; it cannot promote a submission.

## Bias, validation, and legality

M194 is a truth-free, output-cross-fitted, data-dependent linear rule.  Its
deployment bias class is cross-fit biased.  A survivor must next pass a
matched actual-v3 frame-attribution implementation, at least 20 fresh whole
synthetic networks, an untouched network holdout, exact billed/residual cost,
symmetry tests, healthy-output compatibility, and the hostile resource suite.

The operator uses only contest-provided weights, allowed setup randomness,
and estimates computed inside the billed estimator.  It does not inspect
evaluation truth, evaluator internals, hidden page data, or accounting gaps.
