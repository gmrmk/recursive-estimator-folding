# N5 disposition: the vision's multilevel v-lever has near-null first-order headroom

The reverse-oracle vision (VISION_MULTILEVEL_CONTROL_20260807) predicted that
correcting EVERY layer's sampling residual (multilevel control) beats the
champion's LAYER-1-only control, hypothesizing a ~4x v-cut. N5 tested the
premise at first order and it did NOT hold.

## Result

| quantity | value |
|---|---|
| R2 captured by layer-1 residual alone (champion mechanism) | 0.235 |
| R2 captured by layers 1-2 | 0.248 |
| R2 captured by ALL layers (multilevel upper bound) | 0.287 |
| residual variance ratio (multilevel / layer-1) | 0.932 |
| implied v-cut beyond layer-1 | **1.07x** |

Predeclared "win" threshold was residual ratio <= 0.25 (4x cut). Observed 0.93.
**The vision's multilevel v-lever is NOT supported at first order.**

## What it means (honest)

1. **The multilevel increments are ~exhausted by layer-1.** Adding the analytic
   propagation of layers 2..L beyond layer 1 raises capture only 0.235 -> 0.287.
   The champion's single first-layer control already captures nearly all of the
   linearly-capturable variance. The vision's central claim (per-layer beats
   terminal/first-layer) has weak first-order support.

2. **71% of the final-error variance is higher-order** (R2_all = 0.29 means 71%
   is not linear in any layer's residual). That residual is the non-Gaussian
   k3/k4 content the corpus has repeatedly shown is theorem-obstructed (M137)
   and empirically dead (terminal k3 0.493%). The v-lever's remaining headroom
   sits behind that same wall.

3. **This REVALIDATES ultrathink-2:** v is effectively pinned; #1 is the
   engineering (S / native-kernel) lever, not the variance lever. The elegant
   vision was tested cheaply and did not survive — the fold discipline working
   as intended (chase the idea, kill it on evidence, before building the full
   chain expecting a payoff that is not there).

## Caveats (what would still need M172 to be definitive)

N5 is a FIRST-ORDER (mean-tangent), DIAGONAL-closure probe on a SMALL net
(width 24, depth 8). It does NOT include the M179 full-covariance / Owen-T
bivariate increments (the covariance tangent, the exact K/Hmu/Hv). A definitive
kill is the M172 source-variance gate on the full-covariance control. BUT: N5
caps the LINEAR multilevel headroom at ~7%, and the unexplained 71% is
higher-order, so the full-covariance control would have to capture the
higher-order residual to matter — which is the corpus-killed content. The prior
that M172 shows a large cut is now LOW.

## Disposition and preserved tissue

- Vision multilevel v-lever: FIRST-ORDER NULL (1.07x); prior on the M172
  full-cov payoff lowered from "the elegant #1 path" to "unlikely, test at M172
  only as part of the Algorithmic-Contribution artifact."
- M179 G4/G5 still worth completing: the certified provider is a NOVEL
  Algorithmic-Contribution regardless of the v-cut, and M172 is its definitive
  (full-cov) test.
- Campaign #1 path returns to the S-lever (native kernel), organizer-Q2-gated.
- Fold rule honored: a hypothesis was predeclared, tested by its cheapest
  falsifier, and killed on evidence; no in-mutation retune. A richer control
  (full covariance) is a distinct future test (the M172 gate), not a retry.

Response-free; generated net; champion unchanged.
