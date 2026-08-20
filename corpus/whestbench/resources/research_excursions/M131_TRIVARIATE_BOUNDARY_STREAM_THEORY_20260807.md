# M131: trivariate boundary stream and projected-source sampling

Date: 2026-08-07  
Contract: generated mathematics and generated networks only; no scorer, benchmark,
public/private model, target, or outcome access  
Verdict: **KILL AS A COMPLETE CANDIDATE; PRESERVE FOUR COMPONENTS**

## Executive result

M131 closes both proposed escapes from M129's `[2,1,1]` construction cost.

1. Conditioning on the repeated coordinate gives an exact, stable one-dimensional
   representation of `E[(X_i)_+^2 (X_j)_+ (X_k)_+]` and its complete state
   Frechet derivative.  It is an excellent independent oracle.  It is not a
   target evaluator: a genuine trivariate orthant probability survives the
   fourth-cumulant and tree subtractions, and streaming every packed triple costs
   at least `1,973,816,524,800` bivariate-density evaluations before output
   contraction.
2. Direct affine-projected, normal-ordered sampling avoids all ambient order-three
   and order-four tensors.  It is unbiased, differentiable pathwise, and fits an
   installed-shape `<100B` worksheet at useful sample counts.
3. The exact first-Wiener-chaos common-random control reduces complete M125b
   response variance to `0.8230x` at the same number of samples.  Its extra dense
   products increase leading rectangular work from 14 to 26 full-bank
   equivalents.  At equal protected work it is `1.5869x` worse than the
   uncontrolled estimator.  This control is therefore killed in its materialized
   form.
4. Gaussianized Haar frames and regular simplices are lawful: every row is exactly
   Gaussian marginal after an independent chi radius.  A full-budget antithetic
   Haar frame reduces complete response variance to `0.9296x` iid.  This is a real
   but incremental component, not a candidate-changing mechanism.
5. On the binding generated `n=32,L=4` all-source response audit, the best
   projected-source analytic arm had per-output MSE `5.68781e-4`; direct input
   sampling at equal leading rectangular work had `1.73038e-4`.  The analytic
   arm was `3.287x` worse.  Its estimated infinite-sample squared-bias floor,
   `2.27729e-4`, already exceeded the entire direct-sampler MSE.

The recursive disposition is consequently precise: kill the deterministic full
stream, kill the materialized first-chaos control as a candidate, and preserve the
boundary oracle, cross-bank `k3^2` U-statistic, Gaussianized frame geometry, and
normal-ordered projected-source reference for other carriers.

## 1. Exact conditional boundary representation

Let `X ~ N(mu,C)` and let `i,j,k` be distinct.  Standardize the repeated
coordinate by

```text
X_i = mu_i + sigma_i g,       g ~ N(0,1).
```

Conditional on `g`, `(X_j,X_k)` is bivariate Gaussian with

```text
m_{j|g} = mu_j + C_ji g/sigma_i,
m_{k|g} = mu_k + C_ki g/sigma_i,

C_{jk|i} = C_{jk,jk} - C_{jk,i} C_{i,jk}/C_ii.
```

Therefore

```text
E[(X_i)_+^2 (X_j)_+ (X_k)_+]
 = integral_{-alpha_i}^infinity
     phi(g) (mu_i+sigma_i g)^2
     E[(X_j)_+(X_k)_+ | g] dg.                         (1)
```

The inner expectation is the exact bivariate rectified-normal raw moment.  M131
differentiates it with Bonnet/Price identities:

```text
d/d C_jk E[(X_j)_+(X_k)_+] = P(X_j>0,X_k>0),

d/d C_jj E[(X_j)_+(X_k)_+]
 = .5 f_j(0) E[(X_k)_+ | X_j=0],                       (2)
```

with the symmetric `kk` formula and exact mean derivatives.  No finite
difference is used.

For numerical stability, set

```text
g = -alpha_i + t/(1-t),       0<t<1.                   (3)
```

The squared repeated ReLU supplies a double zero at `t=0`, while the Gaussian
density suppresses `t -> 1`.  Paired Gauss-Legendre orders 32/48 are the default
certificate; orders 48/72 are used in the generated oracle tests.  This was much
more stable than unsplit tensor Gauss-Hermite across three kinks.

The implementation agrees with the independent M129 Hermite construction for
both value and state directional derivative.  A separate order-88 tensor
Gauss-Hermite calculation supplies a deliberately expensive third check.

The literature supports the ingredients but not the target-cost conclusion:

