# Research note: conditional response factorization

Date: 2026-08-06

Purpose: ground the H15/H16 mutations in exact probability identities. These
sources justify the algebraic operators, not the empirical claim that they will
beat the WHestBench estimator. The latter remains behind frozen synthetic gates.

## Primary sources

1. Felix Voigtlaender, *A general version of Price's theorem* (2017),
   https://arxiv.org/abs/1710.03576

   The paper gives a rigorous multivariate Price theorem, including
   distributional derivatives. For tensor-product nonlinearities this links
   covariance derivatives of Gaussian nonlinear moments to products of
   univariate response derivatives. ReLU is admissible through the
   distributional formulation. This motivates, but does not prove sufficient,
   a low-order response-vector expansion for conditional ReLU covariance.

2. David R. Brillinger, *The calculation of cumulants via conditioning*,
   Annals of the Institute of Statistical Mathematics 21 (1969), 215--218,
   DOI: 10.1007/BF02532246. Journal index:
   https://www.ism.ac.jp/editsec/aism/vol21.html

   Brillinger's conditioning formula expresses unconditional cumulants as a
   partition sum of cumulants of conditional cumulants. It is the exact basis
   for H16: all-distinct tensor sectors need not be deleted if their directional
   contractions can be assembled from conditional mean/covariance/cumulant
   response factors.

3. Robert Price, *A useful theorem for nonlinear devices having Gaussian
   inputs*, IEEE Transactions on Information Theory 4(2) (1958), 69--72,
   DOI: 10.1109/TIT.1958.1057444.

   The original engineering theorem establishes the covariance-response
   derivative identity for nonlinear transformations of Gaussian inputs. The
   modern rigorous source above is used for implementation details.

## Concrete translation

For a scalar conditioning variable `T` and vector response `Y=ReLU(Z)`,

```text
Cov(Y) = E_T[Cov(Y|T)] + Cov_T(E[Y|T]).
```

The second term is a Gram operator of univariate coordinate responses
`g_i(t)=E[Y_i|T=t]`. Centered Hermite coefficients of `g_i` therefore generate
signed outer products without pairwise bivariate integration. Price's theorem
suggests derivative response vectors as an equivalent/related basis under a
Gaussian conditioning law.

For orders three and four, Brillinger's partition formula adds conditional
cumulants and cross-cumulants among conditional means, variances, and higher
conditional terms. Directional contraction with a next-layer row `w` can be
performed after projection (`w.g(t)`, `w^T C(t) w`, and low-rank analogues),
which retains all index patterns implicitly.

## Falsifiable boundary

- H15 must recover at least 80% of the banked exact conditional-covariance
  energy and material downstream signs with rank at most four and conservative
  target arithmetic below 80B.
- H16 must recover at least 80% of frozen k3/k4 standardized contraction energy
  and material signs while stating a sub-O(n^4) recurrence.
- Passing the representation gate does not establish effect size or a winning
  competition estimator. Dense exact factor discovery and generic recursion
  remain separate links.
