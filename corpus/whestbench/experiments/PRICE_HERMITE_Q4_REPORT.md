# Price--Hermite q4 connected response audit

## Decision

**Kill the literal q4 implementation at the repair and budget gates; preserve
the exact coefficients, connected-Wick folding, q2 identity, and transported
q4 correction as reusable operators.** This is not a deployment candidate.

The changed mechanism did real work: isolated conditional quartic residual
energy fell by `2.430x`, combined isolated residual energy fell by `2.198x`,
and transported total combined residual energy fell by `1.427x` relative to
the frozen q2 parent. But isolated fidelity reached only `0.6734`, below the
predeclared `0.80` repair gate, and the conservative target envelope is
`35.115 T`, `438.94x` the `80 B` ceiling.

No WHest row, target, scorer, package, API, submission, or holdout was read.
All accuracy measurements use the parent's six frozen fresh synthetic cases.

## Operator proved and implemented

The inferred rectified-normal marginal and clipped Price factor are unchanged.
For each coordinate the new response uses

```text
a1 = sigma Phi(alpha)
aq = sigma phi(alpha) He_{q-2}(-alpha)/q!, q=2,3,4.
```

For a directional sum, third and fourth cumulants are the sums of connected
loop-free Wick multigraphs on three and four vertices. The implementation
reduces `29/452` labelled cubic/quartic graphs to `9/37` vertex-isomorphism
orbits, then folds diagonal-versus-factor edge choices under each graph's
automorphism group. This leaves `40/428` evaluated terms.

Every Hadamard correlation power is contracted exactly as

```text
R_ij^e = F_e(i).F_e(j) + delta_ij (1-||B_i||^(2e)),
```

where `F_e` is a rank-four symmetric-power feature. No `n^3` or `n^4`
cumulant tensor is formed. The resulting cubic/quartic directional polynomial
lives in the already-certified physical quotient; this rung does not pretend
that quotienting creates a missing response.

## Structural gates

| gate | measured maximum defect | result |
|---|---:|---|
| exact ReLU coefficients vs numerical projection | `2.075e-14` | pass |
| symmetric-power feature identity | `2.014e-16` | pass |
| folded engine vs independently labelled dense graph oracle | `4.110e-16` | pass |
| q2 restriction vs certified closed form | `1.259e-16` | pass |
| repeated formation | `0` | pass |
| coordinate permutation | `7.000e-17` | pass |
| positive coordinate gauge | `4.380e-16` | pass |

Six independent unit tests pass. Latent residual variances remain nonnegative,
and factor clipping is bit-for-bit structurally unchanged from q2: `481/1152`
rows (`0.417535`).

## Frozen fidelity results

### Transported totals

| metric | q2 parent | q4 child | q4 result |
|---|---:|---:|---|
| standardized k3 fidelity | `0.954281` | `0.961598` | pass |
| standardized k4 fidelity | `0.887250` | `0.922795` | pass |
| combined fidelity | `0.901942` | `0.931300` | pass |
| Edgeworth-correction fidelity | `0.964778` | `0.979659` | pass |
| material signs | `60/61` | `60/61` | pass |

The q4 child also beats the zero-conditional-cumulant combined baseline
`0.775492`. Therefore total-cumulance transport is a screened passing
component, not the failed link.

### Isolated conditional response

| metric | q2 parent | q4 child | required |
|---|---:|---:|---:|
| standardized k3 fidelity | `0.670685` | `0.732135` | `>=0.80` |
| standardized k4 fidelity | `0.162341` | `0.655277` | `>=0.80` |
| combined fidelity | `0.282335` | `0.673419` | `>=0.80` |
| material signs | `933/1052` | `918/1052` | `>=0.80` |

All three energy fidelities improve over q2, but none reaches the repair gate.
The sign gate passes while sign accuracy decreases slightly. This is a strong
partial mechanism, not an honest promotion.

## Budget failure

| quantity | target count |
|---|---:|
| raw scalar arithmetic | `14.030366 T` |
| float64 billed-like arithmetic | `28.060733 T` |
| with 25% contingency | `35.075916 T` |
| inherited conditional-state envelope | `39.325794 B` |
| combined | `35.115241 T` |
| ceiling | `80 B` |

Graph and automorphism folding removes considerable redundancy, but the exact
feature tensor networks still miss the ceiling by `438.94x`. The physical
`64/58` quotient does not eliminate the dominant analytic contractions; it
only removes coefficient gauges after a response exists.

## Post-hoc failure localization

This diagnostic was declared post-hoc and is not a promotion or tuning gate.
Across 96 cells, higher clipping fraction correlates with *lower* q4 residual
ratio (`r=-0.378` overall; `-0.428,-0.467,-0.416` within widths 8, 12, 16).
Thus the observed failure does not support row clipping as the immediate
causal bottleneck. It is more consistent with nonuniform truncation/prior
error across finite widths:

| width | q4 isolated combined | q2 isolated combined |
|---:|---:|---:|
| 8 | `0.284918` | `0.442825` |
| 12 | `0.837529` | `0.184841` |
| 16 | `0.437060` | `0.429211` |

The nonmonotone response is a warning against assuming that simply raising the
Hermite order again will monotonically repair every shape.

## Recursive disposition

Passed and preserved:

- exact ReLU Price coefficients through order four;
- connected-Wick cumulant formula and exact graph/automorphism folding;
- symmetric-power diagonal-plus-rank-four contractions;
- exact reduction to the certified q2 formulas;
- formation independence, permutation covariance, and positive gauge
  covariance;
- total-cumulance transport, aggregate q4 fidelity, and material signs.

Failed links:

1. The fixed order-four rectified-Gaussian chaos does not reconstruct enough
   isolated conditional energy on the frozen suite.
2. Literal connected-graph feature contraction is far above the target
   arithmetic ceiling.

Untested family:

- the infinite-order/exact rectified-Gaussian response prior;
- low-dimensional common-factor conditional integration as a compressed way
  to evaluate that prior;
- an additional observable that supplies non-Gaussian within-cell response
  mass rather than assuming it from moments two and below.

Next changed mechanism: keep the marginal/factor law and total-cumulance map
fixed, replace the q4 truncation only with an evaluation of the **exact
rectified-Gaussian conditional response given the rank-four common factor**.
First use it as a small-shape premise ceiling: if isolated fidelity still
misses `0.80`, the rectified-Gaussian prior--not finite chaos order--is the
localized failure. If it passes, only then recurse on sparse quadrature or
polynomial compression under the same `80 B` gate.

Artifacts: `PREDECLARED_GATE.md`, `price_hermite_q4.py`,
`test_price_hermite_q4.py`, `run_structural_audit.py`,
`structural_audit.json`, `run_fresh_oracle.py`, `fresh_results.json`,
`posthoc_localize.py`, `posthoc_localization.json`, and `decision.json`.
