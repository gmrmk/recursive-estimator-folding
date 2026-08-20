"""Frozen test-first contract for the independent M245 replica core.

This file is scientific *test tissue*, not scientific evidence.  It reads the
committed V2 only for byte/hash authority checks and evaluates only dummy
events outside E00:E07.  The replica implementation is deliberately forbidden
from importing the primary implementation.

The missing replica import is intentionally first among non-stdlib
dependencies so its RED remains independently reproducible.
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

import m245_replica_core as replica


HERE = Path(__file__).resolve().parent
V2_NAME = "M245_FROZEN_MANIFEST_V2_20260810.json"
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
INNER_BASE_PANELS = (0.0, 0.25, 1.0, 2.5, 5.0, 8.0, 10.0, 16.0, math.inf)
QUADRATURE_ERROR_SEMANTICS = "heuristic_diagnostic_estimate_not_interval_certificate"
DIAGNOSTIC_DISPOSITION = "NO_ESTIMATOR_PROVIDER_DEPLOYMENT_SCORE_OR_SUBMISSION_CREDIT"

REPLICA_PUBLIC_CALLABLES = (
    "canonical_event",
    "canonical_json_bytes",
    "load_verified_v2",
    "decode_authoritative_array",
    "inner_panel_bounds",
    "unary_relu_mean",
    "replica_rbar_at_g",
    "conditional_factor_parameters",
    "antithetic_pair_average",
    "cache_scope_id",
    "replica_b_at_g",
    "replica_moments_from_components",
    "run_replica_event",
    "precision_gate",
    "quadrature_call_gate",
    "top_level_error_gate",
    "primary_replica_node_gate",
    "primary_replica_integrated_gates",
    "validate_replica_result",
)


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


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dummy_array_receipt(values: tuple[float, ...], shape: tuple[int, ...]) -> dict:
    raw = struct.pack("<" + "d" * len(values), *values)
    shape_json = json.dumps(list(shape), ensure_ascii=True, separators=(",", ":"))
    digest = hashlib.sha256(b"<f8\0" + shape_json.encode("utf-8") + b"\0" + raw).hexdigest()
    flat_hex = [float(value).hex() for value in values]
    flat_repr = [repr(float(value)) for value in values]
    if len(shape) == 1:
        hex_rows = [flat_hex]
        repr_rows = [flat_repr]
    else:
        width = shape[1]
        hex_rows = [flat_hex[i:i + width] for i in range(0, len(flat_hex), width)]
        repr_rows = [flat_repr[i:i + width] for i in range(0, len(flat_repr), width)]
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


def _dummy_event(rho: float = 0.0) -> dict:
    """Dummy conditional correlation with repeated coordinate independent."""

    covariance = (1.0, 0.0, 0.0, 0.0, 1.0, rho, 0.0, rho, 1.0)
    return {
        "event_id": f"DUMMY_REPLICA_RHO_{rho.hex()}_NOT_IN_FROZEN_CENSUS",
        "event": [0, 1, 2],
        "mu": _dummy_array_receipt((0.0, 0.2, -0.3), (3,)),
        "C": _dummy_array_receipt(covariance, (3, 3)),
        "no_redraw": True,
        "origin": "dummy_test_only",
    }


def _closed_form_dummy(rho: float) -> dict:
    if not (-1.0 < rho < 1.0) or rho == 0.0:
        raise AssertionError("rho must be nonzero and strictly inside (-1,1)")
    event = _dummy_event(rho)
    event["event_id"] = f"DUMMY_CLOSED_FORM_RHO_{rho.hex()}_NOT_IN_FROZEN_CENSUS"
    event["mu"] = _dummy_array_receipt((0.0, 0.0, 0.0), (3,))
    return event


def _varying_dummy_event() -> dict:
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


class _DummyQuadGateway:
    def __init__(self, mp_module: object) -> None:
        self.mp = mp_module
        self.request_count = 0
        self.requests: list[dict] = []

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
        self.requests.append(
            {
                "cache_scope_id": cache_scope_id,
                "call_role": call_role,
                "engine": engine,
                "panel_path": panel_path,
                "parent_request_index": parent_request_index,
                "precision_dps": precision_dps,
                "quantity": quantity,
            }
        )
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


class TestM245ReplicaAuthorityAPIAndFirewall(unittest.TestCase):
    def test_public_surface_and_frozen_constants_are_exact(self) -> None:
        self.assertTrue(issubclass(replica.M245ReplicaContractError, Exception))
        for name in REPLICA_PUBLIC_CALLABLES:
            with self.subTest(name=name):
                self.assertTrue(callable(getattr(replica, name, None)), name)
        self.assertEqual(tuple(replica.DEGREES), DEGREES)
        self.assertEqual(tuple(replica.PRECISIONS_DPS), PRECISIONS_DPS)
        self.assertEqual(tuple(replica.FIXED_B_NODES), FIXED_B_NODES)
        self.assertEqual(tuple(replica.INNER_BASE_PANELS), INNER_BASE_PANELS)
        self.assertEqual(replica.QUADRATURE_ERROR_SEMANTICS, QUADRATURE_ERROR_SEMANTICS)
        self.assertEqual(replica.DIAGNOSTIC_DISPOSITION, DIAGNOSTIC_DISPOSITION)
        self.assertEqual(replica.V2_SHA256, V2_SHA256)
        self.assertEqual(dict(replica.AUTHORITY_SHA256), AUTHORITY_SHA256)

    def test_replica_rehashes_and_validates_v2_independently(self) -> None:
        payload = replica.load_verified_v2(HERE / V2_NAME, V2_SHA256)
        self.assertEqual(_sha256(HERE / V2_NAME), V2_SHA256)
        self.assertEqual((HERE / V2_NAME).read_bytes(), _canonical_json_bytes(payload))
        self.assertEqual([row["event_id"] for row in payload["fixtures"]], [f"E{i:02d}" for i in range(8)])
        self.assertEqual(payload["scientific_quantities_evaluated"], [])
        self.assertFalse(payload["retry_or_redraw"])
        with self.assertRaises(replica.M245ReplicaContractError):
            replica.load_verified_v2(HERE / V2_NAME, "0" * 64)
        tampered = copy.deepcopy(payload)
        tampered["fixtures"][0]["event"] = [0, 2, 1]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "dummy_tampered_v2.json"
            path.write_bytes(_canonical_json_bytes(tampered))
            with self.assertRaises(replica.M245ReplicaContractError):
                replica.load_verified_v2(path, _sha256(path))

    def test_replica_binary64_decoder_is_independent_and_decimal_repr_is_non_authoritative(self) -> None:
        receipt = _dummy_array_receipt((0.1, -0.0, 1.5), (3,))
        decoded = tuple(replica.decode_authoritative_array(receipt))
        for observed, source in zip(decoded, (0.1, -0.0, 1.5)):
            numerator, denominator = source.as_integer_ratio()
            self.assertEqual(observed, replica.mp.mpf(numerator) / replica.mp.mpf(denominator))
        poisoned = copy.deepcopy(receipt)
        poisoned["repr_rows"] = [["-123", "-123", "-123"]]
        self.assertEqual(tuple(replica.decode_authoritative_array(poisoned)), decoded)

    def test_replica_binary64_decoder_refuses_any_authoritative_drift(self) -> None:
        receipt = _dummy_array_receipt((0.125, -0.5, 2.0), (3,))
        mutations = []
        for key, value in (("dtype", ">f8"), ("shape", [1, 3]), ("sha256", "f" * 64)):
            changed = copy.deepcopy(receipt)
            changed[key] = value
            mutations.append(changed)
        changed = copy.deepcopy(receipt)
        changed["hex_rows"][0][1] = "0x1.0p+12"
        mutations.append(changed)
        changed = copy.deepcopy(receipt)
        changed["raw_c_order_sha256"] = "0" * 64
        mutations.append(changed)
        for changed in mutations:
            with self.assertRaises(replica.M245ReplicaContractError):
                tuple(replica.decode_authoritative_array(changed))

    def test_replica_source_is_primary_free_old_lineage_free_and_offline(self) -> None:
        imported = _imports(Path(replica.__file__).resolve())
        forbidden_prefixes = (
            "m245_primary_core",
            "numpy",
            "scipy",
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

    def test_replica_contains_no_direct_or_aliased_mpmath_quad_call(self) -> None:
        path = Path(replica.__file__).resolve()
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


class TestM245ReplicaIndependentMath(unittest.TestCase):
    def test_canonical_event_is_independently_reimplemented(self) -> None:
        self.assertEqual(replica.canonical_event((0, 2, 1)), (0, 1, 2))
        self.assertEqual(replica.canonical_event((2, 1, 0)), (2, 0, 1))
        for invalid in ((0, 0, 1), (0, 1, 1), (False, 1, 2), (0.0, 1, 2), (3, 1, 2)):
            with self.subTest(invalid=invalid):
                with self.assertRaises(replica.M245ReplicaContractError):
                    replica.canonical_event(invalid)

    def test_inner_unary_panels_are_exact_and_not_event_kink_augmented(self) -> None:
        self.assertEqual(tuple(replica.inner_panel_bounds()), INNER_BASE_PANELS)
        self.assertEqual(len(tuple(replica.inner_panel_bounds())), 9)

    def test_unary_relu_mean_matches_exact_special_cases(self) -> None:
        inverse_root_two_pi = 1.0 / math.sqrt(2.0 * math.pi)
        self.assertAlmostEqual(float(replica.unary_relu_mean(0.0, 1.0)), inverse_root_two_pi, places=14)
        self.assertAlmostEqual(float(replica.unary_relu_mean(0.0, 2.5)), 2.5 * inverse_root_two_pi, places=14)
        for invalid_sigma in (0.0, -1.0, math.nan, math.inf):
            with self.subTest(invalid_sigma=invalid_sigma):
                with self.assertRaises(replica.M245ReplicaContractError):
                    replica.unary_relu_mean(0.0, invalid_sigma)

    def test_replica_rebuilds_relu_mean_and_rbar_without_primary_state(self) -> None:
        mu_i, sigma_i = 0.35, 1.7
        alpha = mu_i / sigma_i
        phi = math.exp(-0.5 * alpha * alpha) / math.sqrt(2.0 * math.pi)
        Phi = 0.5 * (1.0 + math.erf(alpha / math.sqrt(2.0)))
        expected_mean = sigma_i * (alpha * Phi + phi)
        observed_mean = replica.unary_relu_mean(mu_i, sigma_i)
        self.assertAlmostEqual(float(observed_mean), expected_mean, places=14)
        for g in (-8.0, -0.25, 0.0, 0.75, 5.0):
            expected_rbar = (
                max(mu_i + sigma_i * g, 0.0) - expected_mean
            ) ** 2 / sigma_i**2
            observed = replica.replica_rbar_at_g(mu_i, sigma_i, g)
            with self.subTest(g=g):
                self.assertAlmostEqual(float(observed), expected_rbar, places=13)
        self.assertAlmostEqual(
            float(replica.replica_rbar_at_g(2.0 * mu_i, 2.0 * sigma_i, 0.75)),
            float(replica.replica_rbar_at_g(mu_i, sigma_i, 0.75)),
            places=14,
        )

    def test_conditional_factorization_uses_sqrt_abs_rho_and_signed_second_loading(self) -> None:
        positive = replica.conditional_factor_parameters(_dummy_event(0.36))
        negative = replica.conditional_factor_parameters(_dummy_event(-0.36))
        zero = replica.conditional_factor_parameters(_dummy_event(0.0))
        for observed in (positive, negative):
            self.assertAlmostEqual(float(observed["ell"]), 0.6, places=14)
            self.assertAlmostEqual(float(observed["s"]), 0.8, places=14)
        self.assertEqual(positive["eta"], 1)
        self.assertEqual(negative["eta"], -1)
        self.assertEqual(zero["eta"], 0)
        self.assertEqual(float(zero["ell"]), 0.0)
        self.assertEqual(float(zero["s"]), 1.0)
        self.assertAlmostEqual(float(positive["rho_c"]), 0.36, places=14)
        self.assertAlmostEqual(float(negative["rho_c"]), -0.36, places=14)

    def test_replica_b_is_zero_for_dummy_independent_pair_at_every_frozen_node(self) -> None:
        dummy = _dummy_event(0.0)
        for dps in PRECISIONS_DPS:
            for g in FIXED_B_NODES:
                with self.subTest(dps=dps, g=g):
                    gateway = _DummyQuadGateway(replica.mp)
                    value, audit = replica.replica_b_at_g(
                        dummy, g, dps, quad_gateway=gateway
                    )
                    self.assertLessEqual(abs(float(value)), 2.0e-30)
                    self.assertGreater(gateway.request_count, 0)
                    self.assertTrue(audit["all_calls_pass"])
                    self.assertEqual(audit["error_semantics"], QUADRATURE_ERROR_SEMANTICS)
                    self.assertFalse(audit["interval_certified"])
                    self.assertEqual(audit["unary_panel_count"], 8)

    def test_replica_b_matches_nonzero_closed_form_for_both_signed_factorizations(self) -> None:
        for rho in (0.36, -0.36):
            dummy = _closed_form_dummy(rho)
            expected = _relu_covariance_closed_form(rho)
            factor = replica.conditional_factor_parameters(dummy)
            self.assertAlmostEqual(float(factor["ell"]), 0.6, places=14)
            self.assertAlmostEqual(float(factor["s"]), 0.8, places=14)
            self.assertEqual(factor["eta"], 1 if rho > 0 else -1)
            for dps in PRECISIONS_DPS:
                for g in (-2.5, 0.0, 2.5):
                    with self.subTest(rho=rho, dps=dps, g=g):
                        gateway = _DummyQuadGateway(replica.mp)
                        value, audit = replica.replica_b_at_g(
                            dummy, g, dps, quad_gateway=gateway
                        )
                        self.assertAlmostEqual(float(value), expected, places=12)
                        self.assertGreater(gateway.request_count, 0)
                        self.assertTrue(audit["all_calls_pass"])
                        self.assertEqual(audit["error_semantics"], QUADRATURE_ERROR_SEMANTICS)
                        self.assertFalse(audit["interval_certified"])
                        self.assertEqual(audit["unary_panel_count"], 8)

    def test_replica_moment_identity_keeps_same_and_sign_reversed_cross_distinct(self) -> None:
        result = replica.replica_moments_from_components(
            mu_rep=0.25,
            M_same=1.5,
            M_cross=-0.5,
        )
        self.assertEqual(result["mu_rep"], 0.25)
        self.assertEqual(result["M_same"], 1.5)
        self.assertEqual(result["M_cross"], -0.5)
        self.assertAlmostEqual(float(result["K_rep"]), 0.5 * (1.5 - 0.5) - 0.25**2, places=15)
        self.assertNotEqual(result["M_same"], result["M_cross"])

    def test_mu_rep_uses_node_level_antithetic_half_normal_factor_one_half(self) -> None:
        def rbar(g: float) -> float:
            return 1.0 + g * g

        def b_rep(g: float) -> float:
            return 1.0 + 0.3 * g / (1.0 + g * g)

        finite_nodes = INNER_BASE_PANELS[:-1]
        observed_nodes = []
        for t in finite_nodes:
            f_plus = rbar(t) * b_rep(t)
            f_minus = rbar(-t) * b_rep(-t)
            observed = replica.antithetic_pair_average(f_plus, f_minus)
            observed_nodes.append(float(observed))
            with self.subTest(t=t):
                self.assertAlmostEqual(float(observed), 0.5 * (f_plus + f_minus), places=15)
                self.assertAlmostEqual(float(observed), 1.0 + t * t, places=13)
                if t > 0:
                    self.assertNotEqual(f_plus, f_minus)
        self.assertEqual(len(observed_nodes), 8)
        self.assertAlmostEqual(
            float(replica.antithetic_pair_average(3.5, -0.5)),
            1.5,
            places=15,
        )
        # E_T[S(F)(T)] = 1 + E[T^2] = 2 = E_G[F(G)].
        self.assertEqual(1.0 + 1.0, 2.0)

    def test_run_replica_event_mu_uses_both_asymmetric_sign_branches_end_to_end(self) -> None:
        rho = 0.36
        dummy = _closed_form_dummy(rho)
        b_constant = _relu_covariance_closed_form(rho)
        lambda_relu = 1.0 / math.sqrt(2.0 * math.pi)
        expected_antithetic_mu = b_constant * (0.5 - lambda_relu**2)
        incorrect_plus_only_mu = b_constant * (1.0 - 3.0 * lambda_relu**2)
        self.assertGreater(
            abs(expected_antithetic_mu - incorrect_plus_only_mu),
            1.0e-3,
        )
        for dps in PRECISIONS_DPS:
            gateway = _DummyQuadGateway(replica.mp)
            scope = replica.cache_scope_id(
                shard_id=95,
                invocation_index=1,
                event_id=dummy["event_id"],
                engine="replica",
                precision_dps=dps,
            )
            result = replica.run_replica_event(
                dummy,
                dps,
                quad_gateway=gateway,
                cache_scope_id=scope,
            )
            with self.subTest(dps=dps):
                self.assertTrue(
                    all(
                        math.isclose(
                            float(value),
                            b_constant,
                            rel_tol=2.0e-10,
                            abs_tol=2.0e-12,
                        )
                        for value in result["b_rep_at_nodes"]
                    )
                )
                self.assertTrue(
                    math.isclose(
                        float(result["mu_rep"]),
                        expected_antithetic_mu,
                        rel_tol=2.0e-10,
                        abs_tol=2.0e-12,
                    ),
                    (result["mu_rep"], expected_antithetic_mu),
                )
                self.assertGreater(
                    abs(float(result["mu_rep"]) - incorrect_plus_only_mu),
                    1.0e-3,
                )
                self.assertEqual(
                    {request["cache_scope_id"] for request in gateway.requests},
                    {scope},
                )


class TestM245ReplicaGatesAndSchema(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.dummy = _varying_dummy_event()
        cls.gateways = {}
        cls.results = {}
        for dps in PRECISIONS_DPS:
            gateway = _DummyQuadGateway(replica.mp)
            scope = replica.cache_scope_id(
                shard_id=97,
                invocation_index=1,
                event_id=cls.dummy["event_id"],
                engine="replica",
                precision_dps=dps,
            )
            cls.gateways[dps] = gateway
            cls.results[dps] = replica.run_replica_event(
                cls.dummy,
                dps,
                quad_gateway=gateway,
                cache_scope_id=scope,
            )

    def test_replica_numeric_gates_share_exact_precision_and_error_thresholds(self) -> None:
        self.assertTrue(replica.precision_gate(0.0, 2.0e-12))
        self.assertFalse(replica.precision_gate(0.0, math.nextafter(2.0e-12, math.inf)))
        saved_eps = 8.0e-80
        self.assertTrue(replica.quadrature_call_gate(1.0e-80, saved_eps))
        self.assertFalse(replica.quadrature_call_gate(math.nextafter(1.0e-80, math.inf), saved_eps))
        self.assertTrue(replica.top_level_error_gate(2.0e-14, 0.0))
        self.assertFalse(replica.top_level_error_gate(math.inf, 1.0))

    def test_primary_replica_node_gate_uses_each_node_each_precision(self) -> None:
        self.assertTrue(replica.primary_replica_node_gate(1.0, 1.0 + 2.0e-10))
        just_over = math.nextafter(1.0 + 2.0e-10, math.inf)
        self.assertFalse(replica.primary_replica_node_gate(1.0, just_over))
        self.assertFalse(replica.primary_replica_node_gate(math.nan, 0.0))

    def test_integrated_replica_gates_use_frozen_mu_and_K_thresholds(self) -> None:
        exact = replica.primary_replica_integrated_gates(
            primary_mu=0.5,
            replica_mu=0.5,
            primary_K=2.0,
            replica_K=2.0,
        )
        self.assertTrue(exact["pass"])
        self.assertTrue(exact["mu_pass"])
        self.assertTrue(exact["K_pass"])
        self.assertFalse(replica.primary_replica_integrated_gates(0.0, 2.1e-9, 2.0, 2.0)["pass"])
        self.assertFalse(replica.primary_replica_integrated_gates(0.0, 0.0, 2.0, 2.0 + 1.1e-7)["pass"])

    def test_replica_result_is_one_event_one_precision_and_json_safe(self) -> None:
        required = {
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
        for dps, result in self.results.items():
            with self.subTest(dps=dps):
                self.assertEqual(set(result), required)
                self.assertEqual(result["artifact"], "M245_REPLICA_EVENT_PRECISION")
                self.assertEqual(result["schema"], "m245-replica-event-v1")
                self.assertEqual(result["event_id"], self.dummy["event_id"])
                self.assertEqual(result["precision_dps"], dps)
                self.assertEqual(len(result["fixed_b_nodes"]), 17)
                self.assertEqual(len(result["b_rep_at_nodes"]), 17)
                self.assertTrue(math.isfinite(float(result["mu_rep"])))
                self.assertTrue(math.isfinite(float(result["M_same"])))
                self.assertTrue(math.isfinite(float(result["M_cross"])))
                self.assertGreater(abs(float(result["M_same"])), 1.0e-30)
                self.assertGreater(abs(float(result["M_cross"])), 1.0e-30)
                self.assertAlmostEqual(
                    float(result["K_rep"]),
                    0.5 * (float(result["M_same"]) + float(result["M_cross"]))
                    - float(result["mu_rep"]) ** 2,
                    places=12,
                )
                self.assertGreater(float(result["K_rep"]), 0.0)
                self.assertTrue(result["quadrature_audit"]["all_calls_pass"])
                self.assertEqual(
                    result["quadrature_audit"]["error_semantics"],
                    QUADRATURE_ERROR_SEMANTICS,
                )
                self.assertFalse(result["quadrature_audit"]["interval_certified"])
                self.assertGreater(result["quadrature_audit"]["observed_call_count"], 0)
                self.assertFalse(result["firewall"]["network"])
                self.assertFalse(result["firewall"]["primary_import"])
                replica.validate_replica_result(result)
                _canonical_json_bytes(result)

    def test_cache_scopes_are_fresh_across_every_bound_dimension(self) -> None:
        scopes = {
            replica.cache_scope_id(
                shard_id=shard_id,
                invocation_index=invocation_index,
                event_id=event_id,
                engine=engine,
                precision_dps=dps,
            )
            for shard_id in (96, 97)
            for invocation_index in (1, 2)
            for event_id in ("DUMMY_REPLICA_SCOPE_A", "DUMMY_REPLICA_SCOPE_B")
            for engine in ("primary", "replica")
            for dps in PRECISIONS_DPS
        }
        self.assertEqual(len(scopes), 2 * 2 * 2 * 2 * 2)
        for dps, gateway in self.gateways.items():
            expected = replica.cache_scope_id(
                shard_id=97,
                invocation_index=1,
                event_id=self.dummy["event_id"],
                engine="replica",
                precision_dps=dps,
            )
            self.assertGreater(len(gateway.requests), 0)
            self.assertEqual(
                {request["cache_scope_id"] for request in gateway.requests},
                {expected},
            )
            self.assertEqual(
                {request["engine"] for request in gateway.requests},
                {"replica"},
            )
            self.assertEqual(
                {request["precision_dps"] for request in gateway.requests},
                {dps},
            )

    def test_replica_integrated_scalars_agree_between_80_and_100_dps(self) -> None:
        low, high = self.results[80], self.results[100]
        pairs = [
            (low["mu_rep"], high["mu_rep"]),
            (low["M_same"], high["M_same"]),
            (low["M_cross"], high["M_cross"]),
            (low["K_rep"], high["K_rep"]),
        ]
        pairs.extend(zip(low["b_rep_at_nodes"], high["b_rep_at_nodes"]))
        for index, (z80, z100) in enumerate(pairs):
            with self.subTest(index=index):
                self.assertTrue(replica.precision_gate(float(z80), float(z100)))

    def test_replica_validator_refuses_missing_node_and_nonfinite_scalar(self) -> None:
        result = self.results[80]
        missing = copy.deepcopy(result)
        missing["b_rep_at_nodes"].pop()
        with self.assertRaises(replica.M245ReplicaContractError):
            replica.validate_replica_result(missing)
        nonfinite = copy.deepcopy(result)
        nonfinite["K_rep"] = "nan"
        with self.assertRaises(replica.M245ReplicaContractError):
            replica.validate_replica_result(nonfinite)


if __name__ == "__main__":
    unittest.main()
