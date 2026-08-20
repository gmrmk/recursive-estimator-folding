# M126 repeated-output source contraction theory -- 2026-08-07

## Decision

**Verdict: REPAIR ONLY / DO NOT PROMOTE.**  The repeated-output source is much
smaller than the full order-three and order-four tensors, but it is not an
exact generic cubic construction.  All order-three terms, every order-four
star, every `AAAB` path, the `AABB` block paths, the complete diagonal
`T4_aaaa`, and the identity part of the remaining `AABB` paths have exact
classical `O(n^3)` all-output contractions.  The off-diagonal covariance
source still contains two full-width pair-feature quadratic forms.  Both the
palindromic `ABBA/BAAB` orbit and the alternating `ABAB/BABA` orbit participate
in this obstruction; the alternating orbit is not the only hard term.

For a generic dense bridge residual, the standard exact Schur, diagonal,
Kronecker, Khatri--Rao, spectral, and dense tensor-network rearrangements all
retain either `Theta(m^2)` pair features or `Theta(n)` separable modes.  At
`m=n` their classical cost is `Theta(n^4)`.  This is a rigorous obstruction in
that contraction model, not an unconditional arithmetic-circuit lower bound
against every algorithm that could ever be invented.

There is an honest stochastic repair.  Outcome-independent Rademacher probes
give an unbiased full `m x m` table with two dense GEMMs per path probe and two
more per `[2,2]` collision probe.  The one-delay response and the M125b carrier
are linear in these source tables, so expectation is preserved if probe
selection, seeds, deflation, and every gate are frozen before any outcome is
seen.  Relative variance is nevertheless unbounded at cancellation-dominated
entries.  Cost feasibility therefore does not establish accuracy.

Two qualifications are binding.  First, the implementation and every M126
cost below use the M124 one/two-coordinate collision convention.  They omit
the exact M122 three-label `[2,1,1]`, or `aabc`, collision stratum.  That
stratum is a separate generic fourth-order contraction and is a hard blocker
to calling M126 an exact M122 source.  Second, a float32 dense-GEMM child makes
eight probes arithmetically plausible, but only under explicit mixed-precision
parity and stability gates.  It does not make the stochastic or omitted
collision error disappear.

This was a generated-algebra audit.  No contest row, truth, scorer, benchmark
outcome, champion, submission, or public dataset was read or used.

## 1. One-delay interface and notation

Let `Q` be the symmetric `n x n` bridge with `diag(Q)=1`.  Let `W` be the
effective source-to-next-layer map after the physical activation scales have
been absorbed into its rows.  Put

\[
 A=QW,
 \qquad g=\gamma_2,
 \qquad h=\gamma_3.
\]

All juxtaposed arrays of the same shape below are Hadamard products.  Thus
`gWA` means `g[:,None] * W * A`, and powers are elementwise.  The transported
sources are

\[
 T^{(3)}_{abc}=\sum_{ijk}S^{(3)}_{ijk}W_{ia}W_{jb}W_{kc},\qquad
 T^{(4)}_{abcd}=\sum_{ijkl}S^{(4)}_{ijkl}W_{ia}W_{jb}W_{kc}W_{ld}.
\]

The one-delay ReLU response needs only

\[
 T^{(3)}_{aaa},\ T^{(3)}_{aab},\ T^{(3)}_{abb},\ T^{(3)}_{bbb},
\]

and

\[
 T^{(4)}_{aaaa},\ T^{(4)}_{aaab},\ T^{(4)}_{aabb},
 T^{(4)}_{abbb},\ T^{(4)}_{bbbb}.
\]

If `K3[a,b]=T3_aab`, `K31[a,b]=T4_aaab`, and
`K22[a,b]=T4_aabb`, symmetry supplies the exchanged tables by transpose and
the fully repeated values by taking diagonals.  In particular,

\[
 \delta m_a=-{T^{(3)}_{aaa}\over6}f'_a
             +{T^{(4)}_{aaaa}\over24}f''_a.
\]

For `a != b`, writing `D_rs` for the frozen Gaussian derivative factors,

