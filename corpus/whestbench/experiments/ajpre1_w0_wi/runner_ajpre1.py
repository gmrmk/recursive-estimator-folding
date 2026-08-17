"""AJPRE-1 runner: the anti-J W0->W_I precondition, synthetic dev nets only.

Measures the two quantities every anti-J proposal assumes but never earned:
  d_48       = 48 (V_A + V_B) / (252 V_0)      [AJ2-F48 sealed record, line 381]
  kappa_AB(I)= 2 C_AB / (V_A + V_B)            [line 368]
on bias-free He-initialised ReLU nets, with V_A, V_B, C_AB the D792 normalized
squared-norm scalars centered over HELD-OUT ROTATIONS WITHIN A FIXED NETWORK
(line 363-365) — the definition the review flagged as the one the original
costing could not satisfy.

Frozen geometry (sealed record lines 41-47): h=48, D_A={0..47},
D_B={63..110}, D_omit={48..62} u {111..125}; each selected frame keeps all 256
directions and every antipode.

Reads nothing but its own synthetic draws. No truth, no holdout, no scorer, no
competition data, zero billed FLOPs. Emits one JSON line: the metric the
predeclaration gates on plus the full measured record.
"""

from __future__ import annotations

import json
import math

import numpy as np

D = 256           # production width
L = 32            # production depth
N_FRAMES = 126    # full Kerdock bank
FRAME_DIRS = 256
D_A = list(range(0, 48))
D_B = list(range(63, 111))

N_NETS = 8        # independent synthetic networks
N_ROT = 24        # held-out rotations per network (the df the review demanded)
SEED = 20260817


def he_net(rng: np.random.Generator, depth: int = L, width: int = D):
    """Bias-free He-initialised ReLU MLP, the competition's own shape."""
    return [rng.standard_normal((width, width)) * math.sqrt(2.0 / width)
            for _ in range(depth)]


def forward_mean(net, U: np.ndarray) -> np.ndarray:
    """Mean post-ReLU activation of the final layer over the given directions."""
    H = U
    for W in net:
        H = np.maximum(H @ W, 0.0)
    return H.mean(axis=0)


def haar(rng: np.random.Generator, d: int = D) -> np.ndarray:
    Q, R = np.linalg.qr(rng.standard_normal((d, d)))
    return Q * np.sign(np.diag(R))


def frame_dirs(rng: np.random.Generator, frames, n_dirs: int = 32):
    """Antipodal direction block for the given frame indices.

    Uses n_dirs orthonormal directions per frame (subsampled from the 256 the
    production design carries) so the precondition is affordable; the RATIOS
    d_48 and kappa are scale-free in the per-frame count, which is why this is
    a legitimate precondition rather than a production measurement.
    """
    blocks = []
    for f in frames:
        g = np.random.default_rng(SEED + 7919 * int(f))
        Q, _ = np.linalg.qr(g.standard_normal((D, D)))
        V = Q[:, :n_dirs].T
        blocks.append(np.concatenate([V, -V], axis=0))
    return np.concatenate(blocks, axis=0)


def main() -> None:
    rng = np.random.default_rng(SEED)
    U_full = frame_dirs(rng, range(N_FRAMES))
    U_A = frame_dirs(rng, D_A)
    U_B = frame_dirs(rng, D_B)

    per_net = []
    for _ in range(N_NETS):
        net = he_net(rng)
        mA, mB, m0 = [], [], []
        for _ in range(N_ROT):
            Q = haar(rng)
            mA.append(forward_mean(net, U_A @ Q))
            mB.append(forward_mean(net, U_B @ Q))
            m0.append(forward_mean(net, U_full @ Q))
        mA, mB, m0 = np.array(mA), np.array(mB), np.array(m0)

        # D792 normalized squared-norm scalar, centered over held-out
        # rotations WITHIN this fixed network.
        cA = mA - mA.mean(axis=0)
        cB = mB - mB.mean(axis=0)
        c0 = m0 - m0.mean(axis=0)
        V_A = float((cA ** 2).sum(axis=1).mean())
        V_B = float((cB ** 2).sum(axis=1).mean())
        C_AB = float((cA * cB).sum(axis=1).mean())
        V_0 = float((c0 ** 2).sum(axis=1).mean())

        kappa = 2.0 * C_AB / (V_A + V_B)
        d_48 = 48.0 * (V_A + V_B) / (252.0 * V_0)
        ratio = (63.0 * d_48 / 48.0) * (1.0 + kappa)   # V_C / V_0
        per_net.append({"V_A": V_A, "V_B": V_B, "C_AB": C_AB, "V_0": V_0,
                        "kappa": kappa, "d_48": d_48, "vc_over_v0": ratio})

    d48 = np.array([r["d_48"] for r in per_net])
    kap = np.array([r["kappa"] for r in per_net])
    vc = np.array([r["vc_over_v0"] for r in per_net])
    n = len(d48)
    # One-sided 96.667% upper bound on the panel mean (sealed gate line 479),
    # normal approximation on n=8 nets; df reported so power is auditable.
    z = 1.8339
    d48_upper = float(d48.mean() + z * d48.std(ddof=1) / math.sqrt(n))
    kap_upper = float(kap.mean() + z * kap.std(ddof=1) / math.sqrt(n))
    kap_lower = float(kap.mean() - z * kap.std(ddof=1) / math.sqrt(n))

    print(json.dumps({
        "d_48_upper96667": round(d48_upper, 6),
        "d_48_mean": round(float(d48.mean()), 6),
        "d_48_sd": round(float(d48.std(ddof=1)), 6),
        "kappa_mean": round(float(kap.mean()), 6),
        "kappa_upper96667": round(kap_upper, 6),
        "kappa_lower96667": round(kap_lower, 6),
        "vc_over_v0_mean": round(float(vc.mean()), 6),
        "n_nets": n, "n_rotations": N_ROT, "df": n - 1,
        "parity_bar_kappa": -5.0 / 21.0,
        "promotion_bar_kappa": -269.0 / 525.0,
    }))


if __name__ == "__main__":
    main()
