# The victory post-mortem

**THIS IS A PLANNING FICTION**, written 2026-08-08 as-if dated 2026-09-20, the
day after Phase 2 closed. Its purpose is reverse-oracle planning: narrate the
win, then check which links of the causal chain exist on disk TODAY. Every
load-bearing claim below carries its present-day artifact. A red-team pass
(appended at the end, unedited) attacked each link; what survived became the
action queue. Nothing here is a prediction or a score claim.

---

*2026-09-20 (fictional). We took a Phase-2 money placement with the sampler
lineage and filed the Algorithmic Contribution report with a graded submission
ID. Here is how it actually happened, and how close we came to throwing it
away.*

## What won

Not a new estimator. September had no algorithmic breakthrough in it. What won
was **reconciliation plus grader evidence**: the campaign entered August
holding three frozen, validated, UNSUBMITTED candidates — each with its own
document declaring it "the" champion — and zero graded numbers. The win was
converting entries into information in the right order, then designating on
the grader's numbers instead of ours.

## The causal chain (each link = an artifact that exists today)

**Link 1 — The user came back and logged in.** Everything was gated here; the
agent could not and did not touch credentials. Present-day artifact: the
runbook preconditions in `work/scorefloor_generation/hosted_submission_audit/
REPORT.md` ("Neither archive is ready to transmit without further
user-authorized steps"; whest login is the user's act; PYTHONIOENCODING;
pinned v014 CLI, never the rc5 starter kit).

**Link 2 — Day 1 spent three entries as instruments, not as bets.**
- L1 champion tar (`bc2ec395…8ae36`, verified byte-identical at two paths,
  CHAMPION_20260806.md) — the anchor: its grader C vs local C measures the
  hosted residual clock directly.
- L2 two-axis tar (`68259f64…936a83a4`, two_axis_production/REPORT.md,
  independently recomputed 2026-08-08: ratio 0.990674633, 88/100, fresh-seed
  bootstrap CI [0.98780, 0.99400]) — the paired graded run IS the
  "independently valid predeclared replication" the register (R3) demanded;
  its win survives iff the hosted residual scale k < 1.42
  (PROMOTION_DECISION_L2_20260808.md, row-level).
- Tangent archive (`D2E58DF6…8CF231`, outputs/SUBMISSION-HANDOFF.md) — the
  clever one: at C/B ~ 0.34 its grader-reported multiplier IS the floor
  answer (0.34 -> floor 0.1 regime; 0.5 -> floor 0.5 regime). One entry
  settled the R1 floor conflict that a never-sent organizer email
  (ORGANIZER_CLARIFICATION_DRAFT_20260806.md) had left open for six weeks.
  It also checked #318609's fate on the same login (the July submission,
  aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/submissions/
  318609, last seen "still grading" in _submit_watch.log).

**Link 3 — Designation followed the grader, not the documents.** Three
documents nominated three different champions (register: L1; handoff: tangent;
promotion memo: L2). All three were wrong in the specific sense that none had
grader evidence. The decision rule written BEFORE the grades came in: designate
the best grader-reported adjusted score among candidates with zero failures,
memory inside the hosted cap, and (for L2) k < 1.42 observed. Present-day
artifact: that rule, in this file and T5's dossier.

**Link 4 — The Algorithmic Contribution filing.** The drafted prize PDF
(outputs/WHestBench-Algorithmic-Prize-Report-DRAFT.pdf) needed a graded
submission ID and was written around the tangent estimator — so grading the
tangent archive on day 1 unblocked the filing regardless of which candidate
won the score race. The certified-provider chapter (M178/M179 exactness
certificates + T2's measured non-Gaussianity wall: full-cov closure 9.6e-5 vs
diagonal 7.2e-4 vs sampling 3.1e-7, t2_closure_score_measurement/T2_REPORT.md)
was added as the negative-result spine: *we can now say, with certificates,
how much of the depth-32 estimation problem is fundamentally non-Gaussian.*

**Link 5 — Nothing new was built in September that the grader hadn't already
priced.** The fold3-with-cap mutation (T3) shipped only because its predeclared
gate passed on the known failure history: the salvage map records fold3-39936's
5/100 budget failures at n=100 as the reason 32,256 became champion, so the cap
existed to fix a MEASURED failure mode, not a hypothetical one. When its paired
run cleared L2, it took the second entry slot; when it hadn't, the plan said
L2/L1 and lost nothing. (Present-day artifacts: SALVAGE_MAP_20260806.md row 1;
fold3_n39936_influence_r8_test/official5.json; the fixed-n_base + discarded
budget arg + data-dependent pruning facts pinned 2026-08-08.)

