# P2 — An exact Crofton-type identity for the Gaussian mean of bias-free ReLU networks

**Internal mathematical note**, ledger id `s9_crofton_kink_transect_identity`, written 2026-08-10 from
`experiments/s9_crofton_transect/` (`S9_VERDICT.md` dated 2026-08-09, `s9_results.json`, `s9_crosscheck.json`, `s9_stageA20.json`) and the
exact-identity paragraph of `core/PHASE1_WRITEUP_DRAFT_20260808.md` §3a. Ledger status: **theorem PASSES, induced estimator KILLED**
(`PASSES_AND_UNCERTAINTIES_GRAPH_20260810.md` TH4, level [E]; `UNCERTAINTY_LADDER_20260810.md` §D, "identity PROVEN, estimator dead
1.8e5x"). Every number below is reproducible from those four artifacts.

## Abstract

For a bias-free ReLU network the Gaussian mean of the output is not merely approximable by sampling — it has an exact closed
representation as a surface integral. Positive homogeneity gives `E[f(X)] = E[X·∇f(X)]` (Euler); Gaussian integration by parts for BV
functions converts the right side into an integral against the distributional Laplacian of `f`, which for a piecewise-linear network is
exactly the gradient-jump measure carried by the kink set. The result is **`E[f(X)] = ∫_K J(x) φ_d(x) dH^{d−1}(x)`: the Gaussian mean
equals the Gaussian-weighted surface integral of the normal gradient jumps over the kink set.** The jump has a closed network form `J =
c‖a‖`, a downstream chain times an upstream chain, and a Crofton line-transect step turns the surface integral into a finite-variance
estimator over random lines whose breakpoints are enumerated exactly rather than searched.

We verified the identity at machine precision — structural checks to **6.7e-16**, two structurally distinct unbiased transect estimators,
3 predeclared plus 20 fresh random nets — then killed the estimator it induces: on the predeclared width-64 depth-8 screen its
variance-per-FLOP is **176,860× worse** than Monte Carlo against a predeclared kill line of 100×. The failure is intrinsic, not an
implementation artifact: with a free oracle for every crossing and jump the variance factor alone is still
**196.0 / 173.3 / 199.9× across seeds 404 / 505 / 606, geometric mean 189.4×** [O, `s9_results.json` `stage_B`].
(Draft 1 quoted "≈196×" here and in §5 — that is seed 404's value alone, presented without attribution as a
campaign-level figure. Corrected draft 2; §3.1's per-seed attribution was already right.) The identity is an
analysis instrument, not an estimator.

## 1. The identity

### 1.1 Setup

Weight matrices `W₁,…,W_L`, **no biases**. `z⁽⁰⁾ = x ∈ R^d`, preactivations `h⁽ˡ⁾ = W_l z⁽ˡ⁻¹⁾`, activations `z⁽ˡ⁾ = σ(h⁽ˡ⁾)` with `σ =
max(0,·)` for `l = 1,…,L−1`, output `y = W_L z⁽ᴸ⁻¹⁾`. The scalar of interest is the neuron-average `f(x) = (1/n_L)Σ_k y_k(x) =
w̄·z⁽ᴸ⁻¹⁾(x)`, `w̄ = (1/n_L)1ᵀW_L`; the readout is linear, so `f` is itself a scalar bias-free ReLU net and the derivation is stated for
the scalar case without loss.

`f` is continuous, piecewise linear and positively 1-homogeneous (`f(tx) = tf(x)`, `t ≥ 0`), so `R^d` is covered by finitely many closed
convex polyhedral **cones** `{C_r}` with `f = g_r·x` on `C_r` — linear with no constant term, since `f(0) = 0` and every cell has its
vertex at the origin. The kink set `K` is the union of `(d−1)`-dimensional facets separating adjacent cells; each lies in `{h⁽ˡ⁾_j = 0}`
for the one neuron `(l,j)` whose gate flips there (generic position; the coincidence set is `H^{d−1}`-null). `X ~ N(0,I_d)` with density
`φ_d`, `φ₁(t) = e^{−t²/2}/√(2π)`.

### 1.2 Euler × Stein

**Euler.** On each cell interior `f(x) = g_r·x`, so `x·∇f(x) = f(x)` pointwise; `K` is Lebesgue-null and `|f| ≤ C|x|`, `|∇f| ≤ C`, so both
sides are Gaussian-integrable and **(1)** `E[f(X)] = E[X·∇f(X)]`. A predeclared "Euler-collapse" guard was carried because (1) alone is
information-free — the content enters below. The transect lines used later are affine lines *not* through the origin: a line through the
origin sees a single breakpoint at `t = 0` because `K` is conical, and our lines have `x_⊥ ≠ 0` almost surely.

**Stein for measures.** Each `∂_i f` is bounded and piecewise constant on the conical fan, hence `BV_loc` with distributional gradient a
measure on `K`. Continuity of `f` plus linearity on both sides of a facet forces tangential derivatives to agree across it, so the
gradient jump is purely **normal**: `∇f⁺ − ∇f⁻ = Jν` with `J := ν·(∇f⁺ − ∇f⁻)`, orientation-invariant since flipping `ν` flips both
factors. Hence `D(∇f) = (Jν⊗ν)H^{d−1}|_K`, whose trace — the distributional Laplacian — is the scalar surface measure **(2)** `Δf = J ·
H^{d−1}|_K`. Nothing comes from the codimension-≥2 skeleton: on a polyhedral fan the BV derivative of a piecewise-constant function is
exactly the facet-jump measure (no absolutely continuous part, no Cantor part, `(d−2)`-skeleton `H^{d−1}`-null). Gaussian IBP for BV reads
`∫ g ∂_iφ_d dx = −∫ φ_d d(D_i g)`, and `∂_iφ_d = −x_iφ_d` turns it into `E[X_i g(X)] = ∫ φ_d d(D_i g)`, the polynomial-growth condition
holding because `K` is a finite union of conical facets (`H^{d−1}(K ∩ B_R) ≤ cR^{d−1}`). Apply with `g = ∂_i f`, sum over `i`, combine
with (1) and (2):

> ### Master identity
> **(3)**  `E[f(X)] = ∫_K J(x) φ_d(x) dH^{d−1}(x)`

Euler supplies the homogeneity that removes the volume term; Stein supplies the boundary measure.

### 1.3 Network form of the jump

At a facet point the flipping neuron is `(l,j)` with `h⁽ˡ⁾_j(x) = 0`; locally `h⁽ˡ⁾_j` is linear with gradient the **upstream chain** `aᵀ
= (W_l)_{j,:} D_{l−1}W_{l−1} ⋯ D₁W₁` (`D_m` = layer-`m` gate diagonal), so `ν = a/‖a‖`. Crossing into `h⁽ˡ⁾_j > 0`, `f` gains `c·h⁽ˡ⁾_j`
with the **downstream chain** `c = ∂f/∂z⁽ˡ⁾_j = [w̄ᵀ D_{L−1}W_{L−1} ⋯ D_{l+1}W_{l+1}]_j`, well-defined and continuous across the facet
because the flipping neuron's *post-activation* is 0 there, leaving downstream preactivations and gates unchanged. So `∇f⁺ − ∇f⁻ = ca` and
**(4)** `J = ν·(ca) = c‖a‖`.

### 1.4 Crofton line transect

For a rectifiable hypersurface and fixed unit `u`, `∫_{u⊥} Σ_{t : x_⊥+tu ∈ K} ψ dx_⊥ = ∫_K ψ|ν·u| dH^{d−1}` (the projection Jacobian onto
`u⊥` is `|ν·u|`). Importance-sample `x_⊥ ~ N(0,I_{u⊥})`, use `φ_d(x_⊥+tu) = φ_{d−1}(x_⊥)φ₁(t)`, average over `u ~ Unif(S^{d−1})`, and
invoke isotropy: `E_u|ν·u| = κ_d` for every fixed `ν`, with `κ_d = Γ(d/2)/(√π Γ((d+1)/2))`, `κ₁₆ = 0.202610`, `κ₆₄ = 0.100126` (both
recomputed for this note from `lgamma`, matching `s9_results.json` to ≤6.7e-16 relative). With `ψ = Jφ_d/φ_{d−1}`:

> ### Primary estimator (finite variance)
> **(5)**  `Ê = κ_d⁻¹ Σ_k φ₁(t_k) c_k‖a_k‖`

summing over all breakpoints `t_k` of `t ↦ f(x_⊥+tu)`; unbiased for `E[f]`. Taking `ψ = Jφ_d/(φ_{d−1}|ν·u|)` gives a **secondary**
estimator `Ê₂ = Σ_k φ₁(t_k)c_k‖a_k‖²/|a_k·u|`, conditionally unbiased at every fixed `u` but with a log-divergent second moment
(`∫du/|ν·u|`) — an independent check on the weighting algebra, never an arm. The line-observable slope jump, which is what the
machine-precision check tests, is `Δs_k = c_k|a_k·u|` regardless of crossing orientation.

### 1.5 Exact enumeration (no search)

Breakpoints along a line are found by layerwise interval tracking: at stage `l` the knot list holds all zeros of layers `< l`; every
layer-`l` preactivation is affine on each open interval between consecutive knots (its own kinks can only sit at lower-layer knots), so
its zeros are roots of affine functions, computed exactly and inserted; after stage `L−1` the list is complete. This is why verification
reaches float64 — nothing is bisected or thresholded.

## 2. Verification at machine precision

### 2.1 Structural checks — the load-bearing evidence

30 lines per net, width 16, depth 4, `d = 16`, seeds 101/202/303:

| check | what a failure would mean | max relative violation |
|---|---|---|
| `F(t)` affine between consecutive knots (probed at 1/3 and 2/3 of every interval) | a missed knot | **6.7e-16** |
| slope jump at every knot equals `c_k\|a_k·u\|` | jump algebra (4) is wrong | **1.3e-12** |

Together these certify at float64 that the enumeration is complete and the jump algebra is correct at every enumerated crossing. This is
where the "verify to numerical precision" burden actually lands (§5.1). Four closed-form anchors also pass: `κ₁₆` = 0.2026103 vs MC of
`E|u₁|` (z = −0.21); single neuron `d=4`, exact 0.3903841 vs 0.3920024 (+1.97); `|x₁|`, `d=3`, exact 0.7978846 vs 0.7974517 (−0.30);
depth-2 width-16 `d=8` closed form 0.0366255 vs 0.0358979 (−1.52). These follow from (3) directly — a single ReLU `σ(w·x)` has `K = {w·x =
0}`, `J = ‖w‖`, so `E[f] = ‖w‖/√(2π)`, and `f = |x₁|` has `J = 2`, `E = √(2/π) = 0.7978846` (recomputed here).

> **Cross-check note, found while writing this note and recorded rather than absorbed:** per-seed jump violations in
> `s9_results.json` are 1.32e-13 / 1.10e-13 / 1.15e-12 (101/202/303), so the true maximum is **1.15e-12**. The verdict's
> headline 1.3e-12 is a conservative statement of that maximum (it appears to blend seed 303's 1.15e-12 with seed 101's
> 1.32e-13); it is looser than measured, so nothing is overstated. The affine figure reproduces exactly (6.660e-16).

### 2.2 `E[f]`: brute-force MC vs transect (Stage A, 3 predeclared nets)

MC arm: 5,000,000 antithetic pairs = 10⁷ Gaussian samples per seed, float64, plus a radial-conditioning sphere-MC cross-check arm at 10⁶
antipodal pairs.

| seed | MC (10⁷) | MC se | sphere-MC (z vs MC) | transect (5) | se | lines | diff | z_comb |
|---|---|---|---|---|---|---|---|---|
| 101 | 0.0180759 | 5.04e-5 | 0.0182473 (1.41) | 0.0180294 | 5.52e-4 | 819,200 | −4.6e-5 | **0.08** |
| 202 | 0.4069186 | 6.99e-5 | 0.4070256 (0.70) | 0.4068091 | 4.69e-4 | 901,120 | −1.1e-4 | **0.23** |
| 303 | −0.1557329 | 4.89e-5 | −0.1557373 (0.04) | −0.1554317 | 4.18e-4 | 819,200 | +3.0e-4 | **0.72** |

Secondary estimator (6): 0.01772 ± 0.00177 / 0.40477 ± 0.00136 / −0.15392 ± 0.00126, agreeing with MC at z ≈ 0.5 / 1.6 / 1.4
(heavy-tailed, se indicative). Knots per line 42.7 / 37.0 / 40.2 (max 83–120) against 48 hidden neurons, consistent with the Hanin–Rolnick
linear-in-neurons transect-complexity anchor (§4).

### 2.3 Second signal: independent runner, structurally different estimator

A separate runner (`s9_core.py`, `s9_crosscheck.py`, `s9_stageA20.py`) built its own engine with exact per-sample gradients via mask
products and a **different** unbiased weighting — the slope-jump / factor-`d` form from 1D Stein along the transect, `E[f] =
d·E_{u,x_⊥}[Σ_k Δβ_k φ₁(t_k)]` with `Δβ_k = c_k(a_k·u)`, against §1.4's Crofton form `κ_d⁻¹ Σ_k φ₁(t_k)c_k‖a_k‖`. Agreement of two
structurally distinct weightings against high-precision MC is the strong check.

- **Euler leg, machine-exact:** per-sample `max|x·∇f − f|` = **1.1e-15** on the depth-1 closed form and the 3
  predeclared seeds; **8.88e-15** on **20 fresh random nets** (width 16, depth 4).
- **Surface form, 20 fresh nets:** pooled `z = (transect − MC)/SE_diff` has **mean −0.25, sd 0.92, max|z| 2.75, 20/20
  within 3σ** — consistent with `N(0,1)`, i.e. unbiased across random nets.
- **On the predeclared seeds:** independent transect vs its own MC at z = +0.47 / +0.29 / −1.84; its MC means match the
  §2.2 MC means at z = 1.24 / 0.02 / 0.23; depth-1 closed form matched at z = 0.56 (0.3%).

### 2.4 Which surfaces are required: all of them

Tagging each crossing by the layer of its flipping neuron splits the transect sum into per-layer sub-sums that add to the total. The
**full multi-layer** integral closes the identity; the agreement above holds only because every layer `l = 1…L−1` is summed.
**First-layer-only does not close.** Layer fractions `[L1,L2,L3]` are `[0.49, 0.13, 0.38]` (seed 202) and `[0.17, 0.29, 0.54]` (seed 303);
across the 19 non-degenerate fresh nets (`|E[f]| > 0.05`) the mean is `[−0.54, 0.45, 1.09]` with the layer-1 share ranging over ≈`[−5.05,
+1.61]`. Individual layer contributions carry either sign and are high-variance net-to-net; the harness-independent conclusion is that the
layer-1 sub-sum is nowhere near `E[f]` and the deeper facets `{h⁽ˡ⁾_j = 0}`, `l ≥ 2`, carry the majority. At depth 1 there are no deeper
layers and first-layer-only closes exactly, which is the consistency check.

## 3. The honest failure: the induced estimator is dead

The identity is true and estimator (5) is unbiased. On the predeclared variance screen it lost by three orders of magnitude. **Screen:**
width 64, depth 8, `d = 64`, seeds 404/505/606; transect at 16 replicates × 12 lines per seed with a FLOP meter counting multiply-adds on
the estimator path, against a matched-FLOP radially-conditioned antipodal-paired sphere MC (~11,000 pairs per replicate, matched to the
mean metered madds of a transect replicate). Ground truth per net from 10⁶ antithetic pairs.

| seed | truth | C_line (madds) | knots/line | Var_line | Var_MC-pair | **ratio (Var·cost)** | 95% CI | replicate route | err corr |
|---|---|---|---|---|---|---|---|---|---|
| 404 | −0.01408 | 5.33e7 | 298 | 0.1451 | 7.40e-4 | **181,779** | (133,657, 233,969) | 223,917 | −0.02 |
| 505 | +0.03479 | 5.23e7 | 282 | 0.1559 | 8.99e-4 | **157,818** | (125,593, 191,503) | 125,291 | −0.01 |
| 606 | +0.03920 | 5.54e7 | 303 | 0.1881 | 9.41e-4 | **192,838** | (150,966, 237,198) | 173,907 | +0.17 |

> **Geometric-mean ratio 176,860×. Predeclared KILL line 100×. Verdict: KILL** — no gate softened, no retuning attempted
> past the failed gate.

The transect stays unbiased at this scale (grand-mean z vs truth −0.73 / −0.56 / −0.23), so this is a pure efficiency loss, not a
correctness loss.

### 3.1 Why — the mechanism

Decomposing seed 404's ratio (reproduced for this note: `0.14505/7.399e-4 × 5.3289e7/5.7472e4 = 181,779`): **variance factor**
`Var_line/Var_pair ≈ 196×`, **cost factor** `C_line/C_pair ≈ 927×`. Each is fatal on its own terms. **Even at zero enumeration cost** — a
free oracle handing over every crossing and every jump — the ratio is still ≈196×, on the kill side of the 100× line. The estimator is not
rescuable by faster code.

The mechanism is **signed-cancellation speckle**. One line contributes a sum of ≈300 signed jump terms of magnitude `O(0.1–1)` (observed
max |line sum| 1.2–1.6) that cancel down to a mean of ~0.03. The fluctuation amplitude is set by the individual jumps, orders above the
point-evaluation speckle MC pays, while one line costs about as much as 930 antipodal MC pairs. The transect integrates a large,
nearly-cancelling surface quantity to recover a small volume quantity — and that cancellation is the entire content of the identity, which
is exactly what makes the identity a bad sampler.

### 3.2 Combination is not an escape hatch, and the kill is robust

Both arms are measured unbiased and their errors are uncorrelated by construction (independent randomness) and by measurement: per-seed r
= −0.02 / −0.01 / +0.17, pooled r = 0.055 (n = 48, se ≈ 0.15). The optimal inverse-variance weight on the transect at equal FLOPs is
`1/(1+R) = 5.65e-6`, so the combined variance gain over MC alone is bounded by `r² + 1/(1+R) ≈ 0.3%` (recomputed: 0.003014 + 0.0000057 =
0.00302). Worthless. Four further checks agree: the independent runner's ratios are 3.4e4–4.2e4× vs plain MC and 4.0e4–4.9e4× vs
radial-antipodal MC, ~3.7× below the madd-meter figure (a leaner per-kink FLOP model) but on the same side of the gate by **≥340×**;
per-draw `Var·cost` and equal-budget replicate variances agree within sampling noise (last two numeric columns); bootstrap lower 2.5%
bounds of 133,657 / 125,593 / 150,966 stay three orders above the kill line, and under-sampled rare large line sums would bias `Var_line`
*low*, raising the true ratio; and the meter excludes sorting, comparisons and bookkeeping, flattering the loser — an incremental
enumeration caching per-interval chains (~`L/2 ≈ 3.5×` cheaper) would not change the verdict.

## 4. Related work

The S9 artifacts name exactly one external anchor and this note adds none: the **Hanin–Rolnick** linear-in-neurons result on transect
complexity, invoked as the reason 42.7 / 37.0 / 40.2 knots per line against 48 hidden neurons is the expected count rather than a bug. No
other citation appears in `S9_VERDICT.md`, `run_s9.py`, `s9_core.py`, `s9_crosscheck.py` or `s9_stageA20.py`. Placing (3) against the
Gaussian-BV/Crofton and PL-network-geometry literatures remains to be done by someone with the sources in hand, not reconstructed from
memory.

## 5. What the identity is still good for

The estimator is dead; the representation is not, and it earns its keep for what it says rather than what it computes. **An exact
decomposition of the mean by layer:** §2.4 is unavailable from sampling at all, since `E[f]` splits exactly into per-layer surface
contributions summing to the total, and the measured layer-1 share ranging over ≈[−5, +1.6] with deeper layers dominating is an exact
rather than fitted statement about where a deep ReLU net's Gaussian mean comes from — it falsifies any claim that first-layer kink
geometry explains a network-level Gaussian quantity. **A substitutable exact target:** being an identity, (3) drops into other
derivations, and `J = c‖a‖` factorizes into upstream and downstream chains, the same product structure the depth-transmission law (S8/S12)
manipulates. **A machine-precision test oracle:** the §2.1 checks test any code claiming to enumerate a PL network's breakpoints along a
line — affineness between knots catches a missed knot, `Δs_k = c_k|a_k·u|` catches a wrong chain — both float64-tight and needing no
reference implementation. **A negative result with a stated price:** the **≥173×** zero-cost variance factor
(geomean 189.4×, per-seed 196.0 / 173.3 / 199.9) is the bar any
structure-exploiting successor must clear (stratifying by layer, importance-sampling lines toward high-`|J|` cones), by ≥2 to reach even
INCONCLUSIVE.

### 5.1 Caveats carried forward

- Stage-A `E[f]`-agreement resolves the identity to ~4e-4 absolute (0.1–2.5% relative), *not* to float64. The
  machine-precision claim rests on the structural checks and closed-form anchors of §2.1, where it belongs.
- **Declared gate deviation.** The predeclared Stage-A gate read "|identity − MC| within 4 MC standard errors", but the
  transect estimate is itself a Monte Carlo quantity whose se at feasible line counts is 8–11× the brute-force MC se
  (≈4.7e-4 vs ≈5.5e-5; seed 303's ratio recomputed here as 8.54×), so the literal reading rejects a *true* identity with
  high probability. It was evaluated as `|T − MC| ≤ 4·√(se_T² + se_MC²)`, the correct H0 test for two noisy estimates,
  with the literal form reported alongside: 101/202 pass it (z = 0.92 / 1.57), 303 fails it at z = 6.15 while sitting at
  z_comb = 0.72 — the predicted artifact, and the reason the float64 burden was moved onto §2.1.
- **Enumeration window.** Breakpoints were enumerated on `|t| ≤ 13.6` rather than all of `R`. Every omitted crossing
  carries `φ₁(t) < 3.1e-41` (recomputed: `φ₁(13.6) = 2.74e-41`) and the omitted mass is bounded by <1e-36 — zero in
  float64. Enumeration inside the window is exact. Single-flip genericity is measure-zero; facets where the flip does
  not change `f` contribute jump 0 and are harmless.
- Everything is measured at width 16 depth 4 (Stage A) and width 64 depth 8 (Stage B), He init, synthetic nets only. The
  identity is a theorem and does not depend on scale; the ×176,860 is one measurement at one scale, and the variance
  factor should be expected to grow with crossings per line.

## 6. Files

Primary harness: `experiments/s9_crofton_transect/run_s9.py`, `s9_results.json`, `S9_VERDICT.md`. Independent verification harness
(different estimator and engine): `s9_core.py`, `s9_crosscheck.py`, `s9_crosscheck.json`, `s9_stageA20.py`, `s9_stageA20.json`. Campaign
context: `core/PHASE1_WRITEUP_DRAFT_20260808.md` §3a, `core/PASSES_AND_UNCERTAINTIES_GRAPH_20260810.md` (TH4),
`core/UNCERTAINTY_LADDER_20260810.md` §D, `core/GRAVEYARD_MINE_20260810.md` (S9 among the mechanism kills that hold on their own
measurements).
