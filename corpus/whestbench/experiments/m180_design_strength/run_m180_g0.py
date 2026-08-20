"""M180 G0 gate runner. Predeclared in M180_PREDECLARATION.md.

ONE mutation under test: the angular design itself. Variance-only premise
gate, no estimator build. On 3 synthetic He f32 256x32 nets (t3-style,
seeds 101/202/303) at matched total n = 126*256 = 32,256 base directions
(antipodally doubled downstream to 64,512), with matched exact-radius
conditioning (every direction at mean_chi(256)) and the matched
sampling-stage-isolating downstream (plain antipodal ReLU forward mean,
the N8a-sanctioned deviation), measure paired variance across 16 rotation
seeds (>= the predeclared 12) of:

  Arm A  frozen Kerdock 126-frame design, one global Haar rotation
         (the baseline; identical construction to n8a run_n8a_gates.py
         arm (a), whose loading/forward/pairing code is reused verbatim).
  Arm B  MUB mix at the same total n: 63 frozen Kerdock frames
         + the identity frame + 31 Haar-MUB pairs (Q_j, H_norm @ Q_j),
         one global Haar rotation shared with Arm A. See notes for the
         exact construction and the mub2_orthogonal_fold3 disposition.
  Arm C  coset-stratified rotations, k in {2,4,8}: the SAME Kerdock set,
         frames partitioned round-robin (frame i -> group i mod k), each
         group rotated by an independent Haar rotation (group 0 shares
         Arm A's rotation for maximal pairing). Changes the randomization
         structure, not the set.
  Arm D  randomized orthogonal re-mix: the SAME Kerdock set, each of the
         126 frames rotated by its own independent Haar rotation
         (frame 0 shares Arm A's rotation). Destroys inter-frame
         correlation structure.

All arms are unbiased for the same fixed-radius spherical mean (a Haar
rotation of any fixed direction is uniform on the sphere), so paired
variance across rotation seeds is the complete comparison.

Gates (predeclared): per arm, aggregate paired variance ratio vs Arm A
(geomean over the 3 nets). KILL the arm if reduction < 10% (ratio >
0.90). PROMOTE only the best arm and only if reduction >= 15% (ratio <=
0.85) with a paired bootstrap 95% CI excluding 10% (CI upper < 0.90).

Firewall: synthetic He nets only; the only .npz loaded is the frozen
estimator's own shipped sampling asset kerdock_phases.npz; the
mub2_orthogonal_fold3 premise5.npz is NOT loaded (premise file); no
dataset, truth, scorer, or submission access; all writes stay inside
this experiment directory; single process, plain numpy (sanctioned
N8a-style deviation: no flopscope metering in G0 -- variance only).

Checkpointing: each net writes m180_g0_partial_net<seed>.npz on
completion; reruns skip finished nets; aggregation + verdicts run once
all three partials exist. This is pure resumability, no statistical
effect: every estimate is produced by one deterministic seed schedule.
"""

from __future__ import annotations

import json
import math
import sys
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
N_FRAMES = 126
N_BASE = N_FRAMES * WIDTH   # 32,256 base directions; antipodal doubling downstream
G0_NET_SEEDS = (101, 202, 303)
G0_REPLICATES = 16          # >= predeclared 12; sized to the probe timing
MEAN_CHI_256 = 15.98438266660852747  # frozen v3 constant (estimator.py)
BOOTSTRAP_DRAWS = 4000
KILL_REDUCTION = 0.10       # reduction < 10%  -> KILL   (ratio > 0.90)
PROMOTE_REDUCTION = 0.15    # reduction >= 15% AND CI excludes 10% -> PROMOTE
C_KS = (2, 4, 8)
MUB_CONSTRUCTION_SEED = 424_242   # frozen Arm B design draw (one-time)
BOOT_SEED = 2026_08_08

ARM_NAMES = ("A_kerdock", "B_mub_mix", "C_coset_k2", "C_coset_k4",
             "C_coset_k8", "D_perframe_remix")


# ----------------------------------------------------------------- nets
def he_mlp_weights(seed: int) -> list[np.ndarray]:
    """He-init f32 width-256 depth-32 net (t3-style; verbatim from n8a)."""
    rng = np.random.default_rng(seed)
    gain = np.float32(math.sqrt(2.0 / WIDTH))
    return [
        rng.standard_normal((WIDTH, WIDTH), dtype=np.float32) * gain
        for _ in range(DEPTH)
    ]


