# M117 — collision-renormalized Hermite/polymer source: theory, cost, and adversarial audit

Date: 2026-08-07  
Scope: a weights-only, target-free analytic investigation at width `n=d=256` and depth `L=32`.  No contest row, truth, scorer, public result, candidate edit, or M113 execution was used.  This is a new construction and an audit of whether it could repair M113's local-source failure; it is not a claim about a final network output.

## Decision

**KILL as a full post-M113 route.**  There is a mathematically valid local Gaussian-source decomposition:

\[
S_r=S_r^{\rm collision,exact}+S_r^{\rm all\text{-}distinct,weak},\qquad r\in\{3,4\},
\]

where every repeated-label stratum can be evaluated through at-most-trivariate truncated-Gaussian ReLU moments.  It removes the literal `R_ii=1` singular-correlation mechanism from the Hermite graph tail and is therefore a legitimate diagnostic hypothesis for the recorded degree-16-to-18 drift.

It does **not** fit the 272B envelope in the only already-specified rank-4, two-sided matrix-free configuration.  Even granting a free, exact all-distinct mask for the sketched bulk—which is not available—the exact sparse collision actions lift the previously corrected 236.251146240B known subtotal to a lower-bound 390.066235392B.  The missing Price response, covariance/mean feedback, masking overhead, quadrature, QR/SVD, and execution residual are still uncharged.  The requisite strict cost gate consequently fails before any numerical test should run.

There is also no propagation closure: this proposal improves a **local source** only.  It neither forms the full `k3/k4` Price responses nor proves that the source, including its exact collision part, has a rank-four pair range.  Arbitrary affine transport immediately turns a collision-supported tensor into a dense all-distinct tensor.  Thus M117 cannot honestly be described as supplying final `k3/k4`.

The narrow component is **REPAIR-worthy only as a separately budgeted local-source diagnostic** if a future method first proves an exact masked/sketched action and a compression of the `aabc` stratum whose cost, error, symmetry, and capture are certified.  It is not IMPLEMENT-ready.

## 1. The local object and what “collision” means

For one Gaussian activation write

\[
 Z_i=m_i+s_i\xi_i,\quad \xi\sim N(0,R),\quad R_{ii}=1,\quad X_i=(Z_i)_+.
\]

For slots \(I=(i_1,\ldots,i_r)\), define the exact local Gaussian source

\[
 S_r(I)=\operatorname{cum}(X_{i_1},\ldots,X_{i_r}). \tag{1}
\]

It equals the source used in a Gaussian ReLU vertex; centering the individual `X` values does not change any cumulant of order at least two.  M113's connected Hermite/multigraph series is an exact representation of (1) only in its infinite-degree, unsketched Gaussian limit.  It is exact as a local distributional identity at the first layer, but it is not an assertion that later fixed-network preactivations are Gaussian.

The equality partition of the *external slots*, not the equality of graph edges, is the relevant collision label.  Let \(\pi(I)\) partition \(\{1,\ldots,r\}\) by equal coordinate labels.  The disjoint supports are

\[
 \mathcal C_r=\{I:\lvert\pi(I)\rvert<r\},\qquad
 \mathcal D_r=\{I:\lvert\pi(I)\rvert=r\}. \tag{2}
\]

This matters because a diagram can have a unit factor `R_ii=1` whenever two distinct slots name the same coordinate.  That factor is not weak merely because the output tensor is globally high-dimensional.

### Exact equality strata

The counts below are for ordered tensor entries.  A canonical value can of course be stored once and scattered over its slot permutations, but a pair-unfolding action must account for all ordered entries.

| order | canonical equality type | slot partitions | ordered entries | distinct axes needed |
|---|---|---:|---:|---:|
| `k3` | `abc` | 1 | \((n)_3\) | 3 |
|  | `aab` | 3 | \(3(n)_2\) | 2 |
|  | `aaa` | 1 | \(n\) | 1 |
| `k4` | `abcd` | 1 | \((n)_4\) | 4 |
|  | `aabc` | 6 | \(6(n)_3\) | 3 |
|  | `aabb` | 3 | \(3(n)_2\) | 2 |
|  | `aaab` | 4 | \(4(n)_2\) | 2 |
|  | `aaaa` | 1 | \(n\) | 1 |

