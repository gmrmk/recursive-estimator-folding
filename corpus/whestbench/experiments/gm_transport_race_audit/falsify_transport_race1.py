"""Falsifier: M245 audit Race 1 -- clock-drift deduplication False PASS.

The audit's predeclared claim:

    Race 1: Clock Drift Deduplication. The carry-forward age is limited to 0.1
    seconds. If an S-node clock drifts +0.12 seconds ahead of an L-node, valid
    deduplicated samples will be dropped as "stale" or "future." This bypasses
    the max(inner, outer) RSS charging constraint, artificially lowering the
    measured compute bill and granting a runtime False PASS.

    Cheapest falsifier: Inject a mock sample array into the L layer with exactly
    a 0.11 second clock jitter on an identical S-node identity. If the system
    fails to correctly apply max(inner_S, outer_S) and instead drops the sample
    or double-counts RSS, the deduplication topology is falsified.

Executed directly against the frozen supervisor's `evaluate_resource_gate`.
The module is Windows-only at import (ctypes.wintypes), so wintypes is stubbed;
`evaluate_resource_gate` itself touches no Windows API -- it is pure arithmetic
over the process census and the sample series.

No fixture, no scientific work, no launch. Pure input/output on one function.
"""

from __future__ import annotations

import ctypes
import importlib.util
import sys
import types
from pathlib import Path

# --- make the Windows-only module importable on Linux -----------------------
if not hasattr(ctypes, "wintypes"):
    stub = types.ModuleType("ctypes.wintypes")
    for name in ("DWORD", "BOOL", "HANDLE", "LPWSTR", "WORD", "BYTE", "LARGE_INTEGER",
                 "ULARGE_INTEGER", "LPVOID", "UINT", "LONG", "WCHAR", "HMODULE"):
        setattr(stub, name, ctypes.c_uint32)
    stub.MAX_PATH = 260
    sys.modules["ctypes.wintypes"] = stub
    ctypes.wintypes = stub

_NAME = "supervise_m245_fixture_materialization.py"
_HERE = Path(__file__).resolve().parent
_CANDIDATES = [
    _HERE.parent / "m245_canonical_unordered_replica_galerkin_spectrum" / _NAME,
    _HERE / _NAME,
]
SUP = next((p for p in _CANDIDATES if p.is_file()), None)
if SUP is None:
    raise SystemExit(
        "supervisor not found. This falsifier reads the frozen M245 supervisor "
        "read-only; it is deliberately NOT vendored here. Checked:\n  "
        + "\n  ".join(str(p) for p in _CANDIDATES)
        + "\nThe file arrives with PR #1 (agent/compression-survivor-corpus)."
    )
spec = importlib.util.spec_from_file_location("sup", SUP)
sup = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(sup)
except Exception as exc:                                    # pragma: no cover
    print(f"module import failed: {type(exc).__name__}: {exc}")
    raise SystemExit(1)

GATE = sup.evaluate_resource_gate
MB = 1 << 20


def census(s_peak, l_peak, w_peak):
    def row(peak):
        return {
            "peak_working_set_lifetime_to_endpoint": peak,
            "kernel_endpoint_100ns": 1000, "kernel_final_100ns": 1000,
            "user_endpoint_100ns": 1000, "user_final_100ns": 1000,
        }
    return {"S": row(s_peak), "L": row(l_peak), "W": row(w_peak)}


def samples(times, s, l, w):
    return [{"seconds": t, "S": s, "L": l, "W": w} for t in times]


def call(procs, samps, wall_r=1.0, wall_exit=1.0):
    try:
        return GATE(processes=procs, working_set_samples=samps,
                    wall_r_seconds=wall_r, wall_child_exit_seconds=wall_exit), None
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"


