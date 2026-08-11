"""CI shim: make the spectral PSD guard suite discoverable by `unittest
discover -s tests`.

The guard and its tests live beside the evidence they came from, in
corpus/whestbench/experiments/gm_spectral_psd_guard/. The workflow only
discovers `tests/`, so without this the suite would never run in CI.

Loading the experiment module by path (rather than copying the tests) keeps one
copy of the assertions and guarantees CI exercises exactly the file the report
cites.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = (ROOT / "corpus" / "whestbench" / "experiments" / "gm_spectral_psd_guard"
          / "test_spectral_psd_guard.py")

_spec = importlib.util.spec_from_file_location("gm_spectral_psd_guard_tests", TARGET)
_module = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
sys.modules[_spec.name] = _module
_spec.loader.exec_module(_module)

# Re-export the TestCase so unittest discovery in this file picks it up.
SpectralGuardTests = _module.SpectralGuardTests
