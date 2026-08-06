# JSpace terminal-Gram aligned control: final report

## Verdict

**Terminate the JSpace estimator branch. Preserve the terminal
`E[J^T J]` implementation only as an offline sensitivity diagnostic.**

The frozen error-link test failed decisively. Every spectral control increased
the randomized 5-design degree-`>=6` variance on every one of the 16 fresh
networks. The primary terminal-Gram control produced `4.7576x` raw variance and
`21.0923x` cost-adjusted variance, with control/teacher design-error correlation
only `0.0506`.

This run used no official data, scorer, API, or outcome-selected direction. It
was executed exactly once after the independent judge unlock.

## Execution provenance

```text
gate SHA-256   ED9C87B7F5EEFA18A785BD747606BF252D67CCAF9B82FEBCCDBADCE311FA38D2
judge SHA-256  7E8E265A767899DB607FEA9B5227FC1B3950F30BEEC74784F67E5144AE32024E
result SHA-256 27F0DEDA1122303DC49B7522AFAF0AD2276681226E8A72FC2E19ED5DB4D4920F
environment    work/whest-starterkit/.venv/Scripts/python.exe
NumPy          2.4.6
executions     1
```

The unlock matched both the frozen gate and the independent judge before the
runner was invoked. No accuracy result existed beforehand, and the seed bank
was not rerun.

## Frozen factorial

| Control directions | Raw degree >=6 variance | Cost ratio | Cost-adjusted | Wins | Design-error correlation |
|---|---:|---:|---:|---:|---:|
| none | 1.0000 | 1.000 | 1.0000 | -- | -- |
| isotropic | 4.2880 | 1.745 | 7.4834 | 0/16 | 0.0195 |
| signed terminal `J_hat` | 9.1184 | 4.433 | 40.4253 | 0/16 | 0.0172 |
| terminal `E[J^T J]` | **4.7576** | **4.433** | **21.0923** | **0/16** | **0.0506** |

The Gram directions do beat the signed-mean-J directions by 47.8%, satisfying
that one relative gate. This is not a useful result: Gram remains 10.95% worse
than isotropic directions and 375.8% worse than no control before charging its
pilot.

Per-network raw ratios were uniformly adverse:

| Cell | Minimum | Median | Maximum |
|---|---:|---:|---:|
| isotropic | 2.015 | 3.913 | 8.651 |
| signed J | 2.291 | 5.678 | 22.737 |
| second Gram | 2.590 | 4.416 | 10.115 |

There is no favorable network subgroup to preserve or route.

## Failure localization

### Not a conditioning failure

The frozen centering and pilot-RMS scaling fixed the previous numerical scale
problem:

| Cell | Median ridge condition | Median centered pilot residual ratio |
|---|---:|---:|
| isotropic | 6.83 | 0.943 |
| signed J | 8.75 | 0.910 |
| second Gram | 8.25 | 0.888 |

Normalized degree-6/8 feature RMS remains small (`~0.004–0.023`), but the
standardized systems are well conditioned. The primary fit removes about 11.2%
of centered pilot variation yet injects over four times the integration
variance. Pointwise/pilot fit is again not the design-surviving objective.

### Not a constant-mode failure

Feature and teacher matrices were centered before fitting, features were
unit-RMS standardized, and the nuisance intercept was discarded. Thus the
dominant constant mode that contaminated the previous Gegenbauer rung is not
the cause here.

### The failed link is observability

The terminal Gram accurately describes local input sensitivity energy, but its
top four eigendirections do not predict the global even high-degree spherical
integration error. Correlation `0.0506` is essentially null and far below the
frozen `0.40` gate. The signed-J and isotropic correlations are even smaller.

This confirms the prior active-subspace warning: a low-rank local sensitivity
workspace can be real while the degree-six-and-higher residual tumbles across
directions. `E[J^T J]` solved signed cancellation, but not the estimator's
error-link problem.

## Gate ledger

The primary passes only:

- beats signed-mean-J directions by at least 10%;
- median ridge condition below `1e8`;
- exact design, symmetry/determinism, PSD, and finite checks.

It fails:

- raw ratio `<=0.60` (`4.7576`);
- cost-adjusted ratio `<=0.90` (`21.0923`);
- wins on at least 12/16 networks (`0/16`);
- design-error correlation `>=0.40` (`0.0506`).

The exact 5-design defects remain degree 2 `0`, probed degree 4 `5.20e-18`,
and degree 5 `0`.

## Scope and cost boundary

This was only the terminal full input-to-output Jacobian Gram. It made no
layer-band or all-layer workspace claim. The previously derived target-shape
K=4/128-state terminal pilot cost is 2.813B operations; a layerwise extension
would require a separate rung and L-fold accounting.

That extension is not recommended. The terminal object already fails the exact
matched high-degree error link before target-shape deployment.

## Validation

- seven algebra, seed-separation, centering, sign, PSD, rotation-covariance,
  deterministic, and cost tests pass after unlock;
- gate and judge hashes reverified;
- source compiles in the WHest environment;
- `accuracy_results.json` was generated once and retained unchanged;
- no ECN artifact, official row, or scorer was touched.

## Preserved artifacts

Keep:

- the independent-pilot terminal `E[J^T J]` estimator;
- its symmetry and Hutchinson tests;
- the exact-mean centered/scaled control harness;
- the negative error-link evidence.

Do not continue mutating degrees, ranks, seeds, or ridge constants on these
outcomes. Under the frozen localization rule, all three controls failed, so the
JSpace path terminates as an estimator family.

Machine-readable results are in [`accuracy_results.json`](accuracy_results.json)
and [`decision.json`](decision.json). The immutable contract is
[`PREDECLARED_GATE.md`](PREDECLARED_GATE.md).
