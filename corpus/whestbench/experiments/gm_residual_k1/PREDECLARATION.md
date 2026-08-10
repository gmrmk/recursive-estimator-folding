# PREDECLARATION — gm_residual_k1 (graveyard revival falsifier)

Written BEFORE any experiment code. Mining search key: `m157_selfhosted_formal_pilot`.
Worker id: `gm_residual_k1`. Date: 2026-08-10.

## 0. Deviations declared UP FRONT (loud, not absorbed)

- **D1 — driver reimplemented, worker frozen.** The frozen runner
  `run_m160_hostile_audit.py` hardcodes its raw output directory to
  `HERE/"raw_workers"` (inside the frozen experiment dir) and hardcodes the
  k=5 gate. Writing there would breach my write firewall. I therefore write my
  own driver `gm_k1_driver.py` in THIS directory. The measurement code
  `m160_cp311_worker.py` is invoked **unmodified, from its original path**,
  via `runpy.run_path(..., run_name="__main__")` inside a thin
  affinity-setting launcher. No frozen file is edited, copied-and-mutated, or
  imported in a mutated form. Gate constants are copied verbatim
  (`258.4e9`, `512.0 MiB`, `4.0 s`, `20.0 s`).
- **D2 — original path, not the published copy.** The worker resolves
  `PINNED_SITE_PACKAGES = HERE.parents[1]/"whest-v014"/"Lib"/"site-packages"`.
  In the publish tree (`corpus/whestbench/experiments/...`) that resolves to a
  nonexistent dir; only the original
  `work/scorefloor_generation/terra_m160_hostile_deploy/` resolves. Verified
  byte-identical (`diff` clean) between publish copy and original. The
  original is read-only to me.
- **D3 — interpreter.** The worker hard-asserts CPython 3.11. The
  task-named `work/whest-v014/Scripts/python.exe` is 3.14.4 and cannot run it.
  I use `C:\Users\strid\.local\bin\python3.11.exe` (3.11.15, resolves to the
  same uv interpreter recorded in the 2026-08-07 run's `runtime` block) with
  the same pinned flopscope 0.10.0 site-packages and `C:\tmp\m160-cp311-deps`
  numpy 2.4.6. This reproduces the frozen environment exactly; the 3.14
  interpreter is used only for my own analysis scripts.
- **D4 — ARM B is new.** ARM B (1 *logical* CPU) is not in the mined
  falsifier. It is declared here, before code, as a strictly-more-hostile
  non-binding stress probe. It cannot open a gate; it can only bound margin.
  ARM A alone decides the verdict.

## 1. What the original kill actually measured

M157 / M160 (and retroactively M145, M153, M163/M164) were killed on a
**projection**, not a measurement. Every structural, numerical, ordering,
replay, restoration, early-pruning and RSS gate PASSED in five fresh
CPython-3.11 workers. The sole binding failure was
`hostile_effective_compute_5x_residual = billed + 1e11 * 5 * residual_s`,
where the multiplier 5 is a REPORTED-level legacy convention whose stated
provenance is "prior official-runner measurements showed roughly 5x local
residual time for call-heavy candidates" (M145_DEPLOYABLE_STRUCTURAL_AUDIT
line 52), never re-measured.

## 2. Changed premise

Hosted grading of #326094 (2026-08-08, four days AFTER the flopscope 0.10.0 /
whestbench 0.14.0 residual-safeguard update, with the 1-physical-core
participant pin and lambda=1e11 already priced in) returned C/B 0.650 =>
hosted mean effective C 176.8e9, against a local metered mean of 178.5e9
computed at **k=1** (`billed + 1e11*residual`). Agreement 1.0%. A k=5 charge
would have projected 198-219e9 (C/B 0.73-0.80), 12-24% high. The hosted
residual multiplier is therefore OBSERVED at k ~= 1.0.

## 3. Mechanism / quantity under test

Effective compute charged **once**:

    C_k1(i) = billed_flops(i) + 1e11 * residual_s(i)          [k = 1]
    C_k5(i) = billed_flops(i) + 1e11 * 5 * residual_s(i)       [legacy k = 5]

against the locked safety gate **B_gate = 258.4e9** (the harness gate is
strict `worst < 258.4e9`).

Break-even multiplier for worker i:  k*(i) = (258.4e9 - billed_i) / (1e11 * residual_i).

## 4. Arms (exactly as mined, plus one declared non-binding probe)

