# P4 — Uniform weights are the constrained minimiser of the Kerdock design's quadrature error at every spherical-harmonic degree: a proof

Internal research paper, draft 1. Date 2026-08-11. Corpus: `corpus/whestbench`. Audience: future Opus / researcher
sessions with no conversation memory. Status: **proof**, not a measurement — every step below is either an exact
arithmetic identity shown in full, or a fact quoted from a committed artifact whose path is given inline and collected
again in §6. Level tags follow P1 and the corpus evidence discipline (`corpus/whestbench/README.md`): **[O]** observed
(a run in this corpus produced it), **[D]** derived (follows from observations by shown steps), **[R]** reported (a
committed artifact says so; not re-derived here), **[A]** assumed (a stated modelling choice). Where a step needed a
fact the corpus does not contain, the paper says so and does not invent one.

This paper proves a statement the corpus has cited three times as a "certificate" without ever proving it
(`experiments/m192_cross_output_gls/M192_PREDECLARATION.md` line 20; `M192_M195_NOTES.md` line 35;
`resources/research_excursions/M115_PROJECTIVE_ARCCOSINE_NYSTROM_THEORY_20260807.md` line 173), and corrects one
sub-claim of the only place a proof sketch was attempted (`sources/research_designs_quadrature_20260810.md` §Q3.2).

---

## Abstract

The champion's frozen Kerdock design — 126 mutually unbiased orthonormal frames of 256 directions each, N = 32,256
base points, antipodally doubled to 64,512 [R, P1 §1.1] — is used with **uniform** weights. This paper proves that
choice is not a convenience: uniform weights are the exact constrained minimiser of the design's quadrature error at
**every** spherical-harmonic degree simultaneously, not only at the degree-4 Bragg notch S6 measured. The proof is
three lines once two facts are in place: the degree-ℓ kernel matrix G_ℓ = [G_ℓ(⟨x_i,x_j⟩)] is a Gram matrix (addition
theorem), hence positive semidefinite; and the all-ones vector is one of its eigenvectors, because every point of the
design sees the identical inner-product fingerprint. The unbiasedness constraint 1ᵀw = 1 then annihilates the linear
term, leaving Q_ℓ(u + δ) = Q_ℓ(u) + δᵀG_ℓδ ≥ Q_ℓ(u).

The second fact is the one that needs care, and it is where the obvious argument fails. S6's committed census gives
**aggregate** counts (32,256 diagonal, 8,225,280 within-frame zeros, 548,352,000 at +1/16, 483,840,000 at −1/16, summing
to 32,256² = 1,040,449,536) [O]. Dividing those by N proves only that the *average* point sees 17,000 plus-signs and
15,000 minus-signs; it does not prove every point does, and for odd degrees the signed split is exactly what matters.
This paper closes that hole [D]: because each frame is an orthonormal basis and the census forces
|Σ_i x_i| = 2016 = 126 × 16 = Σ_a |m_a| exactly, the 126 frame-sums m_a are all equal to a single vector m of norm 16,
whence ⟨x_i, Σ_j x_j⟩ = 126 for **every** i, whence n_i⁺ − n_i⁻ = 2000 for every i. The per-point fingerprint is
therefore constant, signed and unsigned, and the theorem holds at every degree.

Three quantitative consequences are derived exactly, in rational arithmetic, from the census plus S6's committed
Gegenbauer coefficients. (1) The design's three spectral shells are the eigenspaces of a rank-3-structured matrix and
decompose as constant(1) + frame-contrast(125) + within-frame(32,130) = 32,256 [D]. (2) The degree-4 error of the
126-frame set is **exactly** Q₄(u) = |G₄(1/16)|/42 = 65/88,424,448 = 7.350908201315546e-07, reproducing S6's
`lam_top` to every printed digit, and equals the "three missing frames" of the 129-frame complete real MUB spread
whose degree-4 error is exactly zero [D]. (3) The price of deviating from uniform is the Bragg suppression figure
itself: a per-frame reweighting costs **43.3×** and a per-point reweighting **42.5×** the constant mode in S6's
committed deviation-operator normalisation (exactly 43 and 699,008/16,575 = 42.1724× in the quadrature-form
normalisation) [D]. The mode the design suppresses 42× is the mode the constraint pins, and every direction the weights
could move in is priced at 42–43× the error being chased.

What it closes, stated strictly: **none** of `m192_cross_output_gls`, `m193`, `m194`, `m195`, `m197` or `s2` is fully
derived by this theorem, because in every case the criterion optimised was the *realised* network-output covariance,
not a zonal one. What the theorem derives is the baseline each of them had to beat, and the exact reason M192's 87.38 %
oracle headroom cannot be design-side information. It upgrades the F4 SYMMETRY family's positive dual from a hedged
transitivity argument to a proof, and it corrects `sources/research_designs_quadrature_20260810.md` §Q3.2's claim that
an LP over frame-orbit weight classes "could kill both non-bulk shells of the deg-4 operator" — it cannot; uniform is
the strict minimiser. Tonight's `m192_selfanchor_twosided` kill is **not** an instance of this theorem: it reaches the
same fixed point through an estimator identity rather than a design symmetry, which makes it a sibling result and a
genuine second signal.

---

## 1. Notation and the frozen setting

Fixed throughout, all [R] from `experiments/s6_bragg_spectrum/S6_VERDICT.md` and P1 §1.1 unless marked otherwise:

- d = 256, sphere S²⁵⁵, normalised surface measure σ, Gegenbauer parameter α = (d−2)/2 = 127.
- X = {x_1, …, x_N}: the frozen Kerdock v3 base set, N = 32,256 unit vectors, partitioned into 126 frames
  F_1, …, F_126 of 256 points each (32,256 / 126 = 256).
- Y = X ∪ (−X): the antipodal doubling, |Y| = 64,512 — the point set the champion actually evaluates.
- H_ℓ: degree-ℓ real spherical harmonics on S²⁵⁵; m_ℓ = dim H_ℓ; m_4 = 183,148,480 and m_6 = 414,173,091,136 [O,
  `s6_results.json` `constants.dim_H4` / `dim_H6`].
- G_ℓ(t) = C_ℓ^(127)(t) / C_ℓ^(127)(1), the normalised Gegenbauer/zonal kernel with G_ℓ(1) = 1. The addition theorem in
  this normalisation reads Σ_{k=1}^{m_ℓ} Y_{ℓk}(x) Y_{ℓk}(y) = m_ℓ · G_ℓ(⟨x,y⟩) for any L²(σ)-orthonormal basis
  {Y_{ℓk}} of H_ℓ [R, standard; consistent with S6's exact-rational checks E[G_ℓ] = 0 and m_ℓ·E[G_ℓ²] = 1 for ℓ = 4, 6,
  which hold EXACTLY in `Fraction` arithmetic, O].
- K_ℓ := [G_ℓ(⟨x_i, x_j⟩)]_{i,j=1}^{N}, the N × N degree-ℓ kernel matrix on X. Diagonal entries are 1.
- u := (1/N, …, 1/N)ᵀ, the uniform weight vector. 1 := (1, …, 1)ᵀ.
- **W** := {w ∈ R^N : 1ᵀw = 1}, the admissible (unbiased) weight set. Negative weights are permitted; the theorem does
  not need positivity.
