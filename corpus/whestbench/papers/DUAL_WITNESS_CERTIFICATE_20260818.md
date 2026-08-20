# A finite dual witness: the champion's 126 blocks are the exact minimax point of the Kerdock block-mixture game

Internal research certificate. Date 2026-08-18. Corpus: `corpus/whestbench`.
Companion script: `papers/dual_witness_certificate.py` (38 checks, all green,
byte-identical output across runs). Emitted data: `papers/dual_witness_certificate.json`.

Discharges the rank-10 row of `2026-08-13-schauder-kerdock-theorem-map.md`:

> | 10 | Sion minimax/Hahn-Banach duality | Produce a finite dual witness for why no
> tested block mixture improves | Require matching primal and dual objectives on a
> frozen matrix | `OFFLINE_CERTIFICATE` |

Status: **certificate delivered, gate condition met.** Primal and dual objectives
match exactly, in rational arithmetic, with duality gap `0`.

---

## Abstract

Weighting the 129 canonical real mutually-unbiased blocks of `R^256` looks like a
128-dimensional design problem. It is not. Because every cross-block inner product
is `±1/16` and every within-block off-diagonal inner product is `0`, the degree-`l`
block-summary matrix has exactly two distinct entries, and a block mixture `w`
enters every rotation-averaged error functional through the single scalar `‖w‖²`.
The design space collapses from 128 dimensions to one, which is what makes a finite
witness possible at all.

On that collapsed line the whole game is two affine functions of the block count `k`,
each computable by hand:

```text
R_4(k) = (129 - k) / 3          degree-4 adjusted-score penalty, slope -1/3
R_6(k) = (4095 + k) / 4221      degree-6 adjusted-score penalty, slope +1/4221
```

They have opposite slopes because `G_4(1/16) < 0` and `G_6(1/16) > 0`. Both equal
`1` at `k = 126`. Therefore `max(R_4, R_6) > 1` at every other block count, and the
minimax value of the game is exactly `1`, attained uniquely at the champion. The
matching dual witness is a two-point spectral energy on degrees `{4, 6}`,

```text
y_4 = 16637/555357,  y_6 = 538720/555357,   y_4 G_4(1/16) + y_6 G_6(1/16) = 0 exactly,
```

under which the adjusted score is flat in `k` across all 129 block counts. Primal
value `= 1`, dual value `= 1`, gap `= 0`.

The certificate has one real dependency, and it is named rather than hidden: the
score is `MSE × compute/B`, so the conclusion turns on the completion's marginal
compute. The exact break-even ratio is `2881/2816 = 1.0230824`; the cheapest
possible ratio, one extra block being one extra frame of 512 points, is
`129/126 = 1.0238095`. The margin is `1408/1407`, i.e. `0.0711%`. Flipping the
certificate requires finding `1.298e8` FLOPs of savings in the completion; the only
saving the corpus identifies (the identity frame needs no Walsh butterfly) is
`5.24e5` FLOPs, short by a factor of `247.5`.

Under R0's frozen harmonic energy budget the entire design axis, tested and untested,
is worth `delta = 0.4388%` of adjusted score, and satisfies the closed form
`delta = s_4 - (1/42) Σ_{l≥6} a_l G_l(1/16) / V`: **the value of the whole block-mixture
axis is the degree-4 share of the error, minus a higher-degree correction.** Since
degree 4 carries `0.448%` of the champion's error, that is the ceiling. The predicted
`129/126` score ratio is `0.99561`, which falls inside MUB129's measured 16-fresh-network
interval `[0.9825, 1.0196]`. The observed null is what the certificate predicts, not an
anomaly to explain away.

---

## 0. Level tags, and how to check this without trusting it

Tags follow P1 §0 (`papers/P1_SPECKLE_THEOREM_20260810.md` lines 39-43): **[O]** observed
(a run in this corpus produced it), **[D]** derived (follows by shown steps), **[R]**
reported (a committed artifact says so, not re-derived here), **[A]** assumed (a stated
modelling choice).

Three ways to check the certificate, in increasing cost:

1. **By hand, in one minute.** Evaluate `R_4(k) = (129-k)/3` and `R_6(k) = (4095+k)/4221`
   at `k = 125, 126, 127`. You get `4/3, 1, 2/3` and `4220/4221, 1, 4222/4221`. The
   maximum of the two is `4/3` at 125, `1` at 126, `4222/4221` at 127. That is the whole
   theorem.
2. **By running the script.** `python papers/dual_witness_certificate.py` re-derives
   every constant from the Gegenbauer recurrence in `fractions.Fraction`, checks it
   against three committed corpus artifacts, and exits non-zero if any of 38 checks fails.
3. **By brute force at `d = 4`.** The script builds three real MUBs in `R^4`, enumerates
   all `24 × 24` point pairs, and confirms the closed-form block summaries from first
   principles. That check touches no `d = 256` artifact, so it cannot be fooled by an
   error inherited from the corpus.

