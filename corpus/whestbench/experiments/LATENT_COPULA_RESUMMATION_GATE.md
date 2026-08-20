# Predeclared gate: rank-four latent copula resummation

Written on 2026-08-06 before this candidate was evaluated against any
synthetic activation-path oracle.

## Frozen parent, objective, and firewall

- Preserve the Price--Hermite q4 parent's six fresh synthetic cases
  `(n,L,seed) = (8,2,83802), (8,4,83804), (12,2,84202),
  (12,4,84204), (16,2,84602), (16,4,84604)`, its 32,768 Philox base
  inputs plus negatives, 16 principal-score cells, covariance rank four,
  next-row weights, standardization, total-cumulance transport, and metrics.
- Preserve the rectified-normal marginal inversion and clipped first-Price
  factor inversion.  For each cell the assumed copula is exactly

  `Z = B g + diag(s) epsilon`, where `g~N(0,I_4)` and the coordinates of
  `epsilon` are independent standard normals.
- Candidate formation may read only copied `(p,m,D,U,W)`.  Activation paths
  remain evaluation-oracle data and may be read only after the implementation,
  cubature, and gates below are frozen.  No WHest row, target, scorer,
  package, submission, API, official holdout, or private instance is touched.
- Bias class: deterministic approximation to the exact rectified-Gaussian
  copula prior.  It is not claimed exact for an arbitrary activation law.

## Single changed mechanism

Do not increase the Hermite truncation order.  Replace all finite connected
Wick expansions with Rao--Blackwellization over the common rank-four factor.
Given a factor node `g`, coordinates are independent and

`X_i|g = relu(sigma_i(alpha_i + B_i.g + s_i epsilon_i))`.

Compute exact conditional raw moments `r1..r4` of every coordinate from the
truncated-normal recurrence.  Convert them to scalar cumulants, then for every
next-row direction `w` form

```text
mu(g) = sum_i w_i r1_i(g)
v(g)  = sum_i w_i^2 k2_i(g)
c3(g) = sum_i w_i^3 k3_i(g)
c4(g) = sum_i w_i^4 k4_i(g).
```

Convert these four conditional cumulants to raw moments of the directional
sum, integrate those raw moments over `g`, and convert the integrated raw
moments back to unconditional `k3,k4`.  This is the exact law of total
cumulance under the copula prior apart from the frozen cubature.

No dense `n^3` or `n^4` tensor may be formed.

## Frozen target-free Gaussian cubature

The deployed rule is the isotropic Smolyak construction in `r=4` with excess
two (`q=r+2`), tensor components from normalized one-dimensional
Gauss--Hermite rules of orders `1,3,5` (`order=2 level-1`).  Duplicate points
are merged before evaluation.  This produces 49 signed nodes and is exact for
all multivariate Gaussian polynomials through total degree five.  It depends
only on `r`, never on weights, state, oracle responses, or targets.

The numerical-reference rule is frozen independently as Smolyak excess three
(`q=r+3`) with one-dimensional orders `1,3,5,7`, merged to 201 nodes.  It is
used only to report cubature convergence on the already frozen state, never to
select a node, coefficient, case, or output.  The 49-node candidate is not
replaced or retuned after this comparison.

## Frozen gates

1. **Cubature identity:** weights sum to one within `1e-13`; all Gaussian
   monomials through total degree five match analytic moments within `1e-11`.
   Node counts must be exactly 49 and 201.
2. **Conditional moment identity:** scalar rectified-Gaussian raw moments
   through order four agree with a separately coded truncated-normal
   integration-by-parts formula to relative error `<=1e-9` over fixed
   deterministic `(location,scale)` pairs, including a negative tail and zero
   residual scale.  A high-order one-dimensional Gauss--Hermite check is also
   reported as a looser numerical diagnostic, not used to tune the candidate.
3. **Total-cumulance identity:** for a small deterministic factor model, the
   candidate's integrated raw-moment conversion agrees with a separate direct
   evaluation on the same 201-node rule to relative error `<=1e-10`.
4. **Formation and symmetry:** changing activation paths with `(p,m,D,U,W)`
   fixed cannot change the response.  Coordinate permutations and positive
   coordinate gauge actions change responses by at most `1e-10` relative.
   Orthogonal rotations/reflections of the rank-four factor are tested with
   both 49- and 201-node rules and reported separately; because a finite sparse
   grid need not be exactly rotation invariant, this measured defect is a
   convergence diagnostic and must be `<=0.10` on the frozen six-case
   aggregate rather than an algebraic identity gate.
5. **Validity:** latent residual variances are at least `-1e-12`; factor-row
   clipping is reported and identical to the q2/q4 parents; all values finite.
6. **Direct isolated repair:** aggregate isolated-conditional standardized
   `k3`, `k4`, and combined fidelity are each `>=0.80`; material-sign accuracy
   is `>=0.80`.  All three fidelities must exceed the q4 parent
   (`0.732135`, `0.655277`, `0.673419`).
7. **Transport:** aggregate total standardized `k3`, `k4`, combined, and
   Edgeworth-correction fidelity, plus material-sign accuracy, are each
   `>=0.80`; combined fidelity must exceed the zero-conditional baseline and
   must not be below the q4 parent `0.931300` by more than `0.01`.
8. **Convergence/ablation:** report 49-versus-201-node response residual energy
   for isolated `k3`, isolated `k4`, and their combination.  Require combined
   relative squared discrepancy `<=0.10`.  Also report the zero-common-factor
   ablation, which must reduce to a one-node independent-coordinate result.
9. **Complexity:** at target `n=256,L=32,cells=16,r=4`, conservatively count
   four directional contractions per cubature node, bill float64 at 2x, add
   25% contingency and the inherited `39.325794304 B` state envelope.  The
   combined total must be `<80 B`; the 201-node reference is diagnostic and is
   not charged to the candidate.  Tests must pass.

If the direct isolated gate fails while convergence passes, localize the
rectified-Gaussian copula prior/factor inversion as the failed link and
preserve conditional exact integration.  If fidelity passes but convergence
or cost fails, preserve the prior ceiling and recurse only on cubature
compression.  Passing every gate permits only `screen_latent_copula_resummation`;
it does not promote or deploy the competition champion.
