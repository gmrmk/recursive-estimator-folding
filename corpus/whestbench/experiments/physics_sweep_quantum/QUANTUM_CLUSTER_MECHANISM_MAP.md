# Quantum cluster — mechanism cartography (read-only sweep, 2026-08-10)

Scope: Landau levels; Bloch functions / band structure; wave packets in a
lattice; quantum tunnelling (delta-lattice, double-barrier resonance, barrier
penetration); the TDSE evolution operator.

Firewall honoured: no estimator/m245 execution, no measurement, no git, no
network, no submission. Every number below is quoted from a committed record
(`corpus/whestbench/headroom/fold_ledger.json`, 265 candidates) or a committed
source file. Nothing here was run.

Verdict tally: 12 mechanisms mapped — 7 ALREADY-KILLED, 3 FORBIDDEN-BY-THEOREM,
2 ALREADY-IN-CHAMPION, 0 UNTESTED SURVIVORS.

---

## 1. The one new result this sweep produces (derivation, not measurement)

**The entire fixed-direction re-weighting axis is closed by a two-line proof
from S6's already-measured fingerprint.**

S6 (`s6_bloch_design_bragg_spectrum`, killed) measured the degree-4 quadrature
error operator of the frozen Kerdock design exactly:

- inner-product fingerprint EXACTLY `{0 within-frame, +/-1/16 cross-frame}`;
- spectrum EXACTLY three shells: constant mode `7.296e-7` (x1), mid
  `3.16034e-5` (x125), bulk `3.09951e-5` (x32,130);
- identity `(1/N^2) sum G_4 = lambda_top`.

Two consequences that the record states as anatomy but never states as a
prohibition:

**(a) The three shells are named subspaces.** The design is 126 frames x 256
directions = 32,256 lines. `1 + 125 + 32,130 = 32,256`, and the multiplicities
match the only natural decomposition: constant (1) + **frame-contrast (125)** +
within-frame (32,130). The 125-fold mid shell *is* the space of per-frame
re-weightings.

**(b) Uniform weights are the constrained minimiser at every degree.** For even
`l`, `G_l[i,j] = P_l(x_i . x_j)` is a Gram matrix by the addition theorem, so
`G_l >= 0`. S6's fingerprint is the same seen from every point (255 within-frame
at 0, 32,000 cross-frame at +/-1/16), so `G_l` has constant row sums and the
all-ones vector is an eigenvector. Write any admissible weight vector as
`w = u + delta` with `u` uniform and `1^T delta = 0`. The cross term vanishes
(`delta^T G_l u = lambda_c (1^T delta)/N = 0`), so

```
Q_l(w) = w^T G_l w = Q_l(u) + delta^T G_l delta  >=  Q_l(u).
```

No signed, negative, per-frame, or per-point re-weighting of the frozen
directions can reduce the quadrature error at any degree. The inequality is
unconditional and needs no assumption about which shell is smallest — it holds
at degree 6 as well, where the constant mode is *unsuppressed* (S6: 1.015).

Magnitudes attached: a per-frame perturbation lands in the 125-shell at
`3.16034e-5`, i.e. **43.3x** the constant mode's `7.296e-7`; a per-point
perturbation lands in the bulk at **42.5x**. This retroactively derives six
independent empirical kills (`m192`/`m193`/`m194`/`m195`/`m197` frame GLS and
`s2` paid-information rotation weighting) and prices the rival's external
"<= 6.29% with negative weights" ceiling (`gen8_rival_5design_adjudication`) as
loose by construction.

---

## 2. Concept-by-concept

### 2.1 Landau levels

Three distinct sharp mechanisms; all closed.

