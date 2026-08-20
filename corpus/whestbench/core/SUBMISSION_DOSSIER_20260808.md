# WHestBench Phase-II submission dossier + user-return runbook

Date: 2026-08-08. This is the campaign's consolidated terminal deliverable:
every candidate on one basis, the three-champion conflict reconciled, and a
scripted runbook for the day the user is back at a machine with AIcrowd
access. Phase 2 closes 2026-09-19 23:59 UTC. Latest-safe first submission:
**Sep 12** (grading latency is the binding constraint — the only observed
datum is #318609 sitting ungraded for weeks).

## 1. The reconciled candidate table (ONE basis: local public 0..99, seed 0,
subprocess, whestbench 0.14.0 / flopscope 0.10.0, B = 272e9)

| rank | candidate | adjusted | raw MSE | mean C | max C | fail | packaged tar (sha256 prefix) | status |
|---|---|---:|---:|---:|---:|---:|---|---|
| 1 | **Kerdock M71 v3** | **1.6191e-7** | 2.4939e-7 | 178.5e9 | 209.6e9 | 0/100 | `b55a1d8d…30af` (33,344,900 B) | DESCRIPTIVE best; validator-passed; hosted OOM risk (1.445 MiB margin) |
| 2 | two-axis L2 | 2.1020e-7 | 3.0896e-7 | 187.8e9 | 216.7e9 | 0/100 | `68259f64…83a4` (8,510 B) | non-promoted survivor; residual-fragile (k*=1.42); memory margin 15.75 MiB |
| 3 | L1 champion (formal) | 2.1218e-7 | 3.0895e-7 | 189.9e9 | 222.4e9 | 0/100 | `bc2ec395…8ae36` (8,357 B) | the register's champion; safest lineage; the canary |
| — | fold3-cap (NEW) | **unknown** | unknown | capped ≤ 0.9B by construction | ≤ 244.8e9 | — | `d3f5aefa…1a6c` | engineering-gated (G1-G4 all pass); score only via grading |
| — | tangent-control | not comparable (dev20 2.775e-7; lockbox800-999 raw 9.911e-7) | — | ~0.34·B | 0.343·B | 0 | `d2e58df6…f231` (33,332,322 B) | different lineage/split; the floor probe + prize-filing vehicle; local v0.14 validate-package PASS (2026-08-08) |
| ✕ | analytic closure | KILLED (T2: bias 9.6e-5, 46x over boundary at any floor) | | | | | — | Algorithmic-paper exhibit only |
| ✕ | fold3-39936 uncapped | 1.41e-7 on 5 nets only; historically 5/100 budget failures at n=100 | | | | | none | superseded by fold3-cap |

Notes: all ranked numbers are LOCAL and (for Kerdock) DESCRIPTIVE — public
0..99 is burned; nothing above is a competition-current score claim. The
hosted grader's suite, feedback richness, clock, and memory cap are unknown;
the runbook's whole design is to convert entries into that missing knowledge
in the right order.

## 2. The three-champion reconciliation

Three documents declare three champions: UNCERTAINTY_REGISTER (L1, "the only
verified entry"), SUBMISSION-HANDOFF (tangent, "only candidate that passed
every predeclared gate" — of ITS lineage), PROMOTION_DECISION_L2 (L2, gated
on grader evidence). All three were written before 2026-08-08. Resolution:
they are answers to different questions on different bases. The dossier's
single rule replaces them: **grader evidence ranks candidates; local numbers
only order the queue.** Queue order (by local evidence x hosted risk):
L1 (canary) → Kerdock v3 → L2 → tangent → fold3-cap.

## 3. USER-RETURN RUNBOOK (each step gated on the one before it)

Preconditions (hosted-audit items, all verified still applicable 2026-08-08):
- P1. Use ONLY `work\whest-v014\Scripts\whest.exe` (whestbench 0.14.0,
  exe sha `888a44d9…`). NEVER the starter-kit v0.12.0rc5 CLI.
