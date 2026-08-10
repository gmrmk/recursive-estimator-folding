"""Step-4: attribute the I4 (reconstruction identity) float32 error growth.

Two candidate causes, and they have opposite consequences for the revival:
  (H-cancel)  genuine catastrophic cancellation between source(c) and
              source(T-c) -- the failure mode the mined falsifier named.
  (H-accum)   the n^3-term SEQUENTIAL python accumulator inside
              brute_complete_source, which the frozen module itself labels
              "prohibited outside small-width tests" and which no billed path
              would ever use.

Discriminator: re-run the identical algebra with a blocked/pairwise
accumulator (sequential depth n instead of n^3).  If the error collapses,
H-accum; if it persists, H-cancel.
Second discriminator: operand-normalised error.  Under H-cancel the
result-normalised error is large while the operand-normalised error stays at
eps; under H-accum both grow together.
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


def brute_blocked(w, coefficient, D):
    """Algebraically identical to S.brute_complete_source; pairwise reduction."""
    w = np.asarray(w, dtype=D)
    coefficient = np.asarray(coefficient, dtype=D)
    n, m = w.shape
    outer_a, outer_b = [], []
    for i in range(n):
        mid_a, mid_b = [], []
        for j in range(n):
            acc_a = np.zeros((m, m), dtype=D)
            acc_b = np.zeros((m, m), dtype=D)
            for k in range(n):
                s = coefficient[i, j, k]
                if s:
                    f = S.half_owned_feature(w, i, j, k, D)
                    acc_a += s * f.aaab
                    acc_b += s * f.aabb
            mid_a.append(acc_a)
            mid_b.append(acc_b)
        outer_a.append(np.add.reduce(np.stack(mid_a), axis=0))
        outer_b.append(np.add.reduce(np.stack(mid_b), axis=0))
    aaab = np.add.reduce(np.stack(outer_a), axis=0)
    aabb = np.add.reduce(np.stack(outer_b), axis=0)
    return S.S3(np.diag(aaab).copy(), aaab, aabb)


def operand_rel(diff_s3, op_scale):
    v = max(
        float(np.max(np.abs(diff_s3.aaaa))),
        float(np.max(np.abs(diff_s3.aaab))),
        float(np.max(np.abs(diff_s3.aabb))),
    )
    return v / op_scale


rows = []
for w in (8, 12, 16, 20, 24, 28, 32):
    t = time.time()
    mean, cov, wt, rng = cell(w, 205300 + w)
    st = F.build_rank_one_b1_state(mean, cov)
    k4, k31, k22 = owners(w, rng)
    dist = distinct_211(w, rng)
    po = F.PhysicalFourthOwners(k4=k4, k31=k31, k22=k22)
    target64 = F.complete_physical_owner_table(dist, po)
    _, _, _, u32, _ = S.build_state(mean, cov, F32)
    target32 = S.complete_physical_owner_table(
        dist.astype(F32), k4.astype(F32), k31.astype(F32), k22.astype(F32), F32
    )
    ctrl32 = S.rank_one_control_table(u32, F32)
    resid32 = target32 - ctrl32

    # naive sequential accumulator (as in the frozen oracle)
    T_naive = S.brute_complete_source(wt, target32, F32)
    r_naive = S.brute_complete_source(wt, resid32, F32)
    c32 = S.compile_lifted_rank_one_control(wt, u32, F32)
    recon_naive = S.source_add(c32, r_naive)

    # blocked / pairwise accumulator, same algebra
    T_block = brute_blocked(wt, target32, F32)
    r_block = brute_blocked(wt, resid32, F32)
    recon_block = S.source_add(c32, r_block)

    # f64 blocked reference (is the blocked path algebraically the same?)
    T_block64 = brute_blocked(wt, target64, F64)
    T_naive64 = F.brute_complete_source(wt, target64)

    op_scale = max(S.scale_max(c32), S.scale_max(r_naive))
    res_scale = S.scale_max(T_naive)
    d_naive = S.S3(
        recon_naive.aaaa - T_naive.aaaa,
        recon_naive.aaab - T_naive.aaab,
        recon_naive.aabb - T_naive.aabb,
    )
    d_block = S.S3(
        recon_block.aaaa - T_block.aaaa,
        recon_block.aaab - T_block.aaab,
        recon_block.aabb - T_block.aabb,
    )
    row = {
        "width": w,
        "naive_f32_result_rel": S.slot_rel(recon_naive, T_naive)["rel"],
        "blocked_f32_result_rel": S.slot_rel(recon_block, T_block)["rel"],
        "naive_f32_operand_rel": operand_rel(d_naive, op_scale),
        "blocked_f32_operand_rel": operand_rel(d_block, op_scale),
        "kappa": op_scale / res_scale,
        "blocked_vs_naive_f64_rel": S.slot_rel(
            T_block64, S.S3(T_naive64.aaaa, T_naive64.aaab, T_naive64.aabb)
        )["rel"],
        "seconds": time.time() - t,
    }
    rows.append(row)
    print(
        "[I4attr] w=%d naive=%.3e blocked=%.3e kappa=%.2f  operand_naive=%.3e operand_blocked=%.3e  f64blk_check=%.3e (%.1fs)"
        % (
            w,
            row["naive_f32_result_rel"],
            row["blocked_f32_result_rel"],
            row["kappa"],
            row["naive_f32_operand_rel"],
            row["blocked_f32_operand_rel"],
            row["blocked_vs_naive_f64_rel"],
            row["seconds"],
        ),
        flush=True,
    )
    R["I4_attribution"] = rows
    (HERE / "step4_attribute.json").write_text(json.dumps(R, indent=2) + "\n", encoding="utf-8")

R["wall_seconds"] = time.time() - T0
(HERE / "step4_attribute.json").write_text(json.dumps(R, indent=2) + "\n", encoding="utf-8")
print("WROTE step4_attribute.json wall=%.1fs" % R["wall_seconds"])
