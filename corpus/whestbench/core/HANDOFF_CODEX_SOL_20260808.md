# HANDOFF TO CODEX SOL — the entire campaign, nothing withheld (2026-08-08)

Addressee: Codex Sol, successor operator on gmrmk/recursive-estimator-folding.
Author: Fable 5, closing operator of the 2026-08-08 WHestBench live campaign.
Instruction from the owner, verbatim intent: "give Codex Sol the entire thing,
don't hold back — include a granular and extremely detailed list of everything
we have worked on, include everything, do not forget anything."

This document is that delivery. The goals themselves live in
GOAL_STATEMENT_20260808.md (read it first). Appendix A at the bottom is the
mechanically dumped 207-record ledger snapshot. The live
`headroom/fold_ledger.json` now has 213 records after M192--M197 and is the
authoritative continuation; Appendix A is historical, not complete. Nothing
in this campaign exists outside the live ledger.

---

## Part I — Where we stand (the load-bearing facts)

- **Contest**: ARC White-Box Estimation Challenge 2026 (WHestBench). Task:
  predict per-neuron final-layer post-ReLU means of width-256, depth-32,
  He-init, bias-free ReLU MLPs under standard-normal input. Score law:
  S = MSE x max(0.1, C/B), B = 2.72e11 FLOPs, C = billed flopscope FLOPs
  + 1e11 x residual_seconds. Floor 0.1 confirmed from leaderboard arithmetic.
  Adjusted score is scale-invariant along the sampling curve, so the ONLY
  lever is variance-per-billed-FLOP.
- **Last recorded grading snapshot**: submission #326094 (Kerdock v3) graded adjusted
  1.832e-7, final-layer MSE 2.818e-7, 50/50 public MLPs, zero failures,
  team rank #192 -> **#58**. This is historical evidence, not a confirmed
  current rank. Second real graded artifact on the account:
  #318609 (July T5C1 lineage).
- **The board is a fiction above ~4.6e-8**: the top tier (5e-10 .. 4.4e-9)
  bills 6e8-7e9 FLOP/s while running 22-47 s/MLP — unmetered-compute
  accounting arbitrage, patched 2026-08-03, under organizer review, already
  slipping in silent re-grades (observed Aug 8 evening). Honest frontier
  markers: ednacob 4.62e-8, organizer mohanty 9.31e-8. Prizes are decided
  EXCLUSIVELY by the Sep 20-30 private fresh-seed re-run (Rules v12 §5.4).
- **The successor artifact**: Kerdock v3.1 GUARDS — validated 2026-08-08,
  bitwise-identical to v3 on every healthy network (+24,575 FLOPs for an
  isfinite scan), plus M186 (empty-regime crash guard) and M187 (NaN/Inf
  analytic-mean degradation). Tar sha256
  8382e269c9b32e0935492734ddf8182560120f7e9331621aa18839d5d1f4ea06
  (33,347,024 bytes), repository artifact at
  `experiments/v31_guards/submission_kerdock_v31_guards_20260808.tar.gz`;
  refresh any Desktop staging copy before an authorized canary. It remains an
  ungraded Phase-2 candidate pending its own explicitly authorized canary.

### Generation-5 delta (added after the original handoff snapshot)

- M192 truth-oracle cross-output frame GLS: panel ratio 0.126193, but cached
  truth noise is 39--44% of its observed residual and no deployment claim is
  lawful without independent truth streams and fresh networks.
- Exact no-go: one frame matrix identifies `P C P` but not `P C u`; changing
  the unknown target can arbitrarily change the missing cross block while
  leaving the observed frame matrix fixed.
- M193 analytic anchor, M194 independent pilot, M195 two-way split, and M197
  three-way crossed split are killed at correlated-anchor, pilot-SNR/cost, and
  split-Kerdock-geometry links respectively. Do not retune them.
- M196 freezes M151's exact B=1 `[2,1,1]` variance gate and blocks correctly:
  native 49-node provider, non-cubic compiler, coefficient batch binding, and
  inclusive trace are absent. No synthetic substitute is authorized.
- `core/GEN5_MUTANT_RECURSION_20260808.md` is the current attack plan.

## Part II — The champion, fully characterized

Kerdock v3 (a.k.a. M71 lineage), five components, every one measured:

1. **Phased-Hadamard spherical design**: 126 Kerdock-code frames x 256
   directions = 32,256 base directions, antipodally doubled to 64,512, all at
   the exact chi-mean radius, one shared Haar rotation per network as the
   sole randomization. Measured 2.02x variance pillar [CI 1.45, 2.83].
2. **Exact radial conditioning** (positive one-homogeneity integrates the
   radius exactly): 2.14x pillar [1.51, 3.04].
3. **Antipodal pairing**: 1.91x pillar [1.41, 2.56].
4. **Pilot-rescued structural pruning** (dead_alpha = -2.0, 256-pair pilot
   rescue): MSE-neutral (1.014), saves 25.1% of billed budget —
   adjusted-optimal (removing it is 1.33x WORSE adjusted).
5. **Three-terminal-layer folding** (dead/on/kink, on_alpha = 3.0): exactly
   MSE-neutral (1.00003), saves 4.8% of billed budget. Plus the frozen
   first-layer moment-tangent control, lambda = 0.9807112198896164, measured
   neutral by three independent tests.

Four theorems-with-numbers about it:

- **Exact spherical 2-design**: odd harmonics annihilated exactly, degree-2
  quadrature error 8.6e-9. This is WHY every design perturbation loses
  20-49% (M180): mutual unbiasedness of all 126 frames under one shared
  rotation is the mechanism, and it is fragile in every direction.
- **Dispersion no-go**: the residual angular error lives at degree 4 (11% of
  iid) and degree 6 (40%), but its energy disperses across ~1.8e8-dimensional
  harmonic spaces at d=256 — a 24-function weight-derived basis explains
  0.2-0.3% of per-neuron variance; the harmonic CV nets +0.83% (M191).
  Unscoopable by finite projection.
- **The tail theorem**: the hosted 11x per-network score spread is
  rotation-draw sampling variance (worst/median 3.79x -> 1.12x at R=6), NOT
  network difficulty (per-net MC difficulty varies 1.1x) and NOT a defect.
  No a-priori flag exists (A1b killed).
- **Zero bias**: final-layer error is statistically pure variance (N8c bias
  share -0.034, CI [-0.031, 0.097]) — nothing fitted, nothing to overfit on
  fresh private seeds. The strongest re-run robustness property available.

And one closed frontier: **rotation selection**. Oracle-of-8 rotations would
cut MSE 61.6% (Gen3-P2) — but the pilot proxy correlates -0.089, a pilot
costs 33% of budget, and every weights-only proxy fails (P2b best |rho|
0.166). The headroom is real and information-gated. Recorded so you do not
re-spend a week rediscovering it.

## Part III — Granular inventory of everything worked on

