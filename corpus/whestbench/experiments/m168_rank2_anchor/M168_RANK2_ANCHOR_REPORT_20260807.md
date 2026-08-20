# M168: transverse rank-two anchor for the connected `[2,1,1]` defect

## Disposition

**SCREENED TRANSVERSE-RANK-TWO ANCHOR AND ONE-SIDED CONE-TANGENT SURVIVOR; KILL ANY CLAIM OF A GENERIC ALL-PSD, ERROR-CERTIFIED, `606,720`-BILLED PROVIDER.**

M168 closes the precise M165 gap at a positive-marginal rank-two face: it
derives the face value `Delta_211` and its Price/coarea directional
coefficient directly on the two-dimensional Gaussian support plane. It is a
high-precision, response-free reference only: no interval error certificate,
fixed-node accuracy proof, native cost trace, endpoint, or provider dispatch
is supplied.

## Canonical plane and wedge anchor

Let `Sigma=L L^T` have rank two, with `L` of shape `3 x 2`, and write
`X=mu+LZ`, `Z~N(0,I_2)`. M168 accepts exactly

\[
 \|L_i\|>0,\qquad \det\begin{pmatrix}L_i\\L_j\end{pmatrix}\ne0\quad(i\ne j).
\]

Every coordinate kink is then a line in the canonical factor plane, and each
pair crosses transversely. An orthogonal factor-plane rotation writes
`Z=(u,v)` with no vertical kink. For powers `p` and an active-indicator set
`H`, the anchor primitive is

\[
 W_{p,H}=\int\phi(u)\int\phi(v)\prod_i(\mu_i+a_i u+b_i v)_+^{p_i}
 \prod_{i\in H}{\bf1}\{\mu_i+a_i u+b_i v>0\}\,dv\,du.
\]

The outer line is split at pairwise kink intersections. On each interval the
inner bounds are affine roots and the integrand is degree at most four times
`phi(v)`, evaluated from

\[
 I_0(l,r)=\Phi(r)-\Phi(l),\quad I_1(l,r)=\phi(l)-\phi(r),\quad
 I_q=l^{q-1}\phi(l)-r^{q-1}\phi(r)+(q-1)I_{q-2}.
\]

The twelve Tallis raw moments (eleven nonconstant) form the connected
cumulant by the ordinary set-partition identity; two extra univariate second
moments complete the M129 tree. M168 combines the connected object before
presenting `Delta_211=cumulant-tree`. Tallis is used only for the raw-moment
organisation; no opaque trivariate probability is differentiated.

## Correct Price/coarea tangent

For mean direction `m` and symmetric covariance direction `D`, let
`H_i={i}` when `p_i=1`, and empty otherwise. M168 uses

\[
\begin{aligned}
\dot M_p={}&\sum_i m_i p_i W_{p-e_i,H_i}\\
&+\tfrac12\sum_iD_{ii}[{\bf1}_{p_i=1}B_i(p-e_i)+{\bf1}_{p_i=2}2W_{p-2e_i,\{i\}}]\\
&+\sum_{i<j}D_{ij}p_ip_jW_{p-e_i-e_j,H_i\cup H_j},
\end{aligned}
\]

with coarea kink-boundary integral

\[
B_i(q)={\phi(\mu_i/\|L_i\|)\over\|L_i\|}
\int\phi(t)\prod_{j\ne i}(A_{ij}+C_{ij}t)_+^{q_j}\,dt.
\]

This remaining integral also has finite exact normal-interval pieces. The
activity indicators are essential: replacing the `p_i=2` diagonal term by an
unconstrained zeroth raw moment is false. A rank-preserving finite difference
falsified that tempting form; the indicator-weighted expression above passed.

Price is justified by taking the dominated transverse-plane limit of its SPD
identity under one-sided PSD regularisation. Positive marginals make each
single-kink density finite; pair transversality makes wedge changes finite.

Let `n` span `ker(Sigma)`. M168 dispatches `n^T D n>0` as a supported
one-sided opening to rank three; `n^T D n=0` as a rank-preserving/tangent-cone
direction (a normal cross component needs a stated second-order completion);
and refuses `n^T D n<0` as outward from the PSD tangent cone. This is the
rank-two `D0, DB` pair suitable for M165 subtraction on this stratum only.

## Predeclared prediction and kill gates

1. Prediction: planar Price tangent agrees with a rank-preserving
   high-precision central difference and a null-normal opening agrees with a
   one-sided, response-free M147 check. Kill at disagreement above `1e-9` or
   `5e-6`, respectively.
2. Prediction: coordinate permutation (with remapped repeated slot) and a
   positive ReLU gauge obey the exact `d_i^2 d_j d_k` covariance law. Kill on
   any high-precision discrepancy.
3. Prediction: parallel kink lines, zero marginal variance, and an outward
   normal direction refuse. Kill on any silent continuation.
4. Provider kill: without a uniform interval/mixed-error certificate and a
   native billed-operation trace, state no provider, dispatch, or cost credit.

## Generated response-free validation

The deterministic generated rank-two state used rows
`(1.2,.4),(-.35,1.1),(.8,-.9)` and mean `(.3,-.45,.65)`.

- On a rank-preserving factor/mean path, the Price tangent was
  `0.0003254967989760219...`; the high-precision central difference was
  `0.0003254967986993001...`, a disagreement below `2.8e-13`.
- Under unit null-normal opening, the tangent was `0.0541925871537440...`.
  The independent one-sided M147 difference was `0.0541912614001775...`, a
  `1.33e-6` disagreement, passing its `5e-6` gate.
- All six coordinate permutations (labels remapped) and a positive diagonal
  gauge passed value and tangent covariance checks.
- Nontransverse, zero-marginal, and outward-cone inputs all fail closed.

Four response-free tests passed with the bundled local interpreter. M147 is
only a local cross-check; it supplies no M168 formula or provider authority.

## Cost envelope against `606,720` operations/coefficient

The structural inventory is 11 nonconstant Tallis raw moments, 2 extra
univariate tree moments, 20 indicator-weighted Price moments, and 16 coarea
boundary moments: **49 distinct primitives**. This is a primitive-count lower
bound, not a machine-operation lower bound.

For transparency only, a conservative fused bookkeeping model allows seven
wedge cells, 31 raw/indicator components per node, 256 arithmetic-equivalent
operations per cell-component, 16 three-interval boundary terms, and 4,096
setup/tree operations:

\[
C(N)=16,384+55,552N.
\]

`N=10` gives `571,904`, below the cap; `N=11` gives `627,456`, above it.
Neither number is an accuracy or native-bill claim. The M162 87-node
counterexample costs `4,849,408` under this model, but M168 makes no claim
that 87 nodes are necessary. Since it has neither a uniform error enclosure
nor native cost trace, the cost gate is killed: **zero provider/operation
credit**.

## Localised exclusions and firewall

Pair-nontransverse rank-two planes and zero-marginal faces are outside this
branch; the latter remains M159 deterministic/one-sided-conic territory.
Rank one remains M154-owned. Full-rank SPD continuation needs a separate
certified primitive. The preserved component is the rank-two anchor/tangent
only; the failed link is all-PSD endpoint/provider extension.

No network request, model response, target evaluation, truth, label, scorer,
leaderboard, submission, champion selection, fixed-rule provider, ridge,
clipping, retry, or source-variance claim was read or changed.
