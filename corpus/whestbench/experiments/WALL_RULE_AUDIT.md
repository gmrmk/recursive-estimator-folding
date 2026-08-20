# Cleanroom audit: total wall time versus charged residual time

Date: 2026-08-06

## Scope and answer

This is a source-only and already-recorded-summary audit.  It does not open an
MLP row, target, truth array, raw score output, official API, or submission
path, and it does not modify a candidate.

**Answer:** the preallocated Strassen branch's `median total wall ratio <= 1.5`
condition is a campaign safety gate, not a WHestBench scoring rule.  The local
WHestBench 0.14.0 scorer never compares candidate wall time with parent wall
time.  It ranks a valid prediction using

```text
C = billed_FLOPs + 1e11 * residual_wall_time_s
score = MSE * max(0.1, C / B).
```

The extra time spent inside NumPy/BLAS is classified as
`flopscope_backend_time_s` and is excluded from `residual_wall_time_s` and
therefore from `C`.  FlopScope's own dispatch overhead is excluded too.  Total
wall time is not completely irrelevant: a prediction is zeroed if it crosses
an absolute timeout.  In the installed local subprocess path, the default host
response timeout is 30 seconds, while the in-worker cooperative context limit
is 60 seconds.  Thus the effective local default is the stricter 30-second
host limit, not a relative `1.5x` rule.

The strongest preallocated operator is consequently a legitimately reopened
screen, not a retroactive promotion.  A causally new descendant should retain
the same exact arithmetic operator but replace the unsupported relative-call
gate with predeclared **absolute whole-predict** and effective-compute gates.
It still needs a fresh full-entry runner screen; the current single-product
measurements do not prove a whole-entry timeout bound or an MSE result.

## What the installed code proves

### 1. Effective compute does not contain backend or total wall time

The single source of budget math is
`work/whest-v014/Lib/site-packages/whestbench/budget.py`:

- lines 3-6 define `C = F + lambda*R`, strict exhaustion `C > B`, and the
  `max(0.1,C/B)` multiplier;
- lines 13-24 set `lambda=1e11` and implement the formula;
- lines 27-44 implement the strict combined-budget test;
- lines 47-51 force the multiplier to 1 on failure.

The scoring path in
`work/whest-v014/Lib/site-packages/whestbench/scoring.py` confirms that this is
the value used in practice:

- lines 620-638 wrap `predict` in a `BudgetContext` and obtain analytical
  FLOPs;
- lines 762-789 deliberately prefer worker-reported backend, overhead, and
  residual timing for subprocess runs;
- lines 817-843 form `effective_compute` from only `flops_used` and
  `residual_wall_time_s`, then zero predictions if `C>B`;
- lines 862-899 form the score and record total wall only as a separate
  diagnostic/failure field.

FlopScope's decomposition is explicit in
`work/whest-v014/Lib/site-packages/flopscope/_budget.py`:

- lines 65-130 time a counted operation and attribute the actual NumPy call to
  backend time while putting in-wrapper work into FlopScope overhead;
- lines 270-278 measure the backend call itself;
- lines 643-707 define
  `wall = backend + overhead + residual`, with residual being the remainder
  outside backend and FlopScope accounting;
- lines 689-707 specifically identify user Python between operations, GC,
  uninstrumented NumPy, and callbacks as residual.

Therefore the branch report's `0.153100 s` versus `0.099056 s` total-call
comparison is not a score ratio.  Only the candidate's measured residual
`0.0004398 s`, its billed FLOPs, and the absolute timeout are scorer-relevant.

### 2. Total wall has absolute limits, not a parent-relative limit

There are two local timing boundaries:

1. `ContestSpec` defaults to `predict_timeout_s=30`,
   `wall_time_limit_s=60`, and no separate residual-time limit
   (`whestbench/scoring.py`, lines 53-68).
2. The subprocess runner waits only `predict_timeout_s` for the worker reply
   and terminates the worker on expiry (`whestbench/runner.py`, lines 312-334).
   It passes `wall_time_limit_s` into the worker at lines 260-281.

The worker constructs its own `BudgetContext` with that 60-second wall limit
and reports the complete timing split (`whestbench/subprocess_worker.py`, lines
37-46 and 50-112).  FlopScope checks the wall deadline before and after each
counted operation, so one backend call can overshoot until it returns
(`flopscope/_budget.py`, lines 39-61 and 756-785).  The host's response timeout
is the outer hard boundary in the local subprocess runner.

For completeness, setup is outside every per-MLP `BudgetContext`, but it is
not unbounded: the local lifecycle uses a 5-second default setup timeout
(`whestbench/runner.py`, lines 144-173), and subprocess startup waits under the
same limit (`whestbench/runner.py`, lines 260-307).  Candidate setup allocation
must therefore be screened separately.

### 3. The `1.5x` test is visibly local policy

`work/scorefloor_generation/preallocated_strassen_compression/PREDECLARED_GATES.md`
lines 64-70 require a full-product total-wall ratio `<=1.5`.  Neither the
installed scoring formula nor the runner contains that comparison.  It was a
conservative engineering gate intended to avoid a physically slow entry, and
it did useful work, but it was stricter than the competition rule.

The branch's existing synthetic report records:

- direct full product: `8.439201792B` billed, `0.099056 s` median wall;
- batched Winograd product: `7.427768320B` billed, `0.153100 s` median wall;
- billed ratio `0.880151`, effective-proxy ratio `0.885099`;
- candidate residual `0.0004398 s`;
- conservative peak memory `480.94 MiB`;
- depth-32 relative final discrepancy `2.74e-6` and two gate flips in
  4,194,304 activations.

These are at `REPORT.md` lines 11-23 and 92-126.  They prove the synthetic
single-product arithmetic, timing classification, parity, and memory results.
They do not prove a whole-estimator score.