### A. The eras of the corpus (ledger records 0-179, pre-live-campaign)

1. **Headroom h-series** (h1-h4): the founding recursion. h4_random32256
   PROMOTED — the 32,256-direction parent all later champions descend from.
   h1 equivariant residual, h2 weighted control, h3 rank-5 k4: killed.
2. **Closure/cumulant odyssey** (records 3-51): kerdock_design (first
   attempt, killed then later resurrected correctly), fullcov_gaussian,
   cavity/Dyson/TAP resummation, k3 finite-horizon transport, adjoint
   cumulant contraction, latent-factor closures (rank-2/3, sparse-radial,
   randomized-radial family — several screened), gate-aligned splits,
   Rao-Blackwellized marginals, repeated-cumulant retention, conditional
   correlation spectra, response Grams, susceptibility compressors, total
   cumulance, Physarum MoE router, flatworm ladder attenuators, ECN
   compressors, JSpace VJP controls, distilled multifidelity students,
   copula resummations — killed with mechanisms named.
3. **Winograd/Strassen exact-compression lineage** (records 42-61): from
   rectangular Strassen through preallocated and batched variants to
   row_blocked_winograd_production PROMOTED (the fixed-8192-row L1
   champion), then the two-axis fused L2 (screened, later T1-verified as
   adjusted 2.101976e-7 vs champion 2.121762e-7, 88/100 paired wins).
4. **Kerdock resurrection** (records 70-75): kerdock126 formal transplant
   (killed), structured WHT memory folds (killed), then
   m71_kerdock126_one_buffer_owned_l1 SCREENED SURVIVOR — the champion's
   true birth record — and m76 validator fallback (package_validated).
5. **The long M-series** (records 77-179, M73-M179): the deepest sustained
   research arc — signed HOSVD-CP sources, TT recurrences, Huber MLMC,
   James-Stein shrinkage, tangent factorial (lambda frozen here, M80),
   Kerdock-vs-Haar variance attribution (M82), boundary Laplace/coarea
   identities (M86), great-circle Rao-Blackwellization (M88/M89),
   bridge factors, cycle sketches, equivariant learned closures
   (M92-M106: an entire transformer-closure program, killed at protocol
   after protocol), spherical Gegenbauer exact-zero controls (M107),
   heat-band/cymatic/nodal-occupancy harmonics (M108-M110), gate
   interferometers and connected kernels (M111-M113), collision-resummed
   Hermite sources (M117-M120), the bridge-source/Frechet-tangent program
   (M121-M136: source algebra preserved, carriers repaired, [2,1,1]
   collision triples, factored hidden-edge samplers, ACG proposals,
   endpoint-safe pair bridges), terminal-law resummation no-go (M137),
   rank-face anchors and owner unifications (M154-M173), staging/ABI
   audits (M174-M176), and the certified capstones: **M178** (certified
   Phi2/Owen-T provider — per-call enclosure certificates, 4,048-FLOP
   bounded cost, 12,890-case adversarial census, all contained) and
   **M179** (exact metered labelled zero-order full-covariance background
   archive producer, 8.30e9 FLOPs = 3.05% of budget, agrees with 30-digit
   mpmath to 2.144e-9).
6. **The T-series reconciliation** (records 180-186): T1 L2 promotion
   verification (screened), T2 closure-as-standalone-estimator (KILLED —
   the certified exact full-covariance Gaussian closure scores 9.61e-5
   raw at depth 32 vs sampling's ~2.5e-7: the ~380x gap is
   third-and-higher-cumulant structure NO Gaussian closure can represent
   at any compute multiplier; this is the non-Gaussianity-wall measurement
   in the prize writeup), D-PM victory postmortem (red-teamed), D-AC prize
   report extension, T3 fold3 deterministic cap (screened, QUARANTINED —
   its cap sim calls budget_summary_dict() which may inflate residual;
   graded canary required before designation), T4 Kerdock descriptive
   rescore, T5 submission dossier + runbook.

### B. The live campaign (2026-08-08, records 187-206 — every arm)

- **N4** cheap variance levers: null. KILLED.
- **N5** multilevel closure control variate: 1.07x. KILLED.
- **N6** exact great-circle Rao-Blackwellization: FoM 0.006x. KILLED.
- **N7** RQMC superconvergence probe: slopes -0.97/-1.23 vs -1.25 gate.
  KILLED.
- **N8a** Kronecker lattice vs our frames: lattice 2.1x WORSE
  (CI [1.65, 2.65]) — the design dominates a randomized lattice once the
  radius is conditioned away. KILLED (a result in its own right).
- **N8b** disclosed native backend: 0.94e11 FLOP/s < 1e11 lambda. KILLED.
- **N8c** offline-trained corrector: bias share -0.034 — nothing to
  correct. KILLED (the zero-bias theorem).
- **N9** frames + tangent + deeper fold composition: +2.1% (positive
  control +34.5%). KILLED.
- **C1** local-vs-hosted calibration: local MC 1.069e-6 vs grader 6.47e-7,
  ratio 1.65 — AND the hard lesson that MC suite-ratios do NOT transfer to
  structured estimators (Kerdock predicted ~9.8e-8, graded 1.83e-7).
  SCREENED; every projection downstream corrected.
- **M180** design-strength arms (MUB mix / coset stratification / remix):
  all +20-49% variance. KILLED -> local-optimality result.
- **M181** terminal rectified-Gaussian smoothing (3 arms incl. unbiased
  CV): bias 4-6x baseline MSE, lambda -> 0; bias field reproduces on fresh
  iid samples (cosine 0.97-0.98) — the terminal law itself is
  non-Gaussian. KILLED; closure family closed at EVERY insertion point.
- **M183** float32 hot-path recast ("the free 2x"): 0.00% f64-lane billing
  — already clean. KILLED.
- **M184** mid-layer exact on-composition + sparsity: 0.00% billed
  reduction (certain-on absent where wide, 2.3x under break-even at
  depth). KILLED.
- **M185** tail-pruning mechanism (Gen3-P1): the 15.5x tail reproduced on
  80 nets, does NOT correlate with pruning misclassification. KILLED ->
  the tail theorem.
- **A1b** a-priori tail flag mining: no flag exists in the M185
  checkpoint. KILLED.
- **A3** kill-heterogeneity re-audit (skeptic pass on our own 12 kills):
  4 pre-registered suspicions adjudicated, all verdicts STAND. SCREENED.
- **A4** hostile-inputs battery on frozen v3 at the real budget: scale
  extremes, heavy tails, rank deficiency — found the two real failure
  classes (empty-regime crash, NaN propagation) that became v3.1's
  guards. SCREENED.
- **PB-1** Premise Battery + dial battery (M188/M189 crosses,
  fold on_alpha x prune dead_alpha, 5 arms): all flat — both dials at
  their measured optima. KILLED. The Battery itself (cached-truth
  amortization) measured a 3.2x G0 acceleration and STANDS as process
  capital.
