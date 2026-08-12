"""Truth-free DGFL covariance screen on one deterministic hand CPWL network."""

from __future__ import annotations

import hashlib
import math
from typing import Any, Mapping, Sequence

import numpy as np

from dgfl1_f0 import (
    canonical_pairwise_mean,
    dipole_rungs,
    forward_jvp,
    fourier_rung,
    rotation_2d,
    rotation_generator,
)


Array = np.ndarray
FIT_ROTATION_SEED = 0xD6F10001
HELD_ROTATION_SEED = 0xD6F10002
BOOTSTRAP_SEED = 0xD6F10003
PERMUTATION_SEED = 0xD6F10004
BOOTSTRAP_REPLICATES = 4096
PERMUTATION_REPLICATES = 1024
ROTATIONS_PER_SPLIT = 128
PILOT_ANGLE = 0.137
FREQUENCIES = (math.sqrt(2.0), 2.0 * math.sqrt(2.0))
RIDGE_SCALE = 2.0**-20
GEOMETRY_TOLERANCE = 2.0**-20
PREACTIVATION_CLEARANCE = 2.0**-40
SOLVE_RESIDUAL_TOLERANCE = 2.0**-42


class ScientificImplementationKill(RuntimeError):
    """A predeclared candidate degeneracy after a valid manifest preflight."""


def hand_network() -> tuple[Array, ...]:
    """Return the exact two-layer network already used by synthetic F0."""

    return (
        np.array(
            [[1.0, -0.3], [0.4, 0.8], [-0.7, 0.5]], dtype=np.float64
        ),
        np.array(
            [[0.6, -0.2, 0.9], [-0.4, 1.1, 0.3]], dtype=np.float64
        ),
    )


def design_rows() -> Array:
    """Return the frozen positive-bank-then-negative-bank d=2 design order."""

    return np.array(
        [[1.0, 0.0], [-1.0, 0.0], [0.0, 1.0], [0.0, -1.0]],
        dtype=np.float64,
    )


def _validated_weights(weights: Sequence[Array]) -> tuple[Array, Array]:
    if len(weights) != 2:
        raise ValueError("the frozen screen requires exactly two layers")
    first = np.asarray(weights[0], dtype=np.float64)
    second = np.asarray(weights[1], dtype=np.float64)
    if first.shape != (3, 2) or second.shape != (2, 3):
        raise ValueError("hand-network shapes drifted")
    if not (np.all(np.isfinite(first)) and np.all(np.isfinite(second))):
        raise ValueError("hand-network weights must be finite")
    return first, second


def pilot_geometry(weights: Sequence[Array]) -> dict[str, Array]:
    """Derive two deep input pullbacks and one oriented rank-two generator."""

    first, second = _validated_weights(weights)
    pilot = rotation_2d(PILOT_ANGLE) @ np.array([1.0, 0.0])
    first_pre = first @ pilot
    if np.any(np.abs(first_pre) <= PREACTIVATION_CLEARANCE):
        raise ScientificImplementationKill("pilot lies too close to a first-layer gate")
    first_mask = first_pre > 0.0
    pullbacks = second @ np.diag(first_mask.astype(np.float64)) @ first
    norms = np.linalg.norm(pullbacks, axis=1)
    if np.any(~np.isfinite(norms)) or np.any(norms <= PREACTIVATION_CLEARANCE):
        raise ScientificImplementationKill("invalid or degenerate deep pullback")
    axes = pullbacks / norms[:, None]
    separation = 1.0 - abs(float(axes[0] @ axes[1]))
    if not math.isfinite(separation) or separation <= GEOMETRY_TOLERANCE:
        raise ScientificImplementationKill("deep pullback axes are nearly collinear")

    m = np.array([1.0, 0.0], dtype=np.float64)
    b = np.array([0.0, 1.0], dtype=np.float64)
    J = rotation_generator(m, b)
    return {
        "pilot": pilot,
        "first_preactivation": first_pre,
        "deep_preactivation": second @ np.maximum(first_pre, 0.0),
        "first_mask": first_mask,
        "pullbacks": pullbacks,
        "axes": axes,
        "m": m,
        "b": b,
        "J": J,
    }


