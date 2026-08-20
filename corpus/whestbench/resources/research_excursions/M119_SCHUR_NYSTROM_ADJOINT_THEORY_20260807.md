# M119 hostile theory audit: Schur--Nyström covariance adjoint braid

**Disposition: KILL as stated; do not implement or run a correction oracle.**

The proposed braid has one correct algebraic observation: if the Price/orthant
kernel has a *usable* PSD factorization, its Schur action maps a low-rank
covariance adjoint to explicitly factored columns, and all outputs can be
batched through the affine pullback. That observation does **not** imply that
the kernel is compressible in the norm that the Schur action needs. A rank-one
kernel approximation can have an excellent Frobenius spectrum while losing
about half of a legitimate rank-one adjoint. The independent-Gaussian
correlation background gives an exact, permutation-symmetric counterexample.

Consequently a weights-only spectral, pivoted-Cholesky, or Nyström rank
`r in {1,2,4,8}` premise has no theory pass. Keeping the diagonal residual
exact merely recreates a rank-`n` adjoint. The route also has two separate
open interfaces: the complete ReLU covariance Jacobian is more than the
off-diagonal Price Schur multiplier, and an adjoint only weights a supplied
mean/covariance source--it does not form the omitted non-Gaussian source.

This is a theory and pre-execution audit only. It did not read contest data,
targets, public rows, a scorer, an API, a champion package, or an outcome run.
It changes neither the frozen champion nor any prior decision.

## 1. Boundary and prior evidence

The parent `adjoint_cumulant/REPORT.md` proved the exact terminal `LLQ`,
`LLLC`, and `LLQQ` projections on a frozen Gaussian background, then killed
the full adjoint because one ReLU covariance pullback sends a rank-one output
slice to a generic dense slice. `cavity_dyson/REPORT.md` independently
identifies the missing fixed-instance four-point vertex and rejects a
mean/covariance/skew-only closure. M119 is allowed to try only a new
representation of that already-identified covariance-adjoint bottleneck; it
cannot relabel a covariance approximation as a new source law.

This differs in type from the killed rank-5 forward k4 sketch:

| object | M119 | killed `k4_tensor_sketch` |
|---|---|---|
| state | one covariance adjoint per terminal output | a recurrent pair-factor four-cumulant vertex |
| affine action | one-sided action on factor columns | two-sided action on two `n x n` pair factors |
| local source | none supplied by compression | explicit k4 source/`(2,1,1)` action |
| relevant error | Schur-multiplier and signed feedback error | selected quartic-form and nonlinear k4 correction error |

Thus M119 must not reuse the rank-5 cost certificate, nor add a forward k4
copy to its adjoint. The rank-5 result remains an adverse warning: even its
best local pair-eigen approximation had quartic cosine `0.9888` while the
downstream correction cosine was essentially `-1`. A favorable spectrum or
Frobenius tail is not a signed-feedback guarantee. The tensor-train failure
similarly rules out treating generic ReLU geometry as low rank merely because
one has chosen a tensor factorization.

The related M08 audit already found no generic *shared output* rank-4/8/16
block. M119 avoids that particular assertion by retaining output-specific
factors. It therefore owes the corresponding all-output state, compression,
and symmetry account below; it may not claim that the output bases are shared.

## 2. Exact tensor types and the braid identity

Use column activations and the explicit convention

\[
 z_\ell=W_\ell h_{\ell-1}+b_\ell,\qquad
 W_\ell\in\mathbb R^{n^\ell\times n^{\ell-1}},\qquad h_\ell=\rho(z_\ell).
\]

The target shape is `n^ell = n = 256`, `O = n` terminal observables, and 31
hidden ReLU pullbacks. Let `C^z_ell` and `C^h_ell` be Gaussian-background
covariances. For an output scalar objective `J_o`, the covariance adjoints
are symmetric matrices

\[
 A^h_{\ell,o}=\partial J_o/\partial C^h_\ell\in\mathbb S^{n^\ell},
 \qquad A^z_{\ell,o}=\partial J_o/\partial C^z_\ell\in\mathbb S^{n^\ell}.
\]

The exact affine pullback is

\[
 A^h_{\ell-1,o}=W_\ell^T A^z_{\ell,o}W_\ell. \tag{1}
\]

