"""Isolated-process peak-memory probe, on the incumbent's own declared method.

The `<512 MiB` clause of ``ROW_BLOCKED_WINOGRAD_PRODUCTION_GATE.md`` was passed
by the incumbent under the method stated in ``ROW_BLOCKED_WINOGRAD_REPORT.md``
("Frozen full-entry result" and "Memory accounting"):

    identical fresh synthetic width-256/depth-32 He weights, setup frames,
    ``n_base=32256`` and all 64512 antipodal sample paths, in *independent
    one-thread processes* -- one estimator, one setup, one predict, and the
    process-wide ``PeakWorkingSetSize`` read at the end.

That is method A below.  The hostile verifier instead read the peak of the
whole ``verify_fold_floor.py`` process, which holds a direct-product arbiter,
the incumbent package, and five fork routes at once; that is method B, and it
is measured by ``peak_of.py`` wrapping the harness.  The two are not
comparable, so every number this campaign reports names its method.

    python -B peak_probe.py incumbent
    python -B peak_probe.py floor_off        # fork with USE_FLOOR=False
    python -B peak_probe.py floor_on         # fork as shipped (L4, 192 MiB)

Nothing here writes to ``row_blocked_production``: ``sys.dont_write_bytecode``
is set before the first import.
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True          # must precede every package import

import ctypes                                                    # noqa: E402
import json                                                      # noqa: E402
import time                                                      # noqa: E402
from ctypes import wintypes                                      # noqa: E402
from pathlib import Path                                         # noqa: E402

HERE = Path(__file__).resolve().parent
FORK = HERE / "candidate_source"
INCUMBENT = HERE.parent / "row_blocked_production" / "candidate_source"
MIB = 1024.0 * 1024.0


class _PMC(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("PageFaultCount", wintypes.DWORD),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
    ]


_k32 = ctypes.WinDLL("kernel32", use_last_error=True)
_info = _k32.K32GetProcessMemoryInfo
_info.argtypes = [wintypes.HANDLE, ctypes.POINTER(_PMC), wintypes.DWORD]
_info.restype = wintypes.BOOL


def snapshot() -> dict:
    pmc = _PMC()
    pmc.cb = ctypes.sizeof(_PMC)
    if not _info(_k32.GetCurrentProcess(), ctypes.byref(pmc), pmc.cb):
        raise OSError(ctypes.get_last_error(), "GetProcessMemoryInfo failed")
    return {
        "working_set_mib": round(pmc.WorkingSetSize / MIB, 4),
        "peak_working_set_mib": round(pmc.PeakWorkingSetSize / MIB, 4),
        "commit_mib": round(pmc.PagefileUsage / MIB, 4),
        "peak_commit_mib": round(pmc.PeakPagefileUsage / MIB, 4),
    }


def main() -> None:
    route = sys.argv[1] if len(sys.argv) > 1 else "floor_on"
    root = INCUMBENT if route == "incumbent" else FORK
    sys.path.insert(0, str(root))

    import numpy as _np
    import flopscope as flops
    import flopscope.numpy as fnp
    from whestbench import SetupContext
    from whestbench.domain import MLP

    import estimator as est_mod
    if route == "floor_off":
        est_mod.USE_FLOOR = False
    elif route == "floor_on":
        est_mod.USE_FLOOR = True

    stages = {"after_import": snapshot()}

    width, depth = 256, 32
    rng = _np.random.default_rng(20260806)
    weights = [
        (rng.standard_normal((width, width))
         * _np.sqrt(2.0 / width)).astype(_np.float32)
        for _ in range(depth)
    ]
    net = MLP(width=width, depth=depth,
              weights=[fnp.array(w) for w in weights],
              seed=20260806, name="frozen_full_entry")
    del weights
    stages["after_net"] = snapshot()

    est = est_mod.Estimator()
    start = time.perf_counter()
    with flops.BudgetContext(flop_budget=10 ** 13):
        est.setup(SetupContext(width=width, depth=depth,
                               flop_budget=272_000_000_000,
                               api_version="0.14",
                               submission_dir=str(root), seed=0))
    setup_wall = time.perf_counter() - start
    stages["after_setup"] = snapshot()

    start = time.perf_counter()
    with flops.BudgetContext(flop_budget=10 ** 13) as ctx:
        out = est.predict(net, 272_000_000_000)
        billed = int(ctx.flops_used)
    predict_wall = time.perf_counter() - start
    residual = float(ctx.residual_wall_time_s)   # only set on context exit
    stages["after_predict"] = snapshot()

    operator = getattr(est, "_winograd", None)
    pools = getattr(operator, "_pools", {})
    pool_bytes = sum(int(p.nbytes) for p in pools.values())
    # Read the fallback out of ``__dict__``: ``fallback`` is a property that
    # builds it on demand, so ``getattr`` would allocate the very workspace the
    # probe exists to prove absent.  Both the pre-fix attribute name and the
    # post-fix private one are checked.
    inner = operator.__dict__.get("_fallback") or operator.__dict__.get(
        "fallback")
    fallback_bytes = 0 if inner is None else int(inner.buffer_bytes)
    if hasattr(operator, "buffer_bytes"):          # the frozen fallback itself
        fallback_bytes = int(operator.buffer_bytes)

    print(json.dumps({
        "route": route,
        "method": "A: incumbent-equivalent isolated process, one setup + one "
                  "predict, width 256 depth 32, n_base 32256",
        "n_base": int(est.n_base),
        "strategy": getattr(operator, "last_strategy", "frozen_fallback"),
        "setup_s": round(setup_wall, 4),
        "predict_s": round(predict_wall, 4),
        "analytical_flops": billed,
        "residual_s": round(residual, 6),
        "effective_C": billed + 100e9 * residual,
        "operator_workspace_mib": round(
            (pool_bytes + fallback_bytes) / MIB, 4),
        "operator_pool_mib": round(pool_bytes / MIB, 4),
        "operator_fallback_mib": round(fallback_bytes / MIB, 4),
        "fallback_constructed": inner is not None or fallback_bytes > 0,
        "output_finite": bool(_np.isfinite(_np.asarray(out)).all()),
        "stages": stages,
        "peak_working_set_mib": stages["after_predict"]["peak_working_set_mib"],
    }, indent=1))


if __name__ == "__main__":
    main()
