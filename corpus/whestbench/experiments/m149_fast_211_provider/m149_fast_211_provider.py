"""M149: bounded-cost local [2,1,1] value/Frechet provider.

This is deliberately a *component*, not an estimator or a response cell.  It
keeps M147's endpoint-safe, analytic bivariate ReLU primitive, but replaces
M147's expensive ``48/64`` central integral by a single fixed nested
Gauss--Kronrod--Patterson 43/87 rule on a tangent compactification of the
conditioning normal.  The 87 values are evaluated once; the 43-node result is
obtained from the subset.  Thus there is no adaptive split/retry path.

The conservative resource contract is an 87-node outer rule plus the three
pairwise calls required for the local bridge. Each M147 bivariate call is
allowed at most 48 angular evaluations; a strict 8,000 angular-evaluation
cap fails closed.  The fine/coarse disagreement is a numerical certificate,
not a claim of a formal quadrature remainder bound.

No scorer, target network, response, or contest data is accessed here.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
import sys
from typing import Iterable

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
for relative in ("m147_endpoint_safe_bridge", "m129_source_frechet_tangent"):
    path = str(ROOT / relative)
    if path not in sys.path:
        sys.path.insert(0, path)

from m147_endpoint_safe_bridge import (  # noqa: E402
    EndpointCertificationFailure,
    _relu_covariance_dot,
    _tree_entry_dot,
    bivariate_relu_raw_dot_endpoint,
    build_endpoint_state_frechet,
    univariate_relu_mean_dot,
)


_INV_SQRT_2PI = 1.0 / math.sqrt(2.0 * math.pi)
_EPS = np.finfo(np.float64).eps


class Fast211CertificationFailure(EndpointCertificationFailure):
    """A frozen numerical or resource certificate failed; never retry."""


@dataclass(frozen=True)
class Fast211Certificate:
    central_fourth: float
    central_fourth_tangent: float
    cumulant: float
    cumulant_tangent: float
    tree: float
    tree_tangent: float
    defect: float
    defect_tangent: float
    value_disagreement: float
    tangent_disagreement: float
    outer_nodes: int
    bivariate_calls: int
    angular_evaluations: int
    conservative_billed_ops: int
    method: str


@dataclass(frozen=True)
class ZeroSchurFallbackContract:
    """Explicit hand-off for a stratum M149 does not certify.

    A caller may use the independent-normal product estimator below only as a
    *separate predeclared unbiased coefficient estimator*.  ``R`` independent
    draws are divided into four disjoint blocks: raw ``a_i^2a_ja_k`` and the
    three covariance products in the fourth cumulant.  Product blocks use
    independent sample means, hence every subtractand is unbiased.  Tangents
    are pathwise a.e. derivatives and need an independently certified local
    PSD square-root differential.  There is no ridge, clipping, or reuse of a
    failed deterministic value.  The caller must account for all draws.
    """

    stratum: str
    required_independent_blocks: int = 4
    minimum_draws_per_block: int = 2
    per_draw_scalar_relu_evaluations: int = 4
    status: str = "FALLBACK_REQUIRED_NOT_EXECUTED"

    def conservative_billed_ops(self, draws_per_block: int) -> int:
        if type(draws_per_block) is not int or draws_per_block < self.minimum_draws_per_block:
            raise ValueError("draws_per_block violates frozen fallback minimum")
        # 3x3 local root-vector multiply, 3 ReLUs, products and accumulation;
        # 96 scalar operations is intentionally a favorable lower-bound proxy.
        return self.required_independent_blocks * draws_per_block * 96


# QUADPACK's nonadaptive nested Patterson 21/43 core.  The 21 points are a
# literal subset of the 43 point rule.  Values and weights are copied as
# decimal constants so the runtime does not depend on an external library.
_X1 = np.array((
    0.973906528517171720077964012084452, 0.865063366688984510732096688423493,
    0.679409568299024406234327365114874, 0.433395394129247190799265943165784,
    0.148874338981631210884826001129720,
), dtype=np.float64)
_X2 = np.array((
    0.995657163025808080735527280689003, 0.930157491355708226001207180059508,
    0.780817726586416897063717578345042, 0.562757134668604683339000099272694,
    0.294392862701460198131126603103866,
), dtype=np.float64)
_X3 = np.array((
    0.999333360901932081394099323919911, 0.987433402908088869795961478381209,
    0.954807934814266299257919200290473, 0.900148695748328293625099494069092,
    0.825198314983114150847066732588520, 0.732148388989304982788739474980964,
    0.622847970537725238641159120344323, 0.499479574071056499952214885499755,
    0.364901661346580768043989548502644, 0.222254919776601296498260928066212,
    0.074650617461383322043914435796506,
), dtype=np.float64)
_W21A = np.array((
    0.032558162307964727478818972459390, 0.075039674810919952767043140916190,
    0.109387158802297641899210590325805, 0.134709217311473325928054001771707,
    0.147739104901338491374841515972068,
), dtype=np.float64)
_W21B = np.array((
    0.011694638867371874278064396062192, 0.054755896574351996031381300244580,
    0.093125454583697605535065465083366, 0.123491976262065851077958109831074,
    0.142775938577060080797094273138717, 0.149445554002916905664936468389821,
), dtype=np.float64)
_W43A = np.array((
    0.016296734289666564924281974617663, 0.037522876120869501461613795898115,
    0.054694902058255442147212685465005, 0.067355414609478086075553166302174,
    0.073870199632393953432140695251367, 0.005768556059769796184184327908655,
    0.027371890593248842081276069289151, 0.046560826910428830743339154433824,
    0.061744995201442564496240336030883, 0.071387267268693397768559114425516,
), dtype=np.float64)
_W43B = np.array((
    0.001844477640212414100389106552965, 0.010798689585891651740465406741293,
    0.021895363867795428102523123075149, 0.032597463975345689443882222526137,
    0.042163137935191811847627924327955, 0.050741939600184577780189020092084,
    0.058379395542619248375475369330206, 0.064746404951445885544689259517511,
    0.069566197912356484528633315038405, 0.072824441471833208150939535192842,
    0.074507751014175118273571813842889, 0.074722147517403005594425168280423,
), dtype=np.float64)
_X4 = np.array((
    0.999902977262729234490529830591582, 0.997989895986678745427496322365960,
    0.992175497860687222808523352251425, 0.981358163572712773571916941623894,
    0.965057623858384619128284110607926, 0.943167613133670596816416634507426,
    0.915806414685507209591826430720050, 0.883221657771316501372117548744163,
    0.845710748462415666605902011504855, 0.803557658035230982788739474980964,
    0.757005730685495558328942793432020, 0.706273209787321819824094274740840,
    0.651589466501177922534422205016736, 0.593223374057961088875273770349144,
    0.531493605970831932285268948562671, 0.466763623042022844871966781659270,
    0.399424847859218804732101665817923, 0.329874877106188288265053371824597,
    0.258503559202161551802280975429025, 0.185695396568346652015917141167606,
    0.111842213179907468172398359241362, 0.037352123394619870814998165437704,
), dtype=np.float64)
_W87A = np.array((
    0.008148377384149172900002878448190, 0.018761438201562822243935059003794,
    0.027347451050052286161582829741283, 0.033677707311637930046581056957588,
    0.036935099820427907614589586742499, 0.002884872430211530501334156248695,
    0.013685946022712701888950035273128, 0.023280413502888311123409291030883,
    0.030872497611713358675466394126442, 0.035693633639418770719351355457044,
    0.000915283345202241360843392549948, 0.005399280219300471367738743391053,
    0.010947679601118931134327826856808, 0.016298731696787335262665703223280,
    0.021081568889203835112433060188190, 0.025370969769253827243467999831710,
    0.029189697756475752501446154084920, 0.032373202467202789685788194889595,
    0.034783098950365142750781997949596, 0.036412220731351787562801163687577,
    0.037253875503047708539592001191226,
), dtype=np.float64)
_W87B = np.array((
    0.000274145563762072350016527092881, 0.001807124155057942948341311753254,
    0.004096869282759164864458070683480, 0.006758290051847378699816577897424,
    0.009549957672201646536053581325377, 0.012329447652244853694626639963780,
    0.015010447346388952376697286041943, 0.017548967986243191099665352925900,
    0.019938037786440888202278192730714, 0.022194935961012286796332102959499,
    0.024339147126000805470360647041454, 0.026374505414839207241503786552615,
    0.028286910788771200659968002987960, 0.030052581128092695322521110347341,
    0.031646751371439929404586051078883, 0.033050413419978503290785944862689,
    0.034255099704226061787082821046821, 0.035262412660156681033782717998428,
    0.036076989622888701185500318003895, 0.036698604498456094498018047441094,
    0.037120549269832576114119958413599, 0.037334228751935040321235449094698,
    0.037361073762679023410321241766599,
), dtype=np.float64)


def _nodes43() -> Iterable[tuple[float, float, float]]:
    """Yield (t, weight43, weight21); t lies in [-1,1]."""

    yield 0.0, float(_W43B[-1]), float(_W21B[-1])
    for x, wf, wc in zip(_X1, _W43A[:5], _W21A, strict=True):
        yield float(x), float(wf), float(wc)
        yield -float(x), float(wf), float(wc)
    for x, wf, wc in zip(_X2, _W43A[5:], _W21B[:5], strict=True):
        yield float(x), float(wf), float(wc)
        yield -float(x), float(wf), float(wc)
    for x, wf in zip(_X3, _W43B[:11], strict=True):
        yield float(x), float(wf), 0.0
        yield -float(x), float(wf), 0.0


def _nodes87() -> Iterable[tuple[float, float, float]]:
    """Yield (t, weight87, weight43); the latter is exactly nested."""

    yield 0.0, float(_W87B[-1]), float(_W43B[-1])
    for x, wf, wc in zip(_X1, _W87A[:5], _W43A[:5], strict=True):
        yield float(x), float(wf), float(wc); yield -float(x), float(wf), float(wc)
    for x, wf, wc in zip(_X2, _W87A[5:10], _W43A[5:10], strict=True):
        yield float(x), float(wf), float(wc); yield -float(x), float(wf), float(wc)
    for x, wf, wc in zip(_X3, _W87A[10:21], _W43B[:11], strict=True):
        yield float(x), float(wf), float(wc); yield -float(x), float(wf), float(wc)
    for x, wf in zip(_X4, _W87B[:22], strict=True):
        yield float(x), float(wf), 0.0; yield -float(x), float(wf), 0.0


def _local_contract(
    mean: np.ndarray, covariance: np.ndarray, mean_dot: np.ndarray, covariance_dot: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    arrays = tuple(np.asarray(item, dtype=np.float64) for item in (mean, covariance, mean_dot, covariance_dot))
    mu, cov, mud, covd = arrays
    if (
        mu.shape != (3,) or mud.shape != (3,) or cov.shape != (3, 3) or covd.shape != (3, 3)
        or not np.array_equal(cov, cov.T) or not np.array_equal(covd, covd.T)
        or not all(np.all(np.isfinite(item)) for item in arrays)
    ):
        raise Fast211CertificationFailure("local [2,1,1] state is invalid")
    if np.any(np.diag(cov) <= 0.0):
        raise Fast211CertificationFailure("local [2,1,1] needs positive marginal variances")
    return mu, cov, mud, covd


def fallback_contract_for_zero_schur(
    mean: np.ndarray, covariance: np.ndarray, *, repeated_slot: int = 0
) -> ZeroSchurFallbackContract | None:
    """Classify, never modify, the unsupported deterministic singleton stratum."""

    mu = np.asarray(mean, dtype=np.float64)
    cov = np.asarray(covariance, dtype=np.float64)
    if mu.shape != (3,) or cov.shape != (3, 3) or repeated_slot not in (0, 1, 2):
        raise ValueError("local fallback classifier requires a 3x3 state")
    singleton = [slot for slot in range(3) if slot != repeated_slot]
    base = float(cov[repeated_slot, repeated_slot])
    if not math.isfinite(base) or base <= 0.0:
        raise Fast211CertificationFailure("nonpositive repeated variance")
    diagonal = np.diag(cov)[singleton] - cov[singleton, repeated_slot] ** 2 / base
    floor = 256.0 * _EPS * max(1.0, float(np.max(np.abs(np.diag(cov)))))
    if np.any(~np.isfinite(diagonal)):
        raise Fast211CertificationFailure("nonfinite Schur diagonal")
    if np.any(diagonal <= floor):
        return ZeroSchurFallbackContract("zero-Schur-singleton")
    return None


def fast_collision211_local_state_dot(
    mean: np.ndarray,
    covariance: np.ndarray,
    mean_dot: np.ndarray,
    covariance_dot: np.ndarray,
    *,
    repeated_slot: int = 0,
    value_tolerance: float = 2.0e-8,
    tangent_tolerance: float = 2.0e-7,
    max_angular_evaluations: int = 8000,
) -> Fast211Certificate:
    """Bounded, local, deterministic 43/87 [2,1,1] provider.

    The singleton order is intentionally canonicalized.  This makes the
    contract permutation-invariant and prevents a caller from selecting a
    numerically convenient singleton ordering after observing a result.
    """

    mu, cov, mud, covd = _local_contract(mean, covariance, mean_dot, covariance_dot)
    if repeated_slot not in (0, 1, 2):
        raise ValueError("repeated_slot must be 0, 1, or 2")
    singleton = tuple(slot for slot in range(3) if slot != repeated_slot)
    fallback = fallback_contract_for_zero_schur(mu, cov, repeated_slot=repeated_slot)
    if fallback is not None:
        raise Fast211CertificationFailure(
            f"{fallback.stratum}: deterministic provider is not certified; use separately declared fallback"
        )

    # Reuse M147's exact endpoint/PSD tests and local marginal/tree calculus.
    tangent = build_endpoint_state_frechet(mu, cov, mud, covd, allow_psd_directional=True)
    i, j, k = repeated_slot, singleton[0], singleton[1]
    sigma_i = float(tangent.state.sigma[i])
    sigma_i_dot = float(tangent.sigma_dot[i])
    beta = cov[(j, k), i] / sigma_i
    beta_dot = covd[(j, k), i] / sigma_i - beta * sigma_i_dot / sigma_i
    selected = np.asarray((j, k), dtype=int)
    conditional_covariance = cov[np.ix_(selected, selected)] - np.outer(cov[selected, i], cov[selected, i]) / cov[i, i]
    conditional_covariance_dot = (
        covd[np.ix_(selected, selected)]
        - (np.outer(covd[selected, i], cov[selected, i]) + np.outer(cov[selected, i], covd[selected, i])) / cov[i, i]
        + np.outer(cov[selected, i], cov[selected, i]) * covd[i, i] / cov[i, i] ** 2
    )
    if np.any(np.diag(conditional_covariance) <= 0.0):
        raise Fast211CertificationFailure("positive conditional singleton variance was lost")

    fine_value = fine_tangent = coarse_value = coarse_tangent = 0.0
    angular_evaluations = 0
    calls = 0
    for t, wf, wc in _nodes87():
        # t -> tan(pi t/2) maps the entire normal line.  The 87-node rule
        # resolves the fixed ReLU kink while remaining below the hard cap.
        angle = 0.5 * math.pi * t
        z = math.tan(angle)
        jacobian = 0.5 * math.pi / (math.cos(angle) ** 2)
        density = _INV_SQRT_2PI * math.exp(-0.5 * z * z)
        # For remote nodes normal underflow is the exact float64 contribution.
        if density == 0.0:
            continue
        repeated = max(0.0, float(mu[i] + sigma_i * z))
        repeated_dot = (float(mud[i]) + sigma_i_dot * z) if repeated > 0.0 else 0.0
        conditional_mean = mu[selected] + beta * z
        conditional_mean_dot = mud[selected] + beta_dot * z
        pair = bivariate_relu_raw_dot_endpoint(
            conditional_mean, conditional_covariance, conditional_mean_dot,
            conditional_covariance_dot, quadrant_tolerance=1.0e-10,
        )
        calls += 1
        angular_evaluations += pair.quadrant.integrand_evaluations + pair.moment_integrand_evaluations
        if angular_evaluations > max_angular_evaluations:
            raise Fast211CertificationFailure("frozen angular-evaluation cap exceeded")
        left_mean, left_mean_dot = univariate_relu_mean_dot(
            float(conditional_mean[0]), float(conditional_covariance[0, 0]),
            float(conditional_mean_dot[0]), float(conditional_covariance_dot[0, 0]),
        )
        right_mean, right_mean_dot = univariate_relu_mean_dot(
            float(conditional_mean[1]), float(conditional_covariance[1, 1]),
            float(conditional_mean_dot[1]), float(conditional_covariance_dot[1, 1]),
        )
        global_left, global_right = float(tangent.state.relu_mean[j]), float(tangent.state.relu_mean[k])
        global_left_dot, global_right_dot = float(tangent.relu_mean_dot[j]), float(tangent.relu_mean_dot[k])
        conditional_centered = pair.raw - global_left * right_mean - global_right * left_mean + global_left * global_right
        conditional_centered_dot = (
            pair.tangent - global_left_dot * right_mean - global_left * right_mean_dot
            - global_right_dot * left_mean - global_right * left_mean_dot
            + global_left_dot * global_right + global_left * global_right_dot
        )
        repeated_centered = repeated - float(tangent.state.relu_mean[i])
        repeated_centered_dot = repeated_dot - float(tangent.relu_mean_dot[i])
        common = density * jacobian
        value = common * repeated_centered * repeated_centered * conditional_centered
        dot = common * (
            2.0 * repeated_centered * repeated_centered_dot * conditional_centered
            + repeated_centered * repeated_centered * conditional_centered_dot
        )
        fine_value += wf * value
        fine_tangent += wf * dot
        if wc:
            coarse_value += wc * value
            coarse_tangent += wc * dot

    value_disagreement = abs(fine_value - coarse_value)
    tangent_disagreement = abs(fine_tangent - coarse_tangent)
    if value_disagreement > value_tolerance:
        raise Fast211CertificationFailure("43/87 value certificate failed")
    if tangent_disagreement > tangent_tolerance:
        raise Fast211CertificationFailure("43/87 tangent certificate failed")

    var_i, var_i_dot = _relu_covariance_dot(tangent, i, i)
    cov_jk, cov_jk_dot = _relu_covariance_dot(tangent, j, k)
    cov_ij, cov_ij_dot = _relu_covariance_dot(tangent, i, j)
    cov_ik, cov_ik_dot = _relu_covariance_dot(tangent, i, k)
    cumulant = fine_value - var_i * cov_jk - 2.0 * cov_ij * cov_ik
    cumulant_dot = fine_tangent - var_i_dot * cov_jk - var_i * cov_jk_dot - 2.0 * (cov_ij_dot * cov_ik + cov_ij * cov_ik_dot)
    tree, tree_dot = _tree_entry_dot(tangent, (i, i, j, k))
    all_values = (fine_value, fine_tangent, cumulant, cumulant_dot, tree, tree_dot)
    if not all(math.isfinite(item) for item in all_values):
        raise Fast211CertificationFailure("nonfinite [2,1,1] output")
    # 87 bivariate calls, each a strict at-most-48 angular primitive, plus
    # three bridge pair calls (also at most 48) and scalar local algebra.
    conservative_ops = (87 + 3) * 48 * 10 + 4096
    return Fast211Certificate(
        fine_value, fine_tangent, cumulant, cumulant_dot, tree, tree_dot,
        cumulant - tree, cumulant_dot - tree_dot, value_disagreement,
        tangent_disagreement, 87, calls, angular_evaluations, conservative_ops,
        "fixed-nested-patterson-43-87 + M147-endpoint-bivariate",
    )
