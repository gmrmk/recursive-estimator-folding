# Phase-1 Algorithmic Contribution writeup — draft v8

Status: DRAFT v8, 2026-08-10. v8: level-repair pass — §5 adjudication removed, floor language set to S17's earned framing, §3c/3d dispersion corrected per S1B, residual restated. **Graded submission ID: #326094** (adjusted
1.832e-7, 50/50 public MLPs, 0 failures, rank #58 at grading time). Filing deadline
Aug 17, 23:59 UTC per the Algorithmic Contribution guidelines thread.

---

## Structured spherical designs, and a certified measurement of where
## mechanistic estimation stops working at depth 32

### Executive summary

We submit a sampling estimator built on a **structured phased-Hadamard
spherical design** with exact radial conditioning, pilot-rescued structural
pruning, three-terminal-layer folding, and a frozen first-layer moment-tangent
control. On our local suite it scores adjusted 1.62e-7 against a
budget-matched Monte-Carlo baseline of 1.07e-6 — a **6.6x improvement per
FLOP over sampling**, with zero measured bias at the scored layer.

Alongside it we contribute something we believe is more durable than the
score: a **certified-exact Gaussian-closure implementation** and a direct
measurement of its error at depth 32, which quantifies the non-Gaussianity
wall that bounds every moment-propagation method on this benchmark; and an
**eight-mutation falsification ledger** in which every proposed improvement
was predeclared with a kill gate before implementation, and every one of them
died on measurement.

New in v7, restated at its earned level in v8: the wall now has a measured
floor **bound** — a gated lower-bound attempt (§3e(5)) places the champion
within ~2x of the per-forward point-evaluation floor (pooled 1.79x; per net
1.63 / 2.37 / 1.37) and at 0.90x on the distinct-direction accounting,
robust within ~2x of its stated assumptions; it is a lower-bound attempt,
not a minimax-optimality proof — and the falsification structure reduces to
a single stated theorem (§3e).

### 1. The estimator

Five components, each independently measured:

1. **Phased-Hadamard spherical design.** 126 orthonormal frames derived from
   a Kerdock-code phase set, 256 directions each = 32,256 base directions,
   antipodally doubled to 64,512, all at the exact chi-mean radius, with a
   per-network Haar rotation as the sole randomization. Measured **2.0-3.2x
   variance reduction over radially-conditioned Monte Carlo** (three He nets,
   16 paired replicates).
2. **Exact radial conditioning.** A bias-free ReLU network is positively
   one-homogeneous, so the radial degree of freedom integrates exactly and
   every sample can be placed on the mean-radius sphere.
3. **Pilot-rescued structural pruning.** An analytic diagonal pass marks
   neurons with standardized pre-activation below -2 as provisionally cold; a
   256-antipodal-pair pilot rescues any observed firing. Reduces billed FLOPs
   ~1.7x.
4. **Three-terminal-layer folding.** Dead columns vanish, always-on columns
   compose linearly into the next weight matrix, only kink columns retain a
   ReLU.
5. **Moment-tangent control**, frozen coefficient λ = 0.9807112198896164.

Measured compute profile: 2.86 s mean wall per MLP (max 4.11 s against a 60 s
cap), of which residual — the uninstrumented remainder — is **0.080 s mean,
0.137 s max**: 4.5% of scored C on average, 7.7% of adjusted score in the
worst case at C/B 0.650, conditional on λ = 1e11 remaining fixed (Rules §5.3
reserves changes). Essentially all arithmetic is instrumented.

### 2. The non-Gaussianity wall (the main scientific contribution)

Moment/cumulant propagation is the natural white-box approach and the one the
organizers' own materials highlight. We built it to the strongest form we
could **certify**, then measured exactly how far it falls short.

