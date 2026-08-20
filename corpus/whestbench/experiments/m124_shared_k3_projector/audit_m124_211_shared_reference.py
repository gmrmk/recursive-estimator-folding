"""Generated-only audit of M124's omitted three-label [2,1,1] collision.

M122 defines this collision exactly through a tripartite normal-ordered
series.  M124 replaces only one- and two-label collisions, so its candidate
and dense reference share the same tree continuation on [2,1,1].  This script
measures that shared-reference discrepancy on the three frozen width-8 M124
backgrounds.  It reads no contest data, scorer, champion, or outcome file.
"""

from __future__ import annotations

import json
import itertools
import math
import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "m122_nonzero_bridge_theory"))
sys.path.insert(0, str(ROOT / "m124_shared_k3_projector"))

from m122_nonzero_bridge import (  # noqa: E402
    build_state,
    exact_collision_cumulant,
)
from m124_protocol import CASES, generated_background  # noqa: E402
from m124_shared_projector import (  # noqa: E402
    build_nonzero_bridge_source,
    edgeworth_delay_one,
    physical_source,
    transport_dense,
)


def relative(numerator: np.ndarray, denominator: np.ndarray) -> float:
    return float(np.linalg.norm(numerator) / max(np.linalg.norm(denominator), 1.0e-300))


def repeated_tables(tensor: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    n = tensor.shape[0]
    aaaa = np.asarray([tensor[a, a, a, a] for a in range(n)])
    aaab = np.asarray([[tensor[a, a, a, b] for b in range(n)] for a in range(n)])
    aabb = np.asarray([[tensor[a, a, b, b] for b in range(n)] for a in range(n)])
    return aaaa, aaab, aabb


def combined_relative(
    numerator: tuple[np.ndarray, ...], denominator: tuple[np.ndarray, ...]
) -> float:
    top = sum(float(np.sum(value * value)) for value in numerator)
    bottom = sum(float(np.sum(value * value)) for value in denominator)
    return float(np.sqrt(top / max(bottom, 1.0e-300)))


def tree4_continued(state, labels: tuple[int, int, int, int]) -> float:
    q = state.bridge
    star = 0.0
    for centre_position, centre in enumerate(labels):
        star += state.gamma3[centre] * math.prod(
            q[centre, leaf]
            for position, leaf in enumerate(labels)
            if position != centre_position
        )
    path = 0.0
    for permutation in itertools.permutations(range(4)):
        a, b, c, d = (labels[position] for position in permutation)
        path += (
            state.gamma2[b]
            * state.gamma2[c]
            * q[a, b]
            * q[b, c]
            * q[c, d]
        )
    return float(np.prod(state.relu_scale[list(labels)]) * (star + 0.5 * path))


def exact_211_delta(state) -> tuple[np.ndarray, np.ndarray]:
    n = state.mean.size
    exact = np.zeros((n, n, n, n), dtype=np.float64)
    delta = np.zeros_like(exact)
    for repeated in range(n):
        others = [index for index in range(n) if index != repeated]
        for left_position, left in enumerate(others):
            for right in others[left_position + 1 :]:
                canonical = (repeated, repeated, left, right)
                # Use the stricter M122 tail check.  This audit is still a
                # shared-bias falsifier, not a uniform endpoint certificate.
                exact_value = exact_collision_cumulant(state, canonical, terms=48)
                tree_value = tree4_continued(state, canonical)
                for labels in set(itertools.permutations(canonical)):
                    exact[labels] = exact_value
                    delta[labels] = exact_value - tree_value
    return exact, delta


def main() -> None:
    rows: list[dict[str, float | int]] = []
    for case in CASES:
        # One pre-existing frozen cell is enough to quantify the shared-reference
        # defect without turning this audit into a post-hoc grid.
        if case.width != 8 or case.seed != 1_240_801:
            continue
        mean, covariance, weight = generated_background(case)

        state122 = build_state(mean, covariance, pair_terms=96)
        exact211, delta211 = exact_211_delta(state122)
        mask211 = exact211 != 0.0

        source124 = build_nonzero_bridge_source(mean, covariance)
        base4 = physical_source(source124, 4)
        repaired4 = base4 + delta211
        transported_base = transport_dense(base4, weight)
        transported_repaired = transport_dense(repaired4, weight)
        transported_delta = transported_repaired - transported_base

        base_repeated = repeated_tables(transported_base)
        repaired_repeated = repeated_tables(transported_repaired)
        delta_repeated = tuple(
            repaired - base for repaired, base in zip(repaired_repeated, base_repeated)
        )

        next_mean = weight.T @ source124.activation_mean
        next_covariance = weight.T @ source124.activation_covariance @ weight
        next_covariance = 0.5 * (next_covariance + next_covariance.T)
        transported3 = transport_dense(physical_source(source124, 3), weight)
        defect_base = edgeworth_delay_one(
            next_mean, next_covariance, transported3, transported_base
        )
        defect_repaired = edgeworth_delay_one(
            next_mean, next_covariance, transported3, transported_repaired
        )

        rows.append(
            {
                "seed": case.seed,
                "alpha_scale": case.alpha_scale,
                "source_211_tree_relative_error": relative(
                    delta211[mask211], exact211[mask211]
                ),
                "source_211_relative_mass": relative(
                    exact211, base4
                ),
                "transported_full_relative_change": relative(
                    transported_delta, transported_repaired
                ),
                "transported_repeated_relative_change": combined_relative(
                    delta_repeated, repaired_repeated
                ),
                "delay_one_mean_relative_change": relative(
                    defect_repaired.mean - defect_base.mean, defect_repaired.mean
                ),
                "delay_one_cov_relative_change": relative(
                    defect_repaired.covariance - defect_base.covariance,
                    defect_repaired.covariance,
                ),
            }
        )
    print(json.dumps({"audit": "M124_SHARED_REFERENCE_211", "rows": rows}, indent=2))


if __name__ == "__main__":
    main()
