"""M216 response-free strict-distinct antithetic conditional provider.

This child deliberately imports M213 only as a narrow mathematical atom.  It
does not expose M213's collision paths or a complete Source211 table.  The hot
event is the exact symmetry coupling ``(Z(g)+Z(-g))/2``.  Reference work is
lazy so the production-shaped resource runner has no scipy/mpmath dependency.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import ctypes
from ctypes import wintypes
import json
import math
import os
from pathlib import Path
import sys
import time
from typing import Iterable

import numpy as np


HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
for _sibling in (
    "m213_event_local_randomized_source211",
    "m178_certified_phi2_owent",
):
    _path = str(EXPERIMENTS / _sibling)
    if _path not in sys.path:
        sys.path.insert(0, _path)

import m213_event_local_randomized_source211 as _m213  # noqa: E402
import m178_certified_phi2_owent as _m178  # noqa: E402


MUTATION = "M216"
WIDTHS = (3, 4, 5, 6, 7)
STATE_SEEDS = (216700003, 216700004, 216700005, 216700006, 216700007)
NUMERICAL_G = (
    0.0,
    2.0**-8,
    -(2.0**-8),
    0.25,
    -0.25,
    1.0,
    -1.0,
    2.5,
    -2.5,
    5.0,
    -5.0,
    8.0,
    -8.0,
)
NATIVE_SEEDS = (216720001, 216720002, 216720003, 216720004, 216720005)
TARGET_EVENTS = 31 * 128
WARMUP_EVENTS = 256
M178_WORST_INCLUSIVE = 4048
LOCAL_STATIC_ALLOWANCE = 4096
STATIC_PER_EVENT_CEILING = 2 * M178_WORST_INCLUSIVE + LOCAL_STATIC_ALLOWANCE
TARGET_STATIC_CEILING = TARGET_EVENTS * STATIC_PER_EVENT_CEILING
COMPONENT_CEILING = 6_824_272_176
LAMBDA_FLOPS_PER_SECOND = 1.0e11
HOSTILE_WALL_FACTOR = 5.0
RSS_CEILING = 512 * 1024 * 1024
RADIUS_RATIO_LIMIT = 2.0e-7
LOCAL_FIXED_CHARGED = 256
_PLACKETT_GL_NODES, _PLACKETT_GL_WEIGHTS = np.polynomial.legendre.leggauss(32)


class M216DomainRefusal(RuntimeError):
    """The caller requested anything outside strict `[2,1,1]`."""


@dataclass(frozen=True)
class AntitheticEvent:
    labels: tuple[int, int, int, int]
    value: float
    radius: float
    contained: bool
    m178_calls: int
    plus_value: float
    minus_value: float


@dataclass(frozen=True)
class IdentityOracleResult:
    width: int
    labels: tuple[int, int, int]
    reference: float
    reference_crosscheck: float
    candidate_integral: float
    candidate_quad_error: float
    oracle_gap: float
    identity_error: float
    oracle_self_pass: bool
    identity_pass: bool
    oracle_method: str = "mpmath-adaptive-1d-plackett-pair"


def frozen_manifest() -> dict[str, object]:
    return json.loads((HERE / "M216_FROZEN_MANIFEST_20260809.json").read_text())


def generated_spd_cell(width: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    """The inherited response-free cell generator, with M216's width guard."""

    if width not in WIDTHS:
        raise ValueError("width outside frozen M216 domain")
    return _m213.generated_spd_cell(width, seed)


def build_local_state(mean: np.ndarray, covariance: np.ndarray):
    return _m213.build_local_state(mean, covariance)


def frozen_local_state(width: int, seed: int):
    mean, covariance = generated_spd_cell(width, seed)
    return build_local_state(mean, covariance)


def parent_distinct_event(local, repeated: int, left: int, right: int, outer_g: float):
    if len({int(repeated), int(left), int(right)}) != 3:
        raise M216DomainRefusal("M216 parent atom requires three distinct labels")
    return _m213.distinct_event_from_outer_g(
        local, int(repeated), int(left), int(right), float(outer_g)
    )


