"""N8a gate runner. Predeclared in N8A_PREDECLARATION.md.

G0 premise gate (cheapest falsifier, BEFORE any build): the frozen Kerdock
M71 v3 sampler at width 256 is NOT iid -- it is a deterministic structured
spherical set (126 phased-Hadamard frames from kerdock_phases.npz, exact
radius mean_chi(256), antipodal doubling, per-net Haar rotation).  So the
predeclaration's structured branch applies: measure, on 3 synthetic He nets
at the native sample count (n_base = 126*256 = 32,256, antipodally doubled),
the paired variance of

  (a) the existing Kerdock phased-WHT construction, randomized by its own
      randomization device (the Haar rotation; the frozen estimator seeds it
      per-net, so across nets it is a random rotation), vs
  (b) the N7 antithetic Kronecker-lattice + Cranley-Patterson shift +
      Acklam inverse-CDF construction, radially conditioned to the same
      fixed radius so every downstream constant stays valid, sharing the
      SAME per-replicate Haar rotation (paired) plus its CP shift,

with identical downstream processing for both arms (antipodal ReLU forward
mean -- the sampling-stage-isolating downstream; the full fold3 pipeline is
only reached by G2 if this premise survives).

KILL if the aggregate (b)/(a) variance ratio > 0.83 (predeclared: less than
1.2x gain means the lattice adds nothing over the existing structure).

Firewall: synthetic He nets only; frozen v3 sources untouched (read-only
load of the estimator's own shipped sampling asset kerdock_phases.npz,
confirmed from estimator.py to be the sampling asset); no dataset, truth,
scorer, or submission access; single process.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
V3_DIR = Path(
    r"C:\Users\strid\Documents\Codex\2026-08-02"
    r"\https-chatgpt-com-share-6a5556ed-2e1c\work\scorefloor_generation"
    r"\kerdock_l1_owned_buffer\candidate_source_validator_v3"
)

WIDTH, DEPTH = 256, 32
N_BASE = 126 * 256          # native draw count; antipodal doubling downstream
G0_NET_SEEDS = (101, 202, 303)
G0_REPLICATES = 16
KILL_RATIO = 0.83           # predeclared: > 0.83 kills
MEAN_CHI_256 = 15.98438266660852747  # frozen v3 constant (estimator.py)
BOOTSTRAP_DRAWS = 4000


# ----------------------------------------------------------------- nets
def he_mlp_weights(seed: int) -> list[np.ndarray]:
    """He-init f32 width-256 depth-32 net (mimics t3's he_mlp construction)."""
    rng = np.random.default_rng(seed)
    gain = np.float32(math.sqrt(2.0 / WIDTH))
    return [
        rng.standard_normal((WIDTH, WIDTH), dtype=np.float32) * gain
        for _ in range(DEPTH)
    ]


# ------------------------------------------------- arm (a): Kerdock v3 set
def load_kerdock_directions() -> np.ndarray:
    """Rebuild the exact v3 direction set from its shipped sampling asset.

    estimator.py: packed sign bits -> phases (trim [2:128], 126 frames);
    first product is mean_chi * H_norm @ diag(phase_s) @ W1, i.e. the
    effective directions are rows of mean_chi * H_norm * phase_s.
    """
    packed = np.load(V3_DIR / "kerdock_phases.npz")["negative_bits"]
    negative = np.unpackbits(packed, axis=1, bitorder="little")[:, :WIDTH]
    phases = (1.0 - 2.0 * negative.astype(np.float32))[2:128]
    if phases.shape != (126, WIDTH):
        raise RuntimeError(f"unexpected trimmed phase shape {phases.shape}")
    hadamard = np.array([[1.0]], dtype=np.float32)
    while hadamard.shape[0] < WIDTH:
        hadamard = np.block(
            [[hadamard, hadamard], [hadamard, -hadamard]]
        )
    h_norm = (hadamard / 16.0).astype(np.float32)
    directions = (
        MEAN_CHI_256 * (h_norm[None, :, :] * phases[:, None, :])
    ).reshape(N_BASE, WIDTH).astype(np.float32)
    radii = np.linalg.norm(directions, axis=1)
    if not np.allclose(radii, MEAN_CHI_256, rtol=1e-5):
        raise RuntimeError("Kerdock directions lost the fixed radius")
    return directions


def haar_rotation(seed: int) -> np.ndarray:
    """Mirror of estimator.py _haar_rotation (float32 QR, sign-fixed)."""
    rng = np.random.default_rng(seed)
    raw = rng.standard_normal((WIDTH, WIDTH), dtype=np.float32)
    rotation, triangular = np.linalg.qr(raw)
    signs = np.where(np.diag(triangular) < 0.0, -1.0, 1.0)
    return (rotation * signs[None, :]).astype(np.float32)


# ------------------------------------- arm (b): N7 Kronecker + CP + ndtri
_A = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
      1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
_B = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
      6.680131188771972e+01, -1.328068155288572e+01]
_C = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
      -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
