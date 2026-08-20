# Graveyard run-all results (2026-08-10 19:20 UTC) - 16/16 falsifiers adjudicated

Opus-5 workers + Opus-5 judges (Fable conserved per owner). Full per-item
artifacts: corpus/whestbench/experiments/gm_*/ (PREDECLARATION.md +
VERDICT.md + results.json each); judge-drafted ledger appends in workflow
journal wf_9a3a25bd-1c2 (session archive).

REVIVED_SCREENED (4) - Gen-8/Phase-2 proposals, NOT promotions:
- gm_rankone_bill: the M204/M205/M206 "over budget" verdicts were priced
  under an undischarged f64 convention; f32 parity discharged with >2
  independent signals (exact-rational reference 2e-16, alt-association
  1.98e-15, bit-repeat) -> bills reprice ~2x DOWN and fit strict M199
  headroom (34% under). Width-256-specific; not reusable at larger n
  without re-measurement (judge's named residual risks on record).
- gm_u9_s4_d2: S4 Door-B portfolio math re-derived under corrected vD.
- gm_c1_bound: local-vs-hosted calibration bound tightened from committed data.
- gm_u3_grid: tail-model fidelity 2-D bracketing grid passed.
KILL_CONFIRMED (10): a1b_diffflag, p2b_proxy, ecn_psi, a4_constraint,
flatworm, u4_suitesize, latent_cubature, s1s4_vd, m179_m199, s17_reuse -
the graveyard dispositions stand, now MEASURED rather than assumed.
BLOCKED_ESCALATE (1): m116_streams. INCONCLUSIVE_HOLD (1): residual_k1
(the x5-convention re-derivation needs a cleaner second signal).

ORCHESTRATOR TODO (per OPUS5_HANDOFF): review gm_* artifacts, append the
16 judge-drafted ledger records, pytest the ledger, commit. Successor
inherits this if Fable's window closes first.
