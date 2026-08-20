# Open-Frontier Literature Sweep — WhestBench Estimator (research brief)

- **Filed:** 2026-08-09 (dated 20260810 per task spec)
- **Agent:** research subagent, read-only sweep (WebSearch + arXiv + Consensus/Semantic-Scholar corpus)
- **Problem:** per-neuron means E[ReLU-MLP output] over N(0,I) input; width 256, depth 32, He init, bias-free; hard FLOP budget; white-box.
- **Champion:** structured spherical design sampling (exact radial conditioning by positive homogeneity + 64,512-pt MUB design + antipodal pairing); error = independent chi^2_1 speckle.
- **Filter applied:** every item below is checked against the closed-family list (Gaussian/moment closures, design perturbations, rotation selection, RQMC/lattices, tractable harmonic CVs, mid-layer exact composition, offline-trained correctors, terminal smoothing, pruning/fold retuning, f32, bit-tricks). Verdicts: **NEW** / **VARIANT** (of closed family) / **IRRELEVANT**.

---

## Q1 — Exact/algorithmic identities for Gaussian integration of piecewise-linear networks

**Bottom line: the literature contains no algorithm with cost polynomial in width and sub-exponential in depth. Exact approaches all route through the activation-region (bent hyperplane arrangement) decomposition, whose region count and per-region Gaussian measures are both intractable at this scale.**

### Key papers

| Paper | Year / ID | Relevance | Verdict |
|---|---|---|---|
| Parallel Algorithms for Exact Enumeration of DNN Activation Regions | 2024, arXiv:2403.00860 | Exact region enumeration; cost scales with region count, which is exponential in depth. Confirms exact cell-decomposition is dead at 256x32. | IRRELEVANT (cost) |
| Zhang, Naitzat, Lim — Tropical Geometry of Deep Neural Networks | 2018, arXiv:1805.07091 | ReLU nets = tropical rational maps; f = p - q with p,q convex PL (maxima of affine families); depth-2 blocks characterized by zonotopes. E[f] = E[p] - E[q], but monomial count grows exponentially with depth and no integration algorithm is given anywhere in the tropical literature. | IRRELEVANT (representation only) |
| The Real Tropical Geometry of Neural Networks | 2024, arXiv:2403.11871 | Parameter-space semialgebraic geometry; nothing on integration. | IRRELEVANT |
| Ridgway — Computation of Gaussian orthant probabilities in high dimension | 2014, arXiv:1411.1314 | State of the art for the per-region measures the cell decomposition needs: high-dim orthant probabilities are themselves estimated by sequential-conditioning MC (GHK) + quadrature splits. No exact poly algorithm exists even for one orthant. | IRRELEVANT (inner problem already MC) |
| Kabluchko, Zaporozhets — Grassmann angles and absorption probabilities of Gaussian convex hulls | 2020, arXiv:1911.04184 | Conic intrinsic volumes / Grassmann angles are the right invariants for bias-free nets (all activation cells are cones), with exact formulas for special cones (Weyl chambers, simplices). No composition rule for deep-net cone arrangements exists. | IRRELEVANT today; the only Q1 thread with structure |
| Solid angle measure of polyhedral cones | 2023, arXiv:2304.11102 | Hypergeometric-series solid-angle computation, simplicial decomposition; cost blows up with dimension/cone count. | IRRELEVANT (cost) |
| Explicit integral representations for two-layer ReLU networks | 2026, arXiv:2604.23260 | Approximation-theoretic integral representations (harmonic extension + projection); not an estimator, not compositional. | IRRELEVANT |
| Complexity background: polytope volume is #P-hard (Dyer–Frieze); Barvinok-type exact integration is poly only in fixed dimension (arXiv:1108.0117, math/0603308) | — | Confirms no generic escape hatch: exact Gaussian integration over the cell complex inherits #P-hardness flavor. | closes the question |

