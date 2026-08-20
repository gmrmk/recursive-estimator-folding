"""PB-1 Premise Battery -- a cached-truth acceleration harness for the
Kerdock v3 failure-cross arms.  Predeclared in PB1_SPEC_AND_CROSSES.md (governs).

WHAT THIS IS
------------
A reusable accelerator for evaluating estimator dial-mutations ("arms").  The
expensive, arm-INDEPENDENT work -- the 3.5M-sample MC truth and the frozen-v3
baseline replication -- is computed ONCE (or reused from cache); each new arm
then costs only its own predict passes.  ~80% of a from-scratch G0's wall is
truth + baseline, so amortizing them is the acceleration.

HOW TO ADD AN ARM (the whole contract)
--------------------------------------
An arm is a ``Tuned`` subclass of the frozen v3 ``estimator.Estimator`` that
overrides one or more class-attribute dials -- NEVER edits a frozen file:

    Tuned = make_arm(on_alpha=4.0)            # or dead_alpha=-2.5, or both

``self.on_alpha`` / ``self.dead_alpha`` are read via MRO inside the frozen
fold3 ``predict``, so a subclass attribute overrides cleanly (verified).
Register it in ``ARMS`` below with a name and its dial dict; the battery runs
it under the panel's rotation seeds against the cached truth, computes the
paired final-layer MSE ratio + bootstrap 95% CI vs the cached baseline, and
records billed FLOPs.  Gates are applied automatically.

PANELS
------
* PRIMARY (governing): 3 high-precision nets (101/202/303), 16 rotation seeds
  each, cached m181 3.5M truth (floor ~1.5e-8).  Tight CIs -> the gate of
  record.
* WIDE (secondary, caveated): 80 nets (seeds 1000..1079), single rotation seed
  r=0, cached m185 truth31 (~6e-8 floor) with the frozen-v3 baseline pred31
  ALSO cached -> only the arm predicts run.  Reported with its noise caveat;
  does not block.

GATES (per arm, from the spec)
------------------------------
* KILL_FLOPS  : worst-case billed FLOPs (max over nets, max over reps) > 0.95*B
                -> killed regardless of MSE (the A4 constraint).  B = 2.72e11.
* KILL        : panel-MSE reduction < 10%.
* PROMOTE     : reduction >= 15% AND reduction-CI lower bound > 10% (CI excludes
                10%) AND worst-net(=worst-decile proxy) reduction >= 20%.
* otherwise   : SURVIVE_NO_PROMOTE (between the kill and promote bars).

Governing reduction = RAW measured-MSE reduction (what the benchmark literally
scores).  A noise-subtracted "true-MSE" reduction is reported as a diagnostic
(E[measured MSE] = true MSE + truth_noise; both arm and baseline carry the same
floor, so the raw ratio is the conservative choice).

FIREWALL: synthetic He nets only; frozen v3 imported read-only (bytecode off);
only the estimator's shipped sampling assets touched; cached truths & the m185
checkpoint read-only; no dataset/scorer/submission; writes only in this dir.
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True

import numpy as np

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
M181 = EXP / "m181_terminal_smoothing"
M185_CKPT = EXP / "a_series_granular_adversarial" / "m185_g0_stage1_checkpoint.json"

V3_DIR = Path(
    r"C:\Users\strid\Documents\Codex\2026-08-02"
    r"\https-chatgpt-com-share-6a5556ed-2e1c\work\scorefloor_generation"
    r"\kerdock_l1_owned_buffer\candidate_source_validator_v3"
)
sys.path.insert(0, str(V3_DIR))

import flopscope as flops           # noqa: E402
import flopscope.numpy as fnp       # noqa: E402
from whestbench import SetupContext  # noqa: E402
from whestbench.domain import MLP    # noqa: E402

flops.configure(symmetry_warnings=False)

from estimator import Estimator as KerdockV3  # noqa: E402  (frozen v3, read-only)

# ------------------------------------------------------------------ constants
WIDTH, DEPTH = 256, 32
B = int(2.72e11)                 # A4 compute cap denominator
METER = 10**15                   # FlopScope BudgetContext ceiling (never binds)
CAP_FRAC = 0.95                  # kill any arm whose worst-case billed > 0.95 B
PRIMARY_SEEDS = (101, 202, 303)
REPLICATES = 16
WIDE_SEEDS = tuple(range(1000, 1080))
BOOTSTRAP = 4000
KILL_RED = 0.10                  # reduction < 10% -> kill
PROMOTE_RED = 0.15               # reduction >= 15% (with CI + tail) -> promote
PROMOTE_TAIL = 0.20              # worst-net/worst-decile reduction >= 20%
BOOT_RNG_SEED = 20260808

# Predeclared arms (PB1_SPEC_AND_CROSSES.md).  Frozen v3 baseline: on=3.0,dead=-2.0.
ARMS_M188 = [
    ("M188_on3.5", dict(on_alpha=3.5)),
    ("M188_on4.0", dict(on_alpha=4.0)),
    ("M188_on5.0", dict(on_alpha=5.0)),
]
ARMS_M189 = [
    ("M189_dead-2.5", dict(dead_alpha=-2.5)),
    ("M189_dead-3.0", dict(dead_alpha=-3.0)),
]


# --------------------------------------------------------------------- helpers
def make_arm(on_alpha: float | None = None, dead_alpha: float | None = None):
    """Build a Tuned subclass overriding the class-attr dials (never edits v3)."""
    attrs: dict = {}
    if on_alpha is not None:
        attrs["on_alpha"] = float(on_alpha)
    if dead_alpha is not None:
        attrs["dead_alpha"] = float(dead_alpha)
    return type("Tuned", (KerdockV3,), attrs)


def he_weights(seed: int) -> list[np.ndarray]:
    rng = np.random.default_rng(seed)
    gain = np.float32(math.sqrt(2.0 / WIDTH))
    return [rng.standard_normal((WIDTH, WIDTH), dtype=np.float32) * gain
            for _ in range(DEPTH)]


def rot_seed(net_seed: int, r: int) -> int:
    return 900_000 + net_seed * 1_000 + r


def _new_estimator(cls):
    est = cls()
    est.setup(SetupContext(
        width=WIDTH, depth=DEPTH, flop_budget=B, api_version="synthetic",
        seed=0, submission_dir=str(V3_DIR),
    ))
    return est


def predict_final(est, weights_f, net_seed: int, r: int):
    """One predict pass -> (final-layer mean (256,), billed FLOPs int)."""
    mlp = MLP(width=WIDTH, depth=DEPTH, weights=weights_f,
              seed=rot_seed(net_seed, r), name=f"pb1-{net_seed}-{r}")
    mlp.validate()
    with flops.BudgetContext(METER, quiet=True) as ctx:
        out = est.predict(mlp, METER)
    return np.asarray(out).astype(np.float64)[-1], int(ctx.flops_used)


# ----------------------------------------------------------------- statistics
def per_net_mse(finals: np.ndarray, truth: np.ndarray) -> float:
    """Mean over reps of mean-over-neurons squared error vs cached truth."""
    return float(((finals - truth[None]) ** 2).mean())


def summarize_primary(arm_finals, base_finals, truths, noises, billed):
    """Paired panel-MSE ratio + bootstrap CI on the 3-net primary panel.

    arm_finals/base_finals: {net: (R,256)}.  truths/noises: {net: ...}.
    billed: {net: (R,)} for the arm.  Returns a dict of gate inputs.
    """
    nets = list(PRIMARY_SEEDS)
    base_mse = {n: per_net_mse(base_finals[n], truths[n]) for n in nets}
    arm_mse = {n: per_net_mse(arm_finals[n], truths[n]) for n in nets}
    # noise-subtracted (true-MSE) per net, floored at a tiny positive value.
    base_true = {n: max(base_mse[n] - noises[n], 1e-30) for n in nets}
    arm_true = {n: max(arm_mse[n] - noises[n], 1e-30) for n in nets}

    panel_base = float(np.mean([base_mse[n] for n in nets]))
    panel_arm = float(np.mean([arm_mse[n] for n in nets]))
    ratio = panel_arm / panel_base
    reduction = 1.0 - ratio

    panel_base_true = float(np.mean([base_true[n] for n in nets]))
    panel_arm_true = float(np.mean([arm_true[n] for n in nets]))
    reduction_true = 1.0 - panel_arm_true / panel_base_true

    per_net_red = {n: 1.0 - arm_mse[n] / base_mse[n] for n in nets}
    worst_net_red = float(min(per_net_red.values()))

    # Paired bootstrap over rotation seeds within each net.
    rng = np.random.default_rng(BOOT_RNG_SEED)
    reds = np.empty(BOOTSTRAP)
    for b in range(BOOTSTRAP):
        num = den = 0.0
        for n in nets:
            idx = rng.integers(0, REPLICATES, size=REPLICATES)
            den += per_net_mse(base_finals[n][idx], truths[n])
            num += per_net_mse(arm_finals[n][idx], truths[n])
        reds[b] = 1.0 - num / den
    ci = (float(np.percentile(reds, 2.5)), float(np.percentile(reds, 97.5)))

    worst_billed = max(int(billed[n].max()) for n in nets)
    return {
        "panel_mse_baseline": panel_base,
        "panel_mse_arm": panel_arm,
        "mse_ratio": ratio,
        "reduction": reduction,
        "reduction_ci95": ci,
        "reduction_true_mse_diag": reduction_true,
        "per_net_mse_baseline": base_mse,
        "per_net_mse_arm": arm_mse,
        "per_net_reduction": per_net_red,
        "worst_net_reduction": worst_net_red,
        "billed_worstcase_flops": worst_billed,
        "billed_worstcase_frac_B": worst_billed / B,
        "billed_mean_frac_B": float(np.mean([billed[n].mean() for n in nets])) / B,
    }


def summarize_wide(arm_mse_by_net, base_mse_by_net, billed_by_net):
    """Panel-MSE ratio + bootstrap CI over 80 nets; worst-decile reduction."""
    seeds = [s for s in WIDE_SEEDS if s in arm_mse_by_net]
    base = np.array([base_mse_by_net[s] for s in seeds])
    arm = np.array([arm_mse_by_net[s] for s in seeds])
    panel_base = float(base.mean())
    panel_arm = float(arm.mean())
    ratio = panel_arm / panel_base
    reduction = 1.0 - ratio
    per_net_red = 1.0 - arm / base
    k = max(1, len(seeds) // 10)                       # worst decile (8 of 80)
    worst_decile_red = float(np.sort(per_net_red)[:k].mean())

    rng = np.random.default_rng(BOOT_RNG_SEED + 1)
    reds = np.empty(BOOTSTRAP)
    m = len(seeds)
    for b in range(BOOTSTRAP):
        idx = rng.integers(0, m, size=m)
        reds[b] = 1.0 - arm[idx].sum() / base[idx].sum()
    ci = (float(np.percentile(reds, 2.5)), float(np.percentile(reds, 97.5)))
    worst_billed = max(billed_by_net[s] for s in seeds)
    return {
        "n_nets": len(seeds),
        "panel_mse_baseline": panel_base,
        "panel_mse_arm": panel_arm,
        "mse_ratio": ratio,
        "reduction": reduction,
        "reduction_ci95": ci,
        "worst_decile_reduction": worst_decile_red,
        "billed_worstcase_flops": worst_billed,
        "billed_worstcase_frac_B": worst_billed / B,
    }


def verdict_for(reduction, ci, worst_tail_red, billed_frac):
    """Apply the predeclared gates.  billed cap dominates."""
    if billed_frac > CAP_FRAC:
        return ("KILL_FLOPS",
                f"worst-case billed {billed_frac:.3f} B > {CAP_FRAC} B (A4)")
    if reduction < KILL_RED:
        return ("KILL",
                f"panel-MSE reduction {reduction:.3f} < {KILL_RED}")
    ci_excludes_10 = ci[0] > KILL_RED
    if (reduction >= PROMOTE_RED and ci_excludes_10
            and worst_tail_red >= PROMOTE_TAIL):
        return ("PROMOTE",
                f"reduction {reduction:.3f} >= {PROMOTE_RED}, CI lo {ci[0]:.3f} "
                f"> {KILL_RED}, tail {worst_tail_red:.3f} >= {PROMOTE_TAIL}")
    return ("SURVIVE_NO_PROMOTE",
            f"reduction {reduction:.3f} in [{KILL_RED},{PROMOTE_RED}) or "
            f"CI lo {ci[0]:.3f}/tail {worst_tail_red:.3f} short of promote")


# --------------------------------------------------------------- panel loaders
def load_primary_truth():
    truths, noises, truth_wall = {}, {}, {}
    for n in PRIMARY_SEEDS:
        d = np.load(M181 / f"m181_truth_net{n}.npz")
        truths[n] = np.asarray(d["means"], dtype=np.float64)
        noises[n] = float(d["noise_final"])
        truth_wall[n] = float(d["wall_s"])
        d.close()
    return truths, noises, truth_wall


def load_wide_baseline():
    """Cached frozen-v3 baseline on the 80-net wide panel: truth31 + pred31."""
    ck = json.loads(M185_CKPT.read_text())
    nets = ck["nets"]
    truth31, base_mse, base_billed = {}, {}, {}
    for s in WIDE_SEEDS:
        rec = nets.get(str(s))
        if rec is None or "truth31" not in rec or "pred31" not in rec:
            continue
        t = np.array(rec["truth31"], dtype=np.float64)
        p = np.array(rec["pred31"], dtype=np.float64)
        truth31[s] = t
        base_mse[s] = float(((p - t) ** 2).mean())
        base_billed[s] = int(rec["billed_flops"])
        # second signal: recomputed baseline MSE must match stored mse_raw.
        if abs(base_mse[s] - float(rec["mse_raw"])) > 1e-12 + 1e-6 * float(rec["mse_raw"]):
            raise RuntimeError(
                f"wide baseline mse mismatch net {s}: "
                f"recomputed {base_mse[s]:.6e} vs stored {rec['mse_raw']:.6e}")
    return truth31, base_mse, base_billed


# ------------------------------------------------------------- estimator runs
def run_primary(cls, truths):
    """Run one estimator over 3 nets x 16 reps.  Returns finals, billed, wall."""
    finals, billed = {}, {}
    t0 = time.perf_counter()
    for n in PRIMARY_SEEDS:
        wf = [fnp.asarray(w) for w in he_weights(n)]
        est = _new_estimator(cls)
        fs = np.empty((REPLICATES, WIDTH))
        bl = np.empty(REPLICATES, dtype=np.int64)
        for r in range(REPLICATES):
            fm, fb = predict_final(est, wf, n, r)
            fs[r] = fm
            bl[r] = fb
        finals[n] = fs
        billed[n] = bl
        print(f"    net {n}: 16 reps done, mse={per_net_mse(fs, truths[n]):.4e}, "
              f"billed_max_fracB={bl.max()/B:.4f}", flush=True)
    return finals, billed, time.perf_counter() - t0


def run_wide(cls, truth31):
    """Run one estimator over the 80 wide nets at r=0.  MSE vs cached truth31."""
    arm_mse, billed = {}, {}
    t0 = time.perf_counter()
    for i, s in enumerate(sorted(truth31)):
        wf = [fnp.asarray(w) for w in he_weights(s)]
        est = _new_estimator(cls)
        fm, fb = predict_final(est, wf, s, 0)
        arm_mse[s] = float(((fm - truth31[s]) ** 2).mean())
        billed[s] = fb
        if (i + 1) % 20 == 0:
            print(f"    wide {i+1}/{len(truth31)} done", flush=True)
    return arm_mse, billed, time.perf_counter() - t0


# ------------------------------------------------------------------------ main
def main():
    out_path = HERE / "pb1_results.json"
    results = {
        "date": "2026-08-08",
        "predeclaration": "PB1_SPEC_AND_CROSSES.md",
        "baseline": {"on_alpha": 3.0, "dead_alpha": -2.0, "estimator": "frozen v3"},
        "constants": {
            "B": B, "cap_frac": CAP_FRAC, "primary_seeds": list(PRIMARY_SEEDS),
            "replicates": REPLICATES, "wide_seeds": "1000..1079",
            "bootstrap_draws": BOOTSTRAP, "rotation_seed_formula": "900000+net*1000+r",
            "kill_reduction": KILL_RED, "promote_reduction": PROMOTE_RED,
            "promote_tail": PROMOTE_TAIL,
            "governing_metric": "raw measured panel-MSE reduction (primary 3-net)",
        },
        "firewall": (
            "synthetic He nets; frozen v3 read-only; cached truths & m185 "
            "checkpoint read-only; no dataset/scorer/submission; writes in pb1 dir"
        ),
        "arms": {},
        "acceleration": {},
        "notes": [],
    }

    def flush():
        out_path.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n",
                            encoding="utf-8")

    print("== PB-1 Premise Battery ==", flush=True)
    print("loading cached truths (primary 3.5M + wide checkpoint)...", flush=True)
    truths, noises, truth_wall = load_primary_truth()
    truth31, wide_base_mse, wide_base_billed = load_wide_baseline()
    print(f"primary truth cached (avoided wall ~{sum(truth_wall.values()):.0f}s); "
          f"wide baseline cached for {len(truth31)} nets "
          f"(mse_raw cross-checked ok)", flush=True)
    results["acceleration"]["primary_truth_cached_wall_s"] = sum(truth_wall.values())
    results["acceleration"]["wide_nets_cached"] = len(truth31)

    # ---- baseline (frozen v3), run ONCE, primary + wide-billing reference.
    print("\n[baseline v3] primary panel (amortized once)...", flush=True)
    base_finals, base_billed, base_wall = run_primary(KerdockV3, truths)
    results["acceleration"]["baseline_primary_wall_s"] = round(base_wall, 1)
    base_worst_frac = max(int(base_billed[n].max()) for n in PRIMARY_SEEDS) / B
    results["arms"]["baseline_v3"] = {
        "dials": {"on_alpha": 3.0, "dead_alpha": -2.0},
        "primary": {
            "panel_mse": float(np.mean([per_net_mse(base_finals[n], truths[n])
                                        for n in PRIMARY_SEEDS])),
            "per_net_mse": {str(n): per_net_mse(base_finals[n], truths[n])
                            for n in PRIMARY_SEEDS},
            "billed_worstcase_frac_B": base_worst_frac,
        },
        "verdict": "BASELINE",
    }
    flush()
    print(f"[baseline v3] wall={base_wall:.1f}s "
          f"panel_mse={results['arms']['baseline_v3']['primary']['panel_mse']:.4e} "
          f"billed_worst_fracB={base_worst_frac:.4f}", flush=True)

    arm_walls = []
    promoted_m188 = promoted_m189 = False
    best_on = None   # (name, reduction) among M188 survivors for M190
    best_dead = None

    def evaluate_arm(name, dials, is_m190=False):
        nonlocal promoted_m188, promoted_m189, best_on, best_dead
        print(f"\n[{name}] dials={dials} ...", flush=True)
        cls = make_arm(**dials)
        finals, billed, wall = run_primary(cls, truths)
        arm_walls.append(wall)
        prim = summarize_primary(finals, base_finals, truths, noises, billed)
        v, why = verdict_for(prim["reduction"], prim["reduction_ci95"],
                             prim["worst_net_reduction"],
                             prim["billed_worstcase_frac_B"])
        rec = {"dials": dials, "primary": prim, "primary_wall_s": round(wall, 1),
               "verdict": v, "verdict_reason": why}
        # Wide panel (secondary, caveated) -- only if not already KILL_FLOPS.
        if v != "KILL_FLOPS":
            wmse, wbilled, wwall = run_wide(cls, truth31)
            wide = summarize_wide(wmse, wide_base_mse, wbilled)
            wide_frac = wide["billed_worstcase_frac_B"]
            wv, wwhy = verdict_for(wide["reduction"], wide["reduction_ci95"],
                                   wide["worst_decile_reduction"], wide_frac)
            wide["verdict_secondary"] = wv
            wide["verdict_reason"] = wwhy
            wide["caveat"] = ("300k-600k-sample truth floor ~6e-8; single "
                              "rotation seed r=0; secondary to the primary gate")
            rec["wide"] = wide
            rec["wide_wall_s"] = round(wwall, 1)
        results["arms"][name] = rec
        flush()
        print(f"[{name}] VERDICT={v} :: {why}", flush=True)
        print(f"    reduction={prim['reduction']:.3f} "
              f"CI=[{prim['reduction_ci95'][0]:.3f},{prim['reduction_ci95'][1]:.3f}] "
              f"worst_net={prim['worst_net_reduction']:.3f} "
              f"billed_worst_fracB={prim['billed_worstcase_frac_B']:.4f}", flush=True)
        # Track promotions for the M190 interaction gate.
        if v == "PROMOTE":
            if name.startswith("M188"):
                promoted_m188 = True
                if best_on is None or prim["reduction"] > best_on[1]:
                    best_on = (dials.get("on_alpha"), prim["reduction"])
            elif name.startswith("M189"):
                promoted_m189 = True
                if best_dead is None or prim["reduction"] > best_dead[1]:
                    best_dead = (dials.get("dead_alpha"), prim["reduction"])
        return rec

    for name, dials in ARMS_M188 + ARMS_M189:
        evaluate_arm(name, dials)

    # ---- M190: joint best-on x best-dead, ONLY if both families promoted alone.
    if promoted_m188 and promoted_m189:
        dials = {"on_alpha": best_on[0], "dead_alpha": best_dead[0]}
        print(f"\nM190 gate OPEN: M188 and M189 each promoted alone; "
              f"running joint {dials}", flush=True)
        evaluate_arm("M190_joint", dials, is_m190=True)
        results["notes"].append(
            f"M190 ran: joint {dials} (both families promoted alone).")
    else:
        msg = (f"M190 SKIPPED: interaction gate closed "
               f"(M188 promoted alone={promoted_m188}, "
               f"M189 promoted alone={promoted_m189}); "
               f"the spec requires >=1 promotion from EACH family.")
        print("\n" + msg, flush=True)
        results["notes"].append(msg)

    # ---- acceleration accounting.
    marginal = float(np.mean(arm_walls)) if arm_walls else 0.0
    from_scratch = (sum(truth_wall.values()) + base_wall + marginal)
    results["acceleration"].update({
        "battery_marginal_per_arm_wall_s": round(marginal, 1),
        "from_scratch_one_mechanism_wall_s": round(from_scratch, 1),
        "acceleration_factor": round(from_scratch / marginal, 2) if marginal else None,
        "note": ("from-scratch mechanism = recompute 3x3.5M truth + replicate "
                 "baseline + run arm; battery marginal = arm predicts only "
                 "(truth & baseline amortized)."),
    })
    flush()

    n_prom = sum(1 for a in results["arms"].values()
                 if a.get("verdict") == "PROMOTE")
    print(f"\n== DONE == arms={len(results['arms'])-1} promotions={n_prom} "
          f"acceleration~{results['acceleration']['acceleration_factor']}x", flush=True)
    print(f"results -> {out_path}", flush=True)


if __name__ == "__main__":
    main()
