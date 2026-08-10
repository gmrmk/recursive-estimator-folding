"""S3 (archive anchor) + S2-extended for gm_p2b_proxy -- PREDECLARATION.md 5.

S3: prove the seed formula and the archive index mapping this harness relies on
by rebuilding P2's own forward for net 101 / r = 0 from he_weights(101) and
haar_rotation(900000+101*1000+0) and requiring BITWISE equality with
p2_partial_net101.npz["frame_means"][0].  This is P2's own cross-check,
re-derived here independently of the proxy under test.  Also asserted for
net 101 / r = 15 so that the "+r" part of the formula is anchored, not only
the r = 0 base.  No truth file is read: the anchor is on the forward, and the
archived MSE vector is taken from the committed p2_results.json.

S2-extended: max relative deviation, across the 16 rotations of each net, of
the diagonal-pass alpha vector at EVERY layer 0..31 -- the direct measurement
of how much rotation information the mined proxy class can carry at all.
"""
from __future__ import annotations

import os

# DEVIATION (recorded in VERDICT.md): the first run of this script omitted these
# three lines, which run_p2_rotation_selection.py sets verbatim BEFORE importing
# numpy.  Without them the rebuilt forward matched the archive to 4.04e-07
# absolute but not bitwise; with them it is bitwise identical.  The cause is
# BLAS reduction order, not the seed formula.  Both numbers are reported.
os.environ.setdefault("OMP_NUM_THREADS", "6")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "6")
os.environ.setdefault("MKL_NUM_THREADS", "6")

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

import flopscope as flops                          # noqa: E402
from whestbench.domain import MLP                  # noqa: E402
from base_estimator import _diagonal_gaussian_pass  # noqa: E402
from estimator import Estimator as KerdockV3       # noqa: E402

flops.configure(symmetry_warnings=False)

WIDTH, DEPTH = 256, 32
N_FRAMES = 126
N_BASE = N_FRAMES * WIDTH
NET_SEEDS = (101, 202, 303)
N_ROT = 16
MEAN_CHI_256 = 15.98438266660852747
METER_BUDGET = 10 ** 15


def he_weights(seed):
    rng = np.random.default_rng(seed)
    gain = np.float32(math.sqrt(2.0 / WIDTH))
    return [rng.standard_normal((WIDTH, WIDTH), dtype=np.float32) * gain
            for _ in range(DEPTH)]


def load_kerdock_directions():
    packed = np.load(V3_DIR / "kerdock_phases.npz")["negative_bits"]
    negative = np.unpackbits(packed, axis=1, bitorder="little")[:, :WIDTH]
    phases = (1.0 - 2.0 * negative.astype(np.float32))[2:128]
    hadamard = np.array([[1.0]], dtype=np.float32)
    while hadamard.shape[0] < WIDTH:
        hadamard = np.block([[hadamard, hadamard], [hadamard, -hadamard]])
    h_norm = (hadamard / 16.0).astype(np.float32)
    directions = (MEAN_CHI_256 * (h_norm[None, :, :] * phases[:, None, :])
                  ).reshape(N_BASE, WIDTH).astype(np.float32)
    return directions


def haar_rotation(seed):
    rng = np.random.default_rng(seed)
    raw = rng.standard_normal((WIDTH, WIDTH), dtype=np.float32)
    rotation, triangular = np.linalg.qr(raw)
    signs = np.where(np.diag(triangular) < 0.0, -1.0, 1.0)
    return (rotation * signs[None, :]).astype(np.float32)


def forward_frame_means(weights, first_eff, kerdock):
    first = kerdock @ first_eff
    act = np.concatenate(
        (np.maximum(first, np.float32(0.0)), np.maximum(-first, np.float32(0.0))),
        axis=0)
    for layer in range(1, DEPTH):
        act = np.maximum(act @ weights[layer], np.float32(0.0))
    fm = act.reshape(2, N_FRAMES, WIDTH, WIDTH).mean(axis=(0, 2), dtype=np.float64)
    direct = act.mean(axis=0, dtype=np.float64)
    assert np.allclose(fm.mean(axis=0), direct, rtol=0, atol=1e-12)
    return fm


