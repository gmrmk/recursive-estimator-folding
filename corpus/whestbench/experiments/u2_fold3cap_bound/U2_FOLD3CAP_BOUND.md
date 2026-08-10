# U2 — fold3cap residual-billing inflation bound (static analysis)

Date: 2026-08-10. Owner-directed uncertainty U2 (gates Door A's canary read).
Static code analysis only: no estimator run, no submission, no truth/scorer.
Sole compute used: a microbench of the FROZEN flopscope v0.14 library function
`budget_summary_dict` on synthetic accumulator records, to calibrate one cost
constant (see `calib_summary_cost.py`). The estimator itself was never run.

## One-line verdict

NEEDS-FIX before any multi-net graded canary. `budget_summary_dict()` adds
**exactly zero** to billed FLOPs (F) and does **not** corrupt the cap's n_eff
selection, but its wall time lands in the scored **residual** channel (λR) and
**grows with process history**. On a full single-process suite the last nets
absorb up to ~0.30 s (~3.0e10 FLOP-equivalent, ~11 % of B) — the same order as
the entire cap headroom (B−CAP = 2.72e10) — which can flip a typical near-CAP
fold3 net into a `C>B` budget failure (zero-prediction), reintroducing the exact
breach mode the cap exists to remove. Fix is one line.

---

## 1. Located code path (line citations)

**Candidate:** `corpus/whestbench/experiments/t3_fold3_deterministic_cap/capped_fold3.py`

- `_tally()` — the history-dependent accessor:
  - `capped_fold3.py:259-264`
    ```python
    @staticmethod
    def _tally() -> int:
        try:
            return int(flops.budget_summary_dict()["flops_used"])
        except Exception:
            return 0
    ```
- Three `_tally()` calls, all inside `_simulate_cap_sets`:
  - `capped_fold3.py:275` `t0 = self._tally()`            (before diagonal pass)
  - `capped_fold3.py:278` `dp_cost = self._tally() - t0`   (after diagonal pass)
  - `capped_fold3.py:413` `sim_cost = self._tally() - t0`  (after the full cap sim)
- `_simulate_cap_sets` is invoked from `predict()`:
  - `capped_fold3.py:421` `loop_dims, fold, dp_cost, sim_cost = self._simulate_cap_sets(mlp)`
- …and `predict()` then runs the real estimator through `super().predict`:
  - `capped_fold3.py:452-456` (inside the `try`, still inside the metered context).

**Frozen library (installed artifact, ground truth):**
`work/whest-v014/Lib/site-packages/flopscope/_budget.py`

- `budget_summary_dict` snapshots ALL process records and re-aggregates them:
  - `_budget.py:1199-1228` — builds `acc_copy._records = _snapshot_records()` then
    `acc_copy.get_data()`.
- `get_data` collects every OpRecord across every recorded context and iterates them:
  - `_budget.py:1142-1165` — `all_ops.extend(rec.op_log)` (line 1145) then
    `_summarize_operations(all_ops)` (line 1165). Cost = O(total ops in history).
- `_summarize_operations` is a pure-Python dict aggregation, one pass per op:
  - `_budget.py:500-504` + `_update_operation_summary` `_budget.py:482-497`.
- `_snapshot_records` returns the process-global accumulator plus the ACTIVE
  context's unrecorded ops:
  - `_budget.py:1185-1196`.
- Every graded net's context is appended to the process-global accumulator on exit:
  - `_budget.py:995` `_accumulator.record(self)` inside `BudgetContext.__exit__`.
- Residual = wall − backend − overhead (the billed-time formula):
  - `_budget.py:539`.

**Scoring (installed artifact):**
`work/whest-v014/Lib/site-packages/whestbench/`

- Canonical cost law: `budget.py:14-51`
  - `C = F + λ·R`, λ = 1e11 FLOP/s; multiplier `max(0.1, C/B)`; `C>B ⇒ failure`.
- Per-MLP + aggregate: `scoring.py:573-581` (`s_m = mse × multiplier`), mean over MLPs.
- One persistent process over the whole suite (no reset between nets):
  - `scoring.py:611-627` (in-process loop), `subprocess_worker.py:141-219`
    (persistent stdin worker, a fresh `BudgetContext` per predict at line 66),
    `runner.py:221-370` (`SubprocessRunner` = one `Popen`, many predicts).
  - `concurrency.py` is BLAS-thread control only — no net sharding.
- The scorer reads the worker's full `residual_wall_time_s` (which includes the
  `_tally` overhead) and forms `C`: `scoring.py:782-838`.

---

## 2. Is the call billed, does it grow with history, is it inside predict()?

