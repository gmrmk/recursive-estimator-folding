"""M-MUB129: does completing the real-MUB set from 126 to 129 frames pay?

Gate is predeclared in PREDECLARATION.md, committed be3eb44 before this file
existed.  Truth-free by construction: a randomly rotated equal-weight design is
exactly unbiased under Haar, so MSE == Var over rotation draws.  No truth read,
no scorer read, no holdout, no challenge network.

K1  kill unless V129/V126 < 126/129 = 0.9767441860465116
K2  structural preconditions on the frozen archive
K3  no post-result change to the bar, R, net count, or seeds
"""

from __future__ import annotations

import json
import time
from fractions import Fraction
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ARCHIVE = HERE.parents[1] / "experiments" / "v31_guards" / "package_source" / "kerdock_phases.npz"

D = 256
DEPTH = 32
N_NETS = 3
N_ROT = 16
DEPLOYED_SLICE = (2, 128)          # kerdock_v3_estimator.py:51-52
COST_RATIO = Fraction(129, 126)
K1_BAR = float(Fraction(126, 129))  # 0.97674418...
MEAN_CHI_256 = 15.98438266660852747

NET_SEED_BASE = 20260812
ROT_SEED_BASE = 76543210


def sylvester_hadamard(n: int) -> np.ndarray:
    h = np.ones((1, 1), dtype=np.int8)
    while h.shape[0] < n:
        h = np.block([[h, h], [h, -h]]).astype(np.int8)
    return h


def load_phases() -> np.ndarray:
    """Return the frozen phase sign matrix, exactly as the estimator unpacks it."""
    archive = np.load(str(ARCHIVE))
    packed = archive["negative_bits"]
    negative = np.unpackbits(packed, axis=1, bitorder="little")[:, :D]
    return (1.0 - 2.0 * negative.astype(np.float64)).astype(np.int8)


