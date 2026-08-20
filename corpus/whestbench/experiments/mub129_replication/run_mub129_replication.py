"""M-MUB129-R: higher-power replication of the 126 -> 129 frame completion.

Gate predeclared in PREDECLARATION.md, committed 4b23f37 before this file
existed.  Structure copied from experiments/mub129_completion/run_mub129.py
(commit 5ba99f1), which is sealed and untouched.

Truth-free by construction: a randomly rotated equal-weight design is exactly
unbiased under Haar, so MSE == Var over rotation draws.  No truth read, no
scorer read, no holdout, no challenge network.

K1   kill unless geomean_k (V129_k/V126_k) < 126/129 = 0.9767441860465116
K1b  kill if the 97.5th percentile of the paired bootstrap on the geomean
     SCORE ratio is >= 1.0
K2   structural preconditions on the frozen archive
K3   no post-result change to the bar, K, R, the seed bases, B, or the
     percentiles

DEVIATION LOG (loud, top of file, per harness discipline)
---------------------------------------------------------
D1  Commit 4b23f37, which was supposed to carry PREDECLARATION.md alone, also
    carried a foreign staged file, corpus/whestbench/core/
    PHASE1_WRITEUP_DRAFT_20260808.md (+18/-3).  A concurrent agent staged that
    file in the shared index between this agent's `git status` (clean) and its
    `git add <one path>` + `git commit`; plain `git commit` commits the whole
    index, so the foreign hunk rode along.  NOTHING WAS LOST: `git diff HEAD`
    on that path is empty, the other agent's content is intact in the working
    tree and now also in HEAD.  Not repaired by `git reset`, which the task
    forbids outright and which would also clobber the other agent's index
    state.  All later commits in this experiment use `git commit -o <paths>`,
    which commits only the named paths regardless of the rest of the index.

Resumability: this runner checkpoints one JSON per network under partial/ and
exits when its wall budget is spent.  Re-running it resumes.  No seed and no
count depends on how the work is split, because every seed is a pure function
of (k, r) fixed in the predeclaration.
"""

from __future__ import annotations

import json
import statistics
import sys
import time
from fractions import Fraction
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ARCHIVE = HERE.parents[1] / "experiments" / "v31_guards" / "package_source" / "kerdock_phases.npz"
PARTIAL = HERE / "partial"

D = 256
DEPTH = 32
N_NETS = 16                        # predeclared
N_ROT = 24                         # predeclared
DEPLOYED_SLICE = (2, 128)          # kerdock_v3_estimator.py:51-52
COST_RATIO = Fraction(129, 126)
K1_BAR = float(Fraction(126, 129))  # 0.9767441860465116
MEAN_CHI_256 = 15.98438266660852747

NET_SEED_BASE = 31415926           # predeclared, distinct from the original's 20260812
ROT_SEED_BASE = 27182818           # predeclared, distinct from the original's 76543210
BOOT_SEED = 16180339               # predeclared
N_BOOT = 10000                     # predeclared
PCTL = (2.5, 97.5)                 # predeclared

ORIGINAL_POINT_ESTIMATE = 0.9370437357791304   # M-MUB129, commit 97f6ec8


def sylvester_hadamard(n: int) -> np.ndarray:
    h = np.ones((1, 1), dtype=np.int8)
    while h.shape[0] < n:
        h = np.block([[h, h], [h, -h]]).astype(np.int8)
    return h


def load_phases() -> np.ndarray:
    """Return the frozen phase sign matrix, exactly as the estimator unpacks it."""
    archive = np.load(str(ARCHIVE))
    packed = archive["negative_bits"]
    negative = np.unpackbits(packed, axis=1, bitorder="little")[:, :D]
    return (1.0 - 2.0 * negative.astype(np.float64)).astype(np.int8)


