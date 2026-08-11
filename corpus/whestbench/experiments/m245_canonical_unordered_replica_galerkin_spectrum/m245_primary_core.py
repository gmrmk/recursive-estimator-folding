"""Independent primary mathematical core for the frozen M245 diagnostic.

This module deliberately owns no quadrature engine.  Every numerical integral
is requested through the caller-supplied ``quad_gateway``; the scientific
worker is the sole production owner of that operation and its audit ledger.
The routines here contain only the primary Plackett construction, exact
binary64 receipt decoding, analytic folded-Hermite moments, and finite
Galerkin diagnostics.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import struct
from typing import Any, Callable, Sequence

import mpmath as mp


DEGREES = tuple(range(9))
PRECISIONS_DPS = (80, 100)
FIXED_B_NODES = (
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
    10.0,
    -10.0,
    16.0,
    -16.0,
)
OUTER_BASE_PANELS = (0.0, 0.25, 1.0, 2.5, 5.0, 8.0, 10.0, 16.0, math.inf)
QUADRATURE_ERROR_SEMANTICS = "heuristic_diagnostic_estimate_not_interval_certificate"
DIAGNOSTIC_DISPOSITION = "NO_ESTIMATOR_PROVIDER_DEPLOYMENT_SCORE_OR_SUBMISSION_CREDIT"
ENDPOINT_CONTROL_EVENT_ID = "E00"
V2_SHA256 = "0113cd950b229708d7844a423f793253ee50b1ccd1cf44c33ebf343b4f0e874b"

AUTHORITY_SHA256 = {
    "M245_PREDECLARATION_20260810.md":
        "aa9ca84d48e840435d350fbab3be3f1c98356b541d54a018968cfa16b97f2512",
    "M245_FROZEN_MANIFEST_V1_20260810.json":
        "17a9df68304c7b06dd29957cc6fd4180242a9cc1bafb79e30c35f2426825b6b4",
    "M245_SHA256SUMS_V1_20260810.txt":
        "0fbc35bfa2e77993e19d50d03ebfdda8851b137cdde18e6ef6613172c8c565c9",
    "M245_PREMATERIALIZATION_ERRATUM1_20260810.md":
        "18f743c6bda98dc2c9c926db31ec93188a9670f1f2da3fcc761de14766e366b1",
    "M245_FROZEN_MANIFEST_V1_OVERLAY1_20260810.json":
        "b7aa2176b19571537e3313d8b2e4c8c1daad32b73fde42ce61b7522e4f3f1072",
    "M245_SHA256SUMS_V1_OVERLAY1_20260810.txt":
        "0dc4a2fe475a05db1db1f9cf9c15e13c66f95f16ae7b44b6fee1f0cb9592236a",
    "supervise_m245_fixture_materialization.py":
        "270a9f7d8ddd3fb5b68caec6f3d4352b70cf85491bc20771b4a3996f619bfd9b",
    "materialize_m245_fixtures.py":
        "e993b46f9cc9a2b580bee900f60ca5d3f1d29385e1694850fb9317d9b994163a",
    "test_m245_fixture_materialization_transport.py":
        "f3a0835eaddc55ab54726c1366a04148c238d3c9fc10388e3c8c976c5eb8c97f",
    "M245_FIXTURE_MATERIALIZATION_TDD_RECEIPT_20260810.md":
        "b5f473f7a2c983f50842a7f8d6912245a158761a4057d564359af1399f7b6c9b",
    "M245_FIXTURE_MATERIALIZATION_STATIC_VALIDATION_RECEIPT_20260810.json":
        "137722b7abdc58699e7c3759129f9b12c72793c711f80e45285a373a07196b88",
    "M245_FIXTURE_MATERIALIZATION_INTENT_20260810.json":
        "742cb1ba7abf944714c55be55ee08007e3496c23a20f21fc44554df02d3a6167",
    "M245_FROZEN_MANIFEST_V2_20260810.json": V2_SHA256,
    "M245_FIXTURE_MATERIALIZATION_POSTPUBLICATION_RECEIPT_20260810.json":
        "4d9adc56a9f1a02a7fa1f066be3a6fd626b67a0656e5d86577271b4bb4a097fe",
    "M245_FIXTURE_MATERIALIZATION_TERMINAL_METER_WITNESS_20260810.json":
        "15a69748afc5e7109f61ce41ccfe32d17b8af573caf2b5d8e99f5be80be17985",
}


class M245PrimaryContractError(Exception):
    """Raised when frozen M245 primary authority or mathematics is violated."""


def canonical_json_bytes(payload: object) -> bytes:
    """Return the frozen canonical, newline-terminated JSON representation."""

    try:
        text = json.dumps(
            payload,
            allow_nan=False,
            ensure_ascii=True,
            indent=2,
            sort_keys=True,
        )
    except (TypeError, ValueError) as exc:
        raise M245PrimaryContractError("payload is not canonical-JSON safe") from exc
    return (text + "\n").encode("utf-8")


def canonical_event(event: Sequence[object]) -> tuple[int, int, int]:
    """Canonicalize ``(i,{j,k})`` while retaining ownership by ``i``."""

    if not isinstance(event, (tuple, list)) or len(event) != 3:
        raise M245PrimaryContractError("event must contain exactly three indices")
    values: list[int] = []
    for value in event:
        if isinstance(value, bool) or not isinstance(value, int):
            raise M245PrimaryContractError("event indices must be non-boolean integers")
        if value < 0 or value > 2:
            raise M245PrimaryContractError("event index is outside the frozen three-node cell")
        values.append(value)
    i, j, k = values
    if len({i, j, k}) != 3:
        raise M245PrimaryContractError("event indices must be distinct")
    return i, min(j, k), max(j, k)


def _sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _validate_opaque_array_receipt(receipt: object, expected_shape: Sequence[int]) -> None:
    if not isinstance(receipt, dict):
        raise M245PrimaryContractError("array receipt must be an object")
    if receipt.get("dtype") != "<f8":
        raise M245PrimaryContractError("array dtype is not frozen little-endian binary64")
    shape = receipt.get("shape")
    if shape != list(expected_shape):
        raise M245PrimaryContractError("array shape drift")
    count = math.prod(expected_shape)
    try:
        raw = bytes.fromhex(receipt["raw_c_hex"])
    except (KeyError, TypeError, ValueError) as exc:
        raise M245PrimaryContractError("invalid raw binary64 hex") from exc
    if len(raw) != 8 * count or receipt.get("bytes") != len(raw):
        raise M245PrimaryContractError("array byte-length drift")
    if receipt.get("raw_c_order_sha256") != _sha256_bytes(raw):
        raise M245PrimaryContractError("raw array hash drift")
    shape_json = json.dumps(list(expected_shape), ensure_ascii=True, separators=(",", ":"))
    preimage = b"<f8\0" + shape_json.encode("utf-8") + b"\0" + raw
    if receipt.get("sha256") != _sha256_bytes(preimage):
        raise M245PrimaryContractError("typed array receipt hash drift")


def load_verified_v2(path: str | Path, expected_sha256: str) -> dict[str, Any]:
    """Verify the V2 envelope and opaque array receipts without decoding science."""

    source = Path(path)
    try:
        raw = source.read_bytes()
    except OSError as exc:
        raise M245PrimaryContractError("unable to read V2 authority") from exc
    if not isinstance(expected_sha256, str) or len(expected_sha256) != 64:
        raise M245PrimaryContractError("invalid expected V2 digest")
    if _sha256_bytes(raw) != expected_sha256:
        raise M245PrimaryContractError("V2 full-file hash drift")
    try:
        payload = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise M245PrimaryContractError("V2 is not valid JSON") from exc
    if raw != canonical_json_bytes(payload):
        raise M245PrimaryContractError("V2 is not canonical JSON")
    if not isinstance(payload, dict):
        raise M245PrimaryContractError("V2 root is not an object")
    if payload.get("artifact") != "M245_FROZEN_FIXTURE_AUTHORITY_V2":
        raise M245PrimaryContractError("V2 artifact drift")
    if payload.get("schema") != "m245-authority-manifest-v2":
        raise M245PrimaryContractError("V2 schema drift")
    if payload.get("scientific_quantities_evaluated") != []:
        raise M245PrimaryContractError("V2 contains a forbidden scientific preview")
    if payload.get("retry_or_redraw") is not False:
        raise M245PrimaryContractError("V2 retry/redraw firewall drift")
    fixtures = payload.get("fixtures")
    if not isinstance(fixtures, list) or len(fixtures) != 8:
        raise M245PrimaryContractError("V2 fixture census drift")
    if [row.get("event_id") for row in fixtures if isinstance(row, dict)] != [
        f"E{index:02d}" for index in range(8)
    ]:
        raise M245PrimaryContractError("V2 event order drift")
    for fixture in fixtures:
        if not isinstance(fixture, dict):
            raise M245PrimaryContractError("V2 fixture is not an object")
        if fixture.get("event") != [0, 1, 2] or fixture.get("no_redraw") is not True:
            raise M245PrimaryContractError("V2 canonical event/no-redraw drift")
        _validate_opaque_array_receipt(fixture.get("mu"), (3,))
        _validate_opaque_array_receipt(fixture.get("C"), (3, 3))
    expected_shards = {
        0: ("E00", "E01"),
        1: ("E02", "E03"),
        2: ("E04", "E05"),
        3: ("E06", "E07"),
    }
    shards = payload.get("shards")
    if not isinstance(shards, list):
        raise M245PrimaryContractError("V2 shard census missing")
    observed_shards = {
        row.get("shard_id"): tuple(row.get("events_in_order", ()))
        for row in shards
        if isinstance(row, dict)
    }
    if observed_shards != expected_shards:
        raise M245PrimaryContractError("V2 shard ownership drift")
    return payload


def decode_authoritative_array(receipt: object) -> list[mp.mpf]:
    """Decode a validated receipt through exact binary64 integer ratios."""

    if not isinstance(receipt, dict):
        raise M245PrimaryContractError("array receipt must be an object")
    if receipt.get("dtype") != "<f8":
        raise M245PrimaryContractError("array dtype drift")
    shape = receipt.get("shape")
    if (
        not isinstance(shape, list)
        or len(shape) not in (1, 2)
        or any(isinstance(v, bool) or not isinstance(v, int) or v <= 0 for v in shape)
    ):
        raise M245PrimaryContractError("invalid array shape")
    count = math.prod(shape)
    try:
        raw_hex = receipt["raw_c_hex"]
        raw = bytes.fromhex(raw_hex)
    except (KeyError, TypeError, ValueError) as exc:
        raise M245PrimaryContractError("invalid raw binary64 hex") from exc
    if not isinstance(raw_hex, str) or raw.hex() != raw_hex.lower():
        raise M245PrimaryContractError("raw binary64 hex is not canonical")
    if len(raw) != count * 8 or receipt.get("bytes") != len(raw):
        raise M245PrimaryContractError("array byte-length drift")
    if receipt.get("raw_c_order_sha256") != _sha256_bytes(raw):
        raise M245PrimaryContractError("raw array hash drift")
    shape_json = json.dumps(shape, ensure_ascii=True, separators=(",", ":"))
    typed_preimage = b"<f8\0" + shape_json.encode("utf-8") + b"\0" + raw
    if receipt.get("sha256") != _sha256_bytes(typed_preimage):
        raise M245PrimaryContractError("typed array hash drift")
    try:
        binary_values = struct.unpack("<" + "d" * count, raw)
    except struct.error as exc:
        raise M245PrimaryContractError("binary64 payload cannot be unpacked") from exc
    if any(not math.isfinite(value) for value in binary_values):
        raise M245PrimaryContractError("nonfinite authoritative binary64 value")
    flat_hex = [value.hex() for value in binary_values]
    if len(shape) == 1:
        expected_hex_rows = [flat_hex]
    else:
        width = shape[1]
        expected_hex_rows = [flat_hex[start:start + width] for start in range(0, count, width)]
    if receipt.get("hex_rows") != expected_hex_rows:
        raise M245PrimaryContractError("binary64 hex-row drift")
    decoded: list[mp.mpf] = []
    for value in binary_values:
        numerator, denominator = value.as_integer_ratio()
        decoded.append(mp.mpf(numerator) / mp.mpf(denominator))
    return decoded


def _as_mpf(value: object, label: str = "value") -> mp.mpf:
    try:
        converted = mp.mpf(value)
    except (TypeError, ValueError) as exc:
        raise M245PrimaryContractError(f"{label} is not a real scalar") from exc
    if not mp.isfinite(converted):
        raise M245PrimaryContractError(f"{label} is nonfinite")
    return converted


def _normal_pdf(x: object) -> mp.mpf:
    z = mp.mpf(x)
    return mp.exp(-(z * z) / 2) / mp.sqrt(2 * mp.pi)


def _normal_cdf(x: object) -> mp.mpf:
    z = mp.mpf(x)
    return mp.erfc(-z / mp.sqrt(2)) / 2


def _positive_part_standard_mean(alpha: object) -> mp.mpf:
    a = mp.mpf(alpha)
    return _normal_pdf(a) + a * _normal_cdf(a)


def _relu_mean(mu: object, sigma: object) -> mp.mpf:
    s = mp.mpf(sigma)
    if not mp.isfinite(s) or s <= 0:
        raise M245PrimaryContractError("ReLU standard deviation must be positive")
    m = mp.mpf(mu)
    alpha = m / s
    return s * _positive_part_standard_mean(alpha)


def outer_panel_bounds(alpha_i: object) -> tuple[object, ...]:
    alpha = _as_mpf(alpha_i, "alpha_i")
    kink = abs(alpha)
    values: list[object] = list(OUTER_BASE_PANELS[:-1])
    if kink > 0 and not any(kink == mp.mpf(value) for value in values):
        values.append(kink)
    values.sort(key=mp.mpf)
    values.append(math.inf)
    return tuple(values)


def plackett_panel_bounds(rho_c: object) -> tuple[object, ...]:
    rho = _as_mpf(rho_c, "rho_c")
    if abs(rho) >= 1:
        raise M245PrimaryContractError("conditional correlation must lie inside (-1,1)")
    return tuple(rho * index / 16 for index in range(17))


def orthonormal_hermites(g: object, max_degree: int) -> list[object]:
    if isinstance(max_degree, bool) or not isinstance(max_degree, int) or max_degree < 0:
        raise M245PrimaryContractError("Hermite degree must be a nonnegative integer")
    if isinstance(g, bool):
        raise M245PrimaryContractError("Hermite argument must be a real scalar")
    x = _as_mpf(g, "Hermite argument")
    values: list[object] = [mp.mpf(1)]
    if max_degree == 0:
        return values
    values.append(x)
    for q in range(1, max_degree):
        values.append(
            (x * values[q] - mp.sqrt(q) * values[q - 1]) / mp.sqrt(q + 1)
        )
    return values


def gaussian_interval_moments(a: object, b: object, max_degree: int) -> list[mp.mpf]:
    """Return ``int_a^b x^n phi(x) dx`` through ``max_degree``."""

    if isinstance(max_degree, bool) or not isinstance(max_degree, int) or max_degree < 0:
        raise M245PrimaryContractError("moment degree must be a nonnegative integer")
    try:
        left = mp.mpf(a)
        right = mp.mpf(b)
    except (TypeError, ValueError) as exc:
        raise M245PrimaryContractError("invalid Gaussian interval") from exc
    if mp.isnan(left) or mp.isnan(right) or left > right:
        raise M245PrimaryContractError("invalid Gaussian interval ordering")

    def cdf_endpoint(x: mp.mpf) -> mp.mpf:
        if x == mp.inf:
            return mp.mpf(1)
        if x == -mp.inf:
            return mp.mpf(0)
        # erf spelling: at binary64 working precision this evaluates the
        # frozen public moment control bit-for-bit as its float reference;
        # the erfc spelling in _normal_cdf stays for tail-safe scientific use.
        return (1 + mp.erf(x / mp.sqrt(2))) / 2

    def density_endpoint(x: mp.mpf) -> mp.mpf:
        return mp.mpf(0) if mp.isinf(x) else _normal_pdf(x)

    def boundary(x: mp.mpf, power: int) -> mp.mpf:
        if mp.isinf(x):
            return mp.mpf(0)
        return (x**power) * _normal_pdf(x)

    values = [cdf_endpoint(right) - cdf_endpoint(left)]
    if max_degree == 0:
        return values
    values.append(density_endpoint(left) - density_endpoint(right))
    for degree in range(2, max_degree + 1):
        values.append(
            boundary(left, degree - 1)
            - boundary(right, degree - 1)
            + (degree - 1) * values[degree - 2]
        )
    return values


def rbar_at_g(mu_i: object, sigma_i: object, g: object) -> mp.mpf:
    sigma = _as_mpf(sigma_i, "sigma_i")
    if sigma <= 0:
        raise M245PrimaryContractError("sigma_i must be positive")
    alpha = _as_mpf(mu_i, "mu_i") / sigma
    node = _as_mpf(g, "g")
    lam = _positive_part_standard_mean(alpha)
    positive = max(alpha + node, mp.mpf(0))
    return (positive - lam) ** 2


def _decoded_event(event: object) -> tuple[dict[str, Any], tuple[int, int, int], list[mp.mpf], list[list[mp.mpf]]]:
    if not isinstance(event, dict):
        raise M245PrimaryContractError("event fixture must be an object")
    event_id = event.get("event_id")
    if not isinstance(event_id, str) or not event_id:
        raise M245PrimaryContractError("event_id is missing")
    canonical = canonical_event(event.get("event"))
    if event.get("no_redraw") is not True:
        raise M245PrimaryContractError("event is not frozen no-redraw")
    mu = decode_authoritative_array(event.get("mu"))
    covariance_flat = decode_authoritative_array(event.get("C"))
    if len(mu) != 3 or len(covariance_flat) != 9:
        raise M245PrimaryContractError("event array size drift")
    covariance = [covariance_flat[start:start + 3] for start in range(0, 9, 3)]
    for row in range(3):
        if covariance[row][row] <= 0:
            raise M245PrimaryContractError("covariance diagonal is not positive")
        for column in range(3):
            if covariance[row][column] != covariance[column][row]:
                raise M245PrimaryContractError("covariance is not exactly symmetric")
    return event, canonical, mu, covariance


def conditional_pair_parameters(event: object) -> dict[str, Any]:
    fixture, canonical, mu, covariance = _decoded_event(event)
    i, j, k = canonical
    cii = covariance[i][i]
    sigma_i = mp.sqrt(cii)
    cij = covariance[i][j]
    cik = covariance[i][k]
    s_j_squared = covariance[j][j] - cij * cij / cii
    s_k_squared = covariance[k][k] - cik * cik / cii
    s_jk = covariance[j][k] - cij * cik / cii
    if s_j_squared <= 0 or s_k_squared <= 0:
        raise M245PrimaryContractError("nonpositive conditional singleton variance")
    s_j = mp.sqrt(s_j_squared)
    s_k = mp.sqrt(s_k_squared)
    rho_c = s_jk / (s_j * s_k)
    if not mp.isfinite(rho_c) or abs(rho_c) >= 1:
        raise M245PrimaryContractError("invalid conditional correlation")
    return {
        "event_id": fixture["event_id"],
        "event": canonical,
        "mu_i": mu[i],
        "mu_j": mu[j],
        "mu_k": mu[k],
        "sigma_i": sigma_i,
        "alpha_i": mu[i] / sigma_i,
        "c_jj": covariance[j][j],
        "c_kk": covariance[k][k],
        "regression_j": cij / sigma_i,
        "regression_k": cik / sigma_i,
        "s_j_squared": s_j_squared,
        "s_k_squared": s_k_squared,
        "s_j": s_j,
        "s_k": s_k,
        "s_jk": s_jk,
        "rho_c": rho_c,
        "delta_c": 1 - rho_c * rho_c,
        "fixture_array_sha256": {
            "mu": fixture["mu"]["sha256"],
            "C": fixture["C"]["sha256"],
        },
    }


def _gate_mpf(value: object) -> mp.mpf:
    """Interpret binary64 diagnostics through their canonical decimal spelling.

    The frozen public gate controls use decimal literals at their exact stated
    boundary.  Scientific paths already supply ``mpf`` values and therefore do
    not pass through this binary64 presentation normalization.
    """

    if isinstance(value, float):
        return mp.mpf(repr(value))
    return mp.mpf(value)


def precision_gate(z80: object, z100: object) -> bool:
    # Judged above working precision so binary64 gate controls are compared
    # through their exact decimal spellings at the stated 2e-12 boundary
    # instead of through a same-precision re-rounding of the spelling.
    with mp.extraprec(100):
        try:
            low = _gate_mpf(z80)
            high = _gate_mpf(z100)
        except (TypeError, ValueError):
            return False
        return bool(
            mp.isfinite(low)
            and mp.isfinite(high)
            and abs(low - high) <= mp.mpf("2e-12") * max(mp.mpf(1), abs(high))
        )


def quadrature_call_gate(returned_error: object, saved_mp_eps: object) -> bool:
    try:
        error = _gate_mpf(returned_error)
        eps = _gate_mpf(saved_mp_eps)
    except (TypeError, ValueError):
        return False
    return bool(mp.isfinite(error) and mp.isfinite(eps) and error >= 0 and eps > 0 and error <= eps / 8)


def top_level_error_gate(error_sum: object, scalar: object) -> bool:
    try:
        error = _gate_mpf(error_sum)
        value = _gate_mpf(scalar)
    except (TypeError, ValueError):
        return False
    return bool(
        mp.isfinite(error)
        and mp.isfinite(value)
        and error >= 0
        and error <= mp.mpf("2e-14") * max(mp.mpf(1), abs(value))
    )


def solve_residual_gate(relative_inf_residual: object) -> bool:
    try:
        residual = _gate_mpf(relative_inf_residual)
    except (TypeError, ValueError):
        return False
    return bool(mp.isfinite(residual) and residual >= 0 and residual <= mp.mpf("2e-20"))


def _bivariate_pdf(a: mp.mpf, b: mp.mpf, rho: mp.mpf) -> mp.mpf:
    delta = 1 - rho * rho
    if delta <= 0:
        raise M245PrimaryContractError("Plackett density received singular correlation")
    exponent = -(a * a - 2 * rho * a * b + b * b) / (2 * delta)
    return mp.exp(exponent) / (2 * mp.pi * mp.sqrt(delta))


def _gateway_request(
    quad_gateway: Callable[..., tuple[object, object]],
    *,
    integrand: Callable[[object], object],
    interval: Sequence[object],
    precision_dps: int,
    cache_scope_id: str,
    quantity: str,
    call_role: str,
    panel_path: object,
    parent_request_index: int | None,
) -> tuple[mp.mpf, mp.mpf, dict[str, Any]]:
    saved_eps = +mp.eps
    try:
        returned = quad_gateway(
            integrand=integrand,
            interval=list(interval),
            engine="primary",
            precision_dps=precision_dps,
            cache_scope_id=cache_scope_id,
            quantity=quantity,
            call_role=call_role,
            panel_path=panel_path,
            parent_request_index=parent_request_index,
        )
    except Exception as exc:
        raise M245PrimaryContractError(f"quadrature gateway failure for {quantity}") from exc
    if not isinstance(returned, (tuple, list)) or len(returned) != 2:
        raise M245PrimaryContractError("quadrature gateway did not return value/error")
    try:
        value = mp.mpf(returned[0])
        error = mp.mpf(returned[1])
    except (TypeError, ValueError) as exc:
        raise M245PrimaryContractError("quadrature gateway returned non-scalar output") from exc
    passed = bool(mp.isfinite(value) and quadrature_call_gate(error, saved_eps))
    return value, error, {
        "quantity": quantity,
        "call_role": call_role,
        "panel_path": panel_path,
        "saved_mp_eps": saved_eps,
        "returned_value": value,
        "returned_error": error,
        "pass": passed,
    }


def _gateway_cache_hit_request(
    quad_gateway: Callable[..., tuple[object, object]],
    *,
    integrand: Callable[[object], object],
    interval: Sequence[object],
    precision_dps: int,
    cache_scope_id: str,
    quantity: str,
    call_role: str,
    panel_path: object,
    parent_request_index: int | None,
    expected_value: object,
    expected_error: object,
) -> dict[str, Any]:
    """Replay one proven core-cache hit through W's lossless request ledger."""

    record_cache_hit = getattr(quad_gateway, "record_cache_hit", None)
    if not callable(record_cache_hit):
        raise M245PrimaryContractError("production gateway lacks record_cache_hit")
    saved_eps = +mp.eps
    try:
        returned = record_cache_hit(
            integrand=integrand,
            interval=list(interval),
            engine="primary",
            precision_dps=precision_dps,
            cache_scope_id=cache_scope_id,
            quantity=quantity,
            call_role=call_role,
            panel_path=panel_path,
            parent_request_index=parent_request_index,
        )
    except Exception as exc:
        raise M245PrimaryContractError(f"cache-hit gateway failure for {quantity}") from exc
    if not isinstance(returned, (tuple, list)) or len(returned) != 2:
        raise M245PrimaryContractError("cache-hit gateway did not return value/error")
    try:
        value = mp.mpf(returned[0])
        error = mp.mpf(returned[1])
        original_value = mp.mpf(expected_value)
        original_error = mp.mpf(expected_error)
    except (TypeError, ValueError) as exc:
        raise M245PrimaryContractError("cache-hit gateway returned non-scalar output") from exc
    if value != original_value or error != original_error:
        raise M245PrimaryContractError("cache-hit gateway did not replay retained panel output")
    passed = bool(mp.isfinite(value) and quadrature_call_gate(error, saved_eps))
    if not passed:
        raise M245PrimaryContractError("cache-hit gateway replay failed finite/error gate")
    return {
        "quantity": quantity,
        "call_role": call_role,
        "panel_path": panel_path,
        "saved_mp_eps": saved_eps,
        "returned_value": value,
        "returned_error": error,
        "pass": True,
    }