def _parse_strict_labels(local, labels: tuple[int, int, int, int]) -> tuple[int, int, int]:
    labels = tuple(int(item) for item in labels)
    if len(labels) != 4 or any(item < 0 or item >= local.mean.size for item in labels):
        raise M216DomainRefusal("four in-range labels are required")
    counts = {item: labels.count(item) for item in set(labels)}
    if sorted(counts.values(), reverse=True) != [2, 1, 1]:
        raise M216DomainRefusal(
            "M216 excludes [4], [3,1], [2,2], and [1,1,1,1]"
        )
    repeated = next(item for item, count in counts.items() if count == 2)
    singletons = sorted(item for item, count in counts.items() if count == 1)
    if repeated in singletons or len(singletons) != 2:
        raise AssertionError("strict ownership parser failed")
    return repeated, singletons[0], singletons[1]


def antithetic_distinct_event(
    local,
    labels: tuple[int, int, int, int],
    outer_g: float,
) -> AntitheticEvent:
    """Return `(Z(g)+Z(-g))/2`; no collision or wedge fallback exists."""

    repeated, left, right = _parse_strict_labels(local, labels)
    g = float(outer_g)
    if not math.isfinite(g):
        raise M216DomainRefusal("outer G must be finite")
    plus = parent_distinct_event(local, repeated, left, right, g)
    minus = parent_distinct_event(local, repeated, left, right, -g)
    if (
        plus.refused
        or minus.refused
        or plus.value is None
        or minus.value is None
        or not plus.m178_contained
        or not minus.m178_contained
    ):
        raise M216DomainRefusal("one antithetic M178 branch refused")
    value = 0.5 * (float(plus.value) + float(minus.value))
    radius = 0.5 * (float(plus.m178_radius) + float(minus.m178_radius))
    if not (math.isfinite(value) and math.isfinite(radius) and radius >= 0.0):
        raise M216DomainRefusal("nonfinite antithetic value or enclosure")
    return AntitheticEvent(
        (repeated, repeated, left, right),
        value,
        radius,
        True,
        int(plus.conditional_m178_calls + minus.conditional_m178_calls),
        float(plus.value),
        float(minus.value),
    )


def strict_physical_owners(width: int) -> tuple[tuple[int, int, int, int], ...]:
    return tuple(
        (repeated, repeated, left, right)
        for repeated in range(width)
        for left in range(width)
        for right in range(left + 1, width)
        if repeated not in (left, right)
    )


def _load_mpmath():
    try:
        import mpmath as mp
        return mp
    except ModuleNotFoundError:
        site = Path(r"C:\Users\strid\.venvs\whestbench-frozen-m178\Lib\site-packages")
        if not site.exists():
            raise
        sys.path.insert(0, str(site))
        import mpmath as mp
        return mp


def _mp_number(mp, value: float):
    return mp.mpf(repr(float(value)))


def _mp_phi(mp, x):
    return mp.exp(-x * x / 2) / mp.sqrt(2 * mp.pi)


def _mp_Phi(mp, x):
    return mp.erfc(-x / mp.sqrt(2)) / 2


def _mp_Phi2_plackett(mp, a, b, rho):
    """Independent high-precision Phi2 via Plackett's rho integral.

    The outer reference is the predeclared adaptive one-dimensional oracle.
    Its bivariate atom uses a 32-node high-precision Plackett assembly instead
    of recursively nesting another adaptive integrator.  On M216's frozen
    cells the conditional ``|rho|`` is at most 0.036, so the smooth analytic
    rho integrand is far inside this rule's convergence regime.
    """

    base = _mp_Phi(mp, a) * _mp_Phi(mp, b)
    if rho == 0:
        return base

    def density(r):
        one = 1 - r * r
        exponent = -(a * a - 2 * r * a * b + b * b) / (2 * one)
        return mp.exp(exponent) / (2 * mp.pi * mp.sqrt(one))

    half = rho / 2
    integral = mp.fsum(
        _mp_number(mp, weight)
        * density(half * (_mp_number(mp, node) + 1))
        for node, weight in zip(
            _PLACKETT_GL_NODES, _PLACKETT_GL_WEIGHTS, strict=True
        )
    ) * half
    return base + integral