- Q_ℓ(w) := wᵀ K_ℓ w.

**Why sum-one is exactly the unbiasedness constraint.** The estimator applies one Haar rotation R to the frozen design
and returns Σ_i w_i f(R x_i) as an estimate of ∫ f dσ [R, P1 §1.1]. Taking E_R gives (Σ_i w_i) ∫ f dσ, so the estimator
is unbiased for every f if and only if 1ᵀw = 1. Degree 0 is then integrated exactly by every admissible w, and the ℓ = 0
term never appears below.

**Why Q_ℓ is the quadrature error.** For fixed f with harmonic decomposition f = Σ_{ℓ≥0} f_ℓ, the standard Haar
identities E_R[f_ℓ(Rx) f_ℓ(Ry)] = ‖f_ℓ‖² G_ℓ(⟨x,y⟩) and E_R[f_ℓ(Rx) f_{ℓ'}(Ry)] = 0 for ℓ ≠ ℓ' give, for every
w ∈ **W**:

> **(MASTER)**  E_R[( Σ_i w_i f(R x_i) − ∫f dσ )²] = Σ_{ℓ ≥ 1} ‖f_ℓ‖² · Q_ℓ(w).

[D, one line from the two Haar identities.] This is the corpus's own working model: R0 computes exactly
`MSE/sigma^2 = sum_{l even >= 4} a_l · lam_top(l)` with `lam_top(l) = (1/N²)[N·1 + n_0 G_l(0) + n_+ G_l(1/16) +
n_- G_l(−1/16)]`, i.e. `lam_top(l) = Q_l(u)` [R+O, `experiments/r0_harmonic_energy_spectrum/R0_HARMONIC_SPECTRUM.md`
§1]. Equivalently, m_ℓ · Q_ℓ(w) is the squared worst-case error over the unit ball of H_ℓ, by the RKHS bound
sup_{‖f‖=1} |Σ w_i f(x_i)|² = ‖Σ_i w_i Z_ℓ(x_i, ·)‖² = m_ℓ Σ_{i,j} w_i w_j G_ℓ(t_ij). Both readings differ from Q_ℓ by a
positive constant, so the minimiser is the same.

---

## 2. The statement

Given precisely enough to be falsified. Two claims, one on the base set and one on the doubled set.

> **Theorem (uniform optimality at every degree).**
>
> **(A) On the base set X.** For every ℓ ≥ 1, K_ℓ is positive semidefinite and K_ℓ 1 = c_ℓ 1 for a scalar c_ℓ = N·Q_ℓ(u).
> Consequently, for every w = u + δ ∈ **W** (so 1ᵀδ = 0),
>
>     Q_ℓ(w) = Q_ℓ(u) + δᵀ K_ℓ δ  ≥  Q_ℓ(u),        for every ℓ ≥ 1.
>
> At every **even** ℓ ≥ 2 the inequality is **strict** for every δ ≠ 0, because K_ℓ has exactly three eigenvalues, all
> positive. Hence, combining with (MASTER): for every target f with any even-degree content ℓ ≥ 2, uniform weights are
> the **unique** minimiser over **W** of the Haar-averaged mean squared error — pointwise in f, not merely on average
> over a function ensemble.
>
> **(B) On the doubled set Y.** The same holds with |Y| = 64,512 in place of N. At every **odd** ℓ the conclusion is
> stronger still: K_ℓ^Y 1 = 0, so Q_ℓ(u) = 0 and uniform is a global minimiser over all of R^{|Y|}, not merely over
> **W**. At even ℓ the minimum is attained on an affine set of dimension 32,256: any δ that is antisymmetric under the
> antipodal map (δ(−y) = −δ(y)) lies in ker K_ℓ^Y and is free. Uniform is *a* minimiser on Y, and the *unique*
> minimiser on X.

**Falsifiers.** (i) Exhibit w ∈ **W** and an ℓ with Q_ℓ(w) < Q_ℓ(u) — one N-vector and one dot product settles it.
(ii) Exhibit a point x_i of the base set whose signed cross-frame census is not (17,000 at +1/16, 15,000 at −1/16);
that breaks §3.3 and reopens all odd degrees on X. (iii) Exhibit a within-frame pair of the base set with inner product
≠ 0, or a cross-frame pair with |inner product| ≠ 1/16; that breaks the census S6 verified bitwise-exactly and reopens
everything.

**What the theorem is not.** It is a statement about weights on a *fixed* point set under a *zonal* (rotation-averaged)
criterion. It says nothing about changing the point set, and nothing about criteria that depend on the realised network
outputs. §5 states both limits precisely, and §4 shows they are exactly the limits that keep the theorem consistent
with M192's measured 87.38 % oracle reduction.

---

## 3. The proof

Self-contained. Every constant is either quoted with its artifact path or computed here in exact rational arithmetic.

### 3.1 Step (i): K_ℓ is positive semidefinite, at every degree

Let {Y_{ℓk}}_{k=1}^{m_ℓ} be any L²(σ)-orthonormal basis of H_ℓ and let Φ_ℓ ∈ R^{m_ℓ × N} have entries
(Φ_ℓ)_{k,i} = Y_{ℓk}(x_i). The addition theorem gives, entrywise,

    (K_ℓ)_{ij} = G_ℓ(⟨x_i,x_j⟩) = (1/m_ℓ) Σ_k Y_{ℓk}(x_i) Y_{ℓk}(x_j) = (1/m_ℓ) (Φ_ℓᵀ Φ_ℓ)_{ij}.

So K_ℓ = (1/m_ℓ) Φ_ℓᵀ Φ_ℓ is a Gram matrix: vᵀK_ℓv = ‖Φ_ℓ v‖² / m_ℓ ≥ 0 for every v. ∎ [D]

This step needs nothing about the design. It holds for every ℓ ≥ 0 and every point configuration. It is also the
statement that Q_ℓ(w) ≥ 0, which the paper uses in (B).

### 3.2 Step (ii), the easy half: the unsigned per-point fingerprint is forced by counting

From S6's exact census over all 32,256² pairs (`s6_results.json` `fingerprint`, max deviation from the k/256 grid
**0.0** — the entries are dyadic ±1/16 so every f64 inner product is bitwise exact) [O]:

| value | count | location |
|---|---|---|
| 1 | 32,256 | diagonal only |
| 0 | 8,225,280 | ALL within-frame off-diagonal pairs |
| +1/16 | 548,352,000 | cross-frame |
| −1/16 | 483,840,000 | cross-frame |

Arithmetic check, re-run here: 32,256 + 8,225,280 + 548,352,000 + 483,840,000 = **1,040,449,536** = 32,256² [D].

Two structural consequences, both by counting alone and both exact:

1. **Each frame is an orthonormal basis of R²⁵⁶.** The census says *all* within-frame off-diagonal inner products are 0,
   and 8,225,280 = 32,256 × 255 = 126 × 256 × 255 is exactly the number of ordered within-frame off-diagonal pairs when
   every frame has 256 members. So each frame is 256 mutually orthogonal unit vectors in R²⁵⁶ [D]. (S6 states the same
   in prose: "the 126 phased-Hadamard frames are orthonormal bases that are pairwise mutually unbiased" [R].)
2. **Every point has exactly 255 within-frame partners and 32,000 cross-frame partners**, since
   32,256 − 1 − 255 = 32,000 [D].

For **even** ℓ this is already enough. G_ℓ is an even function of t when ℓ is even, so G_ℓ(+1/16) = G_ℓ(−1/16) and the
signed split is irrelevant. Writing a_ℓ := G_ℓ(0) and b_ℓ := G_ℓ(1/16), the i-th row sum of K_ℓ is

    (K_ℓ 1)_i = 1 + 255·a_ℓ + 32,000·b_ℓ ,

the same for every i. Hence K_ℓ 1 = c_ℓ 1 with c_ℓ = 1 + 255a_ℓ + 32,000b_ℓ, for every even ℓ ≥ 2 [D].

### 3.3 Step (ii), the hard half: the SIGNED per-point fingerprint, and why dividing the census is not a proof

For **odd** ℓ, G_ℓ(0) = 0 and G_ℓ(−t) = −G_ℓ(t), so the i-th row sum is

    (K_ℓ 1)_i = 1 + (n_i⁺ − n_i⁻) · b_ℓ ,    n_i⁺ + n_i⁻ = 32,000,

where n_i^± counts point i's cross-frame partners at ±1/16. Constancy of the row sums now depends on the *signed*
excess s_i := n_i⁺ − n_i⁻ being the same at every point.

**The aggregate census does not establish this.** It gives only Σ_i n_i⁺ = 548,352,000 and Σ_i n_i⁻ = 483,840,000, hence
Σ_i s_i = 64,512,000 and a *mean* s̄ = 64,512,000 / 32,256 = **2,000**. That the division comes out to an integer is
consistent with constancy, not proof of it. The corpus contains no per-point signed census. So the sketch's step (ii),
read literally as "verify from the census", has a hole at every odd degree. It is closed as follows.

**Lemma (equal frame sums).** Let m_a := Σ_{i ∈ F_a} x_i for a = 1, …, 126, and M := Σ_{i=1}^{N} x_i = Σ_a m_a. Then
all 126 frame sums are equal: m_a = m for every a, with ‖m‖ = 16.

*Proof.* Each frame is an orthonormal basis (§3.2.1), so ‖m_a‖² = Σ_{i,j ∈ F_a} ⟨x_i,x_j⟩ = 256·1 + 0 = 256, giving
‖m_a‖ = 16 for every a. Next, from the census,

    ‖M‖² = Σ_{i,j} ⟨x_i,x_j⟩
         = 1·(32,256) + 0·(8,225,280) + (1/16)·(548,352,000) + (−1/16)·(483,840,000)
         = 32,256 + 34,272,000 − 30,240,000
         = 4,064,256,

and 4,064,256 = 2016² exactly (2000² + 2·2000·16 + 16² = 4,000,000 + 64,000 + 256). So ‖M‖ = 2016. But
Σ_a ‖m_a‖ = 126 × 16 = **2016** as well. The triangle inequality ‖Σ_a m_a‖ ≤ Σ_a ‖m_a‖ therefore holds with equality
for 126 nonzero vectors, which forces them all to be non-negative multiples of one common unit vector; having equal
norms, they are all equal. ∎ [D]

**Corollary (constant signed fingerprint).** For every i, ⟨x_i, M⟩ = 126, and therefore s_i = 2,000, i.e.
n_i⁺ = 17,000 and n_i⁻ = 15,000 at **every** point of the base set.

*Proof.* Let x_i ∈ F_a. Since m_a = Σ_{j∈F_a} x_j and F_a is orthonormal, ⟨x_i, m_a⟩ = 1. By the Lemma every m_b equals
m = m_a, so ⟨x_i, M⟩ = Σ_b ⟨x_i, m_b⟩ = 126·⟨x_i, m_a⟩ = 126. On the other hand, expanding by the fingerprint,
⟨x_i, M⟩ = Σ_j ⟨x_i,x_j⟩ = 1 + 255·0 + s_i/16. Setting 1 + s_i/16 = 126 gives s_i = 2,000, and with
n_i⁺ + n_i⁻ = 32,000, n_i⁺ = 17,000 and n_i⁻ = 15,000. ∎ [D]

Note what just happened: the aggregate census's per-point *averages* (17,000 and 15,000) turn out to be the per-point
*values*, but that is a theorem, not a division. The proof needed the frame structure, not just the multiset of inner
products.

Two further facts fall out of the same arithmetic and are used later:

- **The base set contains no antipodal pair.** No inner product in the census equals −1, so −x_i ∉ X for every i, and
  |Y| = 64,512 exactly [D]. The doubling is a genuine doubling.
- **The base set is not an exact 1-design.** ‖M‖ = 2016 ≠ 0; equivalently Q_1(u) = ‖M‖²/N² = 4,064,256 / 32,256² =
  **1/256** = 126/N, i.e. 126× the iid degree-1 error 1/N [D]. Odd degrees on the base set are bad, which is precisely
  why the estimator uses Y. This is not a defect of the theorem — uniform is still optimal at ℓ = 1 on X, it is just
  optimal at a large value.

Combining §3.2 and §3.3: **K_ℓ 1 = c_ℓ 1 for every ℓ ≥ 1, on X**, with

    c_ℓ = 1 + 255·G_ℓ(0) + 32,000·G_ℓ(1/16)     (ℓ even),
    c_ℓ = 1 + 2,000·G_ℓ(1/16)                    (ℓ odd).

Sanity check at ℓ = 1: G_1(t) = t, so c_1 = 1 + 2000/16 = 126, and Q_1(u) = c_1/N = 126/32,256 = 1/256 — matching the
independent computation of ‖M‖² above [D, two ways].

### 3.4 Step (iii): the constraint annihilates the linear term

Let w = u + δ with 1ᵀw = 1, hence 1ᵀδ = 0. Since u = 1/N,

    uᵀ K_ℓ δ = (1/N)·1ᵀ K_ℓ δ = (1/N)·(K_ℓ 1)ᵀ δ = (c_ℓ/N)·1ᵀδ = 0.

(K_ℓ is symmetric, so 1ᵀK_ℓ = (K_ℓ1)ᵀ.) Therefore

    Q_ℓ(u + δ) = uᵀK_ℓu + 2 uᵀK_ℓδ + δᵀK_ℓδ = Q_ℓ(u) + δᵀ K_ℓ δ,

and δᵀK_ℓδ ≥ 0 by §3.1. Hence Q_ℓ(w) ≥ Q_ℓ(u) for every w ∈ **W** and every ℓ ≥ 1, with equality iff K_ℓ δ = 0.
Summing against the non-negative coefficients ‖f_ℓ‖² of (MASTER) gives the pointwise-in-f form of the theorem. ∎ [D]

The whole content of the proof is the vanishing of one cross term. Everything else is positive semidefiniteness.

### 3.5 The three shells, exactly: 1 + 125 + 32,130 = 32,256

For even ℓ the row-sum computation of §3.2 upgrades to a full eigendecomposition. Let F ∈ R^{N×126} be the frame
indicator matrix, (F)_{i,a} = 1 iff x_i ∈ F_a. Then (FFᵀ)_{ij} = 1 iff i and j share a frame, and with a_ℓ = G_ℓ(0),
b_ℓ = G_ℓ(1/16),

    K_ℓ = (1 − a_ℓ)·I + (a_ℓ − b_ℓ)·FFᵀ + b_ℓ·11ᵀ .

Check the three entry classes: diagonal (1−a_ℓ) + (a_ℓ−b_ℓ) + b_ℓ = 1 = G_ℓ(1) ✓; within-frame off-diagonal
(a_ℓ−b_ℓ) + b_ℓ = a_ℓ ✓; cross-frame b_ℓ ✓. This is S6's committed form `K = (1−g₀)I + (g₀−g₁)FFᵀ + g₁·11ᵀ` [R,
`S6_VERDICT.md` §"Degree-4 spectrum"]. FFᵀ has eigenvalue 256 on span(F) (dimension 126, since the 126 indicator
columns are linearly independent) and 0 on its orthocomplement; 11ᵀ has eigenvalue N on span(1) ⊂ span(F) and 0
elsewhere. So K_ℓ has exactly three eigenspaces:

