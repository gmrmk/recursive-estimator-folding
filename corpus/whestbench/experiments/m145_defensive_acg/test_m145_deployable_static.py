"""No-outcome static and algebraic checks for the deployable M145 descendant."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import builtins
import types

HERE = Path(__file__).resolve().parent


def test_deployment_closure_has_no_direct_numpy_import() -> None:
    completed = subprocess.run(
        [sys.executable, str(HERE / "audit_m145_deployable_imports.py")],
        check=True,
        text=True,
        capture_output=True,
    )
    payload = json.loads(completed.stdout)
    assert payload["status"] == "PASS"
    assert payload["direct_numpy_imports"] == {}


def test_import_deny_simulation_loads_the_deployment_module() -> None:
    """Import the source with a guard that rejects application NumPy imports.

    Lightweight FlopScope/WhestBench stubs are sufficient because importing
    the candidate only defines functions/classes; no array operation is
    allowed at import time.  This is a closure test, not a runtime substitute
    for the pinned official image.
    """

    old_path = list(sys.path)
    saved = {name: sys.modules.get(name) for name in (
        "flopscope", "flopscope.numpy", "whestbench", "whestbench.domain",
        "m145_deployable_core", "m145_deployable_sidecar", "m145_deployable_estimator",
        "base_estimator", "fold3_estimator", "fold_estimator", "row_blocked_winograd", "cost_model",
    )}
    fake_flopscope = types.ModuleType("flopscope")
    fake_flopscope.__path__ = []
    fake_fnp = types.ModuleType("flopscope.numpy")
    fake_whest = types.ModuleType("whestbench")
    fake_whest.BaseEstimator = type("BaseEstimator", (), {})
    fake_whest.SetupContext = type("SetupContext", (), {})
    fake_domain = types.ModuleType("whestbench.domain")
    fake_domain.MLP = type("MLP", (), {})
    original_import = builtins.__import__
    shipped = {str((HERE / name).resolve()) for name in (
        "m145_deployable_core.py", "m145_deployable_sidecar.py", "m145_deployable_estimator.py",
    )}

    def deny_numpy(name, globals=None, locals=None, fromlist=(), level=0):
        source = str(Path((globals or {}).get("__file__", "")).resolve())
        if source in shipped and (name == "numpy" or name.startswith("numpy.")):
            raise ImportError("ordinary NumPy is denied for shipped M145 source")
        return original_import(name, globals, locals, fromlist, level)

    try:
        sys.path[:0] = [str(HERE), str(HERE.parent / "row_blocked_production" / "candidate_source")]
        sys.modules.update({
            "flopscope": fake_flopscope,
            "flopscope.numpy": fake_fnp,
            "whestbench": fake_whest,
            "whestbench.domain": fake_domain,
        })
        builtins.__import__ = deny_numpy
        __import__("m145_deployable_estimator")
    finally:
        builtins.__import__ = original_import
        sys.path[:] = old_path
        for name, previous in saved.items():
            if previous is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = previous


def test_positive_diagonal_qr_is_algebraically_haar_representative() -> None:
    # This validates the exact QD, DR sign algebra implemented in deployment.
    # It deliberately avoids NumPy so it also runs in the import-deny shell.
    q = ((0.6, -0.8), (0.8, 0.6))
    r = ((-2.0, 3.0), (0.0, 5.0))
    signs = (-1.0, 1.0)
    q_positive = tuple(
        tuple(q[i][j] * signs[j] for j in range(2)) for i in range(2)
    )
    r_positive = tuple(
        tuple(signs[i] * r[i][j] for j in range(2)) for i in range(2)
    )
    product = tuple(
        tuple(sum(q_positive[i][k] * r_positive[k][j] for k in range(2)) for j in range(2))
        for i in range(2)
    )
    assert r_positive[0][0] >= 0.0 and r_positive[1][1] >= 0.0
    assert product == tuple(tuple(row) for row in (
        (q[0][0] * r[0][0] + q[0][1] * r[1][0], q[0][0] * r[0][1] + q[0][1] * r[1][1]),
        (q[1][0] * r[0][0] + q[1][1] * r[1][0], q[1][0] * r[0][1] + q[1][1] * r[1][1]),
    ))


def test_householder_conditional_completion_preserves_radius_and_anchor() -> None:
    # 2D exact case: H maps the first radius-scaled row to the anchor and is
    # orthogonal, which is the only algebra used in the 256D implementation.
    radius = 3.0
    frame = [[radius, 0.0], [0.0, radius]]
    anchor = (0.0, 1.0)
    v = [frame[0][i] - radius * anchor[i] for i in range(2)]
    vv = sum(value * value for value in v)
    transformed = [
        [row[i] - sum(row[j] * v[j] for j in range(2)) * 2.0 / vv * v[i] for i in range(2)]
        for row in frame
    ]
    assert transformed[0] == [0.0, radius]
    gram = [[sum(transformed[i][k] * transformed[j][k] for k in range(2)) for j in range(2)] for i in range(2)]
    assert gram == [[radius * radius, 0.0], [0.0, radius * radius]]
