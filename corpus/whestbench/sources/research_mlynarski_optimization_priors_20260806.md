# Młynarski optimization priors for WHest weight-space routing

Date: 2026-08-06

Primary source: Wiktor F. Młynarski, Michal Hledík, Thomas R. Sokolowski,
and Gašper Tkačik, **Statistical analysis and optimality of neural systems**,
*Neuron* 109(7), 1227--1241.e5 (2021).
https://doi.org/10.1016/j.neuron.2021.01.020

Open author manuscript:
https://pub.ista.ac.at/~gtkacik/Neuron_Optimality.pdf

Record and metadata:
https://research-explorer.ista.ac.at/record/7553

## Actual contribution of the paper

The paper unifies a top-down normative theory and bottom-up statistical
inference by turning a utility function into a family of maximum-entropy
"optimization priors." If a system has parameters `theta`, utility
`U(theta;xi)`, and optional utility/constraint parameters `xi`, the family is

```text
p(theta | beta,xi) = exp(beta U(theta;xi)) / Z(beta,xi),
Z(beta,xi) = integral exp(beta U(theta;xi)) dtheta,
```

relative to a stated base measure. `beta=0` is the unconstrained MaxEnt
baseline; increasing `beta` lowers entropy and raises expected utility;
`beta -> infinity` concentrates on utility maximizers. The authors use this
family to test whether observed systems support a normative theory, infer a
degree of optimality, handle unconstrained/degenerate theory parameters, and
regularize high-dimensional inference. Their examples include a toy
linear-nonlinear neuron, V1 and retinal receptive fields, and C. elegans wiring.

This is not a theorem that biological systems or arbitrary neural networks are
optimal. The choice of utility remains a central scientific hypothesis. The
paper explicitly treats utility ambiguity and uncertainty rather than hiding
them.

## Exact translation to the cleanroom estimator

### Parameters

Let `theta` be one of:

- a finite whole-estimator route;
- an entropic q3 transport/compression plan;
- a rank/probe allocation in the observable-Jacobian space;
- a shallow student/control configuration in per-MLP distillation.

The competition weights `W` are observed covariates, not fitted targets.

### Base measure

`q(theta)` must live on the symmetry quotient and enforce the hard feasible
set: nonnegative normalized masses, exact moment conservation, PSD covariance,
deterministic randomization, no best-seed selection, and the billed cost cap.
Coordinate-dependent "uniform" priors are forbidden unless the parameterization
and invariance measure are stated.

### Normative utility

Use only a target-free predicted utility that can be computed from weights and
current estimator state:

```text
U(theta;xi,W) =
  - predicted_observable_error(theta; J_W, response_state)
  - xi_cost * conservative_compute(theta)
  - infinity * hard_constraint_violation(theta).
```

The first term may use an observable-Jacobian pullback quadratic form, response
Gram reconstruction error, or a proved upper bound. It may not use the
cleanroom/competition reference value at routing time. In a finite candidate
bank the prior is

```text
p(theta_i | beta,xi,W) =
  q_i exp(beta U_i) / sum_j q_j exp(beta U_j).
```

This gives a principled interpretation to the inverse temperature that had
previously appeared as an arbitrary attention/entropic-OT temperature.

### Learning beta without contamination

`beta` and any utility tradeoff `xi` may be inferred only from whole synthetic
networks in the cleanroom premise/screen seed bands. They are frozen before the
scale band. The internal-final seed band is one read and cannot generate a
mutation. Official locked/private results never update them.

For candidate `theta_i` with target-free utility `U_i(W)` and measured
cleanroom outcome `D`, compare:

```text
beta = 0          MaxEnt/null route
0 < beta < inf    partial trust in normative utility
beta -> inf       hard argmax route
```

Use grouped whole-network likelihood or a predeclared finite beta grid, correct
for the grid search, and report the full risk curve. If `beta_hat` returns to
zero on fresh networks, the normative utility is uninformative and the router
must not be promoted.

## Connection to current passes and failures

- The fixed Physarum router collapsed to one expert and had an oracle ceiling
  above the required 0.80 ratio. An optimization prior cannot manufacture a
  missing expert; it can only express uncertainty about a valid utility once a
  complementary expert exists.
- The dual-observable scalar compressor improved only 3.4% because two response
  geometries became nearly orthogonal late in depth. The parameter space must
  retain both lanes; a prior over a one-dimensional collapse cannot repair it.
- The randomized Haar-plus-two-radius q3 closure is the screened parent. Its
  compressor supplies a real feasible parameter space for the new prior.
- Pointwise Jacobian rank is locally low but tumbles across inputs. Therefore
  utility uses local observable-Jacobian actions/response Grams, not a global
  input active subspace.
- A distilled shallow student is valuable only if its analytically-integrable
  mean reduces the degree>=6 residual left by the design after all pilot and
  fit costs. `beta` can regularize student configurations but cannot replace
  that variance-per-cost test.

## Frozen adversarial questions

1. Does the target-free utility rank candidates the same way as fresh
   cleanroom loss? Report rank correlation and calibration, not only selected
   loss.
2. Is the apparent gain only temperature fitting on the same network bank?
3. Does the base measure preserve neuron permutation, covariance-factor gauge,
   and deterministic Haar symmetry?
4. Is the partition function/finite-bank normalization actually affordable in
   FlopScope?
5. Does a nonzero `beta` beat `beta=0`, a fixed pure route, and hard argmax at
   matched compute?
6. Does the prior remain beneficial when utility terms are perturbed within
   their cleanroom uncertainty?
7. Does the optimization prior change a causal routing/compression mechanism,
   or merely rename softmax?

The implementation survives only if the answer to all seven is favorable on a
fresh, predeclared seed band. Otherwise the optimization-prior formalism is
preserved as a diagnostic and the specified utility is locally killed.