For off-diagonal covariance variations, Price's theorem gives the self-adjoint
Schur portion

\[
 A^z_{\ell,o}=K_\ell\circ A^h_{\ell,o},\qquad
 (K_\ell)_{ij}=\Pr_{G_\ell}(Z_i>0,Z_j>0). \tag{2}
\]

At zero mean this is the stated

\[
 K_{ij}=\frac14+\frac{\arcsin R_{ij}}{2\pi}\quad(i\ne j),\qquad K_{ii}=\frac12,
 \tag{3}
\]

where `R` is the correlation matrix. With nonzero background means, (3) must
be replaced by the bivariate Gaussian orthant probability. `K` remains PSD:
it is the Gram matrix of the random variables `1{Z_i>0}`.

Suppose, only for the representation calculation, that a deterministic PSD
approximation is available,

\[
 \widetilde K_\ell=Q_\ell Q_\ell^T,\qquad Q_\ell\in\mathbb R^{n\times r}.
\]

Represent one output slice as

\[
 A^h_{\ell,o}=X_{\ell,o}S_{\ell,o}X_{\ell,o}^T,
 \quad X_{\ell,o}\in\mathbb R^{n\times q},\quad
 S_{\ell,o}=S_{\ell,o}^T\in\mathbb R^{q\times q}. \tag{4}
\]

`S` is a signature/core, so the notation covers a signed terminal Hessian as
well as the PSD rank-one case. Writing `q_s` for column `s` of `Q`, the
approximate Schur step is exactly

\[
 \widetilde K\circ(XSX^T)
 =\widetilde X\,(I_r\otimes S)\,\widetilde X^T,\qquad
 \widetilde X=[\operatorname{diag}(q_1)X\;\cdots\;
                 \operatorname{diag}(q_r)X]
 \in\mathbb R^{n\times qr}. \tag{5}
\]

Equation (5) is the legitimate braid: Schur pullback multiplies rank `q` by
`r`; (1) maps every resulting column by `W^T` without changing that rank.
For all outputs, the compact factor tensor has shape

```text
X[l, o, i, a] : (O, n, q),       S[l, o, a, b] : (O, q, q),
Q[l, i, s]    : (n, r),          expanded X : (O, n, q*r).
```

There is one common **kernel factor** `Q_l`, but no generic common factor
subspace for the `X[l,o]`. At the final affine map the `O` terminal response
directions already span `R^n` generically. Any replacement of these
output-specific factors by one shared rank-`r` output basis is M08's rejected
hypothesis, not a consequence of (5).

### Recompression that at least respects gauge and signs

If this branch were ever reopened, use the same fixed cap for both the kernel
and the retained adjoint rank: `q=r`, with

\[
 r\in\{1,2,4,8\}.
\]

This set is selected before targets from arithmetic only: `r=16` makes the
rank before compression 256 and the deterministic-core recompression alone
exceeds two trillion operations at the target shape. It is not selected from a
spectrum, correction, or output score.

Ordinary Euclidean SVD is not positive-ReLU-gauge covariant. Let
`D_l=diag(sqrt(diag(C^h_l)))` on strictly positive-variance coordinates, and
form the standardized symmetric matrix

\[
 \bar A_{\ell,o}=D_\ell A^h_{\ell,o}D_\ell.
\]

After (5), thin-QR the standardized factor, diagonalize its `(r^2) x (r^2)`
signed core, keep the `r` largest absolute eigenvalues, and map the retained
factor back with `D_l^{-1}`. This is a predeclared, output-observable
weighted spectral compression: it is per output, has no sample/target input,
and retains both signs rather than silently PSD-projecting a signed adjoint.

This is deliberately only a gauge-invariant *standardized-adjoint* metric, not
a magic source-observable metric. Until a weights-only covariance perturbation
source is supplied, the norm that controls
`<A[o], delta C>` is undefined. Weighting a randomized range by a source seen
in a reference calculation would be an oracle leak; weighting it by the
downstream response matrix does not reduce the generic dimension because that
matrix has rank `n`. Thus the declared SVD is the strongest target-free choice
available here, and its success would still require the signed feedback gate
in Section 6 rather than follow from a retained spectral tail.

Under a hidden positive gauge `h_l' = G h_l`,

\[
 C'=GCG,\quad A'=G^{-1}AG^{-1},\quad D'=GD,\quad \bar A'=\bar A,
\]

