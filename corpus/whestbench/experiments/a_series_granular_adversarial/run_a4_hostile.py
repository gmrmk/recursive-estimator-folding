"""A4 hostile-inputs battery on the frozen champion (v3 Kerdock fold3).

Predeclared in A_SERIES_PREDECLARATION.md section A4 (governs). The frozen
v3 estimator is INVOKED ONLY (subclass/instantiate, never edited), with the
run_n8c_g0.py invocation pattern, on hostile synthetic nets (width 256,
depth 32, one net each):

  (a) He gain x 1e-3          near-zero scale (deep underflow by depth 32)
  (b) He gain x 1e3           overflow-range f32
  (c) t_3 heavy-tailed        entries rescaled to He variance
  (d) rank-32 weights         low rank (32 of 256)
  (e) correlated columns      pairwise column correlation rho = 0.95
  (f) all-negative-shifted    every entry - 3/sqrt(256) (rescue storm)
  (g) He gain x 1e-38         f32 denormal-range weights
  (h) determinism             SAME normal net, two separate subprocesses,
                              bitwise-equal predictions required

Per input: completes? / prediction finite? / MSE vs a 200k iid MC truth /
wall seconds / billed FLOPs vs the real 2.72e11 budget (BudgetContext at
the REAL budget so a breach raises BudgetExhaustedError -- a breach IS a
finding) / any exception.

Verdict per input: OK / DEGRADED (finite but MSE >> normal: mse_final >
100 x max(matched-n MC reference MSE, truth noise floor, 1e-30)) /
FAILURE (exception, non-finite prediction, budget breach, or wall > 60s).

Deviations declared loudly:
  - SetupContext api_version='2.0' (task-specified; run_n8c_g0.py used
    'synthetic').  The frozen estimator does not branch on api_version.
  - Truth is 200k MC (task-specified) vs n8c's 3.5M: truth noise floor is
    ~17.5x higher (~2e-7 on He nets), so absolute MSEs vs this truth sit
    near the noise floor on healthy nets; the DEGRADED rule uses the
    per-net matched-n MC reference and noise floor, not raw MSE.

Firewall: synthetic nets only; frozen v3 sources imported read-only
(bytecode writes disabled); only its shipped assets loaded by its own
setup; no dataset/truth/scorer/submission access; writes confined to the
a_series_granular_adversarial directory.
"""

from __future__ import annotations

import json
import math
import subprocess
import sys
import time
import traceback
from pathlib import Path

sys.dont_write_bytecode = True

import numpy as np

HERE = Path(__file__).resolve().parent
V3_DIR = Path(
    r"C:\Users\strid\Documents\Codex\2026-08-02"
    r"\https-chatgpt-com-share-6a5556ed-2e1c\work\scorefloor_generation"
    r"\kerdock_l1_owned_buffer\candidate_source_validator_v3"
)
sys.path.insert(0, str(V3_DIR))

import flopscope as flops            # noqa: E402
import flopscope.numpy as fnp        # noqa: E402
from whestbench import SetupContext  # noqa: E402
from whestbench.domain import MLP    # noqa: E402

flops.configure(symmetry_warnings=False)

from estimator import Estimator as KerdockV3  # noqa: E402  (frozen v3)

WIDTH, DEPTH = 256, 32
BUDGET = int(2.72e11)                # the REAL competition budget
N_TRUTH = 200_000
TRUTH_CHUNK = 65_536
N_MC_REF = 64_512                    # matched to the estimator's sample count
WALL_LIMIT_S = 60.0
GAIN = math.sqrt(2.0 / WIDTH)


# ------------------------------------------------------------ hostile nets
def build_net(kind: str) -> list[np.ndarray]:
    rng = np.random.default_rng(101 if kind in ("normal", "det") else
                                abs(hash(kind)) % 2**31)
    if kind in ("normal", "det"):
        return [rng.standard_normal((WIDTH, WIDTH), dtype=np.float32)
                * np.float32(GAIN) for _ in range(DEPTH)]
    rng = np.random.default_rng(4400 + "abcdefg".index(kind[0]))
    ws = []
    for _ in range(DEPTH):
        if kind == "a_gain_1e-3":
            w = rng.standard_normal((WIDTH, WIDTH)) * (GAIN * 1e-3)
        elif kind == "b_gain_1e3":
            w = rng.standard_normal((WIDTH, WIDTH)) * (GAIN * 1e3)
        elif kind == "c_t3_heavy":
            w = rng.standard_t(3, size=(WIDTH, WIDTH)) / math.sqrt(3.0) * GAIN
        elif kind == "d_rank32":
            a = rng.standard_normal((WIDTH, 32))
            b = rng.standard_normal((32, WIDTH))
            w = (a @ b) * (GAIN / math.sqrt(32.0))
        elif kind == "e_corr_rho095":
            c = rng.standard_normal((WIDTH, 1))
            z = rng.standard_normal((WIDTH, WIDTH))
            w = (math.sqrt(0.95) * c + math.sqrt(0.05) * z) * GAIN
        elif kind == "f_negshift":
            w = rng.standard_normal((WIDTH, WIDTH)) * GAIN - 3.0 / 16.0
        elif kind == "g_gain_1e-38":
            w = rng.standard_normal((WIDTH, WIDTH)) * (GAIN * 1e-38)
        else:
            raise ValueError(kind)
        ws.append(w.astype(np.float32))
    return ws


