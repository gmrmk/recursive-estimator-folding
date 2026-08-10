# Opus 5 handoff - continue as orchestrator when Fable 5 hits limit (2026-08-10)

You are Opus 5 taking the orchestrator seat on the WHestBench campaign.
Read ~/.claude/opus-4-8-operating-manual.md first (the craft manual), then
this file, then AGENT_CHANNEL.md tail (the last Maestro message summarizes
the day). Re-anchor: git log --oneline -15 in this repo.

STATE (all verified today): Phase-1 selection EXECUTED + reload-verified
(#326094 + #327519, changeable until 11 Aug 23:59 UTC - do not touch).
Writeup v8 committed, files by Aug 17 vs ID #326094 (only touch for
red-team-grade accuracy fixes). Phase 2 opens Aug 18. Floor earned by 20
adversarial agents; ledger 242; kills final.

ACTIVE WORK YOU INHERIT:
1. graveyard-run-all workflow (run wf_9a3a25bd-1c2): 16 falsifiers, Opus
   workers + Opus judges. On completion: review artifacts (each gm_* dir
   has PREDECLARATION.md/VERDICT.md), spot-check decisive numbers, append
   the judge-drafted ledger records to fold_ledger.json (run pytest
   tests/test_fold_ledger.py), commit + push. REVIVED_SCREENED items are
   Gen-8/Phase-2 proposals for Jonah - never auto-promote.
2. Bridge monitor (M245 static closure session): on channel PASS status,
   verify bindings as acting /root, prepare the committed GO, and STOP -
   launch needs Jonah's explicit word (two-key). Codex /root reclaims via
   its own append-only channel entry.
3. Sentinel: board/discourse/inbox watch; selection-window close 11 Aug
   23:59 UTC (confirm slots unchanged after); nomination-window and
   re-grade moves get a channel note + push to Jonah.

MODEL POLICY (Jonah, standing): subagent workers/judges = Opus 5 tier
('opus'); EXTERNAL RESEARCH tasks (web, discourse, board scans) =
Sonnet 5 ('sonnet'); do NOT spawn fable-model subagents (usage limit).
Seed every measurement: pinned seed, common random numbers, noise floor
first, twice-run determinism - no promotion without it.

HARD GATES (absolute): no submissions/uploads/logins without Jonah's
explicit word (blind .env key pattern only, value never read/displayed);
no truth/scorer/private/holdout reads; m245_*/M243/M244 held two-key
lane - read-only, never launch; kills final; timestamps: read the clock
BEFORE writing channel headers (this failure fired twice today).
