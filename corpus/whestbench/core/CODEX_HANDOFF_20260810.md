# Codex handoff — full state and mathematical texture (2026-08-10 -> 11)

Written by opus-5 (acting /root) for codex-sol. Companion file:
`CODEX_ULTRAPLAN_20260810.md` is the forward work program — read this for the
mathematics, that for what to do with it.

**Seat:** Fable 5 hit its usage window mid-campaign; Opus 5 took the
orchestrator seat under `OPUS5_HANDOFF_20260810.md`. You reclaim /root at any
time with your own append-only channel entry.

**Where things stand in one paragraph.** Phase 1 closed 2026-08-10 23:59 UTC.
The Algorithmic Contribution write-up is FILED on both channels (private PDF to
arc-whestbench@aicrowd.com against graded ID #326094, verified in Sent; public
tact-scoped companion at Discourse topic 18147). Selection is EXECUTED and
reload-verified: slots #326094 + #327519, changeable until 2026-08-11 23:59 UTC
but with nothing better to swap in. Prize rankings come exclusively from the
private re-evaluation on fresh seeds, Sep 20-30. Phase 2 opens 2026-08-18.
The fold ledger stands at 264 records; kills remain final. Twenty adversarial
agents failed to beat the champion, and the four defects found today were all
in our OWN record, not in the estimator.

**Evidence levels** used throughout: [O] observed in a committed run, [D]
derived with arithmetic shown, [R] reported by an artifact and not re-derived.

**Sections below were each written by a separate Opus-5 specialist reading the
committed record, with instructions to flag anything they could not trace. 649
numbers were traced to artifacts. Their unverifiable flags are reproduced in the
final section — read them; three found real defects.**

---

## The geometry and the theorem

Evidence levels follow the corpus discipline: **[O]** observed in a committed run, **[D]** derived by arithmetic shown here, **[R]** reported by a committed artifact and not re-derived. Every number below is either quoted from a named artifact or carries its arithmetic inline. Two defects in the record surfaced while tracing; they are flagged in §G.9 rather than buried.

---

### G.1 The champion's design algebra

The frozen sampling asset is 126 phased-Hadamard (Kerdock) frames x 256 rows = **32,256 lines** on S^255, each at exact radius `mean_chi(256) = 15.98438266660853`, antipodally doubled to **64,512** evaluation points [O, `experiments/s5_kink_concentration/`, `s15_results.json`, `s18_results.json` config `n_full=64512`]. Identification: this is 126 of the 129 real mutually unbiased bases of the Calderbank–Cameron–Kantor–Seidel extremal line-set in R^256 [R + D, `sources/research_designs_quadrature_20260810.md` §0].

The entire geometry is fixed by one exact census. S6 enumerated all 32,256^2 ordered pairs — not a sample — and because the unit-vector entries are dyadic (+-1/16), every f64 inner product is bitwise exact. Max deviation from the k/256 grid: **0.0** [O, `s6_results.json.fingerprint.max_grid_dev`].

| shell | value | multiplicity | share | location |
|---|---|---|---|---|
| diagonal | 1 | 32,256 | — | self |
| within-frame off-diagonal | 0 | 8,225,280 = N x 255 | — | orthonormal frames |
| cross-frame | +1/16 | 548,352,000 | 17/32 = 53.125% | MUB |
| cross-frame | -1/16 | 483,840,000 | 15/32 = 46.875% | MUB |

Census check [D]: 32,256 + 8,225,280 + 548,352,000 + 483,840,000 = 1,040,449,536 = 32,256^2, closed. Cross-frame pair count = N(N - 256) = 32,256 x 32,000 = 1,032,192,000, of which the +1/16 share is exactly 17/32 and the -1/16 share exactly 15/32 — a sign imbalance of exactly 1/16 of the cross mass.

**Exactly three off-diagonal values.** Within a frame the inner product is 0 (orthonormal basis); across frames it is +-1/sqrt(256) = +-1/16 (mutual unbiasedness). That is the whole angle set.

**Minimum angle** = arccos(1/16) = **86.41667830152804 deg**; 90.00 deg within a frame; antipodal doubling adds no closer pair [O, `s7_results.json.min_angle_deg` = 86.41667830152804, measured on the rebuilt set, frames 0–5 spot check].

**Why it is an exact spherical 2-design** [D]. Each frame U_f is a 256x256 orthogonal matrix, so sum over its rows of u u^T = U_f^T U_f = I_256 exactly. Averaging over the 126 frames, (1/32,256) sum_i u_i u_i^T = (126/32,256) I = I/256 = I/d, exactly, in exact arithmetic and independent of any floating-point path. Odd degrees vanish identically under antipodal doubling (phi(-x) = -phi(x) for odd harmonics), so degrees 1, 3, 5 are structurally zero. The corroborating measurement is `m191_g0a_results.json`: deg-1 / deg-3 / deg-5 design_rms **exactly 0.0** on all three rotations; deg-2 design_rms **8.592e-9 / 7.642e-9 / 8.972e-9** against an iid_rms of 3.937e-3, i.e. ratio ~2.2e-6 — float roundoff on a structurally exact null [O]. Note the discrepancy with the brief I was handed: no artifact in the corpus reports the second-moment residual `(1/N) sum u u^T - I/d` at all, let alone "0.0 bitwise." The exactness is real and derivable; the bitwise measurement does not exist. See §G.9.

`m180_design_strength` is the empirical counterpart: every predeclared mutation of this geometry at matched n = 64,512 raised variance — MUB mix +31.3%, coset stratification k=2/4/8 at +28.0% / +19.6% / +48.8%, per-frame rotation remix +41.9%, geomean ratios 1.3135 / 1.2801 / 1.1962 / 1.4879 / 1.4194 [O, `m180_g0_results.json`]. The strength lives in the mutual unbiasedness of all 126 frames under **one** shared rotation.

---

### G.2 The degree-4 error operator: three shells, one suppressed mode

Setting [O, `S6_VERDICT.md` §Normalization]: H_l on S^255, alpha = (d-2)/2 = 127; reproducing kernel Z_l(x,y) = m_l G_l(<x,y>), G_l(t) = C_l^(alpha)(t)/C_l^(alpha)(1); phi(x) = Z_4(x,.)/sqrt(m_4) so ||phi|| = 1; A = (1/N) sum phi phi^T with tr A = 1 exactly; D = A - I/m. Constants, all exact-rational and cross-checked: dim H_4 = **183,148,480**, dim H_6 = **414,173,091,136**, C_4^(127)(t) = 181,742,080 t^4 - 4,194,048 t^2 + 8,128, C_4^(127)(1) = 177,556,160. The exact-rational identities E[G_l] = 0 and m_l E[G_l^2] = 1 hold in `Fraction` arithmetic for l = 4, 6.

Because the inner-product structure has exactly three values, the Gram kernel factors as K = (1-g_0) I + (g_0-g_1) F F^T + g_1 11^T with F the frame-indicator matrix, giving A exactly three eigenvalue shells in closed form [D from the verified structure, O by subsample eigensolve]:

| shell of D | eigenvalue | multiplicity | reading |
|---|---|---|---|
| mid | 3.1603445214882744e-05 | 125 = frames - 1 | frame-contrast modes, +1.963% over bulk |
| bulk | 3.0995104896346116e-05 | 32,130 | generic design-span modes, ~1/N |
| top-1 | 7.296307693574504e-07 | 1 | the quadrature functional itself |
| sea | -5.460050774104158e-09 = -1/m | 183,116,224 | orthocomplement of the design span |

Suppression ratio [D]: 3.0995104896346116e-05 / 7.296307693574504e-07 = **42.4805**. Mid/bulk = 1.01963. Multiplicity check: 125 + 32,130 + 1 = 32,256 = N.

The mechanism of the suppression is a three-term cancellation, and I reproduced it from the census [D]. lambda_top = (1/N^2) sum_{j,k} G_4(t_jk) = S1/N^2 with

S1 = 32,256 x G_4(1) + 8,225,280 x G_4(0) + 1,032,192,000 x G_4(1/16)
   = 32,256.000000 + 376.529183 - 31,867.704280
   = **764.8249027237362**

