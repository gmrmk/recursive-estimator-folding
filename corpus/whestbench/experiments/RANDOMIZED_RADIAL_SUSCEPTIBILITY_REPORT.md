# Randomized-radial susceptibility q3 compressor

## Decision

**The top gate-susceptibility q3 implementation is killed at the predeclared
one-step premise gate.  Its invariant projection, exact compressor, and causal
measurements are preserved.**

No truth vector, prediction array, WHest row, scorer, holdout, API, or
leaderboard value was read.  The width-64 Haar+chi2 parent and frozen n128
candidate were not modified.  The recorded parent hash is
`150657841fb72b3150e32fe465fb4c24d12c4d11e90df2ce9f1dc22b306215cf`
and still matches the file on disk.

## Mutation

At each frozen non-Gaussian child point cloud with moments `(m,C)` and next
weight `W`, the existing compressor sorts by the leading Euclidean direction
of `C`.  This pass changed only that sorting direction.  It formed

```text
mu = m W,  Sigma = W^T C W,
g_i = phi(mu_i/sigma_i)/sigma_i,
F = diag(g) Sigma diag(g),
a = diag(g) v_1 / sqrt(lambda_1),
s(x) = (x-m)^T W a.
```

The same three equal-mass bins and exact within-bin first/second-moment matches
were retained.  Thus the candidate and generic compressor begin the next step
with identical global mean and covariance; only their retained non-Gaussian
mixture geometry differs.

The one-step reference maps the uncompressed point cloud directly through the
next weight and ReLU.  Each q3 approximation is mapped through the identical
next seeded-Haar/chi2 sigma-point operator, with no second recompression.

## Frozen result

| quantity | result | gate |
|---|---:|:---:|
| susceptibility/generic aggregate RMS error | **0.975251** | `<=0.80`, fail |
| relative improvement | **2.475%** | `>=20%`, fail |
| state wins | **11/24** | `>=18/24`, fail |
| maximum source moment relative error | `3.80e-15` | pass |
| minimum normalized covariance eigenvalue | `-3.79e-16` | pass |
| maximum permutation error | `8.27e-14` | pass |
| maximum positive-gauge error | `9.45e-16` | pass |
| spectral ambiguities / tie collapses | `0 / 0` | pass |
| conservative n256/L32 cost | `71.953B` | `<80B`, pass |

The unit tests for moment conservation, PSD, combined input/output
permutation-positive-gauge covariance, and cost all pass.

## Failure localization

The result is sharply depth dependent:

| frozen group | state wins | RMS ratio | share of generic error energy |
|---|---:|---:|---:|
| L16 layer 0 | 4/4 | 0.9673 | 47.96% |
| L16 layer 8 | 0/4 | 1.3266 | 1.17% |
| L16 layer 14 | 1/4 | 1.2137 | 1.23% |
| L32 layer 0 | 4/4 | 0.9630 | 48.99% |
| L32 layer 16 | 2/4 | 1.1806 | 0.31% |
| L32 layer 30 | 0/4 | 1.2034 | 0.33% |

The early state improves on all eight networks, but after the point law has
been recursively compressed the same direction loses on 10 of 16 middle/late
states.  The large early errors dominate the aggregate and conceal this sign
change.

Covariance is the binding observable: it contributes `0.592736/0.596625 =
99.35%` of the generic joint-error energy.  The susceptibility direction
reduces aggregate mean RMS by 3.94% and covariance RMS by 2.47%, but the
middle/late covariance ratios are 1.18--1.33.  This isolates the failed link:

```text
gate-boundary sensitivity F_phi
    -> good early partition / exact invariant geometry
    -/-> preservation of pair-covariance geometry in a deep non-Gaussian law.
```

That is consistent with the earlier Gaussian no-op theorem.  `F_phi` is an
invariant gate-probability response metric, not a complete metric for the
second-order observable created by a recursively non-Gaussian mixture.

## Salvage map and next mutation

Preserved components:

- the susceptibility Gram and its covariance/contravariance proof;
- downstream pullback through `W`, which makes the compressor one-step causal;
- exact equal-mass q3 moment conservation and PSD construction;
- unordered sign handling with no coordinate tie-breaker;
- the one-step uncompressed-cloud oracle, usable without truth;
- the Gaussian partition no-op theorem and the new deep sign-change evidence.

Killed implementation:

- one signed top-`F_phi` direction as the sole geometry for all three q3 bins.

Untested family:

- a fixed, parameter-free **dual-observable Gram** that adds the active linear
  response required by covariance.  In standardized preactivation coordinates
  with correlation `R`, define

```text
F_gate   = diag(phi(alpha)) R diag(phi(alpha)),
F_active = diag(Phi(alpha)) R diag(Phi(alpha)),
F_dual   = F_gate/tr(F_gate) + F_active/tr(F_active).
```

`F_active` is the correlation-coordinate delta-method metric for
`delta ReLU(z) approximately diag(Phi(alpha)) delta z`.  Both summands are
permutation similar and positive-gauge invariant; trace normalization fixes
their relative scale without fitting.  Pulling the unique top eigenvector of
`F_dual` back through `W` changes the failed observable metric while leaving
q3, exact moments, symmetry, and asymptotic cost unchanged.

That child must be predeclared on fresh iid-He states, not selected on these 24
outcomes.  Its kill signature is now explicit: it must reverse the middle/late
covariance degradation, not merely harvest the already-dominant layer-0 gain.
An even-degree `s(x)^2` tail partition is a separate covariance-targeted
operator and must not be mixed into the same first test.

## Artifacts

- `PREDECLARED_GATE.md` and `gate_contract.json`: frozen premise.
- `susceptibility_compressor.py`: candidate, invariance helpers, and cost.
- `run_one_step_gate.py`: deterministic 24-state truth-free runner.
- `one_step_results.json`: authoritative result, SHA256
  `31c90e55b53d0882e89e3d06b0c7a44817515180ce86b36244fbd0274cf1a3bc`.
- `test_susceptibility_compressor.py`: three structural tests.