Here \((n)_p=n(n-1)\cdots(n-p+1)\).  At `n=256`,

\[
\begin{aligned}
N_{3,\rm coll}&=3(n)_2+n=196{,}096,\\
N_{4,\rm coll}&=6(n)_3+7(n)_2+n=99{,}943{,}936,\\
N_{4,\rm aabc}&=6(n)_3=99{,}486{,}720.
\end{aligned} \tag{3}
\]

So `aabc`, not a small diagonal, is 99.54% of the `k4` collision support.  It is only 2.327% of all \(n^4\) entries at 256, but it is too large for an arbitrary sparse matrix-times-block action to be dismissed.  At `d=12`, the collision fraction is 8,856/20,736 = 42.71%; it is therefore a plausible contributor to the observed small-width drift, but not evidence that it was the cause.

## 2. Exact collision values from truncated-Gaussian moments

This section gives the construction, not a claim that it is numerically free.

Let `A` contain the `p` distinct axes occurring in a collision tuple, where `p<=r-1` and hence `p<=3` for the tables above.  For any nonempty subset `B` of those axes, define the truncated moment-generating function

\[
 \Psi_B(u)=\mathbb E\!\left[e^{u^T Z_B}{\bf1}\{Z_B>0\}\right]
 =e^{u^Tm_B+\frac12u^TC_Bu}\,
   \Phi^+_{|B|}(m_B+C_Bu;C_B). \tag{4}
\]

The equality follows by completing the Gaussian square.  It is the useful specialization of the truncated multivariate-normal MGF derived by Tallis.  For positive integer powers \(\alpha_a\),

\[
 M_B(\alpha)=\mathbb E\prod_{a\in B}(Z_a)_+^{\alpha_a}
 =\left.\partial_u^{\alpha}\Psi_B(u)\right|_{u=0}. \tag{5}
\]

For labelled slots, form the cumulant exactly from the finite moment-partition identity

\[
 S_r(I)=\sum_{\nu\in\Pi_r}(-1)^{|\nu|-1}(|\nu|-1)!
 \prod_{C\in\nu}
 \mathbb E\prod_{t\in C}X_{i_t}. \tag{6}
\]

Every factor on the right is one of (5) in dimension at most three for a collision `k4` entry.  There are only 5 and 15 labelled set partitions for orders three and four respectively.  This is an exact mathematical specification in terms of standard normal orthant probabilities and derivatives; it is not Monte Carlo.

Two independent routes should agree in an implementation:

1. Differentiate (4), preferably with a stable low-dimensional normal-CDF/orthant routine and certified absolute error.
2. Use the covariance derivatives supplied by Price's theorem.  For ReLU powers, the recurrences must retain the indicator/boundary terms when a differentiated positive-part power reaches zero; replacing them by ordinary polynomial moments is wrong.

Price originally established the Gaussian-device covariance identity, and Voigtlaender supplies a rigorous multivariate, distributional form appropriate for ReLU's nonsmooth derivatives.  Tallis is the primary MGF reference.  See [Price (1958)](https://doi.org/10.1109/TIT.1958.1057444), [Voigtlaender (2017)](https://arxiv.org/abs/1710.03576), and [Tallis (1961)](https://doi.org/10.1111/j.2517-6161.1961.tb00408.x).

### Numerical cautions

`R_ii=1` itself is harmless after repeated labels are collapsed: the `aaa` value is one-dimensional and `aabc` is three-dimensional.  The genuine numerical hazard is a nearly singular *distinct-axis* submatrix, for example \(R_{ij}\approx1\).  Formula (4) then has cancellation between the tilted orthant probability and the alternating 15-term cumulant sum.  A sound implementation needs pivoted/whitened submatrices, compensated or interval accumulation, and a mixed absolute-relative error criterion.  A relative-only test is meaningless when a cumulant is near zero.

## 3. The only legal collision-renormalized source

Let \(P_{\mathcal C}\) and \(P_{\mathcal D}\) be entrywise masks for (2), and let \(\mathcal G_{r,E}^{\rm TS}\) denote the degree-`E` TensorSketch Hermite graph operator.  The proposed source is

