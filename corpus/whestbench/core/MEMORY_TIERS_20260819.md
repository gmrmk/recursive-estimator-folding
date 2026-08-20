# MEMORY THREE-TIER RETIREMENT — the four ceilings, what retires, and the debt

Stamped: 2026-08-19T09:30:03Z (`date -u`). Wave item W0.2 of
`core/MI_SOLVE_20260819.md` §4 (authority for this document).

Compliance: `experiments/fold_floor_splice`, `experiments/frame_completion_129`
and `cells/` were read only, never written. Every python invocation used
`-B` with `PYTHONDONTWRITEBYTECODE=1`, and touched only `fold_ledger.json`
arithmetic — no harness, no FlopScope, no estimator ran.

Evidence tags: **[OBS]** read or executed this session; **[DER]** arithmetic from
tagged observations, shown; **[REP]** a corpus document or prior stage says so.

---

## 0. Headline

The mi-solve's ten-second upgrade is **discharged: the 65,536-MiB limit is
confirmed first-hand at all three cited lines** [OBS]. Two corrections came out
of the check, and both matter more than the confirmation:

1. **The enforced tier is not enforced on this campaign's own platform.**
   `subprocess_worker.py` reaches RLIMIT_AS through `import resource`, a
   POSIX-only module absent from this machine's interpreter; the failure path
   writes a stderr warning and continues. The default runner is `local`, which
   never attempts the limit at all. On the box that produced the ledger, **no
   memory ceiling was ever mechanically enforced** [OBS/DER].
2. **The "512-MiB relic" is a ladder, not a value.** Executable campaign code
   carries self-imposed walls at **464, 480, 496 and 512 MiB** [OBS]. Two of
   the four kills the mi-solve prices against the 512 relic (idx 71, idx 80)
   are priced against **480**, and both carry an independent non-memory kill
   leg that survives any memory retirement [OBS].

Net effect on the plan: unchanged in direction, sharper in scope. Retiring the
relic buys exactly what the mi-solve predicted — **the champion lineage's
1.445-MiB margin becomes 545.445 MiB** [DER] — and buys nothing on idx 48/70,
for the reasons recorded in §2.

---

## 1. The four tiers, with provenance

| # | Tier | Value | Status | Provenance |
|---|---|---|---|---|
| 1 | Campaign relic | 464 / 480 / 496 / **512** MiB | **RETIRED** by the 2026-08-19T06:12Z owner ruling | Self-imposed; never a contest rule [REP] |
| 2 | Engineering ceiling | **1 GiB** (1024 MiB) | **RULED** — the operative bar | Owner ruling 2026-08-19T06:12Z; deliberately tight [REP] |
| 3 | Mechanical limit | **65,536 MiB** | **VERIFIED FIRST-HAND** — the only limit any code enforces | Frozen venv, three lines below [OBS] |
| 4 | Contest environment | **64 GB** | Advertised | `HOSTED_INTEL_20260808.md:52`, official facts panel [REP] |

Tiers 3 and 4 are the same physical quantity: 65,536 MiB = 64 GiB, against an
advertised 64 GB. Tier 3 is what the installed harness writes; tier 4 is what
the organizer advertises.

### 1.1 The ten-second check, executed — verbatim lines

Frozen venv `C:/Users/strid/.venvs/whestbench-frozen-m178`
(CPython 3.14.4, whestbench 0.14.0; the three files share mtime
2026-08-07 18:24:29 local) [OBS].

`whestbench/cli.py:389-397` — the default resource limits:

```python
def _default_resource_limits() -> ResourceLimits:
    return ResourceLimits(
        setup_timeout_s=5.0,
        predict_timeout_s=30.0,
        memory_limit_mb=65_536,
```

(line 393 is the `memory_limit_mb` line; the constructor continues with a FLOP
budget, a CPU-time field and `wall_time_limit_s=60.0`.)

`whestbench/scoring.py:64` — the contest spec default:

```python
    memory_limit_mb: int = 65_536
```

`whestbench/subprocess_worker.py:161-174` — the sole `setrlimit` in the package:

```python
                # Enforce memory limit before loading participant code. If the
                # platform doesn't expose RLIMIT_AS (e.g., Windows, some BSDs),
                # write a warning to stderr; the host-side LocalRunner already warns.
                memory_limit_mb = request.get("memory_limit_mb")
                if memory_limit_mb is not None and memory_limit_mb > 0:
                    try:
                        import resource as _resource

                        limit_bytes = int(memory_limit_mb) * 1024 * 1024
                        _resource.setrlimit(_resource.RLIMIT_AS, (limit_bytes, limit_bytes))
                    except (ImportError, ValueError, OSError, AttributeError) as e:
                        sys.stderr.write(
                            f"[worker] could not setrlimit RLIMIT_AS={memory_limit_mb}MB: {e}\n"
                        )
```

**Only setrlimit in the package** — a case-insensitive grep for
`setrlimit|RLIMIT` across `whestbench/` returns exactly these three lines plus
one docstring reference at `runner.py:141` [OBS]. This upgrades the claim from
REPORTED to **OBSERVED**, as the mi-solve's §4 W0.2(i) required. It independently
reproduces `uf1_mem_verdict.json`'s `enforced_ceiling.evidence` block line for
line [OBS], giving the two-signal agreement.

### 1.2 The correction: tier 3 does not bind on this platform

Three observations, each independently checkable:

- **`--runner` defaults to `local`** — `cli.py:1119` `default="local"`;
  the dispatch at `cli.py:2805` is
  `runner = LocalRunner() if normalized_runner == "local" else SubprocessRunner()` [OBS].
- **`LocalRunner` never attempts the limit.** `runner.py:138-143`:

```python
        if limits.memory_limit_mb > 0:
            _LOGGER.warning(
                "memory_limit_mb=%d is advisory in --runner local: enforcement requires "
                "--runner subprocess (uses RLIMIT_AS) or external sandboxing (cgroups).",
                limits.memory_limit_mb,
            )
```

- **`SubprocessRunner` cannot reach RLIMIT_AS here.** `resource` is a Unix-only
  stdlib extension. Two independent signals [OBS]: a recursive search of
  `C:/Python314` for any `resource` module returns only `importlib/resources`,
  `multiprocessing/resource_sharer.py`, `multiprocessing/resource_tracker.py`
  and `test/test_resource.py` — no top-level module and no `.pyd`; and the
  import itself was executed directly:

```
$ python -c "import resource"
ModuleNotFoundError: No module named 'resource'
```

  `import resource` therefore raises, is caught by the `ImportError` arm at
  line 171, and the worker proceeds unlimited with a stderr warning. This is
  **observed, not inferred**.

**Consequence** [DER]: on this Windows host, at the default runner, memory is
enforced by nothing. `uf1_mem_verdict.json` states "This is the only memory
ceiling mechanically enforced anywhere in the installed harness" — true as
written about *which* ceiling exists in code, and its own recorded interpreter
is a Windows path (`work/whest-v014/Scripts/python.exe`), so the RLIMIT_AS path
could not have fired during that audit either. Nothing in the campaign's
measured record depended on enforcement: every memory verdict in the ledger was
produced by *measuring* peak working set and comparing in the experiment's own
Python, not by an OOM.

**What this does and does not change.** It does not weaken the ruling — the
1-GiB engineering ceiling is a self-discipline bar and needs no enforcement to
be policy. It does mean tier 3 is a **contest-environment** fact (POSIX grader,
subprocess runner) rather than a local safety net, so a local run that breaches
1 GiB fails silently rather than loudly. That is exactly the hole §4's
`windows_job_memory.py` wiring closes.

---

## 2. Consequence table — which killed records' memory walls retire

Peaks and kill clauses read first-hand from
`headroom/fold_ledger.json` (`candidates[]`, 276 records) [OBS].

| idx | id | wall | measured peak | retires at 1 GiB? | binding legs |
|---|---|---|---|---|---|
| 48 | `integrated_batched_winograd` | 512 | 667.328 MiB | **YES** (+155.328 over wall; 356.672 under 1 GiB) | **memory only** — 7/8 gates pass, ratio .941206 |
| 70 | `kerdock126_formal_l1_transplant` | 512 | 536.898 MiB | **YES** (+24.898 over wall) | **memory only** — geometry, arithmetic, parity, cost all pass |
| 71 | `kerdock_structured_wht_memory_folds` | **480** | 525.633 / 601.543 MiB | wall yes, **record no** | memory **AND** residual .564209 s / .437650 s vs a .30 s clause |
| 80 | `m81_full129_pareto` | **relative margin** | increment 1.75195 MiB vs 1.44531 MiB margin | wall yes, **record no** | margin **AND** raw-MSE leg: reduction must exceed 2.3256% to improve adjusted score |