## What nearly lost it (all real, all on disk today)

1. **The native fixation.** A week of August chased a wall-priced native
   kernel toward "#1 = 23.5x" (K1_DISPOSITION) while the live rules — read
   only on 2026-08-08 — had billed native work punitively since the 08-03
   patch (LIVE_RULES_RESET_20260808.md). The leaderboard bar that justified
   the chase was an artifact of the patched exploit. Lesson: re-read the
   authoritative rules BEFORE sizing a lever, every time the organizers ship
   an update.
2. **The withheld better candidate.** L2 beat the champion on 2026-08-06 and
   sat unpromoted behind a 0.0007 gate miss while the campaign optimized other
   things. The gate was correct process; leaving the candidate OFF the graded
   queue for weeks was not. Lesson: "non-promoted survivor" and "not worth a
   graded entry" are different judgments; the second was never actually made.
3. **Three unreconciled champions.** Register, handoff, and memo each declared
   a different final answer; no document ranked them on one basis until T5.
   50 entries/day made the reconciliation nearly free — the scarcity was
   attention, not quota.
4. **The unsent email.** The floor question sat drafted for six weeks. The
   tangent submission answered it as a side effect of an entry we wanted
   anyway. Lesson: prefer probes that are also moves.
5. **Ceilings inherited from unverified carries.** The 8.76e-7 closure oracle
   ceiling — load-bearing for two strategy documents — was refuted 46x by the
   first direct measurement (T2). Lesson: any number that gates a track gets
   measured before the track is funded.

## The mechanism transfer (action items, present tense, 2026-08-08)

- A1. T5 runbook: day-1 grading of L1 + L2 + tangent (3 entries), in that
  order, with the decision rule of Link 3 written down before login. DONE when
  T5 ships.
- A2. The L2 memo carries the register's preconditions verbatim (addendum
  added today) — no designation before grader evidence. DONE.
- A3. T3 is re-scoped to fold3-with-deterministic-cap as a NEW mutation whose
  predeclaration cites the 5/100 failure history as its constraint; its
  cheapest falsifier is a worst-case compute bound, not a score run. QUEUED.
- A4. T4 Kerdock: a NEW predeclared descriptive protocol (the frozen gate
  forbids a retry of the old one), with the recorded argv and the
  Path/PATH env-map bug fixed. QUEUED.
- A5. D-AC: extend the existing tangent-based prize PDF with the
  certified-provider + non-Gaussianity-wall chapter, rather than writing a
  competing paper; the filing needs whichever submission grades first. QUEUED.
- A6. T5 dossier reconciles the three champions on the single basis "grader
  evidence else local paired public-100," and records the one-vs-two
  designation-slot ambiguity as a runbook check (hosted audit says one; the
  live page said two on 2026-08-08 — verify at designation time). QUEUED.

---

## Red-team pass (appended unedited — attacks that landed stay visible)

Twelve attacks, most-severe first (agent a87973e8d2038d706, 2026-08-08):

1. CRITICAL — No verified channel shows the submitter C, the multiplier,
   failure counts, or memory. The audit's grading feedback is only "returned
   submission IDs and initial grading status" + the official UI; register T4
   lists reconciling raw/multiplier/FLOP/runtime as UNRESOLVED. If only one
   adjusted number is visible: k is not extractable, failures are invisible
   (zero-predicted, multiplier 1, averaged in), the tangent floor read is
   impossible. Breaks all three day-1 instruments and the Link-3 rule.
2. CRITICAL — Grading latency: the campaign's only grading datum (#318609,
   July) was still ungraded weeks later. "Day-1 graded numbers" contradicts
   the observed base rate; late-cycle submissions may never grade before
   designation.
3. HIGH — Two cited "present-day artifacts" missing: (a) _submit_watch.log
   not found; (b) no T5 dossier exists — Link 3's rule cites only this
   fiction itself.
4. HIGH — k is not identifiable "directly": the hosted suite is unknown
   (R5/R6), FlopScope 0.10 changed absolute counts, so grader-C-vs-local-C
   measures suite-difference x clock, not the clock.
5. HIGH — The tangent floor instrument fails silently if hosted C/B drifts
   near 0.5: a ~0.5 multiplier is consistent with both floor hypotheses.
6. HIGH — The prize PDF is tangent-specific ("insert exactly that one ID");
   an L1/L2 ID cannot substitute. And the tangent tar appears in NO v0.14
   validate-package record (the hosted audit validated only L1 and M71 v3);
   its lineage is flagged near an rc5-era superseded report — hosted failure
   is live, and then the filing is blocked on a rewrite.
