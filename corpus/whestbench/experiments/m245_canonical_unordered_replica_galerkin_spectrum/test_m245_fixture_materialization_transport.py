"""Dummy-only contract tests for the M245 fixture materializer.

The tests deliberately contain no NumPy import and execute no frozen fixture
seed.  Every write uses a temporary directory and dummy basenames.
"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


HERE = Path(__file__).resolve().parent
SUPERVISOR_PATH = HERE / "supervise_m245_fixture_materialization.py"
WORKER_PATH = HERE / "materialize_m245_fixtures.py"
MANIFEST_PATH = HERE / "M245_FROZEN_MANIFEST_V1_20260810.json"

EXPECTED_SUPERVISOR_FLAGS = ("-I", "-B", "-S", "-u")
EXPECTED_WORKER_FLAGS = ("-B", "-P", "-s", "-S", "-u")
EXPECTED_CHILD_ENV = {
    "BLIS_NUM_THREADS": "1",
    "COMSPEC": r"C:\Windows\System32\cmd.exe",
    "MKL_DYNAMIC": "FALSE",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "OMP_DYNAMIC": "FALSE",
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "PATH": (
        r"C:\Users\strid\.venvs\whestbench-frozen-m178\Scripts;"
        r"C:\Python314;C:\Windows\System32;C:\Windows"
    ),
    "PATHEXT": ".COM;.EXE;.BAT;.CMD",
    "PYTHONDONTWRITEBYTECODE": "1",
    "PYTHONHASHSEED": "0",
    "PYTHONNOUSERSITE": "1",
    "SYSTEMROOT": r"C:\Windows",
    "TEMP": r"C:\Users\strid\AppData\Local\Temp",
    "TMP": r"C:\Users\strid\AppData\Local\Temp",
    "VECLIB_MAXIMUM_THREADS": "1",
    "WINDIR": r"C:\Windows",
}
EXPECTED_TRACE = (
    "PREINTENT",
    "INTENT_VERIFIED",
    "LAUNCHER_SUSPENDED",
    "JOB_ASSIGNED",
    "LAUNCHER_RESUMED",
    "WORKER_READY",
    "GO_RELEASED",
    "V2_PUBLISHED",
    "DONE_BARRIER",
    "CHILDREN_LIVE_AT_R",
    "R_PUBLISHED",
    "ENDPOINT_CAPTURED",
    "LIVE_PEAK_CPU_CAPTURED",
    "EXIT_RELEASED",
    "WORKER_OS_EXIT",
    "CHILDREN_EXITED",
    "CHILD_EXIT_CLOCK_CAPTURED",
    "JOB_ACTIVE_ZERO",
    "T_PUBLISHED_PENDING_INDEPENDENT_AUDIT",
)

EXPECTED_EXECUTION_BASENAMES = (
    "M245_FIXTURE_MATERIALIZATION_INTENT_20260810.json",
    ".M245_FROZEN_MANIFEST_V2_20260810.json.tmp",
    "M245_FROZEN_MANIFEST_V2_20260810.json",
    "M245_FIXTURE_MATERIALIZATION_POSTPUBLICATION_RECEIPT_20260810.json",
    "M245_FIXTURE_MATERIALIZATION_TERMINAL_METER_WITNESS_20260810.json",
)


def _import_roots(tree: ast.AST) -> set[str]:
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def _function_with_numpy_import(tree: ast.Module) -> list[str]:
    owners: list[str] = []
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if "numpy" in _import_roots(node):
            owners.append(node.name)
    return owners


def _attribute_path(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _attribute_path(node.value)
        return None if parent is None else f"{parent}.{node.attr}"
    return None


def _call_paths(tree: ast.AST) -> list[str]:
    paths: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            path = _attribute_path(node.func)
            if path is not None:
                paths.append(path)
    return paths


def _identity(role: str, pid: int, parent_pid: int, *, job_member: bool) -> dict:
    return {
        "role": role,
        "pid": pid,
        "parent_pid": parent_pid,
        "creation_filetime": 1000 + pid,
        "image_path": rf"C:\dummy\{role}.exe",
        "image_sha256": str(pid % 10) * 64,
        "argv": [rf"C:\dummy\{role}.exe", "--dummy"],
        "cwd": r"C:\dummy\authority",
        "environment_sha256": "e" * 64,
        "job_member": job_member,
        "process_handle_access_mask": 0x101000,
        "handle_acquisition_filetime": 2000 + pid,
        "handle_retained_at_r": True,
        "live_at_r": True,
    }


def _valid_topology_evidence() -> dict:
    supervisor = _identity("S", 11, 7, job_member=False)
    launcher = _identity("L", 22, 11, job_member=True)
    launcher["child_pids"] = [33]
    worker = _identity("W", 33, 22, job_member=True)
    worker.update({"child_count": 0, "used_os_exit_zero": True})
    return {
        "S": supervisor,
        "L": launcher,
        "W": worker,
        "job": {
            "total_processes": 2,
            "active_at_r": 2,
            "pid_census": [22, 33],
            "active_after_exit": 0,
            "kill_on_close": True,
            "active_process_limit": 2,
        },
        "exits": {"launcher": 0, "worker": 0},
    }


def _load_required(path: Path, module_name: str):
    if not path.is_file():
        raise FileNotFoundError(f"required missing implementation: {path.name}")
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    prior = sys.modules.get(module_name)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        if prior is None:
            sys.modules.pop(module_name, None)
        else:
            sys.modules[module_name] = prior
        raise
    return module


# The authoritative RED is a FileNotFoundError here before either module exists.
SUPERVISOR = _load_required(SUPERVISOR_PATH, "m245_fixture_supervisor_under_test")
WORKER = _load_required(WORKER_PATH, "m245_fixture_worker_under_test")


class M245DummyTransportTests(unittest.TestCase):
    def test_test_tissue_is_dummy_only_and_seed_free(self) -> None:
        source = Path(__file__).read_text(encoding="utf-8")
        self.assertNotIn("numpy", _import_roots(ast.parse(source)))
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        frozen_seeds = {
            str(row["seed"])
            for row in manifest["generated_fixtures"]
            if row.get("seed") is not None
        }
        for seed in frozen_seeds:
            self.assertNotIn(seed, source)

    def test_canonical_json_and_hash_are_stable(self) -> None:
        payload = {"z": [3, 2, 1], "a": {"finite": True, "label": "dummy"}}
        expected = (
            '{\n  "a": {\n    "finite": true,\n'
            '    "label": "dummy"\n  },\n  "z": [\n'
            "    3,\n    2,\n    1\n  ]\n}\n"
        ).encode("utf-8")
        for module in (SUPERVISOR, WORKER):
            observed = module.canonical_json_bytes(payload)
            self.assertEqual(observed, expected)
            self.assertEqual(
                module.sha256_bytes(observed), hashlib.sha256(expected).hexdigest()
            )

    def test_sanitized_environment_does_not_copy_ambient_secrets(self) -> None:
        old = dict(os.environ)
        try:
            os.environ["M245_DUMMY_API_KEY"] = "must-not-survive"
            os.environ["PYTHONPATH"] = "must-not-survive"
            observed = SUPERVISOR.sanitized_child_environment()
        finally:
            os.environ.clear()
            os.environ.update(old)
        self.assertEqual(observed, EXPECTED_CHILD_ENV)
        self.assertNotIn("M245_DUMMY_API_KEY", observed)
        self.assertNotIn("PYTHONPATH", observed)

    def test_five_path_absence_is_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="m245-dummy-") as raw:
            root = Path(raw)
            paths = [root / name for name in EXPECTED_EXECUTION_BASENAMES]
            SUPERVISOR.assert_paths_absent(paths)
            with self.assertRaises(ValueError):
                SUPERVISOR.assert_paths_absent(paths[:-1])
            paths[3].write_bytes(b"dummy\n")
            with self.assertRaises(FileExistsError):
                SUPERVISOR.assert_paths_absent(paths)
            mixed = list(paths)
            mixed[0] = root / "other" / mixed[0].name
            with self.assertRaises(ValueError):
                SUPERVISOR.assert_paths_absent(mixed)
        with tempfile.TemporaryDirectory(prefix="m245-dummy-") as raw:
            paths = [Path(raw) / name for name in EXPECTED_EXECUTION_BASENAMES]
            with mock.patch.object(
                SUPERVISOR.os.path,
                "lexists",
                side_effect=[False, False, True, False, False],
            ) as lexists:
                with self.assertRaises(FileExistsError):
                    SUPERVISOR.assert_paths_absent(paths)
                self.assertEqual(lexists.call_count, 5)

    def test_dummy_publication_is_exclusive_fsynced_and_hardlinked(self) -> None:
        with tempfile.TemporaryDirectory(prefix="m245-dummy-") as raw:
            root = Path(raw)
            temp_path = root / ".dummy-v2.tmp"
            final_path = root / "dummy-v2.json"
            payload = {"artifact": "dummy", "rows": [1, 2, 3]}
            receipt = WORKER.publish_canonical_hardlink(
                temp_path=temp_path, final_path=final_path, payload=payload
            )
            expected = WORKER.canonical_json_bytes(payload)
            self.assertEqual(final_path.read_bytes(), expected)
            self.assertFalse(os.path.lexists(temp_path))
            self.assertTrue(receipt["temporary_removed"])
            self.assertEqual(receipt["bytes"], len(expected))
            self.assertEqual(receipt["sha256"], hashlib.sha256(expected).hexdigest())
            self.assertTrue(receipt["same_device"])
            self.assertTrue(receipt["same_inode"])
            self.assertTrue(receipt["reopened_bytes_equal"])
            self.assertTrue(receipt["reopened_parse_equal"])
            with self.assertRaises(FileExistsError):
                WORKER.publish_canonical_hardlink(
                    temp_path=temp_path, final_path=final_path, payload=payload
                )
        with tempfile.TemporaryDirectory(prefix="m245-dummy-") as raw:
            root = Path(raw)
            temp_path = root / ".dummy-v2.tmp"
            final_path = root / "dummy-v2.json"
            temp_path.write_bytes(b"preexisting")
            with self.assertRaises(FileExistsError):
                WORKER.publish_canonical_hardlink(
                    temp_path=temp_path, final_path=final_path, payload={"x": 1}
                )
        worker_text = WORKER_PATH.read_text(encoding="utf-8")
        worker_calls = _call_paths(ast.parse(worker_text))
        self.assertIn("os.fsync", worker_calls)
        self.assertIn("os.link", worker_calls)
        self.assertNotIn("os.replace", worker_calls)
        self.assertNotIn("os.rename", worker_calls)

    def test_dummy_raw_array_receipt_uses_frozen_preimage(self) -> None:
        raw = bytes.fromhex("000000000000f03f0000000000000040")
        receipt = WORKER.raw_array_receipt(
            dtype_str="<f8",
            shape=(2,),
            raw_c_bytes=raw,
            repr_rows=[["1.0", "2.0"]],
            hex_rows=[["0x1.0000000000000p+0", "0x1.0000000000000p+1"]],
        )
        shape_json = b"[2]"
        expected = hashlib.sha256(b"<f8\0" + shape_json + b"\0" + raw).hexdigest()
        self.assertEqual(receipt["sha256"], expected)
        self.assertEqual(receipt["dtype"], "<f8")
        self.assertEqual(receipt["shape"], [2])
        self.assertEqual(receipt["bytes"], 16)
        self.assertEqual(receipt["raw_c_hex"], raw.hex())
        self.assertEqual(receipt["repr_rows"], [["1.0", "2.0"]])
        self.assertEqual(
            receipt["hex_rows"],
            [["0x1.0000000000000p+0", "0x1.0000000000000p+1"]],
        )
        with self.assertRaises(ValueError):
            WORKER.raw_array_receipt(
                dtype_str="<f8",
                shape=(3,),
                raw_c_bytes=raw,
                repr_rows=[["1.0", "2.0"]],
                hex_rows=[["0x1p+0", "0x1p+1"]],
            )
        with self.assertRaises(ValueError):
            WORKER.raw_array_receipt(
                dtype_str="<f8",
                shape=(2, 2),
                raw_c_bytes=raw + raw,
                repr_rows=[["1.0"], ["2.0", "1.0", "2.0"]],
                hex_rows=[["0x1p+0"], ["0x1p+1", "0x1p+0", "0x1p+1"]],
            )
        for bad_repr, bad_hex in (
            ([['1.25', '2.0']], [["0x1.0000000000000p+0", "0x1.0000000000000p+1"]]),
            ([['1.0', '2.0']], [["0x1.4000000000000p+0", "0x1.0000000000000p+1"]]),
        ):
            with self.assertRaises(ValueError):
                WORKER.raw_array_receipt(
                    dtype_str="<f8",
                    shape=(2,),
                    raw_c_bytes=raw,
                    repr_rows=bad_repr,
                    hex_rows=bad_hex,
                )

    def test_state_trace_accepts_only_the_frozen_order(self) -> None:
        self.assertTrue(SUPERVISOR.validate_state_trace(EXPECTED_TRACE))
        wrong = list(EXPECTED_TRACE)
        wrong[8], wrong[9] = wrong[9], wrong[8]
        with self.assertRaises(ValueError):
            SUPERVISOR.validate_state_trace(tuple(wrong))
        with self.assertRaises(ValueError):
            SUPERVISOR.validate_state_trace(EXPECTED_TRACE[:-1])

    def test_topology_evidence_requires_live_retained_s_l_w_and_clean_exit(self) -> None:
        evidence = _valid_topology_evidence()
        self.assertTrue(SUPERVISOR.validate_topology_evidence(evidence))
        for path, value in (
            (("W", "child_count"), 1),
            (("W", "live_at_r"), False),
            (("job", "active_at_r"), 1),
            (("job", "active_after_exit"), 1),
            (("exits", "worker"), 3),
        ):
            mutated = json.loads(json.dumps(evidence))
            mutated[path[0]][path[1]] = value
            with self.assertRaises(ValueError):
                SUPERVISOR.validate_topology_evidence(mutated)
        missing_identity = json.loads(json.dumps(evidence))
        del missing_identity["L"]["creation_filetime"]
        with self.assertRaises(ValueError):
            SUPERVISOR.validate_topology_evidence(missing_identity)

    def test_control_events_and_worker_transcript_are_exact(self) -> None:
        intent_sha256 = "a" * 64
        names = SUPERVISOR.control_event_names(intent_sha256)
        self.assertEqual(
            names,
            {
                label: rf"Local\M245_{intent_sha256[:32]}_{label}"
                for label in ("READY", "GO", "DONE", "EXIT")
            },
        )
        self.assertTrue(SUPERVISOR.CONTROL_EVENT_MANUAL_RESET)
        self.assertFalse(SUPERVISOR.CONTROL_EVENT_INITIAL_STATE)
        self.assertTrue(
            SUPERVISOR.validate_control_event_creation(
                created_new=True, last_error=0
            )
        )
        with self.assertRaises(FileExistsError):
            SUPERVISOR.validate_control_event_creation(
                created_new=False, last_error=183
            )
        ready = {
            "artifact": "M245_W_READY",
            "status": "READY_PRE_NUMPY",
            "pid": 33,
            "intent_sha256": intent_sha256,
            "numpy_modules": [],
            "job_member": True,
        }
        done = {
            "artifact": "M245_W_DONE",
            "status": "V2_PUBLISHED_WAITING_EXIT",
            "pid": 33,
            "intent_sha256": intent_sha256,
            "v2": {"sha256": "b" * 64},
        }
        stdout = SUPERVISOR.canonical_json_bytes(ready) + SUPERVISOR.canonical_json_bytes(done)
        self.assertTrue(
            SUPERVISOR.validate_worker_transcript(
                stdout_bytes=stdout,
                stderr_bytes=b"",
                intent_sha256=intent_sha256,
                v2_sha256="b" * 64,
                worker_pid=33,
            )
        )
        for bad_stdout, bad_stderr in (
            (stdout[:-1], b""),
            (stdout, b"unexpected"),
            (SUPERVISOR.canonical_json_bytes(ready), b""),
            (SUPERVISOR.canonical_json_bytes(done) + SUPERVISOR.canonical_json_bytes(ready), b""),
            (stdout + SUPERVISOR.canonical_json_bytes(done), b""),
        ):
            with self.assertRaises(ValueError):
                SUPERVISOR.validate_worker_transcript(
                    stdout_bytes=bad_stdout,
                    stderr_bytes=bad_stderr,
                    intent_sha256=intent_sha256,
                    v2_sha256="b" * 64,
                    worker_pid=33,
                )
        for record, key, bad in (
            (ready, "pid", 34),
            (ready, "status", "WRONG"),
            (done, "intent_sha256", "c" * 64),
            (done, "v2", {"sha256": "d" * 64}),
        ):
            bad_ready = dict(ready)
            bad_done = dict(done)
            (bad_ready if record is ready else bad_done)[key] = bad
            with self.assertRaises(ValueError):
                SUPERVISOR.validate_worker_transcript(
                    stdout_bytes=(
                        SUPERVISOR.canonical_json_bytes(bad_ready)
                        + SUPERVISOR.canonical_json_bytes(bad_done)
                    ),
                    stderr_bytes=b"",
                    intent_sha256=intent_sha256,
                    v2_sha256="b" * 64,
                    worker_pid=33,
                )

    def test_resource_gate_is_conservative_and_two_wall_gates_bind(self) -> None:
        processes = {
            "S": {
                "peak_working_set_lifetime_to_endpoint": 30_000_000,
                "kernel_endpoint_100ns": 10, "kernel_final_100ns": 12,
                "user_endpoint_100ns": 20, "user_final_100ns": 22,
            },
            "L": {
                "peak_working_set_lifetime_to_endpoint": 35_000_000,
                "kernel_endpoint_100ns": 30, "kernel_final_100ns": 32,
                "user_endpoint_100ns": 40, "user_final_100ns": 42,
            },
            "W": {
                "peak_working_set_lifetime_to_endpoint": 45_000_000,
                "kernel_endpoint_100ns": 50, "kernel_final_100ns": 52,
                "user_endpoint_100ns": 60, "user_final_100ns": 62,
            },
        }
        samples = [
            {"seconds": 0.00, "S": 20_000_000, "L": 25_000_000, "W": 35_000_000},
            {"seconds": 0.01, "S": 25_000_000, "L": 30_000_000, "W": 35_000_000},
            {"seconds": 0.02, "S": 24_000_000, "L": 29_000_000, "W": 34_000_000},
        ]
        passing = SUPERVISOR.evaluate_resource_gate(
            processes=processes,
            working_set_samples=samples,
            wall_r_seconds=0.015,
            wall_child_exit_seconds=0.02,
        )
        self.assertTrue(passing["pass"])
        self.assertEqual(passing["rss_sampled_bytes"], 90_000_000)
        self.assertEqual(passing["rss_lifetime_to_endpoint_sum_bytes"], 110_000_000)
        self.assertEqual(passing["rss_gate_bytes"], 110_000_000)
        self.assertEqual(passing["cpu_sum_100ns"], 222)
        for mutation in ({"wall_r_seconds": 31.0}, {"wall_child_exit_seconds": 31.0}):
            args = {
                "processes": processes,
                "working_set_samples": samples,
                "wall_r_seconds": 0.015,
                "wall_child_exit_seconds": 0.02,
            }
            args.update(mutation)
            self.assertFalse(SUPERVISOR.evaluate_resource_gate(**args)["pass"])
        gapped = [samples[0], {**samples[-1], "seconds": 0.101}]
        self.assertFalse(
            SUPERVISOR.evaluate_resource_gate(
                processes=processes,
                working_set_samples=gapped,
                wall_r_seconds=0.015,
                wall_child_exit_seconds=0.101,
            )["pass"]
        )
        over_cap = json.loads(json.dumps(processes))
        over_cap["W"]["peak_working_set_lifetime_to_endpoint"] = 220_000_000
        self.assertFalse(
            SUPERVISOR.evaluate_resource_gate(
                processes=over_cap,
                working_set_samples=samples,
                wall_r_seconds=0.015,
                wall_child_exit_seconds=0.02,
            )["pass"]
        )
        sampled_over_cap = json.loads(json.dumps(samples))
        sampled_over_cap[-1]["W"] = 250_000_000
        self.assertFalse(
            SUPERVISOR.evaluate_resource_gate(
                processes=processes,
                working_set_samples=sampled_over_cap,
                wall_r_seconds=0.015,
                wall_child_exit_seconds=0.02,
            )["pass"]
        )
        rollback = json.loads(json.dumps(processes))
        rollback["W"]["kernel_final_100ns"] = 49
        for broken in (
            {"S": processes["S"], "L": processes["L"]},
            {**processes, "W": {**processes["W"], "kernel_final_100ns": -1}},
            {**processes, "W": {"kernel_final_100ns": 1, "user_final_100ns": 1}},
            rollback,
        ):
            with self.assertRaises(ValueError):
                SUPERVISOR.evaluate_resource_gate(
                    processes=broken,
                    working_set_samples=samples,
                    wall_r_seconds=0.015,
                    wall_child_exit_seconds=0.02,
                )
        for bad_walls in ((-0.1, 0.02), (0.02, 0.01)):
            with self.assertRaises(ValueError):
                SUPERVISOR.evaluate_resource_gate(
                    processes=processes,
                    working_set_samples=samples,
                    wall_r_seconds=bad_walls[0],
                    wall_child_exit_seconds=bad_walls[1],
                )

    def test_r_is_provisional_and_t_does_not_self_attest(self) -> None:
        topology = _valid_topology_evidence()
        r_payload = SUPERVISOR.build_provisional_receipt(
            intent_sha256="1" * 64,
            v2_sha256="2" * 64,
            authority_sha256={"dummy": "3" * 64},
            v2_receipt={"path": "dummy-v2.json", "bytes": 10, "sha256": "2" * 64},
            topology=topology,
        )
        r_bytes = SUPERVISOR.canonical_json_bytes(r_payload)
        t_payload = SUPERVISOR.build_terminal_witness(
            intent_sha256="1" * 64,
            v2_sha256="2" * 64,
            r_sha256=hashlib.sha256(r_bytes).hexdigest(),
            r_bytes=len(r_bytes),
            resources={
                "pass": True,
                "rss_sampled_bytes": 90_000_000,
                "rss_lifetime_to_endpoint_sum_bytes": 110_000_000,
                "rss_gate_bytes": 110_000_000,
                "cpu_sum_100ns": 222,
                "wall_r_seconds": 0.015,
                "wall_child_exit_seconds": 0.02,
                "maximum_gap_seconds": 0.01,
                "caps": {
                    "rss_bytes": 268_435_456,
                    "wall_seconds": 30.0,
                    "child_exit_wall_seconds": 30.0,
                    "maximum_gap_seconds": 0.1,
                },
                "processes": {
                    role: {
                        "peak_working_set_lifetime_to_endpoint": peak,
                        "kernel_endpoint_100ns": kernel,
                        "kernel_final_100ns": kernel + 2,
                        "user_endpoint_100ns": user,
                        "user_final_100ns": user + 2,
                    }
                    for role, peak, kernel, user in (
                        ("S", 30_000_000, 10, 20),
                        ("L", 35_000_000, 30, 40),
                        ("W", 45_000_000, 50, 60),
                    )
                },
                "working_set_samples": [
                    {"seconds": 0.0, "S": 20_000_000, "L": 25_000_000, "W": 35_000_000},
                    {"seconds": 0.01, "S": 25_000_000, "L": 30_000_000, "W": 35_000_000},
                    {"seconds": 0.02, "S": 24_000_000, "L": 29_000_000, "W": 34_000_000},
                ],
            },
            exits={
                "launcher": 0,
                "worker": 0,
                "active_processes": 0,
                "child_exit_filetime": 4000,
            },
            identities={role: topology[role] for role in ("S", "L", "W")},
            job_census=topology["job"],
            sampling={
                "maximum_gap_seconds": 0.01,
                "sample_count": 3,
                "timestamps_seconds": [0.0, 0.01, 0.02],
            },
            pre_t_state={"intent": True, "v2": True, "r": True, "temp": False, "t": False},
            expected_t_path=EXPECTED_EXECUTION_BASENAMES[-1],
        )
        self.assertEqual(r_payload["status"], "PROVISIONAL_REQUIRES_T")
        self.assertEqual(t_payload["status"], "PASS_M245_FIXTURE_AUTHORITY_BOUND")
        self.assertEqual(r_payload["v2"]["sha256"], "2" * 64)
        expected_t_keys = {
            "artifact",
            "status",
            "intent_sha256",
            "v2_sha256",
            "r_sha256",
            "r_bytes",
            "resources",
            "exits",
            "identities",
            "sampling",
            "pre_t_state",
            "job_census",
            "expected_t_path",
            "publication_verification_pending_independent_audit",
        }
        self.assertEqual(set(t_payload), expected_t_keys)
        self.assertIs(t_payload["publication_verification_pending_independent_audit"], True)
        self.assertEqual(
            set(r_payload),
            {
                "artifact",
                "status",
                "intent_sha256",
                "v2_sha256",
                "authority_sha256",
                "v2",
                "topology",
                "terminal_witness_required",
            },
        )

    def test_worker_pre_go_runtime_gate_is_fail_closed(self) -> None:
        kwargs = {
            "no_site": 1,
            "no_user_site": 1,
            "safe_path": 1,
            "dont_write_bytecode": True,
            "venv_site_packages_present": False,
            "numpy_module_names": (),
            "intent_verified": True,
            "job_member": True,
            "owned_paths_absent": True,
        }
        self.assertTrue(WORKER.validate_pre_go_runtime(**kwargs))
        for key, bad in (
            ("no_site", 0),
            ("no_user_site", 0),
            ("safe_path", 0),
            ("dont_write_bytecode", False),
            ("venv_site_packages_present", True),
            ("numpy_module_names", ("numpy",)),
            ("numpy_module_names", ("numpy.linalg",)),
            ("intent_verified", False),
            ("job_member", False),
            ("owned_paths_absent", False),
        ):
            mutated = dict(kwargs)
            mutated[key] = bad
            with self.assertRaises(RuntimeError):
                WORKER.validate_pre_go_runtime(**mutated)

    def test_static_startup_and_process_firewalls(self) -> None:
        supervisor_text = SUPERVISOR_PATH.read_text(encoding="utf-8")
        worker_text = WORKER_PATH.read_text(encoding="utf-8")
        supervisor_tree = ast.parse(supervisor_text)
        worker_tree = ast.parse(worker_text)
        supervisor_calls = _call_paths(supervisor_tree)
        worker_calls = _call_paths(worker_tree)
        supervisor_roots = _import_roots(supervisor_tree)
        worker_roots = _import_roots(worker_tree)
        self.assertEqual(tuple(SUPERVISOR.SUPERVISOR_FLAGS), EXPECTED_SUPERVISOR_FLAGS)
        self.assertEqual(tuple(SUPERVISOR.WORKER_FLAGS), EXPECTED_WORKER_FLAGS)
        self.assertIn("CREATE_SUSPENDED", supervisor_text)
        self.assertTrue(any(path.endswith(".AssignProcessToJobObject") for path in supervisor_calls))
        self.assertTrue(any(path.endswith(".ResumeThread") for path in supervisor_calls))
        self.assertIn("JOB_OBJECT_LIMIT_ACTIVE_PROCESS", supervisor_text)
        self.assertIn("JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE", supervisor_text)
        self.assertTrue(supervisor_roots <= set(sys.stdlib_module_names))
        top_level_worker_imports = _import_roots(ast.Module(body=[
            node for node in worker_tree.body
            if isinstance(node, (ast.Import, ast.ImportFrom))
        ], type_ignores=[]))
        self.assertNotIn("numpy", top_level_worker_imports)
        self.assertNotIn("subprocess", top_level_worker_imports)
        self.assertTrue(worker_roots <= set(sys.stdlib_module_names) | {"numpy"})
        self.assertTrue({"site", "socket", "urllib", "http", "ssl"}.isdisjoint(worker_roots))
        self.assertEqual(_function_with_numpy_import(worker_tree), ["_load_numpy_after_go"])
        numpy_imports = [
            node for node in ast.walk(worker_tree)
            if isinstance(node, ast.Import)
            and any(alias.name == "numpy" for alias in node.names)
        ]
        self.assertEqual(len(numpy_imports), 1)
        self.assertEqual(
            [(alias.name, alias.asname) for alias in numpy_imports[0].names],
            [("numpy", "np")],
        )
        self.assertIn("sys.path.insert", worker_calls)
        self.assertEqual(WORKER.EXPECTED_NUMPY_VERSION, "2.4.6")
        worker_main = next(
            node for node in worker_tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "_worker_main"
        )
        ordered_nodes = sorted(
            (
                node for node in ast.walk(worker_main)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id in {"_wait_for_go", "_load_numpy_after_go"}
            ),
            key=lambda node: (node.lineno, node.col_offset),
        )
        ordered_calls = [node.func.id for node in ordered_nodes]
        self.assertEqual(ordered_calls, ["_wait_for_go", "_load_numpy_after_go"])
        zero_exit_calls = [
            node for node in ast.walk(worker_tree)
            if isinstance(node, ast.Call) and _attribute_path(node.func) == "os._exit"
            and len(node.args) == 1 and isinstance(node.args[0], ast.Constant)
            and node.args[0].value == 0
        ]
        self.assertEqual(len(zero_exit_calls), 1)
        self.assertEqual(
            SUPERVISOR.supervisor_argv(),
            [r"C:\Python314\python.exe", *EXPECTED_SUPERVISOR_FLAGS, str(SUPERVISOR_PATH)],
        )
        self.assertEqual(
            SUPERVISOR.worker_argv(),
            [
                r"C:\Users\strid\.venvs\whestbench-frozen-m178\Scripts\python.exe",
                *EXPECTED_WORKER_FLAGS,
                str(WORKER_PATH),
            ],
        )
        self.assertEqual(Path(SUPERVISOR.AUTHORITY_DIRECTORY), HERE)
        self.assertNotIn("subprocess", _import_roots(worker_tree))
        self.assertNotIn("os.system", worker_calls)
        self.assertFalse(any(path.startswith("os.spawn") for path in worker_calls))
        self.assertFalse(any(path.startswith("os.exec") for path in worker_calls))
        self.assertIsInstance(supervisor_tree, ast.Module)


if __name__ == "__main__":
    unittest.main()
