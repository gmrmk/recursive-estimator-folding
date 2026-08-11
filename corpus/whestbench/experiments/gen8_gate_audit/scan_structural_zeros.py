"""Empirical half of the M183 defect-class hunt.

The static scan (scan_m183_class.py) finds shapes that CAN return a structural
zero.  This scan finds measurements that DID: every *.json artifact under
corpus/whestbench/experiments whose value is exactly 0 / 0.0 / [] / {} at a key
that names a measured share, count, fraction, rate, error or violation.

A structural zero is only interesting when the same script has no positive
control, so each hit is joined back to the producing directory's *.py files and
flagged with whether the directory contains any evidence of a positive-control
fixture (a test that makes the detector fire).

Read-only.  Writes only into gen8_gate_audit/.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent

STAT_KEY = re.compile(
    r"(share|frac|fraction|ratio|count|n_|num_|violat|mismatch|defect|"
    r"reduction|gain|hits|detected|found|f64|float64|nonzero|breach|"
    r"failures?|errors?)", re.I)

POSITIVE_CONTROL_HINT = re.compile(
    r"(positive[_ ]control|deliberately|known[_ ]bad|should[_ ]fire|"
    r"must[_ ]detect|fixture_positive|synthetic_violation|sanity_positive)", re.I)


def walk(obj, path, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            walk(v, path + [str(k)], out)
    elif isinstance(obj, list):
        if not obj:
            out.append((".".join(path), "[]"))
        else:
            for i, v in enumerate(obj[:200]):
                walk(v, path + [f"[{i}]"], out)
    else:
        if obj is False:
            return
        if isinstance(obj, (int, float)) and obj == 0:
            out.append((".".join(path), obj))


def main():
    rows = []
    for jf in sorted(EXPERIMENTS.rglob("*.json")):
        if "__pycache__" in jf.parts or jf.parent == HERE:
            continue
        if jf.stat().st_size > 8_000_000:
            continue
        try:
            data = json.loads(jf.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            continue
        zeros = []
        walk(data, [], zeros)
        interesting = [(p, v) for p, v in zeros
                       if STAT_KEY.search(p.split(".")[-1] or "")]
        if not interesting:
            continue
        d = jf.parent
        pysrc = "\n".join(p.read_text(encoding="utf-8", errors="replace")
                          for p in d.glob("*.py"))
        rows.append({
            "dir": str(d.relative_to(EXPERIMENTS)),
            "artifact": jf.name,
            "zero_stat_keys": [p for p, _ in interesting][:25],
            "n_zero_stats": len(interesting),
            "has_positive_control_hint": bool(POSITIVE_CONTROL_HINT.search(pysrc)),
            "py_files": sorted(p.name for p in d.glob("*.py")),
        })

    rows.sort(key=lambda r: (-r["n_zero_stats"], r["dir"]))
    (HERE / "structural_zeros.json").write_text(
        json.dumps(rows, indent=1), encoding="utf-8")
    print(f"artifacts with zero-valued measured statistics: {len(rows)}")
    for r in rows[:45]:
        pc = "posctrl" if r["has_positive_control_hint"] else "NO-POSCTRL"
        print(f"{r['n_zero_stats']:4d}  {pc:11s}  {r['dir']}/{r['artifact']}")
        print(f"        {r['zero_stat_keys'][:6]}")


if __name__ == "__main__":
    main()
