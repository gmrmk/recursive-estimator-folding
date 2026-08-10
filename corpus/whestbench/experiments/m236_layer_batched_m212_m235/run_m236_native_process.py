"""One frozen official same-worker M236 seed-0 A-B-A falsifier."""

from __future__ import annotations

import json
import math
from pathlib import Path
import sys
import tempfile
import time

import numpy as np

from whestbench import SetupContext
from whestbench.domain import MLP
from whestbench.runner import EstimatorEntrypoint, ResourceLimits, SubprocessRunner


HERE = Path(__file__).resolve().parent
BASE = HERE.parent
M235_DIR = BASE / "m235_setup_shared_philox_row_receipt"
if str(M235_DIR) not in sys.path:
    sys.path.insert(0, str(M235_DIR))

import run_m235_native_process as transport  # noqa: E402


WIDTH = 256
LAYERS = 31
SUBSET_ROWS = 32
SETUP_SEED = 0
SOURCE_SEEDS = {"A": 227700001, "B": 227710001}
SEQUENCE = ("A", "B", "A")
EXPECTED_SETUP_RECEIPT_BILL = 32_768
EXPECTED_M212_BILL = 1_249_253_376
EXPECTED_M235_BILL = 864_960_512
EXPECTED_COMBINED_BILL = 2_114_213_888
CONSERVATIVE_COMBINED_BILL = 2_114_246_656
M235_WALL_CAP_S = 0.002025121700262334
LAWFUL_COMBINED_CAP_S = 0.003227087104
CONSERVATIVE_COMBINED_CAP_S = 0.003227021568
OFFICIAL_START_CAP_S = 4.0
OFFICIAL_SETUP_TIMEOUT_S = 5.0
RSS_CAP_MIB = 496.0
EXPECTED_M212_CALLS = {
    "add": 12,
    "copyto": 100,
    "diagonal": 8,
    "matmul": 16,
    "multiply": 44,
    "reshape": 16,
    "stack": 8,
    "sum": 4,
    "swapaxes": 32,
    "transpose": 32,
}
EXPECTED_M235_CALLS = {
    "add": 36,
    "copyto": 4,
    "matmul": 8,
    "multiply": 64,
    "sum": 4,
    "take_along_axis": 4,
}


def _fixture(seed: int) -> MLP:
    rng = np.random.Generator(np.random.Philox(int(seed)))
    he = np.float32(math.sqrt(2.0 / WIDTH))
    weights = [
        rng.standard_normal((WIDTH, WIDTH), dtype=np.float32) * he
        for _ in range(LAYERS)
    ]
    carrier = np.zeros((WIDTH, WIDTH), dtype=np.float32)
    carrier[:LAYERS] = rng.standard_normal(
        (LAYERS, WIDTH), dtype=np.float32
    ) / np.float32(math.sqrt(WIDTH))
    mlp = MLP(width=WIDTH, depth=32, weights=[*weights, carrier], seed=int(seed))
    mlp.validate()
    return mlp


def _read_u64(handle, descriptor: dict[str, object]) -> list[int]:
    payload = transport._read_process_memory(
        handle, int(descriptor["data_pointer"]), int(descriptor["nbytes"])
    )
    return [int(value) for value in np.frombuffer(payload, dtype=np.uint64)]


