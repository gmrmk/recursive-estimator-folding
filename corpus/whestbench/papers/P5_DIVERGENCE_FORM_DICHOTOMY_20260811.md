# P5 — The divergence-form dichotomy: every surface rewrite of a bias-free ReLU sphere-mean is either Euler or is paid for on the kink set

Internal research paper, draft 1. Date 2026-08-11. Corpus: `corpus/whestbench`. Audience: future Opus / researcher
sessions with no conversation memory. Status: **proof, with a measured pricing half that is explicitly not proved.**
Level tags follow P1 and the corpus evidence discipline (defined in P1 §0, `papers/P1_SPECKLE_THEOREM_20260810.md` lines 39-43 — the paper that introduced them; the corpus README does NOT define this scheme, contrary to draft 1): **[O]** observed (a committed
artifact in this corpus contains it, or this session read it out of committed code), **[D]** derived (follows from
observations or from stated mathematics by steps shown here), **[R]** reported (a committed artifact says so and this
paper did not re-derive it), **[A]** assumed (a stated modelling or definitional choice). Firewall: read-only. No
harness was executed, no estimator or m245 code was run, no git, no network. The only computation performed for this
paper is exact rational and floating-point arithmetic on numbers already committed; every such computation is shown
inline so it can be checked by hand.

Read `P1_SPECKLE_THEOREM_20260810.md` first for the setting and `P2_CROFTON_KINK_IDENTITY_20260810.md` for the surface
identity this paper classifies. This paper is proof-first: §3 is the point, and §3 is written to stand alone.

---

## 1. Abstract

For a bias-free ReLU network the target integral admits exactly two kinds of divergence-form rewrite, and the boundary
between them is a theorem rather than a taxonomy. Positive 1-homogeneity makes the function Lipschitz with a piecewise
constant gradient, so its second distributional derivative is a measure carried entirely by the kink set K and its
interior part is identically zero. Consequently any vector field built pointwise from `(x, f, grad f)` has a
distributional divergence whose singular part is exactly the normal jump of that field across K, and the rewrite either
has that jump or does not. **Class A** (no jump) is proved here to carry *no derivative information whatsoever*: an
elementary rigidity lemma shows the jump-free fields are affine in the gradient with an antisymmetric coefficient, and
one tangential integration by parts then collapses every such rewrite to a reweighting of point evaluations of `f`
whose entire radial content is Euler's identity. **Class B** (jump present) has a nonzero summand that is literally an
integral over K, so realizing it requires locating and integrating over K. The dichotomy is exhaustive and exclusive by
construction, and it has a one-line avatar: distributionally `Delta_S f = -(d-1) f + (facet jump measure on K)`, whose
first term is class A and whose second is class B, with no third term [D, corroborated verbatim at d = 256 by ledger
record `compact_group_laplacian_control`].

Two corrections to the thesis as it was handed to me, both material. First, **class A is not identical to the
champion's radial conditioning**; class A is the radial identity *plus* the free choice of angular quadrature, and it
is the radial part alone that the divergence-form machinery determines. Within that part, exact chi-mean conditioning
is provably the variance-minimal unbiased member (Rao-Blackwell, two lines). Second, the wc1 ablation figure of
**2.141x is the bundled design-plus-radius number, not the value of radial conditioning**; the artifact's own derived
isolated radial effect is **1.0618307996653649** [O, `wc1_results.json` `derived_isolated_ratios`], and this paper
explains why it is small by re-deriving, exactly, that the ablated arm retains the *variance-optimal degree-2 member of
the same class-A family* — the frozen constants `257`, `66563`, `2600/537689`, `3/537689` are recovered here from the
chi_256 moments with zero fitted input, and that control already removes **99.9861 %** of the radial second-moment
excess.

The pricing of class B is **measured, not proved**, and the measurement is thinner than the record list suggests. Of
five class-B records, exactly one is a clean gated efficiency kill (S9 Crofton, 176,860x, two independent
implementations), exactly one is a clean cost lower bound at target width (M86, 1.2408797549e86 FLOPs, re-derived here
to eleven digits as `2^263 x 2 x 32 x 256 x 511`), and the remaining three are compromised as efficiency evidence: M95's
39.5-556.7x is a **d = 2, depth-2 toy**, `direction_only_facet_raoblackwell`'s 556.305x sits on top of an admitted bias
failure, and `compact_group_laplacian_control` is an exact-reasoning kill with no variance measurement. A near-collision
between two of those numbers (556.709 and 556.305) in records that share no harness is flagged unresolved.

---

## 2. The statement

### 2.1 Setting

Fix `d >= 2`. Let **F_d** be the set of functions `f : R^d -> R` that are continuous, piecewise linear with finitely
many pieces, and positively 1-homogeneous (`f(tx) = t f(x)` for `t >= 0`). Every bias-free ReLU network with linear
readout is in `F_d`: `R^d` is covered by finitely many closed convex polyhedral **cones** `{C_r}` with `f = g_r . x` on
`C_r`, and the **kink set** `K` is the union of the `(d-1)`-dimensional facets separating adjacent cells, each lying in
`{h^(l)_j = 0}` for the one neuron whose gate flips there [R, P2 §1.1; the coincidence set is `H^{d-1}`-null under
generic position]. `K` is a cone: every facet passes through the origin.

Two targets, related by an exactly known constant:

- `T_S(f) = integral over S^{d-1} of f d(sigma)`, `sigma` the normalized surface measure (the sphere-mean).
- `T_G(f) = E[f(X)]`, `X ~ N(0, I_d)` (the Gaussian mean).

**L0.** `T_G(f) = m_d T_S(f)` with `m_d = E||X|| = sqrt(2) Gamma((d+1)/2) / Gamma(d/2)`.
*Proof.* Polar factorization `X = R U` with `R = ||X|| ~ chi_d` independent of `U ~ Unif(S^{d-1})`; positive
1-homogeneity gives `f(Ru) = R f(u)` pointwise for every `u`, so `E[f(X)] = E[R] E[f(U)]`. [D]

At `d = 256`, `m_256 = 15.98438266660852747777519742115107395022...` (exact, 40 dps). The frozen constant
`MEAN_CHI_256 = 15.98438266660852747` in `experiments/v31_guards/package_source/kerdock_v3_estimator.py` line 18
reproduces it to **4.9e-17 relative** — i.e. the frozen literal is correct to every digit it carries [O + D].

> **CORRECTED (draft 2).** Draft 1 read: "`m_256 = 15.984382666607859` recomputed here from `lgamma`, matching the
> frozen constant … to 6.7e-13 relative (the frozen literal carries more digits than double precision resolves; both
> round to the same float64)." **Three errors in one sentence**, all verified this session:
> 1. `6.679e-13` is the **absolute** difference, not the relative one; the relative difference is **4.1785e-14**.
> 2. "Both round to the same float64" is **false**: the two doubles are `402ff801013faa71` and `402ff801013fa8f9`,
>    **376 ulps apart**.
> 3. The parenthetical blamed the frozen literal for carrying excess digits. It has this backwards — the literal is
>    accurate to `4.9e-17`, and it is **this paper's own `lgamma` recomputation** that is low, by `4.18e-14`
>    relative. That is `lgamma` roundoff, not a discrepancy in the artifact. The champion's design directions are the Kerdock frame scaled by exactly this radius (line 131,
`multiply(output, MEAN_CHI_256 / 16.0)`), which is L0 implemented as an estimator [O].

### 2.2 What "divergence-form rewrite" means (so the claim can be falsified)

