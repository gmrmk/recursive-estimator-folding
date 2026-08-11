# P6 — Under a sum-one constraint the frame covariance acts only through its cross block, and the estimator's own mean is that block's zero

Internal research paper, draft 1. Date 2026-08-11. Corpus: `corpus/whestbench`. Audience: future Opus / researcher
sessions with no conversation memory. Status: **proof, with measured confirmation**. This is the one paper in the P-series
whose central claim is an identity rather than a measurement: §2 stands alone and can be checked with a pencil. Every
numeric claim is quoted from a committed artifact whose path is given inline and collected again in §5, or is arithmetic
performed on such numbers and shown in place. Level tags, per the corpus evidence discipline
(`corpus/whestbench/README.md`): **[O]** observed (a run in this corpus produced it), **[D]** derived (follows by steps
shown here), **[R]** reported (a committed artifact says so; not re-derived here), **[A]** assumed (a stated modelling
choice). Where a step needs a fact this corpus does not contain, it is marked **[GAP]** with the check that would close it.

**Correction to the commissioning statement, stated first because it is load-bearing.** The theorem was handed to me as
"the solution depends on the covariance ONLY through the cross block." That sentence is **false as written** and §2.6
gives the counterexample in one line. What is true — and is what the commissioning brief's own body says — is the pair of
statements proved below: the covariance enters through exactly two objects, `A = PCP` and `b = PCu`; `A` is a metric that
can only convert an existing `b` into a weight direction; and `b = 0` forces the uniform solution for **every** `A` and
**every** ridge. The material claim survives intact. Only the headline needed a clause, and this paper carries the
corrected form.

---

## Abstract

The M192 lineage learned sum-one weights over the 126 Kerdock frame estimates of a realised network from its other
output neurons, and reduced panel MSE by 87.38 % with a truth-trained covariance [R, ledger `m192_cross_output_frame_gls_oracle`].
Four truth-free descendants then failed in four apparently different ways. This paper shows they are one failure, and
that the failure is forced by an identity rather than by noise.

Write `p = 126`, `u = 1/sqrt(p) * 1`, `P = I - u u^T`, and decompose any symmetric covariance as
`C = alpha u u^T + u b^T + b u^T + A` with `alpha = u^T C u`, `b = P C u`, `A = P C P`. On the affine set `1^T w = 1`,
parametrised by `w = 1/p + v` with `v = P v`, the objective collapses to `J(v) = alpha/p + (2/sqrt(p)) b^T v + v^T A v`.
Three consequences follow with no probabilistic content: the scalar `alpha` cannot move the solution at all; the whole
linear term is `b`, so `b = 0` gives `w = 1/p` for every `A` and every positive ridge; and under any strictly positive
ridge `w = 1/p` **if and only if** `b = 0`. `A` is a metric, not a source of information.

The corollary names the trap. Under the estimator's own uniform frame mean as anchor, the self-anchored residual is
`r_j = P x_j`, so the sample second moment is `P C_e P` and its cross block is exactly zero — not approximately, and not
in expectation, but as an algebraic identity in the data. Equivalently, in the M193 autopsy variables the anchor
contamination is `q = -(1/p) C_e 1`, so `P C_a 1 = P C_e 1 + p P q = 0`: the self-anchor does not make `Pq` vanish, it
makes `Pq` exactly minus `1/p` times the cross block the solver needs, and contamination and signal cancel term for term.
Among all linear anchors `a_j = c^T x_j` with `1^T c = 1`, `c = 1/p` is the **unique** choice that annihilates the cross
block identically in the data (§2.7). The uniform frame mean is the one anchor at which the estimator has zero information
about how to deviate from its own mean: a fixed point, not a solution.

The measurement is a kill confirmation with a sharp predeclared falsifier that did not fire: panel ratio
**1.0000000000000073**, per-net 1.0000000000 on all three nets, 48/48 rotations within **2.9e-13** of 1,
`max |w - 1/126| = 1.46e-15`, an independent second solver at **1.0000000000000069**, a permutation null at
**1.0000000000000597** whose power is proved by a positive control that destroys **88.5 %** of the genuine oracle's
log-gain (0.126193 -> 0.788288) [O, `experiments/m192_selfanchor_twosided/results.json`]. Because the self-anchored
covariance equals `P C_m192 P` to **6.40e-15** relative Frobenius error over 384 fits, that run is an exact isolation
experiment: **true `A` with true `b` gives 0.126193 (87.38 % reduction); true `A` with `b = 0` gives exactly 1.000000.**
All of the M192 headroom is carried by the 126-vector `b`, and none of it by the 126x126 contrast block.

This unifies rather than extends the failure list. M193 contaminates `b` additively with `p Pq`; M194 estimates it at
about 5x noise-to-signal; M195 and M197 pay full-Kerdock design structure to buy an estimate of it; the self-anchor
estimates it as exactly zero. The benchmark any future arm on this lane must be quoted against is the realised size of
the object itself: **1.2631074082393916e-05** truth-anchored median against **4.1212792757407778e-19** self-anchored, a
ratio of **3.262809836168492e-14** [O].

---

## 1. The statement

### 1.1 Setting

Fixed for the whole paper, and frozen from M192 [O, `experiments/m192_cross_output_gls/run_m192_g0.py`;
`experiments/m192_selfanchor_twosided/run_selfanchor_g0.py`]:

- `p = 126` Kerdock frames; `n_out = 256` final output neurons; nets 101 / 202 / 303; 16 cached rotations per net; cache
  shape asserted at load as `(16, 126, 256)` [O, `run_selfanchor_g0.py` lines 108-117].
- `x_j` in `R^126` is the vector of the 126 frame estimates of output neuron `j`; `X` is the realised `126 x 256` frame
  matrix of one rotation.
- Output cross-fitting: 8 outer folds by `j % 8`, so each fit trains on 224 output neurons and scores 32 held ones
  [O, `run_selfanchor_g0.py::folds`]. 3 nets x 16 rotations x 8 folds = **384 fits**.
- Baseline: the uniform 126-frame mean. Per-net statistic: ratio of rotation-mean MSEs. Panel: geometric mean over the
  three nets [O, `run_selfanchor_g0.py::panel`].
- Notation: `1` is the all-ones vector in `R^p`; `u = 1/sqrt(p) * 1` so `u^T u = 1`; `P = I - u u^T = I - 1 1^T / p` is the
  orthogonal projector onto the contrast subspace `V = {v : 1^T v = 0}`; `M^+` is the Moore-Penrose pseudoinverse.

### 1.2 Theorem 1 (constrained-GLS reduction)

