# M108 adversarial audit: centered cymatic band energy

**Date:** 2026-08-07  
**Scope:** mathematics and no-network numerical checks only.  No contest
network, target, scorer, M107 packet, champion, or estimator was read or
modified.  
**Verdict:** **FAIL_TO_DRAFT for the centered-energy candidate.**  The heat
multiplier is a legitimate fixed reference filter, but its unit-variance
zonal realization has an astronomically heavy fourth moment in dimension 256.
Squaring it makes the proposed control unsuitable for the predeclared
finite-frame/cross-fit gate before any network is run.

This audit preserves the useful translation of the metaphor:

```text
Chladni displacement -> spherical-harmonic zonal B
Chladni intensity    -> B^2 - 1
```

It rejects only the second arrow at the specified degree band and
normalization.  It is not a claim that every bounded, raw-zonal, or otherwise
regularized harmonic control is impossible; those would be distinct
operators requiring a new frozen mechanism and gate.

## 1. Exact scaled recurrence

Let `d=256`, `alpha=(d-2)/2=127`, and

\[
 P_l(t)={C_l^{\alpha}(t)\over C_l^{\alpha}(1)},\qquad
 N_l=\dim\mathcal H_l
 ={(2l+d-2)(l+d-3)!\over l!(d-2)!}.
\]

The normalized zonal recurrence is

\[
 P_{l+1}=A_l tP_l-B_lP_{l-1},\quad
 A_l={2l+d-2\over l+d-2},\quad B_l={l\over l+d-2}.
\]

For `q_l=sqrt(N_l) P_l`, define

\[
 r_l={N_{l+1}\over N_l}
 ={2l+d\over2l+d-2}{l+d-2\over l+1}.
\]

Substitution of `P_l=q_l/sqrt(N_l)` gives, without approximation,

\[
 q_0=1,\quad q_1=\sqrt d\,t,\quad
 q_{l+1}=A_l\sqrt{r_l}\,tq_l
 -B_l\sqrt{r_lr_{l-1}}q_{l-1}.
\]

Thus the recurrence quoted in the mutation note is correct through degree 32
(and beyond); it is not a repeated depth transfer matrix, merely a
degree-dependent three-term polynomial recurrence.  Useful coefficient checks
are:

| `l` | coefficient of `t q_l` | coefficient of `q_(l-1)` | `r_l` |
|---:|---:|---:|---:|
| 1 | 11.3800651296 | 0.711254070597 | 128.49609375 |
| 8 | 5.58077397571 | 0.948004506397 | 29.3267489712 |
| 18 | 4.04789438059 | 0.978261196736 | 14.4145190563 |
| 31 | 3.31940070685 | 0.988761012883 | 8.96261867089 |

The addition theorem yields, for fixed unit axes `a,b` and `U` uniform on
the sphere,

\[
 E q_l(a^TU)=0\ (l>0),\qquad
 E[q_l(a^TU)q_k(b^TU)]=\mathbf1_{l=k}P_l(a^Tb).
\]

In particular, each `q_l(a^T U)` is exactly unit variance.  This establishes
the exactness claims, but says nothing yet about a fourth moment.

## 2. Frozen heat band: correct, but not uniquely physical

For the stipulated even degrees

\[
 \mathcal L=\{8,10,\ldots,32\},\quad
 \lambda_l=l(l+254),\quad
 t_1={\log2\over\lambda_{18}}=1.4157417903593654\,10^{-4},
\]

use

\[
 b_l=e^{-t_1\lambda_l}-e^{-2t_1\lambda_l},\quad
 c_l={b_l\over(\sum_{r\in\mathcal L}b_r^2)^{1/2}},\quad
 B_a(u)=\sum_{l\in\mathcal L}c_lq_l(a^Tu).
\]

The continuous-`lambda` maximum of `exp(-t lambda)-exp(-2t lambda)` is at
`lambda=log(2)/t`, hence exactly `lambda_18=4896`.  Its discrete normalized
coefficients are fixed, nonnegative, and peak at degree 18:

```text
l       8       10      12      14      16      18      20      22      24      26      28      30      32
c_l  .231219 .260015 .280357 .293541 .300718 .302904 .300997 .295779 .287933 .278049 .266632 .254114 .240861
```

Therefore `E B_a=0` and `E B_a^2=sum c_l^2=1` exactly.

The comparison operators are mathematically distinct but do not provide a
free model-selection argument:

| label | multiplier before normalization | peak condition | relation to the frozen heat band |
|---|---|---|---|
| heat difference | `exp(-t lambda_l)-exp(-2t lambda_l)` | `lambda=4896` | frozen reference |
| Poisson difference | `r^l-r^(2l)`, `r=2^(-1/18)` | `l=18` | normalized coefficient cosine is `0.9999410374` on this band |
| Helmholtz shell | `1[l=18]` | exact degree 18 | a single channel, not a spatially localized heat packet |

The Poisson and heat filters are virtually collinear on the predeclared
finite band.  Helmholtz is a pure spectral shell.  Heat is therefore
defensible only as a **predeclared convention**, not as evidence that a heat
equation governs the heterogeneous gated network.  No post-result migration
among these rows is licensed.

## 3. Centered-energy law and the missing aggregation calculation

For `E_a=B_a^2-1`, the stated identity is correct:

\[
 E E_a=E B_a^2-1=0.
\]

For any weights-only axes `a_j`, the proposed aggregate

\[
 H_C={1\over\sqrt m}\sum_{j=1}^m E_{a_j}
\]

also has exact conditional spherical mean zero.  It remains unbiased after a
coefficient is fitted using independent Haar-frame blocks: conditional on all
other blocks, the coefficient and axes are fixed and the held block has the
correct marginal uniform law.  Dependence among points within one frame is a
variance-estimation issue, not a mean-law exception.  This proof applies to
L1's independently randomized frames, not to a holdout MUB basis sharing a
single rotation.

However, the `1/sqrt(m)` is a scale convention, not a variance guarantee.  To
make that explicit, expand the squared band in the same orthonormal zonal
basis:

\[
 B(t)^2=\sum_{k=0}^{64}d_kq_k(t),\qquad
 d_k=E[B(a^TU)^2q_k(a^TU)].
\]

Only even `k` occur and `d_0=1`.  The exact cross-axis covariance is

\[
 K(s)=\operatorname{Cov}(E_a,E_b)
   =\sum_{k=1}^{64}d_k^2P_k(s),\quad s=a^Tb,
\]

and hence

\[
 \operatorname{Var}(H_C\mid a_{1:m})
 =\underbrace{\sum_{k>0}d_k^2}_{\operatorname{Var}(E_a)}
 +{1\over m}\sum_{j\ne r}K(a_j^Ta_r).
\]

So aggregation cannot turn a giant single-axis energy variance into a small
one.  For iid random axes, `E_axes K(a^T b)=0` for every `k>0`, so the expected
conditional variance is exactly `Var(E_a)`, not `Var(E_a)/m`.  The off-axis
fluctuation has exact second moment

\[
 E_{a,b}K(a^Tb)^2=\sum_{k>0}{d_k^4\over N_k}.
\]

This is the correct cross-axis check omitted from the mutation note.

## 4. No-network quadrature result: the candidate fails its own kurtosis gate

All numbers in this section are deterministic calculations on the one-
dimensional spherical marginal, not networks.  If `t=a^TU`, its density is
proportional to `(1-t^2)^126.5`.  A 65-node Gauss--Jacobi rule with parameters
`(126.5,126.5)` integrates every polynomial through degree 129 exactly in
exact arithmetic.  `B^4` has degree at most 128.  I evaluated the recurrence
in float64 and normalized the Jacobi weights; the result was repeated with
65, 80, 100, 130, 160, and 256 nodes.

```text
E[B]                         -1.56e-17       (100-node check)
E[B^2]                        1.00000000000004
E[B^4]                        2.046953098540e23
Var(B^2-1)                    2.046953098540e23
```

The fourth moment was stable to the displayed precision across all six node
counts.  This is not a quadrature tail accident: polynomial exactness begins
at 65 nodes, and the independent expansions satisfy

`sum_k d_k^2 = 2.0469530985404808e23`.

For scale, pure scaled zonals already have huge fourth moments:

```text
q_8:  1.155799444680e6
q_18: 1.690814244219e14
q_32: 6.656218745732e24
```

The frozen mixture remains at `2.05e23`; it has not regularized this
needle-like behavior.  The dominant energy-self-convolution coefficients are
around degrees 34--44 (for example `d_40=1.976881148498e11`), not around the
original degree-18 center.  This is the concrete spectral self-convolution
failure: after squaring, the proposed “band energy” is a broad 0--64 spectrum
whose variance is concentrated in high-degree tail geometry.

Cross-axis quantities corroborate rather than rescue it:

```text
K(0)                         -0.9845478073
K(1/sqrt(256))               -0.9513492519
K(1)                          2.046953098540e23
E_{a,b}[K(a^T b)^2]           7.435448080492e6
```

