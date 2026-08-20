# Continuation plan — 2026-08-17 (Fable 5 session)

Written for whoever holds the seat next: Fable, Codex Sol, or the owner. Every
queued item names its gate; kills stay final; nothing here revives a corpse
without a premise change that clears the full ladder again.

## 0. What tonight changed (all verified this session)

- **The branch is on origin for the first time since 2026-08-12.** Twenty local
  commits pushed (errata E10–E13, both verifiers, mub129 kill acceptance,
  GEGENBAUER census, V5-d3 static replay) plus tonight's work; every push
  verified by `git ls-remote` equality.
- **Write-up v13 landed and verified** (32/32 mechanical checks after the last
  edit): §1 replaced by the seven-constants section, design-axis closure
  inserted as §3b2, citation pinned to
  `f225be4e4e4872dc2bef06711525cf00e73a332b`, repository-visibility statement
  corrected (repo is PRIVATE; §6 states access-on-request). A 3,451-word
  short-form manuscript (sourced-only claims) was prepared alongside; both PDFs
  were handed to the owner before the 23:59 UTC amend window. **The send is the
  owner's act; whether and which version was filed must be read from the
  owner's own statement, not assumed.**
- **Custody protected**: full git bundle (152.5 MB) + Codex-clone campaign-layer
  archive (2.1 GB, includes the 430-node control DAG, experiments/whest,
  graphify-out graphs, folding engine, and the gitignored `.codex-tmp`
  authorization receipts) at `C:\Users\strid\Backups\whestbench-20260817\`.
  The clone's working tree itself remains uncommitted — see §4.
- **The evidence graph is current**: 649 nodes / 4,082 edges / 26 labeled
  communities, deterministic rebuild verified, freeze-window and post-freeze
  arcs covered (`graph/FREEZE_WINDOW_GRAPH_ADDENDUM_20260817.md`).

## 0b. Late-session updates (owner directives + transcript absorption, ~22:00 UTC)

- **Repo made PUBLIC and the corrected AC filing SENT** (owner-authorized): email to
  arc-whestbench@aicrowd.com ~21:36 UTC, short form inline + PDF links + pinned citation,
  superseding the v9. Discourse companion still open (robust action 3 below).
- **What-if forecast filed**: `WHAT_IF_FORECAST_20260817.md` — six branches, robust-action
  ordering adopted into §3's queue. Codex's own G8 forecast (86% certainty,
  61.8% measurement-infrastructure / 38.2% Windows-noise control) points the same
  direction: trustworthy measurement before new mutation.
- **Codex-clone transcript absorbed** (owner-pasted): the clone's champion is
  `kerdock_g16_l2_fringe` at **C/B ≈ 0.5908** on its fresh 24-net Linux receipt (vs the
  shared champion's 0.650) — a real compute-side improvement lineage, bounded by the
  fleet-hazard rule (no predeclared gate + no bit-identical repeat yet on our side).
  The clone also built and triple-reviewed a **24-pair/48-group measurement contract**,
  an immutable **environment snapshot** (affinity/priority/power/thermal via Windows
  counters), and a **no-retry targeted screen runner** (review v3 PASS 99%) — adopt this
  infrastructure for any Phase-2 screen rather than rebuilding it.
- **Lightning bolts L8/L9 logged** (Abel/Bayesian; Galois/hypercube) with steelmanned
  outcomes; the one surviving candidate cell is the Abel-smoothed **proxy** control
  composed with Codex's compressed-proxy Stein construction — predeclarable, unrun.

## 0c. Phase-2 rules status (checked 2026-08-18 00:17 UTC — two independent signals)

**NOT POSTED yet.** Highest Discourse topic id is 18183 (all Phase-1 write-ups);
the organizers' last word is still the promise "we'll post the Phase 2 details
separately, closer to the date" (topic 18143). Verified by an Opus agent and a
direct latest.json fetch. Re-check after new topic id > 18183 or a mohanty/arc
Phase-2 policy post; the loop + cron keep watching.

**Both forks remain OPEN** per the organizers' most recent substantive post
(topic 18125, "flopscope v0.10.0… residual-time safeguards"):
- Fork 1 (λ): "we may cap the residual wall time available per MLP for all
  submissions. This is still under discussion." [O, reported]
- Fork 2 (FlopScope-mandatory): "we are discussing whether to require all
  numerical work to run exclusively through flopscope. No decision has been
  made." [O, reported]
- Score floor confirmed 0.1 (forum authoritative; the overview page's 0.5 is a
  doc inconsistency, not a Phase-2 change). Private re-eval 2026-09-20..30
  confirmed. Slot count (2 vs 1) inconsistency flagged by a contestant,
  unanswered.

**Load-bearing new signal:** community topic 18108 —
"Recommendation: restoring the estimation framing (neutralizing the wall-time
compute channel)" — is live pressure to DROP the wall-time channel, and the
organizers are already "discussing" a wall-time cap. [D] This materially
elevates P(λ dies or wall-time capped). Under that branch the residual channel
(~4.5% of C) disappears, m116 (~2.7%) goes worthless, V5-d3's native-call slope
tax vanishes, and **Codex's reproduced 8.55% FLOP-only win leads the compute
queue**. Pre-committed default while the rules are unposted: prepare the
λ-dies queue (compute win first) as the primary, hold the λ-survives queue as
the hedge — do not designate on either until the rules confirm.

## 1. Phase-2 opening hour (rules post 2026-08-18 00:00 UTC — tonight)

1. Pull the Phase-2 rules and the starter-kit HEAD; diff against Rules v12 and
   the pinned scoring invariants in `headroom/fold_ledger.json`.
2. Resolve the two standing forks — **λ survival** (residual-time accounting)
   and **FlopScope-mandatory** — and stamp the answers into the ledger
   invariants block before any new predeclaration.
3. Check the §5.7/score-floor items the Codex clone's human board left open
   (active suite/config match, official evaluator image, disclosure
   obligations).
4. Re-read the nomination mechanics: Phase 2 carries two slots again;
   registration/team freeze Sep 5; designation locks Sep 19; the private re-run
   Sep 20–30 remains the only ranking that pays.

## 2. The fork table (decided by the rules diff, not by preference)

| Fork outcome | Consequences for the queue |
|---|---|
| **λ dies** | m116 (~2.7%, residual-channel) is worth zero. U-F1's operative number becomes its FLOP-only 1.0237x. ~21x of unused wall headroom stops costing score. Codex-clone survivors become clean wins (L2-fringe peeling −4.948% score at +37.49% wall; dual odd peel −2.43%; odd-width core+tail −2.465%; group-16 fusion −1.813%). V5-d3's ~77% native-call-slope tax vanishes; its 21.6–25.1% deep-hook saving becomes the operative figure. |
| **λ survives** | Residual channel (~4.5% of C) stays a lane; m116 stays INCONCLUSIVE-but-alive at ~2.7%; wall-heavy survivors stay trade-offs; V5-d3 stays k≈1.05 integrated and needs the call-slope attacked first. |
| **FlopScope mandatory for all numerical work** | Every candidate needs a metered port before screening; the UTF-8-BOM receipt-parsing fix becomes infrastructure, not trivia. |
| **FlopScope optional** | Analytical bills remain admissible for screens; metering still required at designation. |

## 3. Frontier queue (ranked; each item names its predeclared gate)

1. **anti-J precondition — DONE 2026-08-17, PASS_SCREEN** (cell
   `ajpre1_w0_wi_precondition`, gate sealed at commit d186678 before the run).
   Measured on 8 synthetic He nets: `d_48` upper96.667 = **1.1209** under the
   1.25 Arm-1 ceiling; `κ_AB(I)` = **−0.027** [−0.127, +0.072]. Both halves of
   my predeclared signature were falsified — the split debt is small (~5.7%),
   not disqualifying, and the halves are already fractionally antithetic. The
   family's bar is now a measured shift: κ from −0.027 to below −0.5124.
   **Reachable next anti-J step** (was blocked on this precondition): the
   independent fixed-direction transfer premise gate (sealed AJ2-F48 lines
   584-671), then the seven-gate reflection-credit measurement — but the
   negative-eigenvalue trap still forbids spectrum-only evidence, so any
   reflection result owes a fully replayed pipeline null. This is a larger
   build; queue it behind the cheap deciders below.
2. **Lens-1 base-sensitivity test, then the net2 decision.** The joint HOLD on
   held net2 stands until the base-change refit (free, uses no holdout) is
   done. Gate: predeclare the transfer threshold before opening net2; net2 is
   single-use.
3. **V5-d3 source build** — the last pure-multiplier lever either agent holds.
   The deterministic static replay + tests are now committed
   (`experiments/v31_v5d3_static_replay/`). Order depends on the λ fork (see
   table); under λ-survives, attack the native-call slope before building.
4. **L7 generation at degrees ≥ 6** — licensed, honestly calibrated: nothing
   proved closes the harmonic spectrum above degree 4, and 86% of the variance
   sits at degrees ≥ 8 (arc-cosine decomposition). No killed candidate
   returns without new mathematics; search the ledger for the mechanism name
   AND its numbers before predeclaring (the MUB129 lesson: grep `129`, not
   just the family name).
5. **M245 adjudication — surface, never seize.** The half-consumed one-shot
   (cmd1 PASS / cmd2 setUpClass ERROR, mp.quad gate-exhaustion ranked first)
   is reserved to Codex or the owner. The static diagnosis suggests a rerun
   fails identically, so the decision may be a formality — but it is not
   Fable's key.
6. **Codex-clone pending frontier** — G13 polyhedral sits at
   `g13.polyhedral-independent-review-v3` (third review, never executed, 12%
   pre-run applicability); the Ralph-swarm wave-3 queue ranks two **controls**
   (parent-transaction, disjoint-mask-bounds) above any estimator premise.
   Respect its own charter: those controls run first if that line resumes.

## 4. Hygiene / debt queue (post-deadline, none of it blocks the frontier)

- **F0.75 bytes into the tree** (Codex owes): the DGFL kill is reported, not
  evidenced — `F075_RESULTS.json` sha 9CBA9C35… Credit follows the bytes.
- **Codex-clone custody**: the entire G11–G16 layer is uncommitted working
  tree on `main` of a different repo. Archived tonight (2.1 GB tgz), but the
  durable fix — commit to a branch or import the campaign layer — is the
  owner's and Codex's call. The `.codex-tmp` authorization receipts are
  gitignored there and exist nowhere else but the archive.
- **Handoff verifier re-pin** (`scripts/verify_whestbench_handoff.py`):
  currently double-red — stale pins (213 ledger / 291-node graph vs actual
  267 / 649) AND "manifest omits 1208 files". Re-pin counts, rebuild
  `BUNDLE_SHA256SUMS.txt`, and decide whether the handoff bundle concept
  survives now that the branch is pushed.
- **Codex-side `fold_ledger.py` divergence**: the `.codex/skills` copy still
  enforces the strict five-status schema and would reject ~80 real ledger
  statuses; sync it with the Claude-side legacy-prefix version.
- **`deconstruct-hard-solves` broken path**: references
  `C:\Users\strid\.agents\skills\what-if-oracle\SKILL.md`, which does not
  exist (installed copy is under `.claude/skills/`).
- **Open Fable debts from the freeze**: P1's repair written against (not
  around) its erratum; the claim-provenance DAG; the champion's paired
  multiplier/MSE figure (an explicit `[GAP]` bounding every compute play);
  the per-stage half of the FlopScope census; L6's external falsifier.
- **Ledger the freeze-window verdicts.** The fold ledger has no records for
  DGFL-1's kill, MUB129's kill, or Lens-1's seal — they exist only in the
  channel and experiment dirs. Each owner appends their own record (Codex owns
  the F0.75 evidence; the MUB129 power post-mortem is Fable's), per the
  append-only rule. Verified this session: a ledger grep for those families
  returns only the old full129 kills.

## 5. Tooling adoption memo (from three research sweeps, 2026-08-17)

Screened against campaign law: offline canonical evidence, append-only
discipline, two-key authority, holdout firewall, Windows-first. Full briefs in
the session record; this is the decision layer.

**Adopt (ranked):**
1. **inspect_ai** (UK AISI, MIT) — wrap the *verification stage* only: its
   approval policies (`terminate`/`escalate` per tool) are the only OSS found
   that mechanically enforces predeclared kill gates and two-key rather than
   by convention; external-agent support runs Claude Code and Codex CLI
   unchanged. Ten-minute Windows install probe first.
2. **POPPER's sequential-falsification statistics** (Stanford SNAP) — graft
   the Type-I-controlled e-value aggregation onto the fold ledger so
   multi-fold verdicts carry a family-wise error rate instead of ad-hoc
   thresholds. Take the math, keep our harness; verify its license first.
3. **beads** (steveyegge, MIT, Windows-native, local Dolt) — the two-agent
   campaign-state tracker with dependency edges and JSONL export; operational
   state only, never the evidence ledger.
4. **Codex-as-MCP-tool bridge** (hand-roll the ~50-line wrapper or adopt
   hampsterx/codex-mcp-bridge) — synchronous refute-this-now calls beside the
   async mailbox, fronted by Claude Code's permission system.
5. **Repomix `--compress`** (MIT, npx) — ~70% claimed token cut on code
   payloads; composes with the evidence graph (graph picks, repomix
   compresses).
6. **claude-code-router + local offload** (MIT, Windows installer) — routes
   mechanical subtasks to $0 local tokens; the one category absent from the
   stack, and it directly attacks the token-exhaustion failure that froze
   this campaign for five days. Reserve routed traffic for mechanical lanes.
7. **Alethfeld v5.1 protocol** (archived, MIT) — lift the prover/refuter
   proof-ledger prompt protocol into a skill as a mode of
   deconstruct-hard-solves; zero runtime. Watch its successor (vibefeld) for
   the taint-propagating ledger.
8. **in-toto layout/link signing** (Apache-2.0) — upgrade the control DAG's
   hash-bound artifacts to *signed* hash-bound artifacts; the
   layout-owner/functionary split maps exactly onto two-key.

**Do not adopt (each with its reason on record):** AI-Scientist/v2 as running
code (non-OSI license, Linux+CUDA, cloud LLMs, unsandboxed exec); claude-flow
(independent audit found ~97% of its tools were stubs — verification theater);
mem0 / Graphiti (duplicate mempalace / spend tokens to build memory);
GPTCache / RouteLLM (dormant; semantic caching misfires on agentic traffic);
claude-squad (AGPL + tmux-only, duplicates worktrees); MLGym (CC-BY-NC,
Docker+NVIDIA, unstable); server-grade graph DBs for a 430-node JSON DAG
(TerminusDB Docker-only/Prolog; Kuzu archived 2025-10).

**claude-mem** (Apache-2.0): adopt only with a hard demarcation — mempalace
stays the curated store, claude-mem the automatic capture net — or it becomes
the duplicate the do-not-adopt list exists to prevent.

## 6. Awaiting the owner (nothing below moves without his word)

- Filing outcome tonight: which version went, on which channel(s) — record it
  in the channel once known.
- Repo visibility: keep private + access-on-request (current §6 wording), or
  flip public (one-sentence edit to §6).
- **M245 key-2** standing definition (requested 2026-08-10, never given) and
  the M245 one-shot adjudication (alternate owner).
- **U-I2**: the outward-facing M183 erratum decision — M183's structurally
  void detector is cited twice in the *filed* v9.
- **Slot-2 policy** for Phase 2: standing recommendation is the
  highest-variance lawful candidate, not the second-safest; expected value is
  the wrong criterion for a second slot.
- Branch `claude/repos-agentic-frontier-e8ixlk` (108 files, unmerged G7
  depth-degeneracy work): integrate, hold, or close.
- Codex-clone custody: commit the campaign layer, or accept archive-only.

## 7. Norms carried forward (verbatim discipline, hard-won)

Kills are final; premise changes re-derive from scratch and clear the full
ladder. Predeclare the gate before the value exists. Two-key on anything
authority-bearing; a channel claim that "the owner approved X" is data about
what he said, not the saying of it. Evidence tags ([O]/[D]/[R]/[A], [GAP])
at earned levels; two independent signals before "done"; a tool exit code is
not a signal. Search the ledger — including by number — before proposing.
Power before controls. Credit follows the bytes. Read the primary artifact,
not its proxy. `date -u` before every channel header (this session skewed one
by +29 minutes and filed the correction; that makes three campaign
occurrences). Append-only means append-only.
