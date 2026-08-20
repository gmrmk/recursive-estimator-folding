"""U-F1 steps 2-5: closed-form charged ratio r(d), metered verification,
score translation, rival reconciliation.

Signal 1 (analytic): exact integer closed form for the charged FLOP bill of
Strassen-Winograd at recursion depth d under the empirically-metered
flopscope v0.10.0 price table.

Signal 2 (metered): a real recursive Strassen-Winograd built out of flopscope
primitives, run at small scale under a BudgetContext, charged FLOPs compared
bit-for-bit against the closed form, plus a numerical-parity check against the
classical product.

No estimator source is imported; no champion or m245 module is touched.
"""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import numpy as np

import flopscope as fl
import flopscope.numpy as fnp

HERE = Path(__file__).resolve().parent
BUDGET = 10**18

# ---------------------------------------------------------------------------
# Empirically-metered price table (see uf1_price_table.json). rate(f32)=1,
# rate(f64)=2; every op below is weight 1.0 except empty/zeros (0.0).
#   matmul (m,k)@(k,n)        : 2*m*k*n - m*n          per batch item
#   add/subtract/multiply     : 1 per element  (out= is free)
#   copyto / .copy / concat   : 1 per element
#   empty / zeros / slice view/ swapaxes : 0
# The dtype rate multiplies EVERY term identically, so it cancels in r(d).
# ---------------------------------------------------------------------------


def matmul_charge(m: int, k: int, n: int, batch: int = 1) -> int:
    return batch * (2 * m * k * n - m * n)


# ---- variant add-schedules, per Strassen node, in units of block elements ---
# (a_ops, b_ops, c_ops) = number of billed elementwise ops on blocks of size
# (m/2 x k/2), (k/2 x n/2), (m/2 x n/2) respectively.
VARIANTS = {
    # V1 FLOOR: Strassen-Winograd, 15 adds (8 pre + 7 post), strided views,
    # preallocated out= buffers, zero explicit copies. Most favourable.
    "V1_winograd15_floor": (4, 4, 7),
    # V2 BATCHED Winograd: same 15 adds, plus the 2 untransformed left operands
    # (A11, A12) and 2 untransformed right operands (B11, B21) must be COPIED
    # into the contiguous 7-stack that a single batched matmul call needs.
    "V2_winograd15_batched": (4 + 2, 4 + 2, 7),
    # V3 CLASSICAL Strassen, 18 adds (10 pre + 8 post), still copy-free.
    "V3_strassen18_floor": (5, 5, 8),
    # V4 AS-IMPLEMENTED (M218 sidecar idiom: copyto-then-add for every one of
    # the 7 transforms, 4 copyto + 8 add/sub in the recombination).
    "V4_m218_copy_idiom": (7 + 4, 7 + 4, 4 + 8),
}


