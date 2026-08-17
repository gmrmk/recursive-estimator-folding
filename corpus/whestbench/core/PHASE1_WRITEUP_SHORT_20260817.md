# Phase-1 Algorithmic Contribution — short-form writeup

Status: SHORT v1, 2026-08-17, prepared for the Aug 17 23:59 UTC filing. This
document supersedes the v9 filed 2026-08-10, condenses draft v13 (~8,900 words)
to its load-bearing content, and incorporates all thirteen errata recorded
against the filed text (§6). Claim levels use the tags of companion P1:
**[O]** observed, **[D]** derived, **[R]** reported, **[A]** assumed.

## Beyond Gaussian closure: structured spherical quadrature for deep random ReLU networks, and a map of which white-box improvement families fail

### 0. Summary and provenance

1. We submit a structured spherical-quadrature estimator — a frozen
   phased-Hadamard exact spherical 2-design, 64,512 directions at the exact
   chi-mean radius — graded **adjusted 1.832e-7** (raw final-layer MSE 2.818e-7)
   on 50/50 public MLPs with zero failures, 3.5x better than the grader's
   Monte-Carlo reference. **Graded submission ID: #326094.**
2. The durable contribution is a map of the boundary: proofs and matched
   measurements of which white-box improvement families cannot work on these
   networks and why, including an exact two-sided closure of the design axis and
   an analytic variance prediction accurate to 6.4%.
3. The falsification protocol is the second contribution: twelve predeclared
   kills, a 267-record fold ledger with negative results retained in full, and
   adversarial machinery that found and forced the withdrawal of four of our own
   headline claims during the campaign.

Hosted figures throughout are from the graded ledger for #326094
(`a1_hosted_ledger.json`): 5.75 s mean / 6.80 s max wall per MLP against the
60 s cap, at C/B 0.650. Locally measured timings are labelled as such and do
not transfer across hardware.

**Evidence repository** — estimator source, predeclarations, kill gates,
adversarial audits, frozen manifests, and the 267-record fold ledger:

    github.com/gmrmk/recursive-estimator-folding
      /tree/f225be4e4e4872dc2bef06711525cf00e73a332b/corpus/whestbench

Read that path, not the repository root: the default branch is a 2026-08-06
snapshot whose ledger carries 43 records rather than 267. The campaign branch
is `agent/compression-survivor-corpus`; the pinned commit is the pushed branch
tip of 2026-08-17, verified against `origin` before filing, so the citation
cannot drift. The repository is private at the time of this filing; the
organizers are granted read access on request. It contains no challenge data,
no private truth, no scorer, no credentials, and not the #326094 submission
archive.

### 1. The estimator, and exactly which of its numbers were chosen

The estimator integrates over a frozen phased-Hadamard **exact spherical
2-design**: 126 mutually unbiased frames of 256 directions each, every frame an
orthonormal basis `H_256 diag(phi_s)/16`, antipodally doubled to 64,512 points
at the exact chi-mean radius, with a per-network Haar rotation as the sole
randomization. Five components, each independently ablated on a cached-truth
panel with paired seeds and CIs:

1. **The design**, worth 2.02x isolated against radially conditioned Monte Carlo.
2. **Exact radial conditioning.** A bias-free ReLU network is positively
   one-homogeneous, so `E[f(X)] = E||X|| · E[f(U)]` holds exactly at every
   layer. The radial degree of freedom is not reduced, it is *removed*.
3. **Pilot-rescued structural pruning.** An analytic diagonal pass marks
   neurons below a threshold as provisionally cold; a 256-antipodal-pair pilot
   rescues any that fire. Saves **25.109% of B**.
4. **Three-terminal-layer folding.** Dead columns vanish, always-on columns
   compose linearly into the next weight matrix, and only kink columns retain a
   ReLU. Saves **4.828% of B** at an MSE ratio of 1.000033.
5. **A first-layer moment-tangent control**, frozen coefficient, measured
   neutral on this design.

Every value here was read from the deployed method-resolution order
(`estimator.Estimator` → `kerdock_v3` → `fold3` → `base_estimator`), not from
any single class, and is re-derived mechanically by
`scripts/verify_phase1_writeup.py`.

