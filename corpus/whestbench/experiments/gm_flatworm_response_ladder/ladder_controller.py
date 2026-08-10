"""Two-lane flatworm depth controller for q3 response geometry (ledger idx 33).

Frozen sources are imported read-only and never edited.  Only this file and the
runner in this directory are new.
"""

from __future__ import annotations

import importlib.util
import math
from pathlib import Path
import sys
import types

import numpy as np


FROZEN_ROOT = Path(
    r"C:\Users\strid\Documents\Codex\2026-08-02"
    r"\https-chatgpt-com-share-6a5556ed-2e1c\work\scorefloor_generation"
)
PARENT_DIR = FROZEN_ROOT / "latent_randomized_radial"
H18_DIR = FROZEN_ROOT / "randomized_radial_susceptibility_compressor"
DUAL_DIR = FROZEN_ROOT / "randomized_radial_dual_observable_compressor"
FLATWORM_DIR = FROZEN_ROOT / "flatworm_ladder_attenuator"


def _load(name: str, path: Path) -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


for _dir in (PARENT_DIR, H18_DIR, DUAL_DIR):
    if str(_dir) not in sys.path:
        sys.path.insert(0, str(_dir))

rr = _load("randomized_radial", PARENT_DIR / "randomized_radial.py")
sc = _load("susceptibility_compressor", H18_DIR / "susceptibility_compressor.py")
h18 = _load("h18_runner", H18_DIR / "run_one_step_gate.py")
doc = _load("dual_observable_compressor", DUAL_DIR / "dual_observable_compressor.py")

GaussianComponent = rr.GaussianComponent

# Constants inherited verbatim from the frozen flatworm ladder operator.
_flatworm_text = (FLATWORM_DIR / "flatworm_ladder.py").read_text(encoding="utf-8")
RHO = 0.5
KAPPA = 0.25
assert "\nRHO = 0.5\n" in _flatworm_text and "\nKAPPA = 0.25\n" in _flatworm_text

POWER_ITERATIONS = 64
EIGENGAP_TOLERANCE = sc.EIGENGAP_TOLERANCE


def _normal_pdf(values: np.ndarray) -> np.ndarray:
    return np.exp(-0.5 * values * values) / math.sqrt(2.0 * math.pi)


def _normal_cdf(values: np.ndarray) -> np.ndarray:
    flat = np.ravel(values)
    result = np.fromiter(
        (0.5 * (1.0 + math.erf(float(value) / math.sqrt(2.0))) for value in flat),
        dtype=np.float64,
        count=flat.size,
    )
    return result.reshape(values.shape)


def lane_geometry(
    components: list, next_weight: np.ndarray
) -> dict[str, object]:
    """Both response lanes in correlation coordinates (idx-27 formulas)."""
    mean, covariance = rr.mixture_moments(components)
    pre_mean = mean @ next_weight
    pre_covariance = next_weight.T @ covariance @ next_weight
    pre_covariance = 0.5 * (pre_covariance + pre_covariance.T)
    variances = np.maximum(np.diag(pre_covariance), 0.0)
    sigma = np.sqrt(variances)
    positive = sigma > 64.0 * np.finfo(np.float64).eps * max(float(np.max(sigma)), 1.0)
    inverse_sigma = np.zeros_like(sigma)
    inverse_sigma[positive] = 1.0 / sigma[positive]
    alpha = np.zeros_like(pre_mean)
    alpha[positive] = pre_mean[positive] * inverse_sigma[positive]
    correlation = (inverse_sigma[:, None] * pre_covariance) * inverse_sigma[None, :]
    correlation = 0.5 * (correlation + correlation.T)

    gate_response = np.zeros_like(pre_mean)
    active_response = np.zeros_like(pre_mean)
    gate_response[positive] = _normal_pdf(alpha[positive])
    active_response[positive] = _normal_cdf(alpha[positive])
    gate_gram = (gate_response[:, None] * correlation) * gate_response[None, :]
    active_gram = (active_response[:, None] * correlation) * active_response[None, :]
    gate_gram = 0.5 * (gate_gram + gate_gram.T)
    active_gram = 0.5 * (active_gram + active_gram.T)
    gate_trace = float(np.trace(gate_gram))
    active_trace = float(np.trace(active_gram))
    return {
        "gate_gram": gate_gram,
        "active_gram": active_gram,
        "gate_trace": gate_trace,
        "active_trace": active_trace,
        "correlation": correlation,
        "inverse_sigma": inverse_sigma,
        "degenerate": gate_trace <= 0.0 or active_trace <= 0.0,
    }


