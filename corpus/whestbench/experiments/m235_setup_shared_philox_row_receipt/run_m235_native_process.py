"""One frozen same-worker M235 native receipt process."""

from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
import hashlib
import json
import math
from pathlib import Path
import tempfile
import time

import numpy as np

from whestbench import SetupContext
from whestbench.domain import MLP
from whestbench.runner import EstimatorEntrypoint, ResourceLimits, SubprocessRunner


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
WIDTH = 256
LAYERS = 31
SUBSET_ROWS = 32
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
RECEIPT_ISSUE_CAP_S = 0.05
RSS_CAP_MIB = 512.0
SETUP_SEEDS = (0, 235700001, 235700002, 235700003, 235700004)
FIRST_SOURCE_SEEDS = (227700001, 227700002, 227700003, 227700004, 227700005)
SECOND_SOURCE_SEEDS = (227710001, 227710002, 227710003, 227710004, 227710005)

PINNED_HASHES = {
    "flopscope/_registry.py": "D735DA7D36ECF05BA7B927452DB126FE297E33398F3903C59B886E1BC1228795",
    "flopscope/numpy/random/_cost_formulas.py": "D14D86A2CA0700C0899318A9C7CD3F08E91AC80948682225D383D71E2D628F8F",
    "flopscope/numpy/random/_counted_classes.py": "6D7AA1E9C4F7A135EF7487FAF6B645AEA61C74983FA780DAFFB68240C6DA3F0D",
    "numpy/random/_philox.cp314-win_amd64.pyd": "8CEB13F5A97EB161FD7D93D2E597DC99D3387A76F32EF187A57103AC759BDA15",
    "numpy/random/_generator.cp314-win_amd64.pyd": "69C5AA9B41C0A60EE8600A4C1434C86FA96DFC00F4CD3171AED9729AACAA549B",
    "whestbench/sdk.py": "B0FCC52C6B531981E46DA6955365AA786260FAB53FD66DCF3675791ED8C3C105",
    "whestbench/subprocess_worker.py": "F1EA178C94E4F7BA790EC1350D83A078982964D6A0C88F90EF58522A234EC089",
    "whestbench/runner.py": "6176EB3A91233AC6AAB8057141C2E82FEEA02BDF955E9F830EE8F756DE9ABC86",
}
EXPECTED_M212_CALLS = {
    "add": 3,
    "copyto": 25,
    "diagonal": 2,
    "matmul": 4,
    "multiply": 11,
    "reshape": 4,
    "stack": 2,
    "sum": 1,
    "swapaxes": 8,
    "transpose": 8,
}
EXPECTED_M235_CALLS = {
    "add": 9,
    "copyto": 1,
    "matmul": 2,
    "multiply": 16,
    "sum": 1,
    "take_along_axis": 1,
}

PROCESS_VM_READ = 0x0010
PROCESS_QUERY_INFORMATION = 0x0400


class _ProcessMemoryCountersEx(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("PageFaultCount", wintypes.DWORD),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
        ("PrivateUsage", ctypes.c_size_t),
    ]


def _runtime_hashes() -> dict[str, str]:
    site = ROOT / "work" / "whest-v014" / "Lib" / "site-packages"
    return {
        name: hashlib.sha256((site / name).read_bytes()).hexdigest().upper()
        for name in PINNED_HASHES
    }


def _open_worker(pid: int):
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel32.OpenProcess.restype = wintypes.HANDLE
    handle = kernel32.OpenProcess(
        PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, False, int(pid)
    )
    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())
    return handle


def _close_worker_handle(handle) -> None:
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL
    if not kernel32.CloseHandle(handle):
        raise ctypes.WinError(ctypes.get_last_error())


def _read_process_memory(handle, address: int, size: int) -> bytes:
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.ReadProcessMemory.argtypes = [
        wintypes.HANDLE,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_size_t),
    ]
    kernel32.ReadProcessMemory.restype = wintypes.BOOL
    buffer = ctypes.create_string_buffer(int(size))
    received = ctypes.c_size_t(0)
    if not kernel32.ReadProcessMemory(
        handle,
        ctypes.c_void_p(int(address)),
        buffer,
        int(size),
        ctypes.byref(received),
    ):
        raise ctypes.WinError(ctypes.get_last_error())
    if int(received.value) != int(size):
        raise OSError(f"short ReadProcessMemory: {received.value} != {size}")
    return buffer.raw


