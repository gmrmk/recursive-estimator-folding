"""Official same-worker audit entrypoint for frozen M236."""

from __future__ import annotations

from array import array
import json
import os
from pathlib import Path
import time

import flopscope as flops
from whestbench import BaseEstimator, SetupContext

import m236_layer_batched_m212_m235 as m236


LAYERS = 31
WIDTH = 256
EPOCH = 231


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


def _current_workspace(state: m236.ComponentState) -> tuple[object, ...]:
    internal = state.internal_owner
    return (
        state.outputs.aaaa,
        state.outputs.aaab,
        state.outputs.aabb,
        state.staged_owner.weight,
        state.staged_owner.factor,
        internal.scaled,
        internal.gram,
        internal.p,
        internal.p2,
        internal.rho,
        internal.rho_p,
        internal.scratch,
        *internal.level_products,
        state.row_owner.powers,
        state.row_owner.cross,
    )


def _workspace_manifest(state: m236.ComponentState) -> list[dict[str, object]]:
    names = (
        "output_aaaa",
        "output_aaab",
        "output_aabb",
        "staged_weight",
        "staged_factor",
        "scaled",
        "gram",
        "p",
        "p2",
        "rho",
        "rho_p",
        "scratch",
        "level_product_0",
        "level_product_1",
        "level_product_2",
        "level_product_3",
        "row_powers",
        "row_cross",
    )
    return [
        {"name": name, **_descriptor(value)}
        for name, value in zip(names, _current_workspace(state), strict=True)
    ]


def _current_aliases(state: m236.ComponentState) -> tuple[object, ...]:
    values = []
    for plan in state.block_plans:
        values.extend((plan.receipt.rank_order, plan.receipt.selected))
        values.extend((plan.staged.weight, plan.staged.factor))
        values.extend(
            (
                plan.base.scaled,
                plan.base.gram,
                plan.base.p,
                plan.base.p2,
                plan.base.rho,
                plan.base.rho_p,
                plan.base.scratch,
                plan.base.aaab,
                plan.base.aabb,
                plan.base.aaaa,
                *plan.base.level_products,
                plan.row.powers,
                plan.row.cross,
                plan.full.aaaa,
                plan.full.aaab,
                plan.full.aabb,
                plan.full.gram,
                plan.full.p,
            )
        )
    return tuple(values)


def _alias_manifest(state: m236.ComponentState) -> list[dict[str, object]]:
    aliases = []
    for plan in state.block_plans:
        named = (
            ("receipt_rank", plan.receipt.rank_order),
            ("receipt_selected", plan.receipt.selected),
            ("staged_weight", plan.staged.weight),
            ("staged_factor", plan.staged.factor),
            ("scaled", plan.base.scaled),
            ("gram", plan.base.gram),
            ("p", plan.base.p),
            ("p2", plan.base.p2),
            ("rho", plan.base.rho),
            ("rho_p", plan.base.rho_p),
            ("scratch", plan.base.scratch),
            ("aaab", plan.base.aaab),
            ("aabb", plan.base.aabb),
            ("aaaa", plan.base.aaaa),
            *((f"level_product_{i}", value) for i, value in enumerate(plan.base.level_products)),
            ("row_powers", plan.row.powers),
            ("row_cross", plan.row.cross),
        )
        aliases.append(
            {
                "block_index": plan.block_index,
                "start": plan.start,
                "stop": plan.stop,
                "global_ids": list(plan.global_ids),
                "local_ids": list(plan.local_ids),
                "arrays": [
                    {"name": name, **_descriptor(value)} for name, value in named
                ],
            }
        )
    return aliases


