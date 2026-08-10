"""Analyze ell*(n) across every SPD-depth cell on record.

Combines this experiment's sweeps with gm_m179_m199/diag_spd_depth.json, which
uses the identical generator and cell_seed scheme, so overlapping (width,
replicate) cells are exact reproduction checks rather than duplicates.

Censoring: a cell that never trips the floor is right-censored at 32 (the
recurrence has only 32 layers). Rank statistics use 33 as the censored rank
value, which is order-preserving; means are never taken over censored cells.
"""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCES = [
    HERE / "spd_width_scaling.json",
    HERE / "transition.json",
    HERE.parent / "gm_m179_m199" / "diag_spd_depth.json",
]
CENSOR = 33


def load() -> tuple[dict, list[str]]:
    cells: dict[tuple[int, int], dict] = {}
    conflicts: list[str] = []
    agreements = 0
    for src in SOURCES:
        if not src.exists():
            continue
        for rec in json.loads(src.read_text(encoding="utf-8")):
            key = (rec["width"], rec["replicate"])
            val = rec["first_layer_min_eig_le_floor"]
            if key in cells:
                prev = cells[key]["first_layer_min_eig_le_floor"]
                if prev != val:
                    conflicts.append(f"w={key[0]} rep={key[1]}: {prev} vs {val} ({src.name})")
                else:
                    agreements += 1
                continue
            cells[key] = rec
    return cells, conflicts, agreements


def spearman(xs: list[float], ys: list[float]) -> float:
    def rank(v: list[float]) -> list[float]:
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r

    rx, ry = rank(xs), rank(ys)
    n = len(xs)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return num / den if den else float("nan")


def median(v: list[float]) -> float:
    s = sorted(v)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def main() -> None:
    cells, conflicts, agreements = load()
    print(f"cells: {len(cells)}   overlapping-cell agreements: {agreements}   "
          f"conflicts: {len(conflicts)}")
    for c in conflicts:
        print("  CONFLICT " + c)

    widths = sorted({w for w, _ in cells})
    print()
    print(f"{'width':>6} {'n':>3} {'reach32':>9} {'P(reach)':>9} "
          f"{'median l*':>10} {'min':>4} {'max':>4}")
    print("-" * 52)
    rows = []
    for w in widths:
        recs = [r for (ww, _), r in cells.items() if ww == w]
        vals = [r["first_layer_min_eig_le_floor"] for r in recs]
        reach = sum(v is None for v in vals)
        failed = [v for v in vals if v is not None]
        cens = [CENSOR if v is None else v for v in vals]
        rows.append((w, len(vals), reach, reach / len(vals), median(cens),
                     min(failed) if failed else None, max(failed) if failed else None))
        print(f"{w:>6} {len(vals):>3} {reach:>4}/{len(vals):<4} {reach/len(vals):>9.2f} "
              f"{median(cens):>10.1f} {str(min(failed)) if failed else '-':>4} "
              f"{str(max(failed)) if failed else '-':>4}")

    xs = [w for (w, _) in cells]
    ys = [CENSOR if c["first_layer_min_eig_le_floor"] is None
          else c["first_layer_min_eig_le_floor"] for c in cells.values()]
    print()
    print(f"Spearman rho (width vs censored l*), all {len(xs)} cells: {spearman(xs, ys):+.4f}")
    big = [(w, y) for w, y in zip(xs, ys) if w >= 32]
    print(f"Spearman rho, width >= 32 only ({len(big)} cells):        "
          f"{spearman([w for w, _ in big], [y for _, y in big]):+.4f}")

    # KILL_NO_SCALING: monotone trend over 64..224 and 256 separated from 48.
    seq = [(w, m) for (w, _, _, _, m, _, _) in rows if 64 <= w <= 224]
    mono = all(b <= a for (_, a), (_, b) in zip(seq, seq[1:]))
    print()
    print("median l* over 64..224: " + " -> ".join(f"{w}:{m:.1f}" for w, m in seq))
    print(f"  monotone non-increasing: {mono}")
    w48 = [r for r in rows if r[0] == 48][0]
    w256 = [r for r in rows if r[0] == 256][0]
    print(f"  P(reach 32) at w=48: {w48[3]:.2f} ({w48[2]}/{w48[1]});  "
          f"at w=256: {w256[3]:.2f} ({w256[2]}/{w256[1]})")

    first_never = next((w for (w, n, reach, p, *_ ) in rows if w >= 64 and reach == 0), None)
    print(f"\nSmallest width at which NO replicate reaches layer 32: {first_never}")

    # Mechanism: at the failure layer, is min eig at the entrywise-assembly
    # scale eps * n * lambda_max?
    print("\nMechanism check at the failure layer (predeclared: "
          "min_eig ~ eps * n * lambda_max):")
    print(f"{'width':>6} {'cells':>5} {'median |min_eig| / (eps n lam_max)':>36}")
    print("-" * 50)
    for w in widths:
        ratios = []
        for (ww, _), r in cells.items():
            if ww != w:
                continue
            L = r["first_layer_min_eig_le_floor"]
            if L is None or "assembly_scale" not in r["layers"][0]:
                continue
            row = r["layers"][L - 1]
            if row["assembly_scale"] > 0:
                ratios.append(abs(row["min_eig_pre_cov"]) / row["assembly_scale"])
        if ratios:
            print(f"{w:>6} {len(ratios):>5} {median(ratios):>36.3g}")


if __name__ == "__main__":
    main()
