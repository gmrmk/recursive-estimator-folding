# M118 — separated `aabc` collision vertex: theory, cost, and adversarial audit

Date: 2026-08-07  
Scope: a target-free, analytic audit at `n=d=256`, `L=32`.  It does **not**
run M113 or M117, inspect a contest row/truth/scorer, modify a candidate, or
claim a terminal-network result.  “Collision” always means equality of
external tensor slots, not repeated edges in a Hermite graph.

## Decision

**KILL as an M117 cost repair and as an IMPLEMENT candidate.**  The local
object is legitimate and has a useful structure: after collapsing the two
equal axes, the exact zero-mean `aabc` ReLU cumulant is one universal,
three-variable function on the positive-semidefinite correlation domain.  A
Price-recursive Taylor/Chebyshev expansion gives separated polynomial terms,
and each term has a matrix-free `O(n^2 m q)` action in either relevant pair
orientation.  This is a real mechanism change from streaming roughly 100M
`aabc` entries.

It does not clear the frozen `m=32`, `q=12`, two-sided, depth-32 bill.  Its
first nonzero weak-coherence jet is already

\[
 F(x,y,z)=\frac{xy+xz+yz}{4\pi}+O(\|(x,y,z)\|^3). \tag{1}
\]

The three nonzero separated quadratic monomials require three feature banks
if the approximation is to reproduce that jet.  Once all six `aabc` slot
placements are reconstructed as a symmetric pair operator, the favorable
two-sided action cost is `38.654705664B` FLOPs.  Charging only the remaining
small collision strata, feature construction, and the required QR gives
`283.763288064B`, **11.763288064B over 272B**, while charging zero for the
exact all-distinct mask, Price responses, mean/covariance feedback,
coefficient certification, and execution residual.  Therefore it has no
material margin even before its central ownership obligation is met.

More decisively, adding a compressed exact collision vertex does not make the
already-sketches bulk collision-free.  Exact ownership requires

\[
 K_r=P_{\cal D}{\cal G}^{\rm TS}_{r,E}
      +P_{\rm aabc}\widetilde F
      +P_{\rm other\ collision}S_r^{\rm exact}, \tag{2}
\]

not `G + F`.  No cheap exact action for `P_D G^TS` is specified.  The only
currently explicit general construction is equality-partition
inclusion--exclusion, with 15 terms for `k4`; its conservative range-action
schedule alone is `2,876.442624B` rather than the existing `191.762841600B`.
A differently sketched approximation to the collision part cannot be
subtracted from the original sketch and still assert exact ownership.

Finally, an affordable action is not an affordable rank-four state.  The
cross-pair `aabc` suboperator is block diagonal over the repeated axis and is
generically rank `Theta(n^2)` already in (1).  Affine transport then densifies
the collision tensor.  No rank-four capture or deep response closure follows.

Status: **IMPLEMENT: no.  REPAIR: only after the gates below.  KILL: the
frozen M118 proposal.**

## 1. Exact collapsed vertices and their ownership

Let `g(t)=max(t,0)`, `h(t)=g(t)-E g(N)`, and let `(A,B,C)` be standard normal
with

\[
 C(x,y,z)=\begin{pmatrix}1&x&y\\x&1&z\\y&z&1\end{pmatrix}\succeq0.
\]

The `aabc` value, with `A` the repeated coordinate, is

\[
 F(x,y,z)=\operatorname{cum}(g(A),g(A),g(B),g(C))
 =E[h(A)^2h(B)h(C)]-E[h(A)^2]E[h(B)h(C)]
 -2E[h(A)h(B)]E[h(A)h(C)]. \tag{3}
\]

Thus `F(x,y,z)=F(y,x,z)`.  It is an exact three-dimensional truncated-normal
quantity, not an iid or annealed surrogate.  The other collision functions
needed for the source are only lower-dimensional:

\[
\begin{array}{c|c|c}
\text{stratum}&\text{universal value}&\text{axes}\\ \hline
k_3:\ aab&G(x)=\operatorname{cum}(g(A),g(A),g(B))&2\\
k_3:\ aaa&G_0&1\\
k_4:\ aabc&F(x,y,z)&3\\
k_4:\ aabb,H(z);\ aaab,J(z)&2\\
k_4:\ aaaa&J_0&1.
\end{array} \tag{4}
\]