| # | mechanism | verdict | evidence |
|---|---|---|---|
| L1 | Degenerate-level **edge localisation**: build a control/frame supported on the ReLU kink set, where a hugely degenerate harmonic level's realised states should concentrate. | ALREADY-KILLED | `s5_landau_kink_concentration_premise`: pooled near/far decile energy ratio **0.978-1.007** vs a 3x pass bar and 1.5x kill bar; `|rho| < 0.01` (null s.e. 0.0039); sign-inconsistent across nets; positive control **849-883x** proves the instrument could see. 64,512 dirs x 3 nets. |
| L2 | **Degeneracy splitting by re-weighting**: replace equal weights on the 64,512 directions with a signed/negative weight vector that zeroes the degree-4 form. | FORBIDDEN-BY-THEOREM | Section 1 above, from `s6` (`G_l >= 0`, uniform is the constrained minimiser); corroborated by `m180_design_strength_g0` (every design mutation **1.1962-1.4879x worse**) and `gen8_rival_5design_adjudication` (Kerdock within 0.0233% of optimal among positive-weight fixed rules). |
| L3 | The **256 output neurons as a degenerate multiplet**; split it by cross-output GLS / shrinkage on the shared hidden state. | ALREADY-KILLED | `m193_analytic_anchor_frame_gls`, `m194_independent_pilot_block_gls`, `m195_symmetric_half_design_attenuation`, `m197_crossed_three_rotation_u_statistic` all killed; `m192` is oracle-only; `m84`, `m79`, `cross_output_centroid_body_tomography` killed. Mechanism: `s7` coherence plateau `c32(0)=0.9747`, **~1.5-2 effective dof of 256** — the multiplet is near-degenerate precisely because there is nothing independent to shrink toward. |

### 2.2 Bloch functions and band structure

| # | mechanism | verdict | evidence |
|---|---|---|---|
| B1 | **Bloch on the sphere**: the design is a group-orbit crystal; Delsarte duality confines quadrature failure to aliasing (Bragg) modes of the dual code, giving a tractable design-side CV subspace. | ALREADY-KILLED | `s6_bloch_design_bragg_spectrum`: top-100 eigenvalues carry **0.32%** of `tr(D^2)` vs a 5% kill bar; participation rank **32,266 ~ N** — maximally flat, no Bragg peaks. |
| B2 | **Bloch in depth**: treat the 32-layer stack as a 1-D crystal, diagonalise a repeated transfer matrix, work in a band basis. | FORBIDDEN — no periodicity exists | Bloch's theorem needs a discrete translation symmetry of the generator. `W_1..W_32` are independent He draws and the effective map is `W_1 D_1(u) W_2 D_2(u) ...` with direction-dependent gates. Stated in the corpus: `resources/research_excursions/CYMATIC_PHYSICS_HARMONIC_MUTATIONS_20260807.md:143-152` — "There is no fixed normal-mode basis or repeated transfer matrix across depth"; `experiments/EQUIVARIANT_FEATURE_GRAPH.md:327` — "the feed-forward depth axis is not periodic". The only depth-stationary object is *statistical*: transmission **0.87/layer** (`s8`, measured 0.869/0.879/0.876) and **0.890** (`s12`, derived from the Jakub-Nica flow, within 2.4%) — both already flagged "NO estimator arm from this alone". A band basis would also be a low-dimensional invariant subspace of the residual, separately forbidden by S6's flatness. |
| B3 | **Bloch on the frame index**: twist the shared Haar rotation along the Kerdock phase index `s=2..127` (a quasi-momentum), preserving inter-frame coherence to first order. | FORBIDDEN + ALREADY-KILLED | The twist destroys the exact `+/-1/16` fingerprint, which S6 identifies as the *sole* source of the 42x constant-mode suppression; and any frame-index-dependent modification is a 125-shell perturbation (section 1). Measured instance: `m180` arm D (per-frame orthogonal remix) **1.4194x worse**; arms C k=2/4/8 **1.2801/1.1962/1.4879x worse**. |

### 2.3 Quantum wave packets in a lattice