**D1 (admissible field) — STRENGTHENED in draft 2; see the note below.** An *admissible field* is a map
`Phi : (R^d \ {0}) x R x R^d -> R^d`, fixed independently of `f`, **locally Lipschitz jointly in all three slots**, of
polynomial growth in `(x, s, p)` at infinity, and **`o(|x|^{1-d})` as `x -> 0` with locally integrable `x`-gradient**,
applied pointwise as `V_f(x) = Phi(x, f(x), grad f(x))`.

> **Why D1 was strengthened.** Draft 1 required only "continuous in all slots, locally Lipschitz in the first," with no
> condition at the origin. Two independent audits found the same two holes, and both break the dichotomy's
> exhaustiveness rather than its two branches:
>
> 1. **No control at the origin admits a third singular source.** `Phi(x, s, p) = s·x/|x|^(d+1)` is admissible under
>    draft-1 D1, has no `p`-dependence at all — so the non-degeneracy condition holds trivially and the K-deposit
>    vanishes identically — yet `div V_f` carries a Dirac mass at the origin. That is a singular term arising from
>    neither class. The `o(|x|^{1-d})` bound removes it.
> 2. **Continuity in `(s,p)` does not make the composition BV.** D3 infers `V_f ∈ BV_loc` from L1, but L1 is a
>    statement about `f` and `grad f`, not about `Phi(x, f, grad f)`. Joint local Lipschitzness supplies the missing
>    step and makes `V_f` locally Lipschitz on each activation cell.
>
> Both branches (A) and (B) are unaffected — they were proved under hypotheses that already imply what is now written
> into D1. What was genuinely unproved in draft 1 is the **"no third class"** clause, which is the load-bearing one.

**D2 (divergence-form rewrite).** A *divergence-form rewrite* of the target is a pair `(Phi, mu)` with `Phi` admissible
and `mu` a fixed weight (Gaussian density, Lebesgue measure on a ball, or a surface measure obtained by applying the
divergence theorem once), together with an identity

> `T_G(f) = <div V_f, mu>`   valid for every `f` in `F_d`,

where `div` is the **distributional** divergence. Equivalently, by the divergence theorem, a surface-flux form
`T_G(f) = boundary flux of V_f + remainder`. This is exactly the operation "build a field pointwise out of `x`, `f`,
`grad f` and integrate by parts once".

**D3 (K-deposit).** `V_f` is `BV_loc` with jump set contained in `K` (Lemma L1 below), so by the Vol'pert / Federer
structure of a BV divergence,

> `div V_f = (div V_f)^{ac} + <[[V_f]], nu> H^{d-1}|_K`,  `[[V_f]] = Phi(x, f, grad f^+) - Phi(x, f, grad f^-)`.

The measure `<[[V_f]], nu> H^{d-1}|_K` is the rewrite's **K-deposit**. Note `f` itself is continuous across every
facet, so only the third slot of `Phi` jumps.

Two hypotheses, both stated so they can be attacked:

- **(U) Universality.** The identity is required to hold for *every* `f` in `F_d` — every bias-free ReLU net over `R^d`
  of every finite width and depth — not for one net or one family. This is what a "rewrite of the target integral"
  means; an identity tuned to one net is a fitted correction, not a rewrite.
- **(L) Affineness.** `Phi(x, s, p)` is affine in `(s, p)` for each `x`. Motivation: `T_G` is a linear functional on
  `F_d`, and `F_d` is a convex cone closed under sums and positive scalings, so a rewrite that is not affine in `f`
  represents a linear functional by a nonlinear expression. **(L) is used only for the class-A characterization
  (Theorem part 2), never for the dichotomy itself.** §5 records that P2's secondary transect estimator, which carries a
  `1/|a . u|` weight, violates (L) and is nonetheless class B by inspection — so (L) is not load-bearing for the
  conclusion, only for the collapse.

### 2.3 The theorem

> **Theorem (divergence-form dichotomy).** Let `f` range over `F_d` and let `(Phi, mu)` be a divergence-form rewrite of
> `T_G` in the sense of D1-D2. Then exactly one of the following holds.
>
> **(A) K-free.** The K-deposit vanishes `H^{d-1}`-a.e. on `K` for every `f` in `F_d`. Under (U) and (L) this happens
> if and only if
> `Phi(x, s, p) = rho(x) s x/|x|^2 + A(x) P_{x-perp} p + b(x)` with `A(x)` antisymmetric on `x-perp`,
> and then, after one tangential integration by parts on each sphere, the rewrite reduces to
> `T_G(f) = integral of f(x) w(x) d(mu')(x)` for a fixed weight `w` — a reweighting of **point evaluations of `f`**,
> containing no derivative of `f` and evaluating nothing on `K`. Its entire radial content is Euler's identity
> `x . grad f = f`, equivalently the finite homogeneity relation `f(ru) = r f(u)`; the residual angular freedom is a
> choice of quadrature, not a product of the divergence-form machinery.
>
> **(B) K-loaded.** The K-deposit is nonzero on a subset of `K` of positive `H^{d-1}` measure for some `f` in `F_d`. The
> value of the rewrite then contains a nonzero summand that is an integral over `K`, so any realization of the identity
> must locate points of `K` and evaluate the gradient jump there.
>
> There is no third class. The alternative is a condition and its negation; and for `f` in `F_d` the **only** source of
> a singular term in the distributional divergence of any admissible field is the jump of `grad f` across `K`.
>
> *This last clause holds under D1 as strengthened in draft 2, and only under it.* Without the `o(|x|^{1-d})` bound at
> the origin there is an explicit third source (a Dirac mass at 0), and without joint local Lipschitzness the
> composition need not be `BV_loc` at all, so the ac-plus-jump decomposition the argument relies on is unavailable.
> Draft 1 asserted this clause under weaker hypotheses than it needs.

> **Corollary (Rao-Blackwell).** Among unbiased estimators of `T_G(f)` of the form `(1/N) sum_i w(R_i) R_i f(U_i)`,
> with `(R_i, U_i)` the polar decomposition of iid Gaussians and `E[w(R) R] = m_d`, the variance is minimized exactly
> when `w(R) R` is almost surely constant, i.e. by exact conditioning on the mean-chi radius. This is what the champion
> does.

> **Corollary (the one-line avatar).** For every `f` in `F_d`, distributionally on the sphere,
> `Delta_S f = -(d-1) f + J H^{d-1}|_{K cap S^{d-1}}`.
> The first term is class A (proportional to `f`, no K); the second is class B (supported on K); there is no third term.

### 2.4 What the theorem is not

It is a statement about **rewrites of the target integral**, not about estimators. It does not say that class-B
estimators are expensive — that is §4, and it is measured. It does not exclude estimators outside the divergence-form
shape (harmonic expansions, control variates from other sources, multi-fidelity, seed-side extraction); §5 lists them.
Part (A)'s collapse uses hypotheses (U) and (L). Part (B) uses neither. The exhaustiveness uses neither (U) nor (L)
either — but it *does* use the regularity now written into D1, namely joint local Lipschitzness in all three slots and
the `o(|x|^{1-d})` bound at the origin, without which there is a third class. Draft 1 said the exhaustiveness "uses
neither" full stop, which read as needing no hypothesis on `Phi` at all; that was the error.

---

## 3. The proof

Every step below is either elementary, cited to a committed corpus artifact with its evidence level, or marked
**[GAP]**. Nothing is asserted at a level its support does not earn.

### 3.1 L1 — the two-level derivative structure of a piecewise-linear function

