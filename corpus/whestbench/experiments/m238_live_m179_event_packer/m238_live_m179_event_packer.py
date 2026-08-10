"""M238: metered live M179 tape to M226 twenty-column event packer.

This module owns only the packing seam.  It does not construct the layer tape,
issue events, evaluate the downstream atom, or expose response/variance work.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from types import MappingProxyType
from typing import Mapping

import flopscope as flops
import flopscope.numpy as fnp
import numpy as np


MUTATION = "M238"
TAPE_NAMES = ("a", "C", "mu", "V", "p", "r")
RECEIPT_NAMES = ("layer", "i", "j", "k", "g")
COLUMN_NAMES = (
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
DERIVED_COLUMN_NAMES = COLUMN_NAMES[1:]
TREE_RELATIVE_ABSOLUTE_LIMIT = 5.0e-13
PROBABILITY_MIN = 1.0e-12
ABS_RHO_MAX = 0.08
ABS_STANDARD_MAX = 0.8
SCALE_RATIO_MIN = 0.8
SCALE_RATIO_MAX = 1.2
REPEATED_STANDARD_MAX = 9.0
FLOP_CEILING = 4_000_000
CALL_CEILING = 192
OWNED_BYTE_CEILING = 4 * 1024 * 1024


class M238Refusal(RuntimeError):
    """Typed fail-closed M238 domain, provenance, or lifetime refusal."""


def _pointer(value: np.ndarray) -> int:
    return int(value.__array_interface__["data"][0])


def _array_receipt(value: np.ndarray) -> tuple[object, ...]:
    return (
        id(value),
        _pointer(value),
        int(value.nbytes),
        tuple(int(item) for item in value.shape),
        tuple(int(item) for item in value.strides),
        value.dtype.str,
        bool(value.flags.c_contiguous),
        bool(value.flags.writeable),
    )


def _require_exact_mapping(values: Mapping[str, np.ndarray], names: tuple[str, ...], kind: str) -> None:
    if tuple(values.keys()) != names and set(values.keys()) != set(names):
        raise M238Refusal(f"{kind}_EXACT_NAME_SET")
    if len(values) != len(names):
        raise M238Refusal(f"{kind}_EXACT_NAME_SET")


def _require_owner(value: object, dtype: np.dtype, shape: tuple[int, ...], name: str) -> np.ndarray:
    if not isinstance(value, np.ndarray):
        raise M238Refusal(f"{name}_NDARRAY_OWNER")
    if value.dtype != dtype:
        raise M238Refusal(f"{name}_DTYPE")
    if value.shape != shape:
        raise M238Refusal(f"{name}_SHAPE")
    if not value.flags.c_contiguous:
        raise M238Refusal(f"{name}_C_CONTIGUOUS")
    if value.flags.writeable:
        raise M238Refusal(f"{name}_READ_ONLY")
    return value


class StackedLayerTape:
    """Identity-bound immutable same-layer `(a,C,mu,V,p,r)` owner tape."""

    @classmethod
    def issue(
        cls,
        owners: Mapping[str, np.ndarray],
        *,
        epoch: int,
        producer_generation: int,
    ) -> "StackedLayerTape":
        _require_exact_mapping(owners, TAPE_NAMES, "TAPE")
        a = owners["a"]
        if not isinstance(a, np.ndarray) or a.ndim != 2:
            raise M238Refusal("a_SHAPE")
        layers, width = (int(item) for item in a.shape)
        if layers <= 0 or width <= 0:
            raise M238Refusal("TAPE_NONPOSITIVE_SHAPE")
        shapes = {
            "a": (layers, width),
            "C": (layers, width, width),
            "mu": (layers, width),
            "V": (layers, width, width),
            "p": (layers, width),
            "r": (layers, width),
        }
        checked = {
            name: _require_owner(owners[name], np.dtype(np.float64), shapes[name], name)
            for name in TAPE_NAMES
        }
        if not all(np.all(np.isfinite(value)) for value in checked.values()):
            raise M238Refusal("TAPE_NONFINITE")
        if not np.array_equal(checked["C"], np.swapaxes(checked["C"], 1, 2)):
            raise M238Refusal("C_NOT_BITWISE_SYMMETRIC")
        if not np.array_equal(checked["V"], np.swapaxes(checked["V"], 1, 2)):
            raise M238Refusal("V_NOT_BITWISE_SYMMETRIC")
        return cls(checked, layers, width, int(epoch), int(producer_generation))

    def __init__(self, owners, layers, width, epoch, producer_generation):
        for name in TAPE_NAMES:
            object.__setattr__(self, name, owners[name])
        self.layers = int(layers)
        self.width = int(width)
        self.epoch = int(epoch)
        self.producer_generation = int(producer_generation)
        self._receipts = {name: _array_receipt(owners[name]) for name in TAPE_NAMES}
        self._consumed = False

    def verify_live(self) -> None:
        for name in TAPE_NAMES:
            value = getattr(self, name)
            if not isinstance(value, np.ndarray) or _array_receipt(value) != self._receipts[name]:
                raise M238Refusal(f"TAPE_OWNER_SUBSTITUTION_{name}")


class StrictEventReceipt:
    """Immutable canonical strict event plan with exact layer-block ownership."""

    @classmethod
    def issue(
        cls,
        owners: Mapping[str, np.ndarray],
        *,
        layers: int,
        width: int,
        events_per_layer: int,
        epoch: int,
        producer_generation: int,
    ) -> "StrictEventReceipt":
        _require_exact_mapping(owners, RECEIPT_NAMES, "RECEIPT")
        layers = int(layers)
        width = int(width)
        events_per_layer = int(events_per_layer)
        if layers <= 0 or width < 3 or events_per_layer <= 0:
            raise M238Refusal("RECEIPT_NONPOSITIVE_SHAPE")
        count = layers * events_per_layer
        checked = {
            "layer": _require_owner(owners["layer"], np.dtype(np.int64), (count,), "layer"),
            "i": _require_owner(owners["i"], np.dtype(np.int64), (count,), "i"),
            "j": _require_owner(owners["j"], np.dtype(np.int64), (count,), "j"),
            "k": _require_owner(owners["k"], np.dtype(np.int64), (count,), "k"),
            "g": _require_owner(owners["g"], np.dtype(np.float64), (count,), "g"),
        }
        expected_layers = np.repeat(np.arange(1, layers + 1, dtype=np.int64), events_per_layer)
        if not np.array_equal(checked["layer"], expected_layers):
            raise M238Refusal("RECEIPT_LAYER_SLICE_MISSING_OVERLAPPING_OR_REORDERED")
        i, j, k = checked["i"], checked["j"], checked["k"]
        if (
            np.any(i < 0) or np.any(i >= width)
            or np.any(j < 0) or np.any(j >= width)
            or np.any(k < 0) or np.any(k >= width)
        ):
            raise M238Refusal("RECEIPT_LABEL_RANGE")
        if np.any(i == j) or np.any(i == k) or np.any(j >= k):
            raise M238Refusal("RECEIPT_CANONICAL_STRICT_211")
        if not np.all(np.isfinite(checked["g"])):
            raise M238Refusal("RECEIPT_G_NONFINITE")
        return cls(
            checked, layers, width, events_per_layer, int(epoch),
            int(producer_generation),
        )

    def __init__(self, owners, layers, width, events_per_layer, epoch, producer_generation):
        for name in RECEIPT_NAMES:
            object.__setattr__(self, name, owners[name])
        self.layers = int(layers)
        self.width = int(width)
        self.events_per_layer = int(events_per_layer)
        self.event_count = self.layers * self.events_per_layer
        self.epoch = int(epoch)
        self.producer_generation = int(producer_generation)
        self._receipts = {name: _array_receipt(owners[name]) for name in RECEIPT_NAMES}
        self._consumed = False

    def verify_live(self) -> None:
        for name in RECEIPT_NAMES:
            value = getattr(self, name)
            if not isinstance(value, np.ndarray) or _array_receipt(value) != self._receipts[name]:
                raise M238Refusal(f"RECEIPT_OWNER_SUBSTITUTION_{name}")


@dataclass(frozen=True)
class PackedColumns:
    columns: Mapping[str, np.ndarray]
    event_count: int


def tree_211_reduced(A, B, E, D, ei, ej, ek, hi, hj, hk):
    """Nine-monomial exact reduction of M213's `(i,i,j,k)` tree."""

    return (
        2 * B * E * (A * (ei * ei + hi) + D * ej * ek)
        + 2 * ei * (A * D + B * E) * (ej * B + ek * E)
        + D * (hj * B * B + hk * E * E)
    )


