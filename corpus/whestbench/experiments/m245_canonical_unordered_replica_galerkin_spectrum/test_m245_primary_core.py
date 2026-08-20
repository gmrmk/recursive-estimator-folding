"""Frozen test-first contract for the M245 primary scientific core.

This file is scientific *test tissue*, not scientific evidence.  It reads the
committed fixture authority only to verify bytes and hashes.  Every numerical
evaluation below uses a dummy event outside the frozen E00:E07 census.

The import is intentionally first among non-stdlib dependencies.  Until the
separate primary implementation exists, this module must preserve the exact
missing-primary RED captured in ``M245_SCIENTIFIC_TDD_RED_RECEIPT_20260810.md``.
"""

from __future__ import annotations

import ast
import copy
import hashlib
import json
import math
from pathlib import Path
import struct
import tempfile
import unittest

import m245_primary_core as primary


HERE = Path(__file__).resolve().parent
V2_NAME = "M245_FROZEN_MANIFEST_V2_20260810.json"
V2_SHA256 = "0113cd950b229708d7844a423f793253ee50b1ccd1cf44c33ebf343b4f0e874b"
V2_CHECKSUM_NAME = "M245_SHA256SUMS_V2_20260810.txt"
V2_CHECKSUM_SHA256 = "2e56bd140b71527f640e1c1afbbc347fcca601fa4f0ec83f711c69a29e2b444e"

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
    V2_NAME: V2_SHA256,
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
OUTER_BASE_PANELS = (0.0, 0.25, 1.0, 2.5, 5.0, 8.0, 10.0, 16.0, math.inf)
QUADRATURE_ERROR_SEMANTICS = "heuristic_diagnostic_estimate_not_interval_certificate"
DIAGNOSTIC_DISPOSITION = "NO_ESTIMATOR_PROVIDER_DEPLOYMENT_SCORE_OR_SUBMISSION_CREDIT"

SHARD_ASSIGNMENTS = {
    0: ("E00", "E01"),
    1: ("E02", "E03"),
    2: ("E04", "E05"),
    3: ("E06", "E07"),
}