| question | answer | evidence |
|---|---|---|
| (a) charged to **billed FLOPs** (`flops_used` / F)? | **NO — exactly 0** | `budget_summary_dict`→`get_data`→`_summarize_operations` is pure Python; it never calls `_charge_op` or any `flopscope.numpy` wrapper. F is untouched. |
| (a′) charged to the scored **residual** (λR)? | **YES** | `_tally` is plain Python, not wrapped by `_counted_wrapper`/`_OpTimer`/`_call_numpy`, so no time is attributed to backend or overhead; residual = wall−backend−overhead (`_budget.py:539`) therefore absorbs it in full. |
| (b) grows with process/call history? | **YES** | cost = O(total OpRecords in history); history = accumulator (all prior nets, appended at `_budget.py:995`, never reset) + current predict's ops (`_snapshot_records`, `_budget.py:1185-1196`). |
| (c) inside the metered `predict()` path? | **YES** | called at `capped_fold3.py:275/278/413` inside `_simulate_cap_sets`, invoked from `predict()` at line 421, all inside the worker's `with budget_ctx:` (`subprocess_worker.py:72`). |

Key consequence: the inflation is invisible to the T3 gates. `run_t3_gates.py:136-152`
records only `ctx.flops_used` (F) and used a non-binding `METER_BUDGET=1e15`; it
never reads `residual_wall_time_s`. The gates are structurally blind to this channel.

Corollary: the cap's **n_eff selection is clean**. It compares the pure-billed-FLOP
model `C_pred` (op-walk, `capped_fold3.py:125-250`) to `CAP=244.8e9`. Because the
F-channel inflation is exactly 0, `budget_summary_dict` does not perturb `C_pred`,
`n_eff`, or the G1/G3 bitwise-identity results. The problem is entirely in the λR
term of the FINAL scored `C = F + λR`, which the cap does not model.

---

## 3. The bound

Calibrated constant (measured, `calib_summary_cost.py`, flopscope v0.14, this box):
`budget_summary_dict` costs **c_py ≈ 0.50 µs per accumulated OpRecord**
(496 ns/op marginal; stable 495–544 ns/op over 2e3…2e5 ops — clean linear O(n)).
Convert to FLOP-equivalent: `λ·c_py = 1e11 × 5.0e-7 = 5.0e4 FLOP-equiv per op-iteration`.

Structural inputs (labeled estimate; settling check = sum of call-counts in
`ctx.summary_dict()["operations"]` on one metered predict):
- `O_full` ≈ **2000** OpRecords per full capped predict (band [1500, 2500]):
  diagonal pass ~600–900 over 32 layers + 28 pruning layers + 3 fold layers +
  31-layer tangent recursion + the cap-sim replay. (Static op-walk of
  `fold3_estimator.py`/`base_estimator.py` + `capped_fold3.py:266-414`.)
- Within-predict op-iterations for the 3 calls (all K): ~1900
  (call1≈0, call2≈700 [after diagonal pass], call3≈1200 [after cap sim]).
- Cross-net op-iterations for net K in a single-process suite: `3·(K−1)·O_full`.

Per-net injected residual and effective-compute inflation:

```
R_inj(K)  = c_py · [ 3·(K−1)·O_full + 1900 ]      seconds
ΔC(K)     = λ · R_inj(K) = 5.0e4 · [ 3·(K−1)·O_full + 1900 ]   FLOP-equiv
```

| case | residual injected | ΔC (FLOP-equiv, λR channel) | as % of B=2.72e11 |
|---|---|---|---|
| **F (billed-FLOP) channel — any K** | 0 | **0 (exact)** | 0 % |
| **LOWER**: single-net canary / K=1 / process-recycled | ~0.95 ms | **9.5e7 (~1e8)** | 0.035 % |
| K=50 (last of a 50-net single-process suite) | ~0.15 s | 1.48e10 | 5.4 % |
| **UPPER**: K=100 (last of a 100-net single-process suite) | ~0.30 s | **2.98e10 (~3.0e10)** | 10.9 % |
| UPPER with O_full band [1500,2500] | — | [2.2e10, 3.7e10] | 8 – 14 % |

Two-signal check on the constant: the analytic per-call structure (one Python
dict pass over `all_ops`, `_budget.py:500-504`) predicts O(n) with a sub-µs slope;
the microbench independently measures 0.50 µs/op, flat across two decades of n.
Both agree, and neither could be fooled by the other.

---

## 4. Adjusted-score delta at B = 2.72e11

Per-MLP: `s_m = mse_m · max(0.1, C_m/B)` (`scoring.py:573-581`). Above the 0.1
floor, the residual raises the multiplier by `ΔC(K)/B` and thus `s_m` by the same
relative amount. Typical fold3 nets sit at F/B ≈ 0.893 (G1 metered: 2.43e11/2.72e11),
well above the floor, so the delta applies directly.

- **Late single net (K=100):** multiplier +0.110 → that net scored ≈ +12 %
  worse than the mechanism deserves (0.110 / 0.893).