def rotation_angles(seed: int, count: int) -> Array:
    if count <= 0:
        raise ValueError("rotation count must be positive")
    generator = np.random.Generator(np.random.PCG64DXSM(int(seed)))
    return generator.random(int(count), dtype=np.float64) * math.tau


def rotation_matrices(seed: int, count: int) -> Array:
    """Materialize the exact ordered rotation fixture for one stream."""

    matrices = np.stack([rotation_2d(theta) for theta in rotation_angles(seed, count)])
    return np.ascontiguousarray(matrices, dtype="<f8")


def sha256_payload(array: Array) -> str:
    """Hash a canonical C-order numeric payload, excluding container metadata."""

    value = np.asarray(array)
    if value.dtype.hasobject or not value.flags.c_contiguous:
        raise ValueError("payload must be a C-contiguous non-object array")
    return hashlib.sha256(value.tobytes(order="C")).hexdigest().upper()


def permutation_indices(
    *, replicates: int = PERMUTATION_REPLICATES, count: int = ROTATIONS_PER_SPLIT
) -> Array:
    """Return fit/held whole-record permutations in their frozen draw order."""

    if replicates <= 0 or count <= 1 or count > np.iinfo(np.uint16).max:
        raise ValueError("invalid permutation fixture dimensions")
    generator = np.random.Generator(np.random.PCG64DXSM(PERMUTATION_SEED))
    result = np.empty((replicates, 2, count), dtype="<u2")
    for replicate in range(replicates):
        result[replicate, 0] = generator.permutation(count)
        result[replicate, 1] = generator.permutation(count)
    return result


def bootstrap_indices(
    *, replicates: int = BOOTSTRAP_REPLICATES, count: int = ROTATIONS_PER_SPLIT
) -> Array:
    """Return paired whole-record bootstrap indices in a canonical dtype."""

    if replicates <= 0 or count <= 1 or count > np.iinfo(np.uint16).max:
        raise ValueError("invalid bootstrap fixture dimensions")
    generator = np.random.Generator(np.random.PCG64DXSM(BOOTSTRAP_SEED))
    values = generator.integers(
        0, count, size=(replicates, count), dtype=np.uint16
    )
    return np.ascontiguousarray(values, dtype="<u2")


def evaluate_rotation_record(
    *, theta: float, weights: Sequence[Array], geometry: Mapping[str, Array]
) -> tuple[Array, Array, dict[str, Any]]:
    """Return one whole-rotation base record and its six control records."""

    if not math.isfinite(theta):
        raise ValueError("theta must be finite")
    return evaluate_rotation_matrix_record(
        rotation=rotation_2d(theta), weights=weights, geometry=geometry
    )