PRIMARY_PUBLIC_CALLABLES = (
    "canonical_event",
    "canonical_json_bytes",
    "load_verified_v2",
    "decode_authoritative_array",
    "outer_panel_bounds",
    "plackett_panel_bounds",
    "orthonormal_hermites",
    "gaussian_interval_moments",
    "rbar_at_g",
    "conditional_pair_parameters",
    "primary_b_at_g",
    "analytic_R_G",
    "run_primary_event",
    "precision_gate",
    "quadrature_call_gate",
    "top_level_error_gate",
    "solve_residual_gate",
    "ladder_energy_gates",
    "ordinary_beta_identity_gate",
    "classify_curve_ladder",
    "validate_primary_result",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_json_bytes(payload: object) -> bytes:
    return (
        json.dumps(
            payload,
            allow_nan=False,
            ensure_ascii=True,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def _checksum_rows(path: Path) -> dict[str, str]:
    rows: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        digest, name = line.split("  ", 1)
        if name in rows:
            raise AssertionError(f"duplicate checksum row: {name}")
        rows[name] = digest
    return rows


def _dummy_array_receipt(values: tuple[float, ...], shape: tuple[int, ...]) -> dict:
    if math.prod(shape) != len(values):
        raise AssertionError("test helper shape mismatch")
    raw = struct.pack("<" + "d" * len(values), *values)
    shape_json = json.dumps(list(shape), ensure_ascii=True, separators=(",", ":"))
    digest = hashlib.sha256(b"<f8\0" + shape_json.encode("utf-8") + b"\0" + raw).hexdigest()
    flat_hex = [float(value).hex() for value in values]
    if len(shape) == 1:
        hex_rows = [flat_hex]
        repr_rows = [[repr(float(value)) for value in values]]
    elif len(shape) == 2:
        width = shape[1]
        hex_rows = [flat_hex[i:i + width] for i in range(0, len(flat_hex), width)]
        flat_repr = [repr(float(value)) for value in values]
        repr_rows = [flat_repr[i:i + width] for i in range(0, len(flat_repr), width)]
    else:
        raise AssertionError("test helper supports rank one or two")
    return {
        "bytes": len(raw),
        "dtype": "<f8",
        "hash_preimage": "dtype_utf8_NUL_canonical_shape_json_NUL_C_order_bytes",
        "hex_rows": hex_rows,
        "raw_c_hex": raw.hex(),
        "raw_c_order_sha256": hashlib.sha256(raw).hexdigest(),
        "repr_rows": repr_rows,
        "sha256": digest,
        "shape": list(shape),
    }


def _dummy_event() -> dict:
    """A diagonal dummy cell that is deliberately outside E00:E07."""

    return {
        "event_id": "DUMMY_DIAGONAL_NOT_IN_FROZEN_CENSUS",
        "event": [0, 1, 2],
        "mu": _dummy_array_receipt((0.0, 0.25, -0.5), (3,)),
        "C": _dummy_array_receipt((1.0, 0.0, 0.0, 0.0, 1.25, 0.0, 0.0, 0.0, 0.75), (3, 3)),
        "no_redraw": True,
        "origin": "dummy_test_only",
    }


def _correlated_pair_dummy(rho: float) -> dict:
    """Non-census closed-form control for both Plackett orientations."""

    if not (-1.0 < rho < 1.0) or rho == 0.0:
        raise AssertionError("rho must be nonzero and strictly inside (-1,1)")
    covariance = (1.0, 0.0, 0.0, 0.0, 1.0, rho, 0.0, rho, 1.0)
    return {
        "event_id": f"DUMMY_CLOSED_FORM_RHO_{rho.hex()}_NOT_IN_FROZEN_CENSUS",
        "event": [0, 1, 2],
        "mu": _dummy_array_receipt((0.0, 0.0, 0.0), (3,)),
        "C": _dummy_array_receipt(covariance, (3, 3)),
        "no_redraw": True,
        "origin": "dummy_test_only",
    }


def _varying_dummy_event() -> dict:
    """Non-census, nonzero target with conditionally independent singletons."""

    # C_jk=C_ij*C_ik/C_ii makes rho_c exactly zero, while both conditional
    # unary means vary with G.  This exercises the complete outer Galerkin
    # path cheaply without becoming a zero-target stub control.
    covariance = (
        1.0, 0.30, -0.25,
        0.30, 1.0, -0.075,
        -0.25, -0.075, 1.0,
    )
    return {
        "event_id": "DUMMY_VARYING_NONZERO_NOT_IN_FROZEN_CENSUS",
        "event": [0, 1, 2],
        "mu": _dummy_array_receipt((0.10, -0.20, 0.30), (3,)),
        "C": _dummy_array_receipt(covariance, (3, 3)),
        "no_redraw": True,
        "origin": "dummy_test_only",
    }


def _relu_covariance_closed_form(rho: float) -> float:
    second = (
        math.sqrt(1.0 - rho * rho)
        + rho * (math.pi - math.acos(rho))
    ) / (2.0 * math.pi)
    return second - 1.0 / (2.0 * math.pi)


def _as_float(value: object) -> float:
    return float(value)


class _DummyQuadGateway:
    """Test-owned gateway; production owns no direct quadrature call site."""

    def __init__(self, mp_module: object) -> None:
        self.mp = mp_module
        self.request_count = 0

    def __call__(
        self,
        *,
        integrand: object,
        interval: object,
        engine: str,
        precision_dps: int,
        cache_scope_id: str,
        quantity: str,
        call_role: str,
        panel_path: object,
        parent_request_index: int | None,
    ) -> tuple[object, object]:
        del engine, precision_dps, cache_scope_id, quantity, call_role, panel_path, parent_request_index
        self.request_count += 1
        return self.mp.quad(
            integrand,
            interval,
            method="tanh-sinh",
            maxdegree=14,
            error=True,
        )


def _imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module)
    return imported


def _mp_quad_call_owners(path: Path) -> list[str]:
    """Return the lexical function owner of every literal ``*.quad`` call."""

    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    owners: list[str] = []

    class Visitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.stack: list[str] = []

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            self.stack.append(node.name)
            self.generic_visit(node)
            self.stack.pop()

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_Call(self, node: ast.Call) -> None:
            if isinstance(node.func, ast.Attribute) and node.func.attr == "quad":
                owners.append(self.stack[-1] if self.stack else "<module>")
            self.generic_visit(node)

    Visitor().visit(tree)
    return owners


class TestM245PrimaryAuthorityAndAPI(unittest.TestCase):
    def test_public_surface_and_frozen_constants_are_exact(self) -> None:
        self.assertTrue(issubclass(primary.M245PrimaryContractError, Exception))
        for name in PRIMARY_PUBLIC_CALLABLES:
            with self.subTest(name=name):
                self.assertTrue(callable(getattr(primary, name, None)), name)
        self.assertEqual(tuple(primary.DEGREES), DEGREES)
        self.assertEqual(tuple(primary.PRECISIONS_DPS), PRECISIONS_DPS)
        self.assertEqual(tuple(primary.FIXED_B_NODES), FIXED_B_NODES)
        self.assertEqual(tuple(primary.OUTER_BASE_PANELS), OUTER_BASE_PANELS)
        self.assertEqual(primary.QUADRATURE_ERROR_SEMANTICS, QUADRATURE_ERROR_SEMANTICS)
        self.assertEqual(primary.DIAGNOSTIC_DISPOSITION, DIAGNOSTIC_DISPOSITION)
        self.assertEqual(primary.ENDPOINT_CONTROL_EVENT_ID, "E00")
        self.assertEqual(primary.V2_SHA256, V2_SHA256)
        self.assertEqual(dict(primary.AUTHORITY_SHA256), AUTHORITY_SHA256)

    def test_authority_checksum_census_and_every_bound_byte_hash(self) -> None:
        self.assertEqual(_sha256(HERE / V2_CHECKSUM_NAME), V2_CHECKSUM_SHA256)
        self.assertEqual(_checksum_rows(HERE / V2_CHECKSUM_NAME), AUTHORITY_SHA256)
        for name, digest in AUTHORITY_SHA256.items():
            with self.subTest(name=name):
                self.assertEqual(_sha256(HERE / name), digest)

    def test_v2_is_canonical_and_has_the_exact_frozen_census(self) -> None:
        raw = (HERE / V2_NAME).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), V2_SHA256)
        payload = json.loads(raw)
        self.assertEqual(raw, _canonical_json_bytes(payload))
        self.assertEqual(payload["artifact"], "M245_FROZEN_FIXTURE_AUTHORITY_V2")
        self.assertEqual(payload["schema"], "m245-authority-manifest-v2")
        self.assertEqual(payload["scientific_quantities_evaluated"], [])
        self.assertFalse(payload["retry_or_redraw"])
        self.assertEqual(
            [fixture["event_id"] for fixture in payload["fixtures"]],
            [f"E{index:02d}" for index in range(8)],
        )
        self.assertEqual(
            {
                shard["shard_id"]: tuple(shard["events_in_order"])
                for shard in payload["shards"]
            },
            SHARD_ASSIGNMENTS,
        )
        for fixture in payload["fixtures"]:
            self.assertEqual(fixture["event"], [0, 1, 2])
            self.assertTrue(fixture["no_redraw"])
            for name, expected_shape in (("mu", [3]), ("C", [3, 3])):
                receipt = fixture[name]
                self.assertEqual(receipt["dtype"], "<f8")
                self.assertEqual(receipt["shape"], expected_shape)
                raw_array = bytes.fromhex(receipt["raw_c_hex"])
                self.assertEqual(len(raw_array), receipt["bytes"])
                self.assertEqual(hashlib.sha256(raw_array).hexdigest(), receipt["raw_c_order_sha256"])
                shape_json = json.dumps(expected_shape, ensure_ascii=True, separators=(",", ":"))
                preimage = b"<f8\0" + shape_json.encode("utf-8") + b"\0" + raw_array
                self.assertEqual(hashlib.sha256(preimage).hexdigest(), receipt["sha256"])

    def test_load_verified_v2_accepts_only_the_bound_hash_and_schema(self) -> None:
        payload = primary.load_verified_v2(HERE / V2_NAME, V2_SHA256)
        self.assertEqual(payload["artifact"], "M245_FROZEN_FIXTURE_AUTHORITY_V2")
        with self.assertRaises(primary.M245PrimaryContractError):
            primary.load_verified_v2(HERE / V2_NAME, "0" * 64)
        tampered = copy.deepcopy(payload)
        tampered["scientific_quantities_evaluated"] = ["forbidden-preview"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "dummy_tampered_v2.json"
            path.write_bytes(_canonical_json_bytes(tampered))
            with self.assertRaises(primary.M245PrimaryContractError):
                primary.load_verified_v2(path, _sha256(path))

    def test_authoritative_array_decoder_uses_raw_binary64_not_decimal_repr(self) -> None:
        receipt = _dummy_array_receipt((0.1, -0.0, 1.5), (3,))
        decoded = tuple(primary.decode_authoritative_array(receipt))
        self.assertEqual(len(decoded), 3)
        for observed, source in zip(decoded, (0.1, -0.0, 1.5)):
            numerator, denominator = source.as_integer_ratio()
            self.assertEqual(observed, primary.mp.mpf(numerator) / primary.mp.mpf(denominator))

        decimal_poisoned = copy.deepcopy(receipt)
        decimal_poisoned["repr_rows"] = [["999", "999", "999"]]
        self.assertEqual(tuple(primary.decode_authoritative_array(decimal_poisoned)), decoded)

    def test_authoritative_array_decoder_refuses_hash_shape_dtype_and_hex_drift(self) -> None:
        receipt = _dummy_array_receipt((0.125, -0.5, 2.0), (3,))
        mutations = []
        for key, value in (("dtype", ">f8"), ("shape", [1, 3]), ("sha256", "0" * 64)):
            changed = copy.deepcopy(receipt)
            changed[key] = value
            mutations.append(changed)
        changed = copy.deepcopy(receipt)
        changed["hex_rows"][0][0] = "0x1.0p+9"
        mutations.append(changed)
        changed = copy.deepcopy(receipt)
        changed["raw_c_hex"] = changed["raw_c_hex"][:-2]
        mutations.append(changed)
        for index, changed in enumerate(mutations):
            with self.subTest(index=index):
                with self.assertRaises(primary.M245PrimaryContractError):
                    tuple(primary.decode_authoritative_array(changed))

    def test_primary_source_import_firewall_and_independence(self) -> None:
        path = Path(primary.__file__).resolve()
        imported = _imports(path)
        forbidden_prefixes = (
            "numpy",
            "scipy",
            "m245_replica_core",
            "m243",
            "m178",
            "m151",
            "m196",
            "m125",
            "requests",
            "urllib",
            "http",
            "socket",
            "subprocess",
        )
        self.assertFalse(
            any(name.lower().startswith(forbidden_prefixes) for name in imported),
            imported,
        )

    def test_primary_contains_no_direct_or_aliased_mpmath_quad_call(self) -> None:
        path = Path(primary.__file__).resolve()
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "quad"
        ]
        self.assertEqual(calls, [], "the worker owns the sole project-source mp.quad site")
        self.assertEqual(_mp_quad_call_owners(path), [])
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "mpmath":
                self.assertNotIn("quad", {alias.name for alias in node.names})