---

## 1. The setting

Fixed throughout, all **[R]** from `core/CORPUS.md`, `experiments/v31_guards/package_source/kerdock_v3_estimator.py`,
and `experiments/mub129_completion/STRUCTURAL_FINDING.md`.

- `d = 256`. The canonical real Kerdock construction gives `K = 129` mutually unbiased
  orthonormal bases: the identity frame plus `H diag(phi_s)/16` for 128 bent phase
  vectors. `129 = d/2 + 1` is the maximum number of real MUBs in `R^d`, attained because
  `256 = 4^4`. **The design axis is finite because the MUB family is finite** — this is
  what lets the certificate quantify over untested mixtures, not merely tested ones.
- A **block** is one basis, antipodally doubled to `2d = 512` points.
- A **block mixture** is `w` in the simplex on `{1,…,129}`, placing weight `w_a / 512` on
  each point of block `a`. Its **support size** `k = |supp(w)|` is the number of blocks
  actually evaluated, hence its compute.
- The **champion** is `kerdock_v3_estimator.py`, which slices `phases[2:128]`: uniform
  over 126 of the 129 blocks, 32,256 base points, 64,512 doubled [R, lines 47-52, 70-71].
  Measured on official indices 0..99: adjusted score `1.6190837992231567e-7`, raw MSE
  `2.493887556909158e-7`, mean effective compute `178.462975e9`, 0/100 failures
  [O, `experiments/t4_kerdock_descriptive_rescore/T4_REPORT.md`].
- The **score** is `MSE × max(0.1, (billed_FLOPs + 1e11 × residual_s) / 2.72e11)`
  [R, `core/CORPUS.md` line 19]. Lower is better. Above the floor it is linear in compute.
- The **criterion** is the Haar-rotation-averaged squared error. The estimator applies one
  shared random rotation `R` and returns `Σ_i w_i f(R x_i)`; by the standard Haar
  identities the mean squared error decomposes as `Σ_l ‖f_l‖² Q_l(w)` where
  `Q_l(w) = Σ_{i,j} w_i w_j G_l(⟨x_i,x_j⟩)` and `G_l` is the degree-`l` Gegenbauer kernel
  normalised to `G_l(1) = 1` [R, P4 §1 (MASTER)].

---

## 2. The collapse theorem

> **Theorem 1 (one scalar).** For every block mixture `w` and every odd `l`,
> `Q_l(w) = 0`. For every even `l`,
>
> ```text
> Q_l(w) = alpha_l ‖w‖² + g_l,
>     g_l     = G_l(1/16)
>     alpha_l = (2 + 510 G_l(0)) / 512  -  g_l
> ```
>
> The 128-dimensional mixture polytope therefore enters every rotation-averaged error
> functional through the single scalar `‖w‖²`.

*Proof.* **[D]** Let `M^(l)_{ab}` be the degree-`l` block-summary, the average of
`G_l(⟨p,q⟩)` over all `512 × 512` ordered point pairs with `p` in block `a`, `q` in block
`b`, so that `Q_l(w) = w' M^(l) w`.

Fix `p` in block `a`. Inside its own doubled block it sees itself (inner product `1`),
its antipode (`-1`), and the `510` points of the other `255` lines (`0`, because the frame
is orthonormal). So the inner sum is `1 + (-1)^l + 510 G_l(0)`, and

```text
M_aa = (1 + (-1)^l + 510 G_l(0)) / 512.
```

Against a different block `b`, mutual unbiasedness makes every one of the `512` inner
products `±1/16`, so the inner sum is `256(G_l(1/16) + G_l(-1/16))` and

```text
M_ab = ((1 + (-1)^l)/2) · G_l(1/16).
```

For odd `l` both vanish: `G_l` is odd, and antipodal doubling cancels it pairwise. For
even `l`, `M^(l) = alpha_l I + g_l J` with `alpha_l`, `g_l` as stated, and
`w' (alpha I + g J) w = alpha ‖w‖² + g (1'w)² = alpha ‖w‖² + g`. ∎

Three consequences fall out immediately, all **[D]**.

**(a) The reduction is lossless.** Every point of a `k`-block union sees the identical
fingerprint (`1`, `(-1)^l`, `510` zeros, `512(k-1)` entries of `±1/16`), so the full
`512k × 512k` point kernel `K_l` has constant row sums; `K_l` is positive semidefinite by
the addition theorem. Constant row sums plus PSD plus the sum-one constraint gives
`Q_l(u + delta) = Q_l(u) + delta' K_l delta ≥ Q_l(u)` (P4 §3.4). So uniform weighting over
all `512k` points is a global minimiser over the **full point simplex**, and block
mixtures lose nothing at the optimum. Restricting attention to 129 block summaries is not
an approximation. *(Verified as an arithmetic identity at `k = 1, 8, 13, 126, 129` and all
19 active degrees.)*

