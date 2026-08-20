"""Operational, release-gated M120C protocol harness.

This module implements a generated-only component falsifier.  It deliberately
contains no command-line execution path for the binding grid: an externally
sealed manifest and explicit later authorization are prerequisites to any run.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import sys
from typing import Callable, Iterable

import numpy as np

from m120c_protocol_config import CONFIG, directional_seed, network_seed
from corrected_cp_jacobian import affine_dense_pullback, cp_affine_after_reset, cp_local_pullback, factors_to_dense
from m120c_analytic_dense_reference import (
    AnalyticReferenceFailClosed,
    analytic_dense_pullback,
    analytic_local_kernels,
    analytic_relu_gaussian_moments,
)


HERE = Path(__file__).resolve().parent
WORK_ROOT = HERE.parents[1]
CANONICAL_OUTCOME_PATH = Path(CONFIG.output_path)
CANONICAL_OUTCOME_ROOT = CANONICAL_OUTCOME_PATH.parent
if CANONICAL_OUTCOME_PATH != HERE / "out" / "M120C_EXACT_GENERATED_OUTCOME" / "m120c_binding_result.json":
    raise RuntimeError("CONFIG.output_path is not the fixed M120C canonical outcome path")
EXPECTED_SOURCE_KEYS = (
    "scorefloor_generation/m120_price_normal_ordered_adjoint/m120c_protocol_config.py",
    "scorefloor_generation/m120_price_normal_ordered_adjoint/m120c_protocol_harness.py",
    "scorefloor_generation/m120_price_normal_ordered_adjoint/run_m120c_protocol.py",
    "scorefloor_generation/m120_price_normal_ordered_adjoint/m120c_analytic_dense_reference.py",
    "scorefloor_generation/m120_price_normal_ordered_adjoint/corrected_cp_jacobian.py",
    "scorefloor_generation/m120_price_normal_ordered_adjoint/test_m120c_protocol.py",
    "scorefloor_generation/m120_price_normal_ordered_adjoint/test_m120c_operational_harness.py",
    "scorefloor_generation/m120_price_normal_ordered_adjoint/test_m120c_analytic_dense_reference.py",
    "scorefloor_generation/m120_price_normal_ordered_adjoint/test_corrected_cp_jacobian.py",
    "scorefloor_generation/fullcov_gaussian_mm/fullcov.py",
    "scorefloor_generation/adjoint_cumulant/adjoint_born.py",
)
EXPECTED_FIREWALL = (
    "generated networks only",
    "no correction oracle",
    "no source construction",
    "no public or contest outcomes",
    "no targets",
    "no scorer",
    "no champion access",
    "no target-shape efficacy execution",
)


class ProtocolFailClosed(RuntimeError):
    """Raised when a quotient would conceal a zero or near-zero reference."""


@dataclass(frozen=True)
class StandardizedState:
    """Adjoint in the gauge-invariant preactivation coordinates ``D*b,D*A*D``."""

    mean: np.ndarray
    covariance: np.ndarray
    complete_norm: float


@dataclass(frozen=True)
class SignedDirection:
    """A fixed unit direction in the combined mean/covariance adjoint space."""

    mean: np.ndarray
    covariance: np.ndarray


@dataclass(frozen=True)
class BindingMetricRecord:
    """One all-output/layer result row expected from a future bound run."""

    width: int
    depth: int
    replica: int
    layer: int
    output: int
    complete_error: float
    signed_directional_errors: np.ndarray
    reference_norm: float = float("nan")
    reference_mean: np.ndarray | None = None
    reference_covariance: np.ndarray | None = None
    approximation_mean: np.ndarray | None = None
    approximation_covariance: np.ndarray | None = None


@dataclass(frozen=True)
class StandardizedError:
    """Relative error with a signed, independently seeded directional projection."""

    reference: StandardizedState
    approximation: StandardizedState
    numerator_norm: float
    denominator_norm: float
    relative_error: float

    def signed_directional_errors(
        self, directions: Iterable[SignedDirection]
    ) -> np.ndarray:
        delta_mean = self.approximation.mean - self.reference.mean
        delta_covariance = self.approximation.covariance - self.reference.covariance
        return np.asarray(
            [
                (
                    float(np.sum(direction.mean * delta_mean))
                    + float(np.sum(direction.covariance * delta_covariance))
                )
                / self.denominator_norm
                for direction in directions
            ],
            dtype=np.float64,
        )


def _require_square_adjoint(mean: np.ndarray, covariance: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mean = np.asarray(mean, dtype=np.float64)
    covariance = np.asarray(covariance, dtype=np.float64)
    if mean.ndim != 1 or covariance.shape != (mean.size, mean.size):
        raise ValueError("mean must be a vector and covariance a matching square matrix")
    return mean, 0.5 * (covariance + covariance.T)


def standardized_state(
    mean_adjoint: np.ndarray,
    covariance_adjoint: np.ndarray,
    input_covariance: np.ndarray,
) -> StandardizedState:
    """Return the complete gauge-invariant adjoint state at one input-facing layer.

    With ``D=diag(sqrt(diag(C)))``, the state is exactly
    ``(D*b, D*A*D)``.  No epsilon is added: a variance or norm at/below
    ``1e-10`` is a fail-closed protocol violation, not a regularization choice.
    """

    mean_adjoint, covariance_adjoint = _require_square_adjoint(
        mean_adjoint, covariance_adjoint
    )
    input_covariance = np.asarray(input_covariance, dtype=np.float64)
    if input_covariance.shape != covariance_adjoint.shape:
        raise ValueError("input_covariance must match the covariance adjoint")
    variance = np.diag(input_covariance)
    if not np.all(np.isfinite(variance)) or np.any(variance <= CONFIG.fail_closed_floor):
        raise ProtocolFailClosed(
            "preactivation variance at or below 1e-10; standardized quotient is forbidden"
        )
    d = np.sqrt(variance)
    standardized_mean = d * mean_adjoint
    standardized_covariance = d[:, None] * covariance_adjoint * d[None, :]
    complete_norm = float(
        math_sqrt_sum_squares(standardized_mean, standardized_covariance)
    )
    return StandardizedState(standardized_mean, standardized_covariance, complete_norm)


def math_sqrt_sum_squares(mean: np.ndarray, covariance: np.ndarray) -> float:
    """Avoid a dependency beyond NumPy while naming the complete-adjoint norm."""

    return float(np.sqrt(np.sum(mean * mean) + np.sum(covariance * covariance)))


def standardized_complete_error(
    reference_mean: np.ndarray,
    reference_covariance_adjoint: np.ndarray,
    approximation_mean: np.ndarray,
    approximation_covariance_adjoint: np.ndarray,
    input_covariance: np.ndarray,
) -> StandardizedError:
    """Compare full and CP-base adjoints with a fail-closed invariant quotient."""

    reference = standardized_state(
        reference_mean, reference_covariance_adjoint, input_covariance
    )
    approximation = standardized_state(
        approximation_mean, approximation_covariance_adjoint, input_covariance
    )
    if reference.complete_norm <= CONFIG.fail_closed_floor:
        raise ProtocolFailClosed(
            "reference complete-adjoint norm at or below 1e-10; quotient is forbidden"
        )
    numerator = math_sqrt_sum_squares(
        approximation.mean - reference.mean,
        approximation.covariance - reference.covariance,
    )
    return StandardizedError(
        reference=reference,
        approximation=approximation,
        numerator_norm=numerator,
        denominator_norm=reference.complete_norm,
        relative_error=numerator / reference.complete_norm,
    )


def predeclared_signed_directions(width: int, depth: int, layer: int) -> tuple[SignedDirection, ...]:
    """Return outcome-independent signed unit directions from Philox `M120C-DIR-v1`.

    There is intentionally no output or measured-error argument.  Every
    terminal output and every replica receives these same predeclared directions
    for a fixed width/depth/layer coordinate.
    """

    directions: list[SignedDirection] = []
    for index in range(CONFIG.direction_count):
        rng = np.random.Generator(np.random.Philox(directional_seed(width, depth, layer, index)))
        mean = 2.0 * rng.integers(0, 2, size=width, dtype=np.int8).astype(np.float64) - 1.0
        raw_covariance = (
            2.0
            * rng.integers(0, 2, size=(width, width), dtype=np.int8).astype(np.float64)
            - 1.0
        )
        covariance = 0.5 * (raw_covariance + raw_covariance.T)
        norm = math_sqrt_sum_squares(mean, covariance)
        directions.append(SignedDirection(mean / norm, covariance / norm))
    return tuple(directions)


def transport_directions_for_permutation(
    directions: Iterable[SignedDirection], permutation: np.ndarray
) -> tuple[SignedDirection, ...]:
    """Transport fixed directions with a simultaneous hidden permutation."""

    permutation = np.asarray(permutation, dtype=np.float64)
    if permutation.ndim != 2 or permutation.shape[0] != permutation.shape[1]:
        raise ValueError("permutation must be square")
    return tuple(
        SignedDirection(
            permutation.T @ direction.mean,
            permutation.T @ direction.covariance @ permutation,
        )
        for direction in directions
    )


def simultaneous_hidden_reparameterization(
    weights: tuple[np.ndarray, ...],
    permutations: tuple[np.ndarray, ...],
    positive_gauges: tuple[np.ndarray, ...],
) -> tuple[np.ndarray, ...]:
    """Apply all hidden ``T_l=P_l diag(g_l)`` transforms at once.

    For input-output weights, ``W_0' = W_0 T_0``,
    ``W_l' = T_(l-1)^-1 W_l T_l``, and
    ``W_final' = T_last^-1 W_final``.  Positive diagonals commute through
    ReLU and the permutations only relabel hidden coordinates, so final
    preactivations are unchanged exactly in floating-point arithmetic.
    """

    raw = tuple(np.asarray(weight, dtype=np.float64) for weight in weights)
    if len(raw) < 2:
        raise ValueError("need at least one hidden ReLU and one final affine map")
    hidden = len(raw) - 1
    if len(permutations) != hidden or len(positive_gauges) != hidden:
        raise ValueError("one permutation and positive gauge are required per hidden layer")
    width = raw[0].shape[0]
    if any(weight.shape != (width, width) for weight in raw):
        raise ValueError("M120C protocol requires square fixed-width weights")
    transforms: list[np.ndarray] = []
    for permutation, gauge in zip(permutations, positive_gauges):
        permutation = validate_permutation_matrix(permutation)
        gauge = np.asarray(gauge, dtype=np.float64)
        if permutation.shape != (width, width) or gauge.shape != (width,):
            raise ValueError("hidden transform shape mismatch")
        if not np.all(np.isfinite(gauge)) or np.any(gauge <= 0.0):
            raise ValueError("hidden gauge must be finite and strictly positive")
        transforms.append(permutation @ np.diag(gauge))

    result: list[np.ndarray] = []
    for layer, weight in enumerate(raw):
        left = np.eye(width) if layer == 0 else np.linalg.inv(transforms[layer - 1])
        right = np.eye(width) if layer == hidden else transforms[layer]
        result.append(left @ weight @ right)
    return tuple(result)


def binding_plan() -> tuple[dict[str, object], ...]:
    """Describe, but do not execute, the frozen 27-network binding grid."""

    plan: list[dict[str, object]] = []
    for width in CONFIG.widths:
        for depth in CONFIG.depths:
            for replica in range(CONFIG.replicas_per_cell):
                plan.append(
                    {
                        "width": width,
                        "depth": depth,
                        "replica": replica,
                        "network_seed": network_seed(width, depth, replica),
                        "bit_generator": CONFIG.network_bit_generator,
                        "terminal_outputs": list(range(width)),
                        "direction_count": CONFIG.direction_count,
                        "global_mean_limit": CONFIG.global_mean_limit,
                        "cell_worst_output_limit": CONFIG.cell_worst_output_limit,
                    }
                )
    return tuple(plan)


def _expected_metric_keys() -> set[tuple[int, int, int, int, int]]:
    return {
        (width, depth, replica, layer, output)
        for width in CONFIG.widths
        for depth in CONFIG.depths
        for replica in range(CONFIG.replicas_per_cell)
        for layer in range(depth - 1)
        for output in range(width)
    }


def evaluate_predeclared_gates(
    records: tuple[BindingMetricRecord, ...],
) -> dict[str, object]:
    """Apply frozen gates to complete all-output records without selecting an outcome.

    A future runner must supply exactly one row for every
    `(width, depth, replica, input-facing layer, terminal output)` key.  The
    signed directional values remain in the input ledger; gates use their
    absolute magnitudes under exactly the same global/cell limits as the full
    complete-adjoint quotient.
    """

    expected = _expected_metric_keys()
    supplied = {
        (record.width, record.depth, record.replica, record.layer, record.output)
        for record in records
    }
    if len(records) != len(supplied):
        raise ProtocolFailClosed("duplicate binding metric record")
    if supplied != expected:
        missing = len(expected - supplied)
        extra = len(supplied - expected)
        raise ProtocolFailClosed(
            f"incomplete or out-of-protocol metric coverage: missing={missing}, extra={extra}"
        )

    complete_errors: list[float] = []
    directional_errors: list[float] = []
    cell_complete: dict[tuple[int, int], float] = {}
    cell_directional: dict[tuple[int, int], float] = {}
    for record in records:
        complete_error = float(record.complete_error)
        directions = np.asarray(record.signed_directional_errors, dtype=np.float64)
        if not np.isfinite(complete_error) or complete_error < 0.0:
            raise ProtocolFailClosed("non-finite or negative complete-adjoint error")
        if directions.shape != (CONFIG.direction_count,) or not np.all(np.isfinite(directions)):
            raise ProtocolFailClosed("missing/non-finite signed directional contraction")
        cell = (record.width, record.depth)
        complete_errors.append(complete_error)
        directional_errors.extend(np.abs(directions).tolist())
        cell_complete[cell] = max(cell_complete.get(cell, 0.0), complete_error)
        cell_directional[cell] = max(
            cell_directional.get(cell, 0.0), float(np.max(np.abs(directions)))
        )

    global_complete = float(np.mean(complete_errors))
    global_directional = float(np.mean(directional_errors))
    complete_cells_pass = all(
        value <= CONFIG.cell_worst_output_limit for value in cell_complete.values()
    )
    directional_cells_pass = all(
        value <= CONFIG.cell_worst_output_limit for value in cell_directional.values()
    )
    ordered_complete = {
        f"w{width}_d{depth}": cell_complete[(width, depth)]
        for width in CONFIG.widths
        for depth in CONFIG.depths
    }
    ordered_directional = {
        f"w{width}_d{depth}": cell_directional[(width, depth)]
        for width in CONFIG.widths
        for depth in CONFIG.depths
    }
    return {
        "record_count": len(records),
        "global_mean_complete_error": global_complete,
        "global_mean_absolute_directional_error": global_directional,
        "cell_worst_complete_error": ordered_complete,
        "cell_worst_absolute_directional_error": ordered_directional,
        "pass": bool(
            global_complete <= CONFIG.global_mean_limit
            and global_directional <= CONFIG.global_mean_limit
            and complete_cells_pass
            and directional_cells_pass
        ),
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest_errors(path: Path) -> tuple[str, ...]:
    """Verify the source/config hash lock without sampling or evaluating a network."""

    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return (f"manifest unavailable: {error}",)
    errors: list[str] = []
    if manifest.get("protocol_id") != CONFIG.protocol_id:
        errors.append("protocol_id mismatch")
    if manifest.get("fixed_output_path") != CONFIG.output_path:
        errors.append("fixed output path mismatch")
    if manifest.get("execution_mode") != CONFIG.execution_mode:
        errors.append("execution mode mismatch")
    if manifest.get("atomic_no_retry_claim") is not CONFIG.atomic_no_retry_claim:
        errors.append("atomic/no-retry declaration mismatch")
    expected_grid = {
        "widths": list(CONFIG.widths),
        "depths": list(CONFIG.depths),
        "replicas_per_cell": CONFIG.replicas_per_cell,
        "network_bit_generator": CONFIG.network_bit_generator,
        "direction_bit_generator": CONFIG.direction_bit_generator,
        "direction_count": CONFIG.direction_count,
        "global_mean_limit": CONFIG.global_mean_limit,
        "cell_worst_output_limit": CONFIG.cell_worst_output_limit,
        "fail_closed_floor": CONFIG.fail_closed_floor,
    }
    if manifest.get("binding_grid") != expected_grid:
        errors.append("binding grid mismatch")
    for relative, expected_hash in manifest.get("source_sha256", {}).items():
        actual_path = WORK_ROOT / relative
        if not actual_path.is_file():
            errors.append(f"missing source: {relative}")
        elif _sha256(actual_path) != expected_hash:
            errors.append(f"hash mismatch: {relative}")
    if not manifest.get("source_sha256"):
        errors.append("empty source hash binding")
    return tuple(errors)


def runtime_identity() -> dict[str, str]:
    """Return the pinned interpreter/NumPy identity for an external manifest."""

    import numpy

    executable = Path(sys.executable).resolve()
    numpy_path = Path(numpy.__file__).resolve()
    return {
        "python_executable": str(executable),
        "python_sha256": _sha256(executable),
        "python_version": sys.version.split()[0],
        "numpy_path": str(numpy_path),
        "numpy_sha256": _sha256(numpy_path),
        "numpy_version": numpy.__version__,
    }


def _require_hex_digest(value: object, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
        raise ProtocolFailClosed(f"{label} must be a lowercase SHA-256 digest")
    return value


def closed_manifest_errors(path: Path, expected_manifest_sha256: str) -> tuple[str, ...]:
    """Check an externally supplied, complete operational manifest.

    The expected raw manifest digest is supplied by the caller's independent
    release.  This checker deliberately does not create or rewrite a manifest.
    """

    try:
        expected_manifest_sha256 = _require_hex_digest(expected_manifest_sha256, "expected manifest hash")
        raw = path.read_bytes()
        manifest = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ProtocolFailClosed) as error:
        return (f"manifest unavailable or invalid: {error}",)
    errors: list[str] = []
    if hashlib.sha256(raw).hexdigest() != expected_manifest_sha256:
        errors.append("external manifest hash mismatch")
    if manifest.get("schema") != 2 or manifest.get("manifest_status") != "OPERATIONAL_SEALED":
        errors.append("operational manifest schema/status mismatch")
    expected_fields = {
        "schema", "manifest_status", "protocol_id", "fixed_output_path", "execution_mode",
        "atomic_no_retry_claim", "binding_grid", "firewall", "runtime_identity", "source_sha256",
    }
    if set(manifest) != expected_fields:
        errors.append("manifest root field set mismatch")
    if manifest.get("protocol_id") != CONFIG.protocol_id:
        errors.append("protocol_id mismatch")
    if manifest.get("fixed_output_path") != CONFIG.output_path:
        errors.append("fixed output path mismatch")
    if manifest.get("execution_mode") != CONFIG.execution_mode:
        errors.append("execution mode mismatch")
    if manifest.get("atomic_no_retry_claim") is not True:
        errors.append("atomic/no-retry declaration mismatch")
    expected_grid = {
        "widths": list(CONFIG.widths), "depths": list(CONFIG.depths),
        "replicas_per_cell": CONFIG.replicas_per_cell,
        "network_bit_generator": CONFIG.network_bit_generator,
        "direction_bit_generator": CONFIG.direction_bit_generator,
        "direction_count": CONFIG.direction_count,
        "global_mean_limit": CONFIG.global_mean_limit,
        "cell_worst_output_limit": CONFIG.cell_worst_output_limit,
        "fail_closed_floor": CONFIG.fail_closed_floor,
    }
    if manifest.get("binding_grid") != expected_grid:
        errors.append("binding grid mismatch")
    if tuple(manifest.get("firewall", ())) != EXPECTED_FIREWALL:
        errors.append("firewall mismatch")
    if manifest.get("runtime_identity") != runtime_identity():
        errors.append("runtime identity mismatch")
    source_hashes = manifest.get("source_sha256")
    if not isinstance(source_hashes, dict) or tuple(sorted(source_hashes)) != tuple(sorted(EXPECTED_SOURCE_KEYS)):
        errors.append("source binding key set mismatch")
    else:
        for relative in EXPECTED_SOURCE_KEYS:
            value = source_hashes.get(relative)
            try:
                expected = _require_hex_digest(value, f"source hash for {relative}")
            except ProtocolFailClosed as error:
                errors.append(str(error))
                continue
            source = WORK_ROOT / relative
            if not source.is_file() or _sha256(source) != expected:
                errors.append(f"hash mismatch: {relative}")
    return tuple(errors)


def _validate_job(job: dict[str, object]) -> tuple[int, int, int, int]:
    try:
        width = int(job["width"])
        depth = int(job["depth"])
        replica = int(job["replica"])
        seed = int(job["network_seed"])
    except (KeyError, TypeError, ValueError) as error:
        raise ProtocolFailClosed("malformed binding job") from error
    if job.get("bit_generator") != "Philox" or seed != network_seed(width, depth, replica):
        raise ProtocolFailClosed("job is not one exact predeclared Philox binding job")
    if {"width", "depth", "replica", "network_seed", "bit_generator"} - set(job):
        raise ProtocolFailClosed("binding job omitted a required identity field")
    return width, depth, replica, seed


def generated_weights(job: dict[str, object]) -> tuple[np.ndarray, ...]:
    """Generate one and only one frozen network using its declared Philox seed."""

    width, depth, _replica, seed = _validate_job(job)
    rng = np.random.Generator(np.random.Philox(seed))
    return tuple(
        rng.normal(0.0, math.sqrt(2.0 / width), size=(width, width)).astype(np.float64)
        for _ in range(depth)
    )


def validate_permutation_matrix(permutation: np.ndarray) -> np.ndarray:
    """Reject a merely square matrix; a representation check needs a permutation."""

    matrix = np.asarray(permutation, dtype=np.float64)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1] or not np.all(np.isfinite(matrix)):
        raise ProtocolFailClosed("permutation must be finite and square")
    if not np.array_equal(matrix, np.round(matrix)) or not np.all((matrix == 0.0) | (matrix == 1.0)):
        raise ProtocolFailClosed("permutation must contain only zero/one entries")
    if not np.array_equal(np.sum(matrix, axis=0), np.ones(matrix.shape[0])) or not np.array_equal(np.sum(matrix, axis=1), np.ones(matrix.shape[0])):
        raise ProtocolFailClosed("permutation rows and columns must each sum to one")
    return matrix


def _analytic_background(weights: tuple[np.ndarray, ...]) -> tuple[list[tuple[np.ndarray, np.ndarray]], np.ndarray, np.ndarray]:
    width = weights[0].shape[0]
    if len(weights) < 2 or any(weight.shape != (width, width) for weight in weights):
        raise ProtocolFailClosed("M120C requires square weights with a hidden ReLU and final affine map")
    mean = np.zeros(width, dtype=np.float64)
    covariance = np.eye(width, dtype=np.float64)
    layers: list[tuple[np.ndarray, np.ndarray]] = []
    try:
        for weight in weights[:-1]:
            mean = mean @ weight
            covariance = weight.T @ covariance @ weight
            covariance = 0.5 * (covariance + covariance.T)
            layers.append((mean, covariance))
            mean, covariance = analytic_relu_gaussian_moments(mean, covariance)
        final_mean = mean @ weights[-1]
        final_covariance = weights[-1].T @ covariance @ weights[-1]
        return layers, final_mean, 0.5 * (final_covariance + final_covariance.T)
    except AnalyticReferenceFailClosed as error:
        raise ProtocolFailClosed(f"analytic reference rejected generated state: {error}") from error


def _terminal_adjoint(final_mean: np.ndarray, final_covariance: np.ndarray, final_weight: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    variance = np.diag(final_covariance)
    if not np.all(np.isfinite(variance)) or np.any(variance <= CONFIG.fail_closed_floor):
        raise ProtocolFailClosed("terminal variance at or below fail-closed floor")
    sigma = np.sqrt(variance)
    alpha = final_mean / sigma
    probability = np.asarray([0.5 * math.erfc(-float(value) / math.sqrt(2.0)) for value in alpha])
    density = np.exp(-0.5 * alpha * alpha) / math.sqrt(2.0 * math.pi)
    return final_weight * probability[None, :], final_weight, np.diag(density / (2.0 * sigma))


def metric_records_for_generated_network(job: dict[str, object], *, weights: tuple[np.ndarray, ...] | None = None, directions_by_layer: dict[int, tuple[SignedDirection, ...]] | None = None) -> tuple[BindingMetricRecord, ...]:
    """Evaluate one generated job through analytic dense and CP-base reverses.

    This is deliberately a per-job primitive; it does not execute the 27-job
    grid or write an outcome.  The exact grid dispatcher below is the only
    caller that aggregates all jobs.
    """

    width, depth, replica, _seed = _validate_job(job)
    raw = generated_weights(job) if weights is None else tuple(np.asarray(item, dtype=np.float64) for item in weights)
    if len(raw) != depth or any(item.shape != (width, width) for item in raw):
        raise ProtocolFailClosed("generated weight shape/depth mismatch")
    layers, final_mean, final_covariance = _analytic_background(raw)
    b_exact, u_cp, g_cp = _terminal_adjoint(final_mean, final_covariance, raw[-1])
    a_exact = factors_to_dense(u_cp, g_cp)
    b_cp = b_exact.copy()
    records: list[BindingMetricRecord] = []
    for layer in range(depth -2, -1, -1):
        mean, covariance = layers[layer]
        try:
            kernels = analytic_local_kernels(mean, covariance)
            b_exact, a_exact = analytic_dense_pullback(b_exact, a_exact, kernels)
        except AnalyticReferenceFailClosed as error:
            raise ProtocolFailClosed(f"analytic dense pullback rejected layer {layer}: {error}") from error
        cp = cp_local_pullback(b_cp, u_cp, g_cp, kernels)
        u_here, g_here = cp.factors_here()
        a_cp = factors_to_dense(u_here, g_here)
        directions = (directions_by_layer or {}).get(layer, predeclared_signed_directions(width, depth, layer))
        if len(directions) != CONFIG.direction_count:
            raise ProtocolFailClosed("direction schedule does not contain four predeclared directions")
        for output in range(width):
            error = standardized_complete_error(
                b_exact[:, output], a_exact[output], cp.mean_adjoint[:, output], a_cp[output], covariance
            )
            signed = error.signed_directional_errors(directions)
            records.append(BindingMetricRecord(
                width, depth, replica, layer, output, error.relative_error, signed,
                error.denominator_norm, error.reference.mean, error.reference.covariance,
                error.approximation.mean, error.approximation.covariance,
            ))
        if layer:
            b_exact, a_exact = affine_dense_pullback(raw[layer], b_exact, a_exact)
            b_cp, u_cp, g_cp = cp_affine_after_reset(raw[layer], cp)
        else:
            b_cp, u_cp, g_cp = cp.mean_adjoint, u_here, g_here
    expected = (depth - 1) * width
    if len(records) != expected:
        raise ProtocolFailClosed("per-job layer/output record count mismatch")
    return tuple(records)


def all_generated_metric_records() -> tuple[BindingMetricRecord, ...]:
    """The uncalled exact 27-job dispatcher; it rejects count/identity drift."""

    plan = binding_plan()
    if len(plan) != 27 or len({int(job["network_seed"]) for job in plan}) != 27:
        raise ProtocolFailClosed("binding plan must contain exactly 27 unique jobs")
    for job in plan:
        validate_operational_reparameterization(job)
    records = tuple(record for job in plan for record in metric_records_for_generated_network(job))
    if len(records) != 648:
        raise ProtocolFailClosed("binding dispatcher did not produce exactly 648 layer-output records")
    return records


def record_as_json(record: BindingMetricRecord) -> dict[str, object]:
    """Make a complete, signed, JSON-safe ledger row without selecting an outcome."""

    if any(value is None for value in (record.reference_mean, record.reference_covariance, record.approximation_mean, record.approximation_covariance)):
        raise ProtocolFailClosed("binding record omitted standardized-state evidence")
    return {
        "width": record.width,
        "depth": record.depth,
        "replica": record.replica,
        "layer": record.layer,
        "output": record.output,
        "complete_error": record.complete_error,
        "reference_norm": record.reference_norm,
        "signed_directional_errors": np.asarray(record.signed_directional_errors, dtype=np.float64).tolist(),
        "reference_standardized_mean": np.asarray(record.reference_mean, dtype=np.float64).tolist(),
        "reference_standardized_covariance": np.asarray(record.reference_covariance, dtype=np.float64).tolist(),
        "cp_standardized_mean": np.asarray(record.approximation_mean, dtype=np.float64).tolist(),
        "cp_standardized_covariance": np.asarray(record.approximation_covariance, dtype=np.float64).tolist(),
    }


def _scheduled_hidden_transforms(job: dict[str, object]) -> tuple[tuple[np.ndarray, ...], tuple[np.ndarray, ...]]:
    width, depth, _replica, seed = _validate_job(job)
    rng = np.random.Generator(np.random.Philox(seed ^ 0x4D31323043))
    permutations = tuple(np.eye(width)[:, rng.permutation(width)] for _ in range(depth - 1))
    gauges = tuple(np.exp(rng.uniform(-0.35, 0.35, size=width)) for _ in range(depth - 1))
    return permutations, gauges


def validate_operational_reparameterization(job: dict[str, object]) -> None:
    """Run actual analytic-dense and CP reverses under frozen P*diag(g) transforms."""

    raw = generated_weights(job)
    permutations, gauges = _scheduled_hidden_transforms(job)
    checked = tuple(validate_permutation_matrix(matrix) for matrix in permutations)
    transformed = simultaneous_hidden_reparameterization(raw, checked, gauges)
    width, depth, _replica, _seed = _validate_job(job)
    transported = {
        layer: transport_directions_for_permutation(
            predeclared_signed_directions(width, depth, layer), checked[layer]
        )
        for layer in range(depth - 1)
    }
    baseline = metric_records_for_generated_network(job, weights=raw)
    observed = metric_records_for_generated_network(job, weights=transformed, directions_by_layer=transported)
    if len(baseline) != len(observed):
        raise ProtocolFailClosed("representation check changed record coverage")
    for left, right in zip(baseline, observed):
        if (left.width, left.depth, left.replica, left.layer, left.output) != (right.width, right.depth, right.replica, right.layer, right.output):
            raise ProtocolFailClosed("representation check reordered records")
        if abs(left.complete_error - right.complete_error) > 1e-10:
            raise ProtocolFailClosed("representation check changed complete error")
        if np.max(np.abs(left.signed_directional_errors - right.signed_directional_errors)) > 1e-10:
            raise ProtocolFailClosed("representation check changed signed directional contraction")
        permutation = checked[left.layer]
        for before_mean, after_mean in (
            (left.reference_mean, right.reference_mean),
            (left.approximation_mean, right.approximation_mean),
        ):
            if np.linalg.norm(np.asarray(after_mean) - permutation.T @ np.asarray(before_mean)) > 1e-10:
                raise ProtocolFailClosed("representation check changed standardized mean state")
        for before_covariance, after_covariance in (
            (left.reference_covariance, right.reference_covariance),
            (left.approximation_covariance, right.approximation_covariance),
        ):
            expected = permutation.T @ np.asarray(before_covariance) @ permutation
            if np.linalg.norm(np.asarray(after_covariance) - expected) > 1e-10:
                raise ProtocolFailClosed("representation check changed standardized covariance state")


class AtomicLifecycle:
    """One-shot claim and terminal publication, used only by the uncalled runner."""

    def __init__(
        self,
        root: Path = CANONICAL_OUTCOME_ROOT,
        *,
        fault_injector: Callable[[str], None] | None = None,
    ) -> None:
        self.root = Path(root)
        self.claim_path = self.root / "M120C_CLAIM.json"
        self.outcome_path = self.root / CANONICAL_OUTCOME_PATH.name
        self.terminal_path = self.root / "M120C_TERMINAL.json"
        self.outcome_pending_path = self.root / f".{self.outcome_path.name}.pending"
        self.terminal_pending_path = self.root / f".{self.terminal_path.name}.pending"
        self._fault_injector = fault_injector

    @staticmethod
    def _canonical_bytes(payload: dict[str, object]) -> bytes:
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n"

    @staticmethod
    def _write_bytes_exclusive(path: Path, data: bytes) -> None:
        descriptor = os.open(
            path,
            os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_BINARY", 0),
        )
        try:
            view = memoryview(data)
            offset = 0
            while offset < len(view):
                remaining = len(view) - offset
                try:
                    written = os.write(descriptor, view[offset:])
                except InterruptedError:
                    continue
                if type(written) is not int or written <= 0 or written > remaining:
                    raise ProtocolFailClosed(
                        "exclusive artifact write returned an invalid byte count"
                    )
                offset += written
            os.fsync(descriptor)
        finally:
            os.close(descriptor)

    @classmethod
    def _write_exclusive(cls, path: Path, payload: dict[str, object]) -> None:
        cls._write_bytes_exclusive(path, cls._canonical_bytes(payload))

    def _inject(self, stage: str) -> None:
        if self._fault_injector is not None:
            self._fault_injector(stage)

    def _require_clean_claimed_state(self) -> None:
        if not self.claim_path.is_file():
            raise ProtocolFailClosed("outcome publication requires a permanent claim")
        publication_paths = (
            self.outcome_path,
            self.terminal_path,
            self.outcome_pending_path,
            self.terminal_pending_path,
        )
        if any(path.exists() for path in publication_paths):
            raise ProtocolFailClosed("outcome publication already started; no retry is allowed")

    def claim(self, payload: dict[str, object]) -> Path:
        try:
            self.root.mkdir(parents=True, exist_ok=False)
        except FileExistsError as error:
            raise ProtocolFailClosed("canonical root already exists; no retry is allowed") from error
        try:
            self._write_exclusive(self.claim_path, payload)
        except FileExistsError as error:
            raise ProtocolFailClosed("claim already exists; no retry is allowed") from error
        return self.claim_path

    def publish_outcome(self, payload: dict[str, object], status: str) -> Path:
        """Publish one canonical outcome, then a hash-bound terminal marker.

        Any pending or final publication artifact permanently blocks a second
        attempt.  If interruption occurs after the outcome is committed but
        before the terminal rename, the sole outcome remains authoritative and
        the pending terminal is auditable; no failure outcome is layered on top.
        """

        if status not in {"pass", "fail", "error"}:
            raise ProtocolFailClosed("terminal status must be pass, fail, or error")
        self._require_clean_claimed_state()
        outcome_bytes = self._canonical_bytes(payload)
        terminal = {
            "outcome_filename": self.outcome_path.name,
            "outcome_sha256": hashlib.sha256(outcome_bytes).hexdigest(),
            "status": status,
        }
        terminal_bytes = self._canonical_bytes(terminal)
        try:
            self._write_bytes_exclusive(self.outcome_pending_path, outcome_bytes)
            self._inject("after_outcome_pending")
            self._write_bytes_exclusive(self.terminal_pending_path, terminal_bytes)
            self._inject("after_terminal_pending")
            os.replace(self.outcome_pending_path, self.outcome_path)
            self._inject("after_outcome_replace")
            os.replace(self.terminal_pending_path, self.terminal_path)
            self._inject("after_terminal_replace")
        except FileExistsError as error:
            raise ProtocolFailClosed("publication artifact already exists; no retry is allowed") from error
        return self.outcome_path


def main() -> None:
    raise SystemExit(
        "M120C has no CLI execution path: the binding grid has not been authorized or executed. "
        "An externally sealed manifest and explicit future authorization are required."
    )


if __name__ == "__main__":
    main()
