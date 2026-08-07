# M135: exact conditional low-rank ReLU source audit

## Contract

This is generated-only work. It does not read a contest model, score,
leaderboard, public or private instance, champion artifact, or submission.

The mutation is deliberately narrower than the earlier Gaussian-copula/factor
excursion: it does **not** claim that more factor nodes recover a deep
non-Gaussian layer state. The prior graph result (201-node copula fidelity
`.7034`, canonical factor gauge below `.68`) remains a parent falsifier of
that claim.

The proposed operator is exact only when the local Gaussian state has this
typed value-and-tangent factorization:

```
C = diag(d) + U U.T,             d_i > 0,
dC = diag(ddot) + Udot U.T + U Udot.T.
```

The code compares both displayed identities to the state before doing any
work. An approximate factorization raises rather than becoming an unlabelled
approximation.

## Exact conditional operator

Write `X_i = mu_i + u_i.h + eps_i`, where `h~N(0,I_r)` and independently
`eps_i~N(0,d_i)`. Conditional on `h`, the coordinates are independent. The
implementation analytically evaluates every coordinate's ReLU raw positive
moments through order four and their Frechet derivatives:

```
d_mu M_p = p M_(p-1),
d_v M_p = p(p-1) M_(p-2)/2  (p>=2),
d_v M_1 = phi(mu/sqrt(v))/(2 sqrt(v)).
```

It converts these to conditional variance, `k3`, and `k4`; exactly forms the
complete projected repeated patterns `aaa/aab/aaaa/aaab/aabb`; averages only
over `h`; then subtracts exact global Wick partitions. Thus iid factor rows
give an unbiased first-order `k3/k4` source and its Frechet tangent, while all
independent residual-coordinate noise is Rao--Blackwellized away.

For example, with `Z_a=m_a(h)+e_a` and conditional covariance `Q`, the code
uses the full identity

```
E[Z_a^3 Z_b|h]
 = m_a^3 m_b + 3m_a^2 Q_ab + 3m_a m_b Q_aa
   + 3m_a k3_aab + m_b k3_aaa + k4_aaab + 3 Q_aa Q_ab.
```

The variance screen runs the complete one-delay M121 conversion and a frozen
generated output influence functional--not a source-Frobenius norm.

## Independent premise checks

`test_m135_conditional_lowrank_source.py` has seven passing tests:

1. rank-two conditional Gauss-Hermite integration agrees with independent full
   three-dimensional Gaussian normal-order quadrature through all five tables;
2. the complete table tangent agrees with a fixed-factor central difference;
3. a nonzero-residual low-rank approximation is rejected by the exactness gate;
4. the Gaussian density-ratio correction reproduces normalization and a target
   second moment in a generated two-dimensional check;
5. its exact L2 existence gate is checked in diagonal cases;
6. the target-width factor-model dimension obstruction is checked; and
7. the complete cost boundary is checked (three but not four rows per bank fit).

All passed with the bundled runtime on 2026-08-07.

## Generated variance result: a real but conditional win

A frozen fresh width-eight rank-two factor state, a complete one-delay output
functional, and 512 generated repetitions gave:

| Rows | conditional variance | M131 iid equal-row variance | ratio |
| ---: | ---: | ---: | ---: |
| 3 common factors | `0.0198721` | `0.278306` | `0.07140` |
| 12 common factors | `0.00525201` | `0.0692086` | `0.07589` |

The deterministic rank-two common-factor quadrature is only a generated
reference, not a truth source. This validates the causal mechanism if the
typed independent-residual law is actually true; it does not validate that law
for a generic dense layer.

## Generic-state obstruction

The `D+UU.T` family has at most

```
n + n r - r(r-1)/2
```

continuous parameters after quotienting the orthogonal factor gauge. A generic
SPD covariance has `n(n+1)/2` parameters. Therefore a necessary condition to
cover a generic open set is

```
(n-r)(n-r+1) <= 2n.
```

At width 256 this requires `r >= 234`; rank two, sixteen, or sixty-four is
not merely a poor fit--it cannot be a generic exact typed covariance law. The
condition is only necessary, so it is intentionally not reported as a
construction at rank 234.

On a fresh width-256/depth-4 dense Gaussian-closure chain, the safe PSD
diagnostic base `C0=lambda_min(C) I+U_r U_r.T` left these residual Frobenius
fractions:

| retained rank | residual Frobenius fraction | residual trace fraction |
| ---: | ---: | ---: |
| 2 | `.87507` | `.90357` |
| 16 | `.46236` | `.52345` |
| 64 | `.10634` | `.13036` |
| 128 | `.02141` | `.02311` |
| 234 | `8.39e-5` | `3.90e-5` |
| 255 | numerical zero | numerical zero |

