"""M171 response-free rank-stratified endpoint-provider certificate.

This module records one fully specified proposed provider, then proves that it
must fail closed before use.  It intentionally contains no network calls,
model evaluation, CDF package, adaptive retry, or opaque multivariate-normal
primitive.

The proposed algebra is connected-first.  Let ``D`` be the connected [2,1,1]
defect (cumulant minus the M129 tree).  At a rank face with normal opening
``epsilon`` its proposed singular subtraction is

    D(epsilon) = D0 + epsilon*DB
                 + 2*epsilon * integral_0^1 v*(G(epsilon*v**2)-DB) dv.

M154 owns the rank-one ``D0, DB`` pair; M168 owns it on a transverse rank-two
face.  The only proposed interior rule is a single 10-node Gauss--Legendre
panel after that subtraction.  The module supplies a rigorous derivative
envelope obstruction for near-parallel rank-two kinks, so the proposal is not
an endpoint provider and never receives a cost credit.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from fractions import Fraction
from math import factorial
from typing import Iterable, Sequence


# Locked M147 collision-[2,1,1] source contract, transported in M159's
# dimensionless dyadic carrier.  The tangent tolerance is the existing locked
# source value, not a new claim of a tighter generic certificate.
NORMALIZED_VALUE_TOLERANCE = Fraction(1, 50_000_000)  # 2e-8
NORMALIZED_TANGENT_TOLERANCE = Fraction(1, 5_000_000)  # 2e-7
BILLED_OPS_CEILING = 606_720
FIXED_INTERIOR_NODES = 10


class StratumAction(str, Enum):
    """Closed dispatch actions; none silently repairs a state."""

    RANK_ONE_M154_EXACT = "rank1-m154-exact-moving-kink-anchor"
    RANK_TWO_M168_ANCHOR = "rank2-m168-transverse-anchor-and-cone-tangent"
    SPD_SUBTRACTED_GL10 = "spd-rank2-anchor-subtract-then-fixed-gl10-attempt"
    NONTRANSVERSE_REFUSE = "rank2-nontransverse-refuse"
    ZERO_MARGINAL_REFUSE = "zero-marginal-deterministic-conic-route-required"
    OUTWARD_CONE_REFUSE = "outward-psd-cone-refuse"
    CERTIFICATE_KILL = "uniform-remainder-or-native-bill-missing-kill"


@dataclass(frozen=True)
class ProviderPredeclaration:
    """The M171 contract stated before its falsification gate is run."""

    target_coverage: str
    rule: str
    fixed_interior_nodes: int
    normalized_value_tolerance: str
    normalized_tangent_tolerance: str
    billed_ops_prediction: int
    billed_ops_ceiling: int
    analytic_subtraction: str
    kill_gates: tuple[str, ...]


@dataclass(frozen=True)
class CostPrediction:
    """Transparent arithmetic model inherited from M168; not a native bill."""

    setup_and_tree_ops: int
    wedge_cells: int
    raw_and_indicator_components: int
    component_ops: int
    fixed_nodes: int
    boundary_components: int
    boundary_intervals: int
    predicted_ops: int
    under_ceiling: bool
    native_bill_proved: bool
    credit: str


@dataclass(frozen=True)
class RegularityObstruction:
    """A derivative-envelope failure for a positive-marginal rank-two path."""

    eta: Fraction
    rank: int
    all_marginals_positive: bool
    minimum_pairwise_transversality: Fraction
    derivative_order: int
    hermite_at_one: int
    phi_one_lower_bound: Fraction
    twentieth_derivative_lower_bound: Fraction
    gauss_legendre_remainder_floor: Fraction
    tolerance: Fraction
    closes_derivative_envelope: bool
    conclusion: str


@dataclass(frozen=True)
class DispatchDecision:
    action: StratumAction
    reason: str


def predeclare_provider() -> ProviderPredeclaration:
    """Return the fixed candidate and its prespecified kill gates."""

    cost = predicted_cost(FIXED_INTERIOR_NODES)
    return ProviderPredeclaration(
        target_coverage="all PSD local 3x3 states under the M159 dyadic carrier",
        rule="one 10-node fixed Gauss-Legendre interior panel after connected-first rank-face subtraction",
        fixed_interior_nodes=FIXED_INTERIOR_NODES,
        normalized_value_tolerance="2e-8",
        normalized_tangent_tolerance="2e-7 (current locked M147 source certificate)",
        billed_ops_prediction=cost.predicted_ops,
        billed_ops_ceiling=BILLED_OPS_CEILING,
        analytic_subtraction="D(e)=D0+e*DB+2e*integral_0^1 v*(G(e*v^2)-DB)dv",
        kill_gates=(
            "a uniform normalized value/tangent enclosure must be at most the locked tolerance",
            "rank-two nontransverse and every zero-marginal PSD face must have an explicit exact/conic route",
            "a native billed-operation trace must not exceed 606720 per coefficient",
            "no ridge, clipping, adaptive retry, opaque CDF, or response-derived decision is permitted",
        ),
    )


def predicted_cost(fixed_nodes: int = FIXED_INTERIOR_NODES) -> CostPrediction:
    """Give the predeclared <=606720 bookkeeping prediction.

    It is deliberately only a prediction.  The M168 inventory has seven wedge
    cells, 11 raw plus 20 Price-indicator components, and 16 three-interval
    coarea components.  A uniform error result and a native bill remain
    separate mandatory gates.
    """

    if type(fixed_nodes) is not int or not 1 <= fixed_nodes <= FIXED_INTERIOR_NODES:
        raise ValueError("fixed_nodes must be a built-in integer in [1, 10]")
    setup = 4_096
    wedge_cells = 7
    components = 11 + 20
    component_ops = 256
    boundary_components = 16
    boundary_intervals = 3
    total = (
        setup
        + wedge_cells * components * component_ops * fixed_nodes
        + boundary_components * boundary_intervals * component_ops
    )
    return CostPrediction(
        setup,
        wedge_cells,
        components,
        component_ops,
        fixed_nodes,
        boundary_components,
        boundary_intervals,
        total,
        total <= BILLED_OPS_CEILING,
        False,
        "none: bookkeeping prediction only; no native bill or uniform error certificate",
    )


def rank_face_sqrt_model(
    d0: Fraction, db: Fraction, a: Fraction, epsilon: Fraction
) -> Fraction:
    """Evaluate M165's algebraic sqrt endpoint model for square ``epsilon``.

    If ``G(u)-DB = 3*A*sqrt(u)/2``, the proposed M165 substitution integrates
    it exactly and returns ``D0 + epsilon*DB + A*epsilon^(3/2)``.  Restricting
    to square epsilon keeps this response-free certificate exact over rationals.
    """

    if epsilon < 0:
        raise ValueError("epsilon must be nonnegative")
    numerator_root = _exact_fraction_square_root(epsilon)
    if numerator_root is None:
        raise ValueError("this exact model requires square rational epsilon")
    return d0 + epsilon * db + a * epsilon * numerator_root


def _exact_fraction_square_root(value: Fraction) -> Fraction | None:
    """Return an exact rational root, or ``None`` without a float fallback."""

    numerator_root = _integer_square_root(value.numerator)
    denominator_root = _integer_square_root(value.denominator)
    if numerator_root * numerator_root != value.numerator:
        return None
    if denominator_root * denominator_root != value.denominator:
        return None
    return Fraction(numerator_root, denominator_root)


def _integer_square_root(value: int) -> int:
    if value < 0:
        raise ValueError("square root requires a nonnegative integer")
    if value < 2:
        return value
    lower, upper = 1, value
    while lower + 1 < upper:
        middle = (lower + upper) // 2
        if middle * middle <= value:
            lower = middle
        else:
            upper = middle
    return lower


def probabilists_hermite_at_one(order: int) -> int:
    """Exact ``He_order(1)`` using ``He[n+1]=x He[n]-n He[n-1]``."""

    if type(order) is not int or order < 0:
        raise ValueError("order must be a nonnegative built-in integer")
    if order == 0:
        return 1
    previous, current = 1, 1
    for index in range(1, order):
        previous, current = current, current - index * previous
    return current


def gauss_legendre_remainder_coefficient(nodes: int) -> Fraction:
    """Exact derivative remainder coefficient on a unit-length interval.

    For an n-node Gauss--Legendre panel on ``[a,b]``,

      |I-Q| <= (b-a)^(2n+1) (n!)^4 / ((2n+1)((2n)!)^3) max |f^(2n)|.

    This is a rigorous ordinary derivative enclosure, not a sampled error
    surrogate.
    """

    if type(nodes) is not int or nodes < 1:
        raise ValueError("nodes must be a positive built-in integer")
    return Fraction(factorial(nodes) ** 4, (2 * nodes + 1) * factorial(2 * nodes) ** 3)


def near_parallel_rank2_factor(eta: Fraction) -> tuple[tuple[Fraction, Fraction], ...]:
    """Positive-marginal rank-two plane with a pair of kink lines at angle O(eta)."""

    if not isinstance(eta, Fraction) or not 0 < eta < 1:
        raise ValueError("eta must be a Fraction strictly between zero and one")
    # X0=U, X1=U+eta*V, X2=V.  Pair (0,1) has determinant eta.
    return ((Fraction(1), Fraction(0)), (Fraction(1), eta), (Fraction(0), Fraction(1)))


def covariance_from_factor(
    factor: Sequence[Sequence[Fraction]],
) -> tuple[tuple[Fraction, ...], ...]:
    if len(factor) != 3 or any(len(row) != 2 for row in factor):
        raise ValueError("factor must have shape 3x2")
    return tuple(
        tuple(sum((factor[i][q] * factor[j][q] for q in range(2)), Fraction(0)) for j in range(3))
        for i in range(3)
    )


def _det2(left: Sequence[Fraction], right: Sequence[Fraction]) -> Fraction:
    return left[0] * right[1] - left[1] * right[0]


def minimum_pairwise_transversality(factor: Sequence[Sequence[Fraction]]) -> Fraction:
    determinants = [abs(_det2(factor[left], factor[right])) for left in range(3) for right in range(left + 1, 3)]
    return min(determinants)


def rank2_positive_marginal_transverse_dispatch(
    factor: Sequence[Sequence[Fraction]],
) -> DispatchDecision:
    """M168's exact domain predicate, without silently taking a limit."""

    if len(factor) != 3 or any(len(row) != 2 for row in factor):
        raise ValueError("factor must have shape 3x2")
    if any(sum((entry * entry for entry in row), Fraction(0)) == 0 for row in factor):
        return DispatchDecision(StratumAction.ZERO_MARGINAL_REFUSE, "a factor row is zero")
    minimum = minimum_pairwise_transversality(factor)
    if minimum == 0:
        return DispatchDecision(
            StratumAction.NONTRANSVERSE_REFUSE,
            "at least two ReLU kink lines are parallel or coincident; M168's transverse coarea proof does not apply",
        )
    return DispatchDecision(
        StratumAction.RANK_TWO_M168_ANCHOR,
        "positive marginal rank-two plane with all pairwise kink lines transverse",
    )


