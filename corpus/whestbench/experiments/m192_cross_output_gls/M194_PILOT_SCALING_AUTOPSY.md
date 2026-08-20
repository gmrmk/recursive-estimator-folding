# M194 frozen autopsy -- pilot-size scaling

Written after the predeclared eight-frame M194 gate failed and before any
alternative pilot prefix was evaluated.

This is a diagnostic autopsy, not a candidate search and not promotion
evidence.  Reuse the exact M194 rotation pairs, folds, projected-block formula,
`lambda=1/3`, truths, and scoring.  Evaluate the frozen dyadic pilot-prefix
grid

    k in {1, 2, 4, 8, 16, 32, 64, 126}.

For each k, the pilot is the mean of the first k complete frames of rotation
`r+8`; the main estimator remains all 126 frames of rotation r.  Report raw
ratio and the conservative cost-adjusted ratio

    ratio_cost(k) = ratio_raw(k) * (126 + k) / 126.

Fit no coefficients and select no k.  The only inferential questions are:

1. Does excess error above the truth-anchor block oracle scale approximately
   as `1/k`, as predicted for independent pilot noise?
2. Does any point on the frozen grid cross raw parity and cost-adjusted parity?
3. Extrapolating only if the dyadic curve is monotone and approximately linear
   in `1/k`, how many pilot frames would be required for the original M194
   15-percent cost-adjusted screen gate?

Any apparent best k is contaminated by reuse of the same three networks and
cannot be promoted.  A viable scaling result may only predeclare a fresh-unit
child.  A non-monotone curve, a required pilot beyond the budget, or failure
to cross cost-adjusted parity kills independent-pilot block GLS at this
information size while preserving the M192 oracle premise.
