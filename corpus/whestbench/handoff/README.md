# Fable 5 WHestBench handoff

This private bundle is the reproducible continuation point for the recursive
estimator-folding campaign as of 2026-08-07.

Start here:

1. Read [GOAL.md](GOAL.md).
2. Paste [FABLE5_ASCII_RESUME_PROMPT_20260807.txt](FABLE5_ASCII_RESUME_PROMPT_20260807.txt)
   into a fresh Fable 5 session with repository access.
3. Run `python scripts/verify_whestbench_handoff.py` from the repository root.
4. Read [TEST_SWEEP_20260807.md](TEST_SWEEP_20260807.md) and
   [TEST_MATRIX.md](TEST_MATRIX.md) before running historical tests.
5. Read the mathematical, systems, and combined autopsies under
   `corpus/whestbench/headroom/`.
6. Inspect `corpus/whestbench/graph/graph.html` and the deterministic graph
   report. Centrality is navigation, not evidence.
7. Resume only at M178 as specified in the ASCII prompt.

## Snapshot

- Ledger: 176 candidate/component/audit records through M177.
- Graphify: 279 nodes, 576 edges, 12 Graphify communities.
- Deterministic NetworkX partition: 13 communities.
- Current first broken link: no certified, bounded-cost, metered
  `Phi2`/Owen-`T` value-and-derivative provider.
- Current exact-control branch status: blocked before BackgroundArchive,
  source conversion, variance, efficacy, score, and submission.
- Formal champion: unchanged and deliberately absent from this repository;
  identity and hash are recorded in GOAL.md.

## Included

- The complete skill and operator catalog.
- Curated WHestBench corpus and source notes.
- Updated fold ledger and What-If oracles.
- Mathematical, systems, adversarial, and combined failure postmortems.
- Deterministic Graphify/NetworkX builder, JSON, HTML, report, and insights.
- User-supplied mathematical dossier.
- Lawful source, tests, runners, manifests, checksums, and compact result JSON
  for the M120-M177 research chain, including the current M155-M177 throat.
- Research-excursion notes and independent audits used by that chain.
- Root `base_estimator.py` and the audited exploratory full-covariance closure
  needed to understand the M174-M177 interface no-go.
- All 24 response-free M154-M177 test entry points, their frozen supporting
  source, the seven Formal-parent portability dependencies, and the exact
  optional high-precision test pin.

## Deliberately excluded

- challenge truth arrays or private targets;
- raw challenge MLP weights;
- scorer/evaluator binaries and internals;
- credentials, API keys, tokens, environments, caches, or compiled bytecode;
- submission archives;
- third-party repositories or packages whose URLs/versions are sufficient;
- bulky machine-local artifacts not required to reproduce a stated claim.

These exclusions are a legality and provenance firewall. They are not missing
tasks for the next agent to reconstruct.

## Integrity

`BUNDLE_SHA256SUMS.txt` covers the handoff corpus except itself. The verifier
also checks:

- the Fable prompt is strict 7-bit ASCII;
- the ledger parses and has 176 records;
- `graph.json` parses and has 279 nodes and 576 edges;
- no forbidden cache/binary extensions entered the bundle.

Historical per-experiment checksum files remain authoritative for their
owning directories. A mismatch is a stop condition, not permission to rewrite
history.
