# Price--Hermite higher-moment response

## Verdict

**Screen the degree-two Price--Hermite operator as a transported-total
correction; kill this implementation as a faithful direct conditional `k3/k4`
formation rule. Do not deploy it.**

The candidate is genuinely weights/state-only. It takes only cell
probabilities, means, `D+UU'`, and the next weights; exact activation paths are
used only after formation by a fresh synthetic oracle. On the frozen six-case
suite it raises combined total-cumulant fidelity from `0.77549` to `0.90194`
and Edgeworth-correction fidelity from `0.85000` to `0.96478`, with `60/61`
material signs. Those gates pass.

The isolated within-cell source does not. Its aggregate standardized fidelity
is `0.67069` for `k3`, `0.16234` for `k4`, and `0.28234` combined, although
sign accuracy is `0.88688`. Thus the operator supplies useful signed response
mass after exact total-cumulance transport, but does not recover the actual
conditional cumulant energy required by the stronger task. The missing state
has been localized rather than relabeled as a win.

No WHest row, scorer, truth, submission, API, or holdout was touched.

## Why moments through order two cannot solve the problem

The obstruction already exists in one nonnegative coordinate. These two laws
have the same state visible to any second-order recurrence:

| law | mean | variance | `k3` | `k4` |
|---|---:|---:|---:|---:|
| Exponential with mean 1 | 1 | 1 | 2 | 6 |
| `P(X=0)=P(X=2)=1/2` | 1 | 1 | 0 | -2 |

Set the next weight to one. Any deterministic function of `(mean,covariance,
weight)` must return the same value for both inputs, while both higher
cumulants differ. This proves that no finite recurrence closed only on moments
through two can identify `k3,k4` for all conditional activation laws. Network
weights do not remove the witness once the current law has been compressed to
that state.

The consequence is precise: a Gaussian or maximum-entropy closure may be a
prior, but cannot be an identity. A successful recurrence needs at least one
additional signed higher-order response observable in the relevant cubic and
quartic polynomial quotient.

## Exact enlarged response state

For each coordinate, infer the rectified-normal `relu(sigma(alpha+Z))` whose
first two moments equal the supplied conditional mean and variance. Its
probabilists'-Hermite coefficients are fixed by Price/Stein differentiation:

```text
a_1 = sigma Phi(alpha),
a_q = sigma phi(alpha) He_(q-2)(-alpha) / q!,       q >= 2.
```

The frozen mutation retains only `q<=2`:

```text
X_i - E X_i ~= a1_i H1(Z_i) + a2_i H2(Z_i),
a2_i = sigma_i phi(alpha_i)/2.
```

It converts the preserved covariance factor to a latent Gaussian factor using
the exact first Price response,

```text
B_raw[i,:] = U[i,:] / a1_i,
B[i,:] = B_raw[i,:] / max(1, ||B_raw[i,:]||),
R = diag(1 - rownorm(B)^2) + B B'.
```

This is permutation covariant and positively gauge covariant. Under
`X_i->g_i X_i` and `w_i->w_i/g_i`, `alpha` and `R` are invariant while
`a1,a2` scale by `g_i`; every directional response is unchanged.

For one next-row `w`, define `b=w*a1`, `A=diag(w*a2)`. The centered response is
the linear-plus-quadratic Gaussian chaos

```text
Y = b'Z + Z'AZ - tr(AR),       Z ~ N(0,R).
```

Expanding its exact cumulant-generating function gives

```text
k3(Y) = 6 b' R A R b       + 8 tr((A R)^3),
k4(Y) = 48 b' R A R A R b + 48 tr((A R)^4).
```

These are connected Wick-diagram sums, not fitted corrections. With
`R=diag(s^2)+BB'`, the implementation evaluates the traces through weighted
`r x r` Gram matrices and diagonal reductions. It never forms a dense third-
or fourth-order tensor.

## Frozen results

All cases used 65,536 antithetic paths only for oracle evaluation, 16
principal-score cells, covariance rank four, and fresh declared seeds.