| shell | eigenvector space | dim | eigenvalue of K_ℓ |
|---|---|---:|---|
| **constant** | span(1) | **1** | λ_top^{(ℓ)} = (1−a_ℓ) + 256(a_ℓ−b_ℓ) + N·b_ℓ = 1 + 255a_ℓ + 32,000b_ℓ |
| **frame-contrast** | span(F) ⊖ span(1) | **125** | λ_mid^{(ℓ)} = (1−a_ℓ) + 256(a_ℓ−b_ℓ) = 1 + 255a_ℓ − 256b_ℓ |
| **within-frame** | span(F)^⊥ | **32,130** | λ_bulk^{(ℓ)} = 1 − a_ℓ |

1 + 125 + 32,130 = **32,256** [D], and 32,130 = 126 × 255 [D]. This is the exact decomposition S6 reports as
multiplicities (1, 125, 32,130) [O, `s6_results.json` `deg4.closed_form.mult`].

**Reading the shells as reweighting classes.** The three shells are exactly the three kinds of weight change available:
span(1) is the direction the sum-one constraint forbids; the 125-dimensional frame-contrast shell is precisely
*per-frame* reweighting (weights constant within each frame, summing to one across frames); the 32,130-dimensional
within-frame shell is *per-point* reweighting orthogonal to the frames. Every admissible δ is a sum of the last two.

