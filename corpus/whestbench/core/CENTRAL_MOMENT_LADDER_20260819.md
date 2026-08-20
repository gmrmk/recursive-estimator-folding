# THE CENTRAL-MOMENT LADDER — the inferential/constructive lane

**Stamped:** 2026-08-19. **Lane:** inferential / constructive (`wf` sibling
`wf_8bf10a8c-1df` holds the descriptive lane on the excess gain; no table below
duplicates its data — every cross-reference to that object is a theorem about where
the excess *cannot* live, not a re-measurement of how big it is).

**Compute declaration.** Zero billed FLOPs against `B = 2.72e11`. Zero estimator wall
seconds. No Monte Carlo, no production run, no import of any estimator module. All
arithmetic below is exact-rational (`fractions.Fraction`), exact-integer, or
deterministic special-function evaluation (`math.erfc`, `math.lgamma`) in the session
scratchpad under `python -B -P` with `PYTHONDONTWRITEBYTECODE=1`. The deployed sources
at `experiments/row_blocked_production/candidate_source/` and
`experiments/v31_guards/package_source/` were opened read-only; nothing was written
outside this file and the scratchpad.

**Evidence tags.** `[O]` observed — read from source or computed this session.
`[D]` derived — follows from an observation by steps shown here. `[R]` reported — a
committed artifact or the channel says so. `[A]` assumed — a default chosen and
labelled. `[GAP]` named unknown with its settling check.

**Owner's direction, verbatim, as the governing frame:** *"moments about the mean …
the central moments, the deviations of the observations from their mean … what about
the other elements and the inference between them."*

**Death-law binding.** Fitted or trained coefficients are unlawful in a control;
theorem-fixed coefficients (exact closed forms, combinatorial identities) are lawful
by the death law's own criterion. Every construction below is priced against that line.

---

## 0. Verdict, first

**`lawful_construction_verdict = CLOSED-BY-DERIVATION`.**

The three candidate k-statistic corrections on the deployed `row_blocked` host close at
exactly computable numbers, and two of the three close at **zero**:

| candidate | closing number | why |
|---|---:|---|
| exact finite-`n` unbiasing of the squared-deviation mean | **identically 0** | the deployed code centres on the *exact analytic* mean, not on the sample mean, so `first_variance_residual` is already the known-mean central second moment, which is exactly unbiased at every `n`. The `n/(n−1)` k-statistic factor multiplies an object this estimator never forms. |
| `μ₄`-aware weighting of direction contributions | **identically 0** | the 32,256 directions are exchangeable within each orthonormal frame and the 126 frames are i.i.d., so the minimum-variance weight vector is uniform exactly — which is what `fnp.mean` already applies. The available weight space has zero free dimensions. |
| splitting the single `λ` into per-channel coefficients (or adding a third central-moment control) | **unlawful, or identical** | the only theorem-fixed coefficient vector is `(1, 1, …)`, because any other value destroys the first-order tangent identity that is the sole theorem in play. `(1,1)` collapses to the deployed single-`λ` structure. Anything else is fitted, hence dead under the death law. Priced anyway: `8,110,592` extra FLOPs, `ΔC/C = 3.647e-5`. |

**The one live constructive residue is a lawfulness upgrade, not an MSE gain:**
replace the host's fitted `moment_tangent_lambda = 0.9807112198896164` with the
theorem-fixed value `1`. That **removes the last fitted scalar from the correction
path**, **saves 256 FLOPs**, and costs exactly

> `(1 − λ)² / λ² = 3.8683631417925867e-4` of the MSE that the tangent control removes

under the labelled assumption that the frozen `λ` sits at the optimal `λ*` **[D + A]**.

**The instrument-doctrine deliverable stands regardless of that verdict:** the
**rung-2k law** of §2.6, with its predeclaration prescription.

**And one finding the corpus does not currently hold [O, exact]:** the four numeric
literals in the unreachable radial-reweight branch —
`257.0`, `66563.0`, `2600.0/537689.0`, `3.0/537689.0` — are **theorem-fixed, not
fitted**. They are reproduced here to the last digit as the exact rational solution of a
2×2 normal-equation system with integer coefficients (§3.a.4). `SECTION_ESTIMATOR_AND_CONSTANTS_ROW_BLOCKED_20260819.md`
classifies them only as "present, unreachable" and declines to classify their
lawfulness; they are lawful, and the reason is exact.

---

## 1. THE TARGET IS A CENTRAL MOMENT

### 1.1 The estimand, and the deviation field

Write `f` for the deployed estimator's final-layer output coordinate and `t` for the
truth it estimates: `t = E_{x∼ρ}[ f_net(x) ]`, the exact mean of one final-layer
activation over the input law. The graded quantity is the final-layer MSE,
`E[(f̂ − t)²]`.

Define the **deviation field** on the sphere:

```
D(u) = h(u) − t ,        h(u) = the final-layer value at direction u,        E_ρ[D] = 0
```

The estimator is (on its sampled blocks) a plain average of `h` over the carrier, so
its error is the **empirical first moment of a field whose true first moment is zero**:

```
ε = (1/N) Σ_i D(u_i) ,      E[ε] = 0  exactly  (each u_i is marginally uniform)
MSE = E[ε²] = Var(ε)
```

The graded target is therefore *literally* the second central moment of a
first-moment statistic of a centred field. Degree 0 — the mean — is not estimated,
suppressed, or shrunk; it is **subtracted exactly and then squared**. That is the whole
content of the campaign's foundational law.

### 1.2 Subtract-not-predict IS centre-before-square [D + R]

The `340.9x` closure gap **[R, `PHASE1_WRITEUP_DRAFT_20260808.md:364,748`;
`PHASE1_WRITEUP_SHORT_20260817.md:276`]** is the measured statement of exactly this.
A predicting estimator forms `f̂ = P(net)` and pays `E[(P − t)²]`, which carries the
full magnitude of `t` in its error budget. The subtracting estimator forms
`f̂ = a(net) + ε̂` where `a` is the exact analytic part and `ε̂` samples only the
residual, and pays `E[ε̂²]` alone. Centring before squaring collapses the estimator
variance because the squared magnitude of the centre never enters. The campaign
measured the collapse at `340.9x` raw-on-raw; the algebra above is why the collapse
exists at all.

### 1.3 The Gegenbauer degree ladder is the orthogonal decomposition of the deviation

Decompose `D` into spherical-harmonic degrees on `S^{255}`:

```
D = Σ_{l ≥ 1} D_l ,     a_l := ‖D_l‖²  (the degree-l energy of the deviation)
```

Degree 0 is the mean, removed exactly (§1.1). Degrees `l ≥ 1` are the mutually
orthogonal components of the deviation. The carrier's per-component quadrature error is
the **design defect** `A_l`, and the MSE decomposes as

```
MSE = Σ_{l ≥ 1} a_l · A_l                                   (§3.b proves this is exact,
                                                             with no cross-degree term)
```

**`A_l` is literally a variance, and it carries the `1/n` signature of a second central
moment [D, exact].** For a union of `k` orthonormal frames of size `m = d = 256` in
`R^256`, antipodally doubled, with `Q_l` the degree-`l` Gegenbauer normalised to
`Q_l(1) = 1`:

```
A_l,haar(k) = (1/N) [ 1 + (m−1)·Q_l(0) ] ,    N = m·k = 32,256 at k = 126
```

because within one frame every pair is exactly orthogonal (`u_i·u_j = 0`, contributing
`Q_l(0)` per ordered pair) and distinct frames are independent (contributing zero in
expectation). With