**What is forced, with nothing tunable in it.** The design itself; the sample
count `n_base = 126 × 256 = 32,256`, which is the design's size and not a budget
anyone picked; the exact radius `E||X|| = 15.98438266660852747…` from the chi
moments; and the uniform weights, which are *a* global minimiser of the
quadrature error at every spherical-harmonic degree under a zonal Haar-averaged
criterion — though not the unique one, and on the deployed antipodally doubled
set not unique at any even degree.

**What was selected during development, and is therefore fitted in the sense an
auditor cares about. There are seven.**

| constant | value | role |
|---|---|---|
| `moment_tangent_lambda` | 0.9807112198896164 | first-layer control coefficient |
| `pilot_base` | 256 | pilot pairs for the pruning rescue |
| `fold_pilot_base` | 1,024 | pilot pairs for the terminal fold |
| `dead_alpha` | −2.0 | cold-neuron threshold |
| `on_alpha` | **3.0** | always-on threshold in the fold |
| `phase_start` | 2 | first frame of the deployed slice |
| `phase_stop` | 128 | last frame of the deployed slice |

All seven are scalar and all were frozen before grading. `on_alpha` deserves its
own sentence, because earlier drafts of this paper enumerated **six** and omitted
it: it is the mirror of `dead_alpha`, it is live on the deployed path, and it was
swept over `{3.5, 4.0, 5.0}` against `dead_alpha` on development data (ledger
record 202) with **all arms flat**. That flatness is worth more than the
omission cost — it is direct evidence the estimator is insensitive to a dial we
were free to choose, which is the property an auditor is actually looking for.

Two further values are frozen but belong in neither column — the backend block
height `BLOCK_ROWS = 4,096` and the frame ordering — implementation constants
carrying no development selection.

**We have stated this wrongly twice.** An earlier draft claimed "zero fitted
structure anywhere in the estimator." False. The repair was also wrong, reading
values from a base class the deployed subclass overrides. Both were caught within
the hour by adversarial audit, and both are left on the page rather than quietly
replaced, because a paper arguing for an evidence discipline should show that
discipline failing and being caught. The count moved from six to seven for the
same reason.

**What we claim, precisely:** the fitted surface is seven scalars, frozen before
grading, confined to budget and correction coefficients, containing nothing that
could learn the target, and no component was fit to the evaluation suite. Low
measured bias does not prove absence of fitting, and we do not claim it does.

### 2. Why structured spherical designs plateau, and why completing them does not help

Our estimator integrates over 126 phased-Hadamard frames, each an orthonormal
basis `H_256 diag(phi_s)/16`, antipodally doubled to 64,512 points on `S^255`.
It is an exact spherical 2-design, and antipodally therefore a 3-design. The
natural next question is whether pushing to degree-4 exactness would help. It
can be answered exactly, in both directions, and the answer is instructive.

**The design cannot reach degree 4 at its current size.** [D] The
Delsarte–Goethals–Seidel bound for an antipodal spherical 4-design in `S^255` —
which is automatically a 5-design, since odd harmonics cancel pairwise — is
`2*C(257,2) = 65,792` points. We spend 64,512. We are 1,280 points short, so no
reweighting of these nodes under antipodal pair symmetry reaches degree 4.

**Exactly one frame count fixes it.** [D] For `m` mutually unbiased bases
antipodally doubled, every point sees one inner product at `+1`, one at `-1`,
510 at `0`, and `512(m-1)` at `+-1/16`, so `sum_y <x,y>^4 = 2 + (m-1)/128`. A
4-design requires `3N/(d(d+2)) = m/43`. Equating and clearing `128*43` gives
`10965 = 85m`, hence **`m = 129` and no other integer** — 130 clears the counting
floor and still fails. And `129 = d/2 + 1` is the maximum number of real mutually
unbiased bases in `R^d` when `d` is a power of four, which `256 = 4^4` is. Under
the Walsh doubling the complete set has `d^2+2d` points against a floor of
`d^2+d`, clearing by exactly `d` at every level: 24/20, 288/272, 4224/4160,
66048/65792. The completed design is a near-tight antipodal 5-design, over the
floor by 0.39%.

