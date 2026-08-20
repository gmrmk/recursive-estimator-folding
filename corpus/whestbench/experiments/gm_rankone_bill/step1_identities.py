"""Step-1: the four recorded M205 identities under a float32 working dtype.

Frozen modules are imported read-only.  f64 references come from the FROZEN
module; f32 values come from f32_shadow.py.
"""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path
import sys
import time

import numpy as np

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(EXP / "m205_rankone_complete_physical_owner"))

import m205_rankone_complete_physical_owner as F  # frozen, read-only  # noqa: E402
import f32_shadow as S  # noqa: E402

F32 = np.float32
F64 = np.float64


# ---------------- fixtures: byte-identical to the frozen test helpers -------
def cell(width, seed):
    rng = np.random.Generator(np.random.Philox(seed))
    root = rng.normal(size=(width, width))
    covariance = root @ root.T + np.eye(width)
    mean = rng.normal(scale=0.25, size=width)
    weight = rng.normal(size=(width, width + 1))
    return mean, covariance, weight, rng


def distinct_211(width, rng):
    a = np.zeros((width, width, width), dtype=np.float64)
    for i in range(width):
        for j in range(width):
            for k in range(j + 1, width):
                if i == j or i == k:
                    continue
                v = float(rng.normal())
                a[i, j, k] = v
                a[i, k, j] = v
    return a


def owners(width, rng):
    k4 = rng.normal(size=width)
    k31 = rng.normal(size=(width, width))
    np.fill_diagonal(k31, 0.0)
    k22 = rng.normal(size=(width, width))
    k22 = 0.5 * (k22 + k22.T)
    np.fill_diagonal(k22, 0.0)
    return k4, k31, k22


def as_s3(src) -> S.S3:
    return S.S3(np.asarray(src.aaaa), np.asarray(src.aaab), np.asarray(src.aabb))


R = {"stages": {}}
t0 = time.time()


# =========================================================================
# B. Reproduce the four recorded f64 numbers from the FROZEN module
# =========================================================================
def frozen_record_numbers():
    d1 = 0.0
    for w in (3, 4, 5):
        mean, cov, _, _ = cell(w, 205100 + w)
        mean[0] = 0.0
        st = F.build_rank_one_b1_state(mean, cov)
        direct = F.canonical_delta_tilde_distinct(st)
        exp = F.rank_one_control_table(st.factor)
        for i in range(w):
            for j in range(w):
                for k in range(w):
                    if len({i, j, k}) == 3:
                        d1 = max(d1, abs(float(direct[i, j, k]) - float(exp[i, j, k])))
    d2 = 0.0
    for w in (3, 4, 5):
        mean, cov, wt, _ = cell(w, 205200 + w)
        st = F.build_rank_one_b1_state(mean, cov)
        ctrl = F.rank_one_control_table(st.factor)
        d2 = max(
            d2,
            F.source_max_abs_difference(
                F.compile_lifted_rank_one_control(wt, st.factor),
                F.brute_complete_source(wt, ctrl),
            ),
        )
    d3 = 0.0
    d4 = 0.0
    for w in (3, 4, 5):
        mean, cov, wt, rng = cell(w, 205300 + w)
        st = F.build_rank_one_b1_state(mean, cov)
        k4, k31, k22 = owners(w, rng)
        dist = distinct_211(w, rng)
        po = F.PhysicalFourthOwners(k4=k4, k31=k31, k22=k22)
        target = F.complete_physical_owner_table(dist, po)
        ctrl = F.rank_one_control_table(st.factor)
        resid = F.complete_residual_table(target, ctrl)
        phys_only = F.complete_physical_owner_table(np.zeros_like(dist), po)
        direct_phys = S.independent_physical_collision_source(wt, k4, k31, 0.5 * (k22 + k22.T), F64)
        d3 = max(
            d3,
            F.source_max_abs_difference(F.brute_complete_source(wt, phys_only), direct_phys),
        )
        direct = F.brute_complete_source(wt, target)
        recon = F.source_add(
            F.compile_lifted_rank_one_control(wt, st.factor),
            F.brute_complete_source(wt, resid),
        )
        d4 = max(d4, F.source_max_abs_difference(direct, recon))
    return d1, d2, d3, d4


