"""S11 (s11_full129_reopen_measured_breakeven) -- MEASURED break-even for the
126->129 real-MUB completion. Explicit reopen of killed m81_full129_pareto,
which was killed for never MEASURING whether the champion-MSE reduction from
deg-4 exactness beats the +2.381% cost of the extra points.

Break-even (M81, re-derived here): S = MSE * max(0.1, C/B). C proportional to
point count. 66048/64512 = 1.023809524. To improve S in the metered regime
need MSE_129/MSE_126 < 64512/66048 = 0.9767441860 -> "the raw MSE reduction
must exceed 2.32558%" (M81 ledger, verbatim).

Direct falsifier (gold standard): same 3 cached-truth synthetic nets as
m191/m181, champion (plain final-layer mean) estimator, 126-frame Kerdock
design vs the verified 129-frame 5-design (verify_design.py: deg-4 error
identically 0). fhat_129 reuses the 126-frame forward exactly:
    fhat_129 = (64512*fhat_126 + 1536*fhat_add129) / 66048
where fhat_add129 is the antipodal mean over the 3 completion frames
(phased-Hadamard indices 0,1 + standard basis), same net, same rotation.

CONTROL (attack-the-conclusion): fhat_ctrl adds 3 FIXED Haar-random
orthonormal frames instead of the completion -- same +1536 points, same cost,
but NOT a 5-design (deg-4 error NOT zeroed). Isolates the deg-4 value from the
pure more-samples averaging benefit. Prediction: ctrl ratio ~ break-even
0.97674 (iid averaging is score-neutral); completion below it iff deg-4 pays.

Two signals: (1) fhat_126 reproduces cached m181 arm0 baseline bitwise;
(2) an INDEPENDENT rotation reseed reproduces the panel ratio; pooled for the
headline.

Firewall: synthetic He nets only; kerdock_phases.npz + m181 caches read-only;
frozen sources imported unmodified; writes confined to s11_full129_breakeven;
plain numpy; no dataset/scorer/submission; no git.
"""
from __future__ import annotations
import json, math, sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
N8A = HERE.parent / "n8a_rqmc_kerdock"
PB1 = HERE.parent / "pb1_premise_battery"
M181 = HERE.parent / "m181_terminal_smoothing"
sys.path.insert(0, str(N8A))
sys.path.insert(0, str(PB1))
from run_n8a_gates import (load_kerdock_directions, haar_rotation,
                           he_mlp_weights, WIDTH, MEAN_CHI_256)      # noqa: E402
from run_m191_g0b import forward_final, rot_seed                    # noqa: E402

V3 = Path(r"C:\Users\strid\Documents\Codex\2026-08-02"
          r"\https-chatgpt-com-share-6a5556ed-2e1c\work\scorefloor_generation"
          r"\kerdock_l1_owned_buffer\candidate_source_validator_v3")

N = WIDTH
NET_SEEDS = (101, 202, 303)
REPLICATES = 32              # per family (>= m191's 16); 2 families = 64 total
N_TOTAL_126 = 64512
N_ADD = 1536
N_TOTAL_129 = N_TOTAL_126 + N_ADD           # 66048
COST_RATIO = N_TOTAL_129 / N_TOTAL_126      # 1.023809524
BREAKEVEN = N_TOTAL_126 / N_TOTAL_129       # 0.9767441860
BOOT_DRAWS = 4000
BOOT_SEED = 20260809
CTRL_FRAME_SEED = 5110809


def completion_base_directions() -> np.ndarray:
    """3 completion frames at radius MEAN_CHI: phased-Hadamard indices {0,1}
    (the 2 trimmed off the 128-frame Kerdock set) + standard basis. (768,256)."""
    packed = np.load(V3 / "kerdock_phases.npz")["negative_bits"]
    negative = np.unpackbits(packed, axis=1, bitorder="little")[:, :WIDTH]
    phases = (1.0 - 2.0 * negative.astype(np.float32))
    hadamard = np.array([[1.0]], dtype=np.float32)
    while hadamard.shape[0] < WIDTH:
        hadamard = np.block([[hadamard, hadamard], [hadamard, -hadamard]])
    h_norm = (hadamard / 16.0).astype(np.float32)
    ph = phases[0:2]
    phased = (MEAN_CHI_256 * (h_norm[None, :, :] * ph[:, None, :])).reshape(
        2 * WIDTH, WIDTH).astype(np.float32)
    std = (MEAN_CHI_256 * np.eye(WIDTH)).astype(np.float32)
    added = np.concatenate([phased, std], axis=0)
    if not np.allclose(np.linalg.norm(added, axis=1), MEAN_CHI_256, rtol=1e-5):
        raise RuntimeError("completion frames lost the fixed radius")
    return added