_D = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
      3.754408661907416e+00]


def ndtri(p):
    """Acklam's inverse normal CDF, verbatim from run_n7.py."""
    p = np.clip(p, 1e-12, 1 - 1e-12)
    out = np.empty_like(p)
    lo = p < 0.02425
    hi = p > 1 - 0.02425
    mid = ~(lo | hi)
    q = np.sqrt(-2 * np.log(p[lo]))
    out[lo] = (((((_C[0]*q + _C[1])*q + _C[2])*q + _C[3])*q + _C[4])*q + _C[5]) / \
              ((((_D[0]*q + _D[1])*q + _D[2])*q + _D[3])*q + 1)
    q = np.sqrt(-2 * np.log(1 - p[hi]))
    out[hi] = -(((((_C[0]*q + _C[1])*q + _C[2])*q + _C[3])*q + _C[4])*q + _C[5]) / \
               ((((_D[0]*q + _D[1])*q + _D[2])*q + _D[3])*q + 1)
    q = p[mid] - 0.5
    r = q * q
    out[mid] = (((((_A[0]*r + _A[1])*r + _A[2])*r + _A[3])*r + _A[4])*r + _A[5]) * q / \
               (((((_B[0]*r + _B[1])*r + _B[2])*r + _B[3])*r + _B[4])*r + 1)
    return out


def kronecker_alpha(d: int) -> np.ndarray:
    """Verbatim from run_n7.py: alpha_j = frac(sqrt(prime_j))."""
    primes: list[int] = []
    x = 2
    while len(primes) < d:
        if all(x % p for p in primes):
            primes.append(x)
        x += 1
    return np.array([math.sqrt(p) % 1.0 for p in primes])


ALPHA = kronecker_alpha(WIDTH)


def radial_condition(z: np.ndarray) -> np.ndarray:
    """base_estimator.py radial conditioning: scale every point to the mean
    chi radius, keeping the frozen _radial_covariance constant valid."""
    radii = np.sqrt(np.sum(z * z, axis=1))
    return (z * (MEAN_CHI_256 / np.maximum(radii, 1e-12))[:, None]).astype(
        np.float32
    )


def lattice_points(shift_rng: np.random.Generator) -> np.ndarray:
    """Antithetic Kronecker lattice + CP shift + Acklam inverse CDF
    (run_n7.py rqmc_mean draw stage) at the native count, radially
    conditioned to the v3 fixed radius.  Antithesis itself is supplied by
    the shared downstream antipodal doubling (-z = ndtri(1-u))."""
    shift = shift_rng.random(WIDTH)
    i = np.arange(N_BASE)[:, None]
    u = (i * ALPHA[None, :] + shift[None, :]) % 1.0
    return radial_condition(ndtri(u).astype(np.float32))


def mc_points(rng: np.random.Generator) -> np.ndarray:
    """Diagnostic-only arm: radially conditioned iid Gaussian."""
    return radial_condition(
        rng.standard_normal((N_BASE, WIDTH)).astype(np.float32)
    )


# -------------------------------------------------- shared downstream
def antipodal_forward_mean(
    weights: list[np.ndarray], first_weight_eff: np.ndarray, points: np.ndarray
) -> np.ndarray:
    """Identical for every arm: antipodal ReLU forward mean."""
    first = points @ first_weight_eff
    act = np.concatenate(
        (np.maximum(first, np.float32(0.0)), np.maximum(-first, np.float32(0.0))),
        axis=0,
    )
    for layer in range(1, DEPTH):
        act = np.maximum(act @ weights[layer], np.float32(0.0))
    return act.astype(np.float64).mean(axis=0)