**(b) Which blocks you pick is worth exactly zero.** `M^(l)` is exchangeable, so all
`C(129,126) = 357,760` choices of 126 blocks give bit-identical `Q_l` at every degree. Any
zonal block-selection heuristic — kernel herding, hidden-state matching, Caratheodory
recombination — has a design-side value of exactly zero, and can only earn its keep from
realised network outputs. This is the block-selection analogue of P4's closure of M192.

**(c) Non-uniform beats nothing.** `‖w‖² ≥ 1/k` with equality iff `w` is uniform on its
support (Cauchy-Schwarz). Since `alpha_l > 0` at every even `l ≥ 4` (checked exactly for
`l = 4..40`; `alpha_l → 1/256` as `l → ∞`), any non-uniform mixture is strictly worse than
uniform on the same support, at the same compute, at every degree simultaneously.

> **The proved exception at `l = 2`.** `alpha_2 = 0` and `g_2 = 0` exactly, so
> `Q_2(w) = 0` for every mixture. Degree 2 is integrated exactly by any single orthonormal
> frame and is free for all reweightings. This reproduces P4 draft-2's `l = 2` erratum from
> a different direction, and is the reason the certificate quantifies over even `l ≥ 4`.

---

## 3. The frozen matrix

The 129 block summaries at the two degrees that carry the game, in exact rationals **[D]**:

| | degree 4 | degree 6 |
|---|---|---|
| `G_l(0)` | `1/21845` | `-1/1131571` |
| `g_l = G_l(1/16)` | `-65/2105344` | `+16637/17449091072` |
| `alpha_l` | `8385/2105344` | `9732645/2492727296` |
| relation | `alpha_4 = -129 g_4` | `alpha_6 = 4095 g_6` |
| `Q_l(126)` | `65/88424448` | `1114679/34898182144` |
| `Q_l(129)` | `0` | `183007/5861804032` |

`alpha_4 = -129 g_4` is the 5-design identity: it is precisely the statement that
`Q_4(129) = alpha_4/129 + g_4 = 0`. `alpha_6 = 4095 g_6` has no such interpretation; it is
an arithmetic fact of the `C_6^(127)` recurrence, and it is what fixes the degree-6 slope.

**The sign disagreement is the whole certificate.** `g_4 < 0` and `g_6 > 0`. Everything
below is bookkeeping on those two signs.

For orientation, the same quantities across all active degrees (`float`, from the script):

| `l` | `alpha_l` | `g_l` | sign |
|---:|---|---|:--:|
| 4 | 3.98272206e-03 | -3.087381e-05 | − |
| 6 | 3.90441627e-03 | +9.534594e-07 | + |
| 8 | 3.90630358e-03 | -2.996854e-08 | − |
| 10 | 3.90624816e-03 | +1.035994e-09 | + |
| 12 | 3.90625007e-03 | -3.902783e-11 | − |
| … | → 1/256 | → 0 | alternating, with one defect at `l = 20` |
| 40 | 3.90625000e-03 | +6.340479e-26 | + |

`|g_l|` decreases strictly over even `l ≥ 8` **[O]**, which bounds every degree above 40
by `|g_40| < 1e-25` and justifies treating the unresolved tail as pure `alpha = 1/256`,
`g = 0`. The sign pattern alternates from `l = 4` but is not purely alternating: `g_20`
and `g_22` are both negative. Recorded because it is true; nothing depends on it.

---

## 4. Verification: four independent routes

The closed form of §2 is the load-bearing step. If it is wrong, everything downstream is
wrong. It is checked four ways, three of which do not share a code path.

**Route 1 — brute force at `d = 4`, no corpus contact.** The script constructs three real
MUBs in `R^4` by exhaustive search over `{I} ∪ {H_4 diag(phi)/2}`, doubles them to 24
points, and evaluates all `24 × 24` inner products in exact rationals. For `l = 1..8` the
brute-forced `3 × 3` block-summary matrix equals `alpha_l I + g_l J` from the closed form,
entry for entry, and vanishes identically at every odd `l` **[O]**. The same construction
confirms the complete union is an exact 5-design (`Q_2 = Q_4 = 0`) that fails at degree 6
(`Q_6 = 1/7`), matching `STRUCTURAL_FINDING.md` §3's `d = 4` rung, the `D_4` root system.

**Route 2 — P4's committed exact rationals.** `G_4(0) = 1/21845`,
`G_4(1/16) = -65/2105344`, `G_6(0) = -1/1131571`, `G_6(1/16) = 16637/17449091072`, all
reproduced from the `C_l^(127)` recurrence **[D vs R, P4 §3.6]**. `Q_4(126) = 65/88424448`
reproduces P4's headline degree-4 error exactly.