def _alias_law(manifest: dict[str, object]) -> dict[str, bool]:
    def logical_nbytes(shape: list[int], dtype: str) -> int:
        return int(np.prod(np.asarray(shape, dtype=np.int64))) * int(np.dtype(dtype).itemsize)

    def physical_span(descriptor: dict[str, object]) -> int:
        shape = [int(value) for value in descriptor["shape"]]
        strides = descriptor["strides"]
        itemsize = int(np.dtype(descriptor["dtype"]).itemsize)
        if strides is None:
            return int(descriptor["nbytes"])
        return itemsize + sum(
            (extent - 1) * abs(int(stride))
            for extent, stride in zip(shape, strides, strict=True)
        )

    def expected_shape(owner: dict[str, object], axis: int, count: int) -> list[int]:
        shape = [int(value) for value in owner["shape"]]
        shape[axis] = int(count)
        return shape

    def exact_alias(
        alias: dict[str, object],
        owner: dict[str, object],
        *,
        axis: int,
        count: int,
        offset: int,
    ) -> tuple[bool, bool, bool]:
        shape = expected_shape(owner, axis, count)
        pointer_ok = int(alias["data_pointer"]) == int(owner["data_pointer"]) + int(offset)
        shape_stride_ok = (
            [int(value) for value in alias["shape"]] == shape
            and alias["strides"] == owner["strides"]
            and alias["dtype"] == owner["dtype"]
        )
        alias_span = physical_span(alias)
        owner_span = physical_span(owner)
        bytes_span_ok = (
            int(alias["nbytes"]) == logical_nbytes(shape, alias["dtype"])
            and alias_span
            == int(np.dtype(alias["dtype"]).itemsize)
            + sum(
                (extent - 1) * abs(int(stride))
                for extent, stride in zip(shape, alias["strides"], strict=True)
            )
            and int(offset) + alias_span <= owner_span
        )
        return pointer_ok, shape_stride_ok, bytes_span_ok

    owners = {item["name"]: item for item in manifest["workspace"]}
    rank = manifest["receipt_rank"]
    selected = manifest["receipt_selected"]
    output_owner = {"aaaa": "output_aaaa", "aaab": "output_aaab", "aabb": "output_aabb"}
    direct_owner = {
        "staged_weight": "staged_weight",
        "staged_factor": "staged_factor",
        "scaled": "scaled",
        "gram": "gram",
        "p": "p",
        "p2": "p2",
        "rho": "rho",
        "rho_p": "rho_p",
        "scratch": "scratch",
        "row_powers": "row_powers",
        "row_cross": "row_cross",
        "level_product_0": "level_product_0",
        "level_product_1": "level_product_1",
        "level_product_2": "level_product_2",
        "level_product_3": "level_product_3",
    }
    spans = []
    global_ids = []
    pointers = True
    shapes_strides = True
    bytes_spans = True
    receipt_views = True
    for block in manifest["aliases"]:
        start = int(block["start"])
        stop = int(block["stop"])
        count = stop - start
        spans.append((start, stop))
        global_ids.extend(int(value) for value in block["global_ids"])
        shapes_strides = shapes_strides and block["global_ids"] == list(
            range(start + 1, stop + 1)
        ) and block["local_ids"] == list(range(1, count + 1))
        arrays = {item["name"]: item for item in block["arrays"]}
        for name, owner_name in output_owner.items():
            alias = arrays[name]
            owner = owners[owner_name]
            checks = exact_alias(
                alias,
                owner,
                axis=0,
                count=count,
                offset=start * int(owner["strides"][0]),
            )
            pointers = pointers and checks[0]
            shapes_strides = shapes_strides and checks[1]
            bytes_spans = bytes_spans and checks[2]
        for name, owner_name in direct_owner.items():
            alias = arrays[name]
            owner = owners[owner_name]
            axis = 1 if name in {"row_powers", "row_cross"} else 0
            checks = exact_alias(alias, owner, axis=axis, count=count, offset=0)
            pointers = pointers and checks[0]
            shapes_strides = shapes_strides and checks[1]
            bytes_spans = bytes_spans and checks[2]
        for name, owner in (("receipt_rank", rank), ("receipt_selected", selected)):
            alias = arrays[name]
            checks = exact_alias(
                alias,
                owner,
                axis=0,
                count=count,
                offset=start * int(owner["strides"][0]),
            )
            receipt_views = receipt_views and all(checks)
    return {
        "canonical_spans": spans == [(0, 8), (8, 16), (16, 24), (24, 31)],
        "global_coverage": global_ids == list(range(1, 32)),
        "owner_pointers": bool(pointers),
        "exact_shapes_strides": bool(shapes_strides),
        "exact_nbytes_spans": bool(bytes_spans),
        "gapped_receipt_views": bool(receipt_views),
    }


