"""Load the pinned FlopScope wheel in the available CPython 3.11 runtime."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

import numpy


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.append(str(HERE.parents[1] / "whest-v014" / "Lib" / "site-packages"))
sys.argv = ["run_m156_native_trace.py", *sys.argv[1:]]
runpy.run_path(str(HERE / "run_m156_native_trace.py"), run_name="__main__")