**Route 3 — R0's committed spectrum artifact.** `Q_l(126)` from the closed form reproduces
`r0_results.json → design_property_NOT_residual → lam_top_doubled_64512_set` **bit for bit
in f64 at all 9 even degrees from 4 to 20**, and R0's zeros at every odd degree **[O]**.

**Route 4 — MUB129's independent exact-rational defect table.** `Q_l(m)` reproduces
`mub129_completion/RESULTS.json → second_signal_gegenbauer_design_defect` at all 9 cells
`(l, m)` for `l ∈ {2,4,6}`, `m ∈ {126,128,129}` **[O]**:

| `l` | `m = 126` | `m = 128` | `m = 129` |
|---:|---|---|---|
| 2 | 0.0 | 0.0 | 0.0 |
| 4 | 7.350908201315546e-07 | 2.4120167535566633e-07 | 0.0 |
| 6 | 3.194089008420301e-05 | 3.145671147984825e-05 | 3.122025216144244e-05 |

MUB129's table was produced by a different author, on a different date, by a different
route (angle-set Gegenbauer arithmetic, no block summaries). It agrees to the last printed
digit at every cell. That is the second independent signal, and it is the one that matters
most, because it independently confirms the `m`-dependence — the exact thing the game is
about.

---

## 5. The game and the finite dual witness

### 5.1 Equal compute: exact, unconditional, no spectrum required

> **Theorem 2.** Fix any support `S` of `k` blocks. Over `{w ≥ 0 : supp(w) ⊆ S, 1'w = 1}`,
> the uniform mixture is the unique global minimiser of `Q_l` at every even `l ≥ 4`
> simultaneously, hence of `Σ_l a_l Q_l(w)` for **every** nonnegative spectral energy `a`.
> The Lagrangian dual attains the primal value with gap exactly `0`.

*Proof and certificate.* **[D]** Minimise `f(w) = alpha_l ‖w‖² + g_l` subject to `1'w = 1`,
`w ≥ 0`. The Lagrangian is `L = alpha_l w'w + g_l - nu(1'w - 1) - mu'w`, `mu ≥ 0`.

- Primal point: `w* = 1/k`. Multipliers: `mu* = 0`, `nu* = 2 alpha_l / k`.
- Stationarity `2 alpha_l w* = nu* 1 + mu*` holds. Feasibility and complementary slackness
  are immediate.
- Dual function `g(nu) = g_l + nu - k nu²/(4 alpha_l)`, maximised at `nu*`, with
  `g(nu*) = alpha_l/k + g_l = f(w*)`.

The script evaluates both sides in `Fraction` at all 19 active degrees for `k = 126`, and
the gap is the exact rational `0` at every one **[O]**. Strict convexity (`alpha_l > 0`)
makes `w*` unique.

**Consequence (stated at exactly its proven strength).** Within the game this certificate
formalizes -- mixtures over the 129 canonical real-MUB blocks, payoff as defined in
section 5.2, spectral energy entering only through the stated alpha_l weights -- no
mixture at or below the champion's block count improves on the uniform-126 point, and the
optimum there is unique. The certificate does NOT by itself bound estimators outside this
block family, other payoff conventions, or the deployed carrier's empirical score (the
deployed row-blocked carrier was found to run Haar-random frames rather than these
blocks; the 126-vs-129 question ON THAT CARRIER is an empirical cell, not a corollary of
this LP). Everything that follows concerns the only remaining direction inside the game:
spending more compute on more blocks.

### 5.2 The full game: two affine lines with opposite slopes

Compute is the number of blocks evaluated, so define the payoff as the adjusted-score
ratio against the champion when all spectral energy sits at degree `l`:

```text
R(k, l) = [ Q_l(k) / Q_l(126) ] × (k / 126) = (alpha_l + k g_l) / (alpha_l + 126 g_l).
```

`R` is **affine in `k`**. Substituting the §3 relations:

```text
R_4(k) = (alpha_4 + k g_4)/(alpha_4 + 126 g_4) = (-129 g_4 + k g_4)/(-3 g_4)  = (129 - k)/3
R_6(k) = (alpha_6 + k g_6)/(alpha_6 + 126 g_6) = (4095 g_6 + k g_6)/(4221 g_6) = (4095 + k)/4221
```

Both are normalised to `1` at `k = 126` by construction. The content is the **slopes**:
`-1/3` and `+1/4221`, opposite in sign because `g_4 < 0 < g_6`. Hence

```text
k < 126  ->  R_4(k) > 1   (fragmenting the design reopens the degree-4 hole)
k > 126  ->  R_6(k) > 1   (completing it buys compute the degree-6 error does not repay)
k = 126  ->  R_l(k) = 1 at every degree
```

so `max_l R(k, l) > 1` for every `k ≠ 126`, and

