# Local Graphify run

This directory is a compact, auditable corpus for the user-requested local
Graphify/LightRAG-style analysis.

Planned extraction uses the already installed Graphify 0.7.13 and the already
installed Ollama `llama3.2:latest` model. No API key, external upload, or remote
LLM is required. The run is intentionally delayed until official scorer timing
is complete so local model inference cannot contaminate residual wall time.

Expected command shape:

```text
graphify extract <this-directory> --backend ollama --model llama3.2:latest
  --max-workers 1 --max-concurrency 1 --out <this-directory>
```

After extraction, query the graph using the questions in `QUERIES.md`, save
raw answers, and synthesize only claims supported by the evidence-typed corpus.

