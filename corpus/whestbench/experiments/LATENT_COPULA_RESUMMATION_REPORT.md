# Rank-four latent copula resummation audit

## Decision

**Kill the literal 49-node candidate; preserve the exact conditional
resummation, its strong transported-total operator, and its cost collapse.**

This rung changed the failed mechanism instead of raising Hermite order.  It
analytically sums every Hermite order under the same rectified-Gaussian copula
by conditioning on the rank-four common factor.  The conservative target
envelope falls from the q4 connected-graph implementation's `35.115 T` to
`74.427 B`, while aggregate transported combined fidelity reaches `0.93584`.
That is a real compression result.

It is not the requested direct repair.  The 49-node rule reaches only
`0.56923` isolated combined fidelity, differs from its frozen 201-node
reference by `0.12403` squared relative energy, and changes by `0.19931` under
an equivalent right-orthogonal rotation of the latent factor.  All three
predeclared gates fail.  The 201-node reference improves isolated combined
fidelity to `0.70341`, but remains below `0.80`; hence stronger integration
does not yet rescue the fixed copula prior.

No WHest row, target, scorer, package, submission, API, official holdout, or
private instance was read.  The only accuracy oracle was the parent's six
frozen fresh synthetic cases, and activation paths crossed the firewall only
after the rule and gates were written.

## Changed mathematical mechanism

The preserved Price inversion supplies, inside each principal-score cell,

```text
Z = B g + diag(s) epsilon,
g ~ N(0,I_4),  epsilon_i iid N(0,1),
X_i = relu(sigma_i (alpha_i + Z_i)).
```

Conditioning on `g` makes all coordinates independent.  For one coordinate,
the implementation evaluates raw moments through order four of

```text
X_i | g = relu(mu_i(g) + tau_i epsilon_i),
mu_i(g)  = sigma_i(alpha_i + B_i.g),
tau_i    = sigma_i s_i.
```

For `tau>0`, setting `a=mu/tau` gives the truncated-normal recurrence

```text
R_0(a) = Phi(a)
R_1(a) = a Phi(a) + phi(a)
R_k(a) = a R_(k-1)(a) + (k-1) R_(k-2)(a),  k=2,3,4,
E[X^k|g] = tau^k R_k(a).
```

The `tau=0` branch is exactly deterministic.  Severe negative tails avoid
catastrophic Mills subtraction by evaluating the positive-overshoot integral

```text
R_k(-x) = phi(x) x^(-k-1)
          integral_0^infinity t^k exp(-t) exp(-t^2/(2x^2)) dt
```

with a fixed 32-node Gauss--Laguerre realization.  Against an independently
coded truncated-normal integration-by-parts formula, the maximum deterministic
raw-moment defect is `2.34e-13`.  The order-127 Gauss--Hermite diagnostic is
looser (`1.66e-2`) because a global polynomial rule resolves a moving ReLU
kink slowly; it is diagnostic only and was never used for tuning.

After raw-to-cumulant conversion, independence conditional on `g` gives, for
every next-row direction `w`,

```text
mu(g) = sum_i w_i   E[X_i|g]
v(g)  = sum_i w_i^2 k2[X_i|g]
c3(g) = sum_i w_i^3 k3[X_i|g]
c4(g) = sum_i w_i^4 k4[X_i|g].
```

These conditional cumulants are converted to raw moments, integrated over
`g`, and converted back.  This is an exact law-of-total-cumulance contraction
under the declared copula prior apart from the fixed rank-four cubature.  It
uses four `Q x n` by `n x n` contractions and never forms a dense third- or
fourth-order cumulant tensor.

## Frozen cubature

The candidate is the isotropic Gaussian Smolyak construction in four
dimensions with excess two.  Its one-dimensional components are normalized
Gauss--Hermite rules of orders `1,3,5`; after duplicate merging it has exactly
49 signed nodes.  The independently frozen excess-three reference uses
orders `1,3,5,7` and has 201 nodes.

The 49-node weights sum to one within `2.22e-16` and reproduce every Gaussian
monomial through total degree five with maximum defect `2.22e-15`.  This
polynomial exactness does not guarantee orientation stability for the
nonpolynomial rectified conditional moments.  In fact, signed sparse-grid
weights as large as about `0.2` in magnitude amplify the moving-kink error;
the frozen rotation and convergence checks expose that failure.

## Structural audit

| gate | measured maximum defect | result |
|---|---:|---|
| 49/201 node counts | exact | pass |
| candidate weight sum | `2.22e-16` | pass |
| Gaussian degree-five moments | `2.22e-15` | pass |
| rectified raw moments | `2.34e-13` | pass |
| independent total-cumulance convolution | `<1e-10` in tests | pass |
| repeated formation | `0` | pass |
| coordinate permutation | `1.08e-12` | pass |
| positive coordinate gauge | `4.06e-13` | pass |
| zero common factor versus one node | `5.39e-13` | pass |
| six deterministic tests | `6/6` | pass |

Factor clipping is unchanged from both Price parents: `481/1152 = 0.417535`
rows, with minimum residual variance zero.  This rung neither repairs nor
worsens that inherited approximation.

## Frozen accuracy results

### Transported totals