| width | depth | total `k3` | total `k4` | total combined | correction | isolated conditional `k3` | isolated conditional `k4` |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 8 | 2 | .9944 | .9672 | .9743 | .9864 | .7469 | .4634 |
| 8 | 4 | .9985 | .9584 | .9692 | .9992 | .0203 | .0129 |
| 12 | 2 | .9793 | .7326 | .7868 | .9451 | .8465 | -4.8064 |
| 12 | 4 | .9494 | .9309 | .9342 | .9805 | .7490 | .5424 |
| 16 | 2 | .8175 | .8335 | .8297 | .8818 | .6570 | .1286 |
| 16 | 4 | .8864 | .8781 | .8797 | .8584 | .4849 | .5410 |

Aggregate transported totals:

| method | `k3` | `k4` | combined | correction | material signs |
|---|---:|---:|---:|---:|---:|
| zero conditional cumulants | .78561 | .77265 | .77549 | .85000 | 59/61 |
| Price--Hermite Q2 | **.95428** | **.88725** | **.90194** | **.96478** | **60/61** |

Post-hoc localization over the isolated cell/row responses gives `.67069`
`k3`, `.16234` `k4`, `.28234` combined, and `933/1052` material signs. This
diagnostic cannot promote the candidate and is why the disposition remains
split.

The fitted univariate marginals reconstruct supplied means to `8.88e-16` and
variances to `5.33e-15`. Latent residual variances are nonnegative. However,
`481/1152 = 41.75%` of factor rows require norm clipping. This does not violate
the frozen validity gate, but it is a large warning that first-response factor
inversion is strained inside narrow conditional cells.

## Identity, symmetry, and numerical audit

- fast diagonal-plus-low-rank versus dense formulas: relative errors
  `2.42e-16` (`k3`) and `2.14e-16` (`k4`);
- coordinate permutation: `1.47e-16`, `1.57e-16`;
- positive coordinate gauge: `5.23e-16`, `6.25e-16`;
- six deterministic unit/structural tests pass;
- no dense cumulant tensor is formed.

The first suite launch generated nonfinite numbers in one nearly dead cell due
to catastrophic Gaussian-tail subtraction. `AMENDMENT_001.md` records the
repair: stable `erfc`/Mills evaluation only, with mechanism, cases, seeds, and
gates unchanged. The original nonfinite launch is retained as an
implementation failure, not hidden as tuning.

## Arithmetic envelope

At `n=256,L=32,B=16,r=4`, four weighted `r x r` Gram matrices per output/cell
dominate the response contraction:

```text
raw scalar arithmetic                       8.783921 B
float64 billed-like factor                 17.567842 B
plus 25% contingency                       21.959803 B
inherited conditional-state envelope       39.325794 B
-----------------------------------------------------
combined                                   61.285597 B
ceiling                                    80.000000 B
```

The arithmetic gate passes with `18.71B` headroom. This is not a FlopScope
port: special-function billing, small-call residual wall time, and the
weights-only recurrence that creates the conditional state remain deployment
work.

## Recursive disposition

Passed components:

- exact moments-through-two nonidentifiability proof;
- exact ReLU Price coefficients;
- exact quadratic-chaos cumulant formulas;
- diagonal-plus-rank-four matrix-free contraction;
- permutation and positive-gauge covariance;
- strong transported-total synthetic correction under the frozen gate.

Failed link:

- degree-two rectified-Gaussian response is not an accurate direct model of
  isolated within-cell cumulant energy, especially `k4`.

Minimal missing state:

- signed higher-order response mass in the homogeneous cubic/quartic
  polynomial quotient. Amplitude-coded probes can invert that quotient when a
  right-hand side is supplied, but the preserved second-order state does not
  supply the true right-hand side.

Exactly one next mechanism is authorized: hold the factor inversion, cases,
total-cumulance identity, and all gates fixed; enlarge only the analytic ReLU
chaos from Hermite order two to order four, contracting connected Wick graphs
inside the symmetrized polynomial quotient. Kill that child if isolated
`k3/k4` energy still misses `0.80`, if clipping/tail stability worsens, or if
its conservative total exceeds `80B`. Do not retune gains or treat the passing
transported-total aggregate as permission to access WHest.

Artifacts: `PREDECLARED_GATE.md`, `AMENDMENT_001.md`,
`POSTHOC_CONDITIONAL_DIAGNOSTIC.md`, `price_hermite_response.py`,
`run_fresh_oracle.py`, `fresh_results.json`, `structural_audit.py`,
`structural_audit.json`, `decision.json`, and tests in this directory.
