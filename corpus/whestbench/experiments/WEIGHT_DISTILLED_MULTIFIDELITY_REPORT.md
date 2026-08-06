# Weight-distilled multifidelity cleanroom report

## Verdict

**Kill the frozen degree-6/8 Gegenbauer student. Preserve the exact-mean,
independent-pilot control machinery and the clean `R^16` 5-design harness.**

The failure is large enough to resolve the premise: the primary spectral
student multiplies the design-surviving variance by `91.141x`, and its
cost-adjusted ratio is `174.995x`. It wins on `0/16` fresh teachers. No
competition data, truth, scorer, API, feature search, or best seed was used.

## Matched factorial

The variance column is across 32 Haar rotations of an exact antipodal
5-design. Consequently, it measures the angular degree-`>=6` remainder that
the design does not integrate exactly.

| Student | Degree >=6 variance / none | Cost / none | Cost-adjusted | Raw wins | Median pointwise residual variance |
|---|---:|---:|---:|---:|---:|
| none | 1.000 | 1.000 | 1.000 | -- | 1.000 |
| layer-1 ReLU, pilot fit | 1.145 | 1.730 | 1.981 | 2/16 | **0.656** |
| deep-path ReLU, fixed coefficients | 20.497 | 1.305 | 26.755 | 0/16 | 74.882 |
| deep-path ReLU, pilot fit | 1.782 | 1.850 | 3.297 | 0/16 | 0.933 |
| degree-6/8 Gegenbauer, pilot fit | **91.141** | **1.920** | **174.995** | **0/16** | 1.971 |

The cleanest scientific result is the layer-1 contrast: it removes about
34.4% of ordinary pointwise variance yet makes the 5-design residual 14.5%
worse. This directly reproduces and sharpens the earlier layer-1 exact-mean CV
failure. Pointwise surrogate quality is not the target; the design already
annihilates the low-degree content responsible for that apparent gain.

## Failure localization

### 1. Layer-1 null is subsumed

The layer-1 pilot fit has a median in-pilot centered residual ratio of `0.558`
and a held-out pointwise ratio of `0.656`, but its mean correlation with the
teacher's randomized-design error is only `0.143`. It captures common
low-degree variation, not the post-design mode.

### 2. Ungated deep paths are not a fixed student

The weight-only coefficient rule replaces downstream ReLU gates by factors of
one half. It is badly calibrated instance by instance: median pointwise
residual variance is `74.9x`, and degree-`>=6` variance is `20.5x`. Preserve
the equivariant direction generator, not these fixed coefficients.

### 3. The frozen spectral fit has a scale/observability failure

Normalized zonal harmonics in 16 dimensions are small on generic directions:

```text
median feature RMS range       0.00399 .. 0.01690
median coefficient Frobenius norm    420.2
median pilot residual variance ratio   1.051
teacher pilot constant-energy fraction 0.683
```

The ridge systems themselves are not ill-conditioned (median condition
`137.6`, maximum `460.9`). The problem is semantic: eight localized degree-6/8
zonal features, selected by ungated path salience, barely observe the teacher's
relevant high-degree field. A finite pilot dominated by the constant mode then
assigns large output coefficients. The resulting control-error correlation is
slightly negative (`-0.0367`), so subtraction amplifies rather than cancels the
randomized-design error.

This localizes the next admissible question sharply. A successor would need to
freeze pilot centering/an exact-mean intercept and a genuinely gate/Jacobian
response-informed direction bank before metrics. Merely adding features,
tuning degrees, or selecting directions from design errors is forbidden.

## Contract and validation

- 16 fresh width-16, depth-8 bias-free He ReLU teachers.
- Independent 128-point Gaussian pilot; no pilot reuse in the residual set.
- 32 fixed-seed Haar rotations per teacher of 9 real MUB bases plus
  antipodes: 288 points/rotation.
- Exact design defects: degree 2 `0`, probed degree 4 `5.20e-18`, degree 5
  `0`.
- Fixed ranks/degrees: ReLU rank 8; four directions x degrees `{6,8}`.
- Input-rotation, hidden/output permutation, antipodal, and deterministic
  checks: maximum error `6.55e-15`.
- Six construction, moment, mean-identity, parity, and symmetry tests pass.
- All teacher, pilot, direction-product, feature, fit, readout, and exact-mean
  costs are charged. The primary total is `1.920x` the no-student estimator.
- No nonfinite or solve failure.

## What is preserved

The reusable pieces are:

1. a compact generic construction of the complete real-MUB 5-design in
   `R^16`;
2. conditional-unbiased multifidelity estimation with a pilot-independent
   residual design;
3. exact Gaussian means for shallow homogeneous ReLU students;
4. exact zero means for homogeneous spherical Gegenbauer controls;
5. equivariant weight-derived direction banks and symmetry tests;
6. a matched total-cost variance ledger that prevents pointwise-fit mirages.

SB-FNN contributed the spectral-student hypothesis only. No FFT was applied to
neuron indices, and no claim from its ordered systems-biology setting was
treated as evidence that Fourier controls must help a deep random ReLU field.

Machine-readable outcomes are in [`premise_results.json`](premise_results.json)
and [`decision.json`](decision.json); the frozen contract is
[`PREDECLARED_GATE.md`](PREDECLARED_GATE.md).