reproducing `s6_results.json.deg4.S1_sum_G4` = 764.8249027237362 to all printed digits (the artifact's own closed-form cross-check sits at rel. diff 1.04e-15). Hence lambda_top = 764.8249027237362 / 32,256^2 = 7.3509082e-07, and mu_top = lambda_top - 1/m = 7.296307693574504e-07. The Haar-H_4 design/iid RMS is sqrt(N lambda_top) = sqrt(0.0237110895) = **0.15398405597386844**, matching `haar_H4_design_over_iid_rms` = 0.15398405597386836 [D vs O].

**Flatness.** tr(D^2) = **3.09974863e-05**, computed two independent ways — exact pairwise sum 3.099748626998932e-05 vs exact-rational closed form 3.099748626991116e-05, relative difference **2.52e-12** [O]. Top-k concentration (full-N closed form): k=1 -> 3.222e-5, k=10 -> 3.222e-4, k=100 -> **0.0032221249837913308**, k=1000 -> 0.03115. The top-100 eigenvalues carry **0.32%** of tr(D^2), i.e. 99.678% sits in the bulk shelf; the predeclared PASS bar was >= 50% and the KILL bar < 5%. Participation rank tr(D^2)^2/tr(D^4) = **32,266.169565128537**, which is N x 1.0003153 [D]. A structure-agnostic 16,000-direction dense f32 eigensolve (seed 20260809) reproduces the closed-form sorted multiset to max abs error **3.55e-12** and observes the suppressed constant mode directly at 3.223399817943573e-05 against predicted 3.22340013645334e-05 [O].

**The tuning stops at degree 4.** The same run at l = 6: tr(D_6^2) = 3.10019826e-05 (pairwise vs closed form rel. 8.06e-13), shells bulk 3.1002009e-05 x 32,130, mid 3.0987428e-05 x 125, top-1 **3.1940888e-05** x 1 — the constant mode is *not* suppressed; N lambda_top = 1.0303 and design/iid RMS = **1.0150297289025836**, iid-level. I reproduced S1_6 = 32,256 - 7.269e0 + 984.15e0 = 33,232.88426753602 against the recorded 33,232.88426753603 [D vs O]. That single sign flip in G_6(1/16) (+9.5346e-07 vs G_4's -3.0874e-05) is the whole story: the +-1/16 phase cancellation is a degree-4 resonance and nothing else. It derives, from pure code structure, M191's measured degree split — deg-4 design/iid 0.10668 / 0.10719 / 0.09829 versus deg-6 0.3475 / 0.4109 / 0.4329, with S6's own direct recompute at 0.10744 (deg 4) / 0.39423 (deg 6) and its spectral prediction at 0.10778 / 0.40340 [O + R].

---

### G.3 The degree-4 boundary, and why the residual has to live there

The boundary is a counting fact, not a measurement. The Delsarte–Goethals–Seidel bound for an antipodal spherical 4-design (hence 5-design) in d = 256 is

N >= 2 C(257,2) = 257 x 256 = **65,792** = d(d+1)   [D; arithmetic re-run here, matching `sources/research_designs_quadrature_20260810.md` Q2]

Our set has 64,512 points. The deficit is exactly **1,280 points = 1.984%** of N [D]. Consequences, both in the record:

1. **No weighting rescues it.** Positive-weight cubature of degree 5 in d = 256 still needs >= ~65,792 nodes (Moller's symmetric-measure form gives d^2+d+1 = 65,793); 64,512 < 65,792, so no reweighting of the 126 frames achieves exact degree 4 [D + R, §Q3.1]. On a transitive automorphism group the optimal weights are uniform anyway (averaging any weight vector over Aut(X) cannot increase a convex Aut-invariant error functional) [D, §Q3.2].
2. **No larger exactness is reachable at this N.** Exact degree 6 needs ~2,861,952 points (antipodal-7 form 5,658,112); the minimal real Clifford orbit in R^256 — a 7-design — has 162,569,721,600 lines = 3.25e11 points, 5.0e6 x our budget [R + D, §Q2]. At N <= 1e5 the maximum achievable exact strength is t = 5.

So the design is pinned: everything of degree <= 2 is annihilated exactly and contributes zero estimator variance; degree 4 cannot be annihilated at this point count; and the degree-4 deficiency that remains is delocalised over the whole design span with participation rank ~ N and no low-rank handle. Degree 6 is at iid level. The residual therefore lives at degree >= 4, and at degree 4 it lives everywhere at once. Any correction that is not itself ~N-dimensional cannot bite — which is the mechanical content of S6's KILL of the low-rank-correction hypothesis.

Scale, corrected: N / dim H_4 = 32,256 / 183,148,480 = **1.7612e-4** — the design span is roughly one part in 5,678 of the degree-4 space [D]. (P1 §Pillar 1 prints 5.6e-3 here; see §G.9.)

---

### G.4 The rival adjudication, at depth

Topic 18145 (skye_nygaard) published a fixed spherical 5-design of **66,048** Kerdock-based directions with 8 Walsh–Hadamard passes, at ~1.55e-7 public against our 1.832e-7. Adjudicated in `core/GEN8_FORUM_INTELLIGENCE_20260810.md` §2 and ledger record `gen8_rival_5design_adjudication` (status `killed`, 264 records total in `headroom/fold_ledger.json`).

**Their strength claim is true, and near-tight.** 66,048 = d(d+2) = 256 x 258 = 2 x 33,024 = 2 x 129 x 256, i.e. the completed 129-frame real-MUB spread, antipodally doubled. Against the DGS floor of 65,792 the excess is 66,048/65,792 - 1 = **0.3891%** [D].

**The Welch/frame-potential identity, derived.** Per line of the 129-frame spread, the fourth-power inner-product sum is

self 1 + within-frame 255 x 0 + cross-frame 128 x 256 x (1/16)^4 = 1 + 32,768/65,536 = **3/2 exactly**

Summed over all N_L = 33,024 lines, the total ordered-pair fourth-moment sum is 33,024 x 1.5 = **49,536**, which decomposes as 33,024 (diagonal) + 16,512 (cross-frame) — the numbers quoted in the Gen-8 file. Normalising, 49,536 / 33,024^2 = **1/22,016 = 3/66,048 = 3/(d(d+2)) = 4.5421511627906976e-05** [D; every step re-run here]. Equality in the Welch bound is equivalent to the fourth-moment tensor matching Haar's, i.e. a projective 2-design in RP^255; an antipodal set with Haar fourth moments is a spherical 4-design, and every odd-degree integral of an antipodally symmetric set vanishes identically, so a spherical 4-design that is antipodally symmetric is automatically a **5-design** [D, §Q2 of the research brief]. That is the whole "4 implies 5" step: it is symmetry, not an extra condition.

**We had already built, verified and priced it.** S11 §2 ran the exact fourth-moment identity on the frozen asset with `verify_design.py`:

| set | per-line sum_j <v_i,v_j>^4 | Phi4 / Welch | degree-4 error |
|---|---|---|---|
| 126-frame Kerdock (frozen) | 1.48828125 | 1.015811 | present, 1.5811% excess |
| 129-frame completion | **1.5 exactly (min = max)** | **1.0000000000** | identically 0 |
| control: 126 + 3 random frames | 2.3304 (mean) | 1.55362 | inflated |

Both rows reproduce exactly under my own arithmetic [D]: for 126 frames, 1 + 125 x 256 x (1/16)^4 = 1 + 32,000/65,536 = 381/256 = 1.48828125; and Phi4/Welch = (381/256)/32,256 / (3/66,048) = 5461/5376 = **1.0158110119047619**, an excess of exactly 85/5376 = 1.5811%.

**The pricing.** Cost bills proportional to point count: C_129/C_126 = 66,048/64,512 = 1.0238095238095237, so under S = MSE x max(0.1, C/B) the completion must drop MSE by more than 1 - 64,512/66,048 = **2.32558%** to pay for itself. Regime confirmed metered, not floored: hosted #326094 adjusted 1.832e-7 with raw MSE 2.818e-7 gives C/B = **0.6501064584811923 > 0.1** [O, `s11_results.json`].

The measurement that matters is the point-count-matched one. Raw completion vs 126: panel ratio 0.9658071388257757, +3.42%, CI [0.9443, 0.9868]. A control adding **3 random frames** (same +1,536 points, degree-4 not zeroed — in fact inflated to Phi4/Welch 1.55362): 0.9675098153969259, +3.25%, CI [0.9465, 0.9891]. Degree-4 **isolated**, both arms at 66,048 points: ratio **0.9982401454289622**, +**0.17598545710377778%**, CI [0.9695, 1.0280], P(ratio < 1) = 0.5442 — indistinguishable from zero, and an upper bound because the control's own degree-4 error is inflated [O]. Independent corroboration from committed data: m191 `cv_deg4` direct control variate removed +0.42% of champion MSE; R^2_deg4 = 0.18–0.23% [O/R]. Against a 2.32558% bar, that is 13x under.

The rival's own posted ablation attributes their entire 1.5412x gain to arithmetic, "entirely because the second technique is cheaper" — not to directions. Their k^-1.21..1.24 direction-count exponent is confounded: it was measured while shrinking 129 -> 96/64/32, which destroys the design as it removes points; S11's point-count-matched control is exactly the clean version of that experiment and finds +3.25% (random) vs +3.42% (completing) against a +2.38% cost — statistically identical. Cost parity is measured, not assumed: their post-Strassen budget 64.27% against our C/B 65.01% [R]. Their raw 2.2819e-7 is on 100 self-chosen dev nets against our graded 50-public + 50-private, and C1 shows cross-suite offsets reaching 1.65x, so the raw comparison carries no information at the 10–20% level [R].

Net: the degree-4 axis is closed on both ends. Below 65,792 points exactness is impossible; at 66,048 points exactness is achievable and worth <= 0.176% against a 2.326% bar. Nobody in the sub-1e-7 tier is getting there by choosing better directions.

---

### G.5 The two exact identities

**S9 — the Crofton kink transect (Euler x Stein).** For a bias-free ReLU net, f is continuous, piecewise linear and positively 1-homogeneous, so on each activation cell x . grad f = f (Euler). Each partial derivative is piecewise constant on a conical fan, hence BV with distributional gradient supported on the kink set K, purely normal across each facet; the distributional Laplacian is the scalar surface measure Delta f = J H^{d-1}|_K with J = nu . (grad f^+ - grad f^-). Gaussian integration by parts for BV then gives the

**master identity: E[f(X)] = integral over K of J(x) phi_d(x) dH^{d-1}(x)**

with the network form J = c ||a||, a^T = (W_l)_{j,:} D_{l-1} W_{l-1} ... D_1 W_1 (upstream) and c = [wbar^T D_{L-1} W_{L-1} ... D_{l+1} W_{l+1}]_j (downstream). The Crofton projection formula plus isotropy (E_u |nu . u| = kappa_d, kappa_16 = 0.202610, kappa_64 = 0.100126) turns it into the unbiased line-transect estimator Ehat = kappa_d^{-1} sum_k phi_1(t_k) c_k ||a_k|| [D, `papers/P2_CROFTON_KINK_IDENTITY_20260810.md`, `S9_VERDICT.md` §1].

Verification, at machine precision and by two structurally distinct estimators [O]:
- per-interval affineness of F(t) between enumerated knots (a missed knot fails this): max relative violation **6.7e-16**;
- slope-jump identity Delta_s = c_k |a_k . u| at every knot: max relative violation **1.3e-12**;
- Euler residual max |x . grad f - f| = 1.1e-15 on the 3 predeclared seeds and **8.88e-15** on 20 fresh nets;
- E[f] agreement against 1e7-sample MC at z_comb = **0.08 / 0.23 / 0.72**; the independent 20-net leg gives pooled z mean -0.25, sd 0.92, max |z| 2.75, 20/20 within 3 sigma;
- four closed-form anchors (kappa_16, single neuron, |x_1|, depth-2 width-16) all pass.

Structural finding: the **full multi-layer** surface integral closes the identity; **first-layer-only does not**. Layer fractions [L1,L2,L3] = [0.49, 0.13, 0.38] (seed 202) and [0.17, 0.29, 0.54] (seed 303); the 20-net mean is [-0.54, 0.45, 1.09] with layer-1 share ranging over roughly [-5, +1.6]. Deeper facets dominate and carry either sign [O].

And the estimator is dead. Variance-per-FLOP ratio transect/MC, geomean **176,860x** (per-seed 181,779 / 157,818 / 192,838; bootstrap lower bounds 133,657 / 125,593 / 150,966) against a predeclared 100x kill line. Decomposition at seed 404: variance factor **196x**, cost factor **927x** — even a free oracle for all crossings and jumps leaves 196x, still fatal [D from the artifact's own factorisation; 196 x 927 = 181,692 recovers the 1.82e5 ratio]. The mechanism is signed-cancellation speckle: ~300 jump terms of magnitude O(0.1–1) per line cancelling to a mean of ~0.03. The combination hatch is measured shut: transect and MC errors are uncorrelated (pooled r = 0.055, n = 48, per-seed -0.02 / -0.01 / +0.17), so the inverse-variance gain is bounded by r^2 + 1/(1+R) = 0.003025 + 5.65e-6 = **0.30%** [D]. The independent second runner's leaner FLOP accounting gives 3.4e4–4.9e4x, ~3.7x below, on the same side of the gate by >= 340x.

**S16 — residual decomposition = antipodal symmetrization.** The layer-1 identity ReLU(W_1(r u)) + ReLU(W_1(r(-u))) == |W_1(r u)| holds with **max abs deviation exactly 0.0 over 8,257,536 entries per net** (= 32,256 base directions x 256 neurons), all three nets [O]. The second signal is the mechanism rather than a repeat: negation is exact in IEEE-754 round-to-nearest (`max_abs_neg_dev = 0.0` measured), and for any float x, max(x,0) + max(-x,0) == |x| bitwise because the ReLU pair is a clamp partition. So antipodal pairing cancels the odd half z/2 exactly and keeps only the even half |z|.

Full-estimator equivalence at matched billed samples (64,512 each): MSE ratio residual-split / champion = **1.000000** on every net (1.9972e-07 / 5.8721e-07 / 2.3692e-07), max final abs deviation **0.0** over all 48 (net, seed) 256-vectors [O]. The "residual/norm decomposition" is therefore not a lever; it is a re-derivation of what the champion already does. Its deep-reading — analytic linear part plus Gaussian corrections — is the M181/T2 closure family, whose one-step Gaussian closure sits at MSE 1.28e-6, **3.7x above** the sampling arm at 3.41e-7, bias-squared-dominated (bias share 0.67–0.78). And the linear part carries no signal at all: E[f_lin] = M^T E[x] = 0 exactly, confirmed by the rms of the MC mean decaying 2.29 / 2.90 / 1.60 (mean 2.26) when n goes 200k -> 800k against the 1/sqrt(n) prediction of 2.0. Form-1 reparametrization gives per-layer residual ratios R_l with min **1.108**, median 1.162, max 1.231 — every layer above 1, no near-identity anywhere, so no perturbative truncation exists [O].

---

### G.6 S18: the singleton-cell mechanism

Cell census, identical on all three nets: **all 64,512 directions occupy 64,512 DISTINCT first-layer activation cells** — every cell a singleton, max cell count 1, zero exact-zero preactivations, computed by a collision-free perfect hash (256 sign bits packed to 32 bytes, exact byte-row uniqueness) [O, `s18_results.json`]. This is the generic arrangement fact for 256 hyperplanes in R^256 at design spacing.

The consequence is structural, not statistical: a top-k "most frequent cell" indicator is 1 on at most one direction, so fitted on the training half it can memorize a single residual and can **never** activate on the held-out half. Cell-identity features are incapable of out-of-sample generalization here. The measurements confirm it mechanically — gated OOS incremental R^2 beyond S15's Base-B (633 columns): cells_k16 max 1.539e-05, cells_k64 max -7.6e-08, cells_k256 max -6.974e-05 (consistently negative, the overfit penalty of 256 no-signal indicators), hamming_modal_majority max 2.371e-05, hamming_modal_literal max 2.233e-05 — every one below the 2.63e-5 fitting-noise bar, none within an order of magnitude of the 1e-4 signal bar on any net. The permutation null (f shuffled across all 64,512 directions, 3 perms x 3 nets) spans |5.3e-5| to |1.4e-4| per set, so every gated value sits inside its own null. Instrument sensitivity was demonstrated, not assumed: an injected 1e-3 R^2 signal is recovered at 1.53e-3 / 0.89e-3 / 0.71e-3 [O]. The `active_count` control (excluded from the gate as an affine restatement of S15's C1 firing rate) reproduces S15's cached values to |diff| <= 8.8e-7, and the d1 reuse check gives max abs diff **0.0** against the saved S5 arrays.

Only aggregates (count, Hamming distance) can generalize, and those measure at fitting noise. That closes the arrangement-combinatorial family alongside the smooth one.

---

### G.7 The optics identification (added to P1 today)

P1 §"Interlude" upgrades "speckle" from metaphor to identification, at zero new measurement cost, by noting that standard speckle theory makes three sharp predictions and the committed data selects the predicted branch in all three [D over O].

1. **Which law.** Optics distinguishes a real, single-quadrature field (intensity chi^2_1) from a complex, two-quadrature field (intensity Exp(1) = chi^2_2). A depth-32 ReLU output field is real, so chi^2_1 is named in advance. Measured on the actual 64,512-point Kerdock design: KS(chi^2_1) = **0.009857285778166025 / 0.00903263919889108 / 0.007147975690644182** against KS(Exp(1)) = **0.16354602400155832 / 0.16492274030232534 / 0.1642707435175949**. Ratios [D]: 16.59 / 18.26 / 22.98, mean **19.3** — P1's "roughly 18x" is a fair, slightly conservative rounding. Independent n = 4,000 Haar probe agrees (chi^2_1 0.016 / 0.015 / 0.009 vs Exp(1) 0.162 / 0.160 / 0.170). Moment shape k = 1/var(e) = 0.41 / 0.42 / 0.44 against chi^2_1's 0.5 and Exp(1)'s 1.0.
2. **The sampling criterion.** Decorrelated sampling requires a pitch beyond one grain. Measured angular correlation length (half height) xi = **36.98 / 35.60 / 45.95 deg**, bootstrap CIs [32.9, 45.0] / [32.2, 40.6] / [40.0, 49.5]; the design's minimum angle is 86.41667830152804 deg, i.e. pitch/grain = **2.34 / 2.43 / 1.88** [D]. The consequence is then verified independently at the design's own inner products: S17 measures c(0) = -1.2721e-3 / -1.2885e-3 / -1.3492e-3 at 90 deg and c_even(+-1/16) = -5.468e-6 / -5.337e-6 / -4.853e-6 at 86.42 deg — both ~0 [O].
3. **The sign of the finite-size correction.** In optics a finite aperture yields a *larger* grain than the infinite-aperture limit. Here the aperture is the finite-width coherence cone: the depth-32 mean-field plateau c_32(0) = **0.9747204751243136**, with vector-energy shape k_eff ~ 0.77–1.02 implying ~1.5–2 effective independent neuron amplitudes out of 256. The measured xi runs **1.7681 / 1.7025 / 2.1975** times the infinite-width mean-field value of **20.91 deg** — high on all three nets, which S7's own artifact reads independently as "a systematic finite-width offset, not scatter." The offset has the sign the aperture picture requires.

The mean-field kernel is itself doubly verified: c_{l+1} = f(c_l) with f(c) = (sqrt(1-c^2) + c(pi - arccos c))/pi, iterated 32 times, cross-checked against an arcsin-identity re-implementation to **3.3e-16** and against a 2e6-sample Monte Carlo to <= 1.4e-3 [O].

What the identification buys, precisely: the chi^2_1 maximum-entropy law, the design pitch, and the finite-width offset stop being three coincidences and become one phenomenon. Extracting a coherent signal from fully-developed speckle requires resolving below the grain, and the grain here is the aperture of the network itself. It also lines up with the floor: S17's field variance sigma^2 = 7.900e-3 / 1.600e-2 / 1.112e-2 gives N_eff = sigma^2/champ = **39,558 / 27,251 / 46,955**, pooled ~38k independent cells out of 64,512 evaluations (~60%), and champion/floor = **1.79** cost-matched, **0.90** on distinct directions. The doubled inner-product census used there is exact: the five shells sum to 4,161,798,144 = 64,512^2 bitwise, and the +-1/16 shells come out **exactly equal** (2,064,384,000 each) — the base 17/32 vs 15/32 sign imbalance cancels under antipodal doubling, since each base cross pair maps to two pairs at each sign [D; sum re-verified here].

---

### G.8 What this fixes, in one paragraph

Degrees 0–2 are annihilated exactly by construction and contribute zero variance. Degree 4 cannot be annihilated below 65,792 points and we are 1,280 short; what remains there is a three-shell operator that is flat to within 2% across 32,255 of its 32,256 modes, with the single quadrature-functional mode suppressed 42.48x — and that one mode is the entire measured degree-4 advantage. Degree 6 is at iid level because the +-1/16 phase cancellation is a degree-4 resonance. Above the boundary the field is maximum-entropy chi^2_1 speckle whose grain is half the design pitch, so the 64,512 evaluations behave as ~38k independent draws, and the champion sits at 0.90–1.79x of the point-evaluation floor. Every failed mechanism family — low-rank design-side correction (S6), smooth covariates (S15), combinatorial covariates (S18), surface/kink representations (S9), residual reparametrization (S16), design mutation (M180), design completion (S11) — fails against one of those two clauses.

---

### G.9 Defects found while tracing (both new, both cheap to fix)

**D1 — P1 §Pillar 1 misstates the design-span fraction by 32x.** The text reads "dim H_4 = 183,148,480, so the design span is 5.6e-3 of the degree-4 space." The correct ratio is 32,256 / 183,148,480 = **1.7612e-4**, i.e. one part in **5,678**. The likely provenance is the reciprocal 183,148,480/32,256 = 5,677.9 = 5.68e3 losing its exponent sign. Nothing downstream depends on the value — the argument only needs N << dim H_4, which holds far more strongly at the correct figure — but it is a printed number in a paper and should be corrected to 1.76e-4.

**D2 — S6's prose sentence on the sign imbalance is self-contradictory at degree 4.** `S6_VERDICT.md` §"Inner-product fingerprint" says of the 53.1%/46.9% split: "it is invisible to even kernels but is what powers the constant-mode cancellation below." Both halves cannot be true. G_4 is even, so G_4(+1/16) = G_4(-1/16) and the cancellation depends only on the total cross-frame count. My term-by-term reconstruction (§G.2) confirms it: 32,256 + 376.529 - 31,867.704 = 764.825, with the cross-frame term entering solely through 1,032,192,000 x G_4(1/16). Split that same mass 50/50 and the answer is bit-identical. The imbalance is real and exact (17/32 vs 15/32), and it is what antipodal doubling cancels (§G.7), but it is not the source of the 42x suppression. All S6 *numbers* reproduce; only the causal sentence is wrong.

**D3 — the "0.0 bitwise" 2-design certificate does not exist in the record.** See §G.1. The exactness is derivable in closed form and the measurement that does exist (m191 deg-2 rms ~8.6e-9, ratio 2.2e-6 of iid) is float roundoff on a structurally exact null. If a bitwise second-moment certificate is wanted for the write-up it has to be produced; today it would be a new measurement, not a citation.


---

## The cost algebra

Sourcing discipline: every figure is either quoted from a committed artifact with its path,
or is arithmetic I performed this session from committed formulas, marked DERIVED with
operands shown. Two numbers in my tasking are not in the record at all; they are flagged in
§2.3. Paths are relative to `.../publish/recursive-estimator-folding/corpus/whestbench/`.

### 1. The score law, and what its invariance forbids

Verbatim from `headroom/fold_ledger.json` -> `invariants.score_formula` (schema 1, **264
records**):

    S = MSE * max(0.1, C/B),   C = billed_FLOPs + 1e11 * residual_seconds,   B = 2.72e11
    under installed WHestBench 0.14.0 and FlopScope 0.10.0

`core/HANDOFF_CODEX_SOL_20260808.md:23-24` states it identically, with the 0.1 floor
confirmed from leaderboard arithmetic. `invariants.resource_ceiling` adds the hard wall
`C <= 272000000000` and the internal promotion gate `Cmax < 258400000000`, zero failures.

**lambda = 1e11 FLOP/s is an exchange rate, not a penalty.** It buys uninstrumented wall at
a fixed price, so an off-flopscope backend pays iff its sustained one-core throughput
exceeds 1e11. N8b measured the K1 fused f32 kernel at **0.94e11 FLOP/s** against a
predeclared kill line of 1.2e11 (`experiments/n8b_disclosed_native/N8B_PREDECLARATION.md`)
and died on that one inequality. Rules v12 §5.5 makes it structural — "unfavorable
per-second rate", "not on wall-clock time" (`core/LIVE_RULES_RESET_20260808.md`).

**The residual convention carries a free multiplier k, and it is 1.** Write
`C = F + k*1e11*R`. `experiments/gm_residual_k1/VERDICT.md` re-derives the five frozen M160
workers against the 258.4e9 gate: at k=1, **5/5 PASS**, worst 210.352002450e9, margin
48.048e9 = **18.60%**, worst-worker break-even **k\* = 3.8296**; at k=5, 3/5 PASS, worst
**278.273084846e9** — reproducing the ledger's recorded "maximum 278.273084846B, 2/5 exceed"
exactly, which is what validates the recomputation. The hostile x5 convention is refuted by
hosted k ~ 1.0, but the record's label is INCONCLUSIVE_HOLD, not confirmed: the fresh
1-core re-measurement (ARM A) was disqualified by a BLAS-pool artifact **43.30x** larger
than the effect under test (ARM A inflicted 142.36x slowdown; a faithful 1-physical-core pin
costs 3.29x). Confirming k=1 un-kills five of your own exact-control records.

**Scale invariance along the sampling curve.** In the metered regime `S = MSE * C/B`, so for
one matched network a child with cost ratio r_C and raw-MSE ratio r_V gives
`S_child/S_parent = r_C * r_V`, and the strict promotion condition is `r_C*r_V < 1`
(`core/COMPRESSION_SCORE_CALCULUS_20260806.md`). If cost moves only through path count N,
then `MSE ~ 1/N` gives `r_V ~ 1/r_C` and the product is 1 to first order — buying paths and
selling paths are **both** neutral. The only lever is variance per billed FLOP. Committed
tolerances: r_C 0.90 -> r_V 1.1111; 0.75 -> 1.3333; 0.50 -> 2.0000; 0.25 -> 4.0000.

With the floor active the exact ratio is
`r_V * max(0.1, r_C*C_parent/B) / max(0.1, C_parent/B)`. The committed floor ceiling for the
random32,256 parent (raw 3.089512726e-7, adjusted 2.257079776e-7, mean multiplier
0.7436830511): an impossible exact compression to the 0.1 floor with identical predictions
scores 3.089512726e-8, a **7.3056x** gain — **not** 7.4368x = 0.7436830511/0.1, because
per-network MSE and multiplier are correlated and the score is paired per network. Aggregate
ratio arithmetic is not the aggregate score ratio. This is the trap most cost claims fall in.

Worked instance (`experiments/s11_full129_breakeven/S11_VERDICT.md`): completing 126 -> 129
frames costs `66048/64512 = 1.0238095`, so break-even needs `MSE_129/MSE_126 < 64512/66048 =
0.9767442`, i.e. **> 2.32558%** MSE reduction. Measured degree-4-attributable reduction
<= **0.176%**, corroborated at +0.42% (m191 cv_deg4) and R^2_deg4 ~0.2%. An order of
magnitude under break-even; re-killed.

### 2. The champion's measured decomposition

#### 2.1 The graded anchor

#326094, Kerdock v3, graded 2026-08-08 (`core/SUBMISSION_RESULT_20260808.md`): adjusted
**1.832e-7**, final-layer MSE **2.818e-7**, 50/50 public MLPs, zero failures, rank #192 ->
#58; all-layers MSE 8.16e-4, L0->L31 growth 416x.

C/B is not reported by the grader; it is derived, and `S11_VERDICT.md` does the derivation:
`C/B = 1.832e-7 / 2.818e-7 = 0.6501`, which is also the regime check that puts us in the
proportional band, not the floored one. DERIVED from that: **C = 0.6501064585 * 2.72e11 =
176.829e9**. Cross-signals: the pinned-basis dossier gives mean C **178.5e9** (agreement
1.0%); the T4 official-100 run gives mean effective compute **178.462975e9**, max
**209.575026e9** (23% under B), mean multiplier 0.6561138779836238
(`experiments/t4_kerdock_descriptive_rescore/T4_REPORT.md`).
`core/GEN8_FORUM_INTELLIGENCE_20260810.md` quotes the same as **65.01%** against the rival's
published post-Strassen budget **64.27%** — cost parity, so the residual gap to them is raw
MSE, not accounting.

#### 2.2 The two residual framings, reconciled

Both are correct; they differ in **denominator** and in **which residual statistic**. Base
measurement, T4, 100 MLPs, explicitly labelled **local** in
`core/SUBMIT_READINESS_20260808.md`: wall mean 2.86 s / max **4.11 s** (60 s cap, 14.6x
margin), flopscope backend 2.36 s, overhead 0.42 s, residual **0.080 s mean / 0.137 s max**.

DERIVED definition check — `BudgetContext` exposes `residual_wall_time_s`,
`flopscope_backend_time_s`, `flopscope_overhead_time_s`
(`experiments/gen8_gate_audit/_installed_api.json`) — and 2.86 - 2.36 - 0.42 = **0.08**
exactly. The residual is the wall remainder and it closes.

All shares DERIVED at lambda = 1e11, C = 176.829e9, B = 2.72e11:

| framing | residual | FLOP-equiv | denominator | share | as stated |
|---|---:|---:|---|---:|---|
| mean vs scored C | 0.080 s | 8.00e9 | C = 176.83e9 | **4.524%** | "4.5% of scored C on average" (PHASE1_WRITEUP:65) |
| max vs scored C | 0.137 s | 1.370e10 | C = 176.83e9 | **7.748%** | "7.7% of adjusted score in the worst case at C/B 0.650" (:65) |
| max vs budget B | 0.137 s | 1.370e10 | B = 2.72e11 | **5.037%** | "5.0% of budget" (SUBMIT_READINESS; FLIP_READINESS:55) |

4.5% and 7.7% are the same statistic — residual/C — at the mean and at the max. 5.0% is the
max taken against B instead of C. Because S is proportional to C in the metered regime, the
residual/C fraction is simultaneously the *inflation of the adjusted score* attributable to
uninstrumented time, which is why the writeup can say "of adjusted score" without changing
the number. All three are conditional on lambda = 1e11 holding (Rules §5.3 reserves changes),
and the writeup says so.

**Provenance defect found this session (P5 class, verified two ways).**
`core/SUBMIT_READINESS_20260808.md` labels the 0.080/0.137 table "Measured from the T4 run
(100 MLPs, **local**)", and `T4_REPORT.md` confirms T4 was a local subprocess run on public
0..99. `core/FLIP_READINESS_20260810.md:55` then cites "Residual max 0.137 s = 5.0% of
budget" inside a *hosted*-compatibility argument with the local label dropped, and
`experiments/gm_residual_k1/VERDICT.md:128` reads it straight back as "**hosted** residual
max 0.137 s". The number is local. No hosted residual value exists anywhere in the corpus,
even though `core/HOSTED_INTEL_20260808.md:25-32` records that the submission page exposes
per-MLP billed FLOPs, wall time and a full time breakdown — i.e. the hosted residual is
directly measurable from two graded runs and simply has not been read. No verdict moves
(5.0% either way is small), but a local number wearing a hosted label inside a compatibility
audit is the M183/C1 disease on the provenance axis.

#### 2.3 The instrumented-lane split

DERIVED consistency: 145.138/146.794 = **0.988719**, reproducing the record's 98.87%
(`core/CODEX_ULTRAPLAN_20260810.md:40-41`, `core/GEN8_FORUM_INTELLIGENCE_20260810.md:58`,
`core/GEN8_LADDERS_20260810.md:190`, ledger record 262 which carries 98.87% alone). And
9.08/(146.794+9.08) = **5.825%**, reproducing 5.83% and implying C = 155.874e9 and
residual = **0.0908 s**.

**Flag — partially not in the record.** The pair 145.138e9 / 146.794e9 appears **only in
prose**, in those three core documents plus AGENT_CHANNEL (98.87% only). I searched every
`.json`, `.md`, `.txt` and `.py` in the repo: no measurement artifact produces them. The
figures `9.08e9` and `5.83%` **do not appear anywhere in the corpus** — they are internally
consistent with the pair, so they plausibly share its unlocated run, but I cannot trace
them. Two tensions: (i) 146.794e9 is well below both the hosted mean C 176.8e9 and the local
178.5e9, so it is not a 100-net mean — it is one net, or a phase subset; (ii) the M183
falsifier's committed one-net total is **158,028,807,386**
(`experiments/m183_f32_hotpath/m183_falsifier_results.json`), which is neither. Do not mix
this with the *older* random32,256 split — 185.4069e9 total / 184.8217e9 matmul =
**99.6844%** over ~215.41 matmul calls, residual 0.16875 s mean
(`core/COMPRESSION_SCORE_CALCULUS_20260806.md`) — nor with the "~95.5% instrumented" figure
at `GEN8_FORUM_INTELLIGENCE:121`, which is a third denominator and is itself open (U-E4).
**Settling check:** one metered predict on one synthetic net, op_log grouped by
`namespace`/`op_name`, emitting instrumented total, matmul total and
`budget.residual_wall_time_s`. Cheap. Do it before citing any of the three splits.

### 3. The fractal application — the phased-WHT butterfly

`experiments/v31_guards/package_source/kerdock_v3_estimator.py::_first_sample_matmul`
(lines 103-132) computes, per frame s, `mean_chi * H_256 @ (diag(phase_s) @ weight)` without
forming the direction matrix. The ownership invariant is executable, not aspirational:
`setup` deletes `self._gaussian`, and the retained state is 126 phase vectors, one
normalized Walsh matrix, and one half-frame scratch `(126, 128, 256)` f32.

Op by op, with n_base = 126*256 = 32,256, w = 256, E = n_base*w = **8,257,536** elements in
the `(126, 256, 256)` frame block:

    fnp.multiply(phases[:,:,None], weight[None,:,:], out=frames)   # E
    half = 1
    while half < 256:                          # 8 radix-2 stages
        copyto(scratch, left)                  # E/2
        add(scratch, right,  out=left)         # E/2
        subtract(scratch, right, out=right)    # E/2
        half *= 2
    fnp.multiply(output, MEAN_CHI_256/16.0, out=output)            # E

Per element: 1 seed + 8 x 1.5 + 1 scale = **14**. DERIVED total `14*E = 115,605,504`.
Second signal, committed: `experiments/m184_trichotomy_upward/M184_G0_NOTES.md:80-83` states
the same closed form — "the first product is the exact phased-WHT butterfly billed op-by-op
(14 n w ~= 0.116e9, vs ~4.2e9 direct)".

The counterfactual price is source-defined: `direct_cost(m,k,n) = m*n*(2k-1)`
(`experiments/v31_guards/package_source/cost_model.py:8-11`), pinned to
`flopscope/_flops.py` lines 217-234 by `experiments/WALL_RULE_AUDIT.md:165-167`. Pointwise
and copy at 1/element, gather 4/output element, sort `8 n ceil(log2 n)`, int concat
2/element are the v0.10 conventions verbatim at `M184_G0_NOTES.md:79-81`.

DERIVED, at the first-product shape:

| applying the 32,256 directions to W1 | billed FLOPs | vs dense |
|---|---:|---:|
| dense `(32256,256) @ (256,256)` | **4,219,600,896** | 1.000000 |
| one-level batched Winograd on that dense product | 3,713,941,504 | 0.880164 |
| **phased-WHT butterfly (deployed)** | **115,605,504** | **0.027398** |

Closed form: `dense/butterfly = n*w*(2w-1) / (14*n*w) = (2w-1)/14 = 511/14 = 36.5` exactly at
w = 256. Saving `n*w*(511-14) = 8,257,536 * 497 = 4,103,995,392` = **4.104e9** per network,
= 1.51% of B and 2.83% of the 145.138e9 matmul lane. Against the *Winograd-compressed* dense
application it still saves 3.598e9 (32.13x). Transcription check:
`WALL_RULE_AUDIT.md:157-160` independently states "The first hook always has shape
`(32256,256)@(256,256)`. The billing formula gives `4.219600896B` direct" — digit for digit.

Antipodal accounting, because it decides which baseline a claim is quoting.
`AGENT_CHANNEL.md:3110` describes the avoided object as the "64,512x256 direction matrix";
the code's output is `(32256, 256)` with antipodes by negation. Priced at the doubled count,
`direct(64512,256,256) = 8,439,201,792` — which is exactly the `8.4392B` direct baseline the
entire Strassen lineage uses in `core/COMPRESSION_SCORE_CALCULUS_20260806.md`. Same formula,
two row counts.

**Deep layers.** `_sample_matmul` delegates to `RowBlockedBatchedWinograd.multiply`
(`row_blocked_winograd.py`): one exact Winograd level, seven leaves fused into a single
batched matmul, `BLOCK_ROWS = 4096`, preallocated operands, caller-owned output. Bill
(`cost_model.py:30-39, 126-148`):

    leaf = 7*direct(m/2,k/2,n/2);  fills = 7*(m/2)*(k/2) + 7*(k/2)*(n/2);  adds = 7*(m/2)*(n/2)

DERIVED at (64512,256,256): 7,369,850,880 + 28,901,376 + 114,688 + 28,901,376 =
**7,427,768,320**, ratio **0.88015058**. Committed values: `0.880151` and `7.427768320B`
(`WALL_RULE_AUDIT.md:113-115`, `PREALLOCATED_STRASSEN_REPORT.md`,
`COMPRESSION_SCORE_CALCULUS:116`). Six-digit agreement — that is what licenses §7.

**Row-linearity, stated exactly.** The bill is *affine* in m, not linear. Leaves, left fills
and reconstruction adds scale with rows; the right-hand fill `7*(k/2)*(n/2)` is charged once
because `multiply()` packs `rc` outside the row loop (source comment: "Right-hand packing is
deliberately outside the row loop, so the billed right-stack fill is identical to the
unsplit operator"). Blocking therefore preserves the bill exactly — the claim behind
"row-linearity preserves the bill while planning workspace falls from 283.94MiB to about
91.44MiB", with measured peak falling to 474.301MiB against the 667.328MiB failure.

**Minor defect found this session.** `WALL_RULE_AUDIT.md:157-161` gives the batched bill at
the half shape (32256,256,256) as `3.713884160B` with "an exact analytical saving of
`0.505716736B`". That is exactly half the 64512 bill — but halving m does not halve the
m-independent right-stack fill. Correct: **3,713,941,504** and **505,659,392**. The audit
under-counts by exactly **57,344** FLOPs = 114,688/2, relative error 1.54e-5. It changes
nothing (that operator is not the deployed first hook; the butterfly is), but it is an
affine-vs-linear slip inside a document that calls itself an exact bill.

### 4. The v0.10.0 cost model as it prices us

Landed 2026-08-03 (discourse 18125, "cost model fixes, residual time safeguards");
`core/RESEARCH_INTEL_20260808.md:19` summarizes it as "f64 2x, data movement priced, 1 core".

| lever | price | our exposure |
|---|---|---|
| dtype-aware | 64-bit = **2x** 32-bit | the whole of §5-6 |
| data movement | copy/fill/concat **1/elem**; gather/sort **4/elem** | 4 of the butterfly's 14 per-element charges are pure movement (one `copyto` per stage) and bill at the same rate as the 10 arithmetic ones — the transform pays nothing extra for its scratch traffic. Strassen's adds and temporaries, by contrast, went from free to billed: that is A1's crux |
| einsum `out=` casting | destination dtype governs | `fnp.matmul` now takes `out=` (organizer, 18101); our first-product path already passes `out=` throughout, which AGENT_CHANNEL records as partially answering U-P4 for free |
| symmetry discount | `flopscope._accumulation`, ~2x on symmetric contractions | **void for us**: it applies to the `W^T V W` covariance sandwich, T2 killed closure-as-estimator (raw 9.61e-5 at depth 32), and no symmetry exists in the dense `X @ W` sampling matmuls that are 98.87% of the bill |
| participant cores | **1 physical core (2 vCPU)**; backend gets 7 | 14.6x wall margin, and the dominant 2.36 s term is backend, not participant |

The installed surface corroborates the symmetry machinery *and its own void path*:
`_installed_api.json` carries `AccumulationCost` (fields include `savings_ratio`,
`dense_baseline`, `fallback_used`, `unavailable_components`, `unavailable_reason`),
`SymmetricTensor`, `SymmetryGroup`, `SymmetryError`, `SymmetryLossWarning`. The discount is
real, opt-in via `as_symmetric()`, and structurally inapplicable to our hot lane.
`SUBMIT_READINESS` §2 closes the "favourable primitives" question negatively:
`flopscope.numpy.fft._free` covers only `fftfreq`/`fftshift`; `linalg` and `stats` bill at
analytical cost (erf/exp at 32 FLOPs/element) — penalties, not discounts, for our op mix;
bit-packing (32 bools/FLOP) applies to mask bookkeeping and was declined on eligibility risk
(`GEN8_FORUM_INTELLIGENCE:141`).

All of it is already priced into the anchor: #326094 was submitted four days after the
update and graded clean at C/B 0.650 (`core/FLIP_READINESS_20260810.md:41-48`). Second
signal that no compatibility work is owed.

### 5. The M183 retraction, with its arithmetic

**The structural zero.** `experiments/m183_f32_hotpath/run_m183_falsifier.py:58` reads
`dts = getattr(op, "dtypes", None) or ()`. The installed `flopscope.OpRecord` has no such
field. I verified the field list independently from the committed API dump
(`experiments/gen8_gate_audit/_installed_api.json` -> `flopscope.OpRecord`):

    count, cumulative, flop_cost, flopscope_backend_duration_s,
    flopscope_context_start_offset_s, flopscope_overhead_duration_s,
    index, namespace, op_name, resolved_dtype, shapes, subscripts

`resolved_dtype` is the real field, so the guard evaluates `any(...)` over an empty tuple for
every op on every program and `0.00%` was the only value it could ever return.
`GEN8_FORUM_INTELLIGENCE:35-39` gives the two signals collected at the time: STRUCTURAL (this
field list) and EMPIRICAL (the detector returns `f64_share 0.0` on a deliberately 100%-f64
program of five 64x64 f64 matmuls while the corrected `resolved_dtype` detector returns
`1.0` on the same log). A second dead name sits at line 62 — `getattr(op, 'name', '?')`
where the field is `op_name` — masked because line 62 is inside the unreachable `f64 > 0`
branch. I read both lines; they are at 58 and 62 as stated.

**The corrected arithmetic, DERIVED.** The falsifier's committed result records
`total_billed = 158028807386.0` on one synthetic net (width 256, depth 32, inside a
`BudgetContext`). Against that denominator:

    corrected f64 charge = 119,312,624 FLOPs                                  [record: 1.193e8]
    share of predict     = 119,312,624 / 158,028,807,386 = 7.5501e-4 = 0.0755%   [matches]
    recast ceiling       = 119,312,624 / 2 = 59,656,312 FLOPs                    [matches]

The factor of exactly 2 **is** the v0.10.0 dtype rule: recasting an f64 lane to f32 halves
its charge, so the ceiling on the "free 2x" is half the f64 charge, not all of it. 59,656,312
reproduces the Gen-7 cost-remap attacker's independent 59.66M to the digit — the second
signal that keeps the verdict alive. Scale: DERIVED, the ceiling is **0.0219% of B** and
**0.0337% of C**. There is no material f64 lane.

**What is retracted.** The verdict (kill M183, no free 2x) stands on the corrected
measurement. The figure `0.00% f64-lane billing — already clean` does not, and it is in the
filed write-up twice; the line numbers the record gives are exact against
`core/PHASE1_WRITEUP_DRAFT_20260808.md`, and I checked both. Line **129** is the
falsification-ledger row. Line **422** is load-bearing: "the fidelity family formally retired
the dtype-repricing escape (M183 measured the f64 SHARE at 0.00%, **which is invariant to
how f64 is priced**)". That parenthesis is the entire argument, and it rests on a share the
instrument was structurally incapable of measuring. Gen-7's formal retirement of the
dtype-repricing flag is therefore withdrawn. U-I2 (erratum to organizers?) is outward-facing
and Jonah's alone; A2 (`core/CODEX_ULTRAPLAN_20260810.md:75-88`) asks you to adjudicate line
422 independently. My read of the arithmetic: the *conclusion* survives — 0.0755%, ceiling
0.0337% of C, cannot license a repricing escape under any rounding — but the *citation* must
change, because its number is unobtainable from the instrument that produced it.

**Class size.** `experiments/gen8_gate_audit/GATE_AUDIT.md` cleared 7 of 8 shape-matched
detectors by explicit firing checks against positive fixtures, including `gm_m179_m199`'s —
the instrument behind the record that licensed the whole width-gate line. M183 is the sole
confirmed void. The antidote already exists in the corpus at
`m217_.../run_m217_native_trace.py:119`, `int(matmul.get("calls", -1))` — a loud sentinel
instead of a falsy default. It is now a promotion rule: no detector may produce a promotion-
or kill-bearing null unless it fired on a positive fixture in the same run
(`core/GEN8_LADDERS_20260810.md`, clause 3).

### 6. The dtype contagion (topic 18127), and where the firewall actually is

**REPORTED (dipam, organizer, 18127):** all **24** `flopscope.stats` callables promote
f32 -> f64 permanently, and "a single `stats.norm.ppf` call generating the sample matrix was
enough to put all 32 hot matmuls in float64" — a ~2x total-cost effect. v0.11.0 will emit
`FlopscopeWarning` at each site. *I could not verify the count of 24 locally:*
`_installed_api.json` enumerates 58 top-level `flopscope`/`whestbench` symbols and does not
descend into `flopscope.stats`, and no other committed artifact enumerates it.

**Our exposure, OBSERVED from source.** The record says "our champion makes `stats.norm.pdf`
x32 and `stats.norm.cdf` x32 per MLP" and states the guard as "an explicit float32 cast at
every stats callsite" / "all 64 stats callsites". Reading
`experiments/v31_guards/package_source/base_estimator.py:15-38`, the precise shape is **two
source callsites inside one depth-loop**:

    for weight in mlp.weights:                 # depth 32
        phi = flops.stats.norm.pdf(alpha)      # line 27
        cdf = flops.stats.norm.cdf(alpha)      # line 28

64 *invocations* per MLP from **2 source lines**. The guard is two `astype(fnp.float32)`
insertions, not sixty-four edits. Say it that way in the predeclaration.

**Why the promotion does not reach the hot lane today (DERIVED, mechanism).** `alpha` is f32;
`phi`/`cdf` return f64; `mu = mu_pre*cdf + sigma*phi` is therefore f64 and feeds `mu @ weight`
at the next layer — so the promotion *does* enter matmuls, but only the diagonal analytic
recurrence's `(256,) @ (256,256)` matvecs at `direct(1,256,256) = 130,816` each. There is
**no explicit f32 cast anywhere after line 28**: the only `astype` calls in the package are
`base_estimator.py:78/86` in the Sobol/Gaussian draw and `fold3_estimator.py:86`, which
*allocates* the activation buffer as `fnp.empty((2*n_base, width), dtype=fnp.float32)`. Every
hot write lands in that buffer through an `out=` destination — including
`fnp.multiply(output, MEAN_CHI_256/16.0, out=output)`, where an f64 Python scalar is cast on
write under the v0.10.0 `out=` casting rule. **The firewall is the `out=`-pinned f32 buffers,
not a cast.** A refactor that drops `out=` dissolves it. The record's phrasing — "those 64
callsites are one refactor away from moving a 145.138e9-FLOP matmul lane into the 2x rate" —
is right about the risk and wrong about where the safety lives. Standing guard for any
Phase-2 edit: explicit f32 cast at both stats callsites **and** an assertion that the hot-lane
destination buffers remain f32. Open: U-G3 (P1/P4) — is the corrected 0.0755% stable across
nets and widths, or is it a width-256 point measurement? Not measured.

### 7. U-F1: the contested Strassen/Winograd lineage, FLOP versus wall

The lineage `exact_sampler_rectangular_strassen -> preallocated_strassen_winograd ->
integrated_batched_winograd` is worked and killed, not unexplored. The kills
(`experiments/PREALLOCATED_STRASSEN_REPORT.md:98-99`):

| variant | effective/direct | wall/direct | outcome |
|---|---:|---:|---|
| L1 sequential (7 half-width BLAS calls) | 0.882057 | **1.55874** | fail |
| L1 batched (Mutation B) | 0.885099 | **1.54559** | fail |
| packed | 0.886148 | **1.70148** | fail |

Every one **passed the score-side arithmetic and failed a wall-time ratio gate frozen at
1.5x.** Parity across all three: depth-32 relative error < 2.96e-6, gate changes <= 2 in
4,194,304, residual 0.263-0.527 ms, peak memory < 481 MiB.

**Our own record disagrees with itself.** `WALL_RULE_AUDIT.md:103-109` establishes that the
1.5x test "is visibly local policy" — it lives in `PREDECLARED_GATES.md` lines 64-70 and
appears in neither the installed scoring formula nor `whestbench/runner.py`; Rules v12 §5.5
says the metric depends on analytical FLOPs "not on wall-clock time"; wall binds only through
absolute caps (30 s host, 60 s in-context) against which we hold 14.6x; and FlopScope
attributes counted NumPy/BLAS time to *backend* time, excluded from charged residual. Against
that, the Gen-8 skeptic killed the reopening on inflated arithmetic (~4x) and on misread
lineage state. **Contested, not reopened.** A1 hands it to you as R0 arithmetic and gates the
outcome explicitly: even a strict decrease is not a reopening, it becomes a predeclared
Phase-2 candidate that must cross R3 on its declared sensitivity axis (recursion depth, not
width) and carry the instrument-validity gate.

**A head start on the R0, DERIVED, no compute, no code.** Recursing the committed batched
formulation at every level,

    Bill(m,k,n,d) = 7*Bill(m/2,k/2,n/2,d-1) + 7*(m/2)*(k/2) + 7*(k/2)*(n/2) + 7*(m/2)*(n/2)
    Bill(m,k,n,0) = m*n*(2k-1)

on (64512,256) @ (256,256), direct = 8,439,201,792:

| d | billed | vs direct | (7/8)^d | movement+adds share | leaf k=n | batch | scratch @4096 rows |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 8,439,201,792 | 1.000000 | 1.000000 | — | 256 | 1 | — |
| 1 | 7,427,768,320 | **0.880151** | 0.875000 | 0.78% | 128 | 7 | 14.44 MiB |
| 2 | 6,582,603,776 | 0.780003 | 0.765625 | 2.42% | 64 | 49 | 39.70 MiB |
| 3 | 5,912,804,352 | 0.700636 | 0.669922 | 5.69% | 32 | 343 | 83.92 MiB |
| 4 | 5,448,739,072 | 0.645646 | 0.586182 | 11.88% | 16 | 2401 | 161.29 MiB |
| 5 | 5,256,198,080 | 0.622831 | 0.512909 | 22.64% | 8 | 16807 | 296.70 MiB |

The d=1 row reproduces the committed 0.880151 exactly — the check that the recursion is
transcribed correctly. **Provisional answer to A1's gate: the FLOP-only bill strictly
decreases at every depth through 5.** The v0.10.0 movement repricing slows the descent (that
term goes 0.78% -> 22.6% of the bill) but does not reverse it at these shapes, because the
leaf term falls as (7/8)^d while movement grows as (7/4)^d from a base 127x smaller
(0.0579e9 against 7.370e9 at d=1). Memory is no longer the L2-hybrid blocker (667.328 MiB
against a <512 MiB envelope) *provided row-blocking is retained* — last column, DERIVED by
summing every level's left stacks, right stacks and products in f32 at BLOCK_ROWS = 4096.

Label: DERIVED under three stated assumptions — (i) every level's operand stacks bill at
1/element as `batched_winograd_core_cost` does; (ii) the fused batched dispatch keeps one
matmul call per level-set, so the `calls > 8` rule in `candidate_bill` never fires; (iii) no
ragged fallbacks. Assumption (i) is the one to attack: if a real implementation needs one
extra materialization per level, add `7^l * (m/2^l)*(k/2^l)` per level and re-run.

**What the table does not settle.** It is a bill, not a score. Wall time is what killed the
family, and at d >= 2 the leaf contraction depth falls to 64, 32, 16, 8 — one-core BLAS
efficiency collapses far faster there than at 128, which is exactly the mechanism the kill
text names ("one-core half-width BLAS plus Winograd memory traffic, not allocation"). Under
the current metric that cost lands in backend time and is not charged; under a Phase-2 rules
change it might be. And the prize is bounded: the rival's 1.5412x is attributed by their own
ablation "entirely because the second technique is cheaper", and cost parity is already
measured (their 64.27% against our 65.01%), so this axis is worth the difference between
those two figures, not 1.54x. Do not write kernel code on the strength of the table alone.

### 8. What I could not verify

- 145.138e9 / 146.794e9 have no measurement artifact in the corpus; 9.08e9 and 5.83% appear
  nowhere at all. Settling check named in §2.3.
- The 24-callable `flopscope.stats` count is organizer-reported, unverified locally.
- The corrected 0.0755% f64 charge is a single-net, width-256 point measurement (U-G3).
- 0.137 s is a local T4 number cited as hosted downstream; no hosted residual has ever been
  read, though the submission page exposes the breakdown.
- `WALL_RULE_AUDIT.md`'s 3.713884160e9 / 0.505716736e9 pair is off by 57,344 FLOPs
  (affine-not-linear in m). Verdict unaffected.
- `core/CODEX_ULTRAPLAN_20260810.md:3` cites a companion `CODEX_HANDOFF_20260810.md` "for the
  mathematics". **That file is not in the repository** — `core/` contains no such document.
  If the provenance for the 145.138/146.794 split exists, that is where to look for it.

---

## The decision-layer statistics

Everything below is quoted from a committed artifact or is a derivation I performed
this session with its arithmetic shown. Level tags follow the corpus convention:
**[O]** observed/read this session, **[D]** derived here with steps shown,
**[R]** reported by a committed doc, **[A]** assumption. Where the record is silent
I say so.

Source set read: `experiments/s17_ibc_floor/{S17_VERDICT.md,s17_results.json}`,
`experiments/gm_s17_reuse/{VERDICT.md,gm_s17_reuse_checkpoint.json}`,
`experiments/s1b_dispersion_corrected/{S1B_DISPERSION_CORRECTED.md,s1b_results.json}`,
`experiments/gm_s1s4_vd/VERDICT.md`,
`experiments/c1_local_mc_calibration/{C1_REPORT.md,C1_PREDECLARATION.md,estimator.py}`,
`experiments/gm_c1_bound/VERDICT.md`,
`experiments/n8c_offline_corrector/{N8C_PREDECLARATION.md,n8c_g0_results.json}`,
`experiments/t2_closure_score_measurement/T2_REPORT.md`,
`core/{GEN8_FORUM_INTELLIGENCE,FAILURE_MODE_GRAPH,PASSES_AND_UNCERTAINTIES_GRAPH,
PHASE1_WRITEUP_DRAFT,GEN3_RECURSION_PACKET,FLIP_READINESS,RESEARCH_INTEL}.md`,
`papers/P1_SPECKLE_THEOREM_20260810.md`, `headroom/fold_ledger.json` (264 candidates),
`AGENT_CHANNEL.md`.

---

### 1. S17's floor construction

#### 1.1 The exact five-shell fingerprint

The champion evaluates the antipodally-doubled Kerdock design, `N_full = 64,512 =
2 x 32,256`. S17's predeclared four-term correlation-kernel formula
`(1/N^2)[N*C(1) + n0*C(0) + n+*C(1/16) + n-*C(-1/16)]` closes only on the base set,
whose census sums to `32,256^2`; the doubled set needed a five-shell derivation from
the S6 base census under the `{x,-x}` map [R, S17_VERDICT §Deviations 1].

Base census (S6, exact dyadic) [R]:

| shell | t | multiplicity |
|---|---|---|
| diagonal | 1 | 32,256 |
| within-frame | 0 | 8,225,280 (= N x 255) |
| cross-frame | +1/16 | 548,352,000 |
| cross-frame | -1/16 | 483,840,000 |

Sum = 1,040,449,536 = 32,256^2 [D: 548,352,000 + 483,840,000 = 1,032,192,000;
+ 8,225,280 = 1,040,417,280; + 32,256 = 1,040,449,536; 32,256^2 = 1,040,449,536].

Doubled census (derived in S17, reproduced here) [R + D]:

| shell | t | multiplicity | inflation coeff = mult / N_full |
|---|---|---|---|
| diagonal | +1 | 64,512 | — |
| antipode | -1 | 64,512 | 1 |
| within-frame | 0 | 32,901,120 | 510 |
| cross-frame | +1/16 | 2,064,384,000 | 32,000 |
| cross-frame | -1/16 | 2,064,384,000 | 32,000 |

Sum = 4,161,798,144 = 64,512^2, **bitwise** [D: 2x64,512 = 129,024;
+32,901,120 = 33,030,144; +4,128,768,000 = 4,161,798,144; 64,512^2 = 4,161,798,144].
The two off-diagonal cross shells are **exactly equal**, each
`2 x (548,352,000 + 483,840,000) = 2,064,384,000` — the doubling map sends every
base cross pair to two `+1/16` and two `-1/16` pairs, so the Kerdock `+1/16` excess
cancels and the odd harmonic part drops out of the quadrature sum identically
[R, `s17_results.json.A_fingerprint.sign_balanced = true`]. Inflation coefficients
check: 32,901,120/64,512 = 510.0; 2,064,384,000/64,512 = 32,000 [D].

#### 1.2 The DISCLOSED formula correction — the kernel path is numerically unusable

The even combination of the two cross shells carries coefficient
`32,000 + 32,000 = 64,000` [R, `inflation_coefficients_over_iid.cross c_r_even(1/16)
= 64000.0`]. Plugging the S7 depth-32 mean-field kernel into the exact fingerprint:

```
inflation = 1 + 1*c_r(-1) + 510*c_r(0) + 64000*c_r_even(1/16)
          = 1 + (-0.05151847436926806) + 510*0 + 64000*(3.74538433938725e-4)
          = 24.918941297709
```

which reproduces the committed artifact value `24.918941297709132` to the last
printed digit [D, exact arithmetic]. That number is a **documented artifact, not a
floor** [R]. The reason is the coefficient: `d(inflation)/d(c_even) = 64,000`, so a
1e-3 error in `c_even(1/16)` moves the answer by 64. The mean-field `c_even(1/16) =
3.745e-4` is a second-order Taylor tail the depth-32 iteration does not resolve to
the ~1e-5 the coefficient demands, and the **empirical** `c_even(1/16)` at r=0 is
about **75x smaller** (net 101: -5.467822805418879e-06;
3.745e-4/5.0e-6 ≈ 74.9) [R + D]. Substituting the empirical value in the same
formula returns `1 - 0.0515185 + 64000*(-5.4678228e-06) = 0.5985` [D] — i.e. the
same five-shell expression swings from 24.9 to 0.60 over a 3.8e-4 change in one
argument. That is the whole disclosure: **the floor is anchored on `sigma^2 =
Var(ybar)` directly, and the correlation kernel is retained only as corroborating
evidence that the residual is decorrelated at the design spacing** [R].

Empirical shell correlations at the design's own angles, r=0 [R, `A_per_net`]:
`c(0)` = -1.2721e-3 / -1.2885e-3 / -1.3491e-3 (nets 101/202/303);
`c_even(1/16)` = -5.4678e-6 / -5.3369e-6 / -4.8528e-6. Design minimum angle
86.42 deg = arccos(1/16), roughly 2x the S7 speckle length xi ≈ 37-46 deg [R].

#### 1.3 The `sigma^2/N` anchor and the champion's position (n = 3, the S17 record)

`sigma^2 = Var_u(neuron-mean of the layer-31 post-ReLU field)` over the 64,512-point
design, two ways (`Var(ybar)` vs `mean(r_global^2)`), relative difference exactly 0.0
on all three nets [R].

| net | sigma^2 | champion MSE | sigma^2/64,512 | champ/floor | sigma^2/32,256 | champ/dir-floor | N_eff = sigma^2/champ |
|---|---|---|---|---|---|---|---|
| 101 | 7.9004722096335e-3 | 1.9971942916e-7 | 1.2246515702e-7 | **1.6308265471** | 2.4493031404e-7 | 0.8154132736 | 39,557.85 |
| 202 | 1.6002145106e-2 | 5.8720865986e-7 | 2.4804912429e-7 | **2.3673079336** | 4.9609824858e-7 | 1.1836539668 | 27,251.21 |
| 303 | 1.1124831594e-2 | 2.3692484273e-7 | 1.7244592624e-7 | **1.3739080296** | 3.4489185248e-7 | 0.6869540148 | 46,955.11 |
| pooled | | | | **1.7906808368** | | **0.8953404184** | ~37,921 |

Pooled se 0.29770000995, t95 CI **[0.5097, 3.0717]** — an interval spanning 6x
that includes the champion sitting at or below its own floor [R]. The two
accountings differ by exactly 2x because 64,512 forwards are 32,256 base directions
plus antipodes [R].

`N_eff` mean = (39,557.85 + 27,251.21 + 46,955.11)/3 = 37,921.39, i.e.
**58.78% of 64,512** [D]; equivalently an antipodal pair of forwards is worth
`2 x 0.5878 = 1.176 ≈ 1.2` independent draws, not 2, because the antipode carries
correlated even-harmonic information [R + D]. Per-net efficiency 0.6132 / 0.4224 /
0.7279 [R].

The even/odd harmonic split that would *prove* the 2x is the antipodal degeneracy
**could not be verified** — antipodal pairs are not identifiable from the committed
S5 arrays (`dmin` is a net feature, not the geometric distance), so the
decomposition was omitted rather than reported unverified [R, S17 Limitations].

#### 1.4 The n=80 revision — three numbers in §1.3 are dead

`gm_s17_reuse` (ledger 257, status **killed**) re-ran S17's section-A instrument
response-free on the committed 80-net m185 stage-1 panel (seeds 1000..1079). Step 0
reproduced all three per-net `sigma^2`, all three ratios and the pooled
1.7906808367797993 at **rel err 0.00e+00** [R]. Results at n=80:

| accounting | pooled | sd | se | 95% t CI | bootstrap (20k) |
|---|---|---|---|---|---|
| PRIMARY `mse_corr/(sigma^2/64512)` | **2.0088457167** | 1.4329454642 | 0.1602081733 | **[1.6900, 2.3277]** | [1.7080, 2.3335] |
| S17-convention | **2.1117** | 1.4421 | 0.1612 | [1.7908, 2.4326] | [1.8010, 2.4350] |
| distinct-direction `/(sigma^2/32256)` | **1.0044** | — | — | **[0.8450, 1.1639]** | — |
| per-output floor `/(mean_j Var_j/64512)` | 0.3641 | — | — | [0.3105, 0.4177] | — |

Three owed edits, quoted verbatim from the ledger record [R]:

1. **"GATE (i) OBTAINS" must be restated** as "class i/ii, boundary unresolved,
   pooled 2.01 [1.69, 2.33]". S17's own class rule (`run_s17.py` lines 201-204:
   `<2.0 -> class i`, `2.0-4.0 -> class ii`) flips at the point estimate, and the CI
   straddles 2.0 in both accountings.
2. **"champion/floor = 0.90 on distinct-direction accounting" is retired.** At n=80
   it is 1.0044 [0.8450, 1.1639] — the champion sits exactly *on* that floor. The
   objection "a floor the champion beats by 10% is not a lower bound" is dissolved
   by measurement, not argument.
3. **"≥2.2x below the point floor in every accounting" is falsified.** The generous
   ednacob bracket `3.9657744377832187 / pooled` drops 2.2147x -> **1.9742x**
   (PRIMARY, CI 1.7037-2.3467) / 1.8780x (S17-conv). The tight end is unchanged at
   3.9658x. Because the generous CI lower bound is 1.70 > 1, ednacob still sits
   strictly below the point-evaluation floor in every accounting, so U18's dichotomy
   (seed-side extraction vs over-budget/suspect) **survives**. Amend the number,
   keep the conclusion.

Diagnostic, labelled not gated: S17's `sigma^2` is `Var(neuron-mean)`, not
`mean_j Var_j`; on the same design the two differ by **5.52x** (2.0088/0.3641).
Any future restatement of "the point-evaluation floor" must name which object it
means [R].

`N_eff` at n=80 does **not** reproduce the "~1.2 draws per pair" constant. From the
committed checkpoint [D, my computation over the 80 stored
`N_eff_sigma2_over_champ_corr`]: mean 56,915, median 43,031, min 9,876, max 273,537;
median/64,512 = 0.667 -> 1.33 draws per pair. The three available summaries
(inverse of the pooled ratio = 0.498, mean N_eff = 0.882, median = 0.667) disagree
because the n=80 numerator is a **single** rotation draw where S16/S17 averaged 16,
so the ratio is right-skewed (skew 1.157, median 1.499 vs mean 2.009, max 6.53 [R]).
**Treat "~60% efficiency / ~1.2 draws" as an n=3 statement.** The defensible
wide-n statement is the pooled ratio and its CI.

#### 1.5 What this is and is not

A **lower-bound attempt** with gates. Not a minimax proof, not a closure certificate.
Achievable-envelope points are UPPER bounds on S(B); only the ednacob floor-invariant
gap is a lower bound (an impossibility) [R]. Residual risk flagged by the judge:
no primitive-level independence — the worker's S3 path and the judge's re-derivation
both reuse `n8a.haar_rotation` / `he_mlp_weights` / `load_kerdock_directions`, so a
wrong primitive would fool every `sigma^2` signal at once; the one genuinely
different route is the net-identity MC against `truth31`, whose
`ratio_obs_over_expected` is 0.66/0.44/0.30 rather than ~1.0 — understood only in
sign [R].

---

### 2. The S(B) achievable envelope, and why the denominator matters

| regime | FLOPs C | achievable MSE | bound | level |
|---|---|---|---|---|
| (i) B~0, cheap observables | 0 | ≈ sigma^2 (unreduced) | UPPER | observed (S15: covariates explain 1.56%) |
| (ii) analytic closure, deg≤2 exact | ~0 | **9.6e-5** | UPPER/achievable | reported (T2/M181 full-cov) |
| (iii) champion | 1.768e11 | **2.818e-7** | UPPER/achievable | reported (leaderboard, C/B 0.650) |
| (iv) 5.27x budget, 1/N scaling | 9.31736e11 | **5.347248576850095e-8** | UPPER/achievable | derived |
| (v) B = inf | inf | 0 | limit | derived |

Two features: a **budget-independent closure plateau** at 9.6e-5 (more analytic
closure does not move it — S15 cheap first-layer covariates add ≤1.56% out-of-sample
R^2), and a **1/N sampling line** through the champion, where all the achievable
variance reduction lives [R].

The gap, all three denominators, exactly as the writeup states them [R,
`PHASE1_WRITEUP_DRAFT` L98-99 and L355-357: "the denominator matters, so we state
all three"]:

- `9.6e-5 / 2.818e-7 = ` **340.6671** (raw graded final-layer MSE) [D]
- `9.6e-5 / 2.5e-7 = ` **384.0** (the ~2.5e-7 sampling point used in §2 of the
  writeup; the corpus rounds this to "380x" in `FAILURE_MODE_GRAPH` and
  `PASSES_AND_UNCERTAINTIES_GRAPH`) [D]
- `9.6e-5 / 1.832e-7 = ` **524.0175** (adjusted score) [D]

**The 524x is a metric mismatch and codex-sol should know it.** The score law is
`S = MSE x max(0.1, C/B)`, `B = 2.72e11` [R, `CORPUS.md` L19, `HANDOFF` L23]. The
champion's adjusted 1.832e-7 = `2.818e-7 x 0.6501` [D: = 1.8320e-7]. The plateau's
9.6e-5 is a **raw** MSE. The closure's metered cost is 8.30e9 FLOPs = 3.05% of B
[R + D: 8.30e9/2.72e11 = 0.0305], which is **below** the 0.1 multiplier floor, so a
like-for-like adjusted plateau is `9.6e-5 x 0.1 = 9.6e-6`, and the honest adjusted
gap is `9.6e-6 / 1.832e-7 = ` **52.40x** [D] — exactly 1/10th of 524, the multiplier
floor. The record already contains this calculation: T2_REPORT §Consequences 1 says
"even a zero-cost closure at the 0.1 floor would score 9.6e-6 adjusted — 46x worse
than the L2 sampler (2.1020e-7)" [R], and `9.6e-6/2.102e-7 = 45.67` [D]. So 340.7x
and 384x are honest raw-vs-raw statements; 524x is raw-numerator-over-adjusted-
denominator and should not be quoted without that qualifier.

Plateau provenance and its own dispersion [R, T2_REPORT]: 9.6055e-5 is the **mean of
three seeds** — 7.2707e-5 / 1.7879e-4 / 3.7099e-5, a 4.8x spread — against 400k-sample
MC truth with noise floor 1.076e-7 / 1.950e-7 / 1.314e-7 (200-1000x below signal).
The diagonal closure sits at 7.18e-4, so exact covariance buys ~7.5x [R]. The
340.7x/384x/524x therefore all carry the 3-seed dispersion of their numerator; the
record does not attach a CI to 9.6e-5, and **that CI is not in the record**.

---

### 3. S1b's dispersion correction

#### 3.1 The old model is refuted by our own measurements

Committed S1/U9 used `DIFF_RATIO = 1.1`, `vD = 7.57e-4` [R]. Two independent
committed panels refute it. `vF = 0.3641995628656461` from the 48-value P2 rotation
pool, spread 11.0732 [R].

(a) **s17 `sigma2_var(ybar)`** (rotation-free by construction), n=3:
{7.9005e-3, 1.60021e-2, 1.11248e-2}, mean 1.16758e-2, max/min 2.03x;
relative variance ddof0 -> **vD = 0.08135950765383865**, ddof1 -> **0.1220** [R].

(b) **p2 per-net 16-rotation mean MSEs**: {1.99720e-7, 5.87209e-7, 2.36925e-7},
mean 3.41284e-7, max/min 2.94x; observed relvar 0.26160 (ddof0) / 0.39240 (ddof1);
rotation noise of a 16-rotation mean `vF/16 = 0.022762`; deconvolved
`vD = (v_obs - vF/16)/(1 + vF/16)` -> **0.2335** / **0.3614** (subtraction-only:
0.2388/0.3696, the dispatch's quoted range) [R]. Cross-checked against s17
`champion_mse` at max rel diff 1.8e-6 [R].

#### 3.2 The bracketing test

Simulated 80-net single-draw max/min spread of `D*F`, 10,000 replicates, against the
observed **15.53x** [R]:

| arm | vD | DIFF_RATIO | P5 | P50 | P95 | P(sim ≥ 15.53) | brackets? |
|---|---|---|---|---|---|---|---|
| old_control | 7.57e-4 | 1.10 | 9.14 | 11.18 | 11.94 | **0.000** | NO — understates |
| s17_low | 0.0814 | 2.71 | 11.64 | 18.19 | 25.51 | **0.720** | YES |
| s17_high | 0.1220 | 3.40 | 13.19 | 21.22 | 31.21 | **0.862** | YES |
| p2_low | 0.2335 | 5.55 | 17.64 | 30.43 | 48.14 | 0.978 | NO — overshoots |
| p2_high | 0.3614 | 8.67 | 23.95 | 43.19 | 72.09 | 0.999 | NO — overshoots |

**PROVENANCE DEFECT, live, unrepaired.** `S1B_DISPERSION_CORRECTED.md` calls the
15.53x "the observed **hosted** 80-net spread" three times (context line, §2 header,
Limitation 3), while naming its source as `m185 stage1 mse_raw` — which is a
**local-synthetic** 80-net panel (He nets seeds 1000..1079, `truth_stats` at
600k samples). `AGENT_CHANNEL` 2026-08-10 19:2x records that writeup v8 already
"fixed [the] 15.53x provenance to local-synthetic" [R]. The S1b artifact itself was
never corrected. The actual **hosted** wide-n spread is on record and was never used
by S1b: submission #326094, 50 public MLPs, min 5.42e-8 (patricia-hawkins), max
5.96e-7 (patricia-neal) -> **11.00x** [R + D: 5.96e-7/5.42e-8 = 10.996].

#### 3.3 Headline splits and bands (S1b, R = 1, anchor 1.83e-7, 1e6 suites)

- **Variance split: 17.12%-22.997% net-difficulty / 77.00%-82.88% rotation-draw**
  [R, `headline.difficulty_share_range_R1` / `rotation_share_range_R1`], replacing
  S1's "0.21% / 99.79%". Under the p2 upper sensitivity the difficulty share reaches
  34-42%.
- **50-net fresh-seed band (P5-P95 envelope of the bracketing arms):**
  **[1.5365204657e-7, 2.1552570609e-7]**; upper sensitivity (p2_high)
  **[1.4601210108e-7, 2.2460012006e-7]**.
- **100-net band:** [1.6188204409e-7, 2.0567206873e-7]; sensitivity
  [1.5637236074e-7, 2.1200454874e-7].
- **P(score worse than 2.5e-7), 50 nets:** old 6.7e-5; s17_low **4.6e-4**;
  s17_high **8.5e-4**; p2_low 2.71e-3; p2_high 6.277e-3. At 100 nets: 0.0 / 3e-6 /
  7e-6 / 5.2e-5 / 2.11e-4 [R, `arms.*.tail_50/100.p_above_2p5em7`].
- S1's PASS survives: R=6 SD shrink 44%/40% at vD 0.081/0.122 against a 25% gate
  [R], independently confirmed by bootstrap at 0.4429/0.4008 in `gm_s1s4_vd` [R].

#### 3.4 The wide-n instrument S1b never had — and what it says (partly my derivation)

`gm_s1s4_vd` (ledger 253) proved the key structural fact: `floor31` is
**rotation-free** (verified at source: `run_m185_g0.py:342` seeds `truth_stats` on
net seed only; `rot` enters only `predict_once` at :346), so for any rotation-free
`Z`, Cauchy-Schwarz gives `share_D ≥ Corr(Z, mse)^2` and hence
`vD ≥ Corr(Z, mse)^2 * relvar_obs` [R]. Measured: `rho(floor31, mse_raw) = 0.5157925`
-> `vD ≥ 0.10157901`, bootstrap 95% CI **[0.04723, 0.17623]**, permutation two-sided
p = 0.0 (0 of 20,000) [R]. That point bound lands **inside** S1b's operative
0.0814-0.1220 — S1b's replacement value corroborated by an instrument nobody used.

The naive moment reading of the same panel (`vD = (relvar - vF)/(1 + vF)`) gives
0.012913 on `mse_raw` and 0.144634 on `mse_corr`; the raw reading is an artifact of
`mse_raw = mse_corr + floor31` adding a less-dispersed, positively correlated
component worth 25.15% of the mean [R].

**My derivations from `gm_s17_reuse_checkpoint.json` (80 nets, arithmetic shown):**

| statistic | value |
|---|---|
| relvar(`sigma2`) ddof0 / ddof1 | 0.350598 / 0.355036 (max/min 23.278) |
| relvar(`champ_corr`) ddof1 | 0.561509 (max/min 35.342) |
| relvar(`mse_raw`) ddof1 | 0.381816 (max/min 15.5317) |
| Pearson(`sigma2`, `mse_raw`) | 0.485178 (Spearman 0.6376) |
| Pearson(`sigma2`, `champ_corr`) | 0.302968 |
| Pearson(`floor31`, `sigma2`) | 0.973640 |

Three consequences:

1. **S1b's chosen estimator is not consistent for vD.** S1b set `vD =
   relvar(sigma^2)` on 3 nets and got 0.0814/0.1220. The identical estimator on
   80 nets returns **0.3550** [D]. The n=3 chi2(2) CI (S1b's own, spanning
   [0.27x, 39.5x]) covers this, so nothing is contradicted — but the operative range
   0.0814-0.1220 is a small-n draw of a statistic that is upward-biased for `vD`
   anyway, because `sigma^2` carries idiosyncratic variance that never reaches the
   MSE. Quantified: if `sigma^2` were proportional to D with vD = 0.355 we would need
   `Corr(sigma^2, mse_raw) = sqrt(0.355/0.3818) = 0.964`; observed 0.485 [D].
2. **`sigma^2` as a second Cauchy-Schwarz instrument** gives `vD ≥ 0.485178^2 x
   0.381816 = 0.089879` (raw arm) and `≥ 0.302968^2 x 0.561509 = 0.051541` (corr arm)
   [D] — consistent with, and weaker than, `floor31`'s 0.10158. The two instruments
   are **not independent** (Pearson 0.9736); the joint OLS bound is
   `R^2 = 0.271609 -> vD ≥ 0.103704` [D], a marginal improvement over 0.101579.
3. **A sharper point estimator, and it sits above S1b's range.** Under S1b's own
   model `MSE = S*D*F` with `F ⟂ D` and any rotation-free `Z = D*(1+e)`,
   `E[Z*MSE]/(E[Z]*E[MSE]) = E[D^2]/E[D]^2 = 1 + vD` exactly, so
   `vD_hat = mean(Z*M)/(mean(Z)*mean(M)) - 1` is a consistent moment estimator [D,
   algebra shown]. On the 80-net panel (20,000-resample percentile bootstrap):

   | Z | M | vD_hat | 95% CI |
   |---|---|---|---|
   | `sigma2` | `champ_corr` (= mse_corr) | **0.1336** | [0.0537, 0.2203] |
   | `floor31` | `champ_corr` | 0.1297 | [0.0595, 0.2052] |
   | `sigma2` | `mse_raw` | 0.1764 | [0.1085, 0.2502] |
   | `floor31` | `mse_raw` | 0.1669 | [0.1049, 0.2338] |

   The cleanest cell is `Z = sigma2, M = mse_corr` (no mechanical coupling; the
   `floor31 / mse_corr` pair shares the subtracted floor, and the `mse_raw` rows are
   inflated by the additive floor for the reason `gm_s1s4_vd` gives). **Operative
   read: vD ≈ 0.134, 95% CI [0.054, 0.220]** — above S1b's 0.0814-0.1220 point range,
   below the p2-implied 0.2335-0.3614, and CI-compatible with both.

   Caveats, stated: `sigma^2` is computed at the **same** rotation draw
   (`900000 + s*1000 + 0`) as the champion, so it is only *effectively* rotation-free
   (the design is an exact 2-design, so the design variance tracks the sphere variance
   to speckle order); `floor31` is verified rotation-free at source and gives the same
   answer, which is the check that matters. The estimator is a ratio statistic with
   O(1/n) bias. **It is not in the record; I derived it here.**

   Consequence for the band: interpolating S1b's committed table between vD 0.122
   (band [1.537e-7, 2.155e-7], tail 0.085%) and vD 0.2335 (band [1.499e-7,
   2.200e-7], tail 0.271%) puts the vD-corrected 50-net band near [1.52e-7, 2.18e-7]
   with tail ≈0.15%. I did not run the harness; **the settling check is one re-run of
   `run_s1b.py` at vD = 0.134 with the anchor treated as random** (§4).

---

### 4. Today's correction (2026-08-10, Gen-8, ledger 260 `gen8_c1_ratio_artifact_and_anchor_se`, status killed)

#### 4.1 C1's 1.65 is a mean/median artifact — the orchestrator's own hypothesis, killed

C1 measured a budget-matched antithetic MC on 22 of 25 local public nets: mean
adjusted **1.0686276000992886e-6**, per-sample variance 0.0630, against the grader's
printed hosted MC reference **6.470e-7** -> `R = 1.6516655333837535` [R]. The
pre-run Gen-8 hypothesis was that this corroborated forum topic 18141 ("the public 50
are unusually easy") and should shift the band. **Killed:** the local panel's
**median is 6.47355e-7** against the printed 6.470e-7 — a **0.05% match**. The 1.65
is a pure right-tail artifact of the mean; there is no easiness shift to apply [R].
The median is independently in the committed record: `gm_c1_bound` step-0 reports
min 2.1704e-7 / median 6.4735e-7 / max 4.8650e-6, sd 1.1061e-6, relative variance
1.0714, max/min 22.415x [R].

`gm_c1_bound` (ledger 242, REVIVED_SCREENED) had already shown R is not a constant:
95% percentile bootstrap (B = 200,000) **[1.0362, 2.4230]**, width 1.387 = 1.80x the
[1.3706, 2.1415] band in which C1's parity claim keeps its truth value;
P(R in band) = 0.68264; jackknife SE 0.364483209384680 matching the closed form
exactly. Dropping the single largest net moves the **point** to 1.3722, dropping two
to 1.2276 — inside C1's own "suites comparable" region [0.8, 1.25]. What survives is
only the direction: P(R > 1.25) = 0.8763/0.8751 on two RNG streams [R]. "Rank 13-14"
was never tested (needs a hosted read; firewall).

#### 4.2 The real defect: S1b treated the hosted anchor as exact

The hosted 1.830e-7 anchor is a 50-net measurement carrying a **9.83% standard
error**. Folding it in widens the honest 50-net fresh-seed band
**[1.54e-7, 2.16e-7] -> [1.46e-7, 2.25e-7]** and raises **P(private > 2.5e-7) from
0.034% to 0.57% — 17x** [R, GEN8 §3 + ledger 260]. Still small; no longer negligible.

**What I could verify [D]:**

- The 9.83% is consistent with S1b's own model. Per-net relative variance is
  `vD + (1+vD)*vF`; at `vD = 0.08135950765` and `vF = 0.36419956287` that is
  0.475190, per-net CV 0.689340, SE of a 50-net mean `0.689340/sqrt(50) = 9.749%`;
  at vD = 0.1220 it is **10.302%**. So 9.83% sits inside the s17-implied bracket
  [9.75%, 10.30%]. Cross-check against the committed 1e6-suite SDs:
  `1.7856461794e-8/1.83e-7 = 9.757%` and `1.8871029898e-8/1.83e-7 = 10.312%` —
  agreement to three digits.
- **A second, external signal the record never used.** The hosted 50-net grade
  distribution for #326094 is committed: mean 1.832e-7, IQR [1.05e-7, 2.26e-7],
  min 5.42e-8, max 5.96e-7 [R]. Fit a lognormal with the model's per-net CV 0.68934:
  `sigma_log = sqrt(ln(1 + 0.68934^2)) = 0.623528`, median
  `1.832e-7 * exp(-sigma_log^2/2) = 1.5083e-7`, predicted IQR
  `median * exp(±0.6744898*sigma_log)` = **[9.905e-8, 2.2969e-7]** against the
  observed **[1.05e-7, 2.26e-7]** — Q3 within 1.6%, Q1 within 6%. The hosted
  distribution independently supports a per-net CV ≈0.69 and hence a ~9.8% SE on the
  50-net mean. This is my derivation, not in the record.
- **The widened band coincides numerically with an arm S1b already committed and
  rejected.** [1.46e-7, 2.25e-7] is, to the printed digits, S1b's `p2_high`
  50-net P5/P95 = [1.4601210108e-7, 2.2460012006e-7] [D]. Its committed tail is
  6.277e-3 = 0.63%, against Gen-8's 0.57%. Two different routes — folding the anchor
  SE at the s17-implied vD, or simply using the p2-implied vD — land on the same
  band. My §3.4 moment estimate (vD ≈ 0.134) sits between the two, which means
  **the corrections are additive in direction: a vD-corrected *and* anchor-corrected
  tail is above 0.57%.** I cannot put a number on it without the harness.

**What I could NOT verify — flag this to whoever quotes it [O]:**

1. There is **no committed harness directory** for the anchor-SE recomputation.
   `gm_c1_bound` has `PREDECLARATION.md`, four scripts and six JSONs; the anchor-SE
   result exists only as ledger record 260 + `GEN8_FORUM_INTELLIGENCE §3` +
   `AGENT_CHANNEL`. Level: **reported**, not observed. Settling check: one run of a
   modified `run_s1b.py` with the anchor drawn.
2. **The "0.034%" baseline does not match any committed S1b number.** S1b's 50-net
   `P(> 2.5e-7)` is 4.6e-4 (0.046%) at s17_low and 8.5e-4 (0.085%) at s17_high, and
   its own §5 headline says "≈0.05-0.09%". 0.034% is below both. The 17x factor is
   internally consistent with the two quoted numbers (0.57/0.034 = 16.76 [D]), but
   the pre-correction denominator is untraceable. If the baseline should have been
   0.046-0.085%, the true widening is **6.7x-12.4x**, not 17x [D].
3. `gm_c1_bound` DEVIATION 2 stands and applies here too: every C1 interval is
   local-side only; the hosted 6.470e-7 reference has no published error bar, so all
   reported CIs on R are **lower bounds on width**.

---

### 5. The competing public floor at 18105

Topic 18105 (arianvassili): a **Lean-4-machine-verified**, dipam-reproduced
"unbiased budget-respecting floor" of **~3.7e-7 adjusted** [R, `RESEARCH_INTEL` §2,
`GEN8_FORUM_INTELLIGENCE` §4]. Our graded **1.832e-7** at measured bias share
**-0.034** with zero unmetered compute beats it by
`3.7e-7/1.832e-7 = ` **2.0197x** [D].

The claim is not wrong; its scope is. It bounds **pure Monte Carlo** — the reason
dipam gives himself — and the champion is an **exact spherical design**, not MC.
The design's exact degree-≤2 integration removes the variance term the MC bound
prices, so an exact-design estimator is outside the bound's hypothesis class.
This is recorded as "the sharpest available paper citation for P1" [R]. Note the
adjacent fact from the same intelligence sweep: 18053 (evaaaz) puts unbiased
sampling at ~4.1e-7 adjusted at C/B 0.42, so 3.7e-7 is a tight bound *within* its
class [R].

Two boundaries codex-sol should hold when citing this: (i) the falsification is of
the bound's *applicability to exact designs*, not of the Lean proof; (ii) 1.832e-7 is
an **adjusted** score and 3.7e-7 is stated adjusted, so this comparison — unlike the
524x in §2 — is like-for-like.

---

### 6. N8c's zero-bias result, and why it makes the estimator correction-proof

N8c's G0 was the cheapest falsifier for an offline-trained per-neuron ridge corrector:
decompose the frozen Kerdock v3 final-layer error over its Haar-rotation seeds
(16 replicates, rotation seed `900000 + net_seed*1000 + r`, 3.5M-sample MC truth,
nets 101/202/303) into variance and bias^2. **KILL if bias^2 share < 25%**, because
a corrector's ceiling would then be < 1.33x [R].

Measured, governing (full-estimator) arm [R, `n8c_g0_results.json`]:

| net | MSE | variance (ddof0) | truth noise | bias^2 | bias share |
|---|---|---|---|---|---|
| 101 | 1.9869447670e-7 | 1.8600223559e-7 | 1.2312730025e-8 | **-1.2020637960e-8** | -0.06049810 |
| 202 | 5.3299344160e-7 | 5.1135273416e-7 | 2.2198818691e-8 | **-3.4648293529e-8** | -0.06500698 |
| 303 | 2.4019979789e-7 | 2.0551042135e-7 | 1.5034195541e-8 | **+5.9544862447e-9** | +0.02478972 |

Mean bias share **-0.03357178506**, bootstrap 95% CI **[-0.03087, +0.09710]**,
entirely below the 0.25 line. Cross-check arm (`plain_downstream`, a positively
homogeneous no-bias ReLU net on a fixed-radius Haar-rotated spherical set, exactly
unbiased in expectation by construction) gives -0.05342, consistent [R].
**Verdict: KILLED at G0. Kerdock v3's error is ~100% sampling variance; the
corrector has nothing to learn; ceiling ~1.0x. This closed the N-series — N6, N7,
N8a, N8b, N8c all killed at predeclared gates, the local honest program exhausted**
[R, ledger 188].

The side-finding is what matters for September. `bias^2` is *negative* on two of
three nets — the signature of a genuinely zero bias measured through estimation
noise. That converts directly into the private-re-run posture: `FAILURE_MODE_GRAPH`
node P0a, "zero-bias N8c -> nothing to overfit [E] STRONG", alongside P0b (on-budget
C/B 0.65) and P0c (no fitted component) [R]. P1 §3.2 states the mechanism: a
maximum-entropy unbiased field has **zero fitted structure to overfit**, so any
post-hoc correction fitted on one seed has nothing to latch onto that transfers —
and symmetrically, nothing to lose when the seed changes [R]. The estimator is
correction-proof because it is uncorrectable; the same measurement establishes both.

**Two scope conditions on "zero bias":**

1. It is scoped to the **scored final layer**. The same artifact's
   `all_layers_diagnostic` reports bias share **0.99993 / 0.99993 / 0.99993** with
   bias^2 6.8947e-4 / 1.0208e-3 / 6.6008e-4 [R] — i.e. across all layers the
   prediction is almost pure bias. Those magnitudes are the same order as T2's
   measured diagonal-Gaussian closure bias 7.18e-4 [R], which is consistent with the
   intermediate rows being carried by an analytic closure rather than sampled — but
   **I did not verify the champion's intermediate-row path**, and the attribution is
   an inference. Settling check: read the intermediate-layer branch of the frozen v3
   package. (For contrast, C1's own MC reference returns literal zeros for
   intermediate layers, "the same signature the observed hosted leaders show:
   all-layers MSE ~0.75" [R, `c1_local_mc_calibration/estimator.py:7-8`].)
2. The committed bootstrap CI **[-0.030873, +0.097097]** has a lower endpoint
   *above* the point estimate -0.033572, which is impossible for a percentile
   bootstrap of the net-level mean over these three values — enumerating all 27
   resamples, 8/27 = 29.6% of resample means are ≤ -0.0605, so the 2.5th percentile
   would be ≈ -0.065 [D]. The resampling unit is therefore not the net; most likely
   the 16 rotation replicates, but **the artifact does not record it**. This does not
   touch the verdict — the CI upper bound 0.0971 and the per-net maximum +0.0248 are
   both far below the 0.25 gate — but the interval should not be quoted as a
   net-level CI.

---

### 7. Open items for the blade

1. **Owed edits** to `S17_VERDICT.md`, `s17_results.json`, `PHASE1_WRITEUP_DRAFT`,
   `P1_SPECKLE_THEOREM` §"1.79x cost-matched or 0.90x distinct-direction", and
   `PASSES_AND_UNCERTAINTIES_GRAPH`: the three `gm_s17_reuse` corrections of §1.4.
   P1 currently carries the retired 0.90x.
2. **`S1B_DISPERSION_CORRECTED.md` provenance**: three occurrences of "hosted"
   describing a local-synthetic 80-net panel; repaired in writeup v8, not in the
   artifact.
3. **vD is probably ~0.134, not 0.081-0.122** (§3.4). One `run_s1b.py` re-run at
   vD = 0.134 with a random 9.83%-SE anchor settles both today's corrections at once
   and produces the number Phase 2 should actually plan against.
4. **The anchor-SE correction has no committed harness** (§4.2 flag 1) and its
   "0.034%" baseline is untraceable (flag 2).
5. **Committed compute figures disagree**: S17 uses 1.768e11 FLOPs / C/B 0.650;
   `GEN3_RECURSION_PACKET` records mean effective compute 1.79e11 = 65.9% of B;
   `GEN8_FORUM_INTELLIGENCE` says 65.01%. At 1.79e11 the derived FLOPs/forward moves
   2,740,575 -> 2,774,725, ednacob's affordable forwards 50,319 -> 49,700, its point
   floor 2.0176e-7 -> 2.0426e-7 and the generous bracket 2.2147x -> 2.242x [D].
   Immaterial to every verdict; material to anyone re-deriving Part C.
6. **Not in the record**: any CI on the 9.6e-5 closure plateau; the even/odd harmonic
   decomposition that would prove the 2x accounting gap; primitive-level independence
   for any `sigma^2` path; an explanation of the net-identity check's
   `ratio_obs_over_expected` 0.66/0.44/0.30.


---

## The M245 lane — Codex's own state

### 0. Sourcing stance for this section

Every hash, timestamp, byte count, and test name below was read this session from
the working tree at
`C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\publish\recursive-estimator-folding`.
Where a claim in `tasks/journal-m245-static-closure.md` is a numerical assertion, I
re-derived it from first principles in a scratch interpreter (stdlib + mpmath 1.4.1,
no m245 import, no execution of any m245 module, no git). Those derivations are
labelled DERIVED and carry their arithmetic. Read-only throughout; nothing in the
authority directory was touched.

Independent re-hash of all ten frozen files, run fresh this session, matches the
journal's frozen list byte-for-byte — this is the second signal for section (d) and it
also proves no post-run drift has occurred since:

```text
4087adad00ede51734f7368738267be05b34c85662572883f14dd96ca6752062   81432 B  m245_primary_core.py                 (P)
6ab33386ae985942b48b395eba7f78c724a3ad0805744b1ea42f3d31d8ab1326   49092 B  m245_replica_core.py                 (R)
3cce3474d1173c0252a8f2c98fc29a4404275cad0d988ace728a6639207e4047   37500 B  m245_scientific_worker.py            (W)
983e598ce97a56848103efb249b3a249e738a3b32c56c124392de15b17dfe2bf  193504 B  run_m245_scientific_shard.py         (S)
71abeebac9968d519d9dc2ea14cd760256a86f384fe4d5e6f3f4e7b06f4141bf   89121 B  launch_m245_scientific_invocation.py (O)
fc04e9258bb52e5171c54948c5451449e9c96a07a39c9bbab942982371d47c01  121588 B  aggregate_m245_spectrum.py           (A)
355820f372c0e0b7b466ed98f3db2a36b92142927c494406b3f5dbdb5c26d626           test_m245_primary_core.py
e7eceb023b725badb06d59773b7813d2083d3dfd33fffa7fd35fcedf2055fa21           test_m245_replica_core.py
112869bf75a127ae706dcc1346c070f128c15c74a125d1818646fbf46fd5294d           test_m245_scientific_transport.py
6d723cde0a9784cc20bf0a41b25ab4599f8c103f1c3de04cba0d6e8b9336a4e6           test_m245_aggregation.py
```

The I1.7 interpreter pin also re-verifies fresh:
`C:\Users\strid\.venvs\whestbench-frozen-m178\Scripts\python.exe`
= `4b8c3912806b3c1591ba3cb403bff77ad309c3fe5756f87c20b7a6f8f0174262`, identical to
AUTHORIZATION line 288. That venv carries mpmath 1.3.0 and numpy 2.4.6 (dist-info
directory names). My derivations ran on mpmath 1.4.1 — flagged in section (h).

---

### (a) Where the lane stood at the baton

Authority chain, all read in full:

- `M245_SCIENTIFIC_IMPLEMENTATION_AUTHORIZATION_20260810.md` — I1.1 through I1.9;
  I1.6 at line 260 (eight-point pre-GREEN static freeze), I1.7 at line 282 (four
  exact commands), I1.8 at line 325 (GREEN evidence), I1.9 at line 361 (mandatory
  stop).
- `M245_SCIENTIFIC_IMPLEMENTATION_ERRATUM1_20260810.md` — E1.6 at line 138 permits
  adopting/editing the six pre-written drafts and states the precondition chain:
  "No dummy GREEN command may run until this erratum is active, all six candidate
  bytes are frozen, and the complete I1.6 static gate independently passes."
  Erratum1 active at commit `76b446c075343b6b9633156f0d0617af5a417666`, parent
  `130391c`, docs-only, 2 files, 165 insertions (journal line 24).
- `M245_SCIENTIFIC_TRANSPORT_TEST_ERRATUM2_20260810.md` — E2.4 at line 136 carries
  the caller assignment verbatim: "The user-authorized operational handoff after
  Fable's session limit makes Codex `/root` the sole shard owner and external caller
  for M245. This sentence supersedes V1's operational assignment to Fable only; it
  changes no science, census, order, cap, or firewall. No Fable process, session,
  checkpoint, or uncommitted transcript is an execution dependency." Ownership block
  further down E2.4: Codex `/root` is the only external caller and may only launch O
  with exact argv/cwd/environment after the committed trigger.

Implementation-authority commit bound by the receipt builder:
`9886acd7d1eb9f7e887bed70c516e6b0de22b58b`.

Pre-repair source hashes at baton time (journal line 17):

| role | file | baton SHA256 (prefix) | changed by repair? |
|---|---|---|---|
| P | m245_primary_core.py | `d0296d5e` | yes -> `4087adad` |
| R | m245_replica_core.py | `6ab33386` | no |
| W | m245_scientific_worker.py | `3cce3474` | no |
| S | run_m245_scientific_shard.py | `eb561076` | yes -> `983e598c` |
| O | launch_m245_scientific_invocation.py | `eb5b794f` | yes -> `71abeeba` |
| A | aggregate_m245_spectrum.py | `fc04e925` | no |

Frozen test set at baton (journal line 16, I1.1): P-test `355820f3`, R-test
`e7eceb02`, transport `112869bf`, aggregation `6d723cde` — all four still byte-identical
at freeze and still byte-identical now.

Lane posture at the baton, from the channel: HOLD on everything real — no shard,
census, trigger, aggregation, provider, or fixture decode (journal lines 9-11). The
08:44 UTC channel entry states plainly "Zero GREEN consumed to date." The 08:36 UTC
lane division put the bridge instance in sole possession of the m245_* files; the
primary Fable lane declared it would not touch them.

DERIVED (mtimes, local -0500 = CDT, so +5h = UTC): last write to R was 06:32 UTC,
W 08:01 UTC, A 08:19 UTC; the four tests last changed 05:03-05:20 UTC. S/O/P were last
written 10:07:13 / 10:07:43 / 10:06:59 UTC — roughly 30 minutes before command one
started. No source or test file has been written since. This corroborates I1.6's
immutability clause independently of the hashes.

---

### (b) The seven static blockers and the mechanism that closed each

The baton's own enumeration of the seven hostile-audit blockers is **not in the
record** — it arrived through the Maestro-injected bridge prompt and was never
mirrored into `AGENT_CHANNEL.md` or any committed doc. What survives is the
journal's REPAIRS APPLIED entry (line 29), which names the mechanism per blocker.
Repair budget: S x10 apply_patch edits, O x8, A none. A was cleared without edits
because `_validate_production_entry` (A:2515) already binds GetCommandLineW argv,
flags, interpreter, cwd, and source hash, and the aggregation test never calls
`A.main` (journal line 28).

I confirmed each repair's symbols are present in the frozen bytes (grep counts,
this session, S / O / A):

| # | Blocker (as inferable from its repair) | Mechanism that closed it | On-disk evidence |
|---|---|---|---|
| 1 | Trigger verification did not bind the activated authority or the frozen test lineage | `ACTIVATED_AUTHORITY_SHA256` (auth .md/.txt `46ba45dc`/`e0cd1409`, erratum1 .md/.txt `5d089084`/`7bd73b14`, RED-V2 sums `669df011`) + `FROZEN_SCIENTIFIC_TEST_SHA256` + GREEN receipt/checksum structural lineage, verified live and against the GO blob at the end of `verify_committed_trigger` (S) and `_independently_verify_trigger` (O) | `ACTIVATED_AUTHORITY_SHA256` S=2 O=2; `FROZEN_SCIENTIFIC_TEST_SHA256` S=3 O=3 |
| 2 | Static-audit schema unpinned and audited-file map unconstrained | exact audit schema keys `artifact` / `audited_source_sha256` / `reviewer_id` / `schema` / `status`, and audited map == sources minus the 3 self names, in **both** S and O | schema constants present in both; reviewer B's mechanical AST schema diff across all schema constants returned zero drift |
| 3 | Post-finish re-validation ran after the terminal state was sealed (self-validating layers) | S: post-finish `_validate_meter_stream` and `validate_invocation_receipt(receipt, ...)` removed; `_resource_meter_from_raw` split into a validating wrapper plus a pure `_resource_meter_reductions`. O: post-finish reindex loop, `_validate_meter_stream(outer)` and self `validate_terminal_witness` removed | `_resource_meter_reductions` S=3 O=0 |
| 4 | No global ownership census before writing — temp dirs, non-regular files, and artifacts without an intent could be adopted | preflight global ownership census: `owner_by_name` map, temp refusal, non-regular-file refusal, artifact-without-intent refusal | `owner_by_name` S=4 (S-only) |
| 5 | The production authority union was not pinned to an expected set | `_EXPECTED_PRODUCTION_AUTHORITY_UNION` global checked inside `_validate_authority_union`; set in S's production path and set by O on the loaded supervisor | S=5 O=1 |
| 6 | Process self-identity was taken from `sys.argv` (mutable, post-parse) rather than the OS command line | `_observed_windows_command_line_argv` (GetCommandLineW + CommandLineToArgvW, mirroring A's existing implementation) plus `sys.orig_argv`, flags, executable, and cwd binding in S main, S census mode, and O main; census payload argv is the verified actual `orig_argv` | `_observed_windows_command_line_argv` S=2 O=2 A=2; `GetCommandLineW` S=3 O=3 A=3; `orig_argv` S=2 O=1 |
| 7 | S accepted the worker's reported ladder and curve report without recomputing them | `_validate_reported_primary_ladder` (exact `Fraction` pins on c-residual, P, V, V_beta, the beta identity, the tolerances and energy bounds, plus a float64 Jacobi eigenrange bounded by Weyl) and `_float_classify_curve_ladder` port + `_validate_reported_curve_report` (label taken from the reported gate evidence, every field pinned to recomputation); all called at the end of `_validate_scientific_ledger_bindings` | all three symbols S=2/2/2, `_validate_scientific_ledger_bindings` S=3 |

Blocker 7's placement is load-bearing and deliberate: the transport test's dummy
ladder numbers are inconsistent stubs, so the recomputation had to live strictly
inside the production-only path (`_validate_scientific_ledger_bindings`) or it would
have killed the dummy suite (journal line 27).

Constraint the repairs had to respect, extracted from the transport test by full
read (journal line 27): the tests never call `main`, `census`,
`verify_committed_trigger`, or `load_and_verify`; they never pass a third argument to
`validate_invocation_receipt`; the import check is a forbidden-prefix list only; only
`build_final_shard_receipt_from_files` has a frozen signature; and the trigger,
authority, and source key tuples are hardcoded in the test, so **schema extension is
forbidden**.

Static falsifier after the last edit (journal line 30): `ast.parse` clean on both
files, stdlib-only imports, zero forbidden prefixes, zero `mp.quad` owners.

---

### (c) The three compatibility failures the pre-freeze fleet found

Five agents ran pre-freeze. Hostile audit: 0 blockers, 2 RISK, 2 NOTE. The RISKs were
(i) O's independent layer weaker than S's — fixed by pinning assignments, commit,
audit path, reviewer, and census path inside `_independently_verify_trigger`; and
(ii) witness validators relying on caller pre-validation — documented rather than
fixed, because the frozen signatures forbid the change. The NOTEs (curve-port
fail-closed divergence, eigenvalue absolute tolerance) were accepted. R compat =
PASS with two runtime-risk notes; A compat = PASS.

Transport compat = COMPAT_FAIL, one item. The frozen test's `_identity()` helper
(test lines 517-571) hardcodes `kernel_time_100ns = 10_000` and
`user_time_100ns = 20_000` for **every** role, while the meter's final sample carries
L = kernel 12000 / user 8000 and W = kernel 18000 / user 12000 (test lines 633-634,
638-639, 643-644). S's unconditional exact-equality check between identity and meter
CPU counters would have killed 6 of 23 transport methods. Repair: the L/W counter
equality is now gated on `production_paths`, mirroring O's absolute-path gating,
while `exit_code` equality stays unconditional. Verified in the frozen bytes at
S:2798-2809 —

```text
identity["exit_code"] != observation["exit_code"]
# Exact CPU-counter equality with the final raw sample is a
# production binding (sealed after exit); the frozen dummy
# fixtures carry synthetic counters, on the same absolute-
# path axis O uses for its outer-meter identity checks.
or ( production_paths and ( identity["kernel_time_100ns"] != observation["kernel_time_100ns"]
                         or identity["user_time_100ns"]   != observation["user_time_100ns"] ) )
```

with `production_paths` derived at S:2734-2736 from whether the intent publication
path is absolute. Post-fix the full receipt/witness/final trace passes and all 18+
`assertRaises` mutations still raise.

P compat = COMPAT_FAIL x3. All three are numerically real, all three were confirmed
by my own exact arithmetic this session.

**(1) precision_gate binary64 re-rounding.** Test line 645 requires
`primary.precision_gate(1.0e6, 1.0e6 + 2.0e-6)` to be True. `_gate_mpf` (P:450-460)
deliberately routes floats through their `repr` spelling: `mp.mpf(repr(value))`. At
prec53 that parse re-rounds the decimal back onto the same binary64, so the gate
compares the binary64 values, not the spellings.

DERIVED, exact rationals:
```text
repr spellings         : "1000000.0" and "1000000.000002"
decimal-parsed |low-high| = 2e-06 exactly
tolerance 2e-12*max(1,|high|) = 2.000000000004e-06
ELEVATED-PRECISION verdict = True
prec53 re-rounded |low-high| = 2.00001522898674e-06   (excess over 2e-6: 1.5228986740112303e-11)
PREC53 verdict = False
```
The excess is 7.6e-6 relative to the tolerance — a genuine failure, not marginal.
Repair: `with mp.extraprec(100):` wrapping the whole gate body (P:467), so
`mp.mpf("1000000.000002")` is held at 153 bits and the comparison is made at the
stated decimal boundary. Present in the frozen bytes at P:463-477.

**(2) ladder_energy monotonicity violation invisible at prec53.** Test lines 661-672
build K = 10.0, tau = 2.0e-10 * K = 2e-9, P = [1.0 .. 9.0], then sets
`bad[4] = bad[3] - math.nextafter(tau, math.inf)` and asserts the gate refuses it. The
intended violation is exactly one ulp of 2e-9.

DERIVED:
```text
tau                        = 2e-09
nextafter(tau, +inf)       = 2.0000000000000005e-09
intended violation (1 ulp) = 4.1359030627651384e-25
bad4 = fl(4.0 - nextafter(tau,inf)) = 3.999999998
fl(4.0 - tau)                        = 3.999999998     <-- bitwise identical
=> at prec53, bad4 >= P[3] - tau evaluates TRUE, gate passes, assertFalse FAILS
exact bad4 - (4 - tau)     = -400107883/2417851639229258349412352
                           = -1.6548074187361756e-16
```
The realized violation (-1.65e-16, from rounding the subtraction 4.0 - 2.0000000000000005e-9
into the binade below 4) is nine orders of magnitude larger than the intended one, and
is entirely erased when `P[3] - tau` is itself evaluated at prec53. Repair:
`with mp.extraprec(100):` around the bounds/monotonicity/endpoint comparisons (P:875),
with `tau` deliberately computed **outside** the extraprec block (P:870) because it is
a reported artifact value and test line 668 asserts `verdict["tau_K"] == tau` against
the float. That split is visible in the frozen bytes and is annotated in the source
comment at P:871-874.

**(3) gaussian_interval_moments erf spelling.** The finite block of test line 528-541
uses a = -0.75, b = 1.25, max_degree = 20, and a float reference built from
`math.erf` and the same three-term recurrence, checked at `places=13`. The production
`cdf_endpoint` originally used the erfc spelling that `_normal_cdf` (P:275-277) uses
for tail safety. A high-precision fix was proven impossible: `places=13` fails degrees
10-20 even for an exactly-correct module, because the test reference itself diverges
from the true moments. The only remaining move was to make production reproduce the
float reference bitwise.

DERIVED at prec53, mpmath 1.4.1:
```text
endpoint a = -0.75 : erf-spelling 0.2266273523768682  erfc-spelling 0.2266273523768682  math.erf ref 0.2266273523768682
endpoint b =  1.25 : erf-spelling 0.8943502263331446  erfc-spelling 0.8943502263331448  math.erf ref 0.8943502263331446
pdf at both endpoints: mp.exp/mp.sqrt spelling == math.exp/math.sqrt reference, bitwise

seed v[0] = cdf(b) - cdf(a):  erfc spelling is 2.220446049250313e-16 high (exactly 2 ulp)
amplification v[0] -> v[20] is 1*3*5*7*9*11*13*15*17*19 = 19!! = 654,729,075
predicted degree-20 error = 654729075 * 2.2204e-16 = 1.453790587913062e-07

erf  spelling: bitwise-mismatched degrees = []          max |diff| vs testref = 0.0
erfc spelling: bitwise-mismatched degrees = [0,2,4,...,20]  max |diff| = 1.4539302739535742e-07
               places=13 violated at degrees 10,12,14,16,18,20
```
The journal's "diverges by up to 1.5e-7" is exactly the 19!! amplification of a single
2-ulp erfc seed. Repair: `cdf_endpoint` respelled to `(1 + mp.erf(x / mp.sqrt(2))) / 2`
(P:350), with the erfc spelling retained in `_normal_cdf` for tail-safe scientific
paths. Present in the frozen bytes with the reason recorded in the comment at
P:347-349. The sole other production call site of `gaussian_interval_moments` is
`_integrate_polynomial_gaussian` (P:811); the tail-cancellation analysis found no gate
impact at 80 or 100 dps.

Runtime confirmation, which is stronger than any of the above: cmd1 ran all three of
the tests these fixes target and reported `ok` —
`test_precision_gate_has_the_exact_relative_floor` (cmd1.err line 25),
`test_energy_ladder_gates_include_bounds_and_monotonicity_on_dummy_data` (line 23),
`test_gaussian_interval_moment_recursion_has_explicit_half_normal_factor` (line 12).

---

### (d) The frozen hashes and the two independent static PASS verdicts

Final frozen six, re-verified this session (full digests in section 0):
P `4087adad`, R `6ab33386` (unchanged), W `3cce3474` (unchanged), S `983e598c`,
O `71abeeba`, A `fc04e925` (unchanged). Three of six moved; R, W, A are byte-stable
from the baton.

**Reviewer A, authority-first.** Recomputed all ten hashes exact. I1.6 points 1-8 all
PASS with file:line citations. Blocker 1-7 closure PASS with file:line. Re-derived the
sharp edges independently: the extraprec gate arithmetic, the `tau_K` bit-equality
(`mpf('2e-10') * mpf(10)` at prec53 == `2.0e-10 * 10.0`), the erf@53 == math.erf
equality at +/-0.75 and 1.25 over sqrt(2), and the L/W counter gating plus mutation
reachability.

**Reviewer B, test-first.** All ten hashes exact. Per-method verdicts across all test
methods in the four suites: zero statically-detectable failures. Mechanical AST schema
diff across every schema constant: zero drift. Legality PASS under I1.4 and I1.6,
E1.3-E1.6, and E2.3-E2.10. No fail-open, no `exec`/`eval`, no shell, no import-side
effects. Reviewer B classified **~22 methods as bounded numeric-runtime-risk inherent
to live quadrature** — risk it could not resolve without executing, which the static
gate forbade. Reviewer B also disclosed a transient `_tmp_schema_dump.json` it created
and deleted in the authority directory; the journal's next-action line requires a fresh
cleanliness re-verify before GREEN.

Journal line 44: "GREEN AUTHORIZATION SATISFIED per E1.6: erratum1 active (76b446c),
six candidate bytes frozen, I1.6 static gate independently passed twice."

One counting discrepancy, flagged not resolved: the journal records reviewer B
triaging "all 92 test methods in 4 suites." My own count of `def test_` in the four
frozen tests is **91**: primary 31, replica 23, transport 23, aggregation 14. The
primary count is corroborated exactly by cmd1's "Ran 31 tests". The off-by-one is
either a miscount in the journal summary or a counting convention that includes a
`setUpClass`; either way it does not touch any hash or verdict.

---

### (e) The GREEN execution facts

`tasks/m245_green_driver.ps1` (33 lines) runs the four I1.7 commands serially via
`Start-Process -Wait -PassThru` from the authority cwd with the pinned interpreter,
redirecting stdout/stderr per command, appending one pipe-delimited row to
`progress.log` **after** each process exits, breaking on the first nonzero exit, and
writing a `DONE` marker at the end.

`tasks/m245-green-logs/` currently holds exactly five files. There is no `DONE`, no
`cmd3.*`, no `cmd4.*`.

```text
cmd1.out       0 bytes
cmd1.err    5800 bytes  36 lines  sha256 95b10f38c05e732266d5ae5987a33c1039efc1c60654ce6ed39b5d27eade351e
cmd2.out       0 bytes
cmd2.err    3049 bytes  15 lines + one unterminated 16th
                        sha256 210358b53281c6a0163d3727aa9fd086f10f2f09af2741477facd6ceaf1b1d34
progress.log  89 bytes  sha256 109a646519ee08cf935edec42f7036156a5233b13e9c159be0b727944bab965c
```

**progress.log holds exactly one row:**
```text
1|test_m245_primary_core.py|2026-08-10T10:37:07.8232896Z|2026-08-10T10:46:23.3277048Z|0
```

**cmd1** — `test_m245_primary_core.py`, exit 0, `Ran 31 tests in 554.267s` / `OK`
(cmd1.err lines 34-36). All 31 methods report `ok`, including the four
`TestM245PrimaryResultContract` methods whose `setUpClass` (test lines 733-744) calls
`primary.run_primary_event` once per `PRECISIONS_DPS` entry with a `_DummyQuadGateway`
— that is, the primary side of the exact live-quadrature pattern that failed on the
replica side. DERIVED: the driver-recorded interval is 555.5044152 s wall against
unittest's 554.267 s internal, a 1.2374 s difference attributable to interpreter
startup and teardown.

**cmd2** — `test_m245_replica_core.py`. Log line 7 reads
`setUpClass (test_m245_replica_core.TestM245ReplicaGatesAndSchema) ... ERROR`, and
tests continue to report `ok` at lines 8 through 16. unittest's default loader takes
classes in `dir()` order, which is alphabetical, so the sequence in the log is
TestM245ReplicaAuthorityAPIAndFirewall (6 methods, lines 1-6, all ok), then
TestM245ReplicaGatesAndSchema (line 7, class-level ERROR — its 7 methods are not run),
then TestM245ReplicaIndependentMath (10 methods, lines 8-16). The ERROR therefore fired
during normal execution, six passing tests in and eight passing tests before the end of
the artifact. It is not a kill artifact.

**No traceback exists in the artifact.** unittest defers tracebacks to the end-of-run
error summary, which requires the run to complete. It did not. The specific exception,
its type, and its line are unrecoverable from what is on disk; obtaining them requires
a rerun, which I1.7 forbids.

The errored locus, read from the frozen test at lines 566-587:
```python
class TestM245ReplicaGatesAndSchema(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.dummy = _varying_dummy_event()
        cls.gateways = {}
        cls.results = {}
        for dps in PRECISIONS_DPS:                       # PRECISIONS_DPS = (80, 100)
            gateway = _DummyQuadGateway(replica.mp)
            scope = replica.cache_scope_id(shard_id=97, invocation_index=1,
                                           event_id=cls.dummy["event_id"],
                                           engine="replica", precision_dps=dps)
            cls.gateways[dps] = gateway
            cls.results[dps] = replica.run_replica_event(cls.dummy, dps,
                                                         quad_gateway=gateway,
                                                         cache_scope_id=scope)
```
This is live mpmath quadrature at 80 and 100 decimal digits, not a contract or schema
check — exactly the class reviewer B flagged and could not statically resolve.

Two static observations that narrow the space without diagnosing it:

- `run_replica_event` and `cache_scope_id` signatures in the frozen R
  (R:816-822 and R:490-497) match the call sites exactly, keyword-for-keyword, so a
  plain signature mismatch is excluded.
- `run_replica_event` has **exactly two** call sites in the whole replica suite:
  this `setUpClass` at test line 582, and
  `test_run_replica_event_mu_uses_both_asymmetric_sign_branches_end_to_end` at test
  line 529. The setUpClass call was the first execution of that function in the
  process. The second call site is the test that was in flight when writing stopped.

**New forensic timing, DERIVED from file mtimes (local -0500 = CDT; cross-checked
against progress.log, where cmd1.out's creation mtime 10:37:07.858 UTC sits 35 ms after
the driver's recorded start stamp 10:37:07.8232896Z, and cmd1.err's last write
10:46:22.590 UTC sits 0.74 s before the recorded end 10:46:23.3277048Z):**

```text
cmd2.out / progress.log created  2026-08-10 10:46:23.343 UTC   <- cmd2 launched
cmd2.err last write              2026-08-10 14:20:52.281 UTC
elapsed before writing stopped   3 h 34 m 28.94 s  = 12,868.94 s
ratio to cmd1                    23.2x, on 23 methods vs 31
```
Because Python line-buffers stderr and `TextTestResult.startTest` writes and flushes
the `"... "` prefix before the test body runs, that 14:20:52 UTC stamp is the moment
`test_run_replica_event_mu_uses_both_asymmetric_sign_branches_end_to_end` **began**, not
the moment the process died. The process was alive at 14:20:52 UTC, 3h34m into the run,
and produced no further output. When it actually terminated is not determinable from
the artifacts. Jonah restarted the machine at some point before the 22:01 UTC channel
entry, and the bridge's session file was cold from roughly 20:40 UTC.

No cmd2 row was ever appended to progress.log, so **the driver never observed an exit
code for cmd2**, and the driver process itself did not survive to write `DONE`.
cmd3 and cmd4 never started; the driver's `Start-Process` for them was never reached.

Census corroboration, all read-only this session:
- No `M245_SCIENTIFIC_TDD_GREEN_RECEIPT_20260810.md` and no
  `M245_SHA256SUMS_SCIENTIFIC_TDD_GREEN_20260810.txt` exist in the authority directory.
- `__pycache__/` in the authority directory contains only three fixture-materialization
  lane `.pyc` files (`materialize_m245_fixtures`, `supervise_m245_fixture_materialization`,
  `test_m245_fixture_materialization_transport`) — none of the six sources and none of the
  four frozen tests, corroborating that `-B` was honored and the GREEN run published
  nothing.
- All ten hashes are unchanged from the freeze, so `BLOCKED_GREEN_HASH_DRIFT` does not
  apply.

`tasks/m245_green_receipt_builder.py` (200 lines, stdlib-only) cannot manufacture a
receipt from this state and refuses on four independent guards: `DONE` must read
`GREEN_ALL_ZERO` (line 60), progress.log must be the exact four-row serial record in the
frozen order (line 66), every row must be exit 0 (line 68), and the post-run hashes must
match the frozen ten (line 70). The first three fail today. The GREEN evidence path is
structurally closed, not merely unexercised.

---

### (f) The open adjudication, stated neutrally

The question is whether the cmd2 `setUpClass` ERROR consumes the one-shot. I state the
governing text and the facts; I do not recommend an answer. This is Codex's call under
its own erratum chain, or Jonah's.

**What I1.7 says, verbatim (AUTHORIZATION lines 313-319):** "No combined discovery,
parallel runner, coverage wrapper, pytest, alternate interpreter, alternate cwd,
environment injection, test selection, skip, expected-failure conversion, or second
attempt is authorized. A nonzero exit, hang, source/test drift, real event access,
unexpected authority-directory publication, or real-namespace creation is a binding
`FAIL_IMPLEMENTATION_GREEN_STOP_NO_RERUN`. It is not permission to patch and try again;
a new append-only repair authority would be required."

**Facts that bear on it:**

1. The ERROR is real and occurred during normal execution — six tests passed before it,
   eight after it. It is not an artifact of the interruption.
2. No exit code for cmd2 exists. The trigger enumerated in I1.7 is "a nonzero exit";
   cmd2 never produced one. A completed unittest run containing an ERROR would have
   exited 1, but that run never completed.
3. "hang" is in the enumerated trigger list, and cmd2 was still alive 12,868.94 s in,
   23.2x cmd1's total. I1.7 sets **no** time bound, and no timeout for the GREEN
   commands appears anywhere in the record. Whether 3h34m+ on a 23-method suite
   constitutes a hang is a judgment I1.7 does not make.
4. The nearest "an exception consumes the attempt" language in the chain is E2.3
   ("Failure, timeout, exception, nonfinite/over-threshold quadrature error, resource
   breach, publication failure, or hash drift consumes that unique attempt and yields
   the existing binding local-kill disposition. It never opens a replacement, third
   invocation, retry, redraw, or reseed."). That sentence sits under the heading
   "Meaning of the eight-launch cap" and governs the eight shard invocations, **not**
   the four GREEN commands. Whether it is read as an analogy or as inapplicable is part
   of the adjudication.
5. I1.8 gates receipt creation on "all four commands exit zero." One command exited
   zero; one produced no exit; two never ran. No path to a receipt exists on this
   evidence without a new authority.
6. Nothing has been rerun. Nothing has been patched. The ten hashes are intact.

**Status of cmd3 and cmd4:** never started, never launched, no logs, no exit codes.
`test_m245_scientific_transport.py` (23 methods, the suite the L/W counter-gating repair
was made for) and `test_m245_aggregation.py` (14 methods, A untouched since the baton)
are entirely unexercised. Whether they are still runnable under this authority depends
on the same adjudication: if the cmd2 ERROR consumed the one-shot, the run set is closed
at `FAIL_IMPLEMENTATION_GREEN_STOP_NO_RERUN` and a new append-only repair authority is
required for anything further; if it did not, the question of whether cmd3 can start
without cmd2 having a recorded verdict is itself unaddressed by I1.7, which specifies
only "serially and in this order."

---

### (g) What is not in the record

- The baton's own enumeration of the seven hostile-audit blockers. It exists only as
  the repair descriptions in the journal.
- The cmd2 traceback, exception type, and failing line. Unrecoverable without a rerun.
- The exact wall-clock moment cmd2's process terminated, and whether it terminated by
  the machine restart or on its own.
- Any timeout, time bound, or hang threshold for the four GREEN commands.
- Reviewer A's and reviewer B's full reports. Both are described in the journal as
  "subagent reviews recorded in channel/journal only"; per journal line 20 the
  `M245_SCIENTIFIC_STATIC_AUDIT_A/B` JSON artifacts were deliberately not created,
  because they belong to the later post-GREEN I1.9 trigger sequence.
- Any M245 record in `corpus/whestbench/headroom/fold_ledger.json`. That file carries
  264 candidates; six mention M245 in passing (`s17_information_complexity_lower_bound`
  and `recursion_convergence_certificate`, both screened; `gen7_svdv_rotation_construction`,
  `gm_ecn_psi`, `gm_flatworm_response_ladder`, `gm_s17_reuse`, all killed). The M245 lane
  itself holds no ledger candidate — it is a measurement lane, not an estimator mutation.

### (h) Verification caveats

- My erf/ladder/precision derivations ran on mpmath **1.4.1** in a scratch interpreter.
  The frozen venv carries mpmath **1.3.0**. The claims I reproduced are about
  correctly-rounded prec53 evaluation and are not expected to be version-sensitive, but
  I did not verify them under 1.3.0, and I deliberately did not execute anything in the
  frozen venv. The authoritative signal for the three P fixes is cmd1's `OK` on the
  frozen venv itself, which I did not produce and cannot reproduce.
- The mtime-based timing in section (e) assumes the file timestamps are original write
  times rather than checkout times. Cross-checking cmd1.err's mtime (10:46:22.590 UTC)
  against progress.log's independently recorded cmd1 end (10:46:23.3277048Z) confirms
  original write times for at least that file, and the -0500 offset is confirmed by the
  cmd1.out creation stamp matching the recorded start to 35 ms.
- I did not run git and therefore did not confirm which of these files are committed;
  the 23:49 UTC channel entry states the journal, driver, receipt builder, and raw
  cmd1/cmd2 logs were committed.
- The "92 test methods" figure in the journal disagrees with my count of 91.


---

## The method and the defect taxonomy

All of this was committed after you went offline. The two ladders are new
(`core/GEN8_LADDERS_20260810.md`); the promotion rule they imply was revised
inside that same document after an independent audit contradicted its first
draft (`experiments/gen8_gate_audit/GATE_AUDIT.md`); three confirmed defect
classes were found in our *own* record on 2026-08-10. Ledger state, re-derived
rather than quoted: `headroom/fold_ledger.json`, 549,205 bytes, sha256
`387d0c6f44eb2e14d8ed08871c89671f179af50c3b2c3243f5eaee006937a4a4`, **264
candidates** (124 `killed`, 38 `screened`, 2 `promoted`, 1 `validated`, rest
legacy compound statuses). The audit below is pinned to sha256 `60c9c72a…`,
546,363 bytes, 263 candidates — correct at its pin, one record stale now.

### 1. Ladder R — recursion, ordered by cost of inquiry

Answers *is this true?* **Stop at the first rung that RESOLVES.** Escalate only
on inconclusive.

| rung | what it is | cost | resolves when |
|---|---|---|---|
| R0 | ARITHMETIC — closed form, or arithmetic on numbers already committed | minutes, no compute | the answer falls out of algebra (DGS bounds, break-even) |
| R1 | CACHED — recompute from committed artifacts, no new truth generation | minutes | committed data already contains the answer |
| R2 | SCREEN — new measurement at screen scale (small width, few nets) | ~CPU-hour | the effect is absent or overwhelming at screen scale |
| **R3** | **TRANSFER — the same measurement at >= 2 scales spanning the production gap** | 2–3x R2 | the effect's scale-dependence is *established*, not assumed |
| R4 | PRODUCTION — full width, full suite, pinned seed, CRN, twice-run determinism | hours | the effect survives at the real operating point |
| R5 | ADVERSARIAL — independent agents mandated to refute the surviving claim | fleet | the majority fails to break it |
| R6 | OWNER GATE — irreversible, outward-facing, or a genuine scope fork | Jonah | he decides |

R3 is the only new rung; everything else is our existing promotion/resolution
discipline written down. The width-transfer proposal, in its correct
generalization, is exactly the rule *you may not skip R3 on the way to
promotion.*

Worked instance, so R1 is not an abstraction: U-M3 (was cmd2's `setUpClass ...
ERROR` environmental or a genuine contract failure?) resolved without a re-run.
The ERROR prints at line 7 of `cmd2.err` while tests keep passing at lines
8–16, so it fired during normal execution well before the process died; its
locus is `TestM245ReplicaGatesAndSchema.setUpClass` (test file lines 568–587),
which calls `replica.run_replica_event(...)` once per `PRECISIONS_DPS` entry —
live mpmath quadrature at multiple precisions, exactly the class reviewer B
flagged ("~22 methods classified bounded numeric-runtime-risk inherent to live
quadrature"). The traceback is **unrecoverable** from the artifact (unittest
defers tracebacks to an end-of-run summary never written), so the cause cannot
be had without a re-run the one-shot protocol forbids. Net: a genuine runtime
error in a pre-accepted risk class, cause unrecoverable. Disposition (U-M1,
U-M2) is yours or Jonah's.

### 2. Ladder P — perturbation, ordered by measured yield

Answers *where does this stop being true?* **Stop at the first rung that
BREAKS it — that rung IS the answer**, because it names the claim's domain of
validity. Rungs are ordered by how often each has actually broken something in
our record.

| rung | perturbation | what it has broken in our record |
|---|---|---|
| P0 | SEED — re-run under a different seed, CRN-paired | sampling artifacts; the Gen-7 SVD-V null needed this to be readable at all |
| **P1** | **WIDTH — n = 4 / 32 / 64 / 128 / 256** | trace-share dilution; PSD loss; the six *suspected* corpses (see §5) |
| P2 | DEPTH — L = 4 / 8 / 16 / 32 | closure accumulation; the 0.87/layer transmission law |
| P3 | DTYPE / COST — f32 vs f64, v0.10.0 pricing, stats-promotion contagion | billing regime, not mathematics; the live 64-callsite hazard |
| P4 | SUITE — net families, difficulty strata, public vs private | every decision-layer claim; C1's mean/median artifact lives here |
| P5 | INSTRUMENT — can the measuring code return a null/zero regardless of truth? | **M183**; the highest-yield rung and the one we had no gate for |
| P6 | ADVERSARY — an agent whose only mandate is to refute | "9 of 9 Gen-8 proposals; 20 of 20 Gen-7 attacks" (see §8 for what that number does and does not mean) |

### 3. The asymmetry — why these are not one ladder with two names

|  | Ladder R | Ladder P |
|---|---|---|
| question | is it true? | where does it stop being true? |
| direction | escalating **cost of inquiry** | escalating **severity of stress** |
| stopping rule | stop when RESOLVED (cheapest sufficient rung) | stop when BROKEN (the breaking rung is the result) |
| a "pass" means | established at that evidence level | survived to that rung — boundary is the *next* one |
| cost profile | most questions stop early; cheap by design | a claim that never breaks costs the **full** ladder |
| characteristic failure | stopping early on a cheap signal that is wrong | perturbing the wrong axis → **false robustness** |
| output | a verdict with an earned evidence level | a boundary condition attached to the claim |

Three consequences worth stating as theorems about the process rather than as
advice:

1. **R is exhaustible; P is not.** R terminates when the question is answered.
   P has no natural terminus — another perturbation can always be invented —
   so P requires a *declared* rung list plus an honest statement of which rungs
   were not run. An unstated P rung is exactly the mechanism by which false
   robustness enters the record.
2. **R's rungs are ordered by cost; P's must be ordered by measured yield.**
   Ordering P by intuition is what produced a width-only proposal. Width is
   genuinely rung 1 by measured evidence; P5 (instrument) outranks P2–P4 on
   2026-08-10's data and was on nobody's list at all.
3. **They compose asymmetrically.** R gets you a claim; P gets you the claim's
   domain; a promotion needs both. The gap the parallel session found is a
   claim resolved at R2 that was never given a P1 boundary. M183 is the mirror
   image: a claim resolved at R2 that was never given a P5 boundary.

### 4. The revised promotion rule, and the fact that nothing enforces it

A candidate may not be promoted unless **all four** hold:

1. **R-sufficiency** — resolved at the rung its stakes require, with the rung
   named in the record.
2. **R3 crossed on the mechanism's OWN declared sensitivity axis** — the
   load-bearing statistic measured at >= 2 points along whichever axis the
   mechanism's effect is *claimed* to depend on, with the extrapolation to the
   production point reported as an interval and gated on its **unfavourable**
   end. The axis is declared in the predeclaration, before measurement. Where
   the axis is width, >= 3 points or a rank statistic, not a two-point line.
3. **Evidence at production shape, plus the instrument-validity gate** — no
   detector may produce a promotion- or kill-bearing null unless it fired on a
   positive fixture *in the same run*.
4. **Unrun P rungs declared** — the record names which perturbations were not
   attempted. Silence is not robustness.

Kills remain final. Nothing here reopens a killed record; it raises the bar for
promotion only, which is the direction that has cost us.

**Open, and cheap to close.** This rule exists in prose only.
`scripts/fold_ledger.py::audit()` requires `mechanism`, `bias_class`,
`prediction`, `kill_condition` on every candidate, and for
`validated`/`promoted` additionally `artifact_hash`, `matched_units`,
`primary_effect`, `ci_upper`, `failures` (plus `failures == 0`, `ci_upper < 0`,
`holdout_used_for_generation == False`). There is **no** field for a declared
sensitivity axis, none for the R-rung, none for unrun P rungs, and no
instrument-validity assertion; grepping `scripts/`, `tests/`, `headroom/` for
`sensitivity_axis`, `declared_axis`, `unrun_p`, `instrument_valid`,
`positive_fixture` returns zero hits. Across all 264 candidates the observed key
set is `id, status, mechanism, bias_class, prediction, kill_condition, result`
(260/264 carry `result`) plus `status_note` (33), `artifact_hash` (26),
`matched_units`/`primary_effect`/`ci_upper`/`failures` (16 each),
`holdout_used_for_generation` (3), `sensitivity` (3). Clauses 2–4 are
unenforceable by the audit script as it stands; the only field anywhere in the
neighbourhood of a declared axis is `sensitivity`, present on 3 of 264.

### 5. The width gate — the method catching a plausible-but-wrong proposal

#### What was proposed

From the parallel branch (`claude/repos-agentic-frontier-e8ixlk`, commit
`ad04e4a`, `GRAVEYARD_RUN.md` Finding 1), preserved verbatim in the audit dir as
`_ref_GRAVEYARD_RUN.md`:

> Before a screen result may promote, the mechanism's captured-signal statistic
> must be measured at **>= 2 widths**, and its extrapolation to n = 256 must be
> non-vanishing. A mechanism carrying an n-dimensional second-order state must
> additionally report spectral PSD at depth, not only per-pair guards.

Its motivating evidence: trace-share dilution 88.4% at n=4 → 3.02% at n=256, and
PSD loss 0/22 replicates at width >= 96 reaching depth 32 versus 21/32 at widths
32–56, Spearman rho(width, l*) = −0.743 over 74 cells at width >= 32. Its
premise: a cluster of **six corpses** with the signature "passed the screen 8/8,
died at production".

#### What the audit found

`experiments/gen8_gate_audit/` — Opus, independent, read-only, writes confined
to that directory, ledger pinned at `60c9c72a…`.

| corpse | ledger id | measured widths | verdict |
|---|---|---|---|
| Gate-aligned scalar split | `latent_gate_aligned_split` | [64] | NOT width-caused |
| RB conditional marginals | `latent_gate_rb_marginals` | [64] | NOT width-caused |
| q3 response-Gram recursion | `latent_gate_response_gram` | [64] | NOT width-caused |
| Radial susceptibility compressor | `randomized_radial_susceptibility_compressor` | [64] (24 states) | NOT — died on **depth** |
| Full-covariance 2n sigma mixture | `latent_full_sigma` | [64] | NOT — **angular/gate aliasing** |
| Weight-identified latent q3,r2 | `weight_identified_latent_factor` | screen [4,8,16] → kill [32,64] | **CONFIRMED width-caused** |

Tally **1 confirmed / 5 not / 0 indeterminate.** The decisive mechanical fact
for four of the six: the "screen" statistic and the "production" statistic are
two aggregate fields of **one file**, over **one bank of eight cases**, all at
**width 64**. `aggregate.wins = 8` and `aggregate.ratio = 0.9975024218012577`
(C1), `0.9975023609978109` (C2), `0.9975023396798792` (C3) are siblings in the
same object; width was never varied, so it cannot be the discriminating
variable. Width 256 appears in those artifacts only under
`cost_accounting: {width: 256, depth: 32}` — a projected shape-billed model,
never a measurement. (For C3 the audit's machine record shows 256 not present
at all; its cost model lives in the REPORT.md.) Corroborating and independently
decisive: all three carry `baseline_mse_sum = 0.0068680758149980555`
**bit-identically** — same comparator, same eight-case bank, same untouched
parent term, which is why three mechanisms with different state, operators and
cost bounds agree to seven significant figures against a gate of 0.8. One
measurement reported three times, from which the salvage map derived three
separate mutation branches.

Two collateral corrections: the "8/8 screen" signature holds for **3 of 6**
rows, not 6 (C4 is layer-0 8/8, C5 a covariance witness at 1/8 wins, C6 6/7 at
small width); and "kill conditions name widths 3, 4 and 64, none names 256" is
carried by **5 of 223** GEN6 records naming any width at all — 218 of 223 are
width-silent — while the fold ledger holds a kill condition that *does* name
256 (`gm_latent_cubature`: "conservative n=256,L=32 target arithmetic at least
80B").

#### Why the clause would have punished our best records

Pinned snapshot, 60 promotion-eligible records (statuses screened / promoted /
validated / survivor / component-pass / phase-A-pass); 35 carry no width
parameter at all. **14 records fail a >= 2-width clause, and 10 of the 14 fail
it while measured AT 256:** `row_blocked_winograd` (screened),
`row_blocked_winograd_production` (**promoted**), `ple_flash_sidecar`,
`m80_kerdock_tangent_factorial`, `m82_kerdock_vs_haar_variance`,
`m156_extended_domain_star_control`, `m172_selective_22_owner_fusion`,
`wc1_winner_ablation_map`, `v31_guards_m186_m187` (**our only `validated`
record**), `s12_finite_width_kernel_capstone`. The remaining four are
`conditional_corr_spectrum` [16], `m126_repeated_output_source_contraction`
[64], `m198_source211_delay_one_adapter` [4], and `gm_u3_grid` [48] — where the
48 is the empirical rotation-pool size (`build_pool_spec("empirical48")`), not
a width, i.e. a confirmed extractor false positive.

A promotion gate that rejects a record **for having been measured only at the
true operating point** is mis-specified, not merely weak. `h4_random32256`, the
promoted champion component, has no width parameter and would sit outside the
gate entirely. Genuine non-256 exposure is **8 of 60** (`conditional_corr_spectrum`,
`conditional_residual_cumulant_spectrum`, `conditional_residual_covariance_algebra`,
`cumulant_polynomial_quotient`, `m86_boundary_laplace_coarea`,
`m126_repeated_output_source_contraction`, `m198_source211_delay_one_adapter`,
`m200_streaming_overlap_fixture`), of which only the four
`conditional_*`/`cumulant_*` records are genuine targets — the other four are
algebraic/structural conservation fixtures where small width is the *point*.

Also retracted in the same document: the orchestrator's own claim of an hour
earlier that `gm_rankone_bill` was the gate's first customer. It is pinned at
n=256 / layers=31 and passes both clauses.

#### A derivation I performed — the original clause would have passed the one corpse it was drawn from

**This is mine, not in the record.** C6 is the single confirmed width death.
Its captured-signal statistic is the mean top-two trace fraction over 16 fresh
first-layer matrices per width, committed in
`experiments/LATENT_FACTOR_ADVERSARIAL_AUDIT.md`:

```
n:      4       8       16      32      64      128     256
share:  0.8838  0.6168  0.3730  0.2146  0.1144  0.0586  0.0302
```

Multiply through by n: 3.5352, 4.9344, 5.9680, 6.8672, 7.3216, 7.5008, 7.7312 —
i.e. n·share is slowly saturating, and the ratio per doubling settles at
0.6979, 0.6047, 0.5753, 0.5331, 0.5122, 0.5154 → asymptotically 1/2. OLS on
log(share) vs log(n) restricted to n >= 32 gives slope **−0.9452**, prefactor
**5.7411**, predicting share(256) = **0.03039** against a measured 0.0302
(0.6% error). Over the full range the slope is −0.8254 and the prediction
0.03409 (12.9% high). So the closed form U-W4 asks for is, to the accuracy the
data supports, **share(n) ≈ 5.74 · n^−0.945**, an essentially O(1/n) law —
which is the *same* O(1/n) dilution named in `LATENT_GATE_RB_MARGINALS_REPORT`
as the cause of C1–C3's identical ratios. One law, two symptom classes.

Now run the proposed clause on C6's actual screen points. Fitting only n = 4, 8
(the two-point line the clause literally permits) gives slope −0.5189 and
share(256) = **0.10212**, overestimating the true 0.0302 by **3.38x**. Fitting
C6's real screen band n = 4, 8, 16 gives slope −0.6223 and share(256) =
**0.06804**, overestimating by **2.25x**. Both extrapolations are strictly
positive. Since "non-vanishing" is nowhere operationalized in the record — no
threshold, no interval, no side of the interval named — **the gate as worded
passes the one corpse it was drawn from.** The revised clause 2 survives this
attack precisely because it adds the two things the original lacked: >= 3
points or a rank statistic, and gating on the *unfavourable end of an interval*.
Assumption stated: log-log OLS on the committed table with no error model, and
"non-vanishing" read as "does not extrapolate to zero". If you read
"non-vanishing" as "above the materiality gate 0.8" then all three fits fail it
and the clause becomes a screen-kill rule, not a transfer rule — the ambiguity
itself is the specification defect.

### 6. The defect taxonomy — three confirmed classes, found in our own record

This is the part with the longest half-life. Each class is stated with its
general detection rule, because the instances will not recur but the shapes
will.

#### Class 1 — STRUCTURAL ZERO (instrument in a different regime from its claim)

**Instance: M183.** `experiments/m183_f32_hotpath/run_m183_falsifier.py:58`

```python
dts = getattr(op, "dtypes", None) or ()
names = [str(getattr(d, "name", d)) for d in (dts if isinstance(dts, (list, tuple)) else [dts])]
if any(("float64" in n) or ("complex" in n) for n in names):
```

Ground truth from the pinned venv, `flopscope 0.10.0+np2.4.6`: `OpRecord`
carries `count, cumulative, flop_cost, flopscope_backend_duration_s,
flopscope_context_start_offset_s, flopscope_overhead_duration_s, index,
namespace, op_name, resolved_dtype, shapes, subscripts`. On a live record
`hasattr(op,"dtypes")` is `False` and `hasattr(op,"name")` is `False`. Three
sub-patterns compound: a `getattr` with a **falsy** default, an `any()` over
the resulting empty tuple, and an attribute name absent from the installed API.
`f64_share` could only ever be `0.0`, on any program, forever.

Empirical confirmation, run in the pinned venv against a fixture that is 100%
float64 by construction (two chained 256x256 matmuls, `resolved_dtype =
float64` on all 5 ops, 133,955,584 FLOPs billed):

| detector | f64 billed | f64 share |
|---|---|---|
| suspect (`dtypes`) | 0.0 | **0.00%** |
| corrected (`resolved_dtype`) | 133,955,584 | **100.00%** |

A **second dead name** sits at line 62 — `getattr(op, 'name', '?')`, where the
field is `op_name` — masked because the guarded branch never executes. Two
independent defects in five lines, one hiding the other.

Blast radius: ledger `m183_f32_hotpath_falsifier` reads *"KILLED: f64-lane
billed = 0.0000e0 of 1.5803e11 total (0.00%)"*; the **filed** write-up
`PHASE1_WRITEUP_DRAFT_20260808.md` cites it twice — line 129 in the ledger
table, and **line 422, load-bearing**: *"the fidelity family formally retired
the dtype-repricing escape (M183 measured the f64 SHARE at 0.00%, which is
invariant to how f64 is priced)."* The verdict itself survives on independent
evidence — corrected f64 charge 1.193e8 FLOPs = 0.0755% of predict, recast
ceiling 59,656,312 FLOPs, reproducing the Gen-7 cost-remap attacker's 59.66M to
the digit — but the *cited number* is retracted and the citation in a filed
document is U-I2, an outward-facing erratum call that belongs to Jonah alone.

**Detection rule.** For any detector D reporting statistic S: construct an
input on which S must be non-null by construction, and run D on it in the same
process. If D cannot be made to fire, S is not a measurement. Statically, the
signature is the conjunction — falsy default (`getattr(x, "f", None) or ()`,
`.get(k, 0)`, `[]`) **and** a reducer over the result (`any`, `sum`, `max`,
comprehension) **and** a name that must be checked against the *installed*
artifact rather than your memory of the API. Any two of the three is a smell;
all three is a structural zero until proven otherwise.

**Antidote, already in our corpus.**
`m217_balanced_three_color_strict_control/run_m217_native_trace.py:119`:

```python
"matmul_calls": int(matmul.get("calls", -1)),
```

A **loud sentinel**. An absent key yields −1, which is distinguishable from a
true zero, and −1 propagating into a report is visible where 0 is invisible.
`gm_latent_cubature/step0_arithmetic.py` is the stronger form: it hard-indexes
`ops['take']['flop_cost']`, so absence raises `KeyError`.
`u2_fold3cap_bound/calib_summary_cost.py` constructs
`B.OpRecord(..., resolved_dtype="float32")` — the corpus already knew the
correct field name while M183 was reading a name that never existed.

#### Class 2 — DISTRIBUTIONAL MISREAD (statistic in a different regime from its use)

**Instance: C1** (`experiments/c1_local_mc_calibration/`). The C1 report
concluded *"our local suite is 1.65x HARDER than the hosted one"* from
R = mean_local / hosted_reference = 1.0686e-6 / 6.470e-7 = 1.652, and that
ratio then propagated into expectation-setting and into forum adjudication
("C1 shows suite offsets reaching 1.65x"). The orchestrator's Gen-8 hypothesis
was that this corroborated forum claim 18141, that the public 50 are
filtered-easy.

I recomputed the panel from the committed artifact
`c1_local_mc25.json` (22 of 25 nets completed; 3 excluded for
`combined_budget_exhausted`):

| statistic | value |
|---|---|
| mean adjusted | 1.068628e-6 |
| **median adjusted** | **6.473546e-7** |
| min | 2.170436e-7 |
| max | 4.865049e-6 |
| mean / median | 1.65076 |
| **median / grader printed 6.470e-7** | **1.000548** (a 0.055% match) |
| mean / grader printed | 1.6517 |

The top five values are 1.776e-6, 1.968e-6, 2.163e-6, 2.759e-6, 4.865e-6 — the
max is 7.5x the median. The 1.65 is **entirely** the right tail. The local
suite and the grader's suite agree at the median to 0.05%; there is no easiness
shift, and there never was one to apply. The hypothesis is killed
(`gen8_c1_ratio_artifact_and_anchor_se`).

Note the structure: mean/median = 1.65076 and mean/grader = 1.6517 agree to
0.06% *because* median ≈ grader. The "difficulty ratio" was numerically
identical to a pure skew statistic, which is exactly why it read as a
measurement of something.

The same investigation found a real defect the wrong statistic had been hiding:
S1b treats the hosted 1.830e-7 anchor as exact when it is a 50-net measurement
carrying **9.83% SE**. Folding the anchor's own error in widens the honest
50-net fresh-seed band from [1.54e-7, 2.16e-7] to **[1.46e-7, 2.25e-7]** and
raises P(private > 2.5e-7) from 0.034% to **0.57%** — a 17x increase. Still
small; no longer negligible.

**Detection rule.** Before any location statistic is used as a *ratio between
populations*, check the skew of both. If mean/median differs materially from 1
on either side, the ratio of means is a shape comparison, not a level
comparison. Cheap discriminator: report mean, median and max together, and
require that a claimed level shift survive on the median. The general form —
*a statistic computed correctly but read under an assumption the distribution
does not satisfy* — is P4 on the perturbation ladder.

#### Class 3 — POST-HOC PATTERN-MATCH (the six-corpse premise)

The six-corpse premise is the subtlest of the three: the proposal it generated
was reasonable, the mechanism it named is real and measured, and the cited
evidence existed. What failed is that the corpses were selected **after** the
pattern was in hand, by prose reading of a graveyard table, and never checked
against the artifacts. Five of six dissolve under one mechanical R1 check —
were the screen and kill statistics ever measured at different widths? — and
for four of them they are two fields of the same JSON object.

The parallel session's own method section is honest about the risk and still
did not catch it: it records that automated keyword clustering is unreliable
(88 of 161 killed records, 55%, match no obstruction against the atlas text;
`allocation`-type words match 41% of 374 files) and therefore assigned
groupings by *reading*. Reading is what produced the pattern-match. The defect
is not sloppiness — it is that narrative similarity across records is a far
weaker signal than any single artifact field, and it feels stronger.

**Detection rule.** When a set of records is cited as evidence for a shared
cause, require, per record, the *field* in the *artifact* that discriminates
the cause — not the sentence in the record text that describes it. If the
discriminating variable was never varied inside a member's own artifact, that
member is not evidence for that cause. A second, cheaper check that would have
caught C1–C3 alone: if the members' primary metrics agree to within the gate's
resolution (here, seven significant figures against a gate of 0.8), they are
one measurement, and one measurement cannot be a cluster.

### 7. The instrument-validity gate

**No detector may produce a promotion-bearing or kill-bearing null unless it
fired on a positive fixture in the same run.** This is clause 3's new half. It
is cheap, applies to every axis, and is the only one of the four clauses whose
need is proven by a defect that reached a filed document.

The audit's Task 3 also bounds the class. 522 `.py` files scanned under
`corpus/whestbench/experiments`; static pattern counts: 62 `getattr`-with-falsy-
default sites, 991 reducer-over-comprehension sites, 176 raw attribute-name
mismatches against the installed API, 55 token-in-source detectors, 2 dead-name
reads, 0 cross-artifact `.get` with an unknown key. Intersected with an
empirical filter — 109 artifacts carrying a zero-valued measured statistic —
and each survivor traced to its producing detector. Result: **1 confirmed
structurally void, 7 shape-matched and positive-capable.**

| # | detector | firing evidence | record it supports |
|---|---|---|---|
| 1 | `m183_f32_hotpath/run_m183_falsifier.py:58` | **does not fire**: 0.00% on a 100%-float64 fixture | M183 — VOID |
| 2 | `gm_a4_constraint/verify_two_signal.py:64` bytecode needle scan | returns `['_tally']` on `capped_fold3.py` | `a4_hostile_inputs_battery` |
| 3 | `gm_m179_m199/run_depth32_identity_trace.py:134` legacy-tag scan | fires on an injected `m200.legacy_rebuild.full_archive`; 21 real ops observed; independent `LegacyCallCounter` monkeypatch alongside | **`gm_m179_m199`** |
| 4 | `v31_guards/run_v31_gates.py:202` `getattr(est,"last_guard_report",None)` | G2 is an explicit positive control: `m186_empty_regime_fired: true` on `f_negshift`; `m187_finite_output_fired: true` with 164 nonfinite entries replaced on `b_gain_1e3` | **`v31_guards_m186_m187`** |
| 5 | `m184_trichotomy_upward/run_m184_g0.py` certain-on detector | same detector reports max certain-on 39 and certain-dead 37 across 84 layer cells; the 0.00% reduction is a measured negative | `m184_trichotomy_upward_g0` |
| 6 | `m177_bivariate_relu_primitive.py:167-168` `hasattr(...,"owens_t")` | full enumeration: `flopscope.stats` = {cauchy, expon, laplace, logistic, lognorm, norm, truncnorm, uniform}; `norm` = {cdf, name, pdf, ppf}; no owen/multivar/bivar spelling exists | `m177_...` (no-go) — would not survive a rename |
| 7 | `t3_fold3_deterministic_cap/run_t3_gates.py:204,265` | fail-closed: `report is None` sets `g1["pass"] = False` | `t3_fold3_deterministic_cap` |
| 8 | `terra_m153_pilot_reuse/...:97` | trace has 3 entries, `removed_shape_bill = 589,840,384`; blocking assertion computed from matmul dispatch deltas, independent of the attribute | `m153_exact_formal_prefix_reuse` |

**7 of 8 cleared.** The one that matters most for you: **row 3 is
`gm_m179_m199`'s instrument — the record that licensed the entire width-gate
line of work — and it fires.** Your exact-control measurement stands. Row 4 is
our only `validated` record and it carries an explicit positive control. M183 is
a class of one on the evidence available.

The honest boundary on that claim: the sweep was static-pattern-driven,
intersected with a zero-statistic filter. It cannot see a detector that returns
a *wrong non-zero* value, and row 6 is explicitly fragile to an upstream
rename. "Class of one" is a statement about detectors that produce nulls, not
about instrument correctness generally.

### 8. The Gen-7 result as the evidentiary standard

The bar the campaign now holds itself to, from `GEN7_ADVERSARIAL_CLOSURE_20260810.md`:
20 adversarial agents across three fleets, attackers Opus 5, judge Fable 5,
everything seeded, owner mandate *"actually try, dammit."*

- **Fleet 1 (break the champion, 6 lenses):** `FLOOR_HELD_EARNED`. Five lenses
  returned no candidate, each with a named obstruction on record: exact-identity
  (all four closed-form conditional expectations already consumed);
  control-variate (the 2-design absorbs every degree<=2 statistic exactly,
  degree>=4 content ~1e-5 R^2); biased-hybrid (baseline measured-unbiased, so
  MSE-optimal shrinkage weight ~0, every realizable form worse by −5.7% to
  −38%); cost-remap (~99% irreducible float32 matmul at floor rate, f64 share
  0.033% max); design-alt (DGS needs N >= 33,152 for a 4-design and ~44x rows
  for degree-6 nulling; Var·C invariant on the flat speckle).
- **The sixth lens found the one candidate the certificate left open** —
  seed-side rotation *construction*, rotation = V from W0 = U S V^T rather than
  the grader-seed Haar draw. Under the full regime — seed 0, common random
  numbers, twice-run **bit-identical** determinism, noise floor exactly 0.0 —
  it is a clean null: paired t = **+0.19**, better on exactly **50/100** nets,
  bootstrap CI on the mean delta **[−3.19e-8, +2.61e-8]** symmetric about zero,
  drop-top-5 sign flip confirming the artifact, C/B **+0.0014** for 3.6e8
  billed FLOPs with no compensating MSE reduction (ledger 242,
  `gen7_svdv_rotation_construction`, killed). **This is the shape of a null you
  can trust**: a pre-registered attacker prediction of a *win*, a determinism
  check, a sign count at the coin flip, and a CI straddling zero.
- **Fleet 2 (break the kills, 7 families):** 7/7 boundaries held, several
  strengthened. The dispersion hold named the record's one un-probed crack —
  non-smooth cell-membership covariates — and S18 killed it same-day (best
  gated OOS incremental R^2 2.37e-5 against a 2.63e-5 bar; all 64,512
  directions are singleton first-layer cells, so per-point unique labels cannot
  generalize; ledger 241).
- **Fleet 3 (break our certainties, 6 load-bearing claims):** 1 held, 1 watch,
  **4 REAL_ACT_NOW, all executed same-day** — selection default-safety (level
  inflation, corrected), write-up floor language (S17 self-labels a lower-bound
  *attempt*; v8 de-escalates), the dispersion model (DIFF_RATIO 1.1x refuted by
  our own committed data; S1b re-measured vD 0.08–0.12, split 17–23%/77–83%,
  bracket-validated against the hosted 15.53x spread), governance.

**Read the number precisely.** "0 breaks" is a statement about the *champion's
optimality* and about the *kill boundaries*: 0 of 6 attack lenses produced a
surviving candidate, and 7 of 7 re-litigated kill families held. It is emphatically
**not** "0 defects found" — Fleet 3 drew blood on four of six of our own
load-bearing claims. The standard is therefore two-sided, and the base rate in
this record is the part worth carrying forward: **every adversarial pass that
has been pointed at our own paperwork has found defects in it.** Gen-7 Fleet 3
found 4 of 6 load-bearing claims defective; Gen-8 on 2026-08-10 added M183, C1
and the six-corpse premise. Seven self-inflicted defects across two passes,
none of them in the estimator. A future pass that reports zero is reporting on
its own coverage, not on ours.

Ladder P's P6 cell claims "9 of 9 Gen-8 proposals; 20 of 20 Gen-7 attacks". The
20 is traceable to `GEN7_ADVERSARIAL_CLOSURE_20260810.md` under the reading
above. The "9 of 9" appears **only** in that table cell; I found no second
occurrence anywhere in `core/`, and U-G1 in the same document states that "five
of nine Gen-8 proposals were never adversarially verified", which is in tension
with it. Treat the 9 as unsourced.

### 9. Defects I found in the record while writing this section

Reported because the taxonomy is only worth having if it is applied to the
documents that carry it.

1. **The label `C1` is overloaded across two same-day documents.** In
   `GEN8_LADDERS_20260810.md` (and the channel entry at 00:07 UTC) `C1` is the
   local-MC-calibration statistic defect. In `GATE_AUDIT.md` Task 1, `C1` is
   corpse #1, `latent_gate_aligned_split`. Different objects, same short label,
   both committed 2026-08-10, both cited in the promotion-rule discussion.
2. **Three different ledger sizes are in circulation.** `GEN8_LADDERS` says
   "261-record history" and "our 261 records"; the audit pins 263 (546,363
   bytes, sha `60c9c72a…`); the file now holds 264 (549,205 bytes, sha
   `387d0c6f…`). Nothing material turns on it — the audit records the drift as
   deviation 1 and both added records were `killed` — but a reader who quotes
   "261" is quoting a number that was already stale when written.
3. **The `OpRecord` field list is transcribed three ways, and two of them drop
   two fields.** The pinned-venv probe `_installed_api.json` gives 12 fields
   including `count` and `index`; the ledger record `gen8_m183_detector_void`
   quotes all 12; `GATE_AUDIT.md` prose and `audit_results.json` both give 10,
   omitting `count` and `index`. Immaterial to the verdict — `dtypes` and
   `name` are absent under every listing — but it is a transcription defect
   inside the document whose subject is instrument fidelity, and it is exactly
   the kind of drift that Class 1 feeds on.
4. **The parallel branch's width evidence is cited but not independently
   verifiable from our tree.** `gm_spd_width_scaling` has no experiment
   directory under `corpus/whestbench/experiments/` and no record in the
   264-candidate ledger (I enumerated ids matching `spd`/`width`: only
   `s12_finite_width_kernel_capstone` and `s13_width_pooled_mfmc_premise`). The
   0/22-at-width->=96 and rho = −0.743 figures exist in our tree only inside
   `_ref_GRAVEYARD_RUN.md`, which is a `git show ad04e4a:` copy of the other
   branch's file. That is a quotation, not a second signal.
5. **The "64 → 72 non-monotonicity" and the "96-cell data" are not in the
   record.** Both appear only in `GEN8_LADDERS_20260810.md` (clause 2's
   justification for requiring >= 3 points, and U-W2's proposed R0 resolution).
   `_ref_GRAVEYARD_RUN.md` says "74 cells with width >= 32" and says nothing
   about a 64→72 reversal. I could not verify either figure. Clause 2's
   ">= 3 points or a rank statistic" is independently justified by my own
   extrapolation derivation in §5, so the clause survives, but its cited
   justification does not.
6. **"Non-vanishing" was never operationalized**, which is what makes the §5
   derivation possible. Any successor rewriting clause 2 into
   `scripts/fold_ledger.py` must pick a threshold and a side of the interval,
   and the record does not contain that choice.

---

## Unverifiable flags and defects the specialists found

These are reproduced verbatim from the section writers, because they matter more
than the sections they qualify.

### From "The geometry and the theorem"

Three items. (1) The brief's phrasing "(1/N) sum u u^T - I/d = 0.0 bitwise" is NOT in the record as a measured float quantity — no artifact under corpus/whestbench reports a second-moment residual at all. What the record has is m191_g0a_results.json: deg-1/3/5 design_rms exactly 0.0 and deg-2 design_rms 8.592096535015544e-09 / 7.641533832569696e-09 / 8.971971116412737e-09 (ratio ~2.2e-6 of iid) — i.e. float roundoff on a structurally exact null, not bitwise zero. The exact-arithmetic statement is a derivation I performed (each frame is an orthonormal basis, so the frame sum is I exactly and the 126-frame average is I/256 exactly); the bitwise claim as stated should be struck or re-measured. (2) The rival near-optimality ceiling (Kerdock within 0.0233% of optimal among positive-weight fixed rules, <=6.29% allowing negative weights) appears ONLY in core/GEN8_FORUM_INTELLIGENCE_20260810.md as a report of the rival's posted write-up; there is no derivation or independent check of it anywhere in the corpus. Level [R], single-sourced, external. Same for the rival's raw 2.2819e-7 on 100 self-chosen dev nets and their 64.27% post-Strassen budget. (3) Two defects found in the record and reported inline in the section: P1's "design span is 5.6e-3 of the degree-4 space" is wrong by 32x (correct 1.7612e-4), and S6's prose sentence attributing the constant-mode cancellation to the +1/16 sign imbalance is self-contradictory (the degree-4 kernel is even; my term-by-term arithmetic shows the imbalance contributes exactly nothing). All S6 numbers themselves reproduce.

### From "The cost algebra"

Six items, all stated in §8 of the section. (1) The pair 145.138e9 / 146.794e9 exists only as prose in three core documents plus AGENT_CHANNEL; no JSON, PY, TXT or MD measurement artifact in the repo produces it. (2) The figures 9.08e9 and "5.83% of C" from my tasking appear NOWHERE in the corpus — I verified this with a regex sweep over all .md/.txt files; they are arithmetically consistent with the 146.794e9 figure (9.08/(146.794+9.08) = 5.825%) so they plausibly share its unlocated run, but I could not trace them and I did not present them as sourced. (3) The organizer claim of 24 promoting flopscope.stats callables is REPORTED only: the committed _installed_api.json enumerates 58 top-level symbols and never descends into flopscope.stats. (4) No hosted residual value exists anywhere in the corpus; the 0.080 s / 0.137 s pair is a LOCAL T4 measurement that FLIP_READINESS_20260810 cites without its local label and gm_residual_k1/VERDICT.md:128 then re-labels "hosted" — a provenance drift I verified against SUBMIT_READINESS and T4_REPORT. (5) core/CODEX_HANDOFF_20260810.md, cited as the companion "for the mathematics" at CODEX_ULTRAPLAN_20260810.md:3, does not exist in the repository. (6) My depth-2..5 Strassen ladder is my own derivation, not a measurement; it is labelled DERIVED with its three assumptions named, and its d=1 row reproduces the committed 0.880151 as the transcription check.

### From "The decision-layer statistics"

Six items, all flagged inline. (1) The 9.83% anchor SE and the widened band [1.46e-7, 2.25e-7] / P=0.57% exist only as ledger record 260, GEN8_FORUM_INTELLIGENCE §3 and AGENT_CHANNEL — there is no committed harness directory, unlike gm_c1_bound. I corroborated the 9.83% two independent ways (S1b's own analytic per-net CV gives 9.75%-10.30%; a lognormal fit to the committed hosted 50-net IQR predicts [9.905e-8, 2.297e-7] against observed [1.05e-7, 2.26e-7]) but did not reproduce the band or the tail. (2) The pre-correction baseline "0.034%" matches no committed S1b number — S1b's own 50-net tails are 0.046% (s17_low) and 0.085% (s17_high) and its headline says 0.05-0.09%; if the baseline should be 0.046-0.085% the widening is 6.7x-12.4x, not 17x. (3) The N8c all-layers bias share 0.99993 is of the same order as T2's diagonal-closure bias 7.18e-4, which suggests the intermediate rows are carried by an analytic closure, but I did not read the champion's intermediate-layer path — that attribution is an inference. (4) N8c's committed bootstrap CI lower endpoint (-0.030873) lies above its own point estimate (-0.033572), which is impossible for a net-level percentile bootstrap over the three values (8/27 = 29.6% of resample means are <= -0.0605); the resampling unit is not recorded in the artifact. (5) No CI is committed for the 9.6e-5 closure plateau, which is a 3-seed mean with a 4.8x spread (7.2707e-5 / 1.7879e-4 / 3.7099e-5), so 340.7x/384x/524x inherit an unquantified numerator dispersion. (6) The even/odd harmonic decomposition that would prove the 2x gap between the two floor accountings could not be verified from the S5 arrays and is omitted in S17 by design. Separately: my vD moment estimator (vD ~ 0.134, 95% CI [0.054, 0.220]) is my own derivation with its algebra and caveats shown, not a record value, and its downstream band/tail consequence is stated directionally because I did not run run_s1b.py (firewall: read-only).

### From "The M245 lane — Codex's own state"

Four things I could not trace. (1) The baton's own enumeration of the seven hostile-audit static blockers is not in any committed artifact in the repo — it came through the Maestro-injected bridge prompt; the blocker column in my table is inferred from the journal's repair descriptions and is labelled as such. (2) The cmd2 traceback, exception type, and failing line are unrecoverable from the artifacts (unittest defers tracebacks to an end-of-run summary the interruption prevented), so the ERROR's cause is genuinely unknown; I narrowed the static space (signatures match; run_replica_event has exactly two call sites in the suite) but did not and cannot diagnose it without a rerun the protocol forbids. (3) The exact termination time of cmd2's process is not determinable — the 14:20:52 UTC figure is the last stderr write, which is the START of the in-flight test, not the death. (4) Reviewer A's and reviewer B's full reports do not exist on disk; they are summarized in the journal only, and the corresponding M245_SCIENTIFIC_STATIC_AUDIT_A/B JSON artifacts were deliberately not created per journal line 20. One discrepancy flagged rather than resolved: the journal says reviewer B triaged 92 test methods; my count of `def test_` across the four frozen suites is 91 (31/23/23/14), with the 31 corroborated exactly by cmd1's "Ran 31 tests". Also caveated: my numerical re-derivations used mpmath 1.4.1 in a scratch interpreter, while the frozen venv carries mpmath 1.3.0; I did not execute anything in the frozen venv, and I did not run git, so committed-status claims rest on the 23:49 UTC channel entry rather than on my own observation.

### From "The method and the defect taxonomy"

Six items, all flagged inline in section 9 of the deliverable. (1) `gm_spd_width_scaling` — the entire SPD/PSD width evidence (0/22 replicates at width >= 96 reaching depth 32, 21/32 at widths 32-56, Spearman rho = -0.743 over 74 cells) has no experiment directory under corpus/whestbench/experiments/ and no record in the 264-candidate ledger; it exists in our tree only as a quoted `git show ad04e4a:` copy inside experiments/gen8_gate_audit/_ref_GRAVEYARD_RUN.md. Quotation, not second signal. (2) The "64 -> 72 non-monotonicity" and the "96-cell data" cited in GEN8_LADDERS_20260810.md (clause 2's justification and U-W2) appear nowhere else; _ref_GRAVEYARD_RUN.md says "74 cells", not 96, and does not mention a 64->72 reversal. Could not verify either. (3) The "9 of 9 Gen-8 proposals" in Ladder P's P6 cell appears only in that table cell, and U-G1 in the same document says five of nine Gen-8 proposals were never adversarially verified — in tension with it. Treat as unsourced. (4) The `OpRecord` field list is transcribed three ways: _installed_api.json and the ledger record gen8_m183_detector_void give 12 fields (with `count`, `index`); GATE_AUDIT.md prose and audit_results.json give 10. Immaterial to the M183 verdict, but a transcription defect. (5) The label "C1" denotes two different objects in two same-day documents (the local-MC-calibration statistic defect in GEN8_LADDERS; corpse #1 latent_gate_aligned_split in GATE_AUDIT). (6) "Non-vanishing" in the original width clause is nowhere operationalized — no threshold, no interval, no side named — which is what makes my section-5 derivation possible. Separately, three ledger sizes are in circulation (261 in GEN8_LADDERS, 263 at the audit pin, 264 now); I re-derived the current one myself (549,205 bytes, sha256 387d0c6f44eb2e14d8ed08871c89671f179af50c3b2c3243f5eaee006937a4a4, 264 candidates). All arithmetic labelled as mine (the trace-share power-law fit and the screen-band extrapolation error) is log-log OLS on the committed LATENT_FACTOR_ADVERSARIAL_AUDIT table with no error model, stated as such in the text. Firewall respected: read-only throughout, no git, no execution of m245/m243/m244 modules, no submissions, no network.


## Three defects this handoff surfaced in our own record

1. **P1 paper, degree-4 span figure wrong by 32x.** `P1_SPECKLE_THEOREM` states
   the design span is 5.6e-3 of the degree-4 space; the correct value is
   1.7612e-4. Corrected in the same commit as this handoff.
2. **S6 prose contradicts S6 arithmetic.** The verdict's sentence attributing the
   constant-mode cancellation to the +-1/16 sign imbalance is self-contradictory:
   the degree-4 kernel is even, so the imbalance contributes exactly nothing.
   Every S6 NUMBER reproduces; only the prose explanation is wrong.
3. **A phrase I propagated is not in the record.** The formulation
   "(1/N) sum u u^T - I/d = 0.0 bitwise" appears in my own Gen-7 summary and in
   the brief for this handoff. No artifact reports that second-moment residual at
   all. The exactness is REAL and derivable (each frame is orthonormal, so the
   frame sum is I exactly and the 126-frame average is I/256 exactly), and the
   measured corroboration is m191_g0a: deg-1/3/5 design_rms exactly 0.0, deg-2
   design_rms ~8.6e-9 against iid 3.937e-3 (ratio ~2.2e-6). But "bitwise" was my
   overstatement, and it is withdrawn here.

The pattern is the same one the campaign found all day: external attack finds
nothing, internal audit finds real defects. That asymmetry is the strongest
available evidence that the record is honest.
