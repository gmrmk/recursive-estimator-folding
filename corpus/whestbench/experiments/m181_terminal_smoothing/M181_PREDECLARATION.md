# M181 predeclaration — terminal rectified-Gaussian smoothing (the hybrid)

Date: 2026-08-08 (before code). The mandate's hybridization made concrete:
the T2-KILLED closure (passed component: certified exact rectified-Gaussian
moments) fused with the PROMOTED sampler (Kerdock frames), each doing what it
measured well.

## Mechanism

The score is the final layer's MSE, and the final layer currently contributes
its full kink sampling noise: estimate = mean_s ReLU(z_s), z_s = h_s @ W_31.
M181 replaces that with conditional smoothing: from the SAME samples, form
the empirical per-neuron pre-activation moments (mu_i, sigma_i^2) [Arm 1] or
the pair moments (mu, V) at layer 30 propagated ONE exact step via the M178
certified bivariate provider [Arm 2], then predict

    E[ReLU(z_i)] = mu_i * Phi(mu_i/sigma_i) + sigma_i * phi(mu_i/sigma_i)

exactly. T2 measured closure bias ACCUMULATING over 32 layers to 9.6e-5; over
ONE terminal step from an empirical start the Gaussian-approximation bias is
the only bias term and is expected small. The variance drops because two
smooth moments replace a kinked average. Community priors: the exact
rectified-Gaussian final layer appears in the honest 4.1e-7-tier writeups
(evaaaz, radiant-allomancer) — mechanism sound, never composed with a
structured spherical design.

Arms (all predeclared; no post-hoc additions):
- Arm 1: univariate final-layer smoothing (empirical mu_i, sigma_i per neuron).
- Arm 2: two-terminal-layer smoothing — empirical (mu, V) at layer 30, exact
  rectified-Gaussian pair propagation through layer 31 (M178 machinery).
- Arm 3 (control-variate form, unbiased): sample mean PLUS
  lambda * (analytic smoothed estimate - its own sample-consistent estimate),
  lambda from a 20%-holdout of the samples — retains unbiasedness if the
  smoothing bias proves material.

## G0 gate (MSE-based — smoothing trades bias for variance, so variance alone
is not a valid gate)

3 synthetic He nets, matched n = 64,512 Kerdock directions, >= 12 rotation
seeds, MC truth 3.5M samples (noise floor ~6e-9, subtracted): per-arm
final-layer MSE vs the current point-ReLU estimator.
- KILL an arm if MSE reduction < 10%.
- PROMOTE the best arm if reduction >= 15% with bootstrap CI excluding 10%.

## Ladder if promoted

G1 minimal-diff into the v3 scaffold (final-layer stage only; billed via
flopscope stats primitives — Phi/phi bill at 32-96 FLOPs/element, cost is
O(width), negligible vs the sampling matmuls). G2 local paired factorial
(<= 0.87, CI excluding 1.0, billed +2% max, wall margins intact). G3 package
+ validate + members. G4 one graded submission; PASS iff hosted adjusted
< 1.75e-7.

## Honesty bound

Expected gain 1.15-1.6x on final-layer MSE if the pre-activation laws are
near-Gaussian at layer 31 under the sampling distribution; the T2/N5
higher-order-structure findings cut both ways (they say the law is NOT
Gaussian marginally — the arm-3 unbiased form exists for exactly that case).
No claim past the measured sizes; the wall tier stays out of scope.

## Firewall

Synthetic nets until G4; frozen candidates untouched; M178 modules read-only;
no sealed cells; kills final per arm.