**And we can say in advance what completing it is worth.** [D] For a bias-free
He-initialised ReLU network the rotation-averaged two-point function is exactly
the iterated arc-cosine kernel `K(c) = (E||X||^2/d)·kappa^32(c)`, so the
estimator's variance decomposes as `sum_l ||f_l||^2 A_l` against the design
defects above. That predicts `V126 = 2.4977e-7` against a measured geomean of
`2.6697e-7` over sixteen fresh networks — **the variance of this estimator is
predictable from first principles to 6.4%** — and it puts the degree-4 share of
that variance at **0.4497%**.

**So completion is worth about half a percent, against a 2.33% break-even** set
by the point-count cost. [O] Measurement agrees from two further directions: a
point-count-matched experiment isolating degree-4 exactness at equal 66,048
points returns `0.176%, CI [0.970, 1.028], P(better) = 0.54`, and a committed
degree-4 control variate returns `+0.42%`. Three routes, one predictive, all
landing an order of magnitude below the bar.

That agreement is worth more than any of the three alone, because the analytic
route explains the other two. Most of the variance is simply not where design
strength lives: **86% of it sits at degrees 8 and above**, which no reachable
design touches.

**And degree 6, where the error actually lives, is unreachable.** [D] The
measured angular error sits at degree 4 (11% of the iid level) and degree 6
(40%). An antipodal 6-design needs `2*C(258,3) = 5,658,112` points, 87.7x our
budget; any positive-weight rule needs `dim P_3(S^255) = 2,861,952`, still 44.4x.

The design axis is therefore closed from both sides at once, and not for the
reason one would guess. It is not that the design cannot be completed — it can
be, exactly, and we did. It is that **completing it perfectly buys nothing
measurable**, because the estimator's residual does not live in low-order design
strength. Perfecting a design is not the same as reducing its error, and on these
networks the two come apart.

### 3. What we proved

Each result is stated with its exact scope, and the scopes are narrow on
purpose.

**Uniform weights are globally optimal, non-strictly (companion P4).** [D]
Positive-semidefiniteness plus constant row sums make uniform weighting a global
minimiser of the quadrature error at every spherical-harmonic degree, and for
every nonnegative mixture of degrees, under a zonal Haar-averaged criterion.
Strictness is weaker: on the 32,256-point base set uniform is the *unique*
minimiser only at degrees 4, 6 and 8, where the kernel is verified positive
definite; it is false at degree 2, where the design is exact and every per-frame
reweighting is free; and on the antipodally doubled 64,512-point set the
estimator actually deploys, uniqueness fails at every even degree — the
even-degree kernel has block form `J₂ ⊗ K`, whose kernel contains every
antipodally antisymmetric perturbation. A global minimiser is all the closure
needs; "the constrained minimiser" would be the wrong phrase and we do not use
it. Scope: this closes fixed, output-independent reweighting of a fixed design
against a zonal criterion; it does not close adaptive weights, changed point
sets, or non-zonal criteria.

**The Crofton kink-transect identity is true, and the estimator it induces is
dead (companion P2).** [O] The Gaussian mean of a bias-free ReLU network equals
the Gaussian-weighted surface integral of its gradient jumps over the kink set —
verified at machine precision (structural checks to 6.7e-16, two independent
transect implementations, 3 predeclared + 20 fresh nets). The unbiased estimator
it induces was killed at **176,860x worse variance-per-FLOP than Monte Carlo**
on the width-64 depth-8 screen, against a predeclared kill line of 100x. The
theorem stands; it is a mathematical result, not an estimator.

**A family of truth-free estimators is dead by one identity (companion P6).**
[D] If an estimator anchors on its own uniform frame mean, the sum-one GLS
solution is uniform *identically* — for every ridge and every shrinkage, with no
probabilistic model. Four self-anchored GLS descendants that failed in four
apparently different ways are one failure, and the identity predicts it without
an experiment.

**The compute lane is closed: pruning is the only legal rank reduction.** [D/O]
ReLU commutes only with nonnegative monomial matrices, so the only factorization
that passes through the nonlinearity is a per-neuron scaling and permutation —
structural pruning. The measurements agree with the algebra: mid-layer exact
on-composition returned 0.00% billed reduction (M184: certain-on structure
absent where the network is wide, 2.3x under break-even at depth); the float32
recast found no material f64 lane (M183: 0.0755% of billed predict FLOPs, full
recast capped at 59,656,312 FLOPs); the Gen-7 cost-remap attack found the bill
~99% irreducible float32 matmul already at the floor rate. Within the one legal
lane, pruning saves 25.109% of B, MSE-neutral (1.014 [0.98, 1.05]) and strictly
optimal under the adjusted-score arithmetic, and the terminal fold saves 4.828%
of B at an MSE ratio of 1.000033.