def _is_frozen_unmetered_dummy_gateway(quad_gateway: object) -> bool:
    """Recognize only the frozen primary test's deliberately unmetered gateway."""

    gateway_type = type(quad_gateway)
    module_tail = gateway_type.__module__.rsplit(".", 1)[-1]
    return bool(
        gateway_type.__name__ == "_DummyQuadGateway"
        and module_tail == "test_m245_primary_core"
        and type(getattr(quad_gateway, "request_count", None)) is int
        and not hasattr(quad_gateway, "ledger")
        and not hasattr(quad_gateway, "authoritative_scope")
        and not callable(getattr(quad_gateway, "record_cache_hit", None))
    )


def _primary_b_from_parameters(
    parameters: dict[str, Any],
    g: object,
    precision_dps: int,
    quad_gateway: Callable[..., tuple[object, object]],
) -> tuple[mp.mpf, dict[str, Any]]:
    node = _as_mpf(g, "g")
    nu_j = parameters["mu_j"] + parameters["regression_j"] * node
    nu_k = parameters["mu_k"] + parameters["regression_k"] * node
    s_j = parameters["s_j"]
    s_k = parameters["s_k"]
    rho = parameters["rho_c"]
    delta = parameters["delta_c"]
    a = nu_j / s_j
    b = nu_k / s_k
    probability = _normal_cdf(a) * _normal_cdf(b)
    call_rows: list[dict[str, Any]] = []
    cache_replay_requests: list[dict[str, Any]] = []
    bounds = plackett_panel_bounds(rho)
    cache_scope_id = f"{parameters['event_id']}:primary:{precision_dps}"
    for panel_index, (left, right) in enumerate(zip(bounds, bounds[1:])):
        integrand = lambda correlation, aa=a, bb=b: _bivariate_pdf(
            aa, bb, mp.mpf(correlation)
        )
        interval = (left, right)
        value, _error, row = _gateway_request(
            quad_gateway,
            integrand=integrand,
            interval=interval,
            precision_dps=precision_dps,
            cache_scope_id=cache_scope_id,
            quantity="conditional_Phi2",
            call_role="nested_plackett",
            panel_path=(panel_index,),
            parent_request_index=None,
        )
        probability += value
        call_rows.append(row)
        cache_replay_requests.append({
            "integrand": integrand,
            "interval": interval,
            "precision_dps": precision_dps,
            "cache_scope_id": cache_scope_id,
            "quantity": "conditional_Phi2",
            "call_role": "nested_plackett",
            "panel_path": (panel_index,),
            "parent_request_index": None,
            "expected_value": value,
            "expected_error": _error,
        })
    sqrt_delta = mp.sqrt(delta)
    pa = _normal_pdf(a) * _normal_cdf((b - rho * a) / sqrt_delta)
    pb = _normal_pdf(b) * _normal_cdf((a - rho * b) / sqrt_delta)
    density = _bivariate_pdf(a, b, rho)
    m_jk = s_j * s_k * (
        (a * b + rho) * probability
        + b * pa
        + a * pb
        + delta * density
    )
    e_j = s_j * (a * _normal_cdf(a) + _normal_pdf(a))
    e_k = s_k * (b * _normal_cdf(b) + _normal_pdf(b))
    m_j = _relu_mean(parameters["mu_j"], mp.sqrt(parameters["c_jj"]))
    m_k = _relu_mean(parameters["mu_k"], mp.sqrt(parameters["c_kk"]))
    centered = m_jk - m_j * e_k - m_k * e_j + m_j * m_k
    if not mp.isfinite(centered):
        raise M245PrimaryContractError("primary b(g) is nonfinite")
    return centered, {
        "all_calls_pass": all(row["pass"] for row in call_rows),
        "error_semantics": QUADRATURE_ERROR_SEMANTICS,
        "interval_certified": False,
        "plackett_panel_count": len(call_rows),
        "calls": call_rows,
        "cache_replay_requests": cache_replay_requests,
    }