> Let `C` be a real symmetric `p x p` matrix, `p >= 2`. Set `alpha = u^T C u` (scalar), `b = P C u` (the **cross block**),
> `A = P C P` (the **contrast block**), so that `C = alpha u u^T + u b^T + b u^T + A`. Consider
>
>     minimise  w^T C w   subject to   1^T w = 1.
>
> Writing `w = (1/p) 1 + v` with `v = P v`, the objective is exactly
>
>     J(v) = alpha/p + (2/sqrt(p)) b^T v + v^T A v.
>
> Then:
>
> **(i)** The argmin depends on `C` only through the pair `(A, b)`. The scalar `alpha` shifts `J` by a constant and cannot
> move the solution.
>
> **(ii)** If `A` is positive definite on `V`, the minimiser is unique and equals
> `w* = (1/p) 1 - (1/sqrt(p)) A^+ b = 1/p - (1/sqrt(p)) (P C P)^+ P C u`.
>
> **(iii)** If `A` is positive semidefinite on `V` — which holds whenever `C` is a second moment, as it is in every use
> below — then `b = 0` implies `w* = (1/p) 1`, for **every** such `A` and every positive-semidefinite ridge added to `A`.
> For merely symmetric `A`, `v = 0` is still a stationary point, and the unique one when `A` is nonsingular on `V`.
>
> **(iv)** Conversely, if `A` is positive definite on `V` then `w* = (1/p) 1` **if and only if** `b = 0`.
>
> **(v)** `A` alone does not determine `w*`, and neither does `b` alone. `A` is a metric: it converts a nonzero `b` into a
> weight direction and does nothing at all when `b = 0`.

### 1.3 Corollary 1 (the self-anchor fixed point)

> Let `X` be any realised `p x n` frame matrix and let the anchor be the estimator's own uniform frame mean,
> `a_j = (1/p) 1^T x_j`. Then the self-anchored residual is `r_j = x_j - a_j 1 = P x_j`, the sample second moment is
> `C_a = (1/n) sum_j r_j r_j^T = P S P` with `S = (1/n) X X^T`, and
>
>     C_a 1 = 0   identically,   hence   b = P C_a u = 0   identically.
>
> By Theorem 1(iii) the sum-one GLS solution is `w = 1/p` exactly, for every ridge and every shrinkage in `(0, 1]`.
> **No probabilistic model is used.** Under the additive model `x_j = mu_j 1 + e_j` the same fact reads, in the M193
> autopsy variables, `delta_j = mu_j - a_j = -(1/p) 1^T e_j`, `q = -(1/p) C_e 1`, and
> `P C_a 1 = P C_e 1 + p P q = 0`; and among all linear anchors `a_j = c^T x_j` with `1^T c = 1`, `c = 1/p` is the unique
> choice for which `P C_a 1 = 0` holds identically in `X` (§2.7).

### 1.4 What the statement is not

**Not "the solution depends only on the cross block."** Take `b != 0` fixed and compare `A` with `2A`: by Theorem 1(ii),
`w*(2A, b) - 1/p = (1/2)(w*(A, b) - 1/p)`. Different weights, same `b`. The dependence on `A` is real. What is true is
weaker and sharper: `b` is a **sufficient statistic for whether the solution deviates from uniform at all**, and `A` is not.
The frozen suite makes the mirror-image point measured: two matrices with identical `P C P` and different `b` give
different weights, so `PCP` alone cannot determine `w`
[O, `experiments/m192_selfanchor_twosided/test_selfanchor_math.py::test_sum_one_gls_needs_the_cross_block_not_only_PCP`].

**Not "the common block is irrelevant to the deployed solver."** Theorem 1(i) is a statement about a fixed metric. M192
shrinks with `C_bar = (1-alpha_s) C + alpha_s tau I` and `tau = tr(C)/p`, so adding `s 1 1^T` to `C` raises `tau` by `s`
and perturbs the ridge scale. §2.5 works this through: the common block reaches the solution only through the ridge
magnitude, never through the linear term, so Theorem 1(iii) survives the shrinkage unconditionally. This is the exact
nuance already flagged in `M192_M195_NOTES.md`: "With trace shrinkage, even a pure rank-one addition can alter the ridge
scale" [R].

**Not a claim that `b = 0` is the only way to reach uniform.** If `A` is singular on `V` and `b` lies in `ker A`, the
minimiser is also uniform. Under any strictly positive ridge that case is empty, which is why (iv) is stated with the
positive-definiteness hypothesis.

**Not a statement about biased estimators.** The whole reduction is driven by the unbiasedness constraint `1^T w = 1`.
Drop it and `alpha` re-enters immediately. The theorem says that unbiasedness is precisely what makes the common block
inert and promotes `b` to the sole carrier of information.

### 1.5 The one-sentence form

Under a sum-one constraint the frame covariance has exactly one informative component, the 126-vector `b = P C u`; the
126x126 contrast block is only the metric that converts it; and the estimator's own frame mean is the unique linear
anchor at which `b` is identically zero — so the deployable self-anchored arm is not a weak estimator of the missing
information, it is the exactly-zero estimator of it.

---

## 2. The proof

Nothing in this section uses the cache. Every step is finite-dimensional linear algebra over the reals, and every step is
checked numerically in §2.10.

### 2.1 The splitting is exact and orthogonal

`u u^T + P = I` with `u^T u = 1` and `P u = 0`. Therefore

    C = (u u^T + P) C (u u^T + P)
      = u (u^T C u) u^T  +  u (u^T C P)  +  (P C u) u^T  +  P C P.

Using symmetry of `C`, `u^T C P = (P C u)^T = b^T`. Hence

    C = alpha u u^T + u b^T + b u^T + A,      alpha = u^T C u,  b = P C u,  A = P C P.        (2.1)

Two facts used repeatedly: `u^T b = u^T P C u = 0` (so `b` lives in `V`), and `A u = P C P u = 0` (so `A` acts only on
`V`). The splitting is a direct sum decomposition of the quadratic form into a `1`-dimensional common part, a
`(p-1)`-dimensional contrast part, and the coupling between them. **`b` is that coupling.** [D]

### 2.2 The feasible set, parametrised exactly

`1^T w = 1` is equivalent to `u^T w = 1/sqrt(p)`, since `1 = sqrt(p) u`. The uniform vector `w_0 = (1/p) 1 = u/sqrt(p)`
satisfies it. So the feasible set is exactly `{w_0 + v : v in V}`, `V = range(P) = {v : u^T v = 0}` — an affine subspace
of dimension `p - 1`, with no boundary and no inequality. [D]

### 2.3 The objective collapses

Expand `J(v) = (w_0 + v)^T C (w_0 + v)` term by term, for `v in V`:

- `w_0^T C w_0 = (1/p) u^T C u = alpha / p`.
- `w_0^T C v = (1/sqrt(p)) u^T C v`. Since `v = P v`, `u^T C P v = (P C u)^T v = b^T v`. So the cross term is
  `2 w_0^T C v = (2/sqrt(p)) b^T v`.
- `v^T C v = v^T P C P v = v^T A v`, again because `v = P v`.

Hence

    J(v) = alpha/p + (2/sqrt(p)) b^T v + v^T A v,        v in V.                              (2.2)

`alpha` appears once, as an additive constant on a set that does not constrain it. **Theorem 1(i) is proved.** [D]

### 2.4 The minimiser

