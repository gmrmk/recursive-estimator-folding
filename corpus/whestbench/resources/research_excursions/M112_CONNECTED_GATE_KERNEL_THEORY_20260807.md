# M112: connected gate-pair covariance-kernel control

**Scope.** This is a theory, resource, and generated-only-premise design.
It neither reads contest instances nor runs a forward, changes a champion, or
chooses a threshold from an outcome.  All numerical dimensions below use the
stated (d=n=256).  The proposed mutation is deliberately an **L1-only**
candidate: its proof needs independently drawn Haar frames.

## BLOCK repair: fixed-bank claim retracted

This repair supersedes every unqualified unbiasedness or continuation claim
below. The existing M111 bank uses frame seeds
`sha256("m111:<weight_seed>:<frame_index>")`. Conditional on its generated
weight seed, every held frame is therefore fixed; there is no remaining Haar
randomness with which to justify equations (1), (2), or (5). Recomputing the
same deterministic frames in float64 binds an association, but cannot restore
statistical independence. M112 reuse is only a deterministic generated-bank
association diagnostic and makes **no exact conditional-zero or
conditional-unbiasedness claim for that fixed bank**.

The theorem in Sections 1–2 remains valid only for an ideal experiment whose
frame roots are statistically generated independently of all weight roots and
whose whole frames are independently randomized. Any favorable diagnostic
requires a separately specified and frozen **M112b** using fresh independent
frame roots; it does not authorize outer blocks under the old hash namespace.

## Verdict

Under the ideal independent-frame law, M112 is a possible repair of M111's
*information* failure: instead of
pretending that an ungated product supplies the missing connected tensor
(B), it regressively learns the part of that tensor that is visible through
independent frame fluctuations of the actual output. The raw linear kernel
has an exact conditional-zero held control under ideal independent-frame
cross-fitting, but not for the deterministic M111 reuse bank.

That is a validity result, not an efficacy result.  The frame operation
removes the constant, odd, and degree-two parts before learning begins;
M112 consequently cannot rescue M111's leading degree-two overlap.  With at
most 40 training frames, its learned tensor has rank at most 40 inside a
(32,640)-dimensional symmetric off-diagonal gate-pair space.  It can still
overfit exactly as M107/M110 did.  **Disposition: generated-only premise
candidate, not a champion mutation.**

## 1. Exact object and ideal-law theorem

Let (A=[a_1,ldots,a_n]), with (a_i=W_1[:,i]/\|W_1[:,i]\|_2).  Assume
all first-layer columns are nonzero; a zero column must close the static gate
or be removed by a separately specified dimension-changing construction.
For Haar frame (Q_r=(q_{r1},ldots,q_{rd})), define

\[
 V_r[b,i]={\bf1}\{q_{rb}^{\mathsf T}a_i>0\}-\tfrac12,
 \qquad
 \Sigma_{ik}=\frac{\arcsin(a_i^{\mathsf T}a_k)}{2\pi},
\]

\[
 C_r=\frac1dV_r^{\mathsf T}V_r-\Sigma,
 \qquad K_{rs}=\langle C_r,C_s\rangle_F.
\]

Every individual frame direction is uniform on (S^{d-1}).  The bivariate
Gaussian/spherical sign identity gives

\[
 E_Q[V_i(Q)V_k(Q)\mid W]=\Sigma_{ik},
 \quad\text{hence}\quad E[C_r\mid W]=0. \tag{1}
\]

This is exact for a newly randomized Haar frame independent of the weights,
including off diagonal entries. It is not a statement about averaging over
the single fixed hash-derived bank. On the diagonal,

\[
 (V_i)^2=\tfrac14=\Sigma_{ii},
\]

so (C_{r,ii}=0) **for every frame**, not just in expectation.  In real
arithmetic the strict boundary convention is irrelevant because a nonzero
gate hyperplane has Haar measure zero.  A numerical implementation must
calculate in float64, explicitly set the diagonal to zero, and only clamp
dot products to ([-1,1]) to repair documented roundoff excursions.