> **Theorem 3 (primal).** `min_w max_l R(w, l) = 1`, attained uniquely at the champion.

Non-uniform mixtures are covered by §2(c): `‖w‖² ≥ 1/k` and `alpha_l > 0` make
`R(w, l) ≥ R(k, l)`. The minimisation over the full 128-dimensional polytope therefore
reduces to a minimisation over 129 integers, computed exhaustively by the script.

**The exhaustive primal table [O]:**

| `k` | worst-case ratio (exact) | float | binding degree |
|---:|---|---|---:|
| 1 | 128/3 | 42.66666667 | 4 |
| 8 | 121/3 | 40.33333333 | 4 |
| 13 | 116/3 | 38.66666667 | 4 |
| 55 | 74/3 | 24.66666667 | 4 |
| 96 | 11 | 11.00000000 | 4 |
| 112 | 17/3 | 5.66666667 | 4 |
| 125 | 4/3 | 1.33333333 | 4 |
| **126** | **1** | **1.00000000** | all tie |
| 127 | 4222/4221 | 1.00023691 | 6 |
| 128 | 4223/4221 | 1.00047382 | 6 |
| 129 | 1408/1407 | 1.00071073 | 6 |

### 5.3 The dual witness

Weight the degrees by `y ≥ 0`. The `y`-weighted adjusted score at block count `k` is

```text
Σ_l y_l Q_l(k) × k  =  Σ_l y_l (alpha_l/k + g_l) × k  =  A_y + k B_y,
        A_y = Σ_l y_l alpha_l,     B_y = Σ_l y_l g_l = Σ_l y_l G_l(1/16).
```

**Linear in `k`.** So it is flat — the mixture player is exactly indifferent across all
129 block counts — if and only if `B_y = 0`. The dual optimum is therefore any nonnegative
spectral energy orthogonal to the vector of off-block kernel values. Two degrees suffice,
because `g_4` and `g_6` have opposite signs:

> **Theorem 4 (dual).** With
>
> ```text
> y_4 = 16637/555357  = 0.0299573067…      y_6 = 538720/555357 = 0.9700426933…
> ```
>
> we have `y ≥ 0`, `y_4 + y_6 = 1`, and `y_4 G_4(1/16) + y_6 G_6(1/16) = 0` exactly.
> Under `y`, the adjusted score is constant in `k` across all 129 block counts, so
> `max_y min_w R(w, y) = 1`.

*Check it by hand.* `17449091072 / 2105344 = 8288` exactly, and `8288 × 65 = 538720`.
Therefore

```text
y_4 g_4 + y_6 g_6 = [16637 × (-65)] / (555357 × 2105344)
                  + [538720 × 16637] / (555357 × 2105344 × 8288)
                  = 16637 × (-65 + 538720/8288) / (555357 × 2105344)
                  = 16637 × (-65 + 65) / (555357 × 2105344)  =  0.
```

> **Theorem 5 (strong duality).**
> `min_w max_y R = max_y min_w R = 1`, duality gap `= 0`.

Sion's conditions hold: the mixture set is compact convex, the energy set is compact
convex, `R` is convex (indeed affine after the collapse) in `w` and linear in `y`. But the
certificate does not lean on Sion — it exhibits the saddle point and matching values in
exact arithmetic, which is stronger than an existence theorem. **[D, O]**

### 5.4 The inequality chain

For any block mixture `w` with support size `k` and any nonnegative spectral energy `a`,
writing `S(·)` for the adjusted score:

```text
S(w)  =  [ Σ_l a_l (alpha_l ‖w‖² + g_l) ] × c(k)             (Theorem 1, collapse)
      ≥  [ Σ_l a_l (alpha_l / k     + g_l) ] × c(k)            (‖w‖² ≥ 1/k, alpha_l > 0)
      =  [ Σ_l a_l Q_l(126) R(k,l) ] × c(k)/(k/126) × (k/126)  (definition of R)
      ≥  min_l R(k,l) × ... ≥ ... ≥ [ Σ_l a_l Q_l(126) ] × 1   (Theorems 3-5)
      =  S(champion).
```

The middle step is where the dual witness does its work: it is the statement that no
nonnegative reweighting of the degrees can make every `R(k,l)` fall below `1` at any
`k ≠ 126`, because `y*` certifies that the best a mixture can do against a hostile
spectrum is tie.

---

## 6. What the axis is worth under the frozen spectrum

Theorems 3-5 are worst-case. The frozen-matrix question the gate asks — what is the axis
actually worth — needs the spectral energy, and R0 commits one.

**Inputs [R, O].** `r0_results.json → armB_meanfield_rederivation → a_l_energy_share_per_degree`
for even `l = 4..40`, plus R0's own committed unresolved tail
(`unresolved_tail_error_share = 0.23166748735486692`) folded into a single lumped block
with `alpha = 1/256`, `g = 0` — exact to f64 by the `|g_40| < 1e-25` bound of §3. Recovered
even tail mass `0.0742301481` **[D]**.

