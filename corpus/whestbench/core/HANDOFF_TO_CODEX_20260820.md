# HANDOFF TO CODEX — campaign state at 2026-08-20, written under the post-audit rules

Status: VERIFIED — APPROVED-FOR-HANDOFF (hostile verifier pass of 2026-08-20: every
receipt opened against its cited artifact; verdict and fix log in Section 12).
Author: the Fable-5 orchestrator. Register: plain
and neutral. Epistemic contract: **[O-self]** = the orchestrator personally executed
or read it in the 2026-08-19/20 session; **[O-agent]** = an agent observed it and the
artifact is on disk at the cited path; **[D]** = derived, derivation at the citation;
**[R]** = reported, not independently re-derived; **[GAP]** = known hole with its
check named. Every load-bearing number carries a file citation. Where a citation is
to AGENT_CHANNEL.md, the line number is from HEAD at commit 6148a8d.

## 0. READ THIS FIRST — the confabulation register governs everything below

On 2026-08-19 the owner challenged the orchestrator's reliability. A six-agent audit
graded 1,306 orchestrator-authored claims against disk
(`corpus/whestbench/audit_self/CONFABULATION_AUDIT_20260819.md`, commit 031a065;
F7 regraded at commit 6148a8d). Result [O-agent, grade counts re-read first-person]:
77.5% extracted-verbatim, 13.0% ambiguous, **22 distinct false facts** after the F7
regrade. The failure gradient: relayed agent numbers ~0% false; channel record 0.5%;
user-facing retellings 7.2%; durable self-authored state (prompt constants, memory,
diary) 13.3%. Fourteen of sixteen measured mutations strengthened, tidied, or added
urgency. All seven prompt-layer defect rows — six confabulations plus F7, reclassified
by the regrade to an R3 verbatim-label violation — wore authority markers ("certified",
"measured", "[O]", "verbatim") that exempted them from agent fact-checking.

CONSEQUENCES FOR YOU: (1) do not trust any number in a 2026-08-19 channel entry
without checking it against the register's Section 2 — the known-false facts include
the "50.3% oracle-of-8" (true committed value 0.6160089092709584,
`experiments/gm_p2b_proxy/results.json`), the "25.7%/23.5% proxy-guided gains" (no
such gains exist; p2b verdict is "unharvestable with known proxies"), the label "F7"
for rotation-selection (true ledger ids: idx 204 `gen3_p2_rotation_selection`, idx
245 `gm_p2b_proxy`), the phantom "rules email due Aug 19" deadline, and an inverted
leaderboard chronology (#58 is the Aug-8 grading rank, #64 the Aug-10 board, #66 the
Aug-19 live board). (2) `ULTRAMATH_SLATE_20260819.md` entries pricing the
rotation-selection family are GATED (register rule R10): re-derive against the 61.6%
oracle and the p2b unharvestable verdict before funding anything from them. (3) The
ten prescriptions R1-R10 in the register's Section 8 bind all future authored text —
numbers carry receipts, no label without a corpus grep, authority markers only on
copy-pasted text, self-echo is not corroboration, board reads are copied not
paraphrased.

## 1. Competition ground truth [O-agent: 13:06:41Z browser render, channel-recorded; re-read first-person by the orchestrator (get_page_text) 2026-08-19T23:42:36Z]

Source: https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026
(leaderboards page, rendered live; recorded in channel entry
"LIVE BOARD + PHASE-2 TIMING INTEL" and re-read directly by the orchestrator later
the same day).

- Our submission: handle `jonah_butterbaugh`, **rank #66**, adjusted 1.83e-7,
  final-layer MSE 2.82e-7, 3.8x vs sampling, 5 entries, last submission Aug 8 14:41.
  Unchanged since Aug 8; the slide from the Aug-8 grading rank #58 is other teams
  passing it.
- Front: #1 ednacob 1.84e-8 (suspected anomalous, unmoved); #2 J2W/joe_wanza 5.39e-8;
  #3 dstepanov 6.22e-8; #4 dpskv5 7.17e-8; #5 oabuod 7.23e-8. Puffi is **#12** at
  9.09e-8. 756 participants (the 13:06:41Z render said 752, the 23:42:36Z first-person
  re-read said 756 — the public count grew during the day; R9 provenance), 18,469
  submissions, 312 scored entries.
