# M149 disposition: KILL implementation, preserve endpoint provider and fallback contract

## Frozen mechanism tested

M149 held M147's endpoint-safe bivariate primitive fixed and substituted a
fixed, nested QUADPACK Patterson `43/87` outer rule after the tangent
compactification of the conditioning normal.  It made exactly 87 local pair
calls, reusing all 43 coarse nodes, had no recursive splitting, and failed
closed on either the numerical or 8,000-angular-evaluation cap.

## Falsification

Against M147's independently higher-order conditional `48/64` reference,
the exploratory (intentionally *unaccepted*) 87-node result on the moderate
PSD state has absolute cumulant defect about `6.48e-6` and tangent defect
about `1.54e-3`.  The observed `43/87` pair-order disagreements are also far
above the frozen `2e-8`/`2e-7` certificates.  At the conditional-correlation
`.999` adversary the fixed route reaches its resource/accuracy guard.

Consequently, the normal API rejects all such cases and no response or
coefficient is emitted.  The tests deliberately assert this rejection; they
do not relax the tolerance to obtain a passing artifact.

## Salvage

1. The local width-independent `3x3` gather and M147 endpoint/PSD primitive
   remain reusable.
2. The explicit zero-Schur contract is complete: four independent blocks
   estimate the raw fourth moment and the three covariance products, keeping
   each product unbiased; it requires an independently certified PSD-root
   tangent and accounts for every draw.  It is not silently invoked here.
3. The cost worksheet shows a 47,296-op favorable lower-bound for this *failed*
   fixed quadrature path, so compute was not the immediate barrier.  The
   binding mechanism is non-smooth tangent accuracy under the compactification.

## Next distinct mutation

Do not raise the quadrature order or loosen certificates.  A successor must
change the binding mechanism: derive the piecewise moving-kink/tangent
integral analytically, or implement the requested Rosenbaum/Owen-T primitive
with a separately certified nonadaptive endpoint partition.  It must be a new
candidate, not a retuned M149.

No generated response cells, truths, scorer calls, public data, submissions,
or champion artifacts were read or modified.