**The variance is predictable from first principles to 6.4%.** [D/O] The
iterated arc-cosine kernel decomposition of §2 predicts `V126 = 2.4977e-7`
against a measured geomean of 2.6697e-7 over sixteen fresh networks, puts the
degree-4 share of variance at 0.42–0.45% (analytic 0.4497%; committed degree-4
control variate +0.42%), and puts 86% of the variance at degrees 8 and above,
where no reachable design has strength. This is what closes the design axis.

**What we do not claim:** the residual's harmonic spectrum, any maximum-entropy
property, any truncation-class closure, and any minimax floor are all **open**
(§6, E4/E5).

### 4. Negative results, and the method that produced them

**The method.** Every kill was predeclared with its gate before implementation;
none was retuned after seeing results; kills are final and stay in the record.
The 267-record fold ledger retains negative results in full rather than pruning
them, which is what makes it checkable rather than asserted. The same standard
applies to dead entries: a record-level sweep found three historical "kills"
that had never actually been run — dispositions carried by wording, not
evidence — so we ran 16 falsifiers on the strongest candidates and adjudicated
all 16: ten converted from assumption to confirmed measured kills, four revived
as screened Phase-2 proposals, one blocked, one held inconclusive.

**Twelve predeclared kills.** [O]

| mutation | measured | verdict |
|---|---:|---|
| N4 cheap variance levers | null | killed |
| N5 multilevel closure control variate | 1.07x | killed |
| N6 exact great-circle Rao-Blackwellization | FoM 0.006x | killed |
| N7 RQMC superconvergence at depth 32 | slopes −0.97/−1.23 vs −1.25 gate | killed |
| N8a Kronecker lattice vs our frames | lattice 2.1x worse, CI [1.65, 2.65] | killed |
| N8b disclosed native backend | 0.94e11 FLOP/s < λ = 1e11 | killed |
| N8c offline-trained corrector | bias share −0.0336 vs 0.25 gate (see E6) | killed |
| N9 frames + tangent + deeper fold | +2.1% (positive control +34.5% on iid) | killed |
| M180 stronger spherical designs | all arms +20–49% variance | killed |
| M181 terminal rectified-Gaussian smoothing | bias 4–6x baseline MSE, variance identical | killed |
| M183 float32 hot-path recast | f64 lane 0.0755% of billed predict (E1) | killed |
| M184 mid-layer exact on-composition | 0.00% billed reduction | killed |

M180's kill doubles as a structural result: every perturbation of the frame
family or its shared rotation destroys degree-2 exactness and loses 20–49%
variance — the design is locally optimal.

**The Gaussian-closure wall behind N5/M181.** [O] The strongest closure we could
certify — exact full-covariance, pairwise-exact via Owen-T/Φ₂ with per-call
enclosure certificates — lands at 9.61e-5 bias MSE against ~2.5e-7 for sampling
at the same budget. The like-for-like gap is **340.9x raw against the graded raw
2.818e-7** (52.4x adjusted-on-adjusted at the most favourable multiplier; the
formerly printed 524x mixed units and is withdrawn, E7). Exact Gaussian
structure pays when *subtracted* (the moment-tangent control) and fails when
*predicted*. This kills the implementation as an estimator; it does not prove no
Gaussian-informed method can work.

**The completion kill (MUB129).** [D/O] The most attractive open door —
completing the 126-frame design to the full 129 real mutually unbiased bases,
the maximum in `R^256` by prior art, yielding an exact near-tight antipodal
5-design — is killed by arithmetic: the analytic decomposition puts the entire
degree-4 effect at 0.4497% of variance against a 2.33% point-count break-even,
and the point-count-matched measurement (0.176%, CI [0.970, 1.028]) has no power
to resolve an effect that small — its band is several times wider than the
effect. Three routes, one verdict, an order of magnitude below the bar (§2).