def _worker_memory(handle) -> dict[str, float]:
    counters = _ProcessMemoryCountersEx()
    counters.cb = ctypes.sizeof(counters)
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    psapi.GetProcessMemoryInfo.argtypes = [
        wintypes.HANDLE,
        ctypes.c_void_p,
        wintypes.DWORD,
    ]
    psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
    if not psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb):
        raise ctypes.WinError(ctypes.get_last_error())
    mib = 1024.0 * 1024.0
    return {
        "peak_working_set_mib": counters.PeakWorkingSetSize / mib,
        "working_set_mib": counters.WorkingSetSize / mib,
        "private_mib": counters.PrivateUsage / mib,
        "peak_pagefile_mib": counters.PeakPagefileUsage / mib,
    }


def _fixture(seed: int) -> MLP:
    rng = np.random.Generator(np.random.Philox(int(seed)))
    he = np.float32(math.sqrt(2.0 / WIDTH))
    weights = [
        (rng.standard_normal((WIDTH, WIDTH), dtype=np.float32) * he)
        for _ in range(LAYERS)
    ]
    carrier = np.zeros((WIDTH, WIDTH), dtype=np.float32)
    carrier[:LAYERS] = rng.standard_normal(
        (LAYERS, WIDTH), dtype=np.float32
    ) / np.float32(math.sqrt(WIDTH))
    mlp = MLP(width=WIDTH, depth=32, weights=[*weights, carrier], seed=int(seed))
    mlp.validate()
    return mlp


def _exact_calls(bucket: dict[str, object], expected: dict[str, int]) -> bool:
    actual = {
        name: int(receipt["calls"])
        for name, receipt in bucket.get("operations", {}).items()
        if int(receipt["calls"]) != 0
    }
    return actual == expected


def _descriptor_bytes(handle, descriptor: dict[str, object]) -> bytes:
    if not (
        bool(descriptor["c_contiguous"]) or bool(descriptor["f_contiguous"])
    ):
        raise ValueError("remote descriptor is not contiguous in C or Fortran order")
    shape = [int(value) for value in descriptor["shape"]]
    dtype = np.dtype(descriptor["dtype"])
    strides = descriptor["strides"]
    span = int(dtype.itemsize)
    if strides is None:
        span = int(descriptor["nbytes"])
    else:
        span += sum(
            (extent - 1) * abs(int(stride))
            for extent, stride in zip(shape, strides, strict=True)
        )
    return _read_process_memory(
        handle, int(descriptor["data_pointer"]), span
    )


def _receipt_snapshot(
    handle, manifest: dict[str, object]
) -> tuple[dict[str, object], bytes, bytes]:
    rank_descriptor = manifest["receipt_rank"]
    rank_bytes = _descriptor_bytes(handle, rank_descriptor)
    rank = np.ndarray(
        shape=tuple(rank_descriptor["shape"]),
        dtype=np.dtype(rank_descriptor["dtype"]),
        buffer=rank_bytes,
        strides=tuple(rank_descriptor["strides"]),
    )
    selected = np.ascontiguousarray(rank[:, :SUBSET_ROWS])
    selected_bytes = selected.tobytes()
    target = np.arange(WIDTH, dtype=np.int64)
    law = {
        "full_permutations": all(
            np.array_equal(np.sort(row), target) for row in rank
        ),
        "selected_unique": all(
            np.unique(row).size == SUBSET_ROWS for row in selected
        ),
        "independent_slices_distinct": len({row.tobytes() for row in rank})
        == LAYERS,
        "rank_readonly": not bool(rank_descriptor["writeable"]),
        "selected_readonly": not bool(manifest["receipt_selected"]["writeable"]),
        "selected_view_pointer": int(manifest["receipt_selected"]["data_pointer"])
        == int(rank_descriptor["data_pointer"]),
        "selected_view_strides": manifest["receipt_selected"]["strides"]
        == rank_descriptor["strides"],
    }
    snapshot = {
        "rank_sha256": hashlib.sha256(rank_bytes).hexdigest(),
        "selected_sha256": hashlib.sha256(selected_bytes).hexdigest(),
        "law": law,
    }
    return snapshot, rank_bytes, selected_bytes


def _workspace_snapshot(handle, manifest: dict[str, object]) -> dict[str, object]:
    digest = hashlib.sha256()
    bytes_read = 0
    for descriptor in manifest["workspace"]:
        payload = _descriptor_bytes(handle, descriptor)
        digest.update(str(descriptor["name"]).encode("ascii"))
        digest.update(payload)
        bytes_read += len(payload)
    return {"sha256": digest.hexdigest(), "bytes_read": bytes_read}