def check_mutual_unbiasedness(phases: np.ndarray, H: np.ndarray) -> dict:
    """Cross-frame Gram entries are (1/256)*(H @ (phi_s*phi_t))[i^j].

    Mutual unbiasedness <=> every phi_s*phi_t is bent, i.e. |H @ psi| == 16
    everywhere.  The standard basis is unbiased against every H diag(phi) frame
    identically, so it needs no test.
    """
    n = phases.shape[0]
    Hf = H.astype(np.float64)
    bad_pairs, spectra = [], set()
    for s in range(n):
        prods = (phases[s].astype(np.int16) * phases[s + 1 :].astype(np.int16)).astype(np.float64)
        if prods.size == 0:
            continue
        w = prods @ Hf.T
        mag = np.abs(w)
        spectra.update(np.unique(mag).tolist())
        off = np.where(np.any(mag != 16.0, axis=1))[0]
        for k in off.tolist():
            bad_pairs.append((s, s + 1 + k, float(mag[k].min()), float(mag[k].max())))
    return {
        "n_frames_in_archive": int(n),
        "pairs_tested": int(n * (n - 1) // 2),
        "distinct_walsh_magnitudes": sorted(spectra)[:8],
        "non_unbiased_pairs": bad_pairs[:20],
        "all_pairwise_unbiased": len(bad_pairs) == 0,
    }


def degree4_moment_exact(m: int) -> dict:
    """Exact rational degree-4 moment identity for m antipodally doubled MUBs."""
    actual = Fraction(2) + Fraction(m - 1, 128)
    required = Fraction(3 * 512 * m, D * (D + 2))
    return {
        "m": m,
        "n_points": 512 * m,
        "sum_ip4_actual": str(actual),
        "sum_ip4_required": str(required),
        "exact_match": actual == required,
        "dgs_antipodal_4design_floor": 2 * (257 * 256 // 2),
        "clears_dgs_floor": 512 * m >= 2 * (257 * 256 // 2),
    }


def build_directions(phases: np.ndarray, H: np.ndarray) -> np.ndarray:
    """(m, 256, 256) unit directions.  Frame 0 is the standard basis.

    u[s,i,:] = (1/16) * H[i,:] * phi_{s-1}  for s >= 1, matching
    kerdock_v3_estimator.py:103-132.
    """
    n = phases.shape[0]
    out = np.empty((n + 1, D, D), dtype=np.float32)
    out[0] = np.eye(D, dtype=np.float32)
    Hf = H.astype(np.float32) / 16.0
    for s in range(n):
        out[s + 1] = Hf * phases[s].astype(np.float32)[None, :]
    return out


def he_network(seed: int) -> list[np.ndarray]:
    rng = np.random.default_rng(seed)
    sigma = np.sqrt(2.0 / D)
    return [rng.normal(0.0, sigma, size=(D, D)).astype(np.float32) for _ in range(DEPTH)]


def haar(seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    a = rng.normal(size=(D, D))
    q, r = np.linalg.qr(a)
    q *= np.sign(np.diag(r))
    return q.astype(np.float32)


def frame_means(dirs: np.ndarray, weights: list[np.ndarray]) -> np.ndarray:
    """Per-frame mean of the depth-32 post-ReLU activation, antipodally paired.

    Returns (m, 256).  The antipodal partner of u has preactivation -a at layer
    1, so both halves are carried explicitly from there on.
    """
    m = dirs.shape[0]
    x = dirs.reshape(m * D, D) * np.float32(MEAN_CHI_256)
    pre = x @ weights[0]
    act = np.concatenate([np.maximum(pre, 0.0), np.maximum(-pre, 0.0)], axis=0)
    del pre, x
    for w in weights[1:]:
        act = np.maximum(act @ w, 0.0)
    half = act.reshape(2, m, D, D)
    return half.mean(axis=(0, 2))


def main() -> None:
    t0 = time.time()
    H = sylvester_hadamard(D)
    phases = load_phases()

    struct = check_mutual_unbiasedness(phases, H)
    n_arch = struct["n_frames_in_archive"]
    moments = {m: degree4_moment_exact(m) for m in (126, 128, 129)}

    k2_fail = []
    if n_arch < 128:
        k2_fail.append(f"archive holds {n_arch} phase rows, need >= 128")
    if not struct["all_pairwise_unbiased"]:
        k2_fail.append("candidate frames are not pairwise mutually unbiased")
    if not moments[129]["exact_match"]:
        k2_fail.append("129-frame set fails the degree-4 moment identity")

    receipt = {
        "experiment": "M-MUB129",
        "predeclaration_commit": "be3eb44",
        "k1_bar_v129_over_v126": K1_BAR,
        "cost_ratio": str(COST_RATIO),
        "structural": struct,
        "degree4_moment": moments,
        "k2_failures": k2_fail,
    }

    if k2_fail:
        receipt["verdict"] = "KILLED_K2_STRUCTURAL"
        print(json.dumps(receipt, indent=2))
        (HERE / "RESULTS.json").write_text(json.dumps(receipt, indent=2))
        return

    dirs = build_directions(phases, H)
    lo, hi = DEPLOYED_SLICE
    idx126 = np.arange(lo + 1, hi + 1)        # +1 for the standard basis at row 0
    idx129 = np.arange(dirs.shape[0])
    assert idx126.size == 126 and idx129.size == 129, (idx126.size, idx129.size)

    per_net = []
    for k in range(N_NETS):
        w = he_network(NET_SEED_BASE + k)
        q126, q129 = [], []
        for r in range(N_ROT):
            rot = haar(ROT_SEED_BASE + 1000 * k + r)
            wr = [rot.T @ w[0]] + w[1:]
            fm = frame_means(dirs, wr)
            q126.append(fm[idx126].mean(axis=0))
            q129.append(fm[idx129].mean(axis=0))
            print(f"  net {k} rot {r:2d}  t={time.time()-t0:7.1f}s", flush=True)
        q126 = np.asarray(q126, dtype=np.float64)
        q129 = np.asarray(q129, dtype=np.float64)
        v126 = float(q126.var(axis=0, ddof=1).mean())
        v129 = float(q129.var(axis=0, ddof=1).mean())
        per_net.append({
            "net": k,
            "V126": v126,
            "V129": v129,
            "ratio": v129 / v126,
            "score_ratio": (v129 / v126) * float(COST_RATIO),
            "mean_level": float(q126.mean()),
        })
        print(f"net {k}: V126={v126:.6e} V129={v129:.6e} ratio={v129/v126:.6f}", flush=True)

    ratios = np.array([p["ratio"] for p in per_net])
    geo = float(np.exp(np.log(ratios).mean()))
    score = geo * float(COST_RATIO)
    receipt["per_net"] = per_net
    receipt["geomean_variance_ratio"] = geo
    receipt["geomean_score_ratio"] = score
    receipt["variance_removed_pct"] = (1.0 - geo) * 100.0
    receipt["k1_fires"] = bool(score >= 1.0)
    receipt["verdict"] = "KILLED_K1_COMPLETION_DOES_NOT_PAY" if score >= 1.0 else "SURVIVES_K1"
    receipt["wall_seconds"] = time.time() - t0

    (HERE / "RESULTS.json").write_text(json.dumps(receipt, indent=2))
    print(json.dumps({k: v for k, v in receipt.items() if k != "structural"}, indent=2))


if __name__ == "__main__":
    main()