This diagnostic is not evidence about any contest state. It shows that a
fresh dense closure does not present the exceptional rank-two law used in the
positive premise test.

## Exact residual correction and its fail-closed variance gate

An approximate `C0` can be corrected exactly without pretending it is equal to
`C`. If `X~N(0,C0)`, set

```
L(X) = p_C(X) / p_C0(X).
E_C[F(X)] = E_C0[F(X) L(X)].
```

This is an unbiased density-ratio correction for any integrable source
functional. Its second moment exists exactly when

```
A = 2 C^{-1} - C0^{-1}  is positive definite,
log E_C0[L^2] = -logdet(C) + logdet(C0)/2 - logdet(A)/2.
```

For every retained rank `2,4,8,16,32,64,128,234` in the generated width-256
diagnostic, `A` was not positive definite: the exact correction has infinite
second moment. Only the essentially full rank-255 representation passed. A
small residual in Frobenius norm is therefore not a usable importance
correction when a discarded direction changes variance by more than twofold.

For completeness, the formal Russian-roulette alternative is explicit. For a
covariance path `C(t)=C0+tR`, Price's identity gives, in the smoothed or weak
distributional ReLU sense,

```
g(1) = sum_{k>=0} a_k,
a_k = [ (R:partial^2)^k E_C0 F ] / (2^k k!).
```

With a stopping variable `N`, survival probabilities `p_k=P[N>=k]>0`, and
unbiased estimators `ahat_k`,

```
ghat = sum_{k=0}^N ahat_k/p_k
```

is unbiased whenever `sum E|ahat_k| < infinity`; Tonelli/Fubini and
`E[1{N>=k}/p_k]=1` prove the claim. The tangent differentiates the same
series. This is a valid residual-correction family, but it needs repeated
pair/boundary contractions. The failed density-ratio L2 gate and the
full-order contractions give no finite-variance, sub-100B allocation here.
No roulette term was run or promoted.

## Complete exact-reference allocation

The exact conditional implementation needs four dense output-pair contractions
per common-factor row (`Q`, `k3_aab`, `k4_aaab`, `k4_aabb`) and four more for
their tangent. This is deliberately charged as distinct pair-matrix work, not
hidden by a batch dimension. Including the established protected carrier and
response reserve gives:

| independent common-factor rows per bank | float64 protected total |
| ---: | ---: |
| 1 | `75.707B` |
| 2 | `117.240B` |
| 3 | `158.773B` |

The executable exact-small reference uses float64; its only sub-100B setting
has one row per independent bank. A hypothetical float32 port with three rows
per bank projects to `96.483B`, but no float32 tangent/numerical audit exists,
so it is not a candidate. Even that projection would not establish stable
source/output variance in an `r≈234..255` generic factor law, and at rank 255
the common-factor dimension has effectively returned to the original Gaussian
dimension.

## Disposition and salvage

**Killed implementation:** deploy the exact per-factor conditional source as
a generic second-order source replacement. The fatal links are (i) no generic
small-rank typed law, (ii) density-ratio residual correction with infinite L2
variance on the generated dense diagnostic, and (iii) an exact float64
reference cost that permits only one row per bank. This is not a rejection of
Rao-Blackwellization itself.

**Preserved components:**

* complete repeated `k3/k4` conditional formulas and Frechet tangent;
* strict factor value/tangent exactness gate;
* the Gaussian bridge L2 certificate, suitable as a pre-execution kill gate;
* the complete output-influence variance harness; and
* the observation that an independently certified low-rank *typed* local law
  would be a nonincremental variance win and should reopen this branch.

The next mutation must change one failed mechanism--for example, a directly
typed conditional law with independent residual coordinates, or a separately
certified low-cost hidden-edge estimator for the two pair contractions. More
copula nodes, factor rotations, or an approximate covariance alone do not
reopen M135.

## Artifact hashes

```
ddb2a9b29b241ad6052eb1cf843b544ee0d7866b056297b3b2e4d54e86b3802c  m135_conditional_lowrank_source.py
5a913c536a1affbb151cdcd56d5c054063be9266646ce90da4d963ce0e09d497  test_m135_conditional_lowrank_source.py
150e466cd4039ab97376530a947e81954b168ad442cf213c775b186c369a1894  run_m135_generated_audit.py
4ef38d98debee0ded3ce52107fad5b3a174e605cbb448772909656948066b917  run_m135_generated_spectrum.py
```