`J` restricted to `V` is a quadratic with Hessian `2A|_V` and gradient `2 A v + (2/sqrt(p)) b`. Both `A v` and `b` lie in
`V`, so the gradient is already tangent to the affine set and no Lagrange multiplier is needed. Stationarity is

    A v* = -(1/sqrt(p)) b.                                                                    (2.3)

If `A` is positive definite on `V`, `A|_V` is invertible, `J` is strictly convex on `V`, and the unique minimiser is
`v* = -(1/sqrt(p)) A^+ b`, i.e.

    w* = (1/p) 1 - (1/sqrt(p)) (P C P)^+ P C u.                                               (2.4)

(`A^+` restricted to `V` is the inverse of `A|_V`, since `A` annihilates `u` and maps `V` to `V`.) **Theorem 1(ii) is
proved.** [D]

If `A` is only positive semidefinite on `V`, two cases. If `b` is orthogonal to `ker(A|_V)`, (2.3) is solvable, `A^+ b` is
its minimum-norm solution, and (2.4) still names a minimiser (not the unique one — any element of `ker(A|_V)` may be
added). If `b` has a component in `ker(A|_V)`, `J` decreases without bound along that direction and no minimiser exists.
Both are recorded because the first is what the self-anchored arm meets: there `b = 0`, so a minimiser exists and is
uniform, yet `1` lies exactly in `ker C_a`, which is a statement about the *solver's representation* rather than about the
problem. §2.10 row 9 records what the frozen unshrunk solver does with it. [D]

### 2.5 `b = 0` forces uniform, under every metric and every ridge

Set `b = 0` in (2.2): `J(v) = alpha/p + v^T A v`. Since `A` is positive semidefinite (`C` is a second moment in every use
below, hence PSD; and if `C` is merely symmetric the statement is about stationarity), `J(v) >= alpha/p = J(0)` for all
`v in V`, with equality at `v = 0`. So `v* = 0` and `w* = 1/p` — **for every `A` whatsoever**, and in particular
independently of the conditioning, rank, or spectrum of the contrast block. **Theorem 1(iii) is proved.** [D]

Ridge robustness. Replace `A` by `A + R` for any PSD `R`. The linear term is untouched, so the same argument gives
`v* = 0`. Concretely, for the two ridge schemes in the frozen code:

- **M192 trace shrinkage.** `C_bar = (1 - alpha_s) C + alpha_s tau I`, `tau = tr(C)/p`
  [O, `run_m192_g0.py::_weights` lines 39-49]. Then
  `b_bar = P C_bar u = (1 - alpha_s) P C u + alpha_s tau P u = (1 - alpha_s) b`, because `P u = 0`. So `b = 0` implies
  `b_bar = 0` for every `alpha_s`, and the shrinkage cannot resurrect a linear term that is not there. Meanwhile
  `A_bar = (1 - alpha_s) A + alpha_s tau P`, and `tau` depends on the common block, since
  `tr(P C P) = tr(C) - u^T C u`, giving `tau_contrast = tau_full - alpha/p`. **That is the entire route by which the
  common block reaches the solution: it perturbs the ridge magnitude, never the linear term.** [D]
- **M194 projected ridge.** `denom = max(vals, 0) + LAMBDA * tau_z` applied to the contrast block only, with `correction
  = -(A + lambda tau_z)^+ cross` [O, `run_m194_g0.py::_block_weights` lines 43-64]. `cross = 0` returns `uniform` by
  construction. [O]

Converse. If `A` (or `A_bar`) is positive definite on `V`, then `A^+ b = 0` forces `b = 0`, so `w* = 1/p` iff `b = 0`.
Under any strictly positive shrinkage `alpha_s > 0`, `A_bar = (1-alpha_s) A + alpha_s tau P` is positive definite on `V`
whenever `tau > 0`, so the "iff" is the operative form for every deployed arm. **Theorem 1(iv) is proved.** [D]

### 2.6 `A` matters, and `b` matters: neither is sufficient alone

From (2.4), for fixed `b != 0`, replacing `A` by `kA` (`k > 0`) scales the correction by `1/k`; the weights differ. And
for fixed `A` positive definite on `V`, `b1 != b2` give `A^+ b1 != A^+ b2`, so the weights differ. **Theorem 1(v) is
proved**, and with it the correction announced at the head of this paper: the solution does *not* depend on the covariance
only through `b`. What depends only on `b` is the *dichotomy* uniform-versus-not. [D]

The second half is exactly what the frozen suite tests, by constructing `C2 = C + d 1^T + 1 d^T` with `1^T d = 0`, which
leaves `P C P` unchanged to `1e-10` and changes the solver's weights by more than `1e-6`
[O, `test_selfanchor_math.py` lines 47-53].

### 2.7 The self-anchor: two independent routes, and a uniqueness statement

**Route A — model-free, one line.** With `a_j = (1/p) 1^T x_j`,

    r_j = x_j - a_j 1 = x_j - (1 1^T / p) x_j = P x_j.

Hence for any output set `T`,

    C_a = (1/|T|) sum_{j in T} r_j r_j^T = P [ (1/|T|) sum_j x_j x_j^T ] P = P S P,

so `C_a 1 = P S P 1 = 0` because `P 1 = 0`. Therefore `b = P C_a u = (1/sqrt(p)) P C_a 1 = 0` **identically in the data**,
with no assumption on `X` at all: no additive model, no expectation, no independence, no stationarity. This is what
`self_second_moment` computes — it row-centres the frame block and forms `residual @ residual.T / n`
[O, `run_selfanchor_g0.py` lines 52-59]. [D]

**Route B — the M193 autopsy variables, which is where the reconciliation lives.** Assume `x_j = mu_j 1 + e_j` [A] and let
the anchor be arbitrary, `delta_j = mu_j - a_j`. Then `r_j = delta_j 1 + e_j` and the sample second moment is, exactly,

    C_a = C_e + q 1^T + 1 q^T + s 1 1^T,     q = (1/n) sum_j delta_j e_j,   s = (1/n) sum_j delta_j^2,   (2.5)

which is the committed autopsy form [R, ledger `m193_analytic_anchor_frame_gls`; `M192_M195_NOTES.md` lines 55-58].
Contract against `1` and project:

    C_a 1 = C_e 1 + q (1^T 1) + 1 (q^T 1) + s 1 (1^T 1) = C_e 1 + p q + (q^T 1) 1 + p s 1,
    P C_a 1 = P C_e 1 + p P q,                                                                (2.6)

since `P` annihilates every multiple of `1`. Now specialise to the self-anchor: `a_j = (1/p) 1^T x_j = mu_j + (1/p) 1^T e_j`,
so `delta_j = -(1/p) 1^T e_j` and

    q = (1/n) sum_j delta_j e_j = -(1/p) (1/n) sum_j (1^T e_j) e_j = -(1/p) C_e 1.             (2.7)

Substituting (2.7) into (2.6): `P C_a 1 = P C_e 1 - P C_e 1 = 0`. Exactly, at sample level, no expectation taken. [D]