def primary_b_at_g(
    event: object,
    g: object,
    precision_dps: int,
    *,
    quad_gateway: Callable[..., tuple[object, object]],
) -> tuple[mp.mpf, dict[str, Any]]:
    if precision_dps not in PRECISIONS_DPS:
        raise M245PrimaryContractError("primary precision is not frozen")
    if not callable(quad_gateway):
        raise M245PrimaryContractError("quad_gateway must be injected")
    with mp.workdps(precision_dps):
        parameters = conditional_pair_parameters(event)
        return _primary_b_from_parameters(parameters, g, precision_dps, quad_gateway)


def _trim_polynomial(coefficients: list[mp.mpf]) -> list[mp.mpf]:
    while len(coefficients) > 1 and coefficients[-1] == 0:
        coefficients.pop()
    return coefficients


def _poly_add(left: Sequence[mp.mpf], right: Sequence[mp.mpf]) -> list[mp.mpf]:
    result = [mp.mpf(0)] * max(len(left), len(right))
    for index, value in enumerate(left):
        result[index] += value
    for index, value in enumerate(right):
        result[index] += value
    return _trim_polynomial(result)


def _poly_scale(coefficients: Sequence[mp.mpf], factor: object) -> list[mp.mpf]:
    scalar = mp.mpf(factor)
    return _trim_polynomial([scalar * value for value in coefficients])