The kernel is positive semidefinite because it is the Gram kernel of the
matrices (C_r). More importantly, for fixed training frames and a genuinely
independent held Haar frame,

\[
 E[K_{h,s}\mid W,\{C_t:t\in T\}]
 =\langle E[C_h\mid W],C_s\rangle_F=0. \tag{2}
\]

Equation (2), rather than generic kernel-machine folklore, is the entire
reason the held prediction can be used as a control variate.

## 2. Ideal-law cross-fitted estimator and exact unbiasedness

Let (Y_{r,o}) be the existing per-output block mean for frame (r), with
the exact same antipodal/radialization treatment as the base L1 estimator.
For a (K)-fold partition of (R) *independent* Haar frames, let (T_f)
be the training frames for fold (f).  Freeze a ridge rule before any
generated forward:

\[
 \lambda_f=10^{-3}\,\operatorname{tr}(K_{T_fT_f})/|T_f|,
 \qquad
 \alpha^{(o)}_f=(K_{T_fT_f}+\lambda_f I)^{-1}
 \bigl(Y_{T_f,o}-\bar Y_{T_f,o}{\bf1}\bigr), \tag{3}
\]

with the stipulated all-zero prediction when the trace is zero.  The numeric
factor is a frozen definition, not a parameter to sweep.  Centering the
**training response** in (3) is allowed: it only changes a training-measurable
coefficient.  There is no fitted intercept and no centering of held kernel
rows.  For (h\in f), set

\[
 c_{h,o}=K_{h,T_f}\alpha^{(o)}_f,
 \qquad \widehat\mu_o=\frac1R\sum_{f=1}^K\sum_{h\in f}(Y_{h,o}-c_{h,o}). \tag{4}
\]

Let \(\mathcal F_f\) contain the weights and every frame/output in
(T_f).  Then \(\alpha_f^{(o)}\) is \(\mathcal F_f\)-measurable, while
each held frame is independent of it.  From (2),

\[
 E[c_{h,o}\mid\mathcal F_f]=0,
 \qquad E[Y_{h,o}-c_{h,o}\mid\mathcal F_f]=\mu_o(W). \tag{5}
\]

Summing (5) proves (E[\widehat\mu_o\mid W]=\mu_o(W)) exactly **only under
the ideal independent-frame sampling law**. In the fixed M111 bank the held
frame is a deterministic function of the weight seed, so the independence
premise fails and this conclusion is retracted. Under the ideal law, training
sets of different folds overlap, so cross-fitting proves mean unbiasedness but
**not** an independent-observation variance estimate; an
OOF ratio is only a risk screen.  Repeated, independent outer superblocks
are required for any estimator-variance claim.

Three easy ways to void (5) are worth making explicit.

1. Holding out one Kerdock/MUB basis from a shared Haar rotation is not the
   stated independence.  Hold out an entire independent rotation or do not
   make the claim.
2. Dividing a held row by \(\|C_h\|_F\), normalizing it by a held diagonal,
   or using cosine similarity is nonlinear in (C_h); its mean need not be
   zero.
3. Usual double-centering of a kernel subtracts a training-column constant
   from (K_{h,T}).  That constant has nonzero held expectation in general.
   It is forbidden here.  A fixed weights-only linear map (L(C_h)), or a
   scalar depending only on training frames, remains lawful because (1) is
   retained.

## 3. What is learned—and the important qualification

For a fixed fold, (4) is exactly a linear connected-pair control:

\[
 c_{h,o}=\langle C_h,\widehat B_{f,o}\rangle_F,
 \qquad \widehat B_{f,o}=\sum_{s\in T_f}\alpha^{(o)}_{f,s}C_s. \tag{6}
\]

