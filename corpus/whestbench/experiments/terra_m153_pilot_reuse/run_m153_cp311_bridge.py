"""CPython-3.11 bridge for response-free M153 FlopScope traces."""

from __future__ import annotations

import runpy
import sys
import types
from pathlib import Path

import numpy


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "m145_defensive_acg"))
sys.path.append(str(HERE.parents[1] / "whest-v014" / "Lib" / "site-packages"))

whestbench = types.ModuleType("whestbench")
domain = types.ModuleType("whestbench.domain")
whestbench.BaseEstimator = object
whestbench.SetupContext = lambda **values: types.SimpleNamespace(**values)
domain.MLP = lambda **values: types.SimpleNamespace(
    **values, validate=lambda: None
)
sys.modules["whestbench"] = whestbench
sys.modules["whestbench.domain"] = domain

sys.argv = ["run_m153_deployable_structural_trace.py", *sys.argv[1:]]
runpy.run_path(
    str(HERE / "run_m153_deployable_structural_trace.py"), run_name="__main__"
)