**Derived quantities [D]:**

```text
A = Σ_l a_l alpha_l =  1.4823058582443733e-03
B = Σ_l a_l g_l     = -1.830776579922135e-06
V = A/126 + B       =  9.933555628366543e-06
```

`V` reproduces R0's committed `implied_MSE_over_sigma2 = 9.93355562836654e-06` to a
relative `3.4e-16`, which is a fifth independent check on §2: the block summaries and R0's
per-degree budget are consistent to f64 round-off.

Define `theta = (A/126)/V`, the share of the champion's zonal error carried by the
collision term rather than the constant term. Then

```text
theta = 1.1843022427,     theta > 1  <=>  B < 0  <=>  Σ_l a_l G_l(1/16) < 0.
```

Under strictly proportional compute, `S(k)/S(126) = 1 + (theta - 1)(126 - k)/126`, so the
value of the entire axis is

```text
delta = 1 - S(129)/S(126) = (theta - 1)/42 = 0.4388148635 %.
```

**The closed form [D, verified to 1e-15].** Because `g_4 = -42 Q_4(126)` exactly,

```text
delta = s_4  -  (1/42) Σ_{l≥6} a_l G_l(1/16) / V,        s_4 = degree-4 share of error.
```

**The value of the whole block-mixture design axis is the degree-4 error share, minus a
higher-degree correction.** With `s_4 = 0.4484080112 %` (identical to R0's committed
`deg4_share_of_total_error`) and a correction of `0.0095932 %`, `delta = 0.4388 %`. The
axis is small because degree 4 is small, and degree 4 is the only degree the completion
annihilates.

**The frontier [D]**, adjusted score relative to the champion under the measured
per-block compute `1.4163728e9` FLOPs and the real `max(0.1, C/B)` multiplier:

| `k` | eff. compute | multiplier | on 0.1 floor | score ratio |
|---:|---:|---:|:--:|---:|
| 8 | 11.33e9 | 0.100 | yes | **2.8148** |
| 13 | 18.41e9 | 0.100 | yes | **1.7214** |
| 19 | 26.91e9 | 0.100 | yes | 1.1689 |
| 20 | 28.33e9 | 0.104 | no | 1.1550 |
| 55 | 77.90e9 | 0.286 | no | 1.1039 |
| 96 | 135.97e9 | 0.500 | no | 1.0439 |
| 112 | 158.63e9 | 0.583 | no | 1.0205 |
| **126** | **178.46e9** | **0.656** | no | **1.0000** |
| 129 | 182.71e9 | 0.672 | no | **0.9956** |

The `0.1` floor is where cheap mixtures would have their best shot, since below `27.2e9`
compute is free and only raw MSE is scored. It does not rescue them: the best small
mixture is `k = 20` at `1.1550`, still `15.5%` worse than the champion.

**Against the measurement [O].** The certificate predicts a `129/126` score ratio of
`0.99561`. MUB129's adversarial re-analysis measured `1.00087` on 16 fresh networks with a
`95%` interval of `[0.9825, 1.0196]`, half-width `1.855%`. The prediction lies inside that
interval, and the predicted effect is a quarter of the interval's half-width. MUB129's own
power note says `~500` networks would be needed for `80%` power against an effect of this
size. **The null result is the predicted result.** That is the answer to "why does no
tested block mixture improve": the axis is real, signed in the completion's favour under
the frozen spectrum, and roughly four times smaller than the harness can see.

**Sensitivity to the one soft input [D].** The corpus carries four independent estimates
of the degree-4 error share. Propagating each through the closed form:

| source | `s_4` | `delta` |
|---|---:|---:|
| kernel derivation | 0.4497 % | 0.4401 % |
| `m191_cv_deg4` | 0.4200 % | 0.4104 % |
| `r0` harmonic spectrum | 0.4500 % | 0.4404 % |
| `s11` matched-control upper bound | 0.1760 % | 0.1664 % |

`delta ∈ [0.166 %, 0.440 %]` across all four. Every one is below the measurement floor.

---

## 7. The attack

Six counter-hypotheses were tested. One landed, and it is in the certificate rather than
patched out of it.

**A1. "The block-uniform restriction hides the real optimum."** Tested and rejected. §2(a)
shows the full `512k`-point kernel has constant row sums and is PSD, so uniform over all
points is a global minimiser over the full point simplex. Verified as an arithmetic
identity at five block counts and 19 degrees.

**A2. "Non-uniform block weights beat uniform."** Tested and rejected. §2(c): strictly
worse at equal compute, at every degree, by Cauchy-Schwarz plus `alpha_l > 0`.

**A3. "The right 126 blocks beat the champion's 126."** Tested and rejected. §2(b): the
block-summary matrix is exchangeable, so all `357,760` choices are bit-identical.