- **Phase 2 has NOT opened.** Official page: "expected Aug 20 23:59 UTC — tentative";
  Phase-2 close moved Sep 19 -> Oct 16 (struck-through dates on the official
  timeline); the Phase-1 private re-evaluation is RUNNING now. No Phase-2 rules text
  exists anywhere on disk. Highest forum topic seen: 18188.
- Slots #326094 and #327519 locked [R: campaign record; not re-verified this session].

## 2. Owner rulings of 2026-08-19 (all via AskUserQuestion, recorded in channel)

1. **Memory ceiling = 1 GiB** (channel 2026-08-19T06:12:13Z + gate addendum in
   `experiments/fold_floor_splice/FOLD_FLOOR_SPLICE_PRODUCTION_GATE.md`). Basis: the
   contest advertises 64 GB and no memory ceiling; the only mechanically enforced
   limit is 65,536 MiB (`core/MEMORY_TIERS_20260819.md`, site-packages lines read
   first-hand by the Wave-0 agent [O-agent]). NOTE: 1 GiB is an OWNER ruling, not
   contest law — the orchestrator's own phrase "the competition's real 1 GiB ceiling"
   is register item F18, false.
2. **Fold lineage HALTED** (re-plan ruling under the three-red-loops law). Round 4
   retired gate-green: verifier verdict APPROVED_PENDING_CEILING with D-A6 discharged
   by ruling 1 and D-M1 administrative (manifest re-freeze only if an archive is cut)
   [O-agent: tasks output wmxechtry; channel "THREE OWNER RULINGS + TRIPLE HARVEST"].
   M1 (the fold Public100) is CANCELLED; pre-registration P1 = WITHDRAWN BY
   GOVERNANCE BEFORE MEASUREMENT — never run, never falsified (manuscript section 13).
3. **129 cell: repair + run** — executed same day (Section 4).
4. **Rules default**: nothing arrived; the designation is filed against the stated
   Phase-1 default with `core/designation_repricing.py` as the hour-of-posting
   response.

## 3. Lineage and designation state

- Deployed graded champion pair: Kerdock v3 (submission #326094,
  `1_kerdock_v3_BEST.tar.gz`, hosted adjusted 1.832e-7 — `SUBMISSION_RESULT_20260808.md`)
  and its GUARDS-hardened twin v3.1 (submission #327519, graded 1.8320996e-7, raw
  BIT-IDENTICAL to #326094's, delta 0.017% residual-seconds jitter — channel 2026-08-10
  15:0x). Local values [R: DESIGNATION_POLICY_20260819.md v3 annex, verified by
  the Wave-0 hostile verifier, commit d77b855]: kerdock_v3 local adjusted
  1.6190837992231567e-7 (ledger id `t4_kerdock_v3_descriptive_rescore`); v3.1's own
  value 1.6190840245440637e-7 as the annex's linear form prints it (the register's
  float64 route prints ...636e-7, the annex's exact recompute ...643e-7 — a one-ULP
  print divergence, all equal at 1.619084e-7; delta +24,575 FLOPs, relative 1.4e-7,
  annex L1041-1049). v3.1 is the
  slot-1 designation candidate (annex v3.0-v3.9); guard-fire counts are predeclared
  first-class canary outputs of any graded run.
- Incumbent row_blocked_production: local 2.121762464e-7 (ledger id
  `row_blocked_winograd_production`). Carrier: Haar frames by QR (four independent
  in-source confirmations; see `core/SECTION_ESTIMATOR_AND_CONSTANTS_ROW_BLOCKED_20260819.md`
  — six fitted scalars, five if the theorem-fixed lambda->1 substitution is ever
  adopted, NOT the kerdock disclosure's seven).
- **OPEN CAVEAT — the untouched-split gate did not reproduce** [O-self: read directly
  in `core/CLOSING_RUNS_20260819.md`]: on rows 100-131 (n=32, no development ever
  touched them) the v3.1/incumbent ratio landed ABOVE one on all three channels,
  against the recorded 0.7631. The report's own framing: "the recorded 0.7631 does
  not transfer", not "the incumbent is better" — n=32 under this problem's per-net
  dispersion. Adjudication is in the closing-wave merge (running at handoff time).
  Until settled, the designation must not ship v3.1 as an unqualified slot-1.
- Fold ledger: 277 candidates [O-self: parsed]. #277 is the 129 cell (status
  "screened"). The B-prime closure (Section 6) produced no ledger record — it is a
  derivation kill recorded in channel + `experiments/bprime_rephase/SYMMETRY_GATE.md`.