def check_mutual_unbiasedness(phases: np.ndarray, H: np.ndarray) -> dict:
    """Cross-frame Gram entries are (1/256)*(H @ (phi_s*phi_t))[i^j].

    Mutual unbiasedness <=> every phi_s*phi_t is bent, i.e. |H @ psi| == 16
    everywhere.  The standard basis is unbiased against every H diag(phi) frame
    identically, so it needs no test.
    """
    n = phases.shape[0]
    Hf = H.astype(np.float64)
    bad_pairs, spectra = [], set()
    for s in range(n):
        prods = (phases[s].astype(np.int16) * phases[s + 1:].astype(np.int16)).astype(np.float64)
        if prods.size == 0:
            continue
        w = prods @ Hf.T
        mag = np.abs(w)
        spectra.update(np.unique(mag).tolist())
        off = np.where(np.any(mag != 16.0, axis=1))[0]
        for k in off.tolist():
            bad_pairs.append((s, s + 1 + k, float(mag[k].min()), float(mag[k].max())))
    return {
        "n_frames_in_archive": int(n),
        "pairs_tested": int(n * (n - 1) // 2),
        "distinct_walsh_magnitudes": sorted(spectra)[:8],
        "non_unbiased_pairs": bad_pairs[:20],
        "all_pairwise_unbiased": len(bad_pairs) == 0,
    }


def degree4_moment_exact(m: int) -> dict:
    """Exact rational degree-4 moment identity for m antipodally doubled MUBs."""
    actual = Fraction(2) + Fraction(m - 1, 128)
    required = Fraction(3 * 512 * m, D * (D + 2))
    return {
        "m": m,
        "n_points": 512 * m,
        "sum_ip4_actual": str(actual),
        "sum_ip4_required": str(required),
        "exact_match": actual == required,
        "dgs_antipodal_4design_floor": 2 * (257 * 256 // 2),
        "clears_dgs_floor": 512 * m >= 2 * (257 * 256 // 2),
    }


def build_directions(phases: np.ndarray, H: np.ndarray) -> np.ndarray:
    """(m, 256, 256) unit directions.  Frame 0 is the standard basis.

    u[s,i,:] = (1/16) * H[i,:] * phi_{s-1}  for s >= 1, matching
    kerdock_v3_estimator.py:103-132.
    """
    n = phases.shape[0]
    out = np.empty((n + 1, D, D), dtype=np.float32)
    out[0] = np.eye(D, dtype=np.float32)
    Hf = H.astype(np.float32) / 16.0
    for s in range(n):
        out[s + 1] = Hf * phases[s].astype(np.float32)[None, :]
    return out


def he_network(seed: int) -> list[np.ndarray]:
    rng = np.random.default_rng(seed)
    sigma = np.sqrt(2.0 / D)
    return [rng.normal(0.0, sigma, size=(D, D)).astype(np.float32) for _ in range(DEPTH)]


def haar(seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    a = rng.normal(size=(D, D))
    q, r = np.linalg.qr(a)
    q *= np.sign(np.diag(r))
    return q.astype(np.float32)


def frame_means(dirs: np.ndarray, weights: list[np.ndarray]) -> np.ndarray:
    """Per-frame mean of the depth-32 post-ReLU activation, antipodally paired.

    ONE shared forward pass over all 129 frames; both the 126- and the
    129-frame estimates are formed from these same per-frame means.
    Returns (m, 256).
    """
    m = dirs.shape[0]
    x = dirs.reshape(m * D, D) * np.float32(MEAN_CHI_256)
    pre = x @ weights[0]
    act = np.concatenate([np.maximum(pre, 0.0), np.maximum(-pre, 0.0)], axis=0)
    del pre, x
    for w in weights[1:]:
        act = np.maximum(act @ w, 0.0)
    half = act.reshape(2, m, D, D)
    return half.mean(axis=(0, 2))


def var_independent(q: np.ndarray) -> float:
    """C1 cross-check: mean-over-neurons sample variance via pure-Python
    statistics.variance, sharing no code path with numpy.var."""
    cols = q.T.tolist()          # 256 neurons x R rotations, Python floats
    return statistics.fmean(statistics.variance(c) for c in cols)


def run_one_net(k: int, dirs: np.ndarray, idx126: np.ndarray, idx129: np.ndarray,
                t0: float) -> dict:
    w = he_network(NET_SEED_BASE + k)
    q126, q129 = [], []
    keep = None
    for r in range(N_ROT):
        rot = haar(ROT_SEED_BASE + 1000 * k + r)
        wr = [rot.T @ w[0]] + w[1:]
        fm = frame_means(dirs, wr)
        v126 = fm[idx126].mean(axis=0)
        v129 = fm[idx129].mean(axis=0)
        if k == 0 and r == 0:
            keep = np.asarray(v129, dtype=np.float64)
        q126.append(v126)
        q129.append(v129)
        print(f"  net {k:2d} rot {r:2d}  t={time.time() - t0:7.1f}s", flush=True)
    q126 = np.asarray(q126, dtype=np.float64)
    q129 = np.asarray(q129, dtype=np.float64)
    V126 = float(q126.var(axis=0, ddof=1).mean())
    V129 = float(q129.var(axis=0, ddof=1).mean())
    a126 = var_independent(q126)
    a129 = var_independent(q129)
    rec = {
        "net": k,
        "net_seed": NET_SEED_BASE + k,
        "rot_seeds": [ROT_SEED_BASE + 1000 * k + r for r in range(N_ROT)],
        "V126": V126,
        "V129": V129,
        "ratio": V129 / V126,
        "score_ratio": (V129 / V126) * float(COST_RATIO),
        "mean_level": float(q126.mean()),
        "c1_V126_independent": a126,
        "c1_V129_independent": a129,
        "c1_rel_dev_126": abs(a126 - V126) / V126,
        "c1_rel_dev_129": abs(a129 - V129) / V129,
    }
    rec["c1_pass"] = bool(rec["c1_rel_dev_126"] < 1e-10 and rec["c1_rel_dev_129"] < 1e-10)
    if keep is not None:
        rec["c2_cached_q129_net0_rot0"] = keep.tolist()
    return rec


def bootstrap(scores: np.ndarray) -> dict:
    """Paired bootstrap over networks, exactly as predeclared: B=10000
    resamples of the per-network log score ratios, 2.5/97.5 percentiles."""
    rng = np.random.default_rng(BOOT_SEED)
    logs = np.log(scores)
    idx = rng.integers(0, logs.size, size=(N_BOOT, logs.size))
    boot = np.exp(logs[idx].mean(axis=1))
    lo, hi = np.percentile(boot, list(PCTL))
    return {
        "n_boot": N_BOOT,
        "seed": BOOT_SEED,
        "percentiles": list(PCTL),
        "ci_lo": float(lo),
        "ci_hi": float(hi),
        "boot_median": float(np.median(boot)),
        "frac_boot_at_or_above_1": float(np.mean(boot >= 1.0)),
    }


def main() -> None:
    t0 = time.time()
    budget = float(sys.argv[1]) if len(sys.argv) > 1 else 420.0
    PARTIAL.mkdir(exist_ok=True)

    H = sylvester_hadamard(D)
    phases = load_phases()
    struct = check_mutual_unbiasedness(phases, H)
    n_arch = struct["n_frames_in_archive"]
    moments = {m: degree4_moment_exact(m) for m in (126, 128, 129)}

    k2_fail = []
    if n_arch < 128:
        k2_fail.append(f"archive holds {n_arch} phase rows, need >= 128")
    if not struct["all_pairwise_unbiased"]:
        k2_fail.append("candidate frames are not pairwise mutually unbiased")
    if not moments[129]["exact_match"]:
        k2_fail.append("129-frame set fails the degree-4 moment identity")

    receipt = {
        "experiment": "M-MUB129-R",
        "replicates": "M-MUB129 (predeclaration be3eb44, result 97f6ec8)",
        "predeclaration_commit": "4b23f37",
        "n_nets": N_NETS,
        "n_rot": N_ROT,
        "net_seed_base": NET_SEED_BASE,
        "rot_seed_base": ROT_SEED_BASE,
        "k1_bar_v129_over_v126": K1_BAR,
        "cost_ratio": str(COST_RATIO),
        "original_point_estimate_score_ratio": ORIGINAL_POINT_ESTIMATE,
        "structural": struct,
        "degree4_moment": moments,
        "k2_failures": k2_fail,
        "deviations": [
            "D1: commit 4b23f37 (intended: predeclaration alone) also carried a "
            "foreign staged file corpus/whestbench/core/PHASE1_WRITEUP_DRAFT_20260808.md "
            "(+18/-3), staged by a concurrent agent between this agent's status check "
            "and its commit. No content was lost (git diff HEAD on that path is empty). "
            "Not repaired by reset, which the task forbids. Later commits use "
            "`git commit -o <paths>`."
        ],
    }

    if k2_fail:
        receipt["verdict"] = "KILLED_K2_STRUCTURAL"
        (HERE / "RESULTS.json").write_text(json.dumps(receipt, indent=2))
        print(json.dumps(receipt, indent=2))
        return

    dirs = build_directions(phases, H)
    lo, hi = DEPLOYED_SLICE
    idx126 = np.arange(lo + 1, hi + 1)        # +1 for the standard basis at row 0
    idx129 = np.arange(dirs.shape[0])
    assert idx126.size == 126 and idx129.size == 129, (idx126.size, idx129.size)

    for k in range(N_NETS):
        cp = PARTIAL / f"net_{k:02d}.json"
        if cp.exists():
            continue
        rec = run_one_net(k, dirs, idx126, idx129, t0)
        cp.write_text(json.dumps(rec))
        print(f"net {k:2d}: V126={rec['V126']:.6e} V129={rec['V129']:.6e} "
              f"ratio={rec['ratio']:.6f} score={rec['score_ratio']:.6f} "
              f"c1_pass={rec['c1_pass']}", flush=True)
        if time.time() - t0 > budget:
            done = len(list(PARTIAL.glob("net_*.json")))
            print(f"PARTIAL: {done}/{N_NETS} networks checkpointed, budget spent "
                  f"({time.time() - t0:.1f}s). Re-run to resume.", flush=True)
            return

    per_net = [json.loads((PARTIAL / f"net_{k:02d}.json").read_text()) for k in range(N_NETS)]

    # C2: bitwise repeat of net 0 / rotation 0 from freshly built weights.
    cached = np.asarray(per_net[0].pop("c2_cached_q129_net0_rot0"), dtype=np.float64)
    w0 = he_network(NET_SEED_BASE + 0)
    rot0 = haar(ROT_SEED_BASE + 0)
    fm0 = frame_means(dirs, [rot0.T @ w0[0]] + w0[1:])
    repeat = np.asarray(fm0[idx129].mean(axis=0), dtype=np.float64)
    c2 = {
        "bitwise_identical": bool(np.array_equal(repeat, cached)),
        "max_abs_diff": float(np.max(np.abs(repeat - cached))),
        "n_elements": int(repeat.size),
    }

    ratios = np.array([p["ratio"] for p in per_net])
    scores = np.array([p["score_ratio"] for p in per_net])
    geo = float(np.exp(np.log(ratios).mean()))
    score = geo * float(COST_RATIO)
    ci = bootstrap(scores)

    k1 = bool(score >= 1.0)
    k1b = bool(ci["ci_hi"] >= 1.0)
    if k1:
        verdict = "KILLED_K1_COMPLETION_DOES_NOT_PAY"
    elif k1b:
        verdict = "KILLED_K1B_INTERVAL_TOUCHES_BREAKEVEN"
    else:
        verdict = "SURVIVES_K1_AND_INTERVAL"

    receipt["per_net"] = per_net
    receipt["per_net_score_ratios_raw"] = [float(s) for s in scores]
    receipt["per_net_variance_ratios_raw"] = [float(r) for r in ratios]
    receipt["n_nets_individually_below_1"] = int(np.sum(scores < 1.0))
    receipt["geomean_variance_ratio"] = geo
    receipt["geomean_score_ratio"] = score
    receipt["variance_removed_pct"] = (1.0 - geo) * 100.0
    receipt["bootstrap"] = ci
    receipt["original_estimate_inside_ci"] = bool(
        ci["ci_lo"] <= ORIGINAL_POINT_ESTIMATE <= ci["ci_hi"])
    receipt["c1_all_pass"] = bool(all(p["c1_pass"] for p in per_net))
    receipt["c1_max_rel_dev"] = float(max(
        max(p["c1_rel_dev_126"], p["c1_rel_dev_129"]) for p in per_net))
    receipt["c2_bitwise_repeat"] = c2
    receipt["k1_fires"] = k1
    receipt["k1b_fires"] = k1b
    receipt["verdict"] = verdict
    receipt["wall_seconds_final_invocation"] = time.time() - t0

    (HERE / "RESULTS.json").write_text(json.dumps(receipt, indent=2))
    slim = {k: v for k, v in receipt.items() if k not in ("structural", "per_net")}
    print(json.dumps(slim, indent=2))


if __name__ == "__main__":
    main()