def _mp_bivariate_relu(mp, mean0, mean1, var0, var1, cov01):
    """Independent Rosenbaum positive-part product in arbitrary precision."""

    sigma0 = mp.sqrt(var0)
    sigma1 = mp.sqrt(var1)
    rho = cov01 / (sigma0 * sigma1)
    q = mp.sqrt(1 - rho * rho)
    h = -mean0 / sigma0
    k = -mean1 / sigma1
    A = _mp_Phi(mp, (rho * h - k) / q)
    B = _mp_Phi(mp, (rho * k - h) / q)
    ph = _mp_phi(mp, h)
    pk = _mp_phi(mp, k)
    lb = 1 - _mp_Phi(mp, h) - _mp_Phi(mp, k) + _mp_Phi2_plackett(mp, h, k, rho)
    ex = ph * A + rho * pk * B
    ey = pk * B + rho * ph * A
    phi2 = mp.exp(-(h * h - 2 * rho * h * k + k * k) / (2 * q * q)) / (2 * mp.pi * q)
    exy = rho * lb + rho * h * ph * A + rho * k * pk * B + q * q * phi2
    return (
        mean0 * mean1 * lb
        + mean0 * sigma1 * ey
        + mean1 * sigma0 * ex
        + sigma0 * sigma1 * exy
    )


def _mp_univariate_relu_mean(mp, mean, variance):
    sigma = mp.sqrt(variance)
    alpha = mean / sigma
    return mean * _mp_Phi(mp, alpha) + sigma * _mp_phi(mp, alpha)


def _mp_event_atom(mp, local, repeated: int, left: int, right: int, g):
    """Independent high-precision reconstruction of the M213 tower atom."""

    mu = [_mp_number(mp, item) for item in local.mean]
    sigma = [_mp_number(mp, item) for item in local.sigma]
    cov = [[_mp_number(mp, item) for item in row] for row in local.covariance]
    activation_mean = [_mp_number(mp, item) for item in local.activation_mean]
    activation_cov = [
        [_mp_number(mp, item) for item in row]
        for row in local.activation_covariance
    ]
    vi = cov[repeated][repeated]
    conditional_mean_left = mu[left] + cov[left][repeated] * g / sigma[repeated]
    conditional_mean_right = mu[right] + cov[right][repeated] * g / sigma[repeated]
    conditional_var_left = cov[left][left] - cov[left][repeated] ** 2 / vi
    conditional_var_right = cov[right][right] - cov[right][repeated] ** 2 / vi
    conditional_cov = (
        cov[left][right]
        - cov[left][repeated] * cov[right][repeated] / vi
    )
    raw_pair = _mp_bivariate_relu(
        mp,
        conditional_mean_left,
        conditional_mean_right,
        conditional_var_left,
        conditional_var_right,
        conditional_cov,
    )
    left_mean = _mp_univariate_relu_mean(mp, conditional_mean_left, conditional_var_left)
    right_mean = _mp_univariate_relu_mean(mp, conditional_mean_right, conditional_var_right)
    centered_pair = (
        raw_pair
        - activation_mean[left] * right_mean
        - activation_mean[right] * left_mean
        + activation_mean[left] * activation_mean[right]
    )
    preactivation = mu[repeated] + sigma[repeated] * g
    centered_repeated = max(mp.mpf("0"), preactivation) - activation_mean[repeated]
    central = centered_repeated * centered_repeated * centered_pair
    covariance_products = (
        activation_cov[repeated][repeated] * activation_cov[left][right]
        + 2 * activation_cov[repeated][left] * activation_cov[repeated][right]
    )
    tree = _mp_number(mp, local.tree_211(repeated, left, right))
    return central - covariance_products - tree


def _mp_reference(local, repeated: int, left: int, right: int, dps: int) -> float:
    mp = _load_mpmath()
    with mp.workdps(int(dps)):
        boundary = -_mp_number(mp, local.mean[repeated]) / _mp_number(mp, local.sigma[repeated])

        def integrand(g):
            return _mp_phi(mp, g) * _mp_event_atom(
                mp, local, repeated, left, right, g
            )

        value = mp.quad(integrand, [-mp.inf, boundary, mp.inf])
        return float(value)


def _adaptive_antithetic_integral(
    local, repeated: int, left: int, right: int
) -> tuple[float, float]:
    """Independent adaptive outer integration of the actual M216 kernel."""

    from scipy.integrate import quad

    inv_sqrt_2pi = 1.0 / math.sqrt(2.0 * math.pi)

    def integrand(g: float) -> float:
        # Integral over g>=0 of phi(g)*(Z(g)+Z(-g)) equals E[A(G)].
        coupled = antithetic_distinct_event(
            local, (repeated, repeated, left, right), float(g)
        )
        return (
            inv_sqrt_2pi
            * math.exp(-0.5 * g * g)
            * (coupled.plus_value + coupled.minus_value)
        )

    value, error = quad(
        integrand,
        0.0,
        np.inf,
        epsabs=5.0e-11,
        epsrel=5.0e-11,
        limit=300,
        points=None,
    )
    return float(value), float(error)


