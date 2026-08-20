# M113 — matrix-free Gaussian-vertex construction for fixed-weight ReLU cumulant modes

## Scope and verdict

This is a weights-only research derivation for a fixed, bias-free iid-He ReLU
MLP with `d=n=256` and `L=32`.  It uses neither contest data, a scorer, a
target, a network-forward experiment, candidate edits, nor a submission.
"Weights-only" below means that every proposed quantity is a deterministic
function of the fixed matrices (and a declared algorithmic sketch frame), not
an average over sampled Gaussian inputs.

**Result.** There is a genuinely matrix-free way to form the *local Gaussian
ReLU source vertices* for the leading pair-unfolded `k3` and `k4` modes.  It
uses a Hermite connected-multigraph expansion and TensorSketch features of the
correlation matrix.  A `k4` source application costs `O(G n^2 m q)`, rather
than materializing an `n^2 x n^2` object or paying `O(n^4)`; a randomized
two-sided range finder can therefore construct rank-4 signed pair factors.

The result is exact for a Gaussian preactivation in the infinite-degree,
unsketched limit.  In this network that statement is exact at the first ReLU,
but **not** at later ReLUs.  A source-plus-direct-leg recurrence is an explicit
first-Born closure, not an exact fixed-network recurrence.  The full Price
response contains collision and cross-order source terms, while the mean and
covariance also need their own non-Gaussian responses.  Thus M113 resolves the
specific *factor-formation* obstruction for the Gaussian vertex, but does not
justify the `~4.7e-8` terminal claim or replace the conditional-residual
oracle.

For orientation only, the supplied error scales are `~5e-5` for the
full-covariance Gaussian baseline, `~4.7e-8` for an exact terminal `k3/k4`
calculation, and `~2.7e-7` for the raw sampling champion.  No value is
measured, compared, or selected in this note.

