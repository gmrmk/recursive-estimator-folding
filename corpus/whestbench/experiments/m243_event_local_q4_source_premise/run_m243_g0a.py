"""One-shot durable runner for the frozen M243 G0A formula gate.

The process writes an exclusive launch intent before loading any scientific
runtime, evaluates exactly the eight frozen generated events, installs one
provisional scientific RESULT, and then installs the sole binding
post-publication witness.  It never opens G0B, B1, response, truth, score,
challenge-weight, leaderboard, integration, or submission paths.

Importing this module creates no file and performs no experiment.  This file
is intentionally executable only once in a directory where all four frozen
G0A transport paths are absent.
"""

from __future__ import annotations

import _thread
import ast
from collections import Counter
import ctypes
from ctypes import wintypes
from dataclasses import dataclass
import hashlib
import importlib.metadata
import importlib.util
import itertools
import json
import math
import os
from pathlib import Path
import platform
import signal
import sys
import threading
import time
import traceback

HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent
REPOSITORY = HERE.parents[3]
M237 = EXPERIMENTS / "m237_writeahead_native_receipt"
M122 = EXPERIMENTS / "m122_nonzero_bridge_theory"
M129 = EXPERIMENTS / "m129_source_frechet_tangent"
M178 = EXPERIMENTS / "m178_certified_phi2_owent"
M147 = EXPERIMENTS / "m147_endpoint_safe_bridge"
M151 = EXPERIMENTS / "m151_b1_forward_control"
M133 = EXPERIMENTS / "m133_ht_hidden_edge"
M179 = EXPERIMENTS / "m179_background_archive_producer"
M196 = EXPERIMENTS / "m196_m151_b1_gate"
M213 = EXPERIMENTS / "m213_event_local_randomized_source211"
M216 = EXPERIMENTS / "m216_antithetic_distinct_provider"
M224 = EXPERIMENTS / "m224_gauge_invariant_rho08_chart"
M226 = EXPERIMENTS / "m226_preallocated_fused_rho08"

_m237_text = str(M237)
if _m237_text not in sys.path:
    sys.path.insert(0, _m237_text)
_M237_HELPER_PATH = M237 / "m237_durable_native_receipt.py"
_M237_HELPER_SHA256 = "774cef483c33b149524121144a4c5ede9141f094aa6fe5037414e31bddac873c"
if hashlib.sha256(_M237_HELPER_PATH.read_bytes()).hexdigest() != _M237_HELPER_SHA256:
    raise ImportError("M243 pinned M237 durable helper hash mismatch")

from m237_durable_native_receipt import (  # noqa: E402
    canonical_json_bytes,
    publish_native_result,
    write_launch_intent_exclusive,
)


# Bound exactly once by _load_scientific_runtime(), after verified intent and
# a live watchdog.  Importing this runner therefore loads no scientific stack.
mpmath = None
mp = None
np = None
flopscope = None
candidate = None
M243ReferenceFailure = None
QuadAudit = None
ReferenceEvent = None
binary_mpf = None
normal_pdf = None
outer_panel_points = None
build_endpoint_state_frechet = None
conditional_collision211_endpoint_dot = None
ORDERED_SINGLETON_OWNER = None
source_feature_211 = None
collision211_factored_proposal = None
_SCIENTIFIC_RUNTIME_LOAD_COUNT = 0
_ACTIVE_WATCHDOG = None


INTERPRETER = Path(r"C:\Users\strid\.venvs\whestbench-frozen-m178\Scripts\python.exe")
INTENT = HERE / "M243_G0A_LAUNCH_INTENT_20260809.json"
TEMP = HERE / ".M243_G0A_RESULT_20260809.json.tmp"
RESULT = HERE / "M243_G0A_RESULT_20260809.json"
POSTPUBLICATION_RECEIPT = HERE / "M243_G0A_POSTPUBLICATION_RECEIPT_20260809.json"
STATIC_RUNNER_RECEIPT = HERE / "M243_G0A_RUNNER_STATIC_VALIDATION_20260809.json"
TRANSPORT_PATHS = (INTENT, TEMP, RESULT, POSTPUBLICATION_RECEIPT)
WALL_CAP_SECONDS = 2700.0
RSS_CAP_BYTES = 2 * 1024**3
PRECISIONS = (80, 100)
TAIL_VALUES = (
    0.0,
    2.0**-8,
    -(2.0**-8),
    0.25,
    -0.25,
    1.0,
    -1.0,
    2.5,
    -2.5,
    5.0,
    -5.0,
    8.0,
    -8.0,
    10.0,
    -10.0,
    16.0,
    -16.0,
)
EXPECTED_CENSUS = (
    ("A0", (0, 1, 2)),
    ("A1", (0, 1, 2)),
    ("w3", (0, 1, 2)),
    ("w3", (2, 0, 1)),
    ("w5", (0, 1, 2)),
    ("w5", (4, 0, 1)),
    ("w7", (0, 1, 2)),
    ("w7", (6, 0, 1)),
)
EXPECTED_GATE_IDS = (
    "G0A-FROZEN-ENVIRONMENT",
    "G0A-STATIC-FIREWALL",
    "G0A-CENSUS-EXACT",
    "G0A-COLLISION-TYPED-POISON-REFUSAL",
    "G0A-SOURCE-HALF-OWNERSHIP",
    "G0A-MPMATH-MAXDEGREE12-ERROR",
    "G0A-80-100-PRECISION-AGREEMENT",
    "G0A-REPEATED-R-DIRECT",
    "G0A-BETA-ANALYTIC-VS-DIRECT",
    "G0A-ACTUAL-M178-BETA-INTERVAL",
    "G0A-RAW-ANTI-Q2-Q4-EXPECTATIONS",
    "G0A-INTEGRATED-M178-ENCLOSURE",
    "G0A-TAIL-FINITE-AND-ENCLOSED",
    "G0A-SINGLETON-SWAP",
    "G0A-CYCLIC-CO-PERMUTATION",
    "G0A-POSITIVE-DIAGONAL-GAUGE",
    "G0A-M147-M122-M126-TREE",
    "G0A-EIGHT-EVENT-COMPLETION",
    "G0A-RESOURCE-CAPS",
    "G0A-NO-UNCAUGHT-EXCEPTION",
    "G0A-ARTIFACT-STABILITY",
)


AUTHORITY_AND_COMPONENT_HASHES = {
    HERE / "M243_PREDECLARATION_20260809.md": "a53e3cbf58b9bdc290e6abbf3323a1b7e5162a370774dcd918ddb2193340a9c3",
    HERE / "M243_FROZEN_MANIFEST_20260809.json": "2f788fdc8d91abb8cd43b9ce82140c12cc5707b49b9f815c56abae105b906895",
    HERE / "M243_PREIMPLEMENTATION_ERRATUM_20260809.md": "d7d68c59f5a7389a409f7fd6312145347e4597d45b4161ca9919a53837f60d9d",
    HERE / "M243_FROZEN_MANIFEST_V2_20260809.json": "b8517dc722b0ac09331d18721b48d76316c85234b427e1864fba2dd370c1350e",
    HERE / "M243_PREIMPLEMENTATION_ERRATUM2_20260809.md": "34027dd527a3443f08b63d410856388069eae1a07575a3110523cd760b57654a",
    HERE / "M243_FROZEN_MANIFEST_V3_20260809.json": "6f24dfd5f49a3cb12aa4cc3b12afab331d794975aa586c0d04305055c90aafdb",
    HERE / "M243_PREIMPLEMENTATION_ERRATUM3_20260809.md": "1625b0d5dd29e2d7ed5a763b47e3d3d9ddbb992606355f1fde778e9fd93b5a66",
    HERE / "M243_FROZEN_MANIFEST_V4_20260809.json": "3f91ff3851d5e5867c6660c90dbf89a1dc8105222fcdda8c6ae21193b421dee0",
    HERE / "M243_SHA256SUMS_V2_20260809.txt": "de2fbcff97353cfc5f4cb0015b509827909cc57c5b1c41c8cf8fdff76d270d8c",
    HERE / "M243_PRELAUNCH_ERRATUM4_20260809.md": "b5960d598870208056fa4c4f5e8213ce13816905e16d7e54c47cdeb281a1d9db",
    HERE / "M243_FROZEN_MANIFEST_V5_20260809.json": "b472f009fc8f88ff725886043a72ff5eb1c379b8314ca13f8127de2f16c01859",
    HERE / "M243_SHA256SUMS_V3_20260809.txt": "02f310f54776618e5dd96959ec4f13c121a3fc89b7d8204a5da90d4521611a40",
    HERE / "M243_TDD_RECEIPT_20260809.md": "5e3d4fcc5b15770f7c9495620a49360a3af4c8b7aea5836e4d8dd09122b1b7a0",
    HERE / "m243_event_local_q4_source_premise.py": "b9fe9a79b4e0f5273cbaf6a5b38e6399c9ffba5bd6bea2df1c5e04bd01393152",
    HERE / "test_m243_event_local_q4_source_premise.py": "f801e9fe0776686f047a0d21de121ded5ff6fae7104d735ecd7c831d6789d1e4",
    HERE / "M243_G0A_STATIC_VALIDATION_20260809.json": "361f47c55e99a234d6421e41177f7560716fe047c9cf90f31f0579b97e9f4815",
}

PARENT_AND_TRANSITIVE_HASHES = {
    M122 / "m122_nonzero_bridge.py": "c765fe24818f4ec8928a879e217a530077edff98f729555739202c1f7286f927",
    M133 / "m133_ht_hidden_edge.py": "c296c95ede532c1451e0444b9d56b51e96287ef251b11de9cacee0df7d1ea6b1",
    M147 / "m147_endpoint_safe_bridge.py": "b042e3fe5fc7af518e2ae57a0e43ba6417b22e1c12dfaef458164cf33629a0c0",
    M151 / "m151_b1_forward_control.py": "520431079e63b4bb82c6fe3db997d875ce31fc4037538eb64ce7fea24bf55cd5",
    M178 / "m178_certified_phi2_owent.py": "fa3614a22c2250f69f4d891834cc1e7ca6bd8874d67575b87c7d3fa8598f1c5c",
    M179 / "m179_background_producer.py": "a74a6b0b2807c2b1bc0e38777ba542e3fda196d45f7f436ce12e44fd5cfa4012",
    M196 / "M196_PREDECLARATION_20260808.md": "6eedf4199729973bb275745aa037ca21fc2e83f700c461865b481012601a5b60",
    M196 / "M196_BLOCKER_AND_MINIMAL_INTERFACE_20260808.md": "cf1f563c7afcb2781de2415c17d55a6f32366e3a155ca398497e18d432cb0685",
    M213 / "m213_event_local_randomized_source211.py": "ed20bb8e1f28ea4a9f114ce06c4d3979dfa6c10e82c7ae4dd5e74d35e9adee59",
    M216 / "m216_antithetic_distinct_provider.py": "74d7574b6dd07e290c5b70a062b3324c169b9da9c215d0019c5fbb003e8742d7",
    M224 / "m224_gauge_invariant_rho08_chart.py": "6aba2d0ab618ff5d678977cc07fc89962c09092b537aaffc282e069c10dfda7b",
    M226 / "m226_preallocated_fused_rho08.py": "a52ce3b016cbe23b15c1061354d64cd78e405a37461ea727fce119f7ebce3571",
    M129 / "m129_source_frechet.py": "b7b9d4b0228331972f7fd7b5bd2fb6081ba3053d25daf64f3f8dd0f84e31a6bf",
    _M237_HELPER_PATH: _M237_HELPER_SHA256,
}
FROZEN_HASHES = {**AUTHORITY_AND_COMPONENT_HASHES, **PARENT_AND_TRANSITIVE_HASHES}

AUTHORITY_HEAD = "899a92b6a42110ebfaa24c2799539b0c526ad5b8"
SCIENTIFIC_AUTHORITY_HEAD = "49a5ee1abc13a31d6e2ac8930110f4e6afa6d087"
REFERENCE_SHA256 = "b03e9b2ddda22d8ea147c0720ca8644c91bff2d22c8f82bd057b91a55bdc2c25"
STATIC_RUNNER_RECEIPT_SCHEMA = "M243_G0A_RUNNER_STATIC_VALIDATION_V1"
STATIC_RUNNER_RECEIPT_OVERALL = "PASS"
STATIC_RUNNER_AUTHORITY_SHA256 = {
    "M243_PRELAUNCH_ERRATUM4_20260809.md": "b5960d598870208056fa4c4f5e8213ce13816905e16d7e54c47cdeb281a1d9db",
    "M243_FROZEN_MANIFEST_V5_20260809.json": "b472f009fc8f88ff725886043a72ff5eb1c379b8314ca13f8127de2f16c01859",
    "M243_SHA256SUMS_V3_20260809.txt": "02f310f54776618e5dd96959ec4f13c121a3fc89b7d8204a5da90d4521611a40",
}
FABLE_TRIGGER_TEMPLATE = (
    "M243-G0B-FOUR-SHARD-TRIGGER-V1\n"
    "g0a_pass=true\n"
    "g0a_result_sha256=<64 lowercase hex>\n"
    "g0a_postpublication_receipt_sha256=<64 lowercase hex>\n"
    "sampled_manifest_sha256=<64 lowercase hex>\n"
    "shard_count=4"
)
INTERRUPT_STATE_FIELDS = (
    "interrupt_send_claimed",
    "interrupt_send_completed",
    "interrupt_send_error",
    "interrupt_delivery_count",
    "interrupt_raised_count",
    "interrupt_absorbed_count",
    "interrupt_unexpected_count",
)


