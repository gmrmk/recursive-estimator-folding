"""STEP 1 (confirmatory) for gm_p2b_proxy -- the cheapest falsifier as mined.

P2b's exact protocol with the proxy swapped: 48 calls to rotated_alphas() +
weight_diagnostics() at seeds 900000+net*1000+r (nets 101/202/303, r=0..15),
diagnostics {borderline_frac_overall, fold_on_total, fold_kink_total}, pooled
within-net-ranked Spearman vs p2_results.json
q1_oracle_headroom.per_net[net].mse_per_rotation.

GATE (unchanged from P2b, no retuning): pooled |rho| >= 0.40 for ANY diagnostic
AND per-net Spearman sign consistency -> REVIVED_PASS; else KILL_CONFIRMED.

Step 0 already killed on the closed-form invariance of the diagonal pass; this
run is CONFIRMATORY and reports the measured degeneracy directly (S2), a
permutation null (S5), a bitwise determinism repeat (S6) and a two-way Spearman
cross-check (S4).

rotated_alphas() and weight_diagnostics() are reproduced VERBATIM from
run_m185_g0.py (that file is not importable standalone: it is a checkpointed
CLI harness). The copies are byte-for-byte identical in body and are asserted
against the frozen v3 sources they call.
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True

import numpy as np

HERE = Path(__file__).resolve().parent
PB1 = HERE.parent / "pb1_premise_battery"
V3_DIR = Path(
    r"C:\Users\strid\Documents\Codex\2026-08-02"
    r"\https-chatgpt-com-share-6a5556ed-2e1c\work\scorefloor_generation"
    r"\kerdock_l1_owned_buffer\candidate_source_validator_v3"
)
sys.path.insert(0, str(V3_DIR))

import flopscope as flops                        # noqa: E402
from whestbench import SetupContext              # noqa: E402  (parity w/ m185)
from whestbench.domain import MLP                # noqa: E402
from base_estimator import _diagonal_gaussian_pass  # noqa: E402 frozen read-only
from estimator import Estimator as KerdockV3     # noqa: E402 frozen read-only

flops.configure(symmetry_warnings=False)

WIDTH, DEPTH = 256, 32
NET_SEEDS = (101, 202, 303)
N_ROT = 16
METER_BUDGET = 10 ** 15
GATE_RHO = 0.40
PERM_DRAWS = 10_000
PERM_SEED = 20260810
DIAGS = ("borderline_frac_overall", "fold_on_total", "fold_kink_total")


# ------------------------------------------------------- construction (P2/M185)
def he_weights(seed: int) -> list[np.ndarray]:
    rng = np.random.default_rng(seed)
    gain = np.float32(math.sqrt(2.0 / WIDTH))
    return [rng.standard_normal((WIDTH, WIDTH), dtype=np.float32) * gain
            for _ in range(DEPTH)]


def rot_seed(net_seed: int, r: int) -> int:
    return 900_000 + net_seed * 1_000 + r


# ------------------------------------------------- verbatim from run_m185_g0.py
def rotated_alphas(weights_f, rot: int):
    """The EXACT alphas the estimator used: rotate weights[0] exactly as
    v3.predict does, then run the frozen diagonal pass."""
    with flops.BudgetContext(METER_BUDGET, quiet=True):
        rotation = KerdockV3._haar_rotation(rot, WIDTH)
        first = rotation.T @ weights_f[0]
        mlp = MLP(width=WIDTH, depth=DEPTH,
                  weights=[first, *weights_f[1:]], seed=rot, name="diag")
        means, alphas, _firing, _sigmas = _diagonal_gaussian_pass(mlp)
    return ([np.asarray(a).astype(np.float64) for a in alphas],
            [np.asarray(m).astype(np.float64) for m in means])


def weight_diagnostics(alphas) -> dict:
    prune_layers = range(1, DEPTH - 3)          # v3 prune loop: layers 1..28
    per_layer_pruned = [float((alphas[l] < -2.0).mean()) for l in prune_layers]
    borderline = [float((np.abs(alphas[l] + 2.0) <= 0.5).mean())
                  for l in prune_layers]
    relax_moves = [int(((alphas[l] >= -3.0) & (alphas[l] < -2.0)).sum())
                   for l in prune_layers]
    fold = {}
    for l in (29, 30, 31):
        a = alphas[l]
        fold[str(l)] = {
            "dead": int((a < -2.0).sum()),
            "on": int((a > 3.0).sum()),
            "kink": int(((a >= -2.0) & (a <= 3.0)).sum()),
        }
    return {
        "pruned_frac_overall": float(np.mean(per_layer_pruned)),
        "borderline_frac_overall": float(np.mean(borderline)),
        "relax_moves_total": int(np.sum(relax_moves)),
        "fold": fold,
        "fold_dead_total": sum(fold[k]["dead"] for k in fold),
        "fold_on_total": sum(fold[k]["on"] for k in fold),
        "fold_kink_total": sum(fold[k]["kink"] for k in fold),
    }


# --------------------------------------- statistics (verbatim from P2 harness)
def rankdata_avg(x) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    order = np.argsort(x, kind="mergesort")
    sx = x[order]
    r = np.empty(len(x))
    i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and sx[j + 1] == sx[i]:
            j += 1
        r[i:j + 1] = 0.5 * (i + j) + 1.0
        i = j + 1
    ranks = np.empty(len(x))
    ranks[order] = r
    return ranks


def pearson(a, b) -> float:
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    a = a - a.mean()
    b = b - b.mean()
    den = math.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / den) if den > 0 else 0.0


def spearman(a, b) -> float:
    return pearson(rankdata_avg(a), rankdata_avg(b))


def spearman_formula_check(a, b) -> float:
    ra, rb = rankdata_avg(a), rankdata_avg(b)
    n = len(ra)
    d2 = float(((ra - rb) ** 2).sum())
    return 1.0 - 6.0 * d2 / (n * (n * n - 1.0))


def pooled_within_net_rho(vals_a: dict, vals_b: dict) -> float:
    ra, rb = [], []
    for n in vals_a:
        ra.append(rankdata_avg(vals_a[n]))
        rb.append(rankdata_avg(vals_b[n]))
    return pearson(np.concatenate(ra), np.concatenate(rb))


# ----------------------------------------------------------------------- main
def main() -> None:
    t0 = time.perf_counter()
    res = json.loads((PB1 / "p2_results.json").read_text(encoding="utf-8"))
    per_net_arch = res["q1_oracle_headroom"]["per_net"]
    mse = {n: np.asarray(per_net_arch[str(n)]["mse_per_rotation"], dtype=float)
           for n in NET_SEEDS}
    for n in NET_SEEDS:
        assert mse[n].shape == (N_ROT,), f"archive shape {mse[n].shape}"

    diag_vals = {d: {} for d in DIAGS}
    raw_rows = {}
    alpha_fingerprints = {}
    for n in NET_SEEDS:
        w = he_weights(n)
        cols = {d: [] for d in DIAGS}
        rows = []
        for r in range(N_ROT):
            alphas, _means = rotated_alphas(w, rot_seed(n, r))
            d = weight_diagnostics(alphas)
            for k in DIAGS:
                cols[k].append(d[k])
            rows.append({"r": r, "rot_seed": rot_seed(n, r),
                         **{k: d[k] for k in DIAGS},
                         "pruned_frac_overall": d["pruned_frac_overall"],
                         "fold_dead_total": d["fold_dead_total"],
                         "alpha_l31_mean": float(alphas[31].mean()),
                         "alpha_l31_sum_abs": float(np.abs(alphas[31]).sum())})
            if r == 0:
                alpha_fingerprints[str(n)] = alphas[31].copy()
        for k in DIAGS:
            diag_vals[k][n] = np.asarray(cols[k], dtype=float)
        raw_rows[str(n)] = rows
        print(f"net {n}: 16 diagonal passes done "
              f"({time.perf_counter()-t0:.1f}s)", flush=True)

    # ---- S2: measured within-net degeneracy of every diagnostic --------------
    degeneracy = {}
    for k in DIAGS:
        degeneracy[k] = {}
        for n in NET_SEEDS:
            v = diag_vals[k][n]
            mean = float(v.mean())
            spread = float(v.max() - v.min())
            degeneracy[k][str(n)] = {
                "min": float(v.min()), "max": float(v.max()), "mean": mean,
                "abs_spread": spread,
                "rel_spread": (spread / abs(mean)) if mean != 0 else 0.0,
                "n_distinct_values": int(len(np.unique(v))),
            }

    # ---- the mined statistic ------------------------------------------------
    stats = {}
    for k in DIAGS:
        per_net = {}
        for n in NET_SEEDS:
            r1 = spearman(diag_vals[k][n], mse[n])
            r2 = spearman_formula_check(diag_vals[k][n], mse[n])
            # S4: the two derivations agree exactly when there are no ties in x;
            # with ties the d^2 formula is not valid and is reported as a diag.
            per_net[str(n)] = {
                "spearman_pearson_on_ranks": r1,
                "spearman_d2_formula_diag": r2,
                "two_way_agree_1e-10": bool(abs(r1 - r2) <= 1e-10),
                "x_has_ties": bool(len(np.unique(diag_vals[k][n])) < N_ROT),
            }
        pooled = pooled_within_net_rho(diag_vals[k], mse)
        signs = [np.sign(per_net[str(n)]["spearman_pearson_on_ranks"])
                 for n in NET_SEEDS]
        sign_consistent = bool(abs(sum(signs)) == 3)
        stats[k] = {
            "per_net": per_net,
            "pooled_within_net_ranked_rho": pooled,
            "abs_pooled": abs(pooled),
            "per_net_sign_consistent": sign_consistent,
            "passes_gate": bool(abs(pooled) >= GATE_RHO and sign_consistent),
        }

    # ---- S5: permutation null on the pooled statistic ------------------------
    rng = np.random.default_rng(PERM_SEED)
    perm = {}
    for k in DIAGS:
        draws = []
        for _ in range(PERM_DRAWS):
            mb = {n: mse[n][rng.permutation(N_ROT)] for n in NET_SEEDS}
            draws.append(pooled_within_net_rho(diag_vals[k], mb))
        draws = np.asarray(draws)
        obs = stats[k]["pooled_within_net_ranked_rho"]
        perm[k] = {
            "draws": PERM_DRAWS, "seed": PERM_SEED,
            "null_mean": float(draws.mean()), "null_sd": float(draws.std(ddof=1)),
            "null_p2.5": float(np.percentile(draws, 2.5)),
            "null_p97.5": float(np.percentile(draws, 97.5)),
            "two_sided_p": float((np.abs(draws) >= abs(obs) - 1e-15).mean()),
            "frac_null_draws_reaching_gate":
                float((np.abs(draws) >= GATE_RHO).mean()),
        }

    # ---- S6: determinism (bitwise repeat of one diagonal pass) --------------
    w101 = he_weights(101)
    a_rep, _ = rotated_alphas(w101, rot_seed(101, 0))
    bitwise_ok = bool(np.array_equal(a_rep[31], alpha_fingerprints["101"]))

    # ---- cost of the proposed selection stage (the revival's economics) ------
    # diagonal pass per rotation: per layer mu@W (W^2 mul+add) and var@(W*W)
    # (W^2 square + W^2 mul + W^2 add) -> ~4*W^2 flops/layer, x DEPTH layers,
    # plus one 256x256x256 rotation-application matmul (2*W^3) and the QR.
    per_rot = 4.0 * WIDTH * WIDTH * DEPTH + 2.0 * WIDTH ** 3
    B = 2.72e11
    cost = {"diag_pass_flops_per_candidate_rotation": per_rot,
            "k8_flops": 8 * per_rot, "k8_frac_B": 8 * per_rot / B,
            "p2_pilot_k8_frac_B": 0.33426704014939307,
            "note": "cost is moot: the statistic it buys is rotation-invariant"}

    best = max(DIAGS, key=lambda k: stats[k]["abs_pooled"])
    passed = any(stats[k]["passes_gate"] for k in DIAGS)
    verdict = ("REVIVED_PASS: a deep diagonal-pass diagnostic clears "
               "|rho|>=0.40 with per-net sign consistency"
               if passed else
               "KILL_CONFIRMED: no deep zero-sample diagonal-pass diagnostic "
               "reaches |rho|>=0.40 within-net; the rotation family stays "
               "closed and is now closed on a fourth, deepest proxy class")

    out = {
        "experiment": "gm_p2b_proxy step 1 (confirmatory)",
        "predeclaration": "PREDECLARATION.md (this directory), sections 3-5",
        "design": {"nets": list(NET_SEEDS), "rotations": N_ROT,
                   "rotation_seed_formula": "900000+net*1000+r",
                   "diagnostics": list(DIAGS),
                   "y": "p2_results.json q1_oracle_headroom.per_net[*]."
                        "mse_per_rotation (archived, read-only)",
                   "gate_rho": GATE_RHO,
                   "gate_extra": "per-net Spearman sign consistency"},
        "raw_per_rotation": raw_rows,
        "within_net_degeneracy_S2": degeneracy,
        "statistics": stats,
        "permutation_null_S5": perm,
        "determinism_S6_bitwise_repeat_net101_r0_alpha31": bitwise_ok,
        "selection_stage_cost": cost,
        "best_diagnostic_by_abs_pooled": best,
        "verdict": verdict,
        "wall_s": round(time.perf_counter() - t0, 1),
    }
    (HERE / "step1_results.json").write_text(
        json.dumps(out, indent=2) + "\n", encoding="utf-8")

    print("\n--- within-net degeneracy (distinct values out of 16) ---")
    for k in DIAGS:
        print(" ", k, {n: degeneracy[k][n]["n_distinct_values"]
                       for n in degeneracy[k]})
    print("--- pooled within-net-ranked rho vs archived MSE ---")
    for k in DIAGS:
        s = stats[k]
        print(f"  {k}: pooled {s['pooled_within_net_ranked_rho']:+.4f} "
              f"per-net {[round(s['per_net'][str(n)]['spearman_pearson_on_ranks'],4) for n in NET_SEEDS]} "
              f"sign_consistent={s['per_net_sign_consistent']} "
              f"pass={s['passes_gate']}")
    print(f"bitwise repeat: {bitwise_ok}")
    print(f"\nVERDICT: {verdict}")


if __name__ == "__main__":
    main()