class TestM245PrimaryExactMath(unittest.TestCase):
    def test_canonical_event_sorts_only_the_unordered_pair(self) -> None:
        self.assertEqual(primary.canonical_event((0, 1, 2)), (0, 1, 2))
        self.assertEqual(primary.canonical_event((0, 2, 1)), (0, 1, 2))
        self.assertEqual(primary.canonical_event((2, 1, 0)), (2, 0, 1))
        for invalid in (
            (0, 0, 1),
            (0, 1, 1),
            (0, 0, 0),
            (0.0, 1, 2),
            (False, 1, 2),
            (-1, 1, 2),
            (3, 1, 2),
            (0, 1),
        ):
            with self.subTest(invalid=invalid):
                with self.assertRaises(primary.M245PrimaryContractError):
                    primary.canonical_event(invalid)

    def test_outer_panels_are_exact_sorted_union_with_abs_alpha(self) -> None:
        self.assertEqual(tuple(primary.outer_panel_bounds(-1.0)), OUTER_BASE_PANELS)
        expected = (0.0, 0.25, 0.625, 1.0, 2.5, 5.0, 8.0, 10.0, 16.0, math.inf)
        self.assertEqual(tuple(primary.outer_panel_bounds(-0.625)), expected)
        self.assertEqual(tuple(primary.outer_panel_bounds(0.625)), expected)
        self.assertEqual(tuple(primary.outer_panel_bounds(0.0)), OUTER_BASE_PANELS)
        self.assertEqual(tuple(primary.outer_panel_bounds(-0.25)), OUTER_BASE_PANELS)
        self.assertEqual(tuple(primary.outer_panel_bounds(0.25)), OUTER_BASE_PANELS)
        self.assertEqual(tuple(primary.outer_panel_bounds(0.625)).count(0.625), 1)
        with self.assertRaises(primary.M245PrimaryContractError):
            primary.outer_panel_bounds(math.nan)

    def test_plackett_uses_exactly_sixteen_directed_equal_panels(self) -> None:
        for rho in (0.75, -0.75, 0.0):
            with self.subTest(rho=rho):
                bounds = tuple(primary.plackett_panel_bounds(rho))
                self.assertEqual(len(bounds), 17)
                self.assertEqual(bounds[0], 0)
                self.assertEqual(bounds[-1], rho)
                for index, value in enumerate(bounds):
                    self.assertEqual(value, rho * index / 16)
        self.assertTrue(all(a > b for a, b in zip(
            primary.plackett_panel_bounds(-0.5),
            tuple(primary.plackett_panel_bounds(-0.5))[1:],
        )))

    def test_orthonormal_probabilists_hermites_obey_the_frozen_recurrence(self) -> None:
        for g in (-2.5, 0.0, 0.375, 2.0):
            with self.subTest(g=g):
                h = tuple(primary.orthonormal_hermites(g, 20))
                self.assertEqual(len(h), 21)
                self.assertTrue(all(math.isfinite(float(value)) for value in h))
                self.assertEqual(h[0], 1)
                self.assertEqual(h[1], g)
                self.assertAlmostEqual(float(h[2]), (g * g - 1.0) / math.sqrt(2.0), places=14)
                self.assertAlmostEqual(float(h[3]), (g**3 - 3.0 * g) / math.sqrt(6.0), places=14)
                for q in range(1, 20):
                    rhs = (g * h[q] - math.sqrt(q) * h[q - 1]) / math.sqrt(q + 1)
                    self.assertAlmostEqual(float(h[q + 1]), float(rhs), places=14)

    def test_gaussian_interval_moment_recursion_has_explicit_half_normal_factor(self) -> None:
        full = tuple(primary.gaussian_interval_moments(-math.inf, math.inf, 20))
        expected_full = []
        even_moment = 1.0
        for degree in range(21):
            if degree % 2:
                expected_full.append(0.0)
            else:
                if degree >= 2:
                    even_moment *= degree - 1
                expected_full.append(even_moment)
        for observed, expected in zip(full, expected_full):
            self.assertAlmostEqual(float(observed), expected, places=14)
        half = tuple(primary.gaussian_interval_moments(0.0, math.inf, 4))
        inverse_root_two_pi = 1.0 / math.sqrt(2.0 * math.pi)
        expected_half = (0.5, inverse_root_two_pi, 0.5, 2.0 * inverse_root_two_pi, 1.5)
        for observed, expected in zip(half, expected_half):
            self.assertAlmostEqual(float(observed), expected, places=14)
        self.assertAlmostEqual(2.0 * float(half[0]), 1.0, places=14)

        a, b = -0.75, 1.25
        finite = tuple(primary.gaussian_interval_moments(a, b, 20))
        phi = lambda x: math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)
        Phi = lambda x: 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))
        expected = [Phi(b) - Phi(a), phi(a) - phi(b)]
        for degree in range(2, 21):
            expected.append(
                a ** (degree - 1) * phi(a)
                - b ** (degree - 1) * phi(b)
                + (degree - 1) * expected[degree - 2]
            )
        for degree, (observed, reference) in enumerate(zip(finite, expected)):
            with self.subTest(degree=degree):
                self.assertAlmostEqual(float(observed), reference, places=13)

    def test_rbar_is_scale_normalized_exactly(self) -> None:
        for g in (-1.0, 0.0, 0.75, 2.0):
            base = primary.rbar_at_g(0.25, 1.5, g)
            scaled = primary.rbar_at_g(0.5, 3.0, g)
            self.assertAlmostEqual(float(base), float(scaled), places=14)

    def test_rbar_inactive_branch_tail_cross_and_uq_leading_coefficient_are_exact(self) -> None:
        inverse_root_two_pi = 1.0 / math.sqrt(2.0 * math.pi)
        inactive = primary.rbar_at_g(0.0, 1.0, -8.0)
        self.assertAlmostEqual(float(inactive), inverse_root_two_pi**2, places=14)
        t = 8.0
        active = primary.rbar_at_g(0.0, 1.0, t)
        cross = float(active) * float(inactive)
        self.assertGreater(cross, 0.0)
        self.assertAlmostEqual(
            cross,
            (t - inverse_root_two_pi) ** 2 * inverse_root_two_pi**2,
            places=12,
        )

        tail_t = 1.0e6
        r_plus = primary.rbar_at_g(0.0, 1.0, tail_t)
        r_minus = primary.rbar_at_g(0.0, 1.0, -tail_t)
        h_plus = primary.orthonormal_hermites(tail_t, 8)
        h_minus = primary.orthonormal_hermites(-tail_t, 8)
        for q in DEGREES:
            u_q = 0.5 * (
                float(r_plus) * float(h_plus[q])
                + float(r_minus) * float(h_minus[q])
            )
            observed = u_q / (tail_t ** (q + 2))
            expected = 1.0 / (2.0 * math.sqrt(math.factorial(q)))
            with self.subTest(q=q, parity="even" if q % 2 == 0 else "odd"):
                self.assertTrue(
                    math.isclose(observed, expected, rel_tol=2.0e-6, abs_tol=0.0),
                    (q, observed, expected),
                )

    def test_conditional_parameters_are_the_exact_schur_complement(self) -> None:
        dummy = _dummy_event()
        parameters = primary.conditional_pair_parameters(dummy)
        self.assertEqual(tuple(parameters["event"]), (0, 1, 2))
        self.assertEqual(float(parameters["s_j_squared"]), 1.25)
        self.assertEqual(float(parameters["s_k_squared"]), 0.75)
        self.assertEqual(float(parameters["s_jk"]), 0.0)
        self.assertEqual(float(parameters["rho_c"]), 0.0)

    def test_primary_b_is_zero_for_the_dummy_independent_pair_at_all_frozen_nodes(self) -> None:
        dummy = _dummy_event()
        for dps in PRECISIONS_DPS:
            for g in FIXED_B_NODES:
                with self.subTest(dps=dps, g=g):
                    gateway = _DummyQuadGateway(primary.mp)
                    value, audit = primary.primary_b_at_g(
                        dummy, g, dps, quad_gateway=gateway
                    )
                    self.assertLessEqual(abs(float(value)), 2.0e-30)
                    self.assertGreater(gateway.request_count, 0)
                    self.assertTrue(audit["all_calls_pass"])
                    self.assertEqual(audit["error_semantics"], QUADRATURE_ERROR_SEMANTICS)
                    self.assertFalse(audit["interval_certified"])
                    self.assertEqual(audit["plackett_panel_count"], 16)

    def test_primary_b_matches_nonzero_closed_form_for_both_plackett_directions(self) -> None:
        for rho in (0.36, -0.36):
            dummy = _correlated_pair_dummy(rho)
            expected = _relu_covariance_closed_form(rho)
            parameters = primary.conditional_pair_parameters(dummy)
            self.assertAlmostEqual(float(parameters["rho_c"]), rho, places=14)
            bounds = tuple(primary.plackett_panel_bounds(parameters["rho_c"]))
            self.assertEqual(len(bounds), 17)
            self.assertEqual(bounds[0], 0)
            self.assertAlmostEqual(float(bounds[-1]), rho, places=15)
            self.assertEqual(all(left < right for left, right in zip(bounds, bounds[1:])), rho > 0)
            for dps in PRECISIONS_DPS:
                for g in (-2.5, 0.0, 2.5):
                    with self.subTest(rho=rho, dps=dps, g=g):
                        gateway = _DummyQuadGateway(primary.mp)
                        value, audit = primary.primary_b_at_g(
                            dummy, g, dps, quad_gateway=gateway
                        )
                        self.assertAlmostEqual(float(value), expected, places=12)
                        self.assertGreater(gateway.request_count, 0)
                        self.assertTrue(audit["all_calls_pass"])
                        self.assertEqual(audit["error_semantics"], QUADRATURE_ERROR_SEMANTICS)
                        self.assertFalse(audit["interval_certified"])
                        self.assertEqual(audit["plackett_panel_count"], 16)

    def test_analytic_R_G_has_the_full_nine_by_nine_symmetric_census(self) -> None:
        R, G = primary.analytic_R_G(_dummy_event(), 80)
        self.assertEqual(len(R), 9)
        self.assertEqual(len(G), 9)
        self.assertTrue(all(len(row) == 9 for row in G))
        for i in range(9):
            for j in range(9):
                self.assertEqual(G[i][j], G[j][i])


