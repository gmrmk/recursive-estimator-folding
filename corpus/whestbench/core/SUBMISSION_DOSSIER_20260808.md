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
