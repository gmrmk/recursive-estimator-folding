"""STEP 0 (arithmetic gate) for gm_p2b_proxy -- see PREDECLARATION.md section 2.

Premise of the mined revival: the estimator's diagonal Gaussian pass on the
Haar-ROTATED net carries within-net rotation information.

Closed form says it cannot: the pass starts at mu=0, var=1, so at layer 0
  mu_pre  = 0 @ (R.T W1) = 0            (alpha[0] == 0 for every rotation)
  var_pre[j] = || (R.T W1)[:,j] ||^2 = || W1[:,j] ||^2   (R orthogonal)
hence the entire (mu, var) trajectory -- and every alpha-derived diagnostic --
is rotation-invariant in exact arithmetic.

This script measures the ONLY thing that can break that: float32 rounding.
GATE (predeclared): max relative deviation of the layer-0 var_pre vector
between the rotated and unrotated first layer.
  < 1e-4  -> invariance holds at rounding level -> revival dead at step 0
  >= 1e-2 -> invariance argument wrong -> step 1 decides on its merits
"""
from __future__ import annotations

import json
import sys
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

from estimator import Estimator as KerdockV3  # noqa: E402  (frozen, read-only)

WIDTH, DEPTH = 256, 32
NET_SEEDS = (101, 202, 303)
N_ROT = 16
GATE_ROUNDING = 1e-4
GATE_WRONG = 1e-2


def he_weights(seed: int) -> list[np.ndarray]:
    """Verbatim P2/M185 construction."""
    rng = np.random.default_rng(seed)
    gain = np.float32(np.sqrt(2.0 / WIDTH))
    return [rng.standard_normal((WIDTH, WIDTH), dtype=np.float32) * gain
            for _ in range(DEPTH)]


def rot_seed(net_seed: int, r: int) -> int:
    return 900_000 + net_seed * 1_000 + r


def main() -> None:
    out = {"gate": "step0_diagonal_pass_rotation_invariance",
           "predeclared_thresholds": {"rounding_level": GATE_ROUNDING,
                                      "argument_wrong": GATE_WRONG},
           "per_net": {}}
    worst = 0.0
    worst_where = None
    orth_worst = 0.0
    for n in NET_SEEDS:
        W1 = he_weights(n)[0]
        base_varpre = np.ones(WIDTH, dtype=np.float32) @ (W1 * W1)  # f32, as v3
        rows = []
        for r in range(N_ROT):
            R = KerdockV3._haar_rotation(rot_seed(n, r), WIDTH)
            R = np.asarray(R)
            # orthogonality of the frozen rotation, reported as context
            orth = float(np.abs(R.T @ R - np.eye(WIDTH, dtype=np.float32)).max())
            orth_worst = max(orth_worst, orth)
            W1r = (R.T @ W1).astype(np.float32)
            varpre = np.ones(WIDTH, dtype=np.float32) @ (W1r * W1r)
            rel = np.abs(varpre.astype(np.float64) - base_varpre.astype(np.float64))
            rel = rel / np.abs(base_varpre.astype(np.float64))
            m = float(rel.max())
            rows.append({"r": r, "rot_seed": rot_seed(n, r),
                         "max_rel_dev_varpre": m,
                         "mean_rel_dev_varpre": float(rel.mean()),
                         "max_abs_RtR_minus_I": orth})
            if m > worst:
                worst, worst_where = m, (n, r)
        out["per_net"][str(n)] = {
            "varpre_unrotated_first5": [float(v) for v in base_varpre[:5]],
            "rows": rows,
            "max_rel_dev_over_16_rotations": max(x["max_rel_dev_varpre"]
                                                 for x in rows),
        }
    out["max_rel_dev_all"] = worst
    out["max_rel_dev_at"] = {"net": worst_where[0], "r": worst_where[1]}
    out["max_abs_RtR_minus_I_all"] = orth_worst
    if worst >= GATE_WRONG:
        verdict = ("STEP0 SURVIVES: layer-0 var_pre is materially "
                   "rotation-dependent; the invariance argument is wrong; "
                   "step 1 decides on its merits")
        killed = False
    elif worst < GATE_ROUNDING:
        verdict = ("STEP0 KILLS: layer-0 var_pre of the rotated net equals the "
                   "unrotated one to float32 rounding, so the diagonal "
                   "Gaussian pass -- and every alpha-derived diagnostic -- is "
                   "rotation-invariant BY CONSTRUCTION. The mined proxy class "
                   "has zero within-net rotation signal.")
        killed = True
    else:
        verdict = ("STEP0 AMBIGUOUS: deviation between 1e-4 and 1e-2; "
                   "predeclaration requires running step 1 on its merits")
        killed = False
    out["verdict"] = verdict
    out["killed_at_step0"] = killed
    (HERE / "step0_results.json").write_text(
        json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"max |R.T R - I| over 48 rotations: {orth_worst:.3e}")
    print(f"max relative deviation of layer-0 var_pre: {worst:.6e} "
          f"(net {worst_where[0]}, r {worst_where[1]})")
    print(verdict)


if __name__ == "__main__":
    main()