class TestM245PrimaryFrozenGates(unittest.TestCase):
    def test_precision_gate_has_the_exact_relative_floor(self) -> None:
        self.assertTrue(primary.precision_gate(0.0, 2.0e-12))
        self.assertFalse(primary.precision_gate(0.0, math.nextafter(2.0e-12, math.inf)))
        self.assertTrue(primary.precision_gate(1.0e6, 1.0e6 + 2.0e-6))
        self.assertFalse(primary.precision_gate(math.nan, 0.0))

    def test_quadrature_error_gates_use_saved_eps_and_top_level_scale(self) -> None:
        saved_eps = 8.0e-80
        self.assertTrue(primary.quadrature_call_gate(1.0e-80, saved_eps))
        self.assertFalse(primary.quadrature_call_gate(math.nextafter(1.0e-80, math.inf), saved_eps))
        self.assertTrue(primary.top_level_error_gate(2.0e-14, 0.0))
        self.assertTrue(primary.top_level_error_gate(2.0e-8, 1.0e6))
        self.assertFalse(primary.top_level_error_gate(math.inf, 1.0))

    def test_solve_residual_gate_is_exact_and_nonfinite_fails(self) -> None:
        self.assertTrue(primary.solve_residual_gate(2.0e-20))
        self.assertFalse(primary.solve_residual_gate(math.nextafter(2.0e-20, math.inf)))
        self.assertFalse(primary.solve_residual_gate(math.nan))

    def test_energy_ladder_gates_include_bounds_and_monotonicity_on_dummy_data(self) -> None:
        K = 10.0
        tau = 2.0e-10 * K
        P = [1.0 + index for index in range(9)]
        V = [K - value for value in P]
        verdict = primary.ladder_energy_gates("DUMMY_NONCONTROL", K, P, V)
        self.assertTrue(verdict["pass"])
        self.assertEqual(verdict["tau_K"], tau)

        bad = list(P)
        bad[4] = bad[3] - math.nextafter(tau, math.inf)
        self.assertFalse(primary.ladder_energy_gates("DUMMY_NONCONTROL", K, bad, V)["pass"])


    def test_ordinary_beta_identity_gate_uses_both_sides_and_nonnegativity(self) -> None:
        K = 5.0
        self.assertTrue(primary.ordinary_beta_identity_gate(K, 0.25, 0.25)["pass"])
        self.assertFalse(primary.ordinary_beta_identity_gate(K, 0.25, 0.26)["pass"])
        self.assertFalse(primary.ordinary_beta_identity_gate(K, -2.0e-9, -2.0e-9)["pass"])

    def test_curve_ladder_exact_transforms_fit_Q0_5_and_hold_out_Q6_8(self) -> None:
        q = range(9)
        geometric = [1.0 - math.exp(-0.2 - 0.1 * index) for index in q]
        logistic = [1.0 / (1.0 + math.exp(-(-0.4 + 0.15 * index))) for index in q]
        gompertz = [math.exp(-math.exp(0.3 - 0.08 * index)) for index in q]
        for model, values in (
            ("geometric", geometric),
            ("logistic", logistic),
            ("Gompertz", gompertz),
        ):
            with self.subTest(model=model):
                report = primary.classify_curve_ladder(
                    "DUMMY_NONCONTROL", model, values, values
                )
                self.assertEqual(report["fit_degrees"], [0, 1, 2, 3, 4, 5])
                self.assertEqual(report["holdout_degrees"], [6, 7, 8])
                self.assertEqual(report["second_difference_indices"], [1, 2, 3, 4, 5, 6, 7])
                self.assertEqual(report["label"], "NOT_FALSIFIED_ON_Q0_8")
                self.assertEqual(report["only_future_bound"], "0<=additional_explainable_energy_beyond_Q8<=K-P8")

    def test_curve_domains_refuse_negative_geometric_and_endpoints(self) -> None:
        invalid_by_model = {
            "geometric": [-0.01] + [0.5] * 8,
            "logistic": [0.0] + [0.5] * 8,
            "Gompertz": [1.0] + [0.5] * 8,
        }
        for model, values in invalid_by_model.items():
            with self.subTest(model=model):
                report = primary.classify_curve_ladder(
                    "DUMMY_NONCONTROL", model, values, values
                )
                self.assertEqual(report["label"], "FALSIFIED")
                self.assertEqual(report["reason"], "MODEL_DOMAIN_REFUSAL")

    def test_curve_ladder_falsifies_curvature_and_unrefitted_holdout_miss(self) -> None:
        curved = [0.10 + 0.006 * index * index for index in range(9)]
        curved_report = primary.classify_curve_ladder(
            "DUMMY_NONCONTROL", "geometric", curved, curved
        )
        self.assertEqual(curved_report["label"], "FALSIFIED")

        exact = [1.0 - math.exp(-0.2 - 0.1 * index) for index in range(9)]
        held_out_miss = list(exact)
        held_out_miss[8] -= 0.02
        report = primary.classify_curve_ladder(
            "DUMMY_NONCONTROL", "geometric", held_out_miss, held_out_miss
        )
        self.assertEqual(report["fit_degrees"], [0, 1, 2, 3, 4, 5])
        self.assertEqual(report["holdout_degrees"], [6, 7, 8])
        self.assertEqual(report["label"], "FALSIFIED")


