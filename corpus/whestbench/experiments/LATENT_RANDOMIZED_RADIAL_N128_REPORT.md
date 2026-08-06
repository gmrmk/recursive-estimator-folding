# Width-scaling decision: SURVIVE

The frozen Haar + two-node chi-radial, q=3 full-covariance estimator survives the fresh n=128, L=32 synthetic width-scaling gate. This is a production-port candidate, not a claimed competition winner: no WHest data, scorer, holdout, public row, or API was used.

## Frozen experiment

- Networks: four fresh iid-He networks, seeds `32801`, `32803`, `32831`, `32833`.
- Truth: 32,768 Philox antithetic pairs (65,536 forward paths) per network, streamed in batches of at most 1,024 pairs.
- Comparator: corrected full-covariance Gaussian closure.
- Candidate: one Haar frame per layer shared by all q=3 components, two positive chi-radial nodes matching radial moments 0 through 3, antipodal points, ReLU, and the guarded q=3 equal-mass compressor.
- Randomness audit: the same frozen rotation seeds `104729`, `130363`, `155921`, `196613`; the score is the arithmetic mean of the four per-rotation squared losses. No rotation was selected after observing truth.
- Resource limits: external per-case working set strictly below 2 GB and wall time strictly below 600 seconds; reducer zero-progress assertion required.

The frozen contract is [PREDECLARED_WIDTH_SCALING.md](./PREDECLARED_WIDTH_SCALING.md), and the machine-readable result is [scaling_results.json](./scaling_results.json).

## Result

| Network seed | Corrected fullcov MSE | Candidate expected MSE | Ratio | Win |
|---:|---:|---:|---:|:---:|
| 32801 | 6.01883e-4 | 3.54002e-4 | 0.5882 | yes |
| 32803 | 2.24205e-4 | 1.17701e-4 | 0.5250 | yes |
| 32831 | 2.68838e-4 | 2.52866e-4 | 0.9406 | yes |
| 32833 | 3.95000e-4 | 2.21529e-4 | 0.5608 | yes |
| **Aggregate** | **1.48993e-3** | **9.46098e-4** | **0.6350** | **4/4** |

The n=64 precursor ratio was 0.6316; the fresh n=128 ratio is 0.6350. The near-constant ratio is encouraging evidence that the gain is not a narrow small-width artifact, although four synthetic networks are still a screening set rather than a competition validation set.

Per-rotation aggregate ratios were:

| Rotation seed | Aggregate ratio | Wins |
|---:|---:|---:|
| 104729 | 0.5633 | 4/4 |
| 130363 | 0.2825 | 4/4 |
| 155921 | 0.9291 | 2/4 |
| 196613 | 0.7650 | 3/4 |

Every rotation passed the preregistered aggregate-ratio ceiling of 1.0. The weaker third rotation was retained in the arithmetic average exactly as frozen.

## Gate audit

All preregistered gates passed:

- Aggregate ratio 0.6350 <= 0.8.
- Four of four case wins >= three required.
- Every individual rotation aggregate ratio <= 1.0.
- Covariance, chi-radial moments, permutation/Haar coupling, positive-gauge symmetry, and reducer-progress tests passed. Maximum structural error was 4.16e-14.
- Conservative n=256, L=32 arithmetic estimate, including 25% contingency, is 70,590,136,320 operations, below the 80 billion gate.
- Maximum externally observed working set was 241,909,760 bytes; maximum case wall time was 26.115 seconds.
- All reducer zero-progress assertions passed.

The Monte Carlo references had mean-component standard errors from 5.41e-4 to 9.94e-4 and maximum component standard errors from 2.40e-3 to 4.62e-3. These references are adequate for the frozen aggregate screen, but they do not establish a leaderboard score or a guaranteed improvement on official rows.

## Decision

Advance only to a FlopScope production port. Do not promote this result to “winning entry,” and do not run official/public rows without explicit parent authorization. The required implementation and quantization path is specified in [PRODUCTION_PORT_SPEC.md](./PRODUCTION_PORT_SPEC.md).

## Reproducibility hashes

- Scaling contract: `7f7e790d7b6dc070cb52839ad2a550409568a84eecf0164ecdfb30b0a72b63b2`
- Candidate source: `150657841fb72b3150e32fe465fb4c24d12c4d11e90df2ce9f1dc22b306215cf`
- Corrected comparator source: `bdaef07f8c30de33afa78fec71ace3143d1752d095c54eb8801008971e2ae0b3`
- Structural result: `d41775fc223f7bf2be3fe709a45ec7ae5763955a638087458a4d2e1b0e9d98f7`
- Case worker: `f0f6ace1b491e7320e805e9a223f6d1c2e89bfc575ae2150c1ec6259cfee2044`
- Scaling result: `0669df13335c22341f1e418e65f35245c4c3b05f68b8c2a55e622d77fdc311fb`
