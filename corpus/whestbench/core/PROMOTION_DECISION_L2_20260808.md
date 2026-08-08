# T1: Promotion memo — two-axis L2 Winograd as slot-1 designate

Date: 2026-08-08. Author: campaign (Fable). Status: RECOMMENDATION — the
gate-override policy call and final designation belong to the user.

## Recommendation

Designate `submission_random32256_rowwinograd_l2_20260806.tar.gz`
(SHA-256 `68259f644353ac0be2f840d8e48c02083c9f1b21c88f0a795d651f3d936a83a4`)
as the slot-1 (sampler-line) nomination, over the frozen L1 champion. L1
(`bc2ec395…8ae36`) remains the rollback and is submitted as a graded baseline
first per the standing authorization.

## Evidence (all OBSERVED this session, independently recomputed from disk)

Source: `work/scorefloor_generation/two_axis_production/` (paired100_results
.json + candidate_official100.json) and `row_blocked_production/` (parent
artifact). Recompute scripts: scratchpad `t1_recompute.py`, `t1_breakeven.py`.

1. **Tar hash verified**: Get-FileHash reproduces `68259f64…936a83a4` exactly.
2. **Post-patch accounting confirmed from the env lock, not assumed**:
   `run_metadata.json` pins flopscope **0.10.0**, whestbench **0.14.0**, run
   completed 2026-08-06T23:49Z — three days AFTER the organizers' 2026-08-03
   residual-safeguard patch. The red-team attack "the L2 gain was measured
   under the old accounting" is REFUTED at the observed level.
3. **Paired result reproduces exactly**: mean child adjusted 2.101976249e-7,
   parent 2.121762464e-7, ratio 0.990674633, 88/100 paired wins, 0 failures —
   every digit matches REPORT.md.
4. **Fresh-seed bootstrap agrees**: 200k resamples, seed 20260808 (independent
   of the frozen run's 2026080697): ratio CI [0.987799, 0.993996],
   P(child better) = 1.000000. The direction is not an artifact of the
   original bootstrap seed.
5. **Extraction check**: rebuilding adjusted scores from per-network
   (final_layer_mse, flops_used, residual_wall_time_s) via
   `mse * max(0.1, C/B)` reproduces the artifact mean at 0 relative error.
   (Note: all multipliers exceed 0.6, so this does NOT discriminate the
   0.1-vs-0.5 floor question — the floor never binds here.)

## The risk, quantified (row-level, observed)

The L2's entire gain is in C (raw MSE ratio 1.000033); C's residual component
depends on the grader's wall clock, which local hardware cannot observe.
Scaling every per-network residual by k and re-scoring both sides:

- k = 1.00: child wins (2.1020e-7 vs 2.1218e-7)
- k = 1.25: child wins (2.1587e-7 vs 2.1667e-7)
- **break-even k\* = 1.42** — if the grader's residual wall runs >=1.42x
  slower than the local single-core-pinned box, the L2 LOSES to L1.
- Strict-failure cliff (any network breaching B): child k=3.75, parent
  k=3.83 — far from the win/loss boundary; failure risk is NOT the concern,
  rank inversion is.

Settling check (named per protocol): one graded submission of each tar — the
grader's own C report on identical MSE reveals the true k directly. This is
queued in the user-return runbook and costs 2 of the 50 daily entries.

## The gate-override framing

Gate B's <=0.99 mean-ratio threshold was self-imposed and predeclared; the
child scored 0.990675 (miss: 0.000675). REPORT.md correctly refused to weaken
the threshold post hoc, and this memo does not relabel that decision. The
question NOW is different: with only 2 nomination slots and both candidates
already validated, the designation choice is a portfolio decision, not a
promotion-gate decision. On the evidence, L2 is the better slot-1 designate
(P(better) ~ 1.0 locally, downside bounded at ~0.9% and reversible via the
graded-baseline comparison before designation deadline). The user makes the
final call at designation time with both grader-reported scores in hand.

## Disposition

L2: recommended slot-1 designate, pending user + graded confirmation.
L1: rollback + graded baseline. Frozen candidate dirs untouched (verified:
run_metadata hashes_before == hashes_after; this memo lives in the corpus, not
in the candidate tree).