_RAW_NAMES = (
    "ai", "aj", "ak", "mui", "muj", "muk",
    "cii", "cjj", "ckk", "cij", "cik", "cjk",
    "vii", "vjj", "vkk", "vij", "vik", "vjk",
    "pi", "pj", "pk", "ri", "rj", "rk",
)
_WORK_NAMES = (
    "si", "margj", "margk", "slopej", "slopek", "varj", "vark",
    "sj", "sk", "ccond", "rho", "schur",
    "eta2i", "eta2j", "eta2k", "eta3i", "eta3j", "eta3k",
    "tree", "t0", "t1", "t2",
    "alpha_j_plus", "alpha_j_minus", "alpha_k_plus", "alpha_k_minus",
    "t_j_plus", "t_j_minus", "t_k_plus", "t_k_minus",
    "rep_plus", "rep_minus", "q_rho", "signed", "denom",
    "scalej", "scalek",
)
_INT_NAMES = (
    "layer0", "vector_base", "idx_i", "idx_j", "idx_k",
    "matrix_base", "row_i", "row_j", "row_k", "matrix_index",
)


class PersistentEventPacker:
    """Setup-owned vector packer; one successful consume is permitted."""

    def __init__(self, layers: int, width: int, events_per_layer: int):
        self.layers = int(layers)
        self.width = int(width)
        self.events_per_layer = int(events_per_layer)
        if self.layers <= 0 or self.width < 3 or self.events_per_layer <= 0:
            raise ValueError("positive M238 dimensions required")
        self.event_count = self.layers * self.events_per_layer
        n = self.event_count
        float_planes = len(DERIVED_COLUMN_NAMES) + len(_RAW_NAMES) + len(_WORK_NAMES)
        bool_planes = len(_RAW_NAMES) + 20
        self._float_slab = fnp.empty(float_planes * n, dtype=fnp.float64)
        self._int_slab = fnp.empty(len(_INT_NAMES) * n, dtype=fnp.int64)
        self._bool_slab = fnp.empty(bool_planes * n, dtype=fnp.bool_)
        self._completion = np.zeros(self.layers, dtype=np.bool_)

        cursor = 0

        def take_float(rows):
            nonlocal cursor
            start = cursor
            cursor += rows * n
            return self._float_slab[start:cursor].reshape((rows, n))

        self._output_block = take_float(len(DERIVED_COLUMN_NAMES))
        self._raw_block = take_float(len(_RAW_NAMES))
        self._work_block = take_float(len(_WORK_NAMES))
        if cursor != self._float_slab.size:
            raise RuntimeError("M238 float slab ledger mismatch")
        self._outputs = {
            name: self._output_block[index]
            for index, name in enumerate(DERIVED_COLUMN_NAMES)
        }
        self._raw = {name: self._raw_block[index] for index, name in enumerate(_RAW_NAMES)}
        self._work = {name: self._work_block[index] for index, name in enumerate(_WORK_NAMES)}
        self._int_block = self._int_slab.reshape((len(_INT_NAMES), n))
        self._ints = {name: self._int_block[index] for index, name in enumerate(_INT_NAMES)}
        self._bool_block = self._bool_slab.reshape((bool_planes, n))
        self._raw_finite = self._bool_block[: len(_RAW_NAMES)]
        self._conditions = self._bool_block[len(_RAW_NAMES) :]
        self._consumed = False
        self._owner_receipts_stable = False
        self._last_columns = None

    @property
    def completion_bitmap(self) -> tuple[bool, ...]:
        return tuple(bool(value) for value in self._completion)

    def allocation_ledger(self) -> dict[str, int]:
        owned = (
            int(self._float_slab.nbytes)
            + int(self._int_slab.nbytes)
            + int(self._bool_slab.nbytes)
            + int(self._completion.nbytes)
        )
        return {
            "float_bytes": int(self._float_slab.nbytes),
            "int_bytes": int(self._int_slab.nbytes),
            "bool_bytes": int(self._bool_slab.nbytes),
            "completion_bytes": int(self._completion.nbytes),
            "owned_bytes": owned,
            "setup_empty_calls": 3,
        }

    def output_digest(self) -> str:
        return hashlib.sha256(self._output_block.tobytes(order="C")).hexdigest()

    def _verify_binding(self, tape: StackedLayerTape, receipt: StrictEventReceipt) -> None:
        if self._consumed or tape._consumed or receipt._consumed:
            raise M238Refusal("DUPLICATE_CONSUME")
        if (
            tape.layers != self.layers or receipt.layers != self.layers
            or tape.width != self.width or receipt.width != self.width
            or receipt.events_per_layer != self.events_per_layer
        ):
            raise M238Refusal("SHAPE_OR_SLICE_BINDING")
        if tape.epoch != receipt.epoch:
            raise M238Refusal("EPOCH_SUBSTITUTION")
        if tape.producer_generation != receipt.producer_generation:
            raise M238Refusal("GENERATION_SUBSTITUTION")
        tape.verify_live()
        receipt.verify_live()

    def _form_indices(self, receipt: StrictEventReceipt) -> None:
        q = self._ints
        fnp.subtract(receipt.layer, np.int64(1), out=q["layer0"])
        fnp.multiply(q["layer0"], np.int64(self.width), out=q["vector_base"])
        fnp.add(q["vector_base"], receipt.i, out=q["idx_i"])
        fnp.add(q["vector_base"], receipt.j, out=q["idx_j"])
        fnp.add(q["vector_base"], receipt.k, out=q["idx_k"])
        fnp.multiply(
            q["layer0"], np.int64(self.width * self.width), out=q["matrix_base"]
        )
        fnp.multiply(receipt.i, np.int64(self.width), out=q["row_i"])
        fnp.add(q["row_i"], q["matrix_base"], out=q["row_i"])
        fnp.multiply(receipt.j, np.int64(self.width), out=q["row_j"])
        fnp.add(q["row_j"], q["matrix_base"], out=q["row_j"])
        fnp.multiply(receipt.k, np.int64(self.width), out=q["row_k"])
        fnp.add(q["row_k"], q["matrix_base"], out=q["row_k"])

    def _gather(self, tape: StackedLayerTape) -> None:
        q, x = self._ints, self._raw
        for owner, names in (
            (tape.a, ((q["idx_i"], "ai"), (q["idx_j"], "aj"), (q["idx_k"], "ak"))),
            (tape.mu, ((q["idx_i"], "mui"), (q["idx_j"], "muj"), (q["idx_k"], "muk"))),
            (tape.p, ((q["idx_i"], "pi"), (q["idx_j"], "pj"), (q["idx_k"], "pk"))),
            (tape.r, ((q["idx_i"], "ri"), (q["idx_j"], "rj"), (q["idx_k"], "rk"))),
        ):
            for index, destination in names:
                fnp.take(owner, index, out=x[destination], mode="raise")

        for row, column, c_name, v_name in (
            (q["row_i"], q["idx_i"], "cii", "vii"),
            (q["row_j"], q["idx_j"], "cjj", "vjj"),
            (q["row_k"], q["idx_k"], "ckk", "vkk"),
            (q["row_i"], q["idx_j"], "cij", "vij"),
            (q["row_i"], q["idx_k"], "cik", "vik"),
            (q["row_j"], q["idx_k"], "cjk", "vjk"),
        ):
            fnp.subtract(column, q["vector_base"], out=q["matrix_index"])
            fnp.add(row, q["matrix_index"], out=q["matrix_index"])
            fnp.take(tape.C, q["matrix_index"], out=x[c_name], mode="raise")
            fnp.take(tape.V, q["matrix_index"], out=x[v_name], mode="raise")

    def _require_raw_interior(self) -> None:
        x = self._raw
        fnp.isfinite(self._raw_block, out=self._raw_finite)
        if not bool(fnp.all(self._raw_finite)):
            raise M238Refusal("RAW_NONFINITE_INTERIOR")
        condition = self._conditions
        cdiag = self._raw_block[6:9]
        vdiag = self._raw_block[12:15]
        probability = self._raw_block[18:21]
        derivative = self._raw_block[21:24]
        fnp.greater(cdiag, fnp.float64(0.0), out=condition[0:3])
        fnp.greater(vdiag, fnp.float64(0.0), out=condition[3:6])
        fnp.greater(probability, fnp.float64(PROBABILITY_MIN), out=condition[6:9])
        fnp.less_equal(probability, fnp.float64(1.0), out=condition[9:12])
        fnp.greater_equal(derivative, fnp.float64(0.0), out=condition[12:15])
        if not bool(fnp.all(condition[0:15])):
            raise M238Refusal("RAW_INTERIOR_REFUSAL")

    def _derive_conditionals_and_eta(self) -> None:
        x, w = self._raw, self._work
        cdiag = self._raw_block[6:9]
        sigma = self._work_block[0:3]
        fnp.sqrt(cdiag, out=sigma)
        fnp.divide(self._raw_block[9:11], w["si"][None, :], out=self._work_block[3:5])
        fnp.multiply(self._work_block[3:5], self._work_block[3:5], out=self._work_block[5:7])
        fnp.subtract(cdiag[1:3], self._work_block[5:7], out=self._work_block[5:7])
        fnp.multiply(w["slopej"], w["slopek"], out=w["ccond"])
        fnp.subtract(x["cjk"], w["ccond"], out=w["ccond"])
        fnp.multiply(w["varj"], w["vark"], out=w["schur"])
        fnp.multiply(w["ccond"], w["ccond"], out=w["t0"])
        fnp.subtract(w["schur"], w["t0"], out=w["schur"])
        fnp.greater(self._work_block[5:7], fnp.float64(0.0), out=self._conditions[0:2])
        fnp.greater(w["schur"], fnp.float64(0.0), out=self._conditions[2])
        if not bool(fnp.all(self._conditions[0:3])):
            raise M238Refusal("CONDITIONAL_INTERIOR_REFUSAL")
        fnp.sqrt(self._work_block[5:7], out=self._work_block[7:9])
        fnp.multiply(w["sj"], w["sk"], out=w["denom"])
        fnp.divide(w["ccond"], w["denom"], out=w["rho"])

        pblock = self._raw_block[18:21]
        rblock = self._raw_block[21:24]
        eta2 = self._work_block[12:15]
        eta3 = self._work_block[15:18]
        temp3 = self._work_block[19:22]
        fnp.multiply(pblock, pblock, out=temp3)
        fnp.divide(rblock, temp3, out=eta2)
        fnp.multiply(eta2, fnp.float64(2.0), out=eta2)
        fnp.multiply(cdiag, pblock, out=temp3)
        fnp.multiply(self._raw_block[0:3], eta2, out=eta3)
        fnp.divide(eta3, temp3, out=eta3)
        fnp.multiply(eta3, fnp.float64(-1.0), out=eta3)

    def _derive_tree(self) -> None:
        x, w = self._raw, self._work
        ei, ej, ek = w["eta2i"], w["eta2j"], w["eta2k"]
        hi, hj, hk = w["eta3i"], w["eta3j"], w["eta3k"]
        A, B, E, D = x["vii"], x["vij"], x["vik"], x["vjk"]

        fnp.multiply(ei, ei, out=w["t0"])
        fnp.add(w["t0"], hi, out=w["t0"])
        fnp.multiply(w["t0"], A, out=w["t0"])
        fnp.multiply(ej, ek, out=w["t1"])
        fnp.multiply(w["t1"], D, out=w["t1"])
        fnp.add(w["t0"], w["t1"], out=w["t0"])
        fnp.multiply(B, E, out=w["t1"])
        fnp.multiply(w["t0"], w["t1"], out=w["tree"])
        fnp.multiply(w["tree"], fnp.float64(2.0), out=w["tree"])

        fnp.multiply(A, D, out=w["t0"])
        fnp.multiply(B, E, out=w["t1"])
        fnp.add(w["t0"], w["t1"], out=w["t0"])
        fnp.multiply(ej, B, out=w["t1"])
        fnp.multiply(ek, E, out=w["t2"])
        fnp.add(w["t1"], w["t2"], out=w["t1"])
        fnp.multiply(w["t0"], w["t1"], out=w["t0"])
        fnp.multiply(w["t0"], ei, out=w["t0"])
        fnp.multiply(w["t0"], fnp.float64(2.0), out=w["t0"])
        fnp.add(w["tree"], w["t0"], out=w["tree"])

        fnp.multiply(B, B, out=w["t0"])
        fnp.multiply(w["t0"], hj, out=w["t0"])
        fnp.multiply(E, E, out=w["t1"])
        fnp.multiply(w["t1"], hk, out=w["t1"])
        fnp.add(w["t0"], w["t1"], out=w["t0"])
        fnp.multiply(w["t0"], D, out=w["t0"])
        fnp.add(w["tree"], w["t0"], out=w["tree"])

    def _require_literal_chart(self, receipt: StrictEventReceipt) -> None:
        x, w = self._raw, self._work
        fnp.multiply(w["slopej"], receipt.g, out=w["signed"])
        fnp.add(x["aj"], w["signed"], out=w["alpha_j_plus"])
        fnp.multiply(w["signed"], fnp.float64(-1.0), out=w["signed"])
        fnp.add(x["aj"], w["signed"], out=w["alpha_j_minus"])
        fnp.divide(self._work_block[22:24], w["sj"][None, :], out=self._work_block[22:24])

        fnp.multiply(w["slopek"], receipt.g, out=w["signed"])
        fnp.add(x["ak"], w["signed"], out=w["alpha_k_plus"])
        fnp.multiply(w["signed"], fnp.float64(-1.0), out=w["signed"])
        fnp.add(x["ak"], w["signed"], out=w["alpha_k_minus"])
        fnp.divide(self._work_block[24:26], w["sk"][None, :], out=self._work_block[24:26])

        fnp.multiply(w["rho"], w["rho"], out=w["q_rho"])
        fnp.multiply(w["q_rho"], fnp.float64(-1.0), out=w["q_rho"])
        fnp.add(w["q_rho"], fnp.float64(1.0), out=w["q_rho"])
        fnp.sqrt(w["q_rho"], out=w["q_rho"])

        for alpha_j, alpha_k, t_j, t_k in (
            (w["alpha_j_plus"], w["alpha_k_plus"], w["t_j_plus"], w["t_k_plus"]),
            (w["alpha_j_minus"], w["alpha_k_minus"], w["t_j_minus"], w["t_k_minus"]),
        ):
            fnp.multiply(w["rho"], alpha_j, out=t_j)
            fnp.subtract(alpha_k, t_j, out=t_j)
            fnp.divide(t_j, w["q_rho"], out=t_j)
            fnp.multiply(w["rho"], alpha_k, out=t_k)
            fnp.subtract(alpha_j, t_k, out=t_k)
            fnp.divide(t_k, w["q_rho"], out=t_k)

        fnp.multiply(w["si"], receipt.g, out=w["signed"])
        fnp.add(x["ai"], w["signed"], out=w["rep_plus"])
        fnp.maximum(w["rep_plus"], fnp.float64(0.0), out=w["rep_plus"])
        fnp.subtract(w["rep_plus"], x["mui"], out=w["rep_plus"])
        fnp.divide(w["rep_plus"], w["si"], out=w["rep_plus"])
        fnp.multiply(w["signed"], fnp.float64(-1.0), out=w["signed"])
        fnp.add(x["ai"], w["signed"], out=w["rep_minus"])
        fnp.maximum(w["rep_minus"], fnp.float64(0.0), out=w["rep_minus"])
        fnp.subtract(w["rep_minus"], x["mui"], out=w["rep_minus"])
        fnp.divide(w["rep_minus"], w["si"], out=w["rep_minus"])
        fnp.divide(w["sj"], w["margj"], out=w["scalej"])
        fnp.divide(w["sk"], w["margk"], out=w["scalek"])

        condition = self._conditions
        fnp.abs(w["rho"], out=w["t0"])
        fnp.less_equal(w["t0"], fnp.float64(ABS_RHO_MAX), out=condition[0])
        fnp.abs(self._work_block[22:30], out=self._work_block[22:30])
        fnp.less_equal(
            self._work_block[22:30], fnp.float64(ABS_STANDARD_MAX), out=condition[1:9]
        )
        fnp.greater_equal(self._work_block[35:37], fnp.float64(SCALE_RATIO_MIN), out=condition[9:11])
        fnp.less_equal(self._work_block[35:37], fnp.float64(SCALE_RATIO_MAX), out=condition[11:13])
        fnp.abs(self._work_block[30:32], out=self._work_block[30:32])
        fnp.less_equal(
            self._work_block[30:32], fnp.float64(REPEATED_STANDARD_MAX), out=condition[13:15]
        )
        if not bool(fnp.all(condition[0:15])):
            raise M238Refusal("M224_LITERAL_CHART_REFUSAL")

    def _require_derived_finite(self) -> None:
        # Reuse the boolean slab. Every work row has been initialized by this point.
        fnp.isfinite(self._work_block, out=self._bool_block[: len(_WORK_NAMES)])
        if not bool(fnp.all(self._bool_block[: len(_WORK_NAMES)])):
            raise M238Refusal("DERIVED_NONFINITE_INTERIOR")

    def _commit_outputs(self, receipt: StrictEventReceipt) -> PackedColumns:
        x, w = self._raw, self._work
        sources = {
            "repeated_mean": x["ai"],
            "repeated_sigma": w["si"],
            "repeated_activation_mean": x["mui"],
            "pair_base_left": x["aj"],
            "pair_base_right": x["ak"],
            "pair_slope_left": w["slopej"],
            "pair_slope_right": w["slopek"],
            "pair_sigma_left": w["sj"],
            "pair_sigma_right": w["sk"],
            "pair_rho": w["rho"],
            "activation_mean_left": x["muj"],
            "activation_mean_right": x["muk"],
            "activation_vii": x["vii"],
            "activation_vjk": x["vjk"],
            "activation_vij": x["vij"],
            "activation_vik": x["vik"],
            "tree": w["tree"],
            "marginal_sigma_left": w["margj"],
            "marginal_sigma_right": w["margk"],
        }
        for name in DERIVED_COLUMN_NAMES:
            fnp.copyto(self._outputs[name], sources[name])
        fnp.isfinite(self._output_block, out=self._bool_block[: len(DERIVED_COLUMN_NAMES)])
        if not bool(fnp.all(self._bool_block[: len(DERIVED_COLUMN_NAMES)])):
            raise M238Refusal("OUTPUT_NONFINITE")
        for value in self._outputs.values():
            value.flags.writeable = False
        columns = {"g": receipt.g}
        columns.update(self._outputs)
        if tuple(columns) != COLUMN_NAMES:
            raise M238Refusal("OUTPUT_EXACT_NAME_SET")
        self._last_columns = MappingProxyType(columns)
        return PackedColumns(self._last_columns, self.event_count)

    def pack(self, tape: StackedLayerTape, receipt: StrictEventReceipt) -> PackedColumns:
        self._verify_binding(tape, receipt)
        self._form_indices(receipt)
        self._gather(tape)
        self._require_raw_interior()
        self._derive_conditionals_and_eta()
        self._derive_tree()
        self._require_literal_chart(receipt)
        self._require_derived_finite()
        tape.verify_live()
        receipt.verify_live()
        packed = self._commit_outputs(receipt)
        tape.verify_live()
        receipt.verify_live()
        self._completion[:] = True
        self._consumed = True
        tape._consumed = True
        receipt._consumed = True
        self._owner_receipts_stable = True
        return packed


