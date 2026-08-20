"""One-shot authority-only E7 fixture materializer for M244.

This file is not candidate, test, or native-gate code.  It imports no M244 or
other experiment module.  When (and only when) separately authorized, its
``main`` writes a durable exclusive intent before importing NumPy, materializes
the frozen E3--E6 fixtures once, and publishes one canonical no-overwrite JSON
result.  An intent burns the run: no retry or second materialization exists.

Static inspection is the only authorized activity before the independent
audit named by ``M244_E7_STATIC_AUDIT_CONTRACT_20260809.json`` passes.
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import time
import traceback
from typing import Any, Mapping


HERE = Path(__file__).resolve().parent
REPOSITORY_ROOT = HERE.parents[3]
WORKSPACE_ROOT = REPOSITORY_ROOT.parent.parent
SOURCE = Path(__file__).resolve()
PINNED_INTERPRETER = WORKSPACE_ROOT / "work" / "whest-v014" / "Scripts" / "python.exe"

INTENT = HERE / "M244_E7_FIXTURE_MATERIALIZATION_INTENT_20260809.json"
RESULT = HERE / "M244_E7_FIXTURE_AUTHORITY_20260809.json"
RESULT_TEMP = HERE / ".M244_E7_FIXTURE_AUTHORITY_20260809.json.tmp"
POSTPUBLICATION_RECEIPT = HERE / "M244_E7_POSTPUBLICATION_BINDING_RECEIPT_20260809.json"
POSTPUBLICATION_RECEIPT_TEMP = HERE / ".M244_E7_POSTPUBLICATION_BINDING_RECEIPT_20260809.json.tmp"
STATIC_AUDIT_CONTRACT = HERE / "M244_E7_STATIC_AUDIT_CONTRACT_20260809.json"
STATIC_VALIDATION_RECEIPT = HERE / "M244_E7_STATIC_VALIDATION_RECEIPT_20260809.json"

AUTHORITY_COMMIT = "75c87485d3b55fddc50859d29e73e5f293a4bbad"
EXPECTED_NUMPY_VERSION = "2.4.6"
WALL_CAP_SECONDS = 30.0
PROCESS_PEAK_CAP_BYTES = 256 * 1024 * 1024
STATIC_PASS_VERDICT = "PASS_STATIC_E7_MATERIALIZER_ONLY"

THREAD_ENVIRONMENT = {
    "BLIS_NUM_THREADS": "1",
    "MKL_DYNAMIC": "FALSE",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "OMP_DYNAMIC": "FALSE",
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
}

AUTHORITY_SHA256 = {
    "M244_PREDECLARATION_20260809.md":
        "23ca4ddec96d33f2e8430e887b0c9194bdda72ea130c21a2b1285ab02057f181",
    "M244_FROZEN_MANIFEST_20260809.json":
        "2ed0d334949121f46b00d0d0c75c903056cd841c0b071ab62816073549b856ca",
    "M244_SHA256SUMS_20260809.txt":
        "e8b1a0774cf3e08aa2c1212a2e97949a66f8ffa20c836a43a8d7c9f79d041dc2",
    "M244_PREIMPLEMENTATION_ERRATUM1_20260809.md":
        "8063659ab51823bb1c6a5e6ddb591034809fc764ad941e1f5ebe29d1ad9252d0",
    "M244_FROZEN_MANIFEST_V2_20260809.json":
        "47168c11d6cc60ed6df8cdf304268ab0ca17f65f00cce0bd475c1ead452a1b6d",
    "M244_SHA256SUMS_V2_20260809.txt":
        "cdfb6fdb4668d9279e85d9ae56d23d74d4c1d0dd62533eba19cbf91d0b8bd8b7",
}

PARENT_SHA256 = {
    "corpus/whestbench/experiments/m125_source_batched_forward_tangent/m125_forward_tangent.py":
        "fbc9fe32357801b22f0313d4043022e81e2764ff3bf4be94f0dfe3ddb3d1ed32",
    "corpus/whestbench/experiments/m125_source_batched_forward_tangent/PRETHEORY.md":
        "5a6b5b96c74093b5fd90bdd475e86d5aaac68df4770ca807fae41bce33b7ad9c",
    "corpus/whestbench/experiments/m178_certified_phi2_owent/m178_certified_phi2_owent.py":
        "fa3614a22c2250f69f4d891834cc1e7ca6bd8874d67575b87c7d3fa8598f1c5c",
    "corpus/whestbench/experiments/m179_background_archive_producer/m179_jacobian_archive.py":
        "29da770375f6cb15cf70b0f797b09d4775652178ff86ff5b44ccdaaefd3e01de",
    "corpus/whestbench/experiments/m179_background_archive_producer/m179_background_producer.py":
        "a74a6b0b2807c2b1bc0e38777ba542e3fda196d45f7f436ce12e44fd5cfa4012",
    "corpus/whestbench/experiments/m179_background_archive_producer/m179_relu_pair_assembly.py":
        "5f229e2993bf82f014735d3bab7f72091068e1acb6d513a4209b089a01417a00",
    "corpus/whestbench/experiments/m179_background_archive_producer/m179_metering.py":
        "ab5db34dd5b3eb4d62b7855515e7a19b8134a99ba3261f82cb93ed1650bbca07",
    "corpus/whestbench/experiments/m179_background_archive_producer/M179_FROZEN_MANIFEST_20260807.json":
        "b1eed31f44be55ac3b1d2ce5882346537aa96d2fe4edabbb9467aff971153eb0",
    "corpus/whestbench/experiments/m199_composed_cost_reconciliation/m199_cost_ledger.json":
        "b853e494f2f507dede144c58149db7d0c05424745eb21cc3ad7f23a4d551f363",
    "corpus/whestbench/experiments/m199_composed_cost_reconciliation/M199_RESULTS_20260809.md":
        "9030ddb1e41c07ecdbae442df436268250c9500909b0195a30f65afcb7f1963e",
    "corpus/whestbench/experiments/m200_streaming_overlap_fixture/m200_streaming_overlap.py":
        "b26207625f0a2b7b72a46e8694ef53030f1e887b5e06b35efd897fd410fadfee",
    "corpus/whestbench/experiments/m200_streaming_overlap_fixture/M200_FROZEN_INDEX_ERRATUM_20260809.md":
        "c87677935c45305c4c2085eb30d66b133f60bf73eb2414b70c062c5d8410ebfd",
    "corpus/whestbench/experiments/m200_streaming_overlap_fixture/M200_FROZEN_MANIFEST_20260809.json":
        "a39773814c57ed7a9d52e778ebea218023e5141643273dcc45e21b14a19a1e7d",
    "corpus/whestbench/experiments/m206_m204_native_replacement_audit/M206_POSTHOC_ADVERSARIAL_AUDIT_20260809.md":
        "11c9bc785a57e77852358bfa367928198fb50e84b731e84e5fe526f675893ca7",
    "corpus/whestbench/experiments/m243_event_local_q4_source_premise/M243_DISPOSITION_20260809.md":
        "238e7bfb70a86ca8c8a66a1a737d3376d4f4efa0a12e15d484acbcb442af3667",
}

RUNTIME_SHA256 = {
    "work/whest-v014/Lib/site-packages/flopscope/_flops.py":
        "bbdad83348b7ce7b63c9d8da66512c40c69e055c653d24687e62132bd34220c2",
    "work/whest-v014/Lib/site-packages/flopscope/numpy/__init__.py":
        "33edacfc6ca01866d4f558e3a43f8fadfd6a2c0efdbc4e4712acc1d839ad4e2f",
    "work/whest-v014/Lib/site-packages/flopscope/_dtype_billing.py":
        "a73a31f495010b462b2053ef4a9881376fcde1d29a2cd488c8adcf9719d46572",
    "work/whest-v014/Lib/site-packages/flopscope/_pointwise.py":
        "568414bbdb5a5eccb4091c074dde1efd47c823b53e7b3a9253b997617a0a43f9",
    "work/whest-v014/Lib/site-packages/flopscope/data/default_weights.json":
        "9ff1647a0048d2bd23a7a3d76ee0c60bfd3670d03b15ad8bf2b911c2ae19539f",
    "work/whest-v014/Lib/site-packages/flopscope/_weights.py":
        "4fbfe5bf50eb7e86e73372e9d314f86de179aad49bcffd689143570918794f35",
}

GENERIC_SEEDS = {
    1: (244001000, 244001001, 244001002, 244001003),
    2: (244002000, 244002001, 244002002, 244002003),
    3: (244003000, 244003001, 244003002, 244003003),
    5: (244005000, 244005001, 244005002, 244005003),
    7: (244007000, 244007001, 244007002, 244007003),
}
ILL_CONDITIONED = ((2, 244102002), (5, 244105005), (7, 244107007))
TARGET_SEEDS = (244256001, 244256002, 244256003, 244256004, 244256005)
INPUT_NAMES = ("W", "V", "U", "mu", "u")
PROJECTION_NAMES = ("a", "TV", "c", "d", "TU", "q")


def canonical_json_bytes(payload: Mapping[str, Any]) -> bytes:
    """Return the sole M244 E7 JSON representation."""

    rendered = json.dumps(
        dict(payload), allow_nan=False, ensure_ascii=True, indent=2, sort_keys=True
    )
    return (rendered + "\n").encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(Path(path).read_bytes())


def _verify_authority() -> dict[str, str]:
    observed: dict[str, str] = {}
    expected_repository_root = WORKSPACE_ROOT / "publish" / "recursive-estimator-folding"
    if REPOSITORY_ROOT.resolve() != expected_repository_root.resolve():
        raise RuntimeError(
            "BLOCKED_PARENT_DRIFT: repository root does not match the frozen E1 root"
        )
    for name, expected in AUTHORITY_SHA256.items():
        path = HERE / name
        if not path.is_file():
            raise RuntimeError(f"BLOCKED_PARENT_DRIFT: missing authority file {name}")
        value = _sha256_file(path)
        observed[name] = value
        if value != expected:
            raise RuntimeError(
                f"BLOCKED_PARENT_DRIFT: {name}: expected {expected}, observed {value}"
            )
    for relative, expected in PARENT_SHA256.items():
        path = REPOSITORY_ROOT / Path(relative)
        if not path.is_file():
            raise RuntimeError(f"BLOCKED_PARENT_DRIFT: missing parent file {relative}")
        value = _sha256_file(path)
        observed[f"repository::{relative}"] = value
        if value != expected:
            raise RuntimeError(
                f"BLOCKED_PARENT_DRIFT: {relative}: expected {expected}, observed {value}"
            )
    for relative, expected in RUNTIME_SHA256.items():
        path = WORKSPACE_ROOT / Path(relative)
        if not path.is_file():
            raise RuntimeError(f"BLOCKED_PARENT_DRIFT: missing runtime file {relative}")
        value = _sha256_file(path)
        observed[f"workspace::{relative}"] = value
        if value != expected:
            raise RuntimeError(
                f"BLOCKED_PARENT_DRIFT: {relative}: expected {expected}, observed {value}"
            )
    return observed


def _write_exclusive_fsync(path: Path, encoded: bytes) -> None:
    with Path(path).open("xb") as stream:
        stream.write(encoded)
        stream.flush()
        os.fsync(stream.fileno())


def _verify_published(path: Path, expected: bytes) -> dict[str, Any]:
    observed = Path(path).read_bytes()
    if observed != expected:
        raise IOError(f"durable byte mismatch for {path}")
    parsed = json.loads(observed.decode("utf-8"))
    return {
        "bytes": len(observed),
        "parsed_status": parsed.get("materialization_status", parsed.get("status")),
        "path": str(path),
        "sha256": _sha256_bytes(observed),
    }


def _publish_json_exclusive(
    *, temp_path: Path, final_path: Path, payload: Mapping[str, Any]
) -> dict[str, Any]:
    """Publish through same-directory temp + create-if-absent hard link."""

    temporary = Path(temp_path)
    final = Path(final_path)
    if temporary.parent.resolve() != final.parent.resolve():
        raise ValueError("M244 E7 publication paths must share one directory")
    if temporary.exists() or final.exists():
        raise FileExistsError("M244 E7 final or temporary path already exists")
    encoded = canonical_json_bytes(payload)
    _write_exclusive_fsync(temporary, encoded)
    temp_stat = temporary.stat()
    os.link(temporary, final)
    final_stat = final.stat()
    if temp_stat.st_dev != final_stat.st_dev:
        raise IOError("M244 E7 publication crossed devices")
    if hasattr(temp_stat, "st_ino") and temp_stat.st_ino != final_stat.st_ino:
        raise IOError("M244 E7 names are not one hard-linked file")
    receipt = _verify_published(final, encoded)
    if temporary.read_bytes() != encoded:
        raise IOError("M244 E7 temporary bytes changed")
    temporary.unlink()
    if temporary.exists() or not final.exists():
        raise IOError("M244 E7 finalization state mismatch")
    receipt["temporary_removed"] = True
    return receipt


def _windows_peak_working_set_bytes() -> int | None:
    """Read process peak working set using only the Windows stdlib boundary."""

    if os.name != "nt":
        return None

    class ProcessMemoryCounters(ctypes.Structure):
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
        ]

    get_current_process = ctypes.windll.kernel32.GetCurrentProcess
    get_current_process.argtypes = []
    get_current_process.restype = wintypes.HANDLE
    get_process_memory_info = ctypes.windll.psapi.GetProcessMemoryInfo
    get_process_memory_info.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(ProcessMemoryCounters),
        wintypes.DWORD,
    ]
    get_process_memory_info.restype = wintypes.BOOL

    counters = ProcessMemoryCounters()
    counters.cb = ctypes.sizeof(counters)
    handle = get_current_process()
    ok = get_process_memory_info(handle, ctypes.byref(counters), counters.cb)
    if not ok:
        raise OSError("GetProcessMemoryInfo failed")
    return int(counters.PeakWorkingSetSize)


def _freeze_thread_environment() -> dict[str, str]:
    """Freeze all common BLAS/OpenMP controls before NumPy is imported."""

    for name, value in THREAD_ENVIRONMENT.items():
        os.environ[name] = value
    observed = {name: os.environ.get(name, "") for name in sorted(THREAD_ENVIRONMENT)}
    if observed != dict(sorted(THREAD_ENVIRONMENT.items())):
        raise RuntimeError("BLOCKED_PARENT_DRIFT: one-thread environment did not freeze")
    return observed


def _verify_static_validation(
    *, source_sha256: str, contract_sha256: str
) -> dict[str, Any]:
    """Require a canonical committed two-reviewer PASS before intent."""

    if not STATIC_VALIDATION_RECEIPT.is_file():
        raise FileNotFoundError(
            "BLOCKED_STATIC_AUDIT: M244 E7 static validation receipt is absent"
        )
    encoded = STATIC_VALIDATION_RECEIPT.read_bytes()
    payload = json.loads(encoded.decode("utf-8"))
    if not isinstance(payload, dict) or canonical_json_bytes(payload) != encoded:
        raise RuntimeError("BLOCKED_STATIC_AUDIT: validation receipt is not canonical JSON")
    if payload.get("artifact") != "M244_E7_STATIC_VALIDATION_RECEIPT":
        raise RuntimeError("BLOCKED_STATIC_AUDIT: validation artifact mismatch")
    if payload.get("authority_commit") != AUTHORITY_COMMIT:
        raise RuntimeError("BLOCKED_STATIC_AUDIT: authority commit mismatch")
    if payload.get("freeze_status") != STATIC_PASS_VERDICT:
        raise RuntimeError("BLOCKED_STATIC_AUDIT: freeze verdict is not PASS")
    if payload.get("source_sha256") != source_sha256:
        raise RuntimeError("BLOCKED_STATIC_AUDIT: source hash mismatch")
    if payload.get("static_contract_sha256") != contract_sha256:
        raise RuntimeError("BLOCKED_STATIC_AUDIT: contract hash mismatch")
    if payload.get("no_execution_performed") is not True:
        raise RuntimeError("BLOCKED_STATIC_AUDIT: no-execution declaration absent")
    if payload.get("committed_before_launch") is not True:
        raise RuntimeError("BLOCKED_STATIC_AUDIT: committed-freeze declaration absent")
    reviewers = payload.get("reviewers")
    if not isinstance(reviewers, list) or len(reviewers) < 2:
        raise RuntimeError("BLOCKED_STATIC_AUDIT: fewer than two reviewers")
    reviewer_ids: list[str] = []
    for reviewer in reviewers:
        if not isinstance(reviewer, dict):
            raise RuntimeError("BLOCKED_STATIC_AUDIT: malformed reviewer record")
        reviewer_id = reviewer.get("reviewer_id")
        if not isinstance(reviewer_id, str) or not reviewer_id.strip():
            raise RuntimeError("BLOCKED_STATIC_AUDIT: empty reviewer identity")
        canonical_reviewer_id = reviewer_id.strip().casefold()
        if reviewer_id != canonical_reviewer_id or not all(
            character.isascii()
            and (character.isalnum() or character in "-_")
            for character in reviewer_id
        ):
            raise RuntimeError("BLOCKED_STATIC_AUDIT: noncanonical reviewer identity")
        if reviewer.get("verdict") != STATIC_PASS_VERDICT:
            raise RuntimeError("BLOCKED_STATIC_AUDIT: reviewer verdict is not PASS")
        if reviewer.get("source_sha256") != source_sha256:
            raise RuntimeError("BLOCKED_STATIC_AUDIT: reviewer source hash mismatch")
        if reviewer.get("static_contract_sha256") != contract_sha256:
            raise RuntimeError("BLOCKED_STATIC_AUDIT: reviewer contract hash mismatch")
        reviewer_ids.append(canonical_reviewer_id)
    if len(set(reviewer_ids)) < 2:
        raise RuntimeError("BLOCKED_STATIC_AUDIT: reviewer identities are not distinct")
    declared_count = payload.get("independent_reviewer_count")
    if declared_count != len(set(reviewer_ids)):
        raise RuntimeError("BLOCKED_STATIC_AUDIT: reviewer count mismatch")
    return {
        "independent_reviewer_count": declared_count,
        "path": str(STATIC_VALIDATION_RECEIPT),
        "reviewer_ids": sorted(set(reviewer_ids)),
        "sha256": _sha256_bytes(encoded),
    }


def _require(condition: bool, message: str) -> None:
    if not bool(condition):
        raise RuntimeError(message)


def _repr_scalar(value: Any, kind: str) -> str:
    if kind == "f":
        return repr(float(value))
    if kind in ("i", "u"):
        return str(int(value))
    if kind == "b":
        return "True" if bool(value) else "False"
    raise TypeError(f"unsupported receipt dtype kind {kind!r}")


def _array_receipt(np: Any, value: Any, *, include_values: bool) -> dict[str, Any]:
    array = np.asarray(value)
    encoded = array.tobytes(order="C")
    receipt: dict[str, Any] = {
        "c_order_nbytes": len(encoded),
        "c_order_sha256": _sha256_bytes(encoded),
        "dtype_str": array.dtype.str,
        "shape": [int(item) for item in array.shape],
        "source_c_contiguous": bool(array.flags.c_contiguous),
    }
    if include_values:
        receipt["flat_values_repr_c_order"] = [
            _repr_scalar(item, array.dtype.kind) for item in array.ravel(order="C")
        ]
    return receipt


def _array_map_receipt(
    np: Any, arrays: Mapping[str, Any], *, include_values: bool
) -> dict[str, Any]:
    return {
        name: _array_receipt(np, arrays[name], include_values=include_values)
        for name in sorted(arrays)
    }


def _array_bundle_sha256(np: Any, sections: Mapping[str, Mapping[str, Any]]) -> str:
    digest = hashlib.sha256()
    for section_name in sorted(sections):
        for array_name in sorted(sections[section_name]):
            array = np.asarray(sections[section_name][array_name])
            for token in (section_name, array_name, array.dtype.str, repr(array.shape)):
                encoded = token.encode("utf-8")
                digest.update(len(encoded).to_bytes(8, "little"))
                digest.update(encoded)
            raw = array.tobytes(order="C")
            digest.update(len(raw).to_bytes(8, "little"))
            digest.update(raw)
    return digest.hexdigest()


def _all_finite(np: Any, arrays: Mapping[str, Any]) -> bool:
    return all(bool(np.all(np.isfinite(np.asarray(value)))) for value in arrays.values())


def _projection(np: Any, inputs: Mapping[str, Any]) -> dict[str, Any]:
    W = inputs["W"]
    V = inputs["V"]
    U = inputs["U"]
    mu = inputs["mu"]
    u = inputs["u"]
    a = mu @ W
    TV = V @ W
    c = np.sum(W * TV, axis=0, dtype=np.float64)
    d = u @ W
    TU = U @ W
    q = np.sum(W * TU, axis=0, dtype=np.float64)
    c = np.asarray(c, dtype=np.float64).copy(order="C")
    c[c == 0.0] = 0.0
    return {"a": a, "TV": TV, "c": c, "d": d, "TU": TU, "q": q}


def _generic_constructor(np: Any, n: int, seed: int) -> tuple[dict[str, Any], dict[str, Any]]:
    """Literal E3 constructor, including its exact draw order."""

    rng = np.random.Generator(np.random.Philox(seed))

    raw_w = rng.standard_normal((n, n), dtype=np.float64)
    Qw, Rw = np.linalg.qr(raw_w)
    sign_w = np.where(np.diag(Rw) < 0.0, -1.0, 1.0)
    Qw = Qw * sign_w[None, :]
    scale_w = rng.uniform(0.65, 1.35, size=n)
    W = Qw * scale_w[None, :]

    raw_v = rng.normal(0.0, 0.08, size=(n, n))
    off_v = 0.5 * (raw_v + raw_v.T)
    np.fill_diagonal(off_v, 0.0)
    diag_v = rng.uniform(0.65, 1.25, size=n) + np.sum(np.abs(off_v), axis=1)
    V = off_v.copy()
    np.fill_diagonal(V, diag_v)

    raw_qu = rng.standard_normal((n, n), dtype=np.float64)
    Qu, Ru = np.linalg.qr(raw_qu)
    sign_u = np.where(np.diag(Ru) < 0.0, -1.0, 1.0)
    Qu = Qu * sign_u[None, :]
    if n == 1:
        eig_u = np.asarray([-0.625 if seed % 2 else 0.625], dtype=np.float64)
    else:
        eig_u = np.linspace(-0.9, 0.9, n, dtype=np.float64)
        if n % 2:
            eig_u[n // 2] = 0.15
    diag_eig_u = np.diag(eig_u)
    U = Qu @ diag_eig_u @ Qu.T
    U = 0.5 * (U + U.T)

    mu = rng.uniform(-0.9, 0.9, size=n)
    u = rng.normal(0.0, 0.35, size=n)

    inputs = {"W": W, "V": V, "U": U, "mu": mu, "u": u}
    trace = {
        "Qw": Qw,
        "Qu": Qu,
        "Rw": Rw,
        "Ru": Ru,
        "diag_eig_u": diag_eig_u,
        "diag_v": diag_v,
        "eig_u": eig_u,
        "off_v": off_v,
        "raw_qu": raw_qu,
        "raw_v": raw_v,
        "raw_w": raw_w,
        "scale_w": scale_w,
        "sign_u": sign_u,
        "sign_w": sign_w,
    }
    return inputs, trace


def _generic_diagnostics(np: Any, n: int, inputs: Mapping[str, Any], trace: Mapping[str, Any]) -> dict[str, Any]:
    shapes_exact = (
        inputs["W"].shape == (n, n)
        and inputs["V"].shape == (n, n)
        and inputs["U"].shape == (n, n)
        and inputs["mu"].shape == (n,)
        and inputs["u"].shape == (n,)
    )
    dtypes_exact = all(np.asarray(inputs[name]).dtype == np.dtype(np.float64) for name in INPUT_NAMES)
    v_bitwise_symmetric = bool(np.array_equal(inputs["V"], inputs["V"].T))
    u_bitwise_symmetric = bool(np.array_equal(inputs["U"], inputs["U"].T))
    dominance = np.diag(inputs["V"]) - (
        np.sum(np.abs(inputs["V"]), axis=1) - np.abs(np.diag(inputs["V"]))
    )
    min_dominance = float(np.min(dominance))
    min_v_eigenvalue = float(np.min(np.linalg.eigvalsh(inputs["V"])))
    rank_w = int(np.linalg.matrix_rank(inputs["W"]))
    eig_u = trace["eig_u"]
    eig_u_has_both_signs = bool(np.any(eig_u < 0.0) and np.any(eig_u > 0.0))
    finite = _all_finite(np, inputs) and _all_finite(np, trace)
    _require(shapes_exact, "E3 exact shape assertion failed")
    _require(dtypes_exact, "E3 exact dtype assertion failed")
    _require(finite, "E3 finiteness assertion failed")
    _require(v_bitwise_symmetric, "E3 V bitwise symmetry assertion failed")
    _require(u_bitwise_symmetric, "E3 U bitwise symmetry assertion failed")
    _require(min_dominance > 0.0, "E3 V diagonal-dominance assertion failed")
    _require(min_v_eigenvalue > 0.0, "E3 V SPD assertion failed")
    _require(rank_w == n, "E3 W full-rank assertion failed")
    if n >= 2:
        _require(eig_u_has_both_signs, "E3 eig_u sign assertion failed")
    return {
        "all_constructor_arrays_finite": finite,
        "all_input_dtypes_exact_float64": dtypes_exact,
        "all_input_shapes_exact": shapes_exact,
        "eig_u_has_both_signs": eig_u_has_both_signs,
        "eig_u_indefiniteness_required": n >= 2,
        "min_v_diagonal_dominance_margin": min_dominance,
        "min_v_eigenvalue": min_v_eigenvalue,
        "rank_w": rank_w,
        "u_bitwise_symmetric": u_bitwise_symmetric,
        "v_bitwise_symmetric": v_bitwise_symmetric,
    }


def _fixture_record(
    np: Any,
    *,
    fixture_id: str,
    family: str,
    n: int,
    seed: int | None,
    inputs: Mapping[str, Any],
    trace: Mapping[str, Any],
    diagnostics: Mapping[str, Any],
    include_values: bool,
) -> dict[str, Any]:
    projected = _projection(np, inputs)
    _require(_all_finite(np, projected), f"{fixture_id}: nonfinite projection diagnostic")
    _require(bool(np.all(projected["c"] >= 0.0)), f"{fixture_id}: negative projected variance")
    sections = {"constructor_trace": trace, "inputs": inputs, "projection": projected}
    return {
        "array_bundle_sha256": _array_bundle_sha256(np, sections),
        "constructor_trace": _array_map_receipt(np, trace, include_values=include_values),
        "diagnostics": dict(diagnostics),
        "family": family,
        "fixture_id": fixture_id,
        "inputs": _array_map_receipt(np, inputs, include_values=include_values),
        "projection": _array_map_receipt(np, projected, include_values=include_values),
        "seed": seed,
        "width": n,
    }


def _within(np: Any, observed: Any, expected: Any) -> bool:
    observed_array = np.asarray(observed, dtype=np.float64)
    expected_array = np.asarray(expected, dtype=np.float64)
    bound = 5e-12 + 5e-11 * np.abs(expected_array)
    return bool(np.all(np.abs(observed_array - expected_array) <= bound))


def _hidden_transform(
    np: Any,
    *,
    base_id: str,
    kind: str,
    inputs: Mapping[str, Any],
    S: Any,
    include_values: bool,
) -> dict[str, Any]:
    transformed = {
        "mu": inputs["mu"] @ S,
        "V": S.T @ inputs["V"] @ S,
        "u": inputs["u"] @ S,
        "U": S.T @ inputs["U"] @ S,
        "W": np.linalg.solve(S, inputs["W"]),
    }
    base_projection = _projection(np, inputs)
    transformed_projection = _projection(np, transformed)
    invariance = {
        name: _within(np, transformed_projection[name], base_projection[name])
        for name in ("a", "c", "d", "q")
    }
    _require(all(invariance.values()), f"E6 {kind} invariance assertion failed")
    n = int(inputs["W"].shape[0])
    sections = {"inputs": transformed, "projection": transformed_projection, "transform": {"S": S}}
    return {
        "array_bundle_sha256": _array_bundle_sha256(np, sections),
        "base_fixture_id": base_id,
        "diagnostics": {
            "observable_invariance_within_frozen_tolerance": invariance,
            "nontrivial_probe": n > 1,
        },
        "family": "hidden_transform",
        "fixture_id": f"{base_id}__{kind}",
        "inputs": _array_map_receipt(np, transformed, include_values=include_values),
        "projection": _array_map_receipt(np, transformed_projection, include_values=include_values),
        "transform": _array_map_receipt(np, {"S": S}, include_values=include_values),
        "transform_kind": kind,
        "width": n,
    }


def _output_transform(
    np: Any,
    *,
    base_id: str,
    inputs: Mapping[str, Any],
    include_values: bool,
) -> dict[str, Any]:
    n = int(inputs["W"].shape[0])
    order = np.arange(n - 1, -1, -1, dtype=np.int64)
    transformed = {
        "W": inputs["W"][:, order].copy(order="C"),
        "V": inputs["V"].copy(order="C"),
        "U": inputs["U"].copy(order="C"),
        "mu": inputs["mu"].copy(order="C"),
        "u": inputs["u"].copy(order="C"),
    }
    base_projection = _projection(np, inputs)
    transformed_projection = _projection(np, transformed)
    permutation = {
        name: _within(np, transformed_projection[name], base_projection[name][order])
        for name in ("a", "c", "d", "q")
    }
    _require(all(permutation.values()), "E6 output permutation assertion failed")
    sections = {
        "inputs": transformed,
        "projection": transformed_projection,
        "transform": {"reverse_column_order": order},
    }
    return {
        "array_bundle_sha256": _array_bundle_sha256(np, sections),
        "base_fixture_id": base_id,
        "diagnostics": {
            "nontrivial_probe": n > 1,
            "observable_reverse_permutation_within_frozen_tolerance": permutation,
        },
        "family": "output_transform",
        "fixture_id": f"{base_id}__output_reverse",
        "inputs": _array_map_receipt(np, transformed, include_values=include_values),
        "projection": _array_map_receipt(np, transformed_projection, include_values=include_values),
        "transform": _array_map_receipt(
            np, {"reverse_column_order": order}, include_values=include_values
        ),
        "transform_kind": "reverse_columns",
        "width": n,
    }


def _ill_conditioned_constructor(np: Any, n: int, seed: int) -> tuple[dict[str, Any], dict[str, Any]]:
    """Literal E4 constructor, including its exact draw order."""

    rng = np.random.Generator(np.random.Philox(seed))
    exponents = np.linspace(0.0, -24.0, n, dtype=np.float64)
    vdiag = np.exp2(exponents)
    V = np.diag(vdiag)
    wdiag = rng.uniform(0.8, 1.2, size=n)
    W = np.diag(wdiag)
    sigma_terminal = np.sqrt(vdiag) * np.abs(wdiag)
    alpha_pattern = np.resize(
        np.asarray([-35.0, -8.0, 0.0, 8.0, 35.0], dtype=np.float64), n
    )
    mu = alpha_pattern * np.sqrt(vdiag)
    u = rng.normal(0.0, 0.35, size=n)
    raw_u = rng.normal(0.0, 0.2, size=(n, n))
    U = 0.5 * (raw_u + raw_u.T)
    inputs = {"W": W, "V": V, "U": U, "mu": mu, "u": u}
    trace = {
        "alpha_pattern": alpha_pattern,
        "exponents": exponents,
        "raw_u": raw_u,
        "sigma_terminal": sigma_terminal,
        "vdiag": vdiag,
        "wdiag": wdiag,
    }
    return inputs, trace


def _ill_diagnostics(np: Any, inputs: Mapping[str, Any], trace: Mapping[str, Any]) -> dict[str, Any]:
    projected = _projection(np, inputs)
    observed_alpha = projected["a"] / np.sqrt(projected["c"])
    alpha_error = float(np.max(np.abs(observed_alpha - trace["alpha_pattern"])))
    condition_number = float(np.max(trace["vdiag"]) / np.min(trace["vdiag"]))
    C = inputs["W"].T @ inputs["V"] @ inputs["W"]
    denom = np.sqrt(np.diag(C)[:, None] * np.diag(C)[None, :])
    rho = C / denom
    offdiag = rho.copy()
    np.fill_diagonal(offdiag, 0.0)
    max_abs_rho = float(np.max(np.abs(offdiag)))
    symmetric = bool(
        np.array_equal(inputs["V"], inputs["V"].T)
        and np.array_equal(inputs["U"], inputs["U"].T)
    )
    finite = _all_finite(np, inputs) and _all_finite(np, trace)
    _require(symmetric, "E4 symmetry assertion failed")
    _require(float(np.min(trace["vdiag"])) > 0.0, "E4 positive vdiag assertion failed")
    _require(condition_number >= float(2**20), "E4 condition-number assertion failed")
    _require(alpha_error <= 5e-12, "E4 terminal-alpha assertion failed")
    _require(finite, "E4 finiteness assertion failed")
    _require(max_abs_rho == 0.0, "E4 terminal correlation assertion failed")
    return {
        "all_constructor_and_input_arrays_finite": finite,
        "condition_number_vdiag_ratio": condition_number,
        "exact_symmetry": symmetric,
        "max_abs_terminal_alpha_error": alpha_error,
        "max_abs_terminal_pair_correlation": max_abs_rho,
        "min_vdiag": float(np.min(trace["vdiag"])),
    }


def _canonicalize_exact_zeros(np: Any, value: Any) -> Any:
    result = np.asarray(value, dtype=np.float64).copy(order="C")
    result[result == 0.0] = 0.0
    return result


def _boundary_record(
    np: Any,
    *,
    fixture_id: str,
    kind: str,
    inputs: Mapping[str, Any],
    diagnostics: Mapping[str, Any],
) -> dict[str, Any]:
    projected = _projection(np, inputs)
    canonical = {
        name: _canonicalize_exact_zeros(np, projected[name])
        for name in ("a", "c", "d", "q")
    }
    sections = {"inputs": inputs, "projection": projected, "canonical_zero_probe": canonical}
    return {
        "array_bundle_sha256": _array_bundle_sha256(np, sections),
        "boundary_kind": kind,
        "canonical_zero_probe": _array_map_receipt(np, canonical, include_values=True),
        "diagnostics": dict(diagnostics),
        "family": "boundary_or_structural",
        "fixture_id": fixture_id,
        "inputs": _array_map_receipt(np, inputs, include_values=True),
        "projection": _array_map_receipt(np, projected, include_values=True),
        "width": int(inputs["W"].shape[0]),
    }


def _materialize_boundaries(np: Any) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for n in (2, 3, 5):
        for first_mean, label in ((-0.75, "negative"), (0.75, "positive")):
            W = np.eye(n, dtype=np.float64)
            V = np.diag(np.concatenate((np.asarray([0.0]), np.ones(n - 1))))
            mu = np.full(n, 0.25, dtype=np.float64)
            mu[0] = first_mean
            u = np.linspace(-0.4, 0.4, n, dtype=np.float64)
            U = np.diag(np.linspace(-0.6, 0.6, n, dtype=np.float64))
            inputs = {"W": W, "V": V, "U": U, "mu": mu, "u": u}
            projected = _projection(np, inputs)
            c0 = float(projected["c"][0])
            diagnostics = {
                "a0": float(projected["a"][0]),
                "a0_matches_declared_nonzero_mean": float(projected["a"][0]) == first_mean,
                "c0_exact_positive_zero": c0 == 0.0 and not bool(np.signbit(c0)),
                "differentiable_zero_variance_limit": True,
            }
            _require(all(bool(value) for key, value in diagnostics.items() if key.endswith("mean") or key.endswith("zero")), "E5 zero-variance assertion failed")
            records.append(_boundary_record(
                np,
                fixture_id=f"zero_variance_n{n}_{label}_mean",
                kind="zero_variance_nonzero_mean",
                inputs=inputs,
                diagnostics=diagnostics,
            ))

    for n in (2, 3, 5):
        W = np.eye(n, dtype=np.float64)
        W[:, 0] = 0.0
        V = np.eye(n, dtype=np.float64)
        mu = np.zeros(n, dtype=np.float64)
        u = np.zeros(n, dtype=np.float64)
        U = np.diag(np.linspace(-0.5, 0.5, n, dtype=np.float64))
        inputs = {"W": W, "V": V, "U": U, "mu": mu, "u": u}
        projected = _projection(np, inputs)
        zeros = _canonicalize_exact_zeros(
            np,
            np.asarray([projected[name][0] for name in ("a", "c", "d", "q")]),
        )
        zero_exact = bool(np.array_equal(zeros, np.zeros(4, dtype=np.float64)))
        zero_signs_positive = bool(not np.any(np.signbit(zeros)))
        _require(zero_exact and zero_signs_positive, "E5 structural-zero assertion failed")
        records.append(_boundary_record(
            np,
            fixture_id=f"structural_zero_kink_n{n}",
            kind="structural_zero_kink",
            inputs=inputs,
            diagnostics={
                "a_c_d_q_coordinate_zero_bitwise_positive_zero": zero_exact and zero_signs_positive,
                "classification": "inherited_zero_subgradient_convention_only",
            },
        ))

    inv_sqrt_two = 1.0 / np.sqrt(2.0)
    inputs = {
        "W": np.asarray([[1.0, 1.0], [1.0, -1.0]], dtype=np.float64) * inv_sqrt_two,
        "V": np.eye(2, dtype=np.float64),
        "U": np.asarray([[0.0, 1.0], [1.0, 0.0]], dtype=np.float64),
        "mu": np.zeros(2, dtype=np.float64),
        "u": np.zeros(2, dtype=np.float64),
    }
    projected = _projection(np, inputs)
    diag_u_canonical = _canonicalize_exact_zeros(np, np.diag(inputs["U"]))
    diag_u_zero = bool(
        np.array_equal(diag_u_canonical, np.zeros(2, dtype=np.float64))
        and not np.any(np.signbit(diag_u_canonical))
    )
    q_visible = bool(np.all(projected["q"] != 0.0))
    _require(diag_u_zero and q_visible, "E5 off-diagonal visibility assertion failed")
    records.append(_boundary_record(
        np,
        fixture_id="offdiagonal_visibility_n2",
        kind="offdiagonal_visibility",
        inputs=inputs,
        diagnostics={"diag_u_bitwise_zero": diag_u_zero, "projected_diagonal_all_nonzero": q_visible},
    ))

    inputs = {
        "W": np.eye(3, dtype=np.float64),
        "V": np.eye(3, dtype=np.float64),
        "U": np.asarray([[0.0, 1.0, -2.0], [1.0, 0.0, 3.0], [-2.0, 3.0, 0.0]], dtype=np.float64),
        "mu": np.zeros(3, dtype=np.float64),
        "u": np.zeros(3, dtype=np.float64),
    }
    projected = _projection(np, inputs)
    q_canonical = _canonicalize_exact_zeros(np, projected["q"])
    kernel_exact = bool(np.array_equal(q_canonical, np.zeros(3)) and not np.any(np.signbit(q_canonical)))
    _require(kernel_exact, "E5 terminal-kernel assertion failed")
    records.append(_boundary_record(
        np,
        fixture_id="terminal_kernel_n3",
        kind="terminal_kernel",
        inputs=inputs,
        diagnostics={"projected_diagonal_bitwise_positive_zero": kernel_exact},
    ))

    inputs = {
        "W": np.eye(3, dtype=np.float64),
        "V": np.eye(3, dtype=np.float64),
        "U": np.diag(np.asarray([1.0, -1.0, 0.0], dtype=np.float64)),
        "mu": np.zeros(3, dtype=np.float64),
        "u": np.zeros(3, dtype=np.float64),
    }
    projected = _projection(np, inputs)
    trace_canonical = _canonicalize_exact_zeros(
        np, np.asarray([np.trace(inputs["U"])], dtype=np.float64)
    )
    trace_zero = bool(
        np.array_equal(trace_canonical, np.zeros(1, dtype=np.float64))
        and not np.any(np.signbit(trace_canonical))
    )
    visible = bool(np.any(projected["q"] != 0.0))
    _require(trace_zero and visible, "E5 trace-free visibility assertion failed")
    records.append(_boundary_record(
        np,
        fixture_id="tracefree_visible_n3",
        kind="tracefree_visible",
        inputs=inputs,
        diagnostics={"projected_diagonal_visible": visible, "trace_u_exact_zero": trace_zero},
    ))
    _require(len(records) == 12, "E5 boundary fixture count mismatch")
    return records


def _count_array_receipts(value: Any) -> tuple[int, int]:
    if isinstance(value, dict):
        if "c_order_sha256" in value and "c_order_nbytes" in value:
            return 1, int(value["c_order_nbytes"])
        counts = [_count_array_receipts(item) for item in value.values()]
    elif isinstance(value, list):
        counts = [_count_array_receipts(item) for item in value]
    else:
        counts = []
    return sum(item[0] for item in counts), sum(item[1] for item in counts)


def _materialize(np: Any, *, intent_sha256: str, source_sha256: str, authority: Mapping[str, str]) -> dict[str, Any]:
    generic: list[dict[str, Any]] = []
    transforms: list[dict[str, Any]] = []
    for n, seeds in GENERIC_SEEDS.items():
        for seed in seeds:
            inputs, trace = _generic_constructor(np, n, seed)
            diagnostics = _generic_diagnostics(np, n, inputs, trace)
            base_id = f"generic_n{n}_seed{seed}"
            generic.append(_fixture_record(
                np,
                fixture_id=base_id,
                family="generic_dense",
                n=n,
                seed=seed,
                inputs=inputs,
                trace=trace,
                diagnostics=diagnostics,
                include_values=True,
            ))

            P = np.zeros((n, n), dtype=np.float64)
            rows = np.arange(n, dtype=np.int64)
            P[rows, (rows + 1) % n] = 1.0
            powers = np.asarray([2.0 ** ((r % 3) - 1) for r in range(n)], dtype=np.float64)
            D = np.diag(powers)
            transforms.append(_hidden_transform(
                np, base_id=base_id, kind="hidden_cyclic", inputs=inputs, S=P, include_values=True
            ))
            transforms.append(_hidden_transform(
                np, base_id=base_id, kind="hidden_positive_diagonal", inputs=inputs, S=D, include_values=True
            ))
            transforms.append(_output_transform(
                np, base_id=base_id, inputs=inputs, include_values=True
            ))

    ill: list[dict[str, Any]] = []
    for n, seed in ILL_CONDITIONED:
        inputs, trace = _ill_conditioned_constructor(np, n, seed)
        ill.append(_fixture_record(
            np,
            fixture_id=f"ill_conditioned_n{n}_seed{seed}",
            family="ill_conditioned_spd",
            n=n,
            seed=seed,
            inputs=inputs,
            trace=trace,
            diagnostics=_ill_diagnostics(np, inputs, trace),
            include_values=True,
        ))

    boundaries = _materialize_boundaries(np)

    targets: list[dict[str, Any]] = []
    for seed in TARGET_SEEDS:
        inputs, trace = _generic_constructor(np, 256, seed)
        targets.append(_fixture_record(
            np,
            fixture_id=f"target_n256_seed{seed}",
            family="target_generic_dense",
            n=256,
            seed=seed,
            inputs=inputs,
            trace=trace,
            diagnostics=_generic_diagnostics(np, 256, inputs, trace),
            include_values=False,
        ))

    _require(len(generic) == 20, "E3 generic fixture count mismatch")
    _require(len(ill) == 3, "E4 fixture count mismatch")
    _require(len(transforms) == 60, "E6 transform fixture count mismatch")
    _require(sum(bool(item["diagnostics"]["nontrivial_probe"]) for item in transforms) == 48, "E6 nontrivial transform count mismatch")
    _require(len(targets) == 5, "E6 target fixture count mismatch")

    payload: dict[str, Any] = {
        "artifact": "M244_E7_FIXTURE_AUTHORITY",
        "authority_commit": AUTHORITY_COMMIT,
        "authority_precedence": [
            "M244_PREIMPLEMENTATION_ERRATUM1_20260809.md",
            "M244_FROZEN_MANIFEST_V2_20260809.json",
            "M244_PREDECLARATION_20260809.md",
            "M244_FROZEN_MANIFEST_20260809.json",
        ],
        "authority_sha256": dict(authority),
        "boundary_and_structural_fixtures": boundaries,
        "canonical_json_policy": {
            "allow_nan": False,
            "ensure_ascii": True,
            "indent": 2,
            "newline_terminated": True,
            "sort_keys": True,
        },
        "constructor_contract": {
            "authority_sections": ["E3", "E4", "E5", "E6", "E7"],
            "generic_rng": "numpy.random.Generator(numpy.random.Philox(seed))",
            "retry_or_redraw": False,
            "small_width_values": "flat repr-roundtrippable decimal strings in C order",
            "target_width_values_omitted": True,
        },
        "generic_fixtures": generic,
        "ill_conditioned_fixtures": ill,
        "intent_sha256": intent_sha256,
        "binding_receipt_required": POSTPUBLICATION_RECEIPT.name,
        "materialization_status": "MATERIALIZED_E7_AUTHORITY_PROVISIONAL_PASS",
        "numpy_version": str(np.__version__),
        "platform": {
            "byteorder": sys.byteorder,
            "implementation": platform.python_implementation(),
            "python_version": platform.python_version(),
        },
        "resource_contract": {
            "no_retry": True,
            "process_peak_cap_bytes": PROCESS_PEAK_CAP_BYTES,
            "wall_cap_seconds": WALL_CAP_SECONDS,
        },
        "source_sha256": source_sha256,
        "target_fixtures": targets,
        "transform_fixtures": transforms,
    }
    array_count, represented_nbytes = _count_array_receipts(payload)
    payload["receipt_census"] = {
        "array_receipt_count": array_count,
        "boundary_fixture_count": len(boundaries),
        "generic_fixture_count": len(generic),
        "ill_conditioned_fixture_count": len(ill),
        "nontrivial_transform_fixture_count": 48,
        "represented_array_bytes_including_repeated_receipts": represented_nbytes,
        "target_fixture_count": len(targets),
        "total_fixture_record_count": len(generic) + len(ill) + len(boundaries) + len(transforms) + len(targets),
        "transform_fixture_count": len(transforms),
    }
    return payload


def _normalized_path(path: Path) -> str:
    return os.path.normcase(os.path.abspath(str(path)))


def main() -> int:
    if len(sys.argv) != 1:
        raise RuntimeError("M244 E7 accepts no arguments")
    execution_paths = (
        INTENT,
        RESULT,
        RESULT_TEMP,
        POSTPUBLICATION_RECEIPT,
        POSTPUBLICATION_RECEIPT_TEMP,
    )
    if any(path.exists() for path in execution_paths):
        raise FileExistsError("M244 E7 one-shot path already exists; no retry authorized")
    if _normalized_path(Path(sys.executable)) != _normalized_path(PINNED_INTERPRETER):
        raise RuntimeError(
            f"BLOCKED_PARENT_DRIFT: expected interpreter {PINNED_INTERPRETER}, observed {sys.executable}"
        )

    authority = _verify_authority()
    thread_environment = _freeze_thread_environment()
    source_sha256 = _sha256_file(SOURCE)
    static_contract_sha256 = _sha256_file(STATIC_AUDIT_CONTRACT)
    static_validation = _verify_static_validation(
        source_sha256=source_sha256,
        contract_sha256=static_contract_sha256,
    )
    intent_payload = {
        "artifact": "M244_E7_FIXTURE_MATERIALIZATION_INTENT",
        "authority_commit": AUTHORITY_COMMIT,
        "authority_sha256": authority,
        "command": [str(PINNED_INTERPRETER), str(SOURCE)],
        "expected_numpy_version": EXPECTED_NUMPY_VERSION,
        "intent_precedes_numpy_import": True,
        "no_candidate_or_project_imports": True,
        "no_retry": True,
        "publication": {
            "final": str(RESULT),
            "method": "same-directory exclusive temp, fsync, hard-link create-if-absent, reopen byte verify, temp unlink",
            "temporary": str(RESULT_TEMP),
        },
        "postpublication_binding_receipt": {
            "final": str(POSTPUBLICATION_RECEIPT),
            "required_for_pass": True,
            "temporary": str(POSTPUBLICATION_RECEIPT_TEMP),
        },
        "resource_caps": {
            "process_peak_bytes": PROCESS_PEAK_CAP_BYTES,
            "wall_seconds": WALL_CAP_SECONDS,
        },
        "source_sha256": source_sha256,
        "static_audit_contract_sha256": static_contract_sha256,
        "static_validation": static_validation,
        "status": "MATERIALIZATION_INTENT_ONLY",
        "thread_environment_frozen_before_numpy_import": thread_environment,
    }
    encoded_intent = canonical_json_bytes(intent_payload)
    _write_exclusive_fsync(INTENT, encoded_intent)
    intent_receipt = _verify_published(INTENT, encoded_intent)

    started = time.perf_counter()
    success = False
    try:
        import numpy as np  # sole non-stdlib import; deliberately after durable intent

        _require(np.__version__ == EXPECTED_NUMPY_VERSION, "BLOCKED_PARENT_DRIFT: NumPy version mismatch")
        result_payload = _materialize(
            np,
            intent_sha256=str(intent_receipt["sha256"]),
            source_sha256=source_sha256,
            authority=authority,
        )
        result_payload["static_audit_contract_sha256"] = static_contract_sha256
        result_payload["static_validation_sha256"] = static_validation["sha256"]
        result_payload["thread_environment_frozen_before_numpy_import"] = thread_environment
        elapsed = time.perf_counter() - started
        peak = _windows_peak_working_set_bytes()
        _require(elapsed <= WALL_CAP_SECONDS, "E7 wall cap exceeded")
        _require(peak is not None, "E7 peak working-set measurement unavailable")
        _require(peak <= PROCESS_PEAK_CAP_BYTES, "E7 process peak cap exceeded")
        result_payload["resource_observation"] = {
            "process_peak_bytes": peak,
            "process_peak_within_cap": True,
            "wall_seconds": elapsed,
            "wall_within_cap": True,
        }
        success = True
    except BaseException as exc:
        elapsed = time.perf_counter() - started
        try:
            peak = _windows_peak_working_set_bytes()
        except BaseException:
            peak = None
        result_payload = {
            "artifact": "M244_E7_FIXTURE_AUTHORITY",
            "authority_commit": AUTHORITY_COMMIT,
            "authority_sha256": authority,
            "exception": {
                "message": str(exc),
                "traceback": "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
                "type": type(exc).__name__,
            },
            "intent_sha256": intent_receipt["sha256"],
            "materialization_status": "BLOCKED_E7_MATERIALIZATION_FAILURE",
            "no_partial_fixture_authority": True,
            "no_retry": True,
            "resource_observation": {
                "process_peak_bytes": peak,
                "wall_seconds": elapsed,
            },
            "source_sha256": source_sha256,
            "static_audit_contract_sha256": static_contract_sha256,
            "static_validation_sha256": static_validation["sha256"],
        }

    try:
        result_receipt = _publish_json_exclusive(
            temp_path=RESULT_TEMP,
            final_path=RESULT,
            payload=result_payload,
        )
    except BaseException as exc:
        print(json.dumps({
            "exception_message": str(exc),
            "exception_type": type(exc).__name__,
            "final_exists": RESULT.exists(),
            "no_retry": True,
            "publication_failure": True,
            "temporary_exists": RESULT_TEMP.exists(),
        }, allow_nan=False, sort_keys=True))
        return 2

    postpublication_error = None
    postpublication_elapsed = time.perf_counter() - started
    try:
        postpublication_peak = _windows_peak_working_set_bytes()
        if postpublication_peak is None:
            raise RuntimeError("postpublication peak working-set measurement unavailable")
    except BaseException as exc:
        postpublication_peak = None
        postpublication_error = {
            "message": str(exc),
            "type": type(exc).__name__,
        }
    wall_within_cap = postpublication_elapsed <= WALL_CAP_SECONDS
    peak_within_cap = (
        postpublication_peak is not None
        and postpublication_peak <= PROCESS_PEAK_CAP_BYTES
    )
    binding_pass = bool(
        success
        and postpublication_error is None
        and wall_within_cap
        and peak_within_cap
    )
    binding_payload = {
        "artifact": "M244_E7_POSTPUBLICATION_BINDING_RECEIPT",
        "binding_status": (
            "PASS_E7_FIXTURE_AUTHORITY_BOUND"
            if binding_pass
            else "PERMANENT_FAIL_E7_FIXTURE_AUTHORITY_UNBOUND"
        ),
        "caps_cover_result_publication": True,
        "intent_sha256": intent_receipt["sha256"],
        "no_retry": True,
        "postpublication_error": postpublication_error,
        "process_peak_bytes_through_result_publication": postpublication_peak,
        "process_peak_cap_bytes": PROCESS_PEAK_CAP_BYTES,
        "process_peak_within_cap": peak_within_cap,
        "provisional_materialization_status": result_payload["materialization_status"],
        "result_bytes": result_receipt["bytes"],
        "result_path": str(RESULT),
        "result_sha256": result_receipt["sha256"],
        "source_sha256": source_sha256,
        "static_audit_contract_sha256": static_contract_sha256,
        "static_validation_sha256": static_validation["sha256"],
        "wall_cap_seconds": WALL_CAP_SECONDS,
        "wall_seconds_through_result_publication": postpublication_elapsed,
        "wall_within_cap": wall_within_cap,
    }
    try:
        binding_receipt = _publish_json_exclusive(
            temp_path=POSTPUBLICATION_RECEIPT_TEMP,
            final_path=POSTPUBLICATION_RECEIPT,
            payload=binding_payload,
        )
    except BaseException as exc:
        print(json.dumps({
            "binding_receipt_failure": True,
            "exception_message": str(exc),
            "exception_type": type(exc).__name__,
            "no_retry": True,
            "result_exists": RESULT.exists(),
        }, allow_nan=False, sort_keys=True))
        return 2

    print(json.dumps({
        "binding_receipt": str(POSTPUBLICATION_RECEIPT),
        "binding_receipt_sha256": binding_receipt["sha256"],
        "binding_status": binding_payload["binding_status"],
        "materialization_status": result_payload["materialization_status"],
        "no_retry": True,
        "result": str(RESULT),
        "result_sha256": result_receipt["sha256"],
    }, allow_nan=False, sort_keys=True))
    return 0 if binding_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