- **Suite-mean (100-net single process), no failures:** mean_K ΔC(K)/B =
  (5.0e4·3·O_full/B)·mean(K−1) = 1.10e-3 × 49.5 ≈ **+0.055** to the mean
  multiplier ⇒ adjusted suite score ≈ **+6 % worse** than deserved.
  (50-net suite: mean(K−1)=24.5 ⇒ +0.027 ⇒ ≈ +3 % worse.)
- **Catastrophic tail (the real hazard):** the cap trims every net to F ≤ CAP =
  0.9B, leaving headroom B−F ≥ 0.107B ≈ 2.9e10. Failure (`C_m>B`,
  `scoring.py:830-838`) occurs once the history residual exceeds that headroom:
  `3·(K−1)·O_full·λ·c_py ≥ 2.72e10 ⇒ K ≳ 92` (O_full=2000). A **typical** near-CAP
  fold3 net (F/B≈0.89) placed at position ≳92 in a single-process suite breaches B,
  gets multiplier 1.0 and a zero-prediction — `s_m = mse(zeros)`, order 1e-6…1e-5,
  which swamps the family's ~1.4e-7 adjusted score when averaged in. This is
  precisely the "5/100 budget failures … erased the family's gain" mode named in
  `T3_PREDECLARATION.md` ("The failure this fixes"), re-entering through the
  residual side door on the tail of the suite.

---

## 5. Recommendation for Sol / the canary

**Apply the one-line fix before any canary that is more than a handful of nets in
one process.** The graded C the canary returns will be worse than `C_pred`
predicts by an amount that (i) is unmodeled by the cap, (ii) is invisible to the
T3 gates, and (iii) depends on the net's position in the suite — so a raw canary
grade cannot be interpreted without first removing this term. Given a one-line fix
versus a mis-read or failed canary, fix first.

**The fix** (swap the history-scanning accessor for an O(1) current-context read):

```python
@staticmethod
def _tally() -> int:
    from flopscope._budget import get_active_budget   # O(1) live counter
    b = get_active_budget()
    return int(b.flops_used) if b is not None else 0
```

Why this is correct and behavior-preserving:
- `BudgetContext.flops_used` is an O(1) property (`_budget.py:617-619`); no history
  scan ⇒ residual inflation drops to ≈0 (nanoseconds).
- The cap only ever uses **deltas** within a single predict (`sim_cost`,
  `dp_cost`). During one predict the accumulator is constant (records are appended
  only at `__exit__`, `_budget.py:995`), so `Δ(budget_summary_dict flops_used) =
  Δ(active-context flops_used)` exactly. The deltas — and hence `n_eff`, G1, G2,
  G3 — are unchanged. This matches the coherence claim in `T3_BUILD_NOTES.md:119-122`.

Note on the discourse pointer: the literal symbol `current_budget()` does **not**
exist in the pinned flopscope v0.14 (grep = 0 matches in the package). The dipam
note's intent maps to the v0.14-present O(1) accessor above
(`get_active_budget().flops_used`); a literal `flops.current_budget()` call would
`AttributeError`. Sol should use `get_active_budget().flops_used`.

Score error if NOT fixed, quantified: adjusted suite score inflated by ≈ +3 %
(50-net) to ≈ +6 % (100-net) absent failures, plus a step to catastrophic
(one or more zero-prediction failures, each ~1e-6…1e-5 into the mean) for near-CAP
nets past suite position ~92 in a single process. If the canary is instead a
single net or a process-recycled harness, the error is ≤ 0.035 % of B (≈1e8
FLOP-equiv) and the cap reads clean — but that benign case is not guaranteed by
the code paths read here, which all run one process per suite.

---

## 6. Deviations / scope notes (recorded loudly)

- One number was obtained by MEASUREMENT, not pure static reading: the 0.50 µs/op
  constant, via a microbench of the frozen `flopscope.budget_summary_dict` on
  synthetic OpRecords (`calib_summary_cost.py`). This exercises the library only;
  the fold3 estimator was never invoked, nothing was submitted, no truth/scorer
  touched. Treated as the second independent signal for the analytic O(n) claim.
- `O_full ≈ 2000` ops/predict is a labeled static estimate (band 1500–2500); the
  upper bound scales linearly with it. Settling check: read
  `ctx.summary_dict()["operations"]` call-count sum on one metered predict.
- I did not observe the ORGANIZER's exact private-canary harness (external). The
  "single process per suite / no reset" conclusion is derived from the installed
  whestbench runner/worker/scoring code, which is what a local canary uses; the
  private harness is assumed to match (labeled assumption). The recommendation is
  robust to this because the fix is free and the downside of leaving it is a failed
  or uninterpretable canary.
- Firewall honored: writes confined to this dir; `m243_*/m244_*/m245_*/*_fable_oracle`
  untouched; all estimator/experiment/library source read-only.

## Files
- `U2_FOLD3CAP_BOUND.md` (this file)
- `u2_findings.json` (structured verdict)
- `calib_summary_cost.py` (flopscope-only cost calibration harness)