\[
\begin{aligned}
 \delta R_{ab}={1\over6}(&T^{(3)}_{aaa}D_{30}
 +3T^{(3)}_{aab}D_{21}+3T^{(3)}_{abb}D_{12}
 +T^{(3)}_{bbb}D_{03})\\
 +{1\over24}(&T^{(4)}_{aaaa}D_{40}
 +4T^{(4)}_{aaab}D_{31}+6T^{(4)}_{aabb}D_{22}
 +4T^{(4)}_{abbb}D_{13}+T^{(4)}_{bbbb}D_{04}),
\end{aligned}
\]

and `delta V_ab=delta R_ab-m_b delta m_a-m_a delta m_b`.  Therefore the
hard contraction affects the off-diagonal covariance through `T4_aabb`.
The mean source and all fully repeated bridge-tree values are cubic even when
the complete `AABB` table is not.

## 2. Complete orbit accounting

The orbit multiplicities are fixed by labelled slots before any equal output
labels are coalesced.

| family | repeated-output orbit | multiplicity |
|---|---|---:|
| `k3` tree, `AAB` | center has output `A` | 2 |
| `k3` tree, `AAB` | center has output `B` | 1 |
| `k4` star, `AAAB` | center has output `A` | 3 |
| `k4` star, `AAAB` | center has output `B` | 1 |
| `k4` star, `AABB` | center has output `A` | 2 |
| `k4` star, `AABB` | center has output `B` | 2 |
| `k4` path, `AAAB` | singleton at an endpoint | 6 |
| `k4` path, `AAAB` | singleton at an internal vertex | 6 |
| `k4` path, `AABB` | block word `AABB/BBAA` | 4 |
| `k4` path, `AABB` | palindrome `ABBA` | 2 |
| `k4` path, `AABB` | palindrome `BAAB` | 2 |
| `k4` path, `AABB` | alternating `ABAB/BABA` | 4 |

The path counts sum to the twelve labelled undirected Hamilton paths.  In the
M122 oriented path convention, `ABBA` names the `S_ba` representative and
`BAAB` names `S_ab`; their aggregate is invariant under this naming choice.

Collision slot partitions have a separate set of multiplicities:

| order | equality partition | slot multiplicity |
|---|---|---:|
| 3 | `[3]` | 1 |
| 3 | `[2,1]` | 3 |
| 4 | `[4]` | 1 |
| 4 | `[3,1]` | 4 |
| 4 | `[2,2]` | 6 |
| 4 | `[2,1,1]` | 12 |

The first five partitions are represented by the sparse M124 collision
tables used below.  The last partition needs a three-label tensor and is not
represented by those tables.

## 3. Exact cubic bridge-tree contractions

### Order three

The complete `AAB` table is

\[
 K3=2(gWA)^T A+(gA^2)^T W. \tag{1}
\]

The first term owns the two placements with an `A` center and the second owns
the one placement with a `B` center.  This is two square-GEMM equivalents
after `A=QW`.

### Order-four stars

The star tables are

\[
 K31^{\rm star}=3(hWA^2)^T A+(hA^3)^T W, \tag{2}
\]

and, with `C=(hWA)^T A^2`,

\[
 K22^{\rm star}=2(C+C^T). \tag{3}
\]

These equations carry the `3+1` and `2+2` center multiplicities exactly.

### `AAAB` paths

Define

\[
 U=gAW,\qquad V=QU.
\]

The singleton-endpoint and singleton-internal representatives give

\[
 K31^{\rm path}=6\{[A^T(gWV)]^T+[W^T(gAV)]^T\}. \tag{4}
\]

Every operation in (4) is a bridge multiplication, a Schur product, or a
square output GEMM.

### `AABB` paths and the exact boundary

For each ordered output pair define the length-`n` feature

\[
 B_{ab}=g\,A_{:a}W_{:b}.
\]

Let

\[
 P=U^TQU,\qquad
 S_{ab}=B_{ab}^TQB_{ab},\qquad
 C_{ab}=B_{ab}^TQB_{ba}. \tag{5}
\]

Then the twelve path orbits assemble as

\[
 K22^{\rm path}=4P+2(S+S^T)+4C. \tag{6}
\]

`C` is symmetric because `Q` is symmetric.  At `a=b`, all three
representatives coincide, so

\[
 K22^{\rm path}_{aa}=12\,[U^TQU]_{aa}. \tag{7}
\]

