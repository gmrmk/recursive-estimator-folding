# Equivariant residual graph: grouped-CV premise

## Decision: **KILL**

The graph removed 66.27% of anchor residual variance out of network, below the predeclared 96.5% gate or another mandatory stability/symmetry condition failed.  Kill this feature family without opening a broader slice.

No official scorer, API, external model, or holdout was used.  The
experiment used public development MLPs 0..99 only.  Truth entered only
as a grouped train/evaluation label; every feature is weight-derived.

## Results

| Family | Features | OOF MSE | Residual R2 | Fold min..max | Wins |
|---|---:|---:|---:|---:|---:|
| intercept | 1 | 4.784386188e-05 | 0.289586 | 0.2693..0.3272 | 97/100 |
| scale | 2 | 2.365201882e-05 | 0.648801 | 0.5862..0.7262 | 96/100 |
| local | 16 | 2.301150380e-05 | 0.658312 | 0.6115..0.7251 | 97/100 |
| graph | 70 | 2.271787125e-05 | 0.662672 | 0.6298..0.7269 | 95/100 |

The full-covariance anchor MSE was `6.734645095e-05`.  The
graph's network-bootstrap R2 interval was `[0.6228899532744937, 0.6970783455579369]`;
its worst per-network MSE ratio was `1.761`.
The predeclared promotion threshold was R2 > 0.965, every outer fold
positive, bootstrap lower bound > 0.94, and worst ratio <= 2.

## Model

The anchor is the validated full-covariance Gaussian reclosure.  The
readout is nested-CV ridge on dimensionless, output-equivariant features:
final Gaussian law shape; correlation-row moments; incoming edge IPR and
signed/absolute cancellation; Hermite-shaped defect sources transported
through gauge-fixed response edges; and six dyadic depth bands.  Output
corrections are multiplied by the final preactivation scale.

## Leakage and symmetry checks

- Outer and inner folds group complete MLPs; outputs are never split.
- No index, filename, hash, seed, or target-derived inference feature exists.
- Feature standardization and ridge penalties are fit inside training folds.
- Input rotation, hidden permutation, positive gauge, and output scaling
  checks are recorded in `premise_results.json`.
- The extractor refuses malformed networks; the driver refuses index >=600.

## Estimated inference cost

The measured standalone anchor costs 6.189B analytical FLOPs.  The
feature recurrence requires the already-available covariance states plus
roughly 0.0335B for the first Gram, about 0.150B for 36-column normalized
response transport, and under 0.03B for row reductions/readout: a target
increment below 0.14B before official FlopScope porting.  No optional
dense R^2/R^4 tensor square was used.

## Reproducibility

- `run_premise.py` SHA-256: `0107d7c3a7ee30a0f66a9c8c02b8481a13bf40f47e2aa0f2dd238b2759bc2841`
- `cached_features.npz` SHA-256: `5aef60194c5b50651446e2bfb61f814a2055631edf15ee37041ae5cb47d38503`
- 100 MLPs, 256 outputs each, feature count `70`.