**The reconciliation, stated plainly.** The M193 line reads: "`s11` is harmless to an unshrunk sum-one rule, but `Pq` is
not" [R, ledger `m193_analytic_anchor_frame_gls`]. Equation (2.6) shows why both halves are true and why they are the same
fact. The `s 1 1^T` term and the `1 q^T` term are multiples of `1` in the contraction and die under `P`; the surviving
contamination is `p P q`, and it enters the linear term **additively alongside the signal** `P C_e 1`. The self-anchor
does not make `P q` vanish. By (2.7) it makes `P q` exactly `-(1/p)` times the cross block the solver needs, so
contamination and signal cancel term for term. The projection that annihilates the harmless term and the projection that
would have to spare the load-bearing one are the same projection, because both live in the same one-sided contraction
against `1`. There is no anchor choice that keeps one and drops the other by projection alone. [D]

**Uniqueness among linear anchors.** Let the anchor be any linear functional of the frame vector, `a_j = c^T x_j`, with
`1^T c = 1` so that the anchor is unbiased for `mu_j` in the additive model. Then `r_j = (I - 1 c^T) x_j`, so with
`M = I - 1 c^T` and `S = (1/n) X X^T`,

    C_a = M S M^T,     P M = P - (P 1) c^T = P,     M^T 1 = 1 - c (1^T 1) = 1 - p c,
    P C_a 1 = P S (1 - p c).                                                                  (2.8)

For this to vanish **identically in `X`** it must vanish at `S = I`, giving `P(1 - pc) = 0`, i.e. `1 - pc = gamma 1` for
some scalar `gamma`; imposing `1^T c = 1` gives `p - p = gamma p`, so `gamma = 0` and `c = 1/p`. Conversely `c = 1/p`
gives `1 - pc = 0` and (2.8) vanishes for every `S`. **So the uniform frame mean is the unique linear unbiased anchor whose
cross block is identically zero.** Every other linear anchor leaves `P S (1 - pc) != 0` for generic data — which is the
positive half of the same statement: a non-uniform anchor keeps a cross block, it just keeps the *wrong* one, contaminated
by `p P q` per (2.6). [D]

Scope of the uniqueness claim: it is uniqueness within the linear-unbiased anchor class, and it is uniqueness of
*identical* annihilation. It is **not** a claim that no other anchor achieves `P C_a 1 = 0` on a particular dataset —
(2.6) is `p - 1` scalar equations on a much larger family, so accidental solutions exist. It is also not a claim that
`c = 1/p` is the only fixed point of the anchor-rule-to-weight map; that question is open and is flagged in §4 as
**[GAP-2]**.

### 2.8 The two frozen solvers are instances of Theorem 1

**M192.** `_weights` forms `C_bar = (1-alpha_s) C + alpha_s tau I` via its eigendecomposition and returns
`w = C_bar^{-1} 1` normalised to sum one [O, `run_m192_g0.py` lines 33-67]. For `C_bar` positive definite that is exactly
the constrained minimiser: the Lagrange condition `2 C_bar w = lambda 1` gives `w proportional to C_bar^{-1} 1`, and the
normalisation enforces the constraint. So Theorem 1 applies to `C_bar`, whose cross block is `(1 - alpha_s) b`. Second,
direct route to the same conclusion: if `C 1 = 0` then `C_bar 1 = alpha_s tau 1`, so `1` is an eigenvector of `C_bar` and
`C_bar^{-1} 1 = 1/(alpha_s tau) * 1`, whose normalisation is exactly uniform. [D]

**M194.** `_block_weights` forms `contrast_j = P r_j` and `common_j = (1/p) 1^T r_j`, then
`block = (1/n) sum contrast_j contrast_j^T` and `cross = (1/n) sum contrast_j common_j`, and returns
`uniform - (block + lambda tau_z)^+ cross` [O, `run_m194_g0.py` lines 39-64]. Identify the objects:
`block = P C_a P = A` and

    cross = (1/n) sum_j (P r_j) ((1/p) 1^T r_j) = (1/p) P C_a 1 = (1/sqrt(p)) b,               (2.9)

so M194's returned correction `-(A + ridge)^+ cross` is exactly `v* = -(1/sqrt(p)) A^+ b` of (2.4), and its
`cross -= cross.mean()` line is a no-op up to roundoff because `P C_a 1` already has zero mean. Two independently written
solvers, one theorem. Equation (2.9) also fixes the normalisation of every `cross_norm` quoted in this paper:
**`||b|| = sqrt(126) * cross_norm`**. [D]

### 2.9 Why the self-anchored arm is an exact isolation experiment

Under the additive model, M192's oracle covariance is the truth-anchored error second moment
`C_e = (1/n) sum_j e_j e_j^T` [O, `run_m192_g0.py::_second_moment`], whose decomposition is
`(alpha_e, b_e, A_e) = (u^T C_e u, P C_e u, P C_e P)`. The self-anchored covariance is `C_a = P S P`, and by Route A of
§2.7 with `x_j = mu_j 1 + e_j` we have `P x_j = P e_j`, so

    C_a = (1/n) sum_j (P e_j)(P e_j)^T = P C_e P = A_e,                                        (2.10)

whose own decomposition is `(0, 0, A_e)`. **The two arms carry the identical contrast block and differ only in `b`.**
Therefore comparing them holds `A` fixed and varies `b` between its true value and zero: a two-point isolation with no
confounder. [D]

One honest wrinkle, and why it does not bite. Under trace shrinkage the two metrics are not bit-identical: the oracle arm
ridges with `tau_full = tr(C_e)/p` while the self-anchored arm ridges with `tau_contrast = tau_full - alpha_e / p` (§2.5).
The ridge scale differs by `alpha_e / p`. This cannot affect the conclusion, because Theorem 1(iii) makes the `b = 0` side
**ridge-independent** — measured across `alpha_s` in {0.25, 0.5, 0.75, 0.9, 0.99}, panel ratio 1.0 throughout with
`max |w - uniform|` shrinking monotonically from 1.46e-15 to 6.77e-17 [O, `results.json` `A1b_alpha_sweep`]. A quantity
that is invariant to the ridge cannot be explained by a change in the ridge. [D]

### 2.10 Every step, checked numerically

Each row is a step above, re-derived by an independent numerical route. Rows 1-5 come from the standalone suite, which
uses synthetic data and no cache at all (5/5 pass) [R, `VERDICT.md` lines 97-106]; rows 6-10 come from the cached run.