## 4. The 129 cell — the campaign's one fresh measurement (ledger #277, sealed)

Artifacts: `cells/frame_completion_129_three_arm_regime_decomposition_v1/`
(predeclaration, consumed token, report.json, verdict.json),
`experiments/frame_completion_129/report_arm{A,B,C}.json`. Channel: "129 JUDGE
DISPOSITION" 2026-08-19T09:53:09Z, commit 5da4cdc. All numbers below [R: verdict.json
+ report.json; independently re-derived to absdiff 0.0 by the judge and again by the
v1.3 manuscript auditor].

- Mechanical verdict PASS: gated metric `frame_completion_129_margin_t` =
  -4.705301350825718 vs pass_when_lte -1.9842169515086827. Gated FLOP-only score
  ratio A->B = 0.68165697632704, CI95 [0.5950, 0.7836]; raw MSE ratio
  0.6661955563966138 — BELOW the amended band's lower edge 0.78 (direction confirmed
  beyond predicted magnitude; falsifier 0.95 not fired).
- Judged disposition **INSTRUMENT-SUSPECT — the PASS is not honoured**: achieved
  se_log 0.07054498655771349 outside the pre-registered honour window [0.019, 0.03].
  LATER RE-READ (manuscript v1.4 section 13 addendum): the window itself was
  mis-calibrated — at n=5 the pilot's variance estimate has rel-sd exactly sqrt(1/2)
  under normality, so the window was unearnable before the run; the miss is a rung-2
  calibration error, not evidence of heavy tails. The disposition stands as
  pre-registered; its cause is re-diagnosed.
- **The H2 reversal — the cell's main scientific content**: the design-quality leg
  (Haar->Kerdock at identical 126 frames) carries 103.66% of the log gain (score
  ratio 0.6598, CI [0.5756, 0.7596]); the completion leg (126->129) is a small net
  LOSS (1.0332, CI [0.9807, 1.0885] straddling unity). What pays is leaving the Haar
  family, not completing to 129. Log-additivity residual 6.2e-17.
- Custody: burned Public100 rows 0-99; descriptive only; designates nothing.
- Residual anomaly: the cell's 5-net smoke (seed 424242) had the OPPOSITE sign
  (raw B/A 1.0387). The closing runs reproduced the smoke to every printed digit
  [O-agent: CLOSING_RUNS_20260819.md] — it is a real property of that seed's draw,
  unresolved, a candidate future cell.

## 5. The exact theory (all [D], exact rational arithmetic, scripts committed)

- **Dyadic-tax law** (`core/ULTRAMATH_SLATE_20260819.md`; manuscript section 11b;
  verified in-cell by the 129 runner's own fail-closed assertions):
  A_l,mub(k)/A_l,haar(k) = 1 + (k-1)·X_l/S_l with X_4/S_4 = -1/128 and
  X_6/S_6 = +1/4096 exactly. Corollaries: A_4,mub(129) = 0 identically; the 42.67x
  carrier ratio is exactly 128/3; the Kerdock family is 3.0518% WORSE than Haar at
  degree 6 (4221/4096 at k=126; 33/32 at k=129); slope ratio exactly 32.
  Verification you can run [O-self: the orchestrator ran it]:
  `python -B corpus/whestbench/papers/a4_ratio_settling_check.py` prints
  "ratio exact = 128/3 ... IDENTICAL to 128/3: True ... A4_mub(129) = 0.000000000e+00".
- **Carrier optimality**: MUB is the unique degree-4 minimizer over unions of
  orthonormal bases (Jensen/Cauchy-Schwarz). IMPORTANT DISAGREEMENT ON RECORD: the
  slate's adjudicated form is UNCONDITIONAL (Lane 2's theorem, no energy-ratio
  hypothesis); the E6/E4 < 19.71 conditional form quoted in some channel entries was
  retired by the slate itself. Manuscript 11b records the disagreement.
- **Delsarte floor**: degree-6 exactness needs >= 2,861,696 directions (~88.7x out
  of budget); the 129-completion is a near-tight antipodal 4-design. A
  slate-vs-channel denominator-convention discrepancy (2,861,952 / ~44x) is recorded
  in manuscript 11b; no conclusion depends on it.
