# Exact conditional-correlation spectrum audit

## Decision

**Screened survivor for the compression premise; not an estimator promotion.**

The scalar-conditioned ReLU covariance residual is strongly low rank on the
frozen synthetic sweep. Rank four captures **99.3533%** of aggregate
off-diagonal Frobenius energy and preserves **99.1170%** of material signed
downstream-mean corrections (898/906) over horizons two through four. It clears
the predeclared 80%/80% conjunction. Rank two also clears it at 96.4212% energy
and 97.2406% signs.

This does not yet solve the parent's weak-effect or deployment problem. The
residual itself is small (median covariance-residual/parent-covariance ratio
`3.88e-8`, maximum `1.64e-5` in this representative sweep), and direct nested
quadrature to discover the factors at `n=256,L=32` is estimated at **1.855T**
arithmetic, far beyond the 272B envelope. Once known, a rank-four factor costs
only **0.212B** arithmetic with 25% contingency to add to all nine steady
children at all 32 layers. The next missing mechanism is therefore analytic or
univariate-response formation of the factors, not compression.

No WHest data, scorer, truth, holdout, API, or estimator implementation was
used. This is a synthetic structural audit of a preserved component from the
`latent_gate_split` implementation.

## Frozen question and operator

For one parent Gaussian component, the gate split writes

```text
Z = mu + c T + epsilon,
T ~ N(0,1),
epsilon ~ N(0, C - c c^T),
```

and truncates `T` into three equal-probability bins. The existing operator
replaces each truncated bin by a Gaussian with the same first two moments,
then applies the Gaussian bivariate ReLU map. This audit instead computes

```text
E[relu(Z_i) relu(Z_j) | T in bin]
```

by one-dimensional quadrature over `T`, applying the conditional bivariate
Gaussian ReLU moment map at every node. Raw second moments are integrated
before subtracting the integrated marginal means.

For each bin,

```text
Delta_C = Cov_exact(relu Z | bin) - Cov_gaussianized(relu Z | bin).
```

The diagonal of `Delta_C` is retained exactly. The hollow off-diagonal part is
eigendecomposed, modes are ordered by absolute eigenvalue, and ranks
`1,2,4,8` are reconstructed. Because a truncated eigen-expansion of a hollow
matrix generally reintroduces a diagonal, that diagonal is explicitly
compensated; reported energy is the actual off-diagonal reconstruction energy,
not the optimistic sum of retained eigenvalues.

The parent's child mean is held fixed when transporting the full and truncated
covariance corrections through two, three, and four later Gaussian-ReLU
layers. Thus the sign audit isolates the covariance mechanism.

## Frozen synthetic sweep

- iid-He square weights `N(0,2/n)`;
- widths/seeds `(12,27112)`, `(16,27116)`, `(24,27124)`;
- depth 10;
- representative central maximum-mass components entering layers 1, 3, 5;
- all three truncation bins;
- 27 covariance cells and 81 cell/horizon responses;
- exact reference GL128 over `T` and GL128 inside the bivariate map;
- convergence comparator GL96/GL96;
- current parent comparator GL64;
- material coordinate threshold `0.25 * RMS(full correction)`.

The maximum absolute GL96-to-GL128 reference delta is `1.24345e-14`.
Relative to the off-diagonal residual it is at most `2.994e-3` and has median
`3.58e-8`. The parent's GL64-to-GL128 difference is at most `8.88e-16`.
All 27 direction solves are non-fallback and all rank-reconstructed child
covariances remain PSD in the downstream tests.

## Spectrum and signed transport

| rank | aggregate off-diagonal energy | material signs | mean cosine | minimum cosine | frozen gate |
|---:|---:|---:|---:|---:|:---:|
| 1 | 91.1255% | 94.4812% (856/906) | 0.9006 | 0.2059 | pass |
| 2 | 96.4212% | 97.2406% (881/906) | 0.9538 | 0.7580 | pass |
| 4 | **99.3533%** | **99.1170% (898/906)** | **0.9847** | 0.8216 | **pass** |
| 8 | 99.9032% | 100% (906/906) | 0.9989 | 0.9926 | diagnostic (`r>4`) |

