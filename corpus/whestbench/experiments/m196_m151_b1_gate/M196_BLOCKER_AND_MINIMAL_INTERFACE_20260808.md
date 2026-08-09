# M196 blocker and minimal implementation interface

## Current disposition

**BLOCKED BEFORE THE VARIANCE GATE.**  M151 proves a source identity, but the
repository has no implementation that turns a target-width background into the
required deterministic B=1 49-node conditional-moment state, no target-safe
non-cubic M151 source compiler, and no inclusive native trace tying those to
the M147 residual provider.  This is a concrete implementation/input-state
blocker, not negative evidence about the control identity.

The closest existing components are deliberately insufficient:

| component | what it supplies | missing for M196 |
|---|---|---|
| M179 | Gaussian-closure `BackgroundState(mu,V)` | no signed 49-node conditional moments or canonical B=1 factor map |
| M151 | `B1CanonicalState` validation and exhaustive small-width source parity | no `build_b1_state`; its compiler contains ordered triple loops and is explicitly prohibited at width 256 |
| M147 | certified local central `[2,1,1]` reference | no fixed native batch provider; its literal target kernel is recorded cost-killed |
| M125b | source-agnostic forward carrier | no M151 state construction or source compiler |

Consequently a 24-cell run now would either use made-up conditional moments or
silently charge the prohibited cubic reference.  Neither is an honest test of
M151.

## Minimal interfaces that unlock the gate

```python
def build_b1_state(
    background: BackgroundState, source_weight: Array, layer_index: int
) -> B1CanonicalState:
    # Return exactly 49 signed weights and (49,256) conditional mean/variance.
    # It must be deterministic before q0 draws, finite, nonnegative in the
    # conditional variance, hidden-permutation / positive-ReLU-gauge covariant,
    # and expose a fixed operation/copy census.
```

```python
def compile_b1_control(
    source_weight: FnpArray, state: B1CanonicalState,
    out_aaaa: FnpArray, out_aaab: FnpArray, out_aabb: FnpArray
) -> None:
    # Exact M151 source slots.  No n^3 index loop, no output dual, no second
    # carrier.  Must match the M151 exhaustive reference through width 24.
```

```python
def delta211(
    background: BackgroundState, i: int, j: int, k: int
) -> tuple[float, Certificate]:
    # M147-compatible value/certificate.  Refusals propagate; no clipping,
    # unpriced adaptive retry, or replacement coefficient.
```

The trace writer must then produce:

```json
{
  "flopscope_target_trace": true,
  "blocks": 1,
  "nodes": 49,
  "inclusive_new_cost_billions": 10.291363760,
  "peak_mib": 512.0,
  "prohibited_operations": []
}
```

Those numeric fields are ceilings, not suggested values.  The trace must also
record the operation/copy census and residual wall-time conversion.

## Exact test sequence after implementation

1. Exhaustive generated width 5/8/12/16/24 parity against M151's ordered
   source oracle: all three source slots <= `4e-11`; `j/k` symmetry, half
   owner, repeated-label zero, covariance star, gauge, and permutation tests.
2. Native width-256 FlopScope trace: every additional operation and allocation
   billed; `B=1`, 49 nodes, <= `10.291363760B` additional inclusive cost, <=
   512 MiB, no all-output dual or cubic compiler.
3. Only then execute M196's frozen 24-cell finite-population variance gate.
   A source variance pass is still not an end-to-end estimator or a promotion.