**Certified machinery.** A bounded-cost bivariate provider evaluates the
rectified-Gaussian pair moment E[ReLU(X_i)ReLU(X_j)] and its derivatives via
Owen-T/Φ₂ with per-call enclosure certificates, a fixed 4,048-FLOP budget per
pair, charged sign comparisons, exact strata at the rank-one and
zero-variance limits, and a 12,890-case adversarial census (all contained).
On top of it, an exact zero-order full-covariance recurrence (μ₀=0, V₀=I;
aₗ = μWₗ; Cₗ = Wₗᵀ Vₗ₋₁ Wₗ; post-ReLU moments from exact Tallis truncated
moments) propagates the complete 256×256 covariance through all 32 layers,
inclusively metered at 8.30e9 FLOPs = 3.05% of budget. Assembly agrees with
30-digit mpmath references to 2.144e-9 and with an independent closure
implementation to ~2e-16.

**The measurement.** Predicting the depth-32 final layer, against 400k-sample
Monte-Carlo truth on He-initialized networks (MC noise floor 1-2e-7, i.e.
200-1000x below the signal — the numbers are resolved, not noise):

| predictor of the depth-32 final-layer mean | bias MSE |
|---|---:|
| diagonal Gaussian closure | 7.18e-4 |
| **exact full-covariance Gaussian closure** | **9.61e-5** |
| sampling estimator (this submission), same budget | ~2.5e-7 |

Making the covariance exact buys a factor of ~7.5 over the diagonal closure.
The remaining 384x to sampling (340.7x against the graded raw 2.818e-7,
524x against adjusted 1.832e-7 — the denominator matters, so we state all
three) is third-and-higher-cumulant structure that
**no Gaussian-moment closure can represent at any compute multiplier** —
even priced at a zero-cost floor the exact closure trails by more than an
order of magnitude.

**The design principle this yields:** exact Gaussian structure pays when
*subtracted* (our moment-tangent control: -19.8% adjusted on its lineage) and
fails when *predicted* (closure-as-estimator: 46x outside the competitive
boundary). We think this is the sharpest available statement of why depth-32
white-box estimation is hard, and it is stated with certificates rather than
intuition.

### 3. Falsification ledger — eight predeclared kills

Every entry was predeclared with its kill gate **before** implementation; none
was retuned after seeing results. All are reproducible from the corpus.

| mutation | hypothesis | measured | verdict |
|---|---|---:|---|
| N4 | cheap variance levers | null | killed |
| N5 | multilevel closure control variate | 1.07x | killed |
| N6 | exact great-circle Rao-Blackwellization | FoM 0.006x | killed |
| N7 | RQMC superconvergence at depth 32 | slopes -0.97/-1.23 vs -1.25 gate | killed |
| N8a | Kronecker lattice vs our frames | lattice **2.1x worse** (CI [1.65,2.65]) | killed |
| N8b | disclosed native backend | 0.94e11 FLOP/s < λ = 1e11 | killed |
| N8c | offline-trained corrector | bias share -0.034 (CI [-0.031,0.097]) | killed |
| N9 | frames + tangent + deeper fold | +2.1% (positive control +34.5% on iid) | killed |
| M180 | stronger spherical designs (MUB mix / coset rotations / remix) | all arms +20-49% variance | killed |
| M181 | terminal rectified-Gaussian smoothing (3 arms incl. unbiased CV) | bias 4-6x baseline MSE; var identical; lambda -> 0 | killed |
| M183 | float32 hot-path recast (the "free 2x") | 0.00% f64-lane billing — already clean | killed |
| M184 | mid-layer exact on-composition + sparsity | 0.00% billed reduction (certain-on absent where wide; 2.3x under break-even at depth) | killed |

M180's kill carries a structural result: the phased-Hadamard design is
LOCALLY OPTIMAL — its strength is the mutual unbiasedness of all 126 frames
under one shared rotation, and every perturbation (family displacement,
rotation fragmentation, per-frame remixing) destroys that negative-covariance
structure monotonically. M181's kill closes the Gaussian-closure family at
every insertion point (predictor / control-variate / corrector / smoother),
each with an independent measured mechanism of failure — and its adversarial
check (the bias field reproduced on fresh iid samples, cosine 0.97-0.98)
pins the failure on the terminal law's non-Gaussianity itself.

