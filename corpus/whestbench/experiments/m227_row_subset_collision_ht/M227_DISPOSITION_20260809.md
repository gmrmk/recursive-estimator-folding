# M227 disposition -- killed by frozen tie-detection ledger omission

Date: 2026-08-09.

Status: **KILLED_FROZEN_NATIVE_LEDGER_TIE_DETECTION_OMITTED**.

No challenge weights, response, truth, scorer, leaderboard, submission, or
champion artifact was accessed. No G0 source-efficiency cell was opened. The
five frozen fresh-process traces were not run.

## What passed and is preserved

The response-free algebra survived:

- six tests passed over generated widths 3 through 9;
- exhaustive subset averages matched exact M215 strict subtraction and the
  M205 cubic oracle within the frozen `2e-10` tolerance;
- every tested draw matched an independent row-loop oracle;
- hidden-label permutation with the receipt co-permuted, positive ReLU gauge,
  zero factor, duplicate/out-of-range refusal, and explicit tied-priority
  refusal passed;
- exact live `p,B,rho` plus HT-only `t,A,E,D` remained unbiased. No fourth
  sampled `Bhat` product was introduced.

The proposed arithmetic circuit also hit its predicted meter exactly in the
target generated unit:

```text
M227 billed FLOPs             865,484,288
matmul calls                            2
matmul product-equivalents              3
multiply/add/sum/copy calls        16/9/1/1
reshape calls                            0
nominal incremental persistence   36.873046875 MiB
nominal M212+M227 persistence     138.955078125 MiB
```

Three native unit tests and the single generated trace-harness contract passed
after a bookkeeping-only correction to avoid double-counting M227 workspaces.
Observed `aabb` asymmetry was `8.673617379884035e-19`, within the frozen
`2e-10` algebra tolerance.

These are component facts, not deployment credit.

## Fatal mismatch

The predeclaration requires all of the following simultaneously:

1. one float64 Philox priority per hidden row;
2. one `argsort` and one gather as the complete selector ledger;
3. fail-closed detection of every equal-priority receipt;
4. no unmetered runtime data operation and exact `865,484,288` billed FLOPs.

FlopScope 0.10 `argsort` returns rank indices only. It does not return a tie
flag or sorted key values. Detecting equality therefore requires an additional
key gather plus comparison/reduction, or a host-side observation of priority
values. The implemented diagnostic used
`np.asarray(priorities).tolist()` and a Python `set`. Although its time enters
residual wall, it observes runtime array values outside the declared metered
operation path. That does not satisfy the frozen circuit/firewall.

Adding a gather/compare/reduction would change the exact call and bill ledger.
Removing the check or breaking ties by row index would violate the frozen
SRSWOR/pathwise-covariance contract. Retuning after seeing the mismatch is
forbidden. Therefore the fixed M227 implementation is killed even though the
non-tie arithmetic bill and algebra passed.

## What was not run or credited

- no five-process native gate;
- no hostile-wall or integrated-RSS promotion result;
- no G0, G1, or holdout source-efficiency result;
- no `3.727757440B` M151 compiler retirement credit;
- no MSE, score, submission, rank, prize, or winner claim.

## Lawful next mutation

A child must be predeclared before code. The cleanest repair is a supported
Philox random-permutation receipt whose output is already a unique rank packet,
with its exact FlopScope bill, call count, wall, and pathwise co-permutation
audited before reuse of the passed row algebra. Alternatively, explicitly bill
the extra sorted-key gather and equality reduction. Neither repair belongs to
M227, and neither inherits its resource pass because M227 has none.

