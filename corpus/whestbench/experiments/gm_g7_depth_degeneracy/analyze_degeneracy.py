"""Test the four predeclared G7 predictions against the measured trajectories.

Estimator note, recorded because it corrects an earlier report: the median of
per-layer ratios lambda_min(l+1)/lambda_min(l) is an unstable estimator of the
decay rate. lambda_min is non-monotone layer to layer (it bounces by one to two
orders), so the median ratio swings wildly across replicates of the same cell
(0.10, 0.90, 0.12 at width 256). A least-squares fit of log10(lambda_min) on
layer over the healthy prefix uses every point and is robust to the bouncing.
All rates below are fitted; the median-ratio figures quoted in
gm_factored_cholesky/REPORT.md are superseded.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
FLOOR = 1e-12
DEPTH = 32


def fit_log_slope(xs, ys):
    """Least squares slope/intercept/R^2 of ys on xs."""
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        return None
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    slope = sxy / sxx
    intercept = my - slope * mx
    ss_tot = sum((y - my) ** 2 for y in ys)
    ss_res = sum((y - (intercept + slope * x)) ** 2 for x, y in zip(xs, ys))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return slope, intercept, r2


def healthy(rec):
    return [r for r in rec["layers"] if r["lambda_min"] > FLOOR]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", default=str(HERE / "degeneracy.json"))
    args = ap.parse_args()
    data = json.loads(Path(args.data).read_text(encoding="utf-8"))

    for rec in data:
        h = healthy(rec)
        xs = [r["layer"] for r in h]
        ys = [math.log10(r["lambda_min"]) for r in h]
        rec["_fit"] = fit_log_slope(xs, ys)
        kys = [math.log10(r["kappa"]) for r in h if math.isfinite(r["kappa"])]
        rec["_kfit"] = fit_log_slope(xs[:len(kys)], kys)

    # ---------------- P3 first: is log10(kappa) linear in depth? -------------
    print("=" * 74)
    print("P3 — is log10(kappa) linear in depth?  (decades of precision per layer)")
    print(f"{'arm':>5} {'width':>6} {'rep':>4} {'decades/layer':>14} {'R^2':>7} "
          f"{'digits @L32 (extrap)':>21}")
    print("-" * 74)
    per_group = {}
    for rec in data:
        f = rec["_kfit"]
        if not f:
            continue
        slope, intercept, r2 = f
        at32 = intercept + slope * DEPTH
        per_group.setdefault((rec["arm"], rec["width"]), []).append((slope, r2, at32))
        print(f"{rec['arm']:>5} {rec['width']:>6} {rec['replicate']:>4} "
              f"{slope:>14.4f} {r2:>7.3f} {at32:>21.1f}")

    # ---------------- P2: is the rate width-dependent? -----------------------
    print()
    print("=" * 74)
    print("P2 — fitted decay of lambda_min (decades lost per layer), by cell group")
    print(f"{'arm':>5} {'width':>6} {'cells':>6} {'median':>9} {'min':>8} {'max':>8} "
          f"{'median R^2':>11}")
    print("-" * 74)
    rates = {}
    for rec in data:
        f = rec["_fit"]
        if f:
            rates.setdefault((rec["arm"], rec["width"]), []).append((-f[0], f[2]))
    for key in sorted(rates, key=lambda k: (k[0], k[1])):
        vals = [v for v, _ in rates[key]]
        r2s = [r for _, r in rates[key]]
        print(f"{key[0]:>5} {key[1]:>6} {len(vals):>6} {statistics.median(vals):>9.4f} "
              f"{min(vals):>8.4f} {max(vals):>8.4f} {statistics.median(r2s):>11.3f}")

    # ---------------- P4: does orthogonal init rescue anything? --------------
    print()
    print("=" * 74)
    print("P4 — He-Gaussian vs Haar-orthogonal (the mechanism discriminator)")
    print(f"{'width':>6} {'he trips':>22} {'orth trips':>22} {'he rate':>9} {'orth rate':>10}")
    print("-" * 74)
    for w in sorted({r["width"] for r in data}):
        he = [r for r in data if r["width"] == w and r["arm"] == "he"]
        orth = [r for r in data if r["width"] == w and r["arm"] == "orth"]
        f = lambda rs: ", ".join(str(r["first_trip"]) for r in rs)
        hr = [-r["_fit"][0] for r in he if r["_fit"]]
        orr = [-r["_fit"][0] for r in orth if r["_fit"]]
        print(f"{w:>6} {f(he):>22} {f(orth):>22} "
              f"{statistics.median(hr):>9.3f} {statistics.median(orr):>10.3f}")

    # ---------------- P1: is the collapse the angle contraction? -------------
    print()
    print("=" * 74)
    print("P1 — does lambda_min/lambda_max track the equicorrelation prediction?")
    print("    equicorrelation: lambda_min/lambda_max = (1-rho)/(1+(n-1)rho)")
    print(f"{'arm':>5} {'width':>6} {'rep':>4} {'median obs/pred':>16} {'drift (max/min)':>16}")
    print("-" * 74)
    drifts = []
    for rec in data:
        n = rec["width"]
        ratios = []
        for r in healthy(rec):
            rho = r["mean_abs_rho"]
            denom = 1 + (n - 1) * rho
            pred = (1 - rho) / denom if denom > 0 else None
            if pred and pred > 0 and r["lambda_max"] > 0:
                ratios.append((r["lambda_min"] / r["lambda_max"]) / pred)
        if len(ratios) >= 3:
            drift = max(ratios) / min(ratios)
            drifts.append(drift)
            print(f"{rec['arm']:>5} {n:>6} {rec['replicate']:>4} "
                  f"{statistics.median(ratios):>16.4f} {drift:>16.1f}")
    if drifts:
        print(f"\n  median drift across cells: {statistics.median(drifts):.1f}x "
              f"(P1 falsified if > 10x)")
        print(f"  cells with drift <= 10x: "
              f"{sum(d <= 10 for d in drifts)}/{len(drifts)}")

    # ---------------- effective rank collapse -------------------------------
    print()
    print("=" * 74)
    print("Effective rank (spectral entropy) at width 256, He arm")
    for rec in data:
        if rec["width"] == 256 and rec["arm"] == "he" and rec["replicate"] == 0:
            print(f"{'layer':>6} {'eff rank':>10} {'of n':>6} {'mean|rho|':>10} "
                  f"{'max|rho|':>9}")
            for r in rec["layers"]:
                print(f"{r['layer']:>6} {r['effective_rank']:>10.2f} {256:>6} "
                      f"{r['mean_abs_rho']:>10.4f} {r['max_abs_rho']:>9.4f}")


if __name__ == "__main__":
    main()
