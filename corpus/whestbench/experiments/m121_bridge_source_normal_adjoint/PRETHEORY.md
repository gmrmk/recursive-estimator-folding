# M121 pre-theory: bridge source x normal-ordered adjoint

Status: registered mechanism-changing child; blocked on the M120b complete
Jacobian component gate.  No implementation, oracle, target, or outcome run.

## Failure-edge composition

M85 proved that an exact signed rectified-Gaussian pair bridge plus a rank-4 or
rank-8 source factor preserves substantial one-linear-map `k3/k4` contraction
fidelity.  It died because there was no lawful update after the next ReLU.

The terminal adjoint-Born operator proved cheap local higher-cumulant source
contractions and recovered the missing skew magnitude, but changed the final
mean by only 2.12% because it transported sources only in the terminal
higher-cumulant channel.  It omitted repeated downstream mean/covariance
feedback.

M120's corrected shared-CP adjoint is designed to propagate a supplied
mean/covariance defect through all later Gaussian-closure layers without the
generic all-output `n^4` state.  It does not supply that defect.

M121 joins exactly those missing interfaces.

## Frozen prospective mechanism

On the Gaussian background at hidden layer `ell`:

1. Form the M85 signed bridge-resummed local `k3/k4` source of
   `h_ell=ReLU(z_ell)` at fixed rank 4.
2. Apply exactly one affine map `W_(ell+1)` to obtain only the repeated-output
   cumulant contractions required by the next bivariate ReLU mean/covariance
   Edgeworth response.
3. Convert them immediately at ReLU `ell+1` into a signed
   `(delta m_(ell+1), delta V_(ell+1))` source.
4. Contract that source against the corrected M120 all-output
   mean/covariance adjoint from layer `ell+1` to the terminal objective.
5. Sum independently owned layer insertions.  Never propagate an M85
   higher-cumulant state through a second ReLU.

This is a first-Born/one-loop linear response around the Gaussian trajectory,
not a nonlinear cumulant recurrence and not a fitted mixture.

## Diagram ownership

- **M121 owns:** a local Gaussian-ReLU connected source, one affine transport,
  immediate conversion into a next-ReLU mean/covariance defect, followed only
  by Gaussian tangent propagation.
- **Terminal Born owns:** a local source transported in the `k3/k4` channel to
  the final preactivation and contracted directly with the final ReLU.
- **Unowned and omitted:** a source that remains in a higher-cumulant channel
  through two or more downstream ReLUs before conversion; source-source
  interactions; `k3^2`; and connected `E` propagation.

The two owned families may be combined only after a labeled one-layer diagram
incidence test proves the sets disjoint.  Otherwise M121 must run alone.

## Why this is not a forbidden mixture

The mediant theorem kills mixtures of estimator families with separate
variance/cost.  M121 is one analytic perturbation series with complementary
source and response operators.  Its value is a signed deterministic
correction and it must be judged against the unchanged Gaussian anchor; no
post-outcome scalar coefficient is allowed.

## Pre-theory cost hypothesis

- Corrected M120 reverse and background lower bound: `105.910B` before source
  scalar work.
- M85 reports a target charged source cost of `.580B` at rank 4 and `4.297B`
  at rank 8 for its frozen source-to-one-linear-map screen.  The exact scope of
  those numbers must be re-audited before multiplying by layers.
- Rank 4 is the only registered first cost point.  If its complete 31-source
  total plus M120, bivariate response, source contraction, and 25% contingency
  exceeds `258.4B`, kill before an efficacy run.

No cost may be inherited from a small-width oracle or counted as one layer
until the call graph is reconstructed from source.

## Required falsifier ladder

1. M120b corrected CP must match the complete dense `(mu,C)` Jacobian on its
   target-free algebra gate.
2. Reproduce M85 rank-4 one-map source identities independently and derive the
   exact bivariate Edgeworth mean/covariance conversion with all symmetric-slot
   factors.
3. At widths 8/12/16 and depths 2/3/4, compare the complete dense first-Born
   delay-1 correction with the factorized M121 contraction for all outputs.
   Algebraic relative error must be `<=1e-10` before testing approximation.
4. Using frozen generated paths only as an oracle, require natural-coefficient
   correction cosine `>=.80`, material sign agreement `>=.80` in every depth
   stratum, and MSE improvement over the Gaussian anchor in every aggregate
   stratum.  No scalar fit.
5. Reconstruct the target FlopScope/memory ledger and require total effective
   compute `<258.4B` with no unresolved `O(n^4)` action.

Failure preserves the exact ownership partition and the M85/M120 components;
it does not authorize a rank, delay, coefficient, or source retune.