so the reconstructed physical adjoint is gauge covariant. Under a coordinate
permutation, `bar A` is conjugated by the same permutation. A finite rank cut
is permutation covariant only when the cutoff has a strict spectral gap. If a
tied eigenspace crosses the cap, the only covariant rules are to retain the
entire tied space (a rank-budget failure) or abstain. Choosing a lexicographic
pivot, a coordinate-seeded randomized range, or an arbitrary subset of a
degenerate eigenspace breaks the required permutation symmetry. The same rule
applies to the eigenspace/pivot selection for `K`.

Zero or numerically near-zero variances are not a harmless implementation
detail: `D^{-1}` then does not exist, and a fixed variance floor breaks the
gauge argument. Such a coordinate must be handled by an exact quotient with a
separately proved limiting rule, or the case fails closed.

## 3. The fatal norm mismatch

The premise says that actual deep Gaussian-closure kernels might be
spectrally compressible. Even if true in Frobenius energy, that is the wrong
property. Let

\[
 E=K-\widetilde K\succeq0.
\]

The residual Schur map `M_E(A)=E circ A` has induced spectral norm

\[
 \|M_E\|_{2\to2}=\max_i E_{ii}. \tag{6}
\]

The upper bound is the standard PSD Schur-multiplier bound, and equality
follows by applying the map to `e_i e_i^T`. Thus neither small
`||E||_F/||K||_F` nor a small tail relative to the leading eigenvalue controls
the rank-one adjoints that M119 must propagate. A valid kernel gate must
control `max diag(E)`, or a stronger Schur-multiplier norm--not merely spectral
energy.

### Exact adversary: independent Gaussian coordinates

Take the perfectly legitimate zero-mean background `R=I_n`. Then

\[
 K=\frac14\mathbf1\mathbf1^T+\frac14I.
\]

The leading rank-one approximation has excellent Frobenius capture at width
256, but

\[
 \widetilde K_1=\frac{n+1}{4n}\mathbf1\mathbf1^T,\qquad
 E_1=\frac14I-\frac1{4n}\mathbf1\mathbf1^T,\qquad
 \max_i(E_1)_{ii}=\frac{n-1}{4n}.
\]

For the valid rank-one adjoint `A=e_i e_i^T`,

\[
 K\circ A=\frac12e_i e_i^T,\qquad
 \frac{\|(K-\widetilde K_1)\circ A\|_2}
      {\|K\circ A\|_2}=\frac{n-1}{2n},
\]

which is `0.498046875` at `n=256`. The all-output terminal family can
contain these directions exactly (take an identity final map), and generic
full-rank final maps span the same space. This is not a low-probability
output-specific pathology.

For any PSD rank-`r` truncation of this `K`, the tail trace gives

\[
 \max_i E_{ii}\ge {\operatorname{tr}E\over n}
 = {n-r\over4n},
\]

when the leading direction and `r-1` directions of the degenerate complement
are kept. At `r=8`, this lower bound is `0.2421875`, still a relative
rank-one Schur error of at least `0.484375`. Pivoted Cholesky/Nyström cannot
evade this information bound: it may place the residual diagonals unevenly,
but then some output coordinate is worse.

This example also exposes the symmetry problem. The orthogonal complement of
`1` is an `(n-1)`-fold degenerate eigenspace. A deterministic
permutation-equivariant rank in `{2,...,n-1}` cannot select a proper subspace
of it. A rank-one `a 11^T` approximation is covariant but has the error
above; retaining the degenerate complement is rank `n`.

Keeping the diagonal residual exactly is not a repair. For a diagonal `D_0`,
`D_0 circ (XSX^T)` is a diagonal matrix, generically rank `n`, and its next
affine pullback is dense. It reinstates the very rank explosion M119 was meant
to avoid.

Deep He backgrounds are not entitled to avoid this counterexample: an
approximately orthogonal first layer has `R` close to `I`, and random dense
rows have small off-diagonal correlations at width 256. Near-singular or
nearly collinear correlations create a different danger: the arcsine/orthant
kernel is bounded, but its correlation derivatives scale as
`(1-R_ij^2)^(-1/2)`. Hence covariance-background error and the omitted
mean/variance Jacobian terms can become ill conditioned exactly where a
low-rank spectrum may look visually concentrated.