class ResourceLimitFailure(RuntimeError):
    """Raised when the sole G0A process crosses a frozen resource cap."""


class ResourceWatchdogAbort(BaseException):
    """Raised by the main-thread SIGINT handler only during EXECUTING."""


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def observed_hashes(paths) -> dict[str, str | None]:
    answer = {}
    for path in paths:
        try:
            answer[str(path)] = sha256(path)
        except Exception:
            answer[str(path)] = None
    return answer


def verify_frozen_hashes() -> dict[str, str]:
    observed = {str(path): sha256(path) for path in FROZEN_HASHES}
    mismatches = {
        str(path): {"expected": expected, "observed": observed[str(path)]}
        for path, expected in FROZEN_HASHES.items()
        if observed[str(path)] != expected
    }
    if mismatches:
        raise RuntimeError("M243 frozen hash mismatch: " + json.dumps(mismatches, sort_keys=True))
    return observed


def four_path_census() -> dict[str, object]:
    rows = [
        {"role": role, "path": str(path), "exists": path.exists()}
        for role, path in zip(
            ("intent", "result_temp", "result", "postpublication_receipt"),
            TRANSPORT_PATHS,
        )
    ]
    return {
        "expected_path_count": 4,
        "observed_path_count": len(rows),
        "rows": rows,
        "all_absent": len(rows) == 4 and all(not row["exists"] for row in rows),
    }


def static_stdlib_source_receipt(runner_path: Path) -> dict[str, object]:
    tree = ast.parse(runner_path.read_text(encoding="utf-8"), filename=str(runner_path))
    top_level_imports = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            top_level_imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            top_level_imports.append(node.module)
    allowed_nonstdlib = {"__future__", "m237_durable_native_receipt"}
    forbidden_top_level = sorted(
        name
        for name in top_level_imports
        if name.split(".", 1)[0] not in sys.stdlib_module_names
        and name not in allowed_nonstdlib
    )
    loader_nodes = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "_load_scientific_runtime"
    ]
    loader_import_ids = {
        id(node)
        for loader in loader_nodes
        for node in ast.walk(loader)
        if isinstance(node, (ast.Import, ast.ImportFrom))
    }
    scientific_roots = {
        "flopscope",
        "mpmath",
        "numpy",
        "m122_nonzero_bridge",
        "m129_source_frechet",
        "m133_ht_hidden_edge",
        "m147_endpoint_safe_bridge",
        "m151_b1_forward_control",
        "m178_certified_phi2_owent",
        "m243_event_local_q4_source_premise",
        "m243_g0a_reference",
    }
    scientific_outside_loader = []
    scientific_inside_loader = []
    subprocess_imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            names = [node.module]
        else:
            continue
        for name in names:
            root = name.split(".", 1)[0]
            if root == "subprocess":
                subprocess_imports.append(name)
            if root in scientific_roots:
                target = (
                    scientific_inside_loader
                    if id(node) in loader_import_ids
                    else scientific_outside_loader
                )
                target.append(name)
    load_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "_load_scientific_runtime"
    ]
    expected_scientific_roots = scientific_roots
    observed_scientific_roots = {
        name.split(".", 1)[0] for name in scientific_inside_loader
    }
    passed = bool(
        len(loader_nodes) == 1
        and len(load_calls) == 1
        and not forbidden_top_level
        and not scientific_outside_loader
        and not subprocess_imports
        and expected_scientific_roots <= observed_scientific_roots
    )
    return {
        "top_level_imports": sorted(top_level_imports),
        "allowed_nonstdlib_top_level": sorted(allowed_nonstdlib),
        "forbidden_top_level_imports": forbidden_top_level,
        "scientific_imports_inside_loader": sorted(scientific_inside_loader),
        "scientific_imports_outside_loader": sorted(scientific_outside_loader),
        "subprocess_imports": sorted(subprocess_imports),
        "loader_definition_count": len(loader_nodes),
        "loader_call_count": len(load_calls),
        "pass": passed,
    }


def stdlib_interpreter_receipt() -> dict[str, object]:
    executable_match = Path(sys.executable).resolve() == INTERPRETER.resolve()
    version = platform.python_version()
    return {
        "interpreter": sys.executable,
        "expected_interpreter": str(INTERPRETER),
        "interpreter_match": executable_match,
        "python": version,
        "expected_python": "3.14.4",
        "os_name": os.name,
        "sys_platform": sys.platform,
        "pass": executable_match and version == "3.14.4" and sys.platform == "win32",
    }


def verify_static_runner_receipt(
    runner_hash: str, reference_hash: str
) -> dict[str, object]:
    raw = STATIC_RUNNER_RECEIPT.read_bytes()
    parsed = json.loads(raw.decode("utf-8"))
    judgments = parsed.get("independent_read_only_judgments")
    if not isinstance(judgments, list):
        judgments = []
    reviewers = [
        row.get("reviewer") for row in judgments if isinstance(row, dict)
    ]
    judgments_pass = bool(
        len(judgments) >= 2
        and len(reviewers) == len(judgments)
        and all(isinstance(name, str) and name for name in reviewers)
        and len(set(reviewers)) == len(reviewers)
        and all(
            isinstance(row, dict) and row.get("verdict") == "PASS"
            for row in judgments
        )
    )
    launches_consumed = parsed.get("g0a_launches_consumed")
    checks = {
        "schema": parsed.get("schema") == STATIC_RUNNER_RECEIPT_SCHEMA,
        "overall": parsed.get("overall") == STATIC_RUNNER_RECEIPT_OVERALL,
        "authority_sha256": (
            parsed.get("authority_sha256") == STATIC_RUNNER_AUTHORITY_SHA256
        ),
        "authority_head": parsed.get("authority_head") == AUTHORITY_HEAD,
        "runner_sha256": parsed.get("runner_sha256") == runner_hash,
        "reference_sha256": (
            parsed.get("reference_sha256") == reference_hash == REFERENCE_SHA256
        ),
        "no_import_compile_execution": (
            parsed.get("import_compile_or_execution_during_static_review") is False
        ),
        "launches_unconsumed": (
            type(launches_consumed) is int and launches_consumed == 0
        ),
        "two_independent_passes": judgments_pass,
        "finite_json": not nonfinite_numeric_findings(parsed, "static_runner_receipt"),
    }
    if not all(checks.values()):
        raise RuntimeError(
            "M243 repaired-runner static validation mismatch: "
            + json.dumps(checks, sort_keys=True)
        )
    return {
        "path": str(STATIC_RUNNER_RECEIPT),
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "checks": checks,
        "parsed": parsed,
        "pass": True,
    }


def _load_scientific_runtime() -> dict[str, object]:
    global _SCIENTIFIC_RUNTIME_LOAD_COUNT
    global mpmath, mp, np, flopscope, candidate
    global M243ReferenceFailure, QuadAudit, ReferenceEvent
    global binary_mpf, normal_pdf, outer_panel_points
    global build_endpoint_state_frechet, conditional_collision211_endpoint_dot
    global ORDERED_SINGLETON_OWNER, source_feature_211
    global collision211_factored_proposal

    if _SCIENTIFIC_RUNTIME_LOAD_COUNT != 0:
        raise RuntimeError("M243 scientific runtime loader called more than once")
    _SCIENTIFIC_RUNTIME_LOAD_COUNT += 1
    for path in (M122, M129, M178, M147, M151, M133, HERE):
        text = str(path)
        if text not in sys.path:
            sys.path.insert(0, text)

    import mpmath as loaded_mpmath
    from mpmath import mp as loaded_mp
    import numpy as loaded_np
    import flopscope as loaded_flopscope
    import m122_nonzero_bridge as loaded_m122
    import m129_source_frechet as loaded_m129
    import m178_certified_phi2_owent as loaded_m178
    import m147_endpoint_safe_bridge as loaded_m147
    import m151_b1_forward_control as loaded_m151
    import m133_ht_hidden_edge as loaded_m133
    import m243_event_local_q4_source_premise as loaded_candidate
    import m243_g0a_reference as loaded_reference

    mpmath = loaded_mpmath
    mp = loaded_mp
    np = loaded_np
    flopscope = loaded_flopscope
    candidate = loaded_candidate
    M243ReferenceFailure = loaded_reference.M243ReferenceFailure
    QuadAudit = loaded_reference.QuadAudit
    ReferenceEvent = loaded_reference.ReferenceEvent
    binary_mpf = loaded_reference.binary_mpf
    normal_pdf = loaded_reference.normal_pdf
    outer_panel_points = loaded_reference.outer_panel_points
    build_endpoint_state_frechet = loaded_m147.build_endpoint_state_frechet
    conditional_collision211_endpoint_dot = (
        loaded_m147.conditional_collision211_endpoint_dot
    )
    ORDERED_SINGLETON_OWNER = loaded_m151.ORDERED_SINGLETON_OWNER
    source_feature_211 = loaded_m151.source_feature_211
    collision211_factored_proposal = loaded_m133.collision211_factored_proposal
    return {
        "load_count": _SCIENTIFIC_RUNTIME_LOAD_COUNT,
        "module_names": [
            loaded_mpmath.__name__,
            loaded_np.__name__,
            loaded_flopscope.__name__,
            loaded_m122.__name__,
            loaded_m129.__name__,
            loaded_m178.__name__,
            loaded_m147.__name__,
            loaded_m151.__name__,
            loaded_m133.__name__,
            loaded_candidate.__name__,
            loaded_reference.__name__,
        ],
        "scientific_worker_start_count": 1,
        "pass": _SCIENTIFIC_RUNTIME_LOAD_COUNT == 1,
    }


def read_git_head(repository: Path) -> str:
    git_path = repository / ".git"
    if git_path.is_file():
        text = git_path.read_text(encoding="utf-8").strip()
        if not text.startswith("gitdir:"):
            raise RuntimeError("unrecognized .git file")
        git_path = (repository / text.split(":", 1)[1].strip()).resolve()
    head = (git_path / "HEAD").read_text(encoding="ascii").strip()
    if head.startswith("ref:"):
        reference = head.split(":", 1)[1].strip()
        loose = git_path / reference
        if loose.is_file():
            return loose.read_text(encoding="ascii").strip()
        packed = git_path / "packed-refs"
        if packed.is_file():
            for line in packed.read_text(encoding="ascii").splitlines():
                if line and not line.startswith(("#", "^")):
                    value, name = line.split(" ", 1)
                    if name == reference:
                        return value
        raise RuntimeError(f"cannot resolve Git reference {reference}")
    return head


def environment_receipt() -> dict[str, object]:
    versions = {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "mpmath": mpmath.__version__,
        "whestbench": importlib.metadata.version("whestbench"),
        "flopscope_distribution": importlib.metadata.version("flopscope"),
        "flopscope": flopscope.__version__,
    }
    expected = {
        "python": "3.14.4",
        "numpy": "2.4.6",
        "mpmath": "1.3.0",
        "whestbench": "0.14.0",
        "flopscope_distribution": "0.10.0",
        "flopscope": "0.10.0+np2.4.6",
    }
    executable_match = Path(sys.executable).resolve() == INTERPRETER.resolve()
    scipy_absent = importlib.util.find_spec("scipy") is None
    return {
        "interpreter": sys.executable,
        "expected_interpreter": str(INTERPRETER),
        "interpreter_match": executable_match,
        "versions": versions,
        "expected_versions": expected,
        "versions_match": versions == expected,
        "scipy_absent": scipy_absent,
        "os_name": os.name,
        "pass": executable_match and versions == expected and scipy_absent,
    }