def identity_oracle_check(
    local,
    repeated: int,
    left: int,
    right: int,
    *,
    primary_dps: int = 60,
    crosscheck_dps: int = 80,
) -> IdentityOracleResult:
    if len({repeated, left, right}) != 3:
        raise M216DomainRefusal("identity oracle is strict-distinct only")
    primary = _mp_reference(local, repeated, left, right, primary_dps)
    crosscheck = _mp_reference(local, repeated, left, right, crosscheck_dps)
    candidate, quad_error = _adaptive_antithetic_integral(
        local, repeated, left, right
    )
    oracle_gap = abs(primary - crosscheck)
    identity_error = abs(candidate - crosscheck)
    oracle_limit = 2.0e-11 * (1.0 + abs(crosscheck))
    identity_limit = 5.0e-8 * (1.0 + abs(crosscheck))
    return IdentityOracleResult(
        int(local.mean.size),
        (int(repeated), int(left), int(right)),
        primary,
        crosscheck,
        candidate,
        quad_error,
        oracle_gap,
        identity_error,
        bool(math.isfinite(primary) and math.isfinite(crosscheck) and oracle_gap <= oracle_limit),
        bool(math.isfinite(candidate) and identity_error <= identity_limit),
    )


def run_identity_gate() -> dict[str, object]:
    rows: list[dict[str, object]] = []
    for width, seed in zip(WIDTHS, STATE_SEEDS, strict=True):
        local = frozen_local_state(width, seed)
        for repeated, left, right in ((0, 1, 2), (width - 1, 0, 1)):
            rows.append(
                asdict(identity_oracle_check(local, repeated, left, right))
            )
    passed = all(row["oracle_self_pass"] and row["identity_pass"] for row in rows)
    return {
        "identity_gate_pass": bool(passed),
        "event_count": len(rows),
        "max_oracle_gap": max(float(row["oracle_gap"]) for row in rows),
        "max_identity_error": max(float(row["identity_error"]) for row in rows),
        "rows": rows,
    }


def run_invariance_gate() -> dict[str, object]:
    width = 5
    local = frozen_local_state(width, 216700005)
    gauge = np.exp(np.asarray((-0.4, -0.1, 0.0, 0.2, 0.5)))
    permutation = np.asarray((3, 0, 4, 1, 2), dtype=int)
    inverse = np.argsort(permutation)
    gauged = build_local_state(
        local.mean * gauge,
        local.covariance * gauge[:, None] * gauge[None, :],
    )
    permuted = build_local_state(
        local.mean[permutation],
        local.covariance[np.ix_(permutation, permutation)],
    )
    max_swap = 0.0
    max_gauge_ratio = 0.0
    max_permutation_ratio = 0.0
    count = 0
    for labels in strict_physical_owners(width):
        repeated, _, left, right = labels
        for g in (-2.0, -0.5, 0.0, 0.75, 2.5):
            baseline = antithetic_distinct_event(local, labels, g).value
            swapped = antithetic_distinct_event(
                local, (repeated, repeated, right, left), g
            ).value
            max_swap = max(max_swap, abs(swapped - baseline))
            observed_gauge = antithetic_distinct_event(gauged, labels, g).value
            expected_gauge = (
                baseline
                * gauge[repeated] ** 2
                * gauge[left]
                * gauge[right]
            )
            max_gauge_ratio = max(
                max_gauge_ratio,
                abs(observed_gauge - expected_gauge) / (1.0 + abs(expected_gauge)),
            )
            permuted_labels = tuple(int(inverse[index]) for index in labels)
            observed_permutation = antithetic_distinct_event(
                permuted, permuted_labels, g
            ).value
            max_permutation_ratio = max(
                max_permutation_ratio,
                abs(observed_permutation - baseline) / (1.0 + abs(baseline)),
            )
            count += 1
    passed = (
        max_swap <= 2.0e-12
        and max_gauge_ratio <= 5.0e-8
        and max_permutation_ratio <= 5.0e-8
    )
    return {
        "invariance_gate_pass": bool(passed),
        "event_probe_count": count,
        "max_singleton_swap_absolute": max_swap,
        "max_gauge_scaled_error": max_gauge_ratio,
        "max_permutation_scaled_error": max_permutation_ratio,
    }


