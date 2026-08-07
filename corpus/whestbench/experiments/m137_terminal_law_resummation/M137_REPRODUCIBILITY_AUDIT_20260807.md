# M137 reproducibility audit — 2026-08-07

## Verdict

The mathematical four-moment non-identification result survives, and none of
the tested terminal closures is promoted.  The original handoff's claim that
all seven tests passed is not reproducible in the configured bundled runtime.
The defect was isolated to dependency ordering, repaired without changing the
frozen numerical result, and independently checked.

## Reproduction

The bundled Python contains NumPy 2.3.5 but no SciPy.  Before repair, six of
seven tests passed.  The failure was
`test_symmetric_two_gaussian_matches_negative_kurtosis`: the implementation
returned the Gaussian fallback as soon as `least_squares` was unavailable,
before reaching a closed-form symmetric-mixture branch that does not require
an optimizer.

For `p=1/2` and separation-variance fraction `r=1/2`, the component variance is
`1-r=1/2`, the centers are `+-sqrt(1/2)`, and the mixture has
`E[Z^2]=1`, `E[Z^4]=2.5`, excess kurtosis `-0.5`, and
`E[ReLU(Z)]=0.41246632482357504`.  The test and formula are correct.

## Repair

The zero-cumulant and symmetric negative-kurtosis analytic branches now run
before the optional-SciPy guard.  The guard remains in force for the generic
asymmetric nonlinear solve.  The configured bundled runtime then passed all
seven tests.

- Original source SHA-256: `f20e28d3b6aecb66bed977293fdf186cece8c6fbc20e27c8bc122824789b24f9`
- Repaired source SHA-256: `2b0b9e83a1a59fc85c91bc0fd582bf19fcfa126c8a540ea933d9f5045a4452cc`
- Frozen result SHA-256: `608d056b1d2a16f8e9a4feaf17ca4367923531541ef122500bf02c63e7923486`

The frozen JSON was not overwritten.  It reports generic MaxEnt/mixture fits
that imply an unrecorded SciPy-capable environment.  Those numerical values
remain **unverified in the captured runtime** and must not be used as a
promotion claim.  This qualification does not weaken the counterexample that
four moments fail to identify a ReLU expectation, nor does it turn any tested
closure into a survivor.