> **L1.** Let `f` be in `F_d`, with conical fan `{C_r}`, `f = g_r . x` on `C_r`, and kink set `K`. Then:
>
> (i) `f` is Lipschitz; `grad f` is in `L^inf`, piecewise constant on the fan; `Df` has no singular part.
> (ii) `grad f` is in `BV_loc` with `D(grad f) = (J nu (x) nu) H^{d-1}|_K`, where `nu` is the facet unit normal and
>      `J = nu . (grad f^+ - grad f^-)`. This measure is **purely singular**: no absolutely continuous part, because
>      `grad^2 f = 0` identically in every cell interior; no Cantor part, because the BV derivative of a
>      piecewise-constant function on a polyhedral fan is exactly its facet-jump measure; and nothing from the
>      codimension-`>= 2` skeleton, which is `H^{d-1}`-null.
> (iii) Hence for every `k >= 2`, `D^k f` is supported in `K`.
> (iv) **Euler.** `x . grad f(x) = f(x)` for every `x` not in `K`, and `f(rx) = r f(x)` for all `x` and `r >= 0`. The
>      finite form holds **everywhere, including on K**; the differential form holds only off `K`.
> (v) The gradient jump is purely **normal**: `grad f^+ - grad f^- = J nu`. Continuity of `f` plus linearity on both
>      sides of a facet forces the tangential derivatives to agree across it.