All physical values are formed in standardized coordinates and then multiplied
by the product of their slot scales.  In particular,
`K4[i,i,j,k]=s_i^2 s_j s_k F(R_ij,R_ik,R_jk)`.  This is essential for positive
ReLU-gauge covariance.

For a canonical `a,{b,c}` with `b<c`, scatter all 12 ordered placements (six
choices of the repeated slots and the two assignments of `b,c`).  Equivalently
one may work in the symmetric-pair space, but its multiplicities must be
identical.  Storing only `i,i,j,k` is not a symmetric `k4` source.

The disjoint source rule is (2), where `P_D` keeps all-distinct tuples and the
three collision masks partition its complement.  It prohibits both common
errors:

* `G^TS + F` double counts every collision graph present in the TensorSketch
  bulk;
* `G^TS + F - G_E` subtracts a different, unsketched graph and is not the
  sketched operator that was added.

## 2. A genuinely separated construction

On the weak domain

\[
 D_\tau=\{(x,y,z): |x|,|y|,|z|\le\tau,\ C(x,y,z)\succeq(1-2\tau)I\},
 \qquad 0<\tau<\tfrac12, \tag{5}
\]

the collapsed integral is analytic.  A tensor Chebyshev interpolant, or the
equivalent Price-recursive Taylor polynomial, has the form

\[
 \widetilde F_P(x,y,z)=\sum_{a,b,c\ge0\atop a+b+c\le P}
 c_{abc}x^ay^bz^c,\qquad c_{abc}=c_{bac}. \tag{6}
\]

Price differentiation supplies the coefficients and an independent
truncated-normal calculation can validate them.  At zero threshold the
centered ReLU Hermite coefficients are `d1=1/2`, `d2=phi(0)`.  The connected
graphs with two cross-axis edges and one internal `A--A` edge give (1): each
of `xy`, `xz`, and `yz` has coefficient
`d2^2 d1^2 * 2 = 1/(4 pi)`.  This is also a useful implementation check.

The homogeneous quadratic tensor with entries at `(1,1,0)`, `(1,0,1)`, and
`(0,1,1)` is the three-mode W tensor and has real separated rank three.
Consequently the quadratic jet cannot be reproduced by one or two functions
of the form `f(x)g(y)h(z)`.  Writing it as `xy + z(x+y)` only hides the same
three banks: the second summand has separated rank two.  An AAA/rational or
TT proposal must expose an equally charged separated realization; it may not
book one rational evaluation as though it were one pair factor.

For a monomial define `R=BB^T` and use an explicit, covariantly carried
TensorSketch frame.  There are two pair-orientation classes.

### Repeated pair against two distinct slots

For `aa|bc`, let

\[
 P_{(r,s),(j,k)}={\bf1}\{r=s=i\}\,R_{ij}^aR_{ik}^bR_{jk}^c. \tag{7}
\]

With

\[
 \psi_{ab}(i)=TS_m[\Phi_a(i)\otimes\Phi_b(i)],\quad
 \chi_{abc}(j,k)=R_{jk}^cTS_m[\Phi_a(j)\otimes\Phi_b(k)], \tag{8}
\]

`P` is approximated by a rectangular factor whose left rows are nonzero only
at `(i,i)` and whose right rows are `chi(j,k)`.  Its two-sided action costs
`4 n^2 m q+O(nmq)` FLOPs: the large contraction is against the `n^2` right
factor in one direction and against it after a cheap diagonal contraction in
the other.

### Repeated axis split across the two pair sides

For `ab|ac`, let

\[
 Q_{(i,j),(k,l)}={\bf1}\{i=k\}\,R_{ij}^aR_{il}^bR_{jl}^c. \tag{9}
\]

For every fixed `i` it is an `n x n` block.  Set

\[
 U_i(j,:)=R_{ij}^aTS_m[\Phi_c(j)],\qquad
 V_i(l,:)=R_{il}^bTS_m[\Phi_c(l)]. \tag{10}
\]

Then `Q_i approximately equals U_i V_i^T`, so applying all blocks to `q`
columns costs `4 n^2 m q`; applying its adjoint costs the same.  This is
indeed matrix-free and avoids an `n^3 q` sparse gather/scatter loop.

