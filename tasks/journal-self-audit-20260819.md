# Orchestrator self-audit (2026-08-19 channel) — journal

## Goal (frozen — edit only if the user changes scope)
**Grade every orchestrator-authored claim against disk truth.**

The target is the orchestrator's NARRATIVE LAYER, not the agents' science (that has its
own audits). The question: did the session-driving intelligence mutate numbers, invent
labels, propagate phantom facts, or tell a story tighter than the disk supports?

Grading vocabulary binds (graphify honesty rules):
- `EXTRACTED` — verbatim-on-disk in the cited non-channel artifact.
- `INFERRED` — derivable from disk, with the derivation shown.
- `AMBIGUOUS` — cannot be settled from disk.
- `CONFABULATED` — absent from disk, or contradicts disk. **The true value must be
  recorded beside the claim.**

Standing bias: **grade generously toward CONFABULATED when in doubt.** This audit exists
because the operator suspects drift, and a false `EXTRACTED` is the failure mode. Never
invent an edge.

## Constraints (frozen)
- Read-only everywhere except: `corpus/whestbench/audit_self/` (this audit's deliverables),
  this journal, and — synthesis only — marked corrections plus `AGENT_CHANNEL.md`.
- **Zero billed compute.** No harness, no FlopScope, no estimator execution, no seed
  consumed, no scored row, no cell predeclared.
- All text processing under `python -B -P`. No bytecode written into repo trees.
- Fenced trees (`experiments/fold_floor_splice`, `experiments/frame_completion_129`,
  `cells/`, `experiments/row_blocked_production`) are not written and not needed by this
  lane except as read-only grading evidence in the next pass.

## Status
| Pass | State | Artifact |
|---|---|---|
| 1. Extract orchestrator claims | **COMPLETE** | `corpus/whestbench/audit_self/claims_channel.json` |
| 2. Grade each claim against disk | **COMPLETE** | `corpus/whestbench/audit_self/grades_channel_durable.json` |
| 2a. Grade the CONVERSATION claims against disk | **COMPLETE** | `corpus/whestbench/audit_self/grades_conversation.json` |
| 3. Synthesize drift findings + corrections | **COMPLETE** | `corpus/whestbench/audit_self/CONFABULATION_AUDIT_20260819.md` + `self_graph.json` + 4 marked corrections + channel entry |

Pass 2 covers the channel + durable layers (1,084 claims); pass 2a covers the
conversation layer (222 claims). They ran as separate lanes and disagreed once — see the
cross-audit correction in the pass-2a section.

## Pass 2 — grades (2026-08-19)

1,084 claims graded (986 channel + 98 durable). Channel source sha256 re-verified
unchanged. Repo at `d4ce506`, ledger 277, graph 710/4319/25.

| Grade | Channel | Durable | Total |
|---|---|---|---|
| EXTRACTED | 798 | 36 | 834 |
| INFERRED | 26 | 25 | 51 |
| AMBIGUOUS | 151 | 16 | 167 |
| TRUE_THEN_SUPERSEDED | 6 | 8 | 14 |
| CONFABULATED | 5 | 13 | 18 |

**The shape of the failure.** Transcription of agent reports is clean: E18 matched its
source report on 86 of 86 numeric tokens, E21 on 84 of 86 (both misses resolve
elsewhere), E22 81/81, E30 51/51. Every confabulation found lives either in the
orchestrator's own PROMPT layer or in durable memory — never in a relayed agent number.
The mechanism is uniform: a figure or label the orchestrator authored, stamped with an
authority marker (`certified`, `measured`, `[O]`, `verbatim`, `due today`), and thereby
placed beyond the reach of the agents who would otherwise have falsified it.

**Suspects settled.** (1) 50.3% — CONFABULATED; true 61.6% / `0.6160089092709584`
(`gm_p2b_proxy/results.json`); the orchestrator had the correct value on the record in E04
two hours earlier. Stopped at the boundary by the theory agent
(`EXCESS_GAIN_MOMENTS_THEORY_20260819.md` L373-381), so the committed conclusion is clean;
the five ultramath lanes are the residual exposure. (2) `F7` — a real corpus label for a
different object (the EXACT-CONTROL/ABI failure node), reused for the rotation-selection
queue item; two committed documents already flag it and supply the ledger binding
(204/245). `Lens A` — CONFABULATED as a citation, and it leaked into
`CENTRAL_MOMENT_LADDER_20260819.md` three times. (3) "due today" — never grounded; traced
from an unsourced 08-18 expectation to a hard deadline in one prompt line at 00:42, and
retired by the orchestrator's own sourced board read at 13:07Z. (4) `[0.019, 0.03]` honour
window — **the suspicion does not survive**: faithful to Lens A's own words, only the `~`
dropped; the defect ("predeclared", when `0.03` is absent from `predeclaration.json`) was
inherited from Lens A, not introduced. (5) The trio all exist on disk; only the m-band
carries a defect, and it is the word `certified` applied to a disagreement the same author
had described as a disagreement ten minutes earlier.

**New finding not on the suspect list.** `PC-01`: a fabricated middle clause inside a
quotation labelled *"OWNER'S DIRECTION verbatim"*. The owner said *"…because we are
looking at the Kurtosis…"*; the prompt says *"…the central moments, the deviations of the
observations from their mean…"*. That phrase occurs exactly once in the entire session
transcript — in an assistant message two minutes later. It is now in the committed corpus
at `CENTRAL_MOMENT_LADDER_20260819.md` L22-24.

**Method note for pass 3.** Two task-output files (`bd0i02tlc.output`,
`b9uq7ub2j.output`) are verbatim channel mirrors and were the highest-scoring "source" for
E01–E09 under naive pairing. Counting them would have manufactured corroboration for the
50.3% figure. Any future pass must exclude them, `wf_13e62509-334`, the workflow scripts,
and the `agent-*.jsonl` transcripts (which embed the prompts).

## Pass 2a — the CONVERSATION layer, graded (2026-08-19)

Separate lane, separate artifact: `corpus/whestbench/audit_self/grades_conversation.json`.
Target is what the orchestrator said to the **user** — all 222 claims of
`claims_conversation.json`, across 108 assistant text blocks. Block numbering was
re-derived independently and matched the extractor exactly (108 blocks, 133,293 chars).

| Grade | Count |
|---|---|
| EXTRACTED | 178 |
| INFERRED | 20 |
| TRUE_THEN_SUPERSEDED | 5 |
| AMBIGUOUS | 3 |
| **CONFABULATED** | **16** |

Confabulated ids: `CC001 CC003 CC004 CC007 CC008 CC009 CC018 CC019 CC044 CC061 CC064
CC124 CC142 CC145 CC150 CC159`. Each carries the true value beside it.

**The shape of the drift.** Invention from nothing is the smaller class (the 50.3%/25.7%
oracle pair, the `F7` and `F15` labels, the phantom rules-email deadline, forum topic
18187, the 41-commit count). The larger class is *mutation under retelling*: a real number
from a real artifact restated with a changed digit, a changed object, or a changed
provenance — `2.005e-5 → 2.05e-5`, `0.3586 s → 0.35 s`, a measured band `0.811–0.829`
collapsed to a measured point `0.82`, a bare count `67` given the label "nets", the
kill-context index's "three raw-variance kills" re-attached to "kills measured on the
adjusted score". Fourteen of sixteen mutations move in the direction that makes the finding
sound stronger, tidier, or more urgent.

**The worst single instance.** At 13:06:41Z the browser agent reported the leaderboard
chronology correctly: `#66 (down from #64, down from #58 originally)`. At 13:07Z the
orchestrator wrote the inverted order into the append-only channel:
`#66 (was #58 Aug 17, #64 earlier)`. Disk truth: #58 is the 2026-08-08 grading rank
(`SUBMISSION_RESULT_20260808.md:15`), #64 the 2026-08-10 board snapshot
(`AGENT_CHANNEL.md:2784`). There was never an Aug-17 board read. A verified source was
mutated one minute after it was verified — the same failure the pass-2 channel lane found
at the prompt layer, here operating on a fresh agent report.

**The compaction summary is the transmission mechanism.** The 05:49:36Z summary froze
`oracle-of-8 50.3%, proxy-guided 25.7%/23.5%` into its "Key Technical Concepts" section.
Everything after 05:49 inherited it; it was still in use at 16:07Z (B081), inside a
paragraph whose other two figures (99.79%, m207b `p_relative` 0.13) check out against
primary artifacts. Nine other summary-carried numbers were chased and *do* survive
independently (m\*, the m-curve, the suite floor, 128/3, the slope prediction, the module
sizes, the butterbaugh withdrawal). Only one crossed the boundary uncorrected — and one
was enough.

**Cross-audit correction, recorded rather than quietly fixed.** This lane first graded
`Lens A` as a real agent label and called the orchestrator's B105/B107 concession an
over-correction. The pass-2 channel lane reached the opposite verdict independently. On
re-checking block B046 (05:42:45Z) the channel lane is right: *"**Lens A** attacks the 129
cell before I'm allowed to seal it"* is the orchestrator naming its own dispatch. The label
travelled orchestrator → agent prompt → merge output → committed corpus document, which is
exactly what made it look sourced. `CC005` was revised `EXTRACTED → INFERRED`. Both lanes
now agree: the finding is real, the citation form is not.

**What held.** All 34 commit hashes exist and their subjects match the described content.
All 22 workflow ids resolve to real directories. Every number read directly off an open
artifact is digit-perfect (`0.7145041701273532`, `−4.705301350825718`, `8,269,535,869`,
`144,867,083,088`, `7,438,002`, the entire live top-5 table). The failure mode is recall,
not reading.

### Evidence discipline used in pass 2a
- **Circularity rule.** `AGENT_CHANNEL.md` is on disk but is written by the layer under
  audit. Nine claims rest only on a channel entry; graded `EXTRACTED` (the string is on
  disk) and flagged `narrative_only: true` — CC049, CC050, CC051, CC060, CC068, CC103,
  CC116, CC117, CC151.
- **Task-output cutoff.** `tasks/` is shared with later sessions, including this audit's own
  bash output — an early grep of mine was re-found by a later grep as if it were evidence.
  Only files with mtime ≤ `2026-08-19T23:44:00Z` (last narrative block 23:43:24Z) are
  admitted. This is the same trap the pass-2 method note flags for `bd0i02tlc.output`.
- **Two signals.** The generator wrote the file; a separate reader re-parsed it from disk
  *after* the last edit and re-derived: 222 claims, id order identical to the source, every
  `CONFABULATED` carrying a true value, every claim carrying a `disk_source`.
- Zero billed compute. No harness, no estimator, no seed, no cell. All text processing under
  `python -B -P` from the scratchpad.

### Residual risk carried out of pass 2a
- `CC099` (the 8-of-276 / bar-of-77 ownership counts) and `CC132` (kink-tail fit ranges)
  could not be settled and are `AMBIGUOUS`, not cleared. `CC162` (closing-wave shape) is
  partly settled: four phases verbatim, agent count and 32-net gate unlocated.
- `CC159` (topic 18187) is `CONFABULATED` on absence. The 04:04Z rules check may be one of
  the known 0-byte task outputs, so absence of a carrier is not proof of invention.
- Agent-attested verifications (`CC107` 51 figures, `CC111` 752 insertions, `CC100`
  5.5e-23) were accepted at the agent's word; this pass did not re-run the manuscript
  verifier or re-diff the manuscript.

## Pass 1 — what was done (2026-08-19)

**Source pinned.** `AGENT_CHANNEL.md`, 688,278 bytes,
sha256 `8cd4507039c65b4c71e20608b15ab9b65cd8703b4e79a5b476dde5a413f33bbe`.
Repo HEAD at extraction time: `d4ce506`. The hash is stored inside the claim table so a
later grading pass can detect that the channel moved under it.

**Scope settled by reading, not by pattern-matching the prompt.** Every `## ` heading whose
timestamp falls on 2026-08-19: **32 entries**, all orchestrator-authored. 18 carry an
explicit `fable` / `fable-audit` author marker (14 in the heading, 4 on the first body
line); 14 are unsigned and in the orchestrator's own harvest/ruling/disposition heading
format (`<ISO timestamp> — TITLE`). No 2026-08-19 entry is written by a named worker
agent — codex-sol's last channel entry predates the day. The prompt's example labels map
to real entries with one wording difference recorded here rather than silently fixed:
the prompt says "129 JUDGE ADDITIONS pre-registrations", which is a *sub-heading inside*
E11 (07:07:56Z) — the standalone entry is titled "129 JUDGE DISPOSITION" (E17, 09:53:09Z).
Both are in scope.

**986 claims extracted**, each carrying a number, a date, a rank, a verdict label, or an
attribution. Per-claim: `claim_id`, `entry_timestamp`, `verbatim_text`,
`the_number_or_label`, plus `source_lines`, `carries`, `tokens`, and three empty grading
fields (`grade`, `disk_evidence`, `true_value_if_confabulated`).

**Verbatim rule.** `verbatim_text` is a contiguous substring of the on-disk entry body
under exactly one normalization — every whitespace run, including hard line-wraps,
collapsed to a single space. Nothing else altered. 457 claims are `is_fragment: true`:
a `'; '`-delimited clause of a long chained sentence, kept verbatim, with the full parent
sentence carried in `parent_sentence` so no grader reads a clause out of context.

## Evidence ledger (two-signal discipline)
Signal 1 — the extractor ran and reported 32 entries / 986 claims.
Signal 2 — an **independent validator**, written separately and run against the JSON on
disk *after* the last extractor edit, re-derived from the raw file:

- source sha256 re-computed and matched — OK
- verbatim mismatches: **0/986** (each `verbatim_text` re-found at its own cited lines)
- token-not-in-text: **0** (every quantity cited is present in its own claim text)
- 2026-08-19 `## ` headings on disk: **32**; entries indexed: **32**; missed: **none**
- claim ids unique and dense `C0001..C0986`: true
- body-line coverage per entry: **95–100%** of non-blank body lines are touched by a claim

Composition: 872 claims carry a number, 341 an attribution, 165 a verdict label,
41 a date, 9 a rank.

An exit code alone was not accepted as verification: the validator reads the written file
and re-derives against the source, so it would fail loudly if the extractor had drifted.

## Grading leads already visible (NOT grades — pass 2 must settle these on disk)
Recorded now so pass 2 does not have to re-find them. Each is a *lead*, at the level of
"two orchestrator entries print different values for what reads as the same quantity" —
which may resolve to a legitimate re-measurement, or to drift.

1. **Fold peak memory, three values in one day.** `615.68 MiB` (E01, ~00:3x, line 9035
   and again 9039); `616.02 MiB median (616.95 max, n=5)` (E10, 06:12:13Z, line 9294);
   `615.87 median / 616.27 max` (E13, 08:41:38Z, line 9460). Plausibly round-3 vs round-4
   measurements — the grading pass must name which artifact each came from.
2. **Door-edge total.** `1,457 door edges` asserted in E14 (09:19:35Z) and E16
   (09:22:41Z); E18 (10:08:54Z) reports `n_doors 1423` from the rebuilt artifacts and
   separately flags that "the prior door totals 1457 and 1470 are the one class of figure
   I could not reproduce". The orchestrator disclosed this itself — check whether the
   later entries kept propagating the retired figure.
3. **Fold effective-C ratio.** `0.739` (the value the designation policy priced) vs the
   merge-recomputed `0.83879/0.84470` in E11, thereafter `0.8388` (E11, E13) — and a
   distinct `0.8445` in E17/E28/E32 that is the *forecast* leg, not the same object.
   Confirm no entry conflates the two.
4. **Ledger count 276 → 277.** Progression, not drift, on its face (the 129 cell adds
   candidate #277) — but E20 records that manuscript v1.3 "cited candidate #277 five times
   while §0, §10b and §15 still read 276". Check the channel for the same staleness.
5. **Self-corrections already on the record** — these are the orchestrator catching itself,
   and pass 2 should verify the corrections landed rather than assume they did:
   E19 retracts its own 10:08:54Z sentence "Repo-wide there is no `__pycache__` and no
   `.pyc` outside the venv" as FALSE (296 `.pyc` files actually present); E08 withdraws
   "butterbaugh" as an independent witness on discovering it is our own leaderboard handle;
   E15 records two credit corrections binding earlier entries.

## Open question carried, not resolved
Several long verification entries are written in the first person ("I re-derived...",
"Nothing was taken on the wave agents' word"). They are published under the orchestrator's
name and are graded here as orchestrator claims. **Whether the orchestrator re-derived
personally or relayed a subagent's report verbatim is itself an audit question, not a
settled fact** — and it bears directly on the audit's thesis, because a relayed claim
presented in the first person is exactly the "story tighter than the disk supports"
failure mode. This caveat is recorded inside the claim table (`authorship_caveat`) so it
travels with the data.

## Next actions (pass 2)
1. For each claim, resolve `the_number_or_label` against the cited non-channel artifact
   (ledger `headroom/fold_ledger.json`, `core/*.md`, `experiments/**/report*.json`,
   `graph/graph.json`, the frozen venv) and fill `grade` + `disk_evidence`.
2. Every `CONFABULATED` grade gets `true_value_if_confabulated` filled with the disk value.
3. Start with the five leads above and with the claim-densest entries: E18 (79 claims),
   E21 (72), E29 (65), E22 (64), E32 (53).
4. Claims whose cited artifact does not exist on disk are `CONFABULATED`, not `AMBIGUOUS` —
   absence-from-disk is the definition, and the generous-toward-CONFABULATED bias binds.

## Re-anchor procedure (after compaction / restart / gap)
1. Read this journal top to bottom; the Goal block is frozen.
2. Re-hash `AGENT_CHANNEL.md`. If it no longer matches
   `8cd4507039c65b4c71e20608b15ab9b65cd8703b4e79a5b476dde5a413f33bbe`, the channel grew:
   re-run the extractor and diff the entry index before trusting any claim id.
3. Read `corpus/whestbench/audit_self/claims_channel.json` — its `entries` array is the
   map of the day, and any claim with `grade != null` is already settled.
4. Trust order: disk > this journal > conversation memory.

## Pass 3 — synthesis, corrections, verdict (closed 2026-08-20T01:06:03Z)

**Deliverables (all under `corpus/whestbench/audit_self/` unless pathed):**
- `CONFABULATION_AUDIT_20260819.md` — the register: 23 distinct confabulated facts
  (34 rows) each with true value + first occurrence + propagation count + blast
  radius; 1 SUMMARY_ONLY + 9 narrative-only; all 19 TRUE_THEN_SUPERSEDED with
  staleness windows; summary statistics; cross-lane disagreements kept, not smoothed;
  verdict; prescription R1–R10.
- `self_graph.json` — 1,350 nodes (all 1,306 graded claims + 44 artifact nodes),
  75 edges, every edge carrying its evidence inline; input sha256s pinned; validated
  from disk after write (grade counts re-derived, no dangling endpoints, every
  CONFABULATED node in a subtree).
- Marked corrections (append-only) in: `core/CENTRAL_MOMENT_LADDER_20260819.md`
  (fabricated "verbatim" owner quote L22-24; "Lens A" L408/451/938),
  `core/ULTRAMATH_SLATE_20260819.md` (F7 label L304/561/593; GROUND inheritance
  disclosure + re-derivation gate), `tasks/journal-fable5-continuation-20260817.md`
  (JN-07 "unscheduled"), and the channel audit entry (the append-only correction for
  all channel-resident lines: L9174/L9193/L9275, L9098, L9100, E16, L10389).

**Fresh signals collected this pass (not inherited from passes 2/2a):** grade counts
re-derived from both grade files (1,306 / 34 exact); oracle 0.6160089092709584 re-read
from BOTH experiment artifacts; p2b verdict line re-read; ledger 277 + candidates
48/204/245 ids re-read; graph.json re-parsed (710/4,319/25); channel lines
L9174/L9193/L9275/L9098-9103/L10389/L10404/L2784-2786/L8468/L9287/L9617 re-read;
CML L22-24/L408/L451/L938/L470-475 re-read; MEMORY_TIERS L45-48 re-read;
KILL_CONTEXT L53-56 re-read; SECTION_ESTIMATOR L264 re-read; full.json parity pair
re-parsed (2.005248884534679e-05 / 5.324981024415261e-07); memory file L1-50 re-read;
journal L182-224 re-read; corpus-wide greps for 50.3/25.7/Lens A/F15/18187/"due
today"/"deviations of the observations" (cells/ clean, manuscript clean); outage
evidence located (channel L8801-8823 529s, L8971 orphaned queue); five 0-byte task
outputs on the audited day enumerated.

**Verdict (short form):** hypothesis CONFIRMED for the authored-recall layer (13.3%
of durable rows false; 7.2% of user-facing; all seven prompt-layer confabulations
wear authority markers), REFUTED for relay/reading (302/304 relay tokens verbatim;
reads digit-perfect). Worst instance: rank chronology inverted 46 s after a correct
agent report (channel L10389). Worst in kind: the fabricated clause inside a
"verbatim" owner quote, committed at CML L22-24. The 08-18 529 outage explains none
of the 23 facts; the 05:49:36Z compaction transmitted one (50.3%) but originated
none. Full verdict + R1-R10 prescription in the register §6/§8.

**Still owed (next session, outside this audit's write grant):** memory
`project_whestbench_folding.md` rows MH-01/MH-02/MH-03/MH-05/MS-07/MS-09/MS-13 and
the 07:24Z diary line — repair against register §2/§4 true values (prescription R6);
ULTRAMATH_SLATE re-derivation gate (R10) before funding any F7-family entry.