| # | mechanism | verdict | evidence |
|---|---|---|---|
| W1 | Probe direction as a wave packet in the weight crystal; the arccos-kernel dispersion predicts the residual's angular correlation length `xi`; design spacing vs `xi` decides redundancy. | ALREADY-MEASURED, LEVER EXPLICITLY ABSENT | `s7_wavepacket_speckle_correlation` (screened, PASS as physics): `xi` **36.98/35.60/45.95 deg** vs mean-field 20.91 (ratios 1.77/1.70/2.20); chi^2_1 speckle fits (KS **0.007-0.016** at n=64,512), Exp(1) rejected; Kerdock minimum angle `arccos(1/16) = 86.42 deg` ~ **2x above** `xi`, so every design point is an independent draw. Record states plainly: "No new estimator lever opens (independence = nothing between points to exploit)". Finite-width offset since derived by `s12` (1.577-1.868, brackets the measurement). |
| W2 | **Coherent-state / needlet frame**: replace the global design with a spatially localised minimum-uncertainty frame (localised in angle and in degree simultaneously). | FORBIDDEN — the field is homogeneous | Localisation only pays on a spatially structured integrand. Three independent blindness results say the residual has no spatial structure: kink-blind (`s5`, ratio ~1.00), covariate-blind (`s15`, best out-of-sample incremental R^2 **1.56%** vs a 5% kill bar), harmonic-dispersed (`m191_harmonic_cv_g0b`, **+0.83%** vs a 10% bar, basis R^2 0.23-0.29%). Prior instances already killed: `strict_band_boundary_ridgelet_control`, `m108_heat_difference_scaled_harmonic_band`, `m108_centered_cymatic_band_energy`. |

### 2.4 Quantum tunnelling

| # | mechanism | verdict | evidence |
|---|---|---|---|
| T1 | **Barrier penetration**: classify each ReLU gate as fully reflecting (dead), transparent (always-on) or partial (kink), and treat the transparent and reflecting ones exactly. | ALREADY-IN-CHAMPION, extension ALREADY-KILLED | Champion source `corpus/whestbench/experiments/fold3_estimator.py:1-7` — "dead columns vanish, always-on columns remain linear and are algebraically composed into the next weight matrix, and kink columns retain their ReLU" (the three-terminal-layer fold), plus pilot-rescued structural pruning. Extension upward: `m184_trichotomy_upward_g0` **KILLED at 0.00% on all three nets** — certain-on neurons are **zero at layers 1-9**, peak 39/~185 at layer 28 against a break-even of ~85-95; certain-dead increment exactly 0 because v3's pruning is a strict superset (asserted on all 84 layer instances); still 0.00% under illegally lax thresholds alpha>5/4/3. |
| T2 | **Exponential tail / WKB amplitude**: importance-sample the rare firing directions of a nearly-dead output neuron, since the tunnelling amplitude is exponentially small. | NO PRECISE MECHANISM — the premise is false, and the operator it would imply is forbidden | For a bias-free He net the final pre-activation has mean ~0 and O(1) scale, so `E[ReLU(z)]` is bulk-dominated with transmission ~1/2, not exponentially small: there is no barrier to tunnel through and no WKB exponent to expand. The estimator it would imply (non-uniform direction weighting) destroys the exact 2-design annihilation of degrees <= 2 (a certified **2.02x** pillar) and is separately forbidden by section 1; and there is no observable to steer on (`s2` pooled `|rho| = 0.122` vs a 0.4 gate; `p2b`, `gen3_p2` same family, three independent closures). |
| T3 | **Delta-potential lattice**: the kink hyperplanes are literal delta scatterers — the distributional Laplacian of a CPWL function is a signed measure on the kink set; integrate over that measure. | ALREADY-KILLED (mathematics preserved) | `m86_boundary_laplace_coarea`: Phase A exact to **3.33e-16** relative, but Phase B enumeration lower bound **1.24e86 FLOPs** against a 2.72e11 budget. `s9_crofton_kink_transect_identity`: the Euler x Stein surface identity verified to **1.3e-12** with four closed-form anchors, then the estimator killed at **176,860x geomean worse** variance-per-FLOP (3 orders past a 100x kill line); combination hatch measured shut (error laws independent, pooled r 0.055, inverse-variance gain **0.3%**). Also `m95_palm_coarea_sampler`, `m88`/`m89` great-circle RB, `m202_signed_facet_smc_no_go`, `direction_only_facet_raoblackwell` — all killed. The "lattice" half additionally fails: 256 independent He hyperplanes are not a periodic array, so no band gap forms. |
| T4 | **Double-barrier resonant tunnelling**: couple two stages so that a quasi-bound intermediate gives near-unity transmission — i.e. cross the closure plateau (9.6e-5) to the sampling line (2.818e-7) by a two-level control-variate / MFMC resonance. | ALREADY-KILLED, saturated on all four axes | The resonance condition *is* the MFMC correlation threshold, and it has been measured every way: depth fidelity `s10_mlmc_depth_increment_variance` gain **0.056x** geomean (Rhee-Glynn 0.010x; break-even needs rho ~0.53/layer); width fidelity `s13_width_pooled_mfmc_premise` gain **0.9552x** with rho **0.071-0.176** against **0.489** required; closure as predictor `t2` **9.6055e-5**, 46x over the kill boundary; closure as CV `n5` and as smoother `m181` arm 3 ratio **1.057** with lambda collapsed to ~0; closure as corrector `n8c` bias share **-0.034** (CI entirely below the 0.25 line). Mechanism of death, stated by S13: any cheapened copy loses the exact-weight fingerprint and decorrelates — there is no quasi-bound state to resonate with. |

