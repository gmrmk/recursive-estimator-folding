# M231 predeclaration -- exact permuted row receipt for M227 algebra

Date: 2026-08-09. Frozen before any M231 implementation, M231 test, M231
native trace, or source-efficiency readout. Generated-only and response-free;
challenge weights, responses, truth, scorer, leaderboard, submissions, cached
outcomes, and champion artifacts are forbidden.

## Failed-parent fold and one changed mechanism

M227's exact live-`p/B/rho`, sampled-`t/A/E/D` algebra passed, and its
non-tie arithmetic hit the predicted meter. M227 was nevertheless killed:
float64 priorities plus `argsort` cannot detect ties using its frozen calls,
and the host `tolist/set` check observed runtime values outside the declared
metered path.

M231 changes exactly one mechanism: the row-subset receipt. It replaces

```text
float64 Philox priorities -> argsort -> undeclared tie observation
```

with

```text
unique integer label bank -> Philox Generator.permuted(axis=1) -> first 32.
```

Everything else is inherited unchanged from M227:

- `n=256`, `L=31`, `k=32`, float64 source arithmetic;
- exact live M212 `p`, `B`, and `rho`;
- one shared subset for only `t`, `A`, `E`, and `D`;
- three rectangular product-equivalents in two matmul calls;
- M151's independent fixed-`q0`, `K=128` strict residual;
- physical collision owners, Source211 slots, and the one existing linear
  M125b carrier;
- algebra, resource, G0/G1/holdout seeds, metrics, and thresholds;
- no M151 compiler-retirement credit without an integrated ABI trace.

No priority values, tie rule, host uniqueness scan, `choice` loop, adaptive
`k`, response dual, fourth `Bhat` product, or nonlinear source use is allowed.

## Pinned primitive and law audit

Pinned environment:

```text
FlopScope 0.10.0+np2.4.6
NumPy 2.4.6
Python 3.14 Windows runtime: work/whest-v014
```

Installed source evidence:

1. FlopScope registry entry `random.Generator.permuted` is a counted random
   method with `cost_formula="numel(input)"` and movement-op dtype handling.
2. The pinned NumPy docstring states that `permuted(x,axis=1)` shuffles each
   slice along axis 1 independently, unlike `shuffle`.
3. The counted wrapper calls NumPy's base generator once and returns the
   resulting array under one metered `random.Generator.permuted` operation.
4. A pinned generated probe on shape `(31,256)` produced 31 unique row
   permutations in one call. The observed exact bill was `31,744`, i.e. four
   meter units per integer bank element. There is no dtype multiplier because
   `permuted` is registered as a movement method.

Pinned source hashes:

```text
flopscope/_registry.py
  D735DA7D36ECF05BA7B927452DB126FE297E33398F3903C59B886E1BC1228795
flopscope/numpy/random/_cost_formulas.py
  D14D86A2CA0700C0899318A9C7CD3F08E91AC80948682225D383D71E2D628F8F
flopscope/numpy/random/_counted_classes.py
  6D7AA1E9C4F7A135EF7487FAF6B645AEA61C74983FA780DAFFB68240C6DA3F0D
numpy/random/_generator.cp314-win_amd64.pyd
  69C5AA9B41C0A60EE8600A4C1434C86FA96DFC00F4CD3171AED9729AACAA549B
```

For each layer, the bank is exactly `(0,1,...,255)`. A permutation contains
every label once; therefore its first 32 labels are a uniform 32-subset with
no replacement and no possible tie. Independent per-layer slices give the
required product law. For every fixed row quantity `h_i`, inclusion
probability remains `32/256`, so the M227 Horvitz-Thompson proof is unchanged.

If any pinned hash, operation name, one-call behavior, per-layer independence,
or unique-permutation property changes, M231 fails closed before algebra.

## Frozen receipt ownership and covariance

The caller creates one counted base vector with
`fnp.arange(256,dtype=int64)` and one free broadcast view of shape `(31,256)`.
The bank is immutable and bound to canonical layer IDs `1..31`, producer
epoch, width, and domain `M231_ROW_PERMUTED_V1`. One counted
`Generator.permuted(bank,axis=1)` materializes the full integer rank receipt;
the metadata slice `[:, :32]` is the selected label set.

The receipt, not a rerun at row positions, is the random input. Under a hidden
label permutation, rows and selected labels co-permute. A test must transform
the receipt by the inverse position map and recover the identical Source211
draw. Rerunning a position-based selector after permuting weights is forbidden.

The M151 residual stream retains its existing domain and is independent.
No seed replacement, state-dependent permutation, optional retry, or receipt
mutation is allowed.

## Frozen algebra

M231 imports the passed M227 row algebra without change. With
`S=diag(u)W`, exact

```text
p = S^T 1,  B = S^T S,  rho = diag(B),
```

and selected rows `H`, `|H|=32`, use `g=8`:

```text
that = g sum_(i in H) s_i^3
Ahat = g sum_(i in H) outer(s_i^2,s_i)
Ehat = g sum_(i in H) outer(s_i^3,s_i)
Dhat = g sum_(i in H) outer(s_i^2,s_i^2).
```

Substitute these four totals into M215's affine collision formula while
retaining exact `p/B/rho`, then emit

```text
Chat_strict = Cfull(M212) - Chat_collision.
```

For every fixed state,

```text
E[Chat_strict]=Cstrict,
E[Chat_strict + Rhat_D]=T_D.
```

