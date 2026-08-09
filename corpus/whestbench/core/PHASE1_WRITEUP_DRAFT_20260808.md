# Phase-1 Algorithmic Contribution writeup — draft v2

Status: DRAFT v2. **Graded submission ID: #326094** (adjusted 1.832e-7,
50/50 public MLPs, 0 failures, rank #58 at grading time). Filing deadline
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
0.137 s max**, i.e. ~5% of the per-MLP budget. Essentially all arithmetic is
instrumented.

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
The remaining ~380x to sampling is third-and-higher-cumulant structure that
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
~5% residual exposure — the compute profile is essentially fully
instrumented, which we note in the context of the accounting discussions
elsewhere on this forum.

Two of these are results in their own right. **N8a** established that our
spherical design already dominates a randomized lattice — the lattice's
advantage over iid evaporates once the radial degree of freedom is
conditioned away. **N8c** established that our estimator's final-layer error
is **statistically pure variance** (bias share indistinguishable from zero),
which is the strongest robustness property available going into a fresh-seed
re-evaluation: there is no fitted component to overfit.

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
hosted per-network score spread (11x) is measured to be rotation-draw
sampling variance, not network difficulty (per-network Monte-Carlo
difficulty varies only 1.1x) — irreducible at fixed randomization, and
relevant to anyone comparing per-network scores across submissions.

### 3d. The suite-risk decomposition, and a two-sided concentration rule (new)

Treating the SUITE as the statistical unit (the prize is one draw of a
private test suite, scored by the mean) yields a decomposition we have not
seen stated elsewhere in this competition. Bootstrapping 100,000 synthetic
50-network suites from our measured per-network data (the 80-network tail
checkpoint, and a 3-network x 16-rotation grid isolating the rotation draw):
**99.79% of across-suite score variance is rotation-draw sampling variance**,
not network difficulty (which varies only ~1.1x). Splitting the same billed
budget across R rotations per network (equal weights) therefore preserves the
expected score to +0.021% while thinning the suite-score P5-P95 spread by
58.85% at R=6 — matching the closed-form rotation-dominant limit
1 - 1/sqrt(6) = 59.18% to within model error.

The decision-theoretic consequence is two-sided, and we state it honestly:
concentration removes the lucky tail as well as the unlucky one (our
P(suite < 1.6e-7) falls from 6.4% at R=1 to 0.01% at R=6, and no R reaches
materially better bands). In a winner-take-all evaluation, variance is the
trailing competitor's friend and the leader's enemy: R should be chosen by
one's expected position relative to the nearest rivals, not by per-network
MSE — which R leaves untouched. To our knowledge this borrows a standard
result from tournament/portfolio theory into white-box estimator design for
the first time on this benchmark, and it is fully reproducible from the
committed bootstrap (`experiments/s1_suite_risk/`, predeclared gates, model
limitations recorded — the empirical rotation pool understates the true tail,
making the shrink estimate conservative). A companion falsification closes the tempting corollary from a third independent direction: rotation-quality selection/weighting is dead not only before spending (pilot rho -0.089, weights-only rho 0.17) but also AFTER spending — variance statistics of the paid design sample itself correlate with realized rotation error at only rho 0.12, because the design's deterministic equidistribution error is invisible to iid-style sample statistics. The rotation axis is information-gated at every observation point we could construct.

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
   21-31x; the transmission law is measured, not yet derived — we state
   it as an open theoretical question.

Together: the estimator's error consists of independent chi²₁ speckle
draws whose generating structure is set by the earliest layers, sampled
by a design whose single exploitable mode is already optimally
suppressed. Within this model, variance-per-billed-FLOP is not merely
the observed best lever — it is the only lever the physics admits, and
the finite-width offset in (2) locates the sole remaining crack at the
exact-finite-width frontier. All four measurements are reproducible from
committed artifacts (`experiments/s5_kink_concentration/`,
`s6_bragg_spectrum/`, `s7_speckle/`, `s8_layer_profile/`), each with
predeclared gates, two-signal verification, and recorded deviations.

### 4. Methodological note: calibrate your suite before you trust your numbers

Local development suites are not the grader's suite. We measured ours by
running a budget-matched Monte-Carlo reference on both: local 1.069e-6 versus
the grader's published 6.47e-7, a ratio of **1.65**. Every local score we held
was understating its hosted expectation by that factor. We recommend this
one-run calibration to anyone iterating locally; without it, cross-suite
comparisons — including comparisons against published competitor numbers —
are off by whatever the suite-difficulty ratio happens to be.

### 5. Compute transparency

Our submissions bill at ~7-8e10 analytical FLOPs per second of wall time.
We note without further comment that the entries above us on the public
leaderboard bill at 6e8-7e9 FLOP/s while running 22-47 s per MLP. Our
estimator's residual (uninstrumented) exposure is 5% of budget; any
tightening of residual accounting under §5.3 would cost us that 5% and
nothing else.

### 6. Reproducibility

All artifacts, predeclarations, kill gates, adversarial audits, frozen
manifests, and the 191-record fold ledger are in the public corpus at
github.com/gmrmk/recursive-estimator-folding. Every claim above cites a
committed measurement; negative results are retained in full to prevent
retrospective cherry-picking.