# ------------------------------------------------------------------ truth
def truth_final(weights: list[np.ndarray], seed: int) -> dict:
    sums = np.zeros(WIDTH)
    sumsq = np.zeros(WIDTH)
    done = 0
    t0 = time.perf_counter()
    rng = np.random.default_rng(seed)
    with np.errstate(over="ignore", invalid="ignore"):
        while done < N_TRUTH:
            m = min(TRUTH_CHUNK, N_TRUTH - done)
            act = rng.standard_normal((m, WIDTH)).astype(np.float32)
            for w in weights:
                act = np.maximum(act @ w, np.float32(0.0))
            a64 = act.astype(np.float64)
            sums += a64.sum(axis=0)
            sumsq += (a64 * a64).sum(axis=0)
            done += m
    means = sums / N_TRUTH
    per_sample_var = sumsq / N_TRUTH - means * means
    return {
        "means": means,
        "noise": float(np.nanmean(per_sample_var) / N_TRUTH),
        "finite": bool(np.isfinite(means).all()),
        "wall_s": round(time.perf_counter() - t0, 1),
    }


def mc_reference_mse(weights: list[np.ndarray], truth: np.ndarray,
                     seed: int) -> float:
    """Matched-n iid MC forward mean: the 'honest cheap estimator' anchor."""
    rng = np.random.default_rng(seed)
    sums = np.zeros(WIDTH)
    with np.errstate(over="ignore", invalid="ignore"):
        act = rng.standard_normal((N_MC_REF, WIDTH)).astype(np.float32)
        for w in weights:
            act = np.maximum(act @ w, np.float32(0.0))
        sums = act.astype(np.float64).mean(axis=0)
    return float(np.mean((sums - truth) ** 2))


# ------------------------------------------------------- estimator harness
def run_v3(weights_np: list[np.ndarray], mlp_seed: int, name: str) -> dict:
    weights_f = [fnp.asarray(w) for w in weights_np]
    est = KerdockV3()
    est.setup(SetupContext(
        width=WIDTH, depth=DEPTH, flop_budget=BUDGET,
        api_version="2.0", seed=0, submission_dir=str(V3_DIR),
    ))
    mlp = MLP(width=WIDTH, depth=DEPTH, weights=weights_f,
              seed=mlp_seed, name=name)
    mlp.validate()
    out = None
    exc = None
    ctx = flops.BudgetContext(BUDGET, quiet=True)
    t0 = time.perf_counter()
    try:
        with ctx:
            out = est.predict(mlp, BUDGET)
    except BaseException:
        exc = traceback.format_exc(limit=6)
    wall = time.perf_counter() - t0
    stack = None
    if out is not None:
        try:
            stack = np.asarray(out).astype(np.float64)
        except BaseException:
            exc = (exc or "") + "\n[conversion] " + traceback.format_exc(limit=3)
    return {
        "stack": stack,
        "billed": int(ctx.flops_used),
        "wall_s": wall,
        "exception": exc,
    }


# ---------------------------------------------------------- determinism (h)
def det_child(out_path: str) -> None:
    weights = build_net("det")
    r = run_v3(weights, mlp_seed=901_101, name="a4-det")
    if r["exception"] is not None or r["stack"] is None:
        print(r["exception"], file=sys.stderr)
        sys.exit(3)
    np.savez(out_path, stack=r["stack"], billed=r["billed"])
    sys.exit(0)


def det_check() -> dict:
    paths = [HERE / "a4_det_run1.npz", HERE / "a4_det_run2.npz"]
    walls = []
    for p in paths:
        if p.exists():
            p.unlink()
        t0 = time.perf_counter()
        proc = subprocess.run(
            [sys.executable, str(HERE / "run_a4_hostile.py"), "detrun", str(p)],
            capture_output=True, text=True, timeout=600,
        )
        walls.append(round(time.perf_counter() - t0, 1))
        if proc.returncode != 0:
            return {"verdict": "FAILURE",
                    "detail": f"subprocess rc={proc.returncode}: "
                              f"{proc.stderr[-2000:]}"}
    d1, d2 = (np.load(p) for p in paths)
    s1, s2 = d1["stack"], d2["stack"]
    bitwise = (s1.dtype == s2.dtype and s1.shape == s2.shape
               and s1.tobytes() == s2.tobytes())
    return {
        "verdict": "OK" if bitwise else "FAILURE",
        "bitwise_equal": bool(bitwise),
        "billed_equal": int(d1["billed"]) == int(d2["billed"]),
        "billed": [int(d1["billed"]), int(d2["billed"])],
        "max_abs_diff": float(np.max(np.abs(s1 - s2)))
        if s1.shape == s2.shape else None,
        "subprocess_walls_s": walls,
    }


