# P1 — The finite-width residual of deep random ReLU networks is computational speckle: a measured theorem at the boundary of an exact spherical design

Internal research paper, draft 1. Date 2026-08-10. Corpus: `corpus/whestbench`. Audience: future Opus / researcher
sessions with no conversation memory. Status: **measured synthesis**, not a proof. Every numeric claim below is quoted
verbatim from a committed artifact whose path is given inline and collected again in §5. Level tags, per the corpus
evidence discipline (`corpus/whestbench/README.md`): **[O]** observed (a run in this corpus produced it), **[D]**
derived (follows from observations by shown steps), **[R]** reported (a committed artifact says so; not re-derived
here), **[A]** assumed (a stated modelling choice). No claim here is labelled above the level its artifact earned, and
no minimax claim appears anywhere in this document.

---

## Abstract

Across sixteen predeclared experiments and 242 ledger records, the campaign to beat a Kerdock-design Monte-Carlo
estimator of the sphere-mean of a depth-32, width-256, bias-free He-initialised ReLU network failed in seven distinct
ways. This paper argues the seven failures are one measurement read seven times, and states that measurement as a single
theorem-shaped claim: the estimator's finite-width residual field is **maximum-entropy independent chi-squared-with-one-
degree-of-freedom speckle**, living **exactly at the degree-4 boundary** of a maximum-structure exact spherical 2-design.

Two objects meet at that boundary. The design (Kerdock, 126 phased-Hadamard frames x 256 rows = 32,256 directions,
antipodally doubled to 64,512) is engineered for maximum structure: it integrates degree <= 2 exactly and, at degree 4,
its quadrature functional is the single Bragg-suppressed mode of an otherwise perfectly flat error operator — one
eigenvalue 42x below a bulk shelf carrying 99.68 % of the operator's squared mass [O, S6]. The residual left behind is
maximum entropy: its direction-energy law fits chi^2_1 at KS distance 0.0071–0.0099 on the design's own 64,512 points
while the exponential (Maxwell-Boltzmann) null is rejected at KS 0.164–0.165 [O, S7]; it is decorrelated at every inner
product the design realises (shell correlations -1.3e-3 at 90 deg, -5.5e-6 at 86.42 deg) [O, S17]; and it is blind to
every cheap output-side covariate tried, smooth (best pooled out-of-sample incremental R^2 = 1.56 %) [O, S15] and
combinatorial (best gated 2.371e-5 against a 2.63e-5 fitting-noise bar) [O, S18].

The entropy is **computational, not ontic**. The residual is a deterministic, bit-reproducible function of weights the
estimator already possesses; what the seven failure families certify is pseudo-random *strength against every sub-budget
test the campaign constructed*, not the absence of information (`core/RECURSION_PACKET_GEN6_20260810.md`). Three
consequences follow mechanically: every output-side estimator class dies for the same reason; the champion is
correction-proof because a max-entropy unbiased field has no fitted structure to overfit; and the achievable floor is
set by the speckle's independent-cell count N_eff ~ 38k, against which the champion measures 1.79x cost-matched or
0.90x distinct-direction [O, S17]. What this paper does **not** claim: minimax optimality, a proved lower bound, or
exclusion of untested output-side classes — §4 states the scope honestly.

---

## 1. The statement

### 1.1 Setting (frozen and reproducible)

- Nets: synthetic, bias-free, He-initialised (gain 2/width) MLPs, width n = 256, depth D = 32, seeds 101 / 202 / 303,
  one Haar rotation each (`haar_rotation(900000 + net_seed*1000 + 0)`) [O, S5 §"Exact normalizations"].
- Target: f(u) = neuron-averaged final post-ReLU output ("ybar"); the estimator averages f over design directions to
  estimate the sphere mean [O, S15 §"Target"]. Residual r(u) = f(u) - mean_design(f).
- Design: frozen Kerdock v3 base, 126 phased-Hadamard frames x 256 rows = 32,256 directions at exact radius
  `mean_chi(256) = 15.98438266660853`, antipodally doubled to 64,512 [O, S5/S15/S18].
- Champion: Kerdock v3.1 GUARDS; hosted #326094 adjusted 1.832e-7, raw 2.818e-7, C/B 0.650, 1.768e11 billed FLOPs
  [R, `core/RECURSION_PACKET_GEN6_20260810.md` §"Champion state"].

### 1.2 The claim

