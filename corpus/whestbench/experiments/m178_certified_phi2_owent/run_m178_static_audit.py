"""M178 static audit: hostile-grid containment, static charged-operation
table, billed FlopScope trace, and cross-process determinism.

Writes M178_RESULTS_20260807.json.  Response-free: references are internal
mathematical constants (mpmath dps=50); no challenge data, scorer, or model.

Usage:
    python run_m178_static_audit.py [--workers N] [--subset K] [--hash-only]

--hash-only prints the SHA256 of the full-grid evaluator output and exits
(used by the determinism check, which compares two separate processes).
--subset K audits only every K-th grid point (development aid; the frozen
result JSON must be produced with the full grid, subset = 1).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import m178_certified_phi2_owent as m178  # noqa: E402

RESULTS_NAME = "M178_RESULTS_20260807.json"

AB = sorted(
    {0.0}
    | {s * v for s in (1.0, -1.0)
       for v in (2.0 ** -30, 0.5, 1.0, 2.0, 3.4999, 3.5, 3.5000001,
                 4.95, 5.0, 7.0, 8.48, 10.0)}
)
RHO = sorted(
    {0.0}
    | {s * v for s in (1.0, -1.0)
       for v in (2.0 ** -52, 0.1, 0.5, 0.9, 0.99, 0.999999,
                 1.0 - 2.0 ** -45, 1.0 - 2.0 ** -52)}
)
DEEP_AB = [s * v for s in (1.0, -1.0) for v in (37.5, 40.0)]
DEEP_RHO = [0.0, 0.9, -0.9]
REDUCTION_T = [1.0 - 2.0 ** -52, 1.0, 1.0 + 2.0 ** -52]
# extreme family: subnormal, tiny-mean-chart boundary, and overflow-channel
# inputs (encodes the adversarial counterexamples permanently)
EXTREME_AB = [0.0, 5e-324, -5e-324, 1e-320, -1e-320, 1e-300, -1e-300,
              1e-290, -1e-290, 1e-200, -1e-200, 1.0, -1.0,
              1e301, -1e301, 1.5e308, -1.5e308,
              1.7976931348623157e308, -1.7976931348623157e308]
EXTREME_RHO = [0.5, -0.5, 0.9, -0.9, 1.0 - 2.0 ** -52, -(1.0 - 2.0 ** -52)]


def build_grid():
    grid = [(a, b, r) for a in AB for b in AB for r in RHO]
    grid += [(a, b, r) for a in DEEP_AB for b in DEEP_AB for r in DEEP_RHO]
    import math
    for r in RHO:
        s = math.sqrt((1.0 - r) * (1.0 + r))
        for t in REDUCTION_T:
            grid.append((1.0, r + t * s, r))
    grid += [(a, b, r) for a in EXTREME_AB for b in EXTREME_AB
             for r in EXTREME_RHO]
    return grid


# ---------------------------------------------------------------- references

def _mp():
    import mpmath as mp
    mp.mp.dps = 50
    return mp


def _ncdf(mp, z):
    """mp.ncdf with the argument clamped to +-50: mpmath 1.3.0's erfc
    overflows an internal series-length check for astronomically large
    arguments (extreme grid points reach ~1e316).  Truncation is below
    erfc(50)/2 < 1e-540, inside the 1e-300 radius allowance."""
    if z > 50:
        return mp.mpf(1)
    if z < -50:
        return mp.mpf(0)
    return mp.ncdf(z)


def ref_value_conditional(mp, a, b, rho):
    """R1: x-integral of npdf(x)*ncdf((b - rho x)/s) with formula-driven
    split panels around the Phi transition (never adaptive at runtime; this
    is the reference, computed offline)."""
    a, b, rho = mp.mpf(a), mp.mpf(b), mp.mpf(rho)
    s = mp.sqrt((1 - rho) * (1 + rho))
    lo = mp.mpf(-45)
    hi = min(a, mp.mpf(45))   # tail beyond 45 sigma < 1e-440, inside the
    if hi <= lo:              # 1e-300 truncation allowance of the radius
        return mp.mpf(0)
    pts = {lo, hi}
    if rho != 0:
        x0 = b / rho
        w = s / abs(rho)
        for k in (-8, -1, 1, 8):
            p = x0 + k * w
            if lo < p < hi:
                pts.add(p)
        if lo < x0 < hi:
            pts.add(x0)
    f = lambda x: mp.npdf(x) * _ncdf(mp, (b - rho * x) / s)
    return mp.quad(f, sorted(pts))


def ref_value_owen(mp, a, b, rho):
    """R2: Owen assembly, T(h,q) by quadrature in the theta form
    T = (1/2pi) Int_0^{atan q} exp(-h^2/(2 cos^2 t)) dt (smooth, bounded)."""
    a, b, rho = mp.mpf(a), mp.mpf(b), mp.mpf(rho)
    s = mp.sqrt((1 - rho) * (1 + rho))

    def T(h, q):
        if q == 0:
            return mp.mpf(0)
        if h == 0:
            return mp.atan(q) / (2 * mp.pi)
        sign = 1 if q > 0 else -1
        qa = abs(q)
        h2 = h * h / 2
        upper = mp.atan(qa)
        g = lambda t: mp.exp(-h2 / mp.cos(t) ** 2)
        return sign * mp.quad(g, [0, upper]) / (2 * mp.pi)

    if a == 0 and b == 0:
        return mp.mpf(1) / 4 + mp.asin(rho) / (2 * mp.pi)
    ta = (mp.mpf(1) / 4 if b > 0 else mp.mpf(-1) / 4) if a == 0 \
        else T(a, (b - rho * a) / (a * s))
    tb = (mp.mpf(1) / 4 if a > 0 else mp.mpf(-1) / 4) if b == 0 \
        else T(b, (a - rho * b) / (b * s))
    delta = mp.mpf(0) if (a * b > 0 or (a * b == 0 and a + b >= 0)) \
        else mp.mpf("0.5")
    return (_ncdf(mp, a) + _ncdf(mp, b)) / 2 - ta - tb - delta


def ref_derivs(mp, a, b, rho):
    a, b, rho = mp.mpf(a), mp.mpf(b), mp.mpf(rho)
    s = mp.sqrt((1 - rho) * (1 + rho))
    da = mp.npdf(a) * _ncdf(mp, (b - rho * a) / s)
    db = mp.npdf(b) * _ncdf(mp, (a - rho * b) / s)
    drho = mp.exp(-(((a - rho * b) / s) ** 2 + b * b) / 2) / (2 * mp.pi * s)
    return da, db, drho


def audit_chunk(points):
    mp = _mp()
    out = []
    for (a, b, rho) in points:
        r = m178.evaluate(a, b, rho)
        assert not r.refused, (a, b, rho, r.reason)
        r1 = ref_value_conditional(mp, a, b, rho)
        r2 = ref_value_owen(mp, a, b, rho)
        da, db, drho = ref_derivs(mp, a, b, rho)
        # protocol radius rule: max(1e-30, 10*|R1-R2|) plus the 45-sigma
        # truncation allowance; containment demands err + radius <= width
        gap = abs(r1 - r2)
        radius = max(mp.mpf("1e-30"), 10 * gap) + mp.mpf("1e-300")
        verr = abs(mp.mpf(r.value) - r1)
        out.append({
            "point": [a, b, rho],
            "ref_gap": float(gap),
            "ref_radius": float(radius),
            "value_err": float(verr),
            "value_w": r.w_value,
            "value_contained": bool(verr + radius <= r.w_value),
            "da_err": float(abs(mp.mpf(r.d_a) - da)),
            "da_w": r.w_da,
            "da_contained": bool(
                abs(mp.mpf(r.d_a) - da) + radius <= r.w_da),
            "db_err": float(abs(mp.mpf(r.d_b) - db)),
            "db_contained": bool(
                abs(mp.mpf(r.d_b) - db) + radius <= r.w_db),
            "drho_err": float(abs(mp.mpf(r.d_rho) - drho)),
            "drho_w": r.w_drho,
            "drho_contained": bool(
                abs(mp.mpf(r.d_rho) - drho) + radius <= r.w_drho),
            "chart": r.chart,
        })
    return out


# -------------------------------------------- static count-class census
# The dispatch tree's charged count is determined by the branch path AND the
# erf/tail chart selected at each Phi call site, so the honest inventory is
# a census of count-classes (op-multiset signatures), not a hand-picked leaf
# list.  Identical signature implies identical charged total by construction
# (the total is a fixed linear functional of the signature); the assert
# below re-verifies that anyway.

def static_leaf_census(points, rng_seed=20260807, random_points=4000):
    import numpy as np
    rng = np.random.default_rng(rng_seed)
    pts = list(points)
    for _ in range(random_points):
        a = float(rng.normal() * 10.0 ** float(rng.integers(-3, 3)))
        b = float(rng.normal() * 10.0 ** float(rng.integers(-3, 3)))
        rho = float(np.clip(rng.uniform(-1.0, 1.0),
                            -(1.0 - 2.0 ** -52), 1.0 - 2.0 ** -52))
        pts.append((a, b, rho))
    census = {}
    for (a, b, rho) in pts:
        bk = m178.CountingBackend()
        r = m178.evaluate(a, b, rho, backend=bk)
        if r.refused:
            continue
        sig = tuple(sorted(bk.calls.items()))
        row = census.get(sig)
        if row is None:
            census[sig] = {"charged_flops": bk.flops, "count": 1,
                           "example": [a, b, rho], "chart": r.chart}
        else:
            assert row["charged_flops"] == bk.flops, (sig, a, b, rho)
            row["count"] += 1
    return census


def flopscope_billed_sample(census, sample=12):
    """Billed-vs-static agreement on a spread of count-classes including the
    extremes; the meter and the counting backend must agree exactly."""
    import flopscope as flops
    rows = sorted(census.values(), key=lambda r: r["charged_flops"])
    step = max(1, len(rows) // max(1, sample - 2))
    picks = [rows[0], rows[-1]] + rows[::step]
    bk = m178.FlopscopeBackend()
    seen, out = set(), []
    for row in picks:
        if row["charged_flops"] in seen:
            continue
        seen.add(row["charged_flops"])
        a, b, rho = row["example"]
        with flops.BudgetContext(10 ** 9, quiet=True):
            before = flops.budget_summary_dict()["flops_used"]
            r = m178.evaluate(a, b, rho, backend=bk)
            after = flops.budget_summary_dict()["flops_used"]
        assert not r.refused
        out.append({"example": [a, b, rho],
                    "static": row["charged_flops"],
                    "billed": int(after - before),
                    "match": int(after - before) == row["charged_flops"]})
    return out


# ----------------------------------------------------------- determinism

def grid_output_hash():
    h = hashlib.sha256()
    for (a, b, rho) in build_grid():
        r = m178.evaluate(a, b, rho)
        h.update(struct.pack("<4d", r.value, r.d_a, r.d_b, r.d_rho))
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--subset", type=int, default=1)
    ap.add_argument("--hash-only", action="store_true")
    args = ap.parse_args()

    if args.hash_only:
        print(grid_output_hash())
        return

    grid = build_grid()[:: args.subset]
    chunks = [grid[i::args.workers] for i in range(args.workers)]
    chunks = [c for c in chunks if c]
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        rows = [row for part in ex.map(audit_chunk, chunks) for row in part]

    census = static_leaf_census(build_grid())
    worst_static = max(r["charged_flops"] for r in census.values())
    billed_sample = flopscope_billed_sample(census)

    h1 = subprocess.run([sys.executable, __file__, "--hash-only"],
                        capture_output=True, text=True,
                        check=True).stdout.strip()
    h2 = subprocess.run([sys.executable, __file__, "--hash-only"],
                        capture_output=True, text=True,
                        check=True).stdout.strip()

    not_contained = [r for r in rows
                     if not (r["value_contained"] and r["da_contained"]
                             and r["db_contained"] and r["drho_contained"])]
    summary = {
        "mutation": "m178_certified_phi2_owent",
        "grid_points_audited": len(rows),
        "grid_subset_stride": args.subset,
        "reference_dps": 50,
        "max_reference_gap_R1_R2": max(r["ref_gap"] for r in rows),
        "worst_value_err": max(r["value_err"] for r in rows),
        "worst_da_err": max(r["da_err"] for r in rows),
        "worst_db_err": max(r["db_err"] for r in rows),
        "worst_drho_err": max(r["drho_err"] for r in rows),
        "all_contained": not not_contained,
        "not_contained_points": [r["point"] for r in not_contained][:20],
        "count_class_census": {
            "n_count_classes": len(census),
            "totals_sorted": sorted({r["charged_flops"]
                                     for r in census.values()}),
            "worst_example": max(census.values(),
                                 key=lambda r: r["charged_flops"])["example"],
        },
        "worst_static_charged_flops": worst_static,
        "F_EPILOGUE_surcharge": m178.F_EPILOGUE,
        "F_M178_worst_case_inclusive": worst_static + m178.F_EPILOGUE,
        "F_M178_ceiling": 20000,
        "ceiling_respected": worst_static + m178.F_EPILOGUE <= 20000,
        "flopscope_billed_sample": billed_sample,
        "billed_matches_static": all(r["match"] for r in billed_sample),
        "determinism_hash_run1": h1,
        "determinism_hash_run2": h2,
        "deterministic_across_processes": h1 == h2,
    }
    (HERE / RESULTS_NAME).write_text(json.dumps(summary, indent=1))
    print(json.dumps({k: summary[k] for k in
                      ("grid_points_audited", "max_reference_gap_R1_R2",
                       "worst_value_err", "all_contained",
                       "worst_static_charged_flops", "ceiling_respected",
                       "deterministic_across_processes")}, indent=1))
    if not summary["all_contained"] or not summary["ceiling_respected"] \
            or not summary["deterministic_across_processes"] \
            or not summary["billed_matches_static"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