Thus its coefficient matrix lies in the empirical span of other-frame gate
pair fluctuations.  It does not use M111's ungated signed transport at all.
Its labels are the actual network outputs, so omitted downstream ReLU gates
enter the training covariance rather than being replaced by a deterministic
surrogate.

Let the missing M111 object be

\[
 B_o=E_U[(g_o(U)-\mu_o)(v(U)v(U)^{\mathsf T}-\Sigma)\mid W]. \tag{7}
\]

M112 does **not** observe (7) directly.  Its population regression object is

\[
 \Gamma_o=E_Q[(Y_{Q,o}-\mu_o)C_Q\mid W]. \tag{8}
\]

Writing both block means as averages over a frame gives one same-column
contribution (B_o/d), plus (d(d-1)) orthogonal-column contributions.
Equivalently, \(\Gamma_o\) is the frame-sampler covariance operator applied
to the pair information in (7), not necessarily (B_o) itself.  Calling
M112 an empirical **frame-visible projection of (B)** is correct; calling
it recovery of the full tensor is not.  The distinction matters because the
orthogonal-column terms can cancel, attenuate, or rotate the useful signal.

In the idealized linear teacher model
\(Y_r-\mu=\langle C_r,B_*\rangle+\epsilon_r\), kernel ridge is precisely
ridge regression on the projection of (B_*) onto
\(\operatorname{span}\{C_s:s\in T\}\).  At (R=50,K=5), that span has
dimension at most 40, whereas the symmetric zero-diagonal pair space has
\(n(n-1)/2=32,640\) coordinates.  The low rank is regularization, not a
proof that the learned directions generalize.

## 4. Symmetry audit

| Transformation | Effect | Result |
|---|---|---|
| Reorder directions or independently flip any frame vector | Rows of (V_r) are permuted/sign-flipped; (V_r^TV_r) is unchanged | exact |
| Antipode (q\mapsto-q) | (V\mapsto-V); the pair matrix is unchanged | exact, even |
| First-hidden permutation (P) | (C_r\mapsto P^TC_rP) | (K), (3), and output corrections are unchanged after the same output-free gate reindexing |
| Orthogonal input rotation | Rotate weights and Haar frame together; all (q^Ta_i) are fixed | exact covariance/invariance |
| Positive ReLU gauge in any hidden layer | First-layer normal directions do not change under positive scaling; later gauges are absent from (C) | exact |
| Output permutation | (K) is shared and the response columns/\(\alpha^{(o)}\) permute | output-equivariant |

Negative first-layer rescaling is not a ReLU gauge and is intentionally not
claimed.  Nor is a coordinate-tie-broken axis construction hidden in this
proposal: every gate is retained symmetrically through the Frobenius product.

## 5. What the frame and design have already annihilated

Each entry of (v_i(u)v_k(u)-\Sigma_{ik}) is antipodally even.  Centering
removes degree zero.  Complete orthonormal-frame averaging kills every
degree-two spherical harmonic exactly: for a trace-free quadratic
\(u^THu\),

\[
 \frac1d\sum_bq_b^THq_b=\operatorname{tr}(H)/d=0.
\]

Consequently every (C_r) has only frame-residual even degrees
\(\ell\ge4\).  This is a structural loss, not an implementation detail:
the leading degree-two two-leg term in M111's hostile annealed calculation
cannot be fitted by M112 on complete frames.

Further consequences:

* If a_i=\pm a_k, then v_iv_k=\pm1/4=\Sigma_{ik}, so that gate
  pair contributes nothing to every (C_r).  Duplicate/antipodal gate
  clusters are invisible.
* A stronger spherical/projective design which annihilates degrees through
  (t) removes the corresponding pair-field modes before the kernel sees
  them.  More elegant design can therefore make this control worse.
* If a block uses only one Haar rotation to generate many related bases,
  correlations may make apparent train-to-held success while invalidating
  (5).  M112 attaches to independent L1 frames only.