def run_billed_pack(
    packer: PersistentEventPacker,
    tape: StackedLayerTape,
    receipt: StrictEventReceipt,
) -> dict[str, object]:
    budget = flops.BudgetContext(10**10, quiet=True, wall_time_limit_s=120.0)
    failure = None
    packed = None
    try:
        with budget:
            packed = packer.pack(tape, receipt)
    except Exception as exc:
        failure = f"{type(exc).__name__}: {exc}"
    summary = budget.summary_dict()
    operations = summary.get("operations", {})
    operation_calls = sum(int(row.get("calls", 0)) for row in operations.values())
    columns = () if packed is None else tuple(packed.columns.values())
    return {
        "failure": failure,
        "billed_flops": int(budget.flops_used),
        "residual_wall_s": float(budget.residual_wall_time_s or 0.0),
        "operations": operations,
        "operation_calls": operation_calls,
        "allocation": packer.allocation_ledger(),
        "packed": packed,
        "completion_bitmap": packer.completion_bitmap,
        "g_aliases_receipt": bool(
            packed is not None and np.shares_memory(packed.columns["g"], receipt.g)
        ),
        "all_columns_float64_read_only": bool(
            packed is not None
            and all(value.dtype == np.dtype(np.float64) and not value.flags.writeable for value in columns)
        ),
        "owner_receipts_stable": bool(packer._owner_receipts_stable),
        "finite": bool(packed is not None and all(np.all(np.isfinite(value)) for value in columns)),
    }


__all__ = [
    "CALL_CEILING",
    "COLUMN_NAMES",
    "FLOP_CEILING",
    "M238Refusal",
    "OWNED_BYTE_CEILING",
    "PackedColumns",
    "PersistentEventPacker",
    "StackedLayerTape",
    "StrictEventReceipt",
    "TREE_RELATIVE_ABSOLUTE_LIMIT",
    "run_billed_pack",
    "tree_211_reduced",
]