- **WC-1** winner-catalog ablation map: the marginal-value numbers in
  Part II. SCREENED.
- **M191** G0a harmonic spectrum (the Padgett trigonometric bolt,
  steelmanned): produced the exact-2-design theorem. SCREENED. G0b
  harmonic CV: +0.83% vs 10% bar. KILLED -> the dispersion no-go.
- **Gen3-P2** rotation selection: oracle-of-8 = 61.6% headroom; pilot
  proxy -0.089, pilot cost 33%B. KILLED.
- **P2b** weights-only rotation proxies (3 candidates, zero forward
  cost): best |rho| 0.166 vs 0.4 gate. KILLED — rotation family fully
  closed, headroom information-gated.
- **v3.1 GUARDS** (M186+M187): G1 bitwise-equal, G2 both A4 failures
  survived (164 NaNs replaced with analytic means, zero clamps), G3
  package validated 10/10 members. **VALIDATED** — the campaign's first
  validated successor.

### C. Submissions and the submission machinery

- #326094 Kerdock v3, adjusted 1.832e-7, the live designate-apparent's
  predecessor. #318609, July T5C1 lineage, second graded artifact.
- Submission pattern (user-authorized ONLY): load AICROWD_API_KEY blindly
  from C:\Users\strid\projects\whest-starterkit\.env into process env —
  the value is NEVER read, displayed, or logged — then
  `whest.exe submit <tar> --challenge arc-white-box-estimation-challenge-2026`
  from the pinned v014 env with PYTHONIOENCODING=utf-8. Four permission-
  classifier denials were honored before the user authorized this pattern.
- Staged queue at Desktop\whest-submit\: the current guarded artifact is
  `0_kerdock_v31_GUARDS_HARDENED_8382e269.tar.gz` (sha256 8382e269…ea06).
  The older `0_kerdock_v31_GUARDS_BEST.tar.gz` is stale, and the existing
  `SUBMIT_kerdock.cmd` still targets v3; neither should be mistaken for an
  authorized v3.1 canary. Other historical files are
  1_kerdock_v3_BEST, 2_L1_champion, 3_L2_twoaxis (sha256 68259f64…),
  4_fold3cap (QUARANTINED — graded canary first), 5_tangent_prizevehicle.

### D. Core documents (all in corpus/whestbench/core/)

GOAL_STATEMENT_20260808 (the goals), LIVE_RULES_RESET (rules v12 read
first-hand), RULES_V12_ANALYSIS, PROMOTION_DECISION_L2, VICTORY_POSTMORTEM
(red-teamed reverse oracle), HOSTED_INTEL (leaderboard decode + grader
telemetry ~6e8 FLOP/s at 40s wall), SUBMISSION_RESULT, SUBMIT_READINESS,
RESEARCH_INTEL, UNCERTAINTY_LADDER (19 uncertainties: 9 resolved to
observed, 4 honestly BLOCKED with named owners), GEN3_RECURSION_PACKET,
GEN4_CLOSING (the Generation-4 constraint set — the do-not-respin list),
PHASE1_WRITEUP_DRAFT (v3, files by Aug 17 with ID #326094 — carries the
2-design theorem, dispersion no-go, marginal-value map, tail theorem, the
kill ledger, and the calibration method), SUBMISSION_DOSSIER (+ addenda).

### E. Process capital (use these, they are paid for)

1. **The fold discipline** (skill: recursive-estimator-folding): mechanism
   + kill gate predeclared BEFORE code, cheapest falsifier first, kills
   final, one causal mutation, ledger append, commit. 207 records deep.
2. **The Premise Battery** (experiments/pb1_premise_battery/
   premise_battery.py): cached-truth amortization, 3.2x measured G0
   acceleration. Reusable for any dial/cross battery.
3. **The compute-runner agent type** (~/.claude/agents/compute-runner.md):
   NO Monitor/task tools, so a delegated run can never arm a watcher and
   go dormant (the stopped-watcher trap fired 4x on 2026-08-08 before
   this mechanical fix; three flawless missions since).
4. **The calibration lesson**: run one budget-matched MC reference on both
   suites before trusting any cross-suite number; structured estimators
   grade near their LOCAL value, not the MC-ratio-scaled one.
5. **The 61.6%/information-gated pattern**: when an oracle shows headroom,
   cost the information channel before celebrating.

## Part IV — Your standing duties (dates are hard)

1. Aug 10 23:59 UTC — Phase 1 closes; auto-top-2 (#326094 + #318609)
   stands. At Phase-2 open: resubmit v3.1 GUARDS (user-gated: blind .env
   pattern or the owner double-clicks SUBMIT_kerdock.cmd).
2. Aug 17 23:59 UTC — the Phase-1 Algorithmic Contribution writeup files
   on the discourse guidelines thread with ID #326094 (owner posts; the
   draft is final at v3). Highest-probability payout on the board.
3. Sep 19 — designation locks. v3.1 pending its graded canary; verify the
   designation slot count on the live page before recommending.
4. Sep 20-30 — private fresh-seed re-run decides everything. A zero-bias,
   fully-instrumented, hostile-tested champion is exactly the artifact you
   want standing when the accounting tide goes out.
5. Always — the firewall: no sealed cells, no truth/scorer reads, no
   credentials read or displayed, no accounting bypass EVER, public
   endpoints read-only. Kills are final. Measured sizes only. New
   mutations require new external facts or genuinely new mathematics
   against the frontier stated in GEN4_CLOSING.

---

## Appendix A — the complete fold ledger, all 207 records (mechanical dump)

Format: `index | id | status | mechanism (first 110 chars)`. Full text of
every record lives in corpus/whestbench/headroom/fold_ledger.json.