def power_top_eigenvalue(gram: np.ndarray, iterations: int = POWER_ITERATIONS) -> float:
    """Permutation-equivariant fixed-budget top eigenvalue (deployed form)."""
    width = gram.shape[0]
    vector = np.ones(width, dtype=np.float64) / math.sqrt(width)
    for _ in range(iterations):
        nxt = gram @ vector
        norm = float(np.linalg.norm(nxt))
        if not np.isfinite(norm) or norm == 0.0:
            return 0.0
        vector = nxt / norm
    return float(vector @ gram @ vector)


def lane_evidence(geometry: dict[str, object]) -> dict[str, float]:
    """e_l = lambda_max(G_l)/tr(G_l), power-iteration form plus exact diagnostic."""
    out: dict[str, float] = {}
    for name, gram_key, trace_key in (
        ("gate", "gate_gram", "gate_trace"),
        ("active", "active_gram", "active_trace"),
    ):
        gram = geometry[gram_key]
        trace = float(geometry[trace_key])
        if trace <= 0.0:
            out[f"{name}_evidence"] = 0.0
            out[f"{name}_evidence_exact"] = 0.0
            continue
        out[f"{name}_evidence"] = power_top_eigenvalue(gram) / trace
        out[f"{name}_evidence_exact"] = float(np.max(np.linalg.eigvalsh(gram))) / trace
    return out


def commissural(memory: np.ndarray) -> np.ndarray:
    """(I - KAPPA*L) with L the two-lane pair Laplacian."""
    laplacian = np.asarray([[1.0, -1.0], [-1.0, 1.0]], dtype=np.float64)
    return (np.eye(2) - KAPPA * laplacian) @ np.asarray(memory, dtype=np.float64)


def _normalize_pair(values: np.ndarray) -> np.ndarray:
    values = np.maximum(np.asarray(values, dtype=np.float64), 0.0)
    total = float(np.sum(values))
    if total <= 0.0:
        return np.asarray([0.5, 0.5])
    return values / total


def controller_projection(
    components: list,
    next_weight: np.ndarray,
    lane_weights: tuple[float, float],
) -> tuple[np.ndarray | None, dict[str, object]]:
    """Idx-27 pipeline with the 1:1 trace fusion replaced by the ladder weights."""
    geometry = lane_geometry(components, next_weight)
    if geometry["degenerate"]:
        return None, {
            "spectral_ambiguity": True,
            "top_eigenvalue": 0.0,
            "relative_eigengap": 0.0,
            "score_variance": 0.0,
            "lane_weights": list(lane_weights),
        }
    gate_gram = geometry["gate_gram"]
    active_gram = geometry["active_gram"]
    correlation = geometry["correlation"]
    inverse_sigma = geometry["inverse_sigma"]
    fused = (
        lane_weights[0] * gate_gram / float(geometry["gate_trace"])
        + lane_weights[1] * active_gram / float(geometry["active_trace"])
    )
    fused = 0.5 * (fused + fused.T)
    values, vectors = np.linalg.eigh(fused)
    order = np.argsort(values)[::-1]
    values = np.maximum(values[order], 0.0)
    scale = max(float(values[0]), np.finfo(np.float64).tiny)
    gap = float((values[0] - values[1]) / scale) if values.size > 1 else 1.0
    eigenvector = vectors[:, order[0]]
    score_variance = float(eigenvector @ correlation @ eigenvector)
    ambiguous = values[0] <= 0.0 or gap <= EIGENGAP_TOLERANCE or score_variance <= 0.0
    diagnostics: dict[str, object] = {
        "spectral_ambiguity": bool(ambiguous),
        "top_eigenvalue": float(values[0]),
        "relative_eigengap": gap,
        "score_variance": score_variance,
        "lane_weights": [float(lane_weights[0]), float(lane_weights[1])],
        "channel_gram_cosine": float(
            np.sum(gate_gram * active_gram)
            / max(
                float(np.linalg.norm(gate_gram) * np.linalg.norm(active_gram)),
                np.finfo(np.float64).tiny,
            )
        ),
    }
    if ambiguous:
        return None, diagnostics
    loading = inverse_sigma * eigenvector / math.sqrt(score_variance)
    direction = next_weight @ loading
    norm = float(np.linalg.norm(direction))
    if not np.isfinite(norm) or norm == 0.0:
        diagnostics["spectral_ambiguity"] = True
        return None, diagnostics
    return direction, diagnostics


