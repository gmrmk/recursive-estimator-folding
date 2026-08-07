# M109 adversarial theory: bounded ReLU nodal-tube occupancy

**Date:** 2026-08-07  
**Scope:** theory only. No MLP forward, score, contest artifact, champion, or ledger was changed.  
**Disposition:** **PASS_TO_DRAFT, conditional on the strict fresh generated-only gate in section 10.** This is not a claimed win or authorization to edit an estimator.

## 1. Classical operator

After exact radialization the integration law is U ~ Unif(S^255). A nonzero first-layer column w_j has the actual ReLU nodal great sphere

    {u : a_j . u = 0},    a_j = w_j / ||w_j||_2.

The defensible "cymatic" translation is therefore a tube around a real network gate surface, not an asserted resonance. Freeze d=256 and

    c = 1/sqrt(d) = 1/16,
    h_a(u) = 1{|a.u| <= c} - p.

The width is not tuned. Since sqrt(d) a.U tends to N(0,1), it is exactly the one-directional-standard-deviation neighborhood of the kink. In preactivation units the event is

    |w_j.u| <= ||w_j||_2/sqrt(d).

The candidate is a bounded nodal occupancy atom. Its values lie in [-p,1-p], before any aggregation.

## 2. Exact mean and certified constant

For unit a, T=a.U satisfies T^2 ~ Beta(1/2,255/2). Hence

    p = Pr(|T| <= 1/16)
      = I_(1/256)(1/2,255/2)
      = 0.6817415182413444070272442752426179343812814534091667630...

and E[h_a(U)]=0 exactly. The complementary cap probability is

    1-p = 0.3182584817586555929727557247573820656187185465908332370...

A dependency-free high-precision certificate is available. Put theta=asin(1/16) and

    J_0(theta)=theta,
    J_n(theta) =
      (sin(theta) cos(theta)^(2n-1) + (2n-1) J_(n-1)(theta))/(2n).

Then

    p = 2 J_127(theta) / [pi binom(254,127)/4^127].

Using theta=atan(1/sqrt(255)) and the alternating arctangent series gives the displayed value at 90 decimal digits. An independent regularized-beta continued fraction agrees to binary64 roundoff. A runtime draft should hard-code the nearest binary64 literal 0.6817415182413444 rather than call a special function.

    Var(h_a) = p(1-p)
             = 0.21697002054733107815387039331786144...
    sd(h_a)  = 0.4658004084877246...

### Mean-error condition

If p_hat=p+delta is implemented, every convex axis mixture has conditional mean -delta. An adjusted output Y_k-H beta_k therefore has bias beta_k delta. The exact requirement is

    |delta| <= eta * se(Y_k) / max(1,|beta_k|),

where eta is a predeclared bias allocation. The binary64 certificate is below 1e-15; a static gate p_runtime within 1e-12 of the certified constant is over nine orders below the 126-frame control scale in section 6. Fit coefficients without an intercept and apply Y-H beta. Centering a held feature by its own sample mean would break the exact mean law.

## 3. Mixtures, symmetry, and a required gauge repair

Let the nonzero first-layer axes be a_j. The primary uniform feature is

    H_0(u;W) = sum_j omega_(j,0) h_(a_j)(u),
    omega_(j,0)=1/m.

A secondary frozen path feature is permitted only after repairing a gauge defect. The naive squared backward sensitivity is

    s^(L)=1,
    s^(ell-1)=(W_ell^2)s^ell.

But the positive ReLU gauge

    W_1[:,j] -> gamma_j W_1[:,j],
    W_2[j,:] -> W_2[j,:]/gamma_j,  gamma_j>0

leaves the represented network and a_j unchanged while s^1_j scales as gamma_j^(-2). Raw s^1 is therefore not a functional invariant and is forbidden as a primary weight.

The only admissible path weight is the repaired energy

    e_j = ||W_1[:,j]||_2^2 s^1_j,
    omega_(j,1)=e_j/sum_r e_r,
    H_1(u;W)=sum_j omega_(j,1)h_(a_j)(u).

Uniform is the primary atom; repaired path is a predeclared second column, not an after-outcome replacement. Both have nonnegative weights summing to one, hence remain in [-p,1-p].

Conditional on fixed weights, both columns have exact spherical mean zero. They are antipodally even, invariant to axis sign, invariant under positive hidden-unit gauge, covariant under a common input orthogonal rotation, and invariant under a hidden permutation. Starting the backward sensitivity from terminal ones makes the scalar path law output-permutation invariant. Zero columns, nonfinite values, negative weights, or a non-unit weight sum are hard failures.