\[
 \boxed{\quad
 S_{r,E}^{\rm M117}
 =P_{\mathcal C}S_r^{\rm exact}
  +P_{\mathcal D}\mathcal G_{r,E}^{\rm TS},\quad r=3,4.
 \quad} \tag{7}
\]

The supports are disjoint, so (7) has no collision double count.  In particular, the tempting formula

\[
 \mathcal G_{r,E}^{\rm TS}+P_{\mathcal C}S_r^{\rm exact}
\]

is wrong: it adds the finite-degree collision graphs to the exact collision value.  Replacing it by `graph + exact collision - unsketched finite collision` is also wrong when the graph uses TensorSketch: the sketched collision contribution is not the unsketched finite graph contribution.  It must be removed in the same operator that created it.

For `k4` under the pair flattening `(i,j)|(k,l)`, the all-distinct mask is not a left mask times a right mask.  Its exact inclusion-exclusion identity is

\[
 {\bf1}\{i,j,k,l\ \hbox{all distinct}\}
 =\sum_{\nu\in\Pi_4}\mu(\hat0,\nu)
   \prod_{B\in\nu}{\bf1}\{i_a=i_b\ \forall a,b\in B\},\qquad
 \mu(\hat0,\nu)=(-1)^{4-|\nu|}\prod_{B\in\nu}(|B|-1)!. \tag{8}
\]

There are 15 terms.  A cross equality such as `i=k` destroys the simple `A(ij,:) B(kl,:)^T` separability: applying it to a block `Q` requires contractions such as

\[
 [E_{i=k}(AB^T)Q]_{ij}
 =A_{ij,:}\sum_l B_{il,:}Q_{il,:}. \tag{9}
\]

It can be evaluated without forming an \(n^4\) tensor, but it is another structured action, not a free postprocessing mask.  Projecting only after a rank-four range compression is invalid: the projection generally raises pair rank and leaks sketched collision mass back into the result.

The analogous `k3` mask has the three pair equalities and is cheaper.  It does not cure the `k4` obstruction.

## 4. What convergence improves—and what it cannot improve

Equation (7) removes every graph whose bad correlation arose solely from two equal external labels.  That is a real resummation, not a heuristic: the collision value is replaced by its exact truncated-Gaussian cumulant.

It does **not** establish a tail bound for all-distinct tuples.  Distinct normalized rows can be almost collinear, so `R_ij` can be arbitrarily close to one.  Nor does a small average coherence help a uniform Hermite tail.  Thus the observed 74.352640882204292-times-gate degree drift is consistent with the collision hypothesis but does not diagnose it.

A raw threshold \(|R_{ij}|>\tau\) is not by itself a convergence theorem.  For four weak scalar axes it only gives the crude Gershgorin condition

\[
 \lVert R_I-I\rVert_{\rm op}\le3\tau. \tag{10}
\]

After strong axes are grouped, the relevant perturbation is instead block-whitened coherence

\[
 \gamma=\left\|B^{-1/2}(R-B)B^{-1/2}\right\|_{\rm op},\qquad
 B=\operatorname{blockdiag}(R_{C_1},\ldots,R_{C_s}). \tag{11}
\]

Near-singular internal blocks make a raw-edge bound insufficient.  A legitimate polymer Taylor/Price expansion needs a predeclared \(\gamma<1\) domain and a computable remainder majorant.  Smoothness under positive-definite covariance, supplied by the generalized Price theorem, is not a numerical tail certificate.  A degree-16/18 difference is only a falsification statistic, never a proof that all higher degrees are small.

A strict future proposal must therefore provide one of the following before calling a weak tail controlled:

* an explicit, evaluated absolute multigraph majorant for every omitted degree; or
* a proved analytic-radius/Cauchy enclosure derived from a frozen block-whitened norm and a finite derivative bound.

No such bound is presently supplied.  This alone prevents an IMPLEMENT verdict even if the arithmetic ledger were favorable.

## 5. Optional strong-correlation polymer extension

There is a coherent extension, but it reinforces the KILL verdict on cost.