- **STEP 0 (arithmetic, cached, zero compute).** Recompute C_k1 for the five
  2026-08-07 target workers from `M160_HOSTILE_AUDIT_20260807.json`. If the
  cached max C_k1 already exceeds 258.4e9, the revival is dead on arithmetic
  and I STOP without running anything.
- **ARM A (binding falsifier, exactly the mined one).** Re-run the five fresh
  CPython-3.11 target workers + the adversarial early-pruning worker from
  `terra_m160_hostile_deploy/m160_cp311_worker.py`, unmodified, same seeds
  (setup 160310001..160310005, mlp 160320001..160320005; early 160410001 /
  160420001), generated width-256 depth-32 He weights only, **with the
  1-physical-core participant pin** (process affinity mask = the two SMT
  logical processors of one physical core, mask empirically confirmed before
  the run). Charge residual once at lambda=1e11.
- **ARM B (declared, NON-BINDING stress probe).** Same five workers pinned to
  a single *logical* processor (mask 0x1) — strictly more hostile than the
  grader's convention. Reported to bound residual headroom. Cannot open or
  close the gate.

## 5. Predicted outcome — ON RECORD, before running

- STEP 0: passes. Cached k=1 values are
  196.660222962 / 210.352002450 / 189.772717074 / 181.583093776 / 179.675613472 (B).
  Max = **210.352002450B** < 258.4B, margin 48.047997550B = 18.60%,
  break-even k* = 3.8296 on the worst worker.
- ARM A: the 1-core pin inflates residual (adverse direction, and that is the
  point of the test). I predict the inflation factor stays **below 2.5x**, so
  worst-worker residual **<= 0.45 s** and worst **C_k1 <= 240e9**; all five
  target workers pass 258.4e9; all structural assertions pass; peak RSS
  < 512 MiB.
- ARM B: strictly higher residual than ARM A; I predict worst C_k1 still
  < 258.4e9 but with materially thinner margin.
- `billed_flops` is deterministic and must reproduce the 2026-08-07 values
  BITWISE per seed; `prediction_sha256` must match the cached run per seed.

## 6. KILL CONDITION (exact)

**KILLED** if, in ARM A, `max_i C_k1(i) >= 258.4e9` over the five target
workers — equivalently if the worst worker's residual exceeds
`(258.4e9 - billed_i)/1e11`, which for the 2026-08-07 worst worker
(billed 193.371731851e9) is **0.650282682 s**.

Also KILLED (independently, reported as such) if any structural assertion in
the frozen worker fails, or peak RSS >= 512 MiB, or any worker fails to
complete — i.e. if the re-run does not reproduce M160's own PASSED gates.

No retuning past a failed gate. If ARM A kills, I report KILL_CONFIRMED and
stop; I do not soften the pin, change seeds, or fall back to the unpinned
configuration.

## 7. Two-signal verification for any PASS

1. **Independent recomputation.** C_k1 recomputed in the analysis script
   directly from raw `billed_flops` and `residual_s`, compared to the worker's
   own `effective_compute` field. Must agree to < 1e-6 relative.
2. **Bitwise repeat / cross-run reproduction.** Per seed, my fresh
   `prediction_sha256` and `billed_flops` must equal the cached 2026-08-07
   `raw_workers/target_*.json` values, and the worker's own second predict
   must be bitwise equal to its first. The second predict also supplies an
   INDEPENDENT residual draw per worker; its C_k1 is evaluated against the
   same gate.
3. **Already-in-hand external signal (from the mining record).** Hosted
   #326094 C/B 0.650 => 176.8e9 vs local k=1 metered mean 178.5e9 (1.0%).

## 8. Firewall

Generated He weights only. No truth, labels, reference, MSE, scorer,
leaderboard, submission, network, login, or git. No reads or imports of
m245_*/M243/M244/journal-m245*. Writes confined to
`corpus/whestbench/experiments/gm_residual_k1/`. Phase-1 selection is frozen
and untouched by this result.

## 9. Compute envelope

~90 minutes. Cached 2026-08-07 unpinned run: ~3.2-4.0 s per predict, 2 predicts
per worker, 6 workers. A 1-core pin at, say, 6x slowdown gives ~50 s/worker
=> ~5 min/arm. If ARM A alone exceeds the envelope I return BLOCKED with the
measured per-worker wall time rather than silently scaling down; a documented
reduction of ARM B (non-binding) is acceptable if needed.