def _conditional_pair_coordinates(local, repeated: int, left: int, right: int, g: float):
    conditional_mean, conditional_covariance = _m213._condition_on_outer_g(
        local, repeated, left, right, g
    )
    sigma = np.sqrt(np.diag(conditional_covariance))
    alpha = conditional_mean / sigma
    rho = float(conditional_covariance[0, 1] / (sigma[0] * sigma[1]))
    return conditional_mean, conditional_covariance, alpha, rho


def counted_local_cost(local, labels: tuple[int, int, int, int], g: float) -> int:
    """Charged unary charts plus a conservative fixed local-DAG surcharge."""

    repeated, left, right = _parse_strict_labels(local, labels)
    backend = _m178.CountingBackend()
    for sign in (1.0, -1.0):
        _, _, alpha, _ = _conditional_pair_coordinates(
            local, repeated, left, right, sign * float(g)
        )
        for value in alpha:
            x = backend.c(float(value))
            _m178._Phi_cert(backend, x)
            _m178._phi_cert(backend, x)
    return int(backend.flops + LOCAL_FIXED_CHARGED)


def run_numerical_and_static_gates() -> dict[str, object]:
    max_radius_ratio = 0.0
    worst_radius_record: dict[str, object] | None = None
    max_local = 0
    event_count = 0
    numerical_pass = True
    for width, seed in zip(WIDTHS, STATE_SEEDS, strict=True):
        local = frozen_local_state(width, seed)
        for labels in strict_physical_owners(width):
            for g in NUMERICAL_G:
                try:
                    event = antithetic_distinct_event(local, labels, g)
                    ratio = event.radius / (1.0 + abs(event.value))
                    local_cost = counted_local_cost(local, labels, g)
                    numerical_pass = numerical_pass and (
                        event.contained
                        and event.m178_calls == 2
                        and math.isfinite(ratio)
                        and ratio <= RADIUS_RATIO_LIMIT
                    )
                    max_radius_ratio = max(max_radius_ratio, ratio)
                    if worst_radius_record is None or ratio > float(worst_radius_record["radius_ratio"]):
                        worst_radius_record = {
                            "width": width,
                            "seed": seed,
                            "labels": list(labels),
                            "outer_g": g,
                            "value": event.value,
                            "radius": event.radius,
                            "radius_ratio": ratio,
                        }
                    max_local = max(max_local, local_cost)
                    event_count += 1
                except (M216DomainRefusal, _m213.M213Refusal):
                    numerical_pass = False
    static_per_event = 2 * M178_WORST_INCLUSIVE + max_local
    static_pass = (
        max_local <= LOCAL_STATIC_ALLOWANCE
        and static_per_event <= STATIC_PER_EVENT_CEILING
        and TARGET_STATIC_CEILING == 48_377_856
    )
    return {
        "numerical_gate_pass": bool(numerical_pass),
        "static_gate_pass": bool(static_pass),
        "event_probe_count": event_count,
        "max_radius_ratio": max_radius_ratio,
        "worst_radius_record": worst_radius_record,
        "m178_calls_per_event": 2,
        "m178_worst_inclusive_per_call": M178_WORST_INCLUSIVE,
        "local_counted_worst": max_local,
        "local_static_allowance": LOCAL_STATIC_ALLOWANCE,
        "observed_static_per_event": static_per_event,
        "static_per_event_worst": STATIC_PER_EVENT_CEILING,
        "target_static_worst": TARGET_STATIC_CEILING,
    }


def billed_m178_pair_probe(local, labels: tuple[int, int, int, int], g: float) -> dict[str, object]:
    """Verify both actual M178 branches against the installed FlopScope meter."""

    import flopscope as flops

    repeated, left, right = _parse_strict_labels(local, labels)
    arguments: list[tuple[float, float, float]] = []
    expected = 0
    for sign in (1.0, -1.0):
        _, _, alpha, rho = _conditional_pair_coordinates(
            local, repeated, left, right, sign * float(g)
        )
        arguments.append((float(alpha[0]), float(alpha[1]), rho))
        counter = _m178.CountingBackend()
        result = _m178.evaluate(*arguments[-1], backend=counter)
        if result.refused:
            raise M216DomainRefusal("counted M178 probe refused")
        expected += int(counter.flops)
    backend = _m178.FlopscopeBackend()
    with flops.BudgetContext(10**8, quiet=True):
        before = int(flops.budget_summary_dict()["flops_used"])
        results = [_m178.evaluate(*args, backend=backend) for args in arguments]
        after = int(flops.budget_summary_dict()["flops_used"])
    if any(result.refused for result in results):
        raise M216DomainRefusal("billed M178 probe refused")
    billed = after - before
    return {
        "calls": 2,
        "counted": expected,
        "billed": billed,
        "match": billed == expected,
        "within_two_call_worst": billed <= 2 * M178_WORST_INCLUSIVE,
    }