- **R_6 identity**: R_6(k) = (k/126)·A_6,mub(k)/A_6,mub(126) = (4095+k)/4221; the
  dual-witness certificate's 1408/1407 worst-case margin IS R_6(129). CREDIT: the
  1408/1407 value was already stored in `papers/dual_witness_certificate.json`
  (game.worst_case_margin); the NEW part is only the identification with the
  degree-6 design defect (manuscript section 8, marked correction).
- **Kink-tail transport** (`cells/deg_ladder_own_axis_capture_v2/report.json`,
  sealed, exact): lambda_n closed form; the measured readout profile matches
  lambda_n^2 to 3-17% across degrees 8-24 (3.1-16.3% on the gated rungs, 17.3%
  including the ungated one; the degree-48 read sits below the cell's own 3-sigma
  resolvability floor) where the mean-field arccos spectrum misses by +65% to +620%.

## 6. The excess-gain resolution and the doors that closed (2026-08-19/20)

Chain of artifacts, in commit order (verified against `git log --reverse`):
`core/CENTRAL_MOMENT_LADDER_20260819.md` (79aae74) ->
`core/EXCESS_GAIN_MOMENTS_{THEORY,DATA,SYNTHESIS}_20260819.md` (b48efaa) ->
`core/S7_RESCUE_PROBE_20260819.md` (286f5b4) ->
`core/DEG4_ENERGY_SHARE_TRACE_20260819.md` (f4780c6) -> manuscript v1.4 (e744b36).

- The 129 forecast miss (measured 0.6662/0.6564 vs forecast 0.8212/0.8445) is a
  FIRST-MOMENT, ARM-A-LOCATED error: 99.4% of the A->C log gap is arm A
  underperforming the defect-share forecast; the forecast was right about both
  structured arms. Tail-deletion REFUTED (all arms share the per-net rotation; k=1;
  mean-preserving). Cross-degree covariance is EXACTLY ZERO in expectation (Schur).
- Mechanism II (pilot/rescue detection lever) KILLED four independent ways (S7: the
  B-vs-C control reproduces 86% of the effect; the lever measures 0.9994x; Parseval;
  per-net rotation + ReLU-before-rescue code reads).
- Mechanism I narrowed: the committed 0.45% deg-4 share (single producer: the
  infinite-width mean-field arccos kernel) is measurement-falsified in shape;
  replacing only the deg4:deg6 ratio with the exact kink-tail value (3.3471 vs
  1.4100) gives share4 = 1.061%, closing 96.1% of the A->B gap and 77.3% of A->C.
  Honest residue: the full kink profile is NOT a drop-in (hybrid labelled); the
  C->B structural short (>= 3.84% non-quadrature term, p~0.12) is untouched; three
  net families [GAP].
- **B-prime re-phase lever CLOSED BY DERIVATION at zero run cost**
  (`experiments/bprime_rephase/SYMMETRY_GATE.md`, judge-confirmed, 494d918): the
  re-phase family is exactly rotation+row-signs; the carrier enters the estimator at
  one line (fold3_estimator.predict, first_pre = z @ (R.T @ W0)); Haar
  right-invariance + antipodal row-sign inertness make B' identical to B in the
  JOINT distribution of everything. Independent power kill: n >= 651-902 for a
  2-sigma read even if the symmetry failed.
- **Kerdock depth-2 schedule door CLOSED** (final, no successor pass:
  `core/KERDOCK_SCHEDULE_STATIC_GATES_20260819.md` sections 8-11, commit a6481ab):
  four adversarial passes; G-A eligibility confirmed by a 140/140 hand re-derivation;
  G-B fires in the baseline-matched deployment frame at both measured per-dispatch
  laws on 5/5 seeds (mean dL1 = 8,269,535,869 vs boundary 12,422,199,973). Reopening
  conditions quantified in Section 11.
- NET: **no score lever remains in the verified stack.** The one unconfirmed
  candidate (B-prime) died by theorem; everything else was measured to its end.

## 7. The instrument doctrine (binding on future cells)

- **The rung-2k law** (manuscript section 13d; `core/CENTRAL_MOMENT_LADDER_20260819.md`):
  an estimator of a k-th-moment quantity has sampling error governed by moments up to
  mu_2k. Prescription: predeclare the rung-2k estimate, or gate on L-moments, or file
  descriptive-only — else INSTRUMENT-SUSPECT on filing. All three recorded
  instrument failures are instances.