> **Measured Theorem (speckle at the design boundary).** For the setting of §1.1, the residual field r(u) is, to every
> test the campaign applied:
>
> **(a) Maximum-structure below degree 4.** Degrees 0, 1, 2 are integrated exactly and contribute zero estimator
> variance; at degree 4 the design's deviation operator D = A - I/dim(H_4) has a three-shell spectrum whose mass is flat
> at ~1/N across the entire 32,256-mode span, with the single quadrature-functional mode suppressed 42x below bulk [O, S6].
>
> **(b) Maximum-entropy above it.** The direction-energy law is chi^2_1 — a single real Gaussian amplitude, the
> maximum-entropy law for a real field of fixed second moment — fitting at KS 0.0071–0.0099 on n = 64,512, with the
> exponential/MB alternative rejected at KS 0.164–0.165 [O, S7].
>
> **(c) Independent at the sampling geometry.** The design's minimum inter-direction angle is
> arccos(1/16) = 86.41667830152804 deg, ~2x the measured speckle correlation length xi = 35.60–45.95 deg; empirical
> residual correlations at the design's realised inner products are -1.3e-3 (t = 0) and -5.5e-6 (t = +-1/16) [O, S7+S17].
> The 64,512 evaluations behave as N_eff ~ 38,000 independent draws [O, S17].
>
> **(d) The entropy is computational.** r(u) is a deterministic function of the possessed weights, recomputable
> bit-for-bit (S8 check 2; S15 and S18 reuse checks both max abs diff 0.0). Clauses (b) and (c) are statements about what
> *sub-budget output-side tests* can see — pseudo-random strength, not information content
> [R, `core/RECURSION_PACKET_GEN6_20260810.md` §"The corrected god-node"].

### 1.3 What each clause is not

(a) is not "the design is optimal among all designs" — it is a spectral fact about one design at one degree. Degree 6,
measured in the same run, is **not** suppressed: lambda_top ~ 1.03/N, design/iid RMS 1.015, i.e. iid-level [O, S6
§"Degree-6 repeat"]; the Kerdock +-1/16 phase cancellation is tuned to degree 4 and stops there. (b) is descriptive, not
inferential: S7 states plainly that "P2 KS distances are descriptive (n is large; any model misfit dominates sampling
error) — no p-values are claimed", and the chi^2_1 fit holds for the *neuron-averaged* field only; per-neuron pooled
energies fit neither null (shape k ~ 0.000–0.007, rectification-dominated heavy tails) [O, S7]. (c) is measured
decorrelation at the design's own spacings, not proved independence. (d) governs the paper: "maximum entropy" means *no
cheap output-side observable we built extracts it*, a statement about a tested family of adversaries.

### 1.4 The one-sentence form

The finite-width output of a deep random ReLU network is maximum-entropy independent speckle sitting exactly at the
degree-4 boundary of a maximum-structure exact design; this single fact is simultaneously why every mechanism failed,
why the champion is correction-proof, and what sets the achievable floor
[R, `core/GOD_NODE_SYNTHESIS_20260810.md` §"The one-sentence pattern"].

---

## 2. The seven independent measurement pillars

Each pillar is a separately predeclared experiment with its own gate, kill line, and second signal. They fail in
different ways if the theorem is wrong, which is why they count as independent.

### Pillar 1 — S6: the degree-4 boundary is exact, and the error above it is flat

Artifact: `experiments/s6_bragg_spectrum/`. Verdict: **KILL** (of the low-rank-correction hypothesis).

- Inner-product census over all 32,256^2 pairs is **exact** (entries are dyadic +-1/16; max deviation from the k/256
  grid = **0.0**): value 1 x 32,256 (diagonal), 0 x 8,225,280 (all within-frame), +1/16 x 548,352,000,
  -1/16 x 483,840,000 [O]. Exactly three off-diagonal values — the Kerdock mutually-unbiased-bases fingerprint.
- Degree-4 spectrum of D, closed form validated numerically: mid shell **3.1603445e-5** (mult. 125), bulk
  **3.0995105e-5** (mult. 32,130), top-1 **7.2963e-7** (mult. 1, **42x below bulk** — this mode is the quadrature
  functional itself), sea **-5.46e-9** (mult. 183,116,224) [D from exact structure, O by subsample eigensolve].
- Flatness: the top-100 eigenvalues carry **0.32 %** of tr(D^2) (full-N closed form 0.0032221249837913308; subsample
  observed 0.0063737437723080615) against a predeclared KILL threshold of < 5 % and a PASS requirement of >= 50 %.
  Participation rank tr(D^2)^2 / tr(D^4) = **32,266.169565128537 ~ N** [O]. Scale: dim H_4 = **183,148,480**, so the
  design span is 5.6e-3 of the degree-4 space and the deficiency is spread evenly over it.
- **Second signal:** tr(D^2) two independent ways — exact pairwise sum 3.099748626998932e-05 vs exact-rational closed
  form 3.099748626991116e-05, relative difference **2.52e-12**; plus a structure-agnostic 16,000-direction dense
  eigensolve matching the closed-form multiset to max abs error **3.55e-12** [O]. Both reproduced independently for this
  paper from `s6_results.json`; values identical to the verdict prose.
- **Anchor:** the 42x suppression predicts M191's measured degree-4 design/iid ratio — S6 direct recompute 0.10744,
  spectral prediction 0.10778, archived M191 0.10668 / 0.10719 / 0.09829 [O + R].
- *Why it is a pillar:* it fixes **where** the residual lives. Degrees <= 2 are gone by construction; degree 4 is
  present but delocalised over ~1.8e8 dimensions with no low-rank handle, so any correction that is not itself
  ~N-dimensional cannot bite.

### Pillar 2 — S7: the amplitude law is chi^2_1, and the MB alternative is dead

Artifact: `experiments/s7_speckle/`. Verdict: **PASS** (2/3 nets inside the predeclared factor-2 window).