The complete symmetric pair operator is assembled as `P+P^T` plus the four
cross-pair placements from (9), with the `B/C` symmetry in (6) enforced before
compression.  Pair swaps are explicit permutations, not a PSD assertion.
The construction preserves hidden permutations only if the sketch frame is
transformed with the hidden permutation; a frozen index hash is equivariant
only in distribution.  Standardization before truncation preserves the
positive gauge.  Negative rescaling is not a ReLU gauge.

## 3. Rigorous error and near-singularity gates

No degree, CP/TT rank, rational pole set, or `m=32` sketch width is certified
by smooth-looking samples.  A valid M118 would freeze all of the following
before an accuracy experiment.

1. **Deterministic vertex tail.**  Use interval Price recurrences (including
   the ReLU boundary distributions) or interval truncated-normal quadrature
   to enclose all derivatives needed for (6) over every box in `D_tau`.  A
   Taylor certificate can use

   \[
   \epsilon_{\rm poly}\le
   \overline M_{P+1}\frac{(3\tau)^{P+1}}{(P+1)!}, \tag{11}
   \]

   with `Mbar` an actually evaluated interval bound on the directional
   `(P+1)`-st derivative.  A Chebyshev implementation needs the corresponding
   certified Bernstein-ellipse or interval interpolation remainder.  DCT
   coefficient decay or a degree-16/18 difference is a falsifier statistic,
   never this certificate.

2. **Absolute action budget.**  For normalized `Q` with
   `||Q||_F <= sqrt(q)`, an entrywise `aabc` error at most `epsilon_F` implies

   \[
   \|E_{\rm aabc}Q\|_F\le
   \sqrt{6(n)_3q}\,\epsilon_F.
   \tag{12}
   \]

   At `n=256,q=12`, the multiplier is `34551.9991`.  The predeclared allowed
   source-action error must therefore be divided by this number and by the
   appropriate physical scale bound; a relative-only vertex test is invalid
   near a zero cumulant.

3. **Sketch error.**  Add a separately certified
   `epsilon_TS` and numerical moment error to (11).  A width-32 TensorSketch
   offers neither a deterministic uniform inner-product error nor an operator
   norm certificate over approximately 100M `aabc` entries.  A probability
   statement must freeze the distribution, failure probability, all queried
   actions, and the union/operator-norm argument.  A pointwise sketch check
   cannot certify the range finder that chose its probes from the action.

4. **Fail-closed distinct-axis gate.**  Construct the strong-edge graph
   `H_tau={ij: |R_ij|>tau}` before fitting any vertex.  For a proposed strong
   cluster partition, certify both a component cap and the block-whitened
   cross norm

   \[
   \gamma=\|R_{CC}^{-1/2}R_{CD}R_{DD}^{-1/2}\|_{op}<\gamma_0<1. \tag{13}
   \]

   Also use a pivoted factorization/eigenvalue enclosure for each distinct
   three-axis covariance.  A small raw edge bound does not control a nearly
   singular block.  If a component cap, a whitening bound, or a covariance
   lower bound fails, **KILL**; do not loosen `tau` after seeing an error.

   In the present cost model even a component cap does not create a cheap
   strong `aabc` algorithm: one strong pair participates with every third
   axis.  The only currently cost-safe gate is stronger—require no strong
   edge at all (`max_{i!=j}|R_ij|<=tau`)—or supply and bill a separate exact
   strong-triple action.  PSD equicorrelation permits one component of all
   256 coordinates, so a universal bounded-cluster claim is false.

These gates also apply to `G,H,J` in (4).  The univariate `aab` function is
cheap enough to evaluate directly, but it cannot repair an uncertified `F` or
mask the sketched bulk.

## 4. Full two-sided cost ledger

This ledger intentionally grants M118 every favorable convention already used
by M117: `L=32`, `n=256`, `q=12`, `m=32`, two-sided range finding, f64, and the
corrected 30-action base graph bill.  Let one *feature bank* mean one
separated monomial with width `m`.  For its fully slot-symmetric `aabc`
contribution, (7) and (9) each cost `8 L n^2 m q` across the two sides.
Therefore

\[
 C_{\rm action,bank}=16Ln^2mq=12.884901888\text{ B}. \tag{14}
\]

The unavoidable degree-two jet has three banks, not one.  Reusing the base
FFT/CountSketch convention, its `P` right factor and `Q`'s two block factors
cost at least