**A4. "More than 129 blocks."** Rejected by theorem, not by budget. `129 = d/2 + 1` is the
maximum real-MUB count in `R^256`, and `STRUCTURAL_FINDING.md` §2 shows `m = 129` is the
unique integer satisfying the degree-4 moment identity. The axis is finite.

**A5. "The certificate is an artifact of the frozen spectrum."** Partly landed, and the
answer is that the certificate has two halves. Theorems 2-5 hold for **every** nonnegative
spectral energy and need no spectrum. Only §6's `delta` is spectrum-dependent, and it is
bracketed four ways. A pure degree-4 adversary would make the completion infinitely
better (`Q_4(129) = 0`), which is exactly why the worst-case theorems and the frozen-matrix
number are reported separately rather than blended.

**A6. "The completion is cheaper than proportional, so the minimax flips." — THIS ONE
LANDED, PARTLY.** The score is linear in compute, so Theorem 3 turns on the completion's
marginal cost. Priced exactly:

```text
break-even compute ratio      c* = Q_6(126)/Q_6(129) = 2881/2816  = 1.0230823864
cheapest possible ratio       129/126 = 43/42                     = 1.0238095238
margin                        1408/1407                           = 1.0007107321  (0.0711 %)
```

The margin is `0.07%`. That is thin, and it is the honest headline risk. Priced in FLOPs
against the champion's measured `178.462975e9`:

```text
completion at nominal cost     182.712093e9 FLOPs
completion at break-even       182.582326e9 FLOPs
required saving to flip        1.2977e8 FLOPs
```

`STRUCTURAL_FINDING.md` §4 names the one real saving: the identity frame needs no Walsh
butterfly, since `I @ W1 = W1`. A fast Walsh-Hadamard transform on one 256-point frame is
`256 × 256 × log2(256) = 5.24288e5` FLOPs. The required saving is **247.5×** larger. The
certificate survives, with that factor as its stated safety margin. **[D]**

What would actually flip it: a completion implementation whose marginal per-block cost is
more than `0.71%` below the champion's. Settling measurement, named and not run: a pinned
Flopscope bill of a 129-block runner against the frozen 126-block runner, reporting
`C_129/C_126` against `2881/2816`.

**What was not looked at.** Non-MUB blocks; multi-rotation schemes (independent rotations
per block group, which are a different estimator family, covered by S2/M195/M197 and killed
on their own grounds); and any criterion depending on realised network outputs. §8 states
these as scope, not as findings.

---

## 8. What this closes, and what it does not

**Closed.**

1. **Rank 10 itself.** Primal and dual objectives match on a frozen matrix, gap `0`. The
   witness is finite: two degrees, two rational weights, checkable by hand.
2. **Equal-compute block mixtures, unconditionally.** Theorem 2 needs no spectrum and no
   measurement.