def _source_snapshot(
    handle, manifest: dict[str, object]
) -> tuple[dict[str, object], dict[str, bytes]]:
    raw = {
        name: _descriptor_bytes(handle, descriptor)
        for name, descriptor in manifest["source"].items()
    }
    arrays = {
        name: np.frombuffer(payload, dtype=np.dtype(manifest["source"][name]["dtype"]))
        .reshape(tuple(manifest["source"][name]["shape"]))
        for name, payload in raw.items()
    }
    finite = all(np.all(np.isfinite(value)) for value in arrays.values())
    asymmetry = float(
        np.max(np.abs(arrays["aabb"] - np.swapaxes(arrays["aabb"], 1, 2)))
    )
    digest = hashlib.sha256()
    for name in ("aaaa", "aaab", "aabb"):
        digest.update(raw[name])
    return (
        {
            "sha256": digest.hexdigest(),
            "finite": finite,
            "aabb_max_asymmetry": asymmetry,
            "symmetric": asymmetry <= 2.0e-10,
            "arrays": [
                {
                    "name": name,
                    "shape": list(arrays[name].shape),
                    "dtype": str(arrays[name].dtype),
                    "nbytes": len(raw[name]),
                }
                for name in ("aaaa", "aaab", "aabb")
            ],
        },
        raw,
    )


def _timing_values(handle, manifest: dict[str, object]) -> np.ndarray:
    descriptor = manifest["timing_buffer"]
    payload = _read_process_memory(
        handle, int(descriptor["data_pointer"]), int(descriptor["nbytes"])
    )
    return np.frombuffer(payload, dtype=np.float64).copy()


def _identity_values(handle, manifest: dict[str, object]) -> list[int]:
    descriptor = manifest["identity_buffer"]
    payload = _read_process_memory(
        handle, int(descriptor["data_pointer"]), int(descriptor["nbytes"])
    )
    return [int(value) for value in np.frombuffer(payload, dtype=np.uint64)]


def _prediction_receipt(
    *,
    official: SubprocessRunner,
    handle,
    worker_pid: int,
    manifest: dict[str, object],
    fixture: MLP,
    label: str,
    prediction_index: int,
) -> tuple[dict[str, object], dict[str, bytes], bytes, dict[str, object]]:
    returned = official.predict(fixture, budget=272_000_000_000)
    stats = official.last_predict_stats()
    if stats is None or stats.budget_breakdown is None:
        raise RuntimeError("official runner returned no budget breakdown")
    by_namespace = stats.budget_breakdown.get("by_namespace", {})
    m212_bucket = by_namespace.get("m212")
    m235_bucket = by_namespace.get("m235")
    if m212_bucket is None or m235_bucket is None:
        raise RuntimeError("official budget lacks M212/M235 namespaces")
    timings = _timing_values(handle, manifest)
    if int(timings[6]) != prediction_index + 1:
        raise RuntimeError("remote timing receipt prediction count mismatch")
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
    identity_values = _identity_values(handle, manifest)
    identity_stable = identity_values == [
        int(value) for value in manifest["identity_buffer"]["expected"]
    ]
    source, raw_source = _source_snapshot(handle, manifest)
    workspace = _workspace_snapshot(handle, manifest)
    receipt, rank_bytes, _selected_bytes = _receipt_snapshot(handle, manifest)
    memory = _worker_memory(handle)
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
        "exact_calls": _exact_calls(m212_bucket, EXPECTED_M212_CALLS)
        and _exact_calls(m235_bucket, EXPECTED_M235_CALLS),
        "m212_raw_wall_s": float(timings[2 * prediction_index]),
        "m235_raw_wall_s": float(timings[2 * prediction_index + 1]),
        "m212_residual_s": m212_residual,
        "m235_residual_s": m235_residual,
        "combined_residual_s": float(stats.residual_wall_time_s),
        "m235_wall_fits": 0.0 <= m235_residual <= M235_WALL_CAP_S,
        "lawful_combined_fits": float(stats.residual_wall_time_s)
        <= LAWFUL_COMBINED_CAP_S,
        "conservative_combined_fits": float(stats.residual_wall_time_s)
        <= CONSERVATIVE_COMBINED_CAP_S,
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
        "identity_stable": identity_stable,
        "identity_sha256": hashlib.sha256(
            np.asarray(identity_values, dtype=np.uint64).tobytes()
        ).hexdigest(),
    }
    return result, raw_source, rank_bytes, workspace