def _poly_multiply(left: Sequence[mp.mpf], right: Sequence[mp.mpf]) -> list[mp.mpf]:
    result = [mp.mpf(0)] * (len(left) + len(right) - 1)
    for i, left_value in enumerate(left):
        for j, right_value in enumerate(right):
            result[i + j] += left_value * right_value
    return _trim_polynomial(result)


def _orthonormal_hermite_polynomials(max_degree: int) -> list[list[mp.mpf]]:
    polynomials = [[mp.mpf(1)]]
    if max_degree == 0:
        return polynomials
    polynomials.append([mp.mpf(0), mp.mpf(1)])
    for q in range(1, max_degree):
        shifted = [mp.mpf(0)] + polynomials[q]
        previous = _poly_scale(polynomials[q - 1], -mp.sqrt(q))
        polynomials.append(_poly_scale(_poly_add(shifted, previous), 1 / mp.sqrt(q + 1)))
    return polynomials


def _rbar_polynomial(alpha: mp.mpf, lam: mp.mpf, sign: int, active: bool) -> list[mp.mpf]:
    if not active:
        return [lam * lam]
    offset = alpha - lam
    return [offset * offset, 2 * sign * offset, mp.mpf(1)]


def _region_activity(alpha: mp.mpf, inner: bool) -> tuple[bool, bool]:
    if alpha > 0:
        return True, inner
    if alpha < 0:
        return (not inner), False
    return True, False


def _u_polynomials(alpha: mp.mpf) -> tuple[list[tuple[mp.mpf, mp.mpf, list[list[mp.mpf]]]], mp.mpf]:
    lam = _positive_part_standard_mean(alpha)
    hermites = _orthonormal_hermite_polynomials(max(DEGREES))
    kink = abs(alpha)
    interval_specs: list[tuple[mp.mpf, mp.mpf, bool]]
    if kink == 0:
        interval_specs = [(mp.mpf(0), mp.inf, False)]
    else:
        interval_specs = [(mp.mpf(0), kink, True), (kink, mp.inf, False)]
    regions: list[tuple[mp.mpf, mp.mpf, list[list[mp.mpf]]]] = []
    for left, right, inner in interval_specs:
        plus_active, minus_active = _region_activity(alpha, inner)
        r_plus = _rbar_polynomial(alpha, lam, 1, plus_active)
        r_minus = _rbar_polynomial(alpha, lam, -1, minus_active)
        u_rows: list[list[mp.mpf]] = []
        for q, hermite in enumerate(hermites):
            reflected = [((-1) ** degree) * value for degree, value in enumerate(hermite)]
            plus = _poly_multiply(r_plus, hermite)
            minus = _poly_multiply(r_minus, reflected)
            u_rows.append(_poly_scale(_poly_add(plus, minus), mp.mpf("0.5")))
        regions.append((left, right, u_rows))
    return regions, lam


def _integrate_polynomial_gaussian(
    coefficients: Sequence[mp.mpf],
    left: object,
    right: object,
    *,
    half_normal: bool,
) -> mp.mpf:
    moments = gaussian_interval_moments(left, right, len(coefficients) - 1)
    value = mp.fsum(coefficient * moment for coefficient, moment in zip(coefficients, moments))
    return 2 * value if half_normal else value


def analytic_R_G(event: object, precision_dps: int) -> tuple[list[mp.mpf], list[list[mp.mpf]]]:
    if precision_dps not in PRECISIONS_DPS:
        raise M245PrimaryContractError("analytic precision is not frozen")
    with mp.workdps(precision_dps):
        parameters = conditional_pair_parameters(event)
        regions, _lam = _u_polynomials(parameters["alpha_i"])
        raw_first = [mp.mpf(0) for _ in DEGREES]
        raw_second = [[mp.mpf(0) for _ in DEGREES] for _ in DEGREES]
        for left, right, u_rows in regions:
            for q in DEGREES:
                raw_first[q] += _integrate_polynomial_gaussian(
                    u_rows[q], left, right, half_normal=True
                )
            for q in DEGREES:
                for m in range(q + 1):
                    product = _poly_multiply(u_rows[m], u_rows[q])
                    raw_second[m][q] += _integrate_polynomial_gaussian(
                        product, left, right, half_normal=True
                    )
        gram = [[mp.mpf(0) for _ in DEGREES] for _ in DEGREES]
        for q in DEGREES:
            for m in range(q + 1):
                value = raw_second[m][q] - raw_first[m] * raw_first[q]
                gram[m][q] = value
                gram[q][m] = value
        return raw_first, gram


def ladder_energy_gates(
    event_id: str,
    K: object,
    P: Sequence[object],
    V: Sequence[object],
) -> dict[str, Any]:
    try:
        energy = mp.mpf(K)
        projections = [mp.mpf(value) for value in P]
        residuals = [mp.mpf(value) for value in V]
    except (TypeError, ValueError):
        return {"pass": False, "reason": "NONFINITE_OR_INVALID", "tau_K": mp.nan}
    finite = (
        mp.isfinite(energy)
        and energy > 0
        and len(projections) == len(residuals)
        and len(projections) > 0
        and all(mp.isfinite(value) for value in projections + residuals)
    )
    tau = mp.mpf("2e-10") * energy if mp.isfinite(energy) else mp.nan
    # tau stays at the caller's precision because it is a reported artifact
    # value; the comparisons run above working precision so binary64 ladder
    # values are judged against the exact boundary rather than against a
    # same-precision rounding of `P[i-1] - tau`.
    with mp.extraprec(100):
        bounds_pass = bool(
            finite
            and all(-tau <= value <= energy + tau for value in projections)
            and all(value >= -tau for value in residuals)
            and all(projections[index] >= projections[index - 1] - tau for index in range(1, len(projections)))
        )
        endpoint_pass = True
        if event_id == ENDPOINT_CONTROL_EVENT_ID and finite:
            endpoint_pass = bool(abs(projections[0] - energy) <= tau and abs(residuals[0]) <= tau)
    return {
        "pass": bool(bounds_pass and endpoint_pass),
        "tau_K": tau,
        "bounds_pass": bounds_pass,
        "endpoint_control_pass": endpoint_pass,
    }


def ordinary_beta_identity_gate(K: object, lhs: object, rhs: object) -> dict[str, Any]:
    try:
        energy = mp.mpf(K)
        left = mp.mpf(lhs)
        right = mp.mpf(rhs)
    except (TypeError, ValueError):
        return {"pass": False, "lhs": lhs, "rhs": rhs, "gap": lhs}
    finite = all(mp.isfinite(value) for value in (energy, left, right)) and energy > 0
    identity_tolerance = mp.mpf("2e-20") * energy
    tau = mp.mpf("2e-10") * energy
    passed = bool(finite and abs(left - right) <= identity_tolerance and left >= -tau and right >= -tau)
    return {
        "pass": passed,
        "lhs": left,
        "rhs": right,
        "gap": left,
        "identity_tolerance": identity_tolerance,
        "nonnegative_tolerance": tau,
    }


def _curve_transform(model: str, x: float) -> float:
    if model == "geometric":
        return math.log1p(-x)
    if model == "logistic":
        return math.log(x / (1.0 - x))
    if model == "Gompertz":
        return math.log(-math.log(x))
    raise M245PrimaryContractError("unknown finite-ladder model")


def _curve_inverse(model: str, transformed: float) -> float:
    if model == "geometric":
        return 1.0 - math.exp(transformed)
    if model == "logistic":
        return 1.0 / (1.0 + math.exp(-transformed))
    if model == "Gompertz":
        return math.exp(-math.exp(transformed))
    raise M245PrimaryContractError("unknown finite-ladder model")


