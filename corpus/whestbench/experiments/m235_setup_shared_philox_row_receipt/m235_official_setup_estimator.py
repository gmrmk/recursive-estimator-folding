"""Same-worker official-lifecycle audit entrypoint for frozen M235."""

from __future__ import annotations

from array import array
from dataclasses import dataclass
import json
import os
from pathlib import Path
import time

import flopscope as flops
import flopscope.numpy as fnp
from whestbench import BaseEstimator, SetupContext

import m235_setup_shared_philox_row_receipt as m235
import m212_flopscope_sidecar as m212


LAYERS = 31
WIDTH = 256
EPOCH = 231


@dataclass(frozen=True)
class _FullDomainReceipt:
    layer_ids: tuple[int, ...]
    producer_epoch: int
    aaaa: object
    aaab: object
    aabb: object
    gram: object
    p: object


def _descriptor(value) -> dict[str, object]:
    interface = value.__array_interface__
    return {
        "object_id": id(value),
        "data_pointer": int(interface["data"][0]),
        "shape": [int(item) for item in value.shape],
        "strides": (
            [int(item) for item in value.strides]
            if value.strides is not None
            else None
        ),
        "dtype": str(value.dtype),
        "nbytes": int(value.nbytes),
        "c_contiguous": bool(value.flags.c_contiguous),
        "f_contiguous": bool(value.flags.f_contiguous),
        "writeable": bool(value.flags.writeable),
    }


def _workspace_manifest(state: m235.ComponentState) -> list[dict[str, object]]:
    names = (
        "staged_weight",
        "staged_factor",
        "scaled",
        "gram",
        "p",
        "p2",
        "rho",
        "rho_p",
        "scratch",
        "aaab",
        "aabb",
        "aaaa",
        "level_product_0",
        "level_product_1",
        "level_product_2",
        "level_product_3",
        "row_powers",
        "row_cross",
    )
    return [
        {"name": name, **_descriptor(value)}
        for name, value in zip(names, m235.workspace_arrays(state), strict=True)
    ]


class Estimator(BaseEstimator):
    def setup(self, context: SetupContext) -> None:
        if int(context.width) != WIDTH or int(context.depth) != 32:
            raise ValueError("M235 audit entrypoint requires width=256 depth=32")
        if context.scratch_dir is None:
            raise ValueError("M235 audit entrypoint requires official scratch_dir")
        setup_started = time.perf_counter()
        setup_budget = flops.BudgetContext(
            10**12, quiet=True, wall_time_limit_s=30.0
        )
        with setup_budget:
            self._state = m235.setup_component(
                setup_seed=int(context.seed),
                layers=LAYERS,
                width=WIDTH,
                subset_rows=32,
                producer_epoch=EPOCH,
                depth=3,
            )
        self._timings = array("d", [0.0] * 8)
        self._identity_audit = array("Q", [0] * 41)
        self._predict_index = 0
        self._weight_slots = [None] * LAYERS
        self._factor_slots = [None] * LAYERS
        timing_address, timing_length = self._timings.buffer_info()
        identity_address, identity_length = self._identity_audit.buffer_info()
        workspace = _workspace_manifest(self._state)
        by_name = {item["name"]: item for item in workspace}
        identity_expected = self._identity_values()
        manifest = {
            "worker_pid": int(os.getpid()),
            "setup_seed": int(context.seed),
            "setup_bill": int(setup_budget.flops_used),
            "setup_operations": setup_budget.summary_dict()["operations"],
            "setup_pre_manifest_s": time.perf_counter() - setup_started,
            "receipt_issue_s": float(self._state.receipt_elapsed_s),
            "receipt_object_id": id(self._state.receipt),
            "receipt_rank": _descriptor(self._state.receipt.rank_order),
            "receipt_selected": _descriptor(self._state.receipt.selected),
            "workspace": workspace,
            "source": {
                "aaaa": by_name["aaaa"],
                "aaab": by_name["aaab"],
                "aabb": by_name["aabb"],
            },
            "timing_buffer": {
                "data_pointer": int(timing_address),
                "length": int(timing_length),
                "dtype": "float64",
                "nbytes": int(timing_length * 8),
            },
            "identity_buffer": {
                "data_pointer": int(identity_address),
                "length": int(identity_length),
                "dtype": "uint64",
                "nbytes": int(identity_length * 8),
                "expected": identity_expected,
            },
        }
        Path(context.scratch_dir, "m235_worker_manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def _identity_values(self) -> list[int]:
        receipt = self._state.receipt
        values = [
            id(receipt),
            id(receipt.rank_order),
            int(receipt.rank_order.__array_interface__["data"][0]),
            id(receipt.selected),
            int(receipt.selected.__array_interface__["data"][0]),
        ]
        for value in m235.workspace_arrays(self._state):
            values.append(id(value))
            values.append(int(value.__array_interface__["data"][0]))
        return values

    def _write_identity_audit(self) -> None:
        """Audit-only post-kernel scan; its overhead stays in official residual."""

        receipt = self._state.receipt
        self._identity_audit[0] = id(receipt)
        self._identity_audit[1] = id(receipt.rank_order)
        self._identity_audit[2] = int(
            receipt.rank_order.__array_interface__["data"][0]
        )
        self._identity_audit[3] = id(receipt.selected)
        self._identity_audit[4] = int(
            receipt.selected.__array_interface__["data"][0]
        )
        slot = 5
        for value in m235.workspace_arrays(self._state):
            self._identity_audit[slot] = id(value)
            self._identity_audit[slot + 1] = int(
                value.__array_interface__["data"][0]
            )
            slot += 2

    def _stage_f32_fixture(self, mlp) -> None:
        carrier = mlp.weights[LAYERS]
        for layer in range(LAYERS):
            self._weight_slots[layer] = mlp.weights[layer]
            self._factor_slots[layer] = carrier[layer]
        fnp.stack(self._weight_slots, axis=0, out=self._state.staged.weight)
        fnp.stack(self._factor_slots, axis=0, out=self._state.staged.factor)
        self._state.staged.layer_ids = self._state.layer_ids
        self._state.staged.producer_epoch = EPOCH

    def predict(self, mlp, budget: int):
        _ = budget
        index = int(self._predict_index)
        if index >= 3:
            raise ValueError("M235 native audit permits exactly three predictions")
        m212_started = time.perf_counter()
        with flops.namespace("m212"):
            self._stage_f32_fixture(mlp)
            full_outputs = m212.compile_staged_stack(
                self._state.staged, self._state.base, depth=3
            )
        m212_elapsed = time.perf_counter() - m212_started
        full = _FullDomainReceipt(
            layer_ids=self._state.layer_ids,
            producer_epoch=EPOCH,
            aaaa=full_outputs[0],
            aaab=full_outputs[1],
            aabb=full_outputs[2],
            gram=full_outputs[3],
            p=full_outputs[4],
        )
        m235_started = time.perf_counter()
        with flops.namespace("m235"):
            m235.subtract_setup_row_sketch_inplace(self._state, full)
        m235_elapsed = time.perf_counter() - m235_started
        self._timings[2 * index] = m212_elapsed
        self._timings[2 * index + 1] = m235_elapsed
        self._timings[6] = float(index + 1)
        self._write_identity_audit()
        self._predict_index = index + 1
        return mlp.weights[LAYERS][:32]
