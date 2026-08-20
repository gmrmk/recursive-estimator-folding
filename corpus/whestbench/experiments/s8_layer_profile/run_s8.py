"""S8 runner: layer-resolved defect profile of the estimator residual field.

Ledger id: s8_tdse_layer_defect_profile.  Sudden-quench / Dyson frame.

QUESTION: decompose the final-layer residual field's variance by layer --
how much is attributable to each layer's realized-weight defects -- and
compare the profile against the mean-field prediction.

PREDECLARED MEAN-FIELD PREDICTION (derived BEFORE measurement; this module
computes and records it before any forward pass runs):
  f(c)   = (sqrt(1-c^2) + (pi - arccos c) * c) / pi   (normalized arccos map)
  chi(c) = f'(c) = (pi - arccos c) / pi
  A defect injected at layer l propagates through 31-l downstream mean-field
  layers, each multiplying its contribution by chi evaluated on the depth
  trajectory.  The He-critical ReLU trajectory sits at the fixed point c->1,
  where chi_1 = f'(1) = 1 exactly.  Predicted shape: v_l ~ chi_1^(31-l) = 1
  for all l: FLAT, p_l = 1/32.  Top-5 share 5/32, last-3 share 3/32.

  Pre-registered secondary refinement (REPORTED, not gated): a full-layer
  redraw is nonperturbative -- it sets the cross-net activation correlation
  to gamma_0 = f(0) = 1/pi, which heals via gamma_j = f(gamma_{j-1}).
  Downstream layer-k defects (shared weights, partially-healed inputs) then
  only partially decorrelate, with modeled defect-realization correlation
  ghat_j = (gamma_j - 1/pi) / (1 - 1/pi), so
    R_l = 1 + sum_{j=1}^{31-l} (1 - gamma_j) / (1 - gamma_0),
  a profile DECREASING in l (early layers largest).

MEASUREMENT (per net seed in 101/202/303):
  probes  : fixed uniform subsample (seed SUBSAMPLE_SEED, no replacement) of
            M=8192 rows from the antipodally-doubled Kerdock design (64512
            rows), rotated per net by haar_rotation(900000+net_seed*1000+0);
            identical subsample indices across all nets/arms/reps.
  baseline: ybar(u) = neuron-averaged final post-ReLU output; residual
            r(u) = ybar(u) - mean_u ybar.
  arms    : for each layer l in 0..31, rep in 0..2: rebuild the net with ONLY
            layer l redrawn from seed 10_000_000 + net_seed*10_000 + l*100 + rep
            (same He construction), forward the SAME probes, get r_l(u).
  metric  : v_l = mean_u E_reps[(r - r_l)^2]; variant 1 - corr(r, r_l).

PREDECLARED GATES (operationalization fixed here, before measurement):
  shares s_l = v_l / sum_l v_l compared to flat p_l = 1/32;
  dev_l = max(s_l/p_l, p_l/s_l).
  PASS  = max_l dev_l <= 2 on >= 2 of 3 nets.
  KILL  = (>= 2 layers with dev_l > 5 on >= 2 nets) AND no coherent
          structure, where coherent := mean pairwise Spearman rank
          correlation of the three per-net share profiles >= 0.8.
  Top-5 concentration (>= 50%?) and last-3 position are REPORTED evidence.

CROSS-CHECKS (two-signal): (1) per-arm identity v = Var(r) + Var(r_l)
  - 2 Cov(r, r_l) recomputed independently of the direct mean square
  difference; (2) bitwise repeat of one full resampled-arm forward;
  (3) mean-chi closed-form check and Kerdock radius check as in n8a.

FIREWALL: synthetic He nets only; frozen v3 sources mirrored verbatim (not
  imported, not edited); only the shipped sampling asset kerdock_phases.npz
  is read (read-only); no dataset/truth/scorer/submission access; no git;
  writes confined to s8_layer_profile/.
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
N_BASE = 126 * 256                      # 32256 base rows; doubled -> 64512
NET_SEEDS = (101, 202, 303)
M_PROBES = 8192
N_REPS = 3
SUBSAMPLE_SEED = 20260807               # fixed probe subsample seed (all arms)
MEAN_CHI_256 = 15.98438266660852747     # frozen v3 constant (estimator.py)
PASS_FACTOR = 2.0
KILL_FACTOR = 5.0
COHERENCE_SPEARMAN = 0.8


def rotation_seed(net_seed: int) -> int:
    return 900_000 + net_seed * 1_000 + 0


def resample_seed(net_seed: int, layer: int, rep: int) -> int:
    return 10_000_000 + net_seed * 10_000 + layer * 100 + rep


# ------------------------------------------------ verbatim n8a mirrors
def he_mlp_weights(seed: int) -> list[np.ndarray]:
    """He-init f32 width-256 depth-32 net (verbatim run_n8a_gates.py)."""
    rng = np.random.default_rng(seed)
    gain = np.float32(math.sqrt(2.0 / WIDTH))
    return [
        rng.standard_normal((WIDTH, WIDTH), dtype=np.float32) * gain
        for _ in range(DEPTH)
    ]


def redraw_layer(net_seed: int, layer: int, rep: int) -> np.ndarray:
    """Fresh He draw for one layer, seed formula documented above."""
    rng = np.random.default_rng(resample_seed(net_seed, layer, rep))
    gain = np.float32(math.sqrt(2.0 / WIDTH))
    return rng.standard_normal((WIDTH, WIDTH), dtype=np.float32) * gain


def load_kerdock_directions() -> np.ndarray:
    """Verbatim mirror of run_n8a_gates.py load_kerdock_directions."""
    packed = np.load(V3_DIR / "kerdock_phases.npz")["negative_bits"]
    negative = np.unpackbits(packed, axis=1, bitorder="little")[:, :WIDTH]
    phases = (1.0 - 2.0 * negative.astype(np.float32))[2:128]
    if phases.shape != (126, WIDTH):
        raise RuntimeError(f"unexpected trimmed phase shape {phases.shape}")
    hadamard = np.array([[1.0]], dtype=np.float32)
    while hadamard.shape[0] < WIDTH:
        hadamard = np.block([[hadamard, hadamard], [hadamard, -hadamard]])
    h_norm = (hadamard / 16.0).astype(np.float32)
    directions = (
        MEAN_CHI_256 * (h_norm[None, :, :] * phases[:, None, :])
    ).reshape(N_BASE, WIDTH).astype(np.float32)
    radii = np.linalg.norm(directions, axis=1)
    if not np.allclose(radii, MEAN_CHI_256, rtol=1e-5):
        raise RuntimeError("Kerdock directions lost the fixed radius")
    return directions


def haar_rotation(seed: int) -> np.ndarray:
    """Verbatim mirror of run_n8a_gates.py haar_rotation."""
    rng = np.random.default_rng(seed)
    raw = rng.standard_normal((WIDTH, WIDTH), dtype=np.float32)
    rotation, triangular = np.linalg.qr(raw)
    signs = np.where(np.diag(triangular) < 0.0, -1.0, 1.0)
    return (rotation * signs[None, :]).astype(np.float32)


# ------------------------------------------------ mean-field prediction
def f_map(c: float) -> float:
    c = min(1.0, max(-1.0, c))
    return (math.sqrt(max(0.0, 1.0 - c * c))
            + (math.pi - math.acos(c)) * c) / math.pi


def chi(c: float) -> float:
    c = min(1.0, max(-1.0, c))
    return (math.pi - math.acos(c)) / math.pi


def mean_field_prediction() -> dict:
    chi_1 = chi(1.0)                      # = 1 exactly at He criticality
    flat = [chi_1 ** (DEPTH - 1 - l) for l in range(DEPTH)]
    flat_norm = [x / sum(flat) for x in flat]

    gamma = [f_map(0.0)]                  # gamma_0 = 1/pi
    for _ in range(1, DEPTH):
        gamma.append(f_map(gamma[-1]))
    refine = []
    for l in range(DEPTH):
        s = 1.0
        for j in range(1, DEPTH - l):     # j = 1 .. 31-l
            s += (1.0 - gamma[j]) / (1.0 - gamma[0])
        refine.append(s)
    refine_norm = [x / sum(refine) for x in refine]
    return {
        "derived_before_measurement": True,
        "chi_1": chi_1,
        "flat_shape_normalized": flat_norm,
        "flat_top5_share": 5.0 / DEPTH,
        "flat_last3_share": 3.0 / DEPTH,
        "refinement_gamma": gamma,
        "refinement_shape_raw": refine,
        "refinement_shape_normalized": refine_norm,
    }


# ------------------------------------------------ forward + metrics
def forward_ybar(probes: np.ndarray, weights: list[np.ndarray]) -> np.ndarray:
    """Neuron-averaged final post-ReLU output for every probe row (f32
    matmuls throughout; probes already carry the antipodal doubling and the
    per-net rotation)."""
    act = probes
    for w in weights:
        act = np.maximum(act @ w, np.float32(0.0))
    return act.astype(np.float64).mean(axis=1)


def residual(ybar: np.ndarray) -> np.ndarray:
    return ybar - ybar.mean()


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    ra = np.argsort(np.argsort(a)).astype(np.float64)
    rb = np.argsort(np.argsort(b)).astype(np.float64)
    return float(np.corrcoef(ra, rb)[0, 1])


def main() -> None:
    t_start = time.perf_counter()
    results: dict = {
        "date": "2026-08-09",
        "task": "s8_tdse_layer_defect_profile",
        "firewall": (
            "synthetic He nets only; frozen v3 mirrored verbatim, untouched; "
            "only shipped sampling asset kerdock_phases.npz read; no dataset/"
            "truth/scorer/submission; no git; writes confined to "
            "s8_layer_profile/"
        ),
        "config": {
            "width": WIDTH, "depth": DEPTH, "net_seeds": list(NET_SEEDS),
            "m_probes": M_PROBES, "n_reps": N_REPS,
            "subsample_seed": SUBSAMPLE_SEED,
            "rotation_seed_formula": "900000 + net_seed*1000 + 0",
            "resample_seed_formula":
                "10000000 + net_seed*10000 + layer*100 + rep",
            "pass_factor": PASS_FACTOR, "kill_factor": KILL_FACTOR,
            "coherence_spearman_threshold": COHERENCE_SPEARMAN,
        },
    }

    # ---- premise checks (before measurement)
    mean_chi_check = math.exp(
        0.5 * math.log(2.0)
        + math.lgamma((WIDTH + 1.0) / 2.0)
        - math.lgamma(WIDTH / 2.0)
    )
    if abs(mean_chi_check - MEAN_CHI_256) > 1e-9:
        raise RuntimeError("mean chi constant does not match the formula")

    # ---- mean-field prediction FIRST (checkpointed to disk pre-measurement)
    mf = mean_field_prediction()
    results["mean_field"] = mf
    out_path = HERE / "s8_results.json"
    out_path.write_text(
        json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print("mean-field prediction derived and checkpointed BEFORE measurement:")
    print(f"  chi_1 = f'(1) = {mf['chi_1']:.6f}  -> flat shape, p_l = 1/32 = "
          f"{1.0 / DEPTH:.5f}")
    print(f"  flat top-5 share = {mf['flat_top5_share']:.4f}, "
          f"flat last-3 share = {mf['flat_last3_share']:.4f}")
    print("  refinement R_l (secondary, reported not gated), l=0,8,16,24,31: "
          + ", ".join(f"{mf['refinement_shape_raw'][l]:.3f}"
                      for l in (0, 8, 16, 24, 31)), flush=True)

    # ---- probe set
    kerdock = load_kerdock_directions()
    doubled = np.concatenate((kerdock, -kerdock), axis=0)      # 64512 x 256
    idx = np.sort(np.random.default_rng(SUBSAMPLE_SEED).choice(
        doubled.shape[0], size=M_PROBES, replace=False))
    sub = doubled[idx]                                          # fixed, shared
    results["config"]["n_doubled"] = int(doubled.shape[0])
    results["config"]["subsample_first5_idx"] = [int(i) for i in idx[:5]]

    # ---- measurement
    per_net: dict = {}
    identity_max_rel = 0.0
    for net_seed in NET_SEEDS:
        t0 = time.perf_counter()
        weights = he_mlp_weights(net_seed)
        rot = haar_rotation(rotation_seed(net_seed))
        probes = np.ascontiguousarray((sub @ rot.T).astype(np.float32))

        ybar0 = forward_ybar(probes, weights)
        r0 = residual(ybar0)
        var_r0 = float(np.mean(r0 * r0))

        v = np.zeros((DEPTH, N_REPS))
        omc = np.zeros((DEPTH, N_REPS))         # 1 - corr(r, r_l)
        var_rl = np.zeros((DEPTH, N_REPS))
        for layer in range(DEPTH):
            for rep in range(N_REPS):
                w_arm = list(weights)
                w_arm[layer] = redraw_layer(net_seed, layer, rep)
                r_l = residual(forward_ybar(probes, w_arm))
                d = r0 - r_l
                v[layer, rep] = float(np.mean(d * d))
                var_l = float(np.mean(r_l * r_l))
                var_rl[layer, rep] = var_l
                cov = float(np.mean(r0 * r_l))
                omc[layer, rep] = 1.0 - cov / math.sqrt(var_r0 * var_l)
                # identity cross-check (independent recomputation)
                v_id = var_r0 + var_l - 2.0 * cov
                rel = abs(v_id - v[layer, rep]) / max(v[layer, rep], 1e-300)
                identity_max_rel = max(identity_max_rel, rel)
            print(f"net {net_seed} layer {layer:2d}: "
                  f"v_l reps = {v[layer, 0]:.4e} {v[layer, 1]:.4e} "
                  f"{v[layer, 2]:.4e}   1-corr = {omc[layer].mean():.4f}",
                  flush=True)

        v_mean = v.mean(axis=1)
        v_sem = v.std(axis=1, ddof=1) / math.sqrt(N_REPS)
        omc_mean = omc.mean(axis=1)
        shares_v = v_mean / v_mean.sum()
        shares_omc = omc_mean / omc_mean.sum()
        variant_ratio = np.exp(np.abs(np.log(shares_v / shares_omc))).max()

        flat = np.array(mf["flat_shape_normalized"])
        dev_flat = np.exp(np.abs(np.log(shares_v / flat)))
        refn = np.array(mf["refinement_shape_normalized"])
        dev_refn = np.exp(np.abs(np.log(shares_v / refn)))

        order = np.argsort(v_mean)[::-1]
        top5_layers = [int(x) for x in order[:5]]
        top5_share = float(shares_v[order[:5]].sum())
        last3_share = float(shares_v[-3:].sum())

        per_net[str(net_seed)] = {
            "var_r_baseline": var_r0,
            "v_l_mean": v_mean.tolist(),
            "v_l_sem": v_sem.tolist(),
            "v_l_reps": v.tolist(),
            "var_r_l_mean": var_rl.mean(axis=1).tolist(),
            "one_minus_corr_mean": omc_mean.tolist(),
            "shares_v": shares_v.tolist(),
            "shares_one_minus_corr": shares_omc.tolist(),
            "variant_shape_max_ratio": float(variant_ratio),
            "dev_vs_flat_per_layer": dev_flat.tolist(),
            "dev_vs_flat_max": float(dev_flat.max()),
            "layers_dev_gt_pass": [int(l) for l in np.where(
                dev_flat > PASS_FACTOR)[0]],
            "layers_dev_gt_kill": [int(l) for l in np.where(
                dev_flat > KILL_FACTOR)[0]],
            "dev_vs_refinement_per_layer": dev_refn.tolist(),
            "dev_vs_refinement_max": float(dev_refn.max()),
            "top5_layers": top5_layers,
            "top5_share": top5_share,
            "last3_share": last3_share,
            "pass_net": bool(dev_flat.max() <= PASS_FACTOR),
            "wall_s": round(time.perf_counter() - t0, 1),
        }
        print(f"net {net_seed}: var(r)={var_r0:.4e}  "
              f"dev-vs-flat max={dev_flat.max():.2f}  "
              f"dev-vs-refinement max={dev_refn.max():.2f}  "
              f"top5={top5_layers} share={top5_share:.3f}  "
              f"last3 share={last3_share:.3f}  "
              f"({per_net[str(net_seed)]['wall_s']}s)", flush=True)

    results["per_net"] = per_net
    results["checks"] = {
        "mean_chi_formula_ok": True,
        "kerdock_radius_ok": True,
        "identity_max_rel_err": identity_max_rel,
    }

    # ---- bitwise repeat (determinism second signal) on net 101, l=13, rep=0
    weights = he_mlp_weights(101)
    rot = haar_rotation(rotation_seed(101))
    probes = np.ascontiguousarray((sub @ rot.T).astype(np.float32))
    w_arm = list(weights)
    w_arm[13] = redraw_layer(101, 13, 0)
    ya = forward_ybar(probes, w_arm)
    w_arm2 = list(he_mlp_weights(101))
    w_arm2[13] = redraw_layer(101, 13, 0)
    yb = forward_ybar(probes, w_arm2)
    results["checks"]["bitwise_repeat_ok"] = bool(np.array_equal(ya, yb))

    # ---- gates
    profiles = [np.array(per_net[str(s)]["shares_v"]) for s in NET_SEEDS]
    sp = [spearman(profiles[i], profiles[j])
          for i in range(3) for j in range(i + 1, 3)]
    coherence = float(np.mean(sp))
    coherent = coherence >= COHERENCE_SPEARMAN

    n_pass = sum(per_net[str(s)]["pass_net"] for s in NET_SEEDS)
    overall_pass = n_pass >= 2

    # kill: >=2 layers with dev>5 on >=2 nets, AND no coherent structure
    gt5_count = np.zeros(DEPTH, dtype=int)
    for s in NET_SEEDS:
        for l in per_net[str(s)]["layers_dev_gt_kill"]:
            gt5_count[l] += 1
    layers_gt5_on_2nets = [int(l) for l in np.where(gt5_count >= 2)[0]]
    kill = (len(layers_gt5_on_2nets) >= 2) and (not coherent)

    if overall_pass:
        verdict = "PASS"
    elif kill:
        verdict = "KILL"
    else:
        verdict = "FAIL-PASS / NOT-KILLED (coherent structure deviating " \
                  "from the fixed-point mean-field profile)"

    results["gates"] = {
        "pass_per_net": {str(s): per_net[str(s)]["pass_net"]
                         for s in NET_SEEDS},
        "n_pass": int(n_pass),
        "overall_pass": bool(overall_pass),
        "coherence_pairwise_spearman": sp,
        "coherence_mean_spearman": coherence,
        "coherent": bool(coherent),
        "layers_dev_gt5_on_ge2_nets": layers_gt5_on_2nets,
        "kill": bool(kill),
        "verdict": verdict,
    }
    results["wall_s_total"] = round(time.perf_counter() - t_start, 1)

    out_path.write_text(
        json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"\nVERDICT: {verdict}")
    print(f"coherence (mean pairwise Spearman) = {coherence:.4f}")
    print(f"identity cross-check max rel err = {identity_max_rel:.2e}")
    print(f"bitwise repeat ok = {results['checks']['bitwise_repeat_ok']}")
    print(f"results written to {out_path}  "
          f"({results['wall_s_total']}s total)")


if __name__ == "__main__":
    main()