### 2.5 The TDSE as an evolution operator

| # | mechanism | verdict | evidence |
|---|---|---|---|
| E1 | Depth = time; realised weights = background + defect; residual = Dyson/Born series of per-layer defect scatterings; first-Born inhomogeneous forward tangent on a frozen background. | ALREADY-IN-CHAMPION (first order) + ALREADY-KILLED (beyond) | This is literally the M121-M136 carrier program (`m125b_source_batched_forward_tangent` = first Born on a frozen Gaussian background; `m128_second_order_cumulant_response` = Edgeworth order two). The champion carries the surviving first-order piece as the frozen moment-tangent control, lambda **0.9807112198896164**. On the Kerdock frames it is worth **+2.14%** against a 10% bar (`n9_kerdock_composition_interaction`), with a derived `cov^2/(var_i var_corr)` ceiling of **1.9-3.7%** proving no lambda clears the bar — the positive control (identical code on iid sampling at n=14,000) gives **+34.5%**, i.e. the frames already absorb the first-layer residual. |
| E2 | Layer-resolved defect susceptibility profile (which quench carries the residual). | ALREADY-KILLED AS A MODEL, structure preserved | `s8_tdse_layer_defect_profile`: predeclared mean-field gate failed 3/3 (max deviation **21-31x**), but the profile is coherent and near-geometric — transmission **0.869/0.879/0.876**, ~95x span layer 0 to 31; top-5 layers (0-3 plus one of 4/5) carry **0.409-0.511** of residual variance; last-3 layers carry **0.0054**. Record states: "NO estimator arm from this alone". |
| E3 | **Unitarity / conservation law** as a free exact control (the TDSE's defining invariant). | ALREADY-KILLED, twice, by algebra | `s9`: Euler's identity `x . grad f = f` is exact for bias-free ReLU nets — but as a control on already-paid forwards its difference from the target is identically zero, i.e. zero-variance and zero-information; the only non-degenerate realisation (Crofton transects) is the 176,860x kill above. `s16_residual_norm_decomposition_confirm`: the `ReLU(z) = z/2 + |z|/2` conservation split is **bit-exactly** the promoted antipodal pairing (deviation 0.0 on 8.26M entries/net x 3; MSE ratio 1.000000) — an identity, not a lever. |

---

## 3. Untested survivors

**None.** Every mechanism this cluster produces is already killed, already in the
champion, or forbidden by S5 (kink-blindness), S6 (degree-4 flatness plus the
weighting theorem of section 1), S7 (independent chi^2_1 speckle at 2x the
design spacing), S13/S10 (fidelity decorrelation), or the absence of any
periodic structure in the depth axis.

The cluster contributes one theorem and no lever. It does **not** open a
seed-side mechanism: the only seed-side object it names — the exact per-layer
defect source on a frozen background — is the M243/M245 carrier program, which
is already the named frontier and is held two-key.