## 4. What an honest full-adjoint recurrence would still require

Equations (1)--(2) are only the off-diagonal covariance block. A complete
Gaussian ReLU moment map depends on `(mu,C)`. Its adjoint contains, in
addition to (2), the diagonal-variance derivatives and cross blocks

\[
 b^z_{\ell,o}\;{+}{=}\;
  (\partial C^h_\ell/\partial\mu_\ell)^*[A^h_{\ell,o}],\qquad
 A^z_{\ell,o}\;{+}{=}\;
  (\partial C^h_\ell/\partial\operatorname{diag}C^z_\ell)^*[A^h_{\ell,o}],
\]

plus the usual mean-map Jacobians. These terms are pairwise dense row/column
contractions even when `A` is factored. Treating `K circ A` as the whole
pullback therefore cannot claim to restore mean/covariance feedback. The
zero-mean arcsine form is also not the correct kernel for a biased deep
background.

If a declared source produces `(delta mu_l, delta C_l)`, the adjoint produces
only the linear weighting

\[
 \Delta J_o=\sum_l\{b_{l,o}^T\delta\mu_l+
               \langle A_{l,o},\delta C_l\rangle\}. \tag{7}
\]

It does not determine that source. The terminal Born identities supply
specific projected `LLQ/LLLC/LLQQ` cumulant diagrams, not a proved complete
`(delta mu,delta C)` feedback source. The conditional-cumulance and
cavity/Dyson counterexamples still apply. Any future use must first state a
weights-only source, its order, and an ownership partition; adding a forward
copy of `LLQ`, `LLLC`, or `LLQQ` to its adjoint copy is forbidden.

For a compression error `e_l=||A_l-hat A_l||_2`, the best elementary bound is

\[
 e_{l-1}\le \|W_l\|_2^2\left[
 \|M_{K_l}\|e_l+
 \|M_{K_l-\widetilde K_l}\|\,\|\widehat A_l\|_2+
 \epsilon^{\rm comp}_l\right]. \tag{8}
\]

For PSD residuals the middle multiplier is exactly the diagonal quantity in
(6). Downstream propagation multiplies local errors by products of the actual
affine/schur maps. Bounding this by a product of individual singular norms is
safe but can be extremely pessimistic; nonnormal alignment can also make a
benign layerwise spectrum misleading. A target-shape audit must report both
that certified upper bound and deterministic power-iteration lower bounds for
every suffix operator. No cancellation of signed output corrections may be
credited to an unmeasured norm bound.

## 5. Declared target-shape account (conditional arithmetic, not a bill)

This is a deliberately favorable implementation account for the
*representation only*. It assumes 31 braid steps, `O=n=256`, float64, a rank
cap equal to the kernel rank, and an exact small-core standardized signed SVD
after each Schur expansion. It does not claim that an actual source has been
supplied or that the installed FlopScope will bill the special functions and
allocations this way.

Let `m=r^2`. The charged dense-operation formulas are

\[
\begin{aligned}
 F_{\rm affine}&=31(2n^2Or),\\
 F_{\rm Schur\ columns}&=31(nOr^2),\\
 F_{\rm recomp}&=31O\{2nm^2+2nmr+16m^3\},\\
 F_{K\text{-factor}}&=31(8n^2r).
\end{aligned}
\]

The recompression line charges standardized thin QR, signed-core formation and
eigensolve, and factor reconstruction. It is intentionally not the much
cheaper randomized-range sketch: a coordinate-seeded range finder has no
permutation-covariance proof, while an equivariant tied-eigenspace rule must
fail closed. Add one all-output mean-adjoint affine pass (`1.040187 B`), **two**
factor-by-dense-kernel contractions for the covariance-to-mean and
covariance-to-variance-diagonal cross blocks (`2 F_affine` total), and `0.500
B` for source/ownership contractions. These are distinct bivariate ReLU
derivative kernels; charging only one would silently omit half of the complete
`(mu,C)` adjoint. The last allowances are still conditional on an explicit
source and full Jacobian.