def main():
    t0 = time.perf_counter()
    out = {}

    # ---------------- S3: bitwise archive anchor ----------------------------
    kerdock = load_kerdock_directions()
    arch = np.load(PB1 / "p2_partial_net101.npz")
    fms_arch = np.asarray(arch["frame_means"], dtype=np.float64)
    arch.close()
    w101 = he_weights(101)
    anchors = {}
    for r in (0, 15):
        rot = haar_rotation(900_000 + 101 * 1_000 + r)
        fm = forward_frame_means(w101, (rot.T @ w101[0]).astype(np.float32),
                                 kerdock)
        exact = bool(np.array_equal(fm, fms_arch[r]))
        anchors[f"net101_r{r}"] = {
            "bitwise_equal_to_archive": exact,
            "max_abs_diff": float(np.abs(fm - fms_arch[r]).max()),
            "archive_row_mean": float(fms_arch[r].mean()),
            "rebuilt_row_mean": float(fm.mean()),
        }
        print(f"S3 net101 r={r}: bitwise={exact} "
              f"({time.perf_counter()-t0:.1f}s)", flush=True)
    # cross-anchor: the rebuilt r=0 forward must NOT match the archived r=15 row
    # (guards against an accidental constant/degenerate archive)
    rot0 = haar_rotation(900_000 + 101 * 1_000 + 0)
    fm0 = forward_frame_means(w101, (rot0.T @ w101[0]).astype(np.float32), kerdock)
    anchors["distinctness_r0_vs_archive_r15_max_abs_diff"] = float(
        np.abs(fm0 - fms_arch[15]).max())
    out["S3_archive_anchor"] = anchors

    # ---------------- S2-extended: per-layer alpha deviation ----------------
    per_layer = {}
    for n in NET_SEEDS:
        w = he_weights(n)
        A = np.empty((N_ROT, DEPTH, WIDTH))
        for r in range(N_ROT):
            with flops.BudgetContext(METER_BUDGET, quiet=True):
                R = KerdockV3._haar_rotation(900_000 + n * 1_000 + r, WIDTH)
                first = R.T @ w[0]
                mlp = MLP(width=WIDTH, depth=DEPTH, weights=[first, *w[1:]],
                          seed=900_000 + n * 1_000 + r, name="diag")
                _m, alphas, _f, _s = _diagonal_gaussian_pass(mlp)
            A[r] = np.stack([np.asarray(a, dtype=np.float64) for a in alphas])
        rng_layer = []
        for l in range(DEPTH):
            v = A[:, l, :]
            spread = np.abs(v.max(axis=0) - v.min(axis=0))
            scale = np.maximum(np.abs(v).mean(axis=0), 1e-30)
            rng_layer.append({"layer": l,
                              "max_abs_spread_over_rotations": float(spread.max()),
                              "max_rel_spread_over_rotations": float((spread / scale).max())})
        per_layer[str(n)] = {
            "layer0_alpha_all_zero": bool(np.all(A[:, 0, :] == 0.0)),
            "max_rel_spread_any_layer": max(x["max_rel_spread_over_rotations"]
                                            for x in rng_layer),
            "max_abs_spread_any_layer": max(x["max_abs_spread_over_rotations"]
                                            for x in rng_layer),
            "per_layer": rng_layer,
        }
        print(f"S2ext net {n}: max rel alpha spread over 16 rotations "
              f"{per_layer[str(n)]['max_rel_spread_any_layer']:.3e}", flush=True)
    out["S2_extended_alpha_spread"] = per_layer
    out["wall_s"] = round(time.perf_counter() - t0, 1)
    (HERE / "s3_anchor_results.json").write_text(
        json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print("wrote s3_anchor_results.json")


if __name__ == "__main__":
    main()