# -------------------------------------------------------------- gate G0
def run_g0() -> dict:
    mean_chi_check = math.exp(
        0.5 * math.log(2.0)
        + math.lgamma((WIDTH + 1.0) / 2.0)
        - math.lgamma(WIDTH / 2.0)
    )
    if abs(mean_chi_check - MEAN_CHI_256) > 1e-9:
        raise RuntimeError("mean chi constant does not match the formula")

    kerdock = load_kerdock_directions()
    g0 = {
        "sampler_finding": (
            "v3 width-256 sampler is a deterministic structured spherical set: "
            "126 phased-Hadamard (Kerdock) frames x 256 rows = 32,256 "
            "directions of exact radius mean_chi(256)=15.9844, antipodally "
            "doubled to 64,512, randomized only by a per-net Haar rotation. "
            "Structured branch of G0 applies."
        ),
        "n_base": N_BASE,
        "replicates": G0_REPLICATES,
        "kill_ratio": KILL_RATIO,
        "net_rows": [],
    }

    per_net_ratios = []
    all_est = {}
    for net_seed in G0_NET_SEEDS:
        weights = he_mlp_weights(net_seed)
        est = {"kerdock": [], "lattice": [], "mc_radial": []}
        t0 = time.perf_counter()
        for r in range(G0_REPLICATES):
            rotation = haar_rotation(900_000 + net_seed * 1_000 + r)
            first_eff = (rotation.T @ weights[0]).astype(np.float32)
            est["kerdock"].append(
                antipodal_forward_mean(weights, first_eff, kerdock)
            )
            z_b = lattice_points(
                np.random.default_rng(700_000 + net_seed * 1_000 + r)
            )
            est["lattice"].append(
                antipodal_forward_mean(weights, first_eff, z_b)
            )
            z_mc = mc_points(
                np.random.default_rng(500_000 + net_seed * 1_000 + r)
            )
            est["mc_radial"].append(
                antipodal_forward_mean(weights, first_eff, z_mc)
            )
        wall = time.perf_counter() - t0
        arrays = {k: np.stack(v) for k, v in est.items()}
        all_est[net_seed] = arrays
        var = {
            k: float(np.var(a, axis=0, ddof=1).mean())
            for k, a in arrays.items()
        }
        ratio = var["lattice"] / var["kerdock"]
        per_net_ratios.append(ratio)
        g0["net_rows"].append({
            "net_seed": net_seed,
            "var_kerdock": var["kerdock"],
            "var_lattice": var["lattice"],
            "var_mc_radial_diagnostic": var["mc_radial"],
            "ratio_lattice_over_kerdock": ratio,
            "diag_kerdock_over_mc": var["kerdock"] / var["mc_radial"],
            "diag_lattice_over_mc": var["lattice"] / var["mc_radial"],
            "wall_s": round(wall, 1),
        })
        print(
            f"G0 net {net_seed}: var(a)_kerdock={var['kerdock']:.4e}  "
            f"var(b)_lattice={var['lattice']:.4e}  "
            f"ratio b/a={ratio:.4f}  "
            f"[diag: a/mc={var['kerdock']/var['mc_radial']:.4f} "
            f"b/mc={var['lattice']/var['mc_radial']:.4f}]  "
            f"({wall:.0f}s)",
            flush=True,
        )

    aggregate = float(np.exp(np.mean(np.log(per_net_ratios))))

    # Paired bootstrap over replicate indices (diagnostic CI on the aggregate).
    boot_rng = np.random.default_rng(2026_08_08)
    boots = []
    for _ in range(BOOTSTRAP_DRAWS):
        logs = []
        for net_seed in G0_NET_SEEDS:
            idx = boot_rng.integers(0, G0_REPLICATES, size=G0_REPLICATES)
            a = all_est[net_seed]["kerdock"][idx]
            b = all_est[net_seed]["lattice"][idx]
            va = np.var(a, axis=0, ddof=1).mean()
            vb = np.var(b, axis=0, ddof=1).mean()
            if va > 0:
                logs.append(math.log(vb / va))
        boots.append(math.exp(np.mean(logs)))
    ci = (
        float(np.percentile(boots, 2.5)),
        float(np.percentile(boots, 97.5)),
    )

    g0["per_net_ratios"] = per_net_ratios
    g0["aggregate_ratio_geomean"] = aggregate
    g0["bootstrap_ci_95"] = ci
    g0["pass"] = aggregate <= KILL_RATIO
    print(
        f"G0 aggregate (geomean) ratio b/a = {aggregate:.4f} "
        f"(bootstrap 95% CI [{ci[0]:.4f}, {ci[1]:.4f}]); "
        f"kill threshold {KILL_RATIO}",
        flush=True,
    )
    return g0


def main() -> None:
    results = {
        "date": "2026-08-08",
        "predeclaration": "N8A_PREDECLARATION.md",
        "firewall": (
            "synthetic He nets only; frozen v3 untouched; only shipped "
            "sampling asset kerdock_phases.npz read; no dataset/truth/"
            "scorer/submission; single process"
        ),
        "gates": {},
        "verdict": None,
    }
    out_path = HERE / "n8a_results.json"

    def finish(verdict: str) -> None:
        results["verdict"] = verdict
        out_path.write_text(
            json.dumps(results, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"\nVERDICT: {verdict}")
        print(f"results written to {out_path}")

    print("G0: premise gate (structured-sampler branch)", flush=True)
    g0 = run_g0()
    results["gates"]["g0"] = g0
    if not g0["pass"]:
        finish(
            "KILL at G0: the frozen Kerdock v3 sampler is already a "
            "structured spherical construction and the antithetic "
            "Kronecker+CP lattice does not deliver the predeclared >=1.2x "
            "paired variance gain over it "
            f"(aggregate ratio {g0['aggregate_ratio_geomean']:.4f} > "
            f"{KILL_RATIO}). First broken link: the N8a premise."
        )
        return

    # G0 survived: G1 (minimal-diff variant), G2 (paired factorial), and
    # G3 (packaging) run next.  They are implemented only behind a live G0
    # survival to honor the predeclared stop-at-first-broken-link order.
    finish(
        "G0 SURVIVED -- build gates G1-G3 must now be implemented and run "
        "before any promotion claim (this runner stops here by design; "
        "see N8A_BUILD_NOTES.md)."
    )


if __name__ == "__main__":
    main()
