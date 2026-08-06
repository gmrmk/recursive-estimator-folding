# JSpace Gram-aligned control rung: prepared and locked

## Status

**Prepared; accuracy experiment not executed.**

The final frozen gate SHA-256 is:

```text
ED9C87B7F5EEFA18A785BD747606BF252D67CCAF9B82FEBCCDBADCE311FA38D2
```

`EXECUTION_UNLOCK.json` is intentionally absent. `run_accuracy.py` verifies the
current gate hash and unlock contents before creating a teacher or seed stream.
There is no `accuracy_results.json`.

## Frozen experiment

The eventual cleanroom comparison is:

1. no control;
2. four isotropic directions;
3. four top input directions from `J_hat^T J_hat`, where `J_hat` is the K=4
   signed terminal Jacobian estimate;
4. four top input directions from the K=4 terminal second-moment estimate
   `E[J^T J]`.

Each direction receives normalized Gegenbauer degrees 6 and 8. Coefficients
are fit on an independent pilot after centering target/features and scaling
features to unit pilot RMS. The fitted constant is discarded; only exact-zero-
mean homogeneous spectral controls reach the residual estimator.

The three random roles are strictly separated:

- 128 Gaussian states for the terminal JSpace/VJP pilot;
- 128 different Gaussian states for output coefficient fitting;
- 32 independent Haar rotations of the 288-point exact spherical 5-design for
  the accuracy residual.

All use a new seed band above 7.9 million. No official data, scorer, reference,
or outcome-selected seed/direction is in scope.

## Scope boundary

This rung measures only the **terminal full input-to-output Jacobian Gram**.
It does not estimate intermediate `J_l`, identify a layer band, or represent an
all-layer workspace. The prior 2.813B target-shape estimate applies to one
K=4, 128-state terminal/input Gram. A layerwise extension must be a separate
rung charging L-fold outer accumulation/storage and its activation/VJP
plumbing.

## Frozen synthetic cost ledger

The costs below are static formula outputs, not accuracy results.

| Cell | Total scalar FLOPs | Ratio to no control |
|---|---:|---:|
| no control | 1,142,784 | 1.000 |
| isotropic | 1,994,389 | 1.745 |
| signed terminal J | 5,066,389 | 4.433 |
| terminal second Gram | 5,066,389 | 4.433 |

The Jacobian-derived cells charge their independent 128-state K=4 VJP pilot,
not a shared or free workspace. This makes the cost gate deliberately hard:
the spectral residual must contract enough to repay both pilots.

## Implemented safeguards

- exact gate-hash lock before any accuracy object is constructed;
- deterministic eigenvalue ordering and largest-coordinate-positive sign rule;
- K=4 signed and second-Gram directions derived from the same pilot/probes;
- terminal input-direction covariance under orthogonal input transformations;
- independent seed bands asserted;
- centered/scaled ridge invariant to an arbitrary target constant;
- PSD, orthonormality, deterministic rerun, and cost-charge tests;
- machine output path exists but remains unreachable without explicit unlock.

Seven scaffolding tests pass. These tests use small fixtures only and do not
instantiate the frozen 16-network/32-rotation accuracy bank.

## Frozen decision rule after unlock

The second-Gram cell must reach raw degree-`>=6` variance ratio at most 0.60,
cost-adjusted ratio at most 0.90, win at least 12/16 networks, beat the signed-J
cell by 10%, and correlate at least 0.40 with randomized-design teacher error.
Symmetry, conditioning, exact-mean, PSD, and finite checks are mandatory.

The active-subspace objection remains explicit: rank-four capture of a degree-
six residual can scale as `(4/256)^6`. A small-shape win would authorize only a
larger cleanroom confirmation—not integration.

See [`PREDECLARED_GATE.md`](PREDECLARED_GATE.md) for the complete frozen
contract and [`PREPARATION_MANIFEST.json`](PREPARATION_MANIFEST.json) for the
execution state.