Equation (7) is an exact cubic construction of every fully repeated path
value and therefore of the bridge-tree contribution to `delta m`.

Split the central bridge as `Q=I+E`, with `diag(E)=0`.  The identity pieces of
the two hard tables collapse exactly:

\[
 S^{I}=(g^2A^2)^T W^2,\qquad C^{I}=U^TU. \tag{8}
\]

Only

\[
 S^E_{ab}=B_{ab}^TEB_{ab},\qquad
 C^E_{ab}=B_{ab}^TEB_{ba} \tag{9}
\]

remain.  There is a useful aggregate identity.  With
`D_ab=B_ab+B_ba`,

\[
 2S^E_{ab}+2S^E_{ba}+4C^E_{ab}=2D_{ab}^TED_{ab}. \tag{10}
\]

This halves bookkeeping and enforces output symmetry inside each stochastic
sample.  It does not reduce the number of pair features.

## 4. Why diagonal, Schur, and Kronecker rearrangements do not make (9) cubic

Form the pair-feature matrix

\[
 Z_{y,(a,b)}=B_{ab}(y),\qquad Z\in\mathbb R^{n\times m^2}.
\]

If `G=Z^TEZ` and `Pi(a,b)=(b,a)`, then

\[
 \operatorname{vec}(S^E)=\operatorname{diag}(G),\qquad
 \operatorname{vec}(C^E)=\operatorname{diag}(G\Pi). \tag{11}
\]

Taking a diagonal prevents the `m^2 x m^2` Gram matrix from being stored, but
it does not remove its `m^2` queries.  The equivalent rectangular
matricization is a classical `m x n^2` by `n^2 x m` multiplication.  The
underlying index graph is `K4` with only the free `a-b` edge removed; ordinary
variable elimination creates an `n^3` intermediate and performs
`Theta(n^4)` arithmetic when `m=n`.

The spectral rearrangement reaches the same boundary.  If
`E=sum_r lambda_r u_r u_r^T`, define

\[
 M_r=A^T\operatorname{diag}(g u_r)W.
\]

Then

\[
 S^E=\sum_r\lambda_r M_r\odot M_r,\qquad
 C^E=\sum_r\lambda_r M_r\odot M_r^T. \tag{12}
\]

One retained mode costs one square GEMM and supplies both tables.  A bounded
rank residual is consequently cubic, but a generic dense residual needs
`Theta(n)` modes.  More formally, the zero-diagonal symmetric residual space
has dimension `n(n-1)/2`, while the off-diagonal images of symmetric rank-`r`
matrices have dimension at most `nr-r(r-1)/2`.  A generic residual therefore
cannot be diagonal plus bounded rank; its required rank is `Theta(n)`.
Exceptional matrices can of course be cheap, and every such structural claim
must be checked rather than inferred from full rank alone.

Thus no exact `O(n^3)` diagonal/Schur/Kronecker formula for a generic dense
`ABAB` residual is available in the declared classical model.  The same is
true of the `ABBA` self table.  This is not an information-theoretic proof
against fast matrix multiplication, a new arithmetic circuit, or additional
problem-specific structure.

## 5. Exact one/two-coordinate collision contractions

Let `d3_i` be the `[3]` defect and `E3_ij` the `[2,1]` defect with `i` the
repeated coordinate.  Let `d4`, `E31`, and symmetric zero-diagonal `E22`
denote `[4]`, `[3,1]`, and `[2,2]` defects.  These are exact-minus-tree values
under the declared M124 convention.  Their repeated-output tables are

\[
\begin{aligned}
 K3^{\rm coll}={}&(d3\,W^2)^TW+(W^2)^T(E3W)
                 +2[W\odot(E3W)]^TW, \tag{13}\\
 K31^{\rm coll}={}&(d4\,W^3)^TW+(W^3)^T(E31W)
 +3[W^2\odot(E31W)]^TW+3[W\odot(E22W^2)]^TW. \tag{14}
\end{aligned}
\]

For `M=[W odot (E31W)]^T W^2`,

\[
\begin{aligned}
 K22^{\rm coll}={}&(d4\,W^2)^TW^2+2(M+M^T)
 +(W^2)^TE22W^2+H22,\\
 H22_{ab}={}&2\sum_{ij}E22_{ij}(W_{ia}W_{ib})(W_{ja}W_{jb}). \tag{15}
\end{aligned}
\]

