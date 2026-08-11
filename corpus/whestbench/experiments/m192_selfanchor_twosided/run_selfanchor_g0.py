"""M192-SELFANCHOR cached kill-confirmation: self-anchored two-sided contrast GLS.

Governing protocol: PREDECLARATION.md beside this file.  Step 0 of that
protocol already kills the construction algebraically; this runner exists to
confirm the sharp refutable consequence (panel ratio exactly 1.0) and to
measure the killed quantity directly.

Performs no network forward, no generation, no evaluation.  Pure arithmetic on
cached committed artifacts.  Writes only results.json beside itself.
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
import traceback
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "6")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "6")
os.environ.setdefault("MKL_NUM_THREADS", "6")
sys.dont_write_bytecode = True

import numpy as np

HERE = Path(__file__).resolve().parent
M192 = HERE.parent / "m192_cross_output_gls"
PB1 = HERE.parent / "pb1_premise_battery"
M181 = HERE.parent / "m181_terminal_smoothing"
sys.path.insert(0, str(M192))

import run_m192_g0 as m192  # noqa: E402  frozen source, imported not edited
import run_m194_g0 as m194  # noqa: E402  frozen source, imported not edited

NETS = (101, 202, 303)
N_FRAMES = 126
N_OUTPUTS = 256
N_FOLDS = 8
ALPHA_FROZEN = 0.25
ALPHAS = m192.ALPHAS
SHUFFLE_SEED = 20260810
RATIO_TOL = 1e-9
UNIFORM = np.full(N_FRAMES, 1.0 / N_FRAMES, dtype=np.float64)


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def self_second_moment(frame_means: np.ndarray, outputs: np.ndarray) -> np.ndarray:
    """Row-centred (self-anchored) sample second moment: P S P, no truth used.

    a_j = column mean over the 126 frames, r_j = x_j - a_j*1 = P x_j.
    """
    block = frame_means[:, outputs]
    residual = block - block.mean(axis=0, keepdims=True)
    return (residual @ residual.T) / float(len(outputs))


def oracle_second_moment(frame_means: np.ndarray, truth: np.ndarray,
                         outputs: np.ndarray) -> np.ndarray:
    return m192._second_moment(frame_means, truth, outputs)


def row_shuffle(block: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Independently permute the output-neuron index inside each frame row.

    Destroys cross-output coherence (an output no longer owns a coherent
    126-vector) while preserving every frame's marginal set of values.
    """
    out = np.empty_like(block)
    n = block.shape[1]
    for i in range(block.shape[0]):
        out[i] = block[i, rng.permutation(n)]
    return out


def folds():
    outputs = np.arange(N_OUTPUTS)
    for f in range(N_FOLDS):
        yield f, outputs[outputs % N_FOLDS == f], outputs[outputs % N_FOLDS != f]


def panel(per_net_ratio: dict) -> float:
    vals = [per_net_ratio[n] for n in NETS]
    return math.exp(sum(math.log(v) for v in vals) / len(vals))