def control_base_directions() -> np.ndarray:
    """3 FIXED Haar-random orthonormal frames at radius MEAN_CHI (768,256).
    Not a 5-design completion -- the same +1536 points without zeroing deg-4."""
    rng = np.random.default_rng(CTRL_FRAME_SEED)
    frames = []
    for _ in range(3):
        q, r = np.linalg.qr(rng.standard_normal((WIDTH, WIDTH)))
        q = q * np.sign(np.diag(r))[None, :]     # deterministic sign fix
        frames.append(MEAN_CHI_256 * q.T)        # rows = orthonormal directions
    added = np.concatenate(frames, axis=0).astype(np.float32)
    if not np.allclose(np.linalg.norm(added, axis=1), MEAN_CHI_256, rtol=1e-5):
        raise RuntimeError("control frames lost the fixed radius")
    return added


def seed_matched(net, rep):
    return rot_seed(net, rep)            # 900000 + net*1000 + rep (m181/m191)


def seed_reseed(net, rep):
    return 314159 + net * 1000 + rep     # independent rotation family


def run_family(seed_fn, kerdock, comp, ctrl):
    out = {}
    for net in NET_SEEDS:
        w = he_mlp_weights(net)
        f126, f129, fctrl = [], [], []
        t0 = time.perf_counter()
        for rep in range(REPLICATES):
            rot = haar_rotation(seed_fn(net, rep))
            fhat126 = forward_final(
                w, (kerdock @ rot.T).astype(np.float32)
            ).astype(np.float64).mean(axis=0)
            fadd = forward_final(
                w, (comp @ rot.T).astype(np.float32)
            ).astype(np.float64).mean(axis=0)
            fcadd = forward_final(
                w, (ctrl @ rot.T).astype(np.float32)
            ).astype(np.float64).mean(axis=0)
            fhat129 = (N_TOTAL_126 * fhat126 + N_ADD * fadd) / N_TOTAL_129
            fhatc = (N_TOTAL_126 * fhat126 + N_ADD * fcadd) / N_TOTAL_129
            f126.append(fhat126); f129.append(fhat129); fctrl.append(fhatc)
        out[net] = {"f126": np.stack(f126), "f129": np.stack(f129),
                    "fctrl": np.stack(fctrl)}
        print(f"  net {net}: {REPLICATES} reps ({time.perf_counter()-t0:.0f}s)",
              flush=True)
    return out


def mse_ns(est, tm, noise):
    return float(((est - tm[None]) ** 2).mean()) - noise


def panel(fam_a, fam_b, truths, key):
    """geomean over nets of MSE_key/MSE_126 pooling fam_a+fam_b reps per net."""
    logs, rows = [], []
    for net in NET_SEEDS:
        tm = truths[net]["means"]; noise = float(truths[net]["noise_final"])
        e126 = np.concatenate([fam_a[net]["f126"], fam_b[net]["f126"]])
        ekey = np.concatenate([fam_a[net][key], fam_b[net][key]])
        m126 = mse_ns(e126, tm, noise); mkey = mse_ns(ekey, tm, noise)
        logs.append(math.log(mkey / m126))
        rows.append({"net_seed": net, "mse126": m126, f"mse_{key}": mkey,
                     "ratio": mkey / m126, "reduction_pct": 100*(1-mkey/m126)})
    return math.exp(float(np.mean(logs))), rows


def panel_single(fam, truths, key):
    logs = []
    for net in NET_SEEDS:
        tm = truths[net]["means"]; noise = float(truths[net]["noise_final"])
        m126 = mse_ns(fam[net]["f126"], tm, noise)
        mkey = mse_ns(fam[net][key], tm, noise)
        logs.append(math.log(mkey / m126))
    return math.exp(float(np.mean(logs)))