*Status.* (i), (ii), (v) are P2 §1.2, which derives them and verifies the jump algebra numerically: per-interval
affineness to **6.660e-16** and the slope-jump identity `Delta_s = c|a . u|` to a true per-seed maximum of **1.15e-12**
(seeds 101/202/303 read 1.32e-13 / 1.10e-13 / 1.15e-12; P2's headline 1.3e-12 is a conservative restatement)
[R, P2 §2.1 and its cross-check note, from `experiments/s9_crofton_transect/s9_results.json`]. (iii) follows from (ii)
by differentiating a measure supported in `K`. (iv) is immediate: differentiate `f(rx) = r f(x)` in `r` at `r = 1` for
`x` off `K`, where `f` is differentiable; conversely integrate along the ray using `f(0) = 0`. [D]

**Why (iv)'s parenthetical matters.** The champion does not use `x . grad f = f`; it uses `f(ru) = r f(u)`. The finite
form needs no derivative and is valid at every point of the domain, kink points included. Class A is therefore not
merely "K-free by accident of measure zero" — it is K-free pointwise.

**Why (iii) matters.** It closes the escape of "use a higher-order rewrite instead". A second, third or `k`-th
derivative of a piecewise-linear function has *no interior content at all*; all of it is on `K`. Any rewrite that
differentiates twice is class B before it starts.

### 3.2 L2 — realizability: every `(normal, jump, one-sided gradient)` occurs

> **L2.** Let `x_0 != 0`, let `nu` be a unit vector with `nu . x_0 = 0`, let `p` be in `R^d`, and let `J` be in `R`.
> Then there exists `f` in `F_d` with a facet through `x_0` of normal `nu`, one-sided gradient `grad f^- = p` on the
> side `nu . x < 0` near `x_0`, and jump `J`.

*Proof.* Take `f(x) = sigma(p . x) - sigma(-p . x) + J sigma(nu . x)` where `sigma = max(0, .)`. Each summand is a
bias-free ReLU unit with a linear readout, so `f` is in `F_d`; the first two sum to `p . x`. Near `x_0` (where
`p . x_0 != 0`, which we may assume by perturbing `p` in the `x_0` direction, or by noting the argument is needed only
on a dense set and `Phi` is continuous), on `nu . x < 0` we have `grad f = p`, and on `nu . x > 0` we have
`grad f = p + J nu`. [D]

*The constraint that matters.* Because `K` is **conical**, every facet through `x_0` has its normal in `x_0`-perp. So
the realizable normals at a given point form the unit sphere of the hyperplane `x_0`-perp, not of `R^d`. The rigidity
lemma below is stated with that restriction respected; getting this wrong would overclaim.

*Consequence used later.* The radial derivative `x . grad f` is **continuous across `K`**: at a facet point,
`x . grad f^+ - x . grad f^- = J (x . nu) = 0` since `nu` is perpendicular to `x`. This is Euler restated — both sides
equal `f(x)`, and `f` is continuous. Only the **tangential** gradient jumps.

### 3.3 L3 — the K-deposit, and the rigidity of jump-free fields

Fix `x != 0` and `s` in `R`, write `W = x`-perp and `P_W` for the orthogonal projection onto `W`. Define the
**normal-blindness condition**

> **(N)** For all `p` in `R^d`, all `t` in `R`, and all unit `nu` in `W`:
> `nu . Phi(x, s, p + t nu) = nu . Phi(x, s, p)`.

> **L3a.** The rewrite's K-deposit vanishes at `(x, s)` for every `f` in `F_d` if and only if (N) holds at `(x, s)`.

*Proof.* By D3 the deposit density is `<Phi(x, s, p + J nu) - Phi(x, s, p), nu>` where `p = grad f^-`, `nu` the facet
normal and `J` the jump, using L1(v). By L2 the triple `(nu, J, p)` ranges over all of `(unit sphere of W) x R x R^d`.
The deposit vanishes for all of them precisely when (N) holds. [D]

> **L3b (rigidity).** Fix `x != 0` and `s`. Then (N) holds if and only if there exist a scalar `rho`, a vector
> `b` and a linear map `A : W -> W` with `A` antisymmetric, all depending on `(x, s)` only, such that
> `P_W Phi(x, s, p) = A P_W p + P_W b` for all `p` with `x . p` held fixed.
> Equivalently: `Phi`'s dependence on the **tangential** part of the gradient is affine with an antisymmetric linear
> part, and its dependence on the **radial** part `x . p` is unconstrained.

*Proof.* Fix `x`, `s`, and fix the radial coordinate `x . p = c`; write `psi(w) := Phi(x, s, p_c + w)` for `w` in `W`,
where `p_c` is any fixed vector with `x . p_c = c`. Condition (N) says `nu . [psi(w + t nu) - psi(w)] = 0` for every
unit `nu` in `W`, every `t`, and every `w` in `W`. Taking `nu = (w' - w)/|w' - w|` and `t = |w' - w|` gives

> `(psi(w') - psi(w)) . (w' - w) = 0` for all `w, w'` in `W`.   (*)

Set `phi(w) := psi(w) - psi(0)`. Putting `w = 0` in (*) gives `phi(w') . w' = 0` for all `w'`. Expanding (*),

`phi(w') . w' - phi(w') . w - phi(w) . w' + phi(w) . w = 0`,

and the first and last terms vanish, so

> `phi(w') . w = - phi(w) . w'` for all `w, w'` in `W`.   (**)

Define `B(w, w') := P_W phi(w) . w'`. For each fixed `w`, `B(w, .)` is linear in `w'` because it is an inner product.
By (**), `B(w, w') = -B(w', w)`, so `B` is linear in its **first** argument as well — it is minus a function that is
linear in the slot now held second. Hence `B` is bilinear and antisymmetric on `W x W`, so `B(w, w') = (A w) . w'` for a
unique antisymmetric `A : W -> W`, and therefore `P_W phi(w) = A w`. Restoring `psi(0)` gives
`P_W psi(w) = A w + P_W psi(0)`. The component of `Phi` along `x` is untouched by (N) because every admissible `nu` lies
in `W`. Conversely, if `P_W Phi` has that form then for `nu` in `W`,
`nu . [Phi(p + t nu) - Phi(p)] = nu . A (t nu) = t (A nu) . nu = 0` by antisymmetry, so (N) holds. [D]

**Remark on regularity.** No differentiability in `p` is used. (**) is an algebraic identity and bilinearity is forced
by it, so the lemma applies to non-smooth `Phi` — including the absolute values and reciprocals that appear in real
transect weightings. This is deliberate: a rigidity lemma that assumed smoothness would not cover the estimators the
corpus actually built.

**Where the radial freedom goes.** L3b leaves `Phi`'s dependence on `x . p` completely free. That freedom is empty:
by L1(iv), `x . grad f(x) = f(x)` identically on `F_d`, so any dependence on `x . p` is a dependence on `s`. Under
(L) this is affine in `s`. So the general jump-free admissible field is

> `Phi(x, s, p) = rho(x) s x/|x|^2 + A(x) P_W p + b(x)`,  `A(x)` antisymmetric on `x`-perp.   (A-form)

### 3.4 L4 — class A carries no derivative information

> **L4.** Let `(Phi, mu)` be a divergence-form rewrite whose K-deposit vanishes, with `Phi` of the (A-form). Then the
> rewrite reduces, after one tangential integration by parts on each sphere `|x| = r`, to
> `T_G(f) = integral of f(x) w(x) d(mu')(x)` for a fixed weight `w` and measure `mu'` determined by `(rho, A, b, mu)`.
> No derivative of `f` survives, and no point of `K` is evaluated.

*Proof.* Because the K-deposit vanishes, `div V_f` has no singular part (D3), so it may be computed cell by cell. In
the interior of a cell, `grad f` is constant and `grad^2 f = 0` (L1(ii)), hence

`div V_f = div_x[Phi(x, f, grad f)] = (div_x Phi)(x, f, grad f) + (d/ds Phi)(x, f, grad f) . grad f`,

a function of `(x, f(x), grad f(x))` alone. Substituting the (A-form) and splitting `grad f = f x/|x|^2 + grad_S f`
(Euler, L1(iv)):

- the `rho(x) s x/|x|^2` term contributes only in `x` and `f`;
- the `b(x)` term contributes `div_x b`, in `x` alone;
- the `A(x) P_W p` term contributes `(div_x A) . grad_S f` plus `A : grad^2 f`, and the second vanishes because `A` is
  antisymmetric while `D(grad f)` is the symmetric measure `J nu (x) nu` (L1(ii)) — this is exactly the K-deposit
  vanishing again, now seen from the interior;
- the cross term `(d/ds A) : grad f (x) grad_S f` vanishes because `A` annihilates `x` and is antisymmetric on `W`, so
  `grad f^T A grad_S f = (grad_S f)^T A (grad_S f) + (f/|x|^2) x^T A grad_S f = 0 + 0`.

So `div V_f = c(x) . grad_S f + e(x, f)` with `e` affine in `f` by (L). The first term is a **tangential** derivative of
`f`. On each sphere `|x| = r`, `f` restricted is Lipschitz and continuous (it does not jump across `K`; only its
gradient does), and the sphere is closed with no boundary, so tangential integration by parts is exact and produces no
boundary and no jump term:

`integral over the sphere of c . grad_S f = - integral over the sphere of f div_S c`.

Both remaining terms are now affine functionals of `f` evaluated pointwise. Collecting them and re-integrating in `r`
against `mu` gives `T_G(f) = integral of f w d(mu')`. [D]

**This is the substantive half of the theorem.** It says the K-free branch is not a weaker rewrite — it is *no rewrite
at all*. Nothing is gained by integrating by parts unless you are willing to pay for `K`. The only structural fact used
about `f` beyond piecewise linearity is homogeneity, and homogeneity enters exactly once, as the substitution
`x . grad f = f`.

### 3.5 The dichotomy, and its exhaustiveness

*Proof of the Theorem.* Given a rewrite `(Phi, mu)`, D3 splits `div V_f` into an absolutely continuous part and the
K-deposit `<[[V_f]], nu> H^{d-1}|_K`. Either that measure vanishes `H^{d-1}`-a.e. on `K` for all `f` in `F_d`, or it
does not. The two cases are mutually exclusive and jointly exhaustive by construction. In the first case L3a gives (N),
L3b plus L1(iv) give the (A-form), and L4 gives the collapse — branch (A). In the second case the identity's right side
contains the nonzero summand `<[[V_f]], nu> H^{d-1}|_K` integrated against `mu`, which is by definition an integral over
`K` — branch (B). Exhaustiveness against **higher-order** rewrites is L1(iii): for piecewise-linear `f` every
derivative of order `>= 2` is supported in `K`, so no rewrite that differentiates twice can be K-free. [D]

*Two things this does not prove.* It does not prove that the class-B integral is hard to compute (§4). And it does not
prove that a class-A rewrite is *useful* — L4 says class A reduces to a weighted quadrature, and choosing that weighting
well is a design problem the divergence theorem has nothing to say about. The corpus's F4 SYMMETRY family is the
measured statement of that: for a group-orbit design the LP-optimal weights are uniform, and perturbing the design
breaks the exact 2-design [R, P1 §3.1, `core/FAILURE_MODE_GRAPH_20260810.md`].

### 3.6 Corollary: the one-line avatar `Delta_S f = -(d-1) f + facet jumps`

For `f` positively 1-homogeneous, writing `f = r g(u)` in polar coordinates, the standard decomposition of the
Euclidean Laplacian for `f = r^alpha g(u)` is `Delta f = r^(alpha-2)[Delta_S g + alpha(alpha + d - 2) g]`. With
`alpha = 1` this reads `Delta f = r^(-1)[Delta_S g + (d-1) g]`. But by L1(ii) the distributional `Delta f` is exactly
the trace of `D(grad f)`, i.e. the facet-jump measure `J H^{d-1}|_K` — and in each cell interior `f` is linear so
`Delta f = 0` there. Rearranging,

> `Delta_S f = -(d-1) f + J H^{d-1}|_{K cap S^{d-1}}`   (distributionally on the sphere).  [D]

This is the dichotomy compressed to one line. The first term is proportional to `f` itself: it is class A and it is
information-free, since applying it returns a multiple of the quantity you were trying to integrate. The second is the
kink measure: class B. There is no third term because a piecewise-linear function has no interior second derivative.

**Second signal, from an independent corpus record.** Ledger record `compact_group_laplacian_control` (index 66 in
`headroom/fold_ledger.json`, status `killed`) states, in its own result prose: *"Distributionally Delta_S f=-(d-1)f+facet
jumps, so a.e. AD returns only-255f and is not zero mean."* At the corpus width `d = 256`, `d - 1 = 255` [O, exact
match]. That record reached the identity from the opposite direction — it was trying to build a Haar-rotation
Laplace-Beltrami control and discovered that automatic differentiation, which sees only the a.e. derivative, returns the
class-A term and silently discards the class-B term, so the intended zero-mean control is not zero-mean. The theorem
predicts exactly that failure.

### 3.7 Corollary: exact radial conditioning is the variance-minimal class-A member

> **Rao-Blackwell corollary.** Let `X_i` be iid `N(0, I_d)` with polar decomposition `X_i = R_i U_i`. Consider
> estimators `E_w = (1/N) sum_i w(R_i) R_i f(U_i)` for measurable `w >= 0`. Unbiasedness for `T_G(f) = m_d E[f(U)]` on
> all of `F_d` requires `E[w(R) R] = m_d`. Then
> `Var(E_w) = (1/N) ( E[(wR)^2] E[f(U)^2] - m_d^2 (E f(U))^2 )`,
> and `E[(wR)^2] >= (E[wR])^2 = m_d^2` by Cauchy-Schwarz, with equality if and only if `w(R) R = m_d` almost surely.
> Hence the variance-minimal unbiased class-A estimator conditions exactly on the mean-chi radius. [D]

