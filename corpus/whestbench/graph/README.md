# Local Graphify run

This directory is a compact, auditable corpus for the user-requested local
Graphify/LightRAG-style analysis. The builder combines hand-audited causal
edges with an exhaustive descriptive navigation layer generated from all 276
append-only ledger records. The latter prevents omissions but is explicitly
not mathematical evidence. The current rebuilt graph (2026-08-18) has 710
nodes, 4,319 edges, and 25 local Graphify communities in the promoted
`cluster-only` pass (that pass is not deterministic: reruns over the identical
710/4,319 graph returned 26, 26, then 25, with different partitions each time,
so only the node and edge counts are reproducible facts); the freeze-window arc
(DGFL/Lens-1, MUB129/design-axis, compute-lane closure, errata/filing) and
the post-freeze Codex clone line are covered by hand-audited nodes — see
`FREEZE_WINDOW_GRAPH_ADDENDUM_20260817.md`. The 2026-08-18 arc (eight sealed
fold cells, the noise-fitting and design-boundary laws, the certified
per-call ladder floor and the in-progress suite ladder, and the three-miner
adjudication of the Codex freezer) is likewise hand-audited, with insights
142-170 carrying its numbered readings.

The semantic Graphify/Ollama pass is retained only as a proposal source. The
canonical graph is rebuilt deterministically from typed nodes and edges in
`build_evidence_graph.py`; no API key, external upload, or remote LLM is
required.

Deterministic rebuild and local reclustering:

```text
python build_evidence_graph.py
graphify cluster-only . --graph graph.json
```

Before rebuilding the graph, run
`python ../../../scripts/build_failure_salvage_atlas.py --check`; the graph
refuses to ingest a stale atlas.

`cluster-only` writes its refreshed visualization/report under `graphify-out/`;
promote `graph.json`, `graph.html`, `GRAPH_REPORT.md`, and
`.graphify_labels.json` to this directory only after checking the dimensions.
Query using `QUERIES.md`, and synthesize only claims supported by the typed
evidence corpus. Centrality and communities remain navigation, not proof.