def boot_ci(fam_a, fam_b, truths, key):
    rng = np.random.default_rng(BOOT_SEED)
    pooled = {net: {"f126": np.concatenate([fam_a[net]["f126"],
                                            fam_b[net]["f126"]]),
                    key: np.concatenate([fam_a[net][key], fam_b[net][key]])}
              for net in NET_SEEDS}
    R = 2 * REPLICATES
    boots = []
    for _ in range(BOOT_DRAWS):
        logs = []
        for net in NET_SEEDS:
            tm = truths[net]["means"]; noise = float(truths[net]["noise_final"])
            idx = rng.integers(0, R, size=R)
            m126 = float(((pooled[net]["f126"][idx]-tm[None])**2).mean()) - noise
            mkey = float(((pooled[net][key][idx]-tm[None])**2).mean()) - noise
            m126 = max(m126, 1e-18); mkey = max(mkey, 1e-18)
            logs.append(math.log(mkey / m126))
        boots.append(math.exp(float(np.mean(logs))))
    return (float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5)))


def gate(reduction):
    if reduction < 0.0233:
        return "RE-KILLED (below 2.33% break-even)"
    if reduction > 0.03:
        return "ADVANCE-TO-M81-GATES (>~3%; flag for Sol, do NOT build)"
    return "INCONCLUSIVE (2.33-3%, too thin vs memory cost)"


