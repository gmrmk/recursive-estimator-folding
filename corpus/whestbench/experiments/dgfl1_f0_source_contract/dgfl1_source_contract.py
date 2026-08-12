"""Fail-closed source contracts for a prospective DGFL sidecar.

This is not an estimator.  It contains only source/hash inspection, invocation
state, selected-row geometry, and coordinate transforms needed to decide
whether a production implementation can be written without silently changing
the incumbent GUARDS provider.
"""

from __future__ import annotations

import ast
import hashlib
from pathlib import Path
from typing import Mapping, Sequence

import numpy as np


Array = np.ndarray
BASE_BRANCHES = ("healthy", "m186", "m187")
DGFL_BASE_LABELS = tuple(
    (index * 126 // 32) * 256 + ((73 * index) % 256) for index in range(32)
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _haar_calls(path: Path) -> list[ast.Call]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "_haar_rotation"
    ]


class ParentSourceContract:
    """Verify immutable parent bytes and the instance-dispatched Q seam."""

    def __init__(self, parent: Path, expected_hashes: Mapping[str, str]) -> None:
        self.parent = Path(parent)
        self.expected_hashes = {
            str(name): str(digest).upper() for name, digest in expected_hashes.items()
        }

    @staticmethod
    def _require_self_dispatch(calls: Sequence[ast.Call], label: str) -> None:
        if len(calls) != 1:
            raise RuntimeError(f"{label} must contain exactly one Q construction")
        target = calls[0].func
        assert isinstance(target, ast.Attribute)
        if not isinstance(target.value, ast.Name) or target.value.id != "self":
            raise RuntimeError(f"{label} Q construction bypasses instance dispatch")

    def verify(self) -> dict[str, object]:
        observed: dict[str, str] = {}
        for name, expected in self.expected_hashes.items():
            path = self.parent / name
            if not path.is_file():
                raise RuntimeError(f"missing parent source: {name}")
            digest = _sha256(path)
            if digest != expected:
                raise RuntimeError(f"parent source hash drift: {name}")
            observed[name] = digest

        production_calls = _haar_calls(self.parent / "kerdock_v3_estimator.py")
        guard_calls = _haar_calls(self.parent / "estimator.py")
        self._require_self_dispatch(production_calls, "production source")
        self._require_self_dispatch(guard_calls, "guard source")
        return {
            "parent_hashes": observed,
            "production_q_calls": len(production_calls),
            "guard_q_calls": len(guard_calls),
            "calls_through_self": True,
        }


class ProductionRotationCapture:
    """Retain the first production rotation and detect guard regeneration drift."""

    def __init__(self) -> None:
        self._active = False
        self._token: str | None = None
        self._seed: int | None = None
        self._width: int | None = None
        self._production_q: Array | None = None
        self._bytes: bytes | None = None
        self.calls = 0

    @property
    def production_q(self) -> Array:
        if self._production_q is None:
            raise RuntimeError("production Q has not been captured")
        return self._production_q

    def begin(self, token: str) -> None:
        if self._active:
            raise RuntimeError("an invocation is already active")
        if not token:
            raise ValueError("invocation token must be nonempty")
        self._active = True
        self._token = str(token)
        self._seed = None
        self._width = None
        self._production_q = None
        self._bytes = None
        self.calls = 0

    def observe(self, *, seed: int, width: int, rotation: Array) -> Array:
        if not self._active:
            raise RuntimeError("rotation observed outside an active invocation")
        original = rotation
        value = np.asarray(rotation)
        if value.shape != (int(width), int(width)):
            raise RuntimeError("rotation shape drift")
        if not np.all(np.isfinite(value)):
            raise RuntimeError("rotation contains nonfinite values")
        raw = value.tobytes(order="C")
        self.calls += 1

        if self._production_q is None:
            self._seed = int(seed)
            self._width = int(width)
            self._production_q = original
            self._bytes = raw
            return original

        if int(seed) != self._seed or int(width) != self._width:
            raise RuntimeError("production-Q seed or width drift")
        if value.dtype != np.asarray(self._production_q).dtype or raw != self._bytes:
            raise RuntimeError("production-Q byte drift")
        return original

    def end(self) -> dict[str, int | str]:
        """Return non-array metadata and release all invocation-local Q state."""

        if not self._active:
            raise RuntimeError("no invocation is active")
        summary: dict[str, int | str] = {
            "token": self._token or "",
            "calls": int(self.calls),
            "seed": -1 if self._seed is None else int(self._seed),
            "width": -1 if self._width is None else int(self._width),
        }
        self._active = False
        self._token = None
        self._seed = None
        self._width = None
        self._production_q = None
        self._bytes = None
        self.calls = 0
        return summary


class PostQReturnGate:
    """Model the no-silent-fallback rule around a complete base return."""

    def __init__(self) -> None:
        self.phase = "new"
        self.branch: str | None = None
        self.failure: str | None = None

    def begin(self) -> None:
        if self.phase != "new":
            raise RuntimeError("invocation already started")
        self.phase = "pre_q"

    def return_pre_q_w0(self, reason: str) -> str:
        if self.phase != "pre_q":
            raise RuntimeError("post-Q paths may not silently return W0")
        if not reason:
            raise ValueError("pre-Q return reason must be nonempty")
        self.phase = "returned_pre_q_w0"
        return "w0"

    def capture_q(self) -> None:
        if self.phase != "pre_q":
            raise RuntimeError("Q capture has invalid chronology")
        self.phase = "q_captured"

    def accept_base(self, branch: str) -> None:
        if self.phase != "q_captured":
            raise RuntimeError("base output has invalid chronology")
        if branch not in BASE_BRANCHES:
            raise ValueError("unknown complete base branch")
        self.branch = branch
        self.phase = "base_complete"

    def accept_complete_correction(self) -> None:
        if self.phase != "base_complete":
            raise RuntimeError("correction has invalid chronology")
        self.phase = "correction_complete"

    def provider_failure(self, reason: str) -> None:
        if self.phase not in {"q_captured", "base_complete", "correction_complete"}:
            raise RuntimeError("provider failure has invalid chronology")
        if not reason:
            raise ValueError("provider failure reason must be nonempty")
        self.failure = reason
        self.phase = "provider_failure"

    def return_complete(self) -> str:
        if self.phase == "provider_failure":
            raise RuntimeError("provider failure cannot return a scientific output")
        if self.phase != "correction_complete" or self.branch is None:
            raise RuntimeError("complete correction is required after production Q")
        self.phase = "returned_complete"
        return self.branch


def fixed_antipodal_pairs(
    base_labels: Sequence[int], *, total_base_rows: int
) -> tuple[tuple[int, int], ...]:
    """Return immutable `(base, antipode)` labels with strict coverage checks."""

    if total_base_rows <= 0:
        raise ValueError("total_base_rows must be positive")
    labels = tuple(int(label) for label in base_labels)
    if not labels:
        raise ValueError("base_labels must be nonempty")
    if len(set(labels)) != len(labels):
        raise ValueError("base_labels must be unique")
    if any(label < 0 or label >= total_base_rows for label in labels):
        raise ValueError("base label outside the parent design")
    return tuple((label, label + total_base_rows) for label in labels)


def selected_parent_order(
    base_labels: Sequence[int], *, total_base_rows: int
) -> tuple[int, ...]:
    """Return W0's positive-bank-then-antipode order for a fixed subset."""

    pairs = fixed_antipodal_pairs(base_labels, total_base_rows=total_base_rows)
    positives = tuple(pair[0] for pair in pairs)
    negatives = tuple(pair[1] for pair in pairs)
    return positives + negatives


def build_selected_unit_rows(
    hadamard: Array,
    phases: Array,
    production_q: Array,
    base_labels: Sequence[int],
) -> Array:
    """Construct selected physical rows `H_j diag(p_s) Q.T` in label order."""

    h = np.asarray(hadamard, dtype=np.float64)
    p = np.asarray(phases, dtype=np.float64)
    q = np.asarray(production_q, dtype=np.float64)
    if h.ndim != 2 or h.shape[0] != h.shape[1]:
        raise ValueError("hadamard must be square")
    dimension = h.shape[0]
    if p.ndim != 2 or p.shape[1] != dimension:
        raise ValueError("phase table has incompatible shape")
    if q.shape != (dimension, dimension):
        raise ValueError("production Q has incompatible shape")
    if not (np.all(np.isfinite(h)) and np.all(np.isfinite(p)) and np.all(np.isfinite(q))):
        raise ValueError("row-construction inputs must be finite")

    labels = tuple(int(label) for label in base_labels)
    total = p.shape[0] * dimension
    if not labels or len(set(labels)) != len(labels):
        raise ValueError("base labels must be nonempty and unique")
    if any(label < 0 or label >= total for label in labels):
        raise ValueError("base label outside the phase/frame table")

    rows = []
    for label in labels:
        frame, row = divmod(label, dimension)
        rows.append((h[row] * p[frame]) @ q.T)
    result = np.stack(rows)
    norms = np.sum(result * result, axis=1)
    if not np.allclose(norms, 1.0, rtol=0.0, atol=5e-12):
        raise RuntimeError("selected physical rows are not unit length")
    return result


def rotation_generator(m: Array, b: Array) -> Array:
    """Return the oriented rank-two generator `J = b m.T - m b.T`."""

    m64 = np.asarray(m, dtype=np.float64)
    b64 = np.asarray(b, dtype=np.float64)
    if m64.ndim != 1 or b64.shape != m64.shape:
        raise ValueError("m and b must be equal-shaped vectors")
    if not (np.all(np.isfinite(m64)) and np.all(np.isfinite(b64))):
        raise ValueError("m and b must be finite")
    if not np.isclose(m64 @ m64, 1.0, rtol=0.0, atol=1e-13):
        raise ValueError("m must be unit")
    if not np.isclose(b64 @ b64, 1.0, rtol=0.0, atol=1e-13):
        raise ValueError("b must be unit")
    if not np.isclose(m64 @ b64, 0.0, rtol=0.0, atol=1e-13):
        raise ValueError("m and b must be orthogonal")
    return np.outer(b64, m64) - np.outer(m64, b64)


def absorbed_generator(production_q: Array, physical_j: Array) -> Array:
    """Transport a physical column generator into W0's absorbed-Q coordinates."""

    q = np.asarray(production_q, dtype=np.float64)
    j = np.asarray(physical_j, dtype=np.float64)
    if q.ndim != 2 or q.shape[0] != q.shape[1] or j.shape != q.shape:
        raise ValueError("Q and J must be equal-shaped square matrices")
    if not (np.all(np.isfinite(q)) and np.all(np.isfinite(j))):
        raise ValueError("Q and J must be finite")
    if not np.allclose(q.T @ q, np.eye(q.shape[0]), rtol=0.0, atol=5e-12):
        raise ValueError("Q must be orthogonal")
    if not np.allclose(j + j.T, 0.0, rtol=0.0, atol=1e-13):
        raise ValueError("J must be skew-symmetric")
    result = q.T @ j @ q
    return (result - result.T) / 2.0


def replay_cost_orientation(
    *, replay_dtype: str, trigonometry_dtype: str
) -> dict[str, object]:
    """Return a closed-component subtotal that deliberately fails open items.

    The result is an orientation, not a complete path upper bound.  It is kept
    executable so a later source cannot silently omit the dominant primal/JVP
    work or change dtype pricing.
    """

    if replay_dtype not in {"float32", "float64"}:
        raise ValueError("replay_dtype must be float32 or float64")
    if trigonometry_dtype not in {"float32", "float64"}:
        raise ValueError("trigonometry_dtype must be float32 or float64")

    rate = 1 if replay_dtype == "float32" else 2
    components: dict[str, int] = {
        "selected_rows_v_times_qt_float64": 16_744_448,
        "primal_32_matmuls": 267_911_168 * rate,
        "tangent_32_matmuls": 267_911_168 * rate,
        "relu_mask_and_tangent_mask": 1_572_864 * rate,
        "rank2_initial_tangent_and_radius": 147_328 * rate,
        "four_axis_primal_tangent_projections": 261_632 * rate,
        "fused_control_and_canonical_reduction": 2_097_152 * rate,
        "fourier_sin_cos": 16_384
        * (2 if trigonometry_dtype == "float64" else 1),
    }
    if replay_dtype == "float32":
        components["selected_rows_float64_to_float32"] = 32_768

    unresolved = (
        "pilot_A_source_and_bill",
        "axis_and_modulator_casts",
        "route_certificate",
        "coefficient_application_and_finite_guards",
        "cleanup_and_return",
        "inherited_W0_worst_case_prefix",
        "wall_time_upper",
        "allocator_and_process_RSS_upper",
        "official_Phase2_meter_and_resource_rules",
    )
    return {
        "components": components,
        "subtotal": int(sum(components.values())),
        "unresolved": unresolved,
        "complete_upper_bound": False,
        "authorizes_generated_execution": False,
    }