def evaluate_rotation_matrix_record(
    *, rotation: Array, weights: Sequence[Array], geometry: Mapping[str, Array]
) -> tuple[Array, Array, dict[str, Any]]:
    """Evaluate the exact materialized rotation used by the sealed fixture."""

    frozen_weights = _validated_weights(weights)
    rotation64 = np.asarray(rotation, dtype=np.float64)
    if rotation64.shape != (2, 2) or not np.all(np.isfinite(rotation64)):
        raise ValueError("rotation must be a finite two-by-two matrix")
    if not np.allclose(rotation64.T @ rotation64, np.eye(2), rtol=0.0, atol=2e-15):
        raise ValueError("rotation is not orthogonal")
    if not math.isclose(float(np.linalg.det(rotation64)), 1.0, rel_tol=0.0, abs_tol=2e-15):
        raise ValueError("rotation is not orientation preserving")
    m = np.asarray(geometry["m"], dtype=np.float64)
    b = np.asarray(geometry["b"], dtype=np.float64)
    J = np.asarray(geometry["J"], dtype=np.float64)
    axes = np.asarray(geometry["axes"], dtype=np.float64)
    if axes.shape != (2, 2):
        raise ValueError("the frozen screen requires two pullback axes")
    expected_J = rotation_generator(m, b)
    if not np.allclose(J, expected_J, rtol=0.0, atol=2e-15):
        raise ValueError("pilot generator drift")

    base = design_rows()
    rows = (rotation64 @ base.T).T
    y_leaves: list[Array] = []
    z_leaves: list[Array] = []
    for u in rows:
        y, dy = forward_jvp(frozen_weights, u, J @ u)
        rungs = list(dipole_rungs(u, y, dy, m, b))
        for axis in axes:
            for frequency in FREQUENCIES:
                rungs.append(fourier_rung(u, y, dy, J, axis, frequency))
        y_leaves.append(y)
        z_leaves.append(np.stack(rungs))

    y_mean = canonical_pairwise_mean(y_leaves)
    z_mean = canonical_pairwise_mean(z_leaves)
    if y_mean.shape != (2,) or z_mean.shape != (6, 2):
        raise RuntimeError("record codomain drift")
    if not (np.all(np.isfinite(y_mean)) and np.all(np.isfinite(z_mean))):
        raise ScientificImplementationKill("record contains nonfinite values")
    return y_mean, z_mean, {
        "row_order": ["+e1", "-e1", "+e2", "-e2"],
        "jvp_evaluations": 4,
        "rung_order": [
            "dipole_m",
            "dipole_b",
            "axis0_sqrt2",
            "axis0_2sqrt2",
            "axis1_sqrt2",
            "axis1_2sqrt2",
        ],
    }


def generate_split_records(seed: int, count: int = ROTATIONS_PER_SPLIT) -> tuple[Array, Array, dict[str, Any]]:
    """Generate one domain-separated split from materialized rotations."""

    weights = hand_network()
    geometry = pilot_geometry(weights)
    matrices = rotation_matrices(seed, count)
    y_records = np.empty((count, 2), dtype=np.float64)
    z_records = np.empty((count, 6, 2), dtype=np.float64)
    for index, rotation in enumerate(matrices):
        y_records[index], z_records[index], receipt = evaluate_rotation_matrix_record(
            rotation=rotation, weights=weights, geometry=geometry
        )
        if receipt["jvp_evaluations"] != 4:
            raise RuntimeError("rotation record did not use exactly four JVPs")
    return y_records, z_records, {
        "seed": int(seed),
        "rotation_count": int(count),
        "jvp_evaluations": int(4 * count),
        "rotation_payload_sha256": sha256_payload(matrices),
        "y_payload_sha256": sha256_payload(y_records),
        "z_payload_sha256": sha256_payload(z_records),
    }


def _fixed_cholesky_factor(system: Array) -> Array:
    """Unpivoted six-by-six Cholesky in fixed ascending scalar order."""

    if system.shape != (6, 6):
        raise ValueError("the frozen factorization is six-dimensional")
    lower = np.zeros((6, 6), dtype=np.float64)
    for row in range(6):
        for column in range(row + 1):
            value = float(system[row, column])
            for inner in range(column):
                value -= float(lower[row, inner] * lower[column, inner])
            if row == column:
                if not math.isfinite(value) or value <= 0.0:
                    raise ScientificImplementationKill("frozen Cholesky pivot is nonpositive")
                lower[row, column] = math.sqrt(value)
            else:
                lower[row, column] = value / lower[column, column]
    return lower


def _fixed_cholesky_solve_from_factor(lower: Array, rhs: Array) -> Array:
    if lower.shape != (6, 6) or rhs.shape != (6,):
        raise ValueError("the frozen solve is six-dimensional")

    intermediate = np.zeros(6, dtype=np.float64)
    for row in range(6):
        value = float(rhs[row])
        for column in range(row):
            value -= float(lower[row, column] * intermediate[column])
        intermediate[row] = value / lower[row, row]

    beta = np.zeros(6, dtype=np.float64)
    for row in range(5, -1, -1):
        value = float(intermediate[row])
        for column in range(row + 1, 6):
            value -= float(lower[column, row] * beta[column])
        beta[row] = value / lower[row, row]
    return beta


