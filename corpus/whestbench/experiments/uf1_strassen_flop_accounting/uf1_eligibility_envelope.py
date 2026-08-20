"""U-F1 addendum: eligibility. Depth d needs k, n divisible by 2^d, but the
champion's folded active widths are ragged. Two lawful responses exist:
dispatch direct (r = 1) or pad to the next multiple of 2^d and pay the padded
volume. This computes the best achievable per-shape ratio

    r_best(W) = min_d [ r_d(W_pad(d)) * (W_pad(d)/W)^2 ],   W_pad = ceil-to-2^d

which is a pure-arithmetic envelope, not a kernel design. No kernel code.
"""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
import sys
sys.path.insert(0, str(HERE))
from uf1_derive_and_verify import matmul_charge, strassen_charge  # noqa: E402

M = 32256
VARIANT = "V1_winograd15_floor"


def best_for_width(W: int) -> tuple[float, int, int]:
    base = matmul_charge(M, W, W)          # cost of the UNPADDED direct call
    best_r, best_d, best_pad = 1.0, 0, W
    for d in range(0, 9):
        step = 1 << d
        Wp = ((W + step - 1) // step) * step
        if (M % step) or Wp > 4 * W:
            continue
        c = strassen_charge(M, Wp, Wp, d, VARIANT)["total"]
        r = c / base
        if r < best_r - 1e-15:
            best_r, best_d, best_pad = r, d, Wp
    return best_r, best_d, best_pad


def main() -> None:
    table = {}
    for W in range(8, 257):
        r, d, wp = best_for_width(W)
        table[W] = {"r_best": r, "depth": d, "padded_width": wp}
    wins = [W for W in table if table[W]["r_best"] < 1.0]
    out = {
        "note": "M=32256 rows; K=N=W; padding charged at full padded volume; "
                "V1 Winograd-15 floor schedule.",
        "widths_evaluated": len(table),
        "widths_with_r_best_below_1": len(wins),
        "min_width_that_pays": min(wins) if wins else None,
        "samples": {str(W): table[W] for W in
                    (8, 16, 24, 32, 48, 64, 96, 100, 127, 128, 129, 160,
                     192, 200, 224, 250, 255, 256)},
        "unweighted_mean_r_best_over_W_8_to_256":
            sum(table[W]["r_best"] for W in table) / len(table),
        "unweighted_mean_r_best_over_W_128_to_256":
            sum(table[W]["r_best"] for W in table if W >= 128)
            / len([W for W in table if W >= 128]),
        "depth_histogram": {},
    }
    for W in table:
        k = str(table[W]["depth"])
        out["depth_histogram"][k] = out["depth_histogram"].get(k, 0) + 1
    (HERE / "uf1_eligibility_envelope.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