\[
 C_{\rm feature,bank}=6Ln^2m\log_2m=2.013265920\text{ B}. \tag{15}
\]

This omits coefficient evaluation, streaming writes, scale restores, and any
sketch-error certificate.  The QR charge is a favorable thin-QR estimate:
two `k4` pair blocks plus one large and one small `k3` block,
`L[2 QR(n^2,q)+QR(n^2,q)+QR(n,q)] = 1.814151168B`.

| charged item | FLOPs |
|---|---:|
| M117 corrected known subtotal: base formation, base features, affine covariance and rank-4 transport | 236.251146240 B |
| `aabc` quadratic-jet actions, three banks, (14) | 38.654705664 B |
| all other exact collision actions (`k4` non-`aabc` plus `k3`) | 1.003487232 B |
| `aabc` feature construction, three banks, (15) | 6.039797760 B |
| thin QR for both orders | 1.814151168 B |
| **favorable subtotal with masking, response, certification, and residual set to zero** | **283.763288064 B** |
| **over 272B before those required items** | **11.763288064 B** |

Thus the proposal cannot get below 272B with material margin in the stated
configuration.  Reducing `m` below 32 makes this particular arithmetic look
better but supplies no replacement sketch certificate; it does not make the
unbilled mask, response, or rank capture free.  Taking `P<2` discards the
first nonzero source jet and is not a collision repair.

The required omitted costs make the result stronger, not weaker:

| required component | honest status |
|---|---|
| exact `P_D G^TS` ownership mask | no cheap valid action specified; 15-term inclusion--exclusion replaces the existing `191.762841600B` graph-range line by `2,876.442624B` in the disclosed conservative schedule |
| Price `3->3`, `3->4`, `4->3`, `4->4` responses and `r=1,2` feedback | no closed finite-rank formation/action is given, hence no finite full M118 bill can set this to zero |
| coefficient/tail and TensorSketch-error certification | must be charged after a concrete interval and probability procedure exists |
| symmetrization, masking, scale restoration, allocator/bandwidth residual | positive work; no wall-clock exemption follows from the dense-FMA convention |

For scale, replacing just the existing unmasked graph-range line by the
15-action inclusion--exclusion schedule adds `14 * 191.762841600B` to the
favorable subtotal.  It produces **at least `2,968.443070464B` before any
Price response, covariance feedback, or residual**.  This is not asserted as
a lower bound on every imaginable mask algorithm; it is the only explicit
general exact-mask schedule presently available, and it shows why a new mask
identity must be supplied rather than presumed free.

The `16.64B`/`8.32B` affine transports are already inside the known subtotal.
They are not a response calculation.  Calling the displayed favorable
subtotal a complete deep recurrence would silently repeat M113/M117's missing
response and covariance-closure steps.

## 5. Rank capture and affine densification

The `O(n^2mq)` block action in (10) is not a low pair-rank factor.  Retain
only the quadratic jet.  For a fixed repeated axis `i`, the cross block is

\[
 B_i(j,l)=\frac{1}{4\pi}\{R_{ij}R_{il}+R_{ij}R_{jl}+R_{il}R_{jl}\}
 =\frac{1}{4\pi}\{r_i r_i^T+\operatorname{diag}(r_i)R+
 R\operatorname{diag}(r_i)\}, \tag{16}
\]

where `r_i=R[i,:]^T`.  For a generic nonsingular weak-coherence `R` with
nonzero `r_i`, the last two summands make `B_i` full rank.  The operator in
(9) is block diagonal over `i`, so it generically contains `Theta(n^2)` pair
rank before the other slot placements are added.  A fast application of its
many small rank-`m` blocks does not change this fact.

Nor is collision support affine-invariant:

\[
 [W^{\otimes4}K^{\rm aabc}]_{abcd}
 =\sum_{i,j,k}W_{ai}W_{bi}W_{cj}W_{dk}K_{iijk}^{\rm aabc}. \tag{17}
\]

For a dense fixed `W`, this is dense on all-distinct output slots.  If M118
compresses before (17), it must demonstrate rank-four capture for the **full,
symmetrized, collision-inserted source** and bound the discarded energy in a
gauge-covariant norm.  Testing only the all-distinct TensorSketch bulk, or
only one block `B_i`, is an invalid surrogate.  If it transports the block
format without compression, its equality-block structure is destroyed and the
next-layer `O(n^2mq)` action is unavailable.