Freeze `tau` before inspecting any source error.  On distinct coordinates make a graph `H_tau` with an edge when \(|R_{ij}|>\tau\), and let its connected components be the polymers.  For an all-distinct external tuple, classify it canonically as:

1. **weak** if its selected axes lie in different polymers;
2. **strong** otherwise.

For a strong tuple, retain its within-polymer covariance exactly and expand only cross-polymer covariance.  At zero cross covariance, each polymer is an independent Gaussian block; connected polymer diagrams then join blocks using only cross-block edges.  This is the correct resummation idea: internal edges never reappear in the weak graph series.  Collision tuples remain outside this classification and are handled first by (7).

The three sets—collision, all-distinct strong, all-distinct weak—are disjoint and exhaustive.  That classifier, together with either an exact four-axis strong value or a specified polymer expansion, is required to avoid double counting.  A phrase such as “add strong clusters” without a tuple ownership rule is not a mathematical algorithm.

There is no universal small-cluster theorem.  Positive semidefiniteness allows the full-rank equicorrelation family

\[
R=(1-c)I+c\,11^T\quad(0<c<1), \tag{12}
\]

whose threshold graph has a component of all 256 vertices for every `tau<c`.  A connected-component rule therefore cannot claim bounded cost from `d=256` alone.

To make the extension legal, a configuration must freeze a component cap `b_max`, a threshold, and a whitened-cross-block gate such as (11); it must **KILL**, not relax thresholds, whenever a cap or norm gate fails.  If `b_c<=b_max`, a direct enumeration bound for all-distinct tuples containing at least one within-component pair is

\[
 N_{\rm strong}\ \le\ 6\sum_c(b_c)_2(n-2)_2
 \ \le\ 6(b_{\max}-1)n(n-2)(n-3)=O(b_{\max}n^3). \tag{13}
\]

This is an upper bound with repeated counting, suitable for a conservative bill.  Even `b_max=2` is about a collision-sized `O(n^3)` workload.  Exact strong values can require four-dimensional truncated moments; the at-most-trivariate simplification belongs only to equality collisions.

## 6. 272B arithmetic ledger

This is deliberately the favorable M113 formation configuration already specified elsewhere: rank 4, oversampling 8 (`q=12`), TensorSketch width `m=32`, general-threshold graph cutoff `E=3`, 32 activation vertices, and two-sided range finding.  The independently corrected source count is 30 graph-action equivalents, not the earlier uncharged shortcut.

For one graph action the two dense contractions cost

\[
 32\cdot12(2\cdot256^2-1)+256^2\cdot12(2\cdot32-1)
 =99{,}876{,}480\ \text{FLOPs}. \tag{14}
\]

The known, still-incomplete M113 subtotal is:

| charged item | FLOPs |
|---|---:|
| two-sided `k3/k4` graph range actions | 191.762841600B |
| TensorSketch/feature construction | 17.448304640B |
| Gaussian covariance affine transport | 2.080000000B |
| signed rank-4 `k4` affine transport | 16.640000000B |
| symmetric rank-4 `k3` affine transport | 8.320000000B |
| **known subtotal** | **236.251146240B** |
| nominal 272B headroom | **35.748853760B** |

Now charge only the unavoidable sparse scatter/FMA actions for the exact strata.  Treating one multiply-accumulate as two FLOPs, a `k4` collision action on `q=12` vectors costs at least

\[
 2N_{4,\rm coll}q=2.398654464\text{B};
\]

the `k3` analogue costs 0.004706304B.  Two sides across 32 vertices give

| new collision item | FLOPs |
|---|---:|
| `k4` exact sparse actions | 153.513885696B |
| `k3` exact sparse actions | 0.301203456B |
| **collision-action lower bound** | **153.815089152B** |
| **favorable total: known subtotal plus lower bound** | **390.066235392B** |
| **overflow before masking and responses** | **118.066235392B** |

This is a lower bound favorable to M117: it gives the all-distinct masked sketch the same cost as the unmasked M113 action, charges no truncated-normal evaluation, no construction/storage of collision values, no mask action, no compression, and no response.  It already fails.

