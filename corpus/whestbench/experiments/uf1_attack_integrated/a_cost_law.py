"""A - pin the integrated cost law from the cached 100-MLP scored artifact.

Read-only on the cached artifact. No estimator executed, no scorer imported,
no network, no git. All writes confined to this directory.

Establishes, by exact arithmetic on committed cached data:
  1. effective_compute_i == flops_used_i + residual_wall_time_s_i * LAMBDA
  2. residual_wall_time_s_i == wall_i - backend_i - overhead_i
  3. multiplier_i == effective_compute_i / B
  4. adjusted_i == mse_i * max(0.1, multiplier_i)
  5. reported score == mean_i(adjusted_i)   (NOT mean(mse)*mean(mult))
and reconciles the two residual framings in the U-F1 record.
"""
from __future__ import annotations

import json
import math
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(
    HERE, "..", "t4_kerdock_descriptive_rescore", "kerdock_v3_official100.json"
)
LAMBDA = 1e11  # residual-second -> effective-compute conversion (to be verified)

with open(ART, encoding="utf-8-sig") as fh:
    doc = json.load(fh)

res = doc["results"]
cfg = doc["run_config"]
B = float(cfg["flop_budget"])
per = res["per_mlp"]
n = len(per)

rows = []
for m in per:
    br = m["breakdowns"]["estimator"]
    ops = br["by_namespace"]["estimator.estimator-client"]["operations"]
    rows.append(
        dict(
            idx=m["mlp_index"],
            mse=m["final_layer_mse"],
            adj=m["adjusted_final_layer_score"],
            flops=m["flops_used"],
            eff=m["effective_compute"],
            wall=m["wall_time_s"],
            backend=m["flopscope_backend_time_s"],
            overhead=m["flopscope_overhead_time_s"],
            resid=m["residual_wall_time_s"],
            matmul=ops["matmul"]["flop_cost"],
            matmul_calls=ops["matmul"]["calls"],
            move=sum(
                ops[k]["flop_cost"]
                for k in ("add", "subtract", "copyto", "concatenate", "stack")
                if k in ops
            ),
        )
    )

out = {"artifact": os.path.relpath(ART, HERE), "B": B, "n_mlps": n}

# --- law 1: effective compute = flops + residual*LAMBDA -----------------
e1 = max(abs(r["eff"] - (r["flops"] + r["resid"] * LAMBDA)) for r in rows)
out["law1_effective_compute"] = {
    "formula": "eff = flops_used + residual_wall_time_s * 1e11",
    "max_abs_err_flops": e1,
    "max_rel_err": max(
        abs(r["eff"] - (r["flops"] + r["resid"] * LAMBDA)) / r["eff"] for r in rows
    ),
}

# --- law 2: residual = wall - backend - overhead ------------------------
e2 = max(abs(r["resid"] - (r["wall"] - r["backend"] - r["overhead"])) for r in rows)
out["law2_residual_definition"] = {
    "formula": "residual = wall - backend - overhead",
    "max_abs_err_s": e2,
}

# --- law 3/4: multiplier and per-mlp adjusted --------------------------
e3 = max(abs(r["adj"] - r["mse"] * max(0.1, r["eff"] / B)) for r in rows)
out["law3_adjusted"] = {
    "formula": "adj_i = mse_i * max(0.1, eff_i / B)",
    "max_abs_err": e3,
    "max_rel_err": max(
        abs(r["adj"] - r["mse"] * max(0.1, r["eff"] / B)) / r["adj"] for r in rows
    ),
    "n_at_floor": sum(1 for r in rows if r["eff"] / B < 0.1),
}