def zero_marginal_dispatch(covariance: Sequence[Sequence[Fraction]]) -> DispatchDecision:
    """Preserve M159: do not divide by a zero marginal or invent a tangent."""

    if len(covariance) != 3 or any(len(row) != 3 for row in covariance):
        raise ValueError("covariance must have shape 3x3")
    zero_indices = [index for index in range(3) if covariance[index][index] == 0]
    if not zero_indices:
        return DispatchDecision(StratumAction.RANK_TWO_M168_ANCHOR, "no zero marginal in this dispatch")
    for index in zero_indices:
        if any(covariance[index][other] != 0 or covariance[other][index] != 0 for other in range(3)):
            raise ValueError("a zero diagonal with a nonzero row/column is not PSD")
    return DispatchDecision(
        StratumAction.ZERO_MARGINAL_REFUSE,
        "deterministic dimensional reduction and an explicit one-sided conic tangent are required; correlation coordinates are undefined",
    )


def regularity_obstruction(eta: Fraction) -> RegularityObstruction:
    """Certify why the fixed GL10 derivative enclosure cannot be uniform.

    Conditioning the M168 wedge on ``U=u`` produces the required indicator
    primitive ``P(U + eta*V > 0 | U=u) = Phi(u/eta)``.  It occurs in the
    Price-indicator cache before any unproved connected cancellation.  At
    ``u=eta``,

      |d^20/du^20 Phi(u/eta)| = |He_19(1)| phi(1) eta^-20.

    The elementary strict bound ``phi(1)>1/5`` follows from ``e<3`` and
    ``pi<22/7``.  Therefore every standard 20th-derivative Gauss--Legendre
    remainder enclosure has at least the returned floor.  This does not claim
    the actual quadrature error equals that floor; it proves that this
    fixed-panel derivative certificate cannot establish the target uniformly.
    """

    factor = near_parallel_rank2_factor(eta)
    covariance = covariance_from_factor(factor)
    hermite = abs(probabilists_hermite_at_one(19))
    derivative_lower = Fraction(hermite, 5) / (eta ** 20)
    envelope_floor = gauss_legendre_remainder_coefficient(FIXED_INTERIOR_NODES) * derivative_lower
    return RegularityObstruction(
        eta=eta,
        rank=2,
        all_marginals_positive=all(covariance[index][index] > 0 for index in range(3)),
        minimum_pairwise_transversality=minimum_pairwise_transversality(factor),
        derivative_order=20,
        hermite_at_one=hermite,
        phi_one_lower_bound=Fraction(1, 5),
        twentieth_derivative_lower_bound=derivative_lower,
        gauss_legendre_remainder_floor=envelope_floor,
        tolerance=NORMALIZED_VALUE_TOLERANCE,
        closes_derivative_envelope=envelope_floor <= NORMALIZED_VALUE_TOLERANCE,
        conclusion=(
            "fixed GL10 derivative enclosure fails before connected cancellation is symbolically proved"
            if envelope_floor > NORMALIZED_VALUE_TOLERANCE
            else "this particular eta does not kill the derivative enclosure"
        ),
    )


