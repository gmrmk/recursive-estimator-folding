"""P2b: weights-only rotation-quality proxies vs the archived P2 MSEs.

Predeclared (P2 ledger record): can a ZERO-FORWARD-COST proxy rank rotations?
Candidates (all pure linear algebra on (rotation, weights)):
  A) w-aligned deg-4 quadrature error: |mean_s p4_a(u_s)| summed over the
     top-8 right SVs a of W_1 (M191 machinery, rotated design).
  B) same at degree 6.
  C) frame-W1 alignment energy: sum over frames of ||F_r W_1||_F^4 spread
     (dispersion of per-frame first-layer energy).
Gate (predeclared): pooled within-net-ranked spearman |rho| >= 0.4 for ANY
candidate -> P2 reopens with a free selection stage; else P2b KILLED and the
61.6% oracle headroom is recorded as unharvestable with known proxies.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "n8a_rqmc_kerdock"))
from run_n8a_gates import load_kerdock_directions, haar_rotation, WIDTH, MEAN_CHI_256  # noqa: E402

N = WIDTH
RES = json.loads((HERE / "p2_results.json").read_text())


def he_weights_first(seed):
    rng = np.random.default_rng(seed)
    g = np.float32(np.sqrt(2.0 / N))
    return (rng.standard_normal((N, N)).astype(np.float32) * g)  # W_1 only


def get_mses():
    """(net_seed -> [mse per rotation 0..15]) from the archived results."""
    per_net = RES["q1_oracle_headroom"]["per_net"]
    return {int(k): np.asarray(v["mse_per_rotation"], dtype=float)
            for k, v in per_net.items()}


def rot_seed(net_seed, r):
    """The P2 archive's rotation seed formula: 900000 + net*1000 + r."""
    return 900000 + net_seed * 1000 + r


def spearman(x, y):
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    return float(np.corrcoef(rx, ry)[0, 1])


def main():
    base = load_kerdock_directions() / MEAN_CHI_256  # unit, 32256 x 256
    mses = get_mses()
    assert mses, "no per-rotation MSEs found in archives"
    ranked_pool_x = {c: [] for c in "ABC"}
    ranked_pool_y = []
    per_net = {}
    for seed, mse in mses.items():
        W1 = he_weights_first(seed).astype(np.float64)
        # top-8 right singular vectors (input space)
        U, S, Vt = np.linalg.svd(W1, full_matrices=False)
        A_dirs = U[:, :8].T  # rows are input-space directions (W1 is in->out as (in,out)? use both conventions' safer: U columns of (in,out) SVD = input space)
        pA, pB, pC = [], [], []
        for r in range(len(mse)):
            R = haar_rotation(rot_seed(seed, r)).astype(np.float64)
            Ur = base @ R                      # rotated unit directions
            Uall = np.concatenate([Ur, -Ur])   # antipodal
            t = Uall @ A_dirs.T                # (M, 8) projections
            q4 = np.abs((t ** 4 - 3.0 / (N * (N + 2))).mean(axis=0)).sum()
            q6 = np.abs((t ** 6 - 15.0 / (N * (N + 2) * (N + 4))).mean(axis=0)).sum()
            # C: per-frame first-layer energy dispersion
            fr = (Ur @ W1)                     # (32256, 256) first-layer pre-acts of directions
            e = (fr ** 2).sum(axis=1).reshape(126, 256).mean(axis=1)
            qC = float(e.std() / e.mean())
            pA.append(q4); pB.append(q6); pC.append(qC)
        per_net[seed] = {c: spearman(np.array(p), mse) for c, p in zip("ABC", (pA, pB, pC))}
        for c, p in zip("ABC", (pA, pB, pC)):
            ranked_pool_x[c].extend(list(np.argsort(np.argsort(p)) / (len(p) - 1)))
        ranked_pool_y.extend(list(np.argsort(np.argsort(mse)) / (len(mse) - 1)))
    y = np.array(ranked_pool_y)
    pooled = {c: float(np.corrcoef(np.array(ranked_pool_x[c]), y)[0, 1]) for c in "ABC"}
    print("per-net spearman:", json.dumps(per_net, indent=1))
    print("pooled (within-net-ranked):", pooled)
    best = max(pooled.items(), key=lambda kv: abs(kv[1]))
    verdict = ("REOPEN P2 with free selection" if abs(best[1]) >= 0.4
               else "P2b KILLED: no weights-only proxy reaches |rho|>=0.4; the 61.6% oracle headroom is unharvestable with known proxies")
    print(f"best proxy {best[0]} rho {best[1]:+.3f} -> {verdict}")
    (HERE / "p2b_results.json").write_text(json.dumps(
        {"per_net": per_net, "pooled": pooled, "best": best, "verdict": verdict}, indent=2) + "\n")
    print("wrote p2b_results.json")


if __name__ == "__main__":
    main()
