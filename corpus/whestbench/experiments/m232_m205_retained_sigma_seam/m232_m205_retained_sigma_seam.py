"""M232 static seam proof; no current-parent reuse or inclusive trace claim."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
for directory in (
    EXPERIMENTS / "m205_rankone_complete_physical_owner",
    EXPERIMENTS / "m224_gauge_invariant_rho08_chart",
    EXPERIMENTS / "m228_caller_bound_rho08",
    EXPERIMENTS / "m212_backend_packed_explicit_symmetry",
):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

import m205_rankone_complete_physical_owner as m205  # noqa: E402
import m224_gauge_invariant_rho08_chart as m224  # noqa: E402
import m228_caller_bound_rho08 as m228  # noqa: E402
import m212_flopscope_sidecar as m212  # noqa: E402


MUTATION = "M232"
M224_CODE_SHA256 = "6ABA2D0AB618FF5D678977CC07FC89962C09092B537AAFFC282E069C10DFDA7B"


class M232Refusal(RuntimeError):
    """A proposed retained-sigma seam violated frozen provenance."""


@dataclass(frozen=True)
class RetainedM205Sigma:
    layer: int
    epoch: int
    covariance_identity: int
    marginal_sigma: np.ndarray
    factor: np.ndarray
    active_count: int

    @property
    def vector(self) -> np.ndarray:
        return self.marginal_sigma


def retain_m205_marginal_sigma(
    mean: np.ndarray,
    covariance: np.ndarray,
    *,
    layer: int,
    epoch: int,
) -> RetainedM205Sigma:
    """Static model of retaining M205's required diagonal-sqrt output."""
    state = m205.build_rank_one_b1_state(mean, covariance)
    diagonal = np.diag(covariance)
    sigma = np.sqrt(diagonal)
    active_count = int(np.count_nonzero(diagonal > 0.0))
    expected_factor = np.zeros_like(sigma)
    if active_count:
        expected_factor[diagonal > 0.0] = sigma[diagonal > 0.0] / np.sqrt(active_count)
    if not np.array_equal(state.factor, expected_factor):
        raise M232Refusal("M205_FACTOR_SEMANTICS_MISMATCH")
    return RetainedM205Sigma(layer, epoch, id(covariance), sigma, state.factor, active_count)


def bind_retained_sigma(
    retained: RetainedM205Sigma,
    vector: np.ndarray,
    layer: int,
    epoch: int,
) -> np.ndarray:
    if layer != retained.layer:
        raise M232Refusal("M205_RETAINED_SIGMA_LAYER_SUBSTITUTION")
    if epoch != retained.epoch:
        raise M232Refusal("M205_RETAINED_SIGMA_EPOCH_SUBSTITUTION")
    if vector is not retained.vector:
        raise M232Refusal("M205_RETAINED_SIGMA_COPY_OR_CONDITIONAL_SUBSTITUTION")
    return vector


def generated_m224_semantic_proof() -> dict[str, bool]:
    """Compare a generated M205-style gather with M224 and M228 semantics."""
    packed = m224.single_event_batch(
        width=4, seed=221700004, labels=(0, 0, 1, 2), outer_g=(0.0, 0.25, -2.5)
    )
    retained = retain_m205_marginal_sigma(
        packed.local_states[0].mean, packed.local_states[0].covariance, layer=7, epoch=19
    )
    gathered_left = np.take(retained.vector, packed.labels[:, 2])
    gathered_right = np.take(retained.vector, packed.labels[:, 3])
    expected_left, expected_right = m224._marginal_singleton_sigmas(packed)
    exact = bool(np.array_equal(gathered_left, expected_left) and np.array_equal(gathered_right, expected_right))

    bound, _ = m228.caller_owned_inputs(packed)
    columns = dict(bound.columns)
    columns["marginal_sigma_left"] = gathered_left
    columns["marginal_sigma_right"] = gathered_right
    kernel = m228.PersistentKernel(packed.size)
    kernel.bind(m228.BoundInputs(columns=columns, event_count=packed.size))
    value, radius, chart_ok = kernel.compile()
    expected = m224.evaluate_numpy(packed)
    parity = bool(
        np.array_equal(np.asarray(chart_ok), expected.chart_ok)
        and np.all(np.abs(np.asarray(value) - expected.value) < expected.radius)
        and np.allclose(np.asarray(radius), expected.radius, rtol=0.0, atol=1e-20)
    )

    local = packed.local_states[0]
    gauge = np.asarray((0.7, 1.1, 1.4, 0.9), dtype=np.float64)
    gauged_covariance = local.covariance * gauge[:, None] * gauge[None, :]
    gauged = retain_m205_marginal_sigma(local.mean * gauge, gauged_covariance, layer=7, epoch=19)
    gauge_exact = bool(np.allclose(gauged.vector, gauge * retained.vector, rtol=0.0, atol=3e-16))

    permutation = np.asarray((3, 0, 2, 1), dtype=int)
    inverse = np.argsort(permutation)
    permuted = retain_m205_marginal_sigma(
        local.mean[permutation], local.covariance[np.ix_(permutation, permutation)], layer=7, epoch=19
    )
    permutation_exact = bool(
        np.array_equal(permuted.vector[inverse[packed.labels[:, 2]]], gathered_left)
        and np.array_equal(permuted.vector[inverse[packed.labels[:, 3]]], gathered_right)
    )
    return {
        "m224_marginals_exact": exact,
        "m224_value_parity": parity,
        "gauge_exact": gauge_exact,
        "permutation_exact": permutation_exact,
    }


def current_parent_seam_audit() -> dict[str, object]:
    """Inspect current parent artifacts without inventing a live provider."""
    state_fields = tuple(m205.RankOneB1State.__dataclass_fields__)
    input_fields = tuple(m212.LayerInput.__dataclass_fields__)
    present = "marginal_sigma" in state_fields or "marginal_sigma" in input_fields
    return {
        "status": "LIVE_PROVIDER_PRESENT_UNVALIDATED" if present else "SEAM_PROTOTYPE_INTEGRATION_BLOCKED",
        "reason": None if present else "CURRENT_M205_M212_RETAINED_MARGINAL_SIGMA_ABSENT",
        "m205_state_fields": state_fields,
        "m212_layer_input_fields": input_fields,
        "inclusive_trace_authorized": False,
        "integrated_cost_credit": 0,
    }


__all__ = [
    "M224_CODE_SHA256",
    "M232Refusal",
    "RetainedM205Sigma",
    "bind_retained_sigma",
    "current_parent_seam_audit",
    "generated_m224_semantic_proof",
    "retain_m205_marginal_sigma",
]
