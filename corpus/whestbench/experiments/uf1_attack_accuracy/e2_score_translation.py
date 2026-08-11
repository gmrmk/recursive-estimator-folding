"""E2 -- the question the U-F1 run did not ask: what does a depth-d
Strassen-Winograd drift do to the SCORED quantity?

The scorer (whestbench/scoring.py:851) is
    final_layer_mse = mean((final_pred - final_target) ** 2)
over the 256 final-layer neurons, and score = final_layer_mse * max(0.1, C/B).
The champion's prediction for that row is a COLUMN MEAN over 64,512 sampled
rows (base_estimator/fold3_estimator `_weighted_mean` -> `fnp.mean(x, axis=0)`
with radial_conditioning=True so final_weights is None).

So the score-relevant error injected by Strassen is NOT the per-sample
Frobenius drift the U-F1 parity gate measures.  It is
    delta = colmean(x_strassen) - colmean(x_reference)
and its MSE contribution is mean(delta**2).

Geometry is the champion's, not a toy: 126 Kerdock frames x 256 = 32,256
antipodally doubled to 64,512 rows, width 256, depth 32.  Layers 1..28 are the
`_sample_matmul` products that RowBlockedBatchedWinograd owns (fold3
`for layer in range(1, mlp.depth - 3)`); the three terminal layers use direct
products in the frozen source, so they are run direct-float32 here.  An
all-31-Strassen variant is run as a conservative upper bound.

Arms: float64-classical reference; float32 classical (d=0); float32
Strassen-Winograd depth 1..5.  d=1 is the CHAMPION'S CURRENT STATE
(row_blocked_winograd.py is "Exact one-level Winograd"), so the honest marginal
comparison for U-F1 is d=4 against d=1, which is also reported.

Read-only outside this directory.  Synthetic nets; the only external read is
the committed kerdock_phases.npz asset (read-only).
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from e1_chain_distribution import sw_np  # noqa: E402  (verbatim uf1_attack schedule)

PHASES_NPZ = Path(
    "C:/Users/strid/Documents/Codex/2026-08-02/https-chatgpt-com-share-6a5556ed-2e1c"
    "/publish/recursive-estimator-folding/corpus/whestbench/experiments/v31_guards"
    "/package_source/kerdock_phases.npz"
)

WIDTH = 256
DEPTH = 32
N_BASE = 126 * 256           # 32256
STRASSEN_LAYERS = DEPTH - 4  # fold3 runs _sample_matmul for layer in 1..depth-4
MEAN_CHI_256 = 15.98438266660852747
import os
DEPTHS = tuple(int(v) for v in os.environ.get("E2_DEPTHS", "0,1,2,3,4,5").split(","))


def kerdock_directions() -> np.ndarray:
    """z rows = (mean_chi/16) * H_256 @ diag(phase_s), frames s = 2..127."""
    arch = np.load(str(PHASES_NPZ))
    packed = arch["negative_bits"]
    negative = np.unpackbits(packed, axis=1, bitorder="little")[:, :WIDTH]
    phases = (1.0 - 2.0 * negative.astype(np.float32))[2:128]
    assert phases.shape == (126, WIDTH), phases.shape
    # unnormalized Hadamard H_256 by the same radix-2 butterfly the frozen
    # source uses, then the mean_chi/16 scale.
    H = np.eye(WIDTH, dtype=np.float32)
    half = 1
    while half < WIDTH:
        b = H.reshape(-1, 2, half, WIDTH)
        left, right = b[:, 0], b[:, 1]
        H = np.stack((left + right, left - right), axis=1).reshape(WIDTH, WIDTH)
        half *= 2
    z = (H[None, :, :] * phases[:, None, :]) * np.float32(MEAN_CHI_256 / 16.0)
    return z.reshape(N_BASE, WIDTH).astype(np.float32)


def haar_rotation(seed: int, width: int = WIDTH) -> np.ndarray:
    rng = np.random.default_rng(seed)
    raw = rng.standard_normal((width, width)).astype(np.float32)
    q, r = np.linalg.qr(raw)
    signs = np.where(np.diag(r) < 0.0, -1.0, 1.0).astype(np.float32)
    return (q * signs[None, :]).astype(np.float32)


def sample_mlp_weights(seed: int) -> list[np.ndarray]:
    """He init N(0, 2/width), matching whestbench.generation.sample_mlp."""
    rng = np.random.default_rng(seed)
    scale = float(np.sqrt(2.0 / WIDTH))
    return [np.asarray(rng.standard_normal((WIDTH, WIDTH)) * scale,
                       dtype="float32") for _ in range(DEPTH)]


def run_chain(z, Ws, depth_d, *, dtype, all_strassen=False):
    """Champion sampled path: exact first product, antipodal double, deep chain."""
    z = z.astype(dtype)
    W = [w.astype(dtype) for w in Ws]
    first_pre = z @ W[0]
    x = np.concatenate((np.maximum(first_pre, 0), np.maximum(-first_pre, 0)),
                       axis=0)
    del first_pre
    n_strassen = DEPTH - 1 if all_strassen else STRASSEN_LAYERS
    for layer in range(1, DEPTH):
        d = depth_d if layer <= n_strassen else 0
        x = np.maximum(sw_np(x, W[layer], d), dtype(0.0))
    return x


def metrics(x, xref) -> dict:
    xd = x.astype(np.float64)
    cm = xd.mean(axis=0)
    cmr = xref.mean(axis=0)
    delta = cm - cmr
    rel_elem = float(np.linalg.norm(xd - xref) / np.linalg.norm(xref))
    return {
        "rel_frobenius_per_sample": rel_elem,
        "rel_colmean": float(np.linalg.norm(delta) / np.linalg.norm(cmr)),
        "coherence": float(np.linalg.norm(delta) / np.linalg.norm(cmr) / rel_elem)
        if rel_elem else 0.0,
        "mse_contribution": float(np.mean(delta ** 2)),
        "rms_delta": float(np.sqrt(np.mean(delta ** 2))),
        "max_abs_delta": float(np.abs(delta).max()),
        "colmean_ref_rms": float(np.sqrt(np.mean(cmr ** 2))),
        "delta_signed_mean": float(delta.mean()),
    }


def run_net(net_seed: int, rot_seed: int | None, *, all_strassen=False) -> dict:
    z = kerdock_directions()
    Ws = sample_mlp_weights(net_seed)
    if rot_seed is not None:
        rot = haar_rotation(rot_seed)
        Ws = [np.asarray(rot.T @ Ws[0], dtype="float32"), *Ws[1:]]
    t0 = time.time()
    xref = run_chain(z, Ws, 0, dtype=np.float64, all_strassen=all_strassen)
    print(f"  ref f64 done {time.time()-t0:.0f}s", flush=True)
    out = {"colmean_ref": xref.mean(axis=0).tolist()}
    for d in DEPTHS:
        t = time.time()
        x = run_chain(z, Ws, d, dtype=np.float32, all_strassen=all_strassen)
        m = metrics(x, xref)
        m["seconds"] = round(time.time() - t, 1)
        m["colmean"] = x.astype(np.float64).mean(axis=0).tolist()
        out[f"d{d}"] = m
        print(f"  d={d} rel_frob={m['rel_frobenius_per_sample']:.4e} "
              f"rel_colmean={m['rel_colmean']:.4e} coh={m['coherence']:.5f} "
              f"mse_contrib={m['mse_contribution']:.4e} [{m['seconds']}s]",
              flush=True)
        del x
    return out


def main() -> None:
    mode = sys.argv[1]
    if mode == "net":
        net_seed = int(sys.argv[2])
        allS = len(sys.argv) > 3 and sys.argv[3] == "all_strassen"
        tag = f"net{net_seed}" + ("_allS" if allS else "")
        print(f"=== {tag} ===", flush=True)
        res = run_net(net_seed, None, all_strassen=allS)
        (HERE / f"e2_{tag}.json").write_text(json.dumps(res), encoding="utf-8")
        print(f"wrote e2_{tag}.json", flush=True)
    elif mode == "rot":
        net_seed = int(sys.argv[2])
        rot_seed = int(sys.argv[3])
        print(f"=== net{net_seed} rot{rot_seed} ===", flush=True)
        res = run_net(net_seed, rot_seed)
        (HERE / f"e2_rot_net{net_seed}_r{rot_seed}.json").write_text(
            json.dumps(res), encoding="utf-8")
        print("wrote", f"e2_rot_net{net_seed}_r{rot_seed}.json", flush=True)
    else:
        raise SystemExit("usage: e2_score_translation.py net <seed> [all_strassen]"
                         " | rot <net_seed> <rot_seed>")


if __name__ == "__main__":
    main()
