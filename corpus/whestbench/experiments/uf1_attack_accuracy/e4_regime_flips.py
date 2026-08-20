"""E4 -- the discrete tail risk: can a Strassen drift flip a pilot regime
decision?

Continuous drift is harmless if it only perturbs magnitudes.  The champion has
three THRESHOLD predicates whose output is discontinuous in the sampled
pre-activations:

  fold3_estimator.py:136   fired   = max(pilot_pre, axis=0) >  0.0   (rescue)
  fold_estimator.py:20     fired   = max(pilot_pre, axis=0) >  0.0   (_refine_dead)
  fold_estimator.py:29     crossed = min(pilot_pre, axis=0) <= 0.0   (_refine_on)

A flip switches a neuron between a sampled value and an analytic/folded value,
which is an O(1e-2) change on that neuron -- large enough to matter, unlike a
ReLU gate flip (which by construction happens where the activation is ~0).

This harness measures, in the production geometry, how many of those
statistics change sign between the float64 reference and the float32
Strassen-depth-d arm, over every layer and every neuron (an upper bound on the
real flip count, since only cold/on neurons are ever tested).

Pilot row sets are the champion's: rows [0:256] + [n_base:n_base+256] in the
deep loop (pilot_base=256) and [0:1024] + [n_base:n_base+1024] in the terminal
fold (fold_pilot_base=1024).  Both are measured.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from e1_chain_distribution import sw_np  # noqa: E402
from e2_score_translation import (  # noqa: E402
    DEPTH, N_BASE, STRASSEN_LAYERS, kerdock_directions, sample_mlp_weights,
)

PILOTS = {"pilot256": 256, "pilot1024": 1024}


def pilot_stats(pre, n_rows):
    idx = np.r_[0:n_rows, N_BASE:N_BASE + n_rows]
    p = pre[idx]
    return p.max(axis=0), p.min(axis=0)


def run(net_seed: int, depths) -> dict:
    z = kerdock_directions()
    Ws = sample_mlp_weights(net_seed)
    # reference: float64 classical, capture pilot statistics at every layer
    ref = {}
    zf = z.astype(np.float64)
    Wf = [w.astype(np.float64) for w in Ws]
    fp = zf @ Wf[0]
    x = np.concatenate((np.maximum(fp, 0), np.maximum(-fp, 0)), axis=0)
    for layer in range(1, DEPTH):
        pre = x @ Wf[layer]
        for name, n in PILOTS.items():
            ref[(layer, name)] = pilot_stats(pre, n)
        x = np.maximum(pre, 0.0)
    del x, pre, zf, Wf
    out = {}
    for d in depths:
        t0 = time.time()
        zs = z.astype(np.float32)
        Ws32 = [w.astype(np.float32) for w in Ws]
        fp = zs @ Ws32[0]
        x = np.concatenate((np.maximum(fp, 0), np.maximum(-fp, 0)), axis=0)
        flips_max = flips_min = tests = 0
        margin_min = np.inf
        for layer in range(1, DEPTH):
            dd = d if layer <= STRASSEN_LAYERS else 0
            pre = sw_np(x, Ws32[layer], dd)
            for name, n in PILOTS.items():
                mx, mn = pilot_stats(pre.astype(np.float64), n)
                rmx, rmn = ref[(layer, name)]
                flips_max += int(np.count_nonzero((mx > 0.0) != (rmx > 0.0)))
                flips_min += int(np.count_nonzero((mn <= 0.0) != (rmn <= 0.0)))
                tests += 2 * mx.size
                scale = float(np.sqrt(np.mean(rmx ** 2)))
                margin_min = min(margin_min,
                                 float(np.abs(rmx).min() / scale),
                                 float(np.abs(rmn).min() / scale))
            x = np.maximum(pre, np.float32(0.0))
        out[f"d{d}"] = {
            "flips_max_predicate": flips_max,
            "flips_min_predicate": flips_min,
            "threshold_tests": tests,
            "min_relative_margin_to_threshold": margin_min,
            "seconds": round(time.time() - t0, 1),
        }
        print(f"net{net_seed} d={d}: flips(max)={flips_max} flips(min)={flips_min}"
              f" / {tests} tests, closest relative margin={margin_min:.3e}"
              f" [{out[f'd{d}']['seconds']}s]", flush=True)
        del x, pre
    return out


if __name__ == "__main__":
    net = int(sys.argv[1])
    depths = [int(v) for v in sys.argv[2].split(",")]
    res = run(net, depths)
    (HERE / f"e4_flips_net{net}.json").write_text(json.dumps(res, indent=2),
                                                  encoding="utf-8")
    print(f"wrote e4_flips_net{net}.json", flush=True)
