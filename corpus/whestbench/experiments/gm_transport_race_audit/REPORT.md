# M245 transport Race 1 — executed against the frozen supervisor

**Status: Race 1 as predeclared is NOT REPRODUCED. A different, real weakness
was found in the same gate and is reported instead.**

Answers the M245 audit's open falsifier, rated *Probability: High, Consequence:
High, Cost: Low — required before RED tests and shard launch*:

> **Race 1: Clock Drift Deduplication.** The carry-forward age is limited to 0.1
> seconds. If an S-node clock drifts +0.12 s ahead of an L-node, valid
> deduplicated samples will be dropped as "stale" or "future." This bypasses the
> `max(inner, outer)` RSS charging constraint, artificially lowering the measured
> compute bill and granting a runtime False PASS.

Executed directly against `evaluate_resource_gate` in
`supervise_m245_fixture_materialization.py` (frozen, unmodified). The module is
Windows-only at import (`ctypes.wintypes`), so `wintypes` is stubbed; the gate
itself touches no Windows API — it is arithmetic over the process census and the
sample series. No fixture, no scientific work, no launch.

## What the code actually does

`MAXIMUM_GAP_SECONDS = 0.100` is **not** a carry-forward age and **not** a
cross-node staleness or deduplication filter. It is a *sampling-continuity*
bound: `gaps` are differences between consecutive timestamps **within one
series**, and `max(gaps) ≤ 0.100` asserts the sampler never went blind for more
than 100 ms.

Three structural facts follow, and each defeats one clause of the predeclared
race:

1. **There is no S/L merge to race.** Every sample carries `S`, `L` and `W`
   together in one record (`{"seconds", "S", "L", "W"}`). There are not two
   independently-clocked series being deduplicated.
2. **Nothing is silently dropped.** A backward timestamp raises
   `working-set timestamps moved backward`; a timestamp past child exit raises;
   an over-large gap sets `pass=False`. The gate is fail-closed.
3. **The RSS charge cannot be lowered by the sampler.**
   `rss_gate = max(sampled_peak, lifetime_sum)`, where
   `lifetime_sum = Σ_roles peak_working_set_lifetime_to_endpoint` comes from OS
   process counters and is **independent of the sample series**.

## Measured

| probe | input | result |
|---|---|---|
| 1 baseline | dense series, 5 samples | `sampled=65 MiB`, `lifetime=130 MiB`, **gate 130 MiB**, pass=True |
| 2 **the predeclared race** | +0.11 s jitter | `max_gap=0.110` → **`pass=False`**, gate still 130 MiB |
| 3 backward clock | timestamp regression | **raises** `working-set timestamps moved backward` |
| 4 sample starvation | 2 samples, 1 ms apart, in a 30 s run | `sampled=3 B` but **gate still 130 MiB — bill unchanged** |
| 5 inflated samples | 1 GB per role | gate rises to 2861 MiB, `pass=False` |

Probe 2 is the audit's exact scenario and it produces a **hard FAIL, not a False
PASS** — the opposite sign of the predicted defect. Probe 4 confirms the
consequence clause is structurally impossible: suppressing the entire sample
series leaves the charged bill at `lifetime_sum`, byte-identical to the
baseline.

Probe 5 shows the `max` is a **one-way ratchet**: samples can raise the charge,
never lower it. That is the conservative direction, and it is why no
sample-suppression attack on the bill can succeed.

Note also `lifetime_sum = Σ_r max_t RSS_r(t)` while
`sampled_peak ≈ max_t Σ_r RSS_r(t)`, and `max_t Σ_r ≤ Σ_r max_t` always. So
whenever the peaks fall inside the measured window, `sampled_peak ≤ lifetime_sum`
and the charge is decided entirely by the OS counters. The gate over-charges
relative to true concurrent peak — safe, but worth knowing it is not measuring
what the sampler suggests it measures.

## The real weakness, reported in place of the predeclared one

**The continuity gate bounds inter-sample gaps but never requires the series to
cover the run.** Two samples 1 ms apart at the start of a 30-second run satisfy
`max_gap ≤ 0.1` and pass continuity while observing essentially nothing
(probe 4). There is no check that the first sample is near run start, that the
last is near `wall_exit`, or that the series spans a required fraction of the
interval.

Today this is harmless *for the RSS bill*, because `lifetime_sum` dominates. But
that is the point: **the sampler is not load-bearing for the quantity it appears
to police.** Any future gate that reads `rss_sampled_bytes`,
`working_set_samples`, or `first_sample_seconds` as evidence of observed
behaviour would inherit an unguarded coverage hole. Two cheap repairs:

1. Require coverage, not only continuity: `first_sample_seconds ≤ ε` and
   `wall_exit − last_sample ≤ MAXIMUM_GAP_SECONDS`, plus a minimum sample count
   proportional to `wall_exit / NOMINAL_SAMPLE_SECONDS` (= 0.010 s, so a 30 s run
   implies ~3000 samples, against the 2 that currently pass).
2. If the sampled series is meant to be evidence, say what it decides. At
   present it can only raise the bill, so the continuity machinery guards a
   quantity that `lifetime_sum` already determines.

## Disposition

- The audit's Race 1 should be **reclassified**, not resolved: the named
  mechanism does not exist in this code, and its stated consequence is
  structurally unreachable. Its *High probability / High consequence* rating is
  not supported.
- The audit's proposed resolution — "expand carry-forward age bounds to strictly
  subsume maximum domain clock drift" — would be a change to a constant that
  does not do what the resolution assumes, and would **loosen** a continuity
  bound for no benefit. Not recommended.
- The coverage hole above is the item that should carry forward.

## Scope

Only `evaluate_resource_gate` was exercised. **Races 2 (PID/stale handle reuse)
and 3 (intent-burn atomicity) are untouched** — both live in the Windows
process/handle/job machinery, which cannot be executed on this Linux host. They
remain open. Nothing here evaluates a fixture, launches a shard, or makes an
estimator, variance, MSE, or score claim.

## Reproduction

```bash
cd corpus/whestbench/experiments/gm_transport_race_audit
python3 falsify_transport_race1.py
```

Stdlib only. Reads the frozen supervisor read-only and never edits it.
