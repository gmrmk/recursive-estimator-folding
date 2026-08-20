# M224 predeclaration -- gauge-invariant rho-.08 chart

Date: 2026-08-09. Status: `PREDECLARED_BEFORE_IMPLEMENTATION`.

M224 changes exactly one failed M221 mechanism: the numerical chart.  It does
not change M216/M221's antithetic strict-distinct estimator,

```text
A_i;jk(g) = (Z_i;jk(g) + Z_i;jk(-g))/2,
```

its event ownership, deterministic moments, tree subtraction, 16-term Phi
recurrence, 32-panel Plackett/Simpson recurrence, event radius, seeds, speed
threshold, cost ceiling, or kernel topology.  M221's failed native speed gate
is inherited and is not rerun.  M224 cannot open variance.

The parent code hash is
`044D801B0EF0FDC0240FE3A2841D110956118CCACD25A7B8B0879D2B617B9F6D`.
The environment remains Python 3.14.4, NumPy 2.4.6, and FlopScope 0.10.0.
The bias class remains exact in expectation in real arithmetic.  No responses,
truth, scorer, MSE, challenge weights, or leaderboard data may be accessed.

## Frozen normalized chart

For repeated neuron `i` and singleton pair `j,k`, define

```text
s_j = sigma(j | standardized repeated preactivation)
r_j = s_j / sigma_j                         (and analogously r_k)
q_i(g) = (ReLU(mu_i + sigma_i g) - m_i) / sigma_i
alpha_j(g) = conditional_mean_j(g) / s_j
t_j(g) = (alpha_k(g) - rho alpha_j(g)) / sqrt(1-rho^2).
```

The chart is

```text
|rho| <= .08
|alpha_j|, |alpha_k|, |t_j|, |t_k| <= .8
.8 <= r_j,r_k <= 1.2
|q_i(g)| <= 9.
```

Every coordinate is exactly invariant under a positive diagonal neuron gauge
`mu -> D mu`, `Sigma -> D Sigma D`.  In normalized arithmetic,

```text
K = sigma_i^2 s_j s_k
beta_j = m_j/s_j, beta_k = m_k/s_k
C = R(alpha_j,alpha_k,rho) - beta_j H(alpha_k)
    - beta_k H(alpha_j) + beta_j beta_k
value = K * (mean_{g,-g}[q_i(g)^2 C(g)] - offset/K).
```

The bracket is gauge invariant, `K` carries exactly the expected
`d_i^2 d_j d_k` covariance, and chart membership cannot change.  This is an
algebraic refactor only; the estimator and pair kernel are unchanged.

## Frozen rho-.08 Plackett proof

Let `f(r)=phi2(a,b;r)` and `ell=log f`, with `|a|,|b|<=A=.8` and
`|r|<=R=.08`.  Expanding

```text
ell(r) = -.5 log(1-r^2) - (a^2+b^2)/(2(1-r^2))
         + ab r/(1-r^2) - log(2 pi)
```

on the real axis gives rigorous derivative bounds

```text
B1 = 11950/14283                    = .8366589652033887
B2 = 23621875/8869743               = 2.6631972313064765
B3 = 32225562500/5508110403         = 5.850565827883243
B4 = 33860911718750/1140178853421   = 29.69789486724254.
```

Because the quadratic exponent is nonpositive for real `|r|<1`,
`f <= 1/(2 pi sqrt(1-R^2)) < .159666697`.  Therefore

```text
|f''''| <= f (B4 + 4 B3 B1 + 3 B2^2 + 6 B2 B1^2 + B1^4)
         < 13.129531.
```

Composite Simpson with 32 panels then has

```text
error <= 13.129531 * .08^5 / (180 * 32^4)
      < 2.280e-13.
```

Thus the unchanged `2.5e-12` Phi2 enclosure still covers quadrature, Phi
terms, and binary64 rounding.  The unchanged event radius is
`1e-8*(1+abs(midpoint))`, against the frozen required ratio `2e-7`.

## Frozen falsifiers

TDD must first fail because the M224 module does not exist.  After
implementation, all of the following are binding:

1. The original 2,730-event M221 census (widths 3..7, seeds
   `221700003..221700007`, every strict owner and all 13 original outer probes)
   has zero fallback and lies inside the parent M216 interval.
2. All five original 3,968-row M221 native issuers (outer seeds
   `221720001..221720005`, context seeds `221730001..221730031`) have zero
   fallback; this must cover the previously observed `|rho|=.0788555...` rows.
3. A fresh, untuned 2,730-event cell census uses widths 3..7, seeds
   `224700003..224700007`, and the same owners/probes.  Any fallback kills M224;
   seeds and thresholds are not changed afterward.
4. The original positive gauge and permutation test has zero fallback,
   identical normalized chart membership, coordinate error `<=2e-14`, and
   scaled value error `<=5e-8`.
5. The inherited 17 high-precision probes plus 15 fresh probes compare 80 and
   100 digits within `1e-12*(1+abs(reference))` and fall inside M224's radius.
6. A synthetic `|rho|>.08` event must refuse rather than clip or zero.

Any failure kills this implementation locally.  Passing promotes only the
normalized numerical chart as a reusable component.  Native speed remains a
known failed link for a later separately predeclared child; no call fusion,
allocation reuse, native timing, source variance, or score experiment is
authorized here.