This disposes of the hoped-for propagation claim: separated local collision
evaluation can improve a first-layer source approximation, but it neither
survives arbitrary affine transport in the same format nor closes the Price
response hierarchy.

## 6. Cheapest target-free falsifier

The cheapest decisive falsifier is the static ledger in section 4: it is
deterministic, needs no weights, samples, scorer, or network execution, and
already kills the frozen configuration.

If a separately named repair first supplies a new exact mask and a lower
budget, the next cheapest *mathematical* falsifier is still not an M113/M117
rerun:

1. Freeze a public seed and build a fresh `12 x 12` PSD correlation matrix
   `R=(1-alpha)I+alpha R0`, where `R0` is a normalized deterministic Gram
   matrix and `alpha` is chosen before inspection so all off-diagonals lie in
   `D_tau`.
2. Materialize only the harmless `144 x 144` pair unfolding of the **analytic
   quadratic tensor** (1), scattering all `aabc` slots exactly.  No ReLU
   simulation or deep forward is involved.
3. Require exact slot symmetry, pair-swap symmetry, permutation covariance
   with a co-transformed sketch frame, and positive-gauge covariance after
   restoring arbitrary positive scales.  Verify that collision and bulk masks
   have disjoint support.
4. Compute its exact best rank-four pair energy and the frozen separated
   range's captured energy.  Kill the repair if rank four retains less than
   `0.80`, if the proposed range captures less than `0.95` of that rank-four
   energy, or if any identity exceeds `1e-11` relative f64 error.  No rank,
   degree, threshold, sketch width, seed, or norm may be retuned after a
   failure.

This test is cheaper than three-dimensional moment quadrature and attacks the
rank obstruction that compression must overcome.  A pass would not validate
the tail, the all-distinct mask, or deep response; it would only leave those
separate gates open.

## IMPLEMENT / REPAIR / KILL

### IMPLEMENT

**None.**  Do not implement M118 under the frozen M117 formation configuration.
The favorable, response-free subtotal is already over budget, while exact
bulk/collision ownership is unimplemented.

### REPAIR

A new candidate may be considered only if all of these are predeclared and
independently billed:

1. a deterministic or rigorously probabilistic, **exactly collision-masked**
   TensorSketch bulk action—not a post-hoc subtraction with another sketch;
2. a certified `F,G,H,J` approximation on a fail-closed PSD/whitened domain,
   including the absolute action gate (12);
3. a fully symmetrized two-sided cost below 272B with a material reserve for
   Price responses, covariance feedback, QR, masking, and residual;
4. rank capture of the full collision-inserted source before affine transport,
   plus a post-transport closure/capture rule.

The new candidate must use the target-free falsifier above before any deeper
experiment.  A pass is not authority to add it to a production estimator.

### KILL

Kill the present M118 parameterization (`P>=2`, separated quadratic jet,
`m=32`, `q=12`, rank 4, 32 layers, two-sided range finding).  It fails the
static 272B gate and has no exact masked-bulk or affine-rank closure.  Do not
reinterpret its fast block action as a rank-four representation, silently
omit the four Price channels, or tune `tau`, degree, rank, or sketch width in
response to a failed gate.

## Primary-source ledger and boundary of claims

The mathematical tools invoked here are limited to the primary research
sources already frozen for the related source audit: Price's Gaussian
derivative identity ([Price, 1958](https://doi.org/10.1109/TIT.1958.1057444)),
the truncated-normal MGF route ([Tallis, 1961](https://doi.org/10.1111/j.2517-6161.1961.tb00408.x)),
the distributional multivariate formulation needed by ReLU boundaries
([Voigtlaender, 2017](https://arxiv.org/abs/1710.03576)), TensorSketch as an
approximate polynomial feature map ([Pham and Pagh, 2013](https://doi.org/10.1145/2487575.2487591)),
and action-based range finding rather than rank creation
([Halko, Martinsson, and Tropp, 2009](https://arxiv.org/abs/0909.4061)).

They support the local identities and the possible separated constructions.
They do **not** certify a width-32 uniform sketch error, an all-distinct mask,
a rank-four pair range, a deep Gaussian/Price closure, a response truncation,
or a final fixed-network error.  All numerical counts and the KILL conclusion
above are direct derivations from the frozen M117 accounting convention.