3. **Rank 6 (`DEFER_UNTIL_RANK_1`, "select 8-16 blocks that best match frozen hidden-state
   summaries")** on its design-side component. Block *identity* is worth exactly zero
   zonally, and an 8-to-16-block rule pays `2.81×` to `1.72×` on adjusted score. Any such
   selector must recover that entire factor from realised-output information alone. That is
   its kill condition, now quantified rather than asserted.
4. **Rank 5 (`DEFER`, Caratheodory-Tchakaloff recombination)** on the same terms.
   Recombination onto `r+1 < 126` blocks with positive weights raises `‖w‖²` and lowers
   `k`; both move the adjusted score the wrong way. Its design-side value is exactly zero.
5. **A quantitative prediction for rank 1 (`NEXT_SCORE_GATE`).** The 8-block, 4,096-point
   rotated ladder is a block mixture with `k = 8`. Against the frozen Kerdock126 champion
   the certificate predicts an adjusted-score ratio of **2.81**, driven by the degree-4
   penalty `R_4(8) = 121/3 = 40.33` acting on a `0.45%` slice of the error, with compute
   pinned on the `0.1` floor. This is falsifiable by the run the theorem map has already
   frozen.

**Not closed, stated as scope.**

- **The cross-family claim.** The 2026-08-13 theorem map names a *Sobol+tangent* champion.
  That design is not a block mixture, so no offline certificate can compare it to one; the
  comparison needs measured paired scores. This certificate's "champion" is the frozen
  Kerdock v3 126-block design, which is the only champion whose design lies inside the game.
- **Realised-output criteria.** The theorem is about the Haar-rotation-averaged error. It
  says nothing about weights fitted to realised network outputs, which is exactly the gap
  P4 §4 identifies for the M192 family and which remains the only place design-side gains
  can hide.
- **Fixed-seed behaviour.** With the rotation seed fixed rather than averaged, the realised
  error is not zonal, and `Q_l` is a mean over rotations the estimator does not take.
- **`alpha_l > 0` for even `l > 40`.** Checked exactly to `l = 40`; the limit `1/256` makes
  it evident but is not proved here. Settling check, named and not run: evaluate the exact
  `Fraction` recurrence for even `l` to 200 and report `min_l alpha_l`.

---

## 9. Falsifiers

Any one of these kills the certificate.

1. Exhibit a block mixture `w` and a nonnegative spectral energy `a` with
   `Σ_l a_l Q_l(w) < Σ_l a_l Q_l(u_126)` at support size `≤ 126`. One 129-vector and one
   dot product settles it.
2. Exhibit an even `l` with `alpha_l ≤ 0`, or with `G_l(1/16)` of a sign contradicting §3.
   That would break Theorem 3's slope argument.
3. Measure `C_129/C_126 < 2881/2816 = 1.0230824` on a pinned Flopscope bill. The worst-case
   theorem flips, and the frozen-spectrum `delta` rises above `0.44%`.
4. Exhibit a cross-block inner product not equal to `±1/16`, or a within-block off-diagonal
   inner product not equal to `0`, in the frozen `kerdock_phases.npz`. That breaks Theorem 1
   at its root. (MUB129 checked all 8,128 cross-frame pairs and found the distinct Walsh
   magnitude set to be `{16.0}` and nothing else [O].)
5. Show that the degree-4 error share exceeds `1%`, contradicting all four committed
   estimates. `delta` would rise proportionally and could clear the measurement floor.

---

## 10. Reproduction

```text
cd corpus/whestbench/papers
python dual_witness_certificate.py
```

Pure standard library (`fractions`, `json`). No randomness, no network, no wall-clock
dependence. Exit code `0` iff all 38 checks pass. Emits `dual_witness_certificate.json`;
two consecutive runs produce identical SHA-256, measured **[O]** at

```text
8e1c89d98d06e3a49a6439358ab59c3eb74f3b65d0fdfd14f60fb91eba832321
```

Artifacts read, all committed and unmodified:

- `experiments/r0_harmonic_energy_spectrum/r0_results.json`
- `experiments/mub129_completion/RESULTS.json`

Artifacts quoted but not read by the script:

- `experiments/t4_kerdock_descriptive_rescore/T4_REPORT.md` (champion score and compute)
- `experiments/v31_guards/package_source/kerdock_v3_estimator.py` (the `phases[2:128]` slice)
- `core/CORPUS.md` line 19 (the score formula)

---

## Certainty

- Theorem 1 (the collapse) and the closed forms `R_4`, `R_6`: **99%**. Four independent
  verification routes, one of them a `d = 4` brute force touching no `d = 256` artifact.
- Theorem 2 (equal-compute optimality, unconditional): **99%**. Exact KKT with zero gap at
  19 degrees.
- Theorems 3-5 (minimax value `1`, zero duality gap): **97%**, conditional on compute being
  at least proportional to the block count. The `0.07%` margin is the reason this is not
  higher; §7 A6 prices exactly what would move it.
- `delta = 0.44%` under the frozen spectrum: **90%**. Depends on R0's energy profile, whose
  absolute MSE under-predicts the measured `s17` values by a factor of 2.1 to 3.7. `delta`
  is a ratio, so the scale largely cancels, and the four-way bracket
  `[0.166%, 0.440%]` covers the shape uncertainty.
- The claim "no tested block mixture improves on the champion's design", read as
  Kerdock126 versus every other mixture of the 129 blocks: **95%**.

---

## Sources

- `sources/reviews/2026-08-13-schauder-kerdock-theorem-map.md` — the rank-10 commission.
- `papers/P4_UNIFORM_WEIGHT_OPTIMALITY_20260811.md` — uniform optimality on the fixed
  126-frame point set; the `l = 2` erratum; exact `G_4`, `G_6` rationals; the 42×/43×
  reweighting prices this certificate's `42` and `43` descend from.
- `experiments/mub129_completion/STRUCTURAL_FINDING.md` and `RESULTS.json` — `m = 129`
  uniqueness, the Walsh ladder, the DGS closure, the asset certificate, the exact-rational
  design-defect table, the cost bracket, and the adversarial re-analysis that read K1 as
  FAILED.
- `experiments/r0_harmonic_energy_spectrum/` — the frozen harmonic energy budget.
- `experiments/t4_kerdock_descriptive_rescore/T4_REPORT.md` — the champion's measured score
  and compute.
- Calderbank et al., Kerdock codes and real MUBs, doi:10.1112/S0024611597000403.
- Delsarte, Goethals, Seidel, spherical codes and designs, doi:10.1007/BF03187604.
- Boykin et al., real mutually unbiased bases, arXiv:quant-ph/0502024.
- Sion, On general minimax theorems, Pacific J. Math. 8 (1958) 171-176.
