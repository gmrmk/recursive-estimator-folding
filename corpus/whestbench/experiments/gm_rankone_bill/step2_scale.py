"""Step-2: n=256 He-scale float32 parity for the billed objects, plus the
width sweep of the cancellation-sensitive reconstruction identity."""

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
sys.path.insert(0, str(EXP / "m203_terminal_contraction_circuit_no_go"))

import m205_rankone_complete_physical_owner as F  # noqa: E402
import m203_terminal_contraction_circuit_no_go as M203  # noqa: E402
import f32_shadow as S  # noqa: E402

F32 = np.float32
F64 = np.float64
R = {}
T0 = time.time()


def he_cell(n, seed):
    rng = np.random.Generator(np.random.Philox(seed))
    root = rng.normal(size=(n, n)) * np.sqrt(2.0 / n)
    cov = root @ root.T + np.eye(n)
    mean = rng.normal(scale=0.25, size=n)
    weight = rng.normal(size=(n, n + 1)) * np.sqrt(2.0 / n)
    return mean, cov, weight, rng


def as_s3(src):
    return S.S3(np.asarray(src.aaaa), np.asarray(src.aaab), np.asarray(src.aabb))


# =====================================================================
# I6  n=256 He-scale compiler parity  (THE billed object: one square/layer)
# =====================================================================
i6 = []
for n in (64, 128, 256):
    t = time.time()
    mean, cov, wt, _ = he_cell(n, 900000 + n)
    st = F.build_rank_one_b1_state(mean, cov)          # frozen f64 state
    ref = F.compile_lifted_rank_one_control(wt, st.factor)   # frozen f64 compiler
    alt64 = S.compile_lifted_rank_one_control_alt(wt, st.factor, F64)
    _, _, _, u32, _ = S.build_state(mean, cov, F32)
    got = S.compile_lifted_rank_one_control(wt, u32, F32)
    got_alt = S.compile_lifted_rank_one_control_alt(wt, u32, F32)
    i6.append(
        {
            "n": n,
            "f32_vs_f64_rel": S.slot_rel(got, as_s3(ref))["rel"],
            "f32_vs_f64_slots": S.slot_rel(got, as_s3(ref)),
            "f64_alt_assoc_vs_f64_rel": S.slot_rel(alt64, as_s3(ref))["rel"],
            "f32_alt_assoc_vs_f64_rel": S.slot_rel(got_alt, as_s3(ref))["rel"],
            "u32_vs_u64_max_abs": float(np.max(np.abs(u32.astype(F64) - st.factor))),
            "seconds": time.time() - t,
        }
    )
    print("[I6]", i6[-1]["n"], "rel=%.3e alt64=%.3e" % (i6[-1]["f32_vs_f64_rel"], i6[-1]["f64_alt_assoc_vs_f64_rel"]), flush=True)
R["I6_compiler_parity_he"] = i6

# =====================================================================
# I5  M203 two-rectangle packing identity, He-scale floats
# =====================================================================
i5 = []
for n in (64, 128, 256):
    t = time.time()
    rng = np.random.Generator(np.random.Philox(910000 + n))
    x = rng.normal(size=(n, n)) * np.sqrt(2.0 / n)
    a = rng.normal(size=(n, n)) * np.sqrt(2.0 / n)
    p64 = M203.packed_terminal_contractions(x, a)
    e64 = M203.expanded_terminal_contractions(x, a)
    P64 = S.S3(*p64)
    E64 = S.S3(*e64)
    P32 = S.packed_terminal(x, a, F32)
    E32 = S.expanded_terminal(x, a, F32)
    i5.append(
        {
            "n": n,
            "f64_packed_vs_expanded_rel": S.slot_rel(P64, E64)["rel"],
            "f32_packed_vs_expanded_rel": S.slot_rel(P32, E32)["rel"],
            "f32_packed_vs_f64_packed_rel": S.slot_rel(P32, P64)["rel"],
            "f32_slots_packed_vs_expanded": S.slot_rel(P32, E32),
            "seconds": time.time() - t,
        }
    )
    print("[I5]", n, "f32 pack-vs-exp rel=%.3e  f32-vs-f64 rel=%.3e" % (i5[-1]["f32_packed_vs_expanded_rel"], i5[-1]["f32_packed_vs_f64_packed_rel"]), flush=True)
R["I5_m203_two_rectangle"] = i5

# =====================================================================
# I3d  quartic collision cells: physical [4]/[3,1]/[2,2] source, f32 vs f64
# =====================================================================
i3d = []
for n in (16, 32, 64, 128):
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
    got = S.independent_physical_collision_source(
        wt, k4.astype(F32), k31.astype(F32), k22.astype(F32), F32
    )
    i3d.append(
        {
            "n": n,
            "f32_vs_f64_rel": S.slot_rel(got, ref)["rel"],
            "slots": S.slot_rel(got, ref),
            "seconds": time.time() - t,
        }
    )
    print("[I3d]", n, "rel=%.3e (%.1fs)" % (i3d[-1]["f32_vs_f64_rel"], i3d[-1]["seconds"]), flush=True)
R["I3d_physical_collision_source_parity"] = i3d

R["wall_seconds"] = time.time() - T0
(HERE / "step2_scale.json").write_text(json.dumps(R, indent=2) + "\n", encoding="utf-8")
print("WROTE step2_scale.json wall=%.1fs" % R["wall_seconds"])