def imported_modules(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
    return sorted(imports)


def static_firewall_receipt() -> dict[str, object]:
    candidate_imports = imported_modules(HERE / "m243_event_local_q4_source_premise.py")
    reference_imports = imported_modules(HERE / "m243_g0a_reference.py")
    candidate_forbidden = ("mpmath", "scipy", "m213", "m216")
    reference_forbidden = (
        "numpy",
        "scipy",
        "m243_event_local_q4_source_premise",
        "m147",
        "m178",
        "m151",
        "m133",
    )
    candidate_clean = not any(
        name.lower().startswith(candidate_forbidden) for name in candidate_imports
    )
    reference_clean = not any(
        name.lower().startswith(reference_forbidden) for name in reference_imports
    )
    return {
        "candidate_imports": candidate_imports,
        "reference_imports": reference_imports,
        "candidate_forbidden_prefixes": list(candidate_forbidden),
        "reference_forbidden_prefixes": list(reference_forbidden),
        "candidate_clean": candidate_clean,
        "reference_clean": reference_clean,
        "pass": candidate_clean and reference_clean,
    }


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


_WIN64_MEMORY_API = None


def _typed_win64_memory_api():
    global _WIN64_MEMORY_API
    if _WIN64_MEMORY_API is None:
        if sys.platform != "win32":
            raise ResourceLimitFailure("frozen RSS watchdog requires Windows")
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        GetCurrentProcess = kernel32.GetCurrentProcess
        GetCurrentProcess.argtypes = ()
        GetCurrentProcess.restype = wintypes.HANDLE
        GetProcessMemoryInfo = psapi.GetProcessMemoryInfo
        GetProcessMemoryInfo.argtypes = (
            wintypes.HANDLE,
            ctypes.POINTER(_ProcessMemoryCountersEx),
            wintypes.DWORD,
        )
        GetProcessMemoryInfo.restype = wintypes.BOOL
        _WIN64_MEMORY_API = (GetCurrentProcess, GetProcessMemoryInfo)
    return _WIN64_MEMORY_API


def process_memory_receipt() -> tuple[int, int]:
    counters = _ProcessMemoryCountersEx()
    counters.cb = ctypes.sizeof(counters)
    GetCurrentProcess, GetProcessMemoryInfo = _typed_win64_memory_api()
    handle = GetCurrentProcess()
    ok = GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb)
    if not ok:
        raise ctypes.WinError(ctypes.get_last_error())
    return int(counters.WorkingSetSize), int(counters.PeakWorkingSetSize)


class ResourceWatchdog:
    """Background current-process wall/RSS watchdog with main-thread interrupt."""

    def __init__(self, wall_cap: float, rss_cap: int, launch_started: float):
        self.wall_cap = float(wall_cap)
        self.rss_cap = int(rss_cap)
        self.started = float(launch_started)
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._watch, name="m243-g0a-watchdog", daemon=True)
        self.lock = threading.Lock()
        self.breach = None
        self.peak_rss = 0
        self.peak_working_set = 0
        self.polls = 0
        self.thread_started = False
        self.postpublication_sample = None
        self.stop_exceptions = []
        self.last_elapsed_seconds = 0.0
        self.phase = "CREATED"
        self.phase_order_fault = None
        self.executing_transition_count = 0
        self.quiescing_transition_count = 0
        self.publishing_transition_count = 0
        self.sealed_transition_count = 0
        self.handler_installed = False
        self.handler_restored = False
        self.previous_sigint_handler = None
        self.interrupt_send_claimed = False
        self.interrupt_send_completed = False
        self.interrupt_send_error = None
        self.interrupt_delivery_count = 0
        self.interrupt_raised_count = 0
        self.interrupt_absorbed_count = 0
        self.interrupt_unexpected_count = 0
        self.watchdog_live_at_result_publication = False
        self.watchdog_live_at_postpublication_sample = False
        self.joined_after_postpublication_sample = False

    def _handle_sigint(self, signum, frame):
        # Python invokes this handler on the main thread.  It deliberately
        # performs no lock acquisition, I/O, hashing, or transport work.
        self.interrupt_delivery_count += 1
        unexpected = signum != signal.SIGINT or not self.interrupt_send_claimed
        if unexpected:
            self.interrupt_unexpected_count += 1
        if self.phase == "EXECUTING":
            self.phase = "QUIESCING"
            self.quiescing_transition_count += 1
            self.interrupt_raised_count += 1
            raise ResourceWatchdogAbort("M243 watchdog interrupt during EXECUTING")
        if self.phase in ("QUIESCING", "PUBLISHING"):
            self.interrupt_absorbed_count += 1
            return
        if self.phase == "SEALED":
            self.interrupt_raised_count += 1
            raise ResourceWatchdogAbort("M243 watchdog interrupt during SEALED")
        if not unexpected:
            self.interrupt_unexpected_count += 1
        self.interrupt_raised_count += 1
        raise ResourceWatchdogAbort("M243 watchdog interrupt in unexpected phase")

    def _install_interrupt_handler(self):
        if threading.current_thread() is not threading.main_thread():
            raise ResourceLimitFailure("M243 SIGINT handler must be installed by main thread")
        if self.phase != "CREATED" or self.handler_installed:
            raise ResourceLimitFailure("M243 invalid watchdog handler installation order")
        self.previous_sigint_handler = signal.getsignal(signal.SIGINT)
        self.phase = "EXECUTING"
        self.executing_transition_count += 1
        try:
            signal.signal(signal.SIGINT, self._handle_sigint)
        finally:
            # If delivery occurs immediately after the OS handler changes, its
            # ResourceWatchdogAbort still unwinds through this finally, keeping
            # later restoration authoritative.
            self.handler_installed = True

    def quiesce(self):
        if self.phase == "EXECUTING":
            self.phase = "QUIESCING"
            self.quiescing_transition_count += 1
            return
        if self.phase == "QUIESCING":
            return
        self.phase_order_fault = f"quiesce_from_{self.phase}"
        raise ResourceLimitFailure(self.phase_order_fault)

    def quiesce_after_fault(self):
        if self.phase == "CREATED":
            self.phase_order_fault = "start_failed_before_executing"
            self.phase = "QUIESCING"
            self.quiescing_transition_count += 1
            return
        self.quiesce()

    def begin_publication(self):
        if self.phase != "QUIESCING":
            self.phase_order_fault = f"publish_from_{self.phase}"
            raise ResourceLimitFailure(self.phase_order_fault)
        self.phase = "PUBLISHING"
        self.publishing_transition_count += 1

    def mark_result_publication_start(self):
        if self.phase != "PUBLISHING":
            self.phase_order_fault = f"result_publication_from_{self.phase}"
            raise ResourceLimitFailure(self.phase_order_fault)
        self.watchdog_live_at_result_publication = bool(
            self.thread_started and self.thread.is_alive()
        )

    def seal_for_final_receipt(self):
        if self.phase != "PUBLISHING":
            self.phase_order_fault = f"seal_from_{self.phase}"
            raise ResourceLimitFailure(self.phase_order_fault)
        self.phase = "SEALED"
        self.sealed_transition_count += 1

    def restore_interrupt_handler(self):
        if self.handler_installed and not self.handler_restored:
            signal.signal(signal.SIGINT, self.previous_sigint_handler)
            self.handler_restored = True

    def restore_interrupt_handler_protected(self):
        restore_aborts = []
        for attempt in (1, 2, 3):
            try:
                self.restore_interrupt_handler()
            except ResourceWatchdogAbort as exc:
                restore_aborts.append(
                    {
                        "attempt": attempt,
                        "exception_type": type(exc).__name__,
                        "exception_message": str(exc),
                    }
                )
                continue
            return restore_aborts
        raise ResourceWatchdogAbort(
            "M243 SIGINT handler restoration interrupted three times"
        )

    def live_interrupt_state(self):
        with self.lock:
            return {
                field: getattr(self, field)
                for field in INTERRUPT_STATE_FIELDS
            }

    def start(self):
        _typed_win64_memory_api()
        self._install_interrupt_handler()
        self.thread.start()
        self.thread_started = True
        self.checkpoint()

    def _sample(self):
        working, peak = process_memory_receipt()
        elapsed = time.perf_counter() - self.started
        with self.lock:
            self.polls += 1
            self.last_elapsed_seconds = elapsed
            self.peak_working_set = max(self.peak_working_set, working)
            self.peak_rss = max(self.peak_rss, peak)
            if self.breach is None and elapsed > self.wall_cap:
                self.breach = {"kind": "wall", "observed": elapsed, "cap": self.wall_cap}
            if self.breach is None and peak > self.rss_cap:
                self.breach = {"kind": "rss", "observed": peak, "cap": self.rss_cap}
            return {
                "elapsed_seconds": elapsed,
                "working_set_bytes": working,
                "lifetime_peak_working_set_bytes": peak,
                "breach": self.breach,
            }

    def _watch(self):
        while not self.stop_event.wait(0.25):
            try:
                sample = self._sample()
                breach = sample["breach"]
            except BaseException as exc:
                with self.lock:
                    if self.breach is None:
                        self.breach = {
                            "kind": "watchdog_exception",
                            "exception_type": type(exc).__name__,
                            "exception_message": str(exc),
                        }
                breach = self.breach
            if breach is not None:
                with self.lock:
                    should_send = not self.interrupt_send_claimed
                    if should_send:
                        self.interrupt_send_claimed = True
                if should_send:
                    try:
                        _thread.interrupt_main(signal.SIGINT)
                    except BaseException as exc:
                        with self.lock:
                            self.interrupt_send_error = {
                                "exception_type": type(exc).__name__,
                                "exception_message": str(exc),
                            }
                    finally:
                        with self.lock:
                            self.interrupt_send_completed = True
                return

    def checkpoint(self):
        breach = self._sample()["breach"]
        if breach is not None:
            raise ResourceLimitFailure(json.dumps(breach, sort_keys=True))

    def live_snapshot(self):
        sample = self._sample()
        with self.lock:
            return {
                **sample,
                "peak_rss_bytes": self.peak_rss,
                "peak_working_set_bytes": self.peak_working_set,
                "polls": self.polls,
                "thread_started": self.thread_started,
                "thread_alive": self.thread.is_alive(),
                "pass_so_far": (
                    self.thread_started
                    and self.thread.is_alive()
                    and self.breach is None
                ),
                "pending_postpublication_sample": True,
            }

    def sample_after_publication(self):
        self.watchdog_live_at_postpublication_sample = bool(
            self.thread_started and self.thread.is_alive()
        )
        try:
            sample = self._sample()
        except BaseException as exc:
            with self.lock:
                if self.breach is None:
                    self.breach = {
                        "kind": "postpublication_sample_exception",
                        "exception_type": type(exc).__name__,
                        "exception_message": str(exc),
                    }
                sample = {
                    "elapsed_seconds": self.last_elapsed_seconds,
                    "working_set_bytes": None,
                    "lifetime_peak_working_set_bytes": self.peak_rss,
                    "breach": self.breach,
                }
        with self.lock:
            self.postpublication_sample = {
                **sample,
                "peak_rss_bytes": self.peak_rss,
                "peak_working_set_bytes": self.peak_working_set,
                "polls": self.polls,
            }
            return dict(self.postpublication_sample)

    def stop_and_join_protected(self):
        errors = []
        try:
            self.stop_event.set()
        except BaseException as exc:
            errors.append(
                {
                    "phase": "stop_event_set",
                    "exception_type": type(exc).__name__,
                    "exception_message": str(exc),
                }
            )
        if self.thread_started:
            for attempt in (1, 2):
                try:
                    self.thread.join(timeout=2.0)
                except BaseException as exc:
                    errors.append(
                        {
                            "phase": "watchdog_join",
                            "attempt": attempt,
                            "exception_type": type(exc).__name__,
                            "exception_message": str(exc),
                        }
                    )
                if not self.thread.is_alive():
                    break
        if self.thread.is_alive():
            errors.append({"phase": "watchdog_join", "exception_type": "JoinTimeout"})
        self.joined_after_postpublication_sample = bool(
            self.postpublication_sample is not None and not self.thread.is_alive()
        )
        with self.lock:
            self.stop_exceptions.extend(errors)
            if errors and self.breach is None:
                self.breach = {"kind": "watchdog_stop_or_join_exception", "errors": errors}
        return errors

    def receipt(self):
        with self.lock:
            final_sample = (
                None
                if self.postpublication_sample is None
                else dict(self.postpublication_sample)
            )
            return {
                "wall_cap_seconds": self.wall_cap,
                "rss_cap_bytes": self.rss_cap,
                "elapsed_seconds": (
                    None
                    if final_sample is None
                    else final_sample["elapsed_seconds"]
                ),
                "peak_rss_bytes": self.peak_rss,
                "peak_working_set_bytes": self.peak_working_set,
                "polls": self.polls,
                "breach": self.breach,
                "thread_started": self.thread_started,
                "phase": self.phase,
                "phase_order_fault": self.phase_order_fault,
                "executing_transition_count": self.executing_transition_count,
                "quiescing_transition_count": self.quiescing_transition_count,
                "publishing_transition_count": self.publishing_transition_count,
                "sealed_transition_count": self.sealed_transition_count,
                "phase_order_clean": (
                    self.phase == "SEALED"
                    and self.phase_order_fault is None
                    and self.executing_transition_count == 1
                    and self.quiescing_transition_count == 1
                    and self.publishing_transition_count == 1
                    and self.sealed_transition_count == 1
                ),
                "handler_installed_through_receipt": (
                    self.handler_installed and not self.handler_restored
                ),
                "handler_restored": self.handler_restored,
                "interrupt_send_claimed": self.interrupt_send_claimed,
                "interrupt_send_completed": self.interrupt_send_completed,
                "interrupt_send_error": self.interrupt_send_error,
                "interrupt_delivery_count": self.interrupt_delivery_count,
                "interrupt_raised_count": self.interrupt_raised_count,
                "interrupt_absorbed_count": self.interrupt_absorbed_count,
                "interrupt_unexpected_count": self.interrupt_unexpected_count,
                "watchdog_live_at_result_publication": (
                    self.watchdog_live_at_result_publication
                ),
                "watchdog_live_at_postpublication_sample": (
                    self.watchdog_live_at_postpublication_sample
                ),
                "joined_after_postpublication_sample": (
                    self.joined_after_postpublication_sample
                ),
                "thread_alive_after_stop": self.thread.is_alive(),
                "postpublication_sample": final_sample,
                "stop_exceptions": list(self.stop_exceptions),
                "pass": (
                    self.thread_started
                    and final_sample is not None
                    and self.breach is None
                    and not self.stop_exceptions
                    and not self.thread.is_alive()
                    and self.phase == "SEALED"
                    and self.phase_order_fault is None
                    and self.executing_transition_count == 1
                    and self.quiescing_transition_count == 1
                    and self.publishing_transition_count == 1
                    and self.sealed_transition_count == 1
                    and self.handler_installed
                    and not self.handler_restored
                    and not self.interrupt_send_claimed
                    and not self.interrupt_send_completed
                    and self.interrupt_send_error is None
                    and self.interrupt_delivery_count == 0
                    and self.interrupt_raised_count == 0
                    and self.interrupt_absorbed_count == 0
                    and self.interrupt_unexpected_count == 0
                    and self.watchdog_live_at_result_publication
                    and self.watchdog_live_at_postpublication_sample
                    and self.joined_after_postpublication_sample
                    and final_sample["elapsed_seconds"] <= self.wall_cap
                    and final_sample["lifetime_peak_working_set_bytes"] <= self.rss_cap
                ),
            }