**Hosted validation of the submission**: #326094 graded adjusted 1.832e-7
(final-layer MSE 2.818e-7) on 50/50 public MLPs with zero failures, 3.5x
better than the grader's Monte-Carlo reference, at ~1-3 s wall per MLP with
a residual exposure of 4.5% of scored C on average (7.7% of adjusted score
worst-case at C/B 0.650, conditional on λ = 1e11 remaining fixed) — the
compute profile is essentially fully instrumented, which we note in the
context of the accounting discussions elsewhere on this forum.

Two of these are results in their own right. **N8a** established that our
spherical design already dominates a randomized lattice — the lattice's
advantage over iid evaporates once the radial degree of freedom is
conditioned away. **N8c** established that our estimator's final-layer error
is **statistically pure variance** (bias share indistinguishable from zero),
which is the strongest robustness property available going into a fresh-seed
re-evaluation: there is no fitted component to overfit.

Two further proposals die by **exact identity** rather than by statistics,
and we record them as identities. The **Crofton kink-transect identity**
(`experiments/s9_crofton_transect/`): the Gaussian mean of a bias-free ReLU
network equals the Gaussian-weighted surface integral of its gradient jumps
over the kink set — verified at machine precision (structural checks to
6.7e-16, two independent transect estimators, 3 predeclared + 20 fresh
nets) — and the unbiased estimator it induces is killed at 176,860x worse
variance-per-FLOP than MC on the width-64 depth-8 screen (predeclared kill
line 100x). The **residual/norm decomposition identity**
(`experiments/s16_residual_decomp/`, confirmatory; clean statement:
"residual decomposition = antipodal symmetrization"): both proposed forms
reduce exactly to structure the estimator already has. The even/odd
residual split |z|/2 ± z/2 is BIT-IDENTICAL to our antipodal pairing —
layer-1 identity max deviation exactly 0.0 over 8,257,536 entries on each
of 3 nets (IEEE negation is exact and the ReLU pair is a clamp partition),
and the full estimators produce bit-equal final outputs (MSE ratio
1.000000, max final deviation 0.0) on all 48 (net, seed) panels — while
its "analytic linear + Gaussian corrections" deep reading is the closure
family M181 already killed (closure 1.28e-6 vs sampling 3.41e-7): the
linear part is exactly zero-mean (its measured mean decays 2.26x when n
grows 4x, vs 2.0 predicted for pure noise), so the entire signal lives in
the non-Gaussian ReLU corrections. The per-layer residual
reparametrization measures R_l = mean‖F_l‖/mean‖y_l‖ in [1.108, 1.231]
(median 1.162) across all 31 hidden layers — no layer is near-identity, so
no perturbative truncation exists and the form reduces to the depth law of
§3e(4).

### 3b. The design is an exact spherical 2-design, and its error spectrum is
### measured (new)

A deterministic quadrature audit of the 126-frame phased-Hadamard design
(64,512 antipodal directions, three independent rotations): odd-degree
harmonics are annihilated exactly; degree-2 quadrature error is 8.6e-9 —
the design is an exact spherical 2-design, which is the harmonic-analysis
explanation for its measured local optimality (every perturbation of the
family or its shared rotation destroys degree-2 exactness and loses 20-49%
variance). The residual angular error lives at degree 4 (11% of the iid
level) and degree 6 (40%). We then tested the natural exploitation — an
unbiased degree-4/6 harmonic control variate with a weight-derived basis —
and report its honest failure: the estimator functions' energy at those
degrees disperses across ~1.8e8-dimensional harmonic spaces at d=256, so a
tractable basis explains only 0.2-0.3% of per-neuron variance (measured),
and the CV nets +0.83% [CI -0.6%, +2.4%]. The leak is real, characterized,
and — by these measurements — unscoopable by finite projection. We believe
this pair (the exactness theorem + the dispersion no-go) is the sharpest
available characterization of why structured spherical designs plateau on
this task.

### 3c. The marginal-value map (new)

