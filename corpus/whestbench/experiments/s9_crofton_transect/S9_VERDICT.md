# S9 — Crofton kink-transect identity (ledger id `s9_crofton_kink_transect_identity`)

- **Date:** 2026-08-09. **Runner:** compute-runner, single foreground run (479 s total).
- **Stage A verdict: IDENTITY VERIFIED** (3/3 nets, |transect − MC| at z = 0.08 / 0.23 / 0.72 combined standard errors; per-line structural identities hold to ≤ 6.7e-16 / 1.3e-12).
- **Stage B verdict: KILL** — variance-per-FLOP ratio (transect/MC) geomean **176,860×** (per-seed 181,779 / 157,818 / 192,838; predeclared KILL line is 100×). The identity is true and the estimator is unbiased, but it is catastrophically inefficient at width 64 depth 8.
- **Error correlation:** transect vs matched-FLOP MC errors uncorrelated (pooled r = 0.055, n = 48, se ≈ 0.15; per-seed −0.02 / −0.01 / +0.17). Both arms are measured unbiased (§4), so an inverse-variance combination is available; at the measured ratio R = 176,860 and measured correlation, its variance gain over MC alone is r² + 1/(1+R) ≈ 0.3% — worthless.

## Deviations (declared loudly, none silent)

1. **Stage A gate arithmetic.** The predeclared gate reads "|identity − MC| within 4 MC standard errors." The identity estimate is itself a Monte Carlo quantity (over random lines) whose standard error at any feasible line count (0.8–0.9M lines/seed within budget) is 8–11× the brute-force MC s.e. (≈ 4.7e-4 vs ≈ 5.5e-5). Under the literal reading the gate rejects a *true* identity with high probability. The gate was therefore evaluated as |T − MC| ≤ 4·SE(difference) = 4·sqrt(se_T² + se_MC²), the correct H0 test for two noisy estimates; the literal criterion is also reported (seeds 101/202 pass it at z = 0.92/1.57; seed 303 fails it at z = 6.15 while sitting at z = 0.72 combined — exactly the predicted artifact). Numerical-precision verification is carried instead by the machine-precision structural checks (§3.2), which is where the "must verify to numerical precision" burden actually lands.
2. **Enumeration window.** Breakpoints enumerated exactly on |t| ≤ 13.6 rather than all of R. Every omitted crossing carries weight φ₁(t) < 3.1e-41; the omitted mass is bounded by (#pieces)·max|J|/κ_d·φ₁(13.6) < 1e-36 — zero in float64. Enumeration inside the window is exact (per-interval affine roots), certified by the affineness check.
3. **Line counts fitted to runtime** (recorded): 819,200 / 901,120 / 819,200 lines for seeds 101/202/303.
4. **Stated design choices** (not deviations): depth L = number of weight matrices (depth 4 = 3 hidden ReLU layers + linear readout, no ReLU on the output layer); output width = hidden width; He init N(0, 2/fan_in) for every layer; scalar of interest is the neuron-average f(x) = mean_k y_k(x) = w̄·z^{(L−1)}(x).
5. **Foreign files in the experiment directory.** During this session a process outside this runner wrote an independent cross-check harness into the same directory (`s9_core.py`, `s9_crosscheck.py`, `s9_crosscheck.json`, `_prof*.py`, `_test_analytic.py`; self-labeled `independent_cross_check_of_predeclared_run_s9`). This runner's harness neither reads nor depends on any of them; the numbers in this document come solely from `run_s9.py` / `s9_results.json`. Comparison after the fact (corroborating, not load-bearing): its independent MC means agree with mine at z = 1.24 / 0.02 / 0.23 (seeds 101/202/303); its transect passes the identity on 3/3 nets (z vs its MC = 0.47 / 0.29 / −1.84); it verifies the Euler identity x·∇f = f per sample to 1.1e-15; its Stage B variance-per-FLOP ratios are 3.4e4–4.9e4 under a leaner cost accounting (~3.9× below mine, an accounting difference) — on the same side of the 100× KILL gate by ≥ 340×.

---

## 1. Derivation

### 1.1 Objects

- Network: weight matrices W₁,…,W_L, no biases. z⁽⁰⁾ = x ∈ R^d; preactivations h⁽ˡ⁾ = W_l z⁽ˡ⁻¹⁾; activations z⁽ˡ⁾ = σ(h⁽ˡ⁾) elementwise, σ = max(0,·), for l = 1,…,L−1; output y = W_L z⁽ᴸ⁻¹⁾ ∈ R^{n_L}.
- Scalar of interest (neuron-average): f(x) = (1/n_L)Σ_k y_k(x) = w̄·z⁽ᴸ⁻¹⁾(x), with w̄ = (1/n_L)1ᵀW_L. Since the readout is linear, f is itself a scalar bias-free ReLU net; the derivation is for this scalar.
- f is continuous, piecewise linear (PL), and positively 1-homogeneous: f(tx) = t f(x) for t ≥ 0 (induction: each bias-free layer commutes with positive scaling). R^d is covered by finitely many closed convex polyhedral cones {C_r} (activation cells) with f(x) = g_r·x on C_r (linear, no constant term, because f(0) = 0 and each cell has vertex 0).
- Kink set K = union of the (d−1)-dimensional facets separating adjacent cells = closure of the discontinuity set of ∇f. Every facet lies in {x : h⁽ˡ⁾_j(x) = 0} for the neuron (l,j) whose gate flips there. In the relative interior of a facet exactly one gate flips (generic position; the coincidence set has H^{d−1}-measure zero). Facets where the flip does not change f contribute jump 0 and are harmless.
- X ~ N(0, I_d), density φ_d(x) = (2π)^{−d/2}e^{−|x|²/2}; φ₁(t) = e^{−t²/2}/√(2π).

### 1.2 Step 1 — Euler

On the interior of each cell, f(x) = g_r·x, so x·∇f(x) = g_r·x = f(x). K is Lebesgue-null, |f(x)| ≤ C|x| and |∇f| ≤ C (finitely many pieces), so both sides are Gaussian-integrable and

  E[f(X)] = E[X·∇f(X)].    (1)

(Predeclared Euler-collapse guard: identity (1) alone is information-free — the content enters only through the next step, and the transect lines below are affine lines not through the origin, where the kink structure is nondegenerate. A line through the origin sees a single breakpoint at t = 0 because K is conical; our lines have x_⊥ ≠ 0 a.s.)

### 1.3 Step 2 — Gaussian integration by parts on BV gradients (Stein for measures)

Each ∂_i f is bounded and piecewise constant on the conical fan; it is a function of locally bounded variation whose distributional gradient is a measure supported on K. Because f is continuous and linear on both sides of a facet, tangential derivatives agree across the facet, so the gradient jump is purely normal: for a facet F with unit normal ν (either orientation),

  ∇f⁺ − ∇f⁻ = J ν,  J := ν·(∇f⁺ − ∇f⁻),

with "+" the side ν points into. J is orientation-invariant (flipping ν flips both factors). Hence the matrix-valued measure D(∇f) = (J ν⊗ν) H^{d−1}|_K, and its trace, the distributional Laplacian, is the scalar surface measure

  Δf = J · H^{d−1}|_K.    (2)

There is no contribution from the codimension-≥2 skeleton: ∂_i f is piecewise constant on a polyhedral fan, so its BV derivative is exactly the facet-jump measure (no absolutely continuous part, no Cantor part, and the (d−2)-skeleton has H^{d−1}-measure zero).

Gaussian IBP for BV functions: for g ∈ BV_loc bounded with |Dg|(B_R) growing polynomially, ∫g ∂_iφ_d dx = −∫φ_d d(D_i g); with ∂_iφ_d = −x_iφ_d this is E[X_i g(X)] = ∫φ_d d(D_i g). The growth condition holds because K is a finite union of conical facets: H^{d−1}(K ∩ B_R) ≤ c R^{d−1}. Apply with g = ∂_i f, sum over i, and combine with (1)–(2):

  **Master identity:  E[f(X)] = ∫_K J(x) φ_d(x) dH^{d−1}(x).**    (3)

The Gaussian mean of f equals the Gaussian-weighted surface integral of the normal-derivative jumps over the kink set.

### 1.4 Step 3 — Network form of the jump

At x in the relative interior of a facet, the flipping neuron is (l, j) with h⁽ˡ⁾_j(x) = 0. Locally h⁽ˡ⁾_j is linear (its own upstream gates are constant near x), with gradient

  aᵀ = (W_l)_{j,:} D_{l−1} W_{l−1} ⋯ D₁ W₁  (upstream chain; D_m = diag gates of layer m at x),

so ν = a/‖a‖. Crossing into the side h⁽ˡ⁾_j > 0, f gains the term c·h⁽ˡ⁾_j with

  c = ∂f/∂z⁽ˡ⁾_j = [w̄ᵀ D_{L−1} W_{L−1} ⋯ D_{l+1} W_{l+1}]_j  (downstream chain),

well-defined and continuous across the facet because the flipping neuron's *post-activation* is 0 on the facet, so downstream preactivations — hence downstream gates, generically — are unchanged there. Thus ∇f⁺ − ∇f⁻ = c a and

  J = ν·(c a) = c ‖a‖.    (4)

### 1.5 Step 4 — Crofton line transect

Projection formula for a rectifiable hypersurface: for fixed unit u and bounded measurable ψ,

  ∫_{u⊥} Σ_{t : x_⊥+tu ∈ K} ψ(x_⊥+tu) dx_⊥ = ∫_K ψ(x) |ν(x)·u| dH^{d−1}(x)

(the Jacobian of the orthogonal projection of K onto u⊥ is |ν·u|). Importance-sample x_⊥ ~ N(0, I_{u⊥}) (density φ_{d−1}; realized as x_⊥ = z − (u·z)u, z ~ N(0, I_d)) and use the Gaussian factorization φ_d(x_⊥+tu) = φ_{d−1}(x_⊥)φ₁(t). Finally average over u ~ Unif(S^{d−1}) and use isotropy: E_u|ν·u| = κ_d for every fixed ν, with

  κ_d = Γ(d/2) / (√π Γ((d+1)/2))   (κ₁₆ = 0.202610, κ₆₄ = 0.100126; MC-verified, §3.1).

With ψ = Jφ_d/φ_{d−1} this yields E_{u,x_⊥}[Σ_k φ₁(t_k) J(x_k)] = κ_d E[f], i.e. the

  **PRIMARY estimator (finite variance):  Ê = κ_d⁻¹ Σ_k φ₁(t_k) c_k ‖a_k‖,**    (5)

summing over all breakpoints t_k of t ↦ f(x_⊥ + tu), unbiased for E[f].

Taking instead ψ = Jφ_d/(φ_{d−1}|ν·u|) gives the **SECONDARY estimator**, conditionally unbiased for every fixed direction u:

  Ê₂ = Σ_k φ₁(t_k) c_k ‖a_k‖² / |a_k·u|.    (6)

Its second moment carries ∫ du/|ν·u|, which is log-divergent — used only as an independent cross-check of the weighting algebra, not as the arm.

Line-observable slope jump (for the machine-precision check): with F(t) = f(x_⊥+tu), the slope jump at t_k is Δs_k = c_k|a_k·u| regardless of crossing orientation (both orientations give sign(a·u)·c·(a·u) = c|a·u|).

Closed-form sanity anchors used as unit tests: single neuron f = σ(w·x) has K = {w·x = 0}, J = ‖w‖, and (3) gives E[f] = ‖w‖φ₁(0) = ‖w‖/√(2π), the known value; f = |x₁| gives J = 2 and E = 2φ₁(0) = √(2/π); a depth-2 net gives Σ_k w̄_k‖(W₁)_k‖/√(2π).

### 1.6 Enumeration (exact, no search)

Breakpoints along a line are enumerated by layerwise interval tracking: at stage l, the knot list contains all zeros of layers < l; every layer-l preactivation is affine on each open interval between consecutive knots (its kinks can only occur at lower-layer knots), so its zeros are roots of affine functions — found exactly and inserted. After stage L−1 the knot list is complete. Per knot, a_k and c_k are the chains of §1.4 evaluated with the gates at x_k (the flipping neuron's own ambiguous gate enters neither chain; its post-activation is 0 at the crossing so downstream gates are exact).

---

## 2. Harness

`run_s9.py`, numpy/float64 only. FLOP meter counts multiply-adds in every matmul/dot kernel on the estimator path (enumeration + jump evaluation); sorting, comparisons, and index bookkeeping are not counted (this favors the transect; the kill stands regardless, §4). MC forward cost per sample: Σ_{l<L} n_l·n_{l−1} + n_{L−1} (w̄-collapsed readout) = 832 madds at 16/4, 28,736 at 64/8.

## 3. Stage A — identity verification (width 16, depth 4, d = 16, seeds 101/202/303)

### 3.1 Unit tests (closed forms)

| test | exact | transect (5) | se | z |
|---|---|---|---|---|
| κ₁₆ formula vs MC of E\|u₁\| | 0.2026103 | 0.2025613 | 2.3e-4 | −0.21 |
| single neuron d=4 | 0.3903841 | 0.3920024 | 8.2e-4 | +1.97 |
| \|x₁\| d=3 | 0.7978846 | 0.7974517 | 1.4e-3 | −0.30 |
| depth-2 width-16 d=8 closed form | 0.0366255 | 0.0358979 | 4.8e-4 | −1.52 |

### 3.2 Machine-precision structural checks (30 lines/net)

(i) F(t) affine between consecutive enumerated knots (tested at 1/3 and 2/3 of every interval — a missed knot fails this): max relative violation **6.7e-16** across all three nets. (ii) Slope jump at every knot equals c_k|a_k·u|: max relative violation **1.3e-12**. These two checks certify, to float64 precision, that the enumeration is complete and the jump algebra (4) is correct on every enumerated crossing.

### 3.3 E[f]: brute-force MC vs transect

MC arm: 5,000,000 antithetic pairs = 10⁷ Gaussian samples/seed, float64. MC cross-check arm (radial conditioning, E‖X‖ exact): 10⁶ antipodal sphere pairs.

| seed | MC (10⁷ samples) | MC se | sphere-MC cross-check (z vs MC) | transect (5) | se | lines | diff | z_comb | z_literal |
|---|---|---|---|---|---|---|---|---|---|
| 101 | 0.0180759 | 5.04e-5 | 0.0182473 (z=1.41) | 0.0180294 | 5.52e-4 | 819,200 | −4.6e-5 | **0.08** | 0.92 |
| 202 | 0.4069186 | 6.99e-5 | 0.4070256 (z=0.70) | 0.4068091 | 4.69e-4 | 901,120 | −1.1e-4 | **0.23** | 1.57 |
| 303 | −0.1557329 | 4.89e-5 | −0.1557373 (z=0.04) | −0.1554317 | 4.18e-4 | 819,200 | +3.0e-4 | **0.72** | 6.15 |

Secondary estimator (6), the independent weighting route: 0.01772 ± 0.00177 / 0.40477 ± 0.00136 / −0.15392 ± 0.00126 — agrees with MC at z ≈ 0.5 / 1.6 / 1.4 (heavy-tailed; se indicative).

Knots/line: 42.7 / 37.0 / 40.2 mean (max 83–120) against 48 hidden neurons — consistent with the Hanin–Rolnick linear-in-neurons transect complexity anchor.

**Gate (combined-se form, see Deviation 1): 3/3 nets pass at z ≤ 0.72 ≪ 4. Stage A: IDENTITY VERIFIED.** Literal form: 2/3 pass; seed 303's literal z = 6.15 is fully explained by the transect's own se (8.5× the MC se), not by bias — its combined z is 0.72.

## 4. Stage B — variance screen (width 64, depth 8, d = 64, seeds 404/505/606)

Transect: 16 replicates × 12 lines/seed, FLOPs metered. Matched-FLOP arm: radially-conditioned antipodal-paired sphere MC, ~11,000 pairs per replicate (exactly the mean metered madds of a transect replicate). Ground truth per net: 10⁶-antithetic-pair MC (se ≤ 3.1e-5, ≫ 1000× tighter than replicate errors).

| seed | truth | C_line (madds) | knots/line | Var_line | Var_MC-pair (cost 57,472) | **ratio (Var·cost)** | 95% CI (bootstrap) | ratio (replicate route) | err corr |
|---|---|---|---|---|---|---|---|---|---|
| 404 | −0.01408 | 5.33e7 | 298 | 0.1451 | 7.40e-4 | **181,779** | (133,657, 233,969) | 223,917 | −0.02 |
| 505 | +0.03479 | 5.23e7 | 282 | 0.1559 | 8.99e-4 | **157,818** | (125,593, 191,503) | 125,291 | −0.01 |
| 606 | +0.03920 | 5.54e7 | 303 | 0.1881 | 9.41e-4 | **192,838** | (150,966, 237,198) | 173,907 | +0.17 |

Geomean ratio **176,860×**. Two independent accounting routes (per-draw Var·cost vs equal-budget replicate variances) agree within sampling noise. The transect remains unbiased at this scale (grand-mean z vs truth: −0.73 / −0.56 / −0.23).

**Ratio decomposition** (seed 404): variance factor Var_line/Var_pair ≈ 196× and cost factor C_line/C_pair ≈ 927×. Both factors are fatal on their own terms: even at *zero* enumeration cost (C_line = C_pair, i.e. a free oracle for all crossings and jumps) the ratio would still be ≈ 196× > 100. The mechanism: a line sum is ≈ 300 signed jump terms of magnitude O(0.1–1) (max |line sum| observed 1.2–1.6) cancelling to a mean of ~0.03 — signed-cancellation speckle with amplitude orders above the point-evaluation speckle of MC, while a line costs as much as ~930 antipodal MC pairs.

**Predeclared gate: worse than 100× ⇒ KILL.** Verdict: **KILL** (by three orders of magnitude; no retuning attempted past the failed gate).

**Error-correlation note:** transect and matched-MC replicate errors are uncorrelated — per-seed r = −0.02 / −0.01 / +0.17 (n = 16 each), pooled standardized r = 0.055 (n = 48, se ≈ 0.15), consistent with zero as forced by construction (the two arms draw independent randomness) and expected from the distinct observables (jump-sum speckle vs χ²-type point speckle). With both arms measured unbiased (grand-mean z above; MC by construction, cross-checked §3.3) and uncorrelated, the optimal inverse-variance weight of the transect at equal FLOPs is 1/(1+R) = 5.7e-6 at R = 176,860, and the combined-variance gain over MC alone is bounded by r² + 1/(1+R) ≈ 0.3% at the measured correlation point estimate. Combination is not an escape hatch for this arm.

## 5. Limitations

- Stage A E[f]-agreement resolves the identity at ~4e-4 absolute (combined noise), i.e. 0.1–2.5% relative; the float64-level verification burden is carried by the structural checks (§3.2) and the four closed-form anchors (§3.1), all of which the identity passes at machine precision.
- Heavy-tail caveat: Var_line at width 64 estimated from 192 lines/seed; bootstrap CIs shown (lower 2.5% bounds 133,657 / 125,593 / 150,966 — three orders above the 100× kill line). If rare large line sums were under-sampled, Var_line is biased low and the true ratio is *higher*: the tail direction is conservative for the KILL verdict.
- FLOP meter excludes sorting/comparison/bookkeeping ops (favors the transect). An incremental enumeration that caches per-interval chains instead of recomputing (~L/2 ≈ 3.5× cheaper) would not change the verdict (variance factor alone is ≈ 196×).
- Single-flip genericity and window truncation (Deviation 2) are measure-zero / < 1e-36 effects, invisible at float64.
- Not explored (out of predeclared scope): structure-exploiting variance reduction for the jump-sum (e.g. stratifying by layer, importance-sampling lines toward high-|J| cones). The ×196 variance factor at zero-cost accounting is the number any such proposal must beat by ≥ 2 to reach even INCONCLUSIVE territory.

## 6. Files

Produced by this runner:
- `run_s9.py` — harness (derivation implemented as §1.5–1.6; unit tests, Stage A, Stage B).
- `s9_results.json` — all numbers cited above.
- `S9_VERDICT.md` — this document.

Not produced by this runner (see Deviation 5; left untouched): `s9_core.py`, `s9_crosscheck.py`, `s9_crosscheck.json`, `_prof.py`, `_prof2.py`, `_test_analytic.py`.