def _prediction_receipt(
    *,
    official: SubprocessRunner,
    handle,
    worker_pid: int,
    manifest: dict[str, object],
    fixture: MLP,
    label: str,
    prediction_index: int,
) -> tuple[dict[str, object], dict[str, bytes], bytes]:
    returned = official.predict(fixture, budget=272_000_000_000)
    stats = official.last_predict_stats()
    if stats is None or stats.budget_breakdown is None:
        raise RuntimeError("official runner returned no budget breakdown")
    by_namespace = stats.budget_breakdown.get("by_namespace", {})
    m212_bucket = by_namespace.get("m212")
    m235_bucket = by_namespace.get("m235")
    if m212_bucket is None or m235_bucket is None:
        raise RuntimeError("official budget lacks M212/M235 namespaces")
    timings = transport._timing_values(handle, manifest)
    if int(timings[6]) != prediction_index + 1:
        raise RuntimeError("remote timing prediction count mismatch")
    m212_residual = float(
        timings[2 * prediction_index]
        - float(m212_bucket["flopscope_backend_time_s"])
        - float(m212_bucket["flopscope_overhead_time_s"])
    )
    m235_residual = float(
        timings[2 * prediction_index + 1]
        - float(m235_bucket["flopscope_backend_time_s"])
        - float(m235_bucket["flopscope_overhead_time_s"])
    )
    identities = _read_u64(handle, manifest["identity_buffer"])
    identity_stable = identities == [
        int(value) for value in manifest["identity_buffer"]["expected"]
    ]
    slots = _read_u64(handle, manifest["slot_buffer"])
    source, raw_source = transport._source_snapshot(handle, manifest)
    workspace = transport._workspace_snapshot(handle, manifest)
    receipt, rank_bytes, _ = transport._receipt_snapshot(handle, manifest)
    memory = transport._worker_memory(handle)
    returned_array = np.asarray(returned)
    failure = None
    if m212_residual < 0.0 or m235_residual < 0.0:
        failure = "RuntimeError: negative namespace residual estimate"
    result = {
        "label": label,
        "failure": failure,
        "worker_pid": worker_pid,
        "m212_bill": int(m212_bucket["flops_used"]),
        "m235_bill": int(m235_bucket["flops_used"]),
        "combined_bill": int(stats.flops_used),
        "m212_operations": m212_bucket["operations"],
        "m235_operations": m235_bucket["operations"],
        "exact_calls": transport._exact_calls(m212_bucket, EXPECTED_M212_CALLS)
        and transport._exact_calls(m235_bucket, EXPECTED_M235_CALLS),
        "m212_raw_wall_s": float(timings[2 * prediction_index]),
        "m235_raw_wall_s": float(timings[2 * prediction_index + 1]),
        "m212_residual_s": m212_residual,
        "m235_residual_s": m235_residual,
        "combined_residual_s": float(stats.residual_wall_time_s),
        "m235_wall_fits": 0.0 <= m235_residual <= M235_WALL_CAP_S,
        "lawful_combined_fits": float(stats.residual_wall_time_s) <= LAWFUL_COMBINED_CAP_S,
        "conservative_combined_fits": float(stats.residual_wall_time_s) <= CONSERVATIVE_COMBINED_CAP_S,
        "finite": bool(source["finite"]),
        "symmetric": bool(source["symmetric"]),
        "aabb_max_asymmetry": source["aabb_max_asymmetry"],
        "sha256": source["sha256"],
        "arrays": source["arrays"],
        "returned_shape": list(returned_array.shape),
        "returned_dtype": str(returned_array.dtype),
        "returned_finite": bool(np.all(np.isfinite(returned_array))),
        "rss_mib": float(memory["peak_working_set_mib"]),
        "memory": memory,
        "workspace_sha256": workspace["sha256"],
        "workspace_bytes_read": workspace["bytes_read"],
        "receipt_sha256": receipt["rank_sha256"],
        "receipt_law": receipt["law"],
        "identity_stable": identity_stable,
        "slots_clear": int(slots[prediction_index]) == 0,
    }
    return result, raw_source, rank_bytes