- The sealed-but-unrun `deg6_own_axis_zonal_capture_v1` cell is PRE-RUN
  SELF-REFUTED on its resolution premise (its own kurtosis ~2e4 implies ~39% rel-sd
  at production, ~15x short of a 10% instrument; manuscript erratum P2-E2). Do not
  run it as sealed.
- Lawfulness results for the disclosure (row_blocked addendum, e744b36):
  moment_tangent_lambda -> 1 is theorem-fixed (zero-bias control; fitted surface
  six -> five scalars IF adopted); the radial branch's constants are theorem-fixed
  exact rationals (two independent routes); the k-statistic construction is
  CLOSED-BY-DERIVATION.

## 8. The filing package (state at handoff)

- `core/PHASE2_CONTRIBUTION_DRAFT_20260819.md` — v1.4, hostile-audited (e744b36):
  sections 0-15 with 13c (excess-gain resolution), 13d (rung-2k law), 14b (erratum
  register incl. the five-document "11%/40%" object-mismatch, P2-E1). ~39,600 words.
- `core/PHASE2_CONTRIBUTION_SHORT_20260819.md` — the judge-facing short form
  [O-self: opening read first-person — one-paragraph contribution, "Nothing here
  claims a score" in the opening, every number pinned to a long-form section].
  UNCOMMITTED at handoff-write time; the closing-wave merge commits it.
- Designation: `core/DESIGNATION_POLICY_20260819.md` (v1 + v2 + v3 annex),
  `core/designation_repricing.py`, `core/LOCAL_VS_HOSTED_DIVERGENCE_MAP_20260819.md`
  (R=1.65 retired; planning default R=1.0, conservative anchor 0.884),
  `core/SECTION_ESTIMATOR_AND_CONSTANTS_ROW_BLOCKED_20260819.md` + addendum,
  `core/verify_row_blocked_disclosure.py` (74/74).
- IN FLIGHT at handoff: the closing-wave merge (wf_e39c7e97-ae1) — three audit
  lenses (rival, referee, statistician) + merge; it adjudicates the untouched-split
  anomaly and declares filing-ready. Its verdict supersedes this section's state.

## 9. Environment and protocol facts you will need

- Frozen venv: `C:\Users\strid\.venvs\whestbench-frozen-m178` (python 3.14.4,
  numpy 2.4.6, flopscope 0.10.0, whestbench 0.14.0). NOTE: an earlier task doc
  cited a wrong path under the repo; this is the real one [O-agent, corrected in
  round-3; whest.exe runs, verified O-self].
- Dataset: `Documents/Codex/2026-08-02/.../work/whest-full` — 7.9 GB HuggingFace
  arrow shards, sha256 5b00938b6bd809fe80acef08772c5654edf467863225ca9e304b76c779ecf433
  [O-self: existence + size; sha [R] from run configs].
- ALWAYS `python -B` / PYTHONDONTWRITEBYTECODE=1 (an external process was caught
  writing .pyc into custody trees; `verify_fold_floor.py` hard-fails on strays;
  296 pre-existing gitignored .pyc exist tree-wide — do not read "zero bytecode"
  claims as repo-wide).
- The shared scratchpad had a stdlib-shadowing `numbers.py` (renamed
  `winograd_decode_search_renamed_was_numbers.py`) — it broke numpy imports for two
  agents; run from clean dirs (`python -P`).
- Harness: `scripts/fold_search.py --cells corpus/whestbench/cells --ledger
  corpus/whestbench/headroom/fold_ledger.json`; predeclare -> run -> verdict; the
  seal IS the GATE_TOKEN; verdicts are one-shot; seed-agreement and numeric-scan
  kills are live. Method-A measurements: single-thread env vars, A-B-A incumbent
  re-measure recommended (`core/DESIGNATION_POLICY_20260819.md` L660 + the
  incumbent_measured_twice clause at L865; the m-band spread itself is in manuscript
  section 10 — committed-evidence band [1.86, 2.26], carried union [1.86, 2.64],
  register item F8 gates any "certified" reading of it).
- Timing measurements on this host have a documented ~14% incumbent spread across
  runs (`DESIGNATION_POLICY_20260819.md` L660); never quote an m or residual without
  its environment witness.

## 10. Open queue (owner-fundable, none urgent)

1. Closing-wave merge verdict (in flight) -> untouched-split adjudication; if the
   anomaly survives, a larger untouched-split read (n >= 100 rows 100-231) settles it.
2. Phase-2 rules (expected Aug 20 23:59 UTC, tentative) -> `designation_repricing.py`
   against the real text; file designation + contribution.
3. The smoke sign-flip cell (seed-424242 two-anomaly draw, joint ~1e-4).
4. X5 k=1 hostile-residual re-instrumentation (record 255's judge protocol; needs a
   quiet machine, owner-scheduled).
5. R6 memory repairs: DONE for `project_whestbench_folding.md` (2026-08-20);
   mempalace diary inheritance line still owed.
6. The deg-4 rung dual-carrier read + lambda-sweep: check
   `core/DEG4_ENERGY_SHARE_TRACE_20260819.md` addendum (closing wave wrote it;
   uncommitted at handoff-write time).

## 11. Commit chain of record (2026-08-19/20, branch agent/compression-survivor-corpus)

89d44cb (128/3 theorem) -> 21d64c2 (owner 1-GiB ruling + round-3 fixes) -> ecabc23
(ultrareview merge harvest) -> 0a2f179 (owner rulings: halt/129/default) -> e776252
(manuscript v1.2) -> 7239ee2 (MI-solve) -> 5da4cdc (129 judged) -> d77b855/b240709
(Wave 0 + bytecode correction) -> 5ba559d (manuscript v1.3) -> 94ff30b (W1.1/W1.2
verification rejected, G-A confirmed) -> ac2e230 (G-B settlement rejected) -> a6481ab
(settling check approved; door CLOSED final) -> 41a7ecf (live board + Phase-2 timing)
-> 79aae74 (central-moment ladder) -> b48efaa (excess-gain trio) -> 286f5b4 (S7
rescue probe) -> f4780c6 (deg-4 trace) -> 494d918 (B-prime closed) -> e744b36
(manuscript v1.4) -> 031a065 (confabulation audit) -> 6148a8d (F7 regrade).
Journal-only commits (e2f29ea, a0cdc48, 86bdbe7, 337e7ef, d4ce506) omitted. Order
verified against `git log --reverse` by the hostile verifier pass. All pushed;
ls-remote == local verified repeatedly [O-self].

## 12. VERIFIER VERDICT — APPROVED-FOR-HANDOFF (hostile verifier pass, 2026-08-20)

VERDICT: **APPROVED-FOR-HANDOFF**, after ten in-place fixes. Method: every receipt
opened against its cited artifact (files, JSON re-parses under `python -B -P`, greps);
Section 0 re-read line-against-line with the register; every [O-self] tag checked
against the session transcript (tool calls with timestamps); the commit chain checked
against `git log --reverse`; both runnable checks re-run fresh this pass
(`papers/a4_ratio_settling_check.py` reproduces every quoted print;
`core/verify_row_blocked_disclosure.py` returns 74/74). Zero compute; fenced trees
read-only.

FIXES (defect -> fix, one line each):
1. §0 pointed R1-R10 at "the register's Section 5"; the prescriptions are the
   register's Section 8. Fixed.
2. §0 "all seven prompt-layer confabulations" was stale after the F7 regrade (F7 is
   now an R3 violation, not a confabulation); restated as six + F7, all seven rows
   marker-wearing. Fixed.
3. §1 said 756 participants while citing a channel entry that says 752; both reads
   are real (13:06:41Z agent render 752; 23:42:36Z first-person get_page_text 756) —
   provenance annotated per R9 and the section tag rewritten to name both reads
   (the original tag claimed the first read as first-person; it was the agent's). Fixed.
4. §3 called #326094 "Kerdock v3.1 GUARDS"; #326094 is Kerdock v3
   (`SUBMISSION_RESULT_20260808.md`); the GUARDS twin is #327519, graded 1.8320996e-7,
   raw bit-identical (channel 2026-08-10 15:0x). Restated as the champion pair. Fixed.
5. §3 v3.1 value ...637e-7 matches its cited annex print (DESIGNATION_POLICY L1043)
   but the register's F12 prints the float64 sum ...636e-7 (verified: the float64 sum
   IS ...636e-7) and the annex's exact recompute is ...643e-7 — the one-ULP print
   divergence is now annotated so the handoff and register cannot be read as
   contradicting. Fixed (annotation; the cited print kept).
6. §3 "five fitted scalars" strengthened the cited doc's count; SECTION_ESTIMATOR
   L242/L398 says six, five only IF the theorem-fixed lambda->1 substitution is
   adopted. Fixed.
7. §5 kink-tail "at degrees 8-48" overextended the validated range; the manuscript's
   own wording is 3.1-16.3% on the gated rungs, 17.3% including the ungated one
   (degrees 8-24), and the degree-48 read sits below the cell's 3-sigma resolvability
   floor (rho_own 1.9e-05 vs floor 8.9e-05, report.json). Fixed.
8. §6's "chain of artifacts, in order" was not the commit order — the central-moment
   ladder (79aae74) committed FIRST of the five, not fourth. Reordered from git. Fixed.
9. §9 pointed the A-B-A/m-band receipts at "the fold gate doc", which has no m-band
   section; the 14% spread + A-B-A clause are DESIGNATION_POLICY L660/L865 and the
   m-band is manuscript section 10. Re-pointed; the ~14% figure itself is confirmed
   documented. Fixed.
10. §11's commit chain carried five ordering inversions (5ba559d placed before
    7239ee2; Wave 0 before 5da4cdc; 41a7ecf before 94ff30b; f4780c6 before
    79aae74/b48efaa; e744b36 before 494d918) and omitted 286f5b4 — the register's
    "tidied chronology" failure mode, reproduced inside the document written to warn
    about it. Rewritten from `git log --reverse`. Fixed.