### Extracted structural fact
For a bias-free net, every activation region is a polyhedral **cone** and f is linear on each cone, so exactly:
E[f] = sum_over_cones_C ( a_C . m_C ), with m_C = E[X 1{X in C}] the Gaussian first moment of cone C (a conic-intrinsic-volume-type quantity). Everything intractable is in the number of cones and in m_C. No published shortcut.

**Q1 verdict: no NEW mechanism class found.** The one live research direction (not yet in any paper): a composition rule for Grassmann angles of iterated cone arrangements. High risk, no literature support; not recommended for competition timeline.

---

## Q2 — Multilevel / multi-fidelity with width or depth as the fidelity axis

**Bottom line: nobody has published depth-truncated or width-sketched versions of a network as MLMC/MFMC levels for that same network's output statistics. The machinery (coupled two-level estimators, unbiased randomized truncation, MFMC allocation theory) is mature and immediately transplantable. This is a NEW mechanism class for the closed-family list — but the standard MFMC gain formula makes the S8-derived numbers look marginal; run the falsifier before investing.**

### Key papers

| Paper | Year / ID | Relevance | Verdict |
|---|---|---|---|
| Peherstorfer, Willcox, Gunzburger — Optimal model management for multifidelity MC (MFMC) | 2016, SIAM J. Sci. Comput. 38(5) | THE allocation theory: with surrogate correlation rho and cost ratio c, best-case MSE reduction vs plain MC = 1 / (sqrt(1-rho^2) + sqrt(c*rho^2))^2. Directly scores any width/depth surrogate. | NEW (mechanism class: coupled-surrogate two-level estimator) |
| El Amri et al. — Multilevel Surrogate-based Control Variates | 2023, consensus.app id 82b15255 | MLMC + surrogate CVs combined (MLCV / MLMC-CV / MLMC-MLCV); shows surrogates for coarse levels only already capture most of the gain. Template for a depth-hierarchy version. | NEW (same class) |
| Rhee & Glynn — Unbiased estimation with square-root convergence for SDE models | 2015, Oper. Res. 63 | Randomized-truncation unbiased telescoping: Z = sum_{l<=N} Delta_l / P(N>=l). Removes all bias from a level hierarchy if Var(Delta_l) decays. | NEW (enabler) |
| Zheng et al. — Optimal distributions for randomized unbiased estimators, adaptive algorithm | 2023, IMA J. Numer. Anal. | Closed-form optimal truncation distributions + cheap adaptive tuning — solves the level-distribution design problem for free. | NEW (enabler) |
| Multi-level Monte Carlo Dropout | 2026, arXiv:2601.13272 | Coupled coarse–fine estimators by SHARING dropout masks across fidelities → unbiased telescoping MLMC for network predictive means. Closest published relative of "width as fidelity axis": proves the coupling trick works on network outputs. | NEW-adjacent evidence |
| Epperly, Tropp — Efficient error and variance estimation for randomized matrix computations | 2022, arXiv:2207.06342 | Jackknife/leave-one-out variance diagnostics for sketched computations — the audit tooling for a sketched surrogate. | supporting |
| Resource-efficient randomized algorithms for matrix computations | 2025, arXiv:2512.15929 | Unbiased randomized SVD via leave-one-out; decomposition "known low-rank piece + residual" = exactly the two-level template at the linear-algebra level. | supporting |
| Tallec & Ollivier — Unbiasing Truncated Backpropagation Through Time | 2017 | Russian-roulette debiasing of a truncated recursive computation (depth axis in time). Proof the idea transfers to deep compositional structures. | NEW-adjacent evidence |
| Multi-fidelity NN surrogate sampling for UQ | 2019, arXiv:1909.01859 | NN as surrogate for an external simulator — NOT the net-as-its-own-surrogate pattern; listed to mark the distinction. | IRRELEVANT |

