# Randomized angular / radial cubature factorial

## Decision

**Screened synthetic survivor.**  The predeclared combined cell—seeded Haar
angular frames plus positive two-node chi radial quadrature—passes every frozen
width-64 gate:

- aggregate expected-MSE ratio: **0.63160** (`<=0.80` required);
- wins versus corrected fullcov: **7/8** (`>=6/8` required);
- conservative `n=256,L=32` cost: **70.590B** (`<80B` required);
- measured process peak working set: **37,036,032 bytes** (`<2GB` required);
- covariance, radial moments, Haar permutation coupling, and positive-gauge
  obligations: **pass**.

This is not a demonstrated competition winner.  It is a target-free survivor
on eight banked synthetic cases and should advance to an independent external
validation rung.  No WHest data, scorer, holdout, API, or new truth generation
was used.

## Frozen design

The branch is the predeclared 2x2 factorial motivated by
`sources/research_randomized_radial_cubature_20260806.md`:

| factor | level 0 | level 1 |
|---|---|---|
| angular | fixed covariance-square-root axes | one seeded Haar frame shared across q=3 components at each layer |
| radial | one radius `sqrt(n)` | two positive chi-n Gaussian nodes matching moments 0..3 |

It retains the full-covariance Gaussian-mixture state and q=3 equal-mass
moment compressor.  The compressor has a zero-progress guard for its final
bin; this preserves the intended equal-mass rule while preventing the resource
failure documented in `../latent_sparse_cubature/RESOURCE_POSTMORTEM.md`.

Haar master seeds were frozen before accuracy:

```text
104729, 130363, 155921, 196613
```

Each seed is a matched randomized-estimator replicate.  Haar cell loss is the
arithmetic mean of the four per-seed MSEs—expected randomized loss—not the best
seed and not the MSE of a post-hoc selected prediction.  Cost is for one
randomized draw; the four seeds estimate expectation and dispersion.

## Banked evidence only

The runner loaded the eight truth vectors and corrected-fullcov predictions
from `../latent_full_sigma/fresh_n64_results.json` (SHA-256
`A07455AE...F8DC1`).  The case keys exactly matched the frozen contract, and
every baseline prediction/MSE pair was rechecked to `1e-18`.  No forward Monte
Carlo or other truth generation exists in this runner.

## 2x2 factorial result

| angular | radial | aggregate ratio | wins | disposition |
|---|---|---:|---:|---|
| fixed axes | sqrt(n) | 8.87160 | 1/8 | parent failure reproduced |
| fixed axes | chi-2 | 9.10625 | 1/8 | radial repair alone worsens |
| Haar | sqrt(n) | 0.66880 | 7/8 | angular survivor |
| Haar | chi-2 | **0.63160** | **7/8** | **combined survivor** |

The dominant causal repair is angular randomization: at one radius it lowers
the ratio from 8.87160 to 0.66880.  Radial-2 alone changes the fixed-axis ratio
by `+0.23465` (worse), but conditional on Haar it changes the ratio by
`-0.03720` (better).  The difference-in-differences interaction is
**-0.27185**, so the radial gain is specifically enabled by removing fixed-axis
aliasing rather than being a universal improvement.

## Combined cell by case

| depth | seed | baseline MSE | expected Haar+radial2 MSE | ratio | win |
|---:|---:|---:|---:|---:|:---:|
| 16 | 18560 | 3.68836e-4 | 2.02935e-4 | 0.55020 | yes |
| 16 | 18561 | 8.21096e-4 | 4.45762e-4 | 0.54289 | yes |
| 16 | 18562 | 1.44252e-3 | 1.27290e-3 | 0.88241 | yes |
| 16 | 18563 | 2.08471e-4 | 1.71182e-4 | 0.82113 | yes |
| 32 | 18720 | 3.18339e-4 | 1.44504e-4 | 0.45393 | yes |
| 32 | 18721 | 2.80919e-3 | 1.21362e-3 | 0.43202 | yes |
| 32 | 18722 | 3.00407e-4 | 2.15355e-4 | 0.71688 | yes |
| 32 | 18723 | 5.99216e-4 | 6.71619e-4 | 1.12083 | no |

