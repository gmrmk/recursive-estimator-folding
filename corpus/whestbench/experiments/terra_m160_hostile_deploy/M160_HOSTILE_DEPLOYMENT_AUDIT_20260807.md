# M160 hostile deployment audit of M157 -- 2026-08-07

## Disposition

**FAIL CLOSED — response-free structural audit only.** Five independently
spawned CPython-3.11 workers completed and all numerical/ordering/restoration
checks passed, but two of five generated target-shaped traces exceed the
historical `258.4B` ceiling when the measured residual is projected at the
required hostile `5 x 1e11 FLOP/s` rate. The maximum is `278,273,084,846.08`.
No truth, labels, reference output, error, scorer, competition data,
leaderboard, submission, or champion resource was opened or modified.

## Clean worker boundary

Each worker was a new local process running CPython `3.11.15`. NumPy `2.4.6`
was installed only in `C:\tmp\m160-cp311-deps`; after it loaded, the worker
appended the read-only project-pinned FlopScope `0.10.0+np2.4.6` path. It
provided only inert `SetupContext`, `BaseEstimator`, and `MLP` containers to
avoid importing the cached optional CPython-3.14 WhestBench dependency. All
MLPs were freshly generated dense `256 x 256`, depth-32 float32 weights.

## Five fresh target-shaped workers

| Worker (setup / MLP seed) | bill | residual (s) | effective C | hostile 5x C | peak RSS / private MiB | dispatch / FlopScope calls |
|---|---:|---:|---:|---:|---:|---:|
| 160310001 / 160320001 | 181,111,573,555 | 0.155486 | 196,660,222,961.99 | 258,854,820,589.96 | 379.910 / 832.102 | 666 / 1,043 |
| 160310002 / 160320002 | 193,371,731,851 | 0.169803 | 210,352,002,450.02 | 278,273,084,846.08 | 387.152 / 837.449 | 664 / 1,041 |
| 160310003 / 160320003 | 176,451,428,422 | 0.133213 | 189,772,717,073.79 | 243,057,871,680.93 | 368.688 / 824.641 | 667 / 1,044 |
| 160310004 / 160320004 | 167,601,393,926 | 0.139817 | 181,583,093,776.41 | 237,509,893,178.05 | 370.488 / 826.750 | 666 / 1,043 |
| 160310005 / 160320005 | 165,308,703,820 | 0.143669 | 179,675,613,472.02 | 237,143,252,080.09 | 368.887 / 827.211 | 664 / 1,041 |

The historical M145 memory gate was `PeakWorkingSetSize` (RSS), so all five
pass that specific `<512 MiB` condition. Peak private commit is nevertheless
recorded because it reaches `837.449 MiB`; this audit does not silently treat
it as equivalent to RSS or assume a private-commit ceiling absent a locked
rule. Maximum setup time was `1.583 s`; maximum first prediction wall time was
`4.032 s`, both within the historical `4 s` / `20 s` limits.

## Freeze/order/replay checks

For every target worker and the adversarial worker:

- both predictions were finite and byte-identical;
- the SHA-256 of the frame bank after each prediction exactly matched the
  pre-predict bank;
- no `pilot_surrogate:*` dispatch occurred and `cached_q0_reused_after_proposal`
  was true;
- the event sequence was exactly `formal_q0_pilot_materialized`, then
  `proposal_frozen_from_formal_q0_only`, then
  `main_transport_applied_after_proposal`;
- timing instrumentation independently agreed: q0 completed at `0.275–0.382 s`,
  proposal fit started immediately afterward, proposal froze at `0.301–0.415 s`,
  first transport applied at `0.311–0.429 s`, and Formal main began only at
  `0.350–0.487 s`.

## Adversarial early pruning

The adversarial generated MLP makes the first 32 second-layer columns
positive `1/256` and the remaining 224 negative `-1/256`. Since the first
ReLU state is nonnegative, this forces the Formal layer-2 pilot selection to
exactly 32 columns while retaining a nonempty computation path. The fresh
worker recorded that width as `32`; it was finite, replay-identical, fully
restored, proposal-frozen-before-transport, and used no dense surrogate. Its
first bill was `76,667,648,594`, residual `0.142003 s`, and hostile projection
`147,669,095,865.56`.

## Gate result

| Gate | Result |
|---|---|
| Five fresh target processes completed | pass |
| Finite/replay/order/restoration invariants | pass |
| Adversarial early-pruning invariant | pass |
| Historical peak-RSS `<512 MiB` | pass (max `387.152 MiB`) |
| Historical setup `<4 s`, predict `<20 s` | pass |
| Historical hostile `5x` effective C `<258.4B` | **fail** (2/5 exceed; max `278.273B`) |

M157 remains an isolated structural prototype. This audit grants no efficacy,
ranking, deployment, submission, or champion authority.