The relevant primary-source ledger is
[`research_m113_matrixfree_vertex_20260807.md`](../../../sources/research_m113_matrixfree_vertex_20260807.md).
Price's theorem is rigorous for distributional ReLU derivatives in the
multivariate setting [Voigtlaender, 2017](https://arxiv.org/abs/1710.03576);
the original Gaussian-device relation is Price (1958), DOI
[10.1109/TIT.1958.1057444](https://doi.org/10.1109/TIT.1958.1057444).

## 1. Quenched object, not the annealed surrogate

Let the fixed matrices be `W_l`, let

\[
 z_1=W_1x,\qquad h_l=\rho(z_l),\qquad z_{l+1}=W_{l+1}h_l,\qquad
 \rho(u)=u_+ ,\qquad x\sim N(0,I_d).
\]

The required object is the **quenched** mean

\[
 \mu_L(W)=\mathbb E_x[h_L(x)\mid W_1,\ldots,W_L]. \tag{1}
\]

All cumulants below are conditional on those same weights.  In contrast,
averaging the iid-He matrices as well gives `E_W mu_L(W)`.  That annealed
quantity restores exchangeability and often reduces to scalar variance
recurrences.  It averages away the fixed, anisotropic covariance and
pair-eigenmodes that a conditional residual oracle sees.  It is therefore not
an identity for (1), and an annealed low-rank statement is not evidence that a
fixed network's pair factors can be formed.

This distinction also rules out a tempting misuse of Price's theorem.  Price
differentiates a *known Gaussian expectation* with respect to covariance.  It
does not say that `z_l` is Gaussian after a previous fixed ReLU layer, and it
does not supply the integral of a generic deep piecewise-linear fixed network.
Hessian-vector products have the same boundary: Pearlmutter's `Hv` is exact
once the scalar function is available, but neither it nor nested AD evaluates
the missing expectation in (1) [Pearlmutter, 1994](https://doi.org/10.1162/neco.1994.6.1.147).

## 2. Gaussian baseline and the exact local source

At one activation, take the baseline preactivation as

\[
 Z_i=m_i+s_i\xi_i,\qquad \xi\sim N(0,R),\qquad
 s_i>0,\quad R_{ii}=1,\quad t_i=m_i/s_i. \tag{2}
\]

The Gaussian ReLU mean is

\[
 \mu_i^{G}=s_i\{\phi(t_i)+t_i\Phi(t_i)\}. \tag{3}
\]

The full Gaussian covariance is obtainable from the usual bivariate truncated
normal/arc-cosine formula (or by Price differentiation), so maintaining a
full `n x n` Gaussian mean/covariance state is not the `n^4` bottleneck.
Cho--Saul give the associated Gaussian ReLU kernel in the zero-mean case
[Cho--Saul, 2009](https://papers.nips.cc/paper_files/paper/2009/hash/5751ec3e9a4feab575962e78e006250d-Abstract.html).

Expand the centered coordinate in probabilists' Hermites:

\[
 \rho(m_i+s_i\xi_i)-\mu_i^G=\sum_{q\ge1}a_{i,q}H_q(\xi_i),
 \qquad d_{i,q}:=q!a_{i,q}. \tag{4}
\]

Integration by parts gives the useful closed coefficients

\[
 d_{i,1}=s_i\Phi(t_i),\qquad
 d_{i,q}=s_i\phi(t_i)H_{q-2}(-t_i)\quad(q\ge2). \tag{5}
\]

For `t_i=0`, this reduces to `d_1=s_i/2`, `d_{2a}=s_i\phi(0)(-1)^{a-1}(2a-3)!!`,
and `d_q=0` for odd `q>1`.  Equation (5), rather than a zero-threshold
special case, is required after the first fixed layer because its Gaussian
baseline mean is generally nonzero.

For `r` distinct *slots* (the coordinate values need not be distinct), let
`M=(m_uv)_{u<v}` be a symmetric multigraph on `[r]`, with degree
`deg_M(v)=sum_{u != v} m_uv`.  The Gaussian connected source is exactly

\[
 {\cal S}_r(i_1,\ldots,i_r)
 =\sum_{\substack{M\;\text{connected}\\\deg_M(v)\ge1}}
 \left\{\prod_{v=1}^r d_{i_v,\deg_M(v)}\right\}
 \left\{\prod_{u<v}\frac{R_{i_ui_v}^{m_{uv}}}{m_{uv}!}\right\}. \tag{6}
\]

It is the connected Wick/Hermite diagram formula.  Connectedness makes (6) a
cumulant rather than a raw moment.  Equation (6) is an exact analytic source
for `k3`/`k4` if `Z` is Gaussian and the series is not truncated.  It is also
an exact, non-sampling source at the first ReLU since `W_1x` is Gaussian.

The source is the missing term in the naive transport law.  Keeping only
`W^{\otimes r}k_r` says that a ReLU transports existing cumulant but creates
none; (6) shows this is false even for an exactly Gaussian input.

## 3. Matrix-free `k4` pair operator

Flatten the ordered pair `(i,j)` into a row index.  For one graph on four
vertices write

\[
 a=m_{13},\ b=m_{14},\ c=m_{23},\ d=m_{24},\qquad
 u=m_{12},\ v=m_{34}, \tag{7}
\]

Factor `R=BB^T`; for an integer `e>=0`, the exact polynomial feature
`\Phi_e(i)=B_{i,:}^{\otimes e}` obeys

\[
 \langle\Phi_e(i),\Phi_e(j)\rangle=R_{ij}^e. \tag{9}
\]

The tensor product in (9) is never formed.  Let `TS_m` be a declared
TensorSketch of width `m` and set

\[
 \begin{aligned}
 A_M(ij,:)&=\frac{d_{i,\deg(1)}d_{j,\deg(2)}}{\prod m_{pq}!}
 R_{ij}^{u}\;\mathrm{TS}_m\!\left[\Phi_a(i)\otimes\Phi_b(i)
 \otimes\Phi_c(j)\otimes\Phi_d(j)\right],\\
 B_M(kl,:)&=d_{k,\deg(3)}d_{l,\deg(4)}R_{kl}^{v}\;\mathrm{TS}_m\!\left[
 \Phi_a(k)\otimes\Phi_c(k)\otimes\Phi_b(l)\otimes\Phi_d(l)\right].
 \end{aligned} \tag{10}
\]

Then one graph contribution has the matrix-free approximation

\[
 [{\cal S}_{4,M}]_{(ij),(kl)}\ \simeq\ A_M(ij,:)B_M(kl,:)^{\mathsf T}.
 \tag{11}
\]

The two feature inner products in (10) reproduce exactly the four cross-pair
edges `R_ik^a R_il^b R_jk^c R_jl^d` before sketching.  Internal pair edges are
the scalar multipliers `R_ij^u` and `R_kl^v`.  A general graph is not itself a
symmetric pair factor because `u` and `v` can differ.  Summing the graph and
its pair-swapped relabeling (or explicitly symmetrizing) restores the required
pair-unfolding symmetry and allows signed terms; no false PSD claim is made.

For any `Q in R^(n^2 x q)`, the source action is simply

\[
 {\cal S}^{(E,m)}_4Q=\sum_{M:\ |M|\le E}A_M(B_M^{\mathsf T}Q), \tag{12}
\]

plus the symmetrized terms.  It requires `O(G_4(E)n^2mq)` arithmetic and
`O(n^2m)` transient words per graph, never an `n^2 x n^2` matrix.  `G_4(E)`
counts labeled connected multigraphs retained by the Hermite-degree cutoff.
For nonzero thresholds, `G_4(3)=16` and `G_4(4)=79`; the smaller zero-threshold
parity count is not valid at later layers.

TensorSketch is being used in its proper, limited role: an approximate feature
map for a polynomial kernel [Pham--Pagh, 2013](https://doi.org/10.1145/2487575.2487591).
It changes neither the source identity (6) nor a truncation error into an
exact factorization.

## 4. The analogous `k3` operator and factor state

For a three-vertex graph, separate `(i,j)|k`.  Put `u=m_12`, `a=m_13`, and
`b=m_23`; then use

\[
 A_M(ij,:)=\frac{d_{i,\deg(1)}d_{j,\deg(2)}}{\prod m_{pq}!}R_{ij}^u
 \mathrm{TS}_m[\Phi_a(i)\otimes\Phi_b(j)],\quad
 B_M(k,:)=d_{k,\deg(3)}\mathrm{TS}_m[\Phi_a(k)\otimes\Phi_b(k)]. \tag{13}
\]

Thus `S_3 \simeq sum_M A_M B_M^T`; symmetrize over the three choices of the
single slot.  The matrix-free action is `O(G_3(E)n^2mq)`.  At general
threshold, `G_3(3)=10` (and `G_3(2)=3`).

After applying (12)--(13) to a `q=r+p` block of pair probes and the adjoint
to the resulting basis, a standard two-sided randomized range finder produces
rank-`r` signed factors.  This is the legitimate use of matrix-free randomized
low-rank approximation [Halko--Martinsson--Tropp, 2009](https://arxiv.org/abs/0909.4061):
the low-rank conclusion is a measured approximation property, not an input
assumption.  At pair rank `r=4`, retain

\[
 k_4\approx\sum_{a=1}^r\lambda_a U_a\otimes V_a,\qquad
 k_3\approx\operatorname{Sym}\sum_{a=1}^r A_a\otimes b_a, \tag{14}
\]

where every `U_a,V_a,A_a` is an `n x n` matrix after unflattening.  An affine
map transports them exactly within the retained representation:

\[
 U_a\mapsto WU_aW^T,\quad V_a\mapsto WV_aW^T,\quad
 A_a\mapsto WA_aW^T,\quad b_a\mapsto Wb_a. \tag{15}
\]

This is the sought-after matrix-free mode **transport**.  It avoids an exact
`p x p` `k4` matrix with `p=n^2=65,536`; such a dense matrix would contain
over 4.29 billion entries before any eigendecomposition.

## 5. What recurrence is actually justified

Let `K_s^z` be the incoming connected cumulant.  A formal first-Born expansion
about (2) is

\[
 K_r^h={\cal S}_r(m,C)+\sum_{s=3}^4{\cal R}_{r\leftarrow s}(m,C)[K_s^z]
 +O((K_3^z,K_4^z)^2,K_{\ge5}^z),\qquad r=1,\ldots,4. \tag{16}
\]

There is an exact definition of the linear response in (16), but it is not a
free gate product.  With `M(\tau;m)=E_G exp(sum_a tau_a rho(Z_a))` for the
`r` exposed coordinates, its coefficient for an assignment
`alpha in [r]^s` is

\[
 R^{\alpha}_{r\leftarrow s}(C_I)=\frac1{s!}\,
 \partial_{\tau_1}\cdots\partial_{\tau_r}
 \left.\left\{M(\tau;m)^{-1}\partial_{m_{\alpha_1}}\cdots
 \partial_{m_{\alpha_s}}M(\tau;m)\right\}\right|_{\tau=0}. \tag{17}
\]

Consequently

\[
 [{\cal R}_{r\leftarrow s}K_s]_{i_1\ldots i_r}
 =\sum_{\alpha\in[r]^s}R^\alpha_{r\leftarrow s}(C_I)
 [K_s]_{i_{\alpha_1}\ldots i_{\alpha_s}}. \tag{18}
\]

Equations (17)--(18) are the precise Price/characteristic-function response.
ReLU is legal here in the distributional sense, not because it is smooth
[Voigtlaender, 2017](https://arxiv.org/abs/1710.03576).  They expose three
previously hidden requirements:

1. `k3 -> k4` and `k4 -> k3` cross responses exist;
2. repeated-index collision slices such as `K4[i,i,j,k]` enter even when all
   exposed output indices are distinct; and
3. the `r=1,2` responses are required to correct the mean and covariance
   state on which the next Gaussian vertex depends.

The coefficients in (17) are functions of only an `r x r` Gaussian submatrix.
They can themselves be Hermite-expanded in its correlations.  Every monomial
has the same pair-kernel/TensorSketch factorization as (10); multiplying it by
a factor in (14) makes at most `m*r` temporary columns, then range-compresses
again.  This is a real, no-input-Monte-Carlo route to a full *truncated*
response operator.

It is not yet a cheap exact recurrence.  A fully specified implementation
would have to freeze: the coefficient-bank degree, all equality partitions,
the `3->3`, `3->4`, `4->3`, and `4->4` channels, sketch dimension, and the
recompression norm.  Those are source terms, not optional numerical details.
Brillinger's conditional-cumulant identity is a useful warning that dropping
such terms does not become valid merely because a conditional tensor has low
rank [Brillinger, 1969](https://doi.org/10.1007/BF02532246).

The only cheap recurrence currently certified by this derivation is the
**direct-leg subclosure**

\[
 K_r^h\ \leftarrow\ {\cal S}_r^{(E,m)}(m,C)+D^{\otimes r}K_r^z,
 \qquad D_{ii}=E\rho'(Z_i)=\Phi(t_i),\qquad r=3,4, \tag{19}
\]

followed by (15) and rank compression.  The direct leg is exact as one term of
(17), and preserves the pair factors by diagonal scaling.  It deliberately
omits all collision/cross-order responses in (18); it must be labelled a
screened first-Born approximation, not "Price propagation."

## 6. Terminal mean and the covariance obstruction

For a scalar final Gaussian baseline `N(m,s^2)`, the first linear Edgeworth
mean correction is

\[
 E\rho(Z)\approx s\{\phi(t)+t\Phi(t)\}
 -\frac{t\phi(t)}{6s^2}\kappa_3(Z)
 +\frac{(t^2-1)\phi(t)}{24s^3}\kappa_4(Z). \tag{20}
\]

The needed marginal cumulants are accessible from (14) after affine transport
by `U_a[w,w]`-style quadratic forms, without constructing dense `k4`.
Equation (20) does **not** license a terminal precision claim: it omits
`k3^2`, `k3*k4`, `k4^2`, and all `k5+` terms required by a higher-order
Edgeworth expansion.

More seriously, the given full-covariance Gaussian error scale (`~5e-5`) is
already orders of magnitude above a `~4.7e-8` terminal aspiration.  In (16),
the `r=2` response changes `C`; the changed `C` changes every later source
(6), every threshold `t`, and the terminal baseline in (20).  Carrying only
rank-4 `k3/k4` while freezing covariance is therefore not a closed route to
that accuracy.  The known adjoint rank explosion for mean/covariance is a
missing link, not a cost that may be silently waived.

## 7. Honest `n=256, L=32` bill

Use the deliberately modest, fully frozen formation setting
`r=4`, oversampling `p=8` (`q=12`), TensorSketch width `m=32`, and the
general-threshold tree cutoff `E=3`.  It has `G_3=10`, `G_4=16`.  One source
range action for both orders costs

\[
 (G_3+G_4)n^2mq
 =26\cdot256^2\cdot32\cdot12=0.654311424\ \text{B flops}. \tag{21}
\]

Two-sided range finding costs twice this, about `1.309 B` per activation and
`41.90 B` across 32 activations, before QR and feature construction.  A
conservative CountSketch/FFT feature build for both left/right factors is
`O(2(G_3+G_4)n^2m log_2(m))`, about `17.45 B` more across 32 activations.
This is a dense-FMA accounting convention; it is an arithmetic estimate, not
a wall-clock claim.  At `E=4`, the general-threshold graph counts become
`G_3=22,G_4=79`; range finding alone becomes `162.67 B` and the analogous
feature build about `67.78 B`.  That cutoff is already impractical under the
272-B envelope after transports.  The threshold shift is why the deceptively
cheaper zero-mean parity count is not used.

Other unavoidable costs are:

| Item | Conservative cost at `n=256,L=32` | Comment |
|---|---:|---|
| Gaussian covariance affine updates | about `2.08 B` | `31 * 4 n^3`, before elementwise Gaussian-ReLU covariance work |
| `k4` affine transport, general signed rank 4 | `16.64 B` | `31 * 8 n^3 r`; both pair factors are charged |
| `k3` affine transport, symmetric rank 4 | `8.32 B` | `31 * 4 n^3 r`, plus negligible vector maps |
| Tree-source two-sided range finding | `41.90 B` | equation (21) |
| Tree-source TensorSketch factor construction | about `17.45 B` | conservative two-side `m log_2(m)` count |
| Pair-state QR/SVD, scaling/diagonal slices | not free | order `L n^2 q^2`, but implementation-dependent |

The known subtotal is roughly `86 B` before QR/SVD, the Gaussian-ReLU
elementwise work, and all response channels.  A **budgeted** full-response
experiment could allocate at most about `180 B` to the `m*r` response feature
banks and recompressions to remain below `272 B`; it cannot claim that the
unbounded series or all cross-order channels fit.  `E=4` leaves essentially no
credible response budget.  By comparison,
standard TT does not solve source formation: it assumes the relevant
high-dimensional tensor/function is compressible and then rounds it; the
previous product-grid rank evidence is a direct reason not to use it as a
rescue.  TT's representation/rounding distinction is standard
[Oseledets, 2011](https://doi.org/10.1137/090752286).

The persistent rank-4 `k4` state occupies only two `n^2 x 4` f64 factors
(`4.0 MiB`); an `n^2 x 12` range block is `6.0 MiB`.  The constraint is source
work and omitted physics, not storage of the compressed state.

## 8. Invariance audit

Work in standardized coordinates before rank truncation:
`bar K_r[i_1,...,i_r]=K_r[i_1,...,i_r]/prod s_i`.  Compress this object, then
restore the scale.  Otherwise an ordinary Frobenius rank-4 truncation is not
even invariant under a positive ReLU gauge.

| Transformation | Analytic source/response | Finite TensorSketch implementation |
|---|---|---|
| Hidden permutation `P` | equivariant: `m,s,R` and every tensor factor are permuted | only equivariant **in distribution** under ordinary index-hash sketches; exact covariance needs the sketch frame to be permuted with `P` |
| Orthogonal input rotation | invariant at layer 1 because `W_1Q^T(QW_1^T)=W_1W_1^T`; downstream state follows | same, conditional on a coupled sketch frame |
| Positive diagonal ReLU gauge | equivariant after standardized compression; `t,R` invariant and factors rescale tensorially | fails if raw Euclidean factors are truncated; standardized state is mandatory |
| Pair-slot swap / tensor symmetry | restored by graph relabeling and explicit symmetrization | must symmetrize before/after compression, not assume one graph is PSD |
| Negative rescaling | not a ReLU gauge | no invariance claim |

This exposes a nontrivial issue.  A frozen ordinary CountSketch associates
random hashes with hidden-unit labels, so it breaks exact pointwise
permutation equivariance.  One may state distributional equivariance, or make
the random frame an explicit covariant algorithm input and transform it with
the hidden permutation.  Calling a fixed-seed hash result an exact
permutation-invariant weights-only identity would be false.  A deterministic
Krylov seed built only from `I,R,m,s` restores exact covariance but can miss
the leading pair range; it needs its own falsification.

## 9. What remains missing, with no oracle laundering

1. **Gaussianity after layer 1.**  Equation (6) is exact only for Gaussian
   `Z`.  Deep fixed preactivations are not Gaussian; a Gaussian closure is an
   approximation even when its covariance is exact.
2. **Hermite tail and correlations.**  A ReLU has an infinite Hermite series.
   Near correlated/near-degenerate coordinates, a small total-edge cutoff
   need not control the source tail.  TensorSketch adds a second, signed
   approximation error.
3. **Full Price response.**  The collision and `3<->4` channels in (18) are
   mandatory source/response terms.  The direct-leg law (19) omits them.
4. **Mean/covariance feedback.**  `r=1,2` responses and `k5+` cumulants are
   not represented.  They are especially fatal to claims below the known
   covariance-baseline error.
5. **Objective mismatch.**  A pair Frobenius SVD/range finder is not
   contraction-aware for the final mean.  The terminal row directions and
   Edgeworth weights would need to be fixed before choosing the compression
   metric; post hoc oracle alignment is not a formation method.
6. **Conditional-oracle gap.**  The reported rank-1--4 conditional residual
   factors with `>0.98` terminal fidelity say that a *given* residual can be
   represented.  They do not imply that the local Gaussian sources (6), their
   deep response corrections, or their weights-only factors have that rank.
   Substituting oracle scalar cumulant responses into (12) would merely hide
   the exact information the recurrence must create.

## 10. Cheapest generated-only falsifier (specified, not run)

Run one algebraic source test only; it has no contest instance, scorer,
target, input Monte Carlo, or deep network forward.

1. Freeze a seed and generate one `d=n=12` iid-He `W_1`.  Set
   `m=0`, `C=W_1W_1^T`, and normalize to `R`.
2. Build the **first-layer Gaussian** `S_4` exactly enough for reference by
   summing (6) to a predeclared high degree (for example total edge degree
   18) in f64, then materialize its harmless `144 x 144` pair unfolding.
   This is analytic Gaussian algebra, not a forward evaluation.
3. Form its exact best rank-4 pair range.  Independently construct the frozen
   `E=3,m=32,q=12` matrix-free source range from (10)--(12), with the sketch
   frame carried covariantly through one hidden permutation and one positive
   gauge rescaling.
4. Kill M113's formation route if either (i) the analytic rank-4 source energy
   is below `0.80`, or (ii) the sketched range captures below `0.95` of that
   best-rank-4 source energy, or (iii) the coupled permutation/gauge result
   disagrees above `1e-11` relative f64 error.  Record the one result; do not
   retune degree, sketch width, rank, seed, or compression norm after failure.

This is the cheapest binding test because layer one is exactly Gaussian, so a
failure cannot be blamed on deep non-Gaussian closure.  A pass would establish
only that the proposed source-factor operator works on its one domain of
exactness.  It would not promote (19), repair the covariance feedback, or
support a final-mean accuracy claim.

## Final disposition

M113 supplies a concrete source operator that the prior adjoint-only approach
lacked: connected Hermite Gaussian vertices can be applied, sketched, and
range-compressed from fixed weights in sub-`O(n^4)` arithmetic.  It therefore
deserves the narrow generated-only source falsifier above.

It does not solve the full fixed-network problem.  The direct recurrence is a
screened Gaussian/first-Born closure; the exact deep response requires the
unformed Price coefficient banks, covariance/mean feedback, and higher
cumulants.  Until those missing terms are formed and the specified source
falsifier passes, there is no honest path from this derivation to the quoted
terminal precision or to a contest-facing change.