* (K_{rs}) for independent (r\ne s) has conditional mean zero.  It is
  not a positive similarity signal; noisy signed overlaps are the intended
  linear features.

## 6. No-go and adversarial examples

1. **No pair signal.** If the output's frame fluctuation is orthogonal to all
   first-gate pair fluctuations, then \(\Gamma_o=0\).  The exact-zero
   prediction remains valid, but fitted finite-sample slopes add variance.
   A constant output is the simplest witness.
2. **Collapsed first gate.** If all a_i are identical or antipodal, every
   pair product is constant, (C_r=0), and (K=0).  A network can still
   have nonconstant amplitude through its downstream factorization; no
   covariance kernel built from these pair signs can learn it.
3. **Unseen tensor direction.** Choose a frame-visible (B_*) orthogonal to
   the random 40-dimensional training span.  The oracle linear control can
   reduce variance while M112's prediction is zero.  This refutes any claim
   that 40 frames identify the missing tensor.
4. **Kernel-only overfit.** In the null model (Y_r=\mu+\epsilon_r), with
   independent noise, ridge coefficients fit accidental K-response
   correlations on training frames.  Their held corrections have zero mean
   but positive conditional variance.  Cross-fit does not turn this into a
   variance reduction.
5. **Illegal normalization.** Replace (K_{hs}) by
   \(K_{hs}/\|C_h\|_F\).  In general
   \(E[C_h/\|C_h\|_F]\ne0\), so a nonzero mean correction can result even
   though raw (C_h) obeys (1).  This is a direct counterexample to casual
   "kernel whitening preserves the control" reasoning.

## 7. Fully billed cost and memory

No cost is free because it is a control variate.  Let (R) be frame count,
(O) output count, and (m=R(1-1/K)).  The following must be charged in the
same runtime and precision as the submitted estimator.

| Item | Work (dense-FMA convention) | Extra persistent memory |
|---|---:|---:|
| Normalize W1, build Sigma | O(dn)+2dn² plus n² arcsines | A: dn; Sigma: n² f64 words |
| Each Haar block, if not already base-sampler work | QR/draw, approximately (4d^3/3) flops | (Q:d^2) f64 words |
| Per frame signs (Q_r^TA) | (2d^2n=33,554,432) flops | dot workspace (dn) |
| Per frame (V_r^TV_r/d-\Sigma) | (2dn^2=33,554,432) flops | one (C_r) |
| All kernel entries | (O(R^2 n(n-1)/2)), or twice this if dense flattening is used | (R^2) f64 words |
| Each fold/output ridge and prediction | (O(m^3+m^2O+ m(R/K)O)) | (mO+m^2) f64 words |
| Existing network outputs | the full base forward/radialization cost for **all** (R) frames | (RO) f64 words if retained |

For (d=n=256,R=50,K=5), the two new dense products cost
(67,108,864) flops per frame, or (3.355\times10^9) flops before QR and
the one-time (\Sigma) Gram.  A packed symmetric zero-diagonal (C_r)
uses (32,640\times8=261,120) bytes (=0.2490) MiB; retaining 50 costs
12.451 MiB.  A dense f64 implementation costs 25.000 MiB instead.  The
50-by-50 f64 kernel costs 0.0191 MiB and (50\times256) f64 responses cost
0.0977 MiB.  A streaming implementation can discard (V_r) after forming
(C_r); one f64 (Q), dot-product workspace, sign workspace, and dense
(C) add about 2 MiB peak, excluding the base evaluator's activations.

The table is an accounting lower bound, not a performance prediction.  The
actual bill must also include QR generation (unless demonstrably shared with
the base), allocations/conversions, arcsine calculation, training-response
means, all failed/precheck paths, and synchronization. With official FlopScope
calibration unavailable, the repaired implementation freezes a conservative
static cost-charge factor before any output is read and computes charged
per-network, geometric, and pooled ratios from raw risks internally. The proxy
bills the original frame bank, all float64 work, hashes, I/O, allocations,
conversions, synchronization, and failures. It is **not measured final
performance**. Cross-fitting does not make the training frame forwards free.