```
Q_l(0) = (−1)^{l/2} (l−1)!! / [ (d−1)(d+1)(d+3)···(d+l−3) ]
Q_4(0) = 3/(255·257) = 1/21845            Q_6(0) = −15/(255·257·259) = −1/1131571
```

this gives, in exact rationals,

```
A_4,haar(126) = 65/2072448      = 3.136387499227966e-05        = (260/257)/32256
A_6,haar(126) = 16637/536764032 = 3.099499781684329e-05
```

**The 16-digit reproduction of `A_4,haar(126)` is a second independent signal** on the
committed value `3.136387499227966e-5` of `PHASE2_CONTRIBUTION_DRAFT_20260819.md:1215-1260`
**[O vs O]**: that section derives it from `[1 + 255·Q_4(0)]/(256k)`; the derivation here
comes from the frame-pair variance count and lands on the same rational. The exact
`128/3` Haar-to-MUB ratio also reproduces (`42.66666666666666` vs `128/3`) **[D]**.

Two consequences that matter for this lane:

1. **`A_l` scales exactly as `1/n` with `n = 32,256` base directions** — the number of
   antipodal *pairs*, not the 64,512 rows. Odd degrees vanish identically under
   antipodal closure; degree 2 vanishes identically on every orthonormal frame because
   `Σ_i (e_i·u)² = |u|²` is constant in `u`. Degree 4 is the first live channel. So the
   estimator's second central moment lives on `n = 32,256` effective observations, and
   the leading correction to the pure `1/n` law is the exact rational `260/257`, a
   `+1.167%` inflation from the within-frame orthogonality term `255·Q_4(0)`.
2. **`Q_4(0) > 0`.** The within-frame pairs are *positively* coupled at degree 4. This
   is the exact fact that makes uniform weighting optimal in §3.a.2, and it is not an
   assumption — it is `1/21845`.

*(Aside, exact and unexplained: `A_6,haar(126)`'s reduced numerator `16637` is the same
integer as the dual-witness degree-4 spectral weight `y_4 = 16637/555357`
**[R, `PHASE2_CONTRIBUTION_DRAFT_20260819.md:754`]**. Both equal
`(d−2)(d+6)/4 = 127·131 = 16637` at `d = 256` **[D]**. Recorded as an exact coincidence
with no mechanism claimed.)*

### 1.4 What the deployed regime centring already removes — read from the deployed source

The deployed method-resolution order is
`estimator.Estimator → orthogonal_fold3.Estimator → fold3_estimator.Estimator →
base_estimator.Estimator` **[O, `estimator.py`, `orthogonal_fold3.py`; corroborated by
`SECTION_ESTIMATOR_AND_CONSTANTS_ROW_BLOCKED_20260819.md` [R]]**. Live values:
`n_base = 126 * 256 = 32,256`, `radial_conditioning = True`, `dead_alpha = −2.0`,
`on_alpha = 3.0`, `pilot_base = 256`, `fold_pilot_base = 1_024`,
`moment_tangent_lambda = 0.9807112198896164` **[O]**.

**(a) The radial degree of freedom: removed exactly, all moments.** `orthogonal_fold3.setup`
scales every frame row to the exact chi-mean radius:

```python
mean_radius = math.exp(0.5*math.log(2.0) + math.lgamma((ctx.width+1.0)/2.0)
                                         - math.lgamma(ctx.width/2.0))
self._gaussian = (q.reshape((self.n_base, ctx.width)) * mean_radius).astype(fnp.float32)
```

A bias-free ReLU network is positively 1-homogeneous, so `E[f(X)] = E‖X‖ · E[f(U)]`
exactly, and fixing `‖X‖ ≡ E‖X‖` leaves the estimand untouched while setting the radial
variance to **exactly zero** — every central moment of the radial factor, order 2 and
above, is annihilated. §3.a.4 prices what the alternative (the unreachable weighted
branch) would have achieved instead: a residual radial variance of `6.964e-5` against
the unweighted `0.49951`, a factor `7172.7` — good, and strictly worse than zero **[D]**.

**(b) The first-layer moment residuals: exactly centred, and the second one is exactly
the known-mean central moment.** `fold3_estimator.predict`:

```python
sigma0 = fnp.sqrt(fnp.sum(mlp.weights[0] * mlp.weights[0], axis=0))
exact_first_mean = sigma0 / fnp.sqrt(2.0 * fnp.pi)
first_moment_residual = fnp.mean(x, axis=0) - exact_first_mean
first_variance_residual = (
    fnp.mean(x * x, axis=0)
    - 0.5 * self._radial_covariance * sigma0 * sigma0
) - 2.0 * exact_first_mean * first_moment_residual
```

Write `μ = exact_first_mean` and `M₂ = E[x²] = r̄²σ₀²/(2d)` (the code's
`0.5 * _radial_covariance * sigma0²`, with `_radial_covariance = r̄²/d`). Then, as an
algebraic identity:

```
first_variance_residual = ( mean(x²) − M₂ ) − 2μ( mean(x) − μ )
                        = mean( (x − μ)² ) − E[ (x − μ)² ]
```

**verified exactly in `Fraction` arithmetic this session on a five-point example
(`6689/735` on both sides, equality `True`) [O]**. So the deployed second-order control
is **the known-mean central second moment of the first-layer activation**, differenced
against its exact analytic value. It is *not* the sample-mean-centred `m₂`. This single
fact is what closes candidate (i) of §3 at zero.

Both residuals have expectation exactly zero: each direction is marginally uniform, and
by 1-homogeneity `E[relu(r̄ u·w)] = ‖w‖/√(2π)` and `E[relu(r̄ u·w)²] = r̄²‖w‖²/(2d)`
exactly — precisely the two analytic constants the code subtracts **[D]**.

**(c) The tangent propagation is exactly linear in the empirical measure, hence the
control is exactly unbiased for every `λ` [D, exact — and this is a lawfulness
argument the disclosure does not currently make].** The loop is

```python
delta_pre_mean = delta_mean @ weight
delta_pre_var  = delta_var  @ (weight * weight)
next_delta_mean = firing[layer]*delta_pre_mean + (phi/(2.0*analytic_sigmas[layer]))*delta_pre_var
next_delta_var  = 2.0*layer_mean*delta_pre_mean + firing[layer]*delta_pre_var - 2.0*layer_mean*next_delta_mean
```

Every coefficient (`firing`, `phi`, `analytic_sigmas`, `layer_mean`) comes from
`_diagonal_gaussian_pass`, which reads only `mlp.weights`. The map from
`(Δμ, Δv)` to the final `delta_mean` is therefore **linear with sample-independent
coefficients**, and `(Δμ, Δv)` are themselves linear functionals of the empirical
measure. Hence `E[delta_mean] = 0` exactly, for every network and every `λ`.

**Consequence:** `moment_tangent_lambda` is a **pure variance knob with exactly zero
bias consequence**. It cannot leak target information into the estimate at any order,
because the control it scales has mean exactly zero conditional on the network. That is
a materially stronger lawfulness statement than "frozen before grading", and it belongs
in the disclosure.

**(d) The three terminal regimes — exactly which central moments each one deletes.**
`fold_estimator._initial_regimes` splits on the analytic `α`, and
`fold3_estimator.predict` treats the three blocks differently:

| block | rule | what enters the estimate | central moments of the projection distribution |
|---|---|---|---|
| **dead** (`α < −2.0`, pilot-confirmed) | `value_parts.append(analytic_means[layer32][dead32])` | a deterministic analytic scalar | **all orders deleted.** The sampling distribution is replaced by a point mass. What remains is the diagonal-Gaussian pass's own deterministic error — a squared-bias term, carrying no central moment at all. |
| **on** (`α > 3.0`, pilot-confirmed) | `mean_on = _weighted_mean(x) @ (folded29_to31_on @ …) + …` | the **sample mean** of the upstream activations, pushed through a folded *linear* operator | **orders ≥ 2 exactly irrelevant.** A linear map is first-moment-sufficient: `E[L(x)] = L(E[x])` exactly. The block still carries the first-moment sampling variance, but no curvature term. |
| **kink** (`−2.0 ≤ α ≤ 3.0`, plus demotions/rescues) | `sampled_kink = _weighted_mean(fnp.maximum(pre32(kink32, False), 0.0), …)` | a mean of `relu` applied to sampled pre-activations | **untouched at every order ≥ 2.** The ReLU is a kink, so the block's value depends on the whole projection distribution — its variance, its skew, its kurtosis, and its tail. |

**So the answer to the owner's question, stated precisely:** the regime centring deletes
the second and all higher central moments of the projection distribution *exactly* in
the dead and on blocks, and leaves them *entirely untouched* in the kink block. Every
higher-central-moment exposure the deployed estimator has is concentrated in the kink
block, and nothing in the deployed code measures, bounds, or predeclares any of it.

**(e) The nominal thresholds are not the operative thresholds — the pilot converts them
into extreme-value cuts [D, under the diagonal-Gaussian model the estimator itself
uses].** `_refine_dead` rescues on `max(pilot_pre) > 0`; `_refine_on` demotes on
`min(pilot_pre) ≤ 0`. These are **order statistics, not moments**. Under the model, a
unit at `α` survives `r` pilot rows with probability `(1 − Φ(−α))^r`:

| pilot | rows | `α` at 50% survival | `α` at 95% survival | survival of a nominal `on_alpha = 3.0` unit | probability a nominal `dead_alpha = −2.0` unit stays dead |
|---|---:|---:|---:|---:|---:|
| deep loop, `pilot_base = 256` | 512 | **2.9993** | 3.7186 | — (no on-refinement in the deep loop) | `7.636e-06` |
| terminal fold, `fold_pilot_base = 1_024` | 2048 | **3.3988** | 4.0552 | **0.0629** | `3.400e-21` |

Three readings **[D]**:

1. `dead_alpha = −2.0` is **inert in the fold**: a unit at exactly `−2.0` is rescued with
   probability `1 − 3.4e-21`. The operative dead cut is `|α| ≈ 3.40`, set by the pilot
   size, not by the declared constant.
2. `on_alpha = 3.0` is **93.7% inert in the fold**: only `6.3%` of units at exactly `3.0`
   survive as on-blocks. The operative on cut is also `≈ 3.40`.
3. The declared asymmetry between `−2.0` and `+3.0` is therefore **almost entirely erased
   by the pilots**, and the effective cut is symmetric at `|α| ≈ 3.40`. Two of the six
   scalars on the host's fitted surface are, at the deployed pilot sizes, nearly
   inoperative. That is a lawfulness observation with a cheap settling check (one
   offline recount of the realised block sizes at `α = ±2.0/±3.0` versus `±3.40`).

**Residual on-block truncation, exactly [D].** Replacing `relu(y)` by `y` on an on-block
costs `E[max(−y,0)] = σ[φ(α) − αΦ(−α)]`:

| `α` | absolute, in units of `σ` | relative to the mean `ασ` |
|---:|---:|---:|
| 3.000 (nominal) | `3.821543e-04` | `1.273848e-04` |
| 3.399 (pilot-effective 50%) | `8.699721e-05` | `2.559494e-05` |
| 4.000 | `7.145258e-06` | `1.786315e-06` |

This is the exact mass of second-and-higher-order ReLU curvature that the on-block
declines to carry — the one place where "delete the higher central moments" costs a
computable, one-sided bias, and it is `2.56e-05` per surviving on unit at the operative
threshold.

---

## 2. THE `μ_2k` INFERENCE LADDER

### 2.1 The exact finite-`n` law

For i.i.d. observations with central moments `μ₂ = σ²`, `μ₄`, and unbiased sample
variance `s² = k₂ = (1/(n−1)) Σ (x_i − x̄)²`:

```
Var(s²) = (1/n) [ μ₄ − ((n−3)/(n−1)) μ₂² ]                     (exact, all n ≥ 2)
        → (μ₄ − σ⁴)/n + O(1/n²)                                (the asymptotic form)
```

Writing `κ = μ₄/μ₂²` (non-excess kurtosis), the **relative** standard deviation of the
variance estimate is exact:

```
sd(s²)/σ² = sqrt( ( κ − (n−3)/(n−1) ) / n )
sd(ŝ )/σ  ≈ (1/2) sqrt( ( κ − (n−3)/(n−1) ) / n )              (delta method on the SD scale)
```

The **kurtosis-corrected standard error of a standard error** is that second line. It is
the formula the campaign needed three times and used zero times.

### 2.2 The general pattern

`Var(s²)` needs `μ₄`. The skewness of `s²` needs `μ₆`. In general, the sampling error of
the `k`-th central moment estimator is governed by moments **up to `μ_2k`**:

```
Var( m̂_k ) = (1/n)( μ_{2k} − μ_k² − 2k μ_{k−1} μ_{k+1} + k² μ_2 μ_{k−1}² ) + O(1/n²)
```

Every term of order `2k` is present at leading order. **Measuring at rung `k` prices at
rung `2k`.** There is no version of this that depends on the estimator, the domain, or
the sample scheme; it is an identity about central moments.

### 2.3 Failure 1 — the `se_log` blow-out is a rung-2 failure, and it did not need heavy tails

**The record [O, `PHASE2_CONTRIBUTION_DRAFT_20260819.md:1876-1890, 2278-2281`].**
Predeclared honour window on `se_log`: `[0.019, 0.03]`. Achieved on the gated channel:
`0.07054498655771349`. Overshoot `2.3515x` against the ceiling and `3.7129x` against the
spec's own `1/√n` projection. The projection's stated premise: "`0.0843` at five networks
implies about `0.019` at one hundred", recomputed at `0.018850053050323227`.

**Recomputed here [D]:**

```
implied between-network SD from the pilot:  ŝ₅      = 0.0843·√5  = 0.1885005305032323
realised between-network SD at production:  s_true  = 0.070545·√100 = 0.7054498655771348
ratio on the SD scale       s_true/ŝ₅ = 3.742429    (3.712894 against the rounded 0.019)
ratio on the VARIANCE scale             = 14.005775
relative shortfall of ŝ₅² :  1 − 1/14.005775       = 0.9286008825652166
```

**The killer number.** At `n₀ = 5`, `(n₀−3)/(n₀−1) = 1/2`, so under a *Gaussian*
per-network law (`κ = 3`):

```
sd(ŝ₅²)/σ² = sqrt( (3 − 1/2) / 5 ) = sqrt(1/2) = 0.7071067811865476   — exactly 1/√2
sd(ŝ₅ )/σ  ≈ 0.3535533905932738                                       — exactly ±35.4%
```

The observed shortfall of `0.9286` therefore sits at **1.3132 standard deviations**
**[D]**. The miss is *not* evidence of heavy tails. It is the arithmetic consequence of
calibrating a `1.58`-wide window (`0.03/0.019`) on a second moment estimated from five
observations, where the one-sigma band on that second moment is `±70.7%` on the variance
scale before any tail behaviour is invoked. **The `[0.019, 0.03]` window was
unearnable from a 5-network pilot for reasons available in closed form before the run.**

**The rung-4 answer the brief asks for [D].** The kurtosis at which the observed
shortfall is *exactly* a one-standard-deviation draw of the exact finite-`n` formula:

```
κ = (n₀−3)/(n₀−1) + n₀ · (1 − ŝ₅²/s_true²)²
  = 0.5 + 5 · (0.9286008825652166)²
  = 4.811497995504496                        (excess kurtosis 1.811497995504496)
```

So a modest excess kurtosis of `1.81` makes the miss typical rather than a
`1.31σ` draw. Either reading condemns the same thing: the instrument reported a rung-2
quantity and predeclared nothing at rung 4.

**What was actually predeclared, and what should have been [D].** The predeclaration
fixed a *point* projection `ŝ₅/√n` with no uncertainty on `ŝ₅`. The kurtosis-corrected
honour window at `n₀ = 5`, even under `κ = 3`, is

```
se_log(100) ∈ ŝ₅/10 · [ 1 ± 1.96·0.35355 ] = 0.018850 · [0.3070, 1.6930] = [0.005788, 0.031912]
```

— a window whose *upper* edge already grazes `0.03`, at `κ = 3`, before any tail. A
window that wide is not a power guarantee; it is a statement that the pilot could not
size the cell. The correct move was more pilot networks or an L-moment fallback, not a
tighter band.

### 2.4 Failure 2 — the left-skew of a log-ratio-of-means is a rung-3 statistic priced at rung 4

**Cited, not duplicated:** the sibling lane's Lens A reports left-skew on the
log-ratio-of-means; the judge's channel independently records a symmetric bootstrap SE
bias of `6.2%` **[R, `PHASE2_CONTRIBUTION_DRAFT_20260819.md:1890`]**. This lane supplies
the *law*, not another measurement of it.

**The derivation [D].** Let `X = μ(1 + ε)` with `E[ε] = 0`, `E[ε²] = c²` (so `c` is the
CV), `E[ε³] = γc³`, `E[ε⁴] = κc⁴`. Expand `log X = log μ + ε − ε²/2 + ε³/3 − …`. Then

```
Var(log X)      = c² − γc³ + O(c⁴)
μ₃(log X)       = γc³ − (3/2)(κ − 1)c⁴ + O(c⁵)
skew(log X)     = γ − (3/2)(κ − 1 − γ²)·c + O(c²)
```

**For a symmetric mean (`γ = 0`) with Gaussian kurtosis (`κ = 3`): `skew(log X) ≈ −3c`.**
The log of a positive statistic is left-skewed at order CV *even when the statistic
itself is exactly symmetric*, because `log` is concave. Left-skew is not evidence of a
skewed underlying quantity; it is the transform.

**Consistency check on a case where the answer is known exactly [D].** For `X`
lognormal, `skew(log X) = 0` identically. Substituting the lognormal's own moments,
`c ≈ s`, `γ ≈ 3s`, `κ ≈ 3 + 16s²`, the formula returns
`3s − (3/2)(2 + 16s² − 9s²)s = −(21/2)s³`, i.e. zero to leading order — the formula
reproduces the known exact answer. Two independent routes agree. *(The `−γ²` in the
coefficient comes from the `Var^{3/2}` normalisation and was restored by the
hostile-verification pass 2026-08-19: on an exact three-point law the empirical `O(c)`
coefficient converges to `−(3/2)(κ−1−γ²) = −1.5199`, excluding the un-corrected
`−(3/2)(κ−1) = −1.5556`; a two-point law, where `κ − 1 = γ²` identically and any
monotone transform preserves skew exactly, confirms the corrected form with zero on
both sides.)*

**The ladder reading.** The *third* central moment of the reported statistic
(`skew(log r̂)`) is governed by the *fourth* central moment of the data (`κ`, through
`κ − 1 − γ²`) times the CV.
A cell that reports a log-ratio and characterises its asymmetry has silently taken a
position on `μ₄`. Rung 3 priced at rung 4 — again.

**For the ratio specifically.** `log r̂ = log Ā − log B̄`. The `B` leg enters with a minus
sign, so its `−(3/2)(κ_B − 1)c_B` term contributes *positive* skew. The net skew of the
log-ratio-of-means is `≈ −(3/2)[ (κ_A−1)c_A − (κ_B−1)c_B ]` for symmetric legs: left-skewed
exactly when the numerator arm's CV·(κ−1) exceeds the denominator arm's. With paired
resampling over shared networks the two legs are strongly positively coupled, which
shrinks the magnitude without changing the sign rule. That is the falsifiable prediction
this lane hands the sibling lane: **the sign of Lens A's skew is set by which arm carries
the larger `(κ−1)·CV`, and by nothing else at leading order.**

### 2.5 Failure 3 — the deg-6 cell's `κ ≈ 2e4` sits on rung 4 while the instrument reads rung 2

**The record [O, `cells/deg6_own_axis_zonal_capture_v1/predeclaration.json`]:** the judge's
smoke at the shipped-smoke sizes read the instruments "noise-dominated (ratio 0.758,
feature norm 0.734) — consistent with the documented heavy-tail (**kurtosis of order
2e4**) at toy sample counts, resolving at production scale." Disclosed sizes: designer
quarter-scale pilot `8192`, halves `32768`, gradients `4096`.

**Which rung.** The instrument that reads noise-dominated is *mean squared zonal
feature* (`1.018` vs `1.0` at designer scale, `0.734` at judge smoke) — a **second**
moment. The documented `κ ≈ 2e4` is a **fourth** moment. Rung 2 measured, rung 4
governing. Identical structure to §2.3.

**What it predicts, exactly [D, at `κ = 2e4` and the disclosed counts]:**

```
rel-sd of the second-moment readout = sqrt( (κ − 1) / n )

n =     4,096  →  221.0%          n required for  50% rel-sd  =      79,996
n =     8,192  →  156.2%          n required for  20% rel-sd  =     499,975
n =    32,768  →   78.1%          n required for  10% rel-sd  =   1,999,900
n =   131,072  →   39.1%          n required for   5% rel-sd  =   7,999,600
```

**The prediction for that cell's production noise, stated plainly [D]:** at `κ ≈ 2e4`,
a four-fold scale-up of the quarter-scale halves (`32,768 → 131,072`) lands the
second-moment instrument at **`39%` relative standard deviation**, not at a resolved
reading. "Resolving at production scale" requires `n ≳ 2.0e6` for a 10% instrument —
roughly **15x** beyond a four-fold scale-up of the disclosed halves. The predeclaration's
own kurtosis figure is what refutes its own resolution premise.

**[GAP]** I did not read the deg-6 cell's production sample counts — only the
quarter-scale figures the predeclaration discloses. **Settling check:** one read of
`cells/deg6_own_axis_zonal_capture_v1/spec.json` for the production `halves`/`pilot`
counts, substituted into the table above. Zero cost, zero compute.

### 2.6 THE LADDER LAW, and its prescription

> **THE RUNG-2k LAW.** An estimator of a `k`-th central moment has sampling error
> governed by central moments up to `μ_2k`. Every campaign instrument that reported at
> rung `k` while predeclaring nothing at rung `2k` failed in the same way, and the
> failures are ordered by `k`: the `se_log` window (rung 2, priced at rung 4, missed by
> `3.71x`), the log-ratio skew (rung 3, priced at rung 4, wrong sign attribution
> available), the deg-6 zonal instrument (rung 2, priced at rung 4 = `2e4`, declared
> resolved at `39%` noise).

**PRESCRIPTION — binding on every future cell.** Any cell whose gated or reported metric
is a `k`-th-moment quantity must, in its predeclaration, do **one** of:

1. **Predeclare a `2k`-th-moment estimate** with its source, and derive the honour window
   from the exact finite-`n` formula of §2.1 rather than from a point `1/√n` projection.
   The window must be an interval on `se`, computed at the declared `κ`, not a target.
2. **Declare an L-moment or robust fallback** as the gated statistic. L-moments have
   sampling variance governed by the *second* moment of the order statistics regardless
   of `k`, so an L-scale or L-skew gate escapes the ladder entirely. This is the correct
   default when `κ` is unknown.
3. **Declare the instrument descriptive-only** and forfeit the gate.

A cell that does none of the three is INSTRUMENT-SUSPECT on filing, before it runs. Had
this rule been in force, the `frame_completion_129` honour rule would have been written
against a `[0.0058, 0.0319]` window at `κ = 3` (§2.3) and the PASS would have been
honoured or the cell resized — either outcome strictly better than the one on file.

**Corollary — the one exposure the ladder does not cover.** The regime classifiers of
§1.4(e) are `max`/`min` over pilot rows: **order statistics, not moments**. No moment
predeclaration at any rung bounds their error, because their failure probability is a
tail exceedance, not a moment. The correct instrument there is an exceedance bound at
the declared `α`, and §1.4(e) supplies it in closed form. Any future cell touching
`dead_alpha`, `on_alpha`, `pilot_base` or `fold_pilot_base` must predeclare against that
table and not against a variance.

---

## 3. FISHER `k`-STATISTICS AS LAWFUL MACHINERY — the constructive question

### 3.0 Why they are lawful at all

`h`-statistics (unbiased central-moment estimators) and `k`-statistics (unbiased cumulant
estimators) carry exact rational coefficients generated by the Möbius/partition
combinatorics of the moment-cumulant correspondence:

```
k₂ = n/(n−1) · m₂ ,     k₃ = n²/((n−1)(n−2)) · m₃ ,
k₄ = n²[ (n+1)m₄ − 3(n−1)m₂² ] / ((n−1)(n−2)(n−3)) ,   …
```

No datum touches a coefficient; they are determined by `n` and the partition lattice
alone. Under the k32 death law's own criterion — theorem-fixed closed forms and
combinatorial identities are lawful, fitted or trained coefficients are not — this
machinery is **lawful**. The question is therefore not whether it may be used but
whether, at this problem's `n` and distribution shape, it does anything.

### 3.a Is the deployed variance-side arithmetic already optimal?

#### 3.a.1 Candidate (i): the exact finite-`n` unbiasing — **identically zero**

The `n/(n−1)` factor corrects `m₂ = (1/n)Σ(x_i − x̄)²`, whose bias is `−σ²/n` because the
sample mean is estimated. The deployed code does not form `m₂`. §1.4(b) established, in
exact rational arithmetic, that `first_variance_residual` equals

```
(1/n) Σ (x_i − μ)²  −  E[(x − μ)²] ,        μ = the exact analytic mean
```

with `μ` **known**, not estimated. A known-mean central second moment is unbiased at
every `n` — its bias is exactly `0`, not `O(1/n)`. The k-statistic correction therefore
has magnitude **identically zero**, costs **0 FLOPs**, and buys **0 MSE**.

Closed with a number: **0**.

#### 3.a.2 Candidate (ii): `μ₄`-aware weighting of direction contributions — **identically uniform**

The deployed final average is `fnp.mean` over all `2 × 32,256 = 64,512` rows with equal
weight (`radial_conditioning = True ⇒ final_weights = None ⇒ plain mean`) **[O]**.

**Theorem [D, exact].** Let `Y_1 … Y_N` be the per-direction contributions. Within one
frame the 256 directions are exchangeable (the frame law is invariant under permuting
its rows) with common variance `v` and common pairwise covariance `c`; the 126 frames are
i.i.d. For weights with `Σw_i = 1`,

```
Var( Σ w_i Y_i ) = c + (v − c) Σ w_i²          (within a frame)
```

which is minimised at `w_i = 1/N` whenever `v > c`. At degree `l` the exact covariance
ratio is `c/v = Q_l(0)`, and `Q_4(0) = 1/21845 = 4.578e-05 ≪ 1` **[D, §1.3]**. So `v > c`
by an exactly known margin at every live degree, and **uniform weighting is exactly
optimal**.

More sharply: any admissible weight must be measurable with respect to the direction's
observable covariates. The only rotation-invariant covariate is the radius, and the
radius is **fixed to `r̄` exactly** by `radial_conditioning`. The `μ₄`-aware reweighting
therefore has **zero free dimensions** on this carrier — there is no non-uniform,
rotation-equivariant weight to construct.

Closed with a number: **0**.

#### 3.a.3 Candidate (iii): more control channels, or per-channel coefficients — **unlawful, or identical**

The deployed control subtracts `λ · delta_mean`, where `delta_mean` is the image of
`(Δμ, Δv)` under the exact first-order tangent of the analytic Gaussian map (§1.4(c)).
Two extensions are conceivable:

- **Split `λ` into `(λ₁, λ₂)`**, one per input channel, propagating two tangents. Priced
  exactly: two extra `1×256 by 256×256` mat-vecs per layer over 31 layers,
  `2 · 256 · (2·256 − 1) · 31 = 8,110,592` FLOPs. Against the incumbent
  `C = 222.405e9` **[R, `PHASE2_CONTRIBUTION_DRAFT_20260819.md:1002`]** and `B = 2.72e11`,
  `C/B = 0.81767` sits **above** the `0.1` clamp of `S = MSE × max(0.1, C/B)`
  **[R, `CODEX_HANDOFF_20260810.md:219`]**, so compute prices linearly:
  `ΔC/C = 3.6468e-5`, a score penalty factor of `1.0000365`.
- **Add a third central-moment control** `Δ₃ = mean((x−μ)³) − μ₃`. Priced exactly:
  `2 · 64,512 · 256 = 33,030,144` FLOPs to accumulate the cube plus
  `8,118,528` to form and apply the cubed-weight propagation, total `41,148,672`,
  `ΔC/C = 1.8502e-4`.

**Both are dead on lawfulness before the price matters [D].** The *only* theorem in play
is that `delta_mean` is the exact first-order tangent image; the coefficient that theorem
fixes is `1`, on every channel. Any `(λ₁, λ₂) ≠ (1,1)` — and any per-channel weighting of
a third moment — is a variance-minimising choice that must be estimated from data, i.e.
**fitted**, i.e. unlawful under the death law. And `(λ₁, λ₂) = (1,1)` is arithmetically
identical to the single-`λ` structure at `λ = 1`. There is no lawful point in the
extended space that is not already the deployed structure.

**A second, independent reason the extra moment buys nothing at leading order [D].**
All of `g₁(u) = relu(r̄ u·w_j)`, `g₂ = (g₁ − μ)²`, `g₃ = (g₁ − μ)³` are functions of
`t = u·w_j` alone — they are **zonal about the same axis**. Their degree-`l` harmonic
projections are therefore all scalar multiples of the *same* zonal harmonic `Z_l(u·w_j)`.
At every degree, the moment ladder `Δμ, Δv, Δ₃, …` spans a **one-dimensional** subspace
per neuron. The `k`-statistic ladder is exactly rank-deficient on this geometry.

Closed with a number: **`3.6468e-5` of `C` for the split (and `1.85e-4` for the third
moment), both spent on coefficients that are unlawful unless set to the value that makes
them redundant.**

#### 3.a.4 The radial weights are theorem-fixed — an exact result the disclosure does not hold