An explicit inclusion-exclusion realization of (8) can require up to 15 structured factor actions per graph term.  Multiplying the existing graph range line by 15 gives 2,876.442624B before adding exact collisions.  That is an implementable conservative schedule, not a proven lower bound—some contractions might share intermediates—but no such sharing is presently specified and it may not be silently treated as free.

Reducing to `q=4` would remove the oversampling/range-capture protection and is not a rescue.  Even if its raw formation arithmetic were accepted, it has no certified capture for an unknown-rank source, does not implement the all-distinct mask, and leaves all Price responses and numerical certificates unbilled.  A post-hoc choice of `q`, `m`, rank, threshold, or source degree after a failure would be a different candidate, not M117.

### Memory and residual wall

The canonical `aabc` table with the repeated label distinguished and the other two unordered has

\[
 n\binom{n-1}{2}=8{,}290{,}560
\]

f64 values: 63.25 MiB before moment-workspace and indices.  The fully expanded collision pair matrix contains 99,943,936 f64 values, 0.74464 GiB before sparse indices.  Streaming avoids the full matrix but produces irregular gathers from `Q` and scatter-adds to the output; its 2.4B-FLOP action is not a dense-GEMM wall-clock promise.  It is likely more bandwidth/allocator sensitive than the dense sketch contractions.  No residual or peak-memory measurement exists here, so no “fits in time” inference is allowed.

## 7. Propagation, response, and observability failures

M117 changes neither of the following facts.