Independence of `R` and `U` is what makes the bound sharp, and positive 1-homogeneity is what makes `f(X) = R f(U)`
exactly separable. This is the mathematical content of `radial_conditioning = True` in
`experiments/v31_guards/package_source/kerdock_v3_estimator.py` line 48 [O].

### 3.8 Corollary: the frozen fallback is the degree-2 optimum of the same class

When `radial_conditioning` is `False`, the frozen chain applies a quadratic radius control instead
(`base_estimator.py` lines 113-120, and identically `fold3_estimator.py` lines 73-81) [O]:

```
q1 = radius_sq - 257.0
q2 = radius_sq * radius_sq - 66563.0
base_weights = 1.0 - (2600.0/537689.0)*q1 + (3.0/537689.0)*q2
```

Every one of those four constants is re-derived here from the chi_256 law with no fitted input.

**The centering constants.** Because the integrand is positively 1-homogeneous, the estimator multiplies `f(U)` by `R`,
so unbiasedness requires the control terms to have zero mean under the **size-biased** radial law (density proportional
to `r` times the chi_d density). Under it, `E*[R^(2j)] = E[R^(2j+1)] / E[R] = product over i < j of (d + 1 + 2i)`. At
`d = 256`:

- `E*[R^2] = d + 1 = 257` — the constant in `q1`. [D, verified: `2 Gamma((d+3)/2)/Gamma((d+1)/2) = d+1`]
- `E*[R^4] = (d+1)(d+3) = 257 x 259 = 66,563` — the constant in `q2`. [D, `257 x 259 = 257 x 260 - 257 = 66820 - 257`]

**The coefficients.** With `f(U)` independent of `R`, minimizing the estimator variance over `w` in the span
`{1, q1, q2}` is minimizing `E[(w(R) R)^2]`. Writing `S = R^2 ~ chi^2_256` with `E[S^j] = product over i < j of
(d + 2i)`, the two normal equations are

`u E[S q1^2] + v E[S q1 q2] = -E[S q1]`,  `u E[S q1 q2] + v E[S q2^2] = -E[S q2]`,

solved here in exact rational arithmetic. The unique solution is

> `u = -2600/537689`,  `v = 3/537689`   — **exactly** the frozen literals, as rationals, not to floating-point
> tolerance. [D, exact `fractions.Fraction` solve; matches `-0.004835509002415895` and `5.579433464326032e-06`]

**What that buys, and what it therefore costs.** With the optimal control the residual radial second-moment excess is

> `E[(wR)^2] / m_d^2 - 1 = 2.725658116986551e-07`,

against `E[R^2] / m_d^2 - 1 = d/m_d^2 - 1 = 1.9550286144132123e-03` with no control at all. The degree-2 control
removes `1 - 2.7256581e-07 / 1.9550286e-03 = 0.9998605821880615`, i.e. **99.9861 %**, of the radial excess. [D]

**The consequence for the ablation.** The wc1 `A_radial` arm is therefore *not* "the radial identity removed". It is
"the radial identity truncated at degree 2 in `R^2`, at that truncation's exact optimum". Both arms are class-A members
of the same identity; the ablation measures the last 0.014 % of the radial excess, not the identity. This is the single
most important quantitative correction in this paper, and §4.1 states what it does to the 2.141x figure.

---

## 4. What this closes: the ledger, record by record

Paths are relative to
`C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\publish\recursive-estimator-folding\corpus\whestbench`.
The ledger is `headroom/fold_ledger.json`, schema version 1, **267 candidate records** as committed, sha256
`8afec50ab41776225066cab074766e4b4aad6e9a38fc1887d0f7113642c86d2b` [O, computed this session]. Note that
`headroom/GEN6_FAILURE_SALVAGE_ATLAS_20260809.json` carries `ledger_sha256`
`81743b71f3b5ff7d4b34963e7cf3d67767799916452b6ab2862b528ee07b64f9` over **223** records; that hash does **not** bind the
current ledger and a successor should not treat it as an integrity seal for the 267-record state [O].

### 4.1 Class A — the champion's own route, with the number corrected

| item | value | level | source |
|---|---|---|---|
| `radial_conditioning` flag on the champion | `True` | [O] | `experiments/v31_guards/package_source/kerdock_v3_estimator.py` line 48 |
| design radius | `MEAN_CHI_256 = 15.98438266660852747` | [O] | same file, lines 18 and 131 |
| `A_radial` paired MSE ratio vs full v3 | **2.1411108700917687** | [O] | `experiments/wc1_winner_ablation/wc1_results.json`, `arms.A_radial.mse_ratio_vs_baseline` |
| its bootstrap 95 % CI | [1.5094625642710886, 3.042115696081943] | [O] | same |
| its per-net ratios (101/202/303) | 3.1289402665813 / 1.824079228806255 / 2.1292142326285717 | [O] | same |
| its flags | LOAD-BEARING, TAIL-DRIVER | [O] | same |
| `A_frames` paired MSE ratio | 2.016433193279511, CI [1.4474361131536622, 2.831088836140853] | [O] | `arms.A_frames` |
| **isolated radial effect** | **1.0618307996653649** | [O] | `derived_isolated_ratios.A_radial_isolated_over_frames` |
| wc1 baseline mean MSE / billed | 3.6289652200697916e-07 / 1.7208335968108334e11 (0.6327 of B = 2.72e11) | [O] | `baseline` block |

**The correction.** The brief handed to me said radial conditioning is "worth 2.141x by the wc1 ablation". The artifact
disagrees with itself being read that way, in its own words. `wc1_ablation.py` lines 24-33 state that `A_radial` and
`A_frames` **share an iid substrate**, that `A_radial` is "iid substrate with radial_conditioning=False", and — verbatim
— that "the ISOLATED radial effect = ratio(A_radial) / ratio(A_frames); the raw vs-baseline ratio bundles the design"
[O]. The results file computes that quotient itself: `2.1411108700917687 / 2.016433193279511 = 1.0618307996653649`,
reproduced here by division [D]. So:

- **2.141x is the value of the deployed class-A route as a whole** — the Kerdock design *and* exact radius placement —
  measured against an iid Gaussian cloud carrying the degree-2 radial control. That is a real and correctly reported
  number, and it is the top entry of the artifact's own `marginal_value_map`.
- **1.062x is the isolated value of exact radius placement**, and it has no reported confidence interval. The two arms'
  own CIs, [1.509, 3.042] and [1.447, 2.831], overlap over almost their whole length, so the isolated figure is not
  separated from 1.0 by this experiment [D].
- **The theorem explains why 1.062x is small rather than large**: by §3.8, the fallback arm is still class A, at the
  exact degree-2 optimum, which already removes 99.9861 % of the radial excess. The ablation is measuring the tail of an
  identity, not its absence.