- Direction-energy KS distances on the actual 64,512-point Kerdock design: KS(chi^2_1) = **0.009857285778166025 /
  0.00903263919889108 / 0.007147975690644182**; KS(Exp(1)) = **0.16354602400155832 / 0.16492274030232534 /
  0.1642707435175949** [O]. On the independent n = 4,000 Haar probe: chi^2_1 0.016 / 0.015 / 0.009, Exp(1)
  0.162 / 0.160 / 0.170 [O]. Moment shape k = 1/var(e) = **0.41 / 0.42 / 0.44** against chi^2_1's 0.5 and Exp(1)'s 1.0.
- Coherence cone: the depth-32 mean-field correlation plateau is c_32(0) = **0.9747204751243136**; the vector-energy
  shape k_eff ~ 0.77–1.02 implies an effective ~1.5–2 independent neuron amplitudes out of 256 — the neurons are almost
  fully coherent [O + D]. This is the same cone that kills the fidelity family (§3.1, F2).
- Angular correlation length xi (half height): **36.98 / 35.60 / 45.95 deg**, bootstrap 95 % CIs [32.9, 45.0] /
  [32.2, 40.6] / [40.0, 49.5]; ratios to the infinite-width mean-field 20.91 deg: **1.7681434630228277 /
  1.7025351579122494 / 2.1975294620411283** [O]. The artifact's own honest reading: all three sit on the same high side,
  "a systematic finite-width offset, not scatter" — inside the factor-2 gate for 2/3 nets, net 303 marginally out at 2.20.
- **Second signal:** independent fresh pair sets (seed base 740000) reproduce all six gated correlations within 2x joint
  SE, max abs diff 0.042; the mean-field kernel is verified against an arcsin-identity re-implementation to 3.3e-16 and
  against a 2e6-sample Monte-Carlo to <= 1.4e-3 [O].
- *Why it is a pillar:* it fixes the **law**. A real field whose energy is chi^2_1 is a single Gaussian amplitude, the
  maximum-entropy law at fixed second moment. No shape parameter is left to exploit.

### Pillar 3 — S7 + S17: the design samples the speckle at exactly the right pitch

Artifacts: `experiments/s7_speckle/` §"Design-spacing adjudication"; `experiments/s17_ibc_floor/` §A.3.

- Design geometry: minimum inter-direction angle **86.41667830152804 deg** = arccos(1/16) (the Kerdock cross-frame
  coherence), 90.00 deg within a frame; antipodal doubling adds no closer pairs [O, S7].
- Speckle length xi ~ 36–46 deg, so the design sits a factor ~2 **above** the speckle scale: distinct design directions
  are separated by ~2x the correlation length, where measured |C_r| <= 0.04 [O, S7].
- Direct measurement on the champion residual at the design's own inner products: c(0) at 90 deg =
  **-0.0012721317816402036 / -0.0012885292561605843 / -0.0013491547893640598**; even part at t = +-1/16 (86.42 deg) =
  **-5.467822805418879e-06 / -5.336899215208749e-06 / -4.852842224198937e-06** [O, S17]. Both are ~0.
- **Second signal:** the exact doubled inner-product census derived from the S6 base census sums to
  **4,161,798,144 = 64,512^2 bitwise**, and the +-1/16 shells come out exactly equal — sign-balanced, the Kerdock +1/16
  excess cancelling under antipodal doubling [D, S17 §A.1, verified in `s17_results.json`].
- *Why it is a pillar:* it converts clause (b) into an operational statement. Speckle whose grains are half the sampling
  pitch gives independent draws — the regime where direction count buys variance reduction at the full 1/N rate, and,
  symmetrically, the regime where no second-order structure remains to exploit at the geometry actually sampled.

### Pillar 4 — S15 + S5: covariate blindness (smooth observables)

Artifacts: `experiments/s15_stratification/`, `experiments/s5_kink_concentration/`. Verdicts: **KILL** and **KILL**.

- S15's gate quantity is swap-halves out-of-sample incremental R^2 beyond Base-B (633 columns spanning all of degree 1
  and the dominant degree-2 terms). Best pooled result over every cheap first-layer covariate set: **0.0156 (1.56 %)**,
  against a predeclared 5 % KILL bar and a 20 % PASS bar met on **0 of 3** nets. Per set: C1 firing rate 0.0056,
  C2 ||h1||_2 0.0126, C3 top-8 0.0030, union 0.0136 / 0.0195 / 0.0138 [O].
- The base is calibrated by its own control: the pure-degree-1 C4 control reads **-0.0000 on all three nets under
  Base-B**, while under the looser Base-A it reads **+0.29 to +0.37** — proof that Base-A's apparent 11 % headroom is
  degree-<= 2 leakage, not covariate signal [O]. This is the single most important methodological point in the pillar:
  without the control, the same data read as substantial headroom.
- Instrument confirmed by positive control: a known degree-4 zonal harmonic measures raw-t^4 R^2 **0.00149 / 0.00122 /
  0.00219**, inside M191's archived 0.0018–0.0023 band; the *pure* degree-4 increment is **~6e-6 to 1.2e-5** — three to
  four orders smaller, so the apparent degree-4 signal is almost entirely degree-2 contamination the design already
  integrates exactly [O].