def _fixed_cholesky_solve(system: Array, rhs: Array) -> Array:
    return _fixed_cholesky_solve_from_factor(_fixed_cholesky_factor(system), rhs)


def fit_joint_coefficients(y: Array, z: Array) -> tuple[Array, dict[str, float]]:
    """Fit the frozen centered six-rung ridge with one scalar per rung."""

    y64 = np.asarray(y, dtype=np.float64)
    z64 = np.asarray(z, dtype=np.float64)
    if y64.ndim != 2 or z64.shape != (y64.shape[0], 6, y64.shape[1]):
        raise ValueError("fit arrays have incompatible shapes")
    if y64.shape[0] < 2 or y64.shape[1] == 0:
        raise ValueError("fit arrays are empty or undersized")
    if not (np.all(np.isfinite(y64)) and np.all(np.isfinite(z64))):
        raise ValueError("fit arrays must be finite")

    yc = y64 - np.mean(y64, axis=0, keepdims=True)
    zc = z64 - np.mean(z64, axis=0, keepdims=True)
    count = float(y64.shape[0])
    gram = np.einsum("irp,isp->rs", zc, zc) / count
    rhs = np.einsum("irp,ip->r", zc, yc) / count
    trace = float(np.trace(gram))
    if not math.isfinite(trace) or trace <= 0.0:
        raise ScientificImplementationKill("nonpositive control Gram trace")
    ridge = RIDGE_SCALE * trace / 6.0
    system = gram + ridge * np.eye(6)
    beta = _fixed_cholesky_solve(system, rhs)
    residual = system @ beta - rhs
    relative = float(np.linalg.norm(residual) / max(np.linalg.norm(rhs), np.finfo(float).tiny))
    if not np.all(np.isfinite(beta)) or not math.isfinite(relative):
        raise ScientificImplementationKill("coefficient solve produced nonfinite values")
    if relative > SOLVE_RESIDUAL_TOLERANCE:
        raise ScientificImplementationKill("coefficient solve residual exceeds the frozen tolerance")
    return beta, {
        "gram_trace": trace,
        "ridge_lambda": ridge,
        "relative_residual": relative,
    }


def apply_factorial_arms(y: Array, z: Array, beta: Array) -> dict[str, Array]:
    y64 = np.asarray(y, dtype=np.float64)
    z64 = np.asarray(z, dtype=np.float64)
    beta64 = np.asarray(beta, dtype=np.float64)
    if y64.ndim != 2 or z64.shape != (y64.shape[0], 6, y64.shape[1]):
        raise ValueError("arm arrays have incompatible shapes")
    if beta64.shape != (6,) or not np.all(np.isfinite(beta64)):
        raise ValueError("beta must be a finite six-vector")
    dipole = np.einsum("irp,r->ip", z64[:, :2], beta64[:2])
    fourier = np.einsum("irp,r->ip", z64[:, 2:], beta64[2:])
    joint = np.einsum("irp,r->ip", z64, beta64)
    return {
        "00": y64.copy(),
        "10": y64 - dipole,
        "01": y64 - fourier,
        "11": y64 - joint,
    }


def trace_variance(values: Array) -> float:
    array = np.asarray(values, dtype=np.float64)
    if array.ndim != 2 or array.shape[0] < 2 or array.shape[1] == 0:
        raise ValueError("variance input has incompatible shape")
    if not np.all(np.isfinite(array)):
        raise ValueError("variance input must be finite")
    centered = array - np.mean(array, axis=0, keepdims=True)
    result = float(np.sum(centered * centered) / float(array.shape[0] - 1))
    if not math.isfinite(result) or result < 0.0:
        raise ScientificImplementationKill("trace variance is invalid")
    return result


