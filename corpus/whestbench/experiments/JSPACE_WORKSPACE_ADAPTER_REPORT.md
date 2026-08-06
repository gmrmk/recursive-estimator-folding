# JSpace source audit and ReLU workspace adaptation

## Outcome

The source-level audit and NumPy cleanroom adaptation are complete.

**Combined verdict:** kill the signed-pursuit mutation, preserve the PSD
second-moment workspace and its Hutchinson estimator for one narrowly scoped
error-link fold.

The important correction to a direct JSpace transplant is:

```text
upstream transferred object       E[J]
ReLU sensitivity workspace        E[J^T J]
```

On the fresh bank, `(E[J])^T E[J]` retains only **10.28%** median Jacobian
energy. The second moment is therefore not a cosmetic variant—it recovers
about 89.7% of sensitivity energy lost to signed cancellation.

## Pinned upstream audit

- Repository: https://github.com/kameshkanna/jspace
- Commit: `54089367f887dde0b076d99bba71d053b67d70ac`
- Commit date: 2026-07-11
- Package: `jspace 0.1.0`, Python >=3.10
- License: MIT, copyright 2026 Kamesh Kanna
- Runtime dependencies: PyTorch, Transformers, Accelerate, NumPy, tqdm,
  Rich, Matplotlib, Seaborn, Hugging Face Hub, and Safetensors.

The actual source implements a fused Rademacher-VJP estimator of a signed
average residual-stream Jacobian, constructs normalized corpus `J h` vectors,
and uses nonnegative matching pursuit for 95% coverage with cap 30. It then
combines capacity with language-model-specific next-token, position, entropy,
and unembedding signals.

There is a material source-level caveat to the `paper-exact` label. The fused
routine averages target positions only over the second half of the sequence,
then averages gradients over all source positions. Causal zeros remove invalid
pairs, but this is not the literal uniform `E_{t,t'>=t}` over every advertised
position pair. The all-layer fused VJP identity is valid for the scalar the code
actually constructs; its positional weighting claim is not copied into this
feedforward adaptation.

The README's replication and language-workspace results are upstream claims,
not conclusions of this audit. Its referenced results text file is absent from
the pinned tree. No upstream model, checkpoint, prompt corpus, or result was
executed. Full provenance and blob IDs are in
[`UPSTREAM_PROVENANCE.json`](UPSTREAM_PROVENANCE.json), with the claim boundary
in [`research_jspace_source_audit_20260806.md`](../../../sources/research_jspace_source_audit_20260806.md).

## Cleanroom experiment

The frozen bank contains 12 fresh width-16/depth-8 bias-free He ReLU networks,
384 Gaussian states each, nested Hutchinson counts `{1,2,4,8,16}`, and a
288/96 corpus/query split. Exact Jacobians are synthetic diagnostics only.

### Workspace geometry

| Metric | Median |
|---|---:|
| `||EJ||_F^2 / E||J||_F^2` | **0.1028** |
| Effective rank of `(EJ)^T(EJ)` | 1.352 |
| Effective rank of `E[J^TJ]` | **5.587** |
| Second-moment top-4 energy | 0.7282 |
| Second-moment top-8 energy | **0.9300** |

Every network had a cancellation ratio below 0.75; the observed range was
0.0184–0.2414. Averaging signed Jacobians creates an artificially rank-one-like
picture. The PSD Gram retains a meaningfully broader workspace.

### Hutchinson accuracy

For each Rademacher output probe `z`, the adapter computes only the VJP
`g=J^Tz`, accumulating both `outer(z,g)` and `outer(g,g)`.

| K | Median signed-J error | Median Gram error | Median top-8 overlap | Worst Gram error |
|---:|---:|---:|---:|---:|
| 1 | 0.5861 | 0.1773 | 0.9798 | 0.6174 |
| 2 | 0.4297 | 0.1230 | 0.9931 | 0.3040 |
| 4 | 0.3074 | **0.0857** | **0.9957** | 0.1923 |
| 8 | 0.2172 | 0.0554 | 0.9976 | 0.1640 |
| 16 | 0.1502 | **0.0409** | **0.9987** | 0.0793 |

All estimated Grams were PSD. The Gram is easier to estimate accurately than
the signed matrix at this shape, and K=4 already recovers its leading subspace
well.

### Signed versus nonnegative pursuit

| Pursuit | Successful 95% coverage | Median successful k | Median residual | Mean coverage |
|---|---:|---:|---:|---:|
| Nonnegative coefficients | 98.09% | 4 | 0.04221 | 0.95840 |
| Signed coefficients | 100.00% | 4 | 0.03855 | 0.96263 |

Signed pursuit is mathematically safer for signed gradients, and the unit test
includes the exact opposite-atom case where nonnegative pursuit stalls. But on
the actual fresh ReLU bank it improves terminal residual by only 8.66% and
success by 1.91 percentage points. Both are below the predeclared 20%/10-point
materiality gate. Do not add signed pursuit to the estimator path.

## Cost

At the synthetic shape, K=16 Hutchinson costs 1.112x exact materialization
because `K=d`; that is expected and is not a deployment claim.

For a target-shape **128-state pilot** at `d=256,L=32`:

| K | Signed + Gram VJP cost | Fraction of 272B budget |
|---:|---:|---:|
| 1 | 1.105B | 0.41% |
| 2 | 1.675B | 0.62% |
| 4 | **2.813B** | **1.03%** |
| 8 | 5.091B | 1.87% |
| 16 | 9.646B | 3.55% |

Exact 128-state Jacobian materialization is approximately 142.0B. Applying
VJPs at all 64,512 design points would still be prohibitive; this is only a
pilot diagnostic/direction source.

## Symmetry and correctness

- finite-difference Jacobian and exact VJP orientation tests pass;
- Gram PSD and deterministic nested-probe tests pass;
- input orthogonal covariance, hidden permutation invariance, output
  permutation covariance, and positive homogeneity pass;
- maximum coupled numerical error: `1.90e-14`;
- five tests pass; no nonfinite or PSD failure;
- no ECN artifact or official row was touched.

## Failures and survivors

Killed:

- language/token/position workspace signals—out of domain;
- treating the signed mean Jacobian as a sensitivity covariance;
- signed pursuit as a material improvement over the upstream nonnegative rule;
- any claim that workspace geometry already improves the estimand.

Preserved:

- fused/nested Rademacher VJPs;
- `E[J^TJ]` as the correct cancellation-resistant PSD workspace;
- K=4 as the economical leading-subspace premise point;
- pursuit only as an offline diagnostic, not an estimator component.

## Recommended next fold

Use an independent 128-state, K=4 pilot to obtain the top workspace directions,
then replace the failed ungated weight-salience directions in the earlier
degree-6/8 Gegenbauer control with these Gram directions. Predeclare and compare:

1. no control;
2. isotropic directions;
3. signed-mean-J directions;
4. second-moment-Gram directions.

Fit output coefficients on a separate pilot and score only the randomized
5-design degree-`>=6` residual at matched total cost. This is the necessary
error link. It also directly confronts the existing active-subspace warning:
if the post-design residual scales like `(rank/d)^6`, even an accurate workspace
will not pay. Failure there should terminate the JSpace branch.

Machine-readable metrics are in [`premise_results.json`](premise_results.json)
and [`decision.json`](decision.json); the frozen gate is
[`PREDECLARED_GATE.md`](PREDECLARED_GATE.md).
