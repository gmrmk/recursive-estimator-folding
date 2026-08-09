# M192--M197 notes -- large oracle, localized identifiability failure

Date: 2026-08-08.  Scope: cached synthetic G0 only.  Nothing in this folder is
a submission candidate or evidence from the private evaluator.

## Executive result

M192 found a real and unexpectedly large oracle ceiling: learning sum-one
weights over the 126 frame estimates from other final-output neurons reduced
the three-network panel MSE by 87.38 percent.  A separate agent's unarchived
independent recomputation agreed on every network-level ratio.  Three
truth-free descendants then
localized the missing information:

| arm | changed link | panel ratio vs matched 126-frame mean | disposition |
|---|---|---:|---|
| M192 | truth-trained cross-output error covariance | 0.126193 | oracle screen survivor |
| M193 | diagonal-Gaussian analytic anchor | 1057.899 | killed |
| M194 | independent 8-frame Haar pilot + projected blocks | 15.8306 raw; 16.8357 cost-adjusted | killed |
| M195 | two independent 63-frame halves, mutually piloted, equal total cost | 1.15748 | killed |

The result is not “GLS failed.”  The truth-trained projected-block diagnostic
inside M194 still gives panel ratio 0.112710.  The failed link is estimating a
small common/contrast cross-covariance from only about 224 training output
channels without already possessing an estimator as accurate as the answer.

## M192 oracle premise

Per-network ratios were 0.146840, 0.095677, and 0.143037 for seeds
101/202/303.  All 48 cached rotation trials improved.  All 384 outer-fold fits
selected the predeclared shrinkage `alpha=0.25`; median weight L1 was exactly
1 and median maximum absolute weight was about 0.0155.  The archived P2
uniform baseline reproduced exactly.

This does not contradict the fixed-zonal-kernel reweighting certificate.  That
certificate fixes weights independently of the realized output matrix.  M192
uses other exchangeable final rows of the realized network to learn a
nonstationary frame covariance and assesses only held rows.  It also does not
contradict the distribution-free centroid/body no-go, because M192 is an
ensemble-risk oracle over He networks, not a guarantee for arbitrary targets.

The cached truth noise floors are roughly 1.2e-8--2.2e-8, versus baseline MSEs
roughly 2.0e-7--5.9e-7.  They cannot numerically explain an 87-percent gain,
but the three-network panel remains a premise screen and neurons are not
independent network-level validation units.

## Exact M193 first break

Write one output's frame vector as

    x_j = mu_j 1 + e_j,
    delta_j = mu_j - a_j,
    P = I - 1 1^T / 126.

The analytic-anchor residual has second moment

    C_a = C_e + q 1^T + 1 q^T + s 1 1^T,
    q = E_j[delta_j e_j].

The final rank-one term is harmless under a sum-one constraint.  The two cross
terms are harmless only when `P q = 0`.  M193 showed the opposite: diagonal
anchor MSE was 6.09e-4--1.88e-3, many orders above frame error, median weight
L1 rose to 5.76, and rotation-mean bias dominated the result.  With trace
shrinkage, even a pure rank-one addition can alter the ridge scale; this is why
later arms regularize only the projected contrast block.

## Exact M194 identity and finite-output failure

For an independent pilot `y_j=mu_j+eta_j`, form

    z_j = P x_j,
    ctilde_j = (1/126) 1^T x_j - y_j.

Then the projected covariance `A=E[z z^T]` is pilot-invariant exactly and the
needed cross block `b=E[z ctilde]` is unbiased because
`E[z eta]=0`.  For `v` in the contrast subspace,

    J(v) = constant + 2 b^T v + v^T (A + gamma P) v,
    v* = -(A + gamma P)^+ b,
    gamma = tau_z / 3.

The runner has no factor-of-two error.  Its truth-anchor block ratios were
0.124538, 0.082539, and 0.139294, close to M192.  The eight-frame pilot arm,
however, produced ratios 20.3235, 9.67330, and 20.1799.  Median candidate
weight L1 was 1.584 versus about 1.0006 for the truth-block diagnostic.  Across
cached fits, the pilot-noise cross norm was about five times the true cross
signal at the median.  This is an SNR failure, not algebraic or numerical
conditioning failure.

The frozen pilot-prefix autopsy was monotone:

| pilot frames k | raw panel ratio | conservative cost-adjusted ratio |
|---:|---:|---:|
| 1 | 97.6003 | 98.3749 |
| 2 | 47.8062 | 48.5650 |
| 4 | 37.7690 | 38.9680 |
| 8 | 15.8306 | 16.8357 |
| 16 | 8.04104 | 9.06212 |
| 32 | 3.61468 | 4.53270 |
| 64 | 1.52520 | 2.29991 |
| 126 | 0.671408 | 1.34282 |

A full second estimator finally crosses raw parity but remains 34.3 percent
worse after charging its evaluations.  Thus “buy a more accurate independent
anchor” is cost-dilutive on the measured range.

## M195 equal-budget salvage

M195 let two independent 63-frame half-designs serve simultaneously as pilot
and estimator.  The uncorrected two-half uniform ratios versus the full
126-frame Kerdock comparator were 1.29790, 0.865509, and 1.23066.  This exposes
the price of breaking the full design's degree-4 structure.  Attenuation moved
those ratios to 1.34781, 0.886838, and 1.29738, so the covariance correction
added noise rather than recovering the design loss.  Panel ratio was 1.15748,
bootstrap 95-percent interval [0.88427, 1.54798].

## M197 final crossed-U-statistic salvage

M197 tested the only remaining distinct fixed-budget pilot topology: three
independent rotations by 42 frames, with every correction using the other two
group means as crossed pilots. Unknown truth cancels algebraically, and all
360 fits passed the arbitrary-mean and combined sum-one checks. It still gave
per-network ratios 1.917651, 1.008849, and 1.325648; panel ratio 1.368804 with
bootstrap [1.072507, 1.824979]. The uncorrected three-group mean was already
worse on two networks, and correction worsened all three. This closes the
tested equal-budget crossed-pilot topology at the same split-design/SNR break.

## Disposition and recursion lesson

- Preserve M192 as a high-headroom oracle observable, not a deployable win.
- Kill the specific M193 analytic-anchor, M194 independent-pilot, M195
  symmetric-half, and M197 three-way crossed mechanisms at their measured
  links.
- Do not retune anchor scales, pilot prefixes, half sizes, signs, or ridge
  values on this burned three-network cache.
- Reopening requires genuinely new information about the common frame error,
  not another noisy estimate of the same mean.  Examples would be an exact
  weight-derived conditional expectation or a late-layer observable whose
  cross block is estimable without a second full quadrature.
- The production v3 path does not currently retain a 126-by-256 frame matrix.
  Any future child must prove exact per-frame attribution through pruning,
  dead/kink/on reconstruction, and terminal folding before its cheap matrix
  postprocessing claim is accepted.

Evidence files are the four predeclarations, four runners, three primary JSON
results, and the frozen pilot-scaling JSON in this directory.