The off-diagonal participation rank has median `3.53` and ranges from `3.19`
to `5.10`. Every hollow residual is necessarily signed; observed spectra have
both positive and negative modes. Rank four is stable by width:

| width | rank-4 energy | material signs |
|---:|---:|---:|
| 12 | 99.5310% | 96.7742% |
| 16 | 99.3080% | 99.6622% |
| 24 | 99.0097% | 100% |

The two tail bins carry essentially all energy: lower 45.43%, middle
`9.18e-6%`, upper 54.57%. This is the expected truncated-skew signature. The
middle bin is almost symmetric and its covariance correction is nearly zero.
The residual diagonal contributes a median 4.30% of total residual energy
(range 0.72% to 10.41%), supporting the exact-diagonal plus signed-low-rank
off-diagonal representation.

Rank one technically passes the aggregate gate but is not a robust deployment
choice: its worst cell/horizon cosine is 0.206 and its worst sign fraction is
61.5%. Rank four is the first audited choice with minimum cosine above 0.8;
its few sub-80% per-cell sign rates occur in vanishing middle-bin corrections.
No rank was selected or retuned from outcomes; this distinction is diagnostic.

## Cost boundary

For `q=3,n=256,L=32`, applying a known rank-four factor plus exact diagonal to
the nine steady children costs:

| operation | arithmetic |
|---|---:|
| dense factor reconstruction and add | 0.1699B |
| with 25% contingency | **0.2124B** |
| factor transport through the next weight | 0.2829B |
| transport with 25% contingency | **0.3536B** |

But the literal offline reference nests 64 `T` nodes with a 64-node bivariate
map for every pair, yielding **1.855T** arithmetic before eigendecomposition.
The spectrum result therefore validates compressibility, not affordable factor
identification.

## Salvage map and next mutation

Preserved components:

- the gate-boundary scalar direction;
- exact one-dimensional conditioning;
- exact cheap diagonal Rao--Blackwellization;
- a signed off-diagonal response with effective rank about four;
- robust downstream sign transport of its rank-four reconstruction.

Current failed link:

- forming the dense exact pairwise residual by nested bivariate quadrature is
  over budget, while the effect magnitude remains small under the generic
  three-bin recursion.

The next causal mutation should form the same signed factors without dense
pairwise quadrature. A concrete route is a **marginal-response Gram expansion**:
write the exact covariance as

```text
E_T[Cov(relu Z | T)] + Cov_T(E[relu Z | T]),
```

compare the truncated-`T` and moment-matched-Gaussian scalar laws, and test
whether the observed four modes are generated by a small basis of univariate
response vectors (`g(t)`, derivatives/Hermite coefficients, or quadrature
contrasts). That part costs `O(k n)` to form response vectors and `O(k n^2)`
to apply, rather than `O(T * bivariate_order * n^2)`. Its cheapest next
falsifier is the energy and downstream-sign fraction of this explicitly formed
response-Gram proxy against the exact factors already banked here.

If that proxy fails, retain the spectrum as evidence that the missing modes
live in `E_T[conditional covariance]`, requiring a pair-kernel separability or
adjoint contraction instead. The scalar-conditioning family remains unresolved;
only naive dense formation is currently non-working.

## Artifacts

- `PREDECLARED_GATE.md`: frozen scope and conjunction.
- `conditional_corr_spectrum.py`: exact reference, parent comparator, spectral
  reconstruction, downstream propagation, and cost model.
- `run_spectrum.py`: deterministic sweep and hashes.
- `results.json`: complete spectra, per-rank/per-horizon responses, aggregates,
  and cost targets.
- `test_conditional_corr_spectrum.py`: quadrature, oracle, reconstruction,
  cost, and machine-result gates.
