# Rao--Blackwellized within-bin ReLU marginals

## Decision

**Marginal-only implementation killed on the predeclared material-effect gate;
exact conditional integrals and the stable-sign mechanism are preserved.**

Preserving exact conditional marginal skew does not amplify the stable generic
gate-split signal. The child reaches aggregate ratio **0.997502361** with 8/8
wins, versus required ratio `<=0.8`. Its 0.249764% reduction is effectively the
same as the parent's 0.249758%.

The absolute aggregate-ratio improvement over the parent is only `6.08e-8`.
All eight child MSEs are microscopically lower than their parent counterparts,
but final predictions differ by at most `2.04e-8`. The mechanism is real and
directionally favorable, yet materially inert.

No WHest data, scorer, API, new case, or result-driven tuning was used. Before
the accuracy run, the numerical premise exposed slow inverse-CDF tail
quadrature; it was replaced with density-weighted rational-tail GL64 and had to
pass GL192 convergence tests before any case result was inspected.

## Sole mutation

The generic `latent_gate_split` parent is frozen: direction solve, ridge,
equal-probability bins, q=3, conditional Gaussian moments, GL64 full-covariance
ReLU map, generic compressor, cases, references, and tolerances.

For a coordinate of the original preactivation Gaussian, write

```text
Z_i | T=t ~ N(mu_i + c_i t, r_i),
c_i = Cov(Z_i,T),
r_i = C_ii - c_i^2.
```

Within each T-bin, the child replaces the Gaussianized marginal with

```text
E[ReLU(Z_i) | bin]
  = E_T[ g1(mu_i+c_i T, r_i) | bin ],

E[ReLU(Z_i)^2 | bin]
  = E_T[ g2(mu_i+c_i T, r_i) | bin ],
```

where `g1,g2` are exact univariate Gaussian ReLU moments. These one-dimensional
expectations use deterministic GL64 with direct normal-density integration;
infinite bins use `t=b +/- s/(1-s)`. If `r_i` is numerically zero, a closed-form
truncated-linear ReLU integral is used.

The parent's within-bin correlation matrix is retained. With RB marginal
standard deviations `s_i`, reconstruct

```text
C_RB = diag(s) R_parent diag(s).
```

Since this is a diagonal congruence of a PSD correlation matrix, the result is
PSD. The generic q=3 compressor is unchanged.

## Numerical and symmetry audit

Six tests pass:

- GL64 conditional marginals agree with GL192;
- the zero-residual special case satisfies exact truncated-moment identities;
- reconstructed child covariances pass relative PSD checks;
- end-to-end layerwise permutation equivariance;
- end-to-end internal positive-coordinate gauge invariance;
- conservative cost below 80B.

The frozen cases use no fallback and no degenerate residual coordinates.

## Frozen eight-case result

| L | seed | corrected fullcov MSE | RB-marginal MSE | ratio | win |
|---:|---:|---:|---:|---:|:---:|
| 16 | 18560 | 3.6884e-4 | 3.6847e-4 | 0.999014 | yes |
| 16 | 18561 | 8.2110e-4 | 8.1932e-4 | 0.997832 | yes |
| 16 | 18562 | 1.4425e-3 | 1.4335e-3 | 0.993736 | yes |
| 16 | 18563 | 2.0847e-4 | 2.0637e-4 | 0.989914 | yes |
| 32 | 18720 | 3.1834e-4 | 3.1643e-4 | 0.993993 | yes |
| 32 | 18721 | 2.8092e-3 | 2.8091e-3 | 0.999959 | yes |
| 32 | 18722 | 3.0041e-4 | 2.9966e-4 | 0.997522 | yes |
| 32 | 18723 | 5.9922e-4 | 5.9812e-4 | 0.998164 | yes |

Summed corrected-fullcov MSE is `0.00686808`; RB MSE is `0.00685092184`.

## Why the exact marginal correction vanishes

On the first frozen case, the gate statistic T explains only about `1.0304e-4`
of each coordinate's preactivation variance (minimum `1.03028e-4`, maximum
`1.03059e-4`). Therefore `Z_i | T in bin` is already extremely close, in its
univariate marginal, to the moment-matched Gaussian used by the parent. The
largest within-child mean correction over all layers and cases is only about
`1.12e-7`.

This is the high-dimensional dilution law in concrete form: the scalar
direction can align with the aggregate boundary target while coupling only
`O(1/n)` variance into any one neuron. Correcting marginal conditional skew
cannot recover the missing cross-neuron higher-order dependence.

## Conservative n256/L32 cost

| charged term | arithmetic |
|---|---:|
| covariance sandwiches | 6.442B |
| correlation eigensolves | 14.496B |
| generic compressor eigensolver | 4.832B |
| nine GL64 fullcov ReLU maps | 28.991B |
| conditional moments and recompression | 0.151B |
| RB marginal GL64 quadrature | 0.094B |
| correlation reconstruction | 0.113B |
| subtotal | 55.119B |
| with 25% contingency | **68.899B** |

The `<80B` gate passes. The material-effect failure makes a FlopScope port
unwarranted.

## Files

- `PREDECLARED_GATE.md`: frozen mechanism and gates.
- `latent_gate_rb_marginals.py`: quadrature, special case, PSD reconstruction,
  closure, and cost.
- `run_fresh_n64.py` / `fresh_n64_results.json`: matched evidence.
- `test_rb_marginals.py`: numerical, PSD, symmetry, and cost tests.
- `structural_audit.py` / `structural_audit.json`: coupling dilution and parent
  interaction.
- `finalize_decision.py` / `decision.json`: conjunction gate and hashes.