def run_process(*, pair_index: int, order: str) -> dict[str, object]:
    if pair_index not in range(5):
        raise ValueError("pair_index must be in 0..4")
    if order not in {"primary", "mirror"}:
        raise ValueError("order must be primary or mirror")
    setup_seed = SETUP_SEEDS[pair_index]
    first_seed = FIRST_SOURCE_SEEDS[pair_index]
    second_seed = SECOND_SOURCE_SEEDS[pair_index]
    sequence = ["A", "B", "A"] if order == "primary" else ["B", "A", "B"]
    fixtures = {"A": _fixture(first_seed), "B": _fixture(second_seed)}
    runtime_hashes = _runtime_hashes()
    failure = None
    predictions = []
    raw_outputs = []
    receipt_bytes = []
    workspace_snapshots = []
    official = SubprocessRunner()
    worker_pid = -1
    launcher_pid = -1
    start_elapsed = float("inf")
    manifest = None
    initial_receipt = None
    initial_rank_bytes = b""
    with tempfile.TemporaryDirectory(prefix=f"m235_{pair_index}_{order}_") as scratch:
        scratch_path = Path(scratch)
        try:
            start = time.perf_counter()
            official.start(
                EstimatorEntrypoint(
                    file_path=HERE / "m235_official_setup_estimator.py",
                    class_name="Estimator",
                ),
                SetupContext(
                    width=WIDTH,
                    depth=32,
                    flop_budget=272_000_000_000,
                    api_version="2.0",
                    scratch_dir=str(scratch_path),
                    submission_dir=str(HERE),
                    seed=setup_seed,
                ),
                ResourceLimits(
                    setup_timeout_s=OFFICIAL_SETUP_TIMEOUT_S,
                    predict_timeout_s=60.0,
                    memory_limit_mb=512,
                    flop_budget=272_000_000_000,
                    wall_time_limit_s=60.0,
                ),
            )
            start_elapsed = time.perf_counter() - start
            if official._process is None or official._process.poll() is not None:
                raise RuntimeError("official M235 worker is not alive after start")
            launcher_pid = int(official._process.pid)
            manifest = json.loads(
                (scratch_path / "m235_worker_manifest.json").read_text(
                    encoding="utf-8"
                )
            )
            worker_pid = int(manifest["worker_pid"])
            handle = _open_worker(worker_pid)
            try:
                initial_receipt, initial_rank_bytes, _ = _receipt_snapshot(
                    handle, manifest
                )
                # All three calls remain on this exact official setup-owned worker.
                for prediction_index, label in enumerate(sequence):
                    prediction, raw, rank_bytes, workspace = _prediction_receipt(
                        official=official,
                        handle=handle,
                        worker_pid=worker_pid,
                        manifest=manifest,
                        fixture=fixtures[label],
                        label=label,
                        prediction_index=prediction_index,
                    )
                    # Explicit same-process transport receipt required by erratum 4.
                    _read_process_memory(
                        handle,
                        int(manifest["timing_buffer"]["data_pointer"]),
                        8,
                    )
                    predictions.append(prediction)
                    raw_outputs.append(raw)
                    receipt_bytes.append(rank_bytes)
                    workspace_snapshots.append(workspace)
            finally:
                _close_worker_handle(handle)
        except Exception as exc:
            failure = f"{type(exc).__name__}: {exc}"
        finally:
            official.close()

    if manifest is None:
        return {
            "failure": failure or "RuntimeError: missing same-worker manifest",
            "same_worker_transport": False,
            "transport": "Win32 ReadProcessMemory",
            "official_worker_pid": worker_pid,
            "official_launcher_pid": launcher_pid,
            "official_start_response_s": start_elapsed,
            "component_setup_pre_manifest_s": float("inf"),
            "receipt_issue_s": float("inf"),
            "setup_bill": -1,
            "setup_empty_calls": -1,
            "sequence": sequence,
            "predictions": predictions,
            "outputs": [],
            "raw_sources": {},
        }

    setup_operations = manifest["setup_operations"]
    setup_empty_calls = int(setup_operations.get("empty", {}).get("calls", -1))
    receipt_stable = bool(receipt_bytes) and all(
        value == initial_rank_bytes for value in receipt_bytes
    )
    workspace_stable = (
        len(workspace_snapshots) == 3
        and all(int(item["bytes_read"]) > 0 for item in workspace_snapshots)
        and all(bool(item["identity_stable"]) for item in predictions)
    )
    endpoint_bitwise = len(raw_outputs) == 3 and all(
        raw_outputs[0][name] == raw_outputs[2][name]
        for name in ("aaaa", "aaab", "aabb")
    )
    raw_sources = {}
    for label, raw in zip(sequence, raw_outputs):
        raw_sources.setdefault(label, raw)

    setup_ok = (
        runtime_hashes == PINNED_HASHES
        and start_elapsed < OFFICIAL_START_CAP_S
        and int(manifest["setup_bill"]) == EXPECTED_SETUP_RECEIPT_BILL
        and setup_empty_calls == 18
        and float(manifest["setup_pre_manifest_s"]) < OFFICIAL_START_CAP_S
        and float(manifest["receipt_issue_s"]) < RECEIPT_ISSUE_CAP_S
        and initial_receipt is not None
        and all(initial_receipt["law"].values())
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
        and prediction["rss_mib"] < RSS_CAP_MIB
        for prediction in predictions
    )
    if failure is None and not setup_ok:
        failure = "RuntimeError: frozen M235 same-worker setup gate failed"
    if failure is None and not prediction_ok:
        failure = "RuntimeError: frozen M235 same-worker prediction gate failed"
    if failure is None and not receipt_stable:
        failure = "RuntimeError: remote setup receipt bytes changed"
    if failure is None and not workspace_stable:
        failure = "RuntimeError: remote workspace snapshot failed"
    if failure is None and not endpoint_bitwise:
        failure = "RuntimeError: remote repeated endpoint is not bitwise identical"

    return {
        "failure": failure,
        "same_worker_transport": True,
        "transport": "Win32 ReadProcessMemory",
        "pair_index": pair_index,
        "order": order,
        "setup_seed": setup_seed,
        "first_source_seed": first_seed,
        "second_source_seed": second_seed,
        "sequence": sequence,
        "official_worker_pid": worker_pid,
        "official_launcher_pid": launcher_pid,
        "official_start_response_s": start_elapsed,
        "component_setup_pre_manifest_s": float(manifest["setup_pre_manifest_s"]),
        "receipt_issue_s": float(manifest["receipt_issue_s"]),
        "setup_bill": int(manifest["setup_bill"]),
        "setup_empty_calls": setup_empty_calls,
        "setup_operations": setup_operations,
        "runtime_hashes": runtime_hashes,
        "runtime_hashes_match": runtime_hashes == PINNED_HASHES,
        "receipt_law": initial_receipt["law"] if initial_receipt is not None else {},
        "receipt_stable": receipt_stable,
        "workspace_stable": workspace_stable,
        "receipt_snapshots": (
            [
                initial_receipt["rank_sha256"],
                *[hashlib.sha256(value).hexdigest() for value in receipt_bytes],
            ]
            if initial_receipt is not None
            else []
        ),
        "workspace_snapshots": workspace_snapshots,
        "endpoint_bitwise_equal": endpoint_bitwise,
        "predictions": predictions,
        "outputs": [
            {
                "label": label,
                "sha256": prediction["sha256"],
                "arrays": prediction["arrays"],
            }
            for label, prediction in zip(sequence, predictions)
        ],
        "raw_sources": raw_sources,
    }


def _save_raw_sources(raw_dir: Path, result: dict[str, object]) -> dict[str, object]:
    raw_dir.mkdir(parents=True, exist_ok=True)
    paths = {}
    for label, raw in result["raw_sources"].items():
        label_paths = {}
        for name, payload in raw.items():
            path = raw_dir / f"{result['order']}_{label}_{name}.bin"
            path.write_bytes(payload)
            label_paths[name] = str(path)
        paths[label] = label_paths
    return paths


def _jsonable(result: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in result.items() if key != "raw_sources"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pair-index", type=int, required=True)
    parser.add_argument("--order", choices=("primary", "mirror"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--raw-dir", type=Path, required=True)
    args = parser.parse_args()
    result = run_process(pair_index=args.pair_index, order=args.order)
    payload = _jsonable(result)
    payload["raw_paths"] = _save_raw_sources(args.raw_dir, result)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "output": str(args.output),
                "failure": payload["failure"],
                "order": args.order,
                "pair_index": args.pair_index,
                "worker_pid": payload["official_worker_pid"],
            },
            sort_keys=True,
        )
    )
    raise SystemExit(0 if payload["failure"] is None else 1)


if __name__ == "__main__":
    main()