Single-component ablations of the submitted estimator on a cached-truth
panel (paired seeds, CIs): exact radial conditioning 2.14x [1.51, 3.04],
the spherical design 2.02x [1.45, 2.83], antipodal pairing 1.91x [1.41,
2.56] — three multiplicative variance pillars, each exact arithmetic or
proven locally optimal. Terminal folding is exactly MSE-neutral (ratio
1.00003) while saving 4.8% of billed budget; structural pruning is
MSE-neutral (1.014 [0.98, 1.05]) while saving 25.1% — and the adjusted-score
arithmetic makes pruning strictly optimal (removing it is 1.33x worse
adjusted). The first-layer moment-tangent control measures neutral on this
design (1.019 [0.97, 1.06]), consistent with three independent tests. The
hosted per-network score spread (11x) is mostly rotation-draw sampling
variance, with a real net-difficulty component: net-difficulty relative
variance vD 0.08-0.12 (s17 σ²-implied; the p2-implied 0.23-0.36 is an upper
sensitivity), i.e. a per-net difficulty ratio of ~2.7-3.4x
(`experiments/s1b_dispersion_corrected/`). The rotation-draw part is
irreducible at fixed randomization, and the decomposition is relevant to
anyone comparing per-network scores across submissions.

### 3d. The suite-risk decomposition, and a two-sided concentration rule (new)

Treating the SUITE as the statistical unit (the prize is one draw of a
private test suite, scored by the mean) yields a decomposition we have not
seen stated elsewhere in this competition. Bootstrapping synthetic suites
from our measured per-network data (the 80-network tail checkpoint, and a
3-network x 16-rotation grid isolating the rotation draw; dispersion
corrected in `experiments/s1b_dispersion_corrected/`): at R=1, **17-23% of
across-suite score variance is net difficulty and 77-83% is rotation-draw
sampling variance** (net-difficulty relative variance vD 0.08-0.12,
s17 σ²-implied; the p2-implied 0.23-0.36 is an upper sensitivity; per-net
difficulty ratio ~2.7-3.4x). The corrected model brackets the observed
hosted 15.53x 80-net spread (P(sim ≥ obs) = 0.72-0.86), which the original
model missed entirely (P = 0). Splitting the same billed budget across R
rotations per network (equal weights) preserves the expected score while
shrinking the suite-score SD by an analytic 44%/40% at R=6
(vD 0.081/0.122; predeclared 25% gate) — rotation-draw variance stays
dominant under the correction.

The decision-theoretic consequence is two-sided, and we state it honestly:
concentration removes the lucky tail as well as the unlucky one (our
P(suite < 1.6e-7) at R=1 is 9.2-10.6% under the corrected dispersion — the
original model put it at 6.4%, falling to 0.01% at R=6; the R>1 arms were
not re-run under the correction, but the analytic shrink above carries the
same two-sided consequence). In a winner-take-all evaluation, variance is
the trailing competitor's friend and the leader's enemy: R should be chosen
by one's expected position relative to the nearest rivals, not by
per-network MSE — which R leaves untouched. To our knowledge this borrows a
standard result from tournament/portfolio theory into white-box estimator
design for the first time on this benchmark, and it is fully reproducible
from the committed bootstraps (`experiments/s1_suite_risk/`,
`experiments/s1b_dispersion_corrected/`, predeclared gates, model
limitations recorded — the empirical rotation pool understates the true tail,
making the shrink estimate conservative). A companion falsification closes the tempting corollary from a third independent direction: rotation-quality selection/weighting is dead not only before spending (pilot rho -0.089, weights-only rho 0.17) but also AFTER spending — variance statistics of the paid design sample itself correlate with realized rotation error at only rho 0.12, because the design's deterministic equidistribution error is invisible to iid-style sample statistics. The rotation axis is information-gated at every observation point we could construct.

The fresh-seed implication for our own entry, stated for the record: under
the bracket-validated dispersion the champion's suite-score P5-P95 band is
[1.54e-7, 2.16e-7] on a 50-net suite and [1.62e-7, 2.06e-7] on a 100-net
suite, with the mean unchanged (1.830e-7 in every arm). The other exposure
channel in a re-run is accounting, not statistics: the residual channel is
4.5% of scored C on average (7.7% of adjusted score worst-case at C/B
0.650), conditional on λ = 1e11 remaining fixed (Rules §5.3 reserves
changes).