def held_statistics(arms: Mapping[str, Array]) -> dict[str, float]:
    """Compute the frozen 2x2 held variance decomposition."""

    required = ("00", "10", "01", "11")
    if set(arms) != set(required):
        raise ValueError("held arms must contain exactly 00, 10, 01, and 11")
    values = {name: trace_variance(arms[name]) for name in required}
    if any(values[name] <= 0.0 for name in ("00", "10", "01")):
        raise ScientificImplementationKill("held variance denominator is nonpositive")
    statistics = {
        "V00": values["00"],
        "V10": values["10"],
        "V01": values["01"],
        "V11": values["11"],
        "R2_joint": 1.0 - values["11"] / values["00"],
        "R2_F_given_D": 1.0 - values["11"] / values["10"],
        "R2_D_given_F": 1.0 - values["11"] / values["01"],
    }
    if not all(math.isfinite(value) for value in statistics.values()):
        raise ScientificImplementationKill("held statistic is nonfinite")
    return statistics


def _validated_resample_indices(indices: Array, count: int) -> Array:
    value = np.asarray(indices)
    if value.ndim != 2 or value.shape[1] != count or value.shape[0] == 0:
        raise ValueError("resampling fixture has incompatible shape")
    if not np.issubdtype(value.dtype, np.integer):
        raise ValueError("resampling fixture must be integral")
    if np.any(value < 0) or np.any(value >= count):
        raise ValueError("resampling fixture contains an invalid index")
    return value


def bootstrap_joint_lower(
    arms: Mapping[str, Array], indices: Array
) -> tuple[float, Array]:
    """Apply a paired fixed-beta bootstrap and return the 41st order statistic."""

    required = ("00", "10", "01", "11")
    if set(arms) != set(required):
        raise ValueError("bootstrap arms must contain exactly the four frozen arms")
    arrays = {name: np.asarray(arms[name], dtype=np.float64) for name in required}
    shape = arrays["00"].shape
    if len(shape) != 2 or shape[0] < 2 or shape[1] == 0:
        raise ValueError("bootstrap arms have incompatible shape")
    if any(array.shape != shape for array in arrays.values()):
        raise ValueError("bootstrap arm shapes differ")
    if not all(np.all(np.isfinite(array)) for array in arrays.values()):
        raise ValueError("bootstrap arms must be finite")
    fixture = _validated_resample_indices(indices, shape[0])
    values = np.empty(fixture.shape[0], dtype=np.float64)
    for replicate, selected in enumerate(fixture):
        v00 = trace_variance(arrays["00"][selected])
        v11 = trace_variance(arrays["11"][selected])
        if v00 <= 0.0:
            raise ScientificImplementationKill(
                "bootstrap base variance denominator is nonpositive"
            )
        values[replicate] = 1.0 - v11 / v00
    if not np.all(np.isfinite(values)):
        raise ScientificImplementationKill("bootstrap statistic is nonfinite")
    if values.size <= 40:
        raise ValueError("at least 41 bootstrap replicates are required")
    lower = float(np.sort(values)[40])
    return lower, values


def _validated_permutations(permutations: Array, count: int) -> Array:
    value = np.asarray(permutations)
    if value.ndim != 3 or value.shape[1:] != (2, count) or value.shape[0] == 0:
        raise ValueError("permutation fixture has incompatible shape")
    if not np.issubdtype(value.dtype, np.integer):
        raise ValueError("permutation fixture must be integral")
    expected = np.arange(count)
    for pair in value:
        if not np.array_equal(np.sort(pair[0]), expected):
            raise ValueError("fit permutation is not complete")
        if not np.array_equal(np.sort(pair[1]), expected):
            raise ValueError("held permutation is not complete")
    return value