- P2. `$env:PYTHONIOENCODING='utf-8'` before every CLI call.
- P3. No `--dry-run` on sealed artifacts (exits 2 / builds a NEW package).
- P4. Before ANY upload: `Get-FileHash` against §1's sha256, `validate-package
  --json`, and **`tar -tzf` member listing** (T3 near-miss rule: a tar can
  validate while missing its sibling modules — count the members).
- P5. The user personally runs `whest login` (credentials are outside agent
  scope, always).

Steps:
1. **Account audit** (web UI): team membership, Phase-2 eligibility,
  remaining daily quota (cap 50/day), and — decision-critical — whether
  designation allows ONE or TWO submissions for the private re-run (hosted
  audit read: one; rules v12 read: two; believe the live page on the day).
2. **Check submission #318609** (July T5C1): aicrowd.com/challenges/
  arc-white-box-estimation-challenge-2026/submissions/318609. Its grade is
  the first datum on grading latency + feedback richness. Pre-patch
  submission: do not read its score as a Phase-2 signal.
3. **Feedback audit** (before spending entries): open any graded submission's
  detail page and record WHAT the grader exposes (adjusted only? raw MSE?
  C/multiplier? failure count? memory?). This selects the branch below.
4. **Submit the L1 canary** (`bc2ec395…`). Safest artifact; its grade proves
  the pipeline end-to-end and anchors the hosted-vs-local comparison.
5. **Submit Kerdock v3** (`b55a1d8d…`) and **L2** (`68259f64…`) once the
  canary grades (or same day if latency looks long — quota is not scarce;
  ATTENTION is; never submit what P4 hasn't re-verified that day).
6. **Submit the tangent archive** (`d2e58df6…`). Dual purpose: (a) at
  C/B ≈ 0.34, IF the feedback (step 3) exposes the multiplier or anything
  equivalent, its grade reveals the 0.1-vs-0.5 floor; a reading near 0.5 is
  ambiguous — record and move on; (b) its graded ID unblocks the prize
  filing (§4). If feedback is adjusted-only, its floor information is
  limited to how far the visible score sits from the two floor-hypothesis
  predictions (2.775e-7-basis shifted — weak, record honestly).
7. **Submit fold3-cap** (`d3f5aefa…`) last — score-unknown by design; its
  grade is its first score anywhere.
8. **Designate** per the rule in §5, with the user's final say, before the
  deadline, on the live page's slot count.

Degraded-mode branch (if grading is slow or feedback is adjusted-only):
the L2-vs-L1 hosted comparison stays valid as a same-hidden-suite paired
read; k and the floor stay unknown; designation then leans on hosted
adjusted scores alone + local evidence, and the safest designate is
whichever of Kerdock-v3/L1 has the better HOSTED number (Kerdock's local
edge is 23% — big enough to survive rounding; L2's 0.9% edge is not).

## 4. Prize filing ($20k Algorithmic Contribution)

The extended report is ready: `corpus/whestbench/experiments/
dac_prize_report_extension/` (builder v2 + rendered 6-page DRAFT-v2 PDF; §6b
non-Gaussianity wall added; refs DOI-verified). At filing time:
`python build_phase2_report_v2.py <out.pdf> --submission-id <GRADED_ID>`.
The report is written around the TANGENT estimator — use the tangent
archive's graded ID. If the tangent fails hosted grading, the fallback is a
rework around a sampler ID (known risk, recorded in the extension README).
File by the Algorithmic Prize deadline; do not tune anything from private or
lockbox scores.

## 5. Designation decision rule (written before any grade exists)

Among candidates with a successful hosted grade, zero failures, and no
memory/tail anomaly: designate the best hosted adjusted score. Margins under
~1% between candidates are NOT settled by two rounded leaderboard scalars —
prefer the candidate with the larger local margin and the safer compute/
memory profile (which, on today's evidence, is Kerdock v3, then L1). The
private fresh re-run decides prizes; every designation is a proxy bet, and
the user makes the final call.

## 6. Open risks (labeled, with their settling checks)

- Kerdock hosted memory (1.445 MiB margin): settled only by its graded run.
- L2 residual scale k* = 1.42 and 15.75 MiB margin: settled by the paired
  graded runs.
- Floor 0.1-vs-0.5: settled (maybe) by the tangent grade; else organizer
  email (draft exists: ORGANIZER_CLARIFICATION_DRAFT_20260806.md — trim its
  dead student questions before sending).
- One-vs-two designation slots: live page on the day.
- Grading latency: unknown; hence Sep 12 as the latest-safe first submission
  and the canary-first order.
- The fresh private suite may reorder everything; nothing local or public
  is a prize claim.

## 7. Artifact index (all verified on disk 2026-08-08)

- L1: `$SHARE\submission_formal_local_champion_l1_20260806.tar.gz` (also
  byte-identical at row_blocked_production\…rowwinograd8192…) — bc2ec395…
- L2: `$SHARE\work\scorefloor_generation\two_axis_production\
  submission_random32256_rowwinograd_l2_20260806.tar.gz` — 68259f64…
- Kerdock v3: `$SHARE\work\scorefloor_generation\kerdock_l1_owned_buffer\
  submission_kerdock126_l1_owned_b4096_validated_v3_20260806.tar.gz` —
  b55a1d8d…
- tangent: `$SHARE\outputs\WHestBench-Phase-II-tangent-candidate.tar.gz` —
  d2e58df6…
- fold3-cap: `corpus\whestbench\experiments\t3_fold3_deterministic_cap\
  submission_fold3cap_n39936_20260808.tar.gz` — d3f5aefa…
- NEVER upload: `$SHARE\outputs\whest-headroom-owen.tar.gz` (rc5-era).
- Prize report: `corpus\whestbench\experiments\dac_prize_report_extension\`.
- Campaign records: fold ledger records 179-185; commits 6eac6cc → 913121d;
  the red-teamed VICTORY_POSTMORTEM_20260808.md.

($SHARE = C:\Users\strid\Documents\Codex\2026-08-02\
https-chatgpt-com-share-6a5556ed-2e1c)

---

## ADDENDUM (2026-08-08, post-#1-pursuit): intel + N-series, and what they change

The user set the goal "surpass #1." Everything learnable locally was learned;
this addendum supersedes the sections above where they conflict.

### Intel (RESEARCH_INTEL_20260808.md; observed unless labeled)
1. **Floor = 0.1, OBSERVED** (top-3 adjusted/raw = 0.111/0.104/0.100 —
   impossible under max(0.5,·)). The tangent entry is now PRIZE-VEHICLE ONLY
   (its floor-probe role is obsolete). Runbook step 6 simplifies accordingly.
2. **The board's top-4 (adjusted 4e-10..1e-9) are an unmetered-compute
   arbitrage under active organizer review** (instrumented share ~1e-5,
   38-65s wall vs the 0.27s a floor multiplier allows; organizer dipam
   confirms the channel and announces reviews). We did not and will not
   chase it (ledger legality invariant). Prizes come EXCLUSIVELY from the
   private re-execution on fresh MLPs — the displayed board does not decide
   money.
3. **Honest frontiers**: unbiased ~4.1e-7 adjusted (Lean-verified class
   bound ~3.7e-7); best documented mechanistic/hybrid pipelines raw
   2.2e-7..6e-6. **Kerdock v3 (raw 2.49e-7 / adjusted 1.62e-7 local
   descriptive) is at the documented honest frontier.**
4. Designation slots: live challenge page says ONE, the Aug-3 organizer
   thread says two — check the live page on designation day; plan for ONE.
5. Phase-2 Algorithmic writeup deadline: **Sep 26**. Organizers explicitly
   prize mechanistic work — the extended report (dac_prize_report_extension)
   matches their stated taste.

### The N-series (all five killed at predeclared gates; commits 7aa2b77,
235191d, 951f3d5, 21ffa00 + this one)
- N6 great-circle Rao-Blackwellization: FoM 0.006x (circle worth ~6 iid
  samples, costs ~1000). Dead.
- N7 RQMC superconvergence: absent (slopes -0.97/-1.23 vs kill -1.25);
  constant 1.5-2.7x only, and only vs unconditioned iid.
- N8a lattice-vs-Kerdock-frames: the v3 sampler is a phased-Hadamard
  spherical design ALREADY 2-3.2x over conditioned MC; the lattice is 2.1x
  WORSE. (Retro-explains v3's standing.)
- N8b disclosed-native backend: one-core-pinned kernel = 0.94e11 FLOP/s <
  lambda — a 0.94x regression on measurable hardware. Dead.
- N8c offline corrector: v3's final-layer bias share is statistically ZERO
  (CI [-0.031, 0.097]) — pure sampling variance; nothing to correct. Dead —
  and a gift: **v3 is unbiased-in-practice at the scored layer**, the best
  possible private-rerun robustness property.

### Consequence for the goal
Every honest local lever is now either shipped (5 packaged candidates, §1)
or killed with predeclared evidence. Surpassing the displayed #1 requires
(a) the user's login to run the graded queue and designation, and
(b) realistically, the organizer review repricing the arbitrage tier — at
which point the honest ranking (where Kerdock v3 is designate-apparent,
now with a measured unbiasedness argument) is what remains. The runbook
above is the complete playbook for that day.

### ADDENDUM 2 (browser session): the runbook is now URGENT, and our
### candidates are better than the local numbers said

See HOSTED_INTEL_20260808.md and c1_local_mc_calibration/C1_REPORT.md.

1. **PHASE 1 IS LIVE** ($50K pool; Phase 2 is UPCOMING, $100K, closes
   Sep 19). The binding deadline is the Aug-10 Phase-1 extension — the
   "Sep 12 latest-safe" line above was computed for the wrong phase.
2. **#318609 is graded: 5.47e-7** (jonah_butterbaugh, 50/50, 0 failures,
   30.3% budget) — only 1.2x better than the hosted MC reference. That is our
   team's live position, and every candidate below beats it.
3. **Local scores understate hosted by ~1.65x** (C1: local budget-matched MC
   1.069e-6 vs the grader's 6.47e-7 reference). Hosted expectations:
   **Kerdock v3 ~9.8e-8 (rank ~13-14)**, L2 ~1.27e-7, L1 ~1.28e-7.
   Kerdock projects to parity with the best honest hosted entry seen
   (oabuod 9.45e-8) on the MSE x C invariant (2.70e4 vs 2.58e4).
4. **Feedback is rich and fast** (~6 min; per-MLP FLOPs, wall, budget %,
   per-layer MSE). The degraded-mode branch in §3 is unnecessary; the
   L1-vs-L2 residual-scale question is directly measurable from two graded
   runs.
5. **Two designation slots per phase** (official facts panel) — the one-vs-two
   conflict is resolved in our favour. Grader memory is 64 GB, so the
   Kerdock memory worry is moot.
6. Upload = drag-and-drop the tar on /submissions/new (<=50 MB). Files staged
   at `%USERPROFILE%\Desktop\whest-submit\` in submit order. The agent is
   permission-blocked from uploading; the user performs it.

### ADDENDUM 3 (post-sweep): the recursion has closed the mechanism space

After the live grading (#326094, 1.83e-7, rank #58) the user mandated a full
hybridization sweep. Result: M180 (design axis — locally optimal, the shared-
rotation mutual-unbiasedness structure is the strength), M181 (closure-as-
smoother — terminal law too non-Gaussian; closure now dead at all four
insertion points), M183 (f32 recast — already clean, 0.00% f64 lanes), M184
(mid-layer exact composition — 0.00%, structural). With N4-N9 that is twelve
consecutive predeclared kills spanning the corpus salvage bank AND every
mechanism mined from the community frontier. **Kerdock v3 is evidence-optimal
within known mechanism space.** New mechanisms can only come from new
external information (band writeups due before Aug 17 are the named settling
check). Phase-1 defaults are safe: the auto-nominated top-2 public are
#326094 + #318609. The writeup (PHASE1_WRITEUP_DRAFT, ID #326094) files by
Aug 17. The wall tier faces dipam's stated DQ standard at private re-eval.

### N9 (final entry): the composition is measured-dead too
The last unbuilt idea — Kerdock frames + the tangent lineage's moment
control + deeper folding — was predeclared and killed at both interaction
gates (commit trail 1cfc0e4 -> this one): the tangent control buys +2.1%
on the frames (CI [-3.0%, +6.2%]; a positive control shows the identical
code buys +34.5% on iid — the frames already absorb the residual), and v3
already IS the L3 fold (its "L1" names a layer-1 WHT memory fold), so the
fold increment is structurally 0%. With N4-N9 all killed at predeclared
gates, the local exhaustion is a measured enumeration, not a judgment call.
Kerdock v3 stands as the honest local optimum of this corpus: structured
frames (2-3.2x over conditioned MC), zero measured final-layer bias, 23%
compute headroom, validator-passed, packaged.