# --------------------------------------------------- Kerdock design (arm A)
def normalized_hadamard() -> np.ndarray:
    hadamard = np.array([[1.0]], dtype=np.float32)
    while hadamard.shape[0] < WIDTH:
        hadamard = np.block([[hadamard, hadamard], [hadamard, -hadamard]])
    return (hadamard / 16.0).astype(np.float32)   # unit-norm rows


def load_kerdock_frames() -> np.ndarray:
    """Rebuild the exact v3 direction set from its shipped sampling asset.

    Verbatim n8a logic, kept in frame shape (126, 256, 256) so arms C/D
    can rotate per frame. Rows are directions at exact radius mean_chi.
    """
    packed = np.load(V3_DIR / "kerdock_phases.npz")["negative_bits"]
    negative = np.unpackbits(packed, axis=1, bitorder="little")[:, :WIDTH]
    phases = (1.0 - 2.0 * negative.astype(np.float32))[2:128]
    if phases.shape != (N_FRAMES, WIDTH):
        raise RuntimeError(f"unexpected trimmed phase shape {phases.shape}")
    h_norm = normalized_hadamard()
    frames = (
        MEAN_CHI_256 * (h_norm[None, :, :] * phases[:, None, :])
    ).astype(np.float32)
    radii = np.linalg.norm(frames, axis=2)
    if not np.allclose(radii, MEAN_CHI_256, rtol=1e-5):
        raise RuntimeError("Kerdock directions lost the fixed radius")
    return frames


def haar_rotation(seed: int) -> np.ndarray:
    """Mirror of estimator.py _haar_rotation (float32 QR, sign-fixed)."""
    rng = np.random.default_rng(seed)
    raw = rng.standard_normal((WIDTH, WIDTH), dtype=np.float32)
    rotation, triangular = np.linalg.qr(raw)
    signs = np.where(np.diag(triangular) < 0.0, -1.0, 1.0)
    return (rotation * signs[None, :]).astype(np.float32)


def haar_rotation_stack(seed: int, count: int) -> np.ndarray:
    """count independent Haar rotations from one seed (batched QR)."""
    rng = np.random.default_rng(seed)
    raw = rng.standard_normal((count, WIDTH, WIDTH), dtype=np.float32)
    rotation, triangular = np.linalg.qr(raw)
    diag = np.diagonal(triangular, axis1=1, axis2=2)
    signs = np.where(diag < 0.0, -1.0, 1.0).astype(np.float32)
    return (rotation * signs[:, None, :]).astype(np.float32)


# ------------------------------------------------------ MUB mix (arm B)
def build_mub_mix_frames(kerdock_frames: np.ndarray) -> np.ndarray:
    """Frozen Arm B design at the same total n (126 frames x 256).

    63 Kerdock frames (the first 63 of the frozen trimmed set)
    + 1 identity frame (mutually unbiased to EVERY phased-Hadamard frame:
      |<e_i, h_j>| = 1/16 = 1/sqrt(256) exactly)
    + 31 Haar-MUB pairs from the mub2_orthogonal_fold3 construction
      (per pair: Haar orthogonal Q and H_norm @ Q; rows of the pair are
      mutually unbiased because Q (H_norm Q)^T = H_norm^T, all entries
      of magnitude exactly 1/sqrt(256)).

    The pairs are drawn ONCE from a fixed seed: Arm B is a frozen design
    randomized only by the shared per-replicate global rotation, exactly
    like Arm A.
    """
    h_norm = normalized_hadamard()
    qs = haar_rotation_stack(MUB_CONSTRUCTION_SEED, 31)      # (31, 256, 256)
    partners = np.einsum("ij,fjk->fik", h_norm, qs)  # H_norm @ Q per frame
    # H_norm has unit-norm rows; H_norm @ Q is orthogonal -> unit rows.
    pair_check = np.abs(qs[0] @ partners[0].T) * 16.0
    if not np.allclose(pair_check, 1.0, atol=1e-3):
        raise RuntimeError("MUB pair property violated (|Q (HQ)^T| != 1/16)")
    identity_frame = np.eye(WIDTH, dtype=np.float32)[None, :, :]
    new_frames = np.concatenate(
        [identity_frame]
        + [np.stack((qs[j], partners[j])) for j in range(31)]
    )                                                        # (63, 256, 256)
    frames = np.concatenate(
        (kerdock_frames[:63], (MEAN_CHI_256 * new_frames).astype(np.float32))
    )
    if frames.shape != (N_FRAMES, WIDTH, WIDTH):
        raise RuntimeError(f"Arm B frame shape wrong: {frames.shape}")
    radii = np.linalg.norm(frames, axis=2)
    if not np.allclose(radii, MEAN_CHI_256, rtol=1e-4):
        raise RuntimeError("Arm B directions lost the fixed radius")
    return frames


