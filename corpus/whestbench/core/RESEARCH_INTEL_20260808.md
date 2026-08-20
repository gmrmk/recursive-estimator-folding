# Research intel (2026-08-08): the leaderboard decoded

Six-agent public-web sweep (discourse, challenge pages, leader trails,
literature, benchmark repos + synthesis). Full structured findings in the
workflow output; this is the decision-relevant distillation. Confidence
labels per claim.

## 1. The top-4 are an accounting artifact, not an algorithm (INFERRED on
OBSERVED community forensics + organizer statements)

- OBSERVED (3 independent measurers, discourse 18099/18108/18125): top
  submissions run instrumented-FLOP share ~1e-5 (honest entries ~0.93),
  billed FLOPs identical to 3 sig figs across all 50 MLPs, and 38.6-64.8 s
  per-MLP wall against the ~0.27 s residual allowance a floor multiplier
  implies. Nearly all real arithmetic lands unbilled.
- OBSERVED: organizer dipam confirms participants can ship native
  NumPy/BLAS/native code billed only via residual time, and announces
  REVIEWS of submissions routing computation around flopscope accounting.
- The Aug-3 patch (flopscope 0.10.0: f64 2x, data movement priced, 1 core)
  reduced but did not close the channel; the leaders improved ~25x AFTER it
  (consistent with re-optimized all-f32 native kernels).
- Campaign consequence: **we do not chase this.** The fold-ledger legality
  invariant ("no accounting bypass, hidden compute") and the skill's
  non-negotiables prohibit it; the organizer review means those scores may
  not survive the private rerun anyway. Prizes come EXCLUSIVELY from the
  private re-execution on fresh MLPs.

## 2. The honest frontiers (REPORTED, public writeups)

- Unbiased sampling: ~4.1e-7 adjusted at C/B 0.42 (evaaaz, 18053); a
  Lean-4-machine-verified argument bounds unbiased estimators at ~3.7e-7
  adjusted (arianvassili, 18105).
- Mechanistic/hybrid (RQMC + Gaussian closure + measured Edgeworth + offline
  ridge corrector; trajectory-calibrated moment chains): raw 2.2e-7..6e-6
  (18085, 18097, 18106). Pure closure plateaus ~1e-6 raw (18063) — consistent
  with our T2 kill of closure-as-estimator.
- **Our Kerdock v3 (raw 2.49e-7, adjusted 1.62e-7 local descriptive) is AT
  the documented honest public frontier.** Legal bias (pilot-rescue) is why
  it can sit under the unbiased Lean bound.

## 3. The one open scientific lever (REPORTED -> N7 tests it)

Submission 314695 measured the pre-activation covariance participation ratio
contracting 128 -> 5.2 over 32 layers: the integrand is effectively
~5-dimensional by the deep layers — the textbook condition for RQMC
near-O(N^-2) MSE. If that rate is real on this integrand, honest RQMC at
full budget could reach raw ~1e-8 (multiplier 1) or better, entering the
arbitrage tier's band legitimately if/when that tier is repriced. N7
(predeclared separately) measures the actual MSE-vs-N slope locally.

## 4. Runbook deltas (fold into SUBMISSION_DOSSIER at next commit)

- FLOOR = 0.1: now OBSERVED twice (leaderboard arithmetic; consistent with
  starter-kit source). Tangent's floor-probe role is obsolete — it remains
  the prize-filing vehicle only.
- Designation slots: CONFLICT — challenge page says ONE designated
  submission; the Aug-3 organizer thread says "up to two nominated". Verify
  on the live page at designation time; plan for ONE (conservative).
- Prize rankings: private re-execution ONLY, fresh private-seed MLPs. The
  public board (and the arbitrage tier on it) does not decide prizes.
- Algorithmic Contribution: organizers explicitly prioritize MECHANISTIC
  estimation; Phase-2 writeup deadline Sep 26 (Phase-1 Aug 17). Our
  certified-provider chapter aligns exactly with the stated judging taste.
- Bit-packing through metered integer ops (32 bools/FLOP) was ruled LEGAL by
  dipam — a modest honest cost lever for gate masks.
- Residual-vs-instrumented: even post-patch, one core of optimized f32 GEMM
  (~1.5-2e11 FLOP/s) outruns lambda = 1e11/s by ~2x — a DISCLOSED native
  sampler backend is legal per Rules 5.2 and worth ~2x on the multiplier
  (K1's measured kernel is the starting point). Distinct from the
  arbitrage: everything disclosed, wall time honestly charged.

## 5. What remains unknown

- Whether the organizer review will reprice/DQ the arbitrage tier before
  Phase-2 close (their Aug-3 precedent says repricing happens).
- The private-rerun behavior of every candidate (grading feedback richness
  still unverified).
- Whether RQMC superconvergence materializes on this integrand (N7).
