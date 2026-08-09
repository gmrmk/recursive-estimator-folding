# Local Graphify run

This directory is a compact, auditable corpus for the user-requested local
Graphify/LightRAG-style analysis. The current audited graph has 291 nodes,
593 edges, and 15 local Graphify communities.

The semantic Graphify/Ollama pass is retained only as a proposal source. The
canonical graph is rebuilt deterministically from typed nodes and edges in
`build_evidence_graph.py`; no API key, external upload, or remote LLM is
required.

Deterministic rebuild and local reclustering:

```text
python build_evidence_graph.py
graphify cluster-only . --graph graph.json
```

`cluster-only` writes its refreshed visualization/report under `graphify-out/`;
promote `graph.json`, `graph.html`, `GRAPH_REPORT.md`, and
`.graphify_labels.json` to this directory only after checking the dimensions.
Query using `QUERIES.md`, and synthesize only claims supported by the typed
evidence corpus. Centrality and communities remain navigation, not proof.