## Whole-entry feasibility: proof versus inference

The current champion summary in
`work/scorefloor_generation/COMPRESSION_SCORE_CALCULUS_20260806.md`, lines
77-89, records mean analytical FLOPs `185.4069B`, of which `184.8217B`
(`99.6844%`) are matmul, across about `215.41` matmul calls.  Mean residual is
`0.16875 s`.  These aggregate numbers are used only as a frozen planning
ledger.

The preallocated child does **not** replace all 215 matmuls.  Its estimator
overrides only `_first_sample_matmul` and `_sample_matmul`
(`preallocated_strassen_compression/estimator.py`, lines 20-34).  At depth 32,
the frozen parent calls the first hook once and the loop hook 28 times
(`fold3_estimator.py`, lines 78-80 and 101-131), for at most 29 large-row
opportunities.  The batched dispatcher additionally falls back to direct for
odd contracted widths (`cost_model.py`, lines 100-123), so the realized count
is at most 29 and is generally lower.

The retained `estimator.py` currently instantiates the sequential
`PreallocatedWinograd`, not the stronger batched Mutation B (lines 16-17 and
23-34).  Wiring `BatchedPreallocatedWinograd` is therefore itself a prospective
child change.  Nothing in this audit silently changes the existing artifact's
identity or decision.

### Exact or algebraic bounds

- Non-matmul analytical work is `185.406853-184.821668 = 0.585185B`.
- If, unrealistically, every billed matmul received the full-product
  `0.880150576` ratio, analytical FLOPs would be
  `0.585185 + 0.880150576*184.821668 = 163.256083B`.  Thus `22.150770B` is an
  **opportunity ceiling**, not a forecast.
- The first hook always has shape `(32256,256)@(256,256)`.  The billing formula
  gives `4.219600896B` direct and `3.713884160B` batched, an exact analytical
  saving of `0.505716736B` before any residual charge.  This is the only
  shape-independent guaranteed arithmetic win from the available source.
- That first-call saving tolerates up to `0.005057 s` of incremental residual
  before its effective-compute benefit vanishes.

The direct matmul billing formula itself is source-defined as
`m*n*(2*k-1)` (`flopscope/_flops.py`, lines 217-234) and the preallocated
batched Winograd bill is source-defined in `cost_model.py`, lines 30-39 and
100-123.  Those arithmetic statements do not depend on machine timing.

### Timing inferences, not proofs

From the reported effective ratio, the representative direct residual is
about `25.10 us`; the batched candidate's incremental residual is therefore
about `0.4147 ms`, a `0.04147B` charge per full candidate call.  Applying that
increment to all 29 possible hooks would add about `0.0120 s` residual, or
`1.203B` effective compute.  This extrapolation is favorable, but active and
ragged shapes have not been timed as a whole trace.

The representative backend slowdown is `0.153100-0.099056 = 0.054044 s` per
full product.  Even the deliberately pessimistic median extrapolation of 29
full-size slowdowns adds only `1.567 s`.  The already-recorded 100-entry
champion campaign took `510.063 s` total, about `5.101 s` per MLP including
harness effects (`random32256_paired100/REPORT.md`, line 134).  Adding the
full-size median extrapolation gives roughly `6.668 s` per MLP: about 22% of
the local 30-second subprocess timeout and 11% of the 60-second in-context
limit.

That is strong feasibility evidence, **not a hard upper bound**.  Medians are
not maxima, timings need not be monotone for ragged BLAS shapes, setup time is
separate, and the 510-second suite time includes work outside individual
predict contexts.  A proof-grade deployment decision requires an actual
whole-predict timing distribution under the official one-core runner shape,
with an absolute margin predeclared before measurement.

For score planning, a useful envelope is:

```text
best arithmetic ceiling (all matmul compressed):  -22.151B
29-call residual extrapolation:                    +1.203B
optimistic net effective-compute change:          -20.948B
optimistic mean-C ratio:                  about 181.334/202.282 = 0.8964
```

The opposite safe statement is only that the first call saves `0.5057B`
analytically; without a measured whole trace, extra residual could offset some
or all of that.  The likely gain lies between those extremes and cannot be
narrowed honestly from the current aggregate ledger.

## Legally and mathematically justified next descendant

Yes: a causally new descendant is justified because the newly isolated failed
link is the **validation rule**, not the Winograd algebra.  This does not
retroactively turn Mutation B into the champion.  The descendant should be
predeclared as follows:

1. Keep the immutable random32,256 parent, exact nodes, pruning decisions, and
   batched preallocated Winograd operator.
2. Replace the relative `candidate_wall/direct_wall <= 1.5` test with an
   absolute whole-predict gate.  Using the installed local runner semantics, a
   conservative gate such as setup `<4 s`, every predict `<20 s`, and zero
   30/60-second timing failures leaves explicit margin.  The exact margin is a
   campaign choice, not a claimed contest constant.
3. Retain the real score gates: `C<B` on every case, a strict maximum-C safety
   margin, and `r_C*r_MSE<1` with a predeclared safety factor.
4. First run a fresh synthetic full-entry trace to measure setup, whole-predict
   wall, residual, analytical bill, memory, numerical parity, and tails.  Do
   not infer the whole result from one GEMM.
5. Only if that passes, authorize a separately frozen matched development
   score gate to test the small float32-reassociation effect.  No locked row is
   needed for the engineering screen.

This descendant is within the published estimator interface and FlopScope
accounting model: all arithmetic remains visible, no backend bridge or hidden
worker is introduced, and slower backend execution is treated exactly as the
runner specifies.  The honest conclusion is **reopen and whole-entry screen**,
not **promote**.
