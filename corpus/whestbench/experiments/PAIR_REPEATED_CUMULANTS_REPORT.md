# Pair-repeated cumulant representation oracle

## Decision

**Repeated-index omission killed: the representation fails contraction-energy
gates and no exact O(n^3) dense recurrence was derived. Its signed orientation
and compact terminal algebra remain preserved components.**

The subset preserves material Edgeworth correction signs surprisingly well:
94/97, or **96.91%**. But it catastrophically fails magnitude. Aggregate
standardized contraction fidelities are:

| quantity | fidelity | gate |
|---|---:|---:|
| k3 | -248.9998 | >=0.8 |
| k4 | -3578.1022 | >=0.8 |
| combined k3+k4 | -2803.7649 | >=0.8 |
| combined Edgeworth correction | -75.1957 | diagnostic |

Negative fidelity means the squared approximation error exceeds the entire
full-contraction energy. All-distinct tensor entries are not dispensable noise;
they cancel large repeated-index contractions. Removing them keeps the rough
sign while destroying scale.

No WHest data, scorer, API, or competition target was used. The oracle uses
nine fresh synthetic He-ReLU networks, 65,536 deterministic antithetic paths
per case, and independent fresh next-layer weights.

## Oracle construction

For centered activation `X`, estimate

```text
K3_abc  = E[X_a X_b X_c]
K4_abcd = E[X_a X_b X_c X_d]
           - C_ab C_cd - C_ac C_bd - C_ad C_bc.
```

The full diagonal next-layer contractions for output column `w` are

```text
k3(w) = sum_abc  K3_abc  w_a w_b w_c
k4(w) = sum_abcd K4_abcd w_a w_b w_c w_d.
```

The oracle zeros every entry with more than two distinct neuron indices, then
compares the resulting contractions with the full tensors.

## O(n²) representation and O(n³) terminal contraction

Store

```text
d3_i   = K3_iii
p3_ij  = K3_iij,     i != j
d4_i   = K4_iiii
t4_ij  = K4_iiij,    i != j
q4_ij  = K4_iijj,    i != j, symmetric.
```

This is `3n²-2n` k3 tensor positions and `7n²-6n` k4 positions. For n=16,
that is 736 of 4,096 k3 entries and 1,696 of 65,536 k4 entries.

For all output columns of W, with elementwise powers,

```text
k3_rep = sum_i d3_i W_i^3
         + 3 sum_i W_i^2 (P3 W)_i

k4_rep = sum_i d4_i W_i^4
         + 4 sum_i W_i^3 (T4 W)_i
         + 3 sum_i W_i^2 (Q4 W^2)_i.
```

The state is O(n²), and three dense matrix products give all terminal diagonal
contractions in O(n³). Tests match masked full-tensor contractions to at most
`3.33e-15`.

## Frozen case results

Fidelity is `1-SSE/full_energy` on standardized contracted cumulants.

| n | L | k3 | k4 | combined | correction | material sign |
|---:|---:|---:|---:|---:|---:|---:|
| 8 | 2 | 0.9749 | 0.9431 | 0.9509 | 0.9896 | 1.000 |
| 8 | 3 | 0.7402 | 0.5645 | 0.6133 | 0.8881 | 1.000 |
| 8 | 4 | -1598.03 | -24359.99 | -18813.41 | -508.58 | 1.000 |
| 12 | 2 | 0.9281 | 0.8316 | 0.8566 | 0.9273 | 0.917 |
| 12 | 3 | 0.6687 | 0.2905 | 0.3869 | 0.5390 | 1.000 |
| 12 | 4 | -0.8568 | -20.7307 | -13.7339 | -0.7730 | 1.000 |
| 16 | 2 | 0.9243 | 0.9285 | 0.9276 | 0.9652 | 1.000 |
| 16 | 3 | 0.5101 | 0.7280 | 0.6842 | 0.8406 | 0.929 |
| 16 | 4 | 0.6548 | 0.5685 | 0.5840 | 0.6822 | 0.929 |

Only 3/9 cases meet all three 0.8 energy gates. Depth, not width alone, is the
clear failure axis.

## Sample-doubling audit

The same depth-four cases were rerun with 131,072 antithetic paths. Failure is
stable:

| n | doubled-sample k3 fidelity | doubled-sample k4 fidelity |
|---:|---:|---:|
| 8 | -1613.65 | -24945.55 |
| 12 | -0.9485 | -21.8336 |
| 16 | 0.6580 | 0.5672 |

The n=8 pathology is not caused by a vanishing preactivation variance (minimum
is `0.0346`) and persists after doubling samples. It is genuine cancellation
between repeated and all-distinct tensor sectors.

## Edgeworth correction

For preactivation mean `mu`, variance `sigma²`, and contracted cumulants,

```text
Delta3 = -k3 * mu * phi(mu/sigma) / (6 sigma^3)
Delta4 =  k4 * ((mu/sigma)^2 - 1) * phi(mu/sigma) / (24 sigma^3).
```

Material means `abs(Delta3+Delta4) >= 0.25` times within-case RMS. The subset
gets most signs right because the ReLU response factors and dominant cumulant
orientation are stable, but its magnitude errors make those signs unusable as
a quantitative closure.

## Recurrence obstruction

The oracle representation and a deployable recurrence are separate questions.
For k3, all output `iij` entries can be updated in O(n³) using products such as

```text
(W²)^T P W
(W * (P W))^T W.
```

Several k4 `iiij` terms also reduce to O(n³) matrix/Hadamard products. But the
generic `iijj` update contains

```text
R_rs = (w_r * w_s)^T Q (w_r * w_s)
```

for every output pair `(r,s)`. With generic dense Q and W, the available exact
contraction costs O(n⁴). No exact O(n³) or O(n³ log n) recurrence was derived,
and a low-rank/sketched Q would be a new approximation requiring its own oracle
gate. Thus deployability fails independently of representation fidelity.

## Conclusion

Pair-repeated cumulants are a good shallow diagnostic but not a deep closure.
The all-distinct sector supplies essential cancellation by depth 3-4. Do not
promote or sketch this state based on sign accuracy alone.

## Files

- `PREDECLARED_GATE.md`: frozen cases and gates.
- `pair_repeated.py`: tensor estimator, masks, compact state, contractions, and
  Edgeworth formula.
- `run_oracle.py` / `oracle_results.json`: nine-case oracle evidence.
- `convergence_audit.py` / `convergence_audit.json`: doubled-sample depth-four
  audit.
- `test_pair_repeated.py`: four exact tests.
- `structural_audit.py` / `structural_audit.json`: representation/recurrence
  separation.
- `finalize_decision.py` / `decision.json`: final conjunction and hashes.
