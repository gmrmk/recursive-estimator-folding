"""Manifest-gated runner for the truth-free DGFL F0.5 covariance screen."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
F0 = HERE.parent / "dgfl1_f0_synthetic"
EXPECTED_VARIANCE_CONTRACT = (
    "sample trace variance sum_i ||A_i-mean(A)||^2/(n-1)"
)
REQUIRED_BOUND_PATHS = {
    "dgfl1_f05.py",
    "test_dgfl1_f05.py",
    "run_dgfl1_f05.py",
    "../dgfl1_f0_synthetic/dgfl1_f0.py",
    "../dgfl1_f0_synthetic/test_dgfl1_f0.py",
    "../dgfl1_f0_synthetic/PREEXECUTION_MANIFEST.json",
    "../dgfl1_f0_synthetic/RESOURCE_SNAPSHOT.json",
    "../dgfl1_f0_synthetic/F0_RESULTS.json",
    "../dgfl1_f0_source_contract/PREEXECUTION_MANIFEST.json",
    "../dgfl1_f0_source_contract/F0_SOURCE_RESULTS.json",
    "../../core/CODEX_DGFL1_DIPOLE_FOURIER_LADDER_PROPOSAL_20260811.md",
    "../../papers/DGFL_ROTATIONAL_STEIN_FOURIER_LADDER_20260811.md",
}
REQUIRED_NATIVE_SUFFIXES = {
    "python312.dll",
    "Lib/site-packages/numpy/__init__.py",
    "Lib/site-packages/numpy/_core/_multiarray_umath.cp312-win_amd64.pyd",
    "Lib/site-packages/numpy/random/_pcg64.cp312-win_amd64.pyd",
    "Lib/site-packages/numpy/linalg/_umath_linalg.cp312-win_amd64.pyd",
}
REQUIRED_THREAD_ENV = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _resolve_manifest_path(relative: str) -> Path:
    candidate = (HERE / relative).resolve()
    repo_root = HERE.parents[3].resolve()
    try:
        candidate.relative_to(repo_root)
    except ValueError as exc:
        raise RuntimeError("manifest path escapes the repository") from exc
    return candidate


def _load_numeric_modules() -> tuple[Any, Any]:
    """Import bound numerical code only after the stdlib-only integrity gate."""

    import importlib

    sys.path.insert(0, str(HERE))
    sys.path.insert(0, str(F0))
    numpy_module = importlib.import_module("numpy")
    screen_module = importlib.import_module("dgfl1_f05")
    return numpy_module, screen_module


def validate_manifest(path: Path) -> tuple[dict[str, Any], str, Any, Any]:
    """Validate all frozen files, runtime fields, and RNG payloads before data work."""

    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != "dgfl1-f05-preexecution-v1":
        raise RuntimeError("manifest schema mismatch")
    if manifest.get("status") != "SEALED_PREEXECUTION_DO_NOT_EDIT":
        raise RuntimeError("manifest is not sealed for execution")

    if manifest.get("statistical_contract", {}).get("trace_variance") != EXPECTED_VARIANCE_CONTRACT:
        raise RuntimeError("trace-variance contract mismatch")

    entries = manifest.get("bound_files")
    if not isinstance(entries, list):
        raise RuntimeError("bound file list is missing")
    paths = [entry.get("path_from_experiment") for entry in entries]
    if len(paths) != len(set(paths)):
        raise RuntimeError("bound file list contains duplicates")
    if set(paths) != REQUIRED_BOUND_PATHS:
        raise RuntimeError("bound file set mismatch")
    for entry in entries:
        target = _resolve_manifest_path(entry["path_from_experiment"])
        if target.stat().st_size != entry["bytes"]:
            raise RuntimeError(f"bound file size mismatch: {target.name}")
        if file_sha256(target) != entry["sha256"]:
            raise RuntimeError(f"bound file hash mismatch: {target.name}")

    runtime = manifest["runtime"]
    executable = Path(sys.executable).resolve()
    if file_sha256(executable) != runtime["python_executable_sha256"]:
        raise RuntimeError("Python executable hash mismatch")
    if platform.python_version() != runtime["python_version"]:
        raise RuntimeError("Python version mismatch")
    if not sys.dont_write_bytecode:
        raise RuntimeError("Python bytecode writes are not disabled")
    if any(os.environ.get(name) != "1" for name in REQUIRED_THREAD_ENV):
        raise RuntimeError("thread environment is not frozen to one")
    if os.environ.get("PYTHONHASHSEED") != "0":
        raise RuntimeError("PYTHONHASHSEED is not frozen to zero")
    native_entries = runtime.get("native_files")
    if not isinstance(native_entries, list):
        raise RuntimeError("runtime native-file list is missing")
    native_suffixes = {
        Path(entry["absolute_path"]).as_posix().split("/python/", 1)[-1]
        for entry in native_entries
    }
    if native_suffixes != REQUIRED_NATIVE_SUFFIXES or len(native_entries) != len(
        REQUIRED_NATIVE_SUFFIXES
    ):
        raise RuntimeError("runtime native-file set mismatch")
    for entry in native_entries:
        target = Path(entry["absolute_path"]).resolve()
        if target.stat().st_size != entry["bytes"]:
            raise RuntimeError(f"runtime native-file size mismatch: {target.name}")
        if file_sha256(target) != entry["sha256"]:
            raise RuntimeError(f"runtime native-file hash mismatch: {target.name}")

    np, screen = _load_numeric_modules()
    if np.__version__ != runtime["numpy_version"]:
        raise RuntimeError("NumPy version mismatch")

    fixtures = {
        "fit_rotations": screen.rotation_matrices(
            screen.FIT_ROTATION_SEED, screen.ROTATIONS_PER_SPLIT
        ),
        "held_rotations": screen.rotation_matrices(
            screen.HELD_ROTATION_SEED, screen.ROTATIONS_PER_SPLIT
        ),
        "permutations": screen.permutation_indices(),
        "bootstrap": screen.bootstrap_indices(),
    }
    expected = manifest["fixture_payloads"]
    if set(expected) != set(fixtures):
        raise RuntimeError("fixture payload set mismatch")
    for name, value in fixtures.items():
        record = expected[name]
        if list(value.shape) != record["shape"]:
            raise RuntimeError(f"fixture shape mismatch: {name}")
        if value.dtype.str != record["dtype"] or not value.flags.c_contiguous:
            raise RuntimeError(f"fixture dtype/layout mismatch: {name}")
        if screen.sha256_payload(value) != record["sha256_c_order_payload"]:
            raise RuntimeError(f"fixture payload hash mismatch: {name}")

    weights = screen.hand_network()
    geometry = screen.pilot_geometry(weights)
    mechanism = {
        "W1": np.ascontiguousarray(weights[0], dtype="<f8"),
        "W2": np.ascontiguousarray(weights[1], dtype="<f8"),
        "design_rows": np.ascontiguousarray(screen.design_rows(), dtype="<f8"),
        "pilot": np.ascontiguousarray(geometry["pilot"], dtype="<f8"),
        "first_preactivation": np.ascontiguousarray(
            geometry["first_preactivation"], dtype="<f8"
        ),
        "deep_preactivation": np.ascontiguousarray(
            geometry["deep_preactivation"], dtype="<f8"
        ),
        "first_mask": np.ascontiguousarray(geometry["first_mask"], dtype="|b1"),
        "pullbacks": np.ascontiguousarray(geometry["pullbacks"], dtype="<f8"),
        "axes": np.ascontiguousarray(geometry["axes"], dtype="<f8"),
        "m": np.ascontiguousarray(geometry["m"], dtype="<f8"),
        "b": np.ascontiguousarray(geometry["b"], dtype="<f8"),
        "J": np.ascontiguousarray(geometry["J"], dtype="<f8"),
        "frequencies": np.ascontiguousarray(screen.FREQUENCIES, dtype="<f8"),
    }
    expected_mechanism = manifest["mechanism_payloads"]
    if set(expected_mechanism) != set(mechanism):
        raise RuntimeError("mechanism payload set mismatch")
    for name, value in mechanism.items():
        record = expected_mechanism[name]
        if list(value.shape) != record["shape"] or value.dtype.str != record["dtype"]:
            raise RuntimeError(f"mechanism shape/dtype mismatch: {name}")
        if screen.sha256_payload(value) != record["sha256_c_order_payload"]:
            raise RuntimeError(f"mechanism payload hash mismatch: {name}")
    return manifest, file_sha256(path), np, screen


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="PREEXECUTION_MANIFEST.json")
    parser.add_argument("--preflight-only", action="store_true")
    arguments = parser.parse_args()
    manifest_path = (HERE / arguments.manifest).resolve()

    try:
        manifest, manifest_hash, np, screen = validate_manifest(manifest_path)
    except Exception as exc:  # pre-data mismatch is an abort, never a scientific result
        print(
            json.dumps(
                {
                    "status": "ABORT_INVALID_RUN",
                    "stage": "preflight",
                    "exception_type": type(exc).__name__,
                    "message": str(exc),
                },
                sort_keys=True,
                allow_nan=False,
            )
        )
        return 2

    if arguments.preflight_only:
        print(
            json.dumps(
                {
                    "status": "PASS_PREFLIGHT_ONLY",
                    "preexecution_manifest_sha256": manifest_hash,
                },
                sort_keys=True,
                allow_nan=False,
            )
        )
        return 0

    try:
        result = screen.run_screen()
    except screen.ScientificImplementationKill as exc:
        print(
            json.dumps(
                {
                    "status": "KILLED_F05_SYNTHETIC_COVARIANCE_IMPLEMENTATION",
                    "stage": "sealed_screen",
                    "exception_type": type(exc).__name__,
                    "message": str(exc),
                    "preexecution_manifest_sha256": manifest_hash,
                },
                sort_keys=True,
                allow_nan=False,
            )
        )
        return 1
    except Exception as exc:
        print(
            json.dumps(
                {
                    "status": "ABORT_INVALID_RUN",
                    "stage": "unexpected_exception",
                    "exception_type": type(exc).__name__,
                    "message": str(exc),
                    "preexecution_manifest_sha256": manifest_hash,
                },
                sort_keys=True,
                allow_nan=False,
            )
        )
        return 2

    result.update(
        {
            "schema_version": "dgfl1-f05-result-v1",
            "preexecution_manifest_sha256": manifest_hash,
            "runtime": {
                "python_version": platform.python_version(),
                "python_executable_sha256": file_sha256(Path(sys.executable)),
                "numpy_version": np.__version__,
            },
            "variance_convention": manifest["statistical_contract"][
                "trace_variance"
            ],
        }
    )
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return 0 if result["status"] == "PASS_F05_SYNTHETIC_COVARIANCE_ONLY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
