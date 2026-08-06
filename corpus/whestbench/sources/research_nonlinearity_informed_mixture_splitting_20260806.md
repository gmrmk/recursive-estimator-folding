# Research note: nonlinearity-informed Gaussian mixture splitting

Date: 2026-08-06. Evidence type: primary-literature mechanism support, not a
WHestBench accuracy claim.

## Relevant primary work

- Kulik and LeGrand, *Nonlinearity and Uncertainty Informed Moment-Matching
  Gaussian Mixture Splitting* (2024), choose splitting directions using both
  the nonlinear map and the input uncertainty, and explicitly whiten/naturally
  scale the direction to remove coordinate-unit dependence:
  https://arxiv.org/abs/2412.00343
- Duník et al., *Directional splitting of Gaussian density in non-linear random
  variable transformation* (2018), study Gaussian-mixture splitting directions
  selected by non-Gaussianity induced by a nonlinear transform:
  https://ietresearch.onlinelibrary.wiley.com/doi/full/10.1049/iet-spr.2017.0286
- Faubel and Klakow, *Further Improvement of the Adaptive Level of Detail
  Transform: Splitting in Direction of the Nonlinearity* (EUSIPCO 2010), use a
  three-component split and report lower transform MSE from a direction aligned
  with the nonlinearity:
  https://www.eurasip.org/Proceedings/Eusipco/Eusipco2010/Contents/papers/1569292135.pdf
- Luo, Moroz, and Hoteit, *Scaled Unscented Transform Gaussian Sum Filter*
  (2010), combine Gaussian mixtures with deterministic nonlinear uncertainty
  propagation, establishing the broader split/propagate/recombine pattern:
  https://arxiv.org/abs/1005.2665

## WHestBench translation

For one Gaussian preactivation component `Z~N(mu,C)`, define

`b_i = sigma_i * phi(mu_i/sigma_i)` and solve `C a = b`.

The standardized projection

`T = a^T(Z-mu) / sqrt(a^T C a)`

is invariant under a positive coordinate gauge `Z' = D Z`: `b'=Db`,
`a'=D^-1 a`, and therefore `T'=T`. It also commutes with neuron permutations.
The factor `phi(mu_i/sigma_i)` concentrates the split on coordinates with mass
near the ReLU gate; the factor `sigma_i` supplies the required gauge units.

Partition T into three equal-probability standard-normal intervals. For an
interval `(l,u)` with probability `p`,

`m = (phi(l)-phi(u))/p`,

`v = 1 + (l phi(l)-u phi(u))/p - m^2`.

Let `k=C a/sqrt(a^T C a)`. The exact conditional moments are

`E[Z|bin] = mu + k m`,

`Cov[Z|bin] = C + (v-1) k k^T`.

Each conditional law is then Gaussianized, propagated through the exact
Gaussian ReLU moment map, and passed to the existing deterministic compressor.
The approximation is the conditional Gaussianization and later recompression,
not the scalar conditional moments.

## Why this is a causal reimplementation

Fixed-r covariance factors failed because captured trace vanished with width.
Full-covariance 2n sigma points failed because a second-moment-exact axis rule
aliased gate angles. The gate-aligned split chooses a scalar sufficient
direction from the nonlinear observable instead of covariance energy. Its
predeclared falsifier remains the frozen fresh n64 suite: ratio <=0.8 versus
corrected full covariance, at least 6/8 wins, exact scale/permutation tests,
and conservative target arithmetic below 80B.