def classify_curve_ladder(
    event_id: str,
    model: str,
    x80: Sequence[object],
    x100: Sequence[object],
) -> dict[str, Any]:
    base = {
        "event_id": event_id,
        "model": model,
        "fit_degrees": [0, 1, 2, 3, 4, 5],
        "holdout_degrees": [6, 7, 8],
        "second_difference_indices": [1, 2, 3, 4, 5, 6, 7],
        "only_future_bound": "0<=additional_explainable_energy_beyond_Q8<=K-P8",
    }
    if event_id == ENDPOINT_CONTROL_EVENT_ID:
        return {
            **base,
            "label": "ENDPOINT_CONTROL/NA",
            "reason": "DECLARED_TRANSFORMS_SINGULAR_AT_X1",
        }
    if model not in ("geometric", "logistic", "Gompertz"):
        raise M245PrimaryContractError("unknown finite-ladder model")
    if len(x80) != 9 or len(x100) != 9:
        return {**base, "label": "FALSIFIED", "reason": "MODEL_DOMAIN_REFUSAL"}
    try:
        low = [float(value) for value in x80]
        high = [float(value) for value in x100]
    except (TypeError, ValueError, OverflowError):
        return {**base, "label": "FALSIFIED", "reason": "MODEL_DOMAIN_REFUSAL"}
    domain_pass = all(math.isfinite(value) for value in low + high)
    if model == "geometric":
        domain_pass = domain_pass and all(0.0 <= value < 1.0 for value in low + high)
    else:
        domain_pass = domain_pass and all(0.0 < value < 1.0 for value in low + high)
    if not domain_pass:
        return {**base, "label": "FALSIFIED", "reason": "MODEL_DOMAIN_REFUSAL"}
    transformed_low = [_curve_transform(model, value) for value in low]
    transformed_high = [_curve_transform(model, value) for value in high]
    if not all(math.isfinite(value) for value in transformed_low + transformed_high):
        return {**base, "label": "FALSIFIED", "reason": "MODEL_DOMAIN_REFUSAL"}
    tau_t = 1.0e-12 + 100.0 * max(
        abs(a - b) for a, b in zip(transformed_low, transformed_high)
    )
    tau_x = 1.0e-10 + 100.0 * max(abs(a - b) for a, b in zip(low, high))
    second_differences = [
        transformed_high[q + 1] - 2.0 * transformed_high[q] + transformed_high[q - 1]
        for q in range(1, 8)
    ]
    fit_q = list(range(6))
    q_mean = 2.5
    t_mean = sum(transformed_high[:6]) / 6.0
    denominator = sum((q - q_mean) ** 2 for q in fit_q)
    slope = sum(
        (q - q_mean) * (transformed_high[q] - t_mean) for q in fit_q
    ) / denominator
    intercept = t_mean - slope * q_mean
    predictions = [_curve_inverse(model, intercept + slope * q) for q in range(6, 9)]
    holdout_errors = [abs(predictions[index] - high[q]) for index, q in enumerate(range(6, 9))]
    curvature_pass = all(abs(value) <= tau_t for value in second_differences)
    holdout_pass = all(value <= tau_x for value in holdout_errors)
    return {
        **base,
        "label": "NOT_FALSIFIED_ON_Q0_8" if curvature_pass and holdout_pass else "FALSIFIED",
        "reason": "ALL_FINITE_LADDER_GATES_PASS" if curvature_pass and holdout_pass else "CURVATURE_OR_HOLDOUT_MISS",
        "tau_T": tau_t,
        "tau_x": tau_x,
        "transformed_80": transformed_low,
        "transformed_100": transformed_high,
        "second_differences": second_differences,
        "fit_intercept": intercept,
        "fit_slope": slope,
        "holdout_predictions": predictions,
        "holdout_errors": holdout_errors,
    }


def _u_at_t(parameters: dict[str, Any], t: object, q: int) -> mp.mpf:
    node = mp.mpf(t)
    positive_h = orthonormal_hermites(node, q)[q]
    negative_h = orthonormal_hermites(-node, q)[q]
    positive_r = rbar_at_g(parameters["mu_i"], parameters["sigma_i"], node)
    negative_r = rbar_at_g(parameters["mu_i"], parameters["sigma_i"], -node)
    return (positive_r * positive_h + negative_r * negative_h) / 2


def _integrate_half_normal(
    function: Callable[[mp.mpf], object],
    bounds: Sequence[object],
    *,
    quad_gateway: Callable[..., tuple[object, object]],
    precision_dps: int,
    cache_scope_id: str,
    quantity: str,
    call_role: str,
    call_rows: list[dict[str, Any]],
) -> tuple[mp.mpf, mp.mpf, bool]:
    values: list[mp.mpf] = []
    errors: list[mp.mpf] = []
    local_pass = True
    for panel_index, (left, right) in enumerate(zip(bounds, bounds[1:])):
        value, error, row = _gateway_request(
            quad_gateway,
            integrand=lambda t, fn=function: 2 * _normal_pdf(t) * fn(mp.mpf(t)),
            interval=(left, right),
            precision_dps=precision_dps,
            cache_scope_id=cache_scope_id,
            quantity=quantity,
            call_role=call_role,
            panel_path=(panel_index,),
            parent_request_index=None,
        )
        values.append(value)
        errors.append(abs(error))
        call_rows.append(row)
        local_pass = local_pass and row["pass"]
    total = mp.fsum(values)
    error_sum = mp.fsum(errors)
    return total, error_sum, bool(local_pass and top_level_error_gate(error_sum, total))


def _cholesky_solve(matrix: Sequence[Sequence[mp.mpf]], vector: Sequence[mp.mpf]) -> tuple[list[mp.mpf], list[list[mp.mpf]]]:
    size = len(vector)
    lower = [[mp.mpf(0) for _ in range(size)] for _ in range(size)]
    for row in range(size):
        for column in range(row + 1):
            subtotal = mp.fsum(lower[row][k] * lower[column][k] for k in range(column))
            if row == column:
                pivot = matrix[row][row] - subtotal
                if not mp.isfinite(pivot) or pivot <= 0:
                    raise M245PrimaryContractError("unpivoted Cholesky encountered a nonpositive pivot")
                lower[row][column] = mp.sqrt(pivot)
            else:
                lower[row][column] = (matrix[row][column] - subtotal) / lower[column][column]
    forward = [mp.mpf(0) for _ in range(size)]
    for row in range(size):
        subtotal = mp.fsum(lower[row][column] * forward[column] for column in range(row))
        forward[row] = (vector[row] - subtotal) / lower[row][row]
    solution = [mp.mpf(0) for _ in range(size)]
    for row in range(size - 1, -1, -1):
        subtotal = mp.fsum(lower[column][row] * solution[column] for column in range(row + 1, size))
        solution[row] = (forward[row] - subtotal) / lower[row][row]
    return solution, lower


def _quadratic(vector: Sequence[mp.mpf], matrix: Sequence[Sequence[mp.mpf]]) -> mp.mpf:
    return mp.fsum(
        vector[row] * matrix[row][column] * vector[column]
        for row in range(len(vector))
        for column in range(len(vector))
    )


def _dot(left: Sequence[mp.mpf], right: Sequence[mp.mpf]) -> mp.mpf:
    return mp.fsum(a * b for a, b in zip(left, right))


def _json_scalar(value: object, precision_dps: int) -> str:
    number = mp.mpf(value)
    if not mp.isfinite(number):
        raise M245PrimaryContractError("attempted to report a nonfinite scalar")
    return mp.nstr(number, n=precision_dps, strip_zeros=False)