`SECTION_ESTIMATOR_AND_CONSTANTS_ROW_BLOCKED_20260819.md` lists the radial-reweight branch
as "present in the source, unreachable on this host", identifies `257.0` and
`66563.0 = 257 × 259` as "the exact second and fourth moments of a chi-square at 257
degrees of freedom", and explicitly declines to classify the branch's lawfulness **[R]**.
The classification is available in closed form, and the attribution is off by one step.

**The correct reading [D, exact].** At `d = 256`, with `S = ‖z‖² ∼ χ²_d` and
`E[R^{k+2}]/E[R^k] = d + k`:

```
E[R³]/E[R] = d + 1        = 257
E[R⁵]/E[R] = (d+1)(d+3)   = 66563
```

So `q₁ = S − 257` and `q₂ = S² − 66563` are **exactly orthogonal to `R`**, not to `1`:
`E[q₁ R] = E[q₂ R] = 0` identically **[O, verified: both differences evaluate to `0`]**.
They are the first two orthogonal polynomials with respect to the **size-biased**
(`R`-tilted) chi law at `d = 256` — which is precisely the tilting that makes a
*multiplicative* weight `w(S) = 1 + a q₁ + b q₂` unbiased for **every one-homogeneous
integrand and every `(a, b)`**. A bias-free ReLU network is one-homogeneous, so this is
exactly the right orthogonality to impose.

With unbiasedness automatic, `(a, b)` are free to minimise the variance
`Var(w(S)·R) = E[w² S] − E[R]²`. The normal equations have integer coefficients (all
`χ²` raw moments are integers), so the minimiser is **rational**. Solved exactly in
`Fraction` arithmetic this session:

```
a = −2600/537689          b = 3/537689          ← MATCH: True
```

**These are exactly the deployed literals `2600.0/537689.0` and `3.0/537689.0`** **[O]**.
The branch's four constants are therefore **theorem-fixed — lawful under the death law by
its own criterion — and not a fitted surface**. What the optimum achieves, exactly:

```
E[w² S]/E[S]  = 536640/537689 = 0.9980490580986406
Var(w·R)      = 0.0000696406768702994…      against  Var(R) = 0.4995107674248603…
radial variance reduction factor = 7172.687
```

against the deployed `radial_conditioning = True`, which sets the radial variance to
**exactly 0**. The deployed switch strictly dominates its own alternative branch by a
factor `∞`, and the alternative was already the exact optimum of its span. Nothing to
construct on the radial axis; the design is closed at both ends **[D]**.

*(Attack landed and recorded: my first hypothesis was that the weights satisfy the
unbiasedness constraint `a + (2d+3)b = 0` for a one-homogeneous integrand — which gives
`a/b = −517` at `d = 257` against the deployed `−866.67`, a clean falsification. The
hypothesis was wrong because the centring constants are `R`-tilted at `d = 256`, not raw
`χ²` moments at `d = 257`. The attack changed the answer, which is the attack paying for
itself.)*

#### 3.a.5 The one live construction: `λ → 1`

Because the control is exactly unbiased for every `λ` (§1.4(c)),

```
Var(M̂ − λΔ) = Var(M̂)(1 − ρ²) + Var(Δ)·(λ − λ*)² ,        λ* = Cov(M̂,Δ)/Var(Δ)
```

Substituting the theorem-fixed `λ = 1` in place of the fitted
`0.9807112198896164`, and taking `λ_deployed = λ*` **[A — the labelled assumption; the
settling check is one offline `λ`-sweep of the stored tangent and sampled arms, no
forwards]**:

```
extra variance / variance the control removes = (1 − λ)²/λ² = 3.8683631417925867e-04
(1 − λ)²                                                    = 3.7205703814672980e-04
FLOP change: −256  (the width-256 multiply disappears);  ΔC/C = −1.151e-09
```

**Stated as a deliverable:** the substitution removes the deployed `row_blocked` host's
**only fitted scalar in the correction path**, reduces the fitted surface from six
scalars to five, saves `256` FLOPs, and costs `3.868e-4` of whatever MSE the tangent
control removes. If the control removes half the MSE, the cost is `3.9e-4` relative on the
final number; if it removes 90%, `3.5e-3`. Both are below every gate margin on file.

**[GAP]** The tangent control's realised MSE share is not measured in any artifact I read.
**Settling check:** one ablation run with `moment_tangent_lambda = 0.0` against the
deployed value on the stored panel — the ratio is the share, and it converts the bound
above into a number.

**No closed form found for `0.9807112198896164` [O].** Scanned against
`E[R]²/d = 0.9980488`, `(d−1)/d`, `√(E[R]²/d)`, `126/128.478`, `1 − 1/51.845`,
`1 − 2/103.7`; nearest miss `1.43e-6`, which is not a match at 16 digits. It stays
classified fitted, exactly as the committed disclosure has it **[R]**.

### 3.b Cross-cumulant inference between degree channels — the exact answer is "not at order 2"

**The question.** Cumulants add over independent channels, but degree channels share
frame vectors. Does the leading cross-cumulant between two degree channels have the sign
and magnitude to be the excess-gain mechanism?

**Theorem (exact diagonality at order 2) [D].** Let the carrier configuration
`U = {u_1 … u_N}` have a joint law invariant under the diagonal action of `O(d)`, and let
the estimator be linear in the empirical measure, so that
`ε = Σ_{l≥1} ε_l` with `ε_l = (1/N) Σ_i D_l(u_i)`. Then for `l ≠ m`:

```
E[ε_l ε_m] = (1/N²) Σ_{i,j} E[ D_l(u_i) D_m(u_j) ] = 0        exactly
```

*Proof.* For `i = j` the marginal is uniform and the harmonics are orthogonal. For
`i ≠ j`, the bilinear form `B(g,h) = E[g(u_i) h(u_j)]` is `O(d)`-invariant by hypothesis;
`H_l` and `H_m` are inequivalent irreducible `O(d)`-representations for `l ≠ m`; an
invariant bilinear form on `H_l × H_m` vanishes by Schur's lemma. ∎

**Three consequences.**

1. **`MSE = Σ_l a_l A_l` is exact, with no cross-degree term.** The degree decomposition
   of §1.3 is not an approximation and not an independence assumption — it is forced.
2. **Killing `A_4` removes exactly `a_4 A_4` and not one unit more.** The
   `129`-completion's degree-4 annihilation (`A_4,mub(129) = 0` identically
   **[R, §11]**) therefore cannot, by any second-order mechanism, produce more MSE
   reduction than the degree-4 share. **The excess gain is not a cross-degree
   covariance.** Recorded as a negative result with a proof, not a measurement.
3. **The deployed control does not break this**, because §1.4(c) established the tangent
   is exactly *linear* in the empirical measure. The only nonlinearity in the deployed
   estimator is the regime partition (`_refine_dead`/`_refine_on`), which is where any
   second-order cross-degree leakage must live if it lives anywhere.

**Where cross-degree structure does first appear, and how big it is [D].** The joint
cumulant `κ₄(ε_l, ε_l, ε_m, ε_m)` need not vanish, because `H_l ⊗ H_l ⊗ H_m ⊗ H_m`
contains the trivial representation. So the first live cross-degree object is **order
four**, and it moves the **variance of the per-draw MSE**, not its mean. Its magnitude is
suppressed by the frame count: for a mean of `k` i.i.d. frame contributions,
`κ₄(mean) = κ₄(single)/k³`, so

```
suppression at k = 126 :  1/126³ = 4.999e-07
excess kurtosis of the frame-mean falls as 1/k = 7.937e-03
```

