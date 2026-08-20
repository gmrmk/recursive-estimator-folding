"""Probe: import n8a machinery, time one champion forward, cross-check MSE vs
cached m181 truth for net 101.  Read-only; no writes outside this dir."""
import sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
N8A = EXP / "n8a_rqmc_kerdock"
M181 = EXP / "m181_terminal_smoothing"
sys.path.insert(0, str(N8A))

from run_n8a_gates import (  # noqa: E402
    he_mlp_weights, load_kerdock_directions, haar_rotation,
    antipodal_forward_mean, WIDTH, DEPTH, MEAN_CHI_256, N_BASE,
)

print("WIDTH", WIDTH, "DEPTH", DEPTH, "N_BASE", N_BASE, "MEAN_CHI", MEAN_CHI_256)
kerdock = load_kerdock_directions()
print("kerdock", kerdock.shape, kerdock.dtype)

d = np.load(M181 / "m181_truth_net101.npz")
truth = np.asarray(d["means"], dtype=np.float64)
noise = float(d["noise_final"])
d.close()

net = 101
weights = he_mlp_weights(net)
r = 0
rot = haar_rotation(900_000 + net * 1_000 + r)
first_eff = (rot.T @ weights[0]).astype(np.float32)
t0 = time.perf_counter()
final = antipodal_forward_mean(weights, first_eff, kerdock)
dt = time.perf_counter() - t0
mse = float(((final - truth) ** 2).mean())
print(f"one champion forward: {dt:.2f}s  MSE_vs_m181_truth={mse:.4e} "
      f"(m181 arm0 net101 mse_raw=1.997e-07)  noise={noise:.3e}")