| step | claim | check | value |
|---|---|---|---|
| 1 | (2.4) is the M192 solver | `m192._weights(C, 0)` vs `1/p - (1/sqrt p)(PCP)^+ PCu` | agree to `rtol 1e-8, atol 1e-10` [O] |
| 2 | §2.6, `A` alone is insufficient | same `PCP` (to `1e-10`), different `b` | weights differ by `> 1e-6` [O] |
| 3 | §2.5, `b=0` forces uniform | `C = P(FF^T/n)P`, `alpha_s` in {0.25,...,0.99} | `abs(w - 1/p) < 1e-12` all five [O] |
| 4 | (2.7) and (2.6) | `q` vs `-(1/p) C_e 1`; then `norm(P C_a 1) / norm(P C_e 1)` | `q` to `1e-10`; ratio `< 1e-12` [O] |
| 5 | (2.9), M194 cross block | `_block_weights` under self anchor vs generic anchor | `cross_norm < 1e-14` vs `> 1e-3` [O] |
| 6 | Corollary 1, `C_a 1 = 0` | `max norm(C 1) / (norm(C) sqrt(126))` over 384 fits | **4.500451265227899e-15** [O] |
| 7 | Corollary 1, `w = 1/p` | `max abs(w - 1/126)` over 384 fits | **1.4554329963445412e-15** [O] |
| 8 | (2.10), identical `A` | max relative Frobenius `norm(P S P - P C_e P)` over 384 fits | **6.404324061056557e-15** [O] |
| 9 | §2.4 degenerate case | `alpha_s = 0` on `C_a` (1 in the exact kernel) | `RuntimeError: GLS weights do not sum to one` [O] |
| 10 | Theorem 1(iii) is deployable-scale | panel ratio, M192 solver, `alpha_s = 0.25` | **1.0000000000000073** [O] |

Row 9 deserves two sentences of care, because it is the one place where "singular" could be misread. Corollary 1 puts `1`
exactly in the kernel of `C_a`, so `C_a^{-1} 1` — the expression M192's solver evaluates — does not exist at
`alpha_s = 0`; the arm therefore has no unshrunk **solver representation**. It does not follow that the constrained
problem has no solution: with `b = 0` and `A` positive semidefinite the minimiser exists and is uniform (§2.4, first
case), which is precisely why every `alpha_s > 0` returns uniform rather than garbage. The exception was predeclared as
the expected exact singularity and deliberately not repaired [R, `PREDECLARATION.md` §PREDICTION 3; `VERDICT.md`
DEVIATIONS 5]; the artifact records its message verbatim, and which of `_weights`'s guard branches fired is not recorded
and is not claimed here.

### 2.11 The measured kill, in full

All from `experiments/m192_selfanchor_twosided/results.json` unless marked, and reproduced in
`run.stdout.log` / `run2.stdout.log` [O].

| arm | per-net ratios (101 / 202 / 303) | panel |
|---|---|---:|
| A0 harness crosscheck (frozen M192 oracle) | 0.146840 / 0.095677 / 0.143037 | **0.12619260077870575** |
| A1 self-anchor, M192 solver, `alpha_s = 0.25` | 1.0000000000 / 1.0000000000 / 1.0000000000 | **1.0000000000000073** |
| A2 self-anchor, M194 solver (independent impl.) | 1.0000000000 / 1.0000000000 / 1.0000000000 | **1.0000000000000069** |
| A3 permutation null control | 1.0000000000 / 1.0000000000 / 1.0000000000 | **1.0000000000000597** |
| A4 positive control, oracle unshuffled | 0.146840 / 0.095677 / 0.143037 | 0.12619260077870575 |
| A4 positive control, oracle shuffled | 0.774569 / 0.596948 / 1.059396 | **0.7882882297648867** |

- **The harness is the M192 harness.** A0 reproduces the frozen archive at `max_abs_diff_vs_frozen = 0.0` and the archived
  P2 baseline at `max_p2_baseline_crosscheck = 0.0` on all three nets [O].
- **The prediction was sharp and did not fail.** The predeclared falsifier was "if any per-net or per-rotation ratio
  differs from 1 by more than 1e-9 the step-0 algebra is wrong and the verdict reopens" [R, `PREDECLARATION.md`]. Measured:
  per-rotation maxima `1.854e-13 / 1.495e-13 / 2.829e-13`, so **48/48 rotations lie within 2.9e-13 of 1**; the largest
  per-net deviation from 1 in A1 is `1.4876988529977098e-14` (net 303), recorded under the artifact's key
  `gates.max_abs_panel_deviation_from_one`, which is computed from the three per-net ratios and not from the panel [O].
  A theorem that predicts a specific number to 13
  digits, on data it has never seen, and hits it, is a different kind of evidence from a gate that fails to fire.
- **The second solver is independent.** A2 runs the same construction through M194's separately written projected-block
  code and returns 1.0000000000000069 [O]. Agreement here is not a re-run: the two solvers share no line of code, only
  Theorem 1.
- **The null has power.** A3's 1.0000000000000597 would be uninterpretable alone — a dead probe and a real null look
  identical. A4 applies the same per-row output-index shuffle inside the frozen truth-trained M192 oracle and moves the
  panel from 0.126193 to 0.788288. In log-gain terms, `ln 0.7882882297648867 = -0.237891` against
  `ln 0.12619260077870575 = -2.069946`, so the shuffle destroys `1 - 0.237891/2.069946 =` **88.51 %** of the genuine
  oracle's log-gain [D, arithmetic on committed numbers]. The control has power; A3 is a real null [O + D].
- **The decisive pair.** By (2.10) and row 8 of §2.10, A1 ran the frozen solver on the **exact true contrast block** with
  `b = 0`:

      true A, true b  ->  panel 0.126193   (87.38 % reduction; `1 - 0.12619260077870575 = 0.8738073992212942`)
      true A, b = 0   ->  panel 1.000000   (0.00 % reduction)

  One hundred percent of the M192 oracle headroom is carried by `b`; the 126x126 contrast block contributes nothing on its
  own under the sum-one constraint [D from Theorem 1 + O from the two panels].
- **The killed quantity, measured directly.** In M194's normalisation (`cross_norm`, so `||b|| = sqrt(126) * cross_norm`
  by (2.9)): self-anchored median `4.1212792757407778e-19`, max `1.1653983742729381e-18`; truth-anchored median
  `1.2631074082393916e-05`, min `3.6919796504402005e-06`; ratio `3.262809836168492e-14` [O]. In the `||b||` normalisation
  that is `4.63e-18` against `1.42e-04` (`sqrt(126) = 11.224972160321824`; `11.224972160321824 * 1.2631074082393916e-05 =
  1.4178345492983424e-04`) [D]. **The self-anchor is not a noisy estimator of `b`. It is the exactly-zero estimator of `b`:
  100 % attenuation at zero variance.**
- **Determinism.** Three full runs produced byte-identical `results.json` apart from `runtime_seconds`
  [R, `VERDICT.md` §"Both required signals"].

---

## 3. What it closes

The five records below are cited by ledger id from `corpus/whestbench/headroom/fold_ledger.json` (267 candidate records
at the time of writing). For each I state what was previously known, what Theorem 1 or Corollary 1 now derives, and
whether the status changes.

### 3.1 `m192_cross_output_frame_gls_oracle` — status `screened`, unchanged; its content is now localised

Committed result: per-net ratios 0.146840 / 0.095677 / 0.143037, panel 0.126193 (87.38 % reduction), bootstrap
[0.107641, 0.151650], 48/48 rotations improve, all 384 folds chose `alpha_s = 0.25`, median weight L1 exactly 1, median
max abs weight about 0.0155 [R]. Its own status note reads "deployable identifiability unresolved" [R].

