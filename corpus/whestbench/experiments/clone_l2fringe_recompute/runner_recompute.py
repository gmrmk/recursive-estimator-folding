"""Independent static recompute of Codex's kerdock_g16_l2_fringe compute win.

Reads Codex's OWN committed per-network FlopScope receipts (the arm-run JSONs)
and re-aggregates the FLOP-only ratio from the per-op bills, rather than
trusting the summary's effective_compute.point = 0.949316. Also cross-checks
the cost-model route arithmetic (the l2-fringe two-level Winograd route vs the
parent owned-batched route) on the dominant production shape.

Reads only committed dev-side receipts and the candidate's own cost_model.py.
No truth, no holdout, no scorer, no network execution, zero billed FLOPs. The
SCORE half (-4.948%) stays [R] until a lawful owner-keyed truth run; this cell
certifies only the compute-side, FLOP-only, transferable half.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

CLONE = Path("C:/Users/strid/Documents/Codex/2026-07-07/will-you-have-a-look-at")
RPT = CLONE / "experiments/whest/reports/g16-l2-fringe-fresh-linux"
COST_MODEL = (CLONE / "experiments/whest/candidates/kerdock_g16_l2_fringe"
              / "cost_model.py")


def arm_flops(path: Path):
    d = json.loads(path.read_text(encoding="utf-8"))
    per = d["results"]["per_mlp"]
    flops = [m["flops_used"] for m in per]
    eff = [m["effective_compute"] for m in per]
    matmul = []
    for m in per:
        ops = (m["breakdowns"]["estimator"]["by_namespace"]
               ["estimator.estimator-client"]["operations"])
        matmul.append(ops.get("matmul", {}).get("flop_cost", 0))
    return flops, eff, matmul


def load_cost_model():
    spec = importlib.util.spec_from_file_location("cm_l2fringe", COST_MODEL)
    cm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cm)
    return cm


def main() -> None:
    cand_f, cand_e, cand_mm = arm_flops(RPT / "repeat0-candidate.json")
    par_f, par_e, par_mm = arm_flops(RPT / "repeat0-parent.json")
    n = len(cand_f)

    # Independently re-aggregated FLOP-only ratio (the lambda-dies, transferable
    # number) from Codex's own per-net per-op receipts.
    flop_only_ratio = sum(cand_f) / sum(par_f)
    eff_ratio = sum(cand_e) / sum(par_e)          # includes Linux wall residual
    matmul_ratio = sum(cand_mm) / sum(par_mm)     # the pure scheduling win

    # Mechanism cross-check: the cost-model route arithmetic on the dominant
    # even production shape. The candidate route is the grouped-L2 two-level
    # Winograd fringe route; the parent is the owned-batched single-level route.
    cm = load_cost_model()
    m, k, nn = 4096, 256, 256
    cand_bill = cm.grouped_l2_candidate_bill(m, k, nn).total
    par_bill = cm.owned_batched_candidate_bill(m, k, nn).total
    route_ratio = cand_bill / par_bill

    print(json.dumps({
        "flop_only_ratio": round(flop_only_ratio, 6),
        "effective_compute_ratio": round(eff_ratio, 6),
        "matmul_only_ratio": round(matmul_ratio, 6),
        "cost_model_route_ratio_4096x256x256": round(route_ratio, 6),
        "n_nets": n,
        "candidate_matmul_share": round(sum(cand_mm) / sum(cand_f), 6),
        "reported_effective_compute_point": 0.949316,
    }))


if __name__ == "__main__":
    main()