d1, d2, d3, d4 = frozen_record_numbers()
rec = {
    "distinct_delta_tilde_max_abs": d1,
    "compiled_aaaa_aaab_aabb_max_abs": d2,
    "physical_owner_source_max_abs": d3,
    "complete_owner_source_reconstruction_max_abs": d4,
}
recorded = {
    "distinct_delta_tilde_max_abs": 2.6645352591003757e-15,
    "compiled_aaaa_aaab_aabb_max_abs": 6.821210263296962e-13,
    "physical_owner_source_max_abs": 5.684341886080802e-14,
    "complete_owner_source_reconstruction_max_abs": 5.258016244624741e-13,
}
R["stages"]["B_frozen_record_reproduction"] = {
    "recomputed": rec,
    "recorded_M205_RESULTS_20260809": recorded,
    "bitwise_identical": {k: rec[k] == recorded[k] for k in recorded},
    "all_bitwise_identical": all(rec[k] == recorded[k] for k in recorded),
}
print("[B] frozen record reproduced:", R["stages"]["B_frozen_record_reproduction"]["all_bitwise_identical"], flush=True)


# =========================================================================
# A. Transcription fidelity: shadow(float64) vs frozen module
# =========================================================================
fid = []
for w in (3, 4, 5):
    mean, cov, wt, _ = cell(w, 205200 + w)
    stF = F.build_rank_one_b1_state(mean, cov)
    om, cm, cv, u, res = S.build_state(mean, cov, F64)
    fid.append(
        {
            "width": w,
            "factor_max_abs_diff": float(np.max(np.abs(u - stF.factor))),
            "compiler_max_abs_diff": F.source_max_abs_difference(
                F.compile_lifted_rank_one_control(wt, stF.factor),
                S.compile_lifted_rank_one_control(wt, u, F64),
            ),
            "control_table_max_abs_diff": float(
                np.max(np.abs(S.rank_one_control_table(u, F64) - F.rank_one_control_table(stF.factor)))
            ),
            "brute_max_abs_diff": F.source_max_abs_difference(
                F.brute_complete_source(wt, F.rank_one_control_table(stF.factor)),
                S.brute_complete_source(wt, S.rank_one_control_table(u, F64), F64),
            ),
        }
    )
fid_worst = max(
    max(r["factor_max_abs_diff"], r["compiler_max_abs_diff"], r["control_table_max_abs_diff"], r["brute_max_abs_diff"])
    for r in fid
)
R["stages"]["A_transcription_fidelity"] = {
    "rows": fid,
    "worst_abs_diff": fid_worst,
    "gate_le_1e_12": fid_worst <= 1e-12,
}
print("[A] transcription fidelity worst abs diff:", fid_worst, flush=True)


# =========================================================================
# C. Exact-rational ground truth at width 3 (is f64 itself trustworthy?)
# =========================================================================
def exact_compiler(wt, u):
    n, m = wt.shape
    W = [[Fraction(float(wt[i][a])) for a in range(m)] for i in range(n)]
    U = [Fraction(float(x)) for x in u]
    UU = [x * x for x in U]
    p = [sum(U[i] * W[i][a] for i in range(n)) for a in range(m)]
    rho = [sum(UU[i] * W[i][a] * W[i][a] for i in range(n)) for a in range(m)]
    b = [[sum(W[i][a] * UU[i] * W[i][bb] for i in range(n)) for bb in range(m)] for a in range(m)]
    aaab = [[Fraction(-6) * (p[a] * p[a] * b[a][bb] + rho[a] * p[a] * p[bb]) for bb in range(m)] for a in range(m)]
    aabb = [
        [
            Fraction(-2)
            * (rho[a] * p[bb] * p[bb] + p[a] * p[a] * rho[bb] + Fraction(4) * p[a] * b[a][bb] * p[bb])
            for bb in range(m)
        ]
        for a in range(m)
    ]
    return aaab, aabb


w = 3
mean, cov, wt, _ = cell(w, 205200 + w)
stF = F.build_rank_one_b1_state(mean, cov)
ex_aaab, ex_aabb = exact_compiler(wt, stF.factor)
c64 = F.compile_lifted_rank_one_control(wt, stF.factor)
c32 = S.compile_lifted_rank_one_control(wt, stF.factor, F32)