# -------------------------------------------------- shared downstream
def antipodal_forward_mean(
    weights: list[np.ndarray], points: np.ndarray
) -> np.ndarray:
    """Identical for every arm: antipodal ReLU forward mean (n8a verbatim,
    with the rotation applied to the points instead of folded into W1 --
    algebraically the same estimate, required because arms C/D use
    heterogeneous rotations that cannot be folded into one weight)."""
    first = points @ weights[0]
    act = np.concatenate(
        (np.maximum(first, np.float32(0.0)), np.maximum(-first, np.float32(0.0))),
        axis=0,
    )
    for layer in range(1, DEPTH):
        act = np.maximum(act @ weights[layer], np.float32(0.0))
    return act.astype(np.float64).mean(axis=0)


# ---------------------------------------------------------- seed schedule
def shared_rotation_seed(net_seed: int, rep: int) -> int:
    """Arm A's rotation; shared by B, C group 0, D frame 0 (pairing)."""
    return 900_000 + net_seed * 1_000 + rep


def c_extra_seed(net_seed: int, rep: int, k: int, j: int) -> int:
    return 910_000_000 + net_seed * 1_000_000 + rep * 1_000 + k * 100 + j


def d_frames_seed(net_seed: int, rep: int) -> int:
    return 920_000_000 + net_seed * 1_000_000 + rep * 1_000


# ------------------------------------------------------------- arms
def rotate_all(frames: np.ndarray, rotation: np.ndarray) -> np.ndarray:
    """Global rotation: every direction row d -> d @ R.T (v3 semantics:
    first = (points @ R.T) @ W1 == points @ (R.T @ W1))."""
    return (frames.reshape(-1, WIDTH) @ rotation.T).astype(np.float32)


def arm_c_points(
    kerdock_frames: np.ndarray, net_seed: int, rep: int, k: int,
    shared_rot: np.ndarray,
) -> np.ndarray:
    """Round-robin frame partition (frame i -> group i mod k), one
    independent Haar rotation per group; group 0 = Arm A's rotation."""
    out = np.empty((N_FRAMES, WIDTH, WIDTH), dtype=np.float32)
    for j in range(k):
        rot = shared_rot if j == 0 else haar_rotation(
            c_extra_seed(net_seed, rep, k, j)
        )
        sel = np.arange(j, N_FRAMES, k)
        out[sel] = kerdock_frames[sel] @ rot.T
    return out.reshape(-1, WIDTH)


def arm_d_points(
    kerdock_frames: np.ndarray, net_seed: int, rep: int,
    shared_rot: np.ndarray,
) -> np.ndarray:
    """One independent Haar rotation per frame; frame 0 = Arm A's."""
    rots = haar_rotation_stack(d_frames_seed(net_seed, rep), N_FRAMES - 1)
    all_rots = np.concatenate((shared_rot[None], rots))
    pts = np.einsum("fij,fkj->fik", kerdock_frames, all_rots)  # frame @ R.T
    return pts.reshape(-1, WIDTH).astype(np.float32)