What is new: the 87.38 % is now attributed to a **single 126-vector**. Not "a covariance", not "cross-output structure" in
general — the object is `b = P C_e u`, whose realised size is `1.26e-05` in the M194 normalisation (§2.11). The contrast
block `A_e`, a 126x126 object with 7,875 free parameters, is a metric and carries none of the headroom on its own. This is
a **strict localisation of an existing screened result, not a revision of it**: the ratio, the gates and the status are
untouched. The oracle premise still stands, and it still requires truth.

Status change: **none**. Interpretation change: the deployable target shrinks from "estimate a 126x126 covariance without
truth" to "estimate one 126-vector without truth."

### 3.2 `m193_analytic_anchor_frame_gls` — empirical kill, now **upgraded to a proof of mechanism**

Committed result: panel ratio 1057.899; per-net 1530.06 / 1108.71 / 697.92; analytic anchor error 6.09e-4 to 1.88e-3;
median weight L1 inflated to 5.76; "dominant bias" [R].

What is new: (2.6) is the exact statement of the failure. Under any anchor, `P C_a 1 = P C_e 1 + p P q`. The contamination
enters the linear term **additively and in the same subspace as the signal**, so no projection separates them. M193 is not
"a bad anchor" — it is a demonstration that the contamination and the signal are the same kind of object. The record's own
autopsy sentence, "s11 is harmless to an unshrunk sum-one rule, but Pq is not," is exactly Theorem 1(i) plus (2.6): the
scalar rank-one term is invisible to the argmin, and the cross term is not, because the cross term *is* the argmin's only
input.

The corpus does not commit the realised magnitude of `p P q` under M193's analytic anchor, so the phrase "many orders
larger than `b` itself" carried in `VERDICT.md` and `M192_M195_NOTES.md` is **[R] and not re-derived here** — see
**[GAP-1]** in §4. What is derivable from the committed numbers is the realised damage: M193 converted a rotation-mean
squared bias of `8.94921759286583e-09 / 5.376039812636523e-08 / 3.272622369605708e-08` into
`3.036017507149423e-04 / 6.405084837669753e-04 / 1.603251413414867e-04`, factors of
**33,925 / 11,914 / 4,899** [D, division shown, from `m193_g0_results.json`].

Status change: **killed -> killed, with the empirical kill upgraded to a derived mechanism.** The gate would now fire from
(2.6) before any compute.

### 3.3 `m194_independent_pilot_block_gls` — empirical kill, mechanism confirmed and the target renamed

Committed result: panel raw ratio 15.8306, cost-adjusted 16.8357; per-net raw 20.3235 / 9.67330 / 20.1799; the
**truth-anchor** projected solver on the same code still gives 0.124538 / 0.082539 / 0.139294 (panel
`0.11271039626263891` by geometric mean [D], matching the committed 0.112710 in `M192_M195_NOTES.md` [R]); pilot-prefix
autopsy monotone at k = 1/8/64/126 giving raw 97.600 / 15.831 / 1.525 / 0.671, with even k = 126 at cost ratio 1.343;
"pilot cross-noise is about 5x the true cross signal at the median" [R].

What is new: the record's status note already says "expectation identity passes; affordable pilot precision fails". §2.8
identifies *which* expectation and *which* precision: M194's `cross` is exactly `b/sqrt(p)` by (2.9), so the whole arm is
an estimator of one 126-vector, and its failure is the SNR of that vector alone. The "about 5x" is corroborated by a
committed single-fold value: net 101, rotation pair 0, fold 0 has `cross_norm = 6.918094526522331e-05`
[O, `m194_g0_results.json`], against the truth-anchored median `1.2631074082393916e-05` [O], a ratio of **5.477**
[D, division shown]. The two are in the same normalisation (both from `m194._block_weights`) and the same fold structure
(224 train / 32 held); they differ in rotation set (M194 uses rotations 0-7, the self-anchor A2 diagnostic all 16), so
this is an order-of-magnitude corroboration of the committed median, not a recomputation of it.

Status change: **killed -> killed**. The kill was already correctly diagnosed as SNR; this paper names the estimand
exactly and supplies the benchmark to quote against.

### 3.4 `m195_symmetric_half_design_attenuation` — empirical kill, now readable as a price paid for `b`

Committed result: panel ratio 1.15748, bootstrap [0.88427, 1.54798]; per-net 1.34781 / 0.886838 / 1.29738; and crucially
the **uncorrected** two-half means were already 1.29790 / 0.865509 / 1.23066 against the full-Kerdock comparator [R].

What is new: the split is a purchase, and (2.4) says what is being bought. Splitting 126 frames into two independent
63-frame halves is the only way to make each half a pilot for the other, and the sole purpose of a pilot is to identify
`b`. The committed numbers show the bill arriving before the goods: the design-splitting cost (ratio ~1.30 / 0.87 / 1.23
before any correction) exceeds what the recovered `b` can return. Theorem 1 says this is the general shape for this family
— the correction can only act through `A^+ b`, so a noisier `b` bought with a degraded design has no route to a win.

Status change: **killed -> killed**. This is a reframing, not a new derivation; the kill was and remains empirical.

### 3.5 `m197_crossed_three_rotation_u_statistic` — empirical kill, same reframing

Committed result: per-net 1.917651 / 1.008849 / 1.325648; panel 1.368804, bootstrap [1.072507, 1.824979]; the uncorrected
three-by-42 mean was already 1.783449 / 0.976651 / 1.242740; 360 fits, zero fallbacks, max arbitrary-mu cancellation
discrepancy 9.93e-19, max combined sum-one error 2.22e-16 [R]. Its status note: "last fixed-budget crossed-pilot topology
loses full Kerdock geometry".

What is new: the algebra passing at 9.93e-19 while the arm loses is exactly the shape Theorem 1 predicts for this family.
The cancellation identity governs the *construction* of a `b` estimate; the constraint governs what a `b` estimate can buy.
M197 confirms, at a third topology, that the binding constraint is the SNR and the design price of `b`, not the correctness
of the cancellation.

Status change: **killed -> killed**, reframed.

### 3.6 The self-anchored arm itself is not in the ledger

`grep` for `selfanchor` over `headroom/fold_ledger.json` returns zero matches, and no candidate record in the ledger's 267
entries refers to this arm; the only id containing `two_sided` is the unrelated `m91_two_sided_cycle_sketch` [O]. A
corpus-wide `grep -rl "m192_selfanchor"` over `.md` and `.json` returns exactly one file, the arm's own `results.json` [O].
The arm's evidence therefore lives entirely in `experiments/m192_selfanchor_twosided/` (`PREDECLARATION.md`, `VERDICT.md`,
`results.json`, two run logs, the runner and the test suite). This is a bookkeeping gap, not an evidential one — see
**[GAP-3]**.

### 3.7 The unification, in one paragraph