| rank `r` | affine | Schur columns | signed recompression | `K` factor | full provisional total |
|---:|---:|---:|---:|---:|---:|
| 1 | 1.040 B | .002 B | .008 B | .016 B | **10.876 B** |
| 2 | 2.080 B | .008 B | .106 B | .033 B | **14.116 B** |
| 4 | 4.161 B | .033 B | 1.820 B | .065 B | **22.128 B** |
| 8 | 8.321 B | .130 B | 52.009 B | .130 B | **84.963 B** |

Every row includes the previously audited `6.189 B` full-covariance Gaussian
background. The complete provisional `r=8` path is already `4.963 B` above
the `80 B` envelope, before bivariate-CDF/arcsine scalar cost, pivoting,
copies, or a nontrivial source. `r=16` is statically excluded: its small-core
recompression term alone is about `2.4 T` operations. This is an independent
cost account, not the rank-5 k4 ledger's `8 n^3 r` pair-factor transport plus
`(2,1,1)` work.

Streaming makes the raw storage modest but not free. With both pre- and
post-ReLU covariances retained for reverse traversal, background covariances
use about `31 MiB`. The following is conservative live float64 output-factor
storage (two compact buffers plus one expanded buffer), excluding less than a
MiB of small QR/core workspaces:

| rank `r` | one compact `O*n*r` | expanded `O*n*r^2` | live output factors | `K` factors for 31 layers | total with two covariance stacks |
|---:|---:|---:|---:|---:|---:|
| 1 | .5 MiB | .5 MiB | 1.5 MiB | .06 MiB | about 33 MiB |
| 2 | 1 MiB | 2 MiB | 4 MiB | .12 MiB | about 35 MiB |
| 4 | 2 MiB | 8 MiB | 12 MiB | .24 MiB | about 44 MiB |
| 8 | 4 MiB | 32 MiB | 40 MiB | .48 MiB | about 72 MiB |

The storage table is not a success argument. It makes explicit that M119 pays
for per-output factors and does not smuggle in M08's rejected shared basis. Any
dense `A[o,i,j]` reference, all-layer output stack, or dynamic rank increase is
reference-only and forbidden from the target candidate bill.

The two cross-Jacobian derivative matrices can be regenerated from each saved
Gaussian background during reversal; that is the favorable storage choice used
above, but it leaves their bivariate-CDF evaluation in the operation bill. If
they are cached for all 31 layers instead, add about `31 MiB` to every row.

## 6. Frozen target-free falsifier (do not launch under this disposition)

The following is the only acceptable reopening protocol. It is written now to
prevent spectrum selection, source selection, or correction tuning after
reference values are known.

### A. Algebra, covariance, and small-width adjoint test

1. Freeze ranks `{1,2,4,8}`, the standardized signed-SVD rule, full tied-block
   abstention, and deterministic generated networks with widths `{8,12,16}`,
   hidden depths `{2,3,4}`, three Philox replicates each. Use He-normal
   weights, normal biases of standard deviation `.10`, and known Gaussian
   inputs. Generate all seed names and candidate hashes before a reference.
2. Include the exact `R=I`/identity-final-map adversary. For every rank,
   verify (5) against dense Schur multiplication to `1e-12`, then report
   `max diag(K-K_r)`, the rank-one coordinate relative error, and the
   permutation-tie disposition. A coordinate tie-break is a symmetry fail.
3. For each generated small network and every terminal output, build the dense
   adjoint of the **complete declared Gaussian `(mu,C)` recursion**, including
   the diagonal and mean/covariance cross blocks. Compare it with the compressed
   recurrence in the standardized Frobenius metric, per output and globally.
   Require global error at most `.05`, worst-output error at most `.10`, and
   every predeclared rank-one/dense symmetric probe contraction to have the
   correct sign and relative error at most `.10`. These are representation
   gates, not a claim of real-law fidelity.
4. Apply simultaneous hidden permutations and positive diagonal gauges. All
   reconstructed physical adjoints, mean adjoints, factor contractions, and
   compressed scalar feedbacks must equivary to `1e-10`. A crossed cutoff tie,
   zero variance without an exact quotient, or a sign/invariance failure kills
   that rank without a different pivot, seed, or tolerance.

### B. Target-shape, weights-only gate

On four fresh generated `n=256`, depth-32 networks (Philox seed namespace
`119001..119004`), run only the Gaussian closure and the candidate's
weights-only kernel construction. Do not form a dense output-adjoint stack and
do not generate an input/reference correction. For each layer and each frozen
rank report