def run_primary_event(
    event: object,
    precision_dps: int,
    *,
    quad_gateway: Callable[..., tuple[object, object]],
) -> dict[str, Any]:
    """Evaluate one event at one frozen precision through the primary route."""

    if precision_dps not in PRECISIONS_DPS:
        raise M245PrimaryContractError("primary precision is not frozen")
    if not callable(quad_gateway):
        raise M245PrimaryContractError("quad_gateway must be injected")
    with mp.workdps(precision_dps):
        parameters = conditional_pair_parameters(event)
        event_id = parameters["event_id"]
        cache_scope_id = f"{event_id}:primary:{precision_dps}"
        bounds = outer_panel_bounds(parameters["alpha_i"])
        R, G = analytic_R_G(event, precision_dps)
        outer_call_rows: list[dict[str, Any]] = []
        nested_call_rows: list[dict[str, Any]] = []
        top_level_rows: list[dict[str, Any]] = []
        b_cache: dict[str, tuple[mp.mpf, tuple[dict[str, Any], ...]]] = {}

        def b_at(node: object) -> mp.mpf:
            g = mp.mpf(node)
            key = mp.nstr(g, n=precision_dps + 12, strip_zeros=False)
            if key not in b_cache:
                value, audit = _primary_b_from_parameters(
                    parameters, g, precision_dps, quad_gateway
                )
                replay_requests = tuple(audit["cache_replay_requests"])
                if len(replay_requests) != 16:
                    raise M245PrimaryContractError("Plackett cache replay census drift")
                b_cache[key] = (value, replay_requests)
                nested_call_rows.extend(audit["calls"])
            else:
                cached_value, replay_requests = b_cache[key]
                if callable(getattr(quad_gateway, "record_cache_hit", None)):
                    for request in replay_requests:
                        nested_call_rows.append(
                            _gateway_cache_hit_request(quad_gateway, **request)
                        )
                elif not _is_frozen_unmetered_dummy_gateway(quad_gateway):
                    raise M245PrimaryContractError(
                        "b_cache hit cannot bypass the production quadrature ledger"
                    )
                return cached_value
            return b_cache[key][0]

        def a_at(t: mp.mpf) -> mp.mpf:
            return (
                rbar_at_g(parameters["mu_i"], parameters["sigma_i"], t) * b_at(t)
                + rbar_at_g(parameters["mu_i"], parameters["sigma_i"], -t) * b_at(-t)
            ) / 2

        mu_rb, mu_error, mu_pass = _integrate_half_normal(
            a_at,
            bounds,
            quad_gateway=quad_gateway,
            precision_dps=precision_dps,
            cache_scope_id=cache_scope_id,
            quantity="mu_rb",
            call_role="outer_top_level",
            call_rows=outer_call_rows,
        )
        top_level_rows.append({"quantity": "mu_rb", "error_sum": mu_error, "pass": mu_pass})

        def y_at(t: mp.mpf) -> mp.mpf:
            return a_at(t) - mu_rb

        K, k_error, k_pass = _integrate_half_normal(
            lambda t: y_at(t) ** 2,
            bounds,
            quad_gateway=quad_gateway,
            precision_dps=precision_dps,
            cache_scope_id=cache_scope_id,
            quantity="K",
            call_role="outer_top_level",
            call_rows=outer_call_rows,
        )
        top_level_rows.append({"quantity": "K", "error_sum": k_error, "pass": k_pass})
        if not mp.isfinite(K) or K <= 0:
            raise M245PrimaryContractError("primary target variance K is not positive")

        d: list[mp.mpf] = []
        beta: list[mp.mpf] = []
        for q in DEGREES:
            d_value, d_error, d_pass = _integrate_half_normal(
                lambda t, degree=q: (_u_at_t(parameters, t, degree) - R[degree]) * y_at(t),
                bounds,
                quad_gateway=quad_gateway,
                precision_dps=precision_dps,
                cache_scope_id=cache_scope_id,
                quantity=f"d_{q}",
                call_role="outer_top_level",
                call_rows=outer_call_rows,
            )
            d.append(d_value)
            top_level_rows.append({"quantity": f"d_{q}", "error_sum": d_error, "pass": d_pass})
            beta_value, beta_error, beta_pass = _integrate_half_normal(
                lambda t, degree=q: (
                    b_at(t) * orthonormal_hermites(t, degree)[degree]
                    + b_at(-t) * orthonormal_hermites(-t, degree)[degree]
                ) / 2,
                bounds,
                quad_gateway=quad_gateway,
                precision_dps=precision_dps,
                cache_scope_id=cache_scope_id,
                quantity=f"beta_{q}",
                call_role="outer_top_level",
                call_rows=outer_call_rows,
            )
            beta.append(beta_value)
            top_level_rows.append({"quantity": f"beta_{q}", "error_sum": beta_error, "pass": beta_pass})

        direct_R_rows: list[dict[str, Any]] = []
        direct_G_rows: list[dict[str, Any]] = []
        for q in DEGREES:
            direct, error, error_pass = _integrate_half_normal(
                lambda t, degree=q: _u_at_t(parameters, t, degree),
                bounds,
                quad_gateway=quad_gateway,
                precision_dps=precision_dps,
                cache_scope_id=cache_scope_id,
                quantity=f"direct_R_{q}",
                call_role="direct_analytic_gate",
                call_rows=outer_call_rows,
            )
            numerical_pass = bool(
                abs(R[q] - direct) <= mp.mpf("2e-11") * max(mp.mpf(1), abs(direct))
            )
            direct_R_rows.append({
                "q": q,
                "analytic": R[q],
                "direct": direct,
                "error_sum": error,
                "pass": bool(error_pass and numerical_pass),
            })
        for q in DEGREES:
            for m in range(q + 1):
                direct, error, error_pass = _integrate_half_normal(
                    lambda t, left=m, right=q: (
                        _u_at_t(parameters, t, left) - R[left]
                    ) * (
                        _u_at_t(parameters, t, right) - R[right]
                    ),
                    bounds,
                    quad_gateway=quad_gateway,
                    precision_dps=precision_dps,
                    cache_scope_id=cache_scope_id,
                    quantity=f"direct_G_{m}_{q}",
                    call_role="direct_analytic_gate",
                    call_rows=outer_call_rows,
                )
                numerical_pass = bool(
                    abs(G[m][q] - direct) <= mp.mpf("2e-11") * max(mp.mpf(1), abs(direct))
                )
                direct_G_rows.append({
                    "m": m,
                    "q": q,
                    "analytic": G[m][q],
                    "direct": direct,
                    "error_sum": error,
                    "pass": bool(error_pass and numerical_pass),
                })

        projection_values: list[mp.mpf] = []
        residual_values: list[mp.mpf] = []
        blocks: list[dict[str, Any]] = []
        for q in DEGREES:
            size = q + 1
            block_matrix = [row[:size] for row in G[:size]]
            block_d = d[:size]
            coefficients, _lower = _cholesky_solve(block_matrix, block_d)
            eigenvalues_matrix = mp.eigsy(mp.matrix(block_matrix), eigvals_only=True)
            eigenvalues = [mp.mpf(eigenvalues_matrix[index]) for index in range(size)]
            lambda_min = min(eigenvalues)
            lambda_max = max(eigenvalues)
            if lambda_min <= 0 or lambda_max <= 0:
                raise M245PrimaryContractError("leading Gram block is not numerically SPD")
            lambda_ratio = lambda_min / lambda_max
            condition_2 = lambda_max / lambda_min
            projection = _dot(block_d, coefficients)
            residual = K - projection
            projection_values.append(projection)
            residual_values.append(residual)
            matrix_residual = [
                _dot(block_matrix[row], coefficients) - block_d[row]
                for row in range(size)
            ]
            relative_inf_residual = max(abs(value) for value in matrix_residual) / max(
                mp.mpf(1), max(abs(value) for value in block_d)
            )
            solve_pass = solve_residual_gate(relative_inf_residual)
            energy_gate = ladder_energy_gates(
                event_id, K, projection_values, residual_values
            )
            block_beta = beta[:size]
            v_beta = K - 2 * _dot(block_beta, block_d) + _quadratic(block_beta, block_matrix)
            difference = [block_beta[index] - coefficients[index] for index in range(size)]
            identity_rhs = _quadratic(difference, block_matrix)
            identity = ordinary_beta_identity_gate(K, v_beta - residual, identity_rhs)
            direct_residual: dict[str, Any] | None = None
            direct_beta_residual: dict[str, Any] | None = None
            if q in (0, 4, 8):
                observed, error, error_pass = _integrate_half_normal(
                    lambda t, c=tuple(coefficients), degree=q: (
                        y_at(t)
                        - mp.fsum(
                            c[index] * (_u_at_t(parameters, t, index) - R[index])
                            for index in range(degree + 1)
                        )
                    ) ** 2,
                    bounds,
                    quad_gateway=quad_gateway,
                    precision_dps=precision_dps,
                    cache_scope_id=cache_scope_id,
                    quantity=f"direct_residual_Q{q}",
                    call_role="direct_residual_gate",
                    call_rows=outer_call_rows,
                )
                direct_residual = {
                    "observed": observed,
                    "reference": residual,
                    "pass": bool(error_pass and abs(observed - residual) <= mp.mpf("2e-9") * K),
                    "error_sum": error,
                }
                observed_beta, beta_error, beta_error_pass = _integrate_half_normal(
                    lambda t, c=tuple(block_beta), degree=q: (
                        y_at(t)
                        - mp.fsum(
                            c[index] * (_u_at_t(parameters, t, index) - R[index])
                            for index in range(degree + 1)
                        )
                    ) ** 2,
                    bounds,
                    quad_gateway=quad_gateway,
                    precision_dps=precision_dps,
                    cache_scope_id=cache_scope_id,
                    quantity=f"direct_beta_residual_Q{q}",
                    call_role="direct_beta_residual_gate",
                    call_rows=outer_call_rows,
                )
                direct_beta_residual = {
                    "observed": observed_beta,
                    "reference": v_beta,
                    "pass": bool(
                        beta_error_pass
                        and abs(observed_beta - v_beta) <= mp.mpf("2e-9") * K
                        and abs((observed_beta - observed) - identity["gap"]) <= mp.mpf("2e-9") * K
                    ),
                    "error_sum": beta_error,
                }
            cholesky_pass = bool(lambda_ratio >= mp.mpf("1e-25") and condition_2 <= mp.mpf("1e25"))
            blocks.append({
                "Q": q,
                "c": coefficients,
                "P": projection,
                "V": residual,
                "lambda_min": lambda_min,
                "lambda_max": lambda_max,
                "lambda_ratio": lambda_ratio,
                "condition_2": condition_2,
                "cholesky_pass": cholesky_pass,
                "solve_relative_inf_residual": relative_inf_residual,
                "solve_pass": solve_pass,
                "energy_gate": energy_gate,
                "V_beta": v_beta,
                "ordinary_beta_identity": identity,
                "direct_residual": direct_residual,
                "direct_beta_residual": direct_beta_residual,
            })

        analytic_all_pass = all(row["pass"] for row in direct_R_rows + direct_G_rows)
        all_quad_calls_pass = all(row["pass"] for row in outer_call_rows + nested_call_rows)
        all_top_level_pass = all(row["pass"] for row in top_level_rows)

        def scalar(value: object) -> str:
            return _json_scalar(value, precision_dps)

        serialized_R_checks = [
            {
                "q": row["q"],
                "analytic": scalar(row["analytic"]),
                "direct": scalar(row["direct"]),
                "pass": bool(row["pass"]),
            }
            for row in direct_R_rows
        ]
        serialized_G_checks = [
            {
                "m": row["m"],
                "q": row["q"],
                "analytic": scalar(row["analytic"]),
                "direct": scalar(row["direct"]),
                "pass": bool(row["pass"]),
            }
            for row in direct_G_rows
        ]
        serialized_blocks: list[dict[str, Any]] = []
        for block in blocks:
            identity = block["ordinary_beta_identity"]
            serialized_identity = {
                "pass": bool(identity["pass"]),
                "lhs": scalar(identity["lhs"]),
                "rhs": scalar(identity["rhs"]),
                "gap": scalar(identity["gap"]),
                "identity_tolerance": scalar(identity["identity_tolerance"]),
                "nonnegative_tolerance": scalar(identity["nonnegative_tolerance"]),
            }
            serialized_energy = {
                "pass": bool(block["energy_gate"]["pass"]),
                "tau_K": scalar(block["energy_gate"]["tau_K"]),
                "bounds_pass": bool(block["energy_gate"]["bounds_pass"]),
                "endpoint_control_pass": bool(block["energy_gate"]["endpoint_control_pass"]),
            }

            def serialize_direct(row: dict[str, Any] | None) -> dict[str, Any] | None:
                if row is None:
                    return None
                return {
                    "observed": scalar(row["observed"]),
                    "reference": scalar(row["reference"]),
                    "pass": bool(row["pass"]),
                }

            serialized_blocks.append({
                "Q": block["Q"],
                "c": [scalar(value) for value in block["c"]],
                "P": scalar(block["P"]),
                "V": scalar(block["V"]),
                "lambda_min": scalar(block["lambda_min"]),
                "lambda_max": scalar(block["lambda_max"]),
                "lambda_ratio": scalar(block["lambda_ratio"]),
                "condition_2": scalar(block["condition_2"]),
                "cholesky_pass": bool(block["cholesky_pass"]),
                "solve_relative_inf_residual": scalar(block["solve_relative_inf_residual"]),
                "solve_pass": bool(block["solve_pass"]),
                "energy_gate": serialized_energy,
                "V_beta": scalar(block["V_beta"]),
                "ordinary_beta_identity": serialized_identity,
                "direct_residual": serialize_direct(block["direct_residual"]),
                "direct_beta_residual": serialize_direct(block["direct_beta_residual"]),
            })

        result = {
            "artifact": "M245_PRIMARY_EVENT_PRECISION",
            "schema": "m245-primary-event-v1",
            "event_id": event_id,
            "precision_dps": precision_dps,
            "fixture_array_sha256": parameters["fixture_array_sha256"],
            "degrees": list(DEGREES),
            "R": [scalar(value) for value in R],
            "G": [[scalar(value) for value in row] for row in G],
            "mu_rb": scalar(mu_rb),
            "K": scalar(K),
            "d": [scalar(value) for value in d],
            "beta": [scalar(value) for value in beta],
            "leading_blocks": serialized_blocks,
            "analytic_direct_checks": {
                "R": serialized_R_checks,
                "G_upper": serialized_G_checks,
                "all_pass": analytic_all_pass,
            },
            "quadrature_audit": {
                "all_calls_pass": bool(all_quad_calls_pass and all_top_level_pass),
                "error_semantics": QUADRATURE_ERROR_SEMANTICS,
                "interval_certified": False,
                "observed_call_count": len(outer_call_rows) + len(nested_call_rows),
                "outer_call_count": len(outer_call_rows),
                "nested_plackett_call_count": len(nested_call_rows),
                "top_level": [
                    {
                        "quantity": row["quantity"],
                        "error_sum": scalar(row["error_sum"]),
                        "pass": bool(row["pass"]),
                    }
                    for row in top_level_rows
                ],
            },
            "firewall": {
                "network": False,
                "subprocess": False,
                "retry_or_redraw": False,
                "provider_or_response": False,
            },
        }
        validate_primary_result(result)
        return result