The precise classification remains a finite-population HT row estimator with
partial/conditional Rao-Blackwell ancestry only for an expressly matched
row-anchor sampler of the `t/A/E/D` part. No generic collision-HH dominance
is claimed; exact M215 remains the zero-row-variance endpoint.

## Frozen exact FlopScope 0.10 bill

The M227 non-selector circuit is unchanged. The killed priority+argsort cost
`523,776` is replaced by the inclusive counted bank/permutation cost `32,768`.

```text
operation                            calls      exact billed FLOPs
arange(256,int64)                       1               1,024
broadcast_to(31,256)                    1                   0
random.Generator.permuted(axis=1)       1              31,744
take_along_axis selected S, f64         1           2,031,616
matmul (3 product-equivalents)          2         767,950,848
multiply                               16          57,901,056
add                                     9          36,569,088
sum                                     1             492,032
copyto                                  1              15,872
reshape                                 0                   0
TOTAL                                              864,993,280
```

Composed conditional envelope:

```text
M212                                1,249,253,376
M231                                  864,993,280
M212+M231                           2,114,246,656
retired M151 compiler envelope      3,727,757,440
raw remainder                       1,613,510,784
combined hostile-five wall cap       3.227021568 ms
M231 wall left after M212 maximum     2.025121700 ms
```

If and only if a later integrated ABI trace proves the complete old
`3.727757440B` M151 compiler absent, the conditional branch arithmetic is
`88.095125456B`, saving `1.613510784B` from M151. This predeclaration grants
no retirement credit. Every surviving old map, pointwise step, copy, carrier,
allocation, and wall cost is charged in full.

## Frozen memory and hostile wall

The full integer permutation receipt is the same `0.060546875 MiB` rank
packet already reserved by M227; selected values, powers, and A/E workspaces
are unchanged. The broadcast bank is a view of one transient 256-int64 base
vector (`0.001953125 MiB`). Therefore:

```text
incremental persistent              36.873046875 MiB
incremental nominal peak            36.875000000 MiB
M212+M231 nominal persistent       138.955078125 MiB
integrated RSS cap                 512.000000000 MiB
```

Nominal payload is not peak-RSS credit. Five fresh target processes use the
unchanged state seeds `227700001..227700005`. Each must be finite,
bill-identical, below 512 MiB RSS, and satisfy

```text
M212_bill + M231_bill
  + 5 * 1e11 * combined_residual_wall_s
  <= 3,727,757,440.
```

M231-only residual wall must be at most `2.025121700262334 ms` when paired
with M212's frozen maximum. A cold primitive microprobe, local wall estimate,
or theoretical payload cannot replace the five integrated traces.

## Frozen RED/GREEN order

No M231 code or test exists at predeclaration time. Implementation may start
only with RED tests, in this order:

1. **Primitive/receipt.** Pinned hashes match; exactly one independent unique
   permutation per layer; every selected set has 32 unique in-range labels;
   layer/epoch/domain mismatch fails closed; co-permutation is pathwise; no
   tie/value scan, argsort, random float key, or 31-call loop exists.
2. **Algebra.** Reuse M227's widths `3..9`, seeds `227003..227009`, subset
   sizes `{1,min(3,n-1)}`, cubic parity, row-loop parity, gauge, zero, and
   `2e-10` tolerances without change.
3. **Native.** Exact calls/bills above, no cubic tensor/triple loop/fourth
   product/reshape, finite symmetric slots, nominal ledger, five frozen fresh
   processes, hostile wall, and RSS all pass.
4. **Only then G0.** Reuse M227's exact source baseline, cells, seeds,
   bootstrap, p99, slopes, and thresholds. No G0 runner or result may exist
   before steps 1 through 3 pass.

## Inherited source-efficiency firewall

The M151 comparator remains exact strict control plus the unchanged
independent `K=128` residual. The arithmetic-only break-even and one-percent
conditions are recomputed only for M231's frozen cost; no empirical threshold
changes:

```text
G = (88.095125456 / 89.708636240) * (V_R/128 + V_S)/(V_R/128).
```

G0 uses the exact same 24 fresh cells, bootstrap seed `2270001`, 20,000
cell-cluster resamples, `upper90<0.99`, every cell `<1`, p99 ratio `<=1.25`,
and nonpositive width slopes. G1 uses state seeds `22732001..22732104`, event
seeds `22733001..22733008`, 16,384 events/cell, and bootstrap seed `22730001`.
The untouched holdout remains `22732201..22732308` with event seeds
`22734001..22734016`. No M161 diagnostic cell becomes promotion evidence.

The inherited M227 predeclaration and manifest are pinned at:

```text
M227_PREDECLARATION_20260809.md
  3AB6046CB88A26BD22FC390EBDF96DD1DB87750BE751B7EDE158D66D1E8E39A9
M227_FROZEN_MANIFEST_20260809.json
  B29D095F089F41AED66FCEBAF7066AB1038EAC462EE43C6FDFD9DDFCF000A6CA
m227_row_subset_collision_ht.py
  8CBF8724FFC5B3A8C0285DDFDB92630CFA4BA8E2C3EF0DF7CD4CD9A50DE09D7A
```

## Stop and credit rule

Any pinned-law, uniqueness, covariance, binding, bill, call, wall, memory,
algebra, or source-efficiency failure kills fixed M231. Do not fall back to
priorities, `choice`, 31 permutations, host uniqueness scans, or threshold
retuning. Preserve the exact permutation receipt law and passed row algebra
as separate facts.

A native pass grants only a generated resource component and permission to
open the already-frozen G0. It grants no compiler-retirement, final-output
MSE, score, submission, rank, prize, or winning-entry claim.

