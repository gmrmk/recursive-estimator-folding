# Graph addendum — freeze-window arc + post-freeze Codex line (2026-08-17)

Author: Fable (Claude), continuation session 2026-08-17. Convention per the
`M*_GRAPH_ADDENDUM*.md` series: this document records what was added to
`build_evidence_graph.py`, from which sources, and what the rebuild measured.
Nothing here is evidence; the typed nodes/edges in the builder and the artifacts
they cite are.

## Sources

Five absorption briefs produced this session (full AGENT_CHANNEL.md read of
8,052 lines; write-up/deadline state audit; corpus/lineage/satellite-skill map;
post-freeze Codex-clone absorption Aug 13–16; adversarial plan review), plus
direct reads of the primary artifacts they cite. Everything below entered the
graph only after the underlying claim was located in a committed artifact or
explicitly tagged as reported-but-not-evidenced (the F0.75 bytes).

## Delta, in two parts

**Mechanical catch-up (no hand edits).** Rebuilding against the refreshed
267-record atlas (was stale at 223) moved the graph from the promoted
578 nodes / 3,461 edges to **622 nodes / 4,047 edges** — the +44 ledger
candidates and their category edges the stale atlas had been blocking.

**Hand-audited additions (this addendum).** +27 nodes, +36 declared edges
(+35 net: the `writeup_v13_amended` ↔ `seven_constants_correction` pair was
declared in both directions and collapses to one undirected edge), +11
insights (131–141 in `write_insights()`). Final: **649 nodes / 4,082 edges /
26 communities**. Rebuild verified deterministic (two consecutive builds,
identical SHA-256 of graph.json).

New nodes: `dgfl_rotational_stein`, `dgfl_f075_kill`,
`dgfl_coefficient_heterogeneity`, `fourier_lens1_k32`, `d2_ceiling_artifact`,
`alignment_ratio`, `mub129_completion_lever`, `arccos_variance_predictor`,
`gegenbauer_exact_census`, `compute_lane_closure`, `public_oracle_finding`,
`writeup_v9_filed`, `writeup_v13_amended`, `seven_constants_correction`,
`l7_reopening`, `errata_discipline_e5_e13`, `m245_unadjudicated`,
`anti_j_promotion_bar`, `neg_eigenvalue_trap`, `v5d3_static_replay`,
`codex_clone_campaign`, `codex_control_dag`, `codex_domain_history`,
`lightning_ledger`, `headroom_recursion_lineage`, `phase2_lambda_fork`,
`flopscope_bom_receipt`.

Known evidence debt carried on a node rather than hidden: `dgfl_f075_kill` is
`measured_bytes_not_committed` — `F075_RESULTS.json` (sha 9CBA9C35…) is absent
from this tree; the kill is reported by the channel, not evidenced in-repo.

## Recluster and labels

`graphify cluster-only` on the rebuilt graph: 26 communities, all 26
hand-labeled (labels in `.graphify_labels.json`; report regenerated with them).
The freeze-window mechanisms form their own community — **C21 "DGFL & Fourier
Lens-1"** (6 nodes) — while the MUB129/design-axis nodes joined C4
"Spherical-harmonic controls & design axis" and the governance/filing nodes
joined C8 "Budget law & Phase-2 rules", which is where `phase2_lambda_fork`
now sits beside the 272B budget law.

## Deep-analysis findings (queries run on the promoted graph)

Honest framing first: the whole-graph god-node ranking is dominated by the
descriptive ledger-index layer (`approximation or materiality` at 252 edges,
etc.) — that layer is navigation, not proof, exactly as the README warns. The
evidentiary ranking lives in the **hand-audited subgraph: 344 nodes / 677
edges**, whose god nodes are `target` (88), `latent_gate` (28),
`finite_width_vertex` (25), `budget` (16), `symmetry_quotient` (13).