def permutation_p_num(
    y_fit: Array,
    z_fit: Array,
    y_held: Array,
    z_held: Array,
    permutations: Array,
    observed_r2: float,
) -> tuple[int, Array]:
    """Return the plus-one permutation numerator, counting ties as null wins."""

    y_fit64 = np.asarray(y_fit, dtype=np.float64)
    z_fit64 = np.asarray(z_fit, dtype=np.float64)
    y_held64 = np.asarray(y_held, dtype=np.float64)
    z_held64 = np.asarray(z_held, dtype=np.float64)
    if y_fit64.ndim != 2 or y_held64.ndim != 2:
        raise ValueError("permutation responses must be matrices")
    if z_fit64.shape != (y_fit64.shape[0], 6, y_fit64.shape[1]):
        raise ValueError("fit control records have incompatible shape")
    if z_held64.shape != (y_held64.shape[0], 6, y_held64.shape[1]):
        raise ValueError("held control records have incompatible shape")
    if y_fit64.shape != y_held64.shape:
        raise ValueError("fit and held splits must have matching shapes")
    if not math.isfinite(observed_r2):
        raise ValueError("observed statistic must be finite")
    if not all(
        np.all(np.isfinite(array))
        for array in (y_fit64, z_fit64, y_held64, z_held64)
    ):
        raise ValueError("permutation inputs must be finite")

    count = y_fit64.shape[0]
    fixture = _validated_permutations(permutations, count)
    zc = z_fit64 - np.mean(z_fit64, axis=0, keepdims=True)
    yc = y_fit64 - np.mean(y_fit64, axis=0, keepdims=True)
    gram = np.einsum("irp,isp->rs", zc, zc) / float(count)
    trace = float(np.trace(gram))
    if not math.isfinite(trace) or trace <= 0.0:
        raise ScientificImplementationKill("nonpositive control Gram trace")
    ridge = RIDGE_SCALE * trace / 6.0
    system = gram + ridge * np.eye(6)
    lower = _fixed_cholesky_factor(system)
    held_v00 = trace_variance(y_held64)
    if held_v00 <= 0.0:
        raise ScientificImplementationKill("permutation held base variance is nonpositive")

    nulls = np.empty(fixture.shape[0], dtype=np.float64)
    for replicate, (fit_order, held_order) in enumerate(fixture):
        rhs = np.einsum("irp,ip->r", zc[fit_order], yc) / float(count)
        beta = _fixed_cholesky_solve_from_factor(lower, rhs)
        residual = system @ beta - rhs
        relative = float(
            np.linalg.norm(residual)
            / max(np.linalg.norm(rhs), np.finfo(float).tiny)
        )
        if not math.isfinite(relative) or relative > SOLVE_RESIDUAL_TOLERANCE:
            raise ScientificImplementationKill(
                "permutation solve residual exceeds tolerance"
            )
        corrected = apply_factorial_arms(
            y_held64, z_held64[held_order], beta
        )["11"]
        nulls[replicate] = 1.0 - trace_variance(corrected) / held_v00
    if not np.all(np.isfinite(nulls)):
        raise ScientificImplementationKill("permutation statistic is nonfinite")
    return 1 + int(np.count_nonzero(nulls >= observed_r2)), nulls


def classify_screen(
    statistics: Mapping[str, float], bootstrap_lower: float, p_num: int
) -> tuple[str, list[str]]:
    """Apply the frozen ratio-free scientific gates without outcome tuning."""

    required = ("V00", "V10", "V01", "V11")
    if any(name not in statistics for name in required):
        raise ValueError("screen statistics are incomplete")
    values = {name: float(statistics[name]) for name in required}
    if not all(
        math.isfinite(values[name]) and values[name] > 0.0
        for name in ("V00", "V10", "V01")
    ) or not (math.isfinite(values["V11"]) and values["V11"] >= 0.0):
        raise ScientificImplementationKill("screen variance is invalid")
    if not math.isfinite(bootstrap_lower):
        raise ScientificImplementationKill("bootstrap lower bound is nonfinite")
    if not isinstance(p_num, (int, np.integer)) or p_num < 1:
        raise ValueError("permutation numerator is invalid")

    reasons: list[str] = []
    if 10.0 * values["V11"] > 9.0 * values["V00"]:
        reasons.append("JOINT_R2_BELOW_0P10")
    if values["V11"] >= values["V10"]:
        reasons.append("FOURIER_PARTIAL_R2_NONPOSITIVE")
    if values["V11"] >= values["V01"]:
        reasons.append("DIPOLE_PARTIAL_R2_NONPOSITIVE")
    if bootstrap_lower <= 0.0:
        reasons.append("BOOTSTRAP_LOWER_NONPOSITIVE")
    if int(p_num) > 10:
        reasons.append("PERMUTATION_P_EXCEEDS_0P01")
    status = (
        "PASS_F05_SYNTHETIC_COVARIANCE_ONLY"
        if not reasons
        else "KILLED_F05_SYNTHETIC_COVARIANCE"
    )
    return status, reasons