## 4. Harmonic content and what frames erase

With P_l the normalized Gegenbauer zonal,

    h_a(u) = sum_(even l>=2) alpha_l P_l(a.u),
    alpha_l = dim(H_l) E[h_a(U)P_l(a.U)].

The jump at |a.u|=1/16 gives infinitely many nonzero even degrees. Thus M109 is neither a quadratic control nor a finite heat band. It is an angular high-even operator, exactly where antipodal/frame designs leave possible residual content.

It also contains substantial degree two. Exact incomplete-beta algebra yields

    E[h_a P_2(a.U)] = -0.001894094482019165...
    dim(H_2) E[h_a P_2]^2 = 0.1180139015646942...

which is 54.3918% of Var(h_a). A complete orthonormal frame annihilates this degree-two piece exactly. M109 must therefore earn its keep through degrees 4,6,8,... only; it cannot claim its full single-direction variance inside L1.

## 5. The main adversarial conflict: prior first-layer CVs

The old first-layer exact-mean ReLU control was ineffective on frames+antipodes. M109 is not independent evidence against that result. Exact beta integrals give

    E|T|                         = 0.049916507721605406...
    E[|T| 1{|T|<=1/16}]          = 0.019610996009298790...
    Cov(h_a,|T|)                 = -0.014419159750134074...
    Corr(h_a,|T|)                = -0.8230466471903382...

The correlation against the even antithetic ReLU component is the same up to its factor one half. A M109 pass would therefore mean specifically that hard nodal occupancy retains useful higher-even information after the smoother absolute-value control and the frame’s degree-two annihilation have failed. It may not be reported as a generic first-layer-CV revival.

There is an exact residual h_a-gamma(|T|-E|T|), gamma=-10.1931561409..., but it reaches about 9 near |T|=1. It is a new less-bounded operator and is explicitly excluded from M109; it is only a preserved future hypothesis.

## 6. Exact Haar-frame block law

For one fixed axis and a Haar orthonormal frame (q_1,...,q_d),

    ((a.q_1)^2,...,(a.q_d)^2) ~ Dirichlet(1/2,...,1/2).

Let K=sum_i 1{(a.q_i)^2<=1/d}; the frame statistic is K/d-p. Its joint inclusion probabilities are

    q_r = Gamma(d/2) 2^r/[Gamma(1/2)^r Gamma((d-r)/2)]
          integral_[0,1/sqrt(d)]^r
          (1-sum z_i^2)^((d-r)/2-1) dz_1...dz_r.

Tensor Gauss-Legendre integration at 24,32,40,48,64 nodes is stable to the displayed digits:

    q1 = 0.6817415182413444
    q2 = 0.4643104813137846
    q3 = 0.3159102677990908
    q4 = 0.2147251884390728.

Using E[(K)_r]=(d)_r q_r gives:

| quantity | value |
|---|---:|
| E K | 174.5258286697830 |
| Var K | 25.4491759592020 |
| Var(K/d-p) | 0.000388323607775909 |
| sd(K/d-p) | 0.0197059282393880 |
| standardized fourth moment | 2.99536246 |
| pairwise indicator correlation | -0.0021247930 |

The fictitious iid-direction variance would be 0.000847538..., so the real Haar frame is about 2.18 times better. This is a benign nearly-Gaussian block law, sharply unlike M108’s needle-tail. Because h is even, appending antipodes duplicates the block value and supplies no extra control sample. At 126 independent Haar frames its single-axis block-mean sd is 0.01970593/sqrt(126)=0.001756.

For H_0/H_1 the bounded range survives exactly. Their precise frame moments depend on the fixed W1 Gram matrix and must be measured on fresh Haar frames; they cannot be assumed from the single-axis calculation. Require no nonfinite block and kurtosis at most 10 before any MLP is run.

## 7. Geometry-only comparison to the harmonic alternatives

| operator | exact mean | bounded before aggregate | non-arbitrary ReLU/gate reason | tail disposition |
|---|---|---|---|---|
| M108 scaled heat/Helmholtz band | yes | no | degree-18 premise only | closed: frame kurtosis about 3.12e18 |
| M108 B^2-1 energy | yes | no | Chladni intensity analogy | closed: E[B^4] about 2.05e23 |
| clipped/phase heat band | can recenter | yes | no: cap/phase is a new arbitrary rule | separate mutation |
| M109 nodal occupancy | beta CDF | yes, [-p,1-p] | one-sigma tube of an actual gate surface | single-axis frame kurtosis 2.9954 |