| metric | 49 nodes | 201-node reference | q4 parent | zero conditional |
|---|---:|---:|---:|---:|
| standardized `k3` fidelity | `0.95950` | `0.96051` | `0.96160` | `0.78561` |
| standardized `k4` fidelity | `0.92920` | `0.93704` | `0.92280` | `0.77265` |
| combined fidelity | `0.93584` | `0.94218` | `0.93130` | `0.77549` |
| correction fidelity | `0.97975` | `0.97933` | `0.97966` | `0.85000` |
| material signs | `56/57` | `56/57` | `60/61`* | `55/57` |

`*` The q4 sign count used its parent's per-case threshold aggregation; the
present frozen runner uses one aggregate threshold, so counts are not directly
comparable while the accuracies are.

Transport passes: the 49-node compressed operator slightly improves q4's
combined total and preserves essentially all correction fidelity.

### Isolated conditional response

| metric | q4 parent | 49 nodes | 201-node reference | required |
|---|---:|---:|---:|---:|
| standardized `k3` fidelity | `0.73214` | `0.72739` | `0.72658` | `>=0.80` |
| standardized `k4` fidelity | `0.65528` | `0.52036` | `0.69626` | `>=0.80` |
| combined fidelity | `0.67342` | `0.56923` | `0.70341` | `>=0.80` |
| material signs | `918/1052` | `878/1052` | `912/1052` | `>=0.80` |

The stronger 201-node integration recovers the quartic energy lost by the
49-node grid and modestly improves q4 combined fidelity, but it does not reach
the direct-repair threshold.  The failure is therefore not merely "Hermite
order four was too low."  Exact common-factor conditioning exposes a residual
prior/state mismatch: moments through two plus a clipped first-Price Gaussian
factor do not determine the true within-cell higher response.

This is evidence, not a theorem eliminating the infinite-order prior.  The
201-node rule still has a nonzero factor-rotation defect, so its `0.70341` is a
numerical reference rather than an exact ceiling.

## Convergence and factor covariance

| diagnostic (squared relative response energy) | `k3` | `k4` | combined |
|---|---:|---:|---:|
| 49 versus 201 nodes | `0.03028` | `0.15228` | `0.12403` |
| 49 nodes after equivalent factor rotation | `0.04704` | `0.25657` | `0.19931` |
| 201 nodes after equivalent factor rotation | `0.01002` | `0.03387` | `0.02835` |

The 49-node factor-grid defect materially threatens covariance: two matrices
`B` and `BQ` encode exactly the same latent covariance, but the candidate can
return responses separated by `19.9%` squared relative energy.  This gate
fails even though transported fidelity happens to pass.  The 201-node rule
reduces, but does not eliminate, the arbitrary-coordinate dependence.

## Arithmetic compression

At `n=256,L=32,cells=16,r=4,Q=49`:

```text
raw scalar arithmetic                    14.040432640 B
float64 billed-like factor               28.080865280 B
with 25% contingency                     35.101081600 B
inherited conditional-state envelope     39.325794304 B
------------------------------------------------------
combined                                 74.426875904 B
ceiling                                  80.000000000 B
headroom                                  5.573124096 B
```

The budget gate passes, and the total envelope is about `472x` smaller than
the literal q4 connected-diagram envelope.  The remaining `6.97%` headroom is
thin enough that an eventual FlopScope port would still need call/allocation
auditing; this result is an analytic arithmetic envelope, not deployment.

## Recursive disposition

Passed and preserved:

- exact scalar rectified-Gaussian moments, including stable tails and `s=0`;
- exact common-factor Rao--Blackwellization and total-cumulance conversion;
- four matrix contractions per node, with no dense `n^3/n^4` tensors;
- degree-five exact target-free Smolyak construction;
- permutation/gauge covariance and zero-factor collapse;
- strong transported-total/correction response;
- a `472x` envelope reduction from literal q4 graph contraction.

Failed links:

1. The literal 49-node grid is neither converged nor invariant enough under
   the arbitrary right-orthogonal factor gauge.
2. The 201-node reference still misses the direct `0.80` isolated gate,
   localizing additional error in the clipped rectified-Gaussian copula prior
   or its moments-through-two input state.

Untested claims:

- the exact infinite-cubature limit of the fixed prior;
- a factor-gauge-canonical sparse rule at the same 49-node cost;
- a new signed observable that repairs the prior rather than assuming higher
  response from `(mean,D+UU')`.

The next single changed mechanism is **factor-gauge canonicalization**: rotate
`B` into the eigenbasis of `B^T B` before applying the same frozen 49-node
rule.  Because the rule is already invariant to coordinate permutations and
sign flips, this removes arbitrary right-orthogonal presentation generically
without more nodes, a higher Hermite order, fitted coefficients, or target
access.  It must rerun the identical factor-rotation, 49-versus-201,
isolated-fidelity, and `<80 B` gates; no favorable total score can waive them.

Artifacts: `PREDECLARED_GATE.md`, `latent_copula.py`,
`test_latent_copula.py`, `run_structural_audit.py`, `structural_audit.json`,
`run_fresh_oracle.py`, `fresh_results.json`, `audit.json`, `decision.json`, and
this report.
