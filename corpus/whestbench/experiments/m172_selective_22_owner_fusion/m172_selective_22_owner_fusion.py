"""M172: selective physical ``[2,2]`` ownership transfer into M163.

This response-free source-algebra artifact transfers *only* the physical
``{i,i,j,j}`` owner to M163's two ordered ``(i,j,j)`` representatives.  The
separate ``[4]`` and ``[3,1]`` owners are deliberately retained.  M163's
``cE[i,j,j] = -2 A[i,j]**2`` is a control, never a relabelled physical K22
coefficient, so the sampled complete-domain residual is

    K22[i,j] / 2 - cE[i,j,j].

No target/provider call is made here.  The module is a small-width algebra
oracle plus a static accounting record; it does not open the frozen source
variance protocol.
"""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
for _relative in (
    "m156_extended_domain_star_control",
    "m163_exterior_collision_null",
    "m167_collision_owner_unification",
):
    _path = str(ROOT / _relative)
    if _path not in sys.path:
        sys.path.insert(0, _path)

from m156_extended_domain_star_control import (  # noqa: E402
    Source211,
    residual_table as m156_collision_rezeroing_residual_table,
    source_add,
    source_max_abs_difference,
)
from m163_exterior_collision_null import (  # noqa: E402
    compile_exterior_star_control,
    exterior_edge_matrix,
    exterior_star_table,
)
from m167_collision_owner_unification import (  # noqa: E402
    PhysicalFourthOwners,
    complete_owner_table,
    complete_residual_table,
    complete_source_reference,
    direct_physical_owner_source,
    gauge_owners,
    permute_owners,
    physical_collision_tensor,
    source_from_physical_tensor,
)


TARGET_WIDTH = 256
SOURCE_LAYERS = 31
COLLISION_MASS = 0.011688232421875
M163_DENSE_PRODUCTS_PER_LAYER = 5
# M129's primal collision22_probe_dual performs m_probe and m_defect.  The
# tangent-only third contraction is not part of this source-variance arm.
M129_PRIMAL_22_DENSE_CALLS_PER_PROVIDER_EVENT = 2

DEVELOPMENT_CELLS = (
    ("iso_w5", 5, 1720501, 0.22),
    ("factor_w5", 5, 1720502, 0.50),
    ("iso_w6", 6, 1720601, 0.22),
    ("factor_w6", 6, 1720602, 0.50),
    ("iso_w7", 7, 1720701, 0.22),
    ("factor_w7", 7, 1720702, 0.50),
)
CONFIRMATION_CELLS = (
    ("iso_w5c", 5, 1721501, 0.22),
    ("factor_w5c", 5, 1721502, 0.50),
    ("iso_w6c", 6, 1721601, 0.22),
    ("factor_w6c", 6, 1721602, 0.50),
    ("iso_w7c", 7, 1721701, 0.22),
    ("factor_w7c", 7, 1721702, 0.50),
)


def _valid_width(owners: PhysicalFourthOwners) -> int:
    """Validate M167 ownership input and return its hidden width.

    Running the M167 constructor with a zero distinct table checks finiteness,
    symmetry, zero diagonals, and the disjoint fourth-order ownership ABI.
    """

    width = int(np.asarray(owners.k4).size)
    complete_owner_table(np.zeros((width, width, width), dtype=np.float64), owners)
    return width


def _only_22(owners: PhysicalFourthOwners) -> PhysicalFourthOwners:
    """Return the prior separate physical owner containing only ``[2,2]``."""

    width = _valid_width(owners)
    return PhysicalFourthOwners(
        np.zeros(width, dtype=np.float64),
        np.zeros((width, width), dtype=np.float64),
        np.asarray(owners.k22, dtype=np.float64).copy(),
    )


def separate_non22_owners(owners: PhysicalFourthOwners) -> PhysicalFourthOwners:
    """Retain the unchanged separate ``[4]`` and ``[3,1]`` owners only."""

    width = _valid_width(owners)
    return PhysicalFourthOwners(
        np.asarray(owners.k4, dtype=np.float64).copy(),
        np.asarray(owners.k31, dtype=np.float64).copy(),
        np.zeros((width, width), dtype=np.float64),
    )


def retired_old_22_owner(owners: PhysicalFourthOwners) -> PhysicalFourthOwners:
    """The old separate ``[2,2]`` source/probe after its exact retirement."""

    width = _valid_width(owners)
    return PhysicalFourthOwners(
        np.zeros(width, dtype=np.float64),
        np.zeros((width, width), dtype=np.float64),
        np.zeros((width, width), dtype=np.float64),
    )


