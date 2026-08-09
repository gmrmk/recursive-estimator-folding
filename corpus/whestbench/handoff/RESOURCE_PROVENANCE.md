# Resource and environment provenance

This file records external resources used by the campaign without vendoring
their repositories, environments, model weights, or competition binaries.

## Local repository snapshots consulted

| resource | URL | commit |
|---|---|---|
| JSpace | https://github.com/kameshkanna/jspace | `54089367f887dde0b076d99bba71d053b67d70ac` |
| Headroom Recursion | https://github.com/gmrmk/headroom-recursion.git | `23e6758e3b95510736711c9eb09d68fbf91063be` |
| ARC MLP cumulant propagation | https://github.com/alignment-research-center/mlp_cumulant_propagation.git | `6e80f7f2af0d33e252731ad9611dff17880b12fb` |
| WHestBench cumulant propagation | https://github.com/ascender1729/whestbench-cumulant-propagation.git | `c6f87fd1e12634447a452f73ebc136c43bf050d5` |
| WHest starter kit | https://github.com/AIcrowd/whest-starterkit.git | `c99ef4af15bae7dd19e1d9c46fa4794d90a91d40` |

These commits are provenance references, not automatic dependencies of M178.
Inspect their licenses and current identities before cloning. Do not replace a
frozen local result merely because an upstream repository has changed.

## Graph build environment

```text
graphifyy 0.7.13
networkx 3.6.1
Python 3.12.13
Ollama model llama3.2:latest
Ollama model content ID a80c4f17acd5
```

The final relationship graph is the deterministic, human-audited graph built
by `corpus/whestbench/graph/build_evidence_graph.py`, then clustered locally.
LLM extraction is a proposal/audit aid; inferred edges are marked and never
serve as mathematical evidence by themselves.

## Competition numerical environment

Frozen reports identify:

```text
WHestBench 0.14.0
FlopScope 0.10.0 for the M169-M176 accounting audits
M177 capability audit records the installed public API as lacking Phi2/Owen-T
```

The environment itself is deliberately not committed. It may contain
competition packages or machine-specific executables. Reproduce it only from
the organizer-authorized distribution and verify its version/hash before a
resource test.

## Included research resources

- `corpus/whestbench/sources/` contains curated source/research notes.
- `corpus/whestbench/resources/research_excursions/` contains 97 mathematical,
  implementation, independent-audit, biology/physics translation, and
  endpoint/cumulant notes used by the M107-M177 campaign.
- `corpus/whestbench/experiments/row_blocked_production/candidate_source/`
  contains the seven source-only Formal parent dependencies required by the
  M145/M157 portability chain. Vendored contents exclude results and archives.
- `corpus/whestbench/sources/USER_PASTED_MATH_DOSSIER_20260806.txt` is the
  user-supplied self-contained mathematical brick; its original SHA-256 is
  `c8c0ac86e11a28d8f34e18a78a5928455c6309ec960ca409212f595a689d492f`.

## Non-vendored categories

No API token, hosted model, paper PDF, challenge weight/truth file, scorer,
Python environment, Ollama model blob, or third-party repository is included.
The private corpus now retains narrowly allowlisted synthetic premise arrays,
package assets, the quarantined T3 archive, and the hash-bound v3.1 GUARDS
archive; none conveys authorization to submit. URLs, commits, notes, and hashes
remain the provenance boundary for external resources.

`mpmath==1.3.0` is recorded only as an optional high-precision test dependency;
its package files are not committed. The sweep used an isolated temporary
target and left the competition environment unchanged.