def main() -> None:
    t0 = time.time()
    results: dict = {
        "candidate": "m192_selfanchor_two_sided_contrast_gls",
        "protocol": "PREDECLARATION.md",
        "firewall": ("cached synthetic P2 frame matrices and M181 truths; frozen "
                     "M192/M194 sources imported unmodified; no forward, no "
                     "generation, no evaluation, no submission"),
        "frozen_alpha": ALPHA_FROZEN,
        "shuffle_seed": SHUFFLE_SEED,
    }

    p2 = json.loads((PB1 / "p2_results.json").read_text(encoding="utf-8"))
    m192_frozen = json.loads((M192 / "m192_g0_results.json").read_text(encoding="utf-8"))

    cache = {}
    for net in NETS:
        stacks = np.asarray(np.load(PB1 / f"p2_partial_net{net}.npz")["frame_means"],
                            dtype=np.float64)
        truth = np.asarray(np.load(M181 / f"m181_truth_net{net}.npz")["means"],
                           dtype=np.float64)
        if stacks.shape != (16, N_FRAMES, N_OUTPUTS):
            raise RuntimeError(f"net {net}: unexpected cache shape {stacks.shape}")
        if truth.shape != (N_OUTPUTS,):
            raise RuntimeError(f"net {net}: unexpected truth shape {truth.shape}")
        cache[net] = (stacks, truth)
    log(f"loaded caches: 3 nets x {stacks.shape[0]} rotations x {N_FRAMES}x{N_OUTPUTS}")

    # ---------------------------------------------------------------- A0
    # Harness identity: re-run the frozen M192 machinery, reproduce the archive.
    log("A0 crosscheck: re-running frozen M192 oracle machinery (384 outer fits, "
        "9216 inner fits) ...")
    a0 = {"per_net": {}}
    for net in NETS:
        stacks, truth = cache[net]
        rows = [m192._one_rotation(stacks[r], truth) for r in range(stacks.shape[0])]
        base = np.array([r["base_mse"] for r in rows])
        gls = np.array([r["gls_mse"] for r in rows])
        archived_base = np.asarray(
            p2["q1_oracle_headroom"]["per_net"][str(net)]["mse_per_rotation"],
            dtype=np.float64)
        ratio = float(gls.mean() / base.mean())
        frozen_ratio = float(m192_frozen["per_net"][str(net)]["ratio_of_rotation_means"])
        a0["per_net"][str(net)] = {
            "ratio_of_rotation_means": ratio,
            "frozen_archive_ratio": frozen_ratio,
            "abs_diff_vs_frozen": abs(ratio - frozen_ratio),
            "max_p2_baseline_crosscheck": float(np.max(np.abs(base - archived_base))),
        }
        log(f"  A0 net {net}: ratio={ratio:.6f} frozen={frozen_ratio:.6f} "
            f"diff={abs(ratio - frozen_ratio):.3e}")
    a0["panel_ratio_geomean"] = panel(
        {n: a0["per_net"][str(n)]["ratio_of_rotation_means"] for n in NETS})
    a0["frozen_panel_ratio_geomean"] = float(m192_frozen["panel_ratio_geomean"])
    a0["max_abs_diff_vs_frozen"] = max(
        a0["per_net"][str(n)]["abs_diff_vs_frozen"] for n in NETS)
    a0["reproduces_archive"] = bool(a0["max_abs_diff_vs_frozen"] < 1e-12)
    results["A0_harness_crosscheck"] = a0
    log(f"A0 panel={a0['panel_ratio_geomean']:.6f} "
        f"frozen={a0['frozen_panel_ratio_geomean']:.6f} "
        f"reproduces={a0['reproduces_archive']}")

    # ---------------------------------------------------------------- A1
    # Self-anchor through the frozen M192 sum-one GLS solver, alpha frozen.
    log("A1 self-anchor / M192 solver, alpha=0.25 frozen ...")
    a1_per_net = {}
    a1_boot_input = {}
    kernel_residuals, weight_devs, l1s = [], [], []
    for net in NETS:
        stacks, truth = cache[net]
        base_list, cand_list, rot_ratio = [], [], []
        for r in range(stacks.shape[0]):
            fm = stacks[r]
            corrected = np.empty(N_OUTPUTS, dtype=np.float64)
            for _, held, train in folds():
                c = self_second_moment(fm, train)
                nrm = float(np.linalg.norm(c))
                kernel_residuals.append(
                    float(np.linalg.norm(c @ np.ones(N_FRAMES)) /
                          (nrm * math.sqrt(N_FRAMES))))
                w, _ = m192._weights(c, ALPHA_FROZEN)
                weight_devs.append(float(np.max(np.abs(w - UNIFORM))))
                l1s.append(float(np.abs(w).sum()))
                corrected[held] = w @ fm[:, held]
            uniform_pred = fm.mean(axis=0, dtype=np.float64)
            b = float(np.mean((uniform_pred - truth) ** 2))
            c_ = float(np.mean((corrected - truth) ** 2))
            base_list.append(b)
            cand_list.append(c_)
            rot_ratio.append(c_ / b)
        base = np.asarray(base_list)
        cand = np.asarray(cand_list)
        ratio = float(cand.mean() / base.mean())
        a1_per_net[str(net)] = {
            "ratio_of_rotation_means": ratio,
            "per_rotation_ratio": rot_ratio,
            "max_abs_rotation_ratio_minus_one": float(
                np.max(np.abs(np.asarray(rot_ratio) - 1.0))),
            "base_mse_per_rotation": base.tolist(),
            "gls_mse_per_rotation": cand.tolist(),
        }
        a1_boot_input[net] = {"base_mse_per_rotation": base.tolist(),
                              "gls_mse_per_rotation": cand.tolist()}
        log(f"  A1 net {net}: ratio={ratio:.12f} "
            f"max|rot ratio-1|={a1_per_net[str(net)]['max_abs_rotation_ratio_minus_one']:.3e}")
    a1_panel = panel({n: a1_per_net[str(n)]["ratio_of_rotation_means"] for n in NETS})
    results["A1_selfanchor_m192_solver"] = {
        "per_net": a1_per_net,
        "panel_ratio_geomean": a1_panel,
        "bootstrap_95_ratio": m192._bootstrap(a1_boot_input),
        "max_abs_weight_minus_uniform": float(np.max(weight_devs)),
        "median_weight_l1": float(np.median(l1s)),
        "max_weight_l1": float(np.max(l1s)),
        "max_relative_kernel_residual_C1": float(np.max(kernel_residuals)),
        "fits": len(weight_devs),
    }
    log(f"A1 panel={a1_panel:.12f} max|w-1/126|={np.max(weight_devs):.3e} "
        f"max rel |C1|={np.max(kernel_residuals):.3e}")

    # ------------------------------------------------------- A1 alpha sweep
    log("A1b alpha sweep (robustness; predeclared to be alpha-invariant for alpha>0) ...")
    sweep = {}
    for alpha in ALPHAS:
        try:
            per_net_ratio, devs = {}, []
            for net in NETS:
                stacks, truth = cache[net]
                bl, cl = [], []
                for r in range(stacks.shape[0]):
                    fm = stacks[r]
                    corrected = np.empty(N_OUTPUTS, dtype=np.float64)
                    for _, held, train in folds():
                        w, _ = m192._weights(self_second_moment(fm, train), alpha)
                        devs.append(float(np.max(np.abs(w - UNIFORM))))
                        corrected[held] = w @ fm[:, held]
                    u = fm.mean(axis=0, dtype=np.float64)
                    bl.append(float(np.mean((u - truth) ** 2)))
                    cl.append(float(np.mean((corrected - truth) ** 2)))
                per_net_ratio[net] = float(np.mean(cl) / np.mean(bl))
            sweep[str(alpha)] = {
                "per_net_ratio": {str(k): v for k, v in per_net_ratio.items()},
                "panel_ratio_geomean": panel(per_net_ratio),
                "max_abs_weight_minus_uniform": float(np.max(devs)),
                "error": None,
            }
            log(f"  alpha={alpha}: panel={sweep[str(alpha)]['panel_ratio_geomean']:.12f} "
                f"max|w-u|={np.max(devs):.3e}")
        except Exception as exc:  # predeclared: alpha=0 is exactly singular
            sweep[str(alpha)] = {"per_net_ratio": None, "panel_ratio_geomean": None,
                                 "max_abs_weight_minus_uniform": None,
                                 "error": f"{type(exc).__name__}: {exc}"}
            log(f"  alpha={alpha}: EXCEPTION {type(exc).__name__}: {exc}")
    results["A1b_alpha_sweep"] = sweep

    # ---------------------------------------------------------------- A2
    # Independent implementation: frozen M194 projected-block solver, self anchor.
    log("A2 self-anchor / M194 projected-block solver (independent implementation) ...")
    a2_per_net, cross_self, cross_truth, a2_devs = {}, [], [], []
    for net in NETS:
        stacks, truth = cache[net]
        bl, cl = [], []
        for r in range(stacks.shape[0]):
            fm = stacks[r]
            anchor = fm.mean(axis=0, dtype=np.float64)  # the self-anchor
            corrected = np.empty(N_OUTPUTS, dtype=np.float64)
            for _, held, train in folds():
                w, diag = m194._block_weights(fm, anchor, train)
                cross_self.append(diag["cross_norm"])
                a2_devs.append(float(np.max(np.abs(w - UNIFORM))))
                corrected[held] = w @ fm[:, held]
                _, tdiag = m194._block_weights(fm, truth, train)
                cross_truth.append(tdiag["cross_norm"])
            u = fm.mean(axis=0, dtype=np.float64)
            bl.append(float(np.mean((u - truth) ** 2)))
            cl.append(float(np.mean((corrected - truth) ** 2)))
        a2_per_net[str(net)] = float(np.mean(cl) / np.mean(bl))
        log(f"  A2 net {net}: ratio={a2_per_net[str(net)]:.12f}")
    results["A2_selfanchor_m194_solver"] = {
        "per_net_ratio": a2_per_net,
        "panel_ratio_geomean": panel({n: a2_per_net[str(n)] for n in NETS}),
        "max_abs_weight_minus_uniform": float(np.max(a2_devs)),
        "cross_block_norm_self_anchor_max": float(np.max(cross_self)),
        "cross_block_norm_self_anchor_median": float(np.median(cross_self)),
        "cross_block_norm_truth_anchor_median": float(np.median(cross_truth)),
        "cross_block_norm_truth_anchor_min": float(np.min(cross_truth)),
        "killed_information_ratio_median": float(
            np.median(cross_self) / np.median(cross_truth)),
    }
    log(f"A2 panel={results['A2_selfanchor_m194_solver']['panel_ratio_geomean']:.12f} "
        f"|b_self|med={np.median(cross_self):.3e} "
        f"|b_truth|med={np.median(cross_truth):.3e}")

    # ---------------------------------------------------------------- A3
    log("A3 permutation null control (per-frame output-index shuffle on the "
        "covariance training block) ...")
    rng = np.random.default_rng(SHUFFLE_SEED)
    a3_per_net, a3_devs = {}, []
    for net in NETS:
        stacks, truth = cache[net]
        bl, cl = [], []
        for r in range(stacks.shape[0]):
            fm = stacks[r]
            corrected = np.empty(N_OUTPUTS, dtype=np.float64)
            for _, held, train in folds():
                block = row_shuffle(fm[:, train], rng)
                residual = block - block.mean(axis=0, keepdims=True)
                c = (residual @ residual.T) / float(len(train))
                w, _ = m192._weights(c, ALPHA_FROZEN)
                a3_devs.append(float(np.max(np.abs(w - UNIFORM))))
                corrected[held] = w @ fm[:, held]
            u = fm.mean(axis=0, dtype=np.float64)
            bl.append(float(np.mean((u - truth) ** 2)))
            cl.append(float(np.mean((corrected - truth) ** 2)))
        a3_per_net[str(net)] = float(np.mean(cl) / np.mean(bl))
        log(f"  A3 net {net}: ratio={a3_per_net[str(net)]:.12f}")
    results["A3_permutation_null_control"] = {
        "per_net_ratio": a3_per_net,
        "panel_ratio_geomean": panel({n: a3_per_net[str(n)] for n in NETS}),
        "max_abs_weight_minus_uniform": float(np.max(a3_devs)),
    }

    # ---------------------------------------------------------------- A4
    log("A4 positive control: same shuffle inside the frozen M192 truth-trained "
        "oracle (power check for A3) ...")
    rng4 = np.random.default_rng(SHUFFLE_SEED + 1)
    a4_ref, a4_shuf = {}, {}
    for net in NETS:
        stacks, truth = cache[net]
        bl, ref, shf = [], [], []
        for r in range(stacks.shape[0]):
            fm = stacks[r]
            c_ref = np.empty(N_OUTPUTS, dtype=np.float64)
            c_shf = np.empty(N_OUTPUTS, dtype=np.float64)
            for _, held, train in folds():
                err = fm[:, train] - truth[train][None, :]
                w_ref, _ = m192._weights((err @ err.T) / float(len(train)),
                                         ALPHA_FROZEN)
                c_ref[held] = w_ref @ fm[:, held]
                err_s = row_shuffle(err, rng4)
                w_shf, _ = m192._weights((err_s @ err_s.T) / float(len(train)),
                                         ALPHA_FROZEN)
                c_shf[held] = w_shf @ fm[:, held]
            u = fm.mean(axis=0, dtype=np.float64)
            bl.append(float(np.mean((u - truth) ** 2)))
            ref.append(float(np.mean((c_ref - truth) ** 2)))
            shf.append(float(np.mean((c_shf - truth) ** 2)))
        a4_ref[str(net)] = float(np.mean(ref) / np.mean(bl))
        a4_shuf[str(net)] = float(np.mean(shf) / np.mean(bl))
        log(f"  A4 net {net}: oracle_unshuffled={a4_ref[str(net)]:.6f} "
            f"oracle_shuffled={a4_shuf[str(net)]:.6f}")
    results["A4_positive_control_m192_oracle"] = {
        "note": "control only; not a claim about M192",
        "per_net_ratio_unshuffled": a4_ref,
        "per_net_ratio_shuffled": a4_shuf,
        "panel_unshuffled": panel({n: a4_ref[str(n)] for n in NETS}),
        "panel_shuffled": panel({n: a4_shuf[str(n)] for n in NETS}),
    }

    # ---------------------------------------------------------------- A5
    # Identity check: the self-anchored covariance IS M192's true contrast
    # block.  If this holds, A1 ran the solver on the exact oracle A with b=0,
    # so the entire M192 headroom is attributable to b, not to A.
    log("A5 identity check: self-anchored covariance vs P C_m192 P ...")
    rel_errs = []
    proj = np.eye(N_FRAMES) - np.ones((N_FRAMES, N_FRAMES)) / N_FRAMES
    for net in NETS:
        stacks, truth = cache[net]
        for r in range(stacks.shape[0]):
            fm = stacks[r]
            for _, _, train in folds():
                self_c = self_second_moment(fm, train)
                proj_oracle = proj @ oracle_second_moment(fm, truth, train) @ proj
                rel_errs.append(float(np.linalg.norm(self_c - proj_oracle) /
                                      np.linalg.norm(proj_oracle)))
    results["A5_contrast_block_identity"] = {
        "claim": "self-anchored sample second moment == P C_m192 P exactly",
        "max_relative_frobenius_error": float(np.max(rel_errs)),
        "median_relative_frobenius_error": float(np.median(rel_errs)),
        "fits": len(rel_errs),
    }
    log(f"A5 max rel Frobenius error = {np.max(rel_errs):.3e}")

    # ------------------------------------------------------------- gates
    a1_ratios = [a1_per_net[str(n)]["ratio_of_rotation_means"] for n in NETS]
    nets_at_or_above_one = sum(1 for x in a1_ratios if x >= 1.0)
    nets_at_or_below_090 = sum(1 for x in a1_ratios if x <= 0.90)
    max_dev_from_one = max(abs(x - 1.0) for x in a1_ratios)
    prediction_held = bool(max_dev_from_one < RATIO_TOL)
    if nets_at_or_above_one >= 2:
        verdict = "KILLED"
    elif nets_at_or_below_090 >= 2:
        verdict = "SIGNAL"
    else:
        verdict = "INCONCLUSIVE"
    results["gates"] = {
        "kill_if_ratio_ge_1_on_2_of_3": nets_at_or_above_one,
        "signal_if_ratio_le_090_on_2_of_3": nets_at_or_below_090,
        "step0_algebraic_kill": True,
        "predicted_ratio_exactly_one": True,
        "max_abs_panel_deviation_from_one": max_dev_from_one,
        "prediction_tolerance": RATIO_TOL,
        "prediction_held": prediction_held,
        "signal_a_out_of_fold": "all held outputs excluded from their own weight fit",
        "signal_b_permutation_null": results["A3_permutation_null_control"][
            "panel_ratio_geomean"],
    }
    results["verdict"] = verdict
    results["runtime_seconds"] = time.time() - t0

    out = HERE / "results.json"
    out.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    log(f"A1 panel ratio = {a1_panel:.12f}")
    log(f"verdict = {verdict}  (prediction_held={prediction_held})")
    log(f"wrote {out}  in {results['runtime_seconds']:.1f}s")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        raise