First, the exact Price/characteristic-function response contains `3->3`, `3->4`, `4->3`, `4->4`, and `r=1,2` covariance/mean channels.  Repeated incoming slices such as `K4[i,i,j,k]` contribute even to distinct exposed output slots.  The direct-leg rule retains only one response term.  Conditional-cumulant identities do not make the omitted terms vanish merely because a source has a structured representation; see [Brillinger (1969)](https://doi.org/10.1007/BF02532246).

Second, collision sparsity is not invariant under an affine layer.  For example,

\[
 [W^{\otimes4}K^{\rm aabc}]_{abcd}
 =\sum_{i,j,k}W_{ai}W_{bi}W_{cj}W_{dk}K_{iijk}^{\rm aabc}, \tag{15}
\]

which is generally dense for all-distinct \((a,b,c,d)\).  An exact local collision table must therefore be range-compressed before transport, and no rank-four capture theorem follows from its sparse origin.  The same issue applies to strong polymers.

The rank/capture target must be imposed on the **full** M117 source after exact collision insertion and symmetry restoration, not on the all-distinct sketch alone.  Otherwise a source whose difficult energy lies in `aabc` can appear to have a good weak-bulk range while the actual `k4` is missed.

Consequently this construction supplies neither a closed recurrence nor final `k3/k4`.  It also leaves the known covariance-baseline/residual issue untouched: changing `r=1,2` changes the next `m,C`, which changes every later Gaussian source.

## 8. Symmetry and invariance audit

| issue | required treatment | failure mode if omitted |
|---|---|---|
| slot permutation | compute canonical strata but scatter all 3/6/4/etc. slot orbits, then symmetrize before rank truncation | a single `aabc` placement is not a symmetric `k4` |
| hidden permutation | equality partitions, `R`, threshold graph, and collision tables are equivariant | a fixed index-hash sketch is only permutation-equivariant in distribution |
| positive ReLU gauge | standardize by `s_i`, compress standardized cumulants, then restore \(\prod s_i\) | raw Frobenius compression changes under a legal positive hidden-unit rescaling |
| pair swap | use a signed symmetric pair-unfolding and apply the same support masks to both orientations | neither a graph factor nor a sparse orientation is automatically PSD/symmetric |
| sketch frame | transform a declared sketch frame covariantly with a hidden permutation, or make only a distributional claim | a frozen ordinary CountSketch breaks pointwise equivariance |
| cluster threshold | freeze `tau`, tie convention, cap, and whitening gate before source diagnostics | tuning clusters to a source residual is oracle laundering |

No negative-rescaling invariance is claimed; ReLU does not have that gauge.  The TensorSketch limitation is standard: it approximates a polynomial-kernel feature map, not an exact masked operator or a rank certificate; see [Pham and Pagh (2013)](https://doi.org/10.1145/2487575.2487591).  Likewise, matrix-free randomized range finding only estimates a range from actions; it cannot assume rank-four capture ([Halko, Martinsson, and Tropp (2009)](https://arxiv.org/abs/0909.4061)).

## 9. Cheapest strict target-free falsifier

The cheapest falsifier is arithmetic, requires no fixed evaluation network, and is predeclared completely:

> Freeze `n=d=256`, `L=32`, `r=4`, rank 4, oversampling 8 (`q=12`), `m=32`, `E=3`, f64, two-sided range finding, exact `k3/k4` collision actions, and the 30-action graph ledger.  Accept M117 for further testing only if the sum of the existing known subtotal and the unavoidable sparse collision FMA lower bound is at most 272B.

The gate evaluates to 390.066235392B and therefore **fails**.  It is target-free, deterministic, and stricter than a wall-time guess.  Do not execute a source test, retune a parameter, or reinterpret “sparse” after this failure.

For completeness, a new, separately named repair candidate that first clears that budget gate would have to freeze all of the following *before* running one local generated-only experiment:

1. Generate one iid-He `12 x 12` first-layer matrix from a declared seed; set `m=0`, construct and normalize its Gaussian covariance.  This is exactly Gaussian and uses no input sampling.
2. Materialize the harmless `144 x 144` `k4` pair unfolding.  Validate every collision entry from (4)--(6) against an independent low-dimensional deterministic/interval quadrature, with a predeclared absolute-plus-relative tolerance.
3. Form (7) with the mask applied inside the action.  Require exact support separation, slot symmetry, a coupled hidden permutation, and a positive-gauge test; no component may be retuned.
4. Compare degree 16 and 18 only on the all-distinct weak source and on the full stratified source.  Require the frozen relative drift `<=0.05`; label this a falsifier statistic, not a tail theorem.  Separately require the predeclared absolute graph-tail majorant or analytic enclosure described in section 4.
5. On the full stratified `k3/k4` sources, require best rank-four pair energy at least 0.80 and the specified masked/sketched two-sided range to capture at least 0.95 of that energy.  Test the full source, not just the weak remainder.
6. At `n=256`, test the frozen cluster cap and block-whitened norm without looking at a target.  Any cap/norm/budget/symmetry/tail/capture failure is **KILL** for that configuration; changing a threshold, seed, rank, sketch width, degree, or compression norm begins a new candidate.

Those later gates are intentionally not run: the predeclared arithmetic gate has already killed this configuration, and running them would not repair the lack of budget or propagation closure.

## Source ledger and boundary of claims

The cited sources are primary research sources only:

* R. Price, *A Useful Theorem for Nonlinear Devices Having Gaussian Inputs* (1958), [DOI](https://doi.org/10.1109/TIT.1958.1057444): Gaussian covariance-derivative identity.
* F. Voigtlaender, *A General Version of Price's Theorem* (2017), [arXiv:1710.03576](https://arxiv.org/abs/1710.03576): rigorous multivariate/distributional formulation.
* G. M. Tallis, *The Moment Generating Function of the Truncated Multi-Normal Distribution* (1961), [DOI](https://doi.org/10.1111/j.2517-6161.1961.tb00408.x): truncated-normal MGF basis for (4).
* D. R. Brillinger, *The Calculation of Cumulants via Conditioning* (1969), [DOI](https://doi.org/10.1007/BF02532246): conditional-cumulant partition warning.
* N. Pham and R. Pagh, *Fast and Scalable Polynomial Kernels via Explicit Feature Maps* (2013), [DOI](https://doi.org/10.1145/2487575.2487591): TensorSketch's limited feature-map role.
* N. Halko, P.-G. Martinsson, and J. A. Tropp, *Finding Structure with Randomness: Probabilistic Algorithms for Constructing Approximate Matrix Decompositions* (2009), [arXiv:0909.4061](https://arxiv.org/abs/0909.4061): action-based range finding, not rank creation.

Everything specific to equality masks, costs, cluster legality, and the KILL decision above is a derivation from the stated model and accounting convention.  The sources do not certify a deep fixed-ReLU Gaussian closure, a Hermite tail at near-collinear distinct axes, rank-four observability, a response truncation, a 272B fit, or a final error.