**Sign of the leading within-frame term [O — corrected by the hostile-verification pass
2026-08-19, exact rational computation].** The cross-row pair channel does enter through
`Q_4(0)·Q_6(0) = (1/21845)·(−1/1131571) = −4.045e-11 < 0`, but it is **not the leading
term**: the coincident-row term — `Cov(D₄(u)², D₆(u)²)` on a single direction, which no
`Q_l(0)` factor suppresses — dominates it. Computed exactly in the canonical zonal
single-neuron case (`d = m = 256`; `S_l = Σ_i Q_l(t_i)` with `(t_i)` one frame's
projections, i.e. the first `m` coordinates of a uniform vector; all `Fraction`):

```
Cov(S₄², S₆²) = 51989825798144/6048658608830842617174904419 = +8.595e-15   POSITIVE
   coincident-row block : +8.611e-15        (44)(66) row-split : −1.426e-16
   (46)(46) row-splits  : −7.272e-17        remaining partitions: +1.991e-16
```

The pair terms carry exactly the predicted negative sign and are two orders of
magnitude smaller than the coincident term. **The leading order-4 cross-degree sign is
positive**, set by the single-row association of the squared degree components, not by
`Q_4(0)·Q_6(0)`. (The same exact machinery reproduces `E[S₄S₆] = 0` — the §3.b
diagonality in miniature — and the `A_l` frame-variance formula of §1.3, which is the
second signal that the computation is sound.)

**Verdict on 3.b, with numbers.** The degree-4/degree-6 cross-cumulant has (a) exactly
zero weight at the order that sets mean MSE, and (b) a `4.999e-07` suppression at the
order where it is live — an order at which it moves the *variance* of the per-draw MSE,
not its mean. It has **neither the order nor the magnitude** to be the excess-gain
mechanism. *(A sign leg originally claimed here — negative, via `Q_4(0)·Q_6(0)` — was
corrected by the verification pass: the leading order-4 sign is positive, per the exact
computation above. The verdict never rested on it; the two load-bearing legs are order
and magnitude.)*

**The inferential bridge handed to the sibling lane [D].** Since
`MSE = Σ_l a_l A_l` is exact and the completion sets `A_4` to zero while moving `A_6` by
only `A_6,mub(129)/A_6,haar(126) = (126/129)·(4224/4096) = 693/688 = +0.727%` — exact
from the §11b dyadic tax `X_6/S_6 = +1/4096`
**[R, `PHASE2_CONTRIBUTION_DRAFT_20260819.md:1433-1461`]**, and in the *anti*-excess
direction — the observed
excess — raw MSE ratio `0.6661955563966138` against the amended band's lower edge `0.78`
(a `1.1708x` excess) and against the slate's point prediction `0.842` (a `1.2639x`
excess) **[R, `PHASE2_CONTRIBUTION_DRAFT_20260819.md:1854-1868`; `ULTRAMATH_SLATE_20260819.md`]** —
must come from exactly one of three places, and cross-degree coupling is not among them:

1. **the energy profile `a_l`** differing from R0's frozen spectrum — for which the corpus
   already records the specific symptom, "R0's energy profile under-predicts measured
   `s17` absolute MSE by 2.1–3.7x" **[R, `:797`]**;
2. **the estimator's regime partition**, the only nonlinearity in the deployed path
   (§1.4(d)–(e)), whose thresholds §1.4(e) shows are pilot-set rather than
   constant-set;
3. **the between-network mixture** — §3.c, which is where the same `3.71x` that broke the
   instrument also inflates the reported aggregate.

Ranking those three is the sibling lane's descriptive question. This lane's contribution
is that the list has exactly three entries and that a fourth candidate is provably empty.

### 3.c The conditioning lottery as a mixture — the law-of-total-variance statement

**The frame.** Let `K` be the latent per-network conditioning variable (the campaign's own
"lottery draw": `m207`'s intermittent stochastic near-singularity, whose per-network
guard-fire probability and condition-number quantiles are recorded
**[R, `PHASE2_CONTRIBUTION_DRAFT_20260819.md:645-720`]**). The ensemble MSE is a mixture,
and the law of total variance splits it exactly:

```
MSE_ens = E_K[ v(K) ] + Var_K( m(K) ) + ( E_K m(K) )²
                ↑                ↑
        within-component    BETWEEN-COMPONENT  ← the ensemble excess, exactly
```

with `m(K) = E[e | K]`, `v(K) = Var(e | K)`. **The ensemble excess over the typical
network is exactly the between-component variance term `Var_K(m(K))`**, and tail deletion
is the operation that removes the components of `K` whose `m(K)` and `v(K)` dominate that
term. That is the cleanest central-moment statement of the tail-deletion story: trimming
is not a robustness heuristic, it is the deletion of identified mixture components from a
between-component variance.

**Quantified on the campaign's own recorded lottery [D, under a labelled lognormal fit].**
The recorded `log₁₀ κ` quantiles are `q50 = 10.8`, `q90 = 12.3`, `q99 = 15.0`
**[R, `:695`]**. Fitting a lognormal to `(q50, q90)`:

```
σ(log₁₀) = (12.3 − 10.8)/1.2815516 = 1.1704562
implied q99 = 10.8 + 1.1704562·2.3263479 = 13.5228883      observed q99 = 15.0
```

**The observed `q99` exceeds the two-quantile lognormal fit by `1.4771` decades — a factor
of `30.0`.** The mixture is decisively heavier-tailed than lognormal, which is a
sufficient explanation on its own for why moment-based instruments (§2) fail on this
ensemble. Under the fit (a *lower* bound on the true tail, since the fit is refuted on the
strong side at `q99`):

```
E[X] / median(X) = exp(σ² ln²10 / 2) = 37.78
Var(X) / E[X]²   = exp(σ² ln²10) − 1 = 1426.1
```

i.e. the ensemble mean of a `κ`-proportional quantity is a **tail statistic**: it is set by
the top `1/1426` of the mass. Deleting that tail does not perturb the mean; it replaces it.

**Quantified on the deployed lane's own observed dispersion [D, from an observed
`se_log`].** The realised between-network SD of the log score-ratio is
`s_true = 0.7054498655771348` (§2.3). Then:

```
one-SD spread of the per-network ratio  = e^0.70545      = 2.0248 x
arithmetic-mean-over-median inflation   = e^{s²/2}       = 1.28252
```

**So `28.25%` of the reported aggregate ratio is between-component variance rather than
typical behaviour** — under a lognormal per-network ratio with the observed dispersion
**[A: lognormality of the per-network ratio; settling check is one L-skew of the stored
per-network ratios, offline, zero compute]**. This is the same object, measured in the
same run, that produced the `3.71x` instrument miss of §2.3: **one heavy between-component
term explains both the instrument failure and a `28%` slice of the headline number**, and
the law of total variance is the identity that ties them together.

**The prescription that follows.** Any ensemble-aggregated result on this campaign should
report the split — `E_K[v(K)]` and `Var_K(m(K))` separately — because a result whose
between-component share is `28%` is a statement about the tail of the network population,
not about the estimator. Reporting only the aggregate hides which of the two moved.

---

## 4. VERDICT LINE

```
lawful_construction_verdict = CLOSED-BY-DERIVATION
```

**The numbers that close it:**

| object | closing number |
|---|---:|
| finite-`n` unbiasing of the squared-deviation mean | `0` (exactly unbiased already; mean is known, not estimated) |
| `μ₄`-aware direction weighting | `0` (uniform is exactly optimal; `c/v = Q_4(0) = 1/21845 < 1`) |
| per-channel `λ` split | `ΔC/C = 3.6468e-5`, and unlawful unless set to `(1,1)`, which is the deployed structure |
| third central-moment control | `ΔC/C = 1.8502e-4`, and rank-deficient: all first-layer moment controls are zonal about the same axis |
| radial reweight branch | already the exact rational optimum of its span (`a = −2600/537689`, `b = 3/537689` reproduced exactly); strictly dominated by the deployed `radial_conditioning = True`, which achieves radial variance exactly `0` |
| cross-degree covariance as the excess-gain mechanism | `0` at order 2 (Schur); `4.999e-07` suppression at order 4; leading order-4 sign **positive** (coincident-row term dominates; the negative `Q_4(0)·Q_6(0)` pair channel is ~50x smaller — corrected by the verification pass) |

