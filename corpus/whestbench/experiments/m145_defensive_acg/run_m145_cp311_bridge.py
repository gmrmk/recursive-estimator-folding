"""CPython-3.11 bridge for response-free M145 FlopScope structural traces.

The cached WhestBench wheel cannot import its optional CPython-3.14 pyarrow
dependency in the available 3.11 runtime.  The trace needs only the documented
container types below, so this bridge supplies those types while loading the
real pinned FlopScope 0.10 package.  It never creates or reads truth data.
"""

from __future__ import annotations

import runpy
import sys
import types
from pathlib import Path

import numpy  # Load the CPython-3.11 build before appending the cached wheel.


HERE = Path(__file__).resolve().parent
SITE_PACKAGES = HERE.parents[1] / "whest-v014" / "Lib" / "site-packages"
sys.path.append(str(SITE_PACKAGES))

whestbench = types.ModuleType("whestbench")
domain = types.ModuleType("whestbench.domain")
whestbench.BaseEstimator = object
whestbench.SetupContext = lambda **values: types.SimpleNamespace(**values)
domain.MLP = lambda **values: types.SimpleNamespace(
    **values, validate=lambda: None
)
sys.modules["whestbench"] = whestbench
sys.modules["whestbench.domain"] = domain

sys.argv = ["run_m145_deployable_structural_trace.py", *sys.argv[1:]]
runpy.run_path(
    str(HERE / "run_m145_deployable_structural_trace.py"), run_name="__main__"
)