### Extracted estimators
1. **Two-level coupled correction (width-sketch fidelity):** build f_r by replacing each W_l (256x256) with a factored sketch (W_l S_l)(S_l^T .) or shared projection, cost ratio c ≈ r/256 per matmul. Estimate E[f] = mean_many[f_r(x)] + mean_few[f(x) - f_r(x)] with SHARED x in the correction term. Unbiased by construction regardless of sketch quality (bias lives in no term; f_r's bias cancels between the two sums). As r→256 the correction variance →0.
2. **Depth-surrogate CV:** g(x) = linear readout of layer-5 activations (weights chosen white-box, no response fitting — e.g., propagate the champion's fold weights). E[f] = mean_many[g] + mean_few[f - g], same coupling. S8 says layers 0–4 carry 46% of output-field structure → rho^2 ≈ 0.46, c ≈ 5/32 ≈ 0.156. **MFMC formula gives gain = 1/(sqrt(0.54)+sqrt(0.156*0.46))^2 ≈ 1.00 — essentially zero.** Depth-5 at rho^2=0.46 does not pay. The mechanism only pays if a cheap surrogate reaches rho^2 >~ 0.85 at c <~ 0.15 (then ~2.4x).
3. **Randomized-depth unbiasing caveat:** raw depth truncation is NOT a convergent fidelity axis here — layer-l activations are not approximations of the layer-32 output under any natural coupling; Rhee–Glynn needs Var(Delta_l)→0. Depth only becomes a fidelity axis through surrogate readouts, which reduces it to estimator 2. Width sketching IS convergent (r→n exact) and is the axis to prefer.

### Cheapest response-free falsifier (NEW class)
On 3 locally generated He-init 256x32 nets: build (a) rank-r sketched nets for r in {32, 64, 128}, (b) a depth-5 white-box readout surrogate; on 4k shared inputs compute rho between surrogate and full output field per neuron; plug (rho, honest FLOP ratio c including sketch construction) into the MFMC formula. Kill the class if max gain < 1.3x; promote if any (r, c) pair clears 2x.

---

## Q3 — Stein / Malliavin identities on Gaussian space for deep compositions

**Bottom line: two exact identities extracted, one architecture-specific degeneracy discovered that kills the most obvious Stein tricks, and one genuinely new estimator geometry (kink-surface / Crofton transect) that no paper has published for network-mean estimation.**

### Identity ledger (derived this sweep; verify locally before use)
- **Stein / Gaussian IBP:** E[X_i g(X)] = E[d_i g(X)] for X~N(0,I_n), g abs. continuous. For a ReLU net, grad f is piecewise constant, cost ~1 backprop.
- **Dilation interpolation:** E[f(X)] = f(0) + int_0^1 E[X . grad f(sX)] ds (generic f).
- **DEGENERACY (architecture-specific, important):** a bias-free ReLU net is positively homogeneous of degree 1, so Euler's identity gives x . grad f(x) = f(x) a.e. Consequences: (i) the dilation/OU-semigroup interpolation identities are trivially self-consistent — zero information; (ii) exact 1D line integration through the origin collapses to antipodal pairing, which the champion already owns; (iii) the naive Stein control variate f - x.grad f is identically zero. **Any Q3 proposal must first be checked against Euler collapse.**
- **Kink-surface identity (the survivor):** combining Euler + coordinatewise Stein on g_i = d_i f:
  E[f(X)] = E[X . grad f(X)] = sum_i E[d_ii f] = integral over the kink set K of J_nu(x) phi_n(x) dH^{n-1}(x),
  where the distributional Laplacian of a piecewise-linear f is a surface measure on K (the union of conical facets where a neuron flips) and J_nu = jump of the normal derivative across the facet. The mean becomes a Gaussian-weighted surface integral of gradient jumps — a completely different observable than point evaluations, hence a different (non-chi^2_1) error law. Estimable by Crofton/stereology line transects: crossings of K along random lines, weighted 1/|<nu,u>|, give unbiased surface-integral estimates. Cost anchor: Hanin & Rolnick (ICML 2019, arXiv:1901.09021) prove the expected number of linear pieces along a 1D line at init is LINEAR in the number of neurons (~8192 here), and each breakpoint is found by exact 1D piecewise-linear propagation, not search.

### Key papers

| Paper | Year / ID | Relevance | Verdict |
|---|---|---|---|
| Oates, Girolami, Chopin — Control functionals for Monte Carlo integration | 2017, JRSS-B 79(3) (consensus id 10de39ce) | Stein-operator CVs with NONPARAMETRIC (function-adapted) test functions: fit u so A[u](x) = Lap u - x.grad u interpolates f's fluctuation; E[A[u]] = 0 exactly; achieves faster-than-1/n rates. Distinct from the closed "tractable harmonic CV" family: the basis adapts to f via its sampled values/gradients, so the 1.8e8-dim energy-dispersion argument does not directly apply. Known weakness: kernel CFs degrade badly with dimension (d=256 input; but the champion samples on a sphere — spherical-kernel CF in d=255 still hard). | **NEW (borderline)** |
| Si et al. — Scalable Control Variates via Stochastic Optimization | 2020, arXiv:2006.07487 | Unifies polynomial/kernel/NN Stein CVs; the optimization cost counts against the FLOP meter. | VARIANT (harmonic-CV family unless basis adapts) |
| Sun et al. — Vector-Valued Control Variates | 2021, consensus id aae6b9cb | Matrix-valued Stein kernels share strength across MANY related integrals — matches our 256-output-neuron structure (one CV fit, 256 means). | NEW (same borderline class, multi-output twist) |
| SmoothHess: ReLU Network Feature Interactions via Stein's Lemma | 2023, arXiv:2311.00858 | Published precedent of Stein's lemma applied to ReLU nets: grad^2(f * phi_sigma)(x) = E[f(x+Z)(ZZ^T - sigma^2 I)]/sigma^4 estimated by sampling. Aimed at interpretability; no FLOP advantage for mean estimation. | IRRELEVANT as estimator; identity precedent |
| Müller et al. — Neural Control Variates | 2020, ACM TOG (consensus id 2666d9b1) | Unbiased NN-parameterized CVs; training cost inside a metered budget is fatal. | VARIANT/IRRELEVANT (metered FLOPs) |
| Malliavin–Stein literature (e.g. arXiv:1812.02703) | — | CLT/bounds machinery, not estimators. | IRRELEVANT |
| Uncertainty propagation through trained MLPs: exact analytical results | 2026, arXiv:2601.16830 | Closed-form layerwise moments via 1D/2D Gaussian integrals — a Gaussian closure. | VARIANT (closed: moment closure) |

**Q3 verdicts: kink-surface/Crofton estimator = NEW MECHANISM CLASS (no publication found applying it to network-mean estimation — checked "Crofton ReLU", "surface measure piecewise linear integration by parts estimator", conic/stereology angles). Control functionals = NEW (borderline), gated on dimension.**

### Cheapest response-free falsifiers
- **Kink-surface:** width-16 depth-4 bias-free net; enumerate breakpoints exactly along ~200 random lines (1D PL propagation); check the identity E[f] = kink-surface integral against dense MC to float precision; then measure estimator variance per FLOP vs plain MC at width 64. Kill if identity fails or variance/FLOP is worse at width 64 (it will only improve with structure exploitation, so a loss at 64 with no ideas is decisive).
- **Control functionals:** reuse an existing champion sample set on a width-64 depth-8 net, add backprop gradients (~2x FLOPs), fit a spherical-kernel CF on 512 points, measure variance reduction on held-out points. Kill if reduction < 2x (net-zero after the gradient surcharge).

---

## Q4 — ARC / WhestBench competition ecosystem

**Bottom line: the ecosystem is exactly one companion paper + ARC blog lineage + AIcrowd forum. The organizers' method family (cumulant propagation) is inside our closed list; the useful content is competitive intel and their published error scalings.**

| Item | ID | Relevance |
|---|---|---|
| Wu, Lecomte, Winer, Robinson, Hilton, Christiano — Estimating the expected output of wide random MLPs more efficiently than sampling | 2026, arXiv:2605.05179 (v2 May 14) | THE companion paper. Propagates cumulants (through factorized 3rd order) + Hermite expansions layerwise; MSE beats MC by ~factor-n (width) for wide nets: runtime O(n/eps^2) vs MC Theta(n^2/eps^2); explicitly admits "the dependence of our algorithms on depth is worse" (their Appendix D) — depth 32 is chosen to break them. Biggest advantage in distribution tails. | VARIANT (moment closure — closed for us); read App. D for their depth-error mechanics |
| ARC blog — Mechanistic estimation for wide random MLPs | 2026, alignment.org | Plain-language version of the above + future directions: auxiliary "advice", structured weight distributions. | VARIANT |
| Announcing the ARC White-Box Estimation Challenge | 2026, LessWrong Kben8CzS4awCwNw5c + alignment.org | Rules: Phase 1 depth 32 (raised from 8), budget 6.8e10 FLOPs, adjusted score = final_layer_mse x max(0.1, effective_compute/flop_budget). Organizers state top warm-up entries = cumulant-propagation variants + learned nets consuming cumulant features. | intel |
| Forum: Phase 1 write-up, submission #314695 — "Stabilizing cumulant propagation at depth 32: trajectory-calibrated moment chain" | 2026-07, discourse.aicrowd.com t/18097 | Best public competitor disclosure. DAgger-style per-layer linear corrections fitted on the chain's own rolled-forward trajectories (step-exact Edgeworth corrections from TRUE cumulants make it WORSE — the chain is an error-compensating dynamical system, ~16:1 bias-amplification:noise-attenuation). Raw MSE 5.89e-6, adjusted 1.77e-6 at ~7.4e10 FLOPs. Their own admissions: ~half their error is probe-sampling noise; "sampling wins Phase 1's raw metric"; covariance participation ratio contracts 128 -> 5.2 but noise concentrates in the signal subspace, capping analytic exploitation at ~2%. | VARIANT (moment closure + fitted corrector) — but calibrates the bar: a sampler below raw ~6e-6 at budget beats the best disclosed moment chain |
| Estimating Rare Events in Language Models with Proper Evaluation | 2026, arXiv:2607.18454 | ARC-lineage follow-on aimed at LMs/tail events; different regime. | IRRELEVANT to Phase 1 |
| Forum: Flopscope v0.8.0 RC | 2026, discourse t/18025 | FLOP-metering tool update — watch for accounting changes that shift the design/sampling tradeoff. | logistics |

---

## Ranked NEW-mechanism shortlist

1. **Kink-surface / Crofton-transect estimator (Q3).** Exact identity E[f] = Gaussian-weighted integral of gradient jumps over the (conical) kink set, via Euler + Stein. Unpublished for this use; different error law than point sampling (breaks the chi^2_1 speckle structure, so it can COMBINE with the champion rather than compete); cost anchored by Hanin–Rolnick linear-in-neurons transect complexity. Highest novelty, moderate risk; falsifier is a half-day of local compute.
2. **Width-sketched two-level coupled correction (Q2).** Mature theory (MFMC + Rhee–Glynn debiasing), unbiased by construction, convergent fidelity axis. Lives or dies on measured rho at honest cost ratio — the S8 depth-5 numbers already fail the MFMC formula (gain ~1.0x), so only the sketch axis is live. Falsifier is a few hours.
3. **Multi-output Stein control functionals (Q3, borderline).** Function-adapted (not fixed-basis, so arguably outside the closed harmonic-CV family); vector-valued kernels amortize one fit across all 256 output neurons; gated on kernel methods surviving d~255 spherical geometry. Cheap falsifier since it reuses existing samples + gradients.

Q1 returned no viable new class (exact-integration machinery is exponential-in-depth or #P-hard; the conic-intrinsic-volume thread has no composition rule in any literature).