def final_disposition() -> DispatchDecision:
    """Apply all predeclared gates without testing an external response."""

    cost = predicted_cost()
    hostile = regularity_obstruction(Fraction(1, 10))
    if not cost.under_ceiling:
        return DispatchDecision(StratumAction.CERTIFICATE_KILL, "bookkeeping prediction exceeds the billed ceiling")
    if not hostile.closes_derivative_envelope:
        return DispatchDecision(
            StratumAction.CERTIFICATE_KILL,
            "uniform GL10 derivative enclosure exceeds 2e-8 on a transverse positive-marginal rank-two family; nontransverse and zero faces also lack routes",
        )
    return DispatchDecision(StratumAction.CERTIFICATE_KILL, "native bill remains unproved")


def audit_record() -> dict[str, object]:
    """A JSON-ready response-free record for the frozen report and manifest."""

    predeclaration = asdict(predeclare_provider())
    cost = asdict(predicted_cost())
    obstruction = asdict(regularity_obstruction(Fraction(1, 10)))
    for mapping in (predeclaration, cost, obstruction):
        for key, value in tuple(mapping.items()):
            if isinstance(value, Fraction):
                mapping[key] = f"{value.numerator}/{value.denominator}"
            elif isinstance(value, Enum):
                mapping[key] = value.value
    disposition = final_disposition()
    return {
        "scope": "generated response-free mathematics only",
        "predeclaration": predeclaration,
        "cost_prediction": cost,
        "regularity_obstruction_eta_1_10": obstruction,
        "disposition": {"action": disposition.action.value, "reason": disposition.reason},
        "firewall": {
            "network_response": False,
            "truth_or_scorer": False,
            "leaderboard_or_submission": False,
            "adaptive_retry": False,
            "opaque_library_cdf": False,
        },
    }