A sign(B) or fixed clipping can be made bounded and exact-zero by separately computing its spherical mean. Therefore M109 is not unique among all conceivable bounded transforms. It is uniquely defensible among the current physics translations because its threshold follows from d and the actual ReLU nodal geometry, not an arbitrary degree band, cap, phase, or temperature. This is an admissibility result, not evidence of final-error correlation.

## 8. Accounting boundary

Formal L1 already computes

    first_pre=(rho_256 Q)@W1,
    t_sj=first_pre_sj/(rho_256 ||W1[:,j]||_2).

M109 reuses t_sj and adds no dense Q@W1 matmul. That is an exact data reuse identity, not free accounting. For S positive representatives and m=256 axes it still charges S*m normalizations, S*m abs/comparisons, a uniform reduction, a path-weighted multiply/reduction, buffer/copy costs, and setup norms. The optional repaired path requires 31 dense squared-weight matvecs, about 4.05e6 scalar multiply/add operations at n=256,L=32.

At L1's S=32,256 this is 8.26 million cells and O(Sm) scalar work, versus about 1.24 billion recurrence operations for M108. It must stream by the existing first-pre block, retain no all-frame-by-axis float64 matrix solely for M109, and receive a full FlopScope/residual/memory trace before any deployment claim.

## 9. Target-free hard gate

Before a generated network:

1. Recompute p via the trigonometric recurrence and independently via regularized beta; each must agree with the frozen literal within 1e-12.
2. Verify exact zero mean, antipodal equality, axis-sign, input-rotation, hidden-permutation, and repaired positive-gauge invariance on deterministic synthetic matrices. Confirm that raw s^1 fails the gauge test, proving test power.
3. Reproduce q1..q4 and the single-axis Haar-frame variance within 2% and kurtosis within 0.1 on a predeclared Haar simulation.
4. On fresh Gaussian W1 and fresh Haar frames only, require both H_0 and H_1 finite, in [-p,1-p], frame kurtosis <=10, and no forbidden full S*m retention.
5. Produce a charge table covering every scalar operation, copy, allocation, and setup recurrence.

## 10. Strict fresh generated-only premise gate

Only after section 9 passes may a new immutable M109 packet be frozen. It uses four fresh generated n=256,L=32 He/ReLU networks unseen by M107/M108/champions, with 32 independent Haar frames per network: 16 coefficient frames and 16 independent held frames. The frame is the unit; neither individual directions nor antipodal duplicates are units.

The frozen two-column bundle is [H_0,H_1]. Ridge strength, standardization, and a no-intercept adjustment are fixed before data generation. No selection between uniform and path after results is permitted. Fit 256 output coefficients on the 16 coefficient frames only; measure raw/adjusted block estimates on held frames only. Report frame outputs/controls, Gram condition, coefficient norms, per-network trace variance ratios, maximal standardized adjusted block, numerical-bias bound, and full measured cost. L1 is eligible because its Haar frames are independent; M71’s shared-rotation MUB bases are not cross-fit folds.

For this deliberately expensive 16/16 oracle,

    VR_i = tr Cov_held(adjusted)_i / tr Cov_held(base)_i,
    charged_efficiency_i =
       2 VR_i (1+measured_control_overhead/base_cost).

The factor two charges discarded coefficient frames. Kill this specified implementation, without retuning c/path/ridge, if any law, finite, resource, or tail check fails; if any VR_i >=1; or if the four-network geometric mean charged efficiency is not below 0.90. It is a screened survivor only if all four VR_i<0.45, geometric mean charged efficiency<0.90, no material bias, and an independent recomputation agrees.

A survivor authorizes one next question only: integrate the frozen operator into L1 at equal measured cost. It does not authorize combining with M107/M108, retuning c, clipping, changing path weights, or claiming a competition win.

## 11. Salvage map

* Always preserved: radial/nodal translation, exact beta mean, boundedness, Haar-Dirichlet tail audit, and the positive-gauge repair.
* Static tail failure localizes to the mixture/implementation; the scalar atom remains mathematically exact.
* Held covariance failure kills this first-layer nodal-occupancy implementation, not all geometry.
* Information gain without charged gain preserves a diagnostic but prohibits packaging. A future child must change coefficient acquisition, not silently alter the tube width.

The phrase "underlying harmonic" now has a falsifiable meaning: a bounded, exact-zero, antipodally even occupancy statistic around the network's actual ReLU nodal hyperplanes.