All terms in (13)--(15) except `H22` are cubic.  If
`p_ab=W_:a odot W_:b`, then `H22_ab=2 p_ab^T E22 p_ab`, another generic
pair-feature quadratic form.  It has the same exact low-rank, sparse, and
stochastic options as (10).

## 6. The omitted exact `[2,1,1]` collision is a hard blocker

Let `Delta[i,j,k]` store the exact-minus-tree value on the multiset
`{i,i,j,k}`, symmetric in the distinct singleton labels `j,k`.  There are

\[
 n{n-1\choose2}=8,290,560
\]

canonical values at `n=256`, corresponding to `99,486,720` ordered slot
entries after the twelve placements are scattered.  For one canonical triple
its exact repeated-output contributions are

\[
\begin{aligned}
 K31_{ab}\mathrel{+}=\Delta_{ijk}\{&6W_{ia}W_{ib}W_{ja}W_{ka}
 +3W_{ia}^2W_{jb}W_{ka}+3W_{ia}^2W_{kb}W_{ja}\}, \tag{16}\\
 K22_{ab}\mathrel{+}=\Delta_{ijk}\{&2W_{ia}^2W_{jb}W_{kb}
 +2W_{ib}^2W_{ja}W_{ka}\\
 &+4W_{ia}W_{ib}(W_{ja}W_{kb}+W_{jb}W_{ka})\}. \tag{17}
\end{aligned}
\]

For fixed repeated label `i`, write `Delta_i` for the symmetric singleton
matrix and `J_i=W^T Delta_i W`.  Equations (16)--(17) can be assembled from
the `J_i`, but a straightforward exact dense schedule forms `n` such matrices
and costs two square GEMMs per `i`, or `Theta(n^4)`.  Merely observing that
the source support has `O(n^3)` tuples does not make its all-pair transport
cubic.  The small-width oracle in the companion module verifies all twelve
slots but intentionally is not a target-width algorithm.

This omission cannot be relabelled a harmless residual.  It changes
`T4_aaab`, `T4_aabb`, the diagonal `T4_aaaa`, and hence both one-delay mean
and covariance sources.  The M126 implementation, probe ledger, and float32
worksheet all return `exact_three_label_211_collision_charged=False`.

### Quadratic-jet/residual mutation

The weak-correlation three-label cumulant begins with three connected
quadratic graph banks.  In the centered equal-threshold case its universal
form is proportional to

\[
 R_{ij}R_{ik}+R_{ij}R_{jk}+R_{ik}R_{jk}. \tag{18}
\]

The first bank has star structure and its repeated contractions are cubic.
The two chain banks share algebra, but their split `AABB` placements contain a
new pair-feature form.  With `H=RW`, one representative is

\[
 \sum_{ij}R_{ij}(W_{ia}W_{ib})(W_{ja}H_{jb}), \tag{19}
\]

which is again generically quartic if evaluated exactly for all `a,b`.
Using the already available
`N_z=W^T diag(z)W`, (19) has an unbiased probe using one additional matrix
`W^T diag(Rz)H`.  Thus a quadratic-jet mutation can share the M126 probe and
cost only one additional square GEMM per probe for its hard chain part.  It
still has positive cubic work for the easy banks.

That observation is a repair route, not an attachment certificate.  Dropping
the cubic-and-higher remainder of the exact three-label vertex is biased.
Keeping exact expectation requires either a certified fail-closed remainder
bound on a predeclared weak domain, an exact residual action oracle, or an
unbiased residual estimator.  Horvitz--Thompson sampling of canonical triples
is unbiased and each sampled triple needs five output outer-product updates
to form both (16) and (17), about `10m^2` base operations.  With `k=kappa n`
sampled triples per layer this is `10 kappa n^3`, but the uniform inclusion
probability is only about `2kappa/n^2`; without a proved jet residual bound its
variance is prohibitive.  Strong triples and the nonzero-mean local
coefficients also need a separately certified branch.

At float32 and eight shared probes, even the favorable one-extra-GEMM chain
attachment adds `10.381557760B` protected operations.  It raises the
M126-plus-M125b worksheet from `94.490251600B` to `104.871809360B` before the
easy jet, exact coefficient construction, higher residual, or its variance
audit is charged.  The direct exact dense `J_i` schedule would add about
`664.419696640B` in float32, or twice that in float64.  The missing stratum is
therefore a binding blocker under the approximately `100B` child envelope.

