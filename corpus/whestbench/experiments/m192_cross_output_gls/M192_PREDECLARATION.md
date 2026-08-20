# M192 predeclaration -- cross-output frame-covariance attenuation

Date: 2026-08-08, written before runner code or result inspection.

## Frozen boundary

Champion reference: Kerdock v3/v3.1, 126 complete Kerdock frames under one
Haar rotation, antipodal and exact-radius conditioned.  G0 reuses the frozen
P2 cache only: three synthetic He networks (101/202/303), 16 Haar rotations
per network, 126 per-frame estimates by 256 output neurons, and the cached
3.5M-sample truths.  No new network forward, scorer, private instance,
submission, or frozen source is touched.

Objective at this gate: determine whether the 256 final-output channels carry
enough repeated information to learn a better linear combination of the 126
frame estimates.  This is an oracle premise test, not a deployable estimator.

## Why this is not a forbidden respin

The fixed-reweighting certificate proves uniform weights for a zonal kernel
with weights fixed independently of the realized network outputs.  M192 asks
whether the realized 126 x 256 frame-error matrix has a reusable covariance
structure across independently generated final rows.  Weights are learned on
other output neurons and assessed only on held output neurons.  The earlier
cross-output centroid-body kill was distribution-free: arbitrary target
vectors are possible.  WHestBench instead scores average risk over He networks
with 256 exchangeable final rows.  M192 tests that narrower ensemble premise.

The biological/transformer metaphor translates to ordinary generalized least
squares: frame experts are attenuated according to an out-of-fold estimate of
their error covariance.  The Padgett/trigonometric inspiration is the spectral
view of that covariance; no geometric image is treated as evidence.

## Oracle operator

For one network and rotation let X in R^(126 x 256) contain frame estimates
and let mu in R^256 be cached truth.  Split outputs deterministically into
eight folds H_f = {j: j mod 8 = f}.  For each held fold, form the training
error matrix

    E_f = X[:, T_f] - 1 mu[T_f]^T,
    C_f = E_f E_f^T / |T_f|.

For alpha in A = {0.0, 0.25, 0.5, 0.75, 0.9, 0.99}, define

    tau_f = tr(C_f) / 126,
    C_f(alpha) = (1-alpha) C_f + alpha tau_f I,
    w_f(alpha) = C_f(alpha)^(-1) 1 /
                 (1^T C_f(alpha)^(-1) 1).

Alpha is selected using four fixed inner folds of T_f, minimizing inner-held
truth MSE; ties choose the larger alpha.  The selected weight is then refit on
all T_f and applied only to X[:, H_f].  Alpha=0 uses a symmetric pseudoinverse
with relative eigenvalue cutoff 1e-10.  Every weight must be finite and sum to
one within 1e-10.  The baseline is the uniform frame mean on the identical
cached matrix.

This is deliberately an oracle: mu is used inside training folds.  Truth for
H_f is used only to score the held outputs.  If even this cross-fitted ceiling
fails, no truth-free covariance proxy from the same frame matrix can rescue
the family.

## Prediction, gates, and disposition

Prediction: shared hidden activations create a low-dimensional, nonstationary
frame-error covariance across final rows; oracle GLS reduces panel MSE by at
least 15 percent without changing the forward budget.

Primary statistic: geometric mean over the three networks of

    mean_rotation MSE(M192) / mean_rotation MSE(uniform).

Premise kill: reduction below 10 percent, any nonfinite result, or any
network worsens by more than 5 percent.  Screen survivor: reduction at least
15 percent and all networks improve.  The 10--15 percent interval is labelled
unresolved, never promoted.

If it survives, the next mutation replaces training truth with an already
computed analytic anchor, preserves output-fold cross-fitting, meters the
attenuator, and reruns a matched synthetic-network screen.  If killed, retain
the measured covariance spectra and close cross-output frame attenuation;
do not retune alpha, folds, weight caps, or frame subsets.

## Bias and legality

G0 has no deployment bias class because it is an oracle falsifier.  A future
truth-free child would be a cross-validated biased ensemble estimator and
would require network-level validation plus a fresh untouched holdout.  The
operator does not change billed forward work, bypass accounting, inspect
private truth, or exploit evaluator behavior.