# ------------------------------------------------------------- per net
def run_net(
    net_seed: int, kerdock_frames: np.ndarray, mub_frames: np.ndarray
) -> dict[str, np.ndarray]:
    weights = he_mlp_weights(net_seed)
    est: dict[str, list[np.ndarray]] = {name: [] for name in ARM_NAMES}
    t0 = time.perf_counter()
    for rep in range(G0_REPLICATES):
        shared_rot = haar_rotation(shared_rotation_seed(net_seed, rep))
        est["A_kerdock"].append(
            antipodal_forward_mean(weights, rotate_all(kerdock_frames, shared_rot))
        )
        est["B_mub_mix"].append(
            antipodal_forward_mean(weights, rotate_all(mub_frames, shared_rot))
        )
        for k in C_KS:
            est[f"C_coset_k{k}"].append(
                antipodal_forward_mean(
                    weights,
                    arm_c_points(kerdock_frames, net_seed, rep, k, shared_rot),
                )
            )
        est["D_perframe_remix"].append(
            antipodal_forward_mean(
                weights, arm_d_points(kerdock_frames, net_seed, rep, shared_rot)
            )
        )
        print(
            f"  net {net_seed} rep {rep + 1}/{G0_REPLICATES} done "
            f"({time.perf_counter() - t0:.0f}s elapsed)",
            flush=True,
        )
    arrays = {name: np.stack(v) for name, v in est.items()}
    arrays["wall_s"] = np.array([time.perf_counter() - t0])
    return arrays


# ------------------------------------------------------------ aggregate
def mean_var(a: np.ndarray) -> float:
    return float(np.var(a, axis=0, ddof=1).mean())


def aggregate(partials: dict[int, dict[str, np.ndarray]]) -> dict:
    arms = [n for n in ARM_NAMES if n != "A_kerdock"]
    out: dict = {"net_rows": [], "arm_summary": {}}

    per_arm_lognets: dict[str, list[float]] = {a: [] for a in arms}
    for net_seed in G0_NET_SEEDS:
        arrs = partials[net_seed]
        var_a = mean_var(arrs["A_kerdock"])
        row = {
            "net_seed": net_seed,
            "var_A_kerdock": var_a,
            "wall_s": round(float(arrs["wall_s"][0]), 1),
        }
        for arm in arms:
            v = mean_var(arrs[arm])
            row[f"var_{arm}"] = v
            row[f"ratio_{arm}_over_A"] = v / var_a
            per_arm_lognets[arm].append(math.log(v / var_a))
        out["net_rows"].append(row)

    # Paired bootstrap over replicate indices, shared across arms per draw.
    boot_rng = np.random.default_rng(BOOT_SEED)
    boots: dict[str, list[float]] = {a: [] for a in arms}
    for _ in range(BOOTSTRAP_DRAWS):
        logs: dict[str, list[float]] = {a: [] for a in arms}
        for net_seed in G0_NET_SEEDS:
            idx = boot_rng.integers(0, G0_REPLICATES, size=G0_REPLICATES)
            arrs = partials[net_seed]
            va = np.var(arrs["A_kerdock"][idx], axis=0, ddof=1).mean()
            if va <= 0:
                continue
            for arm in arms:
                vb = np.var(arrs[arm][idx], axis=0, ddof=1).mean()
                logs[arm].append(math.log(vb / va))
        for arm in arms:
            boots[arm].append(math.exp(float(np.mean(logs[arm]))))

    promote_eligible = []
    for arm in arms:
        agg = math.exp(float(np.mean(per_arm_lognets[arm])))
        ci = (
            float(np.percentile(boots[arm], 2.5)),
            float(np.percentile(boots[arm], 97.5)),
        )
        reduction = 1.0 - agg
        killed = reduction < KILL_REDUCTION
        eligible = (reduction >= PROMOTE_REDUCTION) and (
            ci[1] < 1.0 - KILL_REDUCTION
        )
        out["arm_summary"][arm] = {
            "aggregate_ratio_geomean": agg,
            "reduction_vs_A": reduction,
            "bootstrap_ci_95_ratio": ci,
            "killed": killed,
            "promote_eligible": eligible,
        }
        if eligible:
            promote_eligible.append((agg, arm))
        print(
            f"{arm}: ratio {agg:.4f} (reduction {100 * reduction:+.1f}%), "
            f"95% CI [{ci[0]:.4f}, {ci[1]:.4f}] -> "
            f"{'KILL' if killed else ('PROMOTE-ELIGIBLE' if eligible else 'SURVIVES KILL, NOT PROMOTABLE')}",
            flush=True,
        )

    if promote_eligible:
        promote_eligible.sort()
        out["promoted_arm"] = promote_eligible[0][1]
    else:
        out["promoted_arm"] = None
    return out