class GateBook:
    def __init__(self):
        self.rows = []
        self.names = set()

    def add(self, gate_id: str, passed: bool, details: object):
        if gate_id in self.names:
            raise RuntimeError(f"duplicate M243 gate id {gate_id}")
        self.names.add(gate_id)
        self.rows.append({"gate_id": gate_id, "passed": bool(passed), "details": details})

    @property
    def passed(self):
        return bool(self.rows) and all(row["passed"] for row in self.rows)


@dataclass
class Fixture:
    name: str
    mean: np.ndarray
    covariance: np.ndarray
    events: tuple[tuple[int, int, int], ...]
    seed: int | None = None
    weight: np.ndarray | None = None


def array_digest(array: np.ndarray) -> dict[str, object]:
    value = np.ascontiguousarray(array)
    shape_json = json.dumps(list(value.shape), separators=(",", ":"), ensure_ascii=True)
    payload = value.dtype.str.encode("ascii") + shape_json.encode("ascii") + value.tobytes(order="C")
    return {
        "dtype": value.dtype.str,
        "shape": list(value.shape),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def build_fixtures() -> list[Fixture]:
    a0 = Fixture(
        "A0",
        np.asarray((-0.4, 0.1, 0.7), dtype=np.float64),
        np.eye(3, dtype=np.float64),
        ((0, 1, 2),),
    )
    a1_mean = np.asarray((-0.2, 0.45, -0.35), dtype=np.float64)
    a1_scale = np.asarray((0.7, 1.3, 1.8), dtype=np.float64)
    a1_correlation = np.asarray(
        ((1.0, 0.75, -0.55), (0.75, 1.0, -0.10), (-0.55, -0.10, 1.0)),
        dtype=np.float64,
    )
    a1_covariance = np.outer(a1_scale, a1_scale) * a1_correlation
    a1_covariance = 0.5 * (a1_covariance + a1_covariance.T)
    fixtures = [Fixture("A1", a1_mean, a1_covariance, ((0, 1, 2),))]
    for width, seed in ((3, 243700003), (5, 243700005), (7, 243700007)):
        rng = np.random.Generator(np.random.Philox(seed))
        raw = rng.normal(0.0, 0.12, size=(width, 3))
        diagonal = rng.uniform(0.65, 1.35, size=width)
        covariance = raw @ raw.T + np.diag(diagonal)
        covariance = 0.5 * (covariance + covariance.T)
        mean = rng.uniform(-0.6, 0.6, size=width)
        weight = None
        if width == 5:
            weight = rng.normal(0.0, 1.0 / math.sqrt(6.0), size=(5, 6))
        fixtures.append(
            Fixture(
                f"w{width}",
                np.asarray(mean, dtype=np.float64),
                np.asarray(covariance, dtype=np.float64),
                ((0, 1, 2), (width - 1, 0, 1)),
                seed,
                None if weight is None else np.asarray(weight, dtype=np.float64),
            )
        )
    return [a0] + fixtures


def build_state(fixture: Fixture):
    return build_endpoint_state_frechet(
        fixture.mean,
        fixture.covariance,
        np.zeros_like(fixture.mean),
        np.zeros_like(fixture.covariance),
    )


def mp_float(value: float):
    return mp.mpf(repr(float(value)))


def scaled_defect(observed, expected):
    return abs(observed - expected) / (1 + abs(expected))


def interval_contains(reference, lower: float, upper: float) -> bool:
    return mp_float(lower) <= reference <= mp_float(upper)


def recursive_numeric_pairs(left, right, prefix=""):
    if isinstance(left, dict) and isinstance(right, dict):
        if set(left) != set(right):
            raise RuntimeError(f"precision receipt key mismatch at {prefix}")
        for key in sorted(left):
            yield from recursive_numeric_pairs(left[key], right[key], f"{prefix}.{key}")
        return
    if isinstance(left, (tuple, list)) and isinstance(right, (tuple, list)):
        if len(left) != len(right):
            raise RuntimeError(f"precision receipt length mismatch at {prefix}")
        for index, (item_left, item_right) in enumerate(zip(left, right)):
            yield from recursive_numeric_pairs(item_left, item_right, f"{prefix}[{index}]")
        return
    if isinstance(left, (int, float, mp.mpf)) and isinstance(right, (int, float, mp.mpf)):
        yield prefix, mp.mpf(left), mp.mpf(right)


def reference_precision_projection(receipt):
    return {
        "R_direct": receipt["R_direct"],
        "beta_direct": receipt["beta_direct"],
        "beta_analytic": receipt["beta_analytic"],
        "analytic_jet": receipt["analytic_jet"],
        "central_fourth": receipt["central_fourth"],
        "delta": receipt["delta"],
        "means": receipt["means"],
        "tree": receipt["tree"],
        "wick_vii_vjk": receipt["wick_vii_vjk"],
        "wick_cross": receipt["wick_cross"],
        "tails": [
            {key: row[key] for key in ("g", "b", "r", "raw", "q2", "q4")}
            for row in receipt["tails"]
        ],
    }


def evaluate_reference(
    fixture: Fixture,
    event: tuple[int, int, int],
    dps: int,
    watchdog: ResourceWatchdog,
):
    i, j, k = event
    selected = np.asarray((i, j, k), dtype=np.int64)
    mean = fixture.mean[selected]
    covariance = fixture.covariance[np.ix_(selected, selected)]
    with mp.workdps(dps):
        audit = QuadAudit(dps, watchdog.checkpoint)
        oracle = ReferenceEvent(mean.tolist(), covariance.tolist(), audit, f"{fixture.name}:{i}:{j}:{k}:{dps}d")
        receipt = oracle.evaluate(TAIL_VALUES)
        receipt["quad_audit"] = audit.receipt()
        return receipt


class CandidateIntegralCache:
    def __init__(self, state, event):
        self.state = state
        self.event = event
        self.values = {}
        self.public_call_count = 0

    def _folded(self, degree, g_float):
        key = (degree, g_float.hex())
        if key not in self.values:
            i, j, k = self.event
            self.values[key] = candidate.folded_distinct_event(
                self.state,
                (i, i, j, k),
                g_float,
                degree=degree,
            )
            self.public_call_count += 1
        return self.values[key]

    def evaluate(self, mode: str, g):
        g_float = float(g)
        if not math.isfinite(g_float):
            raise RuntimeError("candidate integration produced nonfinite binary64 node")
        if mode == "raw_antithetic":
            plus = self._folded(None, g_float)
            minus = self._folded(None, -g_float)
            center = 0.5 * (plus.value + minus.value)
            radius = 0.5 * (plus.radius + minus.radius)
            radius += 64.0 * np.finfo(np.float64).eps * (1.0 + abs(center))
            return center, radius
        degree = {"q2": 2, "q4": 4}[mode]
        observed = self._folded(degree, g_float)
        return observed.value, observed.radius


def evaluate_candidate_integrals(
    fixture: Fixture,
    event,
    state,
    dps: int,
    watchdog: ResourceWatchdog,
):
    i, _, _ = event
    with mp.workdps(dps):
        alpha_i = mp_float(fixture.mean[i]) / mp.sqrt(mp_float(fixture.covariance[i, i]))
        panels = outer_panel_points(alpha_i)
        audit = QuadAudit(dps, watchdog.checkpoint)
        cache = CandidateIntegralCache(state, event)
        answer = {}
        for mode in ("raw_antithetic", "q2", "q4"):
            center, center_error = audit.integrate(
                lambda g, chosen=mode: mp_float(cache.evaluate(chosen, g)[0]) * normal_pdf(g),
                panels,
                f"actual:{fixture.name}:{event}:{dps}:{mode}:center",
            )
            local_radius, radius_error = audit.integrate(
                lambda g, chosen=mode: mp_float(cache.evaluate(chosen, g)[1]) * normal_pdf(g),
                panels,
                f"actual:{fixture.name}:{event}:{dps}:{mode}:radius",
            )
            if local_radius < 0:
                raise RuntimeError("negative integrated candidate radius")
            enclosure_radius = local_radius + abs(center_error) + abs(radius_error)
            answer[mode] = {
                "center": center,
                "radius": enclosure_radius,
                "integrated_local_radius": local_radius,
                "center_quadrature_error": center_error,
                "radius_quadrature_error": radius_error,
            }
        answer["quad_audit"] = audit.receipt()
        answer["candidate_public_call_count"] = cache.public_call_count
        answer["candidate_unique_cache_entries"] = len(cache.values)
        return answer


def repeated_binary(state, repeated: int, g: float) -> float:
    base = state.state
    rectified = max(0.0, float(base.mean[repeated]) + float(base.sigma[repeated]) * float(g))
    return (rectified - float(base.relu_mean[repeated])) ** 2


def compare_float(
    accumulator: dict[str, object],
    label: str,
    observed: float,
    expected: float,
):
    try:
        observed_value = float(observed)
    except (OverflowError, TypeError, ValueError):
        observed_value = math.nan
    try:
        expected_value = float(expected)
    except (OverflowError, TypeError, ValueError):
        expected_value = math.nan
    if math.isfinite(observed_value) and math.isfinite(expected_value):
        defect = abs(observed_value - expected_value) / (1.0 + abs(expected_value))
    else:
        defect = math.inf
    if not math.isfinite(defect):
        defect = math.inf
        accumulator["nonfinite_defect_count"] = int(
            accumulator.get("nonfinite_defect_count", 0)
        ) + 1
        accumulator.setdefault("nonfinite_labels", []).append(label)
    accumulator["count"] = int(accumulator.get("count", 0)) + 1
    if defect > float(accumulator.get("max_defect", 0.0)):
        accumulator["max_defect"] = defect
        accumulator["worst"] = label


def invariance_receipts(fixture: Fixture, event, state, watchdog: ResourceWatchdog):
    i, j, k = event
    width = fixture.mean.size
    base_packet = candidate.q4_packet(state, i, j, k)
    swap_packet = candidate.q4_packet(state, i, k, j)

    permutation = np.asarray([(index + 1) % width for index in range(width)], dtype=np.int64)
    mean_permuted = np.empty_like(fixture.mean)
    covariance_permuted = np.empty_like(fixture.covariance)
    mean_permuted[permutation] = fixture.mean
    covariance_permuted[np.ix_(permutation, permutation)] = fixture.covariance
    perm_fixture = Fixture("perm", mean_permuted, covariance_permuted, ())
    perm_state = build_state(perm_fixture)
    perm_event = tuple(int(permutation[index]) for index in event)
    perm_packet = candidate.q4_packet(perm_state, *perm_event)

    gauge = np.asarray(
        [2.0 ** (((index % 5) - 2) / 4.0) for index in range(width)],
        dtype=np.float64,
    )
    gauge_fixture = Fixture(
        "gauge",
        gauge * fixture.mean,
        np.outer(gauge, gauge) * fixture.covariance,
        (),
    )
    gauge_state = build_state(gauge_fixture)
    gauge_packet = candidate.q4_packet(gauge_state, i, j, k)
    beta_degree = float(gauge[j] * gauge[k])
    repeated_degree = float(gauge[i] ** 2)
    event_degree = beta_degree * repeated_degree

    swap = {"count": 0, "max_defect": 0.0, "worst": None}
    permutation_metric = {"count": 0, "max_defect": 0.0, "worst": None}
    gauge_metric = {"count": 0, "max_defect": 0.0, "worst": None}
    for index in range(5):
        compare_float(swap, f"beta[{index}]", swap_packet.beta[index], base_packet.beta[index])
        compare_float(swap, f"R[{index}]", swap_packet.repeated_R[index], base_packet.repeated_R[index])
        compare_float(permutation_metric, f"beta[{index}]", perm_packet.beta[index], base_packet.beta[index])
        compare_float(permutation_metric, f"R[{index}]", perm_packet.repeated_R[index], base_packet.repeated_R[index])
        compare_float(gauge_metric, f"beta[{index}]", gauge_packet.beta[index], beta_degree * base_packet.beta[index])
        compare_float(gauge_metric, f"R[{index}]", gauge_packet.repeated_R[index], repeated_degree * base_packet.repeated_R[index])

    for g in TAIL_VALUES:
        watchdog.checkpoint()
        pair = candidate.conditional_centered_pair(state, i, j, k, g)
        pair_swap = candidate.conditional_centered_pair(state, i, k, j, g)
        pair_perm = candidate.conditional_centered_pair(perm_state, *perm_event, g)
        pair_gauge = candidate.conditional_centered_pair(gauge_state, i, j, k, g)
        compare_float(swap, f"b:{g.hex()}", pair_swap.value, pair.value)
        compare_float(permutation_metric, f"b:{g.hex()}", pair_perm.value, pair.value)
        compare_float(gauge_metric, f"b:{g.hex()}", pair_gauge.value, beta_degree * pair.value)
        r = repeated_binary(state, i, g)
        r_swap = repeated_binary(state, i, g)
        r_perm = repeated_binary(perm_state, perm_event[0], g)
        r_gauge = repeated_binary(gauge_state, i, g)
        compare_float(swap, f"r:{g.hex()}", r_swap, r)
        compare_float(permutation_metric, f"r:{g.hex()}", r_perm, r)
        compare_float(gauge_metric, f"r:{g.hex()}", r_gauge, repeated_degree * r)
        for degree in (None, 2, 4):
            base_fold = candidate.folded_distinct_event(state, (i, i, j, k), g, degree=degree)
            swap_fold = candidate.folded_distinct_event(state, (i, i, k, j), g, degree=degree)
            pi, pj, pk = perm_event
            perm_fold = candidate.folded_distinct_event(
                perm_state, (pi, pi, pj, pk), g, degree=degree
            )
            gauge_fold = candidate.folded_distinct_event(
                gauge_state, (i, i, j, k), g, degree=degree
            )
            tag = "raw" if degree is None else f"q{degree}"
            compare_float(swap, f"{tag}:{g.hex()}", swap_fold.value, base_fold.value)
            compare_float(permutation_metric, f"{tag}:{g.hex()}", perm_fold.value, base_fold.value)
            compare_float(gauge_metric, f"{tag}:{g.hex()}", gauge_fold.value, event_degree * base_fold.value)
    return {"singleton_swap": swap, "co_permutation": permutation_metric, "positive_gauge": gauge_metric}


def poison_refusal_receipt():
    original = candidate.evaluate_phi2
    calls = 0

    def poison(*args, **kwargs):
        nonlocal calls
        calls += 1
        raise AssertionError("pair jet evaluated before collision refusal")

    rows = []
    candidate.evaluate_phi2 = poison
    try:
        for labels in ((0, 0, 0), (0, 0, 1), (0, 1, 1)):
            refused = False
            exception_type = None
            try:
                candidate.q4_packet(object(), *labels)
            except candidate.M243DomainRefusal as exc:
                refused = True
                exception_type = type(exc).__name__
            rows.append({"surface": "q4_packet", "labels": labels, "refused": refused, "exception_type": exception_type})
        for labels in ((0, 0, 0, 0), (0, 0, 0, 1), (0, 0, 1, 1), (0, 1, 2, 3)):
            refused = False
            exception_type = None
            try:
                candidate.folded_distinct_event(object(), labels, 0.0, degree=None)
            except candidate.M243DomainRefusal as exc:
                refused = True
                exception_type = type(exc).__name__
            rows.append({"surface": "folded_distinct_event", "labels": labels, "refused": refused, "exception_type": exception_type})
    finally:
        candidate.evaluate_phi2 = original
    return {
        "rows": rows,
        "pair_jet_calls": calls,
        "pass": calls == 0 and len(rows) == 7 and all(row["refused"] for row in rows),
    }


def source_ownership_receipt(fixture: Fixture, state, watchdog: ResourceWatchdog):
    if fixture.name != "w5" or fixture.weight is None:
        raise RuntimeError("source ownership fixture must be generated w5 with continued-stream W")
    proposal = collision211_factored_proposal(
        state.state.bridge,
        fixture.weight,
        uniform_mixture=0.05,
    )
    probabilities = []
    for event in itertools.permutations(range(5), 3):
        probabilities.append(proposal.probability(*event))
    mass = math.fsum(probabilities)
    support_minimum = min(probabilities)
    rows = []
    for event in ((0, 1, 2), (4, 0, 1)):
        watchdog.checkpoint()
        i, j, k = event
        source = source_feature_211(fixture.weight, i, j, k)
        swapped = source_feature_211(fixture.weight, i, k, j)
        parity = all(
            np.array_equal(getattr(source, slot), getattr(swapped, slot))
            for slot in ("aaaa", "aaab", "aabb")
        )
        flattened = np.concatenate(
            (source.aaaa.ravel(order="C"), source.aaab.ravel(order="C"), source.aabb.ravel(order="C"))
        )
        q = proposal.probability(i, j, k)
        folded = candidate.folded_distinct_event(state, (i, i, j, k), 0.25, degree=4)
        direct = flattened * (folded.value / (2.0 * q))
        via_owner = flattened * ((folded.value * folded.owner_factor) / q)
        double_owner = flattened * ((folded.value * folded.owner_factor * folded.owner_factor) / q)
        rows.append(
            {
                "event": event,
                "q": q,
                "source_swap_bitwise": parity,
                "flattened_length": int(flattened.size),
                "owner_factor": folded.owner_factor,
                "direct_equals_one_owner_bitwise": bool(np.array_equal(direct, via_owner)),
                "direct_differs_from_double_owner": bool(not np.array_equal(direct, double_owner)),
                "all_three_slots_nonempty": all(getattr(source, slot).size > 0 for slot in ("aaaa", "aaab", "aabb")),
            }
        )
    passed = (
        abs(mass - 1.0) <= 2.0e-12
        and support_minimum > 0.0
        and ORDERED_SINGLETON_OWNER == 0.5
        and all(
            row["source_swap_bitwise"]
            and row["owner_factor"] == 0.5
            and row["direct_equals_one_owner_bitwise"]
            and row["direct_differs_from_double_owner"]
            and row["all_three_slots_nonempty"]
            for row in rows
        )
    )
    return {
        "fixture": "w5",
        "uniform_mixture": 0.05,
        "proposal_mass": mass,
        "support_minimum": support_minimum,
        "ordered_population": len(probabilities),
        "declared_owner": ORDERED_SINGLETON_OWNER,
        "rows": rows,
        "pass": passed,
    }


def candidate_tail_receipt(state, event, reference_100, watchdog: ResourceWatchdog):
    i, j, k = event
    packet = candidate.q4_packet(state, i, j, k)
    rows = []
    all_finite = True
    all_contained = True
    for reference_row in reference_100["tails"]:
        watchdog.checkpoint()
        g = float.fromhex(reference_row["g_hex"])
        pair = candidate.conditional_centered_pair(state, i, j, k, g)
        raw = candidate.folded_distinct_event(state, (i, i, j, k), g, degree=None)
        q2 = candidate.folded_distinct_event(state, (i, i, j, k), g, degree=2)
        q4 = candidate.folded_distinct_event(state, (i, i, j, k), g, degree=4)
        objects = {"b": pair, "raw": raw, "q2": q2, "q4": q4}
        finite = all(
            math.isfinite(item.value)
            and math.isfinite(item.radius)
            and math.isfinite(item.lower)
            and math.isfinite(item.upper)
            and item.radius >= 0.0
            for item in objects.values()
        )
        contained = {
            name: interval_contains(reference_row[name], item.lower, item.upper)
            for name, item in objects.items()
        }
        all_finite = all_finite and finite
        all_contained = all_contained and all(contained.values())
        rows.append(
            {
                "g_hex": reference_row["g_hex"],
                "finite": finite,
                "contained": contained,
                "candidate": {
                    name: {
                        "value": item.value,
                        "radius": item.radius,
                        "lower": item.lower,
                        "upper": item.upper,
                    }
                    for name, item in objects.items()
                },
            }
        )
    return {
        "rows": rows,
        "all_finite": all_finite,
        "all_contained": all_contained,
        "base_jet_contained": packet.base_jet_contained,
        "pass": all_finite and all_contained and packet.base_jet_contained,
    }


def event_gate_metrics(packet, reference_100, actual_integrals, m147_certificate):
    with mp.workdps(120):
        r_defects = [
            scaled_defect(mp_float(packet.repeated_R[index]), reference_100["R_direct"][index])
            for index in range(5)
        ]
        analytic_beta_defects = [
            scaled_defect(reference_100["beta_analytic"][index], reference_100["beta_direct"][index])
            for index in range(5)
        ]
        actual_beta_defects = [
            scaled_defect(mp_float(packet.beta[index]), reference_100["beta_direct"][index])
            for index in range(5)
        ]
        beta_containment = []
        for index in range(5):
            center = mp_float(packet.beta[index])
            radius = mp_float(packet.beta_radius[index])
            beta_containment.append(
                center - radius <= reference_100["beta_direct"][index] <= center + radius
                and center - radius <= reference_100["beta_analytic"][index] <= center + radius
            )
        mean_defects = {}
        mean_enclosures = {}
        mean_intervals = {}
        for mode in ("raw_antithetic", "q2", "q4"):
            observed_100 = actual_integrals[100][mode]
            mean_defects[mode] = scaled_defect(
                observed_100["center"], reference_100["delta"]
            )
            mean_enclosures[mode] = {}
            mean_intervals[mode] = {}
            for dps in PRECISIONS:
                observed = actual_integrals[dps][mode]
                lower = observed["center"] - observed["radius"]
                upper = observed["center"] + observed["radius"]
                mean_intervals[mode][dps] = {
                    "lower": lower,
                    "upper": upper,
                    "center": observed["center"],
                    "radius": observed["radius"],
                }
                mean_enclosures[mode][dps] = (
                    lower <= reference_100["delta"] <= upper
                )
        ideal_mean_defects = {
            mode: scaled_defect(reference_100["means"][mode], reference_100["delta"])
            for mode in ("raw_antithetic", "q2", "q4")
        }
        m147_tree_defect = scaled_defect(mp_float(m147_certificate.tree), reference_100["tree"])
        m147_delta_defect = scaled_defect(mp_float(m147_certificate.defect), reference_100["delta"])
        return {
            "R_max_scaled_defect": max(r_defects),
            "R_scaled_defects": r_defects,
            "analytic_beta_max_scaled_defect": max(analytic_beta_defects),
            "analytic_beta_scaled_defects": analytic_beta_defects,
            "actual_beta_max_scaled_defect": max(actual_beta_defects),
            "actual_beta_scaled_defects": actual_beta_defects,
            "beta_interval_containment": beta_containment,
            "actual_mean_scaled_defects": mean_defects,
            "actual_mean_enclosures": mean_enclosures,
            "actual_mean_intervals": mean_intervals,
            "ideal_mean_scaled_defects": ideal_mean_defects,
            "m147_tree_scaled_defect": m147_tree_defect,
            "m147_delta_scaled_defect": m147_delta_defect,
        }


def precision_metrics(reference_by_dps, actual_by_dps):
    with mp.workdps(120):
        worst_reference = mp.zero
        worst_reference_path = None
        for path, low, high in recursive_numeric_pairs(
            reference_precision_projection(reference_by_dps[80]),
            reference_precision_projection(reference_by_dps[100]),
            "reference",
        ):
            defect = scaled_defect(low, high)
            if defect > worst_reference:
                worst_reference = defect
                worst_reference_path = path
        actual_projection_80 = {
            mode: {"center": actual_by_dps[80][mode]["center"]}
            for mode in ("raw_antithetic", "q2", "q4")
        }
        actual_projection_100 = {
            mode: {"center": actual_by_dps[100][mode]["center"]}
            for mode in ("raw_antithetic", "q2", "q4")
        }
        worst_actual = mp.zero
        worst_actual_path = None
        for path, low, high in recursive_numeric_pairs(
            actual_projection_80, actual_projection_100, "actual"
        ):
            defect = scaled_defect(low, high)
            if defect > worst_actual:
                worst_actual = defect
                worst_actual_path = path
        return {
            "reference_max_scaled_defect": worst_reference,
            "reference_worst_path": worst_reference_path,
            "actual_max_scaled_defect": worst_actual,
            "actual_worst_path": worst_actual_path,
        }


def nonfinite_numeric_findings(value, prefix="payload"):
    findings = []
    if mp is not None and isinstance(value, mp.mpf):
        if not mp.isfinite(value):
            findings.append({"path": prefix, "kind": "mpf", "value": mp.nstr(value)})
        return findings
    if np is not None and isinstance(value, np.ndarray):
        return nonfinite_numeric_findings(value.tolist(), prefix)
    if np is not None and isinstance(value, np.generic):
        return nonfinite_numeric_findings(value.item(), prefix)
    if isinstance(value, float):
        if not math.isfinite(value):
            if math.isnan(value):
                name = "nan"
            elif value > 0:
                name = "+inf"
            else:
                name = "-inf"
            findings.append({"path": prefix, "kind": "binary64", "value": name})
        return findings
    if isinstance(value, dict):
        for key, item in value.items():
            findings.extend(nonfinite_numeric_findings(item, f"{prefix}.{key}"))
        return findings
    if isinstance(value, (tuple, list)):
        for index, item in enumerate(value):
            findings.extend(nonfinite_numeric_findings(item, f"{prefix}[{index}]"))
    return findings


def serialize(value):
    if mp is not None and isinstance(value, mp.mpf):
        if not mp.isfinite(value):
            return {
                "__m243_nonfinite_numeric__": {
                    "kind": "mpf",
                    "value": mp.nstr(value),
                }
            }
        return mp.nstr(value, n=110, strip_zeros=False)
    if np is not None and isinstance(value, np.ndarray):
        return serialize(value.tolist())
    if np is not None and isinstance(value, np.generic):
        return serialize(value.item())
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): serialize(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [serialize(item) for item in value]
    if isinstance(value, float):
        if not math.isfinite(value):
            if math.isnan(value):
                name = "nan"
            elif value > 0:
                name = "+inf"
            else:
                name = "-inf"
            return {
                "__m243_nonfinite_numeric__": {
                    "kind": "binary64",
                    "value": name,
                }
            }
        return value
    return value


def run_g0a(watchdog: ResourceWatchdog, gates: GateBook, work: dict[str, object]):
    fixtures = build_fixtures()
    fixture_map = {fixture.name: fixture for fixture in fixtures}
    observed_census = tuple(
        (fixture.name, event) for fixture in fixtures for event in fixture.events
    )
    fixture_receipts = {
        fixture.name: {
            "seed": fixture.seed,
            "width": int(fixture.mean.size),
            "events": fixture.events,
            "mean": array_digest(fixture.mean),
            "covariance": array_digest(fixture.covariance),
            "weight": None if fixture.weight is None else array_digest(fixture.weight),
        }
        for fixture in fixtures
    }
    work["fixtures"] = fixture_receipts
    gates.add(
        "G0A-CENSUS-EXACT",
        observed_census == EXPECTED_CENSUS,
        {"expected": EXPECTED_CENSUS, "observed": observed_census},
    )

    refusal = poison_refusal_receipt()
    work["collision_refusal"] = refusal
    gates.add("G0A-COLLISION-TYPED-POISON-REFUSAL", refusal["pass"], refusal)

    states = {fixture.name: build_state(fixture) for fixture in fixtures}
    ownership = source_ownership_receipt(fixture_map["w5"], states["w5"], watchdog)
    work["source_ownership"] = ownership
    gates.add("G0A-SOURCE-HALF-OWNERSHIP", ownership["pass"], ownership)

    event_results = []
    aggregate = {
        "R_max": mp.zero,
        "analytic_beta_max": mp.zero,
        "actual_beta_max": mp.zero,
        "actual_mean_max": mp.zero,
        "ideal_mean_max": mp.zero,
        "precision_reference_max": mp.zero,
        "precision_actual_max": mp.zero,
        "quad_error_max": mp.zero,
        "beta_containment": True,
        "mean_enclosure_80": True,
        "mean_enclosure_100": True,
        "tail_pass": True,
        "swap_max": 0.0,
        "permutation_max": 0.0,
        "gauge_max": 0.0,
        "tree_binary_exact": True,
        "tree_reference_max": mp.zero,
        "delta_m147_max": mp.zero,
    }
    for ordinal, (fixture_name, event) in enumerate(EXPECTED_CENSUS):
        watchdog.checkpoint()
        fixture = fixture_map[fixture_name]
        state = states[fixture_name]
        reference_by_dps = {}
        actual_by_dps = {}
        for dps in PRECISIONS:
            reference_by_dps[dps] = evaluate_reference(fixture, event, dps, watchdog)
            actual_by_dps[dps] = evaluate_candidate_integrals(fixture, event, state, dps, watchdog)
        packet = candidate.q4_packet(state, *event)
        tail = candidate_tail_receipt(state, event, reference_by_dps[100], watchdog)
        invariance = invariance_receipts(fixture, event, state, watchdog)
        certificate = conditional_collision211_endpoint_dot(state, *event)
        i, j, k = event
        tree_probe = candidate.folded_distinct_event(
            state, (i, i, j, k), 0.0, degree=4
        )
        tree_binary_exact = tree_probe.tree.hex() == float(certificate.tree).hex()
        metrics = event_gate_metrics(packet, reference_by_dps[100], actual_by_dps, certificate)
        precision = precision_metrics(reference_by_dps, actual_by_dps)
        quad_receipts = [
            reference_by_dps[dps]["quad_audit"] for dps in PRECISIONS
        ] + [actual_by_dps[dps]["quad_audit"] for dps in PRECISIONS]
        event_quad_max = max(receipt["max_error_ratio"] for receipt in quad_receipts)
        aggregate["R_max"] = max(aggregate["R_max"], metrics["R_max_scaled_defect"])
        aggregate["analytic_beta_max"] = max(
            aggregate["analytic_beta_max"], metrics["analytic_beta_max_scaled_defect"]
        )
        aggregate["actual_beta_max"] = max(
            aggregate["actual_beta_max"], metrics["actual_beta_max_scaled_defect"]
        )
        aggregate["actual_mean_max"] = max(
            aggregate["actual_mean_max"], max(metrics["actual_mean_scaled_defects"].values())
        )
        aggregate["ideal_mean_max"] = max(
            aggregate["ideal_mean_max"], max(metrics["ideal_mean_scaled_defects"].values())
        )
        aggregate["precision_reference_max"] = max(
            aggregate["precision_reference_max"], precision["reference_max_scaled_defect"]
        )
        aggregate["precision_actual_max"] = max(
            aggregate["precision_actual_max"], precision["actual_max_scaled_defect"]
        )
        aggregate["quad_error_max"] = max(aggregate["quad_error_max"], event_quad_max)
        aggregate["beta_containment"] = aggregate["beta_containment"] and all(
            metrics["beta_interval_containment"]
        )
        aggregate["mean_enclosure_80"] = aggregate["mean_enclosure_80"] and all(
            row[80] for row in metrics["actual_mean_enclosures"].values()
        )
        aggregate["mean_enclosure_100"] = aggregate["mean_enclosure_100"] and all(
            row[100] for row in metrics["actual_mean_enclosures"].values()
        )
        aggregate["tail_pass"] = aggregate["tail_pass"] and tail["pass"]
        aggregate["swap_max"] = max(
            aggregate["swap_max"], invariance["singleton_swap"]["max_defect"]
        )
        aggregate["permutation_max"] = max(
            aggregate["permutation_max"], invariance["co_permutation"]["max_defect"]
        )
        aggregate["gauge_max"] = max(
            aggregate["gauge_max"], invariance["positive_gauge"]["max_defect"]
        )
        aggregate["tree_binary_exact"] = aggregate["tree_binary_exact"] and tree_binary_exact
        aggregate["tree_reference_max"] = max(
            aggregate["tree_reference_max"], metrics["m147_tree_scaled_defect"]
        )
        aggregate["delta_m147_max"] = max(
            aggregate["delta_m147_max"], metrics["m147_delta_scaled_defect"]
        )
        event_results.append(
            {
                "ordinal": ordinal,
                "fixture": fixture_name,
                "event": event,
                "reference": reference_by_dps,
                "actual_integrals": actual_by_dps,
                "packet": {
                    "beta": packet.beta,
                    "repeated_R": packet.repeated_R,
                    "beta_radius": packet.beta_radius,
                    "base_jet_contained": packet.base_jet_contained,
                    "base_jet_chart": packet.base_jet_chart,
                },
                "tail": tail,
                "invariance": invariance,
                "m147_crosscheck": {
                    "central_fourth": certificate.central_fourth,
                    "cumulant": certificate.cumulant,
                    "tree": certificate.tree,
                    "defect": certificate.defect,
                    "value_disagreement": certificate.value_disagreement,
                    "coarse_order": certificate.coarse_order,
                    "fine_order": certificate.fine_order,
                    "quadrant_integrand_evaluations": certificate.quadrant_integrand_evaluations,
                    "candidate_tree_hex": tree_probe.tree.hex(),
                    "certificate_tree_hex": float(certificate.tree).hex(),
                    "tree_binary_exact": tree_binary_exact,
                },
                "metrics": metrics,
                "precision": precision,
            }
        )
        work["completed_event_count"] = len(event_results)
        work["events"] = event_results

    gates.add(
        "G0A-MPMATH-MAXDEGREE12-ERROR",
        aggregate["quad_error_max"] <= mp.mpf("1e-11"),
        {"max_error_ratio": aggregate["quad_error_max"], "limit": mp.mpf("1e-11")},
    )
    gates.add(
        "G0A-80-100-PRECISION-AGREEMENT",
        aggregate["precision_reference_max"] <= mp.mpf("2e-12")
        and aggregate["precision_actual_max"] <= mp.mpf("2e-12"),
        {
            "reference_max_scaled_defect": aggregate["precision_reference_max"],
            "actual_max_scaled_defect": aggregate["precision_actual_max"],
            "limit": mp.mpf("2e-12"),
        },
    )
    gates.add(
        "G0A-REPEATED-R-DIRECT",
        aggregate["R_max"] <= mp.mpf("2e-10"),
        {"max_scaled_defect": aggregate["R_max"], "limit": mp.mpf("2e-10")},
    )
    gates.add(
        "G0A-BETA-ANALYTIC-VS-DIRECT",
        aggregate["analytic_beta_max"] <= mp.mpf("2e-10"),
        {"max_scaled_defect": aggregate["analytic_beta_max"], "limit": mp.mpf("2e-10")},
    )
    gates.add(
        "G0A-ACTUAL-M178-BETA-INTERVAL",
        aggregate["actual_beta_max"] <= mp.mpf("2e-10") and aggregate["beta_containment"],
        {
            "max_scaled_defect": aggregate["actual_beta_max"],
            "limit": mp.mpf("2e-10"),
            "all_direct_and_analytic_references_contained": aggregate["beta_containment"],
        },
    )
    gates.add(
        "G0A-RAW-ANTI-Q2-Q4-EXPECTATIONS",
        aggregate["actual_mean_max"] <= mp.mpf("5e-8")
        and aggregate["ideal_mean_max"] <= mp.mpf("5e-8"),
        {
            "actual_max_scaled_defect": aggregate["actual_mean_max"],
            "ideal_max_scaled_defect": aggregate["ideal_mean_max"],
            "limit": mp.mpf("5e-8"),
        },
    )
    gates.add(
        "G0A-INTEGRATED-M178-ENCLOSURE",
        aggregate["mean_enclosure_80"] and aggregate["mean_enclosure_100"],
        {
            "all_80_digit_intervals_contain_delta_ref": aggregate["mean_enclosure_80"],
            "all_100_digit_intervals_contain_delta_ref": aggregate["mean_enclosure_100"],
            "cross_precision_deltas_do_not_widen_either_interval": True,
        },
    )
    gates.add(
        "G0A-TAIL-FINITE-AND-ENCLOSED",
        aggregate["tail_pass"],
        {"nodes_per_event": len(TAIL_VALUES), "events": len(event_results), "all_pass": aggregate["tail_pass"]},
    )
    gates.add(
        "G0A-SINGLETON-SWAP",
        aggregate["swap_max"] <= 2.0e-10,
        {"max_scaled_defect": aggregate["swap_max"], "limit": 2.0e-10},
    )
    gates.add(
        "G0A-CYCLIC-CO-PERMUTATION",
        aggregate["permutation_max"] <= 2.0e-10,
        {"max_scaled_defect": aggregate["permutation_max"], "limit": 2.0e-10},
    )
    gates.add(
        "G0A-POSITIVE-DIAGONAL-GAUGE",
        aggregate["gauge_max"] <= 2.0e-10,
        {"max_scaled_defect": aggregate["gauge_max"], "limit": 2.0e-10},
    )
    gates.add(
        "G0A-M147-M122-M126-TREE",
        aggregate["tree_binary_exact"]
        and aggregate["tree_reference_max"] <= mp.mpf("5e-10")
        and aggregate["delta_m147_max"] <= mp.mpf("5e-8"),
        {
            "candidate_m147_tree_bitwise_all": aggregate["tree_binary_exact"],
            "independent_tree_max_scaled_defect": aggregate["tree_reference_max"],
            "independent_delta_vs_m147_max_scaled_defect": aggregate["delta_m147_max"],
            "tree_limit": mp.mpf("5e-10"),
            "delta_crosscheck_limit": mp.mpf("5e-8"),
        },
    )
    gates.add(
        "G0A-EIGHT-EVENT-COMPLETION",
        len(event_results) == len(EXPECTED_CENSUS),
        {"expected": len(EXPECTED_CENSUS), "observed": len(event_results)},
    )
    work["events"] = event_results
    work["aggregate_metrics"] = aggregate


def exception_row(phase: str, exc: BaseException) -> dict[str, object]:
    return {
        "phase": phase,
        "exception_type": type(exc).__name__,
        "exception_message": str(exc),
        "traceback": traceback.format_exc(),
    }


def firewall_boundary_receipt() -> dict[str, bool]:
    return {
        "sampled_manifest_created": False,
        "g0b_run": False,
        "g0b_shards_run": False,
        "provider_accessed": False,
        "b1_state_constructed": False,
        "dtilde_constructed": False,
        "m196_residual_imported": False,
        "v_h_computed": False,
        "m196_cells_accessed": False,
        "response_run": False,
        "truth_accessed": False,
        "scorer_run": False,
        "challenge_weights_accessed": False,
        "leaderboard_accessed": False,
        "integration_run": False,
        "submission_run": False,
    }


def all_firewall_booleans_false(receipt: dict[str, bool]) -> bool:
    return bool(receipt) and all(value is False for value in receipt.values())


def _main() -> int:
    global _ACTIVE_WATCHDOG
    runner_path = Path(__file__).resolve()
    reference_path = HERE / "m243_g0a_reference.py"
    transport_before = four_path_census()
    if not transport_before["all_absent"]:
        existing = [row["path"] for row in transport_before["rows"] if row["exists"]]
        raise FileExistsError(
            "M243 G0A transport path already exists; relaunch is permanently forbidden: "
            + ", ".join(existing)
        )
    if not INTERPRETER.is_file():
        raise FileNotFoundError(str(INTERPRETER))

    # Static, stdlib-only preflight.  None of these operations imports the
    # scientific runtime or creates a transport path.
    frozen_before = verify_frozen_hashes()
    runner_hash_before = sha256(runner_path)
    reference_hash_before = sha256(reference_path)
    if reference_hash_before != REFERENCE_SHA256:
        raise RuntimeError("M243 independent reference hash mismatch")
    stdlib_environment = stdlib_interpreter_receipt()
    stdlib_source = static_stdlib_source_receipt(runner_path)
    static_runner = verify_static_runner_receipt(
        runner_hash_before, reference_hash_before
    )
    if not stdlib_environment["pass"] or not stdlib_source["pass"]:
        raise RuntimeError("M243 stdlib-only runner preflight failed")
    head_before = read_git_head(REPOSITORY)
    launcher_pid = os.getpid()
    process_topology_intent = {
        "process_count": 1,
        "launcher_pid": launcher_pid,
        "scientific_worker_pid": launcher_pid,
        "scientific_worker_start_count": 1,
        "subprocess_count": 0,
    }
    intent_payload = serialize(
        {
            "mutation": "m243_event_local_q4_source_premise",
            "phase": "G0A_ONE_SHOT_FORMULA_COMPONENT_GATE",
            "authority_head": AUTHORITY_HEAD,
            "scientific_authority_head": SCIENTIFIC_AUTHORITY_HEAD,
            "head_before": head_before,
            "stdlib_interpreter_preflight": stdlib_environment,
            "stdlib_source_preflight": stdlib_source,
            "frozen_hashes_before": frozen_before,
            "runner_sha256": runner_hash_before,
            "reference_sha256": reference_hash_before,
            "static_runner_validation": {
                "path": static_runner["path"],
                "sha256": static_runner["sha256"],
                "checks": static_runner["checks"],
            },
            "process_topology": process_topology_intent,
            "expected_census": EXPECTED_CENSUS,
            "expected_gate_ids": EXPECTED_GATE_IDS,
            "tail_g_hex": [value.hex() for value in TAIL_VALUES],
            "precisions_dps": PRECISIONS,
            "quadrature": {
                "method": "tanh-sinh",
                "maxdegree": 12,
                "error_api": True,
                "composite_error_relative_limit": "1e-11",
                "rho_panels": 16,
                "outer_panels": "authority list plus only repeated kink -alpha_i",
            },
            "resource_caps": {
                "wall_seconds": WALL_CAP_SECONDS,
                "peak_rss_bytes": RSS_CAP_BYTES,
                "starts": "after_verified_intent_before_scientific_import",
                "ends": "immediate_synchronous_sample_after_RESULT_publication",
            },
            "transport": {
                "intent": str(INTENT),
                "result_temp": str(TEMP),
                "result": str(RESULT),
                "postpublication_receipt": str(POSTPUBLICATION_RECEIPT),
                "four_path_census": transport_before,
            },
            "firewall": firewall_boundary_receipt(),
            "g0a_launches_authorized": 1,
            "g0b_sample_manifest_authorized": False,
            "g0b_shards_authorized": False,
            "relaunch_authorized": False,
        }
    )
    intent_receipt = write_launch_intent_exclusive(INTENT, intent_payload)
    expected_intent_hash = hashlib.sha256(canonical_json_bytes(intent_payload)).hexdigest()
    if intent_receipt["sha256"] != expected_intent_hash:
        raise RuntimeError("M243 launch intent canonical hash mismatch")

    # The scientific resource interval begins only after the verified intent.
    t0 = time.perf_counter()
    watchdog = ResourceWatchdog(WALL_CAP_SECONDS, RSS_CAP_BYTES, t0)
    _ACTIVE_WATCHDOG = watchdog
    gates = GateBook()
    work: dict[str, object] = {"completed_event_count": 0, "events": []}
    execution_exceptions = []
    runtime_receipt: dict[str, object] = {
        "load_count": 0,
        "scientific_worker_start_count": 0,
        "pass": False,
    }
    environment: dict[str, object] = {"pass": False, "status": "NOT_LOADED"}
    firewall: dict[str, object] = {"pass": False, "status": "NOT_EVALUATED"}
    try:
        try:
            watchdog.start()
            runtime_receipt = _load_scientific_runtime()
            environment = environment_receipt()
            firewall = static_firewall_receipt()
            gates.add("G0A-FROZEN-ENVIRONMENT", environment["pass"], environment)
            gates.add("G0A-STATIC-FIREWALL", firewall["pass"], firewall)
            if not environment["pass"] or not firewall["pass"]:
                raise RuntimeError("M243 post-intent environment/firewall preflight failed")
            run_g0a(watchdog, gates, work)
        except BaseException as exc:
            execution_exceptions.append(
                exception_row("scientific_execution", exc)
            )
        # Ordinary-exception normalization and the normal transition out of
        # EXECUTING remain inside this outer BaseException catch.  A watchdog
        # SIGINT delivered anywhere above either raises into this protected
        # span or is absorbed after the handler has set QUIESCING.
        watchdog.quiesce()
    except BaseException as normalization_exc:
        try:
            watchdog.quiesce_after_fault()
        except BaseException as quiesce_exc:
            watchdog.quiesce_after_fault()
            execution_exceptions.append(
                exception_row("watchdog_quiesce_transition", quiesce_exc)
            )
        execution_exceptions.append(
            exception_row("scientific_exception_normalization", normalization_exc)
        )
    watchdog.begin_publication()

    frozen_after = observed_hashes(FROZEN_HASHES)
    implementation_after = observed_hashes(
        (runner_path, reference_path, STATIC_RUNNER_RECEIPT)
    )
    runner_hash_after = implementation_after[str(runner_path)]
    reference_hash_after = implementation_after[str(reference_path)]
    static_runner_hash_after = implementation_after[str(STATIC_RUNNER_RECEIPT)]
    try:
        head_after = read_git_head(REPOSITORY)
    except BaseException as exc:
        head_after = None
        execution_exceptions.append(exception_row("postflight_head", exc))
    frozen_stable = all(
        frozen_after.get(str(path)) == expected
        for path, expected in FROZEN_HASHES.items()
    )
    implementation_stable = bool(
        runner_hash_after == runner_hash_before
        and reference_hash_after == reference_hash_before == REFERENCE_SHA256
        and static_runner_hash_after == static_runner["sha256"]
    )
    gates.add(
        "G0A-ARTIFACT-STABILITY",
        frozen_stable and implementation_stable,
        {
            "frozen_stable": frozen_stable,
            "runner_before": runner_hash_before,
            "runner_after": runner_hash_after,
            "reference_before": reference_hash_before,
            "reference_after": reference_hash_after,
            "static_runner_receipt_before": static_runner["sha256"],
            "static_runner_receipt_after": static_runner_hash_after,
            "head_before": head_before,
            "head_after": head_after,
        },
    )
    try:
        prepublication_resource = watchdog.live_snapshot()
    except BaseException as exc:
        execution_exceptions.append(exception_row("prepublication_resource_sample", exc))
        prepublication_resource = {
            "pass_so_far": False,
            "pending_postpublication_sample": True,
            "sample_exception": execution_exceptions[-1],
        }
    gates.add(
        "G0A-RESOURCE-CAPS",
        bool(prepublication_resource.get("pass_so_far", False)),
        prepublication_resource,
    )

    nonfinite_findings = nonfinite_numeric_findings(
        {
            "work": work,
            "gates_before_exception_gate": gates.rows,
            "prepublication_resource": prepublication_resource,
        }
    )
    if nonfinite_findings:
        execution_exceptions.append(
            {
                "phase": "canonical_nonfinite_tracker",
                "exception_type": "CanonicalNonfiniteFailure",
                "exception_message": "nonfinite numeric payload values fail G0A",
                "findings": nonfinite_findings,
            }
        )
    gates.add(
        "G0A-NO-UNCAUGHT-EXCEPTION",
        not execution_exceptions,
        {
            "execution_exceptions": execution_exceptions,
            "nonfinite_findings": nonfinite_findings,
        },
    )
    complete = int(work.get("completed_event_count", 0)) == len(EXPECTED_CENSUS)
    missing_gate_ids = sorted(set(EXPECTED_GATE_IDS) - gates.names)
    unexpected_gate_ids = sorted(gates.names - set(EXPECTED_GATE_IDS))
    gate_ids_exact = not missing_gate_ids and not unexpected_gate_ids
    process_topology = {
        "process_count": 1,
        "launcher_pid": launcher_pid,
        "scientific_worker_pid": os.getpid(),
        "scientific_worker_start_count": _SCIENTIFIC_RUNTIME_LOAD_COUNT,
        "subprocess_count": 0,
    }
    topology_pass = bool(
        os.getpid() == launcher_pid
        and process_topology["process_count"] == 1
        and process_topology["scientific_worker_start_count"] == 1
        and process_topology["subprocess_count"] == 0
        and runtime_receipt.get("scientific_worker_start_count") == 1
    )
    component_pass = bool(
        not execution_exceptions
        and not nonfinite_findings
        and complete
        and gates.passed
        and gate_ids_exact
        and frozen_stable
        and implementation_stable
        and topology_pass
    )
    firewall_boundaries = firewall_boundary_receipt()
    result_payload = serialize(
        {
            "mutation": "m243_event_local_q4_source_premise",
            "phase": "G0A_ONE_SHOT_FORMULA_COMPONENT_GATE",
            "transport_status": "DURABLE_PROVISIONAL_RESULT_CAPTURED",
            "adjudication_status": "PROVISIONAL_PENDING_POSTPUBLICATION_RECEIPT",
            "resource_adjudication": "PENDING",
            "g0a_pass": None,
            "component_verdict": component_pass,
            "g0a_complete": complete,
            "completed_event_count": work.get("completed_event_count", 0),
            "expected_event_count": len(EXPECTED_CENSUS),
            "gates": gates.rows,
            "gate_count": len(gates.rows),
            "all_provisional_gates_pass": gates.passed,
            "expected_gate_ids": EXPECTED_GATE_IDS,
            "missing_gate_ids": missing_gate_ids,
            "unexpected_gate_ids": unexpected_gate_ids,
            "gate_ids_exact": gate_ids_exact,
            "work": work,
            "execution_exceptions": execution_exceptions,
            "canonical_nonfinite_findings": nonfinite_findings,
            "resource": {
                "adjudication": "PENDING",
                "prepublication_snapshot": prepublication_resource,
            },
            "environment": environment,
            "scientific_runtime": runtime_receipt,
            "static_firewall": firewall,
            "firewall_boundaries": firewall_boundaries,
            "process_topology": process_topology,
            "process_topology_pass": topology_pass,
            "intent_sha256": intent_receipt["sha256"],
            "intent_bytes": intent_receipt["bytes"],
            "head_before": head_before,
            "head_after": head_after,
            "authority_head": AUTHORITY_HEAD,
            "frozen_hashes_before": frozen_before,
            "frozen_hashes_after": frozen_after,
            "runner_sha256_before": runner_hash_before,
            "runner_sha256_after": runner_hash_after,
            "reference_sha256_before": reference_hash_before,
            "reference_sha256_after": reference_hash_after,
            "postpublication_receipt_required": True,
            "postpublication_receipt_path": str(POSTPUBLICATION_RECEIPT),
            "g0b_sample_manifest_authorized": False,
            "g0b_shards_authorized": False,
            "relaunch_authorized": False,
            "credit": {
                "formula_component": False,
                "total_support": False,
                "provider": False,
                "native_cost": False,
                "source_variance": False,
                "response": False,
                "score": False,
            },
        }
    )

    result_receipt = None
    result_publication_exceptions = []
    try:
        watchdog.mark_result_publication_start()
        result_receipt = publish_native_result(
            temp_path=TEMP,
            final_path=RESULT,
            payload=result_payload,
        )
    except BaseException as exc:
        result_publication_exceptions.append(exception_row("result_publication", exc))
    finally:
        # This is the frozen scientific-interval endpoint: the first
        # synchronous sample immediately after durable RESULT publication.
        if result_receipt is not None and watchdog.postpublication_sample is None:
            try:
                watchdog.sample_after_publication()
            except BaseException as exc:
                result_publication_exceptions.append(
                    exception_row("postpublication_sample_boundary", exc)
                )
        try:
            watchdog.stop_and_join_protected()
        except BaseException as exc:
            result_publication_exceptions.append(
                exception_row("watchdog_protected_stop_boundary", exc)
            )
            try:
                watchdog.stop_and_join_protected()
            except BaseException as retry_exc:
                result_publication_exceptions.append(
                    exception_row("watchdog_protected_stop_retry", retry_exc)
                )

    if result_receipt is None:
        try:
            watchdog.seal_for_final_receipt()
        except BaseException as exc:
            result_publication_exceptions.append(
                exception_row("watchdog_seal_after_result_failure", exc)
            )
        try:
            restore_aborts = watchdog.restore_interrupt_handler_protected()
            for abort in restore_aborts:
                result_publication_exceptions.append(
                    {
                        "phase": "watchdog_handler_restore_after_result_failure",
                        **abort,
                    }
                )
        except BaseException as exc:
            result_publication_exceptions.append(
                exception_row("watchdog_handler_restore_after_result_failure", exc)
            )
        print(
            json.dumps(
                {
                    "result_publication_failure": True,
                    "exceptions": result_publication_exceptions,
                    "intent_exists": INTENT.exists(),
                    "temporary_exists": TEMP.exists(),
                    "result_exists": RESULT.exists(),
                    "postpublication_receipt_exists": POSTPUBLICATION_RECEIPT.exists(),
                    "relaunch_authorized": False,
                },
                sort_keys=True,
            )
        )
        return 2

    watchdog.seal_for_final_receipt()
    final_resource = watchdog.receipt()
    interrupt_state_snapshot = {
        field: final_resource[field]
        for field in INTERRUPT_STATE_FIELDS
    }
    final_frozen = observed_hashes(FROZEN_HASHES)
    final_implementation = observed_hashes(
        (runner_path, reference_path, STATIC_RUNNER_RECEIPT)
    )
    final_artifact_stability = bool(
        all(
            final_frozen.get(str(path)) == expected
            for path, expected in FROZEN_HASHES.items()
        )
        and final_implementation[str(runner_path)] == runner_hash_before
        and final_implementation[str(reference_path)] == reference_hash_before
        and final_implementation[str(STATIC_RUNNER_RECEIPT)] == static_runner["sha256"]
    )
    observed_result_hash = observed_hashes((RESULT,))[str(RESULT)]
    result_hash_matches = bool(
        RESULT.is_file()
        and observed_result_hash == result_receipt["sha256"]
        and result_receipt.get("temporary_removed") is True
    )
    intent_binding = bool(
        intent_receipt["parsed"].get("process_topology") == process_topology_intent
        and result_receipt["parsed"].get("process_topology") == process_topology
        and intent_receipt["parsed"].get("authority_head") == AUTHORITY_HEAD
        and result_receipt["parsed"].get("authority_head") == AUTHORITY_HEAD
        and intent_receipt["parsed"].get("runner_sha256") == runner_hash_before
        and intent_receipt["parsed"].get("reference_sha256") == reference_hash_before
    )
    exact_conjunction = {
        "component_verdict_true": component_pass,
        "result_publication_completed": result_hash_matches,
        "resource_interval_pass": final_resource["pass"],
        "postpublication_sample_present": final_resource["postpublication_sample"] is not None,
        "watchdog_no_breach_exception_or_live_thread": bool(
            final_resource["breach"] is None
            and not final_resource["stop_exceptions"]
            and not final_resource["thread_alive_after_stop"]
        ),
        "watchdog_phase_order_clean": final_resource["phase_order_clean"],
        "watchdog_handler_installed_through_receipt": final_resource[
            "handler_installed_through_receipt"
        ],
        "watchdog_no_interrupt_send_or_delivery": bool(
            not final_resource["interrupt_send_claimed"]
            and not final_resource["interrupt_send_completed"]
            and final_resource["interrupt_send_error"] is None
            and final_resource["interrupt_delivery_count"] == 0
            and final_resource["interrupt_raised_count"] == 0
            and final_resource["interrupt_absorbed_count"] == 0
            and final_resource["interrupt_unexpected_count"] == 0
        ),
        "watchdog_live_at_result_and_sample_then_joined": bool(
            final_resource["watchdog_live_at_result_publication"]
            and final_resource["watchdog_live_at_postpublication_sample"]
            and final_resource["joined_after_postpublication_sample"]
        ),
        "no_result_publication_exception": not result_publication_exceptions,
        "artifact_stability": final_artifact_stability,
        "intent_result_same_pid_and_authority": intent_binding and topology_pass,
        "one_pid_one_scientific_start_no_subprocess": topology_pass,
        "all_firewall_booleans_false": all_firewall_booleans_false(
            firewall_boundaries
        ),
        "exact_gate_census": gate_ids_exact,
        "exact_event_census": complete,
        "no_nonfinite_component_payload": not nonfinite_findings,
    }
    receipt_numeric_findings = nonfinite_numeric_findings(
        {
            "watchdog": final_resource,
            "process_topology": process_topology,
            "result_publication": result_receipt,
        }
    )
    exact_conjunction["postpublication_receipt_numeric_finite"] = not receipt_numeric_findings
    binding_g0a_pass = all(exact_conjunction.values())
    postpublication_payload = serialize(
        {
            "mutation": "m243_event_local_q4_source_premise",
            "phase": "G0A_POSTPUBLICATION_BINDING_WITNESS",
            "adjudication_status": "BINDING_PASS_OR_FAIL",
            "g0a_pass": binding_g0a_pass,
            "component_verdict": component_pass,
            "exact_conjunction": exact_conjunction,
            "receipt_numeric_findings": receipt_numeric_findings,
            "authority_head": AUTHORITY_HEAD,
            "scientific_authority_head": SCIENTIFIC_AUTHORITY_HEAD,
            "intent_sha256": intent_receipt["sha256"],
            "result_sha256": result_receipt["sha256"],
            "result_publication_success": result_hash_matches,
            "result_publication_exceptions": result_publication_exceptions,
            "runner_sha256_before": runner_hash_before,
            "runner_sha256_after": final_implementation[str(runner_path)],
            "reference_sha256_before": reference_hash_before,
            "reference_sha256_after": final_implementation[str(reference_path)],
            "static_runner_receipt_sha256": static_runner["sha256"],
            "frozen_hashes_after": final_frozen,
            "original_parent_hash_count": 12,
            "parent_and_transitive_hash_count": len(PARENT_AND_TRANSITIVE_HASHES),
            "process_topology": process_topology,
            "watchdog": final_resource,
            "elapsed_wall_seconds": final_resource["elapsed_seconds"],
            "lifetime_peak_working_set_bytes": final_resource["peak_rss_bytes"],
            "firewall_boundaries": firewall_boundaries,
            "postpublication_receipt_publication": {
                "method": "write_launch_intent_exclusive",
                "exclusive_create_fsync_reopen_parse_hash_verify_required": True,
                "binding_requires_successful_helper_return_and_zero_exit": True,
                "successful_helper_return_and_zero_exit_required": True,
                "sigint_handler_installed_through_durable_receipt_required": True,
                "posthelper_live_interrupt_state_must_exactly_match_snapshot": True,
                "second_witness_attempt_forbidden": True,
            },
            "g0b_sample_manifest_authorized": binding_g0a_pass,
            "g0b_sample_manifest_owner": "Codex",
            "g0b_shards_authorized": False,
            "relaunch_authorized": False,
            "fable_trigger": {
                "authorized_by_this_receipt": False,
                "owner": "Codex",
                "channel_path": "AGENT_CHANNEL.md",
                "must_be_committed_append_only": True,
                "required_committed_append_only_stanza": FABLE_TRIGGER_TEMPLATE,
                "requires_matching_result_receipt_and_sampled_manifest_hashes": True,
                "fable_must_locally_verify": [
                    "both_G0A_hashes_and_true_binding_receipt",
                    "sampled_manifest_hash",
                    "frozen_authority_hashes",
                    "absence_of_all_four_shard_intent_paths",
                ],
                "shard_count": 4,
                "maestro_or_uncommitted_message_is_not_a_trigger": True,
            },
            "credit": {
                "formula_component": binding_g0a_pass,
                "total_support": False,
                "provider": False,
                "native_cost": False,
                "source_variance": False,
                "response": False,
                "score": False,
            },
        }
    )
    binding_receipt = None
    binding_helper_exception = None
    successful_helper_return = False
    restore_aborts = []
    try:
        binding_receipt = write_launch_intent_exclusive(
            POSTPUBLICATION_RECEIPT, postpublication_payload
        )
        successful_helper_return = True
    except BaseException as exc:
        successful_helper_return = False
        binding_helper_exception = {
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
        }
    finally:
        restore_aborts = watchdog.restore_interrupt_handler_protected()

    live_interrupt_state = watchdog.live_interrupt_state()
    interrupt_state_exact_match = live_interrupt_state == interrupt_state_snapshot
    if binding_helper_exception is not None:
        print(
            json.dumps(
                {
                    "postpublication_receipt_failure": True,
                    "binding_g0a_pass": False,
                    **binding_helper_exception,
                    "handler_restore_aborts": restore_aborts,
                    "interrupt_state_snapshot": interrupt_state_snapshot,
                    "live_interrupt_state": live_interrupt_state,
                    "interrupt_state_exact_match": interrupt_state_exact_match,
                    "successful_helper_return": successful_helper_return,
                    "relaunch_authorized": False,
                },
                sort_keys=True,
            )
        )
        return 3
    if restore_aborts or not interrupt_state_exact_match:
        print(
            json.dumps(
                {
                    "postpublication_interrupt_state_drift": True,
                    "binding_g0a_pass": False,
                    "handler_restore_aborts": restore_aborts,
                    "interrupt_state_snapshot": interrupt_state_snapshot,
                    "live_interrupt_state": live_interrupt_state,
                    "interrupt_state_exact_match": interrupt_state_exact_match,
                    "successful_helper_return": successful_helper_return,
                    "successful_helper_return_and_zero_exit_required": True,
                    "relaunch_authorized": False,
                },
                sort_keys=True,
            )
        )
        return 5
    expected_receipt_hash = hashlib.sha256(
        canonical_json_bytes(postpublication_payload)
    ).hexdigest()
    receipt_verified = bool(
        binding_receipt["sha256"] == expected_receipt_hash
        and binding_receipt["parsed"].get("g0a_pass") is binding_g0a_pass
    )
    if not receipt_verified:
        return 4
    print(
        json.dumps(
            {
                "result": str(RESULT),
                "result_sha256": result_receipt["sha256"],
                "postpublication_receipt": str(POSTPUBLICATION_RECEIPT),
                "postpublication_receipt_sha256": binding_receipt["sha256"],
                "g0a_pass": binding_g0a_pass,
                "successful_helper_return": successful_helper_return,
                "interrupt_state_exact_match": interrupt_state_exact_match,
                "successful_helper_return_and_zero_exit_required": True,
                "completed_event_count": work.get("completed_event_count", 0),
                "g0b_sample_manifest_authorized": binding_g0a_pass,
                "g0b_shards_authorized": False,
                "relaunch_authorized": False,
            },
            sort_keys=True,
        )
    )
    return 0 if binding_g0a_pass else 1


def main() -> int:
    try:
        return _main()
    finally:
        watchdog = _ACTIVE_WATCHDOG
        if watchdog is not None:
            watchdog.restore_interrupt_handler_protected()


if __name__ == "__main__":
    raise SystemExit(main())