### 3.6 Degree 4 in exact rational arithmetic

S6 commits the exact Gegenbauer data: C₄^(127)(t) = 181,742,080·t⁴ − 4,194,048·t² + 8,128 and C₄^(127)(1) =
177,556,160 [O, `s6_results.json` `constants`]. Then

    g₀ := G₄(0)    = 8128 / 177,556,160    = **1/21,845**        = 4.5777065690089265e-05
    g₁ := G₄(1/16) = (181,742,080/65,536 − 4,194,048/256 + 8,128)/177,556,160
                   = (−701,675/128)/177,556,160
                   = **−65/2,105,344**     = −3.087381444552529e-05

Both float values match `s6_results.json` `constants.G4_at_0` and `G4_at_1/16` to every printed digit [D vs O].

**The 129-spread identity.** In rationals,

    1 + 255·g₀ + 32,768·g₁ = 1 + 51/4,369 − 260/257 = (4,369 + 51 − 4,420)/4,369 = **0**   exactly.

(Using 21,845 = 5·17·257, 4,369 = 17·257, and 32,768·65/2,105,344 = 2¹⁵·5·13/(2¹³·257) = 260/257.) [D]

This is not a coincidence: 1 + 255g₀ + 32,768g₁ = 33,024 · Q₄(uniform on a 129-frame complete spread), and the full
129-frame real MUB spread (33,024 lines, 66,048 points) is an exact spherical 5-design with degree-4 error exactly
zero [R, `sources/research_designs_quadrature_20260810.md` §Q2, "derived, exact rational arithmetic"]. The theorem's
arithmetic and that brief's arithmetic are the same identity seen from two sides — an independent cross-check of both.

Substituting into §3.5 and simplifying with the identity:

    λ_top^{(4)}  = 1 + 255g₀ + 32,000g₁ = −768·g₁   = **195/8,224**      = 0.0237110894941634
    λ_mid^{(4)}  = 1 + 255g₀ −   256g₁ = −33,024·g₁ = **8,385/8,224**    = 1.0195768482490273
    λ_bulk^{(4)} = 1 − g₀                            = **21,844/21,845** = 0.9999542229343099

Note 768 = 3 × 256 = the points of the **three missing frames**, and 33,024 = 129 × 256 = the points of the complete
spread. The 126-frame set's degree-4 error is exactly the three frames it does not have.

Dividing by N = 32,256 gives the A-operator shells S6 commits (`deg4.closed_form`, [O]):

| shell | this paper (exact / float) | S6 committed | agreement |
|---|---|---|---|
| λ_top/N | 65/88,424,448 = 7.350908201315546e-07 | `lam_top` 7.350908201315546e-07 | every digit |
| λ_mid/N | 3.160890526565685e-05 | `lam_mid` 3.160890526565685e-05 | every digit |
| λ_bulk/N | 3.100056494712022e-05 | `lam_bulk` 3.100056494712022e-05 | every digit |

**Q₄(u) = λ_top/N = 65/88,424,448 = |g₁|/42 = 7.350908201315546e-07.** Third independent tie: S6's exact pairwise kernel
sum `deg4.S1_sum_G4` = 764.8249027237362 gives Q₄(u) = S1/N² = 7.350908201315552e-07, agreeing to 1 part in 10¹⁵ [O+D].

**Positive definiteness at degree 4.** All three eigenvalues are strictly positive (195/8,224 > 0, 8,385/8,224 > 0,
21,844/21,845 > 0), so K₄ ≻ 0 and δᵀK₄δ > 0 for every δ ≠ 0. Uniform is the **unique** minimiser of Q₄ over **W** [D].

**Degree 6, as an independent check of the machinery.** S6 commits G₆(0) = −8.837271368743101e-07 and G₆(1/16) =
9.534594054985972e-07 [O]. Feeding those floats into the §3.5 formulas:

| shell | this paper | S6 `deg6.closed_form` |
|---|---|---|
| λ_top/N | 3.1940890084203014e-05 | 3.194089008420301e-05 |
| λ_mid/N | 3.098743067870441e-05 | 3.098743067870441e-05 |
| λ_bulk/N | 3.10020115242788e-05 | 3.10020115242788e-05 |

All three reproduce to the last digit, from a general-ℓ formula S6 never printed [D vs O]. All three are positive, so
uniform is the unique minimiser at degree 6 too.

### 3.7 The price of reweighting: 43.3× and 42.5×

Fix a degree and write w = u + δ, δ = δ_F + δ_P with δ_F in the frame-contrast shell and δ_P in the within-frame shell.
By §3.4 and §3.5,

    Q_ℓ(w) = Q_ℓ(u) + λ_mid^{(ℓ)}·‖δ_F‖² + λ_bulk^{(ℓ)}·‖δ_P‖²,   and   Q_ℓ(u) = λ_top^{(ℓ)}/N.

To make the perturbation scale-free, measure it in units of the uniform weight. Put

    η := (1/N) Σ_i (δ_i / u_i)² = N·‖δ‖² ,

