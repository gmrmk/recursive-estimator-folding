"""M173: certified parameter-scaled layer for M171's hostile rank-two panel.

This is a response-free repair of one *specific* M171 failure link.  M171
applied a 10-node Gauss--Legendre derivative enclosure directly in ``u`` to
the conditional primitive ``Phi((u-u_star)/eta)``.  Its twentieth derivative
grows as ``eta**-20``.  M173 instead uses the exact identity

    integral F(u) Phi((u-u_star)/eta) du
      = integral_(u_star)^infinity F(u) du
        + eta integral F(u_star + eta*t) g(t) dt,

where ``g(t) = Phi(t) - 1{t>0}``.  The first term is the existing exact
normal-interval recurrence of the transverse M168 wedge algebra.  The second
term is a local, matched-asymptotic correction.  On the deterministic layer
``|t| <= 8`` it is represented by a degree-nine Taylor jet; outside it is
enclosed analytically by Gaussian tails.  No sample, response, retry, or
opaque multivariate CDF is involved.

The proved enclosure is uniform for every real layer parameter
``0 < eta <= 1/10`` *conditional on the stated analytic-amplitude
envelopes*.  It repairs the singular ``Phi(u/eta)`` channel on a transverse,
positive-marginal rank-two plane only.  It is not a full M168 fixed-node
implementation and cannot authorize an SPD, nontransverse, or zero-face
continuation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from fractions import Fraction
from math import factorial
from typing import Sequence


# Locked source tolerances transported in M159's dimensionless carrier.
NORMALIZED_VALUE_TOLERANCE = Fraction(1, 50_000_000)  # 2e-8
NORMALIZED_TANGENT_TOLERANCE = Fraction(1, 5_000_000)  # 2e-7
BILLED_OPS_CEILING = 606_720

# M173's fully predeclared near-parallel slice and certified layer.
ETA_MAX = Fraction(1, 10)
LAYER_RADIUS = 8
TAYLOR_DEGREE = 9
TAYLOR_REMAINDER_DERIVATIVE = TAYLOR_DEGREE + 1
REGULAR_GL_NODES = 10
LAYER_QUADRATURE_NODES = 0  # analytic jet plus tail enclosure, not a probe

# A provider must derive these from its connected-first analytic kernels.  The
# fixed caps are deliberately part of this limited certificate rather than
# guessed after an evaluation.
AMPLITUDE_ZERO_BOUND = 1_000_000
AMPLITUDE_FIRST_BOUND = 1_000_000
AMPLITUDE_TENTH_BOUND = 3_000_000
TANGENT_AMPLITUDE_ZERO_BOUND = 1_000_000
TANGENT_KERNEL_TENTH_BOUND = 3_000_000
ETA_TANGENT_BOUND = 1
KINK_INTERSECTION_TANGENT_BOUND = 1

# phi(8) < 1 / 150e12 is proved below with rational lower bounds on e and pi.
PHI_EIGHT_UPPER = Fraction(1, 150_000_000_000_000)


class StratumAction(str, Enum):
    """Closed dispatch actions.  Passing one never widens another stratum."""

    TRANSVERSE_RANK2_LAYER_CERTIFIED = "rank2-transverse-near-parallel-boundary-layer-certified"
    TRANSVERSE_RANK2_ENVELOPE_REFUSE = "rank2-transverse-amplitude-envelope-refuse"
    TRANSVERSE_RANK2_NOT_NEAR_PARALLEL = "rank2-transverse-outside-predeclared-eta-range"
    SPD_REFUSE = "spd-not-licensed-by-rank2-boundary-layer"
    NONTRANSVERSE_REFUSE = "rank2-nontransverse-refuse"
    ZERO_MARGINAL_REFUSE = "zero-marginal-deterministic-conic-route-required"
    OUTWARD_CONE_REFUSE = "outward-psd-cone-refuse"
    NATIVE_BILL_UNPROVED = "native-operation-bill-unproved-no-provider-credit"


@dataclass(frozen=True)
class BoundaryLayerPredeclaration:
    """Frozen mechanism, range, allocation, tolerances, and kill gates."""

    target_scope: str
    eta_range: str
    coordinate: str
    deterministic_partition: str
    connected_first_requirement: str
    regular_node_allocation: int
    layer_node_allocation: int
    taylor_degree: int
    normalized_value_tolerance: str
    normalized_tangent_tolerance: str
    amplitude_envelope: str
    cost_prediction: int
    billed_ops_ceiling: int
    kill_gates: tuple[str, ...]


@dataclass(frozen=True)
class LayerEnclosure:
    """Exact rational upper bounds for the degree-nine layer approximation."""

    eta: Fraction
    value_interior: Fraction
    value_tail: Fraction
    value_total: Fraction
    tangent_interior: Fraction
    tangent_tail: Fraction
    tangent_total: Fraction
    value_closes: bool
    tangent_closes: bool


@dataclass(frozen=True)
class CostPrediction:
    """M171 bookkeeping with exactly one hostile channel replaced, not added."""

    setup_and_tree_ops: int
    boundary_ops: int
    wedge_cells: int
    regular_components: int
    regular_nodes_per_component: int
    regular_component_ops: int
    singular_channels: int
    singular_channel_layer_ops: int
    predicted_ops: int
    legacy_m171_prediction: int
    maximum_nodes_per_channel: int
    under_ceiling: bool
    native_bill_proved: bool
    credit: str


@dataclass(frozen=True)
class DispatchDecision:
    action: StratumAction
    reason: str


def predeclare_boundary_layer() -> BoundaryLayerPredeclaration:
    """Return the candidate before any mathematical gate is evaluated."""

    cost = predicted_cost()
    return BoundaryLayerPredeclaration(
        target_scope=(
            "the Phi((u-u_star)/eta) channel of a connected-first, positive-marginal, "
            "transverse rank-two M168 wedge; no all-PSD provider claim"
        ),
        eta_range=(
            "all real 0 < eta <= 1/10, with eta from the frozen ordered-pair chart "
            "X_i=U, X_j=U+eta*V (or its sign-reflected equivalent)"
        ),
        coordinate="u = u_star + eta*t inside |t| <= 8",
        deterministic_partition=(
            "(-infinity,u_star-8*eta], [u_star-8*eta,u_star], "
            "[u_star,u_star+8*eta], [u_star+8*eta,infinity); no adaptive subdivision"
        ),
        connected_first_requirement="assemble cumulant minus M129 tree before deriving amplitude envelopes",
        regular_node_allocation=REGULAR_GL_NODES,
        layer_node_allocation=LAYER_QUADRATURE_NODES,
        taylor_degree=TAYLOR_DEGREE,
        normalized_value_tolerance="2e-8",
        normalized_tangent_tolerance="2e-7 (current locked M147 source certificate)",
        amplitude_envelope=(
            "sup|F|<=1e6, sup|F'|<=1e6, sup|F^(10)|<=3e6, "
            "sup|Fdot|<=1e6, sup|K^(10)|<=3e6, |etadot|<=1, |u_star_dot|<=1"
        ),
        cost_prediction=cost.predicted_ops,
        billed_ops_ceiling=BILLED_OPS_CEILING,
        kill_gates=(
            "eta must lie in the predeclared open transverse range 0<eta<=1/10",
            "connected-first symbolic amplitude and tangent envelopes must meet every stated cap",
            "the exact layer plus tail enclosure must be <=2e-8 for value and <=2e-7 for tangent",
            "nontransverse rank-two, zero-marginal, outward-cone, and SPD states must refuse",
            "no adaptive retry, ridge, clipping, opaque CDF, response-derived selection, or native-bill inference",
        ),
    )


def predicted_cost() -> CostPrediction:
    """Conservative M171 bookkeeping after replacing one hostile channel.

    M171 charged seven wedge cells times 31 components times ten nodes at 256
    arithmetic-equivalent operations, plus its unchanged setup and exact
    boundary inventory.  Here 30 regular components retain their original ten
    nodes.  The one ``Phi(u/eta)`` channel in each cell receives a fixed
    ten-jet/tail calculation charged at 1,024 operations, below its former
    2,560 operation GL10 slot.  Thus the coordinate repair does not exceed
    M171's 10-node-equivalent allocation.
    """

    setup = 4_096
    boundary = 16 * 3 * 256
    wedge_cells = 7
    regular_components = 30
    regular_nodes = REGULAR_GL_NODES
    component_ops = 256
    singular_channels = wedge_cells
    layer_ops = 1_024
    total = (
        setup
        + boundary
        + wedge_cells * regular_components * regular_nodes * component_ops
        + singular_channels * layer_ops
    )
    return CostPrediction(
        setup,
        boundary,
        wedge_cells,
        regular_components,
        regular_nodes,
        component_ops,
        singular_channels,
        layer_ops,
        total,
        571_904,
        max(REGULAR_GL_NODES, LAYER_QUADRATURE_NODES),
        total <= BILLED_OPS_CEILING,
        False,
        "bookkeeping only: M173 has no native billed trace and no endpoint-provider credit",
    )


def _validate_eta(eta: Fraction) -> None:
    if not isinstance(eta, Fraction) or not 0 < eta <= ETA_MAX:
        raise ValueError("eta must be a Fraction in the predeclared interval (0, 1/10]")


def layer_partition(eta: Fraction, u_star: Fraction = Fraction(0)) -> tuple[str, Fraction, Fraction, Fraction, str]:
    """Exact, deterministic physical-coordinate partition for the layer."""

    _validate_eta(eta)
    if not isinstance(u_star, Fraction):
        raise TypeError("u_star must be an exact Fraction in this certificate")
    radius = LAYER_RADIUS * eta
    return ("-infinity", u_star - radius, u_star, u_star + radius, "infinity")


def _absolute_layer_moment_ten_upper() -> Fraction:
    """Bound integral |t|^10 |Phi(t)-1{t>0}| dt without numerical probing.

    For ``Q=1-Phi``, the integral is
    ``2/11 E[(Z_+)^11]``.  On the positive half line,
    ``z^11 <= 1+z^12`` and ``E[Z^12]=10395``, giving ``10396/11``.
    """

    return Fraction(10_396, 11)


def phi_eight_upper_is_certified() -> bool:
    """Prove the rational Gaussian-tail constant using only rational bounds.

    ``e > 1957/720`` from its first seven positive series terms and
    ``sqrt(2*pi)>12/5`` from ``pi>3``.  Hence
    ``exp(32)*sqrt(2*pi)>150e12`` and `phi(8)<1/(150e12)`.
    """

    e_lower = Fraction(1_957, 720)
    sqrt_two_pi_lower = Fraction(12, 5)
    return e_lower**32 * sqrt_two_pi_lower > 150_000_000_000_000


def layer_enclosure(eta: Fraction) -> LayerEnclosure:
    """Return a uniform-in-eta analytic enclosure, not a sampled estimate.

    Let ``F`` be the connected-first normal-polynomial amplitude and put
    ``g(t)=Phi(t)-1{t>0}``.  Taylor-expand ``F(u_star+eta*t)`` through degree
    nine on the layer.  The value remainder is bounded by

      eta^11 sup|F^(10)|/10! * integral |t|^10 |g(t)| dt.

    For a tangent, differentiate the coordinate transform *before* expanding:

      dR = integral K(u_star + eta*t) g(t) dt,
      K(u)=etadot*(F(u)+(u-u_star)*F'(u))
           + eta*(Fdot(u)+u_star_dot*F'(u)).

    Thus its interior remainder has ``eta^10`` rather than ``eta^11``.
    The two tails use ``integral_B^inf Q <= phi(B)`` and
    ``integral_B^inf t Q <= Q(B) <= phi(B)/B``.  All constants are frozen
    above; their endpoint at eta=1/10 dominates the entire declared range.
    """

    _validate_eta(eta)
    if not phi_eight_upper_is_certified():  # Defensive: the proof constant must not drift.
        raise RuntimeError("the rational phi(8) upper bound certificate failed")
    layer_moment = _absolute_layer_moment_ten_upper()
    denominator = factorial(TAYLOR_REMAINDER_DERIVATIVE)
    value_interior = eta ** (TAYLOR_REMAINDER_DERIVATIVE + 1) * AMPLITUDE_TENTH_BOUND * layer_moment / denominator
    value_tail = 2 * eta * AMPLITUDE_ZERO_BOUND * PHI_EIGHT_UPPER
    tangent_interior = eta ** TAYLOR_REMAINDER_DERIVATIVE * TANGENT_KERNEL_TENTH_BOUND * layer_moment / denominator
    tangent_tail = 2 * (
        ETA_TANGENT_BOUND * AMPLITUDE_ZERO_BOUND * PHI_EIGHT_UPPER
        + eta * ETA_TANGENT_BOUND * AMPLITUDE_FIRST_BOUND * PHI_EIGHT_UPPER / LAYER_RADIUS
        + eta * TANGENT_AMPLITUDE_ZERO_BOUND * PHI_EIGHT_UPPER
        + eta * KINK_INTERSECTION_TANGENT_BOUND * AMPLITUDE_FIRST_BOUND * PHI_EIGHT_UPPER
    )
    value_total = value_interior + value_tail
    tangent_total = tangent_interior + tangent_tail
    return LayerEnclosure(
        eta,
        value_interior,
        value_tail,
        value_total,
        tangent_interior,
        tangent_tail,
        tangent_total,
        value_total <= NORMALIZED_VALUE_TOLERANCE,
        tangent_total <= NORMALIZED_TANGENT_TOLERANCE,
    )


def canonical_near_parallel_factor(eta: Fraction) -> tuple[tuple[Fraction, Fraction], ...]:
    """M171's hostile, positive-marginal transverse factor family exactly."""

    _validate_eta(eta)
    return ((Fraction(1), Fraction(0)), (Fraction(1), eta), (Fraction(0), Fraction(1)))


def covariance_from_factor(factor: Sequence[Sequence[Fraction]]) -> tuple[tuple[Fraction, ...], ...]:
    if len(factor) != 3 or any(len(row) != 2 for row in factor):
        raise ValueError("factor must have shape 3x2")
    return tuple(
        tuple(sum((factor[i][q] * factor[j][q] for q in range(2)), Fraction(0)) for j in range(3))
        for i in range(3)
    )


def _det2(left: Sequence[Fraction], right: Sequence[Fraction]) -> Fraction:
    return left[0] * right[1] - left[1] * right[0]


def minimum_pairwise_transversality(factor: Sequence[Sequence[Fraction]]) -> Fraction:
    if len(factor) != 3 or any(len(row) != 2 for row in factor):
        raise ValueError("factor must have shape 3x2")
    return min(abs(_det2(factor[left], factor[right])) for left in range(3) for right in range(left + 1, 3))


def rank2_boundary_layer_dispatch(
    factor: Sequence[Sequence[Fraction]], *, eta: Fraction, envelopes_certified: bool
) -> DispatchDecision:
    """Closed dispatch for M173's deliberately narrow repair surface.

    ``eta`` is intentionally supplied by the frozen M168 pair chart, rather
    than inferred from an unnormalised raw determinant.  For the hostile
    canonical family it is exactly the coefficient in ``U+eta*V``.  A future
    generic factor chart must certify that reduction before calling here.
    """

    if len(factor) != 3 or any(len(row) != 2 for row in factor):
        raise ValueError("factor must have shape 3x2")
    if any(sum((entry * entry for entry in row), Fraction(0)) == 0 for row in factor):
        return DispatchDecision(StratumAction.ZERO_MARGINAL_REFUSE, "a factor row is zero")
    if minimum_pairwise_transversality(factor) == 0:
        return DispatchDecision(
            StratumAction.NONTRANSVERSE_REFUSE,
            "parallel or coincident kinks have no transverse eta coordinate",
        )
    if not isinstance(eta, Fraction) or eta <= 0:
        return DispatchDecision(
            StratumAction.NONTRANSVERSE_REFUSE,
            "the ordered pair chart did not supply a positive transverse eta",
        )
    if eta > ETA_MAX:
        return DispatchDecision(
            StratumAction.TRANSVERSE_RANK2_NOT_NEAR_PARALLEL,
            "pair is transverse but outside M173's predeclared eta range",
        )
    if not envelopes_certified:
        return DispatchDecision(
            StratumAction.TRANSVERSE_RANK2_ENVELOPE_REFUSE,
            "connected-first amplitude or tangent envelope has not been symbolically certified",
        )
    enclosure = layer_enclosure(eta)
    if enclosure.value_closes and enclosure.tangent_closes:
        return DispatchDecision(
            StratumAction.TRANSVERSE_RANK2_LAYER_CERTIFIED,
            "M173's eta-uniform layer enclosure closes for the hostile channel only",
        )
    return DispatchDecision(
        StratumAction.TRANSVERSE_RANK2_ENVELOPE_REFUSE,
        "frozen layer envelope does not close; fail closed rather than add nodes or retry",
    )


def explicit_exclusions() -> dict[str, DispatchDecision]:
    """Record why this panel repair cannot be generalized by implication."""

    return {
        "spd": DispatchDecision(
            StratumAction.SPD_REFUSE,
            "an SPD continuation needs its own connected interval kernel and certified operation trace",
        ),
        "nontransverse_rank2": DispatchDecision(
            StratumAction.NONTRANSVERSE_REFUSE,
            "eta=0 destroys the transverse pair coordinate; a separate coincident-kink analysis is required",
        ),
        "zero_marginal_psd_face": DispatchDecision(
            StratumAction.ZERO_MARGINAL_REFUSE,
            "M159 requires deterministic reduction and an explicit one-sided conic tangent",
        ),
        "outward_psd_tangent": DispatchDecision(
            StratumAction.OUTWARD_CONE_REFUSE,
            "the tangent points outside the PSD cone",
        ),
    }


def audit_record() -> dict[str, object]:
    """JSON-ready, response-free static audit for the frozen artifact."""

    endpoint = layer_enclosure(ETA_MAX)
    predeclaration = asdict(predeclare_boundary_layer())
    cost = asdict(predicted_cost())
    endpoint_dict = asdict(endpoint)
    for mapping in (endpoint_dict,):
        for key, value in tuple(mapping.items()):
            if isinstance(value, Fraction):
                mapping[key] = f"{value.numerator}/{value.denominator}"
    return {
        "scope": "generated response-free mathematics only",
        "predeclaration": predeclaration,
        "coordinate_identity": (
            "int F(u) Phi((u-u_star)/eta) du = int_(u_star)^inf F(u) du "
            "+ eta int F(u_star+eta*t)(Phi(t)-1{t>0})dt"
        ),
        "uniform_enclosure_at_eta_max": endpoint_dict,
        "uniformity": "monotone endpoint bound covers every real 0<eta<=1/10 under frozen envelopes",
        "cost_prediction": cost,
        "exclusions": {
            name: {"action": decision.action.value, "reason": decision.reason}
            for name, decision in explicit_exclusions().items()
        },
        "firewall": {
            "network_response": False,
            "truth_or_scorer": False,
            "leaderboard_or_submission": False,
            "champion_change": False,
            "adaptive_retry": False,
            "opaque_library_cdf": False,
        },
        "disposition": (
            "SCREENED_HOSTILE_TRANSVERSE_RANK2_LAYER_CERTIFICATE_ONLY; "
            "PRESERVE_M154_M165_M168_CONNECTED_FIRST_ANCHORS; "
            "NO_SPD_NONTRANSVERSE_ZERO_FACE_OR_NATIVE_PROVIDER_CREDIT"
        ),
    }
