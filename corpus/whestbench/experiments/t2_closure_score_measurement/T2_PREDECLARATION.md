# T2 predeclaration — the full-covariance closure as a standalone estimator

Date: 2026-08-08 (before code). Task T2 of the approved reset plan.

## Mechanism
Score the certified M179 exact zero-order full-covariance Gaussian closure
(`zero_order_recurrence`: mu_0=0, V_0=I; a_l = mu W_l; C_l = W_l^T V_{l-1} W_l;
(mu_l, V_l) via the M178 Tallis/Phi2 pair moments) as a STANDALONE submission-
style estimator: predict the depth-32 final-layer post-ReLU mean directly from
mu_32, with no sampling. Measure (a) raw MSE vs true-network Monte-Carlo ground
truth on self-generated He-init f32 networks, and (b) the closure's real cost:
billed FlopScope FLOPs (M179 G4 ledger: 8.30e9 = 3.05% of B) plus measured
residual wall seconds, giving the real multiplier max(floor, C/B).

## Equation
adjusted = bias_MSE * max(floor, (8.30e9 + 1e11 * t_wall_s) / 2.72e11),
bias_MSE = mean over networks of ||mu_32_closure - mu_MC||^2/256 minus the MC
noise floor mean(var_MC/n_samples).

## Prediction
Raw bias-MSE lands between the corpus's reported Gaussian-closure oracle
ceiling 8.76e-7 (reported-level, never observed at depth 32) and the observed
diagonal-closure 7.175e-4 (this session's calibration). The pivotal boundary:
- vs the L2 candidate (2.1020e-7 adjusted): closure wins iff
  bias_MSE * multiplier < 2.1020e-7.
- At floor 0.1 with multiplier at floor: win boundary bias_MSE < 2.102e-6.
- At floor 0.5: win boundary bias_MSE < 4.204e-7 — below the oracle ceiling,
  so at floor 0.5 the closure CANNOT win on score (already known analytically).

## Evidence unit
3+ self-generated seeds, per-network closure-vs-MC MSE with the MC noise floor
subtracted and reported alongside; wall time per network measured on this box,
single process. Evidence classes kept distinct: numerical certificate (MSE),
resource observation (wall), reported-level carry-over (the 8.30e9 ledger from
M179 G4, not re-metered here).

## Kill gates (any -> closure is NOT a slot-2 score candidate; remains
Algorithmic-Contribution material)
- K1: bias_MSE >= 2.102e-6 (loses even at floor 0.1 with a floor multiplier).
- K2: measured multiplier at floor 0.1 exceeds 0.24 AND
  bias_MSE * multiplier >= 2.1020e-7 (wall kills it even if MSE is good).
- K3: MC noise floor is not at least 5x below the measured bias_MSE
  (measurement unresolved -> rerun with more samples before any verdict).

## Bias class
Deliberately biased estimator (closure bias); descriptive local measurement on
self-generated networks only — response-free, no public rows, no truth/scorer,
no submission credit. A win here authorizes only PACKAGING for a graded run,
never a rank claim.