The single losing case is retained unchanged; there is no seed or case
selection.

## Rotation dispersion

| Haar seed | aggregate combined ratio | case wins |
|---:|---:|---:|
| 104729 | 0.74774 | 6/8 |
| 130363 | 0.67712 | 6/8 |
| 155921 | 0.48361 | 5/8 |
| 196613 | 0.61793 | 6/8 |

Mean ratio is 0.63160, population variance `0.0094122`, and standard deviation
`0.09702`.  All four individual aggregate ratios are below 0.80, so the mean
is not rescued by a single favorable rotation.  Case-level rotation MSE
standard deviations are recorded in `factorial_results.json`; the largest is
`6.09e-4` on seed 18562.  Dispersion is material and must be carried into the
next validation rung.

## Radial and symmetry proofs

For `R~chi_n`,

```text
E[R^k] = 2^(k/2) Gamma((n+k)/2) / Gamma(n/2).
```

The positive two-node Gaussian rule is constructed from moments 0..3.  At
`n=64`, its nodes are `7.2938891, 8.7067211` with weights
`0.5222906, 0.4777094`.  At `n=256`, nodes are
`15.2931040, 16.7069723` with weights `0.5110728, 0.4889272`.  Maximum audited
relative moment error is `1.50e-14`.

Every fixed/Haar and radius-1/radius-2 point measure recovers input mean and
covariance to at most `1.72e-15` relative covariance error.  For permutation
matrix `P`, coupling `Q'=P^T Q` is Haar and gives transformed nodes exactly;
the numerical coupling error was `1.07e-14`.  For positive scale `c`, the
symmetric root and every point scale by `c`; tested relative errors were below
`2.36e-15` from scales `1e-6` through `1e6`.  Full derivations are in
`SYMMETRY_PROOFS.md`, with machine-readable values in
`structural_results.json`.

## Conservative cost

The combined single-frame radial-2 rule creates `4n` points per component and
`M=4qn=3,072` steady children at `n=256,q=3`.

| charged term | operations |
|---|---:|
| covariance sandwiches | 6.442B |
| component symmetric square roots | 14.496B |
| one shared Haar QR per layer | 4.832B |
| compressor eigensolver | 4.832B |
| global/within-bin child moments | 25.770B |
| node formation | 0.101B |
| subtotal | 56.472B |
| with 25% contingency | **70.590B** |

The four evaluation seeds are independent matched replicates, not four
simultaneous deployed frames, so the single-draw randomized estimator cost is
the relevant bound.  Any deterministic deployment that averages all four
predictions would cost roughly four times as much and would fail the 80B gate;
that is not the candidate tested here.

## Resource and legality audit

The full 80-inference factorial completed in 43.99 seconds.  Process peak
working set was 37.04 MB and private bytes 56.93 MB.  OpenBLAS was pinned to one
thread before NumPy import.  Results checkpointed after every case.

Files and frozen hashes:

```text
factorial_contract.json 47203BF8591BCD04B672FD3926B00575D451F78B11FB54A545C821B6686F4BA6
randomized_radial.py    150657841FB72B3150E32FE465FB4C24D12C4D11E90DF2CE9F1DC22B306215CF
truth bank              A07455AE94A0BE47CD351A430E457BE76DE6C4CD6FC0BD31858E0F9BD72F8DC1
```

## Next rung

Preserve the combined mechanism and all negative ablations.  The next legal
step is an independent synthetic validation set with the same four frozen
rotation seeds and expected-loss aggregation, plus an explicit paired
uncertainty interval and tail analysis.  Do not tune seeds, radii, q, or the
losing case from these eight results, and do not call this the winning entry
until an untouched external gate and the competition's official accounting
boundary are passed.