## 7. Unbiased path and `[2,2]` probes

Let `z` be an outcome-independent Rademacher or standard Gaussian vector with
`E[zz^T]=I`.  Define

\[
 M_z=A^T\operatorname{diag}(gz)W,\qquad
 M_{Ez}=A^T\operatorname{diag}(gEz)W. \tag{20}
\]

Entrywise,

\[
 E[M_z\odot M_{Ez}]=S^E,qquad
 E[M_z\odot M_{Ez}^T]=C^E. \tag{21}
\]

An exactly symmetric sample of the complete hard path aggregate is

\[
 2(M_z+M_z^T)\odot(M_{Ez}+M_{Ez}^T). \tag{22}
\]

Only the two matrices in (20) require square GEMMs.  For the collision term,

\[
 N_z=W^T\operatorname{diag}(z)W,\qquad
 N_{22,z}=W^T\operatorname{diag}(E22z)W, \tag{23}
\]

and `2 N_z odot N_{22,z}` is unbiased for `H22`.  Equations (20) and (23) therefore
use four square GEMMs per shared probe.

For independent Rademacher coordinates and fixed vectors `u,v`,

\[
 \operatorname{Var}[(u^Tz)(v^Tz)]
 =\|u\|^2\|v\|^2+(u^Tv)^2-2\sum_i u_i^2v_i^2. \tag{24}
\]

The variance divides by `P` for `P` independent probes.  Equation (24) is
exact, not an asymptotic bound.  The path aggregate uses `u=D_ab` and
`v=ED_ab` with an overall factor two, so its variance is four times (24).
The collision table uses `u=p_ab`, `v=E22 p_ab` and the same factor.  Shared
probes correlate entries and the two tables; a response-level variance
certificate must propagate those covariances or estimate the complete frozen
linear functional.  Entrywise relative error has no finite uniform bound
when the exact quadratic form is near zero.

No finite `P<n` probe family is a universal exact replacement.  If a fixed
probe matrix `Zp` is to recover every bilinear form by averaging, it needs
`Zp Zp^T/P=I`; rank then requires `P>=n`.  Orthogonal probes can make the
scheme exact at `P=n`, but this restores `Theta(n^4)` work.  Clipping,
retrying seeds, accepting a probe count after inspecting its result, or
selecting a realization by final performance destroys the declared unbiased
experiment.

## 8. Deflation and low-rank residuals

If a bounded-rank factorization is supplied, (12) is exact.  The collision
analogue is

\[
 E22=\sum_s\mu_s v_sv_s^T,\qquad
 L_s=W^T\operatorname{diag}(v_s)W,qquad
 H22=2\sum_s\mu_s L_s\odot L_s. \tag{25}
\]

With `r_Q+r_22=rSigma`, supplied factors cost `rSigma` square GEMMs per layer
after the bridge transport.  At width 256 and 31 layers, the protected
float64 costs for transport plus modes are:

| `rSigma` | protected transport-plus-mode bill |
|---:|---:|
| 4 | 12.976947200B |
| 8 | 23.358504960B |
| 16 | 44.121620480B |
| 32 | 85.647851520B |

These are component costs before the other exact tree/collision formulas and
reserves.  Under the inherited convention, discovering two dense symmetric
factorizations adds twenty square-equivalent calls per layer, or
`51.907788800B` protected in float64.  Full ranks are exact but quartic.

Truncation without a residual estimator is biased.  If `R` is the discarded
path residual,

\[
 |B_{ab}^TRB_{ab}|\le\|R\|_2\|B_{ab}\|^2,\qquad
 |B_{ab}^TRB_{ba}|\le\|R\|_2\|B_{ab}\|\|B_{ba}\|. \tag{26}
\]

The `[2,2]` error is bounded by
`2 ||R22||_2 ||p_ab||^2`.  These are absolute bounds; they do not turn into
relative guarantees near cancellation.

