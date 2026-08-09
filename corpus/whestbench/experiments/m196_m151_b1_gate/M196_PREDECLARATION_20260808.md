# M196 predeclaration -- M151 B=1 residual-variance and native-provider gate

Date: 2026-08-08.  Written before any generated source-variance, native
target trace, response, scorer, contest, or submission run.

## Scope and frozen parent

M196 is the next rung of `m151_b1_forward_control`, not a replacement for it.
It keeps all of the following fixed:

- target: M151's ordered-distinct `[2,1,1]` owner
  `T_211 = (1/2) sum Delta_ijk F_ijk`;
- control: one and only one 49-node signed B=1 state and the M151
  `dtilde_ijk` covariance-star formula;
- residual: M151/M133 fixed full-support three-bank proposal with its frozen
  `uniform_mixture=0.05`, exactly `K=128` draws per source layer, and no
  pilot, adaptive router, or proposal retuning;
- source transport: exactly one forward M125b carrier insertion; no M150
  reverse adjoint, second source carrier, k3-squared insertion, or B>1 stack;
- exact coefficient: the M147-compatible central `[2,1,1]` bridge with its
  explicit refusal/certificate behavior.

The experiment is generated-only.  It may use Philox-generated SPD cells and
their exact source coefficients, but may not read a WHestBench row, public or
private truth, scorer, leaderboard, submission artifact, or champion output.
It does not measure final-output accuracy.

## Required provider and trace, before variance is opened

The variance runner is not authorized unless all four artifacts exist and pass
their local contracts:

1. `m196_b1_state_provider.py` exposes a deterministic B=1/49-node
   `build_b1_state(background, source_weight, layer_index)` implementation.
   Its returned state must satisfy the M151 `B1CanonicalState` contract, be
   fixed before residual draws, preserve hidden-label permutation and positive
   ReLU-gauge covariance, and have no result/outcome input.
2. `m196_native_b1_compiler.py` emits the three M151 source slots without an
   `n^3` label loop, preserves the ordered-singleton half owner and collision
   exclusion, and has exhaustive width <= 24 parity against the M151 oracle.
3. `m196_m147_provider.py` binds the exact coefficient provider, propagates
   M147 certificate refusals, and has a finite fixed target call path for
   `31 * 128 = 3968` residual coefficients.
4. `m196_native_trace.json` is emitted by a target-shaped FlopScope run.  It
   charges provider construction, tables/canonicalization, copies/fills,
   compiler calls, any uncredited carrier work, coefficient glue, and residual
   wall time.  It must show `B=1`, `nodes=49`, no prohibited operation, peak
   allocation <= 512 MiB, and total inclusive new cost <= 10.291363760B.

Missing any artifact is a fail-closed feasibility blocker, not a zero-cost
assumption and not permission to run a synthetic variance screen.

## Generated 24-cell residual premise

Once the provider/trace gate passes, construct exactly 24 Philox cells:

| family | width | Philox seeds |
|---|---:|---|
| diagonal SPD | 12 | 1961201--1961204 |
| diagonal SPD | 16 | 1961601--1961604 |
| diagonal SPD | 24 | 1962401--1962404 |
| iid-He SPD | 12 | 1961211--1961214 |
| iid-He SPD | 16 | 1961611--1961614 |
| iid-He SPD | 24 | 1962411--1962414 |

For each cell, enumerate the finite ordered-distinct domain once.  Let
`q0(e)` be the frozen M133 proposal probability, `F_e` the full three-slot
source feature, `Delta_e` the certified exact coefficient, and
`H_e = Delta_e - dtilde_e`.  Define the squared Frobenius source contribution

```text
R_e = || Delta_e F_e / (2 q0(e)) ||_F^2,
H_e = || (Delta_e-dtilde_e) F_e / (2 q0(e)) ||_F^2.
```

The variance quantities are the finite proposal expectations of `R_e` and
`H_e` minus their squared source means; no sampled estimate, response, or
end-to-end network target is used.  The p99 diagnostic is the p99 of the
same squared Hansen--Hurwitz contributions.  Use a fixed Philox bootstrap
seed 1960001 with 20,000 within-cell resamples, resampling cells within each
family only.  No proposal, threshold, K, width, or state rule may be changed
after this file is written.

## Pass/fail gates

The B=1 configuration survives only if all conditions hold:

1. every static provider/native-trace condition above passes;
2. for each family and pooled over all cells, the one-sided paired-bootstrap
   90% upper bound on `V_H/V_Delta` is strictly below `0.25`;
3. for each family and pooled, `p99(H_e)/p99(R_e) <= 1.25`;
4. no family has a positive least-squares slope of `V_H/V_Delta` against
   width over `{12,16,24}`;
5. every coefficient and source value is finite and every M147 refusal is
   recorded as a cell failure; no fallback, clipping, or omitted term is
   permitted.

Failure kills this B=1 provider/configuration only.  It preserves M151's
unbiased control identity and any correctly audited component.

## Primary commands

```powershell
python check_m196_feasibility.py
python -m unittest -v test_m196_contract.py
# Only after the two commands report READY, not BLOCKED:
python run_m196_generated_variance.py
```

The latter runner is intentionally absent until the provider and native trace
exist.  Implementing it first would create an invalid variance result around a
synthetic substitute rather than the claimed B=1 mechanism.