- [Manjunath and Wilhelm, arXiv:1206.5387](https://arxiv.org/abs/1206.5387)
  extends the Tallis moment-generating-function treatment to general mean,
  covariance, and rectangular truncation and gives bivariate marginal terms.
- [Galarza et al., arXiv:2009.13488](https://arxiv.org/abs/2009.13488) derives
  recurrences for arbitrary product moments of truncated/folded multivariate
  normal-family laws.
- [Mamis, arXiv:2202.00189](https://arxiv.org/abs/2202.00189) gives generalized
  multivariate Stein/Isserlis identities for Gaussian vectors times arbitrary
  functions.

## 2. The trivariate orthant term does not cancel

Write the trivariate positive-orthant probability as `Q3(mu,C)`.  The Tallis MGF
has the form

```text
M(t) = exp(mu.t + .5 t^T C t) Q3(mu+C t,C).             (4)
```

In the coefficient of `t_i^2 t_j t_k`, the multiplier of the *undifferentiated*
`Q3` is the untruncated Gaussian raw moment

```text
G_iijk = mu_i^2 mu_j mu_k
       + C_ii mu_j mu_k
       + 2 C_ij mu_i mu_k
       + 2 C_ik mu_i mu_j
       + C_jk mu_i^2
       + C_ii C_jk
       + 2 C_ij C_ik.                                  (5)
```

This is generically nonzero.  Even at zero mean it is

```text
C_ii C_jk + 2 C_ij C_ik.                               (6)
```

Every proper set-partition subtraction in the fourth cumulant factors into
univariate or bivariate moments.  The M122 bridge tree also contains no `Q3`.
Consequently no lower-dimensional cumulant or tree term can cancel the unique
`G_iijk Q3` contribution.  This proves that a constant-work evaluator made only
from one- and two-dimensional Gaussian primitives does not exist through this
route.

At `n=256`, the number of ordered repeated/distinct packed triples over 31 source
layers is

```text
31 * n * C(n-1,2) = 257,007,360.                        (7)
```

The paired 32+48 outer rule uses 80 nodes.  Charging only 96 density evaluations
per certified bivariate Plackett evaluation gives the favorable lower count

```text
257,007,360 * 80 * 96 = 1,973,816,524,800               (8)
```

before coefficient construction, Frechet arithmetic, output contraction,
copies, allocation, or residual wall time.  The deterministic boundary stream is
therefore **KILL** for deployment and **PASS** as a small-width oracle.

## 3. Direct projected normal ordering

Let `X=mu+L g`, `g~N(0,I)`, `H=ReLU(X)-E[ReLU(X)]`, and let the next affine
output be

```text
O = H W,       V = Cov(O) exactly.                      (9)
```

M131 samples the already-projected repeated tables rather than building a local
tensor.  For each sample, the normal-ordered polynomials are

```text
k3_aab:
  O_a^2 O_b - V_aa O_b - 2 V_ab O_a,

k4_aaab:
  O_a^3 O_b - 3 V_aa O_a O_b - 3 V_ab O_a^2
            + 3 V_aa V_ab,

k4_aabb:
  O_a^2 O_b^2 - V_aa O_b^2 - V_bb O_a^2 - 4 V_ab O_a O_b
              + V_aa V_bb + 2 V_ab^2.                  (10)
```

Their expectations are exactly the connected cumulants.  Diagonals supply
`k3_aaa` and `k4_aaaa`.  The Cholesky tangent is exact:

```text
Ldot = L Phi(L^{-1} Cdot L^{-T}),                       (11)
```

where `Phi` retains the strict lower triangle and halves the diagonal.  This
gives the complete fixed-node pathwise Frechet derivative of (10).

Two independent banks are retained.  For the M128 `k3^2` diagram, M131 now forms
the ordered-distinct-bank U-statistic.  For a pair `(i,j)`, define

```text
K_p = kappa[i repeated p, j repeated 3-p],  0<=p<=3,

A_q = sum_{p+r=q} C(3,p) C(3,r) K_p K_r.                (12)
```

Products in (12) are averaged only over distinct banks.  Same-bank squares are
forbidden.  The implementation returns all seven `A_q` and their exact product
tangent.  This closes product ownership, but the response-variance audit below
is explicitly first-order linear `k3/k4`; it does not pretend that the complete
M128 quadratic response was tested.

## 4. Exact first-chaos control and why it loses after cost

Let

```text
G_i = (X_i-mu_i)/sigma_i,
h1_i = E[(X_i)_+ G_i] = sigma_i Phi(alpha_i),
P_i = h1_i G_i.                                         (13)
```

`P` is the orthogonal first-Wiener-chaos projection of centered ReLU.  It is
jointly Gaussian with exact covariance

```text
Cov(P) = diag(h1) Corr(X) diag(h1).                      (14)
```

Thus every population third/fourth cumulant of `P W` is identically zero.  On
the same Gaussian sample, M131 estimates

```text
normal_order(O) - normal_order(PW).                     (15)
```

Equation (15) is unbiased without an add-back and removes the leading affine
Gaussian fluctuation.  Degree-4 tensor Gauss-Hermite makes the control's value
and tangent vanish to `3e-12`; fixed-node finite differences validate the full
controlled tangent.

The failure is economic.  With two banks:

```text
uncontrolled: 11 full-bank + 3 per-bank products
             = 14 full-bank row equivalents,

controlled:   20 full-bank + 6 per-bank products
             = 26 full-bank row equivalents.           (16)
```

At fixed sample count the complete response variance ratio is `0.823043`.
At fixed work it is approximately

```text
0.823043 * 26/14 = 1.5285,                              (17)
```

and the realized equal-work audit gives `1.586879`.  Break-even requires the
controlled schedule to cost less than `1/0.823043 = 1.2150` times the base,
i.e. fewer than about 17 full-bank equivalents.  The current schedule uses 26.
At least nine equivalents must disappear; ordinary call fusion cannot do that.
Only a different response-projected estimator, which never materializes both
sets of repeated tables, could reopen this control.

## 5. Gaussianized biological/design geometry without folklore

Let `q` be a Haar-uniform unit vector and let `r~chi_n` independently.  Then

```text
g = r q ~ N(0,I_n) exactly.                              (18)
```

M131 applies (18) to two dependent angular families:

1. rows of a Haar orthobasis, with pairwise inner product zero;
2. a Haar-rotated regular simplex of `n+1` directions, with pairwise inner
   product `-1/n`.

Independent chi radii make every row exactly Gaussian marginal.  The source
estimators are linear averages of (10), so marginal exactness is sufficient for
unbiasedness even though rows are dependent.  Separate Haar rotations/radii are
used for the two `k3^2` banks.  Reusing a rotation across source layers while
refreshing radii/permutations is also unbiased; the audit measures its induced
cross-layer response covariance rather than assuming its sign.

The external results motivate, but do not certify, this particular integrand:

- [Lin et al., *Demystifying Orthogonal Monte Carlo and Beyond*,
  arXiv:2005.13590](https://arxiv.org/abs/2005.13590) studies OMC via negative
  dependence and concentration.
- [Choromanski et al., *The Geometry of Random Features*, AISTATS 2018](https://proceedings.mlr.press/v84/choromanski18a.html)
  analyzes variance improvements for stated random-feature/kernel classes.
- [Reid et al., *Simplex Random Features*, ICML 2023](https://proceedings.mlr.press/v202/reid23a.html)
  proves simplex results for softmax/Gaussian random-feature classes.

None proves a favorable variance sign for a signed, normal-ordered ReLU cumulant
response.  The generated M125b comparison remains binding.  It finds:

```text
fresh frame / controlled iid variance       0.859554
fresh simplex / controlled iid variance     0.764940
antithetic frame / equal-S iid variance      0.929617.   (19)
```

The last arm is the fair full-budget comparison.  It is a real 7.0% response
variance reduction, but too small to change the branch verdict.

## 6. Protected target-shape worksheet

These are installed-*shape* bills using the stated GEMM convention, not native
FlopScope traces.  They include 31 layers, float32 rectangular products, a
conservative float64 Cholesky/Frechet cap, 25% protection, the protected carrier
`16.971970384B`, and a `1.6B` response/cross-bank reserve.

| source replacement | samples/bank | source raw | complete protected |
|---|---:|---:|---:|
| iid normal order | 512 | 64.434733056B | 99.115386704B |
| antithetic Haar normal order | 512 | 64.568950784B | 99.283158864B |
| iid first-chaos controlled | 256 | 60.200845312B | 93.823027024B |
| Haar first-chaos controlled | 256 | 60.335063040B | 93.990799184B |
| simplex first-chaos controlled | 257 | 60.548795392B | 94.257964624B |

The Haar rows add a conservative reusable two-bank QR reserve of `0.134217728B`
raw.  Fresh per-layer QR would add more and is not hidden in this table.  The
worksheet proves arithmetic feasibility under `100B`; it does not prove native
dtype parity, residual time, memory, call fusion, or contest efficacy.

## 7. Binding generated response audit

The reproducible audit uses:

```text
width                         32
depth                         4        (L/n = 1/8)
fresh generated weights/state only
all local k3/k4 source insertions
complete M121 one-delay mean/covariance conversion
complete M125b inhomogeneous coalescing
160 independent repetitions
800,000 antithetic direct samples for truth
1,664 direct samples/repetition at matched leading rectangular work
```

The direct sample count equals the controlled source's 26 full-bank row
equivalents times its 64 total local rows.  This comparison ignores the
analytic method's extra factorization, coefficient, and copy work, so it is not
unfairly charging the direct arm.

| method | per-output variance | squared bias | per-output MSE |
|---|---:|---:|---:|
| Gaussian closure, deterministic | 0 | 4.86038e-4 | 4.86038e-4 |
| uncontrolled iid, S=n/bank | 6.61706e-4 | 2.04093e-4 | 8.61664e-4 |
| controlled iid, S=n/bank | 5.44612e-4 | 2.11867e-4 | 7.53075e-4 |
| controlled fresh simplex, S=n+1/bank | 4.16596e-4 | 2.11020e-4 | 6.25012e-4 |
| uncontrolled iid, S=2n/bank | 3.43197e-4 | 2.27729e-4 | **5.68781e-4** |
| uncontrolled antithetic Haar, S=2n/bank | 3.19042e-4 | 2.61564e-4 | 5.78611e-4 |
| direct input MC, matched leading work | 1.71164e-4 | 2.94379e-6 | **1.73038e-4** |

The different empirical bias estimates among analytic sampling designs are
finite-repetition fluctuations: all designs are marginally unbiased for the
same first-order analytic response.  Their common population bias is not known
exactly, but each estimate is around `2.0e-4` to `2.6e-4`; the between-method
variance of the sample mean is only the displayed variance divided by 160.
Thus the conclusion that the analytic truncation floor exceeds the direct arm's
entire MSE is not a one-repetition artifact.

The audit is a falsifier, not an extrapolation theorem from `(32,4)` to
`(256,32)`.  It deliberately matches `L/n=1/8`, exercises every source
insertion and the final output functional, and is strong enough to reject a
promotion claim.  A target candidate would still require native tracing and a
predeclared target-shape efficacy gate.

Raw results are in
`m131_trivariate_boundary_stream/m131_response_variance_audit_n32_l4_r160.json`.

## 8. Test ledger

`python -m unittest -v test_m131_trivariate_boundary_stream.py`:

```text
11 tests passed in 1.259 s
```

The tests cover:

1. exact bivariate Price/Bonnet Frechet derivative;
2. conditional `[2,1,1]` value and tangent against Hermite and tensor-GH oracles;
3. conditional collision defect against the independent M129 set-partition path;
4. Cholesky Frechet identity and fixed-difference check;
5. projected normal ordering against a dense small-width cumulant oracle;
6. complete pathwise source tangent;
7. exact-zero first-chaos value/tangent and controlled fixed differences;
8. complete one-delay response against an independent Hermite-score integral;
9. Haar/simplex geometry and antipodal ownership;
10. independent-bank `k3^2` binomial convolution ownership;
11. mechanical monotone cost and independent-bank checks.

Stable code hashes at the completed run:

| artifact | SHA-256 |
|---|---|
| `m131_trivariate_boundary_stream.py` | `1bb1912b82f8d7b7a204bc19d0d260a9050f02e83b8e87d322188632882ecac3` |
| `test_m131_trivariate_boundary_stream.py` | `60be4a4c7481a2bb40f28d8a89a7f99bdce738b4ac573cdd93276c9bb4d0e207` |
| `run_m131_response_variance_audit.py` | `600d52701b508b59350d773fcf9b52c7ff939df313a2332bc5fa18c699e0968f` |

The result JSON was added after these hashes and is not included in them.

## 9. Recursive promotion ledger

### KILL

- **All-triple deterministic boundary stream.**  Exact, but the surviving `Q3`
  term and `1.974T` favorable primitive count are fatal.
- **Materialized first-chaos controlled source.**  Variance mechanism passes;
  variance per protected work fails by `1.59x`.
- **M131 as a winning entry.**  Generated end-to-end MSE loses to direct
  sampling by `3.287x`, and the inferred analytic bias floor already loses to
  the finite direct estimator.

### PRESERVE

- conditional one-dimensional `[2,1,1]` value/tangent as a certification oracle;
- direct affine normal-order reference and exact Cholesky tangent;
- ordered-distinct-bank M128 `k3^2` convolution U-statistic;
- Gaussianized antithetic Haar/simplex banks as a modest variance component.

### ONLY CREDIBLE REPAIR

The first-chaos control reopens only if a response-projected formulation reduces
its 26 full-bank equivalents below about 17 without losing complete one-delay
and M125b ownership.  A source-table fusion that saves one or two calls is
mathematically insufficient.  Separately, M133's fixed-count importance sampling
of canonical `[2,1,1]` triples remains non-overlapping: it samples the surviving
`Q3` coefficient rather than pretending it cancels.  Its output-response variance
per protected FLOP is the correct next gate.

That is the M131 failure-local handoff.