Five arms, one estimand. M192 obtains `b` from truth and wins 87.38 %. M193 obtains `b` contaminated additively by `p P q`
and loses by three orders of magnitude. M194 obtains `b` from an independent pilot at roughly 5x noise-to-signal and loses
by one order. M195 and M197 obtain `b` by splitting the design, and pay more in lost Kerdock structure than the recovered
`b` returns — visible in that both arms' *uncorrected* split baselines are already worse than the full-design comparator.
The self-anchor obtains `b` from the estimator's own outputs and obtains exactly zero, by (2.8), because the uniform frame
mean is the unique linear unbiased anchor at which the cross block is identically zero. This is not a sixth kind of
failure. It is the fifth reading of one 126-vector, and the reading is `4.1212792757407778e-19` where the object measures
`1.2631074082393916e-05`.

The consequence for the disposition already recorded in `M192_M195_NOTES.md` — "reopening requires genuinely new
information about the common frame error" [R] — is now sharper than a disposition. Any rule that builds its anchor as a
linear unbiased combination of the same realised frames has an anchor of the form `a_j = c^T x_j`, `1^T c = 1`, and by
(2.8) its cross block is `P S (1 - p c)`, a linear functional of the same `S` the solver is already conditioning on.
The self-anchor is the point where that functional is identically zero; every other point in the class is a rescaled
version of the same information, not new information. Genuinely new information must come from outside the realised frame
matrix. [D, within the linear-anchor class; see §4 for what this does not cover.]

---

## 4. Scope, and what this paper does not claim

**4.1 The corrected headline.** Stated at the top and proved in §2.6. "The solution depends on the covariance only through
the cross block" is false; `A` changes `w` whenever `b != 0`. The surviving claims are Theorem 1(i)-(v), and the
load-bearing one for this campaign is (iii)+(iv): under any positive ridge, `w = uniform` if and only if `b = 0`.

**4.2 The theorem is about the constrained problem only.** Every clause is driven by `1^T w = 1`. For a biased rule the
common block `alpha` re-enters the objective as a live term and none of the conclusions transfer. The theorem should be
read as a statement about what unbiasedness costs: it makes the common mode inert, and thereby concentrates all
exploitable information into `p - 1` dimensions.

**4.3 Corollary 1 is model-free; the interpretation is not.** Route A of §2.7 uses no model: `C_a 1 = 0` holds for any
realised `X`. But the *reading* of that fact — that the annihilated object is the common/contrast cross block of the frame
**error** — uses the additive model `x_j = mu_j 1 + e_j` [A]. That model is the campaign's standing frame decomposition
[R, `M192_M195_NOTES.md` lines 49-53], not a result of this paper.

**4.4 Uniqueness is class-local.** §2.7 proves uniqueness among **linear** anchors `a_j = c^T x_j` with `1^T c = 1`, and
uniqueness of *identical* annihilation. A nonlinear anchor rule, or a linear rule with `1^T c != 1`, is not covered. The
"unique anchor" phrasing in `VERDICT.md` is therefore correct within that class and should not be quoted without it.

**4.5 [GAP-1] — the magnitude of the M193 contamination.** The claim that `p P q` under the analytic anchor is "many
orders larger" than `b` itself is [R] from `VERDICT.md` and `M192_M195_NOTES.md` and is **not re-derived here**. The
committed `m193_g0_results.json` records `anchor_mse` (6.09e-4 / 1.88e-3 / 6.85e-4) and rotation-mean bias, but no norm of
`q` or of `P C_a 1`. **Closing check:** recompute `||P C_a 1||` per fold from `run_m193_g0.py`'s analytic anchor on the
cached P2 frames and compare against `||P C_e 1||` from the truth anchor — cached arithmetic only, no forwards, roughly
the cost of the A2 diagnostic. Until then the ordering claim is reported, and only the realised bias inflation
(33,925 / 11,914 / 4,899, §3.2) is derived.

**4.6 [GAP-2] — fixed-point uniqueness.** §2.7 proves `c = 1/p` is *a* fixed point of the anchor-rule-to-weight map
(feed the uniform anchor, receive uniform weights) and the unique identical annihilator. Whether it is the unique fixed
point of that map is not addressed. **Closing check:** characterise the solutions of `c = 1/p - (1/sqrt p) A_c^+ b_c` with
`b_c = (1/sqrt p) P S (1 - pc)` and `A_c = P C_a(c) P`, or exhibit a second fixed point numerically on cached frames.
Nothing in this paper depends on the answer.

**4.7 [GAP-3] — the arm is not ledgered.** §3.6. The self-anchored arm has a predeclaration, a verdict, results, logs and
a passing test suite, but no `fold_ledger.json` record. **Closing action:** add a record with
`id = m192_selfanchor_two_sided_contrast_gls`, `status = killed`, `status_note = "sum-one fixed point; cross block
identically zero"`, `artifact_hash = m192_selfanchor_twosided/results.json`, `primary_effect = 0.0`. This is bookkeeping,
and I did not perform it: this paper is read-only by the contest firewall.

**4.8 What the kill does and does not bound.** It bounds one family: sum-one constrained linear reweighting of the 126
frame estimates, with the covariance built from a linear unbiased anchor derived from the same realised frame matrix. It
says nothing about biased hybrids, about nonlinear functions of the frame matrix, about anchors built from network weights
rather than outputs, or about estimators that change the design. It is the same discipline P1 §4.1 states: kills bound
named families under their own gates [R, `core/RECURSION_PACKET_GEN6_20260810.md`].

**4.9 The oracle premise remains a premise.** The 87.38 % is a truth-trained oracle on three synthetic He nets at
(width, depth) = (256, 32), 16 cached rotations each, scored against cached M181 truths with noise floors roughly
1.2e-8 to 2.2e-8 against baseline MSEs of roughly 2.0e-7 to 5.9e-7 [R, `M192_M195_NOTES.md` lines 42-45]. Output neurons
are not independent network-level validation units. Nothing here is a submission claim, a rank claim, or a statement about
trained networks.

**4.10 Firewall.** This paper was written read-only from committed artifacts. No estimator or m245 code was executed, no
measurement was taken, no network forward was run, no git or network operation was performed. The arithmetic shown in §2.11
and §3 is division and logarithm on numbers quoted from committed JSON, performed and displayed in place. The one file
written is this one.

---

## 5. Reproduction map

Paths are relative to the corpus root
`C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\publish\recursive-estimator-folding\corpus\whestbench`.

