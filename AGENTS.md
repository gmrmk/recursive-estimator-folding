# AGENTS.md — multi-agent coordination for this repo

Two AI agents work in this repository ON THE SAME LOCAL CHECKOUT, coordinated
by the owner (gmrmk):

- **Codex Sol** (OpenAI Codex CLI) — reads this file automatically.
- **Fable** (Claude Code) — runs a sentinel loop that pulls and reads the
  mailbox (below) roughly every 30-60 minutes.

## Read these first (in order)

1. `corpus/whestbench/core/GOAL_STATEMENT_20260808.md` — the standing goals.
2. `corpus/whestbench/core/HANDOFF_CODEX_SOL_20260808.md` — the complete
   campaign inventory + the full fold ledger as Appendix A.
3. `corpus/whestbench/core/GEN4_CLOSING_20260808.md` — the constraint set:
   mechanism families that are CLOSED by measurement. Do not respin them.
4. `AGENT_CHANNEL.md` — the mailbox. Check it every session.

## How to talk to the other agent

Append a message to `AGENT_CHANNEL.md`. Protocol:

- **Append-only.** Never edit or delete an existing entry.
- Entry format: `## [YYYY-MM-DD HH:MM UTC] <agent> -> <agent>: <subject>`
  followed by the body.
- Commit the append promptly (its own commit is fine) so the other agent's
  next pull sees it. Messages only travel when committed.
- Latency is asynchronous: Fable reads on its next sentinel wake; Codex reads
  at its next session start. For anything urgent, ask the owner to relay.

## Shared-checkout safety rules (both agents, non-negotiable)

- Work ONLY on branch `agent/compression-survivor-corpus`. No checkouts to
  other branches, no `git reset --hard`, no rebase of pushed history, no
  force-push, no stash-dropping — the other agent's uncommitted work may be
  in the tree.
- Commit only files YOU created or edited (`git add <paths>`, never `-A`).
- Pull with `--ff-only` before pushing; on divergence, merge (never rebase
  pushed commits).
- The fold ledger (`corpus/whestbench/headroom/fold_ledger.json`) is
  append-only; both agents append records, neither rewrites existing ones.

## Campaign discipline (binds both agents)

- Fold discipline: predeclare mechanism + kill gate BEFORE code; cheapest
  falsifier first; kills are final; one causal mutation at a time.
- FIREWALL: no sealed cells, no truth/scorer reads, no credentials read or
  displayed (submission uses a blind .env load ONLY under the owner's
  explicit authorization), no accounting bypass EVER, public endpoints
  read-only.
- Hard dates: Phase 1 closes Aug 10 23:59 UTC; algorithmic writeup files
  Aug 17 (ID 326094); registration/team freeze Sep 5; designation locks
  Sep 19 (TWO nomination slots); private re-run Sep 20-30 decides prizes.

## Current division of labor (renegotiate via the mailbox)

- **Fable**: sentinel loop (leaderboard/discourse watch, re-grade tracking),
  Phase-2 resubmission of v3.1 GUARDS at the Aug 10 flip, deadline
  shepherding, journal + intel docs.
- **Codex Sol**: research frontier (M198+ exact-control lineage and beyond),
  new experiments under `corpus/whestbench/experiments/`, ledger appends.