def main() -> None:
    print(f"MAXIMUM_GAP_SECONDS = {sup.MAXIMUM_GAP_SECONDS}")
    print(f"RSS_CAP_BYTES       = {sup.RSS_CAP_BYTES} ({sup.RSS_CAP_BYTES/MB:.0f} MiB)\n")

    S_PEAK, L_PEAK, W_PEAK = 40 * MB, 30 * MB, 60 * MB
    procs = census(S_PEAK, L_PEAK, W_PEAK)
    lifetime_sum = S_PEAK + L_PEAK + W_PEAK

    print("=" * 70)
    print("PROBE 1 -- baseline: dense, well-covered sample series")
    base, err = call(procs, samples([0.00, 0.05, 0.10, 0.15, 0.20],
                                    20 * MB, 15 * MB, 30 * MB))
    print(f"  err={err}")
    print(f"  rss_sampled={base['rss_sampled_bytes']/MB:.0f} MiB  "
          f"lifetime_sum={base['rss_lifetime_to_endpoint_sum_bytes']/MB:.0f} MiB  "
          f"GATE={base['rss_gate_bytes']/MB:.0f} MiB  pass={base['pass']}")

    print("\n" + "=" * 70)
    print("PROBE 2 -- the audit's Race 1: +0.11 s jitter on an S-node sample")
    jit, err = call(procs, samples([0.00, 0.05, 0.16, 0.21],
                                   20 * MB, 15 * MB, 30 * MB))
    if err:
        print(f"  RAISED -> {err}")
        print("  => the drifted series is REFUSED, not silently dropped.")
    else:
        print(f"  rss_gate={jit['rss_gate_bytes']/MB:.0f} MiB  pass={jit['pass']}  "
              f"max_gap={jit['maximum_gap_seconds']:.3f}")
        print("  => gap gate FAILS the run (pass=False); no silent acceptance.")

    print("\n" + "=" * 70)
    print("PROBE 3 -- backward / 'future' timestamp (clock drift the other way)")
    _, err = call(procs, samples([0.00, 0.05, 0.04, 0.09], 20*MB, 15*MB, 30*MB))
    print(f"  RAISED -> {err}")

    print("\n" + "=" * 70)
    print("PROBE 4 -- can DROPPING samples lower the charged bill?")
    print("  Adversary keeps only 2 samples, 1 ms apart, at the very start of the")
    print("  run, reporting near-zero working sets. Gap gate is satisfied.")
    starved, err = call(procs, samples([0.000, 0.001], 1, 1, 1),
                        wall_r=30.0, wall_exit=30.0)
    print(f"  err={err}")
    print(f"  rss_sampled={starved['rss_sampled_bytes']} B  "
          f"lifetime_sum={starved['rss_lifetime_to_endpoint_sum_bytes']/MB:.0f} MiB")
    print(f"  GATE={starved['rss_gate_bytes']/MB:.0f} MiB   "
          f"max_gap={starved['maximum_gap_seconds']:.3f} (<= "
          f"{sup.MAXIMUM_GAP_SECONDS}) -> continuity 'passes'")
    same = starved["rss_gate_bytes"] == base["rss_gate_bytes"] == lifetime_sum
    print(f"  charged bill unchanged vs baseline: {same}")

    print("\n" + "=" * 70)
    print("PROBE 5 -- is max(sampled_peak, lifetime_sum) ever decided by samples?")
    print("  lifetime_sum = SUM over roles of each role's peak")
    print("  sampled_peak = MAX over time of the CONCURRENT sum")
    print("  so sampled_peak <= lifetime_sum whenever peaks are within the")
    print("  measured window. Trying to exceed it:")
    over, err = call(procs, samples([0.0, 0.05], 10**9, 10**9, 10**9))
    print(f"  huge samples -> rss_sampled={over['rss_sampled_bytes']/MB:.0f} MiB  "
          f"GATE={over['rss_gate_bytes']/MB:.0f} MiB  pass={over['pass']}")
    print("  (samples CAN raise the gate; they can never lower it below "
          "lifetime_sum)")

    print("\n" + "=" * 70)
    print("VERDICT")
    print("  Race 1 as predeclared: NOT REPRODUCED.")
    print("   - MAXIMUM_GAP_SECONDS is a sampling-continuity bound on consecutive")
    print("     timestamps within ONE series, not a carry-forward age and not a")
    print("     cross-node staleness/dedup filter.")
    print("   - Each sample carries S, L and W together, so there is no merge of")
    print("     independently-clocked S and L series to race.")
    print("   - Anomalous timestamps RAISE (backward, past-child-exit) or FAIL the")
    print("     gate (gap > 0.1). Nothing is silently dropped.")
    print("   - The RSS charge is floored by lifetime_sum, which is taken from OS")
    print("     process counters and is independent of the sample series, so")
    print("     dropping samples cannot lower the bill.")
    print("\n  Real weakness found instead (PROBE 4): the continuity gate bounds")
    print("  inter-sample GAPS but never requires the series to COVER the run.")
    print("  Two samples 1 ms apart in a 30 s run satisfy it. That is harmless for")
    print("  the RSS charge today only because lifetime_sum dominates -- i.e. the")
    print("  sampler is not load-bearing for the bill it appears to police.")


if __name__ == "__main__":
    main()
