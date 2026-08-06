# Reporting-only H1 graph diagnostics

These diagnostics were registered after the primary pipeline was frozen.
They do not alter its features, hypergrid, predictions, or R2>0.965 gate.

## Correction direction

- pooled correction cosine: `0.814274`
- pooled sign agreement: `0.689492`
- above per-network median |residual| cosine: `0.835305`
- above per-network median |residual| sign agreement: `0.828828`
- per-network cosine quantiles: `[0.348121753165285, 0.7592684252438024, 0.8379445542487785, 0.8925615718831927, 0.9705269536846751]`
- per-network sign-agreement quantiles: `[0.4453125, 0.5576171875, 0.708984375, 0.8203125, 0.90625]`

## Fixed feature groups

| Group | Features | OOF residual R2 | Fold minimum |
|---|---:|---:|---:|
| diagnostic_anchor_scale_only | 2 | 0.648801 | 0.586155 |
| diagnostic_signed_absolute_cancellation | 5 | 0.649081 | 0.587847 |
| diagnostic_hermite_defects | 34 | 0.662620 | 0.624309 |
| diagnostic_dyadic_depth_all_sources | 38 | 0.667521 | 0.622779 |
| diagnostic_gauge_edge_concentration | 16 | 0.662978 | 0.607905 |

## Network scale comparison

- shared grouped-CV scale baseline R2: `0.648801`
- per-network target-oracle pure scale R2: `0.724652`
- per-network target-oracle two-parameter affine R2: `0.725299`

The per-network values are optimistic diagnostics, not deployable models.

## Strata

Above each network's median |residual|, graph R2 is `0.697265`.
Residual-norm quartiles and final-alpha bins are fully recorded in
`diagnostics.json`.
