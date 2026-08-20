"""Frozen RED/G0A/G0B contract for M240's meter-safe finite-scan child."""

from __future__ import annotations

from dataclasses import replace
import ast
import hashlib
import importlib.util
import itertools
import math
from pathlib import Path
import struct
import sys
import unittest
from unittest import mock

import flopscope as flops
import numpy as np


HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
for _sibling in (
    "m179_background_archive_producer",
    "m221_batched_certified_distinct_atom",
    "m224_gauge_invariant_rho08_chart",
):
    _path = str(EXPERIMENTS / _sibling)
    if _path not in sys.path:
        sys.path.insert(0, _path)

import m179_jacobian_archive as m179  # noqa: E402
import m221_batched_certified_distinct_atom as m221  # noqa: E402
import m224_gauge_invariant_rho08_chart as m224  # noqa: E402


EXPECTED_COLUMNS = (
    "g",
    "repeated_mean",
    "repeated_sigma",
    "repeated_activation_mean",
    "pair_base_left",
    "pair_base_right",
    "pair_slope_left",
    "pair_slope_right",
    "pair_sigma_left",
    "pair_sigma_right",
    "pair_rho",
    "activation_mean_left",
    "activation_mean_right",
    "activation_vii",
    "activation_vjk",
    "activation_vij",
    "activation_vik",
    "tree",
    "marginal_sigma_left",
    "marginal_sigma_right",
)
RAW_PACKED_NAMES = EXPECTED_COLUMNS[:18]
WIDTHS = (3, 4, 5, 6, 7)
STATE_SEEDS = (238700003, 238700004, 238700005, 238700006, 238700007)
OUTER_G = (0.0, 0.25, -0.25, 1.0, -1.0, 2.5, -2.5)
TARGET_RECEIPT_DIGESTS = {
    221720001: "CF4A9464DE22B0BB58985D51B26C133C528FDFD58BC073C9ED4C654E8FE785D0",
    221720002: "0A77C775907EF12CB9DCD4EE88F9818442EA57B8B830A3958E922D92D2CAB1A9",
    221720003: "E871DD5C844D84CF2F2F3F7CAC0AE74F2DA33060659059CDA7EB41638D8C0ACC",
    221720004: "0198644F60AD8297E3D7CC4551473AD71C116C4AD1BAF1A5F1841B96AF9E50A0",
    221720005: "50AC56BEDDE4309630C9BC457DBE1920CB7611131B700CAEEB1904F34918B418",
}
TARGET_TAPE_DIGEST = "2012133C1CDA19C695B94F0E54A033DD3B1694AC2A009DADA9DADE68AA36FE3C"


