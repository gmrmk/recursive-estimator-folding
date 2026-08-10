# VERDICT — gm_residual_k1

Graveyard revival falsifier for `m157_selfhosted_formal_pilot` /
`m160_hostile_selfhosted_pilot_audit` (retroactively `m145_defensive_acg_transport`,
`m153_exact_formal_prefix_reuse`). Run 2026-08-10. Predeclaration: `PREDECLARATION.md`.

## Gate result: INCONCLUSIVE. No revival gate opens; the original kill stands.

The predeclared binding arm FAILED its gate. I report that plainly and I did
not retune it. But the same session then proved the arm's instrument was
confounded in the adverse direction by a factor far larger than the effect it
was measuring, so the failure cannot be attributed to the mechanism. The
honest label is INCONCLUSIVE, and the practical consequence is identical to a
kill: nothing opens, the M157/M160 deployment configuration stays rejected.

## DEVIATIONS (all predeclared except D5-D7)

- **D1** driver reimplemented in this dir (frozen runner writes inside the
  frozen dir and hardcodes the k=5 gate); frozen worker `m160_cp311_worker.py`
  invoked UNMODIFIED via `runpy` from a thin affinity launcher.
- **D2** worker run from its original `work/scorefloor_generation/...` path
  (the publish copy's relative `PINNED_SITE_PACKAGES` does not resolve); the
  two copies verified byte-identical.
- **D3** CPython 3.11.15 used (worker hard-asserts 3.11); the task-named
  `whest-v014/Scripts/python.exe` is 3.14.4 and is used only for analysis.
- **D4** ARM B declared before code as a non-binding hostility probe.
- **D5 (new, post-hoc)** **ARM B WAS NOT RUN.** ARM A already failed the gate;
  ARM B is strictly more hostile and explicitly non-binding, so it could only
  deepen a failure it cannot change. Skipping it saved ~40 min of the envelope.
- **D6 (new, post-hoc)** A diagnostic (`diag_threadpool.py`) was added AFTER
  ARM A, as the predeclared "attack the conclusion" step. It is not an arm, it
  cannot open a gate, and it did not alter ARM A's numbers. It changed the
  verdict's confidence label from KILL_CONFIRMED to INCONCLUSIVE.
- **D7** `threadpoolctl` is absent from the pinned CPython-3.11 deps, so the
  BLAS pool size is inferred from measured throughput plus
  `OPENBLAS_NUM_THREADS` response, not read directly. Label: derived.

## STEP 0 — cached arithmetic gate at k=1 (zero compute). PASSED.

Re-derivation of M160's five 2026-08-07 target workers at
`C = billed + 1e11 * residual` (k=1) against the locked 258.4e9 gate. This is
the deliverable the item guidance asks for.

| worker | billed (B) | residual (s) | **C at k=1 (B)** | C at k=5 (B) | break-even k | k=1 | k=5 |
|---|---|---|---|---|---|---|---|
| 1 | 181.111573555 | 0.155486 | **196.660222962** | 258.854820590 | 4.9707 | PASS | FAIL |
| 2 | 193.371731851 | 0.169803 | **210.352002450** | 278.273084846 | 3.8296 | PASS | FAIL |
| 3 | 176.451428422 | 0.133213 | **189.772717074** | 243.057871681 | 6.1517 | PASS | PASS |
| 4 | 167.601393926 | 0.139817 | **181.583093776** | 237.509893178 | 6.4941 | PASS | PASS |
| 5 | 165.308703820 | 0.143669 | **179.675613472** | 237.143252080 | 6.4796 | PASS | PASS |

- **k=1: 5/5 PASS.** Worst = 210.352002450B, margin 48.047997550B = **18.60%**
  of the gate; worst-worker break-even multiplier **k\* = 3.8296**.
- k=5: 3/5 PASS, worst 278.273084846B — reproduces the ledger's recorded
  "maximum 278.273084846B, 2/5 exceed" exactly, which validates my recomputation
  against the frozen record.
- The mined revival's arithmetic claim is therefore CONFIRMED on the frozen
  measurement basis.

## ARM A — fresh five-worker re-run, 1-physical-core pin (mask 0x3). GATE FAILED.

Physical-core mask measured via `GetLogicalProcessorInformation` (8 physical
cores, SMT pairs `[0,1] [2,3] ...`), not assumed.

| worker | billed (B) | residual (s) | **C at k=1 (B)** | C at k=5 (B) | k\* | k=1 | resid x vs 08-07 |
|---|---|---|---|---|---|---|---|
| 1 | 181.111573555 | 0.984526 | **279.564203589** | 673.374723724 | 0.7850 | **FAIL** | 6.33 |
| 2 | 193.371731851 | 0.891580 | **282.529771691** | 639.161931050 | 0.7294 | **FAIL** | 5.25 |
| 3 | 176.451428422 | 0.342081 | **210.659528438** | 347.491928500 | 2.3956 | PASS | 2.57 |
| 4 | 167.601393926 | 0.213586 | **188.959993809** | 274.394393343 | 4.2511 | PASS | 1.53 |
| 5 | 165.308703820 | 0.201763 | **185.485033851** | 266.190353976 | 4.6139 | PASS | 1.40 |

- **max C at k=1 = 282.529771691B > 258.4B. k=1 pass count 3/5. Predeclared
  kill condition FIRED** (worst residual 0.984526 s vs the 0.650282682 s
  ceiling on worker 2's bill).
- k=5 on the same fresh data: **0/5 pass**, max 673.374723724B.
- Early-pruning adversarial worker: billed 76.667648594B, residual 0.294837 s,
  C_k1 106.151368730B, all structural invariants PASS, layer-2 width 32.
- Structural invariants: **5/5 workers PASS all assertions**; peak RSS max
  386.1 MiB < 512 MiB. Setup gate 4.0 s **FAILED** (172.87-285.30 s) and the
  20 s predict gate **FAILED** on worker 2 (35.65 s) — both are the confound's
  fingerprint, not a property of the estimator.

## Two-signal verification (all four PASSED)

1. **Independent recomputation** — `C_k1` recomputed in the analysis layer from
   raw `billed_flops` and `residual_s` matches every worker's own
   `effective_compute` field to < 1e-6 relative. Same for the k=5 field on the
   cached run.
2. **Bitwise cross-run reproduction** — for all five seeds, my fresh
   `billed_flops` and `prediction_sha256` equal the 2026-08-07
   `raw_workers/target_*.json` values exactly. The arithmetic half of the
   estimator is bit-identical across three years of harness drift; only the
   wall-clock residual moved.
3. **Within-worker replay** — first and second predictions bitwise equal in
   5/5 workers.
4. **Independent residual draw** — the second predict of each worker is a fresh
   residual sample; at k=1 it passes 5/5 (max 255.157B), i.e. even under the
   confounded pin the failure is not reproducible run-to-run within a process.

## The attack that landed: ARM A's instrument was confounded

Counter-hypothesis tested: ARM A's residual inflation is not the participant
pin but BLAS thread-pool oversubscription. `os.cpu_count()` still reports 16
under the pin, so OpenBLAS sizes a 16-thread pool and spin-contends on 2
logical CPUs.

Measured sgemm (1024^3 f32, x10), replicated twice:

| configuration | GFLOP/s (run 2) | GFLOP/s (run 1) |
|---|---|---|
| unpinned, default pool | 244.388 | 195.782 |
| **pinned 0x3, default pool (= ARM A)** | **1.717** | **1.428** |
| pinned 0x3, `OPENBLAS_NUM_THREADS=1` | 74.327 | 69.160 |
| pinned 0x3, `OPENBLAS_NUM_THREADS=2` | 66.298 | 78.249 |
| unpinned, `OPENBLAS_NUM_THREADS=1` | 63.207 | 71.913 |

- Slowdown ARM A actually inflicted: **142.36x**.
- Slowdown a faithful 1-physical-core pin costs: **3.29x**.
- Throughput recovered purely by sizing the pool to the affinity, at the SAME
  affinity: **43.30x**.

Worker-level corroboration (ARM A vs 2026-08-07): setup inflated
**116.4x-191.6x**, backend 3.56x-9.88x, overhead 1.48x-5.78x, residual
1.40x-6.33x. A 3.29x hardware reduction cannot produce a 192x setup. And the
grader does not throttle the backend at all — FLIP_READINESS_20260810 records
"the dominant term is flopscope backend time, which the grader gives 7 cores",
with hosted residual max 0.137 s = 5.0% of budget.

So ARM A measured "one physical core with a 16-thread BLAS pool thrashing on
it", which is not the deployment condition. Its residuals are inflated by an
artifact roughly 43x larger than the effect under test.

## Disposition

- The mined revival's **arithmetic** is confirmed exactly: at k=1 the frozen
  M160 workers pass 258.4B 5/5 with 18.60% worst-case margin and k\* = 3.83.
- The mined **falsifier** — fresh re-measurement under the 1-core pin — did not
  return a usable answer, because the local emulation of the pin is not
  faithful. The predeclared arm failed; the instrument is disqualified.
- **Nothing opens.** M157/M160/M145/M153 stay killed. No Phase-1 artifact,
  submission, or selection is touched.
- The settling experiment a future worker should PREDECLARE (I did not run it,
  because running it now would be retuning past a failed gate): re-run the same
  five workers at mask 0x3 with the BLAS pool sized to the affinity
  (`OPENBLAS_NUM_THREADS=2`), which reproduces the grader's arrangement far
  more closely, and evaluate the identical k=1 / 258.4e9 gate. Expected cost
  ~10 min. Until that runs, the claim "the k=1 residual charge makes this family
  deployment-legal" sits at DERIVED-from-frozen-data, not OBSERVED-under-pin.

## Files

- `PREDECLARATION.md`, `VERDICT.md`, `results.json`
- `step0_arithmetic_gate.py`, `step0_results.json`
- `topology_probe.py`, `topology.json`
- `pin_launch.py`, `gm_k1_driver.py`, `arm_A_results.json`, `raw_arm_A/*.json`
- `diag_threadpool.py`, `diag_threadpool_mask*_pool*.json`
- `build_results.py`

Firewall honored: generated He weights only; no truth/scorer/holdout/private
reads, no network, no submission, no git, no m245/M243/M244 contact; all writes
inside this directory.
