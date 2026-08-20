"""M237 host runner with write-ahead intent and durable result publication.

Import is inert.  Only an explicit ``run_durable_once`` or script invocation
can create the frozen execution artifacts or start the one authorized worker.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import tempfile
import time

from whestbench import SetupContext
from whestbench.runner import EstimatorEntrypoint, ResourceLimits, SubprocessRunner


HERE = Path(__file__).resolve().parent
BASE = HERE.parent
M236_DIR = BASE / "m236_layer_batched_m212_m235"
if str(M236_DIR) not in sys.path:
    sys.path.insert(0, str(M236_DIR))
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import m237_durable_native_receipt as durable  # noqa: E402
import run_m236_native_process as parent  # noqa: E402


WIDTH = parent.WIDTH
LAYERS = parent.LAYERS
SUBSET_ROWS = parent.SUBSET_ROWS
SETUP_SEED = parent.SETUP_SEED
SOURCE_SEEDS = dict(parent.SOURCE_SEEDS)
SEQUENCE = tuple(parent.SEQUENCE)
EXPECTED_SETUP_RECEIPT_BILL = parent.EXPECTED_SETUP_RECEIPT_BILL
EXPECTED_M212_BILL = parent.EXPECTED_M212_BILL
EXPECTED_M235_BILL = parent.EXPECTED_M235_BILL
EXPECTED_COMBINED_BILL = parent.EXPECTED_COMBINED_BILL
CONSERVATIVE_COMBINED_BILL = parent.CONSERVATIVE_COMBINED_BILL
M235_WALL_CAP_S = parent.M235_WALL_CAP_S
LAWFUL_COMBINED_CAP_S = parent.LAWFUL_COMBINED_CAP_S
CONSERVATIVE_COMBINED_CAP_S = parent.CONSERVATIVE_COMBINED_CAP_S
OFFICIAL_START_CAP_S = parent.OFFICIAL_START_CAP_S
OFFICIAL_SETUP_TIMEOUT_S = parent.OFFICIAL_SETUP_TIMEOUT_S
RSS_CAP_MIB = parent.RSS_CAP_MIB


FROZEN_INPUT_HASHES = {
    HERE / "M237_PREDECLARATION_20260809.md": "02934C3A34D9EF9F80CE9FCAC27A9F179A96FB200493E6BC01661765F1FBCBE8",
    HERE / "M237_FROZEN_MANIFEST_20260809.json": "9E68B52AF4CBA5B8AE0B93388029637A347045BE0A5D16B69ED004A4A0DE577D",
    HERE / "M237_PREIMPLEMENTATION_ERRATUM1_20260809.md": "2A1A083C2FEDE8239F379FA0565D86845DEA1C45F6A765C84F9A37E6867BCA72",
    M236_DIR / "m236_layer_batched_m212_m235.py": "6C9E9AF9727722CB6ADE5E1CDA56D3F7A0E7BF82EF35EBDAEFA8AA883A854B75",
    M236_DIR / "m236_official_setup_estimator.py": "18D60E0FC02D034CC0E0006CFEDFA15E9188F59697C21294BD53B501AA9BFB25",
    M236_DIR / "run_m236_native_process.py": "CFC797EFE73CF5CD16D022E60983BBC84FDB707907D01FE035DDCD5997DCF675",
    M236_DIR / "test_m236_block8_contract.py": "5E2DE041D68B0B07B437D5362D26195D4F7C7C5A1A45058E900BB4BB3AD4B722",
    M236_DIR / "test_m236_native_contract.py": "FED9175D374BAC53D2C03E01A405980F5DDE2AD93165CF5E453936B8B1BFB84F",
    M236_DIR / "M236_NATIVE_ONE_PROCESS_RESULT_20260809.json": "FF69106F5115B5EF68FBDE3683F27BFB341E18BD85594416EAC6708D31AF7969",
    M236_DIR / "M236_DISPOSITION_20260809.md": "030E7550D94EA3EF740880B86A3CF890539AE55D47AC115A1BB0EE215C22E741",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest().upper()


def verify_frozen_inputs() -> dict[str, bool]:
    return {
        str(path): _sha256(path) == expected
        for path, expected in FROZEN_INPUT_HASHES.items()
    }


def _intent_payload(result_path: Path) -> dict[str, object]:
    runner_hash = _sha256(Path(__file__).resolve())
    return {
        "candidate": "M237 durable write-ahead receipt for frozen B=8 compiler",
        "date": "2026-08-09",
        "status": "LAUNCH_INTENT_ONLY",
        "invocation_count": 1,
        "setup_seed": SETUP_SEED,
        "source_seeds": SOURCE_SEEDS,
        "sequence": list(SEQUENCE),
        "result_path": str(Path(result_path).resolve()),
        "runner_sha256": runner_hash,
        "entrypoint": str((M236_DIR / "m236_official_setup_estimator.py").resolve()),
        "frozen_inputs": {
            str(path.resolve()): expected for path, expected in FROZEN_INPUT_HASHES.items()
        },
        "resource_limits": {
            "setup_timeout_s": OFFICIAL_SETUP_TIMEOUT_S,
            "start_response_strict_lt_s": OFFICIAL_START_CAP_S,
            "predict_timeout_s": 60.0,
            "worker_limit_mib": 512,
            "rss_acceptance_strict_lt_mib": RSS_CAP_MIB,
            "flop_budget": 272_000_000_000,
            "wall_time_limit_s": 60.0,
        },
        "bills": {
            "m212": EXPECTED_M212_BILL,
            "m235": EXPECTED_M235_BILL,
            "combined": EXPECTED_COMBINED_BILL,
        },
        "wall_caps_s": {
            "m235_component": M235_WALL_CAP_S,
            "lawful_combined": LAWFUL_COMBINED_CAP_S,
            "conservative_combined": CONSERVATIVE_COMBINED_CAP_S,
        },
    }


def _run_live_scratch(scratch_path: Path) -> dict[str, object]:
    """Copy of frozen M236 host orchestration, with caller-owned live scratch."""

    fixtures = {label: parent._fixture(seed) for label, seed in SOURCE_SEEDS.items()}
    runtime_hashes = parent.transport._runtime_hashes()
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
    try:
        started = time.perf_counter()
        official.start(
            EstimatorEntrypoint(
                file_path=M236_DIR / "m236_official_setup_estimator.py",
                class_name="Estimator",
            ),
            SetupContext(
                width=WIDTH,
                depth=32,
                flop_budget=272_000_000_000,
                api_version="2.0",
                scratch_dir=str(scratch_path),
                submission_dir=str(M236_DIR),
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
            raise RuntimeError("official M237 worker is not alive after start")
        launcher_pid = int(official._process.pid)
        manifest = json.loads(
            (scratch_path / "m236_worker_manifest.json").read_text(encoding="utf-8")
        )
        worker_pid = int(manifest["worker_pid"])
        handle = parent.transport._open_worker(worker_pid)
        try:
            initial_receipt, initial_rank_bytes, _ = parent.transport._receipt_snapshot(
                handle, manifest
            )
            for prediction_index, label in enumerate(SEQUENCE):
                prediction, raw, rank_bytes = parent._prediction_receipt(
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
            parent.transport._close_worker_handle(handle)
    except Exception as exc:
        failure = f"{type(exc).__name__}: {exc}"
    finally:
        official.close()

    if manifest is None:
        return {
            "candidate": "M237 durable write-ahead receipt for frozen B=8 compiler",
            "status": "KILLED_NATIVE_START",
            "failure": failure or "RuntimeError: missing M236 worker manifest",
            "g0_opened": False,
            "native_aggregate_opened": False,
            "same_worker_transport": False,
            "official_worker_pid": worker_pid,
            "official_launcher_pid": launcher_pid,
            "official_start_response_s": start_elapsed,
            "predictions": predictions,
        }

    setup_operations = manifest["setup_operations"]
    setup_empty_calls = int(setup_operations.get("empty", {}).get("calls", -1))
    alias_law = parent._alias_law(manifest)
    receipt_stable = bool(receipt_bytes) and all(
        value == initial_rank_bytes for value in receipt_bytes
    )
    endpoint_bitwise = len(raw_outputs) == 3 and all(
        raw_outputs[0][name] == raw_outputs[2][name]
        for name in ("aaaa", "aaab", "aabb")
    )
    setup_ok = (
        runtime_hashes == parent.transport.PINNED_HASHES
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
        failure = "RuntimeError: frozen M237 same-worker setup gate failed"
    if failure is None and not prediction_ok:
        failure = "RuntimeError: frozen M237 same-worker prediction gate failed"
    if failure is None and not receipt_stable:
        failure = "RuntimeError: remote M237 receipt bytes changed"
    if failure is None and not endpoint_bitwise:
        failure = "RuntimeError: remote M237 A replay is not bitwise identical"
    status = "PASS_NATIVE_ONE_PROCESS" if failure is None else "KILLED_FROZEN_NATIVE_GATE"
    return {
        "candidate": "M237 durable write-ahead receipt for frozen B=8 compiler",
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
        "runtime_hashes_match": runtime_hashes == parent.transport.PINNED_HASHES,
        "receipt_law": initial_receipt["law"] if initial_receipt else {},
        "receipt_stable": receipt_stable,
        "alias_law": alias_law,
        "allocation_ledger": manifest["allocation_ledger"],
        "endpoint_bitwise_equal": endpoint_bitwise,
        "predictions": predictions,
        "outputs": [
            {
                "label": label,
                "sha256": prediction["sha256"],
                "arrays": prediction["arrays"],
            }
            for label, prediction in zip(SEQUENCE, predictions, strict=True)
        ],
    }


def run_durable_once(directory: Path = HERE) -> dict[str, object]:
    """Create intent, run once, and publish one complete durable result."""

    root = Path(directory)
    verified = verify_frozen_inputs()
    if not all(verified.values()):
        raise RuntimeError("M237 frozen M236 input hash mismatch")
    paths = durable.assert_execution_paths_absent(root)
    probe_receipt = durable.hardlink_preflight(root)
    intent_payload = _intent_payload(paths["result"])
    intent_receipt = durable.write_launch_intent_exclusive(
        paths["intent"], intent_payload
    )
    with tempfile.TemporaryDirectory(prefix="m237_seed0_primary_") as raw_scratch:
        result = _run_live_scratch(Path(raw_scratch))
        result["m237_transport"] = {
            "intent_sha256": intent_receipt["sha256"],
            "probe_sha256": probe_receipt["sha256"],
            "runner_sha256": _sha256(Path(__file__).resolve()),
            "frozen_inputs": verified,
        }
        publication = durable.publish_native_result(
            temp_path=paths["result_temp"],
            final_path=paths["result"],
            payload=result,
        )
        reopened = json.loads(paths["result"].read_text(encoding="utf-8"))
        if reopened != result or publication["parsed"] != result:
            raise IOError("M237 durable result parse mismatch")
    return {
        "result": reopened,
        "result_path": str(paths["result"]),
        "result_sha256": publication["sha256"],
        "intent_path": str(paths["intent"]),
        "intent_sha256": intent_receipt["sha256"],
    }


def main() -> None:
    print(json.dumps(run_durable_once(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