so η is the **mean-square fractional change** in the weights (η = 10⁻⁴ is a 1 % RMS reweighting). Then for a pure
perturbation of one shell,

    Q_ℓ(u + δ) / Q_ℓ(u) = 1 + η · ( λ_shell^{(ℓ)} / λ_top^{(ℓ)} ).

The bracket is the **price**. At degree 4, in exact rationals:

    per-frame  price = λ_mid/λ_top  = (8,385/8,224)/(195/8,224) = 8,385/195 = **43** exactly
    per-point  price = λ_bulk/λ_top = (21,844/21,845)/(195/8,224) = 699,008/16,575 = **42.17242835595777**

The exact 43 is the 129-spread identity again: λ_mid = −33,024·g₁ and λ_top = −768·g₁, and 33,024/768 = 43.

**In S6's committed normalisation.** S6 reports the *deviation operator* D = A − I/m₄, whose shells are
μ = λ/N − 1/m₄ with 1/m₄ = 5.460050774104158e-09 [O]. From S6's `deg4.closed_form` values verbatim:

    per-frame price = μ_mid/μ_top  = 3.1603445214882744e-05 / 7.296307693574504e-07 = **43.3142988784784**
    per-point price = μ_bulk/μ_top = 3.0995104896346116e-05 / 7.296307693574504e-07 = **42.480534262065134**

i.e. **43.3×** and **42.5×**. The two normalisations differ by 0.7 %, entirely because of the −1/m₄ orthocomplement
sea, which is 0.74 % of λ_top/N and negligible against λ_mid, λ_bulk. Both are quoted here because the campaign's
headline "42×" is the D-shell ratio [R, S6 §"Degree-4 spectrum": "top-1 … 42× below bulk"; P1 §Pillar 1].

**The punchline.** The 42× Bragg suppression and the price of reweighting are the same number. S6 discovered that the
design suppresses exactly one mode — the quadrature functional — 42× below the bulk. That mode is exactly the one the
unbiasedness constraint forbids you to move in. Every direction the weights *can* move in is one of the unsuppressed
shells, and therefore costs 42–43× the error you are trying to remove, per unit of mean-square reweighting. A 10 % RMS
reweighting (η = 0.01) inflates the degree-4 error by 43 % (per-frame) or 42 % (per-point) [D].

**Honest refinement: the 43× price is a degree-4 phenomenon only.** At degree 6 the same formulas give
λ_mid/λ_top = 0.9701 and λ_bulk/λ_top = 0.9706 [D], because the constant mode there is *not* suppressed
(N·λ_top^{(6)} = 1.0303, i.e. above iid) [O, S6 §"Degree-6 repeat"; R0 §1 table]. R0's committed error budget puts
0.45 % of the estimator's MSE at degree 4 and 99.55 % at even degrees ≥ 6 [O,
`experiments/r0_harmonic_energy_spectrum/R0_HARMONIC_SPECTRUM.md` §5]. So the *inequality* Q_ℓ(w) ≥ Q_ℓ(u) is
unconditional at every degree, but the *steepness* is not: for the error the champion actually pays, reweighting is
priced at roughly par (≈1× per unit η), not 43×. Anyone quoting "43× penalty for reweighting" as an operational number
is quoting the degree-4 figure for a degree-4 sliver of the error. The optimality is exact; the deterrent is degree-4
local.

### 3.8 Two corollaries that come free

**Corollary 1 (frame potential / tr(D²)).** Let A_w = Σ_i w_i φ_iφ_iᵀ be the weighted degree-ℓ moment operator, so that
tr(A_w) = Σ_i w_i = 1 and tr(D_w²) = tr(A_w²) − 1/m_ℓ with tr(A_w²) = Σ_{i,j} w_i w_j G_ℓ(t_ij)² [R, S6
§"Normalization"]. The matrix K_ℓ ∘ K_ℓ = [G_ℓ(t_ij)²] is PSD by the Schur product theorem, and its row sums are
1 + 255·G_ℓ(0)² + 32,000·G_ℓ(1/16)² — constant at **every** degree without any sign argument, since squaring erases the
sign. The identical three-line argument therefore gives: **uniform weights also minimise tr(D_w²) over W, at every
degree** [D]. The design is not only the best-weighted quadrature rule on its own points; it is also the tightest frame
its own points can carry.

**Corollary 2 (sub-spread scaling, and why fragmentation costs).** For any k-frame subset of a 129-frame complete real
MUB spread (N_k = 256k points), the same census algebra gives, using 1 + 255g₀ = −32,768·g₁,

    Q₄(uniform on k frames) = (1/N_k)[1 + 255g₀ + 256(k−1)g₁] = |g₁| · (129 − k)/k .

Check at k = 126: |g₁|·3/126 = |g₁|/42 = 7.350908201315546e-07 ✓, and at k = 129 it is exactly 0 ✓ [D]. So a 63-frame
half-spread has 44× the degree-4 error of the full 126, and a 42-frame third has 87×. Averaging two independently
rotated 63-frame halves at equal weight (cross terms vanish in Haar expectation) gives 44/2 = **22×**; three
independently rotated 42-frame groups give 87/3 = **29×** [D]. Folded through R0's committed error budget (degree 4 at
0.45 %, degree 6 at 13.82 %, whose sub-spread ratio is 0.985 for k = 63 and 0.980 for k = 42), the predicted overall
penalties are **≈ 1.09** (two halves) and **≈ 1.12** (three thirds) [D]. Measured: M195's uncorrected two-half
diagnostic 1.29790 / 0.865509 / 1.23066 [O], M197's uncorrected three-group diagnostic 1.783449 / 0.976651 / 1.242740
[O], M180 arm C k = 2 at 1.2801 [O]. **The corollary under-predicts.** It accounts for the sign and the order of
magnitude but not the size; roughly a third to a half of the measured fragmentation penalty is not degree-4 sub-spread
loss. M180's own note names the missing piece — "the design's strength is the mutual unbiasedness of all 126 frames
under ONE shared rotation (inter-frame negative covariance)" [R] — and this paper does not quantify it. Recorded as an
open item, not as an explanation.

---

## 4. What this closes

Strict criterion, as commissioned: **a record is DERIVED only if its mechanism is a fixed-direction reweighting subject
to sum-one.** Two things must both hold for a derivation: the mechanism must be a reweighting of a fixed point set under
the sum-one constraint, *and* the criterion being optimised must be one the theorem covers — a zonal, rotation-averaged
error functional of the form Σ_ℓ a_ℓ Q_ℓ(w) with a_ℓ ≥ 0. The second condition is where all six records fall out.

| ledger id | mechanism is fixed-direction sum-one reweighting? | criterion is zonal? | verdict |
|---|---|---|---|
| `m192_cross_output_frame_gls_oracle` | **yes** — sum-one GLS over the 126 fixed Kerdock frames | **no** — realised truth-trained cross-output covariance | **not derived**; its baseline and its disclaimer are derived |
| `m193_analytic_anchor_frame_gls` | **yes** — same weight class, analytic anchor | **no** — anchor-contaminated realised covariance | **direction derived, magnitude not** |
| `m194_independent_pilot_block_gls` | partly — reweights the 126, but buys extra pilot points | no | **not derived** |
| `m195_symmetric_half_design_attenuation` | **no** — two independently rotated 63-frame half-designs; different point set | no | **not derived** |
| `m197_crossed_three_rotation_u_statistic` | **no** — three independent rotations × 42 frames; different point set | no | **not derived** |
| `s2_paid_information_rotation_weighting` | partly — sum-one weights over K rotations, directions redrawn per rotation | no | **null derived (by exchangeability), kill not derived** |