| claim | source of the number | file |
|---|---|---|
| Theorem 1, steps 1-5 of §2.10 | standalone suite, no cache, 5/5 | `experiments/m192_selfanchor_twosided/test_selfanchor_math.py` |
| M192 solver is `C_bar^{-1}1` normalised | lines 33-67 | `experiments/m192_cross_output_gls/run_m192_g0.py` |
| M192 covariance is truth-anchored | `_second_moment`, lines 70-73 | same file |
| M194 solver is `uniform - (A+ridge)^+ cross` | `_block_weights`, lines 36-96 | `experiments/m192_cross_output_gls/run_m194_g0.py` |
| self-anchored second moment is `P S P` | `self_second_moment`, lines 52-59 | `experiments/m192_selfanchor_twosided/run_selfanchor_g0.py` |
| A0 reproduces the M192 archive at diff 0.0 | `A0_harness_crosscheck` | `experiments/m192_selfanchor_twosided/results.json` |
| panel 1.0000000000000073; `max abs(w - 1/126)` 1.46e-15; `max norm(C 1)` rel. 4.50e-15 | `A1_selfanchor_m192_solver` | same |
| per-rotation maxima 1.854e-13 / 1.495e-13 / 2.829e-13 | `A1...per_net.*.max_abs_rotation_ratio_minus_one` | same |
| alpha sweep, `alpha_s = 0` raises | `A1b_alpha_sweep` | same |
| second solver 1.0000000000000069; `cross_norm` medians 4.12e-19 vs 1.26e-05; ratio 3.26e-14 | `A2_selfanchor_m194_solver` | same |
| permutation null 1.0000000000000597 | `A3_permutation_null_control` | same |
| positive control 0.126193 -> 0.788288 | `A4_positive_control_m192_oracle` | same |
| `P S P = P C_e P` at 6.40e-15 over 384 fits | `A5_contrast_block_identity` | same |
| gate arithmetic, prediction tolerance 1e-9, max deviation 1.49e-14 | `gates` | same |
| the step-0 algebra, predeclared before compute | §0.2-0.4 | `experiments/m192_selfanchor_twosided/PREDECLARATION.md` |
| deviations, the M193 reconciliation, the isolation reading | whole file | `experiments/m192_selfanchor_twosided/VERDICT.md` |
| M193 anchor error, bias, weight L1 | `per_net.*.anchor_mse`, `*_rotation_mean_bias2`, `weight_diagnostics` | `experiments/m192_cross_output_gls/m193_g0_results.json` |
| M194 `cross_norm` 6.918094526522331e-05 (net 101, pair 0, fold 0) | `per_net.101.pair_rows[0].diagnostics[0]` | `experiments/m192_cross_output_gls/m194_g0_results.json` |
| M194 truth-block per-net 0.124538 / 0.082539 / 0.139294 | `per_net.*.oracle_block_ratio` | same |
| M195 / M197 ratios, split-design baselines | §"M195", §"M197" | `experiments/m192_cross_output_gls/M192_M195_NOTES.md` |
| all five ledger records cited in §3 | `candidates[].id` | `headroom/fold_ledger.json` |
| register, evidence tags, scope discipline | whole file | `papers/P1_SPECKLE_THEOREM_20260810.md` |

**Determinism.** Three runs of `run_selfanchor_g0.py` produced byte-identical `results.json` apart from `runtime_seconds`
[R, `VERDICT.md`]. A future session re-running it should expect bitwise agreement and treat disagreement as an environment
change, not a result.

### Constants worth memorising

| symbol | value | source |
|---|---|---|
| `p`, `u`, `P` | 126, `1/sqrt(126)`, `I - 1 1^T / 126` | §1.1 |
| `sqrt(126)` | 11.224972160321824 | arithmetic |
| M192 oracle panel | 0.12619260077870575 (87.38 % reduction) | `m192_g0_results.json` |
| self-anchor panel (A1) | 1.0000000000000073 | `results.json` |
| second solver panel (A2) | 1.0000000000000069 | `results.json` |
| permutation null (A3) | 1.0000000000000597 | `results.json` |
| positive control, shuffled oracle | 0.7882882297648867 (88.51 % of log-gain destroyed) | `results.json` + arithmetic |
| `max abs(w - 1/126)` | 1.4554329963445412e-15 | `results.json` |
| `max norm(C 1) / (norm(C) sqrt 126)` | 4.500451265227899e-15 | `results.json` |
| `P S P` vs `P C_e P`, max rel. Frobenius | 6.404324061056557e-15 (384 fits) | `results.json` |
| **cross-block benchmark, truth-anchored median** | **1.2631074082393916e-05** (`cross_norm`; `norm(b) = 1.418e-04`) | `results.json` |
| `cross_norm`, self-anchored median | 4.1212792757407778e-19 | `results.json` |
| killed-information ratio | 3.262809836168492e-14 | `results.json` |
| M193 panel / bias inflation | 1057.899 / 33,925x, 11,914x, 4,899x | ledger + `m193_g0_results.json` |
| M194 panel raw / cost-adjusted | 15.8306 / 16.8357 | ledger |
| M194 truth-block panel | 0.11271039626263891 | `m194_g0_results.json` + arithmetic |
| M195 / M197 panels | 1.15748 / 1.368804 | ledger |

---

## 6. How to falsify this paper

**Break Theorem 1** by exhibiting a symmetric `C` with `P C u = 0` whose sum-one constrained minimiser is not uniform under
a positive ridge. By §2.5 that requires `J(v) = alpha/p + v^T A_bar v` to have a minimiser off `v = 0` with `A_bar` PSD,
which is impossible in exact arithmetic; a claimed counterexample is therefore a conditioning artifact, and the first thing
to check is whether the reported `b` is zero to the scale of `||C||` rather than to an absolute tolerance.

**Break Corollary 1** by exhibiting a realised `X` for which the row-centred second moment `P S P` does not annihilate `1`
by more than roundoff. Row 6 of §2.10 measures `4.50e-15` relative over 384 fits; anything above `~1e-12` at that scale is
either a different centring or a bug.

**Break the uniqueness statement** by exhibiting a linear anchor `c` with `1^T c = 1`, `c != 1/p`, whose cross block
vanishes for every `S`. §2.7 shows the `S = I` case already forces `c = 1/p`, so such a `c` cannot exist; a claimed
example is an arithmetic error.

**Break the isolation reading** — this is the softest joint and the one worth attacking. The claim is that A1 and the M192
oracle differ *only* in `b`. It rests on (2.10), measured at `6.40e-15`, and on the ridge argument of §2.9. To break it,
exhibit a channel by which the two arms' metrics differ in a way that is not absorbed by the ridge invariance measured in
`A1b_alpha_sweep` — for instance, show that M192's inner truth-driven `alpha_s` selection lands somewhere other than 0.25
on some fold, which would make the two arms' shrinkage families genuinely different. The ledger records all 384 folds
choosing 0.25 [R], so this is a check on that record, not on this paper's arithmetic.

**Break the unification** by finding an arm in the M192 lineage whose failure is *not* a failure to obtain `b`. The
candidates are the ones this paper reframes rather than derives: M195 and M197 (§3.4, §3.5). If either one's loss can be
attributed to something other than the SNR and design price of `b` — a conditioning failure of `A`, a fold-structure
artifact, a scoring effect — then the unification is a story rather than a theorem, and §3.7 should be weakened to cover
M192/M193/M194 and the self-anchor only.

**The benchmark to quote against.** Any future arm on this lane produces, implicitly or explicitly, an estimate of one
126-vector. Before it is built, state the expected `||b_hat| - |b||` against the realised
`1.2631074082393916e-05` (M194 normalisation), and state the noise-to-signal it would need to beat M194's roughly 5x.
An arm that cannot answer that in advance is a sixth reading of the same vector.