\[
 \epsilon_{\rm Schur}=\max_i(K-K_r)_{ii},\qquad
 \epsilon_F=\|K-K_r\|_F/\|K\|_F,
\]

the spectral gap/tie status, exact residual PSD check, minimum variance,
maximum `|R_ij|`, and the per-layer operation/memory ledger. Require
`epsilon_Schur <= .02` at every layer. This is intentionally a Schur-action
gate; `epsilon_F` is diagnostic and cannot substitute for it. The exact
`R=I` calculation predicts failure for every listed rank, which is why M119
is killed before running this stage.

Also report, for every source-layer/suffix pair, the certified upper bound from
(8) using affine singular norms and the deterministic power-iteration lower
bound of the actual composed standardized operator. The candidate may continue
only if the certified worst-case local-to-output multiplier times
`epsilon_Schur` is at most `.05`; a large upper bound is a nonnormal-growth
non-pass, not evidence that empirical cancellation will save it. The native
integrated bill must be at most `80 B`, have no uncharged dynamic
refactorization, and reproduce the static shape ledger above.

### C. Fresh correction oracle, only after A and B pass

Only then freeze a *separate* generated small/medium network bank, an explicit
weights-only `(delta mu,delta C)` source, its diagram-ownership table, every
rank, and all coefficients. Candidate factors and corrections are written
before any reference samples. Use independent scrambled-normal streams with
split-stream confidence intervals to compare the sealed feedback correction
with the exact dense-adjoint same-source correction and with the generated
network's empirical terminal non-Gaussian correction. The latter comparison
requires at least `.80` signed retention and `.80` material-sign agreement in
every stratum; unresolved reference precision is a kill, not an invitation to
change rank or source. No contest datum or prior generated bank may enter this
oracle.

The correction oracle cannot repair a failure in A or B, and it cannot make a
missing source observable. It is intentionally last rather than a way to
search for a favorable spectrum or feedback coefficient.

## 7. Verdict and cheapest next step

**IMPLEMENT: no.** The proposed rank-small spectral kernel is not controlled in
the Schur-multiplier norm, does not by itself include the full ReLU
mean/covariance adjoint, and has no complete feedback source.

**REPAIR: only with a different theorem.** A future child would have to give a
target-free, permutation/gauge-covariant approximation of the *Schur operator
on the declared all-output adjoint family*, including its diagonal action and a
complete `(mu,C)` Jacobian, with a certified suffix-error bound. It must also
provide the missing weights-only source and ownership partition. Merely
preserving a diagonal residual, selecting pivots with indices, using a
Frobenius spectral tail, or importing the rank-5 k4 sketch is not that repair.

**KILL: M119 as proposed.** The `R=I` counterexample kills the premise before
target-shape execution: rank `r<=8` leaves a Schur residual near `.25`, hence
a nearly 50% error on an admissible rank-one adjoint despite apparent spectral
compressibility.

The cheapest next step is a ten-line, target-free unit test of the displayed
`R=I` kernel at `n=8,16,256`: form each frozen-rank PSD truncation, evaluate
`max diag(K-K_r)` and the `e_i e_i^T` Schur error, and assert the required
permutation-tie abstention. It should be recorded as a theory-kill sentinel,
not used to tune a Nyström variant or to launch the correction oracle.

## Local evidence consulted

- `adjoint_cumulant/REPORT.md` -- exact terminal Born projections and the
  original rank-one-to-full-rank covariance-adjoint obstruction.
- `cavity_dyson/REPORT.md` -- fixed-instance four-point closure and
  conditioning no-go.
- `terra_m08_shared_2pi/REPORT.md` and `SPEC.json` -- no shared output-basis
  assumption, diagram ownership, and clean-room gate discipline.
- `k4_tensor_sketch/REPORT.md` and `DERIVATION.md` -- rank-5 local spectral
  ceiling, downstream sign reversal, and non-transferable pair-factor cost.
- `tensor_train_gaussian_cross/REPORT.md` -- weighted spectral rank is not a
  generic ReLU compression theorem.
- `compressed_residual_cumulant_transport/REPORT.md` and
  `terra_composability/REPORT.md` -- a compact representation does not create
  the higher-order response/source it must contract, and forward/adjoint
  diagram duplication is forbidden.
