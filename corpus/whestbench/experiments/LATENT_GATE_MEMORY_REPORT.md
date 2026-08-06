# Gate-split inherited-label memory recompression

## Decision

**Hard kill on the predeclared material-effect gate.**

Preserving the low/central/high split labels does not amplify the parent
gate-split signal. It reduces aggregate MSE by only **0.03975%** versus corrected
full covariance, for ratio **0.9996025**. The required ratio was `<=0.8`.
Exactly 6/8 cases win, so the win-count gate passes at its boundary, but the
effect is roughly 503 times too small.

More importantly, label memory is worse than the generic-recompression parent
on all 8/8 matched cases. The parent ratio was `0.9975024` (0.2498% reduction),
so explicit one-step path memory erases about 84% of the already-small gain.

No WHest data, scorer, API, new cases, parameter changes, or post-result tuning
were used. The immutable parent truth and corrected-fullcov predictions were
reused bit-for-bit.

## The sole mutation

Everything in `latent_gate_split` is frozen: the correlation-coordinate
boundary solve, ridge `1e-8`, three equal-probability truncated-normal bins,
exact conditional moments, GL64 Gaussian ReLU map, q=3 component cap, relative
PSD tolerances, weights, cases, and references.

Only recompression changes. For each parent component, the split produces an
ordered family

```text
(low child, central child, high child).
```

Instead of mixing all `q^2=9` children by a generic covariance projection, the
child groups are

```text
all low children     -> one moment-matched Gaussian
all central children -> one moment-matched Gaussian
all high children    -> one moment-matched Gaussian.
```

Thus the retained component index is explicit one-step memory of the gate
statistic. Every label has mass exactly `1/3`; steady growth remains nine
children followed by exactly three components.

## Symmetry and moment preservation

The scalar statistic `T` is invariant under neuron permutations and positive
diagonal coordinate gauges. Therefore inherited labels are unchanged. Since
moment matching commutes with a fixed linear transformation, aggregating each
fixed label group is permutation and positive-scale covariant.

On frozen `n=64,L=16,seed=18560`:

- label aggregation reproduces the unrestricted nine-child mixture's global
  first two moments to numerical precision;
- end-to-end layerwise permutation relative error is below `1e-10`;
- an internal positive-coordinate gauge with compensating adjacent weights has
  relative error below `1e-10`;
- every steady layer has nine children, three outputs, and masses `(1/3,1/3,1/3)`.

All five tests pass.

## Frozen eight-case screen

| L | seed | corrected fullcov MSE | label-memory MSE | ratio | win |
|---:|---:|---:|---:|---:|:---:|
| 16 | 18560 | 3.6884e-4 | 3.6864e-4 | 0.999474 | yes |
| 16 | 18561 | 8.2110e-4 | 8.2113e-4 | 1.000042 | no |
| 16 | 18562 | 1.4425e-3 | 1.4414e-3 | 0.999215 | yes |
| 16 | 18563 | 2.0847e-4 | 2.0849e-4 | 1.000100 | no |
| 32 | 18720 | 3.1834e-4 | 3.1787e-4 | 0.998515 | yes |
| 32 | 18721 | 2.8092e-3 | 2.8092e-3 | 0.999997 | yes |
| 32 | 18722 | 3.0041e-4 | 2.9969e-4 | 0.997607 | yes |
| 32 | 18723 | 5.9922e-4 | 5.9896e-4 | 0.999569 | yes |

Summed baseline MSE is `0.00686808`; label-memory MSE is `0.00686535`.

## Interaction with the parent

The parent generic recompressor wins all eight cases and reaches ratio
`0.9975024`. The label-memory child is worse than that parent on every matched
case. This is a clean negative interaction: the useful direction does not
benefit from preserving the sign/centrality label across layers.

A plausible explanation is that `T` is redefined from the current component at
every layer. A “low” label at layer `l` is therefore not the same physical mode
as “low” at layer `l+1`. Forcing those labels to remain separate blocks the
generic compressor from regrouping children by the actually dominant current
covariance direction. The experiment tests one-step inherited labels, not a
globally transported invariant path coordinate.

## Conservative n256/L32 cost

| charged term | arithmetic |
|---|---:|
| covariance sandwiches | 6.442B |
| correlation eigensolves | 14.496B |
| nine GL64 Gaussian ReLU maps | 28.991B |
| conditional and label moments | 0.151B |
| subtotal | 50.080B |
| with 25% contingency | **62.600B** |

Removing the generic compressor eigensolve saves approximately 6.04B including
contingency. The `<80B` gate passes, but the accuracy gate makes a FlopScope
port unwarranted.

## Files

- `PREDECLARED_GATE.md`: frozen mechanism and survival conjunction.
- `latent_gate_memory.py`: label aggregation and cost model.
- `run_fresh_n64.py` / `fresh_n64_results.json`: matched evidence.
- `test_gate_memory.py`: moment, trace, symmetry, and cost guards.
- `structural_audit.py` / `structural_audit.json`: parent interaction and
  machine-readable audit.
- `finalize_decision.py` / `decision.json`: final gate and artifact hashes.
