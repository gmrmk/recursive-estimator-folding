"""M181 post-verdict verification: is the arm-1/arm-2 bias the Gaussian-
approximation bias of the terminal law, or an implementation artifact of the
Kerdock sampling path?

Method: draw 262,144 iid N(0, I) inputs (independent of both the truth stream
and the Kerdock design), forward through net 101, apply the SAME arm-1 and
arm-2 constructions to the iid samples' empirical moments, and compare the
resulting deviation-from-truth field against the Kerdock-run deviation field
(mean over the 16 rotation seeds).  A high cosine similarity means the bias is
a property of the LAW (non-Gaussian terminal pre-activations), not of the
sampling-path plumbing.  Read-only; prints only.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from run_m181_g0 import (  # noqa: E402
    DEPTH, WIDTH, he_mlp_weights, rect_mean, arm2_pairprop,
)

NET = 101
N_IID = 262_144
CHUNK = 65_536


def main() -> None:
    weights = he_mlp_weights(NET)
    truth = np.load(HERE / f"m181_truth_net{NET}.npz")["means"]
    part = np.load(HERE / f"m181_g0_partial_net{NET}.npz")
    dev_arm1_kerdock = part["arm1_univariate"].mean(axis=0) - truth
    dev_arm2_kerdock = part["arm2_pairprop"].mean(axis=0) - truth

    rng = np.random.default_rng(555_000_101)   # fresh stream, disjoint seeds
    g30_parts, z31_parts = [], []
    t0 = time.perf_counter()
    for _ in range(N_IID // CHUNK):
        act = rng.standard_normal((CHUNK, WIDTH)).astype(np.float32)
        for layer in range(DEPTH - 2):
            act = np.maximum(act @ weights[layer], np.float32(0.0))
        g30 = act @ weights[DEPTH - 2]
        h30 = np.maximum(g30, np.float32(0.0))
        z31_parts.append(h30 @ weights[DEPTH - 1])
        g30_parts.append(g30)
    g30 = np.concatenate(g30_parts)
    z31 = np.concatenate(z31_parts)
    print(f"iid forward: {N_IID} samples ({time.perf_counter() - t0:.0f}s)",
          flush=True)

    z = z31.astype(np.float64)
    arm1_iid = rect_mean(z.mean(axis=0), z.std(axis=0, ddof=1))
    dev_arm1_iid = arm1_iid - truth
    arm2_iid = arm2_pairprop(g30, weights[DEPTH - 1])
    dev_arm2_iid = arm2_iid - truth
    plain_iid_dev = np.maximum(z, 0.0).mean(axis=0) - truth

    def cos(a, b):
        return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))

    print(f"plain iid MC mean:  rms dev {np.sqrt((plain_iid_dev**2).mean()):.3e}"
          " (pure MC noise scale)")
    print(f"arm1 on iid moments: rms dev {np.sqrt((dev_arm1_iid**2).mean()):.3e}"
          f", cosine vs Kerdock-run arm1 deviation = "
          f"{cos(dev_arm1_iid, dev_arm1_kerdock):.4f}")
    print(f"arm2 on iid moments: rms dev {np.sqrt((dev_arm2_iid**2).mean()):.3e}"
          f", cosine vs Kerdock-run arm2 deviation = "
          f"{cos(dev_arm2_iid, dev_arm2_kerdock):.4f}")
    print(f"Kerdock arm1 rms dev {np.sqrt((dev_arm1_kerdock**2).mean()):.3e}, "
          f"arm2 rms dev {np.sqrt((dev_arm2_kerdock**2).mean()):.3e}")


if __name__ == "__main__":
    main()