Two corrections to the mi-solve's §4 W0.2 source line [OBS]:

- **idx 71's clause is 480 MiB, not 512**: verbatim, *"Any peak at least480MiB,
  residual above.30s, parity/structure/bill/hash failure, or score-data access."*
  Both rungs breach the residual clause as well (.564209 and .437650 against
  .30). Retiring every memory tier leaves idx 71 killed. The mi-solve reaches
  the same disposition ("idx 71 is NOT rescued") by citing only the memory
  clause; the residual leg is the stronger reason.
- **idx 80's kill_condition carries no numeric MiB at all**: it is
  *"Persistent memory increment exceeds the frozen hosted margin…"* — a
  relative test against M71's frozen margin, crossing the 480-MiB safety gate.
  Its raw-MSE leg is independent and unaffected by any tier ruling.

### 2.1 The value note — reviving 48/70 buys nothing

- **idx 48 → nothing.** idx 50 `row_blocked_winograd` (status `screened`)
  reaches the *same* analytical endpoint — both records read
  `analytical 170.531B -> 159.493B` — at peak **474.301 MiB**, already under
  every tier [OBS]. The saving is banked; only the liveness layout died.
- **idx 70 → nothing.** idx 72 `m71_kerdock126_one_buffer_owned_l1`
  (`screened_survivor`) strictly dominates it: peak lower by **58.343 MiB**,
  analytical lower by **3.318B**, conservative C lower by **7.390B** [DER from
  the two records' figures]. idx 70's own result says the same in words —
  *"no package or score replication is justified."*

### 2.2 The payoff — the champion lineage's OOM risk retires

This is the item worth banking. idx 72's measured peak is **478.555 MiB**
against its own **480-MiB** clause [OBS]:

| Ceiling | Champion margin |
|---|---|
| self-imposed 480 clause | **1.445 MiB** |
| relic 512 | 33.445 MiB |
| **ruled 1 GiB** | **545.445 MiB** |
| enforced 65,536 MiB | 65,057.445 MiB |

`480 − 478.555 = 1.445` [DER] — the same 1.44531-MiB margin idx 80 was killed
for crossing, and the margin `kerdock_v3` / `v3.1` inherit. A 1.445-MiB
headroom on a 478-MiB process is an OOM waiting for any allocator or BLAS
version change; **545.445 MiB is not**. Retiring the relic converts the
champion's most fragile engineering property into a non-issue at zero compute.

Cross-check from an independent measurement [REP, `uf1_mem_verdict.json`]:
`uf1` measured the champion first-hand on a synthetic He net at **452.312 /
452.691 MiB**, more favourable still — margins of 571.688 / 571.309 MiB under
1 GiB [DER]. The two measurements bracket the champion between roughly 452 and
479 MiB; both are comfortable under the ruled ceiling and neither is comfortable
under 480.

### 2.3 The door this opens

idx 58 `two_axis_fused_winograd` (`screened`) peaks at **492.441 MiB** with a
111.453-MiB workspace [OBS]. Headroom under the relic was **19.559 MiB**;
under the ruled ceiling it is **531.559 MiB** [DER]. This is the memory
precondition for door W3.1 (`kerdock_host_depth2_schedule_r1`), and it is now
clear.

### 2.4 Records whose memory wall never bound

Scanning all 276 records, **15** carry a numeric memory wall in
`kill_condition` — at 512 (10), 464 (3) and 480 (2) [OBS]. For these, memory
was measured and passed; the kill came from elsewhere. No tier ruling touches
them:

| idx | id | wall | measured peak | actual kill |
|---|---|---|---|---|
| 42 | `exact_sampler_rectangular_strassen` | 512 | 496.125 MiB (under) | wall ratios 5.28x / 6.20x / 14.51x |
| 117 | `m116b_inplace_streamed_l3_b2048` | 464 | 186.582 MiB | residual .6105131132 s vs .170 s |
| 118 | `m116c_inplace_streamed_l3_b4096` | 464 | 205.109 MiB | residual .3284645767 s vs .170 s |
| 155 | `m157_selfhosted_formal_pilot` | 512 | 387.152 MiB | hostile projection 278.273B vs 258.4B gate |
| 162 | `m164_exterior_native_audit` | 512 | 81.34 MiB | residual wall 9.456–10.639 ms vs 7.149 ms |

Residual, not memory, is the campaign's real resource wall. That is the same
conclusion the mi-solve reaches from the H0 twin pair (§2 F3), arrived at here
from the kill clauses instead.

---

## 3. RETIREMENT DEBT — every executable 512-class predicate, marked

Located by grepping the corpus myself rather than trusting the mi-solve's list
[OBS]. **The mi-solve's inventory is incomplete**: it names m216:67, m217:39,
m145 test:272 and seven `rss_below_512_mib` aggregates — 10 sites.

Two counts, because they measure different things [OBS]:

- **36 sites across 29 files** contain a literal `464`/`480`/`496`/`512` on a
  line carrying a memory token, under `corpus/whestbench/**/*.py`, excluding
  the relic-pricing instrument and the fenced tree. This count is mechanical
  and reproducible.
- **Plus the named-constant usage sites** — lines that gate on `RSS_CEILING`,
  `MEMORY_CAP`, `PEAK_GATE_MIB`, `RSS_CAP_MIB` or `HISTORICAL_RSS_LIMIT_MIB`
  without repeating the literal. These are where the wall actually fires, and
  a literal-only scan misses every one of them. They are listed alongside their
  declarations below.

Four distinct wall values are in force: **464, 480, 496, 512**.

Every entry below is **RETIRED-BY-RULING** (2026-08-19T06:12Z): the predicate
encodes a wall that is no longer campaign policy. Marked here, in this document,
**without editing any of the cited files** — the frozen experiment cells and
their receipts stay byte-identical, and their recorded verdicts remain valid
*as of their own date and convention*. A future agent re-deriving a memory
verdict from any of these lines is re-deriving a dead gate.

### 3.1 `rss_below_512_mib` aggregate predicates — RETIRED-BY-RULING

| File | Line | Predicate |
|---|---|---|
| `experiments/m169_m163_call_fusion/aggregate_m169_results.py` | 72 | `"rss_within_512_mib": all(... <= 512.0 ...)` — note the name is `rss_within_`, not `rss_below_` |
| `experiments/m209_batched_recursive_gram_control/aggregate_m209_results.py` | 67 | `"rss_below_512_mib": all(row["peak_working_set_mib"] < 512.0 ...)` |
| `experiments/m210_level_fused_recursive_gram/aggregate_m210_results.py` | 59 | same form |
| `experiments/m211_explicit_packed_level_fusion/aggregate_m211_results.py` | 51 | same form |
| `experiments/m212_backend_packed_explicit_symmetry/aggregate_m212_results.py` | 49 | same form |
| `experiments/m215_rankone_collision_correction/aggregate_m215_results.py` | 68 | same form |
| `experiments/m218_selective_l2_strassen/aggregate_m218_results.py` | 77 | `"resource_rss_below_512_mib": ... resource_peak_rss_mib < 512.0` |
| `experiments/m227_row_subset_collision_ht/aggregate_m227_results.py` | 93 | `<= 512.0` — **not in the mi-solve's list** |
| `experiments/m231_exact_permuted_row_receipt/aggregate_m231_results.py` | 106 | `<= 512.0` — **not in the mi-solve's list** |

### 3.2 Named ceiling constants — RETIRED-BY-RULING

| File | Line | Site |
|---|---|---|
| `experiments/m216_antithetic_distinct_provider/m216_antithetic_distinct_provider.py` | 67 | `RSS_CEILING = 512 * 1024 * 1024` |
| " | 685 | `"memory_pass": 0 < peak_rss <= RSS_CEILING` |
| " | 686 | `"pass": effective <= COMPONENT_CEILING and 0 < peak_rss <= RSS_CEILING` |
| `experiments/m217_balanced_three_color_strict_control/run_m217_native_trace.py` | 39 | `MEMORY_CAP = 512 * 1024 * 1024` |
| " | 133 | `"memory": peak <= MEMORY_CAP` |
| `experiments/gm_residual_k1/gm_k1_driver.py` | 30 | `HISTORICAL_RSS_LIMIT_MIB = 512.0` |
| " | 216 | `"historical_512MiB_peak_rss": worst_rss < HISTORICAL_RSS_LIMIT_MIB` |
| " | 236 | that gate ANDed into the driver's overall pass |
| `experiments/terra_m160_hostile_deploy/run_m160_hostile_audit.py` | 16 | `HISTORICAL_RSS_LIMIT_MIB = 512.0` |
| " | 146 | `worst_rss is not None and worst_rss < HISTORICAL_RSS_LIMIT_MIB` |
| " | 175 | `"peak_rss_mib": HISTORICAL_RSS_LIMIT_MIB` reported as the bar |
| " | 179 | string: *"Peak private commit is reported, but the historic M145 512 MiB …"* |
| `experiments/m235_setup_shared_philox_row_receipt/run_m235_native_process.py` | 38 | `RSS_CAP_MIB = 512.0` |
| " | 558 | `prediction["rss_mib"] < RSS_CAP_MIB` |

### 3.3 Test assertions — RETIRED-BY-RULING (these fail loudly if a future run legitimately exceeds the dead wall)

| File | Line | Assertion |
|---|---|---|
| `experiments/m145_defensive_acg/test_m145_defensive_acg.py` | 272 | `assert cost["memory_crosswalk"]["projected_peak_mib"] < 512.0` |
| `experiments/m145_defensive_acg/test_m145_integrated.py` | 188 | `assert candidate[...]["peak_working_set_mib"] < 512.0` — **not in the mi-solve's list** |
| " | 189 | same for `comparator` — **not in the mi-solve's list** |
| `experiments/m235_setup_shared_philox_row_receipt/test_m235_native_contract.py` | 92 | `self.assertLess(prediction["rss_mib"], 512.0)` |
| `experiments/m237_writeahead_native_receipt/test_m237_durable_transport.py` | 181 | `self.assertIn("memory_limit_mb=512", live_source)` — **the worst of the set**: a source-text assertion that pins the literal `512` into the live source, so removing the dead wall breaks the test |
| `experiments/m196_m151_b1_gate/test_m196_contract.py` | 25 | `"512 MiB"` as a required contract token |

### 3.3b Feasibility checker and in-source comments — RETIRED-BY-RULING

| File | Line | Site |
|---|---|---|
| `experiments/m196_m151_b1_gate/check_m196_feasibility.py` | 74 | `and payload.get("peak_mib", float("inf")) <= 512.0` — a live feasibility gate, **not in the mi-solve's list** |
| `experiments/m145_defensive_acg/m145_integrated_estimator.py` | 170 | comment: *"both lifetime classes live would violate the 512 MiB setup gate"* |
| " | 174 | comment: *"exceeded the integrated 512 MiB peak once pilot/main lifetimes met"* |
| `experiments/m145_defensive_acg/m145_deployable_estimator.py` | 178 | same comment text |

The three m145 comments are not predicates, but they sit in **estimator source**
and state the dead wall as a live design constraint in the present tense. A
grep of the aggregate scripts finds the predicates; a reader of the operator
finds these. They are named here for that second path, even though nothing
executes them.

### 3.4 Harness limits passed as 512 — RETIRED-BY-RULING

These override the harness default, setting the *enforced* limit down to the
dead relic. On a POSIX grader with `--runner subprocess` they would bind for real.

| File | Line | Site |
|---|---|---|
| `experiments/m235_setup_shared_philox_row_receipt/run_m235_native_process.py` | 448 | `memory_limit_mb=512` |
| `experiments/m236_layer_batched_m212_m235/run_m236_native_process.py` | 336 | `memory_limit_mb=512` |
| `experiments/m237_writeahead_native_receipt/run_m237_native_process.py` | 96 | `"worker_limit_mib": 512` |
| " | 149 | `memory_limit_mb=512` |

### 3.5 The other rungs of the ladder — also RETIRED-BY-RULING

The mi-solve treats the relic as a single 512 value. Executable code carries
three more [OBS]:

| Wall | File | Line | Site |
|---|---|---|---|
| **464** | `experiments/gm_m116_streams/analyze.py` | 18 | `PEAK_GATE_MIB = 464.0` |
| 464 | " | 147 | `"G3_peak_le_464_MiB": {...}` |
| 464 | `experiments/gm_m116_streams/run_arm.py` | 35 | `PEAK_GATE_MIB = 464.0` |
| 464 | " | 186 | `"peak_le_464_mib": ... <= PEAK_GATE_MIB` |
| **496** | `experiments/m236_layer_batched_m212_m235/run_m236_native_process.py` | 44 | `RSS_CAP_MIB = 496.0` |
| 496 | " | 423 | `prediction["rss_mib"] < RSS_CAP_MIB` |
| 496 | `experiments/m236_layer_batched_m212_m235/test_m236_native_contract.py` | 33 | `assertEqual(runner.RSS_CAP_MIB, 496.0)` |
| 496 | `experiments/m237_writeahead_native_receipt/run_m237_native_process.py` | 48, 97, 239 | `RSS_CAP_MIB` inherited, reported, and gated |
| 496 | `experiments/m237_writeahead_native_receipt/test_m237_durable_transport.py` | 164 | `assertEqual(runner.RSS_CAP_MIB, 496.0)` |
| **480** | `experiments/s11_full129_breakeven/run_s11.py` | 295-296 | the 480-MiB safety-gate string in the S11 verdict |
| 480 | `experiments/s11_full129_breakeven/finalize_s11.py` | 187 | same clause, finalized |

Not debt, deliberately excluded:

- `experiments/uf1_attack_memory/uf1_mem_derive.py:174,180,201,202`,
  `memprobe.py:5`, `uf1_mem_blockrows.py:100`, and
  `experiments/uf1_attack_composition/step3_marginal_and_score.py:229` encode
  512 **in order to price the relic**. They are the instrument that produced
  this retirement, not the debt it retires. **KEEP.**
- `experiments/m145_defensive_acg/m145_formal_l1_crosswalk.py:190` —
  `"below_512_mib": 479.859 < 512.0` compares two literals and is constant
  `True`. Dead either way; harmless. **KEEP, flagged as degenerate.**
- `experiments/m243_fable_oracle/fable_g0a_oracle.py:108` —
  `MEMORY_CAP_MIB = 2048.0` is an mpmath-oracle shard cap, a different
  quantity from an estimator peak gate. **Out of scope.**
- `graph/build_evidence_graph.py:364` already records the correction in its own
  node text (*"parked on a self-imposed 512-MiB gate (the enforced limit is
  65,536 MiB)"*). **Already correct.** Lines 636 and 639 carry 512 in
  descriptive edge text; they narrate a historical verdict and stay.
- `experiments/fold_floor_splice/peak_probe.py:3` and
  `candidate_source/estimator.py:67,86` reference the `<512 MiB` clause in
  docstrings. **FENCED lineage, halted by ruling 2 — observed read-only, not
  touched, not counted as live debt.**

---

## 4. fold_search's declared-not-enforced memory GAP

`core/HARNESS_20260817.md:27-29` records it [REP]:

> **Memory cap is declared, not enforced** [GAP]: enforce by wiring the clone's
> `windows_job_memory.py` (Job-Object commit cap, triple-reviewed, 99% pass) as
> the runner wrapper. The seam is `runner.argv` — no harness change needed.

First-hand check makes it **stronger than "declared, not enforced"** [OBS]: a
case-insensitive grep for `memory` across the whole of
`scripts/fold_search.py` (22.4 KB) returns **zero matches**. The harness does
not read, validate, or record a memory field at all.

What that means concretely:

- Cell specs *do* carry one. `cells/clone_l2fringe_flop_recompute/predeclaration.json:5`
  and `cells/clone_l2fringe_flop_recompute_v2/predeclaration.json:5` both
  declare `"memory_mib_declared": 512` [OBS, read-only — these live in the
  fenced `cells/` tree and were not modified]. Both declare the **retired
  relic**.
- `budgets.wall_seconds` is validated at predeclare (`fold_search.py:183-186`,
  rejecting null/0) and enforced at run with a fail-closed
  `BUDGET_KILL_WALL` (`:371`) [OBS].
- `budgets.memory_mib_declared` sits in the same dict and is **inert
  metadata** — no code path reads it. A cell can declare 512 MiB, allocate
  8 GiB, and receive a clean PASS.

### 4.1 Wiring sketch — `windows_job_memory.py` via `runner.argv`

The seam is already designed for this. `fold_search.py:11-13` states it in the
module docstring [OBS]:

> Heavier runners (the clone's 24-pair measurement contract and Windows
> job-object caps) plug in as the `runner.argv` of a cell; this module is the
> authority layer around them, not a replacement for them.

`runner.argv` is read at `:341` and executed via `subprocess` at `:348`, and is
already scanned by the evidence firewall at `:227-231`. So the cap wraps the
child without a harness change:

```jsonc
// cell predeclaration.json
"budgets": {
  "wall_seconds": 120,
  "memory_mib_ruled": 1024,      // owner-ruled engineering ceiling
  "memory_mib_enforced": 65536   // harness/contest mechanical limit
},
"runner": {
  "argv": [
    "python", "-B", "tools/windows_job_memory.py",
    "--commit-cap-mib", "1024",   // must equal budgets.memory_mib_ruled
    "--",
    "python", "-B", "experiments/<cell>/run.py"
  ]
}
```

`windows_job_memory.py` creates a Job Object with
`JOBOBJECT_EXTENDED_LIMIT_INFORMATION.ProcessMemoryLimit`, assigns the child,
and propagates its exit code — a breach kills the child, the non-zero exit
reaches `fold_search`, and the existing
`PROTOCOL_KILL_MALFORMED_METRICS` / budget-kill path turns it into a mechanical
KILL. Nothing in the authority layer changes.

This closes the platform hole in §1.2 as a side effect: a Job Object commit cap
is the Windows analogue of RLIMIT_AS, so the ruled ceiling becomes enforceable
on the box that actually runs the cells.

### 4.2 Standing rule for every future cell

**Declare both numbers, never one.** A cell states the **ruled 1-GiB
engineering ceiling** (the bar it is designed to meet) *and* the **65,536-MiB
mechanical limit** (what the harness/grader will actually enforce, on POSIX
with `--runner subprocess`). A single number invites the next agent to
re-derive which tier it meant — which is how the relic survived this long.

Any cell still declaring `memory_mib_declared: 512` is declaring a retired
gate. The two cells named above are in the fenced tree and stay as they are;
new predeclarations use the two-field form.

---

## 5. Residual risk of this document

- The four-tier structure and the retirement are **[REP]** from owner rulings
  recorded in the channel; this document does not re-litigate them.
- The 65,536-MiB limit and its enforcement path are **[OBS]**, verified at four
  lines in the frozen venv and cross-checked against `uf1_mem_verdict.json`.
- The Windows enforcement gap is **[OBS]** on both legs: the `resource` import
  raises `ModuleNotFoundError` when executed, and the `except ImportError` arm
  that swallows it is read in source. The remaining inference is **[DER]** —
  that the harness reaches that line at all, which follows from `runner.py:277`
  passing `memory_limit_mb` into the worker request. It was **not** confirmed
  by observing the warning in a live harness log; no run was made, per the
  zero-compute constraint. Settling check, when the harness next runs on this
  box: grep the worker's stderr for `could not setrlimit RLIMIT_AS`. Cost:
  seconds, on the next scheduled run.
- The debt inventory is **[OBS]** but bounded by its own search: it covers
  `*.py` under `corpus/whestbench/` matching a memory-token pattern near
  464/480/496/512. A predicate written with a computed constant, in a non-`.py`
  runner, or in a tree outside the corpus would be missed. The mi-solve's own
  list proved incomplete by 24 sites, so treat this count as a floor, not a
  census.
- Peaks in §2 are **[OBS]** from the ledger record text; the underlying
  measurements are **[REP]** from the runs that produced them. The champion's
  1.445-MiB margin is corroborated by two independent measurements (ledger idx
  72 at 478.555 MiB; `uf1` at 452.312/452.691 MiB) that agree on the
  disposition while differing on the value, because they measure different nets.