def rel_vs_exact(arr, ex):
    m = len(ex)
    num = max(abs(Fraction(float(arr[a][bb])) - ex[a][bb]) for a in range(m) for bb in range(m))
    den = max(abs(ex[a][bb]) for a in range(m) for bb in range(m))
    return float(num / den)


R["stages"]["C_exact_rational_width3"] = {
    "f64_rel_vs_exact_aaab": rel_vs_exact(c64.aaab, ex_aaab),
    "f64_rel_vs_exact_aabb": rel_vs_exact(c64.aabb, ex_aabb),
    "f32_rel_vs_exact_aaab": rel_vs_exact(c32.aaab, ex_aaab),
    "f32_rel_vs_exact_aabb": rel_vs_exact(c32.aabb, ex_aabb),
}
print("[C] exact-rational:", R["stages"]["C_exact_rational_width3"], flush=True)


# =========================================================================
# D. The four identities under float32
# =========================================================================
def identity_battery(w):
    out = {"width": w}

    # ---- I1 distinct delta-tilde ----
    mean, cov, _, _ = cell(w, 205100 + w)
    mean[0] = 0.0
    stF = F.build_rank_one_b1_state(mean, cov)
    ref = F.canonical_delta_tilde_distinct(stF)
    exp64 = F.rank_one_control_table(stF.factor)
    om, cm, cv, u32, _ = S.build_state(mean, cov, F32)
    got, raw_scale = S.canonical_delta_tilde_distinct(om, cm, cv, F32)
    exp32 = S.rank_one_control_table(u32, F32)
    mask = np.zeros((w, w, w), dtype=bool)
    for i in range(w):
        for j in range(w):
            for k in range(w):
                if len({i, j, k}) == 3:
                    mask[i, j, k] = True
    den = float(np.max(np.abs(exp64[mask]))) if mask.any() else 0.0
    n_f32 = float(np.max(np.abs(np.asarray(got, dtype=F64)[mask] - exp64[mask])))
    n_f64 = float(np.max(np.abs(ref[mask] - exp64[mask])))
    out["I1_distinct_delta_tilde"] = {
        "f64_max_abs": n_f64,
        "f64_rel": n_f64 / den,
        "f32_max_abs": n_f32,
        "f32_rel": n_f32 / den,
        "answer_scale": den,
        "raw_term_scale": raw_scale,
        "kappa_cancellation": raw_scale / den if den else float("inf"),
    }

    # ---- I2 compiled vs brute ----
    mean, cov, wt, _ = cell(w, 205200 + w)
    stF = F.build_rank_one_b1_state(mean, cov)
    b64 = F.brute_complete_source(wt, F.rank_one_control_table(stF.factor))
    om, cm, cv, u32, _ = S.build_state(mean, cov, F32)
    c32 = S.compile_lifted_rank_one_control(wt, u32, F32)
    b32 = S.brute_complete_source(wt, S.rank_one_control_table(u32, F32), F32)
    out["I2_compiled_vs_brute"] = {
        "f64_max_abs": F.source_max_abs_difference(
            F.compile_lifted_rank_one_control(wt, stF.factor), b64
        ),
        "f32_vs_f32brute": S.slot_rel(c32, b32),
        "f32compiler_vs_f64brute": S.slot_rel(c32, as_s3(b64)),
    }

    # ---- I3 / I4 ----
    mean, cov, wt, rng = cell(w, 205300 + w)
    stF = F.build_rank_one_b1_state(mean, cov)
    k4, k31, k22 = owners(w, rng)
    dist = distinct_211(w, rng)
    po = F.PhysicalFourthOwners(k4=k4, k31=k31, k22=k22)
    target64 = F.complete_physical_owner_table(dist, po)
    ctrl64 = F.rank_one_control_table(stF.factor)
    resid64 = F.complete_residual_table(target64, ctrl64)
    phys64 = F.complete_physical_owner_table(np.zeros_like(dist), po)
    k22s = 0.5 * (k22 + k22.T)

    ref_I3 = S.independent_physical_collision_source(wt, k4, k31, k22s, F64)
    brute_phys64 = F.brute_complete_source(wt, phys64)
    om, cm, cv, u32, _ = S.build_state(mean, cov, F32)
    phys32 = S.complete_physical_owner_table(
        np.zeros_like(dist).astype(F32), k4.astype(F32), k31.astype(F32), k22.astype(F32), F32
    )
    brute_phys32 = S.brute_complete_source(wt, phys32, F32)
    direct_phys32 = S.independent_physical_collision_source(
        wt, k4.astype(F32), k31.astype(F32), k22s.astype(F32), F32
    )
    out["I3_physical_owner_mapping"] = {
        "f64_max_abs": F.source_max_abs_difference(brute_phys64, ref_I3),
        "f64_rel": S.slot_rel(as_s3(brute_phys64), ref_I3)["rel"],
        "f32_rel": S.slot_rel(brute_phys32, direct_phys32)["rel"],
        "f32_slots": S.slot_rel(brute_phys32, direct_phys32),
    }

    target32 = S.complete_physical_owner_table(
        dist.astype(F32), k4.astype(F32), k31.astype(F32), k22.astype(F32), F32
    )
    ctrl32 = S.rank_one_control_table(u32, F32)
    resid32 = target32 - ctrl32
    src_T32 = S.brute_complete_source(wt, target32, F32)
    src_c32 = S.compile_lifted_rank_one_control(wt, u32, F32)
    src_r32 = S.brute_complete_source(wt, resid32, F32)
    recon32 = S.source_add(src_c32, src_r32)
    src_T64 = F.brute_complete_source(wt, target64)
    recon64 = F.source_add(
        F.compile_lifted_rank_one_control(wt, stF.factor), F.brute_complete_source(wt, resid64)
    )
    kappa = max(S.scale_max(src_c32), S.scale_max(src_r32)) / S.scale_max(src_T32)
    out["I4_complete_reconstruction"] = {
        "f64_max_abs": F.source_max_abs_difference(src_T64, recon64),
        "f64_rel": S.slot_rel(as_s3(recon64), as_s3(src_T64))["rel"],
        "f32_rel": S.slot_rel(recon32, src_T32)["rel"],
        "f32_slots": S.slot_rel(recon32, src_T32),
        "kappa_cancellation": kappa,
    }
    return out


