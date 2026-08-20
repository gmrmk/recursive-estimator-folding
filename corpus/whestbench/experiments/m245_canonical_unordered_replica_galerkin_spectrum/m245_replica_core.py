"""Independent unary-factor replica core for the frozen M245 diagnostic.

The module owns no files, processes, or network surface.  It deliberately
does not import the primary core and never invokes quadrature itself.  Every
integration request is sent through the worker-owned ``quad_gateway`` that is
injected by the caller.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import struct
from typing import Any, Callable, Mapping, Sequence

import mpmath as mp


class M245ReplicaContractError(ValueError):
    """Raised when frozen replica authority or numerical policy is violated."""


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
INNER_BASE_PANELS = (0.0, 0.25, 1.0, 2.5, 5.0, 8.0, 10.0, 16.0, math.inf)
QUADRATURE_ERROR_SEMANTICS = "heuristic_diagnostic_estimate_not_interval_certificate"
DIAGNOSTIC_DISPOSITION = "NO_ESTIMATOR_PROVIDER_DEPLOYMENT_SCORE_OR_SUBMISSION_CREDIT"

_ARRAY_KEYS = {
    "bytes",
    "dtype",
    "hash_preimage",
    "hex_rows",
    "raw_c_hex",
    "raw_c_order_sha256",
    "repr_rows",
    "sha256",
    "shape",
}
_RESULT_KEYS = {
    "artifact",
    "schema",
    "event_id",
    "precision_dps",
    "fixture_array_sha256",
    "fixed_b_nodes",
    "b_rep_at_nodes",
    "mu_rep",
    "M_same",
    "M_cross",
    "K_rep",
    "quadrature_audit",
    "firewall",
}
_QUADRATURE_AUDIT_KEYS = {
    "all_calls_pass",
    "cache_scope_id",
    "error_semantics",
    "interval_certified",
    "nested_raw_error_sum_diagnostic",
    "observed_call_count",
    "outer_top_level_error_sums",
    "unary_panel_count",
}
_TOP_LEVEL_QUANTITIES = ("mu_rep", "M_same", "M_cross")
_FIREWALL_KEYS = {"network", "primary_import"}


def canonical_json_bytes(payload: object) -> bytes:
    """Return the sole canonical JSON encoding used by the M245 receipts."""

    try:
        text = json.dumps(
            payload,
            allow_nan=False,
            ensure_ascii=True,
            indent=2,
            sort_keys=True,
        )
    except (TypeError, ValueError) as exc:
        raise M245ReplicaContractError("payload is not canonical-JSON serializable") from exc
    return (text + "\n").encode("utf-8")


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _require_hex_digest(value: object, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise M245ReplicaContractError(f"{label} must be a lowercase SHA-256")
    if value != value.lower() or any(character not in "0123456789abcdef" for character in value):
        raise M245ReplicaContractError(f"{label} must be a lowercase SHA-256")
    return value


def _opaque_array_receipt(receipt: object, expected_shape: tuple[int, ...]) -> None:
    """Verify a V2 array envelope without decoding any binary64 element."""

    if not isinstance(receipt, dict) or set(receipt) != _ARRAY_KEYS:
        raise M245ReplicaContractError("array receipt schema mismatch")
    if receipt.get("dtype") != "<f8" or tuple(receipt.get("shape", ())) != expected_shape:
        raise M245ReplicaContractError("array dtype or shape mismatch")
    if receipt.get("hash_preimage") != "dtype_utf8_NUL_canonical_shape_json_NUL_C_order_bytes":
        raise M245ReplicaContractError("array hash-preimage policy mismatch")
    expected_count = math.prod(expected_shape)
    expected_bytes = expected_count * 8
    if receipt.get("bytes") != expected_bytes:
        raise M245ReplicaContractError("array byte length mismatch")
    raw_hex = receipt.get("raw_c_hex")
    if not isinstance(raw_hex, str):
        raise M245ReplicaContractError("array raw hex is missing")
    try:
        raw = bytes.fromhex(raw_hex)
    except ValueError as exc:
        raise M245ReplicaContractError("array raw hex is malformed") from exc
    if len(raw) != expected_bytes:
        raise M245ReplicaContractError("array raw byte count mismatch")
    if _sha256(raw) != _require_hex_digest(receipt.get("raw_c_order_sha256"), "raw array hash"):
        raise M245ReplicaContractError("array raw hash mismatch")
    shape_json = json.dumps(list(expected_shape), ensure_ascii=True, separators=(",", ":"))
    preimage = b"<f8\0" + shape_json.encode("utf-8") + b"\0" + raw
    if _sha256(preimage) != _require_hex_digest(receipt.get("sha256"), "array receipt hash"):
        raise M245ReplicaContractError("array receipt hash mismatch")
    expected_rows = 1 if len(expected_shape) == 1 else expected_shape[0]
    expected_columns = expected_shape[0] if len(expected_shape) == 1 else expected_shape[1]
    for field in ("hex_rows", "repr_rows"):
        rows = receipt.get(field)
        if not isinstance(rows, list) or len(rows) != expected_rows:
            raise M245ReplicaContractError(f"{field} row census mismatch")
        if any(not isinstance(row, list) or len(row) != expected_columns for row in rows):
            raise M245ReplicaContractError(f"{field} column census mismatch")
        if any(not isinstance(value, str) for row in rows for value in row):
            raise M245ReplicaContractError(f"{field} must contain strings")


def load_verified_v2(path: str | Path, expected_sha256: str) -> dict:
    """Verify and parse only the non-scientific V2 authority envelope."""

    expected = _require_hex_digest(expected_sha256, "expected V2 hash")
    candidate = Path(path)
    try:
        if candidate.is_symlink() or not candidate.is_file():
            raise M245ReplicaContractError("V2 must be a regular non-symlink file")
        raw = candidate.read_bytes()
    except OSError as exc:
        raise M245ReplicaContractError("unable to read V2 authority") from exc
    if _sha256(raw) != expected:
        raise M245ReplicaContractError("V2 full-file hash mismatch")
    try:
        payload = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise M245ReplicaContractError("V2 is not canonical UTF-8 JSON") from exc
    if not isinstance(payload, dict) or raw != canonical_json_bytes(payload):
        raise M245ReplicaContractError("V2 canonical bytes mismatch")
    if payload.get("artifact") != "M245_FROZEN_FIXTURE_AUTHORITY_V2":
        raise M245ReplicaContractError("V2 artifact mismatch")
    if payload.get("schema") != "m245-authority-manifest-v2":
        raise M245ReplicaContractError("V2 schema mismatch")
    if payload.get("scientific_quantities_evaluated") != []:
        raise M245ReplicaContractError("V2 contains scientific preview data")
    if payload.get("retry_or_redraw") is not False:
        raise M245ReplicaContractError("V2 retry/redraw policy mismatch")
    fixtures = payload.get("fixtures")
    if not isinstance(fixtures, list) or len(fixtures) != 8:
        raise M245ReplicaContractError("V2 fixture census mismatch")
    for index, fixture in enumerate(fixtures):
        if not isinstance(fixture, dict):
            raise M245ReplicaContractError("V2 fixture entry is malformed")
        if fixture.get("event_id") != f"E{index:02d}":
            raise M245ReplicaContractError("V2 fixture order mismatch")
        if fixture.get("event") != [0, 1, 2] or fixture.get("no_redraw") is not True:
            raise M245ReplicaContractError("V2 canonical event policy mismatch")
        _opaque_array_receipt(fixture.get("mu"), (3,))
        _opaque_array_receipt(fixture.get("C"), (3, 3))
    expected_shards = {
        0: ("E00", "E01"),
        1: ("E02", "E03"),
        2: ("E04", "E05"),
        3: ("E06", "E07"),
    }
    shards = payload.get("shards")
    if not isinstance(shards, list) or len(shards) != 4:
        raise M245ReplicaContractError("V2 shard census mismatch")
    observed_shards: dict[int, tuple[str, ...]] = {}
    for shard in shards:
        if not isinstance(shard, dict) or shard.get("owner") != "fable":
            raise M245ReplicaContractError("V2 shard entry mismatch")
        shard_id = shard.get("shard_id")
        if isinstance(shard_id, bool) or not isinstance(shard_id, int):
            raise M245ReplicaContractError("V2 shard id mismatch")
        events = shard.get("events_in_order")
        if not isinstance(events, list):
            raise M245ReplicaContractError("V2 shard assignment mismatch")
        observed_shards[shard_id] = tuple(events)
    if observed_shards != expected_shards:
        raise M245ReplicaContractError("V2 shard assignment mismatch")
    return payload


def decode_authoritative_array(receipt: Mapping[str, object]) -> tuple[mp.mpf, ...]:
    """Decode a verified dummy binary64 receipt through exact integer ratios."""

    if not isinstance(receipt, dict) or set(receipt) != _ARRAY_KEYS:
        raise M245ReplicaContractError("array receipt schema mismatch")
    if receipt.get("dtype") != "<f8":
        raise M245ReplicaContractError("only little-endian binary64 is allowed")
    shape_value = receipt.get("shape")
    if (
        not isinstance(shape_value, list)
        or len(shape_value) not in (1, 2)
        or any(isinstance(value, bool) or not isinstance(value, int) or value <= 0 for value in shape_value)
    ):
        raise M245ReplicaContractError("array shape is invalid")
    shape = tuple(shape_value)
    expected_count = math.prod(shape)
    expected_bytes = expected_count * 8
    if receipt.get("bytes") != expected_bytes:
        raise M245ReplicaContractError("array byte length mismatch")
    if receipt.get("hash_preimage") != "dtype_utf8_NUL_canonical_shape_json_NUL_C_order_bytes":
        raise M245ReplicaContractError("array hash-preimage policy mismatch")
    raw_hex = receipt.get("raw_c_hex")
    if not isinstance(raw_hex, str):
        raise M245ReplicaContractError("array raw hex is missing")
    try:
        raw = bytes.fromhex(raw_hex)
    except ValueError as exc:
        raise M245ReplicaContractError("array raw hex is malformed") from exc
    if len(raw) != expected_bytes:
        raise M245ReplicaContractError("array raw byte count mismatch")
    if _sha256(raw) != _require_hex_digest(receipt.get("raw_c_order_sha256"), "raw array hash"):
        raise M245ReplicaContractError("array raw hash mismatch")
    shape_json = json.dumps(list(shape), ensure_ascii=True, separators=(",", ":"))
    preimage = b"<f8\0" + shape_json.encode("utf-8") + b"\0" + raw
    if _sha256(preimage) != _require_hex_digest(receipt.get("sha256"), "array receipt hash"):
        raise M245ReplicaContractError("array receipt hash mismatch")
    expected_rows = 1 if len(shape) == 1 else shape[0]
    expected_columns = shape[0] if len(shape) == 1 else shape[1]
    hex_rows = receipt.get("hex_rows")
    if not isinstance(hex_rows, list) or len(hex_rows) != expected_rows:
        raise M245ReplicaContractError("array hex-row census mismatch")
    if any(not isinstance(row, list) or len(row) != expected_columns for row in hex_rows):
        raise M245ReplicaContractError("array hex-column census mismatch")
    flat_hex = [value for row in hex_rows for value in row]
    if any(not isinstance(value, str) for value in flat_hex):
        raise M245ReplicaContractError("array hex values must be strings")
    try:
        values = struct.unpack("<" + "d" * expected_count, raw)
    except struct.error as exc:
        raise M245ReplicaContractError("array binary64 bytes are malformed") from exc
    if any(not math.isfinite(value) for value in values):
        raise M245ReplicaContractError("array contains a nonfinite binary64")
    if [float(value).hex() for value in values] != flat_hex:
        raise M245ReplicaContractError("array authoritative hex rows mismatch")
    decoded: list[mp.mpf] = []
    for value in values:
        numerator, denominator = value.as_integer_ratio()
        decoded.append(mp.mpf(numerator) / mp.mpf(denominator))
    return tuple(decoded)


def canonical_event(event: Sequence[object]) -> tuple[int, int, int]:
    """Canonicalize ``(i,j,k)`` by sorting only the unordered pair ``j,k``."""

    if isinstance(event, (str, bytes)) or not isinstance(event, Sequence) or len(event) != 3:
        raise M245ReplicaContractError("event must contain exactly three indices")
    values = tuple(event)
    if any(isinstance(value, bool) or not isinstance(value, int) for value in values):
        raise M245ReplicaContractError("event indices must be integral and non-boolean")
    if any(value < 0 or value >= 3 for value in values):
        raise M245ReplicaContractError("event indices are outside dimension three")
    if len(set(values)) != 3:
        raise M245ReplicaContractError("event indices must be pairwise distinct")
    i, j, k = values
    return (i, min(j, k), max(j, k))


def inner_panel_bounds() -> tuple[float, ...]:
    """Return the frozen unary half-normal panel boundaries."""

    return INNER_BASE_PANELS


def _as_mpf(value: object, label: str) -> mp.mpf:
    if isinstance(value, bool):
        raise M245ReplicaContractError(f"{label} must be a finite scalar")
    try:
        result = mp.mpf(value)
    except (TypeError, ValueError) as exc:
        raise M245ReplicaContractError(f"{label} must be a finite scalar") from exc
    if not mp.isfinite(result):
        raise M245ReplicaContractError(f"{label} must be finite")
    return result


def _phi(value: mp.mpf) -> mp.mpf:
    return mp.exp(-(value * value) / 2) / mp.sqrt(2 * mp.pi)


def _Phi(value: mp.mpf) -> mp.mpf:
    return mp.erfc(-value / mp.sqrt(2)) / 2


def unary_relu_mean(nu: object, sigma: object) -> mp.mpf:
    """Return ``E[max(0, nu + sigma Z)]`` for standard-normal ``Z``."""

    mean = _as_mpf(nu, "unary mean")
    scale = _as_mpf(sigma, "unary scale")
    if scale <= 0:
        raise M245ReplicaContractError("unary scale must be strictly positive")
    alpha = mean / scale
    return scale * (alpha * _Phi(alpha) + _phi(alpha))


def replica_rbar_at_g(mu_i: object, sigma_i: object, g: object) -> mp.mpf:
    """Independently rebuild the scale-normalized repeated-coordinate window."""

    mean = _as_mpf(mu_i, "repeated mean")
    scale = _as_mpf(sigma_i, "repeated scale")
    node = _as_mpf(g, "Gaussian node")
    if scale <= 0:
        raise M245ReplicaContractError("repeated scale must be strictly positive")
    relu_mean = unary_relu_mean(mean, scale)
    realized = mean + scale * node
    relu = realized if realized > 0 else mp.mpf("0")
    return ((relu - relu_mean) / scale) ** 2


def _determinant_three(matrix: tuple[tuple[mp.mpf, ...], ...]) -> mp.mpf:
    a, b, c = matrix[0]
    d, e, f = matrix[1]
    g, h, i = matrix[2]
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def _event_context(event_payload: Mapping[str, object]) -> dict[str, Any]:
    if not isinstance(event_payload, Mapping):
        raise M245ReplicaContractError("event payload must be a mapping")
    event_id = event_payload.get("event_id")
    if not isinstance(event_id, str) or not event_id:
        raise M245ReplicaContractError("event id is missing")
    if event_payload.get("no_redraw") is not True:
        raise M245ReplicaContractError("event no-redraw policy mismatch")
    labels = canonical_event(event_payload.get("event", ()))
    mu_receipt = event_payload.get("mu")
    covariance_receipt = event_payload.get("C")
    if (
        not isinstance(mu_receipt, dict)
        or mu_receipt.get("shape") != [3]
        or not isinstance(covariance_receipt, dict)
        or covariance_receipt.get("shape") != [3, 3]
    ):
        raise M245ReplicaContractError("event arrays have the wrong shape")
    mu = decode_authoritative_array(mu_receipt)
    flat_covariance = decode_authoritative_array(covariance_receipt)
    if len(mu) != 3 or len(flat_covariance) != 9:
        raise M245ReplicaContractError("event arrays have the wrong shape")
    covariance = tuple(
        tuple(flat_covariance[row * 3 + column] for column in range(3))
        for row in range(3)
    )
    if any(covariance[row][column] != covariance[column][row] for row in range(3) for column in range(3)):
        raise M245ReplicaContractError("event covariance is not exactly symmetric")
    if covariance[0][0] <= 0:
        raise M245ReplicaContractError("event covariance is not strict SPD")
    if covariance[0][0] * covariance[1][1] - covariance[0][1] ** 2 <= 0:
        raise M245ReplicaContractError("event covariance is not strict SPD")
    if _determinant_three(covariance) <= 0:
        raise M245ReplicaContractError("event covariance is not strict SPD")
    i, j, k = labels
    variance_i = covariance[i][i]
    sigma_i = mp.sqrt(variance_i)
    variance_j = covariance[j][j] - covariance[i][j] ** 2 / variance_i
    variance_k = covariance[k][k] - covariance[i][k] ** 2 / variance_i
    covariance_jk = covariance[j][k] - covariance[i][j] * covariance[i][k] / variance_i
    if variance_j <= 0 or variance_k <= 0:
        raise M245ReplicaContractError("conditional variance is not strictly positive")
    sigma_j = mp.sqrt(variance_j)
    sigma_k = mp.sqrt(variance_k)
    rho_c = covariance_jk / (sigma_j * sigma_k)
    if not mp.isfinite(rho_c) or abs(rho_c) >= 1:
        raise M245ReplicaContractError("conditional correlation is outside (-1,1)")
    ell = mp.sqrt(abs(rho_c))
    residual_loading = mp.sqrt(1 - abs(rho_c))
    eta = 1 if rho_c > 0 else (-1 if rho_c < 0 else 0)
    return {
        "event_id": event_id,
        "event": labels,
        "mu": mu,
        "C": covariance,
        "i": i,
        "j": j,
        "k": k,
        "sigma_i": sigma_i,
        "sigma_j": sigma_j,
        "sigma_k": sigma_k,
        "rho_c": rho_c,
        "ell": ell,
        "s": residual_loading,
        "eta": eta,
        "global_relu_mean_j": unary_relu_mean(mu[j], mp.sqrt(covariance[j][j])),
        "global_relu_mean_k": unary_relu_mean(mu[k], mp.sqrt(covariance[k][k])),
        "fixture_array_sha256": {
            "mu": event_payload["mu"]["sha256"],
            "C": event_payload["C"]["sha256"],
        },
        "audit_records": [],
        "top_level_error_sums": {},
        "b_cache": {},
    }


def conditional_factor_parameters(event_payload: Mapping[str, object]) -> dict[str, Any]:
    """Return the independently reconstructed signed unary factorization."""

    context = _event_context(event_payload)
    return {
        "event": context["event"],
        "event_id": context["event_id"],
        "rho_c": context["rho_c"],
        "ell": context["ell"],
        "s": context["s"],
        "eta": context["eta"],
        "sigma_i": context["sigma_i"],
        "s_j": context["sigma_j"],
        "s_k": context["sigma_k"],
    }


def antithetic_pair_average(plus: object, minus: object) -> mp.mpf:
    """Apply the frozen node-level antithetic factor one half."""

    return (_as_mpf(plus, "plus branch") + _as_mpf(minus, "minus branch")) / 2


def cache_scope_id(
    *,
    shard_id: int,
    invocation_index: int,
    event_id: str,
    engine: str,
    precision_dps: int,
) -> str:
    """Bind a cache to every dimension forbidden from crossing."""

    if isinstance(shard_id, bool) or not isinstance(shard_id, int) or shard_id < 0:
        raise M245ReplicaContractError("shard id must be a nonnegative integer")
    if invocation_index not in (1, 2) or isinstance(invocation_index, bool):
        raise M245ReplicaContractError("invocation index must be one or two")
    if not isinstance(event_id, str) or not event_id or any(character in event_id for character in "\r\n\0"):
        raise M245ReplicaContractError("event id is invalid")
    if engine not in ("primary", "replica"):
        raise M245ReplicaContractError("engine is invalid")
    if precision_dps not in PRECISIONS_DPS or isinstance(precision_dps, bool):
        raise M245ReplicaContractError("precision is invalid")
    return (
        f"m245|shard={shard_id}|invocation={invocation_index}|"
        f"event={event_id}|engine={engine}|dps={precision_dps}"
    )


def _parent_request_index(gateway: object) -> int | None:
    for attribute in ("active_request_index", "current_request_index"):
        value = getattr(gateway, attribute, None)
        if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
            return value
    return None


def _request_quad(
    context: dict[str, Any],
    quad_gateway: Callable[..., tuple[object, object]],
    *,
    integrand: Callable[[object], object],
    left: mp.mpf,
    right: mp.mpf,
    precision_dps: int,
    scope: str,
    quantity: str,
    call_role: str,
    panel_path: list[object],
    record_only_cache_hit: bool = False,
) -> tuple[mp.mpf, mp.mpf]:
    saved_eps = mp.mpf(mp.eps)
    request_callable = quad_gateway
    if record_only_cache_hit:
        request_callable = getattr(quad_gateway, "record_cache_hit", None)
        if not callable(request_callable):
            raise M245ReplicaContractError("quadrature gateway lacks its cache-hit ledger seam")
    try:
        response = request_callable(
            integrand=integrand,
            interval=[left, right],
            engine="replica",
            precision_dps=precision_dps,
            cache_scope_id=scope,
            quantity=quantity,
            call_role=call_role,
            panel_path=panel_path,
            parent_request_index=_parent_request_index(quad_gateway),
        )
    except Exception as exc:
        raise M245ReplicaContractError(f"quadrature gateway failed for {quantity}") from exc
    if not isinstance(response, tuple) or len(response) != 2:
        raise M245ReplicaContractError("quadrature gateway returned the wrong shape")
    value = _as_mpf(response[0], "quadrature value")
    error = _as_mpf(response[1], "quadrature error")
    passed = quadrature_call_gate(error, saved_eps)
    context["audit_records"].append(
        {
            "quantity": quantity,
            "call_role": call_role,
            "panel_path": list(panel_path),
            "saved_mp_eps": mp.nstr(saved_eps, n=precision_dps),
            "returned_error": mp.nstr(error, n=precision_dps),
            "cache_disposition": "hit" if record_only_cache_hit else "miss_or_gateway_owned",
            "pass": passed,
        }
    )
    if not passed:
        raise M245ReplicaContractError("quadrature returned an over-threshold error")
    return value, error


def _panel_endpoint(value: float) -> mp.mpf:
    return mp.inf if math.isinf(value) else mp.mpf(str(value))


def _conditional_means(context: Mapping[str, Any], g: mp.mpf, h: mp.mpf) -> tuple[mp.mpf, mp.mpf]:
    i, j, k = context["i"], context["j"], context["k"]
    covariance = context["C"]
    nu_j = context["mu"][j] + covariance[i][j] * g / context["sigma_i"]
    nu_k = context["mu"][k] + covariance[i][k] * g / context["sigma_i"]
    mean_j = nu_j + context["sigma_j"] * context["ell"] * h
    mean_k = nu_k + context["sigma_k"] * context["eta"] * context["ell"] * h
    scale_j = context["sigma_j"] * context["s"]
    scale_k = context["sigma_k"] * context["s"]
    centered_j = unary_relu_mean(mean_j, scale_j) - context["global_relu_mean_j"]
    centered_k = unary_relu_mean(mean_k, scale_k) - context["global_relu_mean_k"]
    return centered_j, centered_k


def _cache_key(value: mp.mpf) -> tuple[int, int, int, int]:
    return tuple(value._mpf_)


def _replica_b_from_context(
    context: dict[str, Any],
    g: object,
    precision_dps: int,
    quad_gateway: Callable[..., tuple[object, object]],
    scope: str,
) -> tuple[mp.mpf, dict[str, object]]:
    node = _as_mpf(g, "Gaussian node")
    call_role = (
        "nested_unary"
        if _parent_request_index(quad_gateway) is not None
        else "outer_top_level"
    )
    key = (scope, call_role, _cache_key(node))
    cached = context["b_cache"].get(key)
    if cached is not None:
        cache_hit_hook = getattr(quad_gateway, "record_cache_hit", None)
        if callable(cache_hit_hook):
            first_record = len(context["audit_records"])
            replayed_values: list[mp.mpf] = []
            replayed_errors: list[mp.mpf] = []
            for panel_index, (left_value, right_value) in enumerate(
                zip(INNER_BASE_PANELS[:-1], INNER_BASE_PANELS[1:])
            ):
                value, error = _request_quad(
                    context,
                    quad_gateway,
                    integrand=cached["integrand"],
                    left=_panel_endpoint(left_value),
                    right=_panel_endpoint(right_value),
                    precision_dps=precision_dps,
                    scope=scope,
                    quantity="b_rep",
                    call_role=call_role,
                    panel_path=["unary", panel_index],
                    record_only_cache_hit=True,
                )
                replayed_values.append(value)
                replayed_errors.append(abs(error))
            replayed_result = mp.fsum(replayed_values)
            replayed_error_sum = mp.fsum(replayed_errors)
            if replayed_result != cached["result"]:
                raise M245ReplicaContractError("gateway cache-hit replay changed the cached value")
            if not top_level_error_gate(replayed_error_sum, replayed_result):
                raise M245ReplicaContractError("cached unary error sum exceeds its gate")
            records = context["audit_records"][first_record:]
            return replayed_result, {
                "all_calls_pass": all(record["pass"] for record in records),
                "error_semantics": QUADRATURE_ERROR_SEMANTICS,
                "interval_certified": False,
                "observed_call_count": len(records),
                "top_level_error_sum": mp.nstr(replayed_error_sum, n=precision_dps),
                "unary_panel_count": 8,
                "cache_disposition": "HIT_RECORDED_WITH_GATEWAY",
            }
        if hasattr(quad_gateway, "ledger"):
            raise M245ReplicaContractError("metered quadrature gateway lacks its cache-hit ledger seam")
        return cached["result"], {
            "all_calls_pass": True,
            "error_semantics": QUADRATURE_ERROR_SEMANTICS,
            "interval_certified": False,
            "observed_call_count": 0,
            "unary_panel_count": 8,
            "cache_disposition": "HIT_WITHIN_SCOPE_UNMETERED_GATEWAY",
        }
    first_record = len(context["audit_records"])
    values: list[mp.mpf] = []
    errors: list[mp.mpf] = []

    def integrand(t: object) -> mp.mpf:
        point = mp.mpf(t)
        if mp.isinf(point):
            return mp.mpf("0")
        plus_j, plus_k = _conditional_means(context, node, point)
        minus_j, minus_k = _conditional_means(context, node, -point)
        return _phi(point) * (plus_j * plus_k + minus_j * minus_k)

    for panel_index, (left_value, right_value) in enumerate(
        zip(INNER_BASE_PANELS[:-1], INNER_BASE_PANELS[1:])
    ):
        value, error = _request_quad(
            context,
            quad_gateway,
            integrand=integrand,
            left=_panel_endpoint(left_value),
            right=_panel_endpoint(right_value),
            precision_dps=precision_dps,
            scope=scope,
            quantity="b_rep",
            call_role=call_role,
            panel_path=["unary", panel_index],
        )
        values.append(value)
        errors.append(abs(error))
    result = mp.fsum(values)
    error_sum = mp.fsum(errors)
    if not top_level_error_gate(error_sum, result):
        raise M245ReplicaContractError("unary top-level error sum exceeds its gate")
    context["b_cache"][key] = {"integrand": integrand, "result": result}
    records = context["audit_records"][first_record:]
    return result, {
        "all_calls_pass": all(record["pass"] for record in records),
        "error_semantics": QUADRATURE_ERROR_SEMANTICS,
        "interval_certified": False,
        "observed_call_count": len(records),
        "top_level_error_sum": mp.nstr(error_sum, n=precision_dps),
        "unary_panel_count": 8,
        "cache_disposition": "MISS_WITHIN_SCOPE",
    }


def replica_b_at_g(
    event_payload: Mapping[str, object],
    g: object,
    precision_dps: int,
    *,
    quad_gateway: Callable[..., tuple[object, object]],
    cache_scope_id: str | None = None,
) -> tuple[mp.mpf, dict[str, object]]:
    """Evaluate the independent unary-factor conditional pair at one node."""

    if precision_dps not in PRECISIONS_DPS or isinstance(precision_dps, bool):
        raise M245ReplicaContractError("precision must be 80 or 100 dps")
    if not callable(quad_gateway):
        raise M245ReplicaContractError("an injected quadrature gateway is required")
    with mp.workdps(precision_dps):
        context = _event_context(event_payload)
        scope = cache_scope_id
        if scope is None:
            scope = (
                f"m245|standalone|event={context['event_id']}|"
                f"engine=replica|dps={precision_dps}"
            )
        if not isinstance(scope, str) or not scope:
            raise M245ReplicaContractError("cache scope is invalid")
        return _replica_b_from_context(context, g, precision_dps, quad_gateway, scope)


def replica_moments_from_components(
    *,
    mu_rep: object,
    M_same: object,
    M_cross: object,
) -> dict[str, object]:
    """Apply the frozen same/sign-reversed replica identity."""

    mu_value = _as_mpf(mu_rep, "mu_rep")
    same_value = _as_mpf(M_same, "M_same")
    cross_value = _as_mpf(M_cross, "M_cross")
    K_rep = (same_value + cross_value) / 2 - mu_value * mu_value
    if not mp.isfinite(K_rep):
        raise M245ReplicaContractError("replica variance is nonfinite")
    return {
        "mu_rep": mu_value,
        "M_same": same_value,
        "M_cross": cross_value,
        "K_rep": K_rep,
    }


def _outer_panel_bounds(context: Mapping[str, Any]) -> tuple[mp.mpf, ...]:
    alpha = abs(context["mu"][context["i"]] / context["sigma_i"])
    finite = [mp.mpf(str(value)) for value in INNER_BASE_PANELS[:-1]]
    if all(alpha != value for value in finite):
        finite.append(alpha)
    finite.sort()
    return tuple(finite) + (mp.inf,)


def _integrate_outer(
    context: dict[str, Any],
    precision_dps: int,
    quad_gateway: Callable[..., tuple[object, object]],
    scope: str,
    quantity: str,
    branch_function: Callable[[mp.mpf], mp.mpf],
) -> mp.mpf:
    bounds = _outer_panel_bounds(context)
    values: list[mp.mpf] = []
    errors: list[mp.mpf] = []

    def integrand(t: object) -> mp.mpf:
        point = mp.mpf(t)
        if mp.isinf(point):
            return mp.mpf("0")
        return _phi(point) * (branch_function(point) + branch_function(-point))

    for panel_index, (left, right) in enumerate(zip(bounds[:-1], bounds[1:])):
        value, error = _request_quad(
            context,
            quad_gateway,
            integrand=integrand,
            left=left,
            right=right,
            precision_dps=precision_dps,
            scope=scope,
            quantity=quantity,
            call_role="outer_top_level",
            panel_path=[quantity, panel_index],
        )
        values.append(value)
        errors.append(abs(error))
    result = mp.fsum(values)
    error_sum = mp.fsum(errors)
    if not top_level_error_gate(error_sum, result):
        raise M245ReplicaContractError(f"{quantity} outer error sum exceeds its gate")
    context["top_level_error_sums"][quantity] = error_sum
    return result


def _serialized_mpf(value: object, precision_dps: int) -> str:
    scalar = _as_mpf(value, "serialized scalar")
    return mp.nstr(scalar, n=precision_dps)


def run_replica_event(
    event_payload: Mapping[str, object],
    precision_dps: int,
    *,
    quad_gateway: Callable[..., tuple[object, object]],
    cache_scope_id: str,
) -> dict[str, object]:
    """Construct one complete one-event/one-precision replica object."""

    if precision_dps not in PRECISIONS_DPS or isinstance(precision_dps, bool):
        raise M245ReplicaContractError("precision must be 80 or 100 dps")
    if not callable(quad_gateway):
        raise M245ReplicaContractError("an injected quadrature gateway is required")
    if not isinstance(cache_scope_id, str) or not cache_scope_id:
        raise M245ReplicaContractError("cache scope is required")
    with mp.workdps(precision_dps):
        context = _event_context(event_payload)

        def b_at(g: mp.mpf) -> mp.mpf:
            return _replica_b_from_context(
                context,
                g,
                precision_dps,
                quad_gateway,
                cache_scope_id,
            )[0]

        fixed_values = [b_at(mp.mpf(str(node))) for node in FIXED_B_NODES]
        i = context["i"]
        mu_i = context["mu"][i]
        sigma_i = context["sigma_i"]

        def rb(g: mp.mpf) -> mp.mpf:
            return replica_rbar_at_g(mu_i, sigma_i, g)

        mu_rep = _integrate_outer(
            context,
            precision_dps,
            quad_gateway,
            cache_scope_id,
            "mu_rep",
            lambda g: rb(g) * b_at(g),
        )
        M_same = _integrate_outer(
            context,
            precision_dps,
            quad_gateway,
            cache_scope_id,
            "M_same",
            lambda g: rb(g) ** 2 * b_at(g) ** 2,
        )
        M_cross = _integrate_outer(
            context,
            precision_dps,
            quad_gateway,
            cache_scope_id,
            "M_cross",
            lambda g: rb(g) * rb(-g) * b_at(g) * b_at(-g),
        )
        moment_values = replica_moments_from_components(
            mu_rep=mu_rep,
            M_same=M_same,
            M_cross=M_cross,
        )
        records = context["audit_records"]
        nested_error_sum = mp.fsum(
            mp.mpf(record["returned_error"])
            for record in records
            if record["call_role"] == "nested_unary"
        )
        result = {
            "artifact": "M245_REPLICA_EVENT_PRECISION",
            "schema": "m245-replica-event-v1",
            "event_id": context["event_id"],
            "precision_dps": precision_dps,
            "fixture_array_sha256": dict(context["fixture_array_sha256"]),
            "fixed_b_nodes": list(FIXED_B_NODES),
            "b_rep_at_nodes": [
                _serialized_mpf(value, precision_dps) for value in fixed_values
            ],
            "mu_rep": _serialized_mpf(moment_values["mu_rep"], precision_dps),
            "M_same": _serialized_mpf(moment_values["M_same"], precision_dps),
            "M_cross": _serialized_mpf(moment_values["M_cross"], precision_dps),
            "K_rep": _serialized_mpf(moment_values["K_rep"], precision_dps),
            "quadrature_audit": {
                "all_calls_pass": bool(records) and all(record["pass"] for record in records),
                "cache_scope_id": cache_scope_id,
                "error_semantics": QUADRATURE_ERROR_SEMANTICS,
                "interval_certified": False,
                "nested_raw_error_sum_diagnostic": _serialized_mpf(
                    nested_error_sum, precision_dps
                ),
                "observed_call_count": len(records),
                "outer_top_level_error_sums": {
                    name: _serialized_mpf(value, precision_dps)
                    for name, value in context["top_level_error_sums"].items()
                },
                "unary_panel_count": 8,
            },
            "firewall": {
                "network": False,
                "primary_import": False,
            },
        }
        validate_replica_result(result)
        return result


def _finite_float(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        scalar = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return scalar if math.isfinite(scalar) else None


def _all_native_real(*values: object) -> bool:
    return all(
        not isinstance(value, bool) and isinstance(value, (int, float))
        for value in values
    )


def precision_gate(z_80: object, z_100: object) -> bool:
    if _all_native_real(z_80, z_100):
        low = _finite_float(z_80)
        reference = _finite_float(z_100)
        if low is None or reference is None:
            return False
        tolerance = 2.0e-12 * max(1.0, abs(reference))
        return reference - tolerance <= low <= reference + tolerance
    try:
        low_mp = _as_mpf(z_80, "80-digit scalar")
        reference_mp = _as_mpf(z_100, "100-digit scalar")
    except M245ReplicaContractError:
        return False
    tolerance_mp = mp.mpf("2e-12") * max(mp.mpf("1"), abs(reference_mp))
    return reference_mp - tolerance_mp <= low_mp <= reference_mp + tolerance_mp


def quadrature_call_gate(returned_error: object, saved_mp_eps: object) -> bool:
    if _all_native_real(returned_error, saved_mp_eps):
        error = _finite_float(returned_error)
        epsilon = _finite_float(saved_mp_eps)
        if error is None or epsilon is None or error < 0.0 or epsilon <= 0.0:
            return False
        return error <= epsilon / 8.0
    try:
        error_mp = _as_mpf(returned_error, "quadrature error")
        epsilon_mp = _as_mpf(saved_mp_eps, "saved mp epsilon")
    except M245ReplicaContractError:
        return False
    return error_mp >= 0 and epsilon_mp > 0 and error_mp <= epsilon_mp / 8


def top_level_error_gate(error_sum: object, scalar: object) -> bool:
    if _all_native_real(error_sum, scalar):
        error = _finite_float(error_sum)
        value = _finite_float(scalar)
        if error is None or value is None or error < 0.0:
            return False
        return error <= 2.0e-14 * max(1.0, abs(value))
    try:
        error_mp = _as_mpf(error_sum, "top-level error sum")
        value_mp = _as_mpf(scalar, "top-level scalar")
    except M245ReplicaContractError:
        return False
    threshold = mp.mpf("2e-14") * max(mp.mpf("1"), abs(value_mp))
    return error_mp >= 0 and error_mp <= threshold


def primary_replica_node_gate(primary_b: object, replica_b: object) -> bool:
    if _all_native_real(primary_b, replica_b):
        reference = _finite_float(primary_b)
        observed = _finite_float(replica_b)
        if reference is None or observed is None:
            return False
        tolerance = 2.0e-10 * max(1.0, abs(reference))
        return reference - tolerance <= observed <= reference + tolerance
    try:
        reference_mp = _as_mpf(primary_b, "primary node value")
        observed_mp = _as_mpf(replica_b, "replica node value")
    except M245ReplicaContractError:
        return False
    tolerance_mp = mp.mpf("2e-10") * max(mp.mpf("1"), abs(reference_mp))
    return reference_mp - tolerance_mp <= observed_mp <= reference_mp + tolerance_mp


def primary_replica_integrated_gates(
    primary_mu: object,
    replica_mu: object,
    primary_K: object,
    replica_K: object,
) -> dict[str, object]:
    p_mu = _finite_float(primary_mu)
    r_mu = _finite_float(replica_mu)
    p_K = _finite_float(primary_K)
    r_K = _finite_float(replica_K)
    if p_mu is None or r_mu is None or p_K is None or r_K is None or p_K <= 0.0:
        return {
            "mu_pass": False,
            "K_pass": False,
            "pass": False,
            "mu_tolerance": None,
            "K_tolerance": None,
        }
    mu_tolerance = 2.0e-9 * max(1.0, abs(p_mu))
    K_tolerance = 5.0e-8 * p_K
    mu_pass = p_mu - mu_tolerance <= r_mu <= p_mu + mu_tolerance
    K_pass = p_K - K_tolerance <= r_K <= p_K + K_tolerance
    return {
        "mu_pass": mu_pass,
        "K_pass": K_pass,
        "pass": mu_pass and K_pass,
        "mu_tolerance": mu_tolerance,
        "K_tolerance": K_tolerance,
    }


def _validate_result_cache_scope(scope: object, event_id: str, precision_dps: int) -> None:
    if not isinstance(scope, str) or not scope:
        raise M245ReplicaContractError("replica cache scope is invalid")
    logical_parts = scope.split("|")
    if len(logical_parts) == 6 and logical_parts[0] == "m245":
        fields: dict[str, str] = {}
        for part in logical_parts[1:]:
            if part.count("=") != 1:
                break
            name, value = part.split("=", 1)
            if name in fields:
                break
            fields[name] = value
        else:
            if set(fields) == {"shard", "invocation", "event", "engine", "dps"}:
                try:
                    shard_id = int(fields["shard"])
                    invocation_index = int(fields["invocation"])
                    observed_dps = int(fields["dps"])
                    expected = cache_scope_id(
                        shard_id=shard_id,
                        invocation_index=invocation_index,
                        event_id=event_id,
                        engine="replica",
                        precision_dps=precision_dps,
                    )
                except (M245ReplicaContractError, ValueError):
                    pass
                else:
                    if (
                        fields["event"] == event_id
                        and fields["engine"] == "replica"
                        and observed_dps == precision_dps
                        and scope == expected
                    ):
                        return
    transport_parts = scope.split(":")
    if len(transport_parts) == 6:
        shard_text, invocation_text, observed_event, engine, dps_text, freshness = transport_parts
        try:
            shard_id = int(shard_text[1:]) if shard_text.startswith("S") else -1
            invocation_index = int(invocation_text[1:]) if invocation_text.startswith("I") else -1
            observed_dps = int(dps_text)
        except ValueError:
            pass
        else:
            expected = (
                f"S{shard_id}:I{invocation_index}:{event_id}:"
                f"replica:{precision_dps}:fresh"
            )
            if (
                shard_id in range(4)
                and invocation_index in (1, 2)
                and observed_event == event_id
                and engine == "replica"
                and observed_dps == precision_dps
                and freshness == "fresh"
                and scope == expected
            ):
                return
    raise M245ReplicaContractError("replica cache scope is not reconstructible")


def validate_replica_result(result: Mapping[str, object]) -> bool:
    """Fail closed on any lossy, nonfinite, or policy-drifted replica object."""

    if not isinstance(result, Mapping) or set(result) != _RESULT_KEYS:
        raise M245ReplicaContractError("replica result schema mismatch")
    if result.get("artifact") != "M245_REPLICA_EVENT_PRECISION":
        raise M245ReplicaContractError("replica result artifact mismatch")
    if result.get("schema") != "m245-replica-event-v1":
        raise M245ReplicaContractError("replica result version mismatch")
    event_id = result.get("event_id")
    if not isinstance(event_id, str) or not event_id:
        raise M245ReplicaContractError("replica result event id is invalid")
    precision_dps = result.get("precision_dps")
    if precision_dps not in PRECISIONS_DPS or isinstance(precision_dps, bool):
        raise M245ReplicaContractError("replica result precision is invalid")
    fixture_hashes = result.get("fixture_array_sha256")
    if not isinstance(fixture_hashes, dict) or set(fixture_hashes) != {"mu", "C"}:
        raise M245ReplicaContractError("replica fixture-hash schema mismatch")
    for name, digest in fixture_hashes.items():
        _require_hex_digest(digest, f"fixture {name} hash")
    fixed_nodes = result.get("fixed_b_nodes")
    if not isinstance(fixed_nodes, list) or tuple(fixed_nodes) != FIXED_B_NODES:
        raise M245ReplicaContractError("replica fixed-node census mismatch")
    node_values = result.get("b_rep_at_nodes")
    if not isinstance(node_values, list) or len(node_values) != len(FIXED_B_NODES):
        raise M245ReplicaContractError("replica node-value census mismatch")
    decoded_nodes = [_as_mpf(value, "replica node value") for value in node_values]
    if not any(value != 0 for value in decoded_nodes):
        raise M245ReplicaContractError("constant-zero replica node stub is forbidden")
    scalars = {
        name: _as_mpf(result.get(name), name)
        for name in ("mu_rep", "M_same", "M_cross", "K_rep")
    }
    expected_K = (scalars["M_same"] + scalars["M_cross"]) / 2 - scalars["mu_rep"] ** 2
    tolerance = mp.mpf("2e-12") * max(mp.mpf("1"), abs(expected_K))
    if abs(scalars["K_rep"] - expected_K) > tolerance:
        raise M245ReplicaContractError("replica moment identity mismatch")
    if scalars["M_same"] <= 0 or scalars["M_cross"] == 0 or scalars["K_rep"] <= 0:
        raise M245ReplicaContractError("constant-zero or nonpositive replica moment control")
    audit = result.get("quadrature_audit")
    if not isinstance(audit, dict) or set(audit) != _QUADRATURE_AUDIT_KEYS:
        raise M245ReplicaContractError("replica quadrature audit schema mismatch")
    observed_call_count = audit["observed_call_count"]
    if (
        audit["all_calls_pass"] is not True
        or isinstance(observed_call_count, bool)
        or not isinstance(observed_call_count, int)
        or observed_call_count <= 0
    ):
        raise M245ReplicaContractError("replica quadrature audit did not pass")
    if audit["error_semantics"] != QUADRATURE_ERROR_SEMANTICS:
        raise M245ReplicaContractError("replica quadrature semantics mismatch")
    if audit["interval_certified"] is not False:
        raise M245ReplicaContractError("heuristic quadrature errors cannot certify intervals")
    if audit["unary_panel_count"] != len(INNER_BASE_PANELS) - 1:
        raise M245ReplicaContractError("replica unary panel census mismatch")
    _validate_result_cache_scope(audit["cache_scope_id"], event_id, precision_dps)
    nested_error_sum = _as_mpf(
        audit["nested_raw_error_sum_diagnostic"],
        "replica nested raw error sum",
    )
    if nested_error_sum < 0:
        raise M245ReplicaContractError("replica nested raw error sum is negative")
    outer_error_sums = audit["outer_top_level_error_sums"]
    if not isinstance(outer_error_sums, dict) or set(outer_error_sums) != set(_TOP_LEVEL_QUANTITIES):
        raise M245ReplicaContractError("replica outer error-sum quantities mismatch")
    for quantity in _TOP_LEVEL_QUANTITIES:
        error_sum = _as_mpf(outer_error_sums[quantity], f"{quantity} outer error sum")
        if error_sum < 0 or not top_level_error_gate(error_sum, scalars[quantity]):
            raise M245ReplicaContractError(f"{quantity} outer error sum failed reconstruction")
    firewall = result.get("firewall")
    if not isinstance(firewall, dict) or set(firewall) != _FIREWALL_KEYS:
        raise M245ReplicaContractError("replica firewall schema mismatch")
    if any(value is not False for value in firewall.values()):
        raise M245ReplicaContractError("replica firewall failed")
    canonical_json_bytes(result)
    return True