Detail, record by record, each with its measured number.

**`m192_cross_output_frame_gls_oracle` — screened, panel geomean ratio 0.126193 (87.38 % reduction), per-net 0.146840 /
0.095677 / 0.143037, 48/48 rotations improve [O, ledger; `m192_g0_results.json`].** The mechanism qualifies exactly:
sum-one weights on the 126 fixed frames. The criterion does not. M192 learns the error covariance from *realised* truth
on training output neurons, which is not a function of the design's inner products. The theorem is therefore not
contradicted by an 87 % reduction — and it says something sharper than "not contradicted". In the M192/M193 algebra
(`M192_M195_NOTES.md`; `m192_selfanchor_twosided/VERDICT.md` §Step 0), the constrained-GLS solution is
w* = 1/p − (1/√p)(PCP)⁺ P C u, so w* = uniform **iff** b := P C u = 0, i.e. iff 1 is an eigenvector of C. This paper
proves that under any zonal model for the target, the frame-error covariance has constant row sums and hence b = 0
exactly. **Derived: 100 % of M192's oracle headroom is non-design information.** That is precisely what M192's own
ledger entry asserted without proof ("The fixed-reweighting certificate is not contradicted because these weights
depend on other realized outputs") and what its predeclaration cited as given ("The fixed-reweighting certificate
proves uniform weights for a zonal kernel with weights fixed independently of the realized network outputs"). The
citation now has a referent. **Status: previously an unproved certificate cited three times; now a proof. Not an
empirical kill and not upgraded to one — M192 remains a screen survivor.**

**`m193_analytic_anchor_frame_gls` — KILLED, panel ratio 1057.899, per-net 1530.06 / 1108.71 / 697.92, median weight L1
inflated to 5.76 [O, ledger].** Same weight class, so the theorem applies to its design-side component and says the
design-side value of every deviation M193 made was exactly zero: all of it was cost, none of it was signal. The
*direction* of the kill is derived. The *magnitude* is not: 1057.899 is dominated by analytic-anchor bias (anchor MSE
6.09e-4 to 1.88e-3 against frame errors orders smaller [R]), which is outside the theorem. An illustrative bound —
median L1 5.76 over 126 frames implies ‖δ_frame‖₂ ≳ 0.424, hence η ≳ 22.7, hence a degree-4 inflation ≳ 975× — lands
suspiciously close to the measured 1057.899, and this paper **declines to claim the agreement**: the degree-4 price of
43 applies to 0.45 % of the error (§3.7), so the theorem's own budget predicts an overall inflation nearer 1 + η ≈ 24×,
not 975×. The near-match is not derived and is recorded here only so a future session does not rediscover it and
mistake it for a mechanism. **Status: empirical kill; its inevitability-in-direction is now proved, its size is not.**

**`m194_independent_pilot_block_gls` — KILLED at finite-output SNR, panel raw ratio 15.8306, cost ratio 16.8357, pilot
cross-noise ≈ 5× the true cross signal at the median [O, ledger].** Not derived. The theorem says no zonal source can
supply b; M194's failure is that its *non*-zonal source (an 8-frame Haar pilot) supplies b too noisily. The frozen
pilot-prefix autopsy (k = 1/8/64/126 → raw 97.600 / 15.831 / 1.525 / 0.671, cost-adjusted never below 1.343 [O]) is a
statement about pilot precision and cost, on which this paper is silent.

**`m195_symmetric_half_design_attenuation` — KILLED, panel ratio 1.15748 [O, ledger].** Not derived: M195 pairs rotation
r with rotation r+8 and takes 63 frames from each [R, `M195_SYMMETRIC_HALF_PREDECLARATION.md`], so the evaluated point
set is not the champion's design and no reweighting statement applies. Corollary 2 (§3.8) speaks to its *diagnostic*
comparator (the uncorrected two-half mean at 1.29790 / 0.865509 / 1.23066) and under-predicts it at ≈ 1.09. Partial,
and labelled partial.

**`m197_crossed_three_rotation_u_statistic` — KILLED, panel ratio 1.368804, bootstrap [1.072507, 1.824979] [O,
ledger].** Not derived, for the same reason: three independent rotations × 42 frames is a different design. The
ledger's own diagnosis — "Failure is split-design geometry plus cross-block noise, not algebra" — is the correct one and
is untouched here. Corollary 2 predicts ≈ 1.12 against the measured uncorrected 1.783449 / 0.976651 / 1.242740;
under-predicts again.

**`s2_paid_information_rotation_weighting` — KILLED at G0-CORRELATION, pooled within-net |ρ| = 0.122, bootstrap
[−0.153, +0.375], per-net +0.106 / −0.297 / +0.556, closed-form infinite-split proxy +0.047 [O, ledger;
`experiments/s2_paid_weighting/S2_VERDICT.md`].** Half-derived, and the honest half is the *null*. S2 splits budget
across K rotations and combines by split-sample inverse-variance weights summing to one. The directions are redrawn per
rotation, so the census plays no role — but the same **lemma** does, with the eigenvector supplied by a different
symmetry: K iid Haar rotations are exchangeable, so their error covariance C has constant diagonal and constant
off-diagonal, hence C1 ∝ 1, hence b = P C u = 0, hence the constrained optimum is equal weights [D]. **Derived: absent
realised per-rotation information, equal weights are exactly optimal — S2 had nothing to beat except the realised
signal.** S2 then measured that signal at |ρ| = 0.122 against a 0.40 gate. The kill is that measurement, and it is a
statement about information availability, not symmetry. S2's own durable finding — "the deterministic Kerdock
equidistribution error is INVISIBLE to iid-style variance statistics of the design sample itself", paid-sample proxies
spreading only 1.40–1.48× while realised MSE spreads 3.9–12.0× [O] — is a distinct phenomenon and is neither derived
nor superseded here. **Status: empirical kill; its baseline is now proved, its kill is not.**

**Tonight's `m192_selfanchor_twosided` — KILLED at step 0, all three nets 1.0 to within 1.5e-14, max |w − 1/126| =
1.46e-15, A2 self-anchor cross-block norm median 4.12e-19 against 1.26e-05 under the truth anchor (ratio 3.26e-14) [O,
`experiments/m192_selfanchor_twosided/VERDICT.md`, `results.json`]. Is it an instance of this theorem?**

**No — it is a sibling, and that makes it a genuine second signal rather than a duplicate.** Both results are instances
of one lemma: *for a PSD C with C1 ∝ 1, the sum-one-constrained GLS optimum is uniform.* They differ in where the
eigenvector comes from.

- This paper supplies C1 ∝ 1 from the **design's geometry**: the census plus the equal-frame-sum lemma force constant
  row sums in K_ℓ at every degree, so any zonal criterion has uniform as its optimum. The zero is a property of the
  point set and holds before any data exists.
- M192-SELFANCHOR supplies it from an **estimator identity**: self-anchoring at a_j = (1/p)1ᵀx_j makes the residual
  r_j = P x_j, so C_a = P C_e P and C_a 1 = 0 identically — "the anchor contamination and the signal cancel term for
  term" [R, VERDICT.md §Step 0]. The zero is a property of the *construction*, holds for any point set, and would hold
  if the design were random.

So the two are independent routes to the same fixed point, and the coincidence of their conclusions is evidence for the
lemma rather than a restatement of it. One further alignment worth recording: SELFANCHOR's isolation experiment (true
A with true b → 0.126193; true A with b = 0 → 1.000000) establishes that **the 126×126 contrast block A contributes
nothing on its own under sum-one; it is only the metric that converts b into a weight direction** [O]. This paper adds
the complementary half: the design's own contribution to b is exactly zero, at every degree, forever. Together they say
that the entire M192 family lives or dies on one 126-vector, b = P C_e 1/√126, whose median realised norm is 1.26e-05
[O] — and that no property of the design can move it.