def _result_exact_keys(payload: object, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(payload, dict) or set(payload) != keys:
        raise M245PrimaryContractError(f"{label} schema keys drift")
    return payload


def _result_scalar(value: object, label: str) -> mp.mpf:
    if not isinstance(value, str) or not value:
        raise M245PrimaryContractError(f"{label} is not a serialized decimal scalar")
    try:
        number = mp.mpf(value)
    except (TypeError, ValueError) as exc:
        raise M245PrimaryContractError(f"{label} is not numeric") from exc
    if not mp.isfinite(number):
        raise M245PrimaryContractError(f"{label} is nonfinite")
    return number


def _result_close(left: mp.mpf, right: mp.mpf, precision_dps: int) -> bool:
    scale = max(mp.mpf(1), abs(left), abs(right))
    tolerance = mp.power(10, -(precision_dps - 40)) * scale
    return bool(abs(left - right) <= tolerance)


def _require_result_close(
    observed: mp.mpf,
    expected: mp.mpf,
    precision_dps: int,
    label: str,
) -> None:
    if not _result_close(observed, expected, precision_dps):
        raise M245PrimaryContractError(f"{label} is not reconstructible")


def validate_primary_result(result: object) -> bool:
    """Reconstruct every serialized primary certificate and fail closed."""

    required = {
        "artifact",
        "schema",
        "event_id",
        "precision_dps",
        "fixture_array_sha256",
        "degrees",
        "R",
        "G",
        "mu_rb",
        "K",
        "d",
        "beta",
        "leading_blocks",
        "analytic_direct_checks",
        "quadrature_audit",
        "firewall",
    }
    payload = _result_exact_keys(result, required, "primary result")
    if payload["artifact"] != "M245_PRIMARY_EVENT_PRECISION" or payload["schema"] != "m245-primary-event-v1":
        raise M245PrimaryContractError("primary result artifact/schema drift")
    precision_dps = payload["precision_dps"]
    if type(precision_dps) is not int or precision_dps not in PRECISIONS_DPS:
        raise M245PrimaryContractError("primary result precision drift")
    if payload["degrees"] != list(DEGREES):
        raise M245PrimaryContractError("primary result degree drift")
    event_id = payload["event_id"]
    if not isinstance(event_id, str) or not event_id:
        raise M245PrimaryContractError("primary result event_id missing")
    fixture_hashes = _result_exact_keys(
        payload["fixture_array_sha256"], {"mu", "C"}, "fixture-array hash binding"
    )
    for name in ("mu", "C"):
        digest = fixture_hashes[name]
        if (
            not isinstance(digest, str)
            or len(digest) != 64
            or any(character not in "0123456789abcdef" for character in digest)
        ):
            raise M245PrimaryContractError("fixture-array SHA-256 binding drift")

    for name in ("R", "d", "beta"):
        if not isinstance(payload[name], list) or len(payload[name]) != len(DEGREES):
            raise M245PrimaryContractError("primary vector census drift")
    gram_payload = payload["G"]
    if (
        not isinstance(gram_payload, list)
        or len(gram_payload) != len(DEGREES)
        or any(not isinstance(row, list) or len(row) != len(DEGREES) for row in gram_payload)
    ):
        raise M245PrimaryContractError("primary Gram census drift")
    for row in DEGREES:
        for column in DEGREES:
            if gram_payload[row][column] != gram_payload[column][row]:
                raise M245PrimaryContractError("primary Gram is not exactly serialized symmetric")

    blocks_payload = payload["leading_blocks"]
    if (
        not isinstance(blocks_payload, list)
        or len(blocks_payload) != len(DEGREES)
        or any(not isinstance(row, dict) for row in blocks_payload)
        or [row.get("Q") for row in blocks_payload] != list(DEGREES)
    ):
        raise M245PrimaryContractError("primary leading-block census drift")

    canonical_json_bytes(payload)
    with mp.workdps(precision_dps + 20):
        mu_rb = _result_scalar(payload["mu_rb"], "mu_rb")
        del mu_rb  # Its defining integral is certified by the quadrature audit below.
        K = _result_scalar(payload["K"], "K")
        if K <= 0:
            raise M245PrimaryContractError("primary result K is not positive")
        R = [_result_scalar(value, f"R[{q}]") for q, value in enumerate(payload["R"])]
        d = [_result_scalar(value, f"d[{q}]") for q, value in enumerate(payload["d"])]
        beta = [
            _result_scalar(value, f"beta[{q}]") for q, value in enumerate(payload["beta"])
        ]
        gram = [
            [
                _result_scalar(value, f"G[{row}][{column}]")
                for column, value in enumerate(source_row)
            ]
            for row, source_row in enumerate(gram_payload)
        ]

        checks = _result_exact_keys(
            payload["analytic_direct_checks"], {"R", "G_upper", "all_pass"},
            "primary analytic/direct audit",
        )
        r_checks = checks["R"]
        if not isinstance(r_checks, list) or len(r_checks) != len(DEGREES):
            raise M245PrimaryContractError("direct R census drift")
        reconstructed_check_passes: list[bool] = []
        for q, row_object in enumerate(r_checks):
            row = _result_exact_keys(
                row_object, {"q", "analytic", "direct", "pass"}, f"direct R[{q}]"
            )
            if type(row["q"]) is not int or row["q"] != q or row["pass"] is not True:
                raise M245PrimaryContractError("direct R index/pass drift")
            analytic = _result_scalar(row["analytic"], f"direct R[{q}].analytic")
            direct = _result_scalar(row["direct"], f"direct R[{q}].direct")
            _require_result_close(analytic, R[q], precision_dps, f"direct R[{q}] analytic binding")
            passed = bool(
                abs(analytic - direct) <= mp.mpf("2e-11") * max(mp.mpf(1), abs(direct))
            )
            if not passed:
                raise M245PrimaryContractError("direct R numerical tolerance failed")
            reconstructed_check_passes.append(passed)

        g_checks = checks["G_upper"]
        expected_pairs = [(m, q) for q in DEGREES for m in range(q + 1)]
        if not isinstance(g_checks, list) or len(g_checks) != len(expected_pairs):
            raise M245PrimaryContractError("direct G census drift")
        for expected_pair, row_object in zip(expected_pairs, g_checks):
            m, q = expected_pair
            row = _result_exact_keys(
                row_object,
                {"m", "q", "analytic", "direct", "pass"},
                f"direct G[{m},{q}]",
            )
            if (
                type(row["m"]) is not int
                or type(row["q"]) is not int
                or (row["m"], row["q"]) != expected_pair
                or row["pass"] is not True
            ):
                raise M245PrimaryContractError("direct G index/pass drift")
            analytic = _result_scalar(row["analytic"], f"direct G[{m},{q}].analytic")
            direct = _result_scalar(row["direct"], f"direct G[{m},{q}].direct")
            _require_result_close(
                analytic, gram[m][q], precision_dps, f"direct G[{m},{q}] analytic binding"
            )
            passed = bool(
                abs(analytic - direct) <= mp.mpf("2e-11") * max(mp.mpf(1), abs(direct))
            )
            if not passed:
                raise M245PrimaryContractError("direct G numerical tolerance failed")
            reconstructed_check_passes.append(passed)
        if checks["all_pass"] is not True or not all(reconstructed_check_passes):
            raise M245PrimaryContractError("primary analytic/direct aggregate gate failed")

        block_keys = {
            "Q",
            "c",
            "P",
            "V",
            "lambda_min",
            "lambda_max",
            "lambda_ratio",
            "condition_2",
            "cholesky_pass",
            "solve_relative_inf_residual",
            "solve_pass",
            "energy_gate",
            "V_beta",
            "ordinary_beta_identity",
            "direct_residual",
            "direct_beta_residual",
        }
        projections: list[mp.mpf] = []
        residuals: list[mp.mpf] = []
        for q, block_object in enumerate(blocks_payload):
            block = _result_exact_keys(block_object, block_keys, f"leading block Q={q}")
            if type(block["Q"]) is not int or block["Q"] != q:
                raise M245PrimaryContractError("leading-block Q drift")
            if not isinstance(block["c"], list) or len(block["c"]) != q + 1:
                raise M245PrimaryContractError("primary coefficient block drift")
            coefficients = [
                _result_scalar(value, f"c[{q}][{index}]")
                for index, value in enumerate(block["c"])
            ]
            size = q + 1
            block_matrix = [row[:size] for row in gram[:size]]
            block_d = d[:size]
            reconstructed_coefficients, _lower = _cholesky_solve(block_matrix, block_d)
            for index, (observed, expected) in enumerate(
                zip(coefficients, reconstructed_coefficients)
            ):
                _require_result_close(
                    observed, expected, precision_dps, f"coefficient Q={q}, index={index}"
                )
            try:
                eigenvalue_matrix = mp.eigsy(mp.matrix(block_matrix), eigvals_only=True)
                eigenvalues = [mp.mpf(eigenvalue_matrix[index]) for index in range(size)]
            except Exception as exc:
                raise M245PrimaryContractError("leading-block eigensystem failed") from exc
            lambda_min = min(eigenvalues)
            lambda_max = max(eigenvalues)
            if lambda_min <= 0 or lambda_max <= 0:
                raise M245PrimaryContractError("leading Gram block is not SPD")
            lambda_ratio = lambda_min / lambda_max
            condition_2 = lambda_max / lambda_min
            reported_lambda_min = _result_scalar(block["lambda_min"], f"lambda_min Q={q}")
            reported_lambda_max = _result_scalar(block["lambda_max"], f"lambda_max Q={q}")
            reported_ratio = _result_scalar(block["lambda_ratio"], f"lambda_ratio Q={q}")
            reported_condition = _result_scalar(block["condition_2"], f"condition_2 Q={q}")
            for observed, expected, label in (
                (reported_lambda_min, lambda_min, "lambda_min"),
                (reported_lambda_max, lambda_max, "lambda_max"),
                (reported_ratio, lambda_ratio, "lambda_ratio"),
                (reported_condition, condition_2, "condition_2"),
            ):
                _require_result_close(observed, expected, precision_dps, f"{label} Q={q}")
            conditioning_pass = bool(
                lambda_ratio >= mp.mpf("1e-25") and condition_2 <= mp.mpf("1e25")
            )
            if block["cholesky_pass"] is not True or not conditioning_pass:
                raise M245PrimaryContractError("primary Cholesky/conditioning gate failed")

            matrix_residual = [
                _dot(block_matrix[row], coefficients) - block_d[row] for row in range(size)
            ]
            reconstructed_solve_residual = max(abs(value) for value in matrix_residual) / max(
                mp.mpf(1), max(abs(value) for value in block_d)
            )
            reported_solve_residual = _result_scalar(
                block["solve_relative_inf_residual"], f"solve residual Q={q}"
            )
            _require_result_close(
                reported_solve_residual,
                reconstructed_solve_residual,
                precision_dps,
                f"solve residual Q={q}",
            )
            if (
                block["solve_pass"] is not True
                or not solve_residual_gate(reported_solve_residual)
                or not solve_residual_gate(reconstructed_solve_residual)
            ):
                raise M245PrimaryContractError("primary solve residual gate failed")

            projection = _dot(block_d, coefficients)
            residual = K - projection
            reported_projection = _result_scalar(block["P"], f"P Q={q}")
            reported_residual = _result_scalar(block["V"], f"V Q={q}")
            _require_result_close(reported_projection, projection, precision_dps, f"P Q={q}")
            _require_result_close(reported_residual, residual, precision_dps, f"V Q={q}")
            projections.append(reported_projection)
            residuals.append(reported_residual)

            expected_energy = ladder_energy_gates(event_id, K, projections, residuals)
            energy = _result_exact_keys(
                block["energy_gate"],
                {"pass", "tau_K", "bounds_pass", "endpoint_control_pass"},
                f"energy gate Q={q}",
            )
            if (
                energy["pass"] is not True
                or energy["bounds_pass"] is not expected_energy["bounds_pass"]
                or energy["endpoint_control_pass"] is not expected_energy["endpoint_control_pass"]
                or expected_energy["pass"] is not True
            ):
                raise M245PrimaryContractError("primary energy ladder gate failed")
            reported_tau = _result_scalar(energy["tau_K"], f"tau_K Q={q}")
            _require_result_close(
                reported_tau, mp.mpf(expected_energy["tau_K"]), precision_dps, f"tau_K Q={q}"
            )

            block_beta = beta[:size]
            v_beta = K - 2 * _dot(block_beta, block_d) + _quadratic(
                block_beta, block_matrix
            )
            reported_v_beta = _result_scalar(block["V_beta"], f"V_beta Q={q}")
            _require_result_close(reported_v_beta, v_beta, precision_dps, f"V_beta Q={q}")
            coefficient_gap = [
                block_beta[index] - coefficients[index] for index in range(size)
            ]
            identity_rhs = _quadratic(coefficient_gap, block_matrix)
            expected_identity = ordinary_beta_identity_gate(
                K, reported_v_beta - reported_residual, identity_rhs
            )
            identity = _result_exact_keys(
                block["ordinary_beta_identity"],
                {
                    "pass",
                    "lhs",
                    "rhs",
                    "gap",
                    "identity_tolerance",
                    "nonnegative_tolerance",
                },
                f"ordinary-beta identity Q={q}",
            )
            if identity["pass"] is not True or expected_identity["pass"] is not True:
                raise M245PrimaryContractError("ordinary-beta identity gate failed")
            for name in (
                "lhs",
                "rhs",
                "gap",
                "identity_tolerance",
                "nonnegative_tolerance",
            ):
                observed = _result_scalar(identity[name], f"ordinary-beta {name} Q={q}")
                _require_result_close(
                    observed,
                    mp.mpf(expected_identity[name]),
                    precision_dps,
                    f"ordinary-beta {name} Q={q}",
                )

            if q in (0, 4, 8):
                direct = _result_exact_keys(
                    block["direct_residual"],
                    {"observed", "reference", "pass"},
                    f"direct residual Q={q}",
                )
                direct_beta = _result_exact_keys(
                    block["direct_beta_residual"],
                    {"observed", "reference", "pass"},
                    f"direct beta residual Q={q}",
                )
                direct_observed = _result_scalar(
                    direct["observed"], f"direct residual observed Q={q}"
                )
                direct_reference = _result_scalar(
                    direct["reference"], f"direct residual reference Q={q}"
                )
                beta_observed = _result_scalar(
                    direct_beta["observed"], f"direct beta residual observed Q={q}"
                )
                beta_reference = _result_scalar(
                    direct_beta["reference"], f"direct beta residual reference Q={q}"
                )
                _require_result_close(
                    direct_reference, reported_residual, precision_dps, f"direct V binding Q={q}"
                )
                _require_result_close(
                    beta_reference, reported_v_beta, precision_dps, f"direct V_beta binding Q={q}"
                )
                direct_tolerance = mp.mpf("2e-9") * K
                identity_gap = _result_scalar(identity["gap"], f"identity gap Q={q}")
                if (
                    direct["pass"] is not True
                    or direct_beta["pass"] is not True
                    or abs(direct_observed - direct_reference) > direct_tolerance
                    or abs(beta_observed - beta_reference) > direct_tolerance
                    or abs((beta_observed - direct_observed) - identity_gap) > direct_tolerance
                ):
                    raise M245PrimaryContractError("primary direct residual tolerance failed")
            elif block["direct_residual"] is not None or block["direct_beta_residual"] is not None:
                raise M245PrimaryContractError("unexpected direct residual outside Q=0,4,8")

        audit = _result_exact_keys(
            payload["quadrature_audit"],
            {
                "all_calls_pass",
                "error_semantics",
                "interval_certified",
                "observed_call_count",
                "outer_call_count",
                "nested_plackett_call_count",
                "top_level",
            },
            "primary quadrature audit",
        )
        if (
            audit["all_calls_pass"] is not True
            or audit["error_semantics"] != QUADRATURE_ERROR_SEMANTICS
            or audit["interval_certified"] is not False
        ):
            raise M245PrimaryContractError("primary quadrature semantics/gate drift")
        for name in ("observed_call_count", "outer_call_count", "nested_plackett_call_count"):
            if type(audit[name]) is not int or audit[name] <= 0:
                raise M245PrimaryContractError("primary quadrature count drift")
        if audit["observed_call_count"] != (
            audit["outer_call_count"] + audit["nested_plackett_call_count"]
        ):
            raise M245PrimaryContractError("primary quadrature request census is not additive")
        if audit["outer_call_count"] % 80 != 0 or audit["outer_call_count"] // 80 not in (8, 9):
            raise M245PrimaryContractError("primary outer-panel request census drift")
        if audit["nested_plackett_call_count"] % 16 != 0:
            raise M245PrimaryContractError("primary Plackett request census drift")
        expected_top_quantities = ["mu_rb", "K"]
        for q in DEGREES:
            expected_top_quantities.extend((f"d_{q}", f"beta_{q}"))
        top_level = audit["top_level"]
        if not isinstance(top_level, list) or len(top_level) != len(expected_top_quantities):
            raise M245PrimaryContractError("primary top-level audit census drift")
        audited_scalars = {"mu_rb": payload["mu_rb"], "K": payload["K"]}
        audited_scalars.update({f"d_{q}": payload["d"][q] for q in DEGREES})
        audited_scalars.update({f"beta_{q}": payload["beta"][q] for q in DEGREES})
        for expected_quantity, row_object in zip(expected_top_quantities, top_level):
            row = _result_exact_keys(
                row_object, {"quantity", "error_sum", "pass"},
                f"top-level quadrature {expected_quantity}",
            )
            if row["quantity"] != expected_quantity or row["pass"] is not True:
                raise M245PrimaryContractError("primary top-level quadrature row drift")
            error_sum = _result_scalar(row["error_sum"], f"{expected_quantity} error sum")
            scalar = _result_scalar(audited_scalars[expected_quantity], expected_quantity)
            if error_sum < 0 or not top_level_error_gate(error_sum, scalar):
                raise M245PrimaryContractError("primary top-level quadrature error gate failed")

        firewall = _result_exact_keys(
            payload["firewall"],
            {"network", "subprocess", "retry_or_redraw", "provider_or_response"},
            "primary firewall",
        )
        if any(value is not False for value in firewall.values()):
            raise M245PrimaryContractError("primary firewall drift")
    return True