class TestM245PrimaryResultContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.dummy = _varying_dummy_event()
        cls.results = {
            dps: primary.run_primary_event(
                cls.dummy,
                dps,
                quad_gateway=_DummyQuadGateway(primary.mp),
            )
            for dps in PRECISIONS_DPS
        }

    def test_primary_result_is_one_event_one_precision_and_json_safe(self) -> None:
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
        for dps, result in self.results.items():
            with self.subTest(dps=dps):
                self.assertEqual(set(result), required)
                self.assertEqual(result["artifact"], "M245_PRIMARY_EVENT_PRECISION")
                self.assertEqual(result["schema"], "m245-primary-event-v1")
                self.assertEqual(result["event_id"], self.dummy["event_id"])
                self.assertEqual(result["precision_dps"], dps)
                self.assertEqual(result["degrees"], list(DEGREES))
                self.assertEqual(len(result["R"]), 9)
                self.assertEqual(len(result["G"]), 9)
                self.assertTrue(all(len(row) == 9 for row in result["G"]))
                self.assertEqual(len(result["d"]), 9)
                self.assertEqual(len(result["beta"]), 9)
                self.assertEqual([row["Q"] for row in result["leading_blocks"]], list(DEGREES))
                self.assertGreater(_as_float(result["K"]), 0.0)
                self.assertTrue(result["quadrature_audit"]["all_calls_pass"])
                self.assertEqual(
                    result["quadrature_audit"]["error_semantics"],
                    QUADRATURE_ERROR_SEMANTICS,
                )
                self.assertFalse(result["quadrature_audit"]["interval_certified"])
                self.assertFalse(result["firewall"]["network"])
                primary.validate_primary_result(result)
                _canonical_json_bytes(result)

    def test_all_9_R_and_45_upper_G_direct_checks_are_real_and_pass(self) -> None:
        for dps, result in self.results.items():
            checks = result["analytic_direct_checks"]
            self.assertEqual(set(checks), {"R", "G_upper", "all_pass"})
            self.assertEqual([row["q"] for row in checks["R"]], list(DEGREES))
            self.assertEqual(
                [(row["m"], row["q"]) for row in checks["G_upper"]],
                [(m, q) for q in DEGREES for m in range(q + 1)],
            )
            self.assertEqual(len(checks["R"]), 9)
            self.assertEqual(len(checks["G_upper"]), 45)
            self.assertTrue(checks["all_pass"])
            for row in checks["R"] + checks["G_upper"]:
                with self.subTest(dps=dps, row=row):
                    self.assertTrue(row["pass"])
                    self.assertTrue(math.isfinite(_as_float(row["analytic"])))
                    self.assertTrue(math.isfinite(_as_float(row["direct"])))
                    self.assertLessEqual(
                        abs(_as_float(row["analytic"]) - _as_float(row["direct"])),
                        2.0e-11 * max(1.0, abs(_as_float(row["direct"]))),
                    )

    def test_every_leading_block_carries_cholesky_solve_energy_and_beta_certificates(self) -> None:
        required = {
            "Q", "c", "P", "V", "lambda_min", "lambda_max",
            "lambda_ratio", "condition_2", "cholesky_pass",
            "solve_relative_inf_residual", "solve_pass", "energy_gate",
            "V_beta", "ordinary_beta_identity", "direct_residual",
            "direct_beta_residual",
        }
        for dps, result in self.results.items():
            K = _as_float(result["K"])
            tau_K = 2.0e-10 * K
            previous_P = None
            for block in result["leading_blocks"]:
                Q = block["Q"]
                with self.subTest(dps=dps, Q=Q):
                    self.assertTrue(required.issubset(block))
                    self.assertEqual(len(block["c"]), Q + 1)
                    self.assertTrue(block["cholesky_pass"])
                    self.assertGreater(_as_float(block["lambda_min"]), 0.0)
                    self.assertGreaterEqual(_as_float(block["lambda_ratio"]), 1.0e-25)
                    self.assertLessEqual(_as_float(block["condition_2"]), 1.0e25)
                    self.assertTrue(block["solve_pass"])
                    self.assertLessEqual(_as_float(block["solve_relative_inf_residual"]), 2.0e-20)
                    P = _as_float(block["P"])
                    V = _as_float(block["V"])
                    self.assertGreaterEqual(P, -tau_K)
                    self.assertLessEqual(P, K + tau_K)
                    self.assertGreaterEqual(V, -tau_K)
                    if previous_P is not None:
                        self.assertGreaterEqual(P, previous_P - tau_K)
                    previous_P = P
                    self.assertTrue(block["energy_gate"]["pass"])

                    identity = block["ordinary_beta_identity"]
                    self.assertTrue(identity["pass"])
                    self.assertLessEqual(
                        abs(_as_float(identity["lhs"]) - _as_float(identity["rhs"])),
                        2.0e-20 * K,
                    )
                    self.assertGreaterEqual(_as_float(identity["gap"]), -tau_K)
                    if Q in (0, 4, 8):
                        self.assertGreater(
                            _as_float(identity["gap"]),
                            1.0e-30 * max(1.0, K),
                        )
                        for direct in (block["direct_residual"], block["direct_beta_residual"]):
                            self.assertEqual(set(direct), {"observed", "reference", "pass"})
                            self.assertTrue(direct["pass"])
                            self.assertGreater(
                                abs(_as_float(direct["observed"])),
                                1.0e-30 * max(1.0, K),
                            )
                            self.assertGreater(
                                abs(_as_float(direct["reference"])),
                                1.0e-30 * max(1.0, K),
                            )
                            self.assertLessEqual(
                                abs(_as_float(direct["observed"]) - _as_float(direct["reference"])),
                                2.0e-9 * K,
                            )
                    else:
                        self.assertIsNone(block["direct_residual"])
                        self.assertIsNone(block["direct_beta_residual"])

    def test_all_reported_primary_scalars_agree_between_80_and_100_dps(self) -> None:
        low, high = self.results[80], self.results[100]
        scalar_pairs = [(low["mu_rb"], high["mu_rb"]), (low["K"], high["K"])]
        scalar_pairs.extend(zip(low["R"], high["R"]))
        scalar_pairs.extend(zip(low["d"], high["d"]))
        scalar_pairs.extend(zip(low["beta"], high["beta"]))
        for low_row, high_row in zip(low["G"], high["G"]):
            scalar_pairs.extend(zip(low_row, high_row))
        for low_block, high_block in zip(low["leading_blocks"], high["leading_blocks"]):
            scalar_pairs.extend(zip(low_block["c"], high_block["c"]))
            scalar_pairs.extend((
                (low_block["P"], high_block["P"]),
                (low_block["V"], high_block["V"]),
                (low_block["V_beta"], high_block["V_beta"]),
            ))
        for index, (z80, z100) in enumerate(scalar_pairs):
            with self.subTest(index=index):
                self.assertTrue(primary.precision_gate(_as_float(z80), _as_float(z100)))

if __name__ == "__main__":
    unittest.main()