Deflation plus residual probing is stronger.  Retain any deterministic modes
exactly, set the probed operator to the algebraic remainder, and apply
(20)--(23) to that remainder.  The sum stays unbiased.  If `r` modes are
retained from each of the two operators, deflation costs `2r` GEMMs per layer,
whereas one extra full probe costs four.  Exact top-absolute-eigenvalue modes
minimize standard residual norms, but they do not universally minimize every
indefinite output quadratic-form variance.  At equal cost, deflation dominates
an extra probe only if the predeclared aggregate variance of the deflated
remainder is no larger than the `P/(P+1)` fraction achieved by adding that
probe.  Factor discovery and certification must be included.  With no
currently free factorization, the twenty-call discovery charge removes this
option from the approximately `100B` float32 child.

## 9. Honest source sparsification

There is an unbiased edge-sampling mechanism, but it must be applied only to
the remaining central residual after `A=QW` has been computed from the exact
bridge.  For a symmetric residual edge `e`, replace its coefficient `q_e` by
`xi_e q_e/p_e`, where `xi_e` is Bernoulli with inclusion probability `p_e`.
The hard tables are linear in that central edge, so this is
Horvitz--Thompson unbiased.  Sketching `Q` before all three path factors and
reusing the same sketch is not unbiased because the same random edge then
appears in products.

If `F_e` is the complete orbit-weighted output matrix contributed by edge
`e`, independent edge sampling has exact Frobenius mean-square error

\[
 E\|\widehat T-T\|_F^2
 =\sum_e {1-p_e\over p_e}q_e^2\|F_e\|_F^2. \tag{27}
\]

For a fixed expected edge budget, the variance-minimizing probabilities are
`p_e=min(1,c |q_e| ||F_e||_F)`, with `c` chosen to meet the budget.  Every
weight and probability must depend only on generated algebra and be frozen
before outcomes.

A sampled path-residual edge expands to four rank-one output accumulations;
a sampled `E22` edge uses one.  For `k_Q` and `k_22` sampled symmetric edges,
the raw outer-product work is approximately

\[
 2m^2(4k_Q+k_{22}). \tag{28}
\]

At `m=n`, `k_Q=k_22=kappa n`, 31 layers, float64 billing, and one `1.25`
factor, (28) is about `13.0 kappa B`, in addition to the exact easy source.
For `kappa=4`, only about 3.1% of the possible edges are retained and the
uniform variance inflation is about 32 before cancellation.  Deterministic
thresholding is biased.  The `[2,1,1]` tuple sampler in Section 6 is a
separate, substantially sparser problem and cannot be hidden in this edge
ledger.

## 10. FlopScope ledger and the float32 child

The installed dense multiplication convention is

\[
 M(a,b,c)=2abc-ac.
\]

At `n=256`, one square call is `33,488,896` base operations.  FlopScope bills
it as `66,977,792` in float64 and `33,488,896` in float32.  The static M126
schedule has twelve exact cubic tree calls and twelve exact cubic
one/two-coordinate collision calls per layer:

| exact block | square-call equivalents per layer |
|---|---:|
| bridge transport | 1 |
| `k3` tree | 2 |
| `k4` stars | 3 |
| `AAAB` paths and `AABB` block | 4 |
| identity part of hard paths | 2 |
| `k3` sparse collisions | 3 |
| `k4` diagonal collisions | 2 |
| `[3,1]` collisions | 4 |
| nonhard `[2,2]` collisions | 3 |
| **total** | **24** |

Each probe adds two path and two `[2,2]` calls.  Keeping the inherited raw
reserves unchanged at `4.0B` for analytic collision scalars, `1.6B` for the
one-delay response, and `1.6B` for copies/allocation, the protected worksheet
is

\[
 C_{\rm source}(P,d)=1.25\{31(24+4P)M_d+7.2\text{ B}\}. \tag{29}
\]

This is a conservative static envelope, not a native trace.  It includes no
exact `[2,1,1]` correction and no carrier.

| probes `P` | float64 protected source | float32 protected source | float32 source + protected M125b |
|---:|---:|---:|---:|
| 0 | 71.289346560B | 40.144673280B | 52.964020560B |
| 2 | 92.052462080B | 50.526231040B | 63.345578320B |
| 4 | 112.815577600B | 60.907788800B | 73.727136080B |
| 8 | 154.341808640B | 81.670904320B | 94.490251600B |
| 9 | 164.723366400B | 86.861683200B | 99.681030480B |
| 10 | 175.104924160B | 92.052462080B | 104.871809360B |