def selective_22_complete_target(
    distinct_211: np.ndarray, owners: PhysicalFourthOwners
) -> np.ndarray:
    """Inject only physical ``K22/2`` into M163's ordered ``ijj`` rows.

    `complete_owner_table` is reused with zero ``[4]`` and ``[3,1]`` inputs.
    Consequently all `iii`, `iik`, and `iji` target rows remain exactly zero
    in this arm; their physical owners stay outside this table.
    """

    return complete_owner_table(distinct_211, _only_22(owners))


def selective_22_residual(
    distinct_211: np.ndarray, owners: PhysicalFourthOwners, covariance: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return complete target, unchanged M163 control, and its full residual."""

    target = selective_22_complete_target(distinct_211, owners)
    control = exterior_star_table(covariance)
    # This M167 interface is mandatory: M156.residual_table re-zeroes every
    # collision and would silently discard the newly owned physical K22 rows.
    residual = complete_residual_table(target, control)
    return target, control, residual


def m163_control_source(weight: np.ndarray, covariance: np.ndarray) -> Source211:
    """M163 control source, with a direct width-two proof oracle.

    M156's production five-product compiler correctly refuses width two
    because its original distinct-label source has no such production domain.
    M172 still requires an exhaustive width-two ownership proof, so that one
    width uses the same exterior coefficient through the independent complete
    source reference.  Widths three and above call M163's unchanged compiler.
    """

    if np.asarray(weight).shape[0] == 2:
        return complete_source_reference(weight, exterior_star_table(covariance))
    return compile_exterior_star_control(weight, covariance)


def m163_selective_22_conservation_error(
    weight: np.ndarray,
    distinct_211: np.ndarray,
    owners: PhysicalFourthOwners,
    covariance: np.ndarray,
) -> float:
    """Exhaustive complete-domain M163 add/subtract conservation error."""

    target, _, residual = selective_22_residual(distinct_211, owners, covariance)
    direct = complete_source_reference(weight, target)
    reconstructed = source_add(
        m163_control_source(weight, covariance),
        complete_source_reference(weight, residual),
    )
    return source_max_abs_difference(direct, reconstructed)


def independent_22_tensor_source(weight: np.ndarray, owners: PhysicalFourthOwners) -> Source211:
    """Independent dense symmetric fourth-tensor source for physical ``[2,2]``."""

    only_22 = _only_22(owners)
    return source_from_physical_tensor(weight, physical_collision_tensor(only_22))


def old_separate_22_source(weight: np.ndarray, owners: PhysicalFourthOwners) -> Source211:
    """Reference source of the old physical ``[2,2]`` owner alone."""

    return direct_physical_owner_source(weight, _only_22(owners))


def retired_22_source(weight: np.ndarray, owners: PhysicalFourthOwners) -> Source211:
    """Reference source after retiring exactly the old ``[2,2]`` owner."""

    return direct_physical_owner_source(weight, retired_old_22_owner(owners))


def complete_selective_source(
    weight: np.ndarray, distinct_211: np.ndarray, owners: PhysicalFourthOwners
) -> Source211:
    """New table source plus unchanged separate ``[4]``/``[3,1]`` sources."""

    target = selective_22_complete_target(distinct_211, owners)
    return source_add(
        complete_source_reference(weight, target),
        direct_physical_owner_source(weight, separate_non22_owners(owners)),
    )


def old_separate_source(
    weight: np.ndarray, distinct_211: np.ndarray, owners: PhysicalFourthOwners
) -> Source211:
    """Pre-transfer distinct table plus all physical separate owners."""

    width = _valid_width(owners)
    empty = PhysicalFourthOwners(
        np.zeros(width, dtype=np.float64),
        np.zeros((width, width), dtype=np.float64),
        np.zeros((width, width), dtype=np.float64),
    )
    return source_add(
        complete_source_reference(weight, complete_owner_table(distinct_211, empty)),
        direct_physical_owner_source(weight, owners),
    )


def permuted_inputs(
    distinct_211: np.ndarray, owners: PhysicalFourthOwners, permutation: np.ndarray
) -> tuple[np.ndarray, PhysicalFourthOwners]:
    """Apply one hidden-label relabelling to every M172-owned input."""

    p = np.asarray(permutation, dtype=int)
    return distinct_211[np.ix_(p, p, p)], permute_owners(owners, p)


def gauged_inputs(
    distinct_211: np.ndarray, owners: PhysicalFourthOwners, gauge: np.ndarray
) -> tuple[np.ndarray, PhysicalFourthOwners]:
    """Apply the positive ReLU gauge to the table and all physical owners."""

    d = np.asarray(gauge, dtype=np.float64)
    transformed = (
        np.asarray(distinct_211, dtype=np.float64)
        * d[:, None, None] ** 2
        * d[None, :, None]
        * d[None, None, :]
    )
    return transformed, gauge_owners(owners, d)


def static_owner_fusion_ledger(
    width: int = TARGET_WIDTH, layers: int = SOURCE_LAYERS
) -> dict[str, object]:
    """Inclusive static ownership/call delta without an unlicensed K choice.

    The M172 protocol freezes no source-draw count.  The ledger therefore
    reports all delta quantities per accepted ordered ``ijj`` provider event
    and refuses to turn an unspecified event count into a resource pass.  It
    charges the two M129 primal K22 contractions again in the residual path:
    moving ownership does not make physical K22 formation or transport free.
    """

    n, l = int(width), int(layers)
    if n < 2 or l <= 0:
        raise ValueError("width must be at least two and layers positive")
    ordered_ijj = n * (n - 1)
    unordered_22 = ordered_ijj // 2
    compiler_calls = M163_DENSE_PRODUCTS_PER_LAYER * l
    return {
        "candidate": "M172 selective physical [2,2] owner fusion into M163 ijj rows",
        "width": n,
        "layers": l,
        "collision_mass_eta": COLLISION_MASS,
        "nonzero_ordered_ijj_representatives": ordered_ijj,
        "physical_unordered_22_units": unordered_22,
        "zero_target_collision_rows_retained_separately": {
            "iii_[4]": n,
            "iik_iji_[3,1]": 2 * n * (n - 1),
        },
        "proposal": {
            "support": "only nonzero ordered ijj representatives in this arm",
            "mass_each_ordered_ijj": COLLISION_MASS / float(ordered_ijj),
            "zero_rows_receive_mass": False,
            "eta_retuned": False,
        },
        "compiler": {
            "m163_dense_products_per_layer_unchanged": M163_DENSE_PRODUCTS_PER_LAYER,
            "m163_dense_calls_over_layers_unchanged": compiler_calls,
            "m172_added_dense_compiler_products": 0,
        },
        "physical_22_provider_per_accepted_event": {
            "old_separate_owner_probe_dense_calls_retired": M129_PRIMAL_22_DENSE_CALLS_PER_PROVIDER_EVENT,
            "new_residual_k22_provider_dense_calls": M129_PRIMAL_22_DENSE_CALLS_PER_PROVIDER_EVENT,
            "net_dense_calls": 0,
            "reason": "M129 primal K22 formation/transport is still required to evaluate K22/2-cE; ownership transfer is not a Khatri--Rao cost credit.",
        },
        "new_eventwise_f64_operations_per_accepted_event": {
            "physical_half_k22": 1,
            "cE_square_Aij": 1,
            "cE_scale_minus_two": 1,
            "residual_subtraction": 1,
            "HH_importance_division": 1,
            "total": 5,
        },
        "sampler_setup_f64_operations": {
            "ordered_ijj_mass_division": 1,
            "sample_count": "intentionally unspecified by the frozen M172 protocol",
            "added_eventwise_total": "5 * accepted_ordered_ijj_events + 1",
        },
        "call_delta": {
            "old_separate_22_owner_source_contribution": "retired exactly",
            "new_complete_table_22_target_contribution": "K22/2 on each ordered ijj representative",
            "separate_4_and_31_owners": "retained unchanged",
            "net_dense_call_credit_claimed": 0,
        },
        "resource_disposition": "NO_TARGET_RESOURCE_PASS_FROM_THIS_LEDGER: a future integration must bind an exact provider/draw schedule and recheck M169's all-31-W/V staging ABI before projecting the hostile cap.",
    }


def m163_ijj_formula(covariance: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return M163 edge A and the control's physical ``ijj`` coefficient."""

    edge = exterior_edge_matrix(covariance)[2]
    control_ijj = -2.0 * edge * edge
    np.fill_diagonal(control_ijj, 0.0)
    return edge, control_ijj


def intentionally_bad_rezeroed_residual(
    distinct_211: np.ndarray, owners: PhysicalFourthOwners, covariance: np.ndarray
) -> np.ndarray:
    """Test-only M156 residual API result, which must be rejected by M172."""

    target = selective_22_complete_target(distinct_211, owners)
    return m156_collision_rezeroing_residual_table(target, exterior_star_table(covariance))