# ------------------------------------------------------------------ main
HOSTILE = ["a_gain_1e-3", "b_gain_1e3", "c_t3_heavy", "d_rank32",
           "e_corr_rho095", "f_negshift", "g_gain_1e-38"]


def evaluate(kind: str, mlp_seed: int) -> dict:
    weights = build_net(kind)
    truth = truth_final(weights, seed=770_000 + mlp_seed)
    mc_ref = mc_reference_mse(weights, truth["means"], seed=880_000 + mlp_seed)
    r = run_v3(weights, mlp_seed=mlp_seed, name=f"a4-{kind}")
    row: dict = {
        "net": kind,
        "mlp_seed": mlp_seed,
        "completes": r["exception"] is None,
        "wall_s": round(r["wall_s"], 2),
        "billed_flops": r["billed"],
        "budget": BUDGET,
        "budget_breach": r["billed"] > BUDGET,
        "truth_finite": truth["finite"],
        "truth_noise_floor": truth["noise"],
        "truth_mean_sq": float(np.nanmean(truth["means"] ** 2)),
        "mc_reference_mse_final": mc_ref,
        "exception": r["exception"],
    }
    if r["stack"] is not None:
        final = r["stack"][-1]
        row["prediction_finite_final"] = bool(np.isfinite(final).all())
        row["prediction_finite_all_layers"] = bool(
            np.isfinite(r["stack"]).all())
        with np.errstate(invalid="ignore"):
            row["mse_final_vs_200k_truth"] = float(
                np.mean((final - truth["means"]) ** 2))
    else:
        row["prediction_finite_final"] = False
        row["prediction_finite_all_layers"] = False
        row["mse_final_vs_200k_truth"] = None

    if (not row["completes"] or not row["prediction_finite_final"]
            or row["budget_breach"] or row["wall_s"] > WALL_LIMIT_S):
        row["verdict"] = "FAILURE"
    else:
        mse = row["mse_final_vs_200k_truth"]
        bar = 100.0 * max(mc_ref if math.isfinite(mc_ref) else 0.0,
                          truth["noise"] if math.isfinite(truth["noise"])
                          else 0.0, 1e-30)
        row["degraded_bar"] = bar
        row["verdict"] = ("DEGRADED" if (mse is not None
                                         and math.isfinite(mse)
                                         and mse > bar) else "OK")
        if mse is not None and not math.isfinite(mse):
            # finite prediction but non-finite truth (e.g. overflow net):
            # MSE undefined; judged on finiteness + billing + wall only.
            row["verdict_note"] = ("truth non-finite; MSE undefined; "
                                   "verdict from finiteness/billing/wall")
    return row


def main() -> None:
    if len(sys.argv) > 2 and sys.argv[1] == "detrun":
        det_child(sys.argv[2])
        return

    results: dict = {
        "date": "2026-08-08",
        "predeclaration": "A_SERIES_PREDECLARATION.md section A4",
        "firewall": (
            "synthetic nets only; frozen v3 invoked read-only (bytecode "
            "writes disabled); only its shipped assets loaded by its own "
            "setup; no dataset/truth/scorer/submission; writes confined to "
            "a_series_granular_adversarial"
        ),
        "invocation": {
            "setup": ("SetupContext(width=256, depth=32, flop_budget="
                      "int(2.72e11), api_version='2.0', seed=0, "
                      "submission_dir=V3_DIR)"),
            "predict": "BudgetContext(int(2.72e11), quiet=True)",
            "deviation": ("api_version='2.0' per task spec; n8c used "
                          "'synthetic'; the frozen estimator ignores it"),
        },
        "rows": [],
    }

    # Baseline anchor: normal He net (seed 101, n8c rep-0 rotation seed).
    base = evaluate("normal", mlp_seed=901_101)
    base["role"] = "baseline anchor (He net 101, mlp.seed 901101 = n8c rep 0)"
    results["baseline"] = base
    print(f"baseline: verdict={base['verdict']} "
          f"mse={base['mse_final_vs_200k_truth']:.3e} "
          f"wall={base['wall_s']}s billed={base['billed_flops']:.3e}",
          flush=True)

    for i, kind in enumerate(HOSTILE):
        row = evaluate(kind, mlp_seed=555_001 + i)
        results["rows"].append(row)
        mse = row["mse_final_vs_200k_truth"]
        print(f"{kind}: verdict={row['verdict']} completes={row['completes']} "
              f"finite={row['prediction_finite_final']} "
              f"mse={mse if mse is None else format(mse, '.3e')} "
              f"wall={row['wall_s']}s billed={row['billed_flops']:.3e} "
              f"breach={row['budget_breach']}", flush=True)
        if row["exception"]:
            print(f"  exception (tail): {row['exception'][-300:]}", flush=True)

    det = det_check()
    results["determinism"] = det
    print(f"h_determinism: verdict={det['verdict']} "
          f"bitwise={det.get('bitwise_equal')}", flush=True)

    out_path = HERE / "a4_results.json"
    out_path.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    print(f"written {out_path}", flush=True)


if __name__ == "__main__":
    main()