**The one construction that remains, carried as a lawfulness move rather than a gain:**
`moment_tangent_lambda → 1`. Exact cost `(1−λ)²/λ² = 3.8683631417925867e-4` of the MSE the
tangent control removes; exact FLOP change `−256`; effect on the fitted surface: six
declared scalars become five, and the correction path becomes fitting-free.

**The instrument doctrine stands independently of the verdict:** the **rung-2k law** and
its three-way predeclaration prescription (§2.6), plus the order-statistic corollary for
the regime classifiers.

---

## 5. ATTACK LOG — what I tried to break, and what broke

1. **"The radial constants are `χ²_257` moments."** The committed disclosure says so
   **[R]**. Attacked by testing the one-homogeneous unbiasedness condition
   `a + (2d+3)b = 0`, which fails at `d ∈ {256, 257, 258}` (`a/b` would be `−515/−517/−519`
   against the deployed `−866.67`). **The attack landed and changed the answer**: the
   constants are `R`-tilted orthogonality centres at `d = 256`
   (`E[R³]/E[R] = 257`, `E[R⁵]/E[R] = 66563`), which is why the multiplicative weight is
   unbiased for *every* `(a,b)`. That correction is what made §3.a.4's exact match possible.
2. **"The excess gain is a degree cross-term."** Attacked with Schur's lemma rather than by
   re-confirming it. **The attack killed the hypothesis outright** at order 2 and bounded
   it at `4.999e-07` at order 4.
3. **"The `se_log` miss proves heavy tails."** Attacked by computing the Gaussian-case
   sampling error of a 5-network variance estimate. **The attack changed the conclusion**:
   the exact figure is `1/√2` on the variance scale, so the miss is a `1.31σ` event *under
   normality*. The window was unearnable for rung-2 reasons before rung 4 is invoked. The
   kurtosis answer (`4.811`) is reported alongside, not instead.
4. **"`dead_alpha` and `on_alpha` are the operative thresholds."** Attacked by computing the
   pilot survival probabilities. **The attack landed**: at 2048 fold-pilot rows a nominal
   `on_alpha = 3.0` unit survives with probability `0.0629` and a nominal
   `dead_alpha = −2.0` unit stays dead with probability `3.4e-21`. The operative cut is
   `|α| ≈ 3.40` and is symmetric.
5. **`moment_tangent_lambda` closed-form hunt.** Seven candidate closed forms scanned;
   nearest miss `1.43e-6`. **The attack failed to land** — the constant stays fitted, and the
   §3.a.5 substitution is offered as the lawful alternative rather than a rediscovery.
6. **What I did not look at.** I did not read the sibling lane's Lens A output, the deg-6
   cell's production sample counts, any `full.json`, or any bootstrap resample file. Every
   claim that would have needed them is tagged `[GAP]` with its settling check.

---

## 6. LEDGER — assumptions, gaps, and their settling checks

| item | level | settling check |
|---|---|---|
| Exact `O(d)`-invariance of the LAPACK-QR carrier configuration (needed for the Schur diagonality of §3.b) | `[A]` | The disclosure itself flags that the Householder sign convention leaves `Q = H·D` **[R]**. The operational second signal is that `A_4,haar(126) = 65/2072448` reproduces the committed value to 16 digits under exact rotation invariance. Direct check: one exact-arithmetic census of `E[Q_l(u_i·u_j)]` on the deployed `setup` at small width. |
| `λ_deployed = λ*` in the §3.a.5 price | `[A]` | One offline `λ`-sweep over the stored tangent and sampled arms; no forwards. |
| The tangent control's realised MSE share | `[GAP]` | One ablation at `moment_tangent_lambda = 0.0` against the deployed value on the stored panel. |
| Deg-6 cell production sample counts | `[GAP]` | Read `cells/deg6_own_axis_zonal_capture_v1/spec.json`; substitute into the §2.5 table. |
| Lognormality of the per-network score ratio in §3.c | `[A]` | One L-skew of the stored per-network ratios, offline. |
| The `κ ≈ 2e4` figure itself | `[R]` | Reported in `cells/deg6_own_axis_zonal_capture_v1/predeclaration.json`; not re-measured here. |
| Pilot rows treated as independent in §1.4(e) | `[A]` | The two antipodal halves are perfectly anti-correlated at layer 1 and decorrelate with depth, so the effective count lies between `pilot_n` and `2·pilot_n`; the `α₅₀` figures shift by at most `Φ⁻¹` of a factor two, i.e. `≈ 0.09`. Direct check: one offline recount of realised block sizes. |
| `16637 = (d−2)(d+6)/4` appearing in both `A_6,haar(126)` and `y_4` | `[O]` | Exact integer identity; no mechanism claimed. |

**Everything else above is `[O]` or `[D]`, and every `[D]` shows its steps.**

---

## MARKED CORRECTIONS — orchestrator self-audit of 2026-08-19 (append-only; original text above is unedited)

Authority: `corpus/whestbench/audit_self/CONFABULATION_AUDIT_20260819.md` (families F6,
F7) and `audit_self/self_graph.json`. Stamp: 2026-08-20T01:04:31Z.

1. **L22–24 — the quotation labelled "Owner's direction, verbatim" is not verbatim.**
   The owner's actual message (session transcript, 2026-08-19T16:05:36.795Z) reads in
   full: *"What about moments about the mean because we are looking at the Kurtosis
   what about the other elements and the inference between them"*. The middle clause
   quoted at L23 — "the central moments, the deviations of the observations from their
   mean" — was authored by the orchestrator itself while writing the dispatch prompt
   (transcript 16:09:04.709Z; the phrase occurs nowhere else in the session) and is
   not the owner's words. Grade: CONFABULATED (PC-01). The mathematical content of
   this document is unaffected; the attribution is corrected here.

2. **L408, L451, L938 — "Lens A" is not a corpus source.** "Lens A" is an ephemeral
   positional lane label local to workflow `wf_b708199c-ca4` (2026-08-19 00:42),
   coined by the orchestrator in its own dispatch; it names no ledger record and no
   committed artifact. Grade: CONFABULATED as a citation (PC-03). The left-skew
   finding itself is real and is independently derived in §2.4 above; wherever this
   document's "Lens A" citations are consumed, cite the carrying artifact or dated
   channel entry instead.

---

## ADDENDUM 2026-08-20T01:11:30Z — the owner's directive, quoted verbatim from the transcript (correcting the audit's correction)

The confabulation audit's marked correction at L22-24 removed the clause "the central
moments, the deviations of the observations from their mean" as fabricated. A
first-person transcript check shows the owner DID send it, as a queued mid-turn
message the audit's extraction missed. The owner's two messages, copy-pasted verbatim:
1. "What about moments about the mean because we are looking at the Kurtosis what
   about the other elements and the inference between them"
2. "Like the central moments, the deviations from the observations from their mean"
The original prompt's defect was a one-preposition smoothing ("of" for "from") inside
a verbatim label — an R3 violation, not fabrication. Full regrade:
audit_self/CONFABULATION_AUDIT_20260819.md, dated 2026-08-20T01:11:30Z.