- S5 tests the sharpest geometric hypothesis available (residual energy concentrating near ReLU kinks): pooled near/far
  decile ratios **0.978 / 0.978 / 1.006 / 1.007** against a PASS bar of >= 3, per-net Spearman all |rho| <~ 0.005 with
  signs flipping between nets. The data constrain any true |rho| to <~ 0.01, two orders below what a 3x ratio needs [O].
- **Second signals:** S15's reuse of the S5 target validated two ways at max abs diff **0.0** (bit-identical d1
  recompute; full 32-layer forward recompute of ybar). S5 ran a circular positive control — binning |r|^2 by deciles of
  |r| itself — returning ratios **849–883** with strict monotonicity on all 3 nets, proving the decile machinery detects
  real structure when present [O].
- *Why it is a pillar:* it closes the smooth-observable family — every cheap function of the first layer, and the
  sharpest geometric feature of the ReLU arrangement, are blind.

### Pillar 5 — S18: combinatorial blindness, with a stated mechanism

Artifact: `experiments/s18_cell_membership_probe/`. Verdict: **KILL**.

- Every gated cell-membership feature set is below the predeclared fitting-noise cost of 2.63e-5 on all 3 nets; best
  gated value **2.371e-5** (hamming_modal_majority, net 303). The 1e-4 SIGNAL bar is reached on **0 of 3** nets (2+
  required). Top-k cell indicators are consistently negative at k = 256 (**-1.931e-4 / -9.808e-5 / -6.974e-5**) — the
  pure overfit-penalty signature [O].
- **The mechanism, not just the number.** The cell census is identical on all three nets: all **64,512 directions occupy
  64,512 distinct first-layer activation cells** — every cell a singleton, max cell count 1, zero exact-zero
  preactivations [O]. A "most frequent cell" indicator is therefore 1 on at most one direction; fitted on the training
  half it can memorise a single residual and can never activate out of sample. Cell-identity features are *structurally*
  incapable of generalising at design spacing, which is why the number is not merely small but zero-in-expectation.
- **Second signals:** a permutation null (f shuffled, 3 permutations x 3 nets) puts per-set max |incremental OOS| at
  5.6e-5 / 6.7e-5 / 1.4e-4 / 5.3e-5 / 1.2e-4, so every gated measurement sits inside its own null spread; an injection
  test recovers a synthetic 1e-3 R^2 signal at **1.53e-3 / 0.89e-3 / 0.71e-3**, so a 1e-4 effect on 2+ nets could not
  have been missed by an order of magnitude; and the pipeline reproduces S15's cached C1 numbers to |diff| <= 8.8e-7 and
  S15's Base-B OOS R^2 exactly (0.3609 / 0.4037 / 0.4385) [O].
- *Why it is a pillar:* it closes the **non-smooth** family the smooth pillar could not reach, with a structural reason
  rather than a null result alone. This was the one un-probed crack the Gen-7 adversarial fleet named, killed same-day
  [R, `core/GEN7_ADVERSARIAL_CLOSURE_20260810.md` §Fleet 2].

### Pillar 6 — S8 + S12: the depth mechanism and its finite-width offset

Artifacts: `experiments/s8_layer_profile/`, `experiments/s12_finite_width_kernel/`.
Verdicts: **FAIL-PASS / NOT-KILLED** and **PARTIAL / DERIVED**.