**The seed-side rotation null (ledger 242).** [O] The one candidate our own
theory could not exclude in advance: replace the grader-seed Haar rotation with
the deterministic V from the first layer's SVD, coupling the randomization to
the weights we already possess. Measured on the committed public 0–99 net basis
under common random numbers, twice-run bit-identical: paired t = +0.19 against a
t ≥ 3 kill gate, better on exactly 50 of 100 nets, bootstrap CI on the mean
delta [−3.19e-8, +2.61e-8] symmetric about zero, and a drop-top-5 recomputation
that flips the sign — a clean null, bought with +3.6e8 billed FLOPs. The
mechanism: V is marginally Haar, so coupling to the singular basis buys no
alignment with the fixed cubature frame. One null does not close the seed-side
lane, and we say so (§6, E10).

**Adversarial closure.** [O] Twenty adversarial agents mandated to *beat* the
champion attacked through six lenses; five returned no candidate, each leaving a
named obstruction; seven previously killed families were re-litigated under
changed premises and 7/7 held. The one un-probed crack they named — non-smooth
cell-membership covariates — was sealed the same day (S18): all 64,512 design
directions occupy 64,512 *distinct* first-layer activation cells, so cell
identity is a per-point unique label that can memorize a training residual and
can never activate on the held-out half; every gated feature set landed below
the predeclared fitting-noise cost of 2.63e-5.

### 5. LLM involvement

This campaign was conducted end-to-end by large language models operating as
agents under human direction: the estimator, the experiments, the ledger, this
document and the six companion papers were all written by LLMs — nothing here is
human-authored code with LLM assistance; it is the other way round. Because a
fluent model produces plausible text whether or not the claim is true, every
load-bearing claim carries an evidence tag ([O]/[D]/[R]/[A], with [GAP] for
known holes), and the corpus was audited by two LLM agents from different model
families under a sealed evidence charter, plus a twelve-agent refinement pass
instructed to refute rather than confirm. That machinery found, in our own
flagship claims, a false uniqueness theorem, an unproved exhaustiveness step, a
powerless control presented as a control, and an inadmissible measurement
supporting a headline — while public scrutiny of this work found no defect;
every defect was found by our own machinery pointed at ourselves.

### 6. Errata and integrity

This document supersedes the v9 filed 2026-08-10 and incorporates all thirteen
errata recorded against it; full statements with their arithmetic are in draft
v12 §0 and at each marked site. The errata that changed a headline claim:

- **E2** — the 1.65 suite-calibration factor we advised the field to apply was a
  mean artifact; the median-recomputed panel matches the grader to 0.05%, and
  the corrected advice is to calibrate on the median.
- **E4** — the central synthesis (residual as maximum-entropy chi²₁ speckle at
  the degree-4 boundary) was stated as a theorem, is not one, and is now
  **open**; its supporting spectral computation is quarantined as inadmissible,
  and withdrawing it does not revive the older equipartition account, which was
  never established either.
- **E5** — the S17 floor ratios were computed at n = 3 and are retired; at
  n = 80 the distinct-direction ratio is 1.0044, CI [0.8450, 1.1639], so
  champion and floor are indistinguishable at the resolution we have and no
  below-floor claim survives.
- **E6** — N8c's printed confidence interval does not contain its own point
  estimate and is not a usable net-level interval; the bias result stands only
  as a 3-net, 16-rotation screen observation (−0.0336 against a 0.25 gate), not
  a zero-bias theorem.
- **E7** — the 524x closure-gap figure mixed raw against adjusted units and is
  withdrawn; the admissible ratios are 340.9x raw-on-raw and 52.4x
  adjusted-on-adjusted.
- **E8** — the "exact radial conditioning 2.14x" pillar was a bundled
  attribution and is withdrawn; the isolated factors are frame design 2.016x and
  residual radial improvement 1.062x, and "three proven-locally-optimal
  multiplicative pillars" is withdrawn with it.
- **E10** — "decorrelated at every design pair," "the ledger certifies PRNG
  strength," and "the rotation lane is closed" are each withdrawn as stated
  above their evidence: the measured correlations are shell aggregates, a finite
  battery of failed attacks certifies nothing, and one null does not close a
  lane.

The remaining errata (E1, E3, E9, E11–E13) correct published numbers,
provenance labels, and citations without changing any verdict. One matters for
this document's own citation: **E12** — the filed citation pointed at the
repository's stale default branch; the correct path is the pinned-commit
campaign-branch path given in §0.

Word count: 3451