def _rss_bytes() -> int:
    if os.name != "nt":
        try:
            import resource
            # Linux ru_maxrss is KiB; macOS is bytes.  This campaign is Windows.
            value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
            return value * 1024
        except Exception:
            return 0

    class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
        _fields_ = [
            ("cb", ctypes.c_ulong),
            ("PageFaultCount", ctypes.c_ulong),
            ("PeakWorkingSetSize", ctypes.c_size_t),
            ("WorkingSetSize", ctypes.c_size_t),
            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
            ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
            ("PagefileUsage", ctypes.c_size_t),
            ("PeakPagefileUsage", ctypes.c_size_t),
        ]

    counters = PROCESS_MEMORY_COUNTERS()
    counters.cb = ctypes.sizeof(counters)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    kernel32.GetCurrentProcess.argtypes = []
    kernel32.GetCurrentProcess.restype = wintypes.HANDLE
    psapi.GetProcessMemoryInfo.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(PROCESS_MEMORY_COUNTERS),
        wintypes.DWORD,
    ]
    psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
    handle = kernel32.GetCurrentProcess()
    ok = psapi.GetProcessMemoryInfo(
        handle, ctypes.byref(counters), counters.cb
    )
    return int(counters.PeakWorkingSetSize) if ok else 0


def run_native_trace(seed: int) -> dict[str, object]:
    """Time the exact reference implementation for the frozen target count."""

    local = frozen_local_state(7, int(seed))
    owners = strict_physical_owners(7)
    rng = np.random.default_rng(int(seed))
    warm_g = rng.normal(size=WARMUP_EVENTS)
    hot_g = rng.normal(size=TARGET_EVENTS)
    checksum = 0.0
    for slot, g in enumerate(warm_g):
        checksum += antithetic_distinct_event(
            local, owners[slot % len(owners)], float(g)
        ).value
    rss_before = _rss_bytes()
    start = time.perf_counter()
    for slot, g in enumerate(hot_g):
        checksum += antithetic_distinct_event(
            local, owners[slot % len(owners)], float(g)
        ).value
    elapsed = time.perf_counter() - start
    rss_after = _rss_bytes()
    peak_rss = max(rss_before, rss_after)
    effective = (
        TARGET_STATIC_CEILING
        + HOSTILE_WALL_FACTOR * LAMBDA_FLOPS_PER_SECOND * elapsed
    )
    return {
        "seed": int(seed),
        "events": TARGET_EVENTS,
        "warmup_events": WARMUP_EVENTS,
        "elapsed_s": elapsed,
        "events_per_second": TARGET_EVENTS / elapsed,
        "checksum": checksum,
        "peak_rss_bytes": peak_rss,
        "hostile_effective_cost": effective,
        "component_ceiling": COMPONENT_CEILING,
        "time_pass": effective <= COMPONENT_CEILING,
        "memory_pass": 0 < peak_rss <= RSS_CEILING,
        "pass": effective <= COMPONENT_CEILING and 0 < peak_rss <= RSS_CEILING,
    }


def run_native_gate() -> dict[str, object]:
    local = frozen_local_state(3, 216700003)
    billed = billed_m178_pair_probe(local, (0, 0, 1, 2), 0.73)
    traces = [run_native_trace(seed) for seed in NATIVE_SEEDS]
    passed = billed["match"] and billed["within_two_call_worst"] and all(
        trace["pass"] for trace in traces
    )
    return {
        "native_gate_pass": bool(passed),
        "billed_m178_pair_probe": billed,
        "trace_count": len(traces),
        "all_trace_pass": all(trace["pass"] for trace in traces),
        "worst_hostile_effective_cost": max(
            float(trace["hostile_effective_cost"]) for trace in traces
        ),
        "best_hostile_effective_cost": min(
            float(trace["hostile_effective_cost"]) for trace in traces
        ),
        "traces": traces,
    }


def main() -> None:
    # Fast default: no high-precision oracle and no 5-trace timing run.
    print(json.dumps(run_numerical_and_static_gates(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