- S8 measures a layer-resolved defect profile by redrawing one layer at a time. The infinite-width mean-field prediction
  is exactly **flat** (chi_1 = f'(1) = 1 at He criticality; p_l = 1/32 = 0.03125 per layer). The measurement is not: the
  profile is monotone decreasing over two orders of magnitude, max deviation vs flat **31.3 / 26.3 / 21.5** (all at layer
  31), so the PASS gate fails 3/3; the KILL gate does not fire because the structure is highly coherent — pairwise
  Spearman of per-net share profiles **0.992 / 0.985 / 0.987**, mean **0.988** [O].
- The shape is near-geometric with per-layer factor **rho = 0.869 / 0.879 / 0.876** (aggregate 0.876) — an effective
  per-layer defect transmission of ~0.87, not the mean-field 1.0 [O, labelled derived-after-measurement in the
  artifact]. Top-5 layer share **0.459** mean (flat: 0.156); last-3 layers share **0.0054** mean, **16–22x below** their
  flat share of 0.094 — the layers the fold already exactifies are the ones whose realised-weight defects matter least.
- S12 supplies the theory and separates the two offsets cleanly. *Mean drift* (Jakub & Nica arXiv:2302.09712 angle flow,
  rho(256) = 9.2984e-3): the linearised per-layer angular transmission along the ambient 90 deg trajectory has geometric
  mean **0.8898**, inside the predeclared gate [0.83, 0.91] and within 2.4 % of S8's fitted 0.869–0.879 — **PASS**.
  The same drift **cannot** explain S7's widened correlation curve: hits 4/7 on every net (>= 5/7 on >= 2/3 required) —
  **FAIL**; the flow's own half-height is 19.39 deg (verbatim) to 21.72 deg (hybrid) against a measured 36–46 deg.
  *Fluctuation* explains that instead: the ReLU kernel's per-layer variance is (5/n)K^2, compounding to
  Var[ln K_D] = 5D/n = **0.625** (exact-chain MC **0.636**), and the induced expected half-height inflation is
  **1.577 +- 0.001** (MC on the exact mean-field curve) with analytic exponential-tail cross-check **exp(5D/n) = 1.868**
  — gate [1.5, 2.4] **PASS**, bracketing the measured 1.70–2.20 [D + O].
- **Second signals:** S8 recomputed every arm's v as Var(r) + Var(r_l) - 2Cov(r, r_l), max relative discrepancy
  **2.55e-14**, and rebuilt one resampled forward bit-for-bit; S12 ran eight checks including reproducing S7's committed
  mean-field c_32 to 1.4e-15 and re-fitting S8's rho from the committed v_l tables to 0.8695 / 0.8758 / 0.8793 [O].
- *Why it is a pillar:* it says **where the speckle comes from**. The residual is dominated by early layers under a
  geometric 0.87^l weighting, the last three layers contribute 0.5 % of it, and both committed anomalies are two
  different moments of the same 1/n correction — which makes the speckle a physical object, not a fitted description.

### Pillar 7 — S17: the floor, located

Artifact: `experiments/s17_ibc_floor/`. Verdict: **GATE (i)** — champion within 2x of the sampling floor.

- Field variance sigma^2 = Var(ybar) over the 64,512-point design, computed two ways with relative difference **0.0**:
  **7.900e-3 / 1.600e-2 / 1.112e-2** [O].
- Equal-FLOP iid Monte-Carlo floor sigma^2 / N_eval: 1.225e-7 / 2.480e-7 / 1.724e-7 against champion per-net MSE
  1.997e-7 / 5.872e-7 / 2.369e-7 — ratios **1.63 / 2.37 / 1.37**, pooled **1.7906808367797993** (sd 0.5157, se 0.2977,
  t-95 % CI [0.510, 3.072]) [O]. On the distinct-direction accounting (the 64,512 forwards are 32,256 base directions
  plus antipodes) the ratio is **0.82 / 1.18 / 0.69**, pooled **0.8953404183898996** — the champion sits *at* the floor.
- Effective independent draws N_eff = sigma^2 / MSE_champ = **39,557.85 / 27,251.21 / 46,955.11**, pooled **~38k** —
  about 60 % of the 64,512 evaluations, i.e. an antipodal pair is worth ~1.2 independent draws, not 2 [O + D].
- The S(B) envelope: analytic degree-<= 2-exact closure plateaus at **9.6e-5** regardless of budget; the sampling line
  runs through the champion at 2.818e-7 (1.768e11 FLOPs) and 5.35e-8 at 5.27x budget. Gap between plateau and line:
  **340.66713981547196x** raw, **524.0174672489084x** adjusted [R + D].
- **Second signals:** the champion MSE matches the cached m181 arm-0 value to ratio **0.9999972 / 0.9999987 /
  0.9999972**; the doubled census identity is bitwise; the pooled ratio 1.79 lands inside the S7-measured finite-width
  band [1.7, 2.2] (same slow-decorrelation origin — corroborating, explicitly not claimed as an identity); two full runs
  are bitwise identical on every printed number [O].
- *Why it is a pillar:* it turns "nothing left to exploit" into a number with a gate, and it is the only pillar
  constraining the **absolute** achievable error rather than a family of mechanisms.

---

## 3. Consequences

### 3.1 Why every output-side estimator class dies — and dies the same way

The corpus independently reduced 238 falsifications to seven root-cause failure families
[R, `core/FAILURE_MODE_GRAPH_20260810.md`]. Read through the theorem, three of the seven are one clause seen from
different sides and the rest are its boundary conditions:

| family | representative kills | the clause that kills it |
|---|---|---|
| F1 DISPERSION | M191, S5 (0.978), S15 (1.56 %), S18 (2.37e-5) | (a) — degree-4 error spread over ~1.8e8 dims, flat shelf, no low-rank probe |
| F2 FIDELITY | S10 (0.056x), S13 (0.955x) | (b)+(d) — the field is an exact fingerprint of the precise early-layer weights (S8 0.87/layer, S7 coherence cone) |
| F3 CLOSURE | M181, N5, T2 (9.6e-5) | (a) — degrees <= 2 close exactly then stop; the remainder is the non-Gaussian degree >= 4 residual |
| F4 SYMMETRY | M180, kriging/BLUE | (a) — the design is a group orbit, so LP-optimal weights are uniform; perturbing it breaks the exact 2-design |
| F5 INFORMATION-GATING | S2/P2/P2b, A1b | (b)+(c) — an independent max-entropy field carries no cheap quality signal |
| F6 COST/CLOCK | N8b, M183 (0.00 %), M184 (0.00 %) | boundary condition: the meter bills FLOPs and the billed compute is already minimal |
| F7 EXACT-CONTROL/ABI | the M120–M179 exact-control lineage | boundary condition: correct mathematics dying at cost / byte-ownership gates |

The mechanical statement: an output-side estimator improves on the champion only by finding structure in r(u) that a
sub-budget observable can see. Clause (a) says the structure below degree 4 is already consumed and the structure at
degree 4 is N-dimensional and flat; clause (b) says the amplitude law has no free shape parameter; clause (c) says there
is no second-order structure at the geometry actually sampled. Pillars 4 and 5 confirm this for the two concrete
observable families at gates two orders below the profitability floor, and the Gen-7 fleet reached the same conclusion
adversarially: degree->= 4 content measures ~1e-5 R^2 against a control-variate lens, and the exact-identity lens found
all four closed-form conditional expectations already consumed [R, `core/GEN7_ADVERSARIAL_CLOSURE_20260810.md`].

### 3.2 Why the estimator is correction-proof

This is the surprising direction, and it is the same measurement. A maximum-entropy unbiased field has **zero fitted
structure to overfit**. The champion carries **zero measured bias** and **no fitted component**
[R, Gen-6 packet §"Champion state", N8c], so any post-hoc correction fitted on one seed has nothing to latch onto that
transfers — and, symmetrically, nothing to lose on a fresh-seed re-run. The private fresh-seed holdout is **costless** to
a construction with no fitted component [R, same file, §"Holdout firewall"]. The adversarial version: an MSE-optimal
shrinkage weight against a measured-unbiased baseline is ~0, and every realizable biased-hybrid form the Gen-7 fleet
built measured **-5.7 % to -38 %** [R, Gen-7 Fleet 1]. The one seed-side construction the theorem could not exclude a
priori — building the rotation from the weights' own SVD basis instead of the grader seed — measured a clean null under
common random numbers and bit-identical determinism: paired t **+0.19**, better on exactly **50/100 nets**, bootstrap CI
symmetric about zero, **+3.6e8 billed FLOPs for nothing** [R, Gen-7 Fleet 1, ledger 242].

So the hardest wall and the strongest guarantee are one number: the property that makes the residual unimprovable is the
property that makes it unbreakable.

### 3.3 What sets the floor

The floor is the speckle's independent-cell count. (1) sigma^2 is the field's variance over the design, a fixed property
of the net at (n, D) = (256, 32), measured at 7.9e-3 / 1.60e-2 / 1.11e-2 [O, S17]. (2) The 64,512 evaluations realise
**N_eff ~ 38k** independent speckle cells, not 64,512, because antipodes share even-harmonic content [O + D]. (3)
Achievable MSE for any point-evaluation estimator is then bounded below by sigma^2 / (independent evaluations affordable
at budget B); the champion measures 1.79x above that on the forward-count accounting and 0.90x on the distinct-direction
accounting — inside the predeclared 2x band either way, so **the floor is located and the champion sits essentially on
it** [O]. (4) The floor is a FLOP invariant for the point-evaluation class: MSE x C >= sigma^2 x (FLOPs per independent
evaluation). S17 Part C uses this to adjudicate one external leaderboard entry as **2.2x–4.0x below the best
point-evaluation floor at its own budget** — hence either seed-side or mis-metered, a disambiguation S17 explicitly
declines to make from firewall-clean data [O for the arithmetic, A for the class assumption]. Governance note: the
public writeup v8 deleted all competitor-facing adjudication and de-escalated the floor language; this paper retains the
invariant because the invariant is the physics, and flags the adjudication as internal-only
[R, `core/GEN7_ADVERSARIAL_CLOSURE_20260810.md` §Fleet 3 item 2].

The width of the unoccupied region — 340.67x raw / 524.02x adjusted between the analytic closure plateau and the
sampling line — is not headroom left on the table by bad sampling. It is the price of information: pay FLOPs on the
sloped arm, or accept 9.6e-5 on the plateau [D, S17 §B].

---

## 4. Honest scope

This section exists because the campaign's own adversarial pass found that its two injuries were paperwork and
over-claims, both repaired the same day [R, `core/GEN7_ADVERSARIAL_CLOSURE_20260810.md`]. The corrections stand here.

**4.1 The kills are family-local, not universal.** Every KILL above bounds a *named* family under *its own* predeclared
gate: S15 kills cheap first-layer covariates entering linearly, S18 kills first-layer cell-membership features, S5 kills
kink-localised frames. None is a proof that no output-side estimator exists. The Gen-6 packet states it precisely:
"kills bound families, not the universe of output-side estimators"; "untested output-side estimators are not excluded by
proof; they fall only family-by-family as they are named and killed" [R, `core/RECURSION_PACKET_GEN6_20260810.md`].

**4.2 S17 is a lower-bound attempt, not a minimax result.** The artifact self-labels: "This is a **lower-bound attempt**,
not a minimax-optimality proof and not a closure certificate. Achievable-envelope points below are **upper bounds** on
S(B); the ednacob floor-invariant gap is a **lower bound** (impossibility). They are not conflated" [S17 header]. Its own
limitations add that the per-net champion MSE rests on 16 rotation replicates at ~36 % relative SE each, so the pooled
ratio 1.79 has a wide t-CI ([0.510, 3.072]); that the floor is read from sigma^2/N and **not** from the
correlation-kernel formula (the 64,000x cross-shell coefficient makes the kernel path numerically unusable — the naive
plug-in returns 24.9, a documented artifact, not a floor); and that the even/odd harmonic split explaining the 2x
accounting difference could not be verified from the committed arrays and was omitted rather than reported unverified.

**4.3 Per-pillar limitations a future session must carry.** S6's full-N spectrum is a closed form resting on the verified
exact three-value inner-product structure, degree-6's top spectrum was not numerically re-validated, and the subsample
arm is float32 (~6e-8 relative quantization). S7's factor-2 gate is passed by 2/3 nets with net 303 at 2.20, all three
ratios on the same high side; its KS distances are descriptive; its chi^2_1 fit covers the neuron-averaged field only.
S8 used 3 reps per (net, layer), so deep-layer sem/mean reaches ~0.3–0.4 and individual deep-layer deviations carry wide
error bars; v_l conflates a layer's own defect with downstream scrambling, and the separating experiment (small-epsilon
perturbations instead of full redraws) was not predeclared and not run. S12's route-(b) mapping from kernel fluctuation
to angular log-decay is an explicitly unpublished link flagged by its own source brief — everything downstream is exact,
but as a fully quenched per-net factor the model over-disperses (predicted IQR 0.84–2.09 vs a measured 1.70–2.20); its
route-(a) identification of S8's decay rate with the *first* power of the angular transmission is what the data prefer
(0.890 vs 0.869–0.879) while the variance-power reading gives 0.79 and would fail, and no derivation of the power is
claimed. S15's covariates and S18's aggregates enter linearly, and S18 probes the **first** layer's arrangement only.
All of it is three synthetic He nets, one rotation each, at a single (width, depth) = (256, 32) under one frozen probe
design — **no claim about trained networks is made anywhere**.

