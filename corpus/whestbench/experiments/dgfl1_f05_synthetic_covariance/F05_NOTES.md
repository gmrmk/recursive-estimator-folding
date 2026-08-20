# DGFL-1 F0.5 synthetic covariance screen

**Status:** `PASS_F05_SYNTHETIC_COVARIANCE_ONLY`  
**Manifest:** `BCE377D1349BF6412A54DAF823D2B90A06F76DFE1CDD60EC2BFE501229EC8169`  
**Result file:** `06758EF252F55FAB504EC9C6716E8D889C2EBA82199B735EFB8E5D0AF6822392`  
**Runtime seal:** incomplete native inventory, disclosed post-execution

## Outcome

The prospectively frozen truth-free screen passed every gate on its one
deterministic two-dimensional hand ReLU network:

- held joint rotation-variance reduction: `R2 = 0.9416211929936065`;
- held Fourier contribution conditional on the dipoles: `R2 = 0.9388937394051985`;
- held dipole contribution conditional on the Fourier ladder:
  `R2 = 0.33005233901223785`;
- paired-bootstrap one-sided 99% lower order statistic:
  `0.9193896186765471`;
- whole-record permutation result: `p_num/p_den = 1/1025`.

The exact quantitative gates were joint `R2 >= 0.10`, both partial values
strictly positive, bootstrap lower strictly positive, and permutation
`p_num <= 10`. No gate was changed after the result.

The fit used 128 domain-separated rotations; evaluation used 128 untouched
held rotations. One six-vector was fitted by the frozen centered ridge law.
The dipole-only, Fourier-only, and joint arms were all derived by zeroing blocks
of that one vector, without refitting. Each rotation used exactly four shared
JVP evaluations to construct the base record and all six control records.

## Reproduction

Before the screen, 24 of 24 contract tests passed and an independent auditor
verified the exact source, runner, declared runtime inventory, randomization fixtures, mechanism
payloads, and preflight. After the result was saved, a second independent exact
manifest-bound replay returned exit code zero and reproduced the entire parsed
JSON, every displayed statistic, and all realized payload hashes. The runner
used no generated or challenge network, truth, scorer, provider prediction, or
worker process.

The replay audit also found that the original manifest's selected native-file
list omitted two NumPy-wheel DLLs that were loaded by the process. Their exact
paths, sizes, hashes, and an independent Windows process-module check are
preserved in the
[post-execution attestation](POSTEXECUTION_RUNTIME_ATTESTATION.json). The old
manifest was not edited. This means the current-machine result is exactly
reproduced, but the original prospective native dependency inventory was not
exhaustive and no cross-machine bitwise claim is earned.

The manifest also binds the pre-result companion-paper blob at SHA-256
`A690D1367E1C4B516FF5C0478A487462695A135269DD3CFE94647967BDB6E238`.
The paper was intentionally updated only after both runs to report the result.
Therefore a future exact replay must first restore that bound blob at its bound
path from commit `c6c226b211917d1c579cd995161b616ad36e0a98`; the old manifest
must not be edited to point at the post-result paper.

The [result](F05_RESULTS.json) retains raw C-order SHA-256 payloads for the
coefficient vector, all four held arms, all 4,096 bootstrap values, and all
1,024 permutation-null values. Fit and held `Y` and `Z` hashes are also
recorded.

## Interpretation and boundary

This result is the first positive synthetic covariance evidence for DGFL's combined
dipole-Fourier mechanism. On this hand network, the Fourier block carries most
of the explained rotation variance, while the dipole block still supplies a
strictly positive and substantial incremental contribution. The two blocks
are therefore complementary rather than merely duplicate parameterizations of
the same control.

It is not evidence that the effect transfers to `d=256`, Kerdock rows, W0,
generated networks, the challenge distribution, or the hosted evaluator. It
does not establish a provider source, complete cost or resource bound, bias,
MSE, official score, ranking, package, promotion, or submission. The pass earns
only the next source-completeness gate. A generated-network F1 remains blocked
until the production-Q/guard integration, Pilot-A law, complete success and
failure bills, wall/RSS behavior, and applicable Phase-2 rules are frozen.
