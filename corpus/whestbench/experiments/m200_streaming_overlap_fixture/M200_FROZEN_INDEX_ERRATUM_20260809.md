# M200 frozen index erratum (before code or execution)

The predeclaration's symbol `L` is ambiguous. Freeze the following target
semantics before implementation:

- `H` denotes the number of fourth-order source/ReLU layers;
- the screen uses `H in {3,4,5,6}` and exactly `H+1` weight matrices;
- the WHestBench target has `H=31` source layers and a distinct terminal
  matrix `W_32`;
- at source layer `k`, M172 binds to **`W_k` and `V_{k-1}`**;
- M179 computes
  `a_k = mu_{k-1} W_k`, `C_k = W_k^T V_{k-1} W_k`,
  `J_k`, `mu_k`, and `V_k`;
- M198 consumes exactly `(a_k, C_k, mu_k)` and emits post-ReLU source tangent
  `s_k`;
- for `k>1`, the accumulated tangent from layer `k-1` is transported through
  exactly `W_k,J_k` and then `s_k` is injected;
- after `k=1..H`, `W_{H+1}` performs one explicit charged terminal response;
  it has no Source211 injection.

Frozen counts per generated cell are therefore:

```text
H       M179 background/source-layer steps
H       fixture packets, M198 conversions, and source injections
H-1     internal tangent transports
1       terminal W_(H+1) response
H+1     total weights
```

All other M200 gates remain unchanged. This is a pre-execution clarification,
not post-result retuning.