**4.4 The dispersion-model correction.** A previously asserted DIFF_RATIO of 1.1x was refuted by the campaign's own
committed data; S1b re-measured vD at 0.08–0.12 with a 17–23 % / 77–83 % split, bracket-validated against the hosted
15.53x spread, giving fresh-seed bands [1.54e-7, 2.16e-7] (50-net) and [1.62e-7, 2.06e-7] (100-net) [R, Gen-7 Fleet 3
item 3]. Any future use of a dispersion model must start from those numbers, not the retired one.

**4.5 The open question, stated abstractly.** Clause (d) is the whole of it. The residual is a deterministic function of
weights the estimator possesses; every pillar above measures the strength of that determinism *against output-side
adversaries operating below budget*, certifying pseudo-random strength rather than information absence. So:

> **Open (seed-side extraction).** Does there exist an estimator that reads the weights directly — un-randomising the
> residual at its source rather than testing its output — and reaches, at comparable budget, an MSE inside the ~340x
> region between the analytic closure plateau and the sampling line?

Three things are known about it and no more. (i) Among the classes actually tested, that region is reachable only from
the seed side [D, S17 §B + Gen-6]. (ii) The one seed-side construction built and measured so far — deriving the rotation
from the weights' own singular basis — is a clean null (§3.2): a marginally-Haar rotation coupled to the weights'
singular basis buys no alignment with the fixed cubature frame. (iii) A separately-governed, held diagnostic exists to
measure whether the coefficient geometry any seed-side estimator would need is present at all; carrying no per-FLOP
deployment credit, it cannot by construction measure the seed-side segment of the budget curve, certify a floor, or
close the campaign [R, Gen-6 packet, decision rule]. This paper takes no position on that diagnostic's outcome and
cites none of its internals.