# --- law 5: score is the MEAN of per-mlp products ----------------------
mean_adj = statistics.fmean(r["adj"] for r in rows)
mean_mse = statistics.fmean(r["mse"] for r in rows)
mean_mult = statistics.fmean(max(0.1, r["eff"] / B) for r in rows)
out["law5_aggregation"] = {
    "reported_score": res["adjusted_final_layer_score"],
    "mean_of_per_mlp_products": mean_adj,
    "rel_err": abs(mean_adj - res["adjusted_final_layer_score"])
    / res["adjusted_final_layer_score"],
    "naive_meanMSE_times_meanMULT": mean_mse * mean_mult,
    "naive_rel_err_vs_reported": (mean_mse * mean_mult)
    / res["adjusted_final_layer_score"]
    - 1.0,
    "reported_mean_mse": res["final_layer_mse"],
    "reported_mean_multiplier": res["mean_score_multiplier"],
    "reported_mean_effective_compute": res["mean_effective_compute"],
    "recomputed_mean_effective_compute": statistics.fmean(r["eff"] for r in rows),
}

# --- decomposition: means vs MLP #0 ------------------------------------
mm = lambda k: statistics.fmean(r[k] for r in rows)
mlp0 = rows[0]
out["decomposition"] = {
    "mlp0_flops": mlp0["flops"],
    "mlp0_matmul": mlp0["matmul"],
    "mlp0_matmul_share": mlp0["matmul"] / mlp0["flops"],
    "mlp0_residual_s": mlp0["resid"],
    "mlp0_residual_charge": mlp0["resid"] * LAMBDA,
    "mlp0_eff": mlp0["eff"],
    "mlp0_residual_share_of_own_eff": mlp0["resid"] * LAMBDA / mlp0["eff"],
    "mean_flops": mm("flops"),
    "mean_matmul": mm("matmul"),
    "mean_matmul_share_of_flops": mm("matmul") / mm("flops"),
    "mean_matmul_share_per_mlp": statistics.fmean(
        r["matmul"] / r["flops"] for r in rows
    ),
    "mean_movement_flops": mm("move"),
    "mean_residual_s": mm("resid"),
    "max_residual_s": max(r["resid"] for r in rows),
    "mean_residual_charge": mm("resid") * LAMBDA,
    "mean_eff": mm("eff"),
    "mean_residual_charge_share_of_mean_eff": mm("resid") * LAMBDA / mm("eff"),
    "mean_matmul_share_of_mean_eff": mm("matmul") / mm("eff"),
    "mean_matmul_calls": mm("matmul_calls"),
    "flops_spread_min": min(r["flops"] for r in rows),
    "flops_spread_max": max(r["flops"] for r in rows),
}

# --- reconciliation of the two residual framings -----------------------
out["residual_framing_reconciliation"] = {
    "framing_A_9.08e9_is_5.83pct": {
        "source": "MLP #0 of this artifact",
        "residual_charge": mlp0["resid"] * LAMBDA,
        "denominator_used": mlp0["eff"],
        "pct": 100.0 * mlp0["resid"] * LAMBDA / mlp0["eff"],
        "pct_if_denominator_were_champion_C_1.7683e11": 100.0
        * mlp0["resid"]
        * LAMBDA
        / 1.7683e11,
    },
    "framing_B_0.080s_is_4.5pct": {
        "source": "100-MLP mean of this artifact",
        "mean_residual_s": mm("resid"),
        "residual_charge": mm("resid") * LAMBDA,
        "denominator_used": mm("eff"),
        "pct": 100.0 * mm("resid") * LAMBDA / mm("eff"),
    },
    "verdict": (
        "Both are arithmetically correct but they are different objects: "
        "5.83% is MLP #0's residual share of MLP #0's OWN effective compute; "
        "4.5% is the 100-MLP mean residual charge as a share of the 100-MLP "
        "mean effective compute. Neither is 'residual as a share of C=1.7683e11' "
        "-- the champion C is a mean over a different graded set. The correct "
        "integrated statement is the per-MLP one, because the score is a mean "
        "of per-MLP products."
    ),
}

with open(os.path.join(HERE, "a_cost_law.json"), "w", encoding="utf-8") as fh:
    json.dump(out, fh, indent=2)

for k, v in out.items():
    print("==", k)
    print(json.dumps(v, indent=2)[:2400])