### 3e. A physics derivation of the wall (new)

Four physics-framed measurements, each predeclared with kill gates, now
DERIVE the empirical wall rather than merely measure it:

1. **The design's exact anatomy** (Bloch/Bragg frame). The 64,512-point
   phased-Hadamard design's inner-product multiset is exactly
   {0, ±1/16}; its degree-4 quadrature-error operator has exactly three
   eigenvalue shells, and the design's entire degree-4 advantage is the
   42x suppression of a SINGLE constant mode — with the ±1/16 cancellation
   tuned to degree 4 only, which derives, from pure code structure, the
   measured 11%-vs-40% degree-4/degree-6 error split. The remaining error
   operator is maximally flat (participation rank ≈ N): no Bragg modes
   exist for any design-side control variate to target.
2. **The residual is real-amplitude speckle** (wave-packet frame). Its
   angular correlation length is 36-46° against a first-principles
   mean-field (arccos-kernel) prediction of 21°, monotone everywhere,
   with per-direction energies fitting chi²₁ decisively (KS 0.007-0.016
   at n = 64,512). The design's minimum angle — arccos(1/16) = 86.4°,
   fixed by the same MUB structure as (1) — sits 2x above the speckle
   scale: every design point is an independent draw, so no inter-point
   structure exists to exploit.
3. **The field is statistically homogeneous**: residual energy shows no
   concentration near the ReLU kink set (near/far decile ratios ≈ 1.00
   against a method sensitivity of ~850x), as speckle requires.
4. **A geometric depth law**: layer-defect influence on the output field
   decays at a measured ~0.87 per layer (95x across depth 32; the first
   five layers carry ~46% of field variance, the last three 0.5%),
   consistent with the network contracting onto a coherence-0.975 output
   cone (~2 effective output degrees of freedom of 256) that forgets
   late-layer randomness. The flat mean-field prediction is rejected at
   21-31x. (Both laws were subsequently half-closed from first principles:
   the finite-width angle-flow linearization of Jakub-Nica predicts
   per-layer transmission 0.890 against our measured 0.869-0.879, and the
   D/n kernel-fluctuation expansion predicts a correlation-length
   inflation of 1.58-1.87, bracketing our measured 1.70-2.20. The
   curve-widening shape and dispersion tightness remain honestly open;
   `experiments/s12_finite_width_kernel/`.)
5. **The floor itself** (information frame; `experiments/s17_ibc_floor/`).
   The design's exact inner-product census (1) antipodally doubles to an
   exact five-shell 64,512-point fingerprint — the shell counts sum to
   64,512² bitwise and the ±1/16 shells become exactly sign-balanced —
   and the equal-FLOP sampling floor σ²/N is then read directly from the
   measured field variance. This is a gated lower-bound ATTEMPT, not a
   minimax-optimality proof: it places the champion within ~2x of the
   per-forward point-evaluation floor σ²/64,512 (pooled **1.79x**; per net
   1.63 / 2.37 / 1.37) and at **0.90x** the distinct-direction bound
   σ²/32,256, robust within ~2x of its stated assumptions, with
   N_eff ≈ 38k effective independent draws (~60% of the 64,512 forwards:
   an antipodal pair carries correlated even-harmonic information, so a
   pair of forwards is worth ~1.2 draws, not 2). Second signal: the
   empirical residual correlations at the design's own spacings are
   c(0) = -1.3e-3 and c_even(1/16) = -5.5e-6 — decorrelated at every
   design pair, exactly as the speckle model of (2) requires. One
   disclosed formula correction, reported honestly: the predeclared
   four-term correlation-kernel floor formula is numerically unusable at
   this scale — its cross-shell coefficient is 64,000, so a sub-1e-3
   error in c_even(1/16) moves the predicted inflation by O(10), and the
   naive plug-in returns 24.9, a documented artifact — so the floor is
   anchored on σ²/N directly, with the kernel retained only as
   corroboration.