SPOT-CHECKS THAT HELD (selection, all fresh this pass): oracle
0.6160089092709584 verbatim in `experiments/gm_p2b_proxy/results.json`; p2b
"unharvestable" verdict at `pb1_premise_battery/p2b_results.json` L28; ledger idx 204
= `gen3_p2_rotation_selection`, idx 245 = `gm_p2b_proxy`, 277 candidates with #277 =
the 129 cell, status "screened"; row_blocked 2.121762464e-7 and kerdock_v3
1.6190837992231567e-7 in their ledger records; the six-agent audit is literally six
agents (six agent transcripts under workflow wf_13e62509-334); the 296 .pyc count
reproduces EXACTLY today; all quoted 129 numbers verbatim in report/verdict/channel
(margin_t -4.705301350825718, ratio 0.68165697632704, CI [0.5950, 0.7836], raw
0.6661955563966138, se_log 0.07054498655771349, window [0.019, 0.03], legs
0.6598/1.0332, residual 6.2e-17); CLOSING_RUNS quotes verbatim (rows 100-131 above
one on all three channels, "the recorded 0.7631 does not transfer", smoke 1.0387
reproduced digit-exact, joint ~1e-4); "Nothing here claims a score" in the SHORT
opening; 1408/1407 = `game.worst_case_margin` in `dual_witness_certificate.json`;
the sqrt(1/2) honour-window law and the P1-WITHDRAWN rows both in manuscript §13;
P2-E1 five-document mismatch and the Delsarte two-convention discrepancy recorded;
S7 86% / 0.9994x / Parseval; DEG4 3.3471 / 1.4100 / 1.061% / 96.1% / 77.3% /
>=3.84% / p~0.12 / three net families / addendum present; symmetry gate first_pre
line + n >= 651-902; KERDOCK gates 140/140, 5/5 on both laws, 8,269,535,869 vs
12,422,199,973, sections 8-11 with §11.9 final APPROVED; venv python 3.14.4 / numpy
2.4.6 / flopscope 0.10.0 / whestbench 0.14.0 + whest.exe present; dataset present at
7.92 GiB; slots locked to #326094 + #327519 (channel L2847); `tasks/wmxechtry.output`
on disk; closing wave wf_e39c7e97-ae1 exists with rival/referee/statistician lenses;
memory repairs dated 2026-08-20 present in `project_whestbench_folding.md`. [O-self]
tags witnessed in the transcript as first-person tool calls: the a4 script write+run,
the SHORT opening Read, the CLOSING_RUNS grep-read, the ledger parse, repeated
ls-remote checks.

COMMITTED BY THIS PASS: this handoff, the channel entry announcing it,
`core/CLOSING_RUNS_20260819.md` (was untracked), and the DEG4 trace addendum (was an
uncommitted modification) — all four are cited above and must exist on the remote for
Codex. `core/PHASE2_CONTRIBUTION_SHORT_20260819.md` stays uncommitted by design (§8:
the closing-wave merge commits it).