**What is superseded rather than derived.**

1. **`sources/research_designs_quadrature_20260810.md` §Q3.2 is superseded, and one of its sub-claims is corrected.**
   Q3.2 argues: "if Aut(X) is transitive on points (true for spread-symmetric frame sets), averaging any weight vector
   over Aut(X) never increases the (convex, Aut-invariant) error functional, so an optimal weighting exists that is
   Aut-invariant = constant." That argument is sound but rests on an unverified hypothesis (transitivity of Aut(X)),
   yields only *existence* of a uniform optimum rather than optimality of uniform, and the brief itself hedges the
   consequence: "Per-frame weights only matter if the 126 frames split into inequivalent Aut-orbits (plausible for
   126-of-129 — the 3 missing frames break symmetry)." This paper replaces the hypothesis with a *verified* and strictly
   weaker fact — constant row sums, proved from the committed census — and removes the hedge: per-frame weights never
   help, orbit structure or not. It also **corrects** the sentence that follows: "LP over ≤ a few frame-orbit weight
   classes zeroing the ×1 and ×125 shells is a 2-constraint linear solve — could kill both non-bulk shells of the deg-4
   operator." It could not. The ×1 shell *is* the quadrature functional, Q₄(u) = λ_top/N; §3.4 shows no admissible
   reweighting reduces it at all, let alone zeroes it. The correction also removes an internal inconsistency in the same
   section: Q3.1 already states, from the DGS/Möller dimension bound, that "no weighting of our 126 frames achieves
   exact deg-4" [R]. This paper strengthens Q3.1 from *cannot reach zero* to *cannot improve at all*.
2. **The F4 SYMMETRY family's positive dual is now proved for its reweighting half.** `FAILURE_MODE_GRAPH_20260810.md`
   row 4, P1 §3.1 and P3's failure table all carry F4 with the justification "design is a group orbit → LP-optimal
   weights are uniform; perturbations break the exact 2-design" and the positive dual "the design is provably optimal"
   [R]. The reweighting half of that claim is now proved without the orbit hypothesis. The perturbation half —
   `m180_design_strength_g0`, TOTAL KILL with all arms increasing variance (B 1.3135, C k = 2/4/8 at 1.2801 / 1.1962 /
   1.4879, D 1.4194) [O, ledger] — is **not** covered: M180 moves the points, and this paper's theorem holds the points
   fixed. F4's design-mutation half remains an empirical kill.

**Summary of retroactive status changes.** Nothing that was an empirical kill is upgraded to a proof by this paper. What
changes is: one repeatedly cited "certificate" acquires a proof; one hedged derivation is replaced by an unhedged one
and one of its sub-claims is retracted; and four records (M192, M193, S2, M192-SELFANCHOR) acquire a proved baseline
that explains what they were measuring against.

---

## 5. Scope: what this does not claim

**5.1 It is not a statement about designs, only about weights on one.** Every claim holds the point set fixed. Changing
the points — M180's mixes and remixes, M195's half-designs, M197's thirds, the 129-frame completion — is outside it. In
particular the theorem does **not** say the Kerdock design is the best design; the completion to 129 frames is
strictly better at degree 4 (error exactly 0 versus 7.35e-07) at +2.4 % points [R, `research_designs_quadrature` §Q2],
and this paper's own identity 1 + 255g₀ + 32,768g₁ = 0 is that fact restated.

**5.2 It is not a statement about non-zonal criteria, which is exactly why M192 survives it.** The theorem covers
criteria of the form Σ_ℓ a_ℓ Q_ℓ(w), a_ℓ ≥ 0 — equivalently, any criterion that is a function of the design's inner
products alone. M192's 87.38 % oracle reduction optimises a *realised* covariance learned from other output neurons of
one specific network; that object is not a function of the inner products, and no result here bounds it. The theorem's
content there is negative and structural: the design cannot contribute to it.

**5.3 Uniqueness is base-set-only.** On X, K₄ ≻ 0 makes uniform the unique minimiser. On the doubled set Y the even-ℓ
kernel matrix has the block form J₂ ⊗ K (since G_ℓ(−t) = G_ℓ(t)), whose kernel contains every antipodally
*antisymmetric* weight perturbation; those are free at every even degree and cost only at odd degrees, which the design
already integrates exactly. So on Y the minimum is attained on a 32,256-dimensional affine set containing u. Uniform is
*a* minimiser on Y, not *the* minimiser. Since the champion's whole error is even-degree (odd degrees annihilated by
antipodal pairing [R, R0 §1]), this is a real non-uniqueness, not a technicality — it just buys nothing.

**5.4 The odd-degree clause on the base set rests on §3.3, not on the census alone.** If the equal-frame-sum lemma is
wrong — the only way being a census value this paper has mis-transcribed — every odd degree on X reopens. The lemma is
sharp (equality in a triangle inequality), so it is either exactly right or exactly wrong; falsifier (ii) in §2 settles
it with one per-point count. No such per-point count exists in the corpus. **[GAP-CLOSED-BY-PROOF, not by measurement:
the corpus contains no per-point signed census; the constancy of n_i⁺ = 17,000 is derived here and has never been
directly observed.** The settling check is one pass over the design computing the signed cross-frame histogram per
point, ~10 s of the same arithmetic S6 already ran; it was not run here because this paper is firewalled to committed
evidence.]

**5.5 The 43× / 42.5× prices are degree-4 numbers.** §3.7 states this plainly: the inequality holds at every degree, the
steep price does not. Against the error the champion actually pays, reweighting is priced near par. Any future writeup
quoting "43× penalty" as the operational deterrent is over-claiming; the operational deterrent is that the gain is
exactly zero, which is a stronger statement anyway.

**5.6 Nothing here concerns the estimator's other axes.** The theorem is silent on rotation choice, on cost/FLOP
accounting, on seed-side extraction (P1 §4.5), and on every output-side estimator class. It closes one door — the
weights — completely, and touches no other.

**5.7 Two constants are taken on report, not re-derived.** The Gegenbauer coefficients for degree 6 are used only as
S6's committed floats (G₆(0), G₆(1/16)); the exact C₆^(127) recurrence is not re-run here, so the degree-6 shell values
in §3.6 are [D from R], not [D from exact rationals] as degree 4 is. And dim H_4 = 183,148,480 is quoted from S6, which
cross-checked it two ways [O].

---

## 6. Reproduction map

Paths relative to the corpus root
`C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\publish\recursive-estimator-folding\corpus\whestbench`.

