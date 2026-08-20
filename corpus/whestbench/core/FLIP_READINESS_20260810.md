# Flip readiness audit — v3.1 GUARDS vs the updated rules (2026-08-10, pre-flip)

Owner-directed audit run while codex-sol is out of usage. Sources, all read
this session: the AIcrowd update email (Gmail thread 19fcb021d19e8278, sent
2026-08-04), discourse post 18125 ("Phase 1 update: flopscope v0.10.0 cost
model fixes, residual time safeguards, and updated deadlines"), draft PR #1
metadata (gh JSON), a fresh Get-FileHash of the staged tar, and the committed
SUBMIT_READINESS_20260808 / SUBMISSION_DOSSIER_20260808 docs. No submission
was made; nothing was merged.

## Deadlines (from the email)

- Phase 1 close: **2026-08-10 23:59 UTC** (extended — TONIGHT).
- Algorithmic Contribution writeup: 2026-08-17 23:59 UTC (v7 ready, 2399fee).
- Registration + team freeze: 2026-09-05 23:59 UTC.
- Nomination deadline: NOT yet announced — "We will email each team with
  instructions for nominating submissions." Settling check: inbox watch (U19).

## The rule that rewrites the strategy

Prize ranking is EXCLUSIVELY the private re-evaluation, on a freshly generated
suite with private seeds unused in either phase. Each team nominates up to two
**Phase 1** submissions ("up to two submissions for the Phase 1 private
re-evaluation"); default if none nominated = the team's two highest-ranked on
the Phase 1 PUBLIC leaderboard.

Consequences:
1. The nomination pool FREEZES at tonight's close. Phase-2 submissions earn
   no prize eligibility.
2. Door A (fold3cap) is overtaken: it has no Phase-1 entry, needs Sol's U2
   fix + a graded canary, and cannot get either before the freeze. Its value
   is now writeup/Phase-2 evidence only.
3. Door B (decorrelated duplicate) is overtaken identically (plus U1 was
   never answered).
4. The auto-top-2 DEFAULT is a hazard, not a convenience: if the pre-patch
   #318609 (July tangent lineage; lockbox raw 9.911e-7) is ranked on the
   Phase-1 board, silence would pull it into the private re-run.

## Compatibility: v3.1 GUARDS vs flopscope v0.10.0 / whestbench v0.14.0

Verdict: **NO BLOCKERS**, on two independent signals.

- Signal 1 (hosted): #326094 was submitted 2026-08-08 — four days AFTER the
  evaluator update — and graded clean: adjusted 1.832e-7, 50/50 nets, 0
  failures, C/B 0.650. Dtype pricing (64-bit = 2x 32-bit), data-movement
  billing (copy/fill/concat 1/elem, gather/sort 4/elem), the einsum out=
  casting change, the 1-physical-core participant pin, and lambda=1e11
  residual accounting are all already priced into that grade.
- Signal 2 (local): the dossier's candidate table is computed on the pinned
  whestbench 0.14.0 / flopscope 0.10.0 basis, B=272e9; mean C 178.5e9 agrees
  with the hosted C/B 0.650. SUBMIT_READINESS surveyed the installed
  flopscope 0.10.0 API directly.
- Wall safety under the 1-core pin: worst net 4.11 s vs the 60 s cap (14.6x);
  the dominant term is flopscope backend time, which the grader gives 7
  cores. Residual max 0.137 s = 5.0% of budget, inside the scored C.
- Staged artifact: Get-FileHash (this session) = SHA256 8382E269C9B32E0935
  492734DDF8182560120F7E9331621AA18839D5D1F4EA06, matching the frozen
  manifest and PR record; 33,347,024 bytes; passed the pinned G0-G3 GUARDS
  harness (hostile-parent reproduction, exact bills, in-budget finite
  children, exact tar members). Status: UNGRADED guarded rebuild of the
  graded #326094 estimator + M186/M187 crash guards.
- Foregone-optimization note (not a blocker): dtype pricing post-dates some
  cost-family kills (e.g. M183 f32 recast measured 0.00%). Kills stand per
  discipline; C/B 0.650 is on-budget with headroom, so nothing is owed.

## PR #1 (gmrmk/recursive-estimator-folding)

OPEN, DRAFT, MERGEABLE, no review; head agent/compression-survivor-corpus ->
main; +71,636/-39 across 100+ files. It is the Gen-5/6 corpus + handoff
consolidation, not a submission vehicle. Repo visibility: PRIVATE (no method
leakage before the writeup). Correctly left unmerged.

## Go/no-go checklist (Jonah, tonight, in order)

1. GO-gates already verified this session: tar hash matches; artifact
   harness-passed under the pinned versions; #326094 graded clean under the
   new rules; wall/residual margins hold.
2. THE ONE DECISION (before 23:59 UTC): submit the hardened GUARDS tar as a
   second Phase-1 entry, or hold. Tonight is the only chance to create a
   second nomination-eligible entry. Grading may land after the close;
   explicit nomination is by submission, not by grade timing.
3. If submitting, the day-of P-gates: only work\whest-v014\Scripts\whest.exe
   (never the starter-kit v0.12.0rc5 CLI); $env:PYTHONIOENCODING='utf-8';
   NO --dry-run on the sealed tar; re-run Get-FileHash + validate-package
   --json + tar -tzf member count same-day; Jonah personally runs whest
   login; blind .env key pattern only — the key is never read or displayed.
4. After the close: confirm auto-top-2 standing and #318609's board status.
5. When the nomination-instructions email arrives: nominate EXPLICITLY.
6. File writeup v7 by Aug 17 against ID #326094.

## The two safest nominations

- Slot 1 — **#326094**, non-negotiable: graded under the current evaluators,
  on-budget, zero measured bias, no fitted component — constructed to
  survive a fresh-seed re-run.
- Slot 2 — **the hardened GUARDS twin IF it is submitted tonight** (same
  estimator + grade-time crash guards; per U9 a clone adds ~no tail
  probability, so its value is insurance against a grade-time failure).
  If no submission tonight: **nominate #326094 alone, explicitly** — never
  the default.