For 256 iid axes, the standard deviation of the off-axis term in the
conditional variance formula is about `3.85e3`, utterly negligible relative
to `2.05e23`.  (The `sqrt(2)` accounts for the two orientations of each
unordered pair.)  A particular nearly orthogonal weight matrix changes only
that small additive term; it cannot make the candidate's energy variance
finite-frame sized.

The frozen note's hard-kill threshold was held-block excess kurtosis at most
50.  The exact population excess is approximately `2.046953e23`, so the
candidate fails before a frame, a network, a regression, or a score is
observed.  With only tens of frames, the rare caps controlling this fourth
moment will almost never be seen in coefficient fitting, making an apparent
small-sample regression particularly untrustworthy rather than mitigating the
law.

## 5. Numerical stability: not the cause, but a second deployment warning

The scaled recurrence avoids underflow of raw `P_l`, but it creates genuine
dynamic range.  At `t=1`,

```text
sqrt(N_8)  = 2.257069424309e7
sqrt(N_18) = 7.888814060879e13
sqrt(N_32) = 1.673280670218e21
```

These values and their squares are below float64 overflow, so overflow is not
the explanation for the failure.  They do make cancellation and rare-event
dominance material.  A direct float64 recurrence through degree 32 was
checked against a 100-decimal recurrence on the fixed grid
`{-1,-(1-1e-12),-.9,-.5,-.1,-1/16,0,1/16,.1,.5,.9,1-1e-12,1}`.  The largest
relative discrepancy was `6.92e-13` (near a small polynomial value); the
largest absolute discrepancy occurs at endpoint-scale values and is not a
meaningful accuracy certificate there.  Thus the identity failure is not a
float32/float64 artifact, but a future linear-band implementation would still
need float64, endpoint/parity checks, and a material-excursion reject rule.

## 6. Does the same tail law also kill the linear heat band A? Yes.

It would be wrong to infer from `E B^2=1` that the signed band is safe while
only its square is unsafe.  Standardized kurtosis is invariant to arbitrary
rescaling, so scaling the `q_l`, the band, or a regression column cannot hide
this issue.

First consider the stipulated uniform mixture over `m=256` independent first
layer axes, at a single marginally uniform direction.  Under the generated
weight law, conditional on `U` the variables `B_{a_j}(U)` are iid with mean
zero, variance one, and fourth moment `kappa_B=E B^4`.  Hence exactly

\[
 {E\left[(m^{-1/2}\sum_jB_{a_j})^4\right]
  \over \operatorname{Var}(m^{-1/2}\sum_jB_{a_j})^2}
 =3{m-1\over m}+{\kappa_B\over m}
 =7.9959113\ldots\times10^{20}.
\]

The actual L1 observable is a Haar-frame block average, not one arbitrary
point.  That extra structure still cannot regularize enough.  Here is an
exact no-network calculation for it.  Fix a Haar frame `Q=(q_1,...,q_d)` and
an independent uniform axis `a`, and set

\[
 Z(a,Q)={1\over d}\sum_{i=1}^dB(a^Tq_i).
\]

By rotational invariance we can take `q_i` to be coordinate axes.  Then
`y_i=(a^Tq_i)^2` has the Dirichlet law

\[
 (y_1,\ldots,y_d)\sim\operatorname{Dirichlet}(1/2,\ldots,1/2).
\]

The band is even, so write `B(a^Tq_i)=p(y_i)` with `p` a degree-16
polynomial.  Each required joint moment is then exact from

\[
 E\prod_{r=1}^k y_r^{e_r}
 ={\Gamma(d/2)\over\Gamma(d/2+\sum e_r)}
 \prod_{r=1}^k{\Gamma(1/2+e_r)\over\Gamma(1/2)}.
\]

Expanding the fourth power by index-collision partitions gives

\[
\begin{aligned}
 E Z^4=d^{-4}\big[&dM_4+4d(d-1)M_{31}+3d(d-1)M_{22}\\
 &+6d(d-1)(d-2)M_{211}
 +d(d-1)(d-2)(d-3)M_{1111}\big],
\end{aligned}
\]

where `M_{r_1...r_k}=E[prod_s p(y_s)^{r_s}]`.  High-precision polynomial
arithmetic produces

```text
M_4       2.0469530985404400164882118e23
M_31      7.1172194346720317e7
M_22      1.5452192671523919e-2
M_211     1.2255448804127850e-7
M_1111   -5.27e-16  (numerical zero at the cancellation scale)

Var Z     3.906251210072194e-3
E Z^4     1.2200791231043136e16
Kurtosis(Z) 7.995905587256679e20
```