def run_screen() -> dict[str, Any]:
    """Execute the fully frozen truth-free hand-network covariance screen."""

    y_fit, z_fit, fit_receipt = generate_split_records(FIT_ROTATION_SEED)
    y_held, z_held, held_receipt = generate_split_records(HELD_ROTATION_SEED)
    beta, fit_diagnostics = fit_joint_coefficients(y_fit, z_fit)
    arms = apply_factorial_arms(y_held, z_held, beta)
    statistics = held_statistics(arms)
    boot_fixture = bootstrap_indices()
    bootstrap_lower, bootstrap_values = bootstrap_joint_lower(arms, boot_fixture)
    perm_fixture = permutation_indices()
    p_num, nulls = permutation_p_num(
        y_fit,
        z_fit,
        y_held,
        z_held,
        perm_fixture,
        statistics["R2_joint"],
    )
    if y_fit.shape[0] != ROTATIONS_PER_SPLIT or y_held.shape[0] != ROTATIONS_PER_SPLIT:
        raise RuntimeError("split execution count drifted")
    if bootstrap_values.size != BOOTSTRAP_REPLICATES:
        raise RuntimeError("bootstrap replicate count drifted")
    if nulls.size != PERMUTATION_REPLICATES:
        raise RuntimeError("permutation replicate count drifted")
    status, reasons = classify_screen(statistics, bootstrap_lower, p_num)

    def payload_record(value: Array) -> dict[str, Any]:
        array = np.ascontiguousarray(value)
        return {
            "shape": list(array.shape),
            "dtype": array.dtype.str,
            "sha256_c_order_payload": sha256_payload(array),
        }

    return {
        "status": status,
        "kill_reasons": reasons,
        "beta": beta.tolist(),
        "fit_diagnostics": fit_diagnostics,
        "held_statistics": statistics,
        "realized_payloads": {
            "beta": payload_record(beta),
            "held_arm_00": payload_record(arms["00"]),
            "held_arm_10": payload_record(arms["10"]),
            "held_arm_01": payload_record(arms["01"]),
            "held_arm_11": payload_record(arms["11"]),
            "bootstrap_joint_r2": payload_record(bootstrap_values),
            "permutation_null_joint_r2": payload_record(nulls),
        },
        "bootstrap": {
            "replicates": int(bootstrap_values.size),
            "lower_order_index_zero_based": 40,
            "joint_r2_lower": bootstrap_lower,
            "minimum": float(np.min(bootstrap_values)),
            "median": float(np.median(bootstrap_values)),
            "maximum": float(np.max(bootstrap_values)),
            "indices_payload_sha256": sha256_payload(boot_fixture),
        },
        "permutation": {
            "replicates": int(nulls.size),
            "p_numerator": int(p_num),
            "p_denominator": int(nulls.size + 1),
            "null_minimum": float(np.min(nulls)),
            "null_median": float(np.median(nulls)),
            "null_maximum": float(np.max(nulls)),
            "indices_payload_sha256": sha256_payload(perm_fixture),
        },
        "fit_split": fit_receipt,
        "held_split": held_receipt,
        "execution_boundary": {
            "hand_networks": 1,
            "challenge_or_generated_networks": 0,
            "truth_or_scorer_reads": 0,
            "provider_predictions": 0,
            "worker_processes": 0,
            "scientific_scope": "truth-free deterministic d=2 synthetic covariance only",
        },
    }