1. **λ-fork sensitivity.** `phase2_lambda_fork` connects to exactly three
   things: the objective, `v5d3_static_replay` (native-call wall slope eats
   ~77% of the Winograd win under current accounting), and
   `codex_domain_history` (L2-fringe peeling −4.948% score at +37.49% wall).
   The entire open compute queue re-ranks on one organizer decision at
   Phase-2 open.
2. **P1 quarantine propagation.** All five records that leaned on P1 premises
   (`s7_wavepacket_speckle_correlation`, `s8_tdse_layer_defect_profile`,
   `s17_information_complexity_lower_bound`, `t3_fold3_deterministic_cap`,
   `recursion_convergence_certificate`) are `screened_component` — none
   promoted, none killed. P1's withdrawal therefore changes no disposition;
   it attaches a re-verify-independently note to any future reuse of those
   five. (`gm_s17_reuse` and `r0_harmonic_energy_spectrum` are `killed`,
   on their own grounds.)
3. **DGFL → Lens-1 salvage line.** The direct mechanism edge is
   `dgfl_coefficient_heterogeneity → fourier_lens1_k32`
   (the symmetry cut: every k=32 rung transfers positively both directions
   while all of k=16 fails). Lens-1 is the only sealed OPEN candidate with
   its holdout (net2) unopened.
4. **anti-J distance to gate.** Its neighborhood is the bar itself
   (κ ≤ −269/525), the negative-eigenvalue trap (forbidding spectrum-only
   evidence), and the G11 negative signal from the Codex clone. Nothing in
   the graph moves it toward the gate; the W0→W_I precondition remains the
   cheapest decisive measurement and remains unrun.

## Semantic pass (proposal source)

Decision recorded 2026-08-17 by the owner: the Ollama semantic pass is
retired; a dispatched reading agent is the proposal source instead. The
agent's proposals are audited by hand before any enters the builder; accepted
and rejected proposals are recorded here.

**Result.** The dispatched agent read the P1–P6 papers, GEN4/GEN8, the
graveyard-mine and failure-mode-graph docs, and the write-up §2–§4, and returned
31 proposals, each citing file and section. Hand audit: **30 accepted, 1
rejected** (the `neg_eigenvalue_trap` ↔ `trace_collapse` link — thematic
co-occurrence only, no shared mechanism). The accepted set adds 16 nodes (the
four paper-theorem nodes P2/P4/P5/P6, the GEN8 protocol rungs, the
graveyard-mine findings x5/unrun-class, S18's singleton-cell seal, the
output-cone collapse, the subtract-not-predict principle, and the P3 protocol
rules) and 30 edges carried at class `AUDITED_SEMANTIC+…` with the agent's
declared scores — the highest-value single addition being P4's independent
re-derivation of the Gegenbauer census constants (65/88,424,448 at m=126, zero
at 129), which upgrades the design-axis story to a two-route derivation.
Every endpoint id was verified against NODES before commit; the endpoint check
runs clean (`missing-endpoints=NONE`).

**Final dims after the audited pass: 665 nodes / 4,112 edges / 25 communities**
(+16 nodes, +30 edges over the freeze-window build; deterministic rebuild
verified identical twice; coverage test green). The recluster merged DGFL into
a "Coefficient-transfer failures" community with H2 and the sign-changing
control — the graph independently grouping three generations of the same
failure mechanism.

## merge-graphs evaluation (Codex unified overlay)

Evaluated and **rejected for the canonical graph**: the Codex clone's
`whest-unified-graph.json` (9,255 nodes) is a code graph of a different
corpus (the headroom-recursion package plus the clone's experiments/ layer)
overlaid with its control DAG, built from uncommitted working-tree state with
no deterministic rebuild path on this side. Merging it would break the
canonical graph's provenance law. It is preserved verbatim in the 2026-08-17
campaign-layer archive (`Backups\whestbench-20260817\
codex-clone-campaign-layer-20260817.tgz`), and the cross-links the canonical
graph needs are carried by the three hand nodes `codex_clone_campaign`,
`codex_control_dag`, `codex_domain_history`. Revisit only if the clone layer
is ever committed.