def run_one_process() -> dict[str, object]:
    fixtures = {label: _fixture(seed) for label, seed in SOURCE_SEEDS.items()}
    runtime_hashes = transport._runtime_hashes()
    official = SubprocessRunner()
    failure = None
    predictions = []
    raw_outputs = []
    receipt_bytes = []
    worker_pid = -1
    launcher_pid = -1
    start_elapsed = float("inf")
    manifest = None
    initial_receipt = None
    initial_rank_bytes = b""
    with tempfile.TemporaryDirectory(prefix="m236_seed0_primary_") as scratch:
        scratch_path = Path(scratch)
        try:
            started = time.perf_counter()
            official.start(
                EstimatorEntrypoint(
                    file_path=HERE / "m236_official_setup_estimator.py",
                    class_name="Estimator",
                ),
                SetupContext(
                    width=WIDTH,
                    depth=32,
                    flop_budget=272_000_000_000,
                    api_version="2.0",
                    scratch_dir=str(scratch_path),
                    submission_dir=str(HERE),
                    seed=SETUP_SEED,
                ),
                ResourceLimits(
                    setup_timeout_s=OFFICIAL_SETUP_TIMEOUT_S,
                    predict_timeout_s=60.0,
                    memory_limit_mb=512,
                    flop_budget=272_000_000_000,
                    wall_time_limit_s=60.0,
                ),
            )
            start_elapsed = time.perf_counter() - started
            if official._process is None or official._process.poll() is not None:
                raise RuntimeError("official M236 worker is not alive after start")
            launcher_pid = int(official._process.pid)
            manifest = json.loads(
                (scratch_path / "m236_worker_manifest.json").read_text(encoding="utf-8")
            )
            worker_pid = int(manifest["worker_pid"])
            handle = transport._open_worker(worker_pid)
            try:
                initial_receipt, initial_rank_bytes, _ = transport._receipt_snapshot(
                    handle, manifest
                )
                for prediction_index, label in enumerate(SEQUENCE):
                    prediction, raw, rank_bytes = _prediction_receipt(
                        official=official,
                        handle=handle,
                        worker_pid=worker_pid,
                        manifest=manifest,
                        fixture=fixtures[label],
                        label=label,
                        prediction_index=prediction_index,
                    )
                    predictions.append(prediction)
                    raw_outputs.append(raw)
                    receipt_bytes.append(rank_bytes)
            finally:
                transport._close_worker_handle(handle)
        except Exception as exc:
            failure = f"{type(exc).__name__}: {exc}"
        finally:
            official.close()

    if manifest is None:
        return {
            "status": "KILLED_NATIVE_START",
            "failure": failure or "RuntimeError: missing M236 worker manifest",
            "same_worker_transport": False,
            "official_worker_pid": worker_pid,
            "official_launcher_pid": launcher_pid,
            "official_start_response_s": start_elapsed,
            "predictions": predictions,
        }

    setup_operations = manifest["setup_operations"]
    setup_empty_calls = int(setup_operations.get("empty", {}).get("calls", -1))
    alias_law = _alias_law(manifest)
    receipt_stable = bool(receipt_bytes) and all(
        value == initial_rank_bytes for value in receipt_bytes
    )
    endpoint_bitwise = len(raw_outputs) == 3 and all(
        raw_outputs[0][name] == raw_outputs[2][name]
        for name in ("aaaa", "aaab", "aabb")
    )
    setup_ok = (
        runtime_hashes == transport.PINNED_HASHES
        and start_elapsed < OFFICIAL_START_CAP_S
        and int(manifest["setup_bill"]) == EXPECTED_SETUP_RECEIPT_BILL
        and setup_empty_calls == 18
        and float(manifest["setup_pre_manifest_s"]) < OFFICIAL_START_CAP_S
        and initial_receipt is not None
        and all(initial_receipt["law"].values())
        and all(alias_law.values())
        and int(manifest["allocation_ledger"]["numeric_peak_bytes"]) == 61_812_736
    )
    prediction_ok = len(predictions) == 3 and all(
        prediction["failure"] is None
        and prediction["worker_pid"] == worker_pid
        and prediction["m212_bill"] == EXPECTED_M212_BILL
        and prediction["m235_bill"] == EXPECTED_M235_BILL
        and prediction["combined_bill"] == EXPECTED_COMBINED_BILL
        and prediction["exact_calls"]
        and prediction["m235_wall_fits"]
        and prediction["lawful_combined_fits"]
        and prediction["conservative_combined_fits"]
        and prediction["finite"]
        and prediction["symmetric"]
        and prediction["returned_shape"] == [32, WIDTH]
        and prediction["returned_dtype"] == "float32"
        and prediction["returned_finite"]
        and prediction["identity_stable"]
        and prediction["slots_clear"]
        and prediction["rss_mib"] < RSS_CAP_MIB
        for prediction in predictions
    )
    if failure is None and not setup_ok:
        failure = "RuntimeError: frozen M236 same-worker setup gate failed"
    if failure is None and not prediction_ok:
        failure = "RuntimeError: frozen M236 same-worker prediction gate failed"
    if failure is None and not receipt_stable:
        failure = "RuntimeError: remote M236 receipt bytes changed"
    if failure is None and not endpoint_bitwise:
        failure = "RuntimeError: remote M236 A replay is not bitwise identical"
    status = "PASS_NATIVE_ONE_PROCESS" if failure is None else "KILLED_FROZEN_NATIVE_GATE"
    return {
        "candidate": "M236 fixed B=8 layer-batched M212+M235",
        "status": status,
        "failure": failure,
        "g0_opened": False,
        "native_aggregate_opened": False,
        "same_worker_transport": True,
        "transport": "Win32 ReadProcessMemory",
        "setup_seed": SETUP_SEED,
        "source_seeds": SOURCE_SEEDS,
        "sequence": list(SEQUENCE),
        "official_worker_pid": worker_pid,
        "official_launcher_pid": launcher_pid,
        "official_start_response_s": start_elapsed,
        "component_setup_pre_manifest_s": float(manifest["setup_pre_manifest_s"]),
        "setup_bill": int(manifest["setup_bill"]),
        "setup_empty_calls": setup_empty_calls,
        "runtime_hashes_match": runtime_hashes == transport.PINNED_HASHES,
        "receipt_law": initial_receipt["law"] if initial_receipt else {},
        "receipt_stable": receipt_stable,
        "alias_law": alias_law,
        "allocation_ledger": manifest["allocation_ledger"],
        "endpoint_bitwise_equal": endpoint_bitwise,
        "predictions": predictions,
        "outputs": [
            {"label": label, "sha256": prediction["sha256"], "arrays": prediction["arrays"]}
            for label, prediction in zip(SEQUENCE, predictions, strict=True)
        ],
    }


def main() -> None:
    print(json.dumps(run_one_process(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