# ---------------------------------------------------------------- main
def main() -> None:
    mean_chi_check = math.exp(
        0.5 * math.log(2.0)
        + math.lgamma((WIDTH + 1.0) / 2.0)
        - math.lgamma(WIDTH / 2.0)
    )
    if abs(mean_chi_check - MEAN_CHI_256) > 1e-9:
        raise RuntimeError("mean chi constant does not match the formula")

    kerdock_frames = load_kerdock_frames()
    mub_frames = build_mub_mix_frames(kerdock_frames)

    only_nets = None
    if len(sys.argv) > 1:
        only_nets = {int(x) for x in sys.argv[1].split(",")}

    partials: dict[int, dict[str, np.ndarray]] = {}
    for net_seed in G0_NET_SEEDS:
        path = HERE / f"m180_g0_partial_net{net_seed}.npz"
        if path.exists():
            partials[net_seed] = dict(np.load(path))
            print(f"net {net_seed}: loaded existing partial", flush=True)
            continue
        if only_nets is not None and net_seed not in only_nets:
            continue
        print(f"net {net_seed}: running {G0_REPLICATES} replicates x "
              f"{len(ARM_NAMES)} arms", flush=True)
        arrays = run_net(net_seed, kerdock_frames, mub_frames)
        np.savez(path, **arrays)
        partials[net_seed] = arrays
        print(f"net {net_seed}: partial written ({path.name})", flush=True)

    if set(partials) != set(G0_NET_SEEDS):
        missing = sorted(set(G0_NET_SEEDS) - set(partials))
        print(f"nets remaining: {missing} -- rerun to continue", flush=True)
        return

    g0 = aggregate(partials)
    results = {
        "date": "2026-08-08",
        "predeclaration": "M180_PREDECLARATION.md",
        "gate": "G0",
        "config": {
            "width": WIDTH, "depth": DEPTH, "n_base": N_BASE,
            "n_total_antipodal": 2 * N_BASE,
            "net_seeds": list(G0_NET_SEEDS),
            "replicates": G0_REPLICATES,
            "bootstrap_draws": BOOTSTRAP_DRAWS,
            "kill_reduction": KILL_REDUCTION,
            "promote_reduction": PROMOTE_REDUCTION,
            "mub_construction_seed": MUB_CONSTRUCTION_SEED,
        },
        "firewall": (
            "synthetic He nets only; only kerdock_phases.npz loaded "
            "(the estimator's own sampling asset); mub2 premise5.npz NOT "
            "loaded; no dataset/truth/scorer/submission; writes confined "
            "to the m180 experiment directory; plain numpy (sanctioned "
            "N8a-style deviation, no flopscope metering in G0)"
        ),
        "arm_b_construction": (
            "63 frozen Kerdock frames (first 63 of the trimmed set) + "
            "identity frame + 31 Haar-MUB pairs (Q_j, H_norm @ Q_j) drawn "
            "once from seed 424242; all 126 frames x 256 rows at exact "
            "radius mean_chi(256); randomized by the shared per-replicate "
            "global Haar rotation. mub2_orthogonal_fold3 disposition: "
            "performance-killed (premise5.json: mub2 2.42e-7 vs baseline "
            "1.59e-7 mean raw MSE), NOT correctness-killed; construction "
            "reimplemented in plain numpy, no mub2 asset loaded."
        ),
        "g0": g0,
    }
    verdicts = []
    for arm, s in g0["arm_summary"].items():
        tag = ("KILL" if s["killed"]
               else ("PROMOTE-ELIGIBLE" if s["promote_eligible"]
                     else "SURVIVES-KILL-NOT-PROMOTABLE"))
        verdicts.append(f"{arm}={tag}({s['aggregate_ratio_geomean']:.4f})")
    if g0["promoted_arm"]:
        results["verdict"] = (
            f"PROMOTE {g0['promoted_arm']} to G1 (best promote-eligible "
            f"arm); all others held to their per-arm verdicts: "
            + "; ".join(verdicts)
        )
    else:
        results["verdict"] = (
            "NO ARM PROMOTED at G0: " + "; ".join(verdicts)
        )
    out_path = HERE / "m180_g0_results.json"
    out_path.write_text(
        json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"\nVERDICT: {results['verdict']}")
    print(f"results written to {out_path}")


if __name__ == "__main__":
    main()