7. HIGH — "Lost nothing" for fold3-with-cap is false under the one-slot
   reading (hosted audit: ONE designated submission gets the private re-run)
   and ignores that its score gate needs an authorized data slice — public
   0..99 is declared overused (R9); the paired run "quietly assumes a gate
   slice that has to be found first."
8. HIGH — The private re-run, not the public grader, decides prizes; a 0.93%
   margin with break-even k*=1.42 is inside the unknowns (R5, E5).
   "Designating on the grader's numbers" swaps one proxy for another.
9. MEDIUM — Calling one graded pair "the replication R3 demanded" is
   evidence inflation: no per-network pairing, no CI, and leaderboard
   rounding may hide a sub-1% difference entirely.
10. MEDIUM — L2's 15.75-MiB memory margin under an unknown hosted cap: one
    OOM kills two of three instruments.
11. MEDIUM — Link 1's timing is load-bearing and unstated: the same chain
    from Sep 10 fails on the calendar with no step individually wrong.
12. LOW — #318609's fate under the pre-patch pipeline settles nothing for
    Phase 2; its only content is the latency warning of attack 2.

Most fantasy-dependent link: **Link 2** — it needs same-day grading, rich
grader feedback, same-suite comparability, and three hosted survivals, none
established anywhere in the corpus.

## Adjudication (what landed, what was refuted, what changed)

- **Refuted: attack 3a.** _submit_watch.log exists at
  C:\Users\strid\projects\whest-starterkit\_submit_watch.log — outside the
  tree the red team searched. Verified twice this session (direct grep: line
  3 "Submitted (submission id 318609)", lines 2667-2669 the still-grading tip
  + URL; independently quoted by the tangent-july fact-pin agent). 3b stands:
  T5 does not exist yet.
- **Landed: attacks 1, 2, 4, 5 (Link 2 rewritten in place below).** The
  day-1 batch survives as a LATENCY move, not an information-harvest: submit
  the three archives early BECAUSE grading is slow and the deadline is fixed.
  What each entry teaches depends on feedback richness, which is UNKNOWN
  until the user's first login — so the runbook gains a feedback-audit step
  (what does the UI actually show per submission?) with a degraded-mode
  branch: if only adjusted scores are visible, (i) the L2-vs-L1 comparison
  remains valid as a same-hidden-suite paired read (both graded on the same
  networks — attack 4's suite objection cancels in the pairwise comparison),
  (ii) k and the floor are unrecoverable from feedback, and the floor probe
  is informative only if the tangent's visible adjusted score is far from
  both floor-hypothesis predictions.
- **Landed: attack 6, converted to an immediate action.** A7 (new): run
  `whest validate-package --json` with the pinned v014 CLI against the
  tangent tar LOCALLY, TODAY — response-free, no upload, closes the
  biggest filing risk before the user returns. If it fails, D-AC's plan
  changes from "extend the tangent PDF" to "rewrite around a graded sampler
  ID," and that is better known now than on deadline week.
- **Landed: attacks 7, 8, 9.** T3 demoted below D-AC (its gate needs the
  R8-reserved 600..799 read or grader evidence — both expensive); the
  designation rule now says "best available proxy, private re-run decides,
  margins under 1% are not settled by two rounded scalars"; R3-replication
  language downgraded to "the closest available approximation of the
  replication R3 demanded, valid only if per-submission detail is visible."
- **Landed: attacks 10, 11.** Runbook: L1 first, alone, as the canary (its
  memory and lineage are safest), then L2 + tangent after L1 confirms the
  pipeline; every runbook step dated relative to Sep 19 with a latest-safe
  date of Sep 12 for first submissions (attack 2's latency + 1 week margin).

Action items A1-A6 are superseded where they conflict with this adjudication;
A7 added. The fiction above is retained UNEDITED as written before the red
team — the gap between it and this adjudication is the measurement.

**A7 EXECUTED (2026-08-08, minutes after the red-team pass):**
`whest validate-package --json` (pinned v0.14 CLI, PYTHONIOENCODING=utf-8,
local, no upload) on outputs/WHestBench-Phase-II-tangent-candidate.tar.gz
returned `{"ok": true, "issues": [], "whestbench_version": "0.14.0"}`.
Attack 6's package-layer failure scenario is refuted at the observed level;
all three day-1 archives (L1, M71 v3 previously; tangent now) hold v0.14
validate-package passes. Hosted execution risk (memory/wall/tails) remains
open — the package/contract layer is green.