## 8. Repaired deterministic-bank diagnostic and M112b gate

The existing bank supports only a kill-or-redesign association diagnostic. It
cannot promote a champion or validate the ideal-law theorem.

1. Freeze a manifest containing the raw kernel above, float64 association,
   (R=50,K=5), five disjoint ten-frame folds, equation (3), no intercept,
   no held normalization, deterministic association hashes, exact Python and
   NumPy runtime hashes, repaired-theory hash, independent-audit hash, exact
   input/source/config hashes, and the pre-outcome static cost calibration.
2. Before loading any output array, verify the complete manifest/runtime/hash
   surface; during deterministic association regeneration verify nonzero (W_1)
   columns; symmetric
   zero-diagonal (C); the analytic arcsine identity on generated directions;
   row-order, sign-flip, hidden-permutation, input-rotation, and positive
   gauge invariances; rerun determinism; no NaN/Inf; and a complete resource
   trace.  Any failure kills the mutation as specified.
3. At one exact output path, atomically consume a durable no-retry sentinel and
   run exactly one generated-bank association diagnostic. For each network compute the
   covariance-trace ratio of the 50 cross-fitted residual frame blocks to the
   uncorrected blocks.  Freeze the continuation rule: every one of the four
   cost-charged per-network ratios are below 1, their charged geometric mean
   is at most 0.90, and the charged pooled ratio is below 1. Every charged
   quantity is computed internally from raw risks and the frozen factor.
   Every cross-fold covariance, including its sign, is recorded but never
   selected upon. No feature, ridge, fold, rank, or normalization retry
   follows a failure.
4. Even a favorable diagnostic is labelled
   `PASS_DIAGNOSTIC_ONLY_REQUIRES_FRESH_M112B`. It authorizes no estimator.
   A new M112b must be specified and frozen with frame roots statistically
   generated independently of weight roots. Only M112b can test the ideal-law
   theorem using fresh independent whole-frame superblocks.

The gate is smaller than a full factorial because it changes one causal edge
and carries no alternative dictionary.  It is strict because M107 and M110
already demonstrated that training reduction is not evidence of held utility.

## 9. Comparison and final judgment

M107/M110 had exact, symmetric candidate controls but their gains reversed
from train to held; M110's four held variance ratios were all above one.  M112
inherits the same algebraic cross-fit discipline, but the fixed reuse bank is
**not protected against bias by the ideal-law theorem** and remains exposed to
the same variance-overfit failure. Unlike their additive
one-axis features, it retains all first-layer connected gate pairs and learns
their output coupling from other frames.

M111's red team proved that \((W_1,\Sigma,DW_2\cdots W_L)\) is not sufficient
for the true connected tensor (B): an ensemble-preserving internal
orthogonal refactorization can fix M111 pointwise while changing the network.
M112 removes the ungated-transport sufficiency claim by fitting actual
output/pair covariance.  It also loses M111's signed-output routing prior and
starts only at degree four because the complete frame has annihilated degree
two.  The hostile M111 annealed prior—leading usable overlap of order
\(\pi^{-1}2^{-(L-2)}\), about (2.96\times10^{-10}) at depth 32 before that
annihilation—therefore remains a warning, not a theorem about M112.

The repaired conclusion is narrower: raw cross-fitted M112 is exactly unbiased
only in the ideal independent-frame experiment. The fixed hash-derived M111
reuse bank does not satisfy that premise and is only a deterministic
factorization-aware association diagnostic. Whether the projection is useful
must be tested in a separately frozen M112b with frame roots statistically
independent of the weight roots. Neither a favorable reuse diagnostic nor an
M112b premise check may touch a champion or contest evaluator.