| claim | number | artifact |
|---|---|---|
| inner-product census, all 32,256² pairs, max grid deviation 0.0 | 32,256 / 8,225,280 / 548,352,000 / 483,840,000 | `experiments/s6_bragg_spectrum/s6_results.json` → `fingerprint.distinct_values`, `within_frame`, `cross_frame` |
| census sums to N² | 1,040,449,536 | arithmetic, §3.2 |
| exact Gegenbauer data at degree 4 | coeffs [8128, −4194048, 181742080], C₄(1) = 177,556,160 | `s6_results.json` → `constants` |
| G₄(0), G₄(1/16) | 4.5777065690089265e-05, −3.087381444552529e-05 | `s6_results.json` → `constants.G4_at_0`, `G4_at_1/16` |
| exact rational forms | g₀ = 1/21,845, g₁ = −65/2,105,344 | derived §3.6 from the two rows above |
| 129-spread identity | 1 + 255g₀ + 32,768g₁ = 0 | derived §3.6; independently `sources/research_designs_quadrature_20260810.md` §Q2 |
| ‖Σx_i‖² and ‖Σx_i‖ | 4,064,256 and 2016 | derived §3.3 from the census |
| per-point signed fingerprint | n⁺ = 17,000, n⁻ = 15,000, s = 2,000 | derived §3.3 (never directly observed — see §5.4) |
| three shells and multiplicities | 1 / 125 / 32,130 = 32,256 | derived §3.5; multiplicities match `s6_results.json` → `deg4.closed_form.mult` |
| degree-4 A-shells | 7.350908201315546e-07 / 3.160890526565685e-05 / 3.100056494712022e-05 | derived §3.6; `s6_results.json` → `deg4.closed_form.lam_top/lam_mid/lam_bulk` |
| Q₄(u) exact | 65/88,424,448 = \|g₁\|/42 | derived §3.6; third tie via `deg4.S1_sum_G4` = 764.8249027237362 |
| degree-4 D-shells | 7.296307693574504e-07 / 3.1603445214882744e-05 / 3.0995104896346116e-05 | `s6_results.json` → `deg4.closed_form.mu_top/mu_mid/mu_bulk`; 1/m₄ = 5.460050774104158e-09 |
| prices (A-normalisation) | 43 exactly; 699,008/16,575 = 42.17242835595777 | derived §3.7 |
| prices (S6 D-normalisation) | 43.3142988784784; 42.480534262065134 | derived §3.7 from the committed μ row above |
| degree-6 shells, machinery check | 3.1940890084203014e-05 / 3.098743067870441e-05 / 3.10020115242788e-05 | derived §3.6; `s6_results.json` → `deg6.closed_form` |
| N·λ_top by degree (odd ≡ 0 on Y) | ℓ = 4: 0.02371, ℓ = 6: 1.03029, ℓ ≥ 8: 1.0000 | `experiments/r0_harmonic_energy_spectrum/R0_HARMONIC_SPECTRUM.md` §1, `r0_results.json` |
| error budget by degree | deg 4 = 0.45 %, even ℓ ≥ 6 = 99.55 %, max single degree 13.8 % | `R0_HARMONIC_SPECTRUM.md` §5 |
| doubled census, bitwise | 64,512 + 64,512 + 32,901,120 + 4,128,768,000 = 4,161,798,144 = 64,512² | derived §5.3; `experiments/s17_ibc_floor/s17_results.json` §A.1 |
| M192 oracle ratios | 0.126193 panel; 0.146840 / 0.095677 / 0.143037 | `experiments/m192_cross_output_gls/m192_g0_results.json`; ledger `m192_cross_output_frame_gls_oracle` |
| M193 kill | 1057.899 panel; 1530.06 / 1108.71 / 697.92 | `m193_g0_results.json`; ledger `m193_analytic_anchor_frame_gls` |
| M194 kill | 15.8306 raw / 16.8357 cost | `m194_g0_results.json`, `M194_PILOT_SCALING_AUTOPSY.md` |
| M195 kill and diagnostic | 1.15748 panel; uncorrected 1.29790 / 0.865509 / 1.23066 | `m195_g0_results.json`, `M195_SYMMETRIC_HALF_PREDECLARATION.md` |
| M197 kill and diagnostic | 1.368804 panel; uncorrected 1.783449 / 0.976651 / 1.242740 | `experiments/m197_crossed_three_rotation/` |
| S2 kill | within-net \|ρ\| = 0.122, CI [−0.153, +0.375] | `experiments/s2_paid_weighting/S2_VERDICT.md`, `s2_results.json` |
| M192-SELFANCHOR kill | panel 1.0000000000000073; max \|w − 1/126\| = 1.46e-15; cross-block 4.12e-19 vs 1.26e-05 | `experiments/m192_selfanchor_twosided/VERDICT.md`, `results.json` |
| M180 design-mutation kill | B 1.3135; C 1.2801 / 1.1962 / 1.4879; D 1.4194 | ledger `m180_design_strength_g0`, `m180_g0_results.json` |
| the certificate this paper proves, as previously cited | — | `experiments/m192_cross_output_gls/M192_PREDECLARATION.md` L20, `M192_M195_NOTES.md` L35, `resources/research_excursions/M115_PROJECTIVE_ARCCOSINE_NYSTROM_THEORY_20260807.md` L173 |
| the sketch this paper supersedes and corrects | — | `sources/research_designs_quadrature_20260810.md` §Q3.1–Q3.2 |

**Firewall.** Read-only. No measurement was taken, no estimator or m245 code was executed, no network, no git, no
scorer, no private or holdout access. Every number above is either transcribed from a committed artifact with its path
or produced by rational arithmetic on such numbers, shown in the text. The only computation performed was that
arithmetic.

**Determinism note for a successor.** Every derived constant in §3.6 and §3.7 is exact rational arithmetic on integers
already committed in `s6_results.json`. Re-deriving them requires no floating point and no artifact beyond that one
file; disagreement in any digit is a transcription error, not an environment change.

---

## 7. How to falsify this paper

**Break the theorem** by exhibiting one w ∈ R^32,256 with 1ᵀw = 1 and wᵀK_ℓw < Q_ℓ(u) at any ℓ. §3.4 says this is
impossible; one dot product decides it, and the cheapest ℓ to try is 4, where every constant is exact.

**Break the hard step** by computing the per-point signed cross-frame census on the frozen design and finding any point
with n⁺ ≠ 17,000. That falsifies §3.3's lemma and reopens every odd degree on the base set (even degrees survive, since
§3.2 needs no signs). This is the paper's one derived-but-never-observed claim, and the check is cheap.

**Break the pricing** by recomputing λ_mid/λ_top from the exact rationals and finding anything other than exactly 43,
or by showing the 129-spread identity 1 + 255g₀ + 32,768g₁ = 0 fails in `Fraction` arithmetic.

**Break the closure claim** by exhibiting a committed record whose mechanism is a fixed-direction sum-one reweighting
optimising a *zonal* criterion and which nevertheless beat uniform. By §3.4 such a record would have to contain an
arithmetic error; the theorem predicts none exists, and §4 found none.

**What would NOT falsify it**: any further oracle result in the M192 family, however large. Those optimise a realised
covariance and are outside the theorem by construction — which is the whole reason the corpus was right to keep M192
as a screen survivor rather than treating it as a contradiction.