def _load_m240():
    path = HERE / "m240_meter_safe_finite_scan.py"
    spec = importlib.util.spec_from_file_location("m240_candidate", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load M240 module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _readonly(value: np.ndarray) -> np.ndarray:
    value.flags.writeable = False
    return value


def _canonical_digest(fields: dict[str, np.ndarray], order: tuple[str, ...]) -> str:
    digest = hashlib.sha256()
    for name in order:
        value = np.asarray(fields[name])
        digest.update(name.encode("ascii") + b"\0")
        digest.update(value.dtype.str.encode("ascii") + b"\0")
        for extent in value.shape:
            digest.update(struct.pack("<q", int(extent)))
        digest.update(value.tobytes(order="C"))
    return digest.hexdigest().upper()


def _small_raw_case(width: int, seed: int, outer_g=OUTER_G):
    local = m221._m216.frozen_local_state(width, seed)
    owners = m221._m216.strict_physical_owners(width)
    rows = [(labels, float(g)) for labels in owners for g in outer_g]
    reference = m221._pack_rows(local, rows)
    jacobian, _, _ = m179.build_jacobian(local.mean, local.covariance)
    tape = {
        "a": _readonly(np.asarray(local.mean[None, :], dtype=np.float64).copy()),
        "C": _readonly(np.asarray(local.covariance[None, :, :], dtype=np.float64).copy()),
        "mu": _readonly(np.asarray(local.activation_mean[None, :], dtype=np.float64).copy()),
        "V": _readonly(np.asarray(local.activation_covariance[None, :, :], dtype=np.float64).copy()),
        "p": _readonly(np.asarray(jacobian.probability[None, :], dtype=np.float64).copy()),
        "r": _readonly(np.asarray(jacobian.mean_variance_derivative[None, :], dtype=np.float64).copy()),
    }
    receipt = {
        "layer": _readonly(np.ones(reference.size, dtype=np.int64)),
        "i": _readonly(np.asarray(reference.labels[:, 0], dtype=np.int64).copy()),
        "j": _readonly(np.asarray(reference.labels[:, 2], dtype=np.int64).copy()),
        "k": _readonly(np.asarray(reference.labels[:, 3], dtype=np.int64).copy()),
        "g": _readonly(np.asarray(reference.g, dtype=np.float64).copy()),
    }
    return local, reference, tape, receipt


def _issue(module, tape_values, receipt_values, *, epoch: int, generation: int):
    tape = module.StackedLayerTape.issue(
        tape_values,
        epoch=epoch,
        producer_generation=generation,
    )
    receipt = module.StrictEventReceipt.issue(
        receipt_values,
        layers=int(tape.a.shape[0]),
        width=int(tape.a.shape[1]),
        events_per_layer=int(receipt_values["g"].size // tape.a.shape[0]),
        epoch=epoch,
        producer_generation=generation,
    )
    return tape, receipt


def _run_pack(module, tape, receipt):
    packer = module.PersistentEventPacker(
        layers=tape.layers,
        width=tape.width,
        events_per_layer=receipt.events_per_layer,
    )
    budget = flops.BudgetContext(10**10, quiet=True, wall_time_limit_s=120.0)
    with budget:
        packed = packer.pack(tape, receipt)
    return packer, packed, budget


class _Poly:
    def __init__(self, terms=None):
        self.terms = {key: int(value) for key, value in (terms or {}).items() if value}

    @classmethod
    def variable(cls, name):
        return cls({(name,): 1})

    def __add__(self, other):
        other = other if isinstance(other, _Poly) else _Poly({(): other})
        terms = dict(self.terms)
        for key, value in other.terms.items():
            terms[key] = terms.get(key, 0) + value
            if not terms[key]:
                del terms[key]
        return _Poly(terms)

    __radd__ = __add__

    def __mul__(self, other):
        other = other if isinstance(other, _Poly) else _Poly({(): other})
        terms = {}
        for left, left_value in self.terms.items():
            for right, right_value in other.terms.items():
                key = tuple(sorted(left + right))
                terms[key] = terms.get(key, 0) + left_value * right_value
        return _Poly(terms)

    __rmul__ = __mul__


def _general_tree_polynomial():
    labels = ("i", "i", "j", "k")
    edge_names = {
        ("i", "i"): "A",
        ("i", "j"): "B",
        ("i", "k"): "E",
        ("j", "k"): "D",
    }

    def edge(left, right):
        return _Poly.variable(edge_names[tuple(sorted((left, right)))])

    eta2 = {name: _Poly.variable("e" + name) for name in ("i", "j", "k")}
    eta3 = {name: _Poly.variable("h" + name) for name in ("i", "j", "k")}
    total = _Poly()
    for path in itertools.permutations(range(4)):
        if path > path[::-1]:
            continue
        a, b, c, d = (labels[position] for position in path)
        total += edge(a, b) * edge(b, c) * edge(c, d) * eta2[b] * eta2[c]
    for centre in range(4):
        root = labels[centre]
        term = eta3[root]
        for position, other in enumerate(labels):
            if position != centre:
                term *= edge(root, other)
        total += term
    return total


def _reference_columns(local, reference):
    columns = {
        name: np.asarray(getattr(reference, name), dtype=np.float64)
        for name in RAW_PACKED_NAMES
    }
    columns["marginal_sigma_left"] = np.asarray(
        [local.sigma[int(labels[2])] for labels in reference.labels], dtype=np.float64
    )
    columns["marginal_sigma_right"] = np.asarray(
        [local.sigma[int(labels[3])] for labels in reference.labels], dtype=np.float64
    )
    return columns


def _packed_from_columns(reference, columns):
    return replace(
        reference,
        **{name: np.asarray(columns[name]) for name in RAW_PACKED_NAMES},
    )


def _target_tape_and_maps():
    layers, width = 31, 256
    inv_sqrt_two_pi = 1.0 / math.sqrt(2.0 * math.pi)
    inactive_mean = inv_sqrt_two_pi
    inactive_variance = 0.5 - 1.0 / (2.0 * math.pi)
    a = np.zeros((layers, width), dtype=np.float64)
    C = np.zeros((layers, width, width), dtype=np.float64)
    mu = np.full((layers, width), inactive_mean, dtype=np.float64)
    V = np.zeros((layers, width, width), dtype=np.float64)
    p = np.full((layers, width), 0.5, dtype=np.float64)
    r = np.full((layers, width), 0.5 * inv_sqrt_two_pi, dtype=np.float64)
    diagonal = np.arange(width)
    C[:, diagonal, diagonal] = 1.0
    V[:, diagonal, diagonal] = inactive_variance
    maps = []
    for layer in range(1, layers + 1):
        local = m221._m216.frozen_local_state(7, 221730000 + layer)
        mapping = np.sort(
            np.random.Generator(np.random.Philox(238730000 + layer)).permutation(width)[:7]
        )
        maps.append(mapping)
        slot = layer - 1
        a[slot, mapping] = local.mean
        C[slot][np.ix_(mapping, mapping)] = local.covariance
        mu[slot, mapping] = local.activation_mean
        V[slot][np.ix_(mapping, mapping)] = local.activation_covariance
        sigma = np.sqrt(np.diag(local.covariance))
        for local_index, target_index in enumerate(mapping):
            alpha = float(local.mean[local_index] / sigma[local_index])
            p[slot, target_index] = 0.5 * (
                1.0 + math.erf(alpha / math.sqrt(2.0))
            )
            r[slot, target_index] = (
                math.exp(-0.5 * alpha * alpha)
                * inv_sqrt_two_pi
                / (2.0 * sigma[local_index])
            )
    fields = {"a": a, "C": C, "mu": mu, "V": V, "p": p, "r": r}
    return fields, tuple(maps)


def _target_receipt(seed: int, maps):
    packed = m224.generated_native_batch(seed)
    layer = np.repeat(np.arange(1, 32, dtype=np.int64), 128)
    i = np.empty(packed.size, dtype=np.int64)
    j = np.empty(packed.size, dtype=np.int64)
    k = np.empty(packed.size, dtype=np.int64)
    for slot, labels in enumerate(packed.labels):
        mapping = maps[int(layer[slot]) - 1]
        i[slot] = mapping[int(labels[0])]
        j[slot] = mapping[int(labels[2])]
        k[slot] = mapping[int(labels[3])]
    return {
        "layer": layer,
        "i": i,
        "j": j,
        "k": k,
        "g": np.asarray(packed.g, dtype=np.float64).copy(),
    }


class M240AlgebraAndInterfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m238 = _load_m240()

    def test_production_source_has_no_generated_oracle_import(self):
        source_path = HERE / "m240_meter_safe_finite_scan.py"
        source = source_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
        for forbidden in (
            "m213_event_local_randomized_source211",
            "m221_batched_certified_distinct_atom",
            "m224_gauge_invariant_rho08_chart",
        ):
            self.assertNotIn(forbidden, imported)
            self.assertNotIn(f"import {forbidden}", source)
        self.assertNotIn("local_states", source)
        packer_node = next(
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "PersistentEventPacker"
        )
        billed_finite = []
        raw_numpy_finite = []
        for node in ast.walk(packer_node):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                continue
            owner = node.func.value
            if isinstance(owner, ast.Name) and owner.id == "fnp" and node.func.attr == "isfinite":
                billed_finite.append(node)
            if (
                isinstance(owner, ast.Name)
                and owner.id == "np"
                and node.func.attr in {"isfinite", "isinf", "isnan"}
            ):
                raw_numpy_finite.append(node)
        self.assertEqual(len(billed_finite), 3)
        self.assertEqual(raw_numpy_finite, [])

    def test_dependency_free_nine_monomial_census(self):
        variables = {
            name: _Poly.variable(name)
            for name in ("A", "B", "E", "D", "ei", "ej", "ek", "hi", "hj", "hk")
        }
        reduced = self.m238.tree_211_reduced(
            variables["A"], variables["B"], variables["E"], variables["D"],
            variables["ei"], variables["ej"], variables["ek"],
            variables["hi"], variables["hj"], variables["hk"],
        )
        general = _general_tree_polynomial()
        self.assertEqual(reduced.terms, general.terms)
        self.assertEqual(len(reduced.terms), 9)

    def test_all_twenty_columns_tree_and_m224_parity_on_frozen_grid(self):
        max_tree_ratio = 0.0
        for width, seed in zip(WIDTHS, STATE_SEEDS, strict=True):
            local, reference, tape_values, receipt_values = _small_raw_case(width, seed)
            tape, receipt = _issue(self.m238, tape_values, receipt_values, epoch=seed, generation=1)
            _, packed, _ = _run_pack(self.m238, tape, receipt)
            expected = _reference_columns(local, reference)
            self.assertEqual(tuple(packed.columns), EXPECTED_COLUMNS)
            self.assertEqual(packed.event_count, reference.size)
            for name in EXPECTED_COLUMNS:
                observed = np.asarray(packed.columns[name])
                self.assertEqual(observed.dtype, np.dtype(np.float64))
                self.assertFalse(observed.flags.writeable)
                if name == "tree":
                    ratio = np.max(
                        np.abs(observed - expected[name]) / (1.0 + np.abs(expected[name]))
                    )
                    max_tree_ratio = max(max_tree_ratio, float(ratio))
                    self.assertLessEqual(float(ratio), 5.0e-13)
                else:
                    np.testing.assert_allclose(
                        observed, expected[name], rtol=2.0e-13, atol=2.0e-13
                    )
            expected_atom = m224.evaluate_numpy(reference)
            observed_atom = m224.evaluate_numpy(_packed_from_columns(reference, packed.columns))
            np.testing.assert_array_equal(observed_atom.chart_ok, expected_atom.chart_ok)
            np.testing.assert_array_less(
                np.abs(observed_atom.value - expected_atom.value), expected_atom.radius
            )
            np.testing.assert_array_less(
                np.abs(observed_atom.radius - expected_atom.radius), expected_atom.radius
            )
        self.assertLessEqual(max_tree_ratio, 5.0e-13)

    def test_positive_gauge_action_matches_every_frozen_column_degree(self):
        _, _, baseline_values, receipt_values = _small_raw_case(7, 238700007, (0.25,))
        base_tape, base_receipt = _issue(
            self.m238, baseline_values, receipt_values, epoch=1, generation=1
        )
        _, baseline, _ = _run_pack(self.m238, base_tape, base_receipt)
        dq = np.linspace(0.71, 1.39, 7, dtype=np.float64)
        gauged_values = {
            "a": baseline_values["a"] * dq[None, :],
            "C": baseline_values["C"] * dq[None, :, None] * dq[None, None, :],
            "mu": baseline_values["mu"] * dq[None, :],
            "V": baseline_values["V"] * dq[None, :, None] * dq[None, None, :],
            "p": baseline_values["p"].copy(),
            "r": baseline_values["r"] / dq[None, :],
        }
        for value in gauged_values.values():
            _readonly(value)
        gauged_receipt = {name: _readonly(np.asarray(value).copy()) for name, value in receipt_values.items()}
        tape, receipt = _issue(self.m238, gauged_values, gauged_receipt, epoch=2, generation=2)
        _, gauged, _ = _run_pack(self.m238, tape, receipt)
        ii, jj, kk = receipt_values["i"], receipt_values["j"], receipt_values["k"]
        di, dj, dk = dq[ii], dq[jj], dq[kk]
        degrees = {
            "g": np.ones_like(di), "pair_rho": np.ones_like(di),
            "repeated_mean": di, "repeated_sigma": di,
            "repeated_activation_mean": di,
            "pair_base_left": dj, "pair_slope_left": dj,
            "pair_sigma_left": dj, "activation_mean_left": dj,
            "marginal_sigma_left": dj,
            "pair_base_right": dk, "pair_slope_right": dk,
            "pair_sigma_right": dk, "activation_mean_right": dk,
            "marginal_sigma_right": dk,
            "activation_vii": di * di, "activation_vjk": dj * dk,
            "activation_vij": di * dj, "activation_vik": di * dk,
            "tree": di * di * dj * dk,
        }
        for name in EXPECTED_COLUMNS:
            np.testing.assert_allclose(
                gauged.columns[name], baseline.columns[name] * degrees[name],
                rtol=8.0e-13, atol=8.0e-13,
            )

    def test_co_permutation_changes_only_coordinate_names(self):
        local, _, tape_values, _ = _small_raw_case(5, 238700005, (0.25,))
        labels = (0, 0, 1, 2)
        reference = m221._pack_rows(local, ((labels, 0.25),))
        receipt_values = {
            "layer": _readonly(np.ones(1, dtype=np.int64)),
            "i": _readonly(np.asarray((0,), dtype=np.int64)),
            "j": _readonly(np.asarray((1,), dtype=np.int64)),
            "k": _readonly(np.asarray((2,), dtype=np.int64)),
            "g": _readonly(np.asarray((0.25,), dtype=np.float64)),
        }
        base_tape, base_receipt = _issue(self.m238, tape_values, receipt_values, epoch=3, generation=1)
        _, baseline, _ = _run_pack(self.m238, base_tape, base_receipt)
        new_to_old = np.asarray((3, 1, 4, 0, 2), dtype=np.int64)
        old_to_new = np.argsort(new_to_old)
        permuted_values = {
            "a": tape_values["a"][:, new_to_old].copy(),
            "C": tape_values["C"][:, new_to_old][:, :, new_to_old].copy(),
            "mu": tape_values["mu"][:, new_to_old].copy(),
            "V": tape_values["V"][:, new_to_old][:, :, new_to_old].copy(),
            "p": tape_values["p"][:, new_to_old].copy(),
            "r": tape_values["r"][:, new_to_old].copy(),
        }
        for value in permuted_values.values():
            _readonly(value)
        permuted_receipt = {
            "layer": _readonly(np.ones(1, dtype=np.int64)),
            "i": _readonly(np.asarray((old_to_new[0],), dtype=np.int64)),
            "j": _readonly(np.asarray((old_to_new[1],), dtype=np.int64)),
            "k": _readonly(np.asarray((old_to_new[2],), dtype=np.int64)),
            "g": _readonly(np.asarray((0.25,), dtype=np.float64)),
        }
        self.assertLess(int(permuted_receipt["j"][0]), int(permuted_receipt["k"][0]))
        tape, receipt = _issue(self.m238, permuted_values, permuted_receipt, epoch=4, generation=2)
        _, observed, _ = _run_pack(self.m238, tape, receipt)
        for name in EXPECTED_COLUMNS:
            np.testing.assert_allclose(observed.columns[name], baseline.columns[name], rtol=2e-13, atol=2e-13)

    def test_hostile_binders_domain_zero_write_and_one_use_lifetime(self):
        _, _, tape_values, receipt_values = _small_raw_case(3, 238700003, (0.25,))
        writable = {name: np.asarray(value).copy() for name, value in tape_values.items()}
        with self.assertRaisesRegex(self.m238.M238Refusal, "READ_ONLY"):
            self.m238.StackedLayerTape.issue(writable, epoch=1, producer_generation=1)

        receipt_order = ("layer", "i", "j", "k", "g")
        original_digest = _canonical_digest(receipt_values, receipt_order)
        original_values = {
            name: np.asarray(value).copy() for name, value in receipt_values.items()
        }
        j_bad = np.array(receipt_values["j"], dtype=np.int64, order="C", copy=True)
        k_bad = np.array(receipt_values["k"], dtype=np.int64, order="C", copy=True)
        self.assertIs(type(j_bad), np.ndarray)
        self.assertIs(type(k_bad), np.ndarray)
        self.assertTrue(j_bad.flags.owndata)
        self.assertTrue(k_bad.flags.owndata)
        self.assertFalse(np.shares_memory(j_bad, receipt_values["j"]))
        self.assertFalse(np.shares_memory(k_bad, receipt_values["k"]))
        self.assertFalse(np.shares_memory(j_bad, k_bad))
        old_j0, old_k0 = int(j_bad[0]), int(k_bad[0])
        j_bad[0], k_bad[0] = old_k0, old_j0
        j_bad.flags.writeable = False
        k_bad.flags.writeable = False
        self.assertFalse(j_bad.flags.writeable)
        self.assertFalse(k_bad.flags.writeable)
        self.assertEqual(int(j_bad[0]), old_k0)
        self.assertEqual(int(k_bad[0]), old_j0)
        bad_receipt = {
            name: _readonly(np.asarray(value).copy())
            for name, value in receipt_values.items()
            if name not in {"j", "k"}
        }
        bad_receipt["j"] = j_bad
        bad_receipt["k"] = k_bad
        bad_receipt = {name: bad_receipt[name] for name in receipt_order}
        for name in receipt_order:
            np.testing.assert_array_equal(receipt_values[name], original_values[name])
        self.assertEqual(_canonical_digest(receipt_values, receipt_order), original_digest)
        malformed_packer = self.m238.PersistentEventPacker(
            1, 3, int(bad_receipt["g"].size)
        )
        malformed_before = malformed_packer.output_digest()
        with self.assertRaisesRegex(self.m238.M238Refusal, "CANONICAL"):
            self.m238.StrictEventReceipt.issue(
                bad_receipt, layers=1, width=3, events_per_layer=bad_receipt["g"].size,
                epoch=1, producer_generation=1,
            )
        self.assertEqual(malformed_packer.output_digest(), malformed_before)
        for name in receipt_order:
            np.testing.assert_array_equal(receipt_values[name], original_values[name])
        self.assertEqual(_canonical_digest(receipt_values, receipt_order), original_digest)

        tape, receipt = _issue(self.m238, tape_values, receipt_values, epoch=11, generation=7)
        foreign_receipt = self.m238.StrictEventReceipt.issue(
            receipt_values, layers=1, width=3, events_per_layer=receipt_values["g"].size,
            epoch=12, producer_generation=7,
        )
        packer = self.m238.PersistentEventPacker(1, 3, receipt.events_per_layer)
        before = packer.output_digest()
        with self.assertRaisesRegex(self.m238.M238Refusal, "EPOCH"):
            with flops.BudgetContext(10**9, quiet=True, wall_time_limit_s=120.0):
                packer.pack(tape, foreign_receipt)
        self.assertEqual(packer.output_digest(), before)

        tape, receipt = _issue(self.m238, tape_values, receipt_values, epoch=13, generation=8)
        original_a = tape.a
        copied_a = _readonly(np.asarray(tape.a).copy())
        object.__setattr__(tape, "a", copied_a)
        packer = self.m238.PersistentEventPacker(1, 3, receipt.events_per_layer)
        before = packer.output_digest()
        with self.assertRaisesRegex(self.m238.M238Refusal, "OWNER"):
            with flops.BudgetContext(10**9, quiet=True, wall_time_limit_s=120.0):
                packer.pack(tape, receipt)
        self.assertEqual(packer.output_digest(), before)
        object.__setattr__(tape, "a", original_a)

        tape, receipt = _issue(self.m238, tape_values, receipt_values, epoch=14, generation=9)
        tape.p.flags.writeable = True
        tape.p[0, int(receipt.i[0])] = 0.0
        tape.p.flags.writeable = False
        packer = self.m238.PersistentEventPacker(1, 3, receipt.events_per_layer)
        before = packer.output_digest()
        with self.assertRaisesRegex(self.m238.M238Refusal, "INTERIOR"):
            with flops.BudgetContext(10**9, quiet=True, wall_time_limit_s=120.0):
                packer.pack(tape, receipt)
        self.assertEqual(packer.output_digest(), before)

        tape, receipt = _issue(self.m238, tape_values, receipt_values, epoch=15, generation=10)
        packer = self.m238.PersistentEventPacker(1, 3, receipt.events_per_layer)
        view_pairs = (
            (packer._raw_finite_base, packer._raw_finite),
            (packer._derived_finite_base, packer._derived_finite),
            (packer._output_finite_base, packer._output_finite),
        )

        def view_state(value):
            return (
                id(value), int(value.__array_interface__["data"][0]),
                tuple(value.shape), tuple(value.strides), value.dtype.str,
                bool(value.flags.owndata), type(value),
            )

        prebound_state = tuple(view_state(base) for base, _ in view_pairs)
        for base, owner in view_pairs:
            self.assertIs(type(base), np.ndarray)
            self.assertEqual(base.dtype, np.dtype(np.bool_))
            self.assertFalse(base.flags.owndata)
            self.assertTrue(np.shares_memory(base, packer._bool_slab))
            self.assertTrue(np.shares_memory(base, owner))
            self.assertEqual(
                int(base.__array_interface__["data"][0]),
                int(owner.__array_interface__["data"][0]),
            )
            self.assertEqual(base.shape, owner.shape)
            self.assertEqual(base.strides, owner.strides)

        observed_finite_calls = []
        original_isfinite = self.m238.fnp.isfinite

        def metered_isfinite(value, *args, **kwargs):
            observed_finite_calls.append((value, kwargs.get("out")))
            return original_isfinite(value, *args, **kwargs)

        budget = flops.BudgetContext(10**10, quiet=True, wall_time_limit_s=120.0)
        with mock.patch.object(self.m238.fnp, "isfinite", new=metered_isfinite):
            with budget:
                packed = packer.pack(tape, receipt)
        self.assertEqual(len(observed_finite_calls), 3)
        self.assertEqual(
            tuple(value.shape for value, _ in observed_finite_calls),
            ((24, receipt.event_count), (37, receipt.event_count), (19, receipt.event_count)),
        )
        for (_, observed_out), (expected_out, _) in zip(
            observed_finite_calls, view_pairs, strict=True
        ):
            self.assertIs(observed_out, expected_out)
            self.assertIs(type(observed_out), np.ndarray)
        operations = budget.summary_dict().get("operations", {})
        self.assertEqual(int(operations["isfinite"]["calls"]), 3)
        self.assertEqual(tuple(view_state(base) for base, _ in view_pairs), prebound_state)
        self.assertTrue(all(packer.completion_bitmap))
        self.assertEqual(tuple(packed.columns), EXPECTED_COLUMNS)
        with self.assertRaisesRegex(self.m238.M238Refusal, "CONSUM"):
            with flops.BudgetContext(10**9, quiet=True, wall_time_limit_s=120.0):
                packer.pack(tape, receipt)

    def test_target_digests_non_degeneracy_and_static_flopscope_contract(self):
        tape_values, maps = _target_tape_and_maps()
        self.assertEqual(
            _canonical_digest(tape_values, ("a", "C", "mu", "V", "p", "r")),
            TARGET_TAPE_DIGEST,
        )
        receipts = {seed: _target_receipt(seed, maps) for seed in TARGET_RECEIPT_DIGESTS}
        for seed, expected_digest in TARGET_RECEIPT_DIGESTS.items():
            self.assertEqual(
                _canonical_digest(receipts[seed], ("layer", "i", "j", "k", "g")),
                expected_digest,
            )
        first = receipts[221720001]
        selected = []
        for layer, i, j, k in zip(first["layer"], first["i"], first["j"], first["k"], strict=True):
            matrix = tape_values["V"][int(layer) - 1]
            selected.extend((abs(matrix[int(i), int(j)]), abs(matrix[int(i), int(k)]), abs(matrix[int(j), int(k)])))
        self.assertEqual(sum(value == 0.0 for value in selected), 0)
        self.assertEqual(min(selected), 2.9276288362745095e-06)

        for value in tape_values.values():
            _readonly(value)
        for value in first.values():
            _readonly(value)
        tape, receipt = _issue(self.m238, tape_values, first, epoch=238, generation=1)
        packer = self.m238.PersistentEventPacker(31, 256, 128)
        report = self.m238.run_billed_pack(packer, tape, receipt)
        self.assertIsNone(report["failure"], report)
        self.assertLessEqual(report["billed_flops"], 4_000_000)
        self.assertLessEqual(report["operation_calls"], 192)
        self.assertLessEqual(report["allocation"]["owned_bytes"], 4 * 1024 * 1024)
        for forbidden in ("empty", "reshape", "concatenate", "sort"):
            self.assertNotIn(forbidden, report["operations"])
        self.assertEqual(tuple(report["packed"].columns), EXPECTED_COLUMNS)
        self.assertTrue(all(report["completion_bitmap"]))
        self.assertTrue(report["g_aliases_receipt"])
        self.assertTrue(report["all_columns_float64_read_only"])
        self.assertTrue(report["owner_receipts_stable"])
        self.assertTrue(report["finite"])


if __name__ == "__main__":
    unittest.main()