rows = []
for w in (3, 4, 5, 8, 12):
    ts = time.time()
    rows.append(identity_battery(w))
    print(f"[D] width {w} done in {time.time()-ts:.1f}s", flush=True)
R["stages"]["D_identities"] = rows


# =========================================================================
# E. I1 cancellation scaling with n (the analytic risk channel)
# =========================================================================
scal = []
for w in (3, 4, 5, 8, 12, 16, 24, 32, 48):
    mean, cov, _, _ = cell(w, 205100 + w)
    mean[0] = 0.0
    stF = F.build_rank_one_b1_state(mean, cov)
    exp64 = F.rank_one_control_table(stF.factor)
    ref = F.canonical_delta_tilde_distinct(stF)
    om, cm, cv, u32, _ = S.build_state(mean, cov, F32)
    got, raw_scale = S.canonical_delta_tilde_distinct(om, cm, cv, F32)
    mask = np.zeros((w, w, w), dtype=bool)
    for i in range(w):
        for j in range(w):
            for k in range(w):
                if len({i, j, k}) == 3:
                    mask[i, j, k] = True
    den = float(np.max(np.abs(exp64[mask])))
    scal.append(
        {
            "width": w,
            "f64_rel": float(np.max(np.abs(ref[mask] - exp64[mask]))) / den,
            "f32_rel": float(np.max(np.abs(np.asarray(got, dtype=F64)[mask] - exp64[mask]))) / den,
            "kappa": raw_scale / den,
        }
    )
    print(f"[E] width {w}: {scal[-1]}", flush=True)
R["stages"]["E_I1_scaling"] = scal

R["wall_seconds"] = time.time() - t0
(HERE / "step1_identities.json").write_text(json.dumps(R, indent=2) + "\n", encoding="utf-8")
print("WROTE step1_identities.json  wall=%.1fs" % R["wall_seconds"])
