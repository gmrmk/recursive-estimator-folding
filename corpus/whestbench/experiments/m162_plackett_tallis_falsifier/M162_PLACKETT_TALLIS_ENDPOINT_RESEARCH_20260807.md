# M162: Plackett–Tallis dimensionless trivariate endpoint research

## Decision

**KILL the fixed common-node Plackett/Owen-T/Genz-line implementation; keep the generic endpoint family open.** A compact deterministic reduction exists for the `[2,1,1]` coefficient, but it does not provide the missing uniform certificate across high-correlation and singular strata. M162 earns no `606,720`-operation implementation credit.

This is response-free research. It does not evaluate source variance or make a model, score, or efficacy claim.

## Exact moment reduction

Work in M159's dyadically normalized local state. Let `X ~ N(mu,Sigma)`, `Y=X_+` coordinatewise, and define

\[
P(\nu,\Sigma)=\Pr_{Z\sim N(\nu,\Sigma)}(Z_0,Z_1,Z_2>0).
\]

Tallis's exponential tilt gives the unnormalised truncated MGF:

\[
T(u)=\mathbb E[e^{u^T X}{\bf1}_{X>0}]
=\exp(\mu^Tu+\tfrac12u^T\Sigma u)P(\mu+\Sigma u,\Sigma). \tag{1}
\]

Therefore all required raw ReLU moments are derivatives of one scalar object:

\[
M_{p_0p_1p_2}=\partial_{u_0}^{p_0}\partial_{u_1}^{p_1}\partial_{u_2}^{p_2}T(0),
\quad p_0\in\{0,1,2\},\quad p_1,p_2\in\{0,1\}. \tag{2}
\]

There are twelve raw moments. They form

\[
C_{211}=\mathbb E[(Y_0-m_0)^2(Y_1-m_1)(Y_2-m_2)],\qquad
\kappa_{211}=C_{211}-V_{00}V_{12}-2V_{01}V_{02}. \tag{3}
\]

The existing M129 tree continuation requires only this same first- and second-moment cache. Thus `Delta_211=kappa_211-tree(0,0,1,2)` needs no fourth-order tensor if (2) is available. Tallis eliminates a separate integral for every ReLU monomial, not the numerical trivariate truncation problem.

## Smallest probability/boundary inventory

At a positive-marginal SPD state, mean derivatives of `P` are boundary integrals:

\[
P_i=f_{X_i}(0)\Pr(X_{-i}>0\mid X_i=0),\tag{4}
\]

and, for distinct `i,j`,

\[
P_{ij}=f_{X_i,X_j}(0,0)\Pr(X_k>0\mid X_i=X_j=0).\tag{5}
\]

Repeated derivatives recursively add normal pdf/CDF factors and conditional mean/covariance derivatives but no further trivariate probability. Hence the algebraic minimum through order four is one `P3`, three bivariate facet probabilities `P2^(i)`, three univariate edge probabilities `P1^(ij)`, and one vertex density. The `P2` values admit an Owen-T/bivariate-normal representation.

Differentiating the Plackett formula below with a 35-coefficient Taylor jet is an alternative computation: it evaluates `P3` and all needed mean derivatives in one vector integral. That removes calls to `P2`, not the same singular boundary algebra.

## One-dimensional Plackett line formula

Let `R` be the correlation matrix and `a_i=mu_i/sigma_i`, hence `P(mu,Sigma)=Phi_3(a;R)`. On the SPD path

\[
R(t)=I+t(R-I),\qquad 0\le t\le1,
\]

Plackett's identity gives

\[
\Phi_3(a;R)=\prod_i\Phi(a_i)+\int_0^1\sum_{i<j}r_{ij}\phi_2(a_i,a_j;tr_{ij})
\Phi\!\left({a_k-m_{k\mid ij}(t)\over s_{k\mid ij}(t)}\right)dt.\tag{6}
\]

`m_{k|ij}` and `s_{k|ij}` are the ordinary conditional Gaussian mean and standard deviation using the `ij` block of `R(t)`. This is a deterministic **one-dimensional** representation for SPD `R`; each integrand evaluation uses elementary arithmetic, one bivariate density, and one univariate CDF.

For zero thresholds, the conditional CDF is `1/2`, yielding the exact reference

\[
\Phi_3(0;R)=\frac18+{\arcsin r_{01}+\arcsin r_{02}+\arcsin r_{12}\over4\pi}.\tag{7}
\]

## Fixed-rule falsification