def controller_reduce_components(
    components: list,
    next_weight: np.ndarray,
    lane_weights: tuple[float, float],
    maximum_components: int = 3,
) -> tuple[list, dict[str, object]]:
    direction, diagnostics = controller_projection(
        components, next_weight, lane_weights
    )
    reduced, collapsed = sc._equal_mass_reduce_along(
        components, direction, maximum_components
    )
    return reduced, {**diagnostics, "tie_or_degenerate_collapse": bool(collapsed)}


def ladder_pass(
    width: int, depth: int, seed: int, rotation_seed: int
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Frozen forward pass plus the depth-recurrent two-lane ladder state."""
    weights = h18.make_weights(width, depth, seed)
    frame_rng = np.random.Generator(np.random.Philox(rotation_seed))
    frames = [rr.haar_frame(width, frame_rng) for _ in range(depth)]
    snapshots = {0, depth // 2, depth - 2}
    components = [
        GaussianComponent(1.0, np.zeros(width), np.eye(width, dtype=np.float64))
    ]
    states: list[dict[str, object]] = []
    trace: list[dict[str, object]] = []
    memory = None
    for layer, weight in enumerate(weights):
        children = h18.expand_layer(components, weight, frames[layer])
        if layer <= depth - 2:
            geometry = lane_geometry(children, weights[layer + 1])
            evidence_pack = lane_evidence(geometry)
            evidence = np.asarray(
                [evidence_pack["gate_evidence"], evidence_pack["active_evidence"]]
            )
            memory = (
                evidence.copy()
                if memory is None
                else RHO * memory + (1.0 - RHO) * evidence
            )
            diffused = commissural(memory)
            leak_weights = _normalize_pair(memory)
            commissural_weights = _normalize_pair(diffused)
            record = {
                "depth": depth,
                "seed": seed,
                "layer": layer,
                "gate_evidence": float(evidence[0]),
                "active_evidence": float(evidence[1]),
                "gate_evidence_exact": float(evidence_pack["gate_evidence_exact"]),
                "active_evidence_exact": float(evidence_pack["active_evidence_exact"]),
                "memory": [float(memory[0]), float(memory[1])],
                "diffused": [float(diffused[0]), float(diffused[1])],
                "leak_lane_weights": [
                    float(leak_weights[0]),
                    float(leak_weights[1]),
                ],
                "commissural_lane_weights": [
                    float(commissural_weights[0]),
                    float(commissural_weights[1]),
                ],
                "channel_gram_cosine": float(
                    np.sum(geometry["gate_gram"] * geometry["active_gram"])
                    / max(
                        float(
                            np.linalg.norm(geometry["gate_gram"])
                            * np.linalg.norm(geometry["active_gram"])
                        ),
                        np.finfo(np.float64).tiny,
                    )
                ),
                "snapshot": layer in snapshots,
            }
            trace.append(record)
            if layer in snapshots:
                states.append(
                    {
                        "width": width,
                        "depth": depth,
                        "seed": seed,
                        "layer": layer,
                        "children": children,
                        "next_weight": weights[layer + 1],
                        "next_frame": frames[layer + 1],
                        "leak_lane_weights": (
                            float(leak_weights[0]),
                            float(leak_weights[1]),
                        ),
                        "commissural_lane_weights": (
                            float(commissural_weights[0]),
                            float(commissural_weights[1]),
                        ),
                        "ladder": record,
                    }
                )
        components = rr.reduce_components(children, 3)
    if len(states) != 3:
        raise RuntimeError("frozen snapshot count changed")
    return states, trace


def conservative_cost_bound(width: int = 256, depth: int = 32) -> dict[str, object]:
    """Idx-27 cost plus the fixed-budget two-lane ladder scalars."""
    parent_subtotal = 56_472_109_056
    added_sandwich = 2 * depth * width**3
    added_dual_quadratic = 12 * depth * width**2
    # Two lanes x 64 power iterations x (matvec + Rayleigh/normalize) ~ 4 n^2 each.
    added_ladder_power = 2 * POWER_ITERATIONS * 4 * depth * width**2
    # Convex lane fusion of two Grams.
    added_fusion = 4 * depth * width**2
    subtotal = (
        parent_subtotal
        + added_sandwich
        + added_dual_quadratic
        + added_ladder_power
        + added_fusion
    )
    bound = int(1.25 * subtotal)
    return {
        "parent_subtotal": parent_subtotal,
        "added_global_covariance_sandwich": added_sandwich,
        "added_dual_gram_and_pullback_quadratic": added_dual_quadratic,
        "added_ladder_power_iteration": added_ladder_power,
        "added_lane_fusion": added_fusion,
        "subtotal": subtotal,
        "contingency_fraction": 0.25,
        "with_contingency": bound,
        "gate": 80_000_000_000,
        "pass": bound < 80_000_000_000,
    }