class Estimator(BaseEstimator):
    def setup(self, context: SetupContext) -> None:
        if int(context.width) != WIDTH or int(context.depth) != 32:
            raise ValueError("M236 audit entrypoint requires width=256 depth=32")
        if context.scratch_dir is None:
            raise ValueError("M236 audit entrypoint requires official scratch_dir")
        setup_started = time.perf_counter()
        setup_budget = flops.BudgetContext(10**12, quiet=True, wall_time_limit_s=30.0)
        with setup_budget:
            self._state = m236.setup_component(setup_seed=int(context.seed))
        self._timings = array("d", [0.0] * 8)
        self._slot_audit = array("Q", [0] * 3)
        expected_identity = self._identity_values()
        self._identity_audit = array("Q", [0] * len(expected_identity))
        self._predict_index = 0
        timing_address, timing_length = self._timings.buffer_info()
        slot_address, slot_length = self._slot_audit.buffer_info()
        identity_address, identity_length = self._identity_audit.buffer_info()
        workspace = _workspace_manifest(self._state)
        source_by_name = {item["name"]: item for item in workspace}
        manifest = {
            "worker_pid": int(os.getpid()),
            "setup_seed": int(context.seed),
            "setup_bill": int(setup_budget.flops_used),
            "setup_operations": setup_budget.summary_dict()["operations"],
            "setup_pre_manifest_s": time.perf_counter() - setup_started,
            "receipt_object_id": id(self._state.receipt),
            "receipt_rank": _descriptor(self._state.receipt.rank_order),
            "receipt_selected": _descriptor(self._state.receipt.selected),
            "workspace": workspace,
            "aliases": _alias_manifest(self._state),
            "allocation_ledger": m236.allocation_ledger(self._state),
            "source": {
                "aaaa": source_by_name["output_aaaa"],
                "aaab": source_by_name["output_aaab"],
                "aabb": source_by_name["output_aabb"],
            },
            "timing_buffer": {
                "data_pointer": int(timing_address),
                "length": int(timing_length),
                "nbytes": int(timing_length * 8),
            },
            "slot_buffer": {
                "data_pointer": int(slot_address),
                "length": int(slot_length),
                "nbytes": int(slot_length * 8),
            },
            "identity_buffer": {
                "data_pointer": int(identity_address),
                "length": int(identity_length),
                "nbytes": int(identity_length * 8),
                "expected": expected_identity,
            },
        }
        Path(context.scratch_dir, "m236_worker_manifest.json").write_text(
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
        for value in (*_current_workspace(self._state), *_current_aliases(self._state)):
            values.append(id(value))
            values.append(int(value.__array_interface__["data"][0]))
        return values

    def _write_identity_audit(self) -> None:
        values = self._identity_values()
        if len(values) != len(self._identity_audit):
            raise RuntimeError("M236 current-field identity length changed")
        for index, value in enumerate(values):
            self._identity_audit[index] = int(value)

    def _records(self, mlp):
        carrier = mlp.weights[LAYERS]
        return [
            m236.m212.LayerInput(
                layer=layer + 1,
                weight=mlp.weights[layer],
                factor=carrier[layer],
                producer_epoch=EPOCH,
            )
            for layer in range(LAYERS)
        ]

    def predict(self, mlp, budget: int):
        _ = budget
        index = int(self._predict_index)
        if index >= 3:
            raise ValueError("M236 native audit permits exactly three predictions")
        records = self._records(mlp)
        m236.validate_records(self._state, records)
        m212_elapsed = 0.0
        m235_elapsed = 0.0
        for plan in self._state.block_plans:
            started = time.perf_counter()
            with flops.namespace("m212"):
                m236.compile_block_m212(plan, records, EPOCH)
            m212_elapsed += time.perf_counter() - started
            started = time.perf_counter()
            with flops.namespace("m235"):
                m236.subtract_block_m235(plan)
            m235_elapsed += time.perf_counter() - started
        del records
        slots_clear = m236.staging_slots_clear(self._state)
        self._slot_audit[index] = 0 if slots_clear else 1
        if not slots_clear:
            raise RuntimeError("M236 staging slots retained payload views")
        self._timings[2 * index] = m212_elapsed
        self._timings[2 * index + 1] = m235_elapsed
        self._timings[6] = float(index + 1)
        self._write_identity_audit()
        self._predict_index = index + 1
        return mlp.weights[LAYERS][:32]

