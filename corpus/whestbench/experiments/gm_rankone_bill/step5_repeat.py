"""Step-5: bit-repeat verification in a fresh interpreter.

Re-runs the decisive computations and compares them BITWISE against the values
already on disk from the first pass.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import time

import numpy as np

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(EXP / "m205_rankone_complete_physical_owner"))

PY = sys.executable
T0 = time.time()

first = {
    "step0": json.loads((HERE / "step0_bill.json").read_text()),
    "step1": json.loads((HERE / "step1_identities.json").read_text()),
    "step2": json.loads((HERE / "step2_scale.json").read_text()),
    "step3": json.loads((HERE / "step3_attack.json").read_text()),
    "step4": json.loads((HERE / "step4_attribute.json").read_text()),
}
for name in ("step0_bill.json", "step1_identities.json", "step2_scale.json", "step4_attribute.json"):
    (HERE / name).rename(HERE / (name + ".pass1"))

for script in ("step0_bill.py", "step1_identities.py", "step2_scale.py", "step4_attribute.py"):
    t = time.time()
    r = subprocess.run([PY, "-B", "-u", str(HERE / script)], cwd=str(HERE), capture_output=True, text=True)
    print(f"  rerun {script}: exit={r.returncode} ({time.time()-t:.1f}s)", flush=True)
    if r.returncode != 0:
        print(r.stdout[-2000:], r.stderr[-2000:])
        raise SystemExit(1)

second = {
    "step0": json.loads((HERE / "step0_bill.json").read_text()),
    "step1": json.loads((HERE / "step1_identities.json").read_text()),
    "step2": json.loads((HERE / "step2_scale.json").read_text()),
    "step4": json.loads((HERE / "step4_attribute.json").read_text()),
}


def strip_time(o):
    if isinstance(o, dict):
        return {k: strip_time(v) for k, v in o.items() if k not in ("seconds", "wall_seconds")}
    if isinstance(o, list):
        return [strip_time(v) for v in o]
    return o


rep = {}
for k in ("step0", "step1", "step2", "step4"):
    a = json.dumps(strip_time(first[k]), sort_keys=True)
    b = json.dumps(strip_time(second[k]), sort_keys=True)
    rep[k + "_bitwise_identical"] = a == b
    print(f"  {k} bitwise identical: {rep[k+'_bitwise_identical']}", flush=True)

# --- the one expensive step-3 number, repeated on its own ---
import f32_shadow as S  # noqa: E402

n = 256
rng = np.random.Generator(np.random.Philox(920000 + n))
wt = rng.normal(size=(n, n + 1)) * np.sqrt(2.0 / n)
k4 = rng.normal(size=n)
k31 = rng.normal(size=(n, n))
np.fill_diagonal(k31, 0.0)
k22 = rng.normal(size=(n, n))
k22 = 0.5 * (k22 + k22.T)
np.fill_diagonal(k22, 0.0)
ref = S.independent_physical_collision_source(wt, k4, k31, k22, np.float64)
naive32 = S.independent_physical_collision_source(
    wt, k4.astype(np.float32), k31.astype(np.float32), k22.astype(np.float32), np.float32
)
rel = S.slot_rel(naive32, ref)["rel"]
row = [r for r in first["step3"]["I3d_accumulator_attack"] if r["n"] == 256][0]
rep["I3d_n256_naive_first"] = row["naive_f32_vs_naive_f64_rel"]
rep["I3d_n256_naive_repeat"] = rel
rep["I3d_n256_bitwise_identical"] = rel == row["naive_f32_vs_naive_f64_rel"]
print("  I3d n=256 repeat:", rel, "identical:", rep["I3d_n256_bitwise_identical"], flush=True)

rep["all_bitwise_identical"] = all(v for k, v in rep.items() if k.endswith("bitwise_identical"))
rep["wall_seconds"] = time.time() - T0
(HERE / "step5_repeat.json").write_text(json.dumps(rep, indent=2) + "\n", encoding="utf-8")
print("WROTE step5_repeat.json  all_identical=%s  wall=%.1fs" % (rep["all_bitwise_identical"], rep["wall_seconds"]))