Together: the estimator's error consists of independent chi²₁ speckle
draws whose generating structure is set by the earliest layers, sampled
by a design whose single exploitable mode is already optimally
suppressed. Within this model, variance-per-billed-FLOP is not merely
the observed best lever — it is the only lever the physics admits, and
the finite-width offset in (2) locates the sole remaining crack at the
exact-finite-width frontier. All five measurements are reproducible from
committed artifacts (`experiments/s5_kink_concentration/`,
`s6_bragg_spectrum/`, `s7_speckle/`, `s8_layer_profile/`,
`s17_ibc_floor/`), each with predeclared gates, two-signal verification,
and recorded deviations.

These measurements assemble into an achievable-envelope map S(B) — the
least MSE reached at FLOP budget B **among tested method classes**. It has
two arms. A budget-independent **closure plateau** at 9.6e-5: analytic
degree-≤2-exact integration removes only the exactly-integrable part, and
cheap first-layer covariates add ≤1.56% out-of-sample R², so more analytic
effort does not lower it. A **1/N sampling line** through the champion
(2.818e-7 at C/B 0.65; 5.35e-8 at 5.27x budget), on which the champion
sits within ~2x of the floor attempt of (5). The vertical gap between plateau and line
at our budget is **340.7x** in raw final-layer MSE (384x against the
~2.5e-7 sampling point of §2, 524x against adjusted 1.832e-7 — the
denominator matters). The gap is not headroom we left by sampling badly;
it is the price of point-evaluation information: pay FLOPs on the sloped
arm, or accept the plateau. Among the classes we tested, the only way to
sit INSIDE the gap — low MSE at low budget — is to leave the
point-evaluation oracle entirely and read the weights themselves. This is
a map of tested classes, not a proof that no untested output-side method
enters the gap.

The synthesis, stated once (`core/GOD_NODE_SYNTHESIS_20260810.md`): a
centrality analysis of the campaign's full failure-and-passes evidence
graph finds ONE god node. The finite-width output of a deep random ReLU
network is maximum-entropy independent chi²₁ speckle sitting exactly at
the degree-4 boundary of a maximum-structure exact 2-design — and this
single fact is simultaneously why every proposed mutation fails (the
speckle's dimensionality, weight-fidelity, and independence are one
property), why the champion is correction-proof (a maximum-entropy
unbiased residual has zero fitted structure to overfit — N8c's measured
zero bias), and what sets the floor of (5) (the speckle's
independent-cell count N_eff). One precision matters, and we state it
carefully: the entropy is COMPUTATIONAL, not ontic. The residual is a
deterministic function of weights we possess — the weights are the seed —
that behaves as strong pseudo-randomness against every sub-budget test we
constructed; the falsification ledger certifies PRNG strength, not
information absence. That is exactly why the 340.7x gap region is, among
tested classes, reachable only by seed-side methods — estimators that use
the weights to un-randomize the structure at the source instead of
testing the output.

### 4. Methodological note: calibrate your suite before you trust your numbers

Local development suites are not the grader's suite. We measured ours by
running a budget-matched Monte-Carlo reference on both: local 1.069e-6 versus
the grader's published 6.47e-7, a ratio of **1.65**. Every local score we held
was understating its hosted expectation by that factor. We recommend this
one-run calibration to anyone iterating locally; without it, cross-suite
comparisons — including comparisons against published competitor numbers —
are off by whatever the suite-difficulty ratio happens to be.

### 5. Compute transparency

Our submissions bill at ~7-8e10 analytical FLOPs per second of wall time;
the graded submission runs at C/B 0.650 (1.768e11 scored FLOPs). Our
estimator's residual (uninstrumented) exposure is 4.5% of scored C on
average and 7.7% of adjusted score in the worst case at that C/B,
conditional on λ = 1e11 remaining fixed; any tightening of residual
accounting under §5.3 (which the Rules reserve) would cost us at most
that worst-case 7.7% and nothing else.

### 6. Reproducibility

All artifacts, predeclarations, kill gates, adversarial audits, frozen
manifests, and the 191-record fold ledger are in the public corpus at
github.com/gmrmk/recursive-estimator-folding. Every claim above cites a
committed measurement; negative results are retained in full to prevent
retrospective cherry-picking.
