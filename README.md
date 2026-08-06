# Recursive Estimator Folding

A Claude- and Codex-compatible agent skill for recursively generating,
falsifying, promoting, combining, and documenting mathematical estimator
mutations under fixed legality and compute constraints.

The core discipline is simple:

```text
champion_g
  -> one-mechanism mutations
  -> cheapest premise falsifiers
  -> matched screens
  -> untouched validation
  -> interaction test
  -> champion_(g+1)
```

Failed implementations remain in the ledger as constraints and salvage banks;
their passed components are retained for new mechanisms. Headroom-style
recursion can propose mutations, but cannot promote them; experimental evidence
remains authoritative.

## Contents

- `SKILL.md` — complete skill instructions.
- `references/operator-catalog.md` — rigorous translations for fractal, tau,
  memristive, biological, retinal/quantum, and physics analogies.
- `scripts/fold_ledger.py` — initializes and audits a JSON promotion ledger.
- `tests/test_fold_ledger.py` — standard-library regression tests.
- `corpus/whestbench/` — the private WHestBench estimator-research corpus,
  evidence graph, recursion packets, negative-result reports, and source ledger.

## Install for Claude Code

Clone the repository, then copy or link the repository directory to:

```text
~/.claude/skills/recursive-estimator-folding/
```

Claude should discover `SKILL.md` from that directory. Restart the session if
the skill list was already loaded.

## Install for Codex

Copy or link the repository directory to:

```text
~/.codex/skills/recursive-estimator-folding/
```

## Ledger usage

```bash
python scripts/fold_ledger.py init experiments/fold_ledger.json
python scripts/fold_ledger.py audit experiments/fold_ledger.json
```

Before proposing a mutation, fill the ledger invariants: objective, score
formula, legality boundary, resource ceiling, split firewall, champion hash,
and reproducible randomization.

## Principles

- Translate metaphors into ordinary mathematics.
- Mutate one causal mechanism at a time.
- Predeclare predicted signatures and kill conditions.
- Use whole independent instances as statistical units.
- Inspect tails, failures, bias, and cost—not only aggregate score.
- Combine winners only after residual-covariance or factorial interaction tests.
- Treat failure as local to a specified implementation and gate; preserve every
  passed component and revisit it only through a new causal mechanism.
- Distinguish a locally best candidate from a demonstrated competition winner.

## License

MIT

The skill implementation is MIT-licensed. The private research corpus retains
the provenance and usage constraints of its individual source materials and is
not intended for redistribution without review.
