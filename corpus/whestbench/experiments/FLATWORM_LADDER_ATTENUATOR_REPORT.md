# Flatworm ladder attenuation P2 report

## Verdict

**Kill the router attenuation; preserve the ladder operator for the separate
two-lane response problem.** The full child solved the discrete load-collapse
symptom but did so by replacing the uniquely cheap/best selected expert with
costlier, less accurate experts. It is neither an accuracy promotion nor a
stability-only promotion under the frozen gate.

P0/P1 was not modified. Its four key artifacts and SHA-256 digests are recorded
in [`P0_FREEZE_AUDIT.json`](P0_FREEZE_AUDIT.json). The P2 contract was frozen in
[`PREDECLARED_GATE.md`](PREDECLARED_GATE.md) before the P2 reference pass.

## Primary result

All values below use exactly the same 24 fresh P0 states and the same hidden
uncompressed one-step references.

| Top-1 route | Loss / Physarum | Max load | Experts used | Selected expert cost | Proxy + router cost |
|---|---:|---:|---:|---:|---:|
| Physarum only | 1.000000 | 1.000 | 1 | 1.000x | 1.000x |
| + longitudinal leak | 1.000000 | 1.000 | 1 | 1.000x | 1.000240x |
| + commissural diffusion | 1.000000 | 1.000 | 1 | 1.000x | 1.000721x |
| + fatigue / novelty | **1.101064** | **0.333** | **4** | **4.684x** | **1.524840x** |

The full child selected `fullcov/fixed/Haar-sqrt/Haar-chi2` on
`8/2/7/7` states. It beat the base on only 5/24 states. Its normalized soft
entropy rose to 0.999961, but the important fact is discrete: all four experts
were used and maximum load fell by 0.667. That real load improvement is not
free: aggregate loss worsened 10.1%, selected-expert cost rose 368%, and total
proxy-plus-router cost rose 52.5%.

The tiny negative covariance eigenvalues in two mixture diagnostics were
roundoff (`>= -1.6e-19`), well within the frozen `-1e-9` PSD tolerance. No
nonfinite/PSD failure occurred.

## Why accuracy was nonidentifiable as a global promotion

The untouched P0 oracle already establishes:

```text
best pure top-1 / old parent       = 0.8338178444
best convex top-2 / old parent     = 0.8290544993
required original family ratio     = 0.8000000000
```

An allocation transform over this fixed expert bank cannot manufacture a
missing estimator. P2 was therefore judged as a structural/load falsifier.
Even its local 10%-versus-Physarum gate failed in the opposite direction.

## Component localization

- **Longitudinal leak:** top-1 selection and loss were exactly neutral. It
  slightly changed continuous route weights and top-2 loss (1.030143 to
  1.029856 versus the top-1 base), too little to pay even its tiny charge.
- **Commissural diffusion:** top-1 remained exactly neutral. It changed the
  second choice from Haar-sqrt to fixed-sqrt and made top-2 loss worse
  (1.078132 versus the top-1 base). The paired-consensus link is not useful for
  this expert bank.
- **Fatigue plus continuous novelty:** this is the only mechanism that changed
  top-1 specialization. It succeeded as an anti-collapse device and failed as
  an estimator because load diversity is not a proxy for marginal efficiency.

The component ledger preserves leak as a harmless longitudinal state operator,
commissural diffusion as a mathematically valid pair-equivariant operator, and
fatigue/novelty only as a load-balancing hypothesis. None survives inside this
router.

## Structural checks

- P0 base route reproduction: exact to printed precision (`max error 0`).
- Neuron-permutation ladder route error: `0` after invariant-query error
  `1.11e-16`.
- Pair-lane swap error of commissural diffusion: `0`.
- Deterministic route rerun error: `0`.
- Coupled expert permutation symmetry: `2.69e-15` scaled maximum.
- Six algebra/determinism tests pass.
- Complexity remains `O(L E^2)` with `E=4`; the full child was conservatively
  charged 24,576 scalar operations.

## Biological boundary

The source note supports paired longitudinal cords, transverse commissures,
and temporal habituation/adaptation in planarians. It does not establish this
diffusion matrix, divisive conductance law, lateral inhibition, Physarum flow,
or an MoE router. Those were explicitly tested computational hypotheses. The
negative router result should not be read as a biological result.

## Preserved next translation

Move the topology—not the failed router—to a clean two-lane depth controller:

```text
lane 1 = gate / mean susceptibility response Gram
lane 2 = active pair-covariance response Gram
```

The reported lane cosine falls from roughly 0.73 early to 0.15–0.25 late.
That is where longitudinal state plus transverse coupling has a real target:
attenuate common noise while cosine is high, retain rank two as the lanes
decorrelate, and use no post-hoc depth threshold. This is a new premise and is
not silently promoted by P2.

Full machine-readable results are in [`p2_results.json`](p2_results.json).