```
  0 | h4_random32256 | promoted | Reduce the recursive-frame parent to 32,256 base directions so activation-dependent tail cost stays below the 
  1 | h1_equivariant_residual | killed | Predict deterministic full-covariance closure residual from 70 symmetry-quotiented Hermite, gauge-edge, cancel
  2 | h3_rank5_k4 | killed | Compress the connected fourth-cumulant vertex to pair rank 5 and transport it through depth.
  3 | kerdock_design | killed | Use a maximal real MUB/Kerdock spherical design to annihilate low-degree harmonics.
  4 | fullcov_gaussian | killed | Propagate exact full covariance and reclose every ReLU layer as Gaussian.
  5 | cavity_dyson_tap | killed | Resum finite-width corrections through cavity, Dyson, TAP, or Onsager feedback.
  6 | h2_weighted_control | killed | Predict a network-specific analytic/sampler blend coefficient from weights.
  7 | k3_finite_horizon | killed | Transport a factorized third cumulant with a fixed recent-layer horizon H, preserving coordinatewise sign whil
  8 | goal_oriented_adjoint_cumulant | killed | Contract layerwise connected cumulant defects with downstream observable adjoints instead of materializing ful
  9 | weight_identified_latent_factor | killed | Condition each Gaussian closure layer on one or two weight-identified leading covariance factors, rectify diag
 10 | latent_factor_rank3 | killed | Increase only the screened latent factor rank from r=2 to r=3 while freezing q=3, tensor quadrature, recompres
 11 | latent_sparse_radial_cubature | proposed | Replace q^r tensor Gauss-Hermite nodes with signed spherical-radial nodes over an adaptive leading subspace ca
 12 | latent_sparse_radial_harness | killed | Evaluate the frozen sparse-radial candidate and streaming truth in one process through the existing generic re
 13 | latent_randomized_radial | screened | Factorially replace the full-sigma rule's fixed covariance axes with seeded Haar frames and its single sqrt(n)
 14 | latent_randomized_radial_n128 | screened | Run the frozen combined Haar plus two-node chi radial q3 closure on four fresh n128,L32 synthetic networks wit
 15 | latent_randomized_radial_flopscope | screened | Port the frozen Haar-plus-chi2 q3 closure to FlopScope with setup-hoisted buffers/transforms, deterministic pe
 16 | latent_randomized_radial_development100 | killed | Run the hash-frozen FP32 randomized-radial closure exactly once on the lowest untouched permitted development 
 17 | latent_full_sigma | killed | Replace selected-factor tensor quadrature with a full-covariance 2n-point spherical-radial rule built from the
 18 | latent_gate_aligned_split | killed | Split each Gaussian component into three exact truncated-normal bins along the covariance-whitened ReLU bounda
 19 | latent_gate_label_memory | killed | Preserve low/central/high gate-split labels across parent components and recompress by label rather than a gen
 20 | latent_gate_rb_marginals | killed | Rao-Blackwellize exact within-bin ReLU marginal first and second moments over the scalar truncation, retaining
 21 | pair_repeated_cumulants | killed | Retain only third- and fourth-cumulant entries having at most two distinct neuron indices: k3(iii), k3(iij), k
 22 | conditional_corr_spectrum | screened | Compute exact scalar-conditioned bivariate ReLU covariances and test whether the non-Gaussian covariance corre
 23 | conditional_response_gram | screened | Construct the frozen conditional-covariance rank-four modes from coordinatewise univariate ReLU response vecto
 24 | latent_gate_response_gram | killed | Insert the frozen degree-four signed response-Gram covariance correction and exact diagonal Rao-Blackwellizati
 25 | multidirection_gate_response | killed | Use a fixed additive bank of orthogonal directions from the invariant boundary-susceptibility Gram diag(g) C d
 26 | randomized_radial_susceptibility_compressor | killed | Use the preserved invariant gate-susceptibility direction to compress the genuinely non-Gaussian Haar-plus-chi
 27 | randomized_radial_dual_observable_compressor | killed | Use the top direction of a parameter-free normalized sum of gate-boundary and active-linear covariance Grams t
 28 | conditional_total_cumulance | killed | Use the law of total cumulance under a scalar-conditioned low-rank state to retain all-distinct k3/k4 cancella
 29 | conditional_residual_cumulant_spectrum | screened | Represent exact within-cell residual k3 by a signed mode-1 unfolding and k4 by a signed pair-unfolding, retain
 30 | conditional_residual_covariance_algebra | screened | Constrain residual k3 quadratic and k4 pair factors to the fixed small matrix algebra generated by already-ava
 31 | physarum_moe_router | killed | Route complete moment-safe cubature/closure experts using a parameter-free Physarum conductance flow initializ
 32 | flatworm_ladder_attenuator | killed | Apply a frozen two-lane longitudinal/commissural recurrence with dyadic leaky evidence, pairwise nonexpansive 
 33 | flatworm_response_ladder | proposed | Use the flatworm-inspired longitudinal/commissural recurrence only as a two-lane depth controller for gate-bou
 34 | ecn_jacobian_maxent_compressor | killed | Apply the ECN-style extract-transform-remap pattern: extract invariant response features, transform with a max
 35 | ecn_exact_jspace_psi_streaming | proposed | Replace only the ECN compressor's surrogate psi with the exact ReLU observable Jacobian in theta=(alpha,log si
 36 | weight_distilled_multifidelity | killed | Distill each disclosed deep teacher into a small analytically integrable control student from a frozen pilot, 
 37 | jspace_workspace_distillation | screened | Adapt JSpace's Hutchinson VJP identity at the terminal input-to-output map, compare the signed average E[D_0] 
 38 | jspace_gram_aligned_control | killed | Use an independent K=4 fused-VJP pilot to obtain top directions of E[J^T J], construct predeclared exact-mean 
 39 | jspace_inverse_complement_control | killed | Invert only the failed JSpace subspace choice by testing bottom-G0 and top-G0-orthogonal-complement directions
 40 | randomized_radial_inverse_residual | killed | Invert the failed direct analytic replacement only through a genuinely coupled residual observable; reject the
 41 | compressed_residual_cumulant_transport | killed | Compress only the signed design-relevant k3/k4 correction into the screened <=12-dimensional covariance-genera
 42 | exact_sampler_rectangular_strassen | killed | Compress only the promoted random32,256 sampler's exact matrix products using a shape-dispatched whole-row rec
 43 | amplitude_coded_cumulant_probes | killed | Replace only constant-modulus coefficient probes by P=128 normalized-Gaussian sphere lines, retaining the fixe
 44 | cumulant_polynomial_quotient | screened | Replace the redundant literal cubic and quartic covariance-algebra core coordinates by deterministic response-
 45 | price_hermite_q2_response | killed | Infer rectified-Gaussian Hermite coefficients through degree two from conditional mean and diagonal-plus-rank-
 46 | preallocated_strassen_winograd | killed | Repair the exact whole-row Winograd allocation graph with legal setup-preallocated out= buffers, then separate
 47 | price_hermite_q4_response | killed | Hold the Q2 marginal/factor/total-cumulance state fixed, add exact ReLU Hermite coefficients through order fou
 48 | integrated_batched_winograd | killed | Wire the preserved single-batched seven-product Winograd operator into the immutable random32,256 fold3 hooks 
 49 | latent_copula_resummation | killed | Condition the clipped rank-four rectified-Gaussian copula on its common factor, compute exact independent coor
 50 | row_blocked_winograd | screened | Replace only full-height seven-product liveness by fixed8192-row streaming while packing the right operands on
 51 | canonical_latent_copula | killed | Canonicalize the rank-four Gaussian factor through the eigenspaces and projectors of B^T B before applying the
 52 | ple_flash_sidecar | screened | Translate the static per-layer-embedding storage pattern into a clean-room analytic response sidecar: factor a
 53 | row_blocked_winograd_production | promoted | Port the exact fixed8192-row Winograd survivor into an immutable descendant of random32,256 fold3, validate th
 54 | quadratic_chaos_fourier_resummation | killed | Replace the finite four-cumulant terminal Q2 Edgeworth map by the exact characteristic-function positive-part 
 55 | tensor_train_gaussian_cross | killed | Approximate the full vector-valued network on a three-node standard-normal tensor-product grid with TT cross, 
 56 | signed_gate_innovation | killed | Propagate weights-only signed marginal k3/k4 through exact gate-boundary Gram-Charlier raw moments, invert eac
 57 | diagonal_vertex_innovation | killed | Keep the signed q2 correlated sector and add exact residual marginal vertices eta3/eta4 transported as eta_p d
 58 | two_axis_fused_winograd | screened | Compose the champion's fixed8192-row L1 fallback with a fixed6144-row fully fused two-level Winograd operator 
 59 | two_axis_fused_winograd_production | screened | Port the frozen6144-row fused L2 operator into the promoted8192-row L1 package, validate the exact seven-file 
 60 | coherent_root_vertex_innovation | killed | Replace the failed diagonal eta transport by canonical rank-one cubic and signed rank-two quartic root tensors
 61 | direction_only_facet_raoblackwell | killed | Use the exact distributional-Laplacian facet identity for a fixed homogeneous CPWL network; sample a gate and 
 62 | crossfitted_inpath_quotient_sensor | killed | Read a predeclared subset of already-paid hidden paths at selected late layers, estimate actual directional cu
 63 | bounded_characteristic_function_mixture | killed | Replace unbounded sampled k3/k4 quotient responses by bounded empirical characteristic-function values, then f
 64 | output_projected_all_order_2pi_resolvent | killed | Represent the fixed-network output law by a 2PI effective action and solve a rank-at-most12 output-projected B
 65 | cross_output_centroid_body_tomography | killed | Use the256 independent final rows as simultaneous query directions for the common one-sided-zonoid support fun
 66 | compact_group_laplacian_control | killed | Apply a Haar-rotation Poisson/Laplace--Beltrami control to the MUB cubature error, using either the native ReL
 67 | terminal_exact_moment_anchor | killed | Use the exact identity E[Z+]=(E[Z]+E|Z|)/2 and exact-zero-mean terminal controls Z-EZ and Z^2-EZ^2, acquiring 
 68 | strict_band_boundary_ridgelet_control | killed | Use exact-zero-mean normalized Gegenbauer atoms with strict even degree support10..40, aligned to fixed first-
 69 | residual_aware_l2_dispatch_ladder | killed | Retain the exact fused L2 formulas but choose direct, L1, or L2 by a frozen shape-only analytical-bill plus100
 70 | kerdock126_formal_l1_transplant | killed | Transplant the frozen Kerdock phase subset s=2..127 and seeded Haar absorption into the current row-blocked L1
 71 | kerdock_structured_wht_memory_folds | killed | Remove the persistent32256x256 direction matrix by exact phase-ordered WHT first propagation, then test a512-r
 72 | m71_kerdock126_one_buffer_owned_l1 | screened_survivor | Use Kerdock phases s=2..127 with Haar absorption and phased WHT first propagation, while one caller-owned acti
 73 | m76_validator_fallback_v3 | package_validated | Add a width-not-256 direct fallback solely so the sealed M71 package satisfies the official validator while pr
 74 | m77_m71_descriptive_launcher | killed_harness | Run the sealed M76 package once through a frozen descriptive launcher on already-burned public0..99 and compar
 75 | m73_signed_hosvd_cp_source | killed | Construct the Gaussian first-gate signed cubic/quartic source and compress it as a fixed-rank signed HOSVD-CP 
 76 | m74_finite_chaos_tt_recurrence | killed | Represent connected k3/k4 by tensor trains and propagate a finite Hermite connected-diagram alphabet through d
 77 | m78_homogeneous_huber_haar_mlmc | killed | Use a radial-covariant Huber ladder, common outer-Haar frame, shared antipodes, and an exact final residual to
 78 | m79_common_axis_output_shrinkage | killed | Apply a frozen common-axis positive-part contrast James--Stein shrinker to a streamed 256-output ReLU sample m
 79 | m80_kerdock_tangent_factorial | screened/uncertain | Hold M71's inherited diagonal tangent T_lambda=T0-lambda Delta at frozen lambda=.9807112198896164, then compar
 80 | m81_full129_pareto | killed | Restore the full 129-point real-MUB antipodal union, including coordinate basis, in place of the 126-point tri
 81 | m82_kerdock_vs_haar_variance | screened/unresolved | Compare frozen M71 Kerdock-126 outputs with formal L1 independent QR-Haar-frame outputs under their lawful see
 82 | m84_exchangeable_output_residual_ridge | killed | Use leave-one-output-row-out ridge to predict the residual of a weights-computable Gaussian/second-moment supp
 83 | m86_boundary_laplace_coarea | phase_a_pass_phase_b_unresolved | Replace smooth-cell Hessian reasoning with the distributional spherical Laplacian/coarea identity, then seek a
 84 | m83_common_backend_geometry | killed_protocol | Compare Kerdock and Haar point families through one common numerical forward backend so geometry is the only i
 85 | m85_deterministic_signed_source | killed | Build deterministic signed k3/k4 source loadings from exact rectified pair bridges and leading weak-correlatio
 86 | m87_equivariant_motif_attenuator | killed_static | Feed exact bridge path/star/triangle/cycle motif responses and transported rank-8 source loadings into a tiny 
 87 | m88_random_great_circle_rb | killed_calibration | Rao-Blackwellize spherical sampling by exactly integrating a deep ReLU network around a random great circle us
 88 | m89_great_circle_efficiency | killed | Compare exact random-great-circle fan integration with matched direct antipodal evaluation under an equal dens
 89 | m90_bridge_factor | killed | Apply a signed fixed-rank eigenfactor with exact diagonal repair to the complete centered ReLU pair bridge bef
 90 | m91_two_sided_cycle_sketch | killed | Estimate the full rank-8 fourth-order cycle core with independent two-sided Rademacher trace probes using E[(x
 91 | m92_equivariant_learned_closure | killed_protocol | Use a generated-only, dimension-free shared graph learner with batched W^T H, |W|^T H, and W^2^T H messages to
 92 | m93_wishart_linear_motif | killed | Split centered standardized ReLU into first Hermite chaos plus an orthogonal residual and delete a claimed pur
 93 | m96_equivariant_attention_closure | killed_pretarget | Repair M92 with explicit shared two-head attention, a previous-correction token, message-only edge interventio
 94 | m95_palm_coarea_sampler | killed_literal_intended_law_unresolved_disfavored | Sample the first forward output-fan facet from a uniform angular start, recover its preceding-sector inclusion
 95 | m97_transport_only_attention_closure | killed_protocol | Place every prior hidden/scalar state in a source tensor and transport it through W before forming current-nod
 96 | m98_transport_attention_controlled | killed | Train a generated-only transport-equivariant two-head closure against a Gaussian anchor with a correctly train
 97 | m99_hermite_conditioned_attention | killed_pretarget | Augment the transport-only closure with node-specific first-through-fourth Hermite response coefficients of ce
 98 | m100_identity_hermite_capacity_control | killed_preexecution_protocol | Correct M99's input boundary with identity-Gaussian chaos at layer zero and compare node-specific Hermite tran
 99 | m101_identity_hermite_reference_complete | killed_preexecution_protocol | Preserve M100's identity-correct, capacity-matched Hermite carrier while recomputing final precision after esc
100 | m102_identity_hermite_durable_reference | killed_preexecution_protocol | Nest an exact centered Hermite source-node/edge/state association residual beside the raw transport, repair ne
101 | m103_nested_hermite_audited | killed_pretarget | Restore hidden-permutation and gradient-block audits around M102's stable nested raw-plus-centered carrier and
102 | m104_nested_hermite_final_preexec | killed_preexecution_protocol | Freeze a complete self-contained nested Hermite experiment with tolerant permutation assertions, per-network r
103 | m105_nested_hermite_final_audited | killed_preexecution_protocol | Repair M104's seeding, clipping, tail/decomposition regressions, score retention, and descriptive shuffle whil
104 | m106_active_null_hermite_controlled | killed | Compare the correctly associated centered-Hermite recurrent transformer with a separately trained active null 
105 | m107_spherical_gegenbauer_exact_zero_controls | killed | Use six weights-only exact-zero spherical controls formed from normalized Gegenbauer degrees4,6,8 over W1-colu
106 | m108_heat_difference_scaled_harmonic_band | killed_preexecution_theory | Fold orthonormal-scaled spherical zonals q_l=sqrt(dim H_l)P_l through even degrees8..32 and combine them with 
107 | m108_centered_cymatic_band_energy | killed_preexecution_theory | Square the frozen unit-variance degree18 heat band and subtract its exact mean, E_a(u)=B_a(u)^2-1, then aggreg
108 | m109_uncorrected_nodal_occupancy | killed_preexecution_static | Center the bounded ReLU gate-tube indicator 1{|a.u|<=1/16} by an embedded spherical occupancy probability, the
109 | m110_corrected_nodal_occupancy | killed | Correct the spherical nodal-tube mean to I_(1/256)(1/2,255/2), repair positive-ReLU gauge invariance with ||W1
110 | m111_coherent_gate_interferometer | killed | Normal-order all off-diagonal first-gate sign pairs with the exact arcsine covariance and route them to each o
111 | m112_connected_gate_kernel | killed | For each independent Haar frame form the centered first-gate pair matrix C=V^T V/d-Sigma, then use the raw Fro
112 | m113_connected_hermite_vertex_engine | killed | Apply connected Hermite source vertices through independently sketched low-rank pair operators, with labeled g
113 | m117_collision_resummed_hermite_source | killed_preexecution_cost | Partition local Gaussian k3/k4 by external-label equality, evaluate every repeated-label stratum exactly with 
114 | m118_separated_collision_vertex | killed_preexecution_cost_and_mask | Represent the exact aabc collision cumulant as a certified separated approximation of its universal three-corr
115 | m119_schur_nystrom_adjoint_braid | killed_preexecution_theory_and_cost | Approximate each Price/orthant Schur kernel by a shared low-rank PSD Nyström factor, braid that factor through
116 | m120_normal_ordered_price_adjoint | killed_one_shot_connected_e_omission | Normal-order each Price gate kernel as pp^T plus an exact diagonal reset plus a zero-diagonal connected residu
117 | m116b_inplace_streamed_l3_b2048 | killed_one_shot_residual | Replace each 256-square layer multiply by an exact three-level Winograd/Strassen leaf bank, streamed over 2048
118 | m116c_inplace_streamed_l3_b4096 | killed_one_shot_residual_family_closed | A separately named B4096 child of M116b that doubles row-block height, halves full depth-32 L3 matmul calls fr
119 | m115_projective_arc_nystrom_control | killed_one_shot_variance_and_cost_no_retry | Normalize the first-layer weight axes, form the exact rectified-Gaussian arc kernel M, and use the projective 
120 | m121_bridge_source_normal_adjoint | repair_source_interface_carrier_blocked | Insert a signed non-Gaussian k3/k4 source at one hidden layer, transport it through exactly one affine map, co
121 | m122_nonzero_mean_bridge_source | preserved_source_algebra | Define signed nonzero-mean central k3/k4 ReLU bridge-tree sources using exact Hermite coefficients, exact pair
122 | m122_bridge_tree_factor | repair_implicit_operator_not_factor | Construct the k3 mode Gram exactly in O(n3), project k4 path/star cores once a factor is supplied, and expose 
123 | m123_implicit_krylov_source_factor | killed_preexecution_static_cost | Use the exact 16-orbit k4 path-pair reduction in a deterministic block-Lanczos schedule to obtain a certified 
124 | m124_shared_k3_source_projector | preserved_blocked_shared_reference_211_omission | Choose one standardised rank-four projector from the exact collision-corrected k3 mode Gram, reuse it for k3 a
125 | m125b_source_batched_forward_tangent | passed_carrier_component_independently_judged_cost_repaired | Exploit exact first-Born superposition on one frozen Gaussian background: add each layer's already-constructed
126 | m128_second_order_cumulant_response | repair_exact_response_missing_source_frechet | Extend the frozen-background first-Born recurrence to classical Edgeworth order two: add the linear connected 
127 | m126_repeated_output_source_contraction | repair_blocked_independent_component_pass | Compute only the repeated iii/iij/iiii/iiij/iijj cumulant slices consumed by the one-delay Edgeworth response.
128 | m129_source_frechet_tangent | repair_p2_mixed_f32_higher_counts_killed | Differentiate the entire state-dependent M122/M126 source, including normalized background coordinates, local 
129 | m130_direct_aabc_quadratic_collision | repair_preserved_quadratic_component | Replace the silently omitted three-label collision by the universal quadratic vertex (xy+xz+yz)/(4pi), contrac
130 | m132_p8_reduced_source_protocol | killed_preexecution_by_211_omission_gate | Freeze a target-free generated-only protocol around the M125b carrier and M126 mixed-f32 P in {2,4,6,8} reduce
131 | m131_trivariate_boundary_and_sampled_source | killed_complete_candidate_components_preserved | Evaluate the exact nonzero-mean [2,1,1] boundary coefficient and its Frechet tangent, or bypass coefficient en
132 | m133_factored_hidden_edge_sampler | killed_complete_allocations_components_preserved | Sample exact [2,1,1] collision triples from an O(n2) factored three-bank conductance law with a fixed uniform 
133 | m134_hermite_graph_degree_sampler | killed_raw_degree_sampling_components_preserved | Represent exact central [2,1,1] incidence as a finite signed population of hidden Hermite graph factors, sampl
134 | m135_conditional_lowrank_source | killed_generic_deployment_true_lowrank_operator_preserved | For an exactly typed Gaussian state C=diag(d)+UU^T and matching Frechet tangent, condition on the r common fac
135 | m136_equivariant_diagram_transformer | killed_generated_implementation_components_preserved | Canonicalize positive ReLU gauge, compile signed star/ABAB/ABBA/[2,1,1]/delayed-response graph motifs, add one
136 | m137_terminal_law_resummation | killed_closures_theorem_preserved_numerics_unverified | Grant exact terminal mean, variance, third cumulant, and fourth cumulant for free, then map those four moments
137 | m138_balanced_triple_sampler | killed_output_variance_operator_preserved | Keep M133's exact factored proposal, five repeated-output products, 5 percent uniform rescue, canonical Hansen
138 | m139_positive_partial_trivariate_proposal | killed_static_proposal_components_preserved | Use a singularity-subtracted low-rank approximation to the exact nonzero-mean trivariate [2,1,1] boundary only
139 | m140_quadratic_residual_control | killed_preexecution_cost_completeness_and_variance | Partition the exact standardized nonzero-mean [2,1,1] coefficient into the universal quadratic jet J=(QijQik+Q
140 | m141_local_factor_boundary_cubature | repair_local_identity_killed_deployable_engine | For each sampled three-coordinate Gaussian block, factor C=lambda I+UU^T with rank(U)<=2, condition on the loc
141 | m144_gate_aligned_split_merge | killed_cost_and_recursive_novelty_components_preserved | Split each Gaussian surrogate component along a gauge-covariant gate-boundary direction using exact half-space
142 | m143_output_aware_suffix_proposal | killed_implementation_endpoint_link_preserved | Use a cheap sign-scrambled suffix-energy response sketch only to steer an exact full-support HH hidden-edge pr
143 | m145_defensive_acg_transport | killed_deployable_tail_components_preserved | Fit a low-rank angular-central-Gaussian proposal on an independent pilot, mix it with20 percent uniform mass s
144 | m146_pilot_adaptive_hidden_edge_hh | killed_cost_wall_theorem_preserved | Use pilot edge responses to form a causally frozen adaptive full-support HH proposal for remaining hidden trip
145 | m147_endpoint_safe_pair_bridge | pair_component_pass_generic_nested_endpoint_open | Use exact endpoint limits, Price-remainder enclosures, and a cancellation-safe nonnegative integral for bivari
146 | m148_exact_control_residual_law | proved_operator_literal_copula_killed | Add a deterministic [2,1,1] source control and an exact full-support HH estimate of target minus control, pres
147 | m149_fixed_43_87_endpoint_provider | killed_accuracy_api_preserved | Replace recursive endpoint integration by a fixed nested43/87 compactified outer rule with87 pair calls and fa
148 | m150_direct_all_output_adjoint_control | killed_generic_rank_cost_local_identity_preserved | Associate the exact C_211 sum directly with a supplied response dual so dense source matrices need not be emit
149 | m151_b1_forward_control | killed_masked_compiler_control_identity_preserved | Use one signed49-node canonical block to emit a deterministic C_211 control into the existing one-carrier forw
150 | m152_crossrisk_weight_student | killed_preexecution_capacity_and_cost | Train the existing50-column gauge-equivariant weight student using independent cross-risk/noise2noise sampler 
151 | m153_exact_formal_prefix_reuse | killed_resource_descendant_memoization_preserved | Memoize proposal-pilot states only while every preceding Formal active set remains full width, then fail the s
152 | m154_rankone_analytic_endpoint_partition | rankone_pass_generic_provider_killed | Partition the moving ReLU kink analytically on rank-one conditional Gaussian states using Price/delta identiti
153 | m155_masked_star_khatri_obstruction | proved_no_go_domain_lift_open | Expose the exact split-pair action induced by zeroing covariance-star coefficients on repeated labels.
154 | m156_extended_domain_star_control | compiler_resource_pass_source_variance_open | Extend the target by zero to collision triples, define c=-2VijVik on all triples, sample target-minus-control 
155 | m157_selfhosted_formal_pilot | killed_hostile_resource_mechanism_preserved | Replace the separate32-layer dense proposal pilot by the already-required Formal q0 pilot response, freeze q1,
156 | m158_physical_absolute_endpoint_abi | killed_literal_contract_endpoint_family_preserved | Require every admissible PSD state to materialize a physical binary64 [2,1,1] coefficient within2e-8 absolute 
157 | m159_scale_normalized_endpoint_abi | abi_repaired_generic_evaluator_open | Carry Delta as2^(4e)d with exact dyadic exponent metadata, evaluate a dimensionless state, preserve PSD rank/z
158 | m160_hostile_selfhosted_pilot_audit | killed_resource_audit_complete | Run M157 in five independent CPython3.11 target-shaped workers plus a forced early-pruning worker, measuring c
159 | m161_complete_domain_star_variance | killed_source_variance_domain_lift_preserved | Evaluate M156's exact complete-domain covariance-star control on six frozen generated Gaussian backgrounds wit
160 | m162_plackett_tallis_fixed_line | killed_fixed_rule_generic_family_open | Use Tallis's tilted truncated-normal MGF to reduce the twelve [2,1,1] raw moments to one trivariate orthant pr
161 | m163_exterior_collision_null_control | resource_killed_identity_preserved | Replace M156's covariance star by A=V o (1-R^2), the two-vector exterior Gram determinant factor, and use c_ij
162 | m164_exterior_native_audit | killed_hostile_resource_no_efficacy_run | Run the frozen M163 exterior collision-null source and M156 five-product compiler in five fresh target-shaped 
163 | m165_rank_face_subtraction | rankone_survivor_generic_provider_open | Assemble the complete connected [2,1,1] defect before differentiation, subtract the M154 rank-one value and co
164 | m166_oriented_collision_null_control | exact_f64_cost_killed_orientation_preserved | Orient covariance edges by the permutation-covariant row score s_i=max_{ell!=i} R_iell^2, split them into disj
165 | m167_collision_owner_unification | owner_algebra_pass_relabelling_rejected | Move complete-domain collision triples into their true fourth-cumulant owners with exact orbit multiplicities:
166 | m168_transverse_rank2_anchor | rank2_face_survivor_generic_provider_killed | Represent a positive-marginal transverse rank-two Gaussian state on its canonical 2D support plane, compute th
167 | m169_m163_two_axis_call_fusion | resource_survivor_conditional_staging_interface | Stage all31 already-owned M163 layer pairs, batch the31 Z products once and the124 post-Z products once throug
168 | m170_m166_dense_tensor_rank | killed_dense_product_reduction_triangular_edge_preserved | Attempt an exact at-most-five-family compiler for M166 using polarization, common subexpressions, B=A^T, symme
169 | m171_fixed10_rank_stratified_provider | killed_uniform_certificate_rank_face_algebra_preserved | Combine M154/M165 rank-one and M168 rank-two connected-first anchors with one ungraded fixed10-node Gauss-Lege
170 | m172_selective_22_owner_fusion | static_owner_algebra_pass_development_blocked_m174_unlawful_caller_abi | Move only physical[2,2] ownership into M163's ijj rows, retire the old[2,2] source/probe, and sample residual 
171 | m173_parameter_scaled_boundary_layer | screened_hostile_transverse_rank2_layer_certificate_only | Replace only M171's near-parallel physical-coordinate GL10 panel by the exact split Phi((u-u*)/eta)=1{u>u*}+g(
172 | m174_m169_staging_interface_audit | repair_missing_actual_caller_abi | Audit whether an actual estimator lawfully owns the31 labelled full-covariance W,V states and M163-slot-to-M12
173 | m175_b8_labelled_background_abi | no_go_current_code_exact_labelled_producer_absent | Instantiate M174's only frozen fallback as fixed B=8 blocks [8,8,8,7] with immutable zero-order background lab
174 | m176_exact_background_archive_producer | no_go_endpoint_complete_bivariate_primitive_absent | Pin and implement only the exact labelled FlopScope-metered zero-order mu,V,J recurrence required before M175'
175 | m177_bivariate_relu_value_jacobian_primitive | formal_runtime_no_go_phi2_owent_certificate_absent | Bundle an endpoint-complete scale-normalized noncentral bivariate Gaussian ReLU value-and-Jacobian dispatcher 
176 | m178_certified_phi2_owent_provider | component_pass_certified_bounded_cost_phi2_owent_provider | Implement a certified, statically bounded-cost, scale-normalized Phi2/Owen-T value-and-first-derivative evalua
177 | m179_exact_background_archive_producer | component_pass_exact_metered_labelled_background_archive_producer | Build the exact zero-order full-covariance recurrence (mu_0=0,V_0=I; a_l=mu W_l; C_l=W_l^T V_{l-1} W_l) and th
178 | t1_l2_promotion_verification | screened | Independent re-verification of the non-promoted two-axis L2 Winograd scored survivor (submission_random32256_r
179 | t2_fullcov_closure_standalone_estimator | killed | Score the certified M179 exact zero-order full-covariance Gaussian closure as a standalone submission-style es
180 | dpm_victory_postmortem_redteamed | screened | Reverse-oracle planning artifact: narrate the Phase-2 win as-if from 2026-09-20, ground every causal link in a
181 | dac_prize_report_extension_v2 | screened | Extend the frozen tangent-lineage Algorithmic-Contribution report (builder extracted from the frozen source-re
182 | t3_fold3_deterministic_cap | screened | fold3-39936 with a deterministic per-network billed-FLOP cap: a billed pilot-identical simulation of the paren
183 | t4_kerdock_v3_descriptive_rescore | screened | NEW predeclared descriptive protocol (old single-use gate stays burned): execute the frozen Kerdock M71 v3 ent
184 | t5_submission_dossier_runbook | screened | Terminal consolidation: every candidate ranked on ONE basis (local public-100 descriptive), the three-champion
185 | n7_rqmc_scaling_law_probe | killed | Premise probe: does RQMC (antithetic Kronecker lattice + Cranley-Patterson) exhibit superconvergent MSE-vs-N s
186 | n8a_rqmc_kerdock_draw_stage | killed | Swap the Kerdock v3 draw stage for antithetic Kronecker+Cranley-Patterson RQMC, gated on the G0 premise that v
187 | n8b_disclosed_native_backend | killed | Route sampler forwards through the verified K1 fused kernel as a Rules-5.2 disclosed off-flopscope backend pri
188 | n8c_offline_corrector_premise | killed | G0 premise gate for the sanctioned offline per-neuron corrector: decompose the frozen Kerdock v3 estimators fi
189 | n9_kerdock_composition_interaction | killed | G0 interaction gates for the last unbuilt composition: (a) moment-tangent control (frozen lambda 0.98071121988
190 | c1_local_vs_hosted_calibration | screened | Measure our local suites budget-matched Monte-Carlo baseline (plain antithetic MC, 57344 samples, final layer 
191 | m180_design_strength_g0 | killed | Mutate the angular design itself (the axis the corpus never touched): Arm B MUB-family mix, Arm C coset-strati
192 | m183_f32_hotpath_falsifier | killed | M182-mined top mechanism: flopscope stats functions silently return float64 (billed 2x) and one promoted array
193 | m181_terminal_smoothing_g0 | killed | Hybridize the T2-killed closures certified rectified-Gaussian moments onto the promoted sampler as a terminal 
194 | m184_trichotomy_upward_g0 | killed | Extend the terminal dead/on/kink trichotomy to middle layers: exact on-run linear composition + firing-sorted 
195 | gen3_recursion_packet | proposed | Headroom-Recursion Generation 3: recursion packet built per the skill spec from the LIVE hosted champion (Kerd
196 | a3_kill_heterogeneity_reaudit | screened | Skeptic pass on our own 12 kills: 4 pre-registered heterogeneity suspicions adjudicated STANDS/WEAKENS/FLIPS f
197 | a4_hostile_inputs_battery | screened | Hostile-inputs battery on the frozen v3 at the real 2.72e11 budget: scale extremes, heavy tails, rank deficien
198 | a1b_tail_apriori_flag | killed | Independent mining of the M185 stage-1 checkpoint (80 nets, 15.5x MSE spread reproducing the hosted tail): can
199 | m185_tail_pruning_mechanism | killed | Gen3-P1: is the hosted 11x per-net tail a fixable pruning/fold misclassification? Stage 1: reproduce + correla
200 | m191_harmonic_spectrum_g0a | screened | Padgett trigonometric-model bolt steelmanned: measure the Kerdock designs quadrature-error spectrum on zero-me
201 | wc1_winner_ablation_map | screened | Winner catalog by ablation: disable each promoted component of the frozen v3 one at a time (frames/radial/prun
202 | pb1_dial_battery_m188_m189 | killed | The failure-cross dial arms on the cached-truth Premise Battery: M188 fold on_alpha {3.5,4.0,5.0} x M189 dead_
203 | m191_harmonic_cv_g0b | killed | The harmonic control variate at the designs first non-exact degrees: 24 weight-derived deg-4/6 basis functions
204 | gen3_p2_rotation_selection | killed | Rotation SELECTION (not fragmentation): oracle-of-k headroom across 16 full-n rotations x 3 nets vs cached tru
205 | p2b_weights_only_rotation_proxy | killed | Zero-forward-cost rotation-quality proxies tested against the archived P2 data (48 net-rotation MSEs): A) w-al
206 | v31_guards_m186_m187 | validated | Kerdock v3.1 GUARDS: frozen v3 + M186 empty-regime guard (specific-ValueError catch -> analytic-means degradat
```