**4.6 Firewall.** Every pillar ran on synthetic nets with cached Monte-Carlo only: no truth arrays, no scorer, no private
targets, no submissions, no git. Frozen sources are imported read-only and never edited (`run_n8a_gates.py` and
`kerdock_phases.npz` are read-only imports; see the S15 and S18 firewall sections).

---

## 5. Reproduction map

Paths are relative to the corpus root
`C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\publish\recursive-estimator-folding\corpus\whestbench`.

| pillar / claim | harness | numeric results | verdict prose |
|---|---|---|---|
| P1 degree-4 boundary, flat shelf, 42x mode | `experiments/s6_bragg_spectrum/run_s6.py` | `s6_results.json`, `s6_sub_eigs.npz` | `experiments/s6_bragg_spectrum/S6_VERDICT.md` |
| P2 chi^2_1 speckle, coherence cone, xi | `experiments/s7_speckle/run_s7.py` | `s7_results.json` | `experiments/s7_speckle/S7_VERDICT.md` |
| P3 design spacing vs speckle length | `run_s7.py` + `experiments/s17_ibc_floor/run_s17.py` | `s7_results.json` (`design_spacing`), `s17_results.json` (`A_per_net.*.emp_c*`) | S7 §"Design-spacing adjudication", S17 §A.3 |
| P4 smooth covariate blindness | `experiments/s15_stratification/run_s15.py`, `experiments/s5_kink_concentration/run_s5.py` | `s15_results.json`, `s5_results.json`, `s5_net{101,202,303}_arrays.npz` | `S15_VERDICT.md`, `S5_VERDICT.md` |
| P5 singleton-cell mechanism | `experiments/s18_cell_membership_probe/run_s18.py` | `s18_results.json` | `S18_VERDICT.md` |
| P6 depth law 0.87/layer + finite-width origin | `experiments/s8_layer_profile/run_s8.py`, `experiments/s12_finite_width_kernel/run_s12.py` | `s8_results.json`, `s8_run.log`, `s12_results.json` | `S8_VERDICT.md`, `S12_VERDICT.md` |
| P7 floor, N_eff, S(B) envelope | `experiments/s17_ibc_floor/run_s17.py` | `s17_results.json` | `S17_VERDICT.md` |
| the synthesis (god-node framing) | — | — | `core/GOD_NODE_SYNTHESIS_20260810.md` |
| computational-vs-ontic entropy correction | — | — | `core/RECURSION_PACKET_GEN6_20260810.md` |
| adversarial evidence (20 agents, 3 fleets) | — | — | `core/GEN7_ADVERSARIAL_CLOSURE_20260810.md` |
| 7 failure families / positive duals | — | — | `core/FAILURE_MODE_GRAPH_20260810.md` |