The isolated packet evaluates two 87-node fixed Gauss–Legendre rules for the centered formula: straight integration in `t`, and the endpoint map `t=1-u^2` followed by fixed integration in `u`. Each gets the exact analytic reference (7).

| State `(r01,r02,r12)` | Rule | Absolute error |
|---|---|---:|
| `(.999,0,0)` | straight 87-node | `4.1205795886511964e-8` |
| `(.999999,0,0)` | endpoint-square 87-node | `3.931942285650969e-8` |

Both exceed `2e-8` before noncentrality, moment derivatives, tree algebra, or a tangent is introduced. These are closed-form centered orthant identities, not response outcomes.

The mechanism is structural. At zero threshold a pair contribution contains

\[
{r\over4\pi\sqrt{1-t^2r^2}},\tag{8}
\]

whose endpoint layer tightens as `r` tends to one. The square map removes the literal singularity at `r=1` but leaves a moving near-endpoint layer for `r<1`; coarse/fine fixed-node agreement is not an interval remainder proof.

There is a more serious derivative problem. The exact centered bivariate probability obeys

\[
{d\over dr}\Phi_2(0,0;r)={1\over2\pi\sqrt{1-r^2}}.\tag{9}
\]

At `nextafter(1,0)`, (9) is `10,680,707.430881744`. Positive-part moments may have finite rank-face limits only after analytic cancellation between probability derivatives and polynomial prefactors. An opaque numerically enclosed `P3` line integral cannot certify those cancellations. A successor must factor them symbolically, as the existing bivariate endpoint bridge does; more fixed nodes do not prove that fact.

## Strata, cost, and remaining obstruction

- **SPD:** (6) is a promising one-dimensional value representation. A 35-component derivative jet can cover (2), but M162 has no uniform interval remainder or native bill.
- **Rank one:** use M154's exact moving-kink partition, not a fixed quadrature endpoint limit.
- **Rank two with positive marginals:** (6) has an integrable SPD limit but a terminal conditional variance can vanish; a rank-aware limiting proof is still required.
- **Zero marginal variance:** M159's primary dyadic ABI preserves the deterministic state, but correlation coordinates are undefined. Deterministic reduction plus an explicitly one-sided/conic tangent route is mandatory.

Thus the literal scope “one fixed certified 1D rule across SPD, rank-one/rank-two, and zero-variance strata” fails for this mechanism. M162 does **not** prove that every parameter-aware interval transform costs more than `606,720`; it establishes that no fixed-rule cost credit is justified until symbolic cancellation, rank branches, a mixed-error enclosure, and a native cost trace exist.

## Evidence and sources

- [Plackett (1954), *A Reduction Formula for Normal Multivariate Integrals*](https://doi.org/10.1093/biomet/41.3-4.351): correlation-differentiation reduction used in (6).
- [Tallis (1961), *The Moment Generating Function of the Truncated Multi-Normal Distribution*](https://doi.org/10.1111/j.2517-6161.tb00408.x): truncated-normal MGF route in (1)–(2).
- [Price (1958), *A Useful Theorem for Non-Linear Devices Having Gaussian Inputs*](https://doi.org/10.1109/TIT.1958.1057444): covariance differentiation relevant to the required tangent and boundary terms.
- [Genz (1992), *Numerical Computation of Multivariate Normal Probabilities*](https://doi.org/10.1080/10618600.1992.10477010): transformed numerical integration setting; not a fixed-rule certificate here.
- [Wang and Kennedy (1992)](https://doi.org/10.1016/0167-9473(92)90007-3): interval analysis plus automatic differentiation for self-validation, the missing ingredient for a certified future jet.
- The [official CRAN `mvtnorm` package](https://stat.ethz.ch/CRAN/web/packages/mvtnorm/index.html) documents `pmvnorm`'s Genz/Bretz/Miwa lineage, but does not establish this source's all-strata error or billing contract.

## Artifact and firewall

`m162_plackett_tallis_falsifier.py` is a standard-library-only analytic probability falsifier. Its four tests cover the rank-one common-factor limit, both fixed-rule counterexamples, and the rank-face derivative blow-up. No response cells, model outputs, truth, scorer, leaderboard, submission, or champion data are read.

**Disposition:** `KILL_FIXED_COMMON_NODE_PLACKETT_LINE_RULE; KEEP_M159_SCALE_CARRIED_GENERIC_FAMILY_OPEN; REQUIRE_SYMBOLIC_CANCELLATION_PLUS_RANK_AWARE_INTERVAL_CERTIFICATE_AND_NATIVE_COST_TRACE`.
