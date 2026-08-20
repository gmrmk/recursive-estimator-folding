# M231 frozen disposition -- 2026-08-09

Status: `KILLED_FROZEN_NATIVE_RESOURCE_OR_LEDGER_GATE`

M231 changed exactly one M227 mechanism: its uncertifiable finite-float
priority/argsort selector was replaced by one counted independent-slice
`Generator.permuted(bank, axis=1)` call over an integer label bank.  The first
`k=32` labels in each layer are therefore an exact uniform subset without
replacement, with no tie state or unmetered uniqueness check.  M227's passed
three-product collision algebra remained unchanged.

For `S = diag(u) W`, `g = n/k`, and selected hidden-row set `H`, M231 forms

```text
that = g sum_(i in H) s_i^3
Ahat = g sum_(i in H) outer(s_i^2, s_i)
Ehat = g sum_(i in H) outer(s_i^3, s_i)
Dhat = g sum_(i in H) outer(s_i^2, s_i^2).
```

These Horvitz-Thompson totals enter M215's collision expression only affinely.
The live `p`, `B`, and `rho` totals remain exact.  Hence the emitted source

```text
Chat_strict = Cfull_M212 - Chat_collision
```

is unbiased for the strict source for every fixed generated rank-one state.
This is the partially conditioned two-part estimator frozen in M227/M231; it
is not claimed to be a generic Rao-Blackwellization of every collision-event
estimator.

## Passed receipts

- RED/GREEN contract and algebra suite: 6/6 passed.
- Five frozen seeds `227700001..227700005` ran in fresh sequential processes.
- Every trace was finite and matched the pinned FlopScope `0.10.0+np2.4.6`
  and NumPy `2.4.6` source hashes.
- The exact selector law, layer/epoch/domain binding, pathwise co-permutation,
  call counts, arithmetic bill, zero reshape calls, and AABB symmetry passed.
- M231's exact bill was `864,993,280` in all five processes.
- M212 + M231's exact arithmetic bill was `2,114,246,656` in all five.
- Maximum observed RSS was `228.46875 MiB`, below the frozen `512 MiB` cap.

The exact M231 bill was:

```text
arange                         1,024
broadcast                          0
permuted                      31,744
gather                     2,031,616
matmul                    767,950,848
multiply                   57,901,056
add                        36,569,088
sum                           492,032
copy                           15,872
reshape                             0
TOTAL                     864,993,280
```

## Binding failure

The frozen combined hostile-five wall cap was `3.227021568 ms`; M231's
incremental allowance after the frozen M212 maximum was
`2.025121700262334 ms`.

```text
combined residual mean       5.017620051512495 ms
combined residual maximum    5.171800119569525 ms
M231 residual maximum        4.049100098200142 ms
hostile maximum              4,700,146,715.784762
minimum budget margin         -972,389,275.7847624
```

Both `m231_wall_cap` and `combined_hostile_five_x_fits` failed in every
meaningful aggregate; all other frozen native gates passed.  The candidate is
therefore killed without retuning, batching, call changes, or threshold drift.

## Firewall and preserved result

G0 was not authorized or run, and no G0 result file exists.  M231 receives no
M151 compiler-retirement credit, source-efficiency credit, output-MSE credit,
score, submission, rank, prize, or winner claim.  What survives is the exact
integer-permutation receipt and the unbiased three-product row-total algebra;
their present native realization does not fit the frozen hostile-wall budget.

Machine-readable evidence is in `M231_NATIVE_RESULTS_20260809.json`; the five
per-seed receipts are `M231_NATIVE_TRACE_227700001.json` through
`M231_NATIVE_TRACE_227700005.json`.