Shared machinery (read-only): `experiments/n8a_rqmc_kerdock/run_n8a_gates.py` exports `load_kerdock_directions`,
`he_mlp_weights`, `haar_rotation`, `WIDTH`, `DEPTH`, `MEAN_CHI_256`, `N_BASE`; the frozen sampling asset is
`kerdock_phases.npz`. Reference anchors reproduced by more than one pillar:
`experiments/pb1_premise_battery/m191_g0a_results.json` (degree-4 design/iid ratios 0.10668 / 0.10719 / 0.09829) and
`m191_g0b_results.json` (per-harmonic degree-4 R^2 band 0.0018–0.0023).

**Determinism.** S5, S6, S12 and S17 each report two runs bitwise identical on every measured quantity; S8 reproduced a
resampled forward bit-for-bit; S15 and S18 reproduced the S5 target at max abs diff exactly **0.0**. A future session
re-running any harness should expect bitwise agreement and treat disagreement as an environment change, not a result.

### Constants worth memorising

Setting constants (width 256, depth 32, N = 32,256 / 64,512, radius `mean_chi(256) = 15.98438266660853`, champion raw
2.818e-7 / adjusted 1.832e-7 at C/B 0.650 and 1.768e11 FLOPs) are in §1.1. The measured ones:

| symbol | value | source |
|---|---|---|
| design min angle | `arccos(1/16) = 86.41667830152804 deg` | S7 `design_spacing` |
| dim H_4 / dim H_6 | 183,148,480 / 414,173,091,136 | S6 `constants` |
| tr(D^2) at degree 4 | 3.099748626998932e-05 (exact pairwise) | S6 |
| top-100 share of tr(D^2) | 0.0032221249837913308 | S6 `gate` |
| participation rank | 32,266.169565128537 | S6 |
| quadrature-mode suppression | 42x below bulk | S6 |
| coherence plateau c_32(0) | 0.9747204751243136 | S7 `meanfield` |
| speckle length xi (half height) | 36.98 / 35.60 / 45.95 deg | S7 |
| KS(chi^2_1) on the Kerdock design | 0.009857 / 0.009033 / 0.007148 | S7 |
| per-layer defect transmission | 0.869 / 0.879 / 0.876 (S8); 0.8898 (S12 flow) | S8, S12 |
| Var[ln K_D] = 5D/n | 0.625 predicted, 0.636 exact-chain MC | S12 |
| smooth covariate ceiling | 1.56 % pooled OOS incremental R^2 | S15 |
| combinatorial ceiling | 2.371e-5 best gated (bar 2.63e-5) | S18 |
| sigma^2 (field variance) | 7.900e-3 / 1.600e-2 / 1.112e-2 | S17 |
| N_eff | 39,558 / 27,251 / 46,955 (~38k) | S17 |
| champion / floor | 1.7906808367797993 cost-matched, 0.8953404183898996 distinct-direction | S17 |
| plateau-to-line gap | 340.66713981547196x raw, 524.0174672489084x adjusted | S17 |

---

## 6. How to falsify this paper

Stated so a future session does not have to invent the attack. **Break clause (a)** by exhibiting a degree->= 4
statistic of r(u) whose out-of-sample incremental R^2 beyond the S15 Base-B basis exceeds the 2.63e-5 profitability
floor on 2+ of nets 101/202/303 — the S18 harness is the ready-made instrument, and its injection test shows it detects
at 1e-3 and would not miss 1e-4 by an order of magnitude. **Break clause (b)** by finding a shape statistic on which the
direction-energy law departs from chi^2_1 by more than the 0.0071–0.0099 KS distance already measured, on a probe set
independent of the design. **Break clause (c)** by exhibiting a design geometry whose realised inner-product shells show
residual correlation materially above the measured -1.3e-3 / -5.5e-6 — a sampling pitch that resolves speckle grains.
**Break the floor** by measuring a point-evaluation estimator at MSE x C below the S17 invariant at matched budget; by
S17's own arithmetic that requires more independent information than the estimator has function queries, so a positive
result is more likely a metering error than a physics result — check the meter first. **Break clause (d)**, the only
genuinely open door, per §4.5. A failure of the first three localises the error to one pillar; a failure of the fourth
without a metering fault falsifies the synthesis.