def strassen_charge(M: int, K: int, N: int, d: int, variant: str) -> dict:
    """Exact integer charged cost at recursion depth d (single product)."""
    a_ops, b_ops, c_ops = VARIANTS[variant]
    if d == 0:
        return {"matmul": matmul_charge(M, K, N), "movement": 0,
                "total": matmul_charge(M, K, N)}
    for lvl in range(d):
        if (M >> lvl) % 2 or (K >> lvl) % 2 or (N >> lvl) % 2:
            raise ValueError(f"shape not 2-divisible to depth {d}")
    movement = 0
    for lvl in range(d):
        nodes = 7**lvl
        m, k, n = M >> lvl, K >> lvl, N >> lvl
        per_node = (a_ops * (m // 2) * (k // 2)
                    + b_ops * (k // 2) * (n // 2)
                    + c_ops * (m // 2) * (n // 2))
        movement += nodes * per_node
    leaves = 7**d
    mm = matmul_charge(M >> d, K >> d, N >> d, batch=leaves)
    return {"matmul": mm, "movement": movement, "total": mm + movement}


def closed_form_total(M: int, K: int, N: int, d: int, variant: str) -> Fraction:
    """Closed form, exact rationals, independent re-derivation of the above.

    matmul(d)   = (7/8)^d * 2MKN - (7/4)^d * MN
    movement(d) = (a*MK + b*KN + c*MN)/4 * ((7/4)^d - 1) / (7/4 - 1)
                = (a*MK + b*KN + c*MN)/3 * ((7/4)^d - 1)
    """
    a_ops, b_ops, c_ops = VARIANTS[variant]
    f78 = Fraction(7, 8) ** d
    f74 = Fraction(7, 4) ** d
    mm = f78 * 2 * M * K * N - f74 * M * N
    mv = Fraction(a_ops * M * K + b_ops * K * N + c_ops * M * N, 3) * (f74 - 1)
    return mm + mv


# ---------------------------------------------------------------------------
# Metered Strassen-Winograd (signal 2)
# ---------------------------------------------------------------------------

def sw_product(A, B, C, depth: int) -> None:
    """Recursive Strassen-Winograd writing A@B into C. V1 floor schedule."""
    if depth <= 0:
        fnp.matmul(A, B, out=C)
        return
    m, k = int(A.shape[-2]), int(A.shape[-1])
    n = int(B.shape[-1])
    hm, hk, hn = m // 2, k // 2, n // 2
    dt = A.dtype

    A11, A12 = A[..., :hm, :hk], A[..., :hm, hk:]
    A21, A22 = A[..., hm:, :hk], A[..., hm:, hk:]
    B11, B12 = B[..., :hk, :hn], B[..., :hk, hn:]
    B21, B22 = B[..., hk:, :hn], B[..., hk:, hn:]

    ash = tuple(A.shape[:-2]) + (hm, hk)
    bsh = tuple(B.shape[:-2]) + (hk, hn)
    csh = tuple(C.shape[:-2]) + (hm, hn)

    S1 = fnp.empty(ash, dtype=dt); fnp.add(A21, A22, out=S1)
    S2 = fnp.empty(ash, dtype=dt); fnp.subtract(S1, A11, out=S2)
    S3 = fnp.empty(ash, dtype=dt); fnp.subtract(A11, A21, out=S3)
    S4 = fnp.empty(ash, dtype=dt); fnp.subtract(A12, S2, out=S4)

    T1 = fnp.empty(bsh, dtype=dt); fnp.subtract(B12, B11, out=T1)
    T2 = fnp.empty(bsh, dtype=dt); fnp.subtract(B22, T1, out=T2)
    T3 = fnp.empty(bsh, dtype=dt); fnp.subtract(B22, B12, out=T3)
    T4 = fnp.empty(bsh, dtype=dt); fnp.subtract(T2, B21, out=T4)

    M1 = fnp.empty(csh, dtype=dt); sw_product(A11, B11, M1, depth - 1)
    M2 = fnp.empty(csh, dtype=dt); sw_product(A12, B21, M2, depth - 1)
    M3 = fnp.empty(csh, dtype=dt); sw_product(S4, B22, M3, depth - 1)
    M4 = fnp.empty(csh, dtype=dt); sw_product(A22, T4, M4, depth - 1)
    M5 = fnp.empty(csh, dtype=dt); sw_product(S1, T1, M5, depth - 1)
    M6 = fnp.empty(csh, dtype=dt); sw_product(S2, T2, M6, depth - 1)
    M7 = fnp.empty(csh, dtype=dt); sw_product(S3, T3, M7, depth - 1)

    C11, C12 = C[..., :hm, :hn], C[..., :hm, hn:]
    C21, C22 = C[..., hm:, :hn], C[..., hm:, hn:]
    fnp.add(M1, M2, out=C11)                                    # U1 -> C11
    U2 = fnp.empty(csh, dtype=dt); fnp.add(M1, M6, out=U2)      # U2
    U3 = fnp.empty(csh, dtype=dt); fnp.add(U2, M7, out=U3)      # U3
    U4 = fnp.empty(csh, dtype=dt); fnp.add(U2, M5, out=U4)      # U4
    fnp.add(U4, M3, out=C12)                                    # U5 -> C12
    fnp.subtract(U3, M4, out=C21)                               # U6 -> C21
    fnp.add(U3, M5, out=C22)                                    # U7 -> C22


def meter_sw(M, K, N, depth, dtype="float32"):
    rng = np.random.default_rng(20260810 + depth)
    a = np.asarray(rng.standard_normal((M, K)), dtype=dtype)
    b = np.asarray(rng.standard_normal((K, N)), dtype=dtype)
    fa, fb = fnp.asarray(a), fnp.asarray(b)
    with fl.BudgetContext(flop_budget=BUDGET, quiet=True) as bud:
        C = fnp.empty((M, N), dtype=getattr(fnp, dtype))
        sw_product(fa, fb, C, depth)
        used = int(bud.summary_dict()["flops_used"])
    ref = np.asarray(a, dtype=np.float64) @ np.asarray(b, dtype=np.float64)
    got = np.asarray(C, dtype=np.float64)
    rel = float(np.linalg.norm(got - ref) / np.linalg.norm(ref))
    return used, rel


def main() -> None:
    fl.configure(symmetry_warnings=False)
    out: dict[str, object] = {}

    # ---------------- extra price probes the derivation leans on -----------
    probes = {}
    rng = np.random.default_rng(1)
    A = fnp.asarray(np.asarray(rng.standard_normal((16, 8)), dtype="float32"))
    B = fnp.asarray(np.asarray(rng.standard_normal((8, 8)), dtype="float32"))
    O = fnp.empty((16, 8), dtype=fnp.float32)
    with fl.BudgetContext(flop_budget=BUDGET, quiet=True) as b:
        fnp.matmul(A, B, out=O)
        probes["matmul_out_16x8@8x8"] = int(b.summary_dict()["flops_used"])
    probes["matmul_out_formula"] = matmul_charge(16, 8, 8)
    with fl.BudgetContext(flop_budget=BUDGET, quiet=True) as b:
        fnp.matmul(A[8:, :4], B[:4, :4])
        probes["matmul_strided_view_8x4@4x4"] = int(b.summary_dict()["flops_used"])
    probes["matmul_strided_formula"] = matmul_charge(8, 4, 4)
    v = fnp.asarray(np.arange(64, dtype="float32"))
    idx = fnp.asarray(np.arange(64))
    with fl.BudgetContext(flop_budget=BUDGET, quiet=True) as b:
        fnp.take(v, idx)
        probes["take_64_gather"] = int(b.summary_dict()["flops_used"])
    with fl.BudgetContext(flop_budget=BUDGET, quiet=True) as b:
        fnp.sort(v)
        probes["sort_64"] = int(b.summary_dict()["flops_used"])
    out["extra_price_probes"] = probes

    # ---------------- signal 2: metered vs closed form ---------------------
    ver = []
    for (M, K, N) in [(256, 64, 64), (1024, 64, 64), (512, 128, 128)]:
        maxd = 0
        while (M >> (maxd + 1)) % 1 == 0 and (K >> maxd) % 2 == 0 \
                and (N >> maxd) % 2 == 0 and (M >> maxd) % 2 == 0 and maxd < 4:
            maxd += 1
        for d in range(0, maxd + 1):
            used, rel = meter_sw(M, K, N, d)
            pred = strassen_charge(M, K, N, d, "V1_winograd15_floor")
            cf = closed_form_total(M, K, N, d, "V1_winograd15_floor")
            ver.append({
                "shape": f"({M}x{K})@({K}x{N})", "depth": d,
                "metered_charged_flops": used,
                "analytic_charged_flops": pred["total"],
                "closed_form_charged_flops": (int(cf) if cf.denominator == 1
                                              else float(cf)),
                "match_metered_vs_analytic": used == pred["total"],
                "match_analytic_vs_closed_form": Fraction(pred["total"]) == cf,
                "relative_frobenius_vs_classical": rel,
                "ratio_vs_depth0": pred["total"] / matmul_charge(M, K, N),
            })
    out["verification"] = ver

    # ---------------- production shape: r(d) ------------------------------
    prod = {}
    for (label, M) in [("m64512", 64512), ("m32256", 32256)]:
        K = N = 256
        base = matmul_charge(M, K, N)
        rows = {}
        for d in range(0, 6):
            entry = {"classical_charged": base}
            for variant in VARIANTS:
                c = strassen_charge(M, K, N, d, variant)
                cf = closed_form_total(M, K, N, d, variant)
                assert Fraction(c["total"]) == cf, (variant, d)
                entry[variant] = {
                    "matmul": c["matmul"], "movement": c["movement"],
                    "total": c["total"], "r": c["total"] / base,
                }
            rows[f"d{d}"] = entry
        prod[label] = {"M": M, "K": K, "N": N,
                       "classical_charged_flops": base, "by_depth": rows}
    out["production_shape"] = prod

    # ---------------- width sensitivity (folded active widths) ------------
    wid = {}
    for W in (256, 192, 128, 64):
        M = 32256
        if W % 32:
            continue
        base = matmul_charge(M, W, W)
        wid[f"W{W}"] = {
            "classical": base,
            "r": {f"d{d}": strassen_charge(M, W, W, d,
                                           "V1_winograd15_floor")["total"] / base
                  for d in range(0, 6) if (W >> d) % 2 == 0 or d == 0},
        }
    out["width_sensitivity_m32256"] = wid

    # ---------------- score translation -----------------------------------
    C_champ = 1.7683e11
    CB = 0.650
    adjusted = 1.832e-7
    B_budget = C_champ / CB
    raw_mse = adjusted / max(0.1, CB)
    instrumented = 146.794e9
    matmul_lane = 145.138e9
    lane_share_of_instrumented = matmul_lane / instrumented
    eligible_measured = 0.574164          # from INTEGRATED_BATCHED_WINOGRAD_REPORT
    trans = {
        "champion": {"C": C_champ, "B_implied": B_budget, "C_over_B": CB,
                     "adjusted_score": adjusted, "raw_MSE_implied": raw_mse,
                     "instrumented": instrumented, "matmul_lane": matmul_lane,
                     "matmul_share_of_instrumented": lane_share_of_instrumented},
        "by_depth": {},
    }
    M, K, N = 64512, 256, 256
    base = matmul_charge(M, K, N)
    for d in range(0, 6):
        r = strassen_charge(M, K, N, d, "V1_winograd15_floor")["total"] / base
        for tag, frac in (("all_lane_eligible", 1.0),
                          ("measured_eligibility_0.574164", eligible_measured)):
            saved = (1.0 - r) * matmul_lane * frac
            C_new = C_champ - saved
            cb_new = C_new / B_budget
            mult_new = max(0.1, cb_new)
            score_new = raw_mse * mult_new
            trans["by_depth"].setdefault(f"d{d}", {})[tag] = {
                "r_matmul": r,
                "flops_saved": saved,
                "C_new": C_new,
                "C_over_B_new": cb_new,
                "multiplier_new": mult_new,
                "adjusted_score_new": score_new,
                "score_improvement_x": adjusted / score_new,
                "r_C_whole_entry": C_new / C_champ,
            }
    out["score_translation"] = trans

    # ---------------- rival reconciliation ---------------------------------
    target = 1.5412
    needed_mult = adjusted / target / raw_mse           # required multiplier
    needed_CB = needed_mult
    needed_C = needed_CB * B_budget
    needed_rC = needed_C / C_champ
    # implied r on the matmul lane if MSE unchanged and only the lane changes
    needed_r_lane = 1.0 - (C_champ - needed_C) / matmul_lane
    out["rival_reconciliation"] = {
        "claimed_score_improvement_x": target,
        "required_multiplier": needed_mult,
        "required_C_over_B": needed_CB,
        "required_C": needed_C,
        "required_whole_entry_r_C": needed_rC,
        "required_r_on_matmul_lane_if_MSE_unchanged": needed_r_lane,
        "our_r5_floor": strassen_charge(M, K, N, 5, "V1_winograd15_floor")["total"] / base,
        "our_r5_batched": strassen_charge(M, K, N, 5, "V2_winograd15_batched")["total"] / base,
        "our_r5_m218_idiom": strassen_charge(M, K, N, 5, "V4_m218_copy_idiom")["total"] / base,
    }

    # ---------------- cross-check against our own recorded measurements ----
    recorded = {}
    Mr, Kr, Nr = 64512, 256, 256
    br = matmul_charge(Mr, Kr, Nr)
    recorded["corpus_direct_full_product_8.4392B"] = {
        "recorded": 8.4392e9, "computed": br, "delta_rel": br / 8.4392e9 - 1.0}
    l1 = {v: strassen_charge(Mr, Kr, Nr, 1, v)["total"] / br for v in VARIANTS}
    recorded["mutationB_billed_0.880151_at_L1"] = {
        "recorded_r": 0.880151, "model_bracket": l1,
        "inside_bracket": (l1["V1_winograd15_floor"] <= 0.880151
                           <= l1["V4_m218_copy_idiom"])}
    l2 = {v: strassen_charge(Mr, Kr, Nr, 2, v)["total"] / br for v in VARIANTS}
    recorded["corpus_L2_hybrid_6.7128B_r0.795427"] = {
        "recorded_r": 0.795427, "recorded_flops": 6.7128e9,
        "model_bracket": l2,
        "inside_bracket": (l2["V1_winograd15_floor"] <= 0.795427
                           <= l2["V4_m218_copy_idiom"])}
    out["cross_check_vs_recorded"] = recorded

    (HERE / "uf1_results.json").write_text(json.dumps(out, indent=2),
                                           encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
