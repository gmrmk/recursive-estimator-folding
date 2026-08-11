# Predeclaration — factored second-order propagation (Cholesky Gram form)

Written before any code in this directory was run. No result was read before
this file was committed.

## Mechanism (exactly one)

Change the **representation** of the propagated second-order state. Nothing
else — no coefficient, tolerance, rank, gate, or ordering changes.

Current path, per layer:

```
a = mu @ W
C = W.T @ (V @ W)              # dense, entrywise
(mu', V') = relu_moments(a, C) # M178 Tallis/Owen-T, entrywise
```

Proposed path:

```
L such that V = L @ L.T        # Cholesky of the carried state
M = L.T @ W
C = M.T @ M                    # a Gram of a real matrix
(mu', V') = relu_moments(a, C) # unchanged
L' = cholesky(V')              # re-factor; FAILS CLOSED if V' is not PSD
```

`C = M.T @ M` is positive semidefinite **by construction** in exact arithmetic
and to `O(eps * ||M||^2)` in floating point, because it is a Gram matrix. The
dense path forms the same object entrywise, where each entry carries independent
`O(eps)` error and no structural guarantee.

## The question this experiment actually answers first

`gm_spd_width_scaling` measured `min eig(C) <= 1e-12` before layer 32 at width
`>= 96`. Congruence preserves positive definiteness **exactly**: if `V` is PSD
then `C = W.T V W` is PSD as mathematics. So the observed indefiniteness must be
born in one of two places, and they have opposite consequences:

- **(a) forming `C`.** Rounding in the two-matmul product `W.T @ (V @ W)` drives
  the computed `min eig` below zero once `lambda_min <~ eps * n * lambda_max`.
  **The Gram form fixes this exactly.**
- **(b) `V'` itself.** `relu_moments` assembles the post-ReLU covariance entry by
  entry from bivariate moments, each with independent `O(eps)` error and no joint
  PSD constraint, so `V'` can already fail to be PSD before any congruence.
  **The Gram form cannot fix this**, because the defect is upstream of the
  representation being changed.

**This is a cheaper and more decisive falsifier than the one recorded in
`RECURSION_PACKET_GEN7 section 6`**, which proposed building the factored
producer and observing whether `ell*` rises. That is the right *outcome* test but
the wrong *first* test: it costs a full producer implementation to learn
something one diagnostic settles. The packet's version is superseded here, and
the reason is recorded rather than silently swapped.

## Predicted signature

Stated before running, on the two-regime mechanism already measured (round-off
dominated above width ~80):

1. `min eig(V')` — the post-ReLU state straight out of `relu_moments` — stays
   **strictly positive** through the layer at which the dense `C` first trips the
   floor. i.e. the defect is (a), not (b).
2. `min eig(C_gram) > min eig(C_dense)` at every layer where they differ, and
   `C_gram` remains above the `1e-12` floor for strictly more layers.
3. `||C_gram - C_dense||_max / ||C_dense||_max <= 1e-9` wherever both are
   SPD-safe — the two are the same object, differing only in assembly error.

Confidence is deliberately not asserted: (1) is the premise under test, and the
corpus's own diagnosis that the indefiniteness is "round-off in the dense
entrywise representation" was inferred from the `eps * n * lambda_max` ratio, not
from a direct measurement of `V'`.

## Kill conditions (predeclared, no post-hoc adjustment)

- **`KILL_UPSTREAM`** — `min eig(V') <= 0` at or before the layer where the dense
  `C` first trips the floor, on any replicate. The indefiniteness is born in the
  entrywise ReLU-moment assembly, factoring the *propagation* cannot repair it,
  and this mutation is dead at its cheapest gate. Any repair would have to change
  `relu_moments` itself, which is frozen.
- **`KILL_NO_GAIN`** — `C_gram` trips the `1e-12` floor at the same layer as
  `C_dense` on a majority of replicates at width 256. The representation is not
  the binding constraint.
- **`KILL_DIVERGENCE`** — relative max-norm difference between `C_gram` and
  `C_dense` exceeds `1e-9` on the SPD-safe prefix. They are not computing the
  same object and no comparison between them is admissible.

## Scope and honesty limits

- Synthetic He-Gaussian weights only, via `m200.generated_weights` with the
  `cell_seed` scheme of `gm_m179_m199/diag_spd_depth.py`, so cells are directly
  comparable with the existing SPD record.
- Diagnostic mode records the full trajectory rather than raising at the first
  failure; the *producer* form fails closed. These are separate entry points and
  the report will not mix them.
- **No clip, no floor, no ridge, no eigenvalue truncation** anywhere. If `V'` is
  not factorable, that is a recorded refusal, not a repaired matrix.
- float64 only. Higher precision is a different mechanism.
- This measures **definedness**, not accuracy. Even a complete pass makes no
  estimator, variance, MSE, or score claim: `t2` measured the closure at 311x
  from competitive as a predictor, and the analytic-control direction is capped
  at 1.40x by the R^2 arithmetic. Both stand regardless of the outcome here.

## Second signal

Every layer's `min eig` is computed by `numpy.linalg.eigvalsh` on the explicitly
symmetrized matrix, and the dense-path column must reproduce the
`gm_spd_width_scaling` value of `ell*` for the same `(width, replicate)` cell.
A mismatch there invalidates this harness before any claim is read from it.