The M125b number `12.819347280B` includes its protected carrier and Gaussian
background.  `P=9` leaves only `0.318969520B` below a nominal `100B` line,
which is not material headroom.  `P=8` leaves `5.509748400B` and is the only
plausible predeclared float32 child in this neighborhood.  It is still an
unvalidated stochastic source, and Section 6 shows that attaching even the
favorable quadratic-jet chain for the missing three-label collision consumes
that headroom.

### Required mixed-precision gates

The float32 child may be considered only as a new, frozen mechanism.  It may
not be substituted after an outcome or after a float64 budget failure.  The
following generated-only gates are required before any activation:

1. Dense calls must use true IEEE binary32 inputs and accumulation with TF32
   and reduced-mantissa modes disabled.  Rademacher signs are exact.  Form
   `E` by explicitly zeroing its diagonal before casting rather than by a
   cancellation-prone float32 subtraction `Q-I`.
2. Compute analytic bridge/collision coefficients and one-delay scalar
   response factors in float64.  Cast only the dense-GEMM operands; promote
   every probe matrix immediately and accumulate probes and orbit sums in
   float64 with pairwise or compensated summation.  This keeps the ledger's
   unchanged scalar reserves honest.
3. With `u32=2^-24` and `gamma_n=n*u32/(1-n*u32)`, each generated GEMM must
   pass the componentwise backward-error gate
   `|C32-C64| <= 4 gamma_n (|X|^T |Y|) + tiny` against a same-input float64
   oracle.  A relative-only gate is invalid where the exact entry cancels.
4. The assembled `K3`, `K31`, `K22`, `delta m`, and `delta V` must pass frozen
   absolute-envelope and Frobenius parity gates against the same-probe
   float64 algebra.  Check exact output symmetry after the explicit
   symmetrization, positive-gauge/permutation covariance, finiteness, and
   deterministic seed replay.  Any condition, variance, or parity gate whose
   pass/fail status differs between precisions fails closed.
5. Probe count, deflation rank, seeds, dtype, accumulation order, and all
   tolerances must be hash-locked before the generated parity run.  No seed
   retry, clipping, precision fallback selected from final performance, or
   tolerance retuning is allowed.

Float32 expectation is exact only for the rounded float32 algebra.  Relative
to the intended float64 source it introduces deterministic rounding bias;
the parity gates, not the word "unbiased", control that difference.

## 11. Generated tests and boundaries of evidence

The companion test was written before its implementation import and first
failed with `ModuleNotFoundError`.  Two later additions were also observed
red before implementation: the symmetric hard-path assembly and the exact
three-label twelve-slot oracle.  The final generated suite runs eight tests.
It checks:

1. every orbit multiplicity;
2. all exact tree tables against independently materialized `S3/S4` tensors
   at widths 2 through 5;
3. all M124 sparse collision tables against dense transport;
4. the omitted `[2,1,1]` twelve-slot formulas against a dense tensor oracle;
5. exhaustive averaging over all Rademacher sign vectors at width 4;
6. exact recovery from full symmetric eigendecompositions;
7. the closed Rademacher variance formula;
8. hidden-coordinate permutation covariance and both float64/float32 static
   FlopScope ledgers.

These tests prove the displayed finite-dimensional identities to their stated
tolerances.  They do not prove target-width runtime, stochastic accuracy,
float32 parity, a three-label compression, response efficacy, or final-network
performance.

## Final disposition

Preserve the exact cubic contractions and the symmetric Rademacher estimator
as a source component.  Do not describe it as an exact full-width M122 source
and do not promote a probe count merely because it fits a worksheet.  A valid
next mutation must choose one of two explicit contracts:

* remain on the M124 one/two-coordinate source definition, freeze `P=8` as a
  new float32 stochastic child, and pass the mixed-precision and complete
  response-variance gates; or
* restore the exact M122 `[2,1,1]` ownership with a fully billed quadratic-jet
  plus certified residual mechanism, including its new pair-feature probe and
  strong-triple branch.

Until one of those contracts is independently implemented, tested, and
hash-locked, the correct status is **REPAIR / BLOCKED**, not IMPLEMENT.
