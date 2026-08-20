"""Inert generated-only protocol for the M126+M125b reduced-source child.

This is deliberately a pre-outcome harness: it has no network loader, scorer,
submission builder, or contest-data path.  Its only role is to make the
reduced one/two-label convention, mixed-precision probe parity, and the M122
three-label omission visible before a proposed child can be activated.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
import sys
from typing import Final

import numpy as np

ROOT: Final[Path] = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "m126_repeated_output_source_contraction"))
sys.path.insert(0, str(ROOT / "m122_nonzero_bridge_theory"))
sys.path.insert(0, str(ROOT / "m124_shared_k3_projector"))

from m126_repeated_output_contractions import (  # noqa: E402
    collision22_hard_exact,
    collision_repeated_exact,
    path_hard_tables_exact,
    tree_repeated_exact,
)
from m122_nonzero_bridge import build_state, small_source_tensor, tree_tensor_continuation  # noqa: E402
from m124_shared_projector import edgeworth_delay_one  # noqa: E402


PROBE_COUNTS: Final[tuple[int, ...]] = (2, 4, 6, 8)
PREFERRED_PROBES: Final[int] = 8
PROBE_SEED: Final[int] = 1_320_080
M125B_EFFECTIVE_FLOPS: Final[int] = 12_819_347_280
SOURCE_F32_EFFECTIVE: Final[dict[int, int]] = {
    2: 50_526_231_040,
    4: 60_907_788_800,
    6: 71_289_346_560,
    8: 81_670_904_320,
}


@dataclass(frozen=True)
class ReducedTables:
    k3_aaa: np.ndarray
    k3_aab: np.ndarray
    k4_aaaa: np.ndarray
    k4_aaab: np.ndarray
    k4_aabb: np.ndarray


def frozen_signs(width: int, probes: int, *, seed: int = PROBE_SEED) -> np.ndarray:
    """Outcome-independent Rademacher probes, identical in f32/f64 branches."""
    if probes not in PROBE_COUNTS or width < 2:
        raise ValueError("unfrozen probe count or invalid width")
    rng = np.random.default_rng(seed + 1009 * width + 9176 * probes)
    return rng.choice(np.array((-1.0, 1.0)), size=(probes, width)).astype(np.float64)


def _mixed_probe_aabb(
    q: np.ndarray,
    gamma2: np.ndarray,
    paired4: np.ndarray,
    weight: np.ndarray,
    signs: np.ndarray,
    *,
    dtype: np.dtype,
) -> np.ndarray:
    """Shared-sign M126 hard path+[2,2] estimator; only GEMM operands cast."""
    qd = np.asarray(q, dtype=dtype)
    gd = np.asarray(gamma2, dtype=dtype)
    ed = np.asarray(paired4, dtype=dtype)
    wd = np.asarray(weight, dtype=dtype)
    residual = qd.copy()
    np.fill_diagonal(residual, np.dtype(dtype).type(0.0))
    answer = np.zeros((weight.shape[1], weight.shape[1]), dtype=np.float64)
    propagated = qd @ wd
    for sign in signs:
        z = np.asarray(sign, dtype=dtype)
        ez = residual @ z
        mz = propagated.T @ ((gd * z)[:, None] * wd)
        mez = propagated.T @ ((gd * ez)[:, None] * wd)
        path = 2.0 * (mz * mez + (mz * mez).T) + 2.0 * (mz * mez.T + (mz * mez.T).T)
        nz = wd.T @ (z[:, None] * wd)
        nez = wd.T @ ((ed @ z)[:, None] * wd)
        collision = 2.0 * nz * nez
        # Enforce the source's output-exchange law inside each rounded sample.
        sample = path + collision
        sample = 0.5 * (sample + sample.T)
        answer += np.asarray(sample, dtype=np.float64)
    return answer / float(signs.shape[0])


def reduced_tables_same_probes(
    q: np.ndarray,
    gamma2: np.ndarray,
    gamma3: np.ndarray,
    collision: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray],
    weight: np.ndarray,
    signs: np.ndarray,
    *,
    dtype: np.dtype,
) -> ReducedTables:
    """Exact easy M126 convention plus mixed-precision shared hard probes.

    The one/two-label convention is intentional and explicitly incomplete:
    no `[2,1,1]` value is accepted by this function.
    """
    d3, e3, d4, e31, e22 = collision
    full_tree = tree_repeated_exact(q, gamma2, gamma3, weight)
    full_collision = collision_repeated_exact(d3, e3, d4, e31, e22, weight)
    hard_path = path_hard_tables_exact(q, gamma2, weight)
    exact_path_residual = (
        2.0 * (hard_path["residual_self"] + hard_path["residual_self"].T)
        + 4.0 * hard_path["residual_cross"]
    )
    exact_collision_hard = collision22_hard_exact(e22, weight)
    sampled_hard = _mixed_probe_aabb(q, gamma2, e22, weight, signs, dtype=dtype)
    return ReducedTables(
        k3_aaa=full_tree["k3_aaa"] + full_collision["k3_aaa"],
        k3_aab=full_tree["k3_aab"] + full_collision["k3_aab"],
        k4_aaaa=full_tree["k4_aaaa"] + full_collision["k4_aaaa"],
        k4_aaab=full_tree["k4_aaab"] + full_collision["k4_aaab"],
        k4_aabb=(
            full_tree["k4_aabb"] + full_collision["k4_aabb"]
            - exact_path_residual - exact_collision_hard + sampled_hard
        ),
    )


def linear_one_delay_response(tables: ReducedTables, mean: np.ndarray) -> np.ndarray:
    """Frozen linear proxy for response variance, not a competition estimate."""
    n = mean.size
    if tables.k3_aab.shape != (n, n) or tables.k4_aabb.shape != (n, n):
        raise ValueError("table and mean dimensions disagree")
    first = 0.17 + 0.03 * np.tanh(mean)
    second = 0.11 + 0.02 * np.cos(mean)
    delta_mean = -tables.k3_aaa * first / 6.0 + tables.k4_aaaa * second / 24.0
    delta_cov = (
        0.13 * (tables.k3_aab + tables.k3_aab.T)
        + 0.07 * (tables.k4_aaab + tables.k4_aaab.T)
        + 0.19 * tables.k4_aabb
    )
    delta_cov = 0.5 * (delta_cov + delta_cov.T)
    return np.concatenate((delta_mean, delta_cov[np.triu_indices(n)]))


def table_vector(tables: ReducedTables) -> np.ndarray:
    return np.concatenate(tuple(np.asarray(getattr(tables, field)).ravel() for field in ReducedTables.__dataclass_fields__))


def relative_error(value: np.ndarray, reference: np.ndarray) -> float:
    return float(np.linalg.norm(value - reference) / max(np.linalg.norm(reference), 1e-12))


def exact_m122_211_omission_response(mean: np.ndarray, covariance: np.ndarray, weight: np.ndarray) -> dict[str, float]:
    """Small-width independent M122 oracle for the omitted `[2,1,1]` mass."""
    state = build_state(mean, covariance, pair_terms=64)
    exact4 = small_source_tensor(state, 4, terms=32)
    tree4 = tree_tensor_continuation(state, 4)
    n = mean.size
    delta211 = np.zeros_like(exact4)
    for labels in np.ndindex(*(n,) * 4):
        multiplicities = sorted(labels.count(index) for index in set(labels))
        if multiplicities == [1, 1, 2]:
            delta211[labels] = exact4[labels] - tree4[labels]
    transport = np.einsum("ijkl,ia,jb,kc,ld->abcd", delta211, weight, weight, weight, weight, optimize=True)
    base4 = np.zeros_like(transport)
    base3 = np.zeros((n, n, n), dtype=np.float64)
    activation_cov = np.outer(state.relu_scale, state.relu_scale) * state.bridge
    next_mean = weight.T @ state.relu_mean
    next_cov = weight.T @ activation_cov @ weight
    next_cov = 0.5 * (next_cov + next_cov.T)
    zero = edgeworth_delay_one(next_mean, next_cov, base3, base4)
    repaired = edgeworth_delay_one(next_mean, next_cov, base3, transport)
    response = np.concatenate((repaired.mean - zero.mean, (repaired.covariance - zero.covariance).ravel()))
    return {
        "source_relative_mass": relative_error(delta211, exact4),
        "transported_repeated_rms": float(np.sqrt(np.mean(transport * transport))),
        "one_delay_response_rms": float(np.sqrt(np.mean(response * response))),
    }


def candidate_cost(probes: int) -> int:
    if probes not in PROBE_COUNTS:
        raise ValueError("unfrozen probe count")
    return SOURCE_F32_EFFECTIVE[probes] + M125B_EFFECTIVE_FLOPS


def predeclared_choice(rows: list[dict[str, float | int | bool]]) -> int | None:
    """Select only among passed rows by variance-times-cost; ties favour lower P."""
    eligible = [row for row in rows if bool(row["all_gates_pass"])]
    if not eligible:
        return None
    chosen = min(eligible, key=lambda row: (float(row["response_variance"]) * int(row["effective_flops"]), int(row["probes"])))
    return int(chosen["probes"])