def main():
    t0 = time.perf_counter()
    kerdock = load_kerdock_directions()
    comp = completion_base_directions()
    ctrl = control_base_directions()
    truths = {net: dict(np.load(M181 / f"m181_truth_net{net}.npz"))
              for net in NET_SEEDS}

    print("PRIMARY (matched m181/m191 rotation seeds):", flush=True)
    prim = run_family(seed_matched, kerdock, comp, ctrl)
    print("RESEED (independent rotation family):", flush=True)
    rese = run_family(seed_reseed, kerdock, comp, ctrl)

    bitwise = {}
    for net in NET_SEEDS:
        ref = np.load(M181 / f"m181_g0_partial_net{net}.npz")["arm0_baseline"]
        bitwise[str(net)] = float(np.max(np.abs(prim[net]["f126"][:16] - ref)))

    np.savez(HERE / "s11_stacks.npz",
             **{f"prim_{net}_{k}": prim[net][k]
                for net in NET_SEEDS for k in ("f126", "f129", "fctrl")},
             **{f"rese_{net}_{k}": rese[net][k]
                for net in NET_SEEDS for k in ("f126", "f129", "fctrl")})

    # pooled headline (both families, 64 reps/net)
    comp_ratio, comp_rows = panel(prim, rese, truths, "f129")
    comp_ci = boot_ci(prim, rese, truths, "f129")
    ctrl_ratio, ctrl_rows = panel(prim, rese, truths, "fctrl")
    ctrl_ci = boot_ci(prim, rese, truths, "fctrl")
    # per-family (independent-signal agreement)
    comp_prim = panel_single(prim, truths, "f129")
    comp_rese = panel_single(rese, truths, "f129")

    comp_red = 1.0 - comp_ratio
    results = {
        "ledger_id": "s11_full129_reopen_measured_breakeven",
        "date": "2026-08-09",
        "reopen_of": "m81_full129_pareto (killed: never measured MSE reduction; "
                     "and on memory margin -- see memory_ground_status)",
        "break_even": {
            "adjusted_score": "S = MSE * max(0.1, C/B); C proportional to points",
            "point_counts": {"design126": N_TOTAL_126, "design129": N_TOTAL_129,
                             "added": N_ADD},
            "cost_ratio_C129_over_C126": COST_RATIO,
            "mse_ratio_breakeven_bar": BREAKEVEN,
            "required_raw_mse_drop_pct": 100.0 * (1.0 - BREAKEVEN),
            "regime_check": {
                "hosted_326094_adjusted": 1.832e-7, "hosted_326094_mse": 2.818e-7,
                "cb_implied": 1.832e-7 / 2.818e-7,
                "conclusion": "C/B=0.6501 > 0.1 floor => metered regime => the "
                              "proportional break-even (2.32558%) applies, NOT "
                              "the floored regime"},
        },
        "design_verification": "verify_design.py: 129-frame per-line 4th-moment "
                               "sum = 1.5 exactly (min=max) = Welch 3/(d(d+2)) => "
                               "exact spherical 5-design => deg-4 error == 0; "
                               "126-frame = 1.48828 (1.581% frame-potential "
                               "excess). All 3 completion frames unbiased {0,1/16}.",
        "committed_data_sufficiency": (
            "INSUFFICIENT to pin the deg-4 SHARE of champion MSE from arithmetic "
            "alone: S6 gives the design's per-degree ERROR operator (deg4 tr(D^2), "
            "3-shell eigs) and m191-g0a the per-degree error LEVELS "
            "(deg4 rms/iid=0.107, deg6=0.40), but neither pins the champion "
            "ESTIMAND's per-degree ENERGY E_l needed for share = E_4 D_4 / "
            "sum_l E_l D_l. Committed proxies bound it: m191 cv_deg4 removed "
            "0.42% (aligned/removable, 12-dir basis), R^2_deg4=0.18-0.23% -- both "
            "lower bounds, underestimates because the estimand's deg-4 energy is "
            "spread across the 1.8e8-dim H4 space. Hence the DIRECT measurement."),
        "config": {"width": N, "depth": 32, "net_seeds": list(NET_SEEDS),
                   "replicates_per_family": REPLICATES, "families": 2,
                   "estimator": "plain final-layer antipodal ReLU mean (champion)",
                   "truth": "m181_truth_net*.npz 3.5M iid MC, noise subtracted",
                   "matched_seed_formula": "900000+net*1000+rep",
                   "reseed_formula": "314159+net*1000+rep",
                   "control": "3 fixed Haar-random orthonormal frames "
                              f"(seed {CTRL_FRAME_SEED}), radius MEAN_CHI, +1536 "
                              "points, NOT a 5-design",
                   "bootstrap_draws": BOOT_DRAWS},
        "firewall": ("synthetic He nets only; kerdock_phases.npz + m181 caches "
                     "read-only; frozen sources imported unmodified; writes "
                     "confined to s11_full129_breakeven; plain numpy; no "
                     "dataset/scorer/submission; no git"),
        "signal1_bitwise_fhat126_vs_m181_arm0_maxdiff": bitwise,
        "completion_129": {
            "panel_ratio_pooled_64reps": comp_ratio,
            "panel_reduction_pct": 100.0 * comp_red,
            "bootstrap_ci95_ratio": comp_ci,
            "per_family_ratio": {"primary_32": comp_prim, "reseed_32": comp_rese},
            "per_net": comp_rows,
            "adjusted_score_ratio_S129_over_S126": comp_ratio * COST_RATIO,
            "gate": gate(comp_red)},
        "control_random3frames": {
            "panel_ratio_pooled_64reps": ctrl_ratio,
            "panel_reduction_pct": 100.0 * (1.0 - ctrl_ratio),
            "bootstrap_ci95_ratio": ctrl_ci,
            "per_net": ctrl_rows,
            "interpretation": "isolates pure more-samples averaging; ~break-even "
                              "0.97674 confirms adding generic points is "
                              "score-neutral; completion below it = deg-4 value"},
        "deg4_attributable_score_gain_pct": 100.0 * (ctrl_ratio - comp_ratio),
        "memory_ground_status": (
            "UNCHANGED / STILL APPLIES. M81's kill had TWO edges: (1) unmeasured "
            "variance value -- addressed here; (2) memory margin -- min persistent "
            "increment 1.75195 MiB vs M71 frozen margin 1.44531 MiB, crossing the "
            "480 MiB safety gate. S11 measured ONLY edge (1). The memory kill "
            "still stands and is a separate gate Sol must clear before any build."),
        "wall_s": time.perf_counter() - t0,
    }
    outp = HERE / "s11_results.json"
    outp.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(f"\nCOMPLETION panel MSE_129/MSE_126 = {comp_ratio:.6f} "
          f"(reduction {100*comp_red:+.3f}%), CI [{comp_ci[0]:.5f}, "
          f"{comp_ci[1]:.5f}]  bar {BREAKEVEN:.6f}")
    print(f"  per-family: primary {comp_prim:.6f}, reseed {comp_rese:.6f}")
    print(f"  adjusted-score ratio S129/S126 = {comp_ratio*COST_RATIO:.6f}")
    print(f"CONTROL (random 3 frames) ratio = {ctrl_ratio:.6f} "
          f"(reduction {100*(1-ctrl_ratio):+.3f}%), CI [{ctrl_ci[0]:.5f}, "
          f"{ctrl_ci[1]:.5f}]  (break-even ref {BREAKEVEN:.6f})")
    print(f"deg-4-attributable score gain = {100*(ctrl_ratio-comp_ratio):+.3f}%")
    print(f"bitwise fhat126 vs m181 arm0: {bitwise}")
    print(f"GATE: {gate(comp_red)}")
    print(f"results -> {outp}  ({results['wall_s']:.0f}s)")


if __name__ == "__main__":
    main()
