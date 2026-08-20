"""Step-3: attack the conclusion.

Two things the step-1/step-2 numbers do not settle:
 (a) I4, the cancellation-sensitive reconstruction identity, only ran to width 12.
 (b) I3d, the quartic collision-cell source, degrades with n in the naive
     sequential accumulator.  Is that float32, or is it a 65k-term sequential
     Python accumulation that would degrade in any dtype?

Attack (b) by running the SAME sum with a pairwise-summed (numpy-reduced)
accumulator in the same dtype.  If the pairwise f32 error is flat in n, the
degradation is the accumulator, not the dtype.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
import time

import numpy as np

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(EXP / "m205_rankone_complete_physical_owner"))

import m205_rankone_complete_physical_owner as F  # noqa: E402
import f32_shadow as S  # noqa: E402

F32 = np.float32
F64 = np.float64
R = {}
T0 = time.time()


def as_s3(src):
    return S.S3(np.asarray(src.aaaa), np.asarray(src.aaab), np.asarray(src.aabb))


def cell(width, seed):
    rng = np.random.Generator(np.random.Philox(seed))
    root = rng.normal(size=(width, width))
    covariance = root @ root.T + np.eye(width)
    mean = rng.normal(scale=0.25, size=width)
    weight = rng.normal(size=(width, width + 1))
    return mean, covariance, weight, rng


def owners(width, rng):
    k4 = rng.normal(size=width)
    k31 = rng.normal(size=(width, width))
    np.fill_diagonal(k31, 0.0)
    k22 = rng.normal(size=(width, width))
    k22 = 0.5 * (k22 + k22.T)
    np.fill_diagonal(k22, 0.0)
    return k4, k31, k22


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


# =====================================================================
# (a) I4 width sweep to width 32
# =====================================================================
i4 = []
for w in (3, 4, 5, 8, 12, 16, 20, 24, 28, 32):
    t = time.time()
    mean, cov, wt, rng = cell(w, 205300 + w)
    st = F.build_rank_one_b1_state(mean, cov)
    k4, k31, k22 = owners(w, rng)
    dist = distinct_211(w, rng)
    po = F.PhysicalFourthOwners(k4=k4, k31=k31, k22=k22)
    target64 = F.complete_physical_owner_table(dist, po)
    ctrl64 = F.rank_one_control_table(st.factor)
    resid64 = F.complete_residual_table(target64, ctrl64)
    srcT64 = F.brute_complete_source(wt, target64)
    recon64 = F.source_add(
        F.compile_lifted_rank_one_control(wt, st.factor), F.brute_complete_source(wt, resid64)
    )
    _, _, _, u32, _ = S.build_state(mean, cov, F32)
    target32 = S.complete_physical_owner_table(
        dist.astype(F32), k4.astype(F32), k31.astype(F32), k22.astype(F32), F32
    )
    ctrl32 = S.rank_one_control_table(u32, F32)
    srcT32 = S.brute_complete_source(wt, target32, F32)
    srcc32 = S.compile_lifted_rank_one_control(wt, u32, F32)
    srcr32 = S.brute_complete_source(wt, target32 - ctrl32, F32)
    recon32 = S.source_add(srcc32, srcr32)
    i4.append(
        {
            "width": w,
            "f64_rel": S.slot_rel(as_s3(recon64), as_s3(srcT64))["rel"],
            "f32_rel": S.slot_rel(recon32, srcT32)["rel"],
            "kappa": max(S.scale_max(srcc32), S.scale_max(srcr32)) / S.scale_max(srcT32),
            "seconds": time.time() - t,
        }
    )
    print("[I4]", w, "f32_rel=%.3e f64_rel=%.3e kappa=%.2f (%.1fs)"
          % (i4[-1]["f32_rel"], i4[-1]["f64_rel"], i4[-1]["kappa"], i4[-1]["seconds"]), flush=True)
R["I4_width_sweep"] = i4

# =====================================================================
# (b) accumulator attack on the quartic collision cells
# =====================================================================
def collision_source_pairwise(w, k4, k31, k22, D):
    """Same [4]/[3,1]/[2,2] sum, numpy-pairwise accumulation instead of a
    sequential Python += loop.  Algebraically identical."""
    w = np.asarray(w, dtype=D)
    x3 = (w * w * w).astype(D)
    x2 = (w * w).astype(D)
    n = w.shape[0]
    # [4]
    aaab = np.einsum("i,ia,ib->ab", k4, x3, w, optimize=True).astype(D)
    aabb = np.einsum("i,ia,ib->ab", k4, x2, x2, optimize=True).astype(D)
    # [3,1] i != j (diagonal of k31 is zero, so the full sum is safe)
    aaab = aaab + D(3.0) * np.einsum("ij,ia,ja,ib->ab", k31, x2, w, w, optimize=True).astype(D)
    aaab = aaab + np.einsum("ij,ia,jb->ab", k31, x3, w, optimize=True).astype(D)
    mixed = np.einsum("ij,ia,ia,ib,jb->ab", k31, w, w, w, w, optimize=True).astype(D)
    aabb = aabb + D(2.0) * (mixed + mixed.T)
    # [2,2] i < j; k22 symmetric with zero diagonal -> full sum is 2x the i<j sum
    half = D(0.5)
    aaab = aaab + D(3.0) * half * (
        np.einsum("ij,ia,ja,ja,ib->ab", k22, w, w, w, w, optimize=True).astype(D)
        + np.einsum("ij,ia,ia,ja,jb->ab", k22, w, w, w, w, optimize=True).astype(D)
    )
    aabb = aabb + half * (
        np.einsum("ij,ia,jb->ab", k22, x2, x2, optimize=True).astype(D)
        + np.einsum("ij,ja,ib->ab", k22, x2, x2, optimize=True).astype(D)
        + D(4.0) * np.einsum("ij,ia,ja,ib,jb->ab", k22, w, w, w, w, optimize=True).astype(D)
    )
    return S.S3(np.diag(aaab).copy(), aaab, aabb)


i3d = []
for n in (16, 32, 64, 128, 256):
    t = time.time()
    rng = np.random.Generator(np.random.Philox(920000 + n))
    wt = rng.normal(size=(n, n + 1)) * np.sqrt(2.0 / n)
    k4 = rng.normal(size=n)
    k31 = rng.normal(size=(n, n))
    np.fill_diagonal(k31, 0.0)
    k22 = rng.normal(size=(n, n))
    k22 = 0.5 * (k22 + k22.T)
    np.fill_diagonal(k22, 0.0)
    ref = S.independent_physical_collision_source(wt, k4, k31, k22, F64)
    naive32 = S.independent_physical_collision_source(
        wt, k4.astype(F32), k31.astype(F32), k22.astype(F32), F32
    )
    pw64 = collision_source_pairwise(wt, k4, k31, k22, F64)
    pw32 = collision_source_pairwise(
        wt, k4.astype(F32), k31.astype(F32), k22.astype(F32), F32
    )
    row = {
        "n": n,
        "naive_f32_vs_naive_f64_rel": S.slot_rel(naive32, ref)["rel"],
        "pairwise_f64_vs_naive_f64_rel": S.slot_rel(pw64, ref)["rel"],
        "pairwise_f32_vs_pairwise_f64_rel": S.slot_rel(pw32, pw64)["rel"],
        "pairwise_f32_vs_naive_f64_rel": S.slot_rel(pw32, ref)["rel"],
        "seconds": time.time() - t,
    }
    i3d.append(row)
    print("[I3d] n=%d naive_f32=%.3e  pairwise_f32=%.3e  pairwise_f64_check=%.3e (%.1fs)"
          % (n, row["naive_f32_vs_naive_f64_rel"], row["pairwise_f32_vs_pairwise_f64_rel"],
             row["pairwise_f64_vs_naive_f64_rel"], row["seconds"]), flush=True)
R["I3d_accumulator_attack"] = i3d

R["wall_seconds"] = time.time() - T0
(HERE / "step3_attack.json").write_text(json.dumps(R, indent=2) + "\n", encoding="utf-8")
print("WROTE step3_attack.json wall=%.1fs" % R["wall_seconds"])