As a cross-check, the variance also follows directly from the addition theorem:

\[
 \operatorname{Var}Z=\sum_{l\in\mathcal L}c_l^2
 {1+(d-1)P_l(0)\over d}=0.00390625121007219\ldots.
\]

Finally, conditionally on a frame, the 256 random-axis block variables are
iid.  For the actual uniformly aggregated block statistic
`m^{-1/2} sum_j Z(a_j,Q)`, the standardized fourth moment is therefore

\[
 3{255\over256}+{\operatorname{Kurtosis}(Z)\over256}
 =3.123400620022140\ldots\times10^{18}.
\]

That is still eighteen orders of magnitude above even a very permissive
finite-frame regression regime.  The random W1 axes and complete Haar frames
are a quantitatively insufficient regularizer, not a mechanism for escaping
the tail.  This derivation is over the legitimate generated first-layer
weight/axis distribution; a particular fixed realization cannot carry a
universal regularity claim that its generating law fails so severely.

Consequently the linear heat band `A`, in its **orthonormal-scaled** frozen
form from the cymatic note, also receives **FAIL_TO_DRAFT**.  This disposition
does not invalidate M107's raw `P_l` controls: M107 explicitly avoids blindly
materializing `sqrt(N_l)P_l` and is a different operator with a separate
frozen gate.

## 7. Required small tests if this mechanism is ever reopened

No reopening is authorized by this audit.  A distinct future mechanism should
first pass all of the following without a network:

1. Compare `q_0,...,q_32` from the float64 recurrence against a 100-bit
   recurrence at fixed interior points and both endpoints; verify parity and
   `q_l(1)=sqrt(N_l)`.
2. Use a >=65-node Gauss--Jacobi `(126.5,126.5)` rule to verify `E B=0`,
   `E B^2=1`, `E(B^2-1)=0`, and to compute—not merely sample—`E B^4`.
3. Expand `B^2` in `q_0,...,q_64`; verify `d_0=1`, the Parseval equality
   `sum d_k^2=E B^4`, and `K(s)=sum_{k>0}d_k^2P_k(s)` at `s=0,1/16,1`.
4. Check that the exact mean-zero law survives a frame-block holdout only
   when the coefficient is fitted on independent L1 Haar frames; treat a
   shared-rotation MUB basis as dependent.
5. Before any MLP is evaluated, reject a proposed squared feature if its
   exact excess kurtosis breaches the frozen cap.  Sampling a few Haar frames
   is not an adequate replacement for this calculation.

## 8. Operation and memory consequence in L1

For L1, `t=first_pre/(rho*column_norm)` reuses the existing first-layer
matmul.  Streaming the 31 degree updates and 13 selected coefficients is
still roughly `1.239e9` scalar recurrence/band operations at the stated
`S=32,256`, `m=256`, before all FlopScope and residual-time charges.  Energy
adds one square plus one reduction per axis and a final center/scale, roughly
`1.658e7` scalar operations.  It can be implemented with two `S x m`
recurrence buffers plus one accumulator; storing an `S x m x 32` tensor is
unnecessary.

That arithmetic/memory profile is only relevant if the statistic is viable.
Here it is not: no plausible small incremental charge compensates for a
population energy variance of order `10^23`.  A fully charged L1 integration,
FlopScope trace, or generated-network screen is therefore not authorized for
M108-C.

## Final disposition

**Exactness:** PASS.  The `q_l` recurrence, heat multiplier, unit variance,
zero mean, conditional cross-fit unbiasedness, and covariance decomposition
are sound.

**Centered-energy and scaled-linear mechanisms:** FAIL_TO_DRAFT.  Exact
no-network harmonic calculation violates the energy candidate's kurtosis gate
by about twenty-one orders of magnitude.  Exact Dirichlet/frame/axis
calculation leaves the scaled-linear band with standardized kurtosis
`3.12e18` even after all 256 frame directions and all 256 uniform W1 axes are
aggregated.  Do not freeze, package, run, or score M108-C or scaled M108-A.
Preserve the heat multiplier only as an immutable mathematical reference; it
is not a promoted linear-band or energy-control candidate.

**Blocking conditions for any distinct descendant:** it must change the
specific tail mechanism (for example, an exactly normalized bounded/raw
zonal construction with a separately proved mean law), predeclare that change
before generated outcomes, recompute its exact fourth moment and cross-axis
covariance, and pass a complete-cost independent-frame gate.  Renaming the
square, clipping it after inspecting outcomes, swapping in Poisson/Helmholtz,
or tuning the band endpoints is not a valid reimplementation of M108-C.
