# M197 G0 notes -- crossed three-rotation U-statistic

## Disposition

**KILLED implementation.**  M197 uses exactly 126 complete frames, but its
three-rotation crossed estimator worsens the matched full-126 Kerdock baseline
on all three frozen synthetic networks.

| Network | M197 / matched full-126 | Uncorrected 3x42 / matched full-126 |
| --- | ---: | ---: |
| 101 | 1.917651 | 1.783449 |
| 202 | 1.008849 | 0.976651 |
| 303 | 1.325648 | 1.242740 |
| Geometric panel | **1.368804** | diagnostic only |

The five-triple cluster bootstrap interval for the candidate ratio is
`[1.072507, 1.824979]`.  It misses both the predeclared 10-percent reduction
floor and the all-network non-worsening requirement.

## Checks and localization

All 360 group fits completed with zero numerical fallbacks.  The largest
unknown-mean cancellation discrepancy was `9.93e-19`; the largest combined
sum-one discrepancy was `2.22e-16`.  Thus the crossed U-statistic and its
unknown-target cancellation are implemented as predeclared.

The uncorrected equal three-group average is already worse on networks 101 and
303.  M197's additional correction worsens it further on every network.  The
failed link is therefore the fixed-budget split into 42-frame independent
rotations, compounded by noisy crossed covariance estimation; it is not a
hidden target leakage, a failed sum-one constraint, or a numerical fallback.

## Salvage

Preserve the exact cancellation identity

`Z_r [q_r - (q_s + q_t)/2]`,

and the fact that it gives a target-free covariance U-statistic under
independent Haar rotations.  At this fixed 126-frame budget, however, the
loss of the full Kerdock union's geometry dominates any benefit from two
independent pilot rotations.  Do not retune rotation count, the 42-frame
prefix, lambda, or triple partition on this cache.  Reopen only if a new
observable preserves the full 126-frame geometry while identifying the
common/contrast block.

`m197_g0_results.json` is the machine-readable result artifact.