**An open tension, stated rather than hidden.** A pure radial-variance account predicts an isolated ratio of
`1 + 2.7256581e-07 x (1 + mean^2/variance)`. Using S17's committed field variance `sigma^2 = 7.900e-3 / 1.600e-2 /
1.112e-2` [R, P1 §1.1 and `experiments/s17_ibc_floor/s17_results.json`] and any plausible mean for the neuron-averaged
output of a He net at norm-preserving initialization, that predicts roughly `1.00001`, three or more orders below the
measured 1.0618 [D]. Part of the discrepancy has a code-verified cause: `final_weights` is applied **only** to the
terminal folded sample (`fold3_estimator.py` lines 249-259), while the pilot rescue, the pruning decision, the
first-moment and first-variance residuals and the tangent correction all consume the unweighted cloud [O]. So the
degree-2 class-A control corrects one term of a composed estimator, not the estimator. **[GAP]** — I cannot close the
quantitative account from committed data. *What would close it:* recompute, for nets 101/202/303 under the fold3
terminal observable, the ratio `avg_k E[g_k^2] / avg_k Var(g_k)` over the 256 output components (`g` the antipodally
even part), and compare `1 + 2.7256581e-07 x (that ratio)` against the measured per-net ratios `A_radial/A_frames`. That
is a forward-pass measurement, forbidden here by the firewall.

**Retroactive derivation.** The theorem does retroactively derive the *structure* of the champion's winning component:
given that the target is the sphere-mean of a positively 1-homogeneous function, class A is forced to be a reweighting
of point evaluations (L4), its radial content is forced to be Euler (L1(iv)), and among unbiased radial reweightings
exact chi-mean conditioning is forced to be optimal (§3.7). The champion's radial conditioning was previously an
empirically validated component; it is now **a proved optimum within its class**. The angular half of the champion —
the Kerdock design — is *not* derived by this theorem and remains an empirical result (P1 pillar 1).

### 4.2 Class B — five records, and an honest independence audit

All five are class B under the theorem: each rewrites the target as an integral over the activation-boundary facets,
i.e. each has a nonzero K-deposit. **None of them was previously a proof; four were empirical kills and one was a cost
lower bound. The theorem upgrades none of their *kill verdicts* to proofs. What it does upgrade is the *explanation*:
they did not fail for five reasons, they failed for one — they are all in class B, and class B is where the mean gets
deposited onto K.** That is a derivation of the common cause, not of the individual numbers.

| id (ledger index) | what it realized | headline number | what kind of evidence | scale | artifact dir |
|---|---|---|---|---|---|
| `s9_crofton_kink_transect_identity` (231) | sample `K` by random line transects with exact breakpoint enumeration | **176,860x** worse variance-per-FLOP (geomean), kill line 100x | gated efficiency kill, two independent implementations | width 64 depth 8, `d = 64` | `experiments/s9_crofton_transect/` |
| `m86_boundary_laplace_coarea` (83) | enumerate `K` exactly via the distributional-Laplacian / coarea identity | **1.2408797549e86** FLOPs lower bound vs 272e9 budget | cost lower bound (Phase A passes, Phase B unresolved) | target width 256 | **none** |
| `m95_palm_coarea_sampler` (94) | Palm / Horvitz-Thompson facet sampling with a local inclusion probability | **39.503 / 39.817 / 556.709** efficiency ratios | efficiency kill of the literal law; intended law nonpromotable | **`d = 2`, depth 2** | **none** |
| `direction_only_facet_raoblackwell` (61) | per-gate realized-prefix-cone projection with exact Student-t interval probability `B` and `1/B` correction | **556.305** held-out equal-cost MSE ratio, one-sided 95 % upper 1126.452 | efficiency number **on top of a bias failure** | target scale (35B proxy slice) | **none** |
| `compact_group_laplacian_control` (66) | Haar-rotation Poisson / Laplace-Beltrami control on the MUB cubature error | no variance number; killed by exact reasoning | exact-reasoning kill | target width 256 | **none** |

Plus one closely related record the brief did not name but which belongs here:

| `m202_signed_facet_smc_no_go` (217) | unnormalized Feynman-Kac / SMC on the signed facet envelope | sign ratio `epsilon/(2-epsilon) -> 0` | **exact rational counterexample** | `d = 2, width 2, depth 2` witness | `experiments/m202_signed_facet_smc_no_go/` |

#### Which are independent, and which are not

- **One identity, several realizations.** M86's Phase A and S9's Stage A verify *the same theorem* — the Gaussian /
  spherical mean of a bias-free CPWL network equals the weighted surface integral of the gradient jumps over `K`. M86
  reached it via the distributional spherical Laplacian and coarea; S9 reached it via Euler times Stein, and its ledger
  record explicitly describes it as a literature-fleet find that was "NOT in any closed family" [R]. Both verified it at
  machine precision (M86: `3.3306691e-16` relative on 24 generated `d = 2` networks, `1.9285002e-12` against dense
  angular quadrature; S9: `6.660e-16` affineness and `1.15e-12` jump algebra) [R]. **Two independent derivations of one
  identity.**
- **M95, `direction_only_facet_raoblackwell` and M202 are descendants of M86, not independent of it.** Each ledger
  record says so in its own preservation clause: M95 "Preserve M86 coarea, local gap recovery, augmented HT identity";
  M202 "Preserve M86's signed identity and owned output-jump collapse"; `direction_only_facet_raoblackwell` "The global
  distributional-Laplacian identity is preserved" [R, verbatim]. They are **independent realizations of a shared
  identity**, which is the right way to count them: they do not corroborate the identity independently, but they do
  probe genuinely different sampling laws.
- **S9's two implementations are two implementations, not two realizations.** P2 §2.3 and the ledger addendum record
  that a second runner built an independent engine with exact mask-product gradients and a *structurally different*
  unbiased weighting (the slope-jump / factor-`d` form `E[f] = d E[sum_k Delta_beta_k phi_1(t_k)]` against §1.4's
  Crofton form), agreeing on both stages, with the kill confirmed under both FLOP accountings — 1.77e5x metered versus
  4.0e4-4.9e4x lean, "both >=340x past gate" [R, P2 §3.2 and the ledger addendum]. The addendum also corrects the
  provenance: the two runners are "possibly a duplicated fable launch, not a Sol cross-check as first attributed" [R].
  Treat this as **one realization with two implementations**, which is still the strongest evidence in the set.
- **Only one of the five is a clean gated efficiency kill at a nontrivial scale.** That is S9. M95's numbers are `d = 2`,
  **depth 2** — the ledger says "Literal depth2 efficiency ratios are39.503,39.817,556.709" [R, verbatim] — so they are
  a toy, and the 556.709 in particular is one toy configuration, not a target-scale measurement.
  `direction_only_facet_raoblackwell` is at target scale but its own result prose says "only1/30 joint truth checks pass
  and its direct companion encounters8211 invalid local-cell events" and identifies the missing term as "the cross-cell
  pushforward normalization" [R, verbatim] — so its 556.305 is the efficiency of a **biased** proposal, quoted with the
  bias disclosed, and it cannot be read as a clean efficiency price for a correct class-B estimator.
  `compact_group_laplacian_control` reports no variance ratio at all.
- **An unresolved near-collision, flagged.** M95's largest literal ratio is `556.709` and
  `direction_only_facet_raoblackwell`'s held-out ratio is `556.305`. These records share no harness, no scale
  (`d = 2` versus target width), and no estimator. Neither has an experiment directory or an `artifact_hash` in the
  ledger [O, both `artifact_hash: None`, no matching directory under `experiments/`]. **[GAP]** — I could not determine
  from the corpus whether the proximity is coincidence or a transcription artifact. *What would close it:* locate the
  M95 and `direction_only_facet_raoblackwell` harnesses (absent from `experiments/`), or any run log that produced
  either number, and confirm the two figures come from different computations.

#### The two numbers this paper re-derived rather than repeated

**S9's 176,860x, from the committed raw variances and costs.** `s9_results.json` `stage_B` gives per seed
`(Var_line, Var_MC-pair, C_line, C_pair)`:

| seed | Var_line | Var_MC-pair | C_line (madds) | C_pair (madds) | variance factor | cost factor | product |
|---|---|---|---|---|---|---|---|
| 404 | 0.14505094784308317 | 0.0007398774748562043 | 53,289,082.0 | 57,472.0 | 196.0473 | 927.2182 | 181,778.6 |
| 505 | 0.155868969981101 | 0.0008992060615697491 | 52,325,541.33 | 57,472.0 | 173.3407 | 910.4528 | 157,818.5 |
| 606 | 0.18811763367463796 | 0.0009408310782311122 | 55,428,181.33 | 57,472.0 | 199.9484 | 964.4380 | 192,837.8 |

Geometric mean of the products: **176,860.5241415622**, against the committed
`stage_B_geomean_ratio = 176860.52414156235` — agreement to 8e-16 relative [D]. The geometric-mean **variance** factor
alone is **189.4057**, and the geometric-mean cost factor is **933.7656** [D]. P2's headline "≈196x at zero enumeration
cost" is seed 404's variance factor; the three-seed geomean is 189.4, so the zero-cost variance kill is real on all
three seeds and P2's quoted figure is the largest of them [D]. **The theorem says why the variance factor cannot be
engineered away**: the identity's content *is* the cancellation of a large signed surface quantity down to a small
volume quantity, and that is a property of the K-deposit, not of the sampler. P2 §3.1 measures it: about 300 signed jump
terms of magnitude `O(0.1-1)` per line cancelling to a mean near 0.03 [R].

**M86's 1.2408797549e86, from its own stated ingredients.** The ledger record says the first-layer facet-cell count is
"2^263" and that the bound is "an optimistic scalar forward-plus-adjoint first-layer enumeration lower bound" [R,
verbatim; the count `256 x 2^255 = 2^263` is confirmed exactly, and independently restated in
`experiments/m202_signed_facet_smc_no_go/M202_RESULTS_20260809.json` as
`"target_first_layer_candidate_facet_cells": "256*2^255 = 2^263"` [O]]. A scalar forward pass at width 256, depth 32,
counting multiply-adds as `n(2n-1)` per layer, costs `256 x 511 = 130,816` per layer, `x 32 = 4,186,112`, and forward
plus adjoint doubles it to `8,372,224`. Then

> `2^263 x 8,372,224 = 1.2408797549091844e86`,

against the ledger's `1.2408797549e86` — agreement to **7.4e-12** relative, i.e. every quoted digit [D, exact integer
arithmetic]. That is a complete re-derivation of a number that was previously only reported, and it makes the bound
auditable: it is `(facet-cell count) x (forward + adjoint FLOPs per cell)`, with the budget for comparison being
`272e9`. The ratio to budget is about `4.6e74`.

#### What the theorem contributes to each record

- **S9 / M86 identity:** now understood as *the* canonical class-B object. Not upgraded from empirical to proved; it was
  already a verified theorem in both records. What is new is that it is proved to be **the only alternative to Euler**.
- **S9's kill:** remains empirical. The theorem explains the mechanism's inevitability (you must integrate over `K`) but
  does not prove a variance bound. Not upgraded.
- **M86's Phase B:** remains a cost lower bound. The theorem removes the hope that a cleverer *rewrite* avoids the
  enumeration, since by L1(iii) any higher-order rewrite is also K-supported. This is a genuine strengthening of the
  record's own conclusion, and it is proved.
- **M95 and `direction_only_facet_raoblackwell`:** remain empirical and, as noted, compromised. The theorem predicts
  that both must sample `K`, which they do; it says nothing about their inclusion laws.
- **`compact_group_laplacian_control`:** this is the one record whose kill the theorem does retroactively **derive**.
  Its stated mechanism — a.e. autodiff returns `-255 f` and misses the facet mass, so the intended zero-mean control is
  not zero-mean — is exactly §3.6 at `d = 256`. An empirical kill upgraded to a corollary. [D]
- **M202:** its exact rational counterexample (`f_epsilon = ReLU(ReLU(x1)) - (1-epsilon) ReLU(ReLU(x2))`, signed mass
  `2 epsilon`, absolute mass `2(2-epsilon)`, ratio to 0) is already proof-grade within its subclass and is *not*
  superseded. It proves something the dichotomy does not: that even a correct class-B identity can have unbounded
  relative variance under the best absolute-envelope proposal [R + O, `M202_RESULTS_20260809.json`].

#### Class-B population in the corpus

`headroom/GEN6_FAILURE_SALVAGE_ATLAS_20260809.json` tags **52 of 223** records with the operator family
`endpoint_facet_and_coarea` [O, `summary.operator_family_counts`]. That tag is multi-assigned and looser than D2, so it
is an upper bound on the class-B population rather than a census; but it locates the family the theorem describes and it
is the right index for a successor looking for further realizations. The same summary records 16 entries under the
failure boundary `theorem_or_class_closure` [O].

---

## 5. Scope: what this paper does not claim

**5.1 It is about rewrites, not estimators.** The theorem classifies identities of the shape D2. It says nothing about
estimators that are not rewrites of the target integral: harmonic / spherical-design constructions, control variates
drawn from a surrogate, multi-level or multi-fidelity schemes, importance sampling, quasi-Monte Carlo point sets, or
seed-side extraction that reads the weights directly. P1 §4.5 states the last of these as the campaign's one genuinely
open door and this paper does not touch it.

**5.2 The pricing of class B is measured, not proved.** The theorem proves that class B *must* integrate over `K`. That
touching `K` is expensive is an empirical claim supported by the records in §4.2, whose weight is: one clean gated
efficiency kill at width 64 depth 8, one cost lower bound at width 256, one exact counterexample at `d = 2`, and two
compromised efficiency records. Extrapolating S9's cancellation mechanism from 448 hidden neurons (width 64, depth 8) to
the target's 7,936 (width 256, depth 32) is **[GAP]** — not measured anywhere in the corpus. *What would close it:*
re-run the S9 Stage-B screen at width 256 depth 32 and report the variance factor at zero enumeration cost. P2's own
caveat says the same thing: "the ×176,860 is one measurement at one scale, and the variance factor should be expected to
grow with crossings per line" [R].

**5.3 Hypotheses (U) and (L) are load-bearing for part (A) only.** If a rewrite is tuned to a single network rather than
required on all of `F_d`, L2's realizability argument fails and L3b does not apply. If a rewrite is non-affine in `f`,
L4's collapse is not established. P2's secondary transect estimator
`E_2 = sum_k phi_1(t_k) c_k ||a_k||^2 / |a_k . u|` is non-affine and therefore outside (L); it is class B by inspection
(it sums over breakpoints of `K`), which is why (L) is not load-bearing for the dichotomy's conclusion — but a
successor who wants the class-A collapse without (L) must prove it.

**5.4 Mollification is not covered by the proof, only by the corpus.** A rewrite may first smooth `f` (convolve with a
mollifier, or use a smooth surrogate) and then apply a genuinely volume-supported divergence identity. At `epsilon > 0`
that is not of the form D2. The structural fact is that `grad^2 f_epsilon = rho_epsilon * (J nu (x) nu H^{d-1}|_K)`, so
the mass sits in an `epsilon`-tube around `K` and returns to `K` as `epsilon -> 0` [D]. The *cost* of the smooth route
is not proved here; it is the measured content of `compact_group_laplacian_control`, whose result prose states that
"primal/first/second tangent sweeps cannot cover64512 nodes under35B" and that "a subset of M nodes has aggregate R2 at
most M/N even under perfect per-node correlation" [R, verbatim]. That last clause is an exact bound and is the strongest
part of that record.

**5.5 Everything numerical is at one setting.** All the class-A measurements are three synthetic He-initialized
bias-free nets, width 256, depth 32, seeds 101/202/303, one Haar rotation per replicate, 12 replicates, truth from the
cached m181 3.5M-sample final-layer means [O, `wc1_results.json` `constants`]. No claim is made about trained networks,
other widths or depths, biased networks, or other activation functions. The theorem itself is scale-free and holds for
any `d` and any bias-free CPWL network, but it is a statement about identities, and identities have no error bars.

**5.6 What was not attacked.** I did not verify M86's, M95's, `direction_only_facet_raoblackwell`'s or
`compact_group_laplacian_control`'s Phase-A checks — none has an experiment directory in this corpus, so all four are
[R] and only the arithmetic I re-derived from their stated ingredients is [D]. I did not re-run any harness. I did not
verify P2's Stage-A agreement table beyond the two numbers I recomputed. Absence of evidence in those four records
counts for nothing here because I did not look where the evidence would be — it is not in the corpus.

---

## 6. Reproduction map

Corpus root:
`C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\publish\recursive-estimator-folding\corpus\whestbench`.

| claim | number | path |
|---|---|---|
| champion radial conditioning flag, design radius | `radial_conditioning = True`, `MEAN_CHI_256 = 15.98438266660852747` | `experiments/v31_guards/package_source/kerdock_v3_estimator.py` lines 48, 18, 131 |
| radial conditioning implementation (mean-radius rescale) | `mean_radius = exp(0.5 log 2 + lgamma((w+1)/2) - lgamma(w/2))` | `experiments/v31_guards/package_source/base_estimator.py` lines 88-98 |
| degree-2 radial control (the class-A fallback) | `257`, `66563`, `2600/537689`, `3/537689` | `base_estimator.py` lines 113-120; `fold3_estimator.py` lines 73-81 |
| control applied only at the terminal fold | — | `fold3_estimator.py` lines 249-259 |
| ablation arms, ratios, CIs, flags, isolated radial effect | 2.1411108700917687; 2.016433193279511; 1.0618307996653649 | `experiments/wc1_winner_ablation/wc1_results.json` |
| ablation arm definitions (the "bundles the design" statement) | — | `experiments/wc1_winner_ablation/wc1_ablation.py` lines 24-33, 148-185; `WC1_SPEC.md` |
| S9 raw variances and costs; geomean ratio | 176860.52414156235 | `experiments/s9_crofton_transect/s9_results.json` (`stage_B`, `stage_B_geomean_ratio`) |
| S9 identity certificates, layer decomposition, second runner | 6.660e-16; 1.15e-12; 8.88e-15 on 20 fresh nets | `experiments/s9_crofton_transect/S9_VERDICT.md`, `s9_crosscheck.json`, `s9_stageA20.json`; and `papers/P2_CROFTON_KINK_IDENTITY_20260810.md` |
| M86 / M95 / direction-only / compact-group records | 1.2408797549e86; 39.503/39.817/556.709; 556.305; `-255 f` | `headroom/fold_ledger.json` indices 83, 94, 61, 66 (no experiment directories, no artifact hashes) |
| M202 exact counterexample | signed mass `2 eps`, absolute `2(2-eps)`, `2^263` cells | `experiments/m202_signed_facet_smc_no_go/M202_RESULTS_20260809.json` |
| class-B family tag population | 52 of 223 | `headroom/GEN6_FAILURE_SALVAGE_ATLAS_20260809.json` `summary.operator_family_counts` |
| field variance `sigma^2`, `N_eff`, champion state | 7.900e-3 / 1.600e-2 / 1.112e-2; ~38k; raw 2.818e-7 | `experiments/s17_ibc_floor/s17_results.json`; `core/RECURSION_PACKET_GEN6_20260810.md`; summarized in `papers/P1_SPECKLE_THEOREM_20260810.md` §1.1, §5 |

**Arithmetic performed for this paper** (all exact or shown; reproducible in four lines of Python, no corpus code
imported):

1. `m_256 = exp(0.5 log 2 + lgamma(257/2) - lgamma(128)) = 15.984382666607859`; `m^2 = 255.50048923255378`;
   `d - m^2 = 0.4995107674462247`.
2. Size-biased chi_256 moments `product over i<j of (257 + 2i)`: `257`, `66563`, `17372943`, `4569084009`,
   `1210807262385`. The first two are the frozen `q1`, `q2` centering constants.
3. Exact rational solve of the two normal equations for the degree-2 control gives `(-2600/537689, 3/537689)` —
   identical to the frozen literals as **rationals**. Residual radial excess `2.725658116986551e-07`; uncontrolled
   excess `1.9550286144132123e-03`; removed fraction `0.9998605821880615`.
4. `2^263 = 256 x 2^255`; `256 x 511 = 130816`; `x 32 = 4186112`; `x 2 = 8372224`;
   `2^263 x 8372224 = 1.2408797549091844e86` versus the ledger's `1.2408797549e86`, relative difference `7.40e-12`.
5. S9 per-seed variance and cost factors and their geometric mean, table in §4.2; geomean `176860.5241415622` versus the
   committed `176860.52414156235`.
6. `2.1411108700917687 / 2.016433193279511 = 1.0618307996653649`, matching the committed `derived_isolated_ratios`.

---

## 7. How to falsify this paper

Stated so a successor does not have to invent the attack.

- **Break the dichotomy** by exhibiting an admissible field `Phi` (D1) whose rewrite of `T_G` is valid on all of `F_d`,
  whose K-deposit vanishes, and which nonetheless does not reduce to a reweighting of point evaluations of `f`. By L3b
  and L4 that is impossible under (U) and (L), so a counterexample must violate one of them explicitly — and naming
  which one is the useful part of the counterexample.
- **Break the rigidity lemma** by finding a map `psi : W -> R^d` satisfying `(psi(w') - psi(w)) . (w' - w) = 0` for all
  `w, w'` in `W` whose `W`-component is not affine with antisymmetric linear part. The proof in §3.3 is four lines of
  algebra; if it is wrong, it is wrong at (**).
- **Break the class-A optimality** by exhibiting an unbiased radial reweighting with variance below exact conditioning.
  By §3.7 that contradicts Cauchy-Schwarz, so a positive result is a metering or unbiasedness error — check
  `E[w(R) R] = m_d` first.
- **Break the pricing claim, which is the weak half.** Build a class-B estimator whose variance-per-FLOP at width 256
  depth 32 is within 100x of matched-budget radially-conditioned Monte Carlo. S9's zero-enumeration-cost variance factor
  of 189-196x is the bar to clear even with a free oracle for every crossing and jump; P2 §5 states the same bar and
  names the two obvious attacks (stratify by layer, importance-sample lines toward high-`|J|` cones). A success here
  would not falsify the theorem — it would falsify §4.2's reading of the ledger, which is the more useful target.
- **Close the two [GAP]s.** (i) The isolated-radial account of §4.1, by measuring
  `avg_k E[g_k^2] / avg_k Var(g_k)` on the fold3 terminal observable. (ii) The 556.709 / 556.305 near-collision of
  §4.2, by locating either harness. Both are cheap; neither is possible under this paper's firewall.
